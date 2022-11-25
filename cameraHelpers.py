import cv2
import calibration

def getFrameGenerator(videoPath,calibrationPath,imageWidth):
    cap = cv2.VideoCapture(videoPath)
    CAM,DIST = calibration.load_coefficients(calibrationPath)

    def frameGenerator():
        ret, frame = cap.read()
        if frame is not None:
            frame = cv2.undistort(frame,CAM,DIST)
            w ,h = frame.shape[0],frame.shape[1]
            sf = imageWidth/w
            dim = [int(h*sf),int(w*sf)]
            frame = cv2.resize(frame,dim)
            return frame
        return None
        
    return frameGenerator


