import requests
from io import open as iopen
import time
import serial
from datetime import datetime


def getMultiBytesValue(data,signed):
	if signed and ord(data[-1]) > 127:
		result = ord(data[-1]) - 256
	else:
		result = ord(data[-1])
	for b in data[-2::-1]:
		result = (result << 8) | ord(b)
	return result


class GPS_DATA():

  	def __init__(self,s=chr(0x00) * 44):
  		self.getfromString(s)

  	def getfromString(self,s):
  		if len(s) == 44:
  			self.latitude = getMultiBytesValue(s[0:4],True)
  			self.longitude = getMultiBytesValue(s[4:8],True)
  			self.height = getMultiBytesValue(s[8:12],True)
  			self.speed_x = getMultiBytesValue(s[12:16],True)
  			self.speed_y = getMultiBytesValue(s[16:20],True)
  			self.heading = getMultiBytesValue(s[20:24],True)
  			self.horizontal_accuracy = getMultiBytesValue(s[24:28],False)
  			self.vertical_accuracy = getMultiBytesValue(s[28:32],False)
  			self.speed_accuracy = getMultiBytesValue(s[32:36],False)
  			self.numSV = getMultiBytesValue(s[36:40],False)
  			self.status = getMultiBytesValue(s[40:44],False)



def receiveFromLL(high_byte,low_byte):
	# Open xbee serial
	xbee = serial.Serial('/dev/ttyUSB0',baudrate=57600,timeout = 10)
	print('Xbee Serial Opened')
	
	#Send Polling Request
	#'>*>p' is the start string of every request. Package number should be sent as [lower byte, higher byte]
	#If we want to request 0x0200(GPS Advanced) we need to send 0x00 then 0x20. 
	
	w = xbee.write(data = ['>','*','>','p',low_byte,high_byte])   #request GPS Advanced 0x0080
	xbee.flush()
	time.sleep(0.1) #wait for repsonse
	receive_size = xbee.in_waiting
	received_data = xbee.read(receive_size)
	if received_data[0:3] == '>*>' and received_data[-3:] == '<#<':
		length = getMultiBytesValue(received_data[3:5],False)
		package_description = ord(received_data[5])
		crc16 = getMultiBytesValue(received_data[-5:-3],False) 
		data = received_data[6:-5]
	else:
		length = -1
		package_description = -1
		data = ''
	xbee.close()
	return length,package_description,data

def getGPSdata():

	length,package_description,data = receiveFromLL(0x00,0x80)
	gps_data = GPS_DATA()
	
	if length <= 0:
		print('Requested GPS Data BUT NOTHING Received!')
	elif length != len(data) or package_description!=0x23:
		print('Request GPS Data BUT WRONG Messege Received!')
	else:
		gps_data.getfromString(data)
	return gps_data

def getvel_d():

	length,package_description,data = receiveFromLL(0x00,0x04)
	vel_d = 0
	if length <= 0:
		print('Requested vel_d Data BUT NOTHING Received!')
	elif length != len(data) or package_description!=0x03:
		print('Requested vel_d Data BUT WRONG Messege Received!')
	else:
		vel_d = getMultiBytesValue(data[-12:-8])
	return vel_d

def main():

	home_url = 'http://192.168.10.254'

	gps_data = getGPSdata()
	utc_time = datetime.utcnow()
	vel_d = getvel_d()

	# set GPS Data
	GPS_params = {
				  'latitude':gps_data.latitude,
				  'longitude':gps_data.longitude,
				  'altitude':gps_data.height,
				  'vel_n':gps_data.speed_y,
				  'vel_e':gps_data.speed_x,
				  'vel_d':vel_d,
				  'p_acc':gps_data.speed_accuracy,
				  'v_acc':gps_data.vertical_accuracy,
				  'fix3d':gps_data.status == 0x03 and gps_data.numSV >= 4,
				  'utc_time':utc_time
				 }

	r = requests.post(home_url+'/gps',params=GPS_params)

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

if __name__ == "__main__":
	try:
		main()
	except requests.exceptions.ConnectionError:
		print('CANNOT Connect RedEdge WIFI!')





