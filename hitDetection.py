"""Functions for detecting if ans where a hit has taken place
Visual methods - Using marker location info
Audio methods - Using signal processing
"""
import math
import numpy as np
import scipy.signal

def inDrum(drum,location):
    #Returns True if a given location is within a given drums circle
    if (location[0] - drum.centre[0])**2 + (location[1] - drum.centre[1])**2 < drum.radius**2:
        return True
    else:
        return False
    


#Each frame query wheter the frame determines a hit... (doesnt work with peaks method, need to assign a hit slightly in the past)
#Find peaks is fast, MVP return all hits 
def getHitsFromSticks(stickLocations,drumCircles):
    #Calulate the ratio between distance between each end and the midpoint
    #Assign a hit to a frame if peak in ratio (e.g stick changes angle) AND over drum
    #Knowledge about hit end is needed!
    #TODO - either use coloured marker to track end OR track end moving fastest

    distRatios = []
    for stick in stickLocations:
        distRatios.append(math.dist(stick[0],stick[3])/math.dist(stick[3],stick[-1]))
        peaks = np.ndarray.tolist(scipy.signal.find_peaks(distRatios,height=1.1)[0])
    
    hits = [[] for stick in stickLocations] #TODO make this range(len())

    #TODO ugly refactor
    for peak in peaks:
        hitFound = False
        for marker in stickLocations[peak]:
            if hitFound:
                break
            for drum in drumCircles:
                if inDrum(drum,marker):
                    hits[peak].append(drum.notation)
                    hitFound = True
                    break
    return hits