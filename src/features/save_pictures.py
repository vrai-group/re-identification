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
MIN_HEIGHT=1200
N_ITER=5

DIR1="img"
DIR2="depth"
DIR3="mask"
DIR4="depth_corr" #i frame depth corretti vengono usati dallo script DepthToMesh

skip=5 #salto dei frame

def removeBlackPixels(depth):
	
	#vengono realizzate delle operazioni morfologiche che distorcendo in
	#parte il depth frame, eliminano i pixel neri
	kernel = np.ones((5,5),np.uint8)
	depth_dil = cv2.dilate(depth,kernel,iterations = N_ITER)
	depth_er = cv2.erode(depth_dil,kernel,iterations = N_ITER)
	
	#creazione di una maschera che avrà valore 1 in corrispondenza dei pixel 
	#neri, e zero in corrispondenza di quelli di diverso colore
	mask = cv2.inRange(depth.copy(), 0, 1)
	
	#applicazione della maschera al depth frame 
	depth_er = cv2.bitwise_and(depth_er,depth_er,mask=mask)
	
	#il depth frame viene corretto "riempiendo" i pixel neri
	depth = depth + depth_er
	
	return depth

def extractMask(depth_array_fore):
	#segmentazione della maschera
	mask = cv2.inRange(depth_array_fore, MIN_RANGE, MAX_RANGE)
	
	contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	#eliminazione, dal vettore contours, dei contorni che hanno area superiore a MIN_AREA (quindi quelli più significativi)
	for idx, cnt in enumerate(contours):
		area = cv2.contourArea(cnt)		
		if (area>MIN_AREA):
			contours.pop(idx)	
		
	#eliminazione dei contorni rimanenti dalla maschera
	cv2.drawContours(mask, contours, -1, 0, -1)	
	
	#eliminazione del rumore tramite l'operazione morfologica di apertura
	kernel = np.ones((5,5),np.uint8)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
	
	return mask

def getMaxHeight(depth, mask):
	#applicazione della maschera, così si è certi che il massimo venga
	#trovato nell'area desiderata
	masked = cv2.bitwise_and(depth,depth,mask = mask)
	_,h,_,pos = cv2.minMaxLoc(masked)
	
	return h, pos[0], pos[1]

def main():
	p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
	p.add_argument('--v', dest = 'video_path', action = 'store', default = '', help = 'path file *.oni')
	args = p.parse_args()
	
	#creazione delle directory in cui salvare le immagini, se non sono già presenti
	if not os.path.isdir(DIR1):
		os.mkdir(DIR1)
	
	if not os.path.isdir(DIR2):
		os.mkdir(DIR2)
		
	if not os.path.isdir(DIR3):
		os.mkdir(DIR3)	
		
	if not os.path.isdir(DIR4):
		os.mkdir(DIR4)
		
	#inizializzazione di OpenNI e apertura degli stream video	
	openni2.initialize()
	dev = openni2.Device.open_file(args.video_path)
	depth_stream = dev.create_depth_stream()
	color_stream = dev.create_color_stream()
	depth_stream.start()
	color_stream.start()
    	
	#contiene il timestamp del frame precedente
	t_prev = -2
	#contiene il timestamp del frame corrente
	t_curr = -1
	#indice incrementato ogni volta che si salvano i frame
	i = 0
	#indice che conta i frame aperti dallo stream video
	frame_count = 0
	
	while (t_curr > t_prev):
		#acquisizione degli array relativi ai frame dagli stream RGB e Depth
		frame_depth = depth_stream.read_frame()
		frame_color = color_stream.read_frame()
		
		#aggiornamento dei timestamp		
		t_prev = t_curr
		t_curr = frame_depth.timestamp
		
		frame_count += 1
		
		if frame_count % skip == 1:
			
			
			print frame_count
			
			#conversione di tipo
			frame_depth_data = frame_depth.get_buffer_as_uint16()
			frame_color_data = frame_color.get_buffer_as_uint8()
			#conversione degli array in un formato utilizzabile da OpenCV
			depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
			color_array = np.ndarray((frame_color.height, frame_color.width, 3), dtype = np.uint8, buffer = frame_color_data)
			color_array = cv2.cvtColor(color_array, cv2.COLOR_BGR2RGB)
			
			#cv2.imshow("RGB", color_array)
			#cv2.imshow("Depth", depth_array)
			
			#se il frame è il primo, può essere preso come background del canale depth
			if frame_count == 1:
				depth_array_back = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
				depth_array_back = depth_array
			
			#eliminazione delle aree nere dal depth frame dovute ad errori del sensore di profondità
			depth_array_clean = removeBlackPixels(depth_array)
			
			#si ottiene il foreground togliendo il background al frame corrente
			depth_array_fore = cv2.absdiff(depth_array_clean, depth_array_back)
			#estrazione della maschera dal depth foreground
			mask = extractMask(depth_array_fore)
			h, x, y = getMaxHeight(depth_array_fore, mask)
			#se l'altezza massima nel frame depth è maggiore della soglia, si salvano le immagini
			if (h>MIN_HEIGHT):
				i+=1				
				os.chdir(DIR1)
				cv2.imwrite(str(i)+".png",color_array)
				os.chdir("..")
				os.chdir(DIR2)
				cv2.imwrite(str(i)+".png",depth_array)
				os.chdir("..")
				os.chdir(DIR3)
				cv2.imwrite(str(i)+".png",mask)
				os.chdir("..")
				os.chdir(DIR4)
				cv2.imwrite(str(i)+".png",depth_array_clean)
				os.chdir("..")
				
			ch = 0xFF & cv2.waitKey(1)
			if ch == 27:
				break	
	
	depth_stream.stop()
	color_stream.stop()
	openni2.unload()
	cv2.destroyAllWindows()

if __name__ == '__main__':
        main()
