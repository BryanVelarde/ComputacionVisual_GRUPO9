import cv2
import numpy as np
import math


def outerContour(contour, gray, margin=10):
    
    kernel = np.ones((margin, margin), np.uint8)
    mask = np.zeros(gray.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, contour, 255)
    eroded = cv2.erode(mask, kernel)
    mask = cv2.bitwise_xor(eroded, mask)

    mean = cv2.mean(gray, mask)
    return mean[0]


def loadIntrinsics(path="intrinsics.xml"):

    intrinsics = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
    K = intrinsics.getNode("K").mat()
    dist = intrinsics.getNode("dist").mat()
    return K, dist


def sortCorners(corners):

    center = np.sum(corners, axis=0) / len(corners)

    def rot(point):
        return math.atan2(point[0][0] - center[0][0], point[0][1] - center[0][1])

    sortedCorners = sorted(corners, key=rot, reverse=True)
    return np.roll(sortedCorners, 2, axis=0)


def findPointsInsidePoly(img, poly):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, poly, 255)
    imgMasked = np.bitwise_and(img, mask)
    points = cv2.findNonZero(imgMasked)
    return points


def createRays(pts, K_inv):
    return [np.matmul(K_inv, p) for p in pts]


def linePlaneIntersection(plane, rayDir):
    pOrigin, pNormal = plane
    d = np.dot(pOrigin, pNormal) / np.dot(rayDir, pNormal)
    return rayDir * d


def findPlaneFromHomography(H, K_inv):
    result = np.matmul(K_inv, H)
    result /= cv2.norm(result[:, 1])
    r0, r1, t = np.hsplit(result, 3)
    r2 = np.cross(r0.T, r1.T).T
    _, u, vt = cv2.SVDecomp(np.hstack([r0, r1, r2]))
    R = np.matmul(u, vt)
    origin = t[:, 0]
    normal = R[:, 2]
    return origin, normal


def fitPlane(points):
    centroid = np.mean(points, axis=0)
    xxSum = 0
    xySum = 0
    xzSum = 0
    yySum = 0
    yzSum = 0
    zzSum = 0

    for point in points:
        diff = point - centroid
        xxSum += diff[0] * diff[0]
        xySum += diff[0] * diff[1]
        xzSum += diff[0] * diff[2]
        yySum += diff[1] * diff[1]
        yzSum += diff[1] * diff[2]
        zzSum += diff[2] * diff[2]

    detX = yySum * zzSum - yzSum * yzSum
    detY = xxSum * zzSum - xzSum * xzSum
    detZ = xxSum * yySum - xySum * xySum
    detMax = max(detX, detY, detZ)

    if detMax == detX:
        normal = np.array([detX, xzSum * yzSum - xySum * zzSum, xySum * yzSum - xzSum * yySum])
    elif detMax == detY:
        normal = np.array([xzSum * yzSum - xySum * zzSum, detY, xySum * xzSum - yzSum * xxSum])
    else:
        normal = np.array([xySum * yzSum - xzSum * yySum, xySum * xzSum - yzSum * xxSum, detZ])

    normal = normal / np.linalg.norm(normal)
    origin = np.array(centroid)
    return origin, normal
