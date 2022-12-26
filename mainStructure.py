import cv2
import cameraHelpers
from projectTypes import *
import numpy as np
import calibration
import stickFinder
import tracking


#LoadImage
videoPath = 'Videos/ABOVEHIHAT.mp4'
calibrationPath = 'calibration.yml'
imageWidth = 500

#Load camera calibration
CAM,DIST = calibration.load_coefficients(calibrationPath)

#Assume set HSV range
markerHSVRange = HSVRange(np.array([127,71,71]),np.array([255,255,255]))

#Setup frames
frameGenerator = cameraHelpers.getFrameGenerator(videoPath,calibrationPath,imageWidth)
frame = frameGenerator()


stickFound = False

#Loop until video has ended
while frame is not None:

    #Look for stick if stick hasn't been found in the prev frame
    if not stickFound:
        stickFound,stick = stickFinder.findStick(frame,markerHSVRange)
      

    #If stick location was known the prev frame update its location
    else:
        stickFound,stick = tracking.findNewMarkers(frame,stick,markerHSVRange)
        #update markers based on prev info

    redBlobs = cameraHelpers.getPossibleMarkers(frame,markerHSVRange)
    for blob in redBlobs:
        cv2.circle(frame,blob,5,(100,90,90),-1)

    lineSets = cameraHelpers.get_hough_sets(redBlobs,frame)
    for line in lineSets:
        cv2.line(frame,line[0],line[-1],(255,255,255),1)

    if stickFound:
        for position in stick:
            cv2.circle(frame,position,5,(255,30,30),-1)




    #Show frame
    cv2.imshow('video',frame)
    cv2.waitKey(0)

    #Get new frame
    frame = frameGenerator()

        

