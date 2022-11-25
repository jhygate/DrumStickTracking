import cv2
import numpy as np

def load_coefficients(path):
    '''Loads camera matrix and distortion coefficients.'''
    # FILE_STORAGE_READ
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)

    camera_matrix = cv_file.getNode('mtx').mat()
    dist_matrix = cv_file.getNode('dists').mat()

    cv_file.release()
    return [camera_matrix, dist_matrix]

def save_coefficients(mtx, dist,rvecs,tvecs, path):
    '''Save the camera matrix and the distortion coefficients to given path/file.'''
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    cv_file.write('mtx', mtx)
    cv_file.write('dists', dist)
    cv_file.release()

def save_coefficents_from_vid(vid_path,data_path):
    cap = cv2.VideoCapture(vid_path)
    ret, image = cap.read()
    cali_images = []
    while image is not None:
        cali_images.append(image)
        ret, image = cap.read()

    matrix,distortion,r_vecs,t_vecs = calculate_coefficents_from_images(cali_images)

    save_coefficients(matrix,distortion,r_vecs,t_vecs,data_path)
    return True

def calculate_coefficents_from_images(images):
    CHECKERBOARD = (6, 9)


    # stop the iteration when specified
    # accuracy, epsilon, is reached or
    # specified number of iterations are completed.
    criteria = (cv2.TERM_CRITERIA_EPS +
                cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Vector for 3D points
    threedpoints = []

    # Vector for 2D points
    twodpoints = []

    # 3D points real world coordinates
    objectp3d = np.zeros((1, CHECKERBOARD[0]
                        * CHECKERBOARD[1],
                        3), np.float32)
    objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],
                                0:CHECKERBOARD[1]].T.reshape(-1, 2)

    i = 0
    print(len(images))
    for image in images[::10]:
        i+=1
        print(i/len(images))
        grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        # If desired number of corners are
        # found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(
                        grayColor, CHECKERBOARD,
                        cv2.CALIB_CB_ADAPTIVE_THRESH
                        + cv2.CALIB_CB_FAST_CHECK +
                        cv2.CALIB_CB_NORMALIZE_IMAGE)

        # If desired number of corners can be detected then,
        # refine the pixel coordinates and display
        # them on the images of checker board
        if ret == True:
            threedpoints.append(objectp3d)

            # Refining pixel coordinates
            # for given 2d points.
            corners2 = cv2.cornerSubPix(
                grayColor, corners, (11, 11), (-1, -1), criteria)

            twodpoints.append(corners2)

    ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
    threedpoints, twodpoints, grayColor.shape[::-1], None, None,flags = cv2.CALIB_USE_LU)

    return matrix,distortion,r_vecs,t_vecs