# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from midi import *

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

min_radius = 9

# if a video path was not supplied, grab the reference

vs = VideoStream(src=0).start()

# allow the camera or video file to warm up
time.sleep(2.0)

frame_size = (600, 450)

pan_control= 14

volume_control = 9

#pitch
elevation_control = 3

def map_to_midi_127(value, max_value, inverse=False):
    if inverse:
        return 127 - int(value / max_value * 127)
    else:
        return int(value/max_value *127)

output = open_port(get_midi_port())
# hog = cv2.HOGDescriptor()
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

while True:
    # grab the current frame
    frame = vs.read()
    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    width, height = frame.shape[0:2]

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)

    # boxes, weights = hog.detectMultiScale(gray, winStride=(8, 8))
    #
    # boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])



    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # for (xA, yA, xB, yB) in boxes:
    #     # display the detected boxes in the colour picture
    #     cv2.rectangle(frame, (xA, yA), (xB, yB),
    #                   (0, 255, 0), 2)

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > min_radius:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            cv2.putText(frame, f'X: {x}', (0, 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
            cv2.putText(frame, f'Y: {y}', (0, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))
            #pan
            output.send(construct_midi('control_change', control=pan_control, value=map_to_midi_127(x, 600, True)))
            time.sleep(0.01)
            #volume/radius
            output.send(construct_midi('control_change', control=volume_control, value=map_to_midi_127(radius, 300)))
            time.sleep(0.01)
            # elevation
            output.send(construct_midi('control_change', control=elevation_control, value=map_to_midi_127(y, 450, True)))
            time.sleep(0.01)



    # update the points queue
    pts.appendleft(center)
    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
