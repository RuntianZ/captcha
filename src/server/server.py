import urllib.request


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

# The default error function
def default_error_function(result, answer):
    '''
    This is the default error function. It returns 1.0 if
    result == answer and 0.0 otherwise.

    Examples:
    >>> default_error_function('abc', 'abc')
    1.0
    >>> default_error_function('abc', 'AbC')
    0.0
    '''
    if result == answer:
        return 1.0
    else:
        return 0.0

# The error function library
error_function_lib = [default_error_function]

def error_function(result, answer, version):
    '''
    error_function - The error function.
    :param result:   Recognition result.
    :param answer:   Real captcha.
    :param version:  The version of the error function to be used.
    :return:         A value between 0 and 1. 1 means identical strings
                     while 0 means totally wrong.

    This function provides an interface between C code and python code.
    If version is 0, the default error function will be used. The
    default error function returns 1.0 if result == answer and 0.0 
    otherwise.
    '''
    return error_function_lib[version](result, answer)

def register_ef(func, docstr):
    '''
    register_ef -     Register an error function.
    :param func:      The function to be registered.
    :param docstr:    The doc string of the function.
    :return:          The version of this error function.
    '''
    func.__doc__ = docstr
    error_function_lib.append(func)
    return len(error_function_lib) - 1


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
    You may attempt multiple times after you call server_attempt, which means
    that you can attempt on the same captcha file more than once.
    '''
    ans = server_view(username, password)
    return error_function(result, ans, ef_version)
