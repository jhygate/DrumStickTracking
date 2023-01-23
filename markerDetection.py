"""Functions used for detecting potential stick markers"""
import numpy as np
import cv2

def getColourMask(frame,HSVrange):
    #Given a HSVrange return a mask of pixels that are withing the range
    #Apply closure and opening to improve marker detection
    #TODO experiment on morphology 

    KERNEL = np.ones((5,5),np.uint8)
    hsvframe = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    threshed = cv2.inRange(hsvframe, HSVrange.lower, HSVrange.upper)
    threshed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, KERNEL)
    threshed = cv2.morphologyEx(threshed, cv2.MORPH_OPEN, KERNEL)
    threshed = cv2.dilate(threshed,KERNEL,iterations=1)

    return threshed

def get_cnt_centre(cnt):
    #Returns the centre of a contour
    M = cv2.moments(cnt)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return [cX,cY]
    return [0,0]

def floodFillMask(frame,floodCentre,toleranceVal=32):
    #Returns a mask of pixels that flood fill thinks is part of the same region

    h,w = frame.shape[:2]

    flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)

    tolerance =(toleranceVal,) * 3
    connectivity = 4
    flood_fill_flags = (
            connectivity | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | 255 << 8
        )


    cv2.floodFill(
            frame,
            flood_mask,
            floodCentre,
            0,
            tolerance,
            tolerance,
            flood_fill_flags,
        )
    mask = flood_mask[1:-1, 1:-1].copy()
    return mask

def getPossibleMarkers(frame,HSVRange):
    #return a list of HSV region contours
    threshed = getColourMask(frame,HSVRange)
    cnts = cv2.findContours(threshed, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2]

    # floodMasks = []
    # for cnt in cnts:
    #     cntCentre = get_cnt_centre(cnt)
    #     floodMask = floodFillMask(frame,cntCentre,toleranceVal=10)

    #     oldFloodMasks = floodMasks.copy()
    #     combinedMask = False
    #     for oldMaskIndex, oldMask in enumerate(oldFloodMasks):
    #         overlapArea = cv2.countNonZero(cv2.bitwise_and(oldMask,floodMask))
    #         if overlapArea > 0:
    #             floodMasks[oldMaskIndex] = cv2.bitwise_or(oldMask,floodMask)
    #             combinedMask = True
    #             break

    #     if not combinedMask:
    #         floodMasks.append(floodMask)     
    
    # posMarkerPoints = []

    # for mask in floodMasks:
    #     cnt = cv2.findContours(mask, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2][0]
    #     centre = get_cnt_centre(cnt)

    #     posMarkerPoints.append(centre)

    posMarkerPoints = []

    for cnt in cnts:
        # cnt = cv2.findContours(mask, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2][0]
        centre = get_cnt_centre(cnt)
        posMarkerPoints.append(centre)

    
    
    return posMarkerPoints