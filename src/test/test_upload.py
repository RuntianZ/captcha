from server import *

server.server_login('user3', 'cptbtptp')
t = server.server_upload(path = 'model/model.ckpt', model_name = 'first')
print(t)
