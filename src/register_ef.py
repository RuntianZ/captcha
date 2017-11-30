# register_ef.py
# This file automatically registers error functions you may need.
# You can only use this file on Windows.
from server import *

ef.register_error_function('captcha.dll', 'error_function', \
	'改进过的Levenshtein算法(即计算编辑距离)\n' + \
	'将删除字符和加入字符的代价赋为100\n' + \
	'替换的代价视字符的相似程度而定：一致则为0，完全不相似则为1\n')

