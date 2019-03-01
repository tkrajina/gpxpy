import unittest
import datetime as mod_datetime

from .helper import parse, reparse, equals


class TestWaypoints(unittest.TestCase):
    def test_waypoints_equality_after_reparse(self):
        gpx = parse('cerknicko-jezero.gpx')
        gpx2 = reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

    def test_waypoint_time(self):
        gpx = parse('cerknicko-jezero.gpx')

        self.assertTrue(gpx.waypoints[0].time)
        self.assertTrue(isinstance(gpx.waypoints[0].time, mod_datetime.datetime))
