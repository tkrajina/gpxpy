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
Regression tests for GPX extension namespace handling and round-trip
preservation.

These tests are wired into the repository's standard entry point via the
load_tests hook at the bottom of test.py, so they run with:

    $ python -m unittest test
"""

import unittest as mod_unittest

import gpxpy as mod_gpxpy

# GPX 1.1 document in the style emitted by some tools (e.g. GPSMID):
# every attribute, including the xmlns declarations, uses single quotes.
# This is well-formed XML, so parse() must accept it and to_xml() must
# produce output that can be parsed back.
SINGLE_QUOTED_XMLNS_GPX = """<?xml version='1.0' encoding='UTF-8'?>
<gpx version='1.1' creator='GPSMID' xmlns='http://www.topografix.com/GPX/1/1' xmlns:gpxx='http://www.garmin.com/xmlschemas/GpxExtensions/v3'>
<trk><trkseg>
<trkpt lat='40.61262' lon='10.592117'><ele>100</ele>
<extensions><gpxx:TrackPointExtension><gpxx:hr>120</gpxx:hr></gpxx:TrackPointExtension></extensions>
</trkpt>
</trkseg></trk>
</gpx>"""

# Same document, but with a single-quoted xsi:schemaLocation. Base only
# matched double-quoted values, so schema_locations came back empty.
SINGLE_QUOTED_SCHEMA_LOCATION_GPX = """<?xml version='1.0' encoding='UTF-8'?>
<gpx version='1.1' creator='x' xmlns='http://www.topografix.com/GPX/1/1' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd'>
<wpt lat='40.61262' lon='10.592117'><ele>100</ele></wpt>
</gpx>"""

# A valid xsi:schemaLocation whose attribute value spans two lines.
# Base (which allowed any character except a double quote inside the
# value) kept both schema locations; the fix must not regress this.
MULTILINE_SCHEMA_LOCATION_GPX = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="x" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1
http://www.topografix.com/GPX/1/1/gpx.xsd">
<wpt lat='40.61262' lon='10.592117'><ele>100</ele></wpt>
</gpx>"""

# A namespace URI (in double quotes) that ends with a literal apostrophe.
# Base preserved the apostrophe and the document round-tripped; the fix
# must remove exactly the enclosing quote delimiters, not every quote
# character at the ends of the value.
APOSTROPHE_URI_GPX = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="x" xmlns="http://www.topografix.com/GPX/1/1" xmlns:foo="https://example.org/ns'">
<wpt lat='40.61262' lon='10.592117'><ele>100</ele></wpt>
</gpx>"""


class RegressionTests(mod_unittest.TestCase):
    """ Regression tests for namespace round-trip preservation """

    def test_single_quoted_xmlns_prefixes_are_registered(self) -> None:
        """ Prefixed namespaces declared with single quotes must be kept """
        gpx = mod_gpxpy.parse(SINGLE_QUOTED_XMLNS_GPX)

        self.assertIn('gpxx', gpx.nsmap)
        self.assertEqual(
            'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
            gpx.nsmap['gpxx']
        )

    def test_single_quoted_xmlns_round_trip(self) -> None:
        """ to_xml() output for single-quoted xmlns input must reparse """
        gpx = mod_gpxpy.parse(SINGLE_QUOTED_XMLNS_GPX)

        xml = gpx.to_xml()

        # The serialized document must remain well-formed: prefixes must be
        # resolved through the nsmap, not glued onto the namespace URI.
        self.assertNotIn('{http://', xml)

        reparsed = mod_gpxpy.parse(xml)
        point = reparsed.tracks[0].segments[0].points[0]
        self.assertEqual(1, len(point.extensions))
        extension = point.extensions[0]
        self.assertEqual(
            '{http://www.garmin.com/xmlschemas/GpxExtensions/v3}TrackPointExtension',
            extension.tag
        )
        children = list(extension)
        self.assertEqual(1, len(children))
        self.assertEqual(
            '{http://www.garmin.com/xmlschemas/GpxExtensions/v3}hr',
            children[0].tag
        )
        self.assertEqual('120', children[0].text)

    def test_single_quoted_schema_location_is_registered(self) -> None:
        """ A single-quoted xsi:schemaLocation must populate the locations """
        gpx = mod_gpxpy.parse(SINGLE_QUOTED_SCHEMA_LOCATION_GPX)

        self.assertEqual(
            [
                'http://www.topografix.com/GPX/1/1',
                'http://www.topografix.com/GPX/1/1/gpx.xsd',
            ],
            gpx.schema_locations
        )

    def test_multiline_schema_location_is_preserved(self) -> None:
        """ A schemaLocation spanning lines must keep all its locations """
        gpx = mod_gpxpy.parse(MULTILINE_SCHEMA_LOCATION_GPX)

        self.assertEqual(
            [
                'http://www.topografix.com/GPX/1/1',
                'http://www.topografix.com/GPX/1/1/gpx.xsd',
            ],
            gpx.schema_locations
        )

        # The full document must still round-trip.
        reparsed = mod_gpxpy.parse(gpx.to_xml())
        self.assertEqual(1, len(reparsed.waypoints))

    def test_double_quoted_uri_ending_with_apostrophe(self) -> None:
        """ Only the enclosing quote delimiters may be removed from URIs """
        gpx = mod_gpxpy.parse(APOSTROPHE_URI_GPX)

        self.assertEqual("https://example.org/ns'", gpx.nsmap['foo'])

        # The serialized document must remain well-formed.
        reparsed = mod_gpxpy.parse(gpx.to_xml())
        self.assertEqual(1, len(reparsed.waypoints))
        self.assertEqual("https://example.org/ns'",
                         reparsed.nsmap['foo'])


if __name__ == '__main__':
    mod_unittest.main()
