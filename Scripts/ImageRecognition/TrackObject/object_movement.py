# Impor the libraries
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import os

# Define the parameters for args
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size")
args = vars(ap.parse_args())

# Define the rgb  upper an lower  data  that you previously get from objectdata.py
objectLower = (0,67, 116)
objectUpper = (255, 232, 240)

# Initialize the list of tracked points, the frame counter and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
direction = ""

#camera = cv2.VideoCapture("/dev/video13")
if int(os.environ['camera']) == 0:
    camera = cv2.VideoCapture('/dev/video13')
else:
    camera = cv2.VideoCapture(0)
while True:
	# Read each frame of the camera
	(grabbed, frame) = camera.read()

	# Resize the frame and convert it to the HSV
	frame = imutils.resize(frame, width=600)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the object
	# Series of dilations and erosions to remove any blobs left in the mask
	mask = cv2.inRange(hsv, objectLower, objectUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# Find contours in the mask 
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,	cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# Validad that at least one cnts exits
	if len(cnts) > 0:
		# We need to get the largest contour in the mask and then use
		# it to get minimum enclosing circle centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# This get valid if radius es greater than the minium  expected
		if radius > 10:
			# Draw the circle and centroid on the frame
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
			pts.appendleft(center)

	# loop over the set of tracked points
	for i in np.arange(1, len(pts)):
		# If either of the tracked points are None, ignore them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# Otherwise, compute the thickness of the line and draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	counter += 1

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

camera.release()
cv2.destroyAllWindows()
