"""Stick finder
Returns each marker location if all markers are detected in an img


"""
import cameraHelpers
import numpy as np

def findStick(img,HSVRange,numMarkers=7):
    #Returns Ret,val pair
    #Ret - whether a good stick was found
    #Val - list of marker positions

    #Get centrePoints of all regions in HSVRange
    redBlobs = cameraHelpers.getPossibleMarkers(img,HSVRange)

    #Get array of possible lines
    #Each line is an array of HSVregion centres that fall on the same line
    lineSets = cameraHelpers.get_hough_sets(redBlobs,img)

    #Iterate through all lines of HSVregion centres until a successful stick found
    for line in lineSets:

        #If the wrong number of markers is detected check the next possible line
        #TODO - this is a bad hueristic, you should be able to find the good markers if there are extra points detected
        if len(line) != numMarkers:
            continue

        
        #Create quadRegression based on the first 3 markers
        #If all points on the stick fit the model, assume a stick has been found#
        #TODO - This is a greedy ugly method, maybe multiple lines are good, find best one, put thought into it

        threshold  = 30

        xPoints = [point[0] for point in line]
        yPoints = [point[1] for point in line]
        indices = list(range(0,numMarkers))

        modelx = np.poly1d(np.polyfit(indices[:3],
                            xPoints[:3], 2))

        modely = np.poly1d(np.polyfit(indices[:3],
                            yPoints[:3], 2))


        goodStick = True

        for index in indices[3:]:
            if not (cameraHelpers.withinRange(modelx(index),xPoints[index],threshold) and cameraHelpers.withinRange(modely(index),yPoints[index],threshold)):
                goodStick = False
                break
        if goodStick:
            return True,line
    return False, []