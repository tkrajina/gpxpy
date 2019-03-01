import unittest

from .helper import parse, custom_open
from gpxpy.utils import make_str
import gpxpy.parser as mod_parser


class TestUnicode(unittest.TestCase):
    def test_unicode(self):
        with custom_open('test_files/unicode2.gpx', encoding='utf-8') as f:
            parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        gpx.to_xml()

    def test_unicode_name(self):
        gpx = parse('unicode.gpx', encoding='utf-8')
        name = gpx.waypoints[0].name
        self.assertTrue(make_str(name) == 'šđčćž')

    def test_unicode_2(self):
        with custom_open('test_files/unicode2.gpx', encoding='utf-8') as f:
            parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        gpx.to_xml()

    def test_unicode_bom(self):
        # TODO: Check that this file has the BOM and is unicode before checking gpxpy handling
        gpx = parse('unicode_with_bom.gpx', encoding='utf-8')
        name = gpx.waypoints[0].name

        self.assertTrue(make_str(name) == 'test')

    def test_unicode_bom_noencoding(self):
        gpx = parse('unicode_with_bom_noencoding.gpx', encoding='utf-8')
        name = gpx.waypoints[0].name

        self.assertTrue(make_str(name) == 'bom noencoding ő')
