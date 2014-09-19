import euclid


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
    def __init__(self, plane):
        super(RaycastingPlane, self).__init__()
        if type(plane)!=euclid.Plane:
            raise TypeError("Requires Plane")
        self.shape = plane
        self.color1 = (0,0,0)
        self.color2 = (200,200,200)

    def intersect(self, ray):
        return self.shape.intersect(ray)

    def distance(self, ray):
        return self.shape.distance(ray)

    def getColor(self, coords=None):
        s = int(coords[0]) + int(coords[1]) + int(coords[2])
        if s % 2 == 0:
            return self.color1
        return self.color2

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        a = self.n == other.n
        b = self.k == other.k
        return a and b

    def __ne__(self, other):
        return not self.__eq__(other)