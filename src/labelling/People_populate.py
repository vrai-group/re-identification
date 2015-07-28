#!/usr/bin/python

import MySQLdb
import csv


# Open database connection
db=MySQLdb.connect(passwd="",db="reidentification",host="127.0.0.1",user="root")




def populate(depth_file,color_file):
        """
        This script populates People_in_depth_frame and People_in_rgb_frame tables.
         @param depth_file: contains the depth.csv file name
         @param depth_file: contains the depth.csv file name
        """

        ####getting depth_file info #############
        with open(depth_file, 'rb') as d_file:
                reader = csv.reader(d_file,delimiter=';')
                for row in reader:
                            video_id= int(row[0])
                            person_id = row[1]
                            frame_num = int(row[2])
                            z = row[4]
                            x= row[5]
                            y = row[6]

                            if (person_id!='NULL'):
                                person_id=int(person_id)
                                # prepare a cursor object using cursor() method
                                cursor = db.cursor()

                                #populates PEOPLE_IN_DEPTH_FRAME table####################
                                sql = """INSERT INTO PEOPLE_IN_DEPTH_FRAME(VIDEOID,PERSONID,FRAMENO,MAXIMUMHEIGHT,MH_X,MH_Y)
                                 VALUES (%s,%s,%s,%s,%s,%s)"""
                                data = (video_id,person_id,frame_num,z,x,y)
                                try:
                                   # Execute the SQL command
                                   cursor.execute(sql,data)
                                   # Commit changes in the database
                                   db.commit()
                                except:
                                   # Rollback in case there is any error
                                   db.rollback()

        d_file.close()
        print "depth file loaded"
        ####getting color_file info #############
        with open(color_file, 'rb') as c_file:
                reader = csv.reader(c_file,delimiter=';')
                for row in reader:
                            video_id= int(row[0])
                            person_id = row[1]
                            frame_num = int(row[2])

                            if (person_id!='NULL'):
                                person_id=int(person_id)
                                # prepare a cursor object using cursor() method
                                cursor = db.cursor()

                                #populates PEOPLE_IN_RGB_FRAME table####################
                                sql = """INSERT INTO PEOPLE_IN_RGB_FRAME(VIDEOID,PERSONID,FRAMENO)
                                 VALUES (%s,%s,%s)"""
                                data = (video_id,person_id,frame_num)
                                try:
                                   # Execute the SQL command
                                   cursor.execute(sql,data)
                                   # Commit changes in the database
                                   db.commit()
                                except:
                                   # Rollback in case there is any error
                                   db.rollback()

        c_file.close()
        print "color file loaded"
        db.close()

def main():
        """The entry point"""
        depth_file= raw_input('Write the name of the depth file(ex.001_depth.csv): ')
        color_file= raw_input('Write the name of the color file(ex.001_color.csv): ')
        populate(depth_file,color_file)

if __name__ == '__main__':
        main()
