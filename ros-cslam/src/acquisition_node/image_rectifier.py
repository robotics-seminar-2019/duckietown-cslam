#!/usr/bin/env python

import cv2
import numpy as np

class ImageRectifier():
    def __init__(self, image, cameraMatrix, distCoeffs):
        """
        Rectifies an image with a particular cameraMatrix(K) and distCoeffs(D); based on opencv undistort function
        see: https://docs.opencv.org/2.4/modules/imgproc/doc/geometric_transformations.html?highlight=initundistort#undistort
        see: http://docs.ros.org/api/sensor_msgs/html/msg/CameraInfo.html
        """
        # Validate the inputs
        if len(np.shape(cameraMatrix)) !=2 or np.shape(cameraMatrix)[0]!=3 or np.shape(cameraMatrix)[1]!=3:
            raise ValueError("Camera matrix is not a 3x3 matix! It is of shape %s." % str(np.shape(cameraMatrix)))
        if len(np.shape(distCoeffs)) !=1 or np.shape(distCoeffs)[0]!=5:
            raise ValueError("distCoeffs should be a vector of length 5! It is of shape %s." % str(np.shape(cameraMatrix)))

        # Enlarge the image such that it is not cropped
        # vMargin = int(image.shape[0]*0.3)
        # hMargin = int(image.shape[1]*0.3)
        # imageLarge = cv2.copyMakeBorder(image, vMargin, hMargin, vMargin, hMargin, borderType=cv2.BORDER_CONSTANT)

        # return cv2.undistort(image, cameraMatrix, distCoeffs)

        self.newCameraMatrix, self.validPixROI = cv2.getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, (image.shape[1], image.shape[0]), 1.0)
        self.map1, self.map2 = cv2.initUndistortRectifyMap(cameraMatrix, distCoeffs, np.eye(3), self.newCameraMatrix, (image.shape[1], image.shape[0]), cv2.CV_32FC1)

        self.rectify(image)

    def rectify(self, image):
        remappedIm = cv2.remap(image, self.map1, self.map2, cv2.INTER_NEAREST)

        return remappedIm, self.newCameraMatrix

    def beautify(self, image):

        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3., tileGridSize=(8,8))

        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)  # convert from BGR to LAB color space
        l, a, b = cv2.split(lab)  # split on 3 different channels

        l2 = clahe.apply(l)  # apply CLAHE to the L-channel

        lab = cv2.merge((l2,a,b))  # merge channels
        img2 = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  # convert from LAB to BGR

        return img2

if __name__ == "__main__":
    import cv2
    im = cv2.imread("wt10_sample.png")
    D = np.array([-0.2967039649743125, 0.06795775093662262, 0.0008927768064001824, -0.001327854648098482, 0.0])
    K = np.array([336.7755634193813, 0.0, 333.3575643300718, 0.0, 336.02729840829176, 212.77376312080065, 0.0, 0.0, 1.0]).reshape((3,3))

    rectIm, newCameraMatrix = ImageRectifier().rectify(im, K, D)
    cv2.imshow('Rectified image',ImageRectifier().beautify(rectIm))
    while True:
        if cv2.waitKey(0) and 0xFF == ord('q'):
            break