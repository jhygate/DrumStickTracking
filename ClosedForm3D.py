import numpy as np
import math

def getTranslateMatrix(dX,dY,dZ):
     Translate_matrix = np.array([[1, 0, 0, dX],
                                   [0, 1, 0, dY],
                                   [0, 0, 1, dZ],
                                   [0, 0, 0, 1]])
     return Translate_matrix

def getXRotateAxis(theta):
     rotate_matrix = np.array([[1, 0, 0, 0],
                              [0, math.cos(theta), -math.sin(theta), 0],
                              [0, math.sin(theta), math.cos(theta), 0],
                              [0, 0, 0, 1]])
     return rotate_matrix

def getYRotateAxis(theta):
     rotate_matrix = np.array([[math.cos(theta), 0, 0, math.sin(theta)],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [-math.sin(theta), 0, 0, math.cos(theta)]])
     return rotate_matrix

def getZRotateAxis(theta):
     rotate_matrix = np.array([[math.cos(theta), -math.sin(theta), 0, 0],
                              [math.sin(theta), math.cos(theta), 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])
     return rotate_matrix

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def transformToXYPlane(A,B,C,F):
     # A = np.append(np.array(A), [1]) 
     # B = np.append(np.array(B), [1]) 
     # C = np.append(np.array(C), [1]) 
     # F = np.append(np.array(F), [1]) 

     points = np.array([A,B,C,F]).T
     
     T = getTranslateMatrix(-A[0],-A[1],0)

     lineVec = unit_vector(T.dot(C)[:3])
     axis = unit_vector(np.array([1,0,0]))

     xTheta = angle_between(lineVec,axis)
     Rz = getZRotateAxis(-xTheta)

     focalVec = np.subtract(F,B)
     focalVec[3] = 1
     xTheta = angle_between(focalVec,[0,1,0,1])
     Rx = getXRotateAxis(-xTheta)

     A = np.array(A)
     Transform = T.dot(points)
     RotatedToX = Rz.dot(Transform)
     RotatedToPlane = Rx.dot(RotatedToX)

     M = np.dot(Rx,np.dot(Rz,T))

     Minv = np.linalg.inv(M)

     converted = np.dot(M,points)
     reversed = np.dot(Minv,converted)
    

     return M


     

     points = RotatedToPlane.T
     A2d = points[0][:2]
     B2d = points[1][:2]
     C2d = points[2][:2]
     F2d = points[3][:2]

     return A2d,B2d,C2d,F2d

def convertToPlanarXY(points,M):


     points = points.T
     points = M.dot(points)
     points = points.T

     points2D = []
     for point in points:
          points2D.append(point[:2])

     return points2D


def convertPlanarToWorld(points,M):
     expandedPoints = []
     for point in points:
          expandedPoints.append(np.append(point,[0,1]))
     points = np.array(expandedPoints).T
     Minv = np.linalg.inv(M)
     points = np.dot(Minv,points)
     points = points.T
     return points




def getPoints(a,b,c,FocalPoint):

     sticklength = 10
     d1 = sticklength/2
     d2 = sticklength/2

     V1 = unit_vector(np.subtract(FocalPoint,a))
     V2 = unit_vector(np.subtract(FocalPoint,b))
     V3 = unit_vector(np.subtract(FocalPoint,c))

     # V3 = alpha*V1 + beta*V2
     #Solve for alpha,beta
     A = [[V1[0],V2[0]],
          [V1[1],V2[1]]]

     B = [[V3[0]],
          [V3[1]]]

     X = np.dot(np.linalg.inv(A),B)
     alpha = X[0] #CAREFUl HERE CHOICE OF SOLUTIONS 4 ALPHA,BETA
     beta = X[1]

     v3Pred = np.multiply(V1,alpha) + np.multiply(V2,beta)

     c = d2/np.linalg.norm((d2/d1)*alpha*V1 +(d2/(d1+d2))*beta*V2)
     a = (-d2/d1)*alpha*c
     b = (d2/(d1+d2))*beta*c



     P1 = np.multiply(V3,c)
     P2 = np.multiply(V2,b)
     P3 = np.multiply(V1,a)

     return P1,P2,P3

def getStickLocation(stickPointsPlane,focalPoint):
     #Points must be 1x4 vector
     A = np.append(np.array(stickPointsPlane[0]), [1]) 
     B = np.append(np.array(stickPointsPlane[1]), [1]) 
     C = np.append(np.array(stickPointsPlane[2]), [1]) 
     F = np.append(np.array(focalPoint), [1]) 

     points = np.array(A,B,C,F)

     M = transformToXYPlane(A,B,C,F)

     points2D = convertToPlanarXY(points,M)
     realPos2d = getPoints(points2D[0],points2D[1],points2D[2],points2D[3])
     points3D = convertPlanarToWorld(realPos2d,M)

     stickPoints = []
     for point in points3D:
          stickPoints.append(point[:3])
     return stickPoints




# M = transformToXYPlane([0,3,0,1],[0,4,0,1],[0,5,0,1],[0,3,5,1])
# points = np.array([[0,3,0,1],[0,4,0,1],[0,5,0,1],[0,3,5,1]])
# points2D = convertToPlanarXY(points,M)



# realPos2d = getPoints(points2D[0],points2D[1],points2D[2],points2D[3])
# print(realPos2d)
# print(points2D,'2d')
# points3D = convertPlanarToWorld(realPos2d,M)
# print(points3D,'world')

















