from server import *

i = ef.register_error_function('./test_ef.so', 'test_ef', 'This is my function.')
print(i)
print(ef.help_error_function(i))
print(server.server_attempt('user3', 'cptbtptp', 'yes', i))
