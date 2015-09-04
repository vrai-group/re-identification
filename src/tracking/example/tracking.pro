QT       += core

QT       -= gui

TARGET = tracking
CONFIG   += c++11

CONFIG   -= app_bundle

TEMPLATE = app


SOURCES += main.cpp


LIBS    += -lopencv_core -lopencv_imgproc -lopencv_ml -lopencv_video -lopencv_features2d -lopencv_calib3d -lopencv_objdetect -lopencv_contrib -lopencv_legacy -lopencv_flann -lopencv_highgui -lOpenNI2
