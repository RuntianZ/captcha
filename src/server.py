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


def error_function(result, answer):
    '''
    error_function - The error function.
    :param result:   Recognition result.
    :param answer:   Real captcha.
    :return:         A value between 0 and 1. 1 means identical strings
                     while 0 means totally wrong.

    This function provides an interface between C code and python code.
    '''
    if result == answer:
        return 1.0
    else:
        return 0.0


def server_attempt(username, password, result):
    '''
    server_attempt -   Attempt to recognize a captcha file on the server.
    :param username:   Username.
    :param password:   Password.
    :param result:     The attempting result.
    :return:           The result of the error function.

    You must call server_get before server_attempt. Otherwise, the server
    will raise an exception.
    You may attempt multiple times after you call server_attempt, which means
    that you can attempt on the same captcha file more than once.
    '''
    ans = server_view(username, password)
    return error_function(result, ans)
