#!/usr/bin/python

import MySQLdb
import os,sys
import numpy as np
import argparse
import csv
import string
import imp
import getpass


# Open database connection
db = MySQLdb.connect(passwd="", db="ReIdentification", host="127.0.0.1", user="")



def populate(file_name):
    """
    This script populates Person table.
     @param file_name: contains the id.csv file path
     @param path_to_ID: contains the path to the ID folder
    """

    ####getting person info #############
    with open(file_name, 'rb') as id_file:
        reader = csv.reader(id_file,delimiter=';')
        for row in reader:
            person_id=row[0]
            name = row[1]
            surname = row[2:]
            ###concatenates surname's strings #########
            surname = ' '.join( surname )


            path = '/home/user/ID/'+str(person_id)+'/gt/'
            os.chdir(path)
            with open('gt.csv', 'rb') as gt_file:
                reader = csv.reader(gt_file, delimiter=';')
                for row in reader:
                    height=int(row[0])
                    pelvis=int(row[1])
                    gender=row[2]
                    head_shoulder=int(row[3])
                    shoulder_widht=int(row[4])
                    shoulder_contour=int(row[5])
                    head_contour=int(row[6])
            gt_file.close()

            # prepare a cursor object using cursor() method
            cursor = db.cursor()

            #populates PERSON table####################
            sql = """INSERT INTO `Person`(`PersonId`, `Private_Name`, `Private_Surname`, `Private_Gender`, `Height`, `PelvisHeight`, `HeadShouldersDiff`, `ShouldersWidth`, `ShouldersContourLength`, `HeadContourLength`)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            data = (person_id, name, surname, gender, height, pelvis, head_shoulder, shoulder_widht, shoulder_contour, head_contour)
            print data
            try:
                # Execute the SQL command
                cursor.execute(sql, data)
                # Commit changes in the database
                db.commit()
            except:
                # Rollback in case there is any error
                db.rollback()
            ###########################################
            print person_id+" "+name+" "+surname+" || Saved in Person Table "
    id_file.close()
    db.close()

def main():
    """The entry point"""
    p = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description="")
    p.add_argument('--v', dest = 'file_name', action = 'store', default = './id.csv', help = 'path file id.csv')
    args = p.parse_args()
    populate(args.file_name)

if __name__ == '__main__':
    main()
