import unittest

from .helper import custom_open
import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx


class TestSimple(unittest.TestCase):
    def test_simple_parse_function(self):
        # Must not throw any exception:
        with custom_open('test_files/korita-zbevnica.gpx', encoding='utf-8') as f:
            mod_gpxpy.parse(f)

    def test_simple_parse_function_invalid_xml(self):
        try:
            mod_gpxpy.parse('<gpx></gpx')
            self.fail()
        except mod_gpx.GPXException as e:
            self.assertTrue(('unclosed token: line 1, column 5' in str(e)) or ('expected \'>\'' in str(e)))
            self.assertTrue(isinstance(e, mod_gpx.GPXXMLSyntaxException))
            self.assertTrue(e.__cause__)

            try:
                # more checks if lxml:
                import lxml.etree as mod_etree
                import xml.parsers.expat as mod_expat
                self.assertTrue(
                    isinstance(e.__cause__, mod_etree.XMLSyntaxError) or isinstance(e.__cause__, mod_expat.ExpatError)
                )
            except:  # noqa
                pass
