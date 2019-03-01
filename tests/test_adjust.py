import unittest
import datetime as mod_datetime

import gpxpy.gpx as mod_gpx


class TestAdjust(unittest.TestCase):
    def test_adjust_time_tracks_only(self):
        gpx = mod_gpx.GPX()

        t0 = mod_datetime.datetime(2013, 1, 2, 12, 30, 0)
        t1 = mod_datetime.datetime(2013, 1, 2, 12, 31, 0)
        t0_adjusted = t0 + mod_datetime.timedelta(seconds=1)
        t1_adjusted = t1 + mod_datetime.timedelta(seconds=1)

        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0)
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1)
        gpx.tracks[0].segments[0].points.append(p0)
        gpx.tracks[0].segments[0].points.append(p1)

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0, time=t0)
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1, time=t1)
        gpx.tracks[0].segments[1].points.append(p0)
        gpx.tracks[0].segments[1].points.append(p1)

        gpx.waypoints.append(mod_gpx.GPXWaypoint(latitude=13.0, longitude=13.0))
        gpx.waypoints.append(mod_gpx.GPXWaypoint(latitude=13.1, longitude=13.1, time=t0))

        d1 = mod_datetime.timedelta(-1, -1)
        d2 = mod_datetime.timedelta(1, 2)
        # move back and forward to add a total of 1 second
        gpx.adjust_time(d1)
        gpx.adjust_time(d2)

        self.assertEqual(gpx.tracks[0].segments[0].points[0].time, None)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].time, None)
        self.assertEqual(gpx.tracks[0].segments[1].points[0].time, t0_adjusted)
        self.assertEqual(gpx.tracks[0].segments[1].points[1].time, t1_adjusted)
        self.assertEqual(gpx.waypoints[0].time, None)
        self.assertEqual(gpx.waypoints[1].time, t0)

    def test_adjust_time_all(self):
        gpx = mod_gpx.GPX()

        t0 = mod_datetime.datetime(2018, 7, 15, 12, 30, 0)
        t1 = mod_datetime.datetime(2018, 7, 15, 12, 31, 0)
        t0_adjusted = t0 + mod_datetime.timedelta(seconds=1)
        t1_adjusted = t1 + mod_datetime.timedelta(seconds=1)

        gpx.waypoints.append(mod_gpx.GPXWaypoint(latitude=13.0, longitude=13.0))
        gpx.waypoints.append(mod_gpx.GPXWaypoint(latitude=13.1, longitude=13.1, time=t0))

        gpx.routes.append(mod_gpx.GPXRoute())
        p0 = mod_gpx.GPXRoutePoint(latitude=13.0, longitude=13.0)
        p1 = mod_gpx.GPXRoutePoint(latitude=13.1, longitude=13.1)
        gpx.routes[0].points.append(p0)
        gpx.routes[0].points.append(p1)

        gpx.routes.append(mod_gpx.GPXRoute())
        p0 = mod_gpx.GPXRoutePoint(latitude=13.0, longitude=13.0, time=t0)
        p1 = mod_gpx.GPXRoutePoint(latitude=13.1, longitude=13.1, time=t1)
        gpx.routes[1].points.append(p0)
        gpx.routes[1].points.append(p1)

        d1 = mod_datetime.timedelta(-1, -1)
        d2 = mod_datetime.timedelta(1, 2)
        # move back and forward to add a total of 1 second
        gpx.adjust_time(d1, all=True)
        gpx.adjust_time(d2, all=True)

        self.assertEqual(gpx.waypoints[0].time, None)
        self.assertEqual(gpx.waypoints[1].time, t0_adjusted)
        self.assertEqual(gpx.routes[0].points[0].time, None)
        self.assertEqual(gpx.routes[0].points[1].time, None)
        self.assertEqual(gpx.routes[1].points[0].time, t0_adjusted)
        self.assertEqual(gpx.routes[1].points[1].time, t1_adjusted)
