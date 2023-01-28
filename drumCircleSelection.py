"""Iniitial setup of drums from camera, find hough circles and assign their relevent drum


Pehaps for MVP, user defined circles"""


import numpy as np
import cv2
from projectTypes import *
# img = cv2.imread('CalibrationImages/95.jpg',0)
# img = cv2.medianBlur(img,5)
# cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
# circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,500,
#                             param1=40,param2=30,minRadius=100,maxRadius=300)
# circles = np.uint16(np.around(circles))
# for i in circles[0,:]:
#     # draw the outer circle
#     cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
#     # draw the center of the circle
#     cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
# cv2.imshow('detected circles',cimg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


def getDrumCircles(img):
    #Return a list of drumCircle type
    #TODO atm all are sn, add user custom stuff
    drumCircles = []

    cimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(cimg,cv2.HOUGH_GRADIENT,1,500,
                                param1=40,param2=30,minRadius=100,maxRadius=300)
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

        drum = drumCircle((i[0],i[1]),i[2],'sn')
        drumCircles.append(drum)
    return drumCircles

def viewDrumCircles(img,drumCircles):
    for circle in drumCircles:
        cv2.circle(img,circle.centre,circle.radius,[100,50,30],2)

    cv2.imshow('circles',img)
    cv2.waitKey(0)

class SelectionWindow:
    def __init__(self, img, name="Drum selector", connectivity=4, tolerance=32):
        self.name = name
        h, w = img.shape[:2]
        self.img = img

        self.point1 = None
        self.radius = None

        cv2.namedWindow(self.name)
        
        cv2.setMouseCallback(self.name, self._mouse_callback)





    def _mouse_callback(self, event, x, y, flags, *userdata):
        

        if event != cv2.EVENT_LBUTTONDOWN:
            return

        if not self.point1:
            self.point1 = (x,y)
            self.img = cv2.circle(self.img,self.point1,2,(255,255,255),-1)
        elif not self.radius:
            point2 = (x,y)
            self.radius = int(np.linalg.norm(np.subtract(self.point1,point2)))
            self.img = cv2.circle(self.img,self.point1,self.radius,(255,255,255),2)


        self._update()




    def _update(self):
        """Updates an image in the already drawn window."""
        viz = self.img.copy()
        
        cv2.imshow(self.name, viz)
        # cv2.displayStatusBar(self.name, ", ".join((meanstr, stdstr)))

    def show(self):
        """Draws a window with the supplied image."""
        self._update()
        print("Press [q] or [esc] to close the window.")
        while cv2.getWindowProperty('Drum selector', cv2.WND_PROP_VISIBLE) > 0:
            k = cv2.waitKey(1) & 0xFF

            if self.point1 and self.radius:
                cv2.destroyWindow(self.name)
                return self.point1,self.radius
                break
        
            if k in (ord("q"), ord("\x1b")):
                cv2.destroyWindow(self.name)
                return None,None
                break
        return None,None





def drumSelector(img):
    window = SelectionWindow(img)
    centre,radius = window.show()
    return centre,radius


