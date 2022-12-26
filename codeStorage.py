"""
Tracking

Detect all markers with initial HSV range
(merge all that fall withing flood fill?)

Detecting markers contours:
-Flood fill each detected
-Combine markers with overlappping flood fill
-What HSV range to use, HSV range for each marker, search multiple times? ahhhh



Find all lines

-Create a list of potential lines (3+ markers that fit quad regression), order by number of markers, mean**2 dist from quad regression
-Check each line for succesfull quad regression points - best line is min mean**2 dist


^^usefull for initial line detection

Line tracking
-Same as finding initial lines, but best line takes hueristic of closeness of previous marker 


THRESHOLD needed to determine line not found/lost

Issues
-How to deal with wrong marker being found, throwing off future guesses
-How to deal with marker in fornt of its colour
    -Too large marker, assume 1+ markers may be hidden inside of (check if quad regression fits with others detected)



CHECK MARKERS ARE RIGHT SHAPE TO ADJUST FLOOD FILL THRESH

"""

from  cameraHelpers import *
import cv2
from copy import deepcopy

def find_exterior_contours(img):
    ret = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(ret) == 2:
        return ret[0]
    elif len(ret) == 3:
        return ret[1]
    raise Exception("Check the signature for `cv.findContours()`.")



def getMarkerList(image,HSVRange):
    #Return list of marker contours
    #Try multiple methods
    threshed = getColourMask(image,HSVRange)
    cnts = cv2.findContours(threshed, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2]
    return cnts

img = cv2.imread("CalibrationImages/95.jpg")
img = cv2.resize(img,(500,500))
markerHSVRange = HSVRange(np.array([127,71,71]),np.array([255,255,255]))

markerContours = getMarkerList(img,markerHSVRange)

centres = getPossibleMarkers(img,markerHSVRange)


cnts = []



imgCpy = img.copy()




h,w = img.shape[:2]

flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)


floodMasks = []


for centreIndex,centre in enumerate(centres):
    flood_mask[:] = 0
    tolVal = 40

    tolerance =(tolVal,tolVal,tolVal)
    connectivity = 4
    flood_fill_flags = (
            connectivity | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | 255 << 8
        )


    cv2.floodFill(
            img,
            flood_mask,
            centre,
            0,
            tolerance,
            tolerance,
            flood_fill_flags,
        )
    mask = flood_mask[1:-1, 1:-1].copy()

    
    oldFloodMasks = deepcopy(floodMasks)


    combinedMask = False

    for oldMaskIndex, oldMask in enumerate(oldFloodMasks):
        overlapArea = cv2.countNonZero(cv2.bitwise_and(oldMask,mask))
        if overlapArea > 0:
            floodMasks[oldMaskIndex] = cv2.bitwise_or(oldMask,mask)
            combinedMask = True
            break

    if not combinedMask:
        floodMasks.append(mask)     



# cv2.drawContours(img,cnts,-1,(255,255,255),-1)

# niceImg = cv2.bitwise_and(img,img,mask=mask)

for mask in floodMasks:
    thresh = 1000
    cnt = cv2.findContours(mask, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2][0]
    # if cnt.area > thresh:
    #     break

    centre = get_cnt_centre(cnt)

    cv2.drawContours(img,[cnt],-1,(255,255,255),-1)
    

    # cv2.imshow('markers',cv2.bitwise_and(img,img,mask=mask))
    # cv2.waitKey(0)

cv2.imshow('markers',img)
cv2.waitKey(0)




