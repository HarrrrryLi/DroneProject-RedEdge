#!/usr/bin/env python

import rospy
import requests
import sys
# from sensor_msgs.msg import Image
# from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String
import signal
import time
from cv_bridge import CvBridge
import numpy as np
import cv2

def getImage(publisher,camera_nums):

	home_url = 'http://192.168.10.254'
	# Capture
	capture_params = {'preview':'true','block':'true'}
	r = requests.post(home_url+'/capture',params=capture_params)
	time.sleep(0.6) #wait for save complete

	# Get latest capture image
	r = requests.get(home_url+'/files')
	json_dict = r.json()
	# print json_dict

	lastest_set = json_dict['directories'][-1]
	# print lastest_set
	r = requests.get('{}/files/{}'.format(home_url,lastest_set))
	json_dict = r.json()

	lastest_group = json_dict['directories'][-1]
	r = requests.get('{}/files/{}/{}'.format(home_url,lastest_set,lastest_group))
	json_dict = r.json()
	# print json_dict
	lastest_image_sets = json_dict['files'][-1*camera_nums:]
	# print last_image_sets 

	file_lists = []
	bridge = CvBridge()
	publish_string_list = [] 
	for cnt in range(camera_nums): 
		image_file = lastest_image_sets[cnt]
		file_name = image_file['name']
		file_lists.append(file_name)
		publish_string_list.append('{}/files/{}/000/{}'.format(home_url,lastest_set,file_name))

	publish_string = ';'.join(publish_string_list)
	publisher.publish(publish_string)
	rospy.loginfo(publish_string)
		

	# file_list_print = ' '.join(['Latest Image Files are:',','.join(file_lists)])

	# print(file_list_print)
def RedEdge():
    rospy.init_node('rededge',anonymous=True)

    # if len(sys.argv) < 2:
    #     rospy.logwarn('Using All Cameras.')
    #     camera_nums = 5
    # else:
    #     camera_nums = sys.argv[1]

    try:
        camera_nums = rospy.get_param("~camera_num")
    except KeyError:
        rospy.logwarn('Using All Cameras.')
        camera_nums = 5

    publisher = rospy.Publisher('rededge',String,queue_size=10)
    rate = rospy.Rate(2.5)
    while not rospy.is_shutdown():
        try:
            getImage(publisher,camera_nums)
        except requests.exceptions.ConnectionError:
            rospy.logerr('CANNOT Connect RedEdge WIFI!')
            # sys.exit(1)
        finally:
        	rate.sleep()


def handler(signum, frame):
    sys.exit(0)


if __name__ == '__main__':
	signal.signal(signal.SIGINT, handler)
	try:
		RedEdge()
	except rospy.ROSInterruptException:
	    pass
	
