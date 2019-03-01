import unittest

import gpxpy.geo as mod_geo


class TestHaversine(unittest.TestCase):
    def test_haversine_and_nonhaversine(self):
        haversine_dist = mod_geo.distance(0, 0, 0, 0.1, 0.1, 0, haversine=True)
        nonhaversine_dist = mod_geo.distance(0, 0, 0, 0.1, 0.1, 0, haversine=False)

        print("haversine_dist=", haversine_dist)
        print("nonhaversine_dist=", nonhaversine_dist)

        self.assertTrue(haversine_dist != nonhaversine_dist)
        self.assertTrue(abs(haversine_dist - nonhaversine_dist) < 15)

    def test_haversine_distance(self):
        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(2, 3)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.distance(loc1.latitude, loc1.longitude, None, loc2.latitude, loc2.longitude, None))

        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(3, 4)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.distance(loc1.latitude, loc1.longitude, None, loc2.latitude, loc2.longitude, None))

        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(3.1, 4)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.haversine_distance(loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude))

        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(2, 4.1)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.haversine_distance(loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude))
