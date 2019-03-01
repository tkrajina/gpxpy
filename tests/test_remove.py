import unittest
import datetime as mod_datetime

from .helper import parse, equals
import gpxpy.gpx as mod_gpx
import gpxpy.parser as mod_parser


class TestRemove(unittest.TestCase):
    def test_remove_elevation(self):
        gpx = parse('cerknicko-jezero.gpx')

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.elevation is not None)

        gpx.remove_elevation(tracks=True, waypoints=True, routes=True)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.elevation is None)

        xml = gpx.to_xml()

        self.assertFalse('<ele>' in xml)

    def test_remove_time_tracks_only(self):
        gpx = parse('cerknicko-jezero.gpx')

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time is not None)

        gpx.remove_time()

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time is None)

    def test_remove_time_all(self):
        gpx = mod_gpx.GPX()

        t0 = mod_datetime.datetime(2018, 7, 15, 12, 30, 0)
        t1 = mod_datetime.datetime(2018, 7, 15, 12, 31, 0)

        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0, time=t0)
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1, time=t1)
        gpx.tracks[0].segments[0].points.append(p0)
        gpx.tracks[0].segments[0].points.append(p1)

        gpx.waypoints.append(mod_gpx.GPXWaypoint(latitude=13.0, longitude=13.0, time=t0))
        gpx.waypoints.append(mod_gpx.GPXWaypoint(latitude=13.1, longitude=13.1, time=t1))

        gpx.routes.append(mod_gpx.GPXRoute())
        p0 = mod_gpx.GPXRoutePoint(latitude=13.0, longitude=13.0, time=t0)
        p1 = mod_gpx.GPXRoutePoint(latitude=13.1, longitude=13.1, time=t1)
        gpx.routes[0].points.append(p0)
        gpx.routes[0].points.append(p1)

        gpx.remove_time(all=True)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time is None)

        for point in gpx.waypoints:
            self.assertTrue(point.time is None)

        for route in gpx.routes:
            for point, _ in route.walk():
                self.assertTrue(point.time is None)

    def test_remove_point_from_segment(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        track = gpx.tracks[1]
        segment = track.segments[0]
        original_segment = segment.clone()

        segment.remove_point(3)
        print(segment.points[0])
        print(original_segment.points[0])
        self.assertTrue(equals(segment.points[0], original_segment.points[0]))
        self.assertTrue(equals(segment.points[1], original_segment.points[1]))
        self.assertTrue(equals(segment.points[2], original_segment.points[2]))
        # ...but:
        self.assertTrue(equals(segment.points[3], original_segment.points[4]))

        self.assertTrue(len(segment.points) + 1 == len(original_segment.points))
