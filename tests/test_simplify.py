import unittest
import os as mod_os

from .helper import custom_open
import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx


class TestSimplify(unittest.TestCase):
    def test_simplify(self):
        for gpx_file in mod_os.listdir('test_files'):
            print('Parsing:', gpx_file)
            with custom_open('test_files/%s' % gpx_file, encoding='utf-8')as f:
                gpx = mod_gpxpy.parse(f)

            length_2d_original = gpx.length_2d()

            with custom_open('test_files/%s' % gpx_file, encoding='utf-8') as f:
                gpx = mod_gpxpy.parse(f)
            gpx.simplify(max_distance=50)
            length_2d_after_distance_50 = gpx.length_2d()

            with custom_open('test_files/%s' % gpx_file, encoding='utf-8') as f:
                gpx = mod_gpxpy.parse(f)
            gpx.simplify(max_distance=10)
            length_2d_after_distance_10 = gpx.length_2d()

            print(length_2d_original, length_2d_after_distance_10, length_2d_after_distance_50)

            # When simplifying the resulting distance should always be less than the original:
            self.assertTrue(length_2d_original >= length_2d_after_distance_10)
            self.assertTrue(length_2d_original >= length_2d_after_distance_50)

            # Simplify with bigger max_distance and => bigger error from original
            self.assertTrue(length_2d_after_distance_10 >= length_2d_after_distance_50)

            # The resulting distance usually shouldn't be too different from
            # the original (here check for 80% and 70%)
            self.assertTrue(length_2d_after_distance_10 >= length_2d_original * .6)
            self.assertTrue(length_2d_after_distance_50 >= length_2d_original * .5)

    def test_simplify_circular_gpx(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13, longitude=12))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.25, longitude=12))

        # Then the first point again:
        gpx.tracks[0].segments[0].points.append(gpx.tracks[0].segments[0].points[0])

        gpx.simplify()
