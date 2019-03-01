import math as mod_math

import unittest

import gpxpy.geo as mod_geo


class TestAngle(unittest.TestCase):
    def test_angle_0(self):
        loc1 = mod_geo.Location(0, 0)
        loc2 = mod_geo.Location(0, 1)

        loc1.elevation = 100
        loc2.elevation = 100

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEqual(angle_radians, 0)
        self.assertEqual(angle_degrees, 0)

    def test_angle(self):
        loc1 = mod_geo.Location(0, 0)
        loc2 = mod_geo.Location(0, 1)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEqual(angle_radians, mod_math.pi / 4)
        self.assertEqual(angle_degrees, 45)

    def test_angle_2(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + 0.5 * loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertTrue(angle_radians < mod_math.pi / 4)
        self.assertTrue(angle_degrees < 45)

    def test_angle_3(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + 1.5 * loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertTrue(angle_radians > mod_math.pi / 4)
        self.assertTrue(angle_degrees > 45)

    def test_angle_4(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation - loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEqual(angle_radians, - mod_math.pi / 4)
        self.assertEqual(angle_degrees, - 45)

    def test_angle_loc(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        self.assertEqual(loc1.elevation_angle(loc2), mod_geo.elevation_angle(loc1, loc2))
        self.assertEqual(loc1.elevation_angle(loc2, radians=True), mod_geo.elevation_angle(loc1, loc2, radians=True))
        self.assertEqual(loc1.elevation_angle(loc2, radians=False), mod_geo.elevation_angle(loc1, loc2, radians=False))
