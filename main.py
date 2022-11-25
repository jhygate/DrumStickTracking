import cv2
import cameraHelpers

videoPath = 'Videos/ABOVETRIM.mp4'
calibrationPath = 'calibration.yml'
imageWidth = 500

frameGenerator = cameraHelpers.getFrameGenerator(videoPath,calibrationPath,imageWidth)

frame = frameGenerator()
while frame is not None:
    cv2.imshow('frame',frame)
    cv2.waitKey(1)
    frame = frameGenerator()
    
