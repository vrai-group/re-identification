#!/usr/bin/python

import MySQLdb
import os,sys
import numpy as np
import argparse
from primesense import openni2
import cv2
import csv


# Open database connection
db=MySQLdb.connect(passwd="",db="reidentification",host="127.0.0.1",user="root")




def populate(video_name):
        """
        Populates Video and Person tables
        """
        #####obtains Video id####################
        # prepare a cursor object using cursor() method
        cursor = db.cursor()
        query ="SELECT COUNT(*) from VIDEO"
        cursor.execute(query)             #execute query separately
        res=cursor.fetchone()
        total_rows=res[0]
        videoid=total_rows+1
        #populates VIDEO table####################
        sql = """INSERT INTO VIDEO(VIDEOID,
         VIDEO)
         VALUES (%s, %s)"""
        data=(videoid,video_name)

        try:
           # Execute the SQL command
           cursor.execute(sql,data)
           # Commit your changes in the database
           db.commit()
        except:
           # Rollback in case there is any error
           db.rollback()
        ###########################################
        person_id=video_name[:-4]
        ####getting person info #############
        with open('id.csv', 'rb') as gt_file:
                reader = csv.reader(gt_file,delimiter='\t')
                for row in reader:
                   if row[0]== person_id :
                           name = row[1]
                           surname = row[2:]
        gt_file.close()
        ###checking if surname has two words #########
        if (len(surname) == 1):
                 surname = surname[0]
        else:
                 surname = surname[0]+' '+surname[1]

        with open('gt.csv', 'rb') as gt_file:
                reader = csv.reader(gt_file,delimiter=';')
                for row in reader:
                  height=int(row[0])
                  pelvis=int(row[1])
                  gender=row[2]
                  head_shoulder=int(row[3])
                  shoulder_widht=int(row[4])
                  shoulder_contour=int(row[5])
                  head_contour=int(row[6])
        gt_file.close()
        #populates PERSON table####################
        sql = """INSERT INTO PERSON(PERSONID,PRIVATE_NAME,PRIVATE_SURNAME,PRIVATE_GENDER,HEIGHT,PELVISHEIGHT,HEADSHOULDERSDIFF,
                SHOULDERSWIDTH,SHOULDERSCONTOURLENGTH,HEADCONTOURLENGTH)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        data = (person_id,name,surname,gender,height,pelvis,head_shoulder,shoulder_widht,shoulder_contour,head_contour)
        try:
           # Execute the SQL command
           cursor.execute(sql,data)
           # Commit your changes in the database
           db.commit()
        except:
           # Rollback in case there is any error
           db.rollback()
        ###########################################
        db.close()


def main():
        """The entry point"""
        p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="")
        p.add_argument('--v', dest = 'video_name', action = 'store', default = '', help = 'path file *.oni')
        args = p.parse_args()
        populate(args.video_name)

if __name__ == '__main__':
        main()
