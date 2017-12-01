# server.py - The server module

import urllib.request
import server.ef as ef
import tarfile
import glob
import os
import requests


# Cached user and password.
cached_username = ''
cached_password = ''


def cache_login(func):

    def cached_func(*args, **kwargs):
        global cached_username, cached_password
        if (cached_username == '') or ('username' in kwargs):
            return func(*args, **kwargs)
        return func(username = cached_username, password = cached_password, *args, **kwargs)

    return cached_func


@cache_login
def server_get(username, password, groupid):
    '''
    server_get -       Create a captcha image file on the server and get its url.
    :param username:   Username.
    :param password:   Password.
    :param groupid:    The ID of the captcha group, can be either a number or a string.
    :return:           The URL of the captcha image.

    If all arguments are correct, the server will generate a captcha file and return
    its url. Otherwise, an exception will be raised.
    The argument groupid can be either a number or a string. If a string, the method
    will check whether the string is a number, and raise an exception if not.
    '''
    groupid = str(groupid)
    if not groupid.isdigit():
        raise ValueError('Groupid must be a digit.')
    url = 'http://vitas.runtianz.cn/captcha/get?username=' + \
          username + '&password=' + password + '&groupid=' + groupid
    with urllib.request.urlopen(url) as page:
        data = page.read()
    resp = str(data, 'utf-8')
    if (len(resp) > 8) and ('Success' == resp[0:7]):
        return resp[8:]
    raise ValueError(resp)


def server_view(username, password):
    '''
    server_view -     View the characters of a captcha image file.
    :param username:  Username.
    :param password:  Password.
    :return:          The characters of a captcha file.

    This function is not supposed to be called directly in order
    to ensure that machine learning is done under supervised mode.
    You should instead call server_attempt.
    '''
    url = 'http://vitas.runtianz.cn/captcha/attempt?username=' + \
        username + '&password=' + password
    with urllib.request.urlopen(url) as page:
        data = page.read()
    resp = str(data, 'utf-8')
    if (len(resp) > 8) and ('Success' == resp[0:7]):
        return resp[8:]
    raise ValueError(resp)


@cache_login
def server_attempt(username, password, result, ef_version = 0):
    '''
    server_attempt -   Attempt to recognize a captcha file on the server.
    :param username:   Username.
    :param password:   Password.
    :param result:     The attempting result.
    :param ef_version: Indicate the error function that will be used to
                       evaluate the result. If ef_version is 0, the default
                       function will be used.  
    :return:           The result of the error function.

    You must call server_get before server_attempt. Otherwise, the server
    will raise an exception.
    If you want to attempt on the same captcha multiple times or use more
    than one error function, consider using server_iterate instead.

    For example:
    >>> server_attempt('user', 'password', 'abcde', 2)
    0.35
    '''
    ans = server_view(username, password)
    return ef.error_function_lib[ef_version](bytes(result, 'utf-8'), bytes(ans, 'utf-8'))


@cache_login
def server_iterate(username, password, results, versions):
    '''
    server_iterate -  To test a group of results using a group of error functions.
    :param username:  Username.
    :param password:  Password.
    :param results:   A list of results that will be tested.
    :param versions:  A list of error function versions that will be used.
    :return:          A list. Each item contains the results of different error
                      functions that test the same result.

    Use this method if you want to test on multiple results and use more than one
    error function. This function returns compare results in their input order.

    For example: If we have the following result
    Result     Version     Error function return
    'abc'      0           0.0
    'abc'      1           0.4
    'abc'      2           0.7
    'def'      0           0.0
    'def'      1           0.6
    'def'      2           0.9

    >>> server_iterate('user', 'password', ['def', 'abc'], [0, 2, 1])
    [[0.0, 0.9, 0.6], [0.0, 0.7, 0.4]]
    '''
    cmplist = []
    ans = server_view(username, password)
    l = len(results)
    m = len(versions)
    bans = bytes(ans, 'utf-8')

    # Iterate tests.
    for i in range(0, l):
        tmp = []
        bresult = bytes(results[i], 'utf-8')
        for j in range(0, m):
            tmp.append(ef.error_function_lib[versions[j]](bresult, bans))
        cmplist.append(tmp)

    return cmplist


def server_login(username, password):
    '''
    server_login -    Log in so that you don't need to provide user info every time.
    :param username:  Username.
    :param password:  Password.

    This method does not check whether username and password match. It only caches
    the login information and use that information whenever you call a method in the
    server module.
    Only one user can be logged in at a time, but you can call this method multiple 
    times. For example, if you happened to provide the wrong password, you can call
    this method to modify your password.
    Moreover, you can call server methods using another account even if you have 
    already logged in. But logging in with another account will log out the previous
    account.
    Once you have logged in, you cannot use positional arguments when calling server
    methods.

    Examples:
    >>> server_login('user1', 'password1')
    >>> server_get(groupid = 1)
    http://www.example.com/user1.png
    >>> server_get(1)
    Traceback (most recent call last):
        ...
    >>> server_get('user1', 'password1', 1)
    Traceback (most recent call last):
        ...
    >>> server_get(username = 'user2', password = 'password2', groupid = 1)
    http://www.example.com/user2.png
    '''
    global cached_username, cached_password
    cached_username = username
    cached_password = password


def server_logout():
    '''
    server_logout -  Log out if you have already logged in.

    Note:
    This method will not raise an error even if you haven't logged in.
    '''
    global cached_username
    cached_username = ''


# Walk in a directory and yielding files that match the extension.
def file_traverse(dir, ext):
    for i in glob.glob(os.path.join(dir, ext)):
        yield i


# Package a model file into a tar.gz file.
def packager(path, tarpath):
    if os.path.isdir(path):
        raise ValueError('Path should not be a directory.');
    dirpath, filepath = os.path.split(path)
    tar = tarfile.open(tarpath, 'w:gz')

    # Check 3 essential files.
    efile = path + '.index'
    if not os.path.isfile(efile):
        raise ValueError('Essential file ' + efile + ' does not exist.')
    efile = path + '.meta'
    if not os.path.isfile(efile):
        raise ValueError('Essential file ' + efile + ' does not exist.')
    efile = os.path.join(dirpath, 'checkpoint')
    if not os.path.isfile(efile):
        raise ValueError('Essential file ' + efile + ' does not exist.')

    print(efile)
    tar.add(efile)    
    ext = filepath + '.*'
    for file in file_traverse(dirpath, ext):
        print(file)
        tar.add(file)
    tar.close()
    return tarpath


@cache_login
def server_upload(username, password, path, model_name, replace = False):
    '''
    TODO
    '''
    
    # Process files.
    tarpath = 'temp.tar'
    packager(path, tarpath)

    url = 'http://vitas.runtianz.cn/captcha/upload'
    postdata = {'username': username, 'password': password, 'filename': model_name}
    files = {'file': (tarpath, open(tarpath, 'rb'))}
    r = requests.post(url = url, data = postdata, files = files)

    resp = r.text
    if (len(resp) > 8) and ('Success' == resp[0:7]):
        return resp[8:]
    raise ValueError(resp)

