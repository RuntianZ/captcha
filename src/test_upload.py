import requests

url = 'http://vitas.runtianz.cn/captcha/upload'

files = {'file': ('test.txt', open('test.txt', 'rb'))}

data = {'filename': 'func', 'username': 'user3', 'password': 'cptbtptp'}

r = requests.post(url = url, files = files, data = data)
print(r.text)
