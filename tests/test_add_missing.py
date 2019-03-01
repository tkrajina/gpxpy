import unittest
import datetime as mod_datetime

import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx


class TestAddMissing(unittest.TestCase):
    def test_add_missing_data_no_intervals(self):
        # Test only that the add_missing_function is called with the right data
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=14,
                                                                      elevation=100))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=15,
                                                                      elevation=20))

        # Shouldn't be called because all points have elevation
        def _add_missing_function(interval, start_point, end_point, ratios):
            raise Exception()

        gpx.add_missing_data(get_data_function=lambda point: point.elevation,
                             add_missing_function=_add_missing_function)

    def test_add_missing_data_one_interval(self):
        # Test only that the add_missing_function is called with the right data
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=14,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=15,
                                                                      elevation=20))

        # Shouldn't be called because all points have elevation
        def _add_missing_function(interval, start_point, end_point, ratios):
            assert start_point
            assert start_point.latitude == 12 and start_point.longitude == 13
            assert end_point
            assert end_point.latitude == 12 and end_point.longitude == 15
            assert len(interval) == 1
            assert interval[0].latitude == 12 and interval[0].longitude == 14
            assert ratios
            interval[0].elevation = 314

        gpx.add_missing_data(get_data_function=lambda point: point.elevation,
                             add_missing_function=_add_missing_function)

        self.assertEqual(314, gpx.tracks[0].segments[0].points[1].elevation)

    def test_add_missing_data_one_interval_and_empty_points_on_start_and_end(self):
        # Test only that the add_missing_function is called with the right data
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=14,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=15,
                                                                      elevation=20))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=None))

        # Shouldn't be called because all points have elevation
        def _add_missing_function(interval, start_point, end_point, ratios):
            assert start_point
            assert start_point.latitude == 12 and start_point.longitude == 13
            assert end_point
            assert end_point.latitude == 12 and end_point.longitude == 15
            assert len(interval) == 1
            assert interval[0].latitude == 12 and interval[0].longitude == 14
            assert ratios
            interval[0].elevation = 314

        gpx.add_missing_data(get_data_function=lambda point: point.elevation,
                             add_missing_function=_add_missing_function)

        # Points at start and end should not have elevation 314 because have
        # no two bounding points with elevations:
        self.assertEqual(None, gpx.tracks[0].segments[0].points[0].elevation)
        self.assertEqual(None, gpx.tracks[0].segments[0].points[-1].elevation)

        self.assertEqual(314, gpx.tracks[0].segments[0].points[2].elevation)

    def test_add_missing_speeds(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0,
                                                                      time=mod_datetime.datetime(2013, 1, 2, 12, 0),
                                                                      speed=0))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.00899,  # 1 km/h over 1 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 13, 0)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.02697,  # 2 km/h over 2 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 14, 0)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.03596,  # 3 km/h over 1 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 14, 20)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.06293,  # 9 km/h over 3 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 14, 40),
                                                                      speed=0))
        gpx.add_missing_speeds()

        self.assertTrue(abs(3000. / (2 * 3600) - gpx.tracks[0].segments[0].points[1].speed) < 0.01)
        self.assertTrue(abs(3000. / (80 * 60) - gpx.tracks[0].segments[0].points[2].speed) < 0.01)
        self.assertTrue(abs(4000. / (40 * 60) - gpx.tracks[0].segments[0].points[3].speed) < 0.01)

    def test_add_missing_elevations(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.25, longitude=12,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.5, longitude=12,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.9, longitude=12,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=14, longitude=12,
                                                                      elevation=20))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=15, longitude=12,
                                                                      elevation=None))

        gpx.add_missing_elevations()

        self.assertTrue(abs(12.5 - gpx.tracks[0].segments[0].points[1].elevation) < 0.01)
        self.assertTrue(abs(15 - gpx.tracks[0].segments[0].points[2].elevation) < 0.01)
        self.assertTrue(abs(19 - gpx.tracks[0].segments[0].points[3].elevation) < 0.01)

    def test_add_missing_elevations_without_ele(self):
        xml = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx>
    <trk>
        <trkseg>
            <trkpt lat="65.263305" lon="-14.003859"><time>2017-03-06T01:47:34Z</time></trkpt>
            <trkpt lat="65.263383" lon="-14.003636"><time>2017-03-06T01:47:37Z</time></trkpt>
            <trkpt lat="65.26368" lon="-14.002705"><ele>0.0</ele><time>2017-03-06T01:47:46Z</time></trkpt>
        </trkseg>
    </trk>
</gpx>"""
        gpx = mod_gpxpy.parse(xml)
        gpx.add_missing_elevations()

        self.assertTrue(gpx.tracks[0].segments[0].points[0].elevation is None)
        self.assertTrue(gpx.tracks[0].segments[0].points[1].elevation is None)
        self.assertTrue(gpx.tracks[0].segments[0].points[2].elevation == 0.0)

    def test_add_missing_times(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                                                      time=mod_datetime.datetime(2013, 1, 2, 12, 0)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.25, longitude=12,
                                                                      time=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.5, longitude=12,
                                                                      time=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.75, longitude=12,
                                                                      time=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=14, longitude=12,
                                                                      time=mod_datetime.datetime(2013, 1, 2, 13, 0)))

        gpx.add_missing_times()

        time_1 = gpx.tracks[0].segments[0].points[1].time
        time_2 = gpx.tracks[0].segments[0].points[2].time
        time_3 = gpx.tracks[0].segments[0].points[3].time

        self.assertEqual(2013, time_1.year)
        self.assertEqual(1, time_1.month)
        self.assertEqual(2, time_1.day)
        self.assertEqual(12, time_1.hour)
        self.assertEqual(15, time_1.minute)

        self.assertEqual(2013, time_2.year)
        self.assertEqual(1, time_2.month)
        self.assertEqual(2, time_2.day)
        self.assertEqual(12, time_2.hour)
        self.assertEqual(30, time_2.minute)

        self.assertEqual(2013, time_3.year)
        self.assertEqual(1, time_3.month)
        self.assertEqual(2, time_3.day)
        self.assertEqual(12, time_3.hour)
        self.assertEqual(45, time_3.minute)

    def test_add_missing_times_2(self):
        xml = ''
        xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<gpx>\n'
        xml += '<trk>\n'
        xml += '<trkseg>\n'
        xml += '<trkpt lat="35.794159" lon="-5.832745"><time>2014-02-02T10:23:18Z</time></trkpt>\n'
        xml += '<trkpt lat="35.7941046982" lon="-5.83285637909"></trkpt>\n'
        xml += '<trkpt lat="35.7914309254" lon="-5.83378314972"></trkpt>\n'
        xml += '<trkpt lat="35.791014" lon="-5.833826"><time>2014-02-02T10:25:30Z</time><ele>18</ele></trkpt>\n'
        xml += '</trkseg></trk></gpx>\n'
        gpx = mod_gpxpy.parse(xml)

        gpx.add_missing_times()

        previous_time = None
        for point in gpx.walk(only_points=True):
            if point.time:
                if previous_time:
                    print('point.time=', point.time, 'previous_time=', previous_time)
                    self.assertTrue(point.time > previous_time)
            previous_time = point.time
