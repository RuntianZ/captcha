# server.py - The server module

import urllib.request
import server.ef as ef


class ServerException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def message(self):
        return self.msg


def server_get(username, password, groupid):
    '''
    server_get -       Create a captcha image file on the server and get its url.
    :param username:   Username.
    :param password:   Password.
    :param groupid:    The ID of the captcha group.
    :return:           The URL of the captcha image.

    If all arguments are correct, the server will generate a captcha file and return
    its url. Otherwise, an exception will be raised.
    '''
    groupid = str(groupid)
    if not groupid.isdigit():
        raise ServerException('Groupid must be a digit.')
    url = 'http://vitas.runtianz.cn/captcha/get?username=' + \
          username + '&password=' + password + '&groupid=' + groupid
    with urllib.request.urlopen(url) as page:
        data = page.read()
    resp = str(data, 'utf-8')
    if (len(resp) > 8) and ('Success' == resp[0:7]):
        return resp[8:]
    raise ServerException(resp)


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
    raise ServerException(resp)


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
