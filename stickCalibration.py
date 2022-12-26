"""Define a function -
- Give a set of calibration images
- Label all markers
- find HSV range such that number of good marker detections is maximized

Used for:
-Setting initial values for tracker before transcription


Possible implementations:

-Find each region, colour fill (photoshop magic wind, flood fill) from clicking on centre, human verify
Technique for filling regions

-Gradient decent:
    Maximize masked pixels in regions, minimize masked pixels outside 


is HSV the best metric for finding regions in tracking - YES!!
we dont need to detect blobs fully just as much as possible, its better to get some of a marker and reject false detecions
Tracking should update HSV range (ASK GREEK LADY)





GOOD ACCURACY FUNCTION NEEDED!!
AIM:
-Each marker must be detected so that it can be tracked
(we need a seperate fitness function for each marker, if number of pixels frop to 0, whole fitness = 0)
-Non marker pixels must be minimal

We want all markers to be detected:
starting HSV range gives initial state, if three markers can be found then whole stick can

dream:
hold stick up (horizontal i guess) auto detect colour range in skeleton format, find markers, find colour range bish bash bosh
method:

EZ solution: hold up in correct pos, check markers pos, find values






Tracker - HSV range for each marker, HSV range is updated with each frame
    Therefore individual HSV selection for each marker! simplified problem yaaaaaaaay
WRONG, stick will have moved after marker selection

multiHSV tracker seems complex:
-find all points with markers HSV, apply floodfill, get HSV range for marker
-searchHSV range, how does it change? caluculate HSV velocity for each component etc



PLAN:
magic method to find HSV of each marker
Find intersection of all marker HSV ranges, thats your base HSV range


floodfill is freind for tracking

"""

import cv2
from cameraHelpers import *

from magicwand import SelectionWindow
 
img = cv2.imread("CalibrationImages/50.jpg")
img = cv2.resize(img,(600,600))
window = SelectionWindow(img)
markerMasks = window.show()

print(cv2.countNonZero(markerMasks))

def getAccuracy(img,masks,hsvRange):
    #Return correctlyClassifiedPixels - wronglyClassifiedPixels
    #Best huersitic?

    hsvMask = getColourMask(img,hsvRange)
    maskOverlap = cv2.bitwise_and(masks,hsvMask)
    wrongHsvMask = cv2.bitwise_and(hsvMask,cv2.bitwise_not(masks))
    correctPixels = cv2.countNonZero(maskOverlap)
    wrongPixels = cv2.countNonZero(wrongHsvMask)


    


    return correctPixels


bottomHSV = [0,0,0]
upperHSV = [255,255,255]


for bottomIndex in range(3):
    increasingAccuracy = True
    prevAccuracy = float('-inf')
    while increasingAccuracy:
        hsvRange = HSVRange(np.array(bottomHSV),np.array(upperHSV))
        accuracy = getAccuracy(img,markerMasks,hsvRange)
        print(accuracy,bottomHSV)
        if accuracy < prevAccuracy:
            increasingAccuracy = False
            bottomHSV[bottomIndex] -= 2
        if bottomHSV[bottomIndex] >= 255:
            increasingAccuracy = False
        prevAccuracy = accuracy
        bottomHSV[bottomIndex] += 1

        print(bottomHSV)

for upperIndex in range(3):
    increasingAccuracy = True
    prevAccuracy = float('inf')
    while increasingAccuracy:
        hsvRange = HSVRange(np.array(bottomHSV),np.array(upperHSV))
        accuracy = getAccuracy(img,markerMasks,hsvRange)
        if accuracy < prevAccuracy:
            increasingAccuracy = False
            upperHSV[upperIndex] += 2
        if upperHSV[upperIndex] >= 255:
            increasingAccuracy = False
        prevAccuracy = accuracy
        bottomHSV[bottomIndex] -= 1

        print(bottomHSV)

hsvRange = HSVRange(np.array(bottomHSV),np.array(upperHSV))
print(bottomHSV,upperHSV)
hsvMask = getColourMask(img,hsvRange)
cv2.imshow('test',cv2.bitwise_and(img,img,mask=hsvMask))
cv2.waitKey(0)














def saveVideoFrames(path):
    # Opens the Video file
    cap= cv2.VideoCapture(path)
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break


        cv2.imshow('image',frame)
        key = cv2.waitKey(0)

        if key == ord('s'):
            cv2.imwrite('CalibrationImages/'+str(i)+'.jpg',frame)

        if key == ord('q'):
            break
        

        
        
        i+=1
    
    cap.release()
    cv2.destroyAllWindows()




