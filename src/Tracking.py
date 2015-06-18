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
	masked = cv2.bitwise_and(depth_array_fore,depth_array_fore,mask = mask)
	# ricerca dell'altezza e della posizione del soggetto
	_,height,_,position = cv2.minMaxLoc(depth_array_fore)
	
	#print "Altezza:" + str(height) + "mm Posizione:" + str(position) + " all'istante:" + str("{:020d}".format(frame_depth.timestamp))
	cv2.circle(depth_array_fore, position, 10, 65000)
	cv2.imwrite("./Filtered/Filtered_" + str("{:020d}".format(frame_depth.timestamp)) + "a.png", depth_array_fore)		
	cv2.imshow("Filtered", depth_array_fore)
	return (str(height)+";"+str(position[0])+";"+str(position[1])), mask
	
def main():
	"""The entry point"""
	p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
	p.add_argument('--v', dest = 'video_path', action = 'store', default = '', help = 'path file *.oni')
	args = p.parse_args()
	
	if not os.path.isdir("mask"):
		os.mkdir("mask")
	
	if not os.path.isdir("img"):
		os.mkdir("img")
		
	if not os.path.isdir("depth"):
		os.mkdir("depth")	
		
	openni2.initialize()
        dev = openni2.Device.open_file(args.video_path)
        print (dev.get_sensor_info(openni2.SENSOR_DEPTH))
        depth_stream = dev.create_depth_stream()
        color_stream = dev.create_color_stream()
        depth_stream.start()
        color_stream.start()
		
	global frame_depth
	frame_depth0 = depth_stream.read_frame()
	frame_color0 = color_stream.read_frame()
	frame_depth_data= frame_depth0.get_buffer_as_uint16()
	frame_color_data = frame_color0.get_buffer_as_uint8()
	
	
	# cattura del primo frame (quello del background)	
	depth_array_back = np.ndarray((frame_depth0.height, frame_depth0.width), dtype = np.uint16, buffer = frame_depth_data)
	color_array_back = np.ndarray((frame_color0.height, frame_color0.width, 3), dtype = np.uint8, buffer = frame_color_data)
	color_array_back = cv2.cvtColor(color_array_back, cv2.COLOR_BGR2RGB)
    
	continua = True
	frameNumber=0;	
	personId=args.video_path.split(".")[0]
	depth_file = open(args.video_path + ".csv","w")
	
	while continua:
		frame_depth = depth_stream.read_frame()
		frame_color = color_stream.read_frame()
		frame_depth_data = frame_depth.get_buffer_as_uint16()
		frame_color_data = frame_color.get_buffer_as_uint8()
		depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
		color_array = np.ndarray((frame_color.height, frame_color.width, 3), dtype = np.uint8, buffer = frame_color_data)
		color_array = cv2.cvtColor(color_array, cv2.COLOR_BGR2RGB)
		if int(frame_depth.timestamp)==0:
			continua=False
		else:
			frameNumber=frameNumber+1
			featStr, mask = process(depth_array, depth_array_back)
			depth_file.write("VideoId"+";"+str(frameNumber)+";"+personId+";"+featStr +"\n")
			masked_color_frame = cv2.bitwise_and(color_array,color_array,mask = mask)
			masked_depth_frame = cv2.bitwise_and(depth_array,depth_array,mask = mask)

			#masked_depth_frame viene scalato perché imshow lavora con 8 bit
			cv2.imshow("Depth", masked_depth_frame/10000.)
			cv2.imshow("Color",masked_color_frame)
			os.chdir("mask")
			cv2.imwrite(str(frameNumber)+".png",mask)
			os.chdir("..")
			os.chdir("img")
			cv2.imwrite(str(frameNumber)+".png",masked_color_frame)
			os.chdir("..")
			os.chdir("depth")
			cv2.imwrite(str(frameNumber)+".png",masked_depth_frame)
			os.chdir("..")
		ch = 0xFF & cv2.waitKey(1)
		if ch == 27:
			break	
	
	depth_file.close()		
	depth_stream.stop()
	color_stream.stop()
	openni2.unload()
	cv2.destroyAllWindows()

if __name__ == '__main__':
        main()
