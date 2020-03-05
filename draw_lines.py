import cv2
import numpy as np
import imutils


import argparse
ap = argparse.ArgumentParser()


ap.add_argument("-i", "--image", help ="path to the image")
ap.add_argument("-v", "--video", help ="path to the video")


def draw_scoring_area(input_frame):
    """takes a frame as an input detects red markers in image and draws scoring area"""
    resized = imutils.resize(input_frame, 600, 480)
    ratio = input_frame.shape[0] / float(resized.shape[0])
    # make the lower and upper bounds for our detection via color
    red_range = np.array([0, 0, 100]), np.array([50, 12, 255])
    mask = cv2.inRange(resized, red_range[0], red_range[1])
# find the shapes in the mask
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    centers = []
    for c in contours:
        M = cv2.moments(c)
        # calculate center of targets
        cX = int((M["m10"]/M["m00"]))
        cY = int((M["m01"]/M["m00"]))
        centers.append((cX,cY))

        cv2.drawContours(resized, [c], -1, (0, 255,0))
    centers.sort(key=lambda x: x[0] )

    output = cv2.rectangle(resized,centers[1], centers[-1],color=[255,255,255], thickness=5)

    return output

def draw_floor_lines(input_frame):
    resized = imutils.resize(input_frame, 600, 480)
    ratio = input_frame.shape[0] / float(resized.shape[0])
    # make the lower and upper bounds for our detection via color
    blue = np.array([120, 0, 100]), np.array([255, 20, 255])
    mask = cv2.inRange(resized, blue[0], blue[1])
    # find the in the mask
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)
    print(len(contours))
    centers = []
    for c in contours:
        M = cv2.moments(c)
        # calculate center of targets
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        centers.append((cX, cY))

        cv2.drawContours(resized, [c], -1, (0, 255, 0))
    centers.sort(key=lambda x: x[0])


    one = cv2.line(resized, centers[0], centers[1], color=[255, 255, 255], thickness=5)
    output = cv2.line(one, centers[2], centers[3], color=[255, 255, 255], thickness=5)

    return output




if __name__ == '__main__':
    args = vars(ap.parse_args())
    # load the image

    font = cv2.FONT_HERSHEY_COMPLEX  # in case we want to put text on screen

    # load img and resize for simplicity's sake
    img = cv2.imread(args['image'])
    scoring  = draw_scoring_area(img)
    floor = draw_floor_lines(img)

    re_out = cv2.bitwise_or(scoring,floor)
    # re_out = imutils.resize(floor,600,480)
    cv2.imshow("img", re_out)
    cv2.waitKey(0)