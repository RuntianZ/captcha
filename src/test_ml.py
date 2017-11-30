from ml import *
from server import *


server.server_login('user3', 'cptbtptp')
captcha_file = server.server_get(groupid = 1)
result = train.recognize(captcha_file)
print(result)
