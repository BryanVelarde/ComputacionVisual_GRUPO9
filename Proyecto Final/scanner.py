import cv2
import numpy as np
import open3d as o3d
import sys
import getopt

from utils import (
    loadIntrinsics,
    sortCorners,
    createRays,
    linePlaneIntersection,
    fitPlane,
    outerContour,
    findPlaneFromHomography,
    findPointsInsidePoly
)

# Dimensiones del rectángulo (Referencia)
rectWidth = 25
rectHeight = 15

# Rango HSV para detectar el laser
hsvMin = (150, 20, 78)
hsvMax = (200, 255, 255)

kernel2 = np.ones((2, 2), np.uint8)
kernel4 = np.ones((4, 4), np.uint8)


def findRectanglePatterns(firstFrame):

    gray = cv2.cvtColor(firstFrame, cv2.COLOR_RGBA2GRAY)
    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    winSize = (16, 16)
    zeroZone = (-1, -1)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_COUNT, 200, 0.1)
    minContourLength = 30
    polys = []
    for contour in contours:
        if len(contour) >= minContourLength:
            epsilon = 0.01 * cv2.arcLength(contour, True)
            curve = cv2.approxPolyDP(contour, epsilon, True)
            if len(curve) == 4 and cv2.isContourConvex(curve):
                curve = cv2.cornerSubPix(gray, np.float32(
                    curve), winSize, zeroZone, criteria)
                sortedCurve = sortCorners(curve)
                score = outerContour(sortedCurve.astype(np.int32), gray)
                polys.append((sortedCurve, score))

    polys.sort(key=lambda x: x[1], reverse=False)
    return [p[0] for p in polys]


def findReference3DPoints(img, rect, plane, K_inv):

    imgPoints = findPointsInsidePoly(img, rect.astype(np.int32))
    if imgPoints is None:
        return None, None


    homoImgPoints = np.hstack(
        (imgPoints[:, 0], np.ones(imgPoints.shape[0]).reshape(-1, 1),))
    rays = createRays(homoImgPoints, K_inv)
    points3D = [linePlaneIntersection(plane, ray) for ray in rays]
    return points3D, imgPoints


def processFrame(firstFrame, undistorted, K_inv, upperRect, lowerRect, upperPlane, lowerPlane, debug=False):

    hsv = cv2.cvtColor(undistorted, cv2.COLOR_BGR2HSV)
    inRange = cv2.inRange(hsv, hsvMin, hsvMax)
    final = cv2.morphologyEx(inRange, cv2.MORPH_OPEN, kernel4)
    laserPts = cv2.findNonZero(final)

    if debug:
        if laserPts is not None:
            for p in laserPts:
                cv2.circle(undistorted, (p[0][0], p[0][1]), 1, (0, 0, 255))
        cv2.imshow('undistorted', undistorted)

    upper3DPoints, upperImgPoints = findReference3DPoints(
        final, upperRect, upperPlane, K_inv)
    lower3DPoints, lowerImgPoints = findReference3DPoints(
        final, lowerRect, lowerPlane, K_inv)

    if upper3DPoints is not None and lower3DPoints is not None:

        referencePoints = np.array(upper3DPoints + lower3DPoints)
        laserPlane = fitPlane(referencePoints)

        homoImgPoints = np.hstack(
            (laserPts[:, 0], np.ones(laserPts.shape[0]).reshape(-1, 1),))
        rays = createRays(homoImgPoints, K_inv)
        points3D = [linePlaneIntersection(laserPlane, ray) for ray in rays]

        x = laserPts.squeeze(1)
        colors = np.flip(firstFrame[x[:, 1], x[:, 0]].astype(
            np.float64) / 255.0, axis=1)
        return points3D, colors, laserPlane
    return None, None, None


def run(path, debug=False):

    K, dist = loadIntrinsics()
    K_inv = np.linalg.inv(K)

    cap = cv2.VideoCapture(path)
    firstFrameDistorted = cap.read()[1]
    firstFrame = cv2.undistort(firstFrameDistorted, K, dist)

    polys = findRectanglePatterns(firstFrame)
    upperRect, lowerRect = polys[0:2]

    if debug:
        firstFrameDbg = firstFrame.copy()
        cv2.drawContours(firstFrameDbg, [upperRect.astype(
            np.int32), lowerRect.astype(np.int32)], -1, (0, 0, 255))
        cv2.imshow("debug rect contours", firstFrameDbg)
        cv2.waitKey(1)

    upperDestPoints: np.ndarray = np.array(
        [[[0, rectHeight]], [[0, 0]], [[rectWidth, 0]], [[rectWidth, rectHeight]]])
    upperRectHomo = cv2.findHomography(
        sortCorners(upperDestPoints), upperRect)[0]
    upperPlane = findPlaneFromHomography(upperRectHomo, K_inv)

    lowerDestPoints: np.ndarray = np.array(
        [[[0, rectHeight]], [[0, 0]], [[rectWidth, 0]], [[rectWidth, rectHeight]]])
    lowerRectHomo = cv2.findHomography(
        sortCorners(lowerDestPoints), lowerRect)[0]
    lowerPlane = findPlaneFromHomography(lowerRectHomo, K_inv)

    objPoints = []
    objColors = []

    isRecording = True
    while cap.isOpened():
        if isRecording:
            ret, frame = cap.read()
            if not ret:
                break

        undistorted = cv2.undistort(frame, K, dist)
        framePts, frameColors, laserPlane = processFrame(firstFrame, undistorted, K_inv, upperRect, lowerRect,
                                                         upperPlane,
                                                         lowerPlane, debug)
        if framePts is not None and frameColors is not None:
            objPoints.extend(framePts)
            objColors.extend(frameColors)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('p'):  # Pausa
            isRecording = False
        if cv2.waitKey(1) & 0xFF == ord('c'):  # Continuar 
            isRecording = True

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(
        np.vstack(objPoints).astype(np.float64))
    pcd.colors = o3d.utility.Vector3dVector(np.vstack(objColors))
    o3d.io.write_point_cloud("output.ply", pcd)
    o3d.visualization.draw_geometries([pcd])

    cap.release()
    cv2.destroyAllWindows()


def run_main_scann():
    opts, args = getopt.getopt(sys.argv, "v")
    debug = args.count("-v") > 0
    path = args[-1]
    run(path, debug)
