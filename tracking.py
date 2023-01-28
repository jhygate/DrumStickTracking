"""Code to find marker locations based on knowledge of previous locations"""

from scipy.spatial import distance_matrix
import cameraHelpers
import markerDetection
import numpy as np

def findKnownMarkers(prevStick,blobs):
    #Returns List[markerIndex],List[blob]
    #Gives the blobs and their related marker indices

    stickBlobDists = distance_matrix(prevStick,blobs)

    #Maps blobIndex to marker indices
    blobMarkerIndexDict = {}
    for prevMarkerIndex,prevStickMarker in enumerate(stickBlobDists):
        minBlobIndex = np.argmin(prevStickMarker)
        if minBlobIndex in blobMarkerIndexDict:
            blobMarkerIndexDict[minBlobIndex].append(prevMarkerIndex)
        else:
            blobMarkerIndexDict[minBlobIndex] = [prevMarkerIndex]
    
    print(blobMarkerIndexDict,'dict')


    goodBlobs = []
    stickMarkerIndices = []

    for blobIndex,markerIndices in blobMarkerIndexDict.items():
        markerIndex = min(markerIndices,key=lambda markerIndex:np.linalg.norm(np.subtract(prevStick[markerIndex],blobs[blobIndex])))
        blob = blobs[blobIndex]
        goodBlobs.append(blob)
        stickMarkerIndices.append(markerIndex)

    
    return stickMarkerIndices,goodBlobs


def closest_point_on_line(model, point):
    line_pt1 = [0,model(0)]
    line_pt2 = [1,model(1)]
    line_vec = np.subtract(line_pt2, line_pt1)
    point_vec = np.subtract(point, line_pt1)
    line_unit_vec = line_vec / np.linalg.norm(line_vec)
    point_on_line = np.dot(point_vec, line_unit_vec) * line_unit_vec
    closest_point = np.add(line_pt1, point_on_line)
    return closest_point

def getStraightenedMarkers(points):
    #Given a list of points
    #returns the list of points translated onto their line of bets fit

    xPoints = [point[0] for point in points]
    yPoints = [point[1] for point in points]
    modelLinear = np.poly1d(np.polyfit(xPoints,
                            yPoints, 1))



    linePoints = [closest_point_on_line(modelLinear,point) for point in points]

    return linePoints



    






    



def noHoughTracking(img, prevStick,HSVRange):
    #Get centrePoints of all regions in HSVRange
    redBlobs = markerDetection.getPossibleMarkers(img,HSVRange)

    markerIndices,goodBlobs = findKnownMarkers(prevStick,redBlobs)
    goodBlobs = getStraightenedMarkers(goodBlobs)
    if len(goodBlobs) < 3:
        return False, []



    # dist_mat = distance_matrix(prevStick,redBlobs)

    # closestMarkers = []

    # for prevMarkerIndex,prevStickMarker in enumerate(dist_mat):
    #     minBlobIndex = np.argmin(prevStickMarker)
    #     closestMarkers.append((prevMarkerIndex,minBlobIndex,prevStickMarker[minBlobIndex]))

    # sortedClosestMarkers = sorted(closestMarkers,key=lambda data:data[2])

    # bestMapping = sortedClosestMarkers
    # print(bestMapping)

    # indexVals = [mapping[0] for mapping in bestMapping]
    # positions = [redBlobs[mapping[1]] for mapping in bestMapping]
    # print(positions)
    return cameraHelpers.getEstimatedPosition(markerIndices,goodBlobs)




    #for each prevStick: (closestBlobIndex, dist)
    #Output: 3 * (prevstickIndex,redBlobIndex)

    


def findNewMarkers(img,prevStick,HSVRange):
    #V1 return ret, stick

    #TODO - find through experimentation
    MSDThresh = 10000000000000000000000000000000


    #Get centrePoints of all regions in HSVRange
    redBlobs = markerDetection.getPossibleMarkers(img,HSVRange)

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


        

