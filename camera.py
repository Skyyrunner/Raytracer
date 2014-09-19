import euclid
from euclid import Point3 as P3
from euclid import Vector3 as V3
from euclid import Ray3 as R3
import math

# v is vector to be rotated, k is axis, and t is amount of rotation in radians
def rotate(v, k, t):
    k = k.normalized()
    return v * math.cos(t) + k.cross(v) * math.sin(t) + k * k.dot(v) * (1 - math.cos(t))

# can handle rotating various geometry.
def rotateGeneric(shape, k, t):
    if type(shape) == V3:
        return rotate(shape, k, t)
    if type(shape) == P3:
        v = rotate(shape,k, t)
        return P3(v.x, v.y, v.z)
    if type(shape) == R3:
        v, p = R3.v, R3.p
        out = R3(p, v)
        out.v = rotate(v, k, t)
        out.p = rotate(p, k, t)
        return out
    if type(shape) == euclid.Plane:
        n,k = shape.n, shape.k
        out = euclid.Plane(n, k)
        out.n = rotate(n, k, t)
        return out
    if type(shape) == euclid.Sphere:
        c,r = shape.c,shape.r
        out = euclid.Sphere(c, r)
        out.c = rotate(c, k, t)
        return out
    raise TypeError("Argument type for shape(" + type(shape) + ") is unknown.")

class Camera(object):
    # rotation is in degrees.
    def __init__(self,focus=(1,0,0), FoV=90, width=180, height=180, rotation=(0,0,0), translation=P3(0,0,0), zoom=1.0):
        if len(focus) != 3 or type(focus) != tuple:
            raise TypeError("'focus' must be a tuple of length 3.")
        self.focus = euclid.Point3(focus[0], focus[1], focus[2])
        self.FoV = float(FoV)
        self.LRAngle = math.radians(self.FoV)
        self.width = int(width)
        self.height = int(height)
        self.aspectRatio = float(self.width)/self.height
        if len(rotation) != 3 or type(rotation) != tuple:
            raise TypeError("'rotation' must be a tuple of length 3.")
        self.rotation = (math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]))
        if len(translation) != 3:
            raise TypeError("'translation' must be a Point3 or Vector3.")
        self.translation = translation
        self.zoom = float(zoom)

        self.calculateRepr() # calculate representation

    # TODO translation
    def calculateRepr(self):
        # first, reset to default values
        Ly = -self.zoom * math.tan( self.LRAngle/2 )
        Ry = -Ly
        self.L = P3(0, Ly, 0) - self.focus # to leftmost point on mid row of screen
        self.R = P3(0, Ry, 0) - self.focus # to rightmost "" ""
        self.D = V3(-1, 0, 0) * self.zoom # line from camera to screen.
        # figure out up angle
        # first get x distance
        x = Ry * 2
        y = 1.0/self.aspectRatio * x
        # next use trig to figure out up angle
        self.TBAngle = math.atan(y/2/self.zoom) * 2
        Tz = self.zoom * math.tan( self.TBAngle / 2)
        Bz = -self.zoom * math.tan( self.TBAngle / 2)
        self.T = V3(0, 0, Tz) - self.focus # to topmost point on mid column of screen
        self.B = V3(0, 0, Bz) - self.focus # to bottommost "" ""
        # screen's plane
        self.screenPlane = euclid.Plane(P3(0,0,0), self.D) # the normal is the line from cam to screen.

        # Next, rotate all vectors accordingly.        
        for i in xrange(3):
            if self.rotation[i] != 0:
                t = self.rotation[i]
                axis = V3(1 if i==0 else 0, 1 if i ==1 else 0, 1 if i==2 else 0)
                self.L     = rotateGeneric(self.L, axis, t)
                self.R     = rotateGeneric(self.R, axis, t)
                self.D     = rotateGeneric(self.D, axis, t)
                self.T     = rotateGeneric(self.T, axis, t)
                self.B     = rotateGeneric(self.B, axis, t)
                self.focus = rotateGeneric(self.focus, axis, t)

        # Figure out the basic vectors for the screen.
        self.basic_horizontal = self.R - self.L
        self.basic_vertical = self.B - self.T

        # Topleft corner finding.
        self.topleft = self.focus + self.L + self.basic_vertical * .5

    def getPixelCoords(self, w, h):
        # Slice basic vectors horiz/vert into w, h pieces and add.
        vert = self.basic_vertical / float(w)
        horiz = self.basic_horizontal / float(h)
        for x in xrange(w):
            for y in xrange(h):
                yield x, y, self.topleft + horiz * x + vert * y 






