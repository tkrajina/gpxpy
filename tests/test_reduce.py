import unittest
import time as mod_time
import sys as mod_sys

import gpxpy as mod_gpxpy
import gpxpy.parser as mod_parser


class TestReduce(unittest.TestCase):
    def test_reduce_gpx_file(self):
        f = open('test_files/Mojstrovka.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        max_reduced_points_no = 50

        started = mod_time.time()
        points_original = gpx.get_track_points_no()
        time_original = mod_time.time() - started

        gpx.reduce_points(max_reduced_points_no)

        points_reduced = gpx.get_track_points_no()

        result = gpx.to_xml()
        if mod_sys.version_info[0] != 3:
            result = result.encode('utf-8')

        started = mod_time.time()
        parser = mod_parser.GPXParser(result)
        parser.parse()
        time_reduced = mod_time.time() - started

        print(time_original)
        print(points_original)

        print(time_reduced)
        print(points_reduced)

        self.assertTrue(points_reduced < points_original)
        self.assertTrue(points_reduced < max_reduced_points_no)

    def test_reduce_by_min_distance(self):
        with open('test_files/cerknicko-jezero.gpx') as f:
            gpx = mod_gpxpy.parse(f)

        min_distance_before_reduce = 1000000
        for point, track_no, segment_no, point_no in gpx.walk():
            if point_no > 0:
                previous_point = gpx.tracks[track_no].segments[segment_no].points[point_no - 1]
                if point.distance_3d(previous_point) < min_distance_before_reduce:
                    min_distance_before_reduce = point.distance_3d(previous_point)

        gpx.reduce_points(min_distance=10)

        min_distance_after_reduce = 1000000
        for point, track_no, segment_no, point_no in gpx.walk():
            if point_no > 0:
                previous_point = gpx.tracks[track_no].segments[segment_no].points[point_no - 1]
                if point.distance_3d(previous_point) < min_distance_after_reduce:
                    min_distance_after_reduce = point.distance_3d(previous_point)

        self.assertTrue(min_distance_before_reduce < min_distance_after_reduce)
        self.assertTrue(min_distance_before_reduce < 10)
        self.assertTrue(10 < min_distance_after_reduce)
