#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import numpy as np
import argparse
import cv2
import pcl

OUTDIR = "mesh"
DEPTHDIR = "depthROI"
EXT1 = ".png"
EXT2 = ".ply"
EXT3 = ".pcd"

def cvtDepthTo3DPoints(m, scale_factor):
	H, W = m.shape
	nrows = cv2.countNonZero(m)
	points_array = np.zeros((nrows,3)).astype(np.float32)
	k = 0
	for i in range(1,W):
		for j in range(1,H):
			if m[j-1][i-1] != 0:
				points_array[k][0] = i
				points_array[k][1] = j
				points_array[k][2] = m[j-1][i-1].astype(np.float32)/scale_factor
				k+= 1
	return points_array

def main():
	p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
	p.add_argument('--v', dest = 'video_path', action = 'store', default = '', help = 'path file *.oni')
	args = p.parse_args()
	
	if not os.path.isdir(OUTDIR):
		os.mkdir(OUTDIR)	

	i = 1
	while os.path.isfile(DEPTHDIR + "/" + str(i) + EXT1):
		depth_frame = cv2.imread(DEPTHDIR + "/"+str(i)+EXT1,2)
		depth_frame = cv2.split(depth_frame)
		depth_frame = depth_frame[0]
				
		points = cvtDepthTo3DPoints(depth_frame, 1)
		pointcloud = pcl.PointCloud()
		pointcloud.from_array(points)
		
		os.chdir(OUTDIR)
		pcl.save(pointcloud, str(i) + EXT2)
		pointcloud.to_file(str(i) + EXT3)
		
		print "Converting " + str(i) + ".png" + "into " + str(i) + ".pcd"
		os.chdir("..")
		
		i+=1
		
		ch = 0xFF & cv2.waitKey(1)
		if ch == 27:
			break	
	
	cv2.destroyAllWindows()

if __name__ == '__main__':
        main()
