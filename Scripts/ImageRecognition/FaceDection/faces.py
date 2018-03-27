#!/usr/bin/env python
import os
import cv2
import sys
from time import sleep

cascPath = "database.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
if int(os.environ['camera']) == 0:
   video_capture = cv2.VideoCapture('/dev/video13')
else:
   video_capture = cv2.VideoCapture(0)
#video_capture = cv2.VideoCapture(0)
anterior = 0

while True:
    if not video_capture.isOpened():
        print('No camera detected.')
        sleep(5)
        pass

    # Read each frame
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Create a  rectangle when a face is detected
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 9, 9), 2)


    cv2.imshow('Face detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Face detector', frame)

# Finish an release all the resources
video_capture.release()
cv2.destroyAllWindows()
