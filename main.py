import numpy as np
import cv2

from imutils.video import VideoStream




filter_params =  params = cv2.SimpleBlobDetector_Params()
filter_params.blobColor = 0
filter_params.filterByColor = True
filter_params.minArea = 20
filter_params.filterByArea = True
filter_params.minThreshold = 0
filter_params.maxThreshold = 200

# detect object and track
tracker = cv2.TrackerKCF_create()






if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    video = cv2.VideoWriter(r'6.avi', fourcc, 25, size)
    while(1):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.convertScaleAbs(frame)


        ver = (cv2.__version__).split('.')
        if int(ver[0]) < 3:
            detector = cv2.SimpleBlobDetector(params)
        else:
            detector = cv2.SimpleBlobDetector_create(params)
        # gray = cv2.cvtColor(frame, cv2.IMREAD_GRAYSCALE)
        keypoints = detector.detect(frame)
        im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        if ret == True:
            video.write(im_with_keypoints)
            cv2.imshow('frame', im_with_keypoints)
        else:
            cap.release()
            break
        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break