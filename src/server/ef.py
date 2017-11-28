# ef.py - The error function module
from ctypes import *
import os
import platform


class ErrorFunctionException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def message(self):
        return self.msg


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
error_function_docstr = [default_error_function.__doc__]


def load_cfunc(sofile, funcname):
	if not os.path.exists(sofile):
		raise ErrorFunctionException('Shared library file does not exist.')
	if platform.system() == "Windows":
		lib = windll.LoadLibrary(sofile)
	else:
		lib = cdll.LoadLibrary(sofile)
	if not hasattr(lib, funcname):
		raise ErrorFunctionException('The function name does not exist.')
	c_func = getattr(lib, funcname)
	c_func.argtypes = [c_char_p, c_char_p]
	c_func.restype = c_double
	return c_func


def register_ef(func, docstr):
    '''
    register_ef -     Register an error function.
    :param func:      The function to be registered.
    :param docstr:    The doc string of the function.
    :return:          The internal version of this error function.
    '''
    func.__doc__ = docstr
    error_function_lib.append(func)
    error_function_docstr.append(docstr)
    return len(error_function_lib) - 1


def register_error_function(sofile, funcname, docstr):
	'''
	register_error_function - Register an error function from a shared library.
	:param sofile:            The shared library file name.
	:param funcname:          The function name.
	:param docstr:            The doc string of this function.
	:return:                  The internal version of this error function.

	Error functions are called using their internal version numbers. The version
	number 0 is reserved for the default error function. Other error functions
	can be registered using this function. The function should have the following
	header (in C):
	double new_function(char *result, char *ans)

	For example:
	>>> register_error_function('./ef.so', 'my_error_function', 'This is my function.')
	1
	
	The doc string can be accessed using help_error_function(version).
	For example:
	>>> help_error_function(1)
	This is my function.
	'''
	ef = load_cfunc(sofile, funcname)
	return register_ef(ef, docstr)


def help_error_function(version):
	return error_function_docstr[version]
