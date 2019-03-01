import unittest
import math as mod_math

import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx


class TestElevation(unittest.TestCase):
    def test_track_with_elevation_zero(self):
        with open('test_files/cerknicko-jezero-with-elevations-zero.gpx') as f:
            gpx = mod_gpxpy.parse(f)

            minimum, maximum = gpx.get_elevation_extremes()
            self.assertEqual(minimum, 0)
            self.assertEqual(maximum, 0)

            uphill, downhill = gpx.get_uphill_downhill()
            self.assertEqual(uphill, 0)
            self.assertEqual(downhill, 0)

    def test_track_without_elevation(self):
        with open('test_files/cerknicko-jezero-without-elevations.gpx') as f:
            gpx = mod_gpxpy.parse(f)

            minimum, maximum = gpx.get_elevation_extremes()
            self.assertEqual(minimum, None)
            self.assertEqual(maximum, None)

            uphill, downhill = gpx.get_uphill_downhill()
            self.assertEqual(uphill, 0)
            self.assertEqual(downhill, 0)

    def test_has_elevation_false(self):
        with open('test_files/cerknicko-jezero-without-elevations.gpx') as f:
            gpx = mod_gpxpy.parse(f)
            self.assertFalse(gpx.has_elevations())

    def test_has_elevation_true(self):
        with open('test_files/cerknicko-jezero.gpx') as f:
            gpx = mod_gpxpy.parse(f)
            self.assertFalse(gpx.has_elevations())

    def test_track_with_some_points_are_without_elevations(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        tmp_latlong = 0
        segment_1 = mod_gpx.GPXTrackSegment()
        for i in range(4):
            point = mod_gpx.GPXTrackPoint(latitude=tmp_latlong, longitude=tmp_latlong)
            segment_1.points.append(point)
            if i % 3 == 0:
                point.elevation = None
            else:
                point.elevation = 100 / (i + 1)

        track.segments.append(segment_1)

        minimum, maximum = gpx.get_elevation_extremes()
        self.assertTrue(minimum is not None)
        self.assertTrue(maximum is not None)

        uphill, downhill = gpx.get_uphill_downhill()
        self.assertTrue(uphill is not None)
        self.assertTrue(downhill is not None)

    def test_add_elevation(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13, elevation=100))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13))

        gpx.add_elevation(10)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 110)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].elevation, None)

        gpx.add_elevation(-20)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 90)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].elevation, None)

    def test_nan_elevation(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<gpx>
    <wpt lat="12" lon="13">
        <ele>nan</ele>
    </wpt>
    <rte>
        <rtept lat="12" lon="13">
            <ele>nan</ele>
        </rtept>
    </rte>
    <trk>
        <name/>
        <desc/>
        <trkseg>
            <trkpt lat="12" lon="13">
                <ele>nan</ele>
            </trkpt>
        </trkseg>
    </trk>
</gpx>"""
        gpx = mod_gpxpy.parse(xml)

        self.assertTrue(mod_math.isnan(gpx.tracks[0].segments[0].points[0].elevation))
        self.assertTrue(mod_math.isnan(gpx.routes[0].points[0].elevation))
        self.assertTrue(mod_math.isnan(gpx.waypoints[0].elevation))
