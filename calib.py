#!/usr/bin/env python3
import numpy as np
import cv2, PIL, os, math, time
from cv2 import aruco
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

fig = plt.figure()
nx = 8
ny = 6
for i in range(1, nx*ny + 1):
    ax = fig.add_subplot(ny, nx, i)
    img = aruco.drawMarker(aruco_dict, i-1, 700)
    plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
    ax.axis("off")
plt.savefig("markers.png")
# plt.show()


board = aruco.CharucoBoard_create(3, 3, 1, 0.8, aruco_dict)
imboard = board.draw((4000, 4000))
# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# plt.imshow(imboard, cmap = mpl.cm.gray, interpolation = "nearest")
# ax.axis("off")
# cv2.imwrite("chessboard.tiff", imboard)
# plt.grid()
# plt.show()
# print('Print the calibration checkerboard')

# ***********************************
#   detect charuco corners and ids
# ***********************************
def detect_charuco_corners(board, aruco_dict):
    cap = cv2.VideoCapture(0)
    pTime = 0
    i = 0
    
    while (cap.isOpened()):
        ret, frame = cap.read()
        origFrame = frame.copy()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict)
            if ids is not None:
                ret, ch_corners, ch_ids = aruco.interpolateCornersCharuco(corners, ids, gray, board)
                if ch_ids is not None:
                    aruco.drawDetectedCornersCharuco(frame, ch_corners, ch_ids, (0,255,0))
            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime
            cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

def save_chessboard(board, aruco_dict):
    cap = cv2.VideoCapture(0)
    pTime = 0
    i = 0
    
    while (cap.isOpened()):
        ret, frame = cap.read()
        origFrame = frame.copy()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict)
            if ids is not None:
                ret, ch_corners, ch_ids = aruco.interpolateCornersCharuco(corners, ids, gray, board)
                if ch_ids is not None:
                    aruco.drawDetectedCornersCharuco(frame, ch_corners, ch_ids, (0,255,0))
                    if (i <= 100):
                        cv2.imwrite('image'+str(i)+'.png', origFrame)
                        i += 1
                    else:
                        break
            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime
            cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break




def read_chessboards():
    """charuco base pose estimation"""
    print('charuco base pose estimation')
    allCorners = []
    allIds = []
    imSize = []
    decimator = 0
    i = 0
    # read all images from folder
    for fname in os.listdir('images'):
            print(str(i) + '. processing image %s...'%fname)
            frame = cv2.imread('images/'+fname)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            res = cv2.aruco.detectMarkers(gray, aruco_dict)
            if len(res[0]) > 0:
                res2 = cv2.aruco.interpolateCornersCharuco(res[0], res[1], gray, board)
                if res2[1] is not None and res2[2] is not None and len(res2[1]) > 3 and decimator%1 == 0:
                    allCorners.append(res2[1])
                    allIds.append(res2[2])
                    imSize.append(gray.shape)
            decimator+=1
            i += 1
    return allCorners, allIds, imSize[0]
    print("finished!")

def calibrate_camera(allCorners, allIds, imSize):
    """ Calibrates camera using the detected corners"""
    print ('Camera Calibration')
    
    cameraMatrixinit = np.array([[2000., 0., imSize[0]/2.], [0., 2000., imSize[1]/2.], [0., 0., 1.]])
    distCoeffsinit = np.zeros((5,1))
    flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL)
    print ('still going.. ')
    (ret, camera_matrix, distortion_coefficients0,
     rotation_vectors, translation_vectors,
     stdDeviationsIntrinsics, stdDeviationsExtrinsics,
     perViewErrors) = cv2.aruco.calibrateCameraCharucoExtended(
         charucoCorners = allCorners,
         charucoIds = allIds,
         board = board,
         imageSize = imSize,
         cameraMatrix = cameraMatrixinit,
         distCoeffs = distCoeffsinit,
         flags = flags,
         criteria = (cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))
    print ('still going.. ')
    return ret, camera_matrix, distortion_coefficients0, rotation_vectors, translation_vectors
    print('Finished!')

            


# record webcam video
def webcam_record():
    pTime = 0
    cap = cv2.VideoCapture(0)
    framerate = cap.get(cv2.CAP_PROP_FPS)
    i = 0
    while (cap.isOpened()):
        cTime = time.time()
        ret, frame = cap.read()
        if ret == True:
            fps = 1/(cTime-pTime)
            cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            cv2.imshow('frame', frame)
            pTime = cTime
            if (i <= 150):
                cv2.imwrite('image'+str(i)+'.png', frame)
            i += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    print('image saved')

# write 100 images from webcam
def write_images():
    cap = cv2.VideoCapture(0)
    i = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            if (i <= 100):
                cv2.imshow('frame', frame)
                cv2.imwrite('image'+str(i)+'.png', frame)
                i += 1
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    print('image saved')



if __name__ == "__main__":

    # save_chessboard(board, aruco_dict)
    detect_charuco_corners(board, aruco_dict)
    # allCorners, allIds, imSize = read_chessboards()
    
    # calibrate_camera(allCorners, allIds, imSize)
    
    print(allCorners)
    print(allIds)
    print(imSize)