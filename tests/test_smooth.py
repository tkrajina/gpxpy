import unittest

from .helper import parse
import gpxpy.parser as mod_parser


class TestSmooth(unittest.TestCase):
    def test_smooth_without_removing_extreemes_preserves_point_count_2(self):
        gpx = parse('first_and_last_elevation.gpx')
        list_len = len(list(gpx.walk()))
        gpx.smooth(vertical=False, horizontal=True)
        self.assertEqual(list_len, len(list(gpx.walk())))

    def test_smooth_without_removing_extreemes_preserves_point_count_3(self):
        gpx = parse('first_and_last_elevation.gpx')
        list_len = len(list(gpx.walk()))
        gpx.smooth(vertical=True, horizontal=True)
        self.assertEqual(list_len, len(list(gpx.walk())))

    def test_clone_and_smooth(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        original_2d = gpx.length_2d()
        original_3d = gpx.length_3d()

        cloned_gpx = gpx.clone()

        cloned_gpx.reduce_points(2000, min_distance=10)
        cloned_gpx.smooth(vertical=True, horizontal=True)
        cloned_gpx.smooth(vertical=True, horizontal=False)

        print('2d:', gpx.length_2d())
        print('2d cloned and smoothed:', cloned_gpx.length_2d())

        print('3d:', gpx.length_3d())
        print('3d cloned and smoothed:', cloned_gpx.length_3d())

        self.assertTrue(gpx.length_3d() == original_3d)
        self.assertTrue(gpx.length_2d() == original_2d)

        self.assertTrue(gpx.length_3d() > cloned_gpx.length_3d())
        self.assertTrue(gpx.length_2d() > cloned_gpx.length_2d())

    def test_horizontal_smooth_remove_extremes(self):
        with open('test_files/track-with-extremes.gpx', 'r') as f:

            parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=False, horizontal=True, remove_extremes=True)
        points_after = gpx.get_track_points_no()

        print(points_before)
        print(points_after)

        self.assertTrue(points_before - 2 == points_after)

    def test_vertical_smooth_remove_extremes(self):
        with open('test_files/track-with-extremes.gpx', 'r') as f:
            parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=True, horizontal=False, remove_extremes=True)
        points_after = gpx.get_track_points_no()

        print(points_before)
        print(points_after)

        self.assertTrue(points_before - 1 == points_after)

    def test_horizontal_and_vertical_smooth_remove_extremes(self):
        with open('test_files/track-with-extremes.gpx', 'r') as f:
            parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=True, horizontal=True, remove_extremes=True)
        points_after = gpx.get_track_points_no()

        print(points_before)
        print(points_after)

        self.assertTrue(points_before - 3 == points_after)

    def test_smooth_without_removing_extreemes_preserves_point_count(self):
        gpx = parse('first_and_last_elevation.gpx')
        list_len = len(list(gpx.walk()))
        gpx.smooth(vertical=True, horizontal=False)
        self.assertEqual(list_len, len(list(gpx.walk())))
