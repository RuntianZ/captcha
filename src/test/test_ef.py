from ctypes import *
lib = cdll.LoadLibrary('./test_ef.so')
ef = lib.test_ef
ef.argtypes = [c_char_p, c_char_p]
ef.restype = c_double
print(ef(b"yes", b"no"))
