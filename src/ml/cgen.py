#coding:utf-8
'''
Created by nicklin96
on 01:32:22 Nov. 30, 2017
'''
from captcha.image import ImageCaptcha  
import numpy as np
from PIL import Image
import random
import requests as req
from io import BytesIO

import sys
sys.path.append('../')
from server import *

# TO DO replace this with server.py API.
# Numbers, upper characters and lower characters will appear in captcha text.
# To accelerate the training process, we can reduce the character set, for example using numbers and lower characters only.
number = ['0','1','2','3','4','5','6','7','8','9']
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']


# genarate a random 4-character string 
def random_captcha_text(char_set=number+alphabet+ALPHABET, captcha_size=4):
    
    tmp = list(char_set)
    random.shuffle(tmp)
    
    return ''.join(tmp[0:captcha_size])
    
	

# genarate a random captcha image. The image will be returned as a numpy array so as to put it into the CNN conveniently
def gen_captcha_text_and_image():
    # First genarate an empty image
	image = ImageCaptcha() 

	captcha_text = ''.join(random_captcha_text())
    
    # Initialize the captcha
	captcha = image.generate(captcha_text)
    
    # Turn the captcha into a python image, and then a numpy array.
	captcha_image = Image.open(captcha) 
	captcha_image = np.array(captcha_image) 

	return captcha_text, captcha_image


def get_captcha_from_url(url, local):
    if not local:
        response = req.get(url)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(url)
    out = image.resize((160,60),Image.ANTIALIAS)
    output = np.array(out)
    return output


def server_generator(username, password, groupid):

	def real_generator():
		url = server.server_get(username = username, password = password, groupid = groupid)
		ans = server.server_view(username, password)
		img = get_captcha_from_url(url, False)
		return ans, img

	return real_generator
