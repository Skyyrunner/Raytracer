import euclid
from camera import rotateGeneric
import math

class RaycastingObject(object):
    def __init__(self):
        self.color = (255,255,0)
        self.reflectionIndex = 0.0
    
    def getColor(self, coords=None):
        return self.color

    def intersect(self, ray):
        raise BaseException("Must overload intersect() in class " + type(self).__name__)

    def distance(self, ray):
        raise BaseException("Must overload distance() in class " + type(self).__name__)
        
    def __eq__(self, other):
        raise BaseException("Must overload __eq__() in class " + type(self).__name__)
        
    def __ne__(self, other):
        raise BaseException("Must overload __ne__() in class " + type(self).__name__)

class RaycastingSphere(RaycastingObject):
    def __init__(self, center, radius):
        super(RaycastingSphere, self).__init__()
        if type(center) != euclid.Point3:
            raise TypeError("Must provide Point3 for center")
        self.c = center
        self.r = radius
        self.shape = euclid.Sphere(center, radius)

    def intersect(self, ray):
        return self.shape.intersect(ray)

    def distance(self, ray):
        return self.shape.distance(ray)
        
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        a = self.c == other.c
        b = self.r == other.r        
        c = self.color == other.color
        return a and b and c
    
    def __ne__(self, other):
        return not self.__eq__(other)

class RaycastingPlane(RaycastingObject):
    def __init__(self, rotation=(0,0,0), translation=euclid.Point3(0,0,0)):
        super(RaycastingPlane, self).__init__()
        self.color1 = (20, 20,20)
        self.color2 = (200,200,200)
        # default X/Y/normal
        Xaxis = euclid.Vector3(1,0,0)
        Yaxis = euclid.Vector3(0,1,0)
        Zaxis     = euclid.Vector3(0,0,1)
        self.shape = euclid.Plane(translation, Zaxis)
        # Next, rotate x/y/n
        xrot = math.radians(rotation[0])
        yrot = math.radians(rotation[1])
        zrot = math.radians(rotation[2])
        xyz = [xrot,yrot,zrot] # rotation degrees.
        XYZ = [Xaxis, Yaxis, Zaxis] # rotation axes
        axes = [Xaxis, Yaxis, Zaxis] # basic axes for plane, plus normal vector
        # rotate all axes by all directions.
        for i in xrange(3):
            for i2 in xrange(3):
                axes[i] = rotateGeneric(axes[i], XYZ[i2], xyz[i2])
        self.shape.n = axes[2]
        self.basicX = axes[0]
        self.basicY = axes[1]
        self.squaresize = 0.5 

    def intersect(self, ray):
        return self.shape.intersect(ray)

    def distance(self, ray):
        return self.shape.distance(ray)

    def getColor(self, coords=None):
        if not coords: 
            raise TypeError("Must provide a non-None argument for 'coords")
        # project coords to the plane.
        x = self.basicX.dot(coords)
        y = self.basicY.dot(coords)
        x, y = int((x-0.5)*self.squaresize), int((y-0.5)*self.squaresize)
        if (x+y)%2 == 0:
            return self.color2
        else:
            return self.color1

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        a = self.shape.n == other.shape.n
        b = self.shape.k == other.shape.k
        c = self.color1 == other.color1
        d = self.color2 == other.color2
        return a and b and c and d

    def __ne__(self, other):
        return not self.__eq__(other)
