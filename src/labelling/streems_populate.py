#!/usr/bin/python

import MySQLdb
import os,sys
import numpy as np
import argparse
from primesense import openni2
import cv2
import csv
import datetime



# Open database connection
db=MySQLdb.connect(passwd="",db="reidentification",host="127.0.0.1",user="root")




def populate(video_path):
        """
        This script populates Video,Depth_Frame and RGB_frame tables
        @param video_path: contains the ONI file path
        """

        ##### obtains Video id ####################
        # preparing a cursor object
        cursor = db.cursor()
        query ="SELECT COUNT(*) from VIDEO"
        cursor.execute(query)             #executes query
        res=cursor.fetchone()
        total_rows=res[0]
        videoid=total_rows+1

        #query for VIDEO table####################

        query = """INSERT INTO VIDEO(VIDEOID,
         VIDEO)
         VALUES (%s, %s)"""
        video_data=(videoid,video_path)
        try:
           # Execute the SQL command
           cursor.execute(query,video_data)
           # Commit changes in the database
           db.commit()
        except:
           # Rollback in case there is any error
           db.rollback()

        ###########################################

        openni2.initialize()
        dev = openni2.Device.open_file(video_path)
        print (dev.get_sensor_info(openni2.SENSOR_DEPTH))
        depth_stream = dev.create_depth_stream()
        color_stream = dev.create_color_stream()
        depth_stream.start()
        color_stream.start()
        ##### getting first frame timestamp ##########################
        first_frame=depth_stream.read_frame()
        frame1_timestamp = datetime.datetime.fromtimestamp(float(first_frame.timestamp)/1000000.0  )

        ### we want to start counting from  2015-06-01 01:00:00 ####
        frame1_timestamp += datetime.timedelta(days=((365*45)+162))

        ##### initialize a frame counter and the variable flag  #########
        frameno = 0
        flag= False
        while True:




                frame_depth = depth_stream.read_frame()
                frame_color = color_stream.read_frame()

                frame_depth_data = frame_depth.get_buffer_as_uint16()
                frame_color_data = frame_color.get_buffer_as_uint8()

                depth_array = np.ndarray((frame_depth.height, frame_depth.width), dtype = np.uint16, buffer = frame_depth_data)
                color_array = np.ndarray((frame_color.height, frame_color.width, 3), dtype = np.uint8, buffer = frame_color_data)
                color_array = cv2.cvtColor(color_array, cv2.COLOR_BGR2RGB)

                depth_timestamp = datetime.datetime.fromtimestamp(float(frame_depth.timestamp)/1000000.0  )
                color_timestamp = datetime.datetime.fromtimestamp(float(frame_color.timestamp)/1000000.0  )
                depth_timestamp += datetime.timedelta(days=((365*45)+162))
                color_timestamp += datetime.timedelta(days=((365*45)+162))

                cv2.imshow("depth", depth_array)
                cv2.imshow("color", color_array)
                ##### counting frames #############
                frameno = frameno + 1



                #### this is for avoid that the video loops  ######
                if (frame1_timestamp == depth_timestamp and frameno != 1):
                    flag=True


                if (flag == False):
                    ### query for depth_frame table ####################
                    query_3 = """INSERT INTO DEPTH_FRAME(VIDEOID,FRAMENO,TIMESTAMP)
                    VALUES (%s, %s, %s)"""
                    depth_dbdata=(videoid,frameno,depth_timestamp)

                    ### query for rgb_frame table ####################
                    query_4 = """INSERT INTO RGB_FRAME(VIDEOID,FRAMENO,TIMESTAMP)
                    VALUES (%s, %s, %s)"""
                    rgb_dbdata=(videoid,frameno,color_timestamp)

                    try:
                       # Execute the SQL command
                       cursor.execute(query_3,depth_dbdata)
                       cursor.execute(query_4,rgb_dbdata)
                       # Commit changes in the database
                       db.commit()
                    except:
                       # Rollback in case there is any error
                       db.rollback()

                ch = 0xFF & cv2.waitKey(1)
                if (ch == 27 or flag == True):
                    break




        depth_stream.stop()
        color_stream.stop()
        openni2.unload()
        cv2.destroyAllWindows()




        # disconnect from server
        db.close()


def main():
        """The entry point"""
        p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
        p.add_argument('--v', dest = 'video_path', action = 'store', default = '', help = 'path file *.oni')
        args = p.parse_args()
        populate(args.video_path)

if __name__ == '__main__':
        main()
