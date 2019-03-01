import unittest
import datetime as mod_datetime
import math as mod_math

from .helper import parse

import gpxpy.gpx as mod_gpx
from gpxpy.utils import total_seconds


class TestGpxFill(unittest.TestCase):
    def test_gpx_fill_time_data_with_start_time_and_end_time(self):
        gpx = parse('cerknicko-jezero.gpx')

        start_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)
        end_time = mod_datetime.datetime(2018, 7, 4, 1, 0, 0)

        gpx.fill_time_data_with_regular_intervals(start_time=start_time, end_time=end_time)
        time_bounds = gpx.get_time_bounds()

        tolerance = 1.0
        start_time_diff = total_seconds(time_bounds.start_time - start_time)
        end_time_diff = total_seconds(time_bounds.end_time - end_time)
        self.assertLessEqual(mod_math.fabs(start_time_diff), tolerance)
        self.assertLessEqual(mod_math.fabs(end_time_diff), tolerance)

    def test_gpx_fill_time_data_with_start_time_and_end_time_and_time_delta(self):
        gpx = parse('cerknicko-jezero.gpx')

        start_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)
        time_delta = mod_datetime.timedelta(seconds=60)
        end_time = mod_datetime.datetime(2018, 7, 4, 1, 0, 0)

        gpx.fill_time_data_with_regular_intervals(start_time=start_time, time_delta=time_delta, end_time=end_time)
        time_bounds = gpx.get_time_bounds()

        tolerance = 1.0
        start_time_diff = total_seconds(time_bounds.start_time - start_time)
        end_time_diff = total_seconds(time_bounds.end_time - end_time)
        self.assertLessEqual(mod_math.fabs(start_time_diff), tolerance)
        self.assertLessEqual(mod_math.fabs(end_time_diff), tolerance)

    def test_gpx_fill_time_data_with_start_time_and_time_delta(self):
        gpx = parse('cerknicko-jezero.gpx')

        start_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)
        time_delta = mod_datetime.timedelta(seconds=1)
        end_time = start_time + (gpx.get_points_no() - 1) * time_delta

        gpx.fill_time_data_with_regular_intervals(start_time=start_time, time_delta=time_delta)
        time_bounds = gpx.get_time_bounds()

        tolerance = 1.0
        start_time_diff = total_seconds(time_bounds.start_time - start_time)
        end_time_diff = total_seconds(time_bounds.end_time - end_time)
        self.assertLessEqual(mod_math.fabs(start_time_diff), tolerance)
        self.assertLessEqual(mod_math.fabs(end_time_diff), tolerance)

    def test_gpx_fill_time_data_with_end_time_and_time_delta(self):
        gpx = parse('cerknicko-jezero.gpx')

        end_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)
        time_delta = mod_datetime.timedelta(seconds=1)
        start_time = end_time - (gpx.get_points_no() - 1) * time_delta

        gpx.fill_time_data_with_regular_intervals(time_delta=time_delta, end_time=end_time)
        time_bounds = gpx.get_time_bounds()

        tolerance = 1.0
        start_time_diff = total_seconds(time_bounds.start_time - start_time)
        end_time_diff = total_seconds(time_bounds.end_time - end_time)
        self.assertLessEqual(mod_math.fabs(start_time_diff), tolerance)
        self.assertLessEqual(mod_math.fabs(end_time_diff), tolerance)

    def test_gpx_fill_time_data_raises_when_not_enough_parameters(self):
        gpx = parse('cerknicko-jezero.gpx')

        start_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)

        with self.assertRaises(mod_gpx.GPXException):
            gpx.fill_time_data_with_regular_intervals(start_time=start_time)

    def test_gpx_fill_time_data_raises_when_start_time_after_end_time(self):
        gpx = parse('cerknicko-jezero.gpx')

        start_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)
        end_time = mod_datetime.datetime(2018, 7, 3, 0, 0, 0)

        with self.assertRaises(mod_gpx.GPXException):
            gpx.fill_time_data_with_regular_intervals(start_time=start_time, end_time=end_time)

    def test_gpx_fill_time_data_raises_when_force_is_false(self):
        gpx = parse('Mojstrovka.gpx')

        start_time = mod_datetime.datetime(2018, 7, 4, 0, 0, 0)
        end_time = mod_datetime.datetime(2018, 7, 4, 1, 0, 0)

        gpx.fill_time_data_with_regular_intervals(start_time=start_time, end_time=end_time)

        with self.assertRaises(mod_gpx.GPXException):
            gpx.fill_time_data_with_regular_intervals(start_time=start_time, end_time=end_time, force=False)
