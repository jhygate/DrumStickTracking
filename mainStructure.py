import cv2
import cameraHelpers
from projectTypes import *
import numpy as np
import calibration
import stickFinder
import tracking
import markerDetection
import hitDetection
import drumCircleSelection
import sheetMusicGenerator
import signalProcessing

#LoadImage
videoPath = 'Videos/Above60BPM.MOV'
calibrationPath = 'calibration.yml'
imageWidth = 500

audioHits = signalProcessing.audio_hit_frames(videoPath)
print(audioHits)
maxFrame = max(audioHits)
frameVals = [[] for frame in range(maxFrame+1)]
for hit in audioHits:
    if frameVals[hit] == []:
        frameVals[hit].append('sn')
subHitList = sheetMusicGenerator.frameHitListToSubdivisionHitList(30,110,frameVals,8)
sheetMusicGenerator.createSnareMusic(subHitList,8)

#Load camera calibration
CAM,DIST = calibration.load_coefficients(calibrationPath)

#Assume set HSV range
markerHSVRange = HSVRange(np.array([100,140,30]),np.array([140,250,255]))

#Setup frames
frameGenerator = cameraHelpers.getFrameGenerator(videoPath,calibrationPath,imageWidth)
frame = frameGenerator()

drumCircles = drumCircleSelection.getDrumCircles(frame)
drumCircleSelection.viewDrumCircles(frame,drumCircles)


stickFound = False
goodStick = []

stickLocations = []
#Loop until video has ended
while frame is not None:

    #Look for stick if stick hasn't been found
    # if not stickFound:
    stickFound = False
    stickFound,stick = stickFinder.findStick(frame,markerHSVRange)
    if stickFound:
        goodStick = stick
    # If stick location was known the prev frame update its location
    if not stickFound and goodStick != []:
        stickTracked,stick = tracking.noHoughTracking(frame,goodStick,markerHSVRange)
        print(stickTracked,stick)
        if stickTracked:
            goodStick = stick

        #TODO how to deal with no stick found, what is recorded (consider scipy.findpeaks)
        stickLocations.append(goodStick)
        #update markers based on prev info

    #Check for audio hit
        #find drum stick is closest to and record

    
    ##Visualise red blobs
    redBlobs = markerDetection.getPossibleMarkers(frame,markerHSVRange)

    for point in goodStick:
        cv2.circle(frame,point,5,(0,255,255),-1)

    
    for point in redBlobs:
        cv2.circle(frame,point,2,(255,255,0),-1)

    

    #Show frame
    cv2.imshow('video',frame)
    cv2.waitKey(1)

    #Get new frame
    frame = frameGenerator()


hits = hitDetection.getHitsFromSticks(stickLocations,drumCircles)

subHitList = sheetMusicGenerator.frameHitListToSubdivisionHitList(30,110,hits,16)
sheetMusicGenerator.createSnareMusic(subHitList,16)

print(hits)
#Convert hits to pdf + display
#(Optionally convert hits to MIDI)
        

