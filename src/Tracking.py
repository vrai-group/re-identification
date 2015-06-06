#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import numpy as np
import argparse
from primesense import openni2
import cv2

def process(depth_array, depth_array_back):
	depth_array_fore = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16)
	
	# background subtraction
	cv2.absdiff(depth_array, depth_array_back, depth_array_fore)

	# segmentation
	mask = cv2.inRange(depth_array_fore, 150, 2500)
	mask1=mask.copy()
	
	#find contours	
	a, contours, hierarchy = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	#delete contour with a little area by a mask array
	for idx, cnt in enumerate(contours):
		area = cv2.contourArea(cnt)		
		if (area>5000):
			contours.pop(idx)	
	
	
	cv2.drawContours(mask, contours, -1, 0, -1)		
	
	#apply the mask to image
	depth_array_fore = cv2.bitwise_and(depth_array_fore,depth_array_fore,mask = mask)
	
	#find the subject height and the subject position
	a,height,a,position = cv2.minMaxLoc(depth_array_fore)
	
	print "Altezza:" + str(height) + "mm Posizione:" + str(position) + " all'istante:" + str("{:020d}".format(frame_depth.timestamp))
	
	cv2.circle(depth_array_fore, position, 10, 65000)

	cv2.imwrite("./Filtered/Filtered_" + str("{:020d}".format(frame_depth.timestamp)) + "a.png", depth_array_fore)		
	cv2.imshow("Filtered", depth_array_fore)
	
def main():
        """The entry point"""
        p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
        p.add_argument('--v', dest = 'video_path', action = 'store', default = '', help = 'path file *.oni')
        args = p.parse_args()
	
	openni2.initialize()
        dev = openni2.Device.open_file(args.video_path)
        print (dev.get_sensor_info(openni2.SENSOR_DEPTH))
        depth_stream = dev.create_depth_stream()
        depth_stream.start()
		
	global frame_depth
	frame_depth1 = depth_stream.read_frame()
	back = frame_depth1.get_buffer_as_uint16()
	depth_array_back = np.ndarray((frame_depth1.height, frame_depth1.width), dtype = np.uint16, buffer = back)

	while True:
                frame_depth = depth_stream.read_frame()
		frame_depth_data = frame_depth.get_buffer_as_uint16()
                depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
		process(depth_array, depth_array_back)
		
		ch = 0xFF & cv2.waitKey(1)
                if ch == 27:
                        break	
		
        depth_stream.stop()
        openni2.unload()
        cv2.destroyAllWindows()

if __name__ == '__main__':
        main()
