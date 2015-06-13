#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import numpy as np
import argparse
from primesense import openni2
import cv2

MIN_RANGE=150
MAX_RANGE=2500
MIN_AREA=5000

def process(depth_array, depth_array_back):
	depth_array_fore = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16)
	
	# sottrazione del background dal frame corrente
	cv2.absdiff(depth_array, depth_array_back, depth_array_fore)

	# segmentazione
	mask = cv2.inRange(depth_array_fore, MIN_RANGE, MAX_RANGE)
	
	# copia della maschera appena creata (ci servirà per il passo successivo)		
	mask1=mask.copy()
	
	# ricerca dei contorni presenti nella maschera appena creata
	# si lavora sulla copia della maschera dato che la funzione findContours modifica la sorgente su cui viene applicata 	
	#a, contours, hierarchy = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours, hierarchy = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	# eliminazione, dal vettore contours, dei contorni che hanno area superiore a MIN_AREA (quindi quelli più significativi)
	for idx, cnt in enumerate(contours):
		area = cv2.contourArea(cnt)		
		if (area>MIN_AREA):
			contours.pop(idx)	
	
	# eliminazione dei contorni rimanenti dalla maschera
	cv2.drawContours(mask, contours, -1, 0, -1)		
	
	# applicazione della maschera al frame del foreground
	depth_array_fore = cv2.bitwise_and(depth_array_fore,depth_array_fore,mask = mask)
	
	# ricerca dell'altezza e della posizione del soggetto
	a,height,a,position = cv2.minMaxLoc(depth_array_fore)
	
	print "Altezza:" + str(height) + "mm Posizione:" + str(position) + " all'istante:" + str("{:020d}".format(frame_depth.timestamp))
	cv2.circle(depth_array_fore, position, 10, 65000)
	cv2.imwrite("./Filtered/Filtered_" + str("{:020d}".format(frame_depth.timestamp)) + "a.png", depth_array_fore)		
	cv2.imshow("Filtered", depth_array_fore)
	return str(height)+";"+str(position[0])+";"+str(position[1])
	
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
	
	# cattura del primo frame (quello del background)	
	depth_array_back = np.ndarray((frame_depth1.height, frame_depth1.width), dtype = np.uint16, buffer = back)
	
	continua = True
	frameNumber=0;
	personId=args.video_path.split(".")[0]
	depth_file = open(args.video_path + ".csv","w")
	
	while continua:
                frame_depth = depth_stream.read_frame()
		frame_depth_data = frame_depth.get_buffer_as_uint16()
                depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
		if int(frame_depth.timestamp)==0:
			continua=False
		else:
			frameNumber=frameNumber+1
			result = process(depth_array, depth_array_back)
			depth_file.write("VideoId"+";"+str(frameNumber)+";"+personId+";"+result +"\n")
		ch = 0xFF & cv2.waitKey(1)
                if ch == 27:
                        break	
		
        depth_stream.stop()
        openni2.unload()
        cv2.destroyAllWindows()

if __name__ == '__main__':
        main()
