import glob
import os
import sys
import getopt

import cv2
import numpy as np

from utils import outerContour

warpedW = 700
warpedH = 900


def checkBlankArea(warped):

    roi = warped[75:160, 510:635]
    mean = cv2.mean(roi)
    return mean[0]

def removeXYSigns(warped):

    points = np.array(
        [[[97, 869], [36, 858], [27, 810], [74, 810], [94, 832]]])
    cv2.fillPoly(warped, points, (255, 255, 255))


def findRectanglePatterns(gray):

    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    polys = []
    minContourLength = 300
    for contour in contours:
        if len(contour) >= minContourLength:
            epsilon = 0.05 * cv2.arcLength(contour, True)
            curve = cv2.approxPolyDP(contour, epsilon, True)
            if len(curve) == 4 and cv2.isContourConvex(curve):
                polys.append(curve)

    polys.sort(key=lambda x: outerContour(x, thresh), reverse=False)
    return polys


def findRectanglePatternHomography(gray):

    polys = findRectanglePatterns(gray)
    biggerContour = polys[0]

    destPoints: np.ndarray = np.array(
        [[[0, warpedH]], [[0, 0]], [[warpedW, 0]], [[warpedW, warpedH]]])
    M = cv2.findHomography(biggerContour, destPoints)[0]
    warped = cv2.warpPerspective(gray, M, (warpedW, warpedH))

    currMax = checkBlankArea(warped)
    for i in range(3):
        biggerContour = np.roll(biggerContour, shift=1, axis=0)
        M2 = cv2.findHomography(biggerContour, destPoints)[0]
        rotated = cv2.warpPerspective(gray, M2, (warpedW, warpedH))
        rotatedScore = checkBlankArea(rotated)
        if rotatedScore > currMax:
            M = M2
            warped = rotated
            currMax = rotatedScore

    removeXYSigns(warped)

    return M, biggerContour, warped


def genExpectedChessboardCorners(width=160, height=200, excludeTrickyPoints=True):

    outerBorderPoints = [[0, 0], [160, 0], [160, 200], [0, 200]]
    innerBorderPoints = [[10, 10], [150, 10], [150, 190]]
    innerChessboardPoints = \
        [[20, j] for j in range(40, 180, 20)] + \
        [[i, j] for i in range(40, 120, 20) for j in range(20, 200, 20)] + \
        [[120, j] for j in range(40, 200, 20)] + \
        [[140, j] for j in range(60, 180, 20)]

    if excludeTrickyPoints == False:
        innerBorderPoints.append([10, 190])
        innerChessboardPoints.append([20, 180])

    innerPoints = innerBorderPoints + innerChessboardPoints
    transformedInnerPoints = [
        [[x / width * warpedW, y / height * warpedH]] for x, y in innerPoints]
    transformedOuterPoints = [
        [[x / width * warpedW, y / height * warpedH]] for x, y in outerBorderPoints]
    return np.array(transformedInnerPoints, dtype=np.float32), np.array(transformedOuterPoints, dtype=np.float32)


def findChessboardCorners(H, rectangle, cropped, gray, useOuterPoints=False):

    imagePoints = []
    objectPoints = []

    innerTargetPoints, outerTargetPoints = genExpectedChessboardCorners()

    zeroZone = (-1, -1)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_COUNT, 2000, 0.01)
    refinedInnerPoints = cv2.cornerSubPix(
        cropped, innerTargetPoints, (32, 32), zeroZone, criteria)
    refinedOuterPoints = cv2.cornerSubPix(
        gray, outerTargetPoints, (4, 4), zeroZone, criteria)

    H_inv = np.linalg.inv(H)
    projectedInner = cv2.perspectiveTransform(refinedInnerPoints, H_inv)
    projectedOuter = cv2.perspectiveTransform(refinedOuterPoints, H_inv)

    if useOuterPoints:
        innerTargetPoints.extend(outerTargetPoints)
        projectedInner.extend(projectedOuter)

    for t, p in zip(innerTargetPoints, projectedInner):
        tx, ty = t[0]
        px, py = p[0]
        objectPoints.append([tx, ty, 0.0])
        imagePoints.append([px, py])

    return imagePoints, objectPoints


def run(debug=False):
    imagePoints = []
    objectPoints = []

    i = 0
    for file in glob.glob("./calibration_images/*.png"):
        img = cv2.imread(file)
        gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

        H, rectangle, cropped = findRectanglePatternHomography(gray)

        imgImagePoints, imgObjectPoints = findChessboardCorners(
            H, rectangle, cropped, gray)
        imagePoints.append(imgImagePoints)
        objectPoints.append(imgObjectPoints)

        if debug:
            cv2.drawContours(img, [rectangle], -1, (255, 0, 0))
            for c in imgImagePoints:
                px, py = c
                px, py = int(px), int(py)
                cv2.circle(img, (px, py), 3, (0, 0, 255), -1)
            cv2.imshow(file, img)
            cv2.waitKey(1)

        print(f"Image {i}/50")
        i += 1

    imagePoints = np.array(imagePoints, dtype=np.float32)
    imagePoints = np.reshape(
        imagePoints, (imagePoints.shape[0], imagePoints.shape[1], 1, 2)
    )
    objectPoints = np.array(objectPoints, dtype=np.float32)

    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        objectPoints, imagePoints, (img.shape[0], img.shape[1]), None, None
    )
    print(f"\n\nRMS: {ret}")
    print(f"\nK: {K}")
    print(f"Distortion parameters:\n{dist}")
    print(f"\nImages used for calibration: {imagePoints.shape[0]}/50")

    Kfile = cv2.FileStorage("intrinsics.xml", cv2.FILE_STORAGE_WRITE)
    Kfile.write("RMS", ret)
    Kfile.write("K", K)
    Kfile.write("dist", dist)
    Kfile.release()
    print("Saved intrinsics in intrinsics.xml")

    if debug:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def run_main():
    opts, args = getopt.getopt(sys.argv, "v")
    debug = args.count("-v") > 0
    run(debug)
