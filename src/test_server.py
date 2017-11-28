from server import *

i = ef.register_error_function('test_ef.dll', 'test_ef', 'This is my function.')
print(server.server_iterate('user3', 'cptbtptp', ['yes', 'no', 'yes'], [i, 0]))
