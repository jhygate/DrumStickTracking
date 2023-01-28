import cv2
import cameraHelpers
from projectTypes import *
import numpy as np
from scipy.spatial import distance_matrix
import ClosedForm3D
import calibration
import unityStuff
import math
from threading import Thread

videoPath = 'Videos/ABOVETRIM.mp4'
calibrationPath = 'calibration.yml'
imageWidth = 500

CAM,DIST = calibration.load_coefficients(calibrationPath)

# redHSVRange = HSVRange(np.array([127,71,71]),np.array([255,255,255]))
redHSVRange = HSVRange(np.array([100,140,30]),np.array([140,250,255])) #above trim
# redHSVRange = HSVRange(np.array([50,50,0]),np.array([140,250,255]))


frameGenerator = cameraHelpers.getFrameGenerator(videoPath,calibrationPath,imageWidth)

frame = frameGenerator()
peaks = None
oldPeaks = None

from pydub import AudioSegment
from pydub.playback import play


def playSound():
    song = AudioSegment.from_wav('bassShort.wav')
    play(song)

stick = False
zdistsA = []
zdistsB = []
actualFrames = []
frameNum = 0

distRatios = []
while frame is not None:
    frameNum+=1
    redBlobs = cameraHelpers.getPossibleMarkers(frame,redHSVRange)
    lineSets = cameraHelpers.get_hough_sets(redBlobs,frame)
    print(len(lineSets))
    linesetFrame = cameraHelpers.draw_hough_sets(frame,lineSets)
    cv2.imshow('lineSets',linesetFrame)



    bestLine = None
    prevMSD = False
    for potentialLine in lineSets:
        #Set marker positions to stick if obviously good
        if cameraHelpers.check_for_good_stick(potentialLine):
            print("GOOD LINE FOUND")
            stick = potentialLine
            break

        #Distances between detected marker points and good stick found
        if not stick:
            break

        dist_mat = distance_matrix(potentialLine,stick)

        meanSquaredDistance = 0
        for rowNum in range(len(dist_mat)):
            markerIndex = np.argmin(dist_mat[rowNum])
            meanSquaredDistance += dist_mat[rowNum][markerIndex]**2
        meanSquaredDistance /= len(dist_mat[rowNum])

        #Save min MSD line
        if not prevMSD:
            bestLine = potentialLine
            prevMSD = meanSquaredDistance

        if meanSquaredDistance < prevMSD: #What about case where no lines are remotely good!
            bestLine = potentialLine
            prevMSD = meanSquaredDistance

        closePoints = [[] for i in range(7)]

        rowNum = 0
        for row in dist_mat:
            markerIndex = np.argmin(row)
            # print(markerIndex,rowNum)
            closePoints[markerIndex].append(bestLine[rowNum])
            rowNum+=1
            #


        #Set marker positions of all markers that are closest to only one prevmarker
        newMarkerPositions = [None]*7
        index = 0
        for pointList in closePoints:
            if len(pointList) == 1:
                newMarkerPositions[index] = pointList[0]
            index +=1

        indexVals = []
        positions = []
        for foundPointIndex in range(len(newMarkerPositions)):
            if newMarkerPositions[foundPointIndex] is not None:
                indexVals.append(foundPointIndex)
                positions.append(newMarkerPositions[foundPointIndex])

        ret,stick = cameraHelpers.getEstimatedPosition(indexVals,positions)

        for position in positions:
            cv2.circle(frame,position,5,(100,90,90),-1)

    if stick:
        cv2.line(frame,stick[0],stick[-1],(0,0,255),2)

        distRatios.append(math.dist(stick[0],stick[3])/math.dist(stick[3],stick[-1]))

    if stick:
        stick3D = stick.copy()
        stick3D = np.append(stick3D, np.array([[0,1]]*len(stick3D)), 1)

        pointA = stick3D[0]
        pointB = stick3D[3]
        pointC = stick3D[-1]
        focalPoint = np.array([CAM[0][2],CAM[1][2],1,1])
        

        M = ClosedForm3D.transformToXYPlane(pointA,pointB,pointC,focalPoint)
        points = np.array([pointA,pointB,pointC,focalPoint])
        points2D = ClosedForm3D.convertToPlanarXY(points,M)



        realPos2d = ClosedForm3D.getPoints(points2D[0],points2D[1],points2D[2],points2D[3])
        points3D = ClosedForm3D.convertPlanarToWorld(realPos2d,M)

        zdistsA.append(points3D[0][2])
        zdistsB.append(points3D[2][2])

        # print(points3D[0])
        # print(points3D[2])

        # unityStuff.send_to_unity(points3D[0],points3D[-1])
        
        for blob in redBlobs:
            cv2.circle(frame,blob,3,(100,40,70),-1)

        


    


    #Best line - average distance to closests marker is minimum
    #Pick three smallest 1-1 connections
    #quadRegression remaining points?
    


    cv2.imshow('frame',frame)
    q = cv2.waitKey(1)
    import matplotlib.pyplot as plt
    import scipy.signal

    try:
        peaks = np.ndarray.tolist(scipy.signal.find_peaks(distRatios,height=1.1)[0])
        # print(peaks,oldPeaks)
        if peaks != oldPeaks:
            print('NEWHIT')
            newThread =  Thread(target = playSound)
            newThread.start()
        # print(peaks)
        plt.scatter(peaks, [2]*len(peaks))
        oldPeaks = peaks
    except Exception as e:
        print(e)
    if peaks:
        plt.scatter(list(peaks), [2 for i in peaks])

    # plt.plot(list(range(len(distRatios))), distRatios)
    # plt.show(block=False)
    # plt.pause(0.5) 
    # plt.close()


    

    frame = frameGenerator()





    
