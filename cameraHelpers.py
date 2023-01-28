from typing import Union,List,Callable
import cv2
import numpy as np
import calibration
from projectTypes import *
import math




def getFrameGenerator(videoPath:str,calibrationPath:str,imageWidth:int) -> Callable:
    cap = cv2.VideoCapture(videoPath)
    CAM,DIST = calibration.load_coefficients(calibrationPath)

    def frameGenerator() -> Union[np.ndarray,None]:
        ret, frame = cap.read()
        if frame is not None:
            frame = cv2.undistort(frame,CAM,DIST)#Undistort

            w ,h = frame.shape[0],frame.shape[1] #Resize to width with Aspect Ratio
            sf = imageWidth/w
            dim = [int(h*sf),int(w*sf)]
            frame = cv2.resize(frame,dim)
            return frame
        return None

    return frameGenerator

def getPossibleMarkers(frame:np.ndarray ,HSVrange:HSVRange) -> List[List[int]]:
    threshed = getColourMask(frame,HSVrange)
    cnts = cv2.findContours(threshed, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2]

    posMarkerPoints = []
    for cnt in cnts:
        posMarkerPoints.append(get_cnt_centre(cnt))
    
    return posMarkerPoints



def getColourMask(frame:np.ndarray ,HSVrange:HSVRange) -> np.ndarray:

    KERNEL = np.ones((5,5),np.uint8)
    hsvframe = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    threshed = cv2.inRange(hsvframe, HSVrange.lower, HSVrange.upper)
    threshed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, KERNEL)
    threshed = cv2.morphologyEx(threshed, cv2.MORPH_OPEN, KERNEL)
    threshed = cv2.dilate(threshed,KERNEL,iterations=1)


    return threshed

def get_cnt_centre(cnt:np.ndarray) -> List[int]:
    M = cv2.moments(cnt)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return [cX,cY]
    return [0,0]

def get_hough_sets(markerPoints:list,frame:np.ndarray) -> List[List[List[int]]]:
    #INEFFICENT FUNCTION WORKS FOR NOW TODO

    #Add points to blank image
    blank_image = np.zeros((frame.shape[0],frame.shape[1],1), np.uint8)
    for marker in markerPoints: 
        cX,cY = marker
        blank_image[cY][cX] = 255
    


    lines = cv2.HoughLines(blank_image, 2, np.pi/180,3)
    
    if lines is not None:
        print('len lines',len(lines))
    else:
        print('Hough lines in None')

    lineSets = []
    if lines is not None:
        for r_theta in lines:
            arr = np.array(r_theta[0], dtype=np.float64)
            rho, theta = arr
            closePoints = getPointsCloseToLine(rho,theta,5,markerPoints)
            if len(closePoints)>=1:
                potLine = []
                for point in closePoints:
                    point=list(point)
                    potLine.append(point)
                lineSets.append(potLine)
    return lineSets


def draw_hough_sets(frame,lineSets):
    for line in lineSets:
        cv2.line(frame,line[0],line[-1],(200,90,255),2)
    return frame

def getPointsCloseToLine(rho:float,theta:float,distance:float,points:List[List[int]]) -> List[List[int]]:
    if theta != 0:
        p1 = [0,rho/math.sin(theta)]
        p2 =[1000,(rho-1000*math.cos(theta))/math.sin(theta)]
        

        pt1 = np.asarray(p1)
        pt2 = np.asarray(p2)
        pt3 = np.asarray(points)

        d=np.cross(pt2-pt1,pt3-pt1)/np.linalg.norm(pt2-pt1)
        npPoints = np.asarray(points)

        indices = np.where(abs(d)<distance)
        if len(indices) == 0:
            return []
        closePoints = npPoints[indices]
        return closePoints
    return []


def check_for_good_stick(line):
    goodStick = False
    if len(line) == 7:
        xPoints = [point[0] for point in line]
        yPoints = [point[1] for point in line]
        indices = list(range(0,7))

        modelx = np.poly1d(np.polyfit(indices[:3],
                            xPoints[:3], 2))

        modely = np.poly1d(np.polyfit(indices[:3],
                            yPoints[:3], 2))

        threshold  = 30

        goodStick = True

        for index in indices[3:]:
            if not (withinRange(modelx(index),xPoints[index],threshold) and withinRange(modely(index),yPoints[index],threshold)):
                goodStick = False
                break
        return goodStick

def withinRange(value,target,threshold):
    if abs(target -value) < threshold:
        return True
    else:
        return False

def closest_point_on_line(model, point):
    line_pt1 = [0,model(0)]
    line_pt2 = [1,model(1)]
    line_vec = np.subtract(line_pt2, line_pt1)
    point_vec = np.subtract(point, line_pt1)
    line_unit_vec = line_vec / np.linalg.norm(line_vec)
    point_on_line = np.dot(point_vec, line_unit_vec) * line_unit_vec
    closest_point = np.add(line_pt1, point_on_line)
    return closest_point

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def getEstimatedPosition(indices,points):
    #Given indices (x val) and points (2D y val) find the points that best match the curve
    #to ensure curve is a straight line, find MSD line to all points given, and translate points to their closest point on  the line
    # try:

    try:
        xPoints = [point[0] for point in points]
        yPoints = [point[1] for point in points]

        modelx = np.poly1d(np.polyfit(indices,
                            xPoints, 1))

        modely = np.poly1d(np.polyfit(indices,
                            yPoints, 1))

        estimatedPosition = []
        for markerIndex in range(7):
            x,y = modelx(markerIndex),modely(markerIndex)
            estimatedPosition.append([int(x),int(y)])
            
        print(estimatedPosition,'estpos')
        return True,estimatedPosition
    except:
        return False,[]


    # pt0 = [0,modelLinear(0)]
    # pt1 = linePoints[0]

    # directionVector = normalize(np.subtract(pt1,pt0))
    # print(directionVector)

    # lineDists = [np.divide(np.subtract(point,pt0)[0],directionVector[0]) for point in linePoints]
    # print(lineDists,'lineDists')

    # modelQuad = np.poly1d(np.polyfit(indices,
    #                         lineDists, 2))

    # estimatedPosition = []
    # for i in range(7):
    #     pos = np.subtract(pt0,np.multiply(directionVector,modelQuad(i)))
    #     x = int(pos[0])
    #     y= int(pos[1])
    #     estimatedPosition.append([x,y])
    # print(estimatedPosition,'estPos')
    # return True,estimatedPosition
    # # except:
    # #     return False,[]










    try:
        xPoints = [point[0] for point in points]
        yPoints = [point[1] for point in points]

        modelx = np.poly1d(np.polyfit(indices,
                            xPoints, 2))

        modely = np.poly1d(np.polyfit(indices,
                            yPoints, 2))

        estimatedPosition = []
        for markerIndex in range(7):
            if markerIndex not in indices:
                x,y = modelx(markerIndex),modely(markerIndex)
                estimatedPosition.append([int(x),int(y)])
            else:
                estimatedPosition.append(points[indices.index(markerIndex)])
        return True,estimatedPosition
    except:
        return False,[]


