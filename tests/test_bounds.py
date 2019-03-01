import unittest
import datetime as mod_datetime
import random as mod_random

import gpxpy.gpx as mod_gpx


class TestBounds(unittest.TestCase):
    def test_bounds(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()

        segment_1 = mod_gpx.GPXTrackSegment()
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=13))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-100, longitude=-5))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=100, longitude=-13))
        track.segments.append(segment_1)

        segment_2 = mod_gpx.GPXTrackSegment()
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=100))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-10, longitude=-5))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=10, longitude=-100))
        track.segments.append(segment_2)

        gpx.tracks.append(track)

        bounds = gpx.get_bounds()

        self.assertEqual(bounds.min_latitude, -100)
        self.assertEqual(bounds.max_latitude, 100)
        self.assertEqual(bounds.min_longitude, -100)
        self.assertEqual(bounds.max_longitude, 100)

        # Test refresh bounds:

        gpx.refresh_bounds()
        self.assertEqual(gpx.bounds.min_latitude, -100)
        self.assertEqual(gpx.bounds.max_latitude, 100)
        self.assertEqual(gpx.bounds.min_longitude, -100)
        self.assertEqual(gpx.bounds.max_longitude, 100)

    def test_time_bounds(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()

        segment_1 = mod_gpx.GPXTrackSegment()
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=13))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-100, longitude=-5, time=mod_datetime.datetime(2001, 1, 12)))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=100, longitude=-13, time=mod_datetime.datetime(2003, 1, 12)))
        track.segments.append(segment_1)

        segment_2 = mod_gpx.GPXTrackSegment()
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=100, time=mod_datetime.datetime(2010, 1, 12)))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-10, longitude=-5, time=mod_datetime.datetime(2011, 1, 12)))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=10, longitude=-100))
        track.segments.append(segment_2)

        gpx.tracks.append(track)

        bounds = gpx.get_time_bounds()

        self.assertEqual(bounds.start_time, mod_datetime.datetime(2001, 1, 12))
        self.assertEqual(bounds.end_time, mod_datetime.datetime(2011, 1, 12))

    def test_get_bounds_and_refresh_bounds(self):
        gpx = mod_gpx.GPX()

        latitudes = []
        longitudes = []

        for i in range(2):
            track = mod_gpx.GPXTrack()
            for i in range(2):
                segment = mod_gpx.GPXTrackSegment()
                for i in range(10):
                    latitude = 50. * (mod_random.random() - 0.5)
                    longitude = 50. * (mod_random.random() - 0.5)
                    point = mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude)
                    segment.points.append(point)
                    latitudes.append(latitude)
                    longitudes.append(longitude)
                track.segments.append(segment)
            gpx.tracks.append(track)

        bounds = gpx.get_bounds()

        print(latitudes)
        print(longitudes)

        self.assertEqual(bounds.min_latitude, min(latitudes))
        self.assertEqual(bounds.max_latitude, max(latitudes))
        self.assertEqual(bounds.min_longitude, min(longitudes))
        self.assertEqual(bounds.max_longitude, max(longitudes))

        gpx.refresh_bounds()

        self.assertEqual(gpx.bounds.min_latitude, min(latitudes))
        self.assertEqual(gpx.bounds.max_latitude, max(latitudes))
        self.assertEqual(gpx.bounds.min_longitude, min(longitudes))
        self.assertEqual(gpx.bounds.max_longitude, max(longitudes))
