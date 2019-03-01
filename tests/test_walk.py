import unittest

from .helper import parse
import gpxpy as mod_gpxpy


class TestWalk(unittest.TestCase):
    def test_walk_route_points(self):
        with open('test_files/route.gpx') as f:
            gpx = mod_gpxpy.parse(f)

        for point in gpx.routes[0].walk(only_points=True):
            self.assertTrue(point)

        for point, point_no in gpx.routes[0].walk():
            self.assertTrue(point)

        self.assertEqual(point_no, len(gpx.routes[0].points) - 1)

    def test_walk_gpx_points(self):
        gpx = parse('korita-zbevnica.gpx')

        for point in gpx.walk():
            self.assertTrue(point)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point)

        self.assertEqual(track_no, len(gpx.tracks) - 1)
        self.assertEqual(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEqual(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)

    def test_walk_gpx_points2(self):
        gpx = parse('korita-zbevnica.gpx')
        track = gpx.tracks[1]

        for point in track.walk():
            self.assertTrue(point)

        for point, segment_no, point_no in track.walk():
            self.assertTrue(point)

        self.assertEqual(segment_no, len(track.segments) - 1)
        self.assertEqual(point_no, len(track.segments[-1].points) - 1)

    def test_walk_segment_points(self):
        gpx = parse('korita-zbevnica.gpx')
        track = gpx.tracks[1]
        segment = track.segments[0]

        assert len(segment.points) > 0

        for point in segment.walk():
            self.assertTrue(point)

        """
        for point, segment_no, point_no in track.walk():
            self.assertTrue(point)

        self.assertEqual(segment_no, len(track.segments) - 1)
        self.assertEqual(point_no, len(track.segments[-1].points) - 1)
        """
