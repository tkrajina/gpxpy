import unittest

from .helper import parse


class TestNamedTuples(unittest.TestCase):
    def test_named_tuples_values_time_bounds(self):
        gpx = parse('korita-zbevnica.gpx')

        time_bounds = gpx.get_time_bounds()
        start_time, end_time = gpx.get_time_bounds()

        self.assertEqual(start_time, time_bounds.start_time)
        self.assertEqual(end_time, time_bounds.end_time)

    def test_named_tuples_values_moving_data(self):
        gpx = parse('korita-zbevnica.gpx')

        moving_data = gpx.get_moving_data()
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx.get_moving_data()
        self.assertEqual(moving_time, moving_data.moving_time)
        self.assertEqual(stopped_time, moving_data.stopped_time)
        self.assertEqual(moving_distance, moving_data.moving_distance)
        self.assertEqual(stopped_distance, moving_data.stopped_distance)
        self.assertEqual(max_speed, moving_data.max_speed)

    def test_named_tuples_values_uphill_downhill(self):
        gpx = parse('korita-zbevnica.gpx')

        uphill_downhill = gpx.get_uphill_downhill()
        uphill, downhill = gpx.get_uphill_downhill()
        self.assertEqual(uphill, uphill_downhill.uphill)
        self.assertEqual(downhill, uphill_downhill.downhill)

    def test_named_tuples_values_elevation_extremes(self):
        gpx = parse('korita-zbevnica.gpx')

        elevation_extremes = gpx.get_elevation_extremes()
        minimum, maximum = gpx.get_elevation_extremes()
        self.assertEqual(minimum, elevation_extremes.minimum)
        self.assertEqual(maximum, elevation_extremes.maximum)

    def test_named_tuples_values_nearest_location_data(self):
        gpx = parse('korita-zbevnica.gpx')

        location = gpx.tracks[1].segments[0].points[2]
        location.latitude *= 1.00001
        location.longitude *= 0.99999
        nearest_location_data = gpx.get_nearest_location(location)
        found_location, track_no, segment_no, point_no = gpx.get_nearest_location(location)
        self.assertEqual(found_location, nearest_location_data.location)
        self.assertEqual(track_no, nearest_location_data.track_no)
        self.assertEqual(segment_no, nearest_location_data.segment_no)
        self.assertEqual(point_no, nearest_location_data.point_no)

    def test_named_tuples_values_point_data(self):
        gpx = parse('korita-zbevnica.gpx')

        points_datas = gpx.get_points_data()

        for point_data in points_datas:
            point, distance_from_start, track_no, segment_no, point_no = point_data
            self.assertEqual(point, point_data.point)
            self.assertEqual(distance_from_start, point_data.distance_from_start)
            self.assertEqual(track_no, point_data.track_no)
            self.assertEqual(segment_no, point_data.segment_no)
            self.assertEqual(point_no, point_data.point_no)
