import requests
from PIL import Image
from io import BytesIO
from StringIO import StringIO
from io import open as iopen
from urlparse import urlsplit

home_url = 'http://192.168.10.254'

payload = {'preview':'true','block':'true'}

r = requests.post(home_url+'/capture',params=payload)
print r.json()
# r =requests.post(home_url+'/capture')
r = requests.get(home_url+'/files/0006SET/000') 
print r.json()
r1 = requests.get(home_url+'/files/0005SET/000/IMG_0020_5.tif') 

with iopen('test.tif', 'wb') as file:
	file.write(r1.content)


## TODO: find the newest capture.  RUN using GPS from drone.