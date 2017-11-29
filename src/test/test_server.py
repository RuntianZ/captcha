<<<<<<< Updated upstream
import sys;
=======
import sys
>>>>>>> Stashed changes
sys.path.append("../")
from server import *

server.server_login('user3', 'cptbtptp')
print(server.server_get(groupid = 1))
server.server_logout()
print(server.server_get('user1', 'yqqlmgsycl', '4'))
