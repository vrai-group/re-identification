#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
PyNiTracking
~~~~~~~~~~

This script implements an algorithm of people-tracking using a depth stream.

Usage: python2 PyNiTracking

You should link the libOpenNI2.so and the OpenNI2 directory in the script path.
If they are located inside /usr/lib, you could

$ ln -s /usr/lib/libOpenNI2.so
$ ln -s /usr/lib/OpenNI2

:copyright: (c) 2015 by IM Students of UnivPM.
:license: Apache2, see LICENSE for more details.
:date: 2015-05-29
"""

import numpy as np
from primesense import openni2
from primesense import _openni2 as c_api

import cv2

MAX = 10000
MIN = 100
AREA_MAX = 100000
AREA_MIN = 100


def process(color_array, depth_array, depth_array_back):
	# background subtraction
	depth_array_fore = depth_array_back - depth_array

	# segmentation
	mask = cv2.inRange(depth_array_fore, MIN, MAX)

	# find contours
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	for idx, cnt in enumerate(contours):
		area = cv2.contourArea(cnt)

		if (area < 100 or area > 10000):
			contours.pop(idx)

	# find cv2.minMaxLoc

	cv2.imshow('Fore', depth_array_fore)
	cv2.imshow('Mask', mask)

	cv2.imshow('Depth', depth_array)
	cv2.imshow('Color', color_array)
def main():
	try:
		openni2.initialize()
		dev = openni2.Device.open_any()
		print (dev.get_sensor_info(openni2.SENSOR_DEPTH))
	except (RuntimeError, TypeError, NameError):
		print(RuntimeError, TypeError, NameError)
	depth_stream = dev.create_depth_stream()
	color_stream = dev.create_color_stream()
	depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX = 640, resolutionY = 480, fps = 30))
	color_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX = 640, resolutionY = 480, fps = 30))
	depth_stream.start()
	color_stream.start()

	frameNo = 0

	while True:
		frame_depth = depth_stream.read_frame()
		frame_color = color_stream.read_frame()

		frame_depth_data = frame_depth.get_buffer_as_uint16()
		frame_color_data = frame_color.get_buffer_as_uint8()

		depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
		color_array = np.ndarray((frame_color.height, frame_color.width, 3), dtype = np.uint8, buffer = frame_color_data)
		color_array = cv2.cvtColor(color_array, cv2.COLOR_BGR2RGB)

		if frameNo == 0:
			depth_array_back = depth_array.copy()
			frameNo += 1

		process(color_array, depth_array, depth_array_back)

		ch = 0xFF & cv2.waitKey(1)
		if ch == 27:
			break
	depth_stream.stop()
	color_stream.stop()
	openni2.unload()
	cv2.destroyAllWindows()

if __name__ == '__main__':
    main()