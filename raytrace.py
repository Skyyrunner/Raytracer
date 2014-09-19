from PIL import Image
import euclid
from math import floor
from shapes import RaycastingSphere, RaycastingPlane
from camera import Camera
from time import time


class RayColor:
    def __init__(self, intensity, rgb=(0,0,0)):
        self.intensity = intensity
        self.rgb = rgb
        
    def toRGB(self):
        i = self.intensity
        return (int(self.rgb[0]*i), int(self.rgb[1]*i), int(self.rgb[2]*i))

distances = []

def reflect(point, obj, ray):
    if type(obj) == RaycastingSphere:
        n = (point - obj.c).normalized()
        v = ray.v.normalized()
        return 2 * n.dot(v) * n - v
    else:
        raise TypeError("Unknown shape")

# Supply 2 RayColors, returns RGB tuple that must be floor()'d before used in PIL
def blend(colors):
    intensity = 0.0
    for c in colors:
        intensity += c.intensity
    colors.insert(0, 0.0)
    rgb = [0,0,0]
    for x in xrange(3):
        rgb[x] = reduce(lambda s, c: s + c.rgb[x] * c.intensity, colors)   
    return RayColor(intensity, rgb) 

class Scene:
    def __init__(self):
        self.BackgroundColor = (255, 0, 255)
        self.objects = []
        # for now, directly define screen
        self.topleft = euclid.Point3(20.0, -4.0, -4.0)
        self.bottomright = euclid.Point3(20.0, -12.0, -12.0)
        #self.camera = euclid.Point3(30.0, 0.0, 0.0)
        self.camera = Camera(zoom=0.05, rotation=(0, 6, 0))
        # light source is a single point for now
        self.light = euclid.Point3(-60.0,0.0,20.0)


    def getPixelCoords(self, w, h):
        # must assume that x is fixed and y,z are what is being iterated over.
        deltaW = (self.topleft.y - self.bottomright.y)/float(w)
        deltaH = (self.topleft.z - self.bottomright.z)/float(h)
        for x in xrange(w):
            for y in xrange(h):
                yield x, y, euclid.Point3(self.topleft.x, self.topleft.y + deltaW * x, self.topleft.z + deltaH * y)

    def getColor(self, intersect, obj, intensity):
        # DEBUG: no shadows
        #return RayColor(intensity, obj.getColor(intersect))
        # get a ray from the intersect to the source of light
        vectorToLight = self.light - intersect
        rayToLight = euclid.Ray3(intersect, vectorToLight)
        for o in self.objects:
            i = o.intersect(rayToLight)
            if obj == o:
                if type(i) == euclid.Point3:
                    # often means intercept with self
                    continue
                elif i == None:
                    continue # no intercept
                lenI = abs(i)
                distances.append(lenI)
                if lenI < 0.1:
                    continue
            if type(i) != None:
                # is in shadow
                return RayColor(intensity, (0,0,0))
        # otherwise not in shadow
        # find intensity depending on angle to light.
        if type(obj) == RaycastingPlane:
            normal = obj.shape.n
        elif type(obj) == RaycastingSphere:
            normal = (intersect - obj.shape.c).normalize()
        strength = abs(vectorToLight.normalized().dot(normal))
        #strength = 1.0
        return RayColor(intensity*strength, obj.getColor(intersect))

    def findIntersect(self, ray):
        maxD = 0
        intersect = None
        obj = None
        for o in self.objects:
            inter = o.intersect(ray)
            if type(inter)!= None:
                # intersects
                if type(inter) == euclid.LineSegment3:
                    d = abs(ray.p - o.c)
                    if d > maxD:
                        maxD = d
                        obj = o
                        # if inter is a line segment. We require the closer point.
                        L1 = abs(ray.p - inter.p1)
                        L2 = abs(ray.p - inter.p2)
                        if L1 > L2:
                            intersect = inter.p1
                        else:
                            intersect = inter.p2
                elif type(inter) == euclid.Point3:
                    d = abs(inter - ray.p)
                    if d > maxD:
                        maxD = d
                        obj = o
                        intersect = inter
                        
        if obj == None:
            return None,None
        else:
            return intersect, obj

    def trace(self, ray, intensity, depth = 0):
        depth -= 1
        if depth < 0:
            return RayColor(intensity, self.BackgroundColor)
        point, obj = self.findIntersect(ray)
        if obj == None: # no intersections
            return RayColor(intensity, self.BackgroundColor)
        if obj.reflectionIndex == 0.0:
            return self.getColor(point, obj, intensity)
        # otherwise shoot off reflected rays
        col1 = self.getColor(point, obj, (1 - obj.reflectionIndex)*intensity)
        col2 = self.trace(reflect(point, obj, ray), intensity * obj.reflectionIndex, depth)
        return blend(col1, col2)


if __name__=="__main__":
    #import rpdb2; rpdb2.start_embedded_debugger('1234')
    start = time()
    w = 180
    scene = Scene()
    scene.objects.append(RaycastingSphere(euclid.Point3(-50, 0, 0), 2.0))
    #scene.objects.append(RaycastingPlane(euclid.Plane(euclid.Point3(1,1,1), euclid.Vector3(0.0,1.0,1.0))))
    im = Image.new("RGB", (w, w), (0,0,255))
    pixels = im.load()
    for x, y, point in scene.camera.getPixelCoords(w, w):
        color = scene.trace(euclid.Ray3(point, point-scene.camera.focus), 1.0, 1)
        if color.__class__.__name__ == "RayColor":
            pixels[x,y] = color.toRGB()
        elif type(color)==tuple:
            pixels[x,y] = color
        else:
            raise TypeError("unknown color type: " + str(type(color)) + " containing:\n" + repr(color))
    if not len(distances) < 2:
        print "average:" + str(reduce(lambda x,y: x + y, distances)/float(len(distances)))
        print "min:" + str(reduce(lambda x,y: x if x < y else y, distances))
        distances.insert(0, 0.0)
        print "number of 0.0s:" + str(reduce(lambda x,y: x+1 if y == 0.0 else x, distances))
    #im.save("/home/skyrunner/upload/imgs/test.png")
    im.save("out/test.png")
    end = time()
    print "Took %.2f seconds." % (end - start)