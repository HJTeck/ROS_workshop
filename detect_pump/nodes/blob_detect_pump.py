#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import math
import numpy as np

# known pump geometry
#  - units are pixels (of half-size image)
PUMP_DIAMETER = 360
PISTON_DIAMETER = 90
PISTON_COUNT = 7

def showImage(img):
    cv2.imshow('image', img)
    cv2.waitKey(1)

def plotCircles(img, circles, color):
    if circles is None: return

    for (x,y,r) in circles[0]:
        cv2.circle(img, (int(x),int(y)), int(r), color, 2)

def process_image(msg):
    try:
        # convert sensor_msgs/Image to OpenCV Image
        bridge = CvBridge()
        orig = bridge.imgmsg_to_cv2(msg, "bgr8")
        drawImg = orig

        # resize image (half-size) for easier processing
        resized = cv2.resize(orig, None, fx=0.5, fy=0.5)
        drawImg = resized

        # convert to single-channel image
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        drawImg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # threshold grayscale to binary (black & white) image
        threshVal = 150
        ret,thresh = cv2.threshold(gray, threshVal, 255, cv2.THRESH_BINARY)
        drawImg = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

	# plot back on the original image
	drawImg = resized

        # detect outer pump circle
        pumpRadiusRange = ( PUMP_DIAMETER/2-2, PUMP_DIAMETER/2+2)
        pumpCircles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, 1, PUMP_DIAMETER, param2=7, minRadius=pumpRadiusRange[0], maxRadius=pumpRadiusRange[1])
        plotCircles(drawImg, pumpCircles, (255,0,0))
        if (pumpCircles is None):
            raise Exception("No pump circles found!")
        elif len(pumpCircles[0])<>1:
            raise Exception("Wrong # of pump circles: found {} expected {}".format(len(pumpCircles[0]),1))
        else:
            pumpCircle = pumpCircles[0][0]

        # detect blobs inside pump body
	pistonRadiusRange = ( PISTON_DIAMETER/2-1, PISTON_DIAMETER/2+1)        
	pistonCircles = cv2.HoughCircles(thresh,cv2.HOUGH_GRADIENT,1,PISTON_DIAMETER, param2=6,minRadius=pistonRadiusRange[0],maxRadius=pistonRadiusRange[1])
	plotCircles(drawImg, pistonCircles, (255,0,0))
        if (pistonCircles is None):
            raise Exception("No pump circles found!")
        elif len(pistonCircles[0])<>7:
            raise Exception("Wrong # of pump circles: found {} expected {}".format(len(pistonCircles[0]),1))
        else:
            pistonCircle = pistonCircles[0][0]

        

    except Exception as err:
        print err

    # show results
    showImage(drawImg)

def start_node():
    rospy.init_node('detect_pump')
    rospy.loginfo('detect_pump node started')

    rospy.Subscriber("image", Image, process_image)
    rospy.spin()

if __name__ == '__main__':
    try:
        start_node()
    except rospy.ROSInterruptException:
        pass

