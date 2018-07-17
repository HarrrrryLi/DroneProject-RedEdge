import requests
from io import open as iopen
import time

home_url = 'http://192.168.10.254'

# Capture
capture_params = {'preview':'true','block':'true'}
r = requests.post(home_url+'/capture',params=capture_params)
time.sleep(0.6) #wait for save complete

# Get latest capture image
r = requests.get(home_url+'/files')
json_dict = r.json()
lastest_set = json_dict['directories'][-1]
# print last_set
r = requests.get('{}/files/{}/000'.format(home_url,lastest_set))
json_dict = r.json()
# print json_dict
lastest_image_sets = json_dict['files'][-5:]
# print last_image_sets 

file_lists = []
for image_file in lastest_image_sets: 
	file_name = image_file['name']
	file_lists.append(file_name)
	r = requests.get('{}/files/{}/000/{}'.format(home_url,lastest_set,file_name))
	with iopen(file_name, 'wb') as file:
		file.write(r.content)

file_list_print = ' '.join(['Latest Image Files are:',','.join(file_lists)])

print(file_list_print)

## TODO: RUN using GPS from drone.