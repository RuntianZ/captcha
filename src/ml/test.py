# -*- coding: utf-8 -*-
from train import crack_captcha, convert2gray
from gen_captcha import gen_captcha_text_and_image

def test_cnn():
    def wrap_gen_captcha_text_and_image():
        while True:
            text, image = gen_captcha_text_and_image()
            if image.shape == (60, 160, 3):
                return text, image
    
    text,image = wrap_gen_captcha_text_and_image()
    image = convert2gray(image) 
    image = image.flatten() / 255 
    predict = crack_captcha(image)
    
    print(predict,'  ', text)
    
test_cnn()
    
    
    

