# Copyright 2011 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Regression tests for has_times() with empty track segments.

An empty track segment must not change a track's (or file's) time-data
status: GPXTrackSegment.has_times() returns True for an empty segment
precisely so that it is neutral under AND aggregation, see the comment
in gpxpy/gpx.py. A GPX file whose points have no timestamps must
therefore keep reporting has_times() == False even when an empty
<trkseg/> is present.
"""

import datetime as mod_datetime
import unittest as mod_unittest

import gpxpy as mod_gpxpy

# Four points without <time> and a trailing empty segment:
GPX_WITHOUT_TIMES_AND_EMPTY_SEGMENT = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test">
<trk><trkseg>
<trkpt lat="45.0" lon="9.0"><ele>100</ele></trkpt>
<trkpt lat="45.001" lon="9.0"><ele>101</ele></trkpt>
<trkpt lat="45.002" lon="9.0"><ele>102</ele></trkpt>
<trkpt lat="45.003" lon="9.0"><ele>103</ele></trkpt>
</trkseg><trkseg/></trk>
</gpx>"""

# The same points with timestamps and a trailing empty segment:
GPX_WITH_TIMES_AND_EMPTY_SEGMENT = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test">
<trk><trkseg>
<trkpt lat="45.0" lon="9.0"><ele>100</ele><time>2023-01-01T12:00:00Z</time></trkpt>
<trkpt lat="45.001" lon="9.0"><ele>101</ele><time>2023-01-01T12:01:00Z</time></trkpt>
<trkpt lat="45.002" lon="9.0"><ele>102</ele><time>2023-01-01T12:02:00Z</time></trkpt>
<trkpt lat="45.003" lon="9.0"><ele>103</ele><time>2023-01-01T12:03:00Z</time></trkpt>
</trkseg><trkseg/></trk>
</gpx>"""


class EmptySegmentHasTimesTests(mod_unittest.TestCase):
    """ Empty segments must be neutral for has_times(). """

    def test_has_times_false_with_empty_segment(self) -> None:
        gpx = mod_gpxpy.parse(GPX_WITHOUT_TIMES_AND_EMPTY_SEGMENT)
        self.assertFalse(gpx.has_times())

    def test_has_times_true_with_empty_segment(self) -> None:
        gpx = mod_gpxpy.parse(GPX_WITH_TIMES_AND_EMPTY_SEGMENT)
        self.assertTrue(gpx.has_times())

    def test_fill_times_with_empty_segment_and_no_force(self) -> None:
        """ fill_time_data_with_regular_intervals must not refuse a file
        without time data just because it has an empty segment. """
        gpx = mod_gpxpy.parse(GPX_WITHOUT_TIMES_AND_EMPTY_SEGMENT)
        start_time = mod_datetime.datetime(2023, 1, 1, 12, 0, 0)
        time_delta = mod_datetime.timedelta(seconds=10)
        gpx.fill_time_data_with_regular_intervals(
            start_time=start_time, time_delta=time_delta, force=False)
        first_point = gpx.tracks[0].segments[0].points[0]
        self.assertEqual(first_point.time, start_time)
        last_point = gpx.tracks[0].segments[0].points[-1]
        self.assertEqual(last_point.time,
                         start_time + 3 * time_delta)


if __name__ == '__main__':
    mod_unittest.main()
