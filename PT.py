import adsk.core, adsk.fusion, adsk.cam
from . import NS

class ProfileTools():
    def __init__(self) -> None:
        pass

    def pLoopDetails(self, ploop):
        msg = "\n%s: %s" % (
            "outer" if ploop.isOuter else "inner",
            ploop.parentProfile.areaProperties().area
        )

        for j in range(ploop.profileCurves.count):
            curve = ploop.profileCurves.item(j)
            line = adsk.fusion.SketchLine.cast(curve.sketchEntity)
            if line:
                s = line.startSketchPoint.geometry
                e = line.endSketchPoint.geometry
                msg += "\n  [%5.2f,%5.2f]->[%5.2f,%5.2f]" % (
                    s.x, s.y,e.x,e.y 
                )
        return msg

    def getIntersections(self, line, curves):
        points = adsk.core.ObjectCollection.create()
        for i in range(curves.count):
            curve = curves.item(i).geometry
            pnts = line.intersectWithCurve(curve)
            for j in range(pnts.count):
                c = pnts.item(j)
                for k in range(points.count):
                    e = points.item(k)
                    if e.x == c.x and e.y == c.y and e.z == c.z:
                        c = None
                        break
                if c: 
                    points.add(c)

        return points

    def findIntersections(self, centroid, profile ):
        global _ui
        sketch = adsk.fusion.Sketch.cast(profile.parentSketch)
        profile = adsk.fusion.Profile.cast(profile)
        outerPoint = profile.boundingBox.maxPoint
        pCurves = profile.profileLoops.item(0).profileCurves
        line = adsk.core.Line3D.create(outerPoint, centroid)
        points = self.getIntersections(line, pCurves)
        if points.count == 0:
            outerPoint = profile.boundingBox.minPoint
            line = adsk.core.Line3D.create(outerPoint, centroid)
            points = self.getIntersections(line, pCurves)

        # don't beleive it is possible in euclidian space for not found second time
        return points

    def midPoint(self, pnt0, pnt1):
        ax = (pnt0.x + pnt1.x) / 2
        ay = (pnt0.y + pnt1.y) / 2
        az = (pnt0.z + pnt1.z) / 2
    
        return adsk.core.Point3D.create(ax, ay, az)

    def findInsidePoint(self, profile ):
        # best guesss at point inside
        centroid = profile.areaProperties().centroid
        
        for i in range(10):
            points = self.findIntersections(centroid, profile)
            # if number of intersecting points is odd, the centroid is inside
            if (points.count % 2) == 1:
                return centroid
            #else guess at new centroid
            centroid = self.midPoint(points.item(0), points.item(1))
            
        return None

    def containsProfile(self, outer, profile):
        # return outer.boundingBox.intersects(profile.boundingBox)
        points = None
        insidePnt = self.findInsidePoint( profile)
        if insidePnt:
            points = self.findIntersections(insidePnt, outer)
            # if number of intersecting points is odd, the profile is inside
            if (points.count % 2) == 1:
                return True

        return False

    def offsetProfiles(self, topProfile, kerf_width, deleteProfiles=False):
        sketch = adsk.fusion.Sketch.cast(topProfile.parentSketch)
        pCurves = topProfile.profileLoops.item(0).profileCurves
        kerfs = [NS.Namespace(
            curve=pCurves.item(0).sketchEntity, 
            point=self.findInsidePoint(topProfile),
            offset = -kerf_width
        )]

        for i in range(sketch.profiles.count):
            profile = sketch.profiles.item(i)
            if  profile != topProfile and self.containsProfile(topProfile, profile):

                pCurves = profile.profileLoops.item(0).profileCurves
                kerfs.append(NS.Namespace(
                    curve=pCurves.item(0).sketchEntity, 
                    point=self.findInsidePoint(profile),
                    offset = kerf_width
                ))

        for kerf in kerfs:
            curves = sketch.findConnectedCurves(kerf.curve)
            sketch.offset(curves, kerf.point, kerf.offset)

            if deleteProfiles:
                for i in range(curves.count):
                    curves.item(i).deleteMe()


    
        
