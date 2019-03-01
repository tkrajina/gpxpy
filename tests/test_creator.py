import unittest

from .helper import parse, reparse


class TestCreator(unittest.TestCase):
    def test_creator_field(self):
        gpx = parse('cerknicko-jezero.gpx')
        self.assertEqual(gpx.creator, "GPSBabel - http://www.gpsbabel.org")

    def test_no_creator_field(self):
        gpx = parse('cerknicko-jezero-no-creator.gpx')
        self.assertEqual(gpx.creator, None)

    def test_to_xml_creator(self):
        gpx = parse('cerknicko-jezero.gpx')
        xml = gpx.to_xml()
        self.assertTrue('creator="GPSBabel - http://www.gpsbabel.org"' in xml)

        gpx2 = reparse(gpx)
        self.assertEqual(gpx2.creator, "GPSBabel - http://www.gpsbabel.org")
