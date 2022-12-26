"""Code to find marker locations based on knowledge of previous locations"""

from scipy.spatial import distance_matrix
import cameraHelpers
import numpy as np

def findNewMarkers(img,prevStick,HSVRange):
    #V1 return ret, stick

    #TODO - find through experimentation
    MSDThresh = 10000000000000000000000000000000


    #Get centrePoints of all regions in HSVRange
    redBlobs = cameraHelpers.getPossibleMarkers(img,HSVRange)

    #Get array of possible lines
    #Each line is an array of HSVregion centres that fall on the same line
    lineSets = cameraHelpers.get_hough_sets(redBlobs,img)

    if len(lineSets) == 0:
        print('No hough sets')
        return False,[]

    bestLine = []
    prevMSD = 99999999999999999

    for potentialLine in lineSets:

        #Find distance from each marker in potential line to each marker in the stick
        dist_mat = distance_matrix(potentialLine,prevStick)


        meanSquaredDistance = 0

        #Using the potenital marker closest to the prev found marker
        #find the total meanSquaredDist of the new markers from old markers
        for rowNum in range(len(dist_mat)):
            #index of new potential marker
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


    if prevMSD > MSDThresh:
        print('MSD TOO HIGH')
        return False,[]

    if not bestLine:
        print('')

    closePoints = [[] for i in range(7)]


    dist_mat = distance_matrix(bestLine,prevStick)
    #Create list of potenital markers that are closest to each marker
    for rowNum,row in enumerate(dist_mat):
        markerIndex = np.argmin(row)
        closePoints[markerIndex].append(bestLine[rowNum])
        


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
    

    return cameraHelpers.getEstimatedPosition(indexVals,positions)


        

