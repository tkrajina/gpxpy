import unittest
import datetime as mod_datetime

import gpxpy as mod_gpxpy


class TestTimezone(unittest.TestCase):
    def test_remove_timezone_from_timestamp(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<gpx>
<trk>
<trkseg>
<trkpt lat="35.794159" lon="-5.832745"><time>2014-02-02T10:23:18Z+01:00</time></trkpt>
</trkseg></trk></gpx>"""
        gpx = mod_gpxpy.parse(xml)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2014, 2, 2, 10, 23, 18))

    def test_timestamp_with_single_digits(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<gpx>
<trk>
<trkseg>
<trkpt lat="35.794159" lon="-5.832745"><time>2014-2-2T2:23:18Z-02:00</time></trkpt>
</trkseg></trk></gpx>"""
        gpx = mod_gpxpy.parse(xml)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2014, 2, 2, 2, 23, 18))
