#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import numpy as np
import argparse
import cv2

OUTDIR = "depthROI"
MASKDIR = "mask"
DEPTHDIR = "depth"
EXT = ".png"

def getMaskROI(mask):
	contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	area = cv2.contourArea(contours[0])
	x,y,w,h = cv2.boundingRect(contours[0])
	return y,y+h,x,x+w
	
def main():
	p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
	p.add_argument('--v', dest = 'video_path', action = 'store', default = '', help = 'path file *.oni')
	args = p.parse_args()
	
	if not os.path.isdir(OUTDIR):
		os.mkdir(OUTDIR)	

	i = 1
	while os.path.isfile(MASKDIR+"/"+str(i)+EXT) & os.path.isfile(DEPTHDIR+"/"+str(i)+EXT):
		#carica i frame depth evitando la conversione automatica a profondità 8 bit, mandenendo quella a 16.
		depth_frame = cv2.imread(DEPTHDIR+"/"+str(i)+EXT, 2)
		#viene preso soltanto uno dei tre canali dell'immagine, dato che sono tutti identici
		depth_frame = cv2.split(depth_frame)
		depth_frame = depth_frame[0]
		
		mask_frame = cv2.imread(MASKDIR+"/"+str(i)+EXT)
		mask_frame = cv2.split(mask_frame)
		mask_frame = mask_frame[0]
				
		masked_depth_frame = cv2.bitwise_and(depth_frame,depth_frame,mask = mask_frame)
		
		y1,y2,x1,x2 = getMaskROI(mask_frame)
		roi = masked_depth_frame[y1:y2,x1:x2]
		
		os.chdir(OUTDIR)
		cv2.imwrite(str(i)+EXT, roi)
		os.chdir("..")
		
		cv2.imshow("depthroi", roi/10000.)
		print str(i)+EXT

		i+=1
		
		ch = 0xFF & cv2.waitKey(1)
		if ch == 27:
			break	
	
	cv2.destroyAllWindows()

if __name__ == '__main__':
        main()
