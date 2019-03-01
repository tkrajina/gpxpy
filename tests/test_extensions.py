import unittest
try:
    import lxml.etree as mod_etree  # Load LXML or fallback to cET or ET
except ImportError:
    try:
        import xml.etree.cElementTree as mod_etree
    except ImportError:
        import xml.etree.ElementTree as mod_etree

from .helper import print_etree, elements_equal
import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx


class TestSplit(unittest.TestCase):
    def test_read_extensions(self):
        """ Test extensions """

        with open('test_files/gpx1.1_with_extensions.gpx') as f:
            xml = f.read()

        namespace = '{gpx.py}'
        root1 = mod_etree.Element(namespace + 'aaa')
        root1.text = 'bbb'
        root1.tail = 'hhh'
        root1.attrib[namespace + 'jjj'] = 'kkk'

        root2 = mod_etree.Element(namespace + 'ccc')
        root2.text = ''
        root2.tail = ''

        subnode1 = mod_etree.SubElement(root2, namespace + 'ddd')
        subnode1.text = 'eee'
        subnode1.tail = ''
        subnode1.attrib[namespace + 'lll'] = 'mmm'
        subnode1.attrib[namespace + 'nnn'] = 'ooo'

        subnode2 = mod_etree.SubElement(subnode1, namespace + 'fff')
        subnode2.text = 'ggg'
        subnode2.tail = 'iii'

        gpx = mod_gpxpy.parse(xml)

        print("Extension 1")
        print(print_etree(gpx.waypoints[0].extensions[0]))
        print()
        self.assertTrue(elements_equal(gpx.waypoints[0].extensions[0], root1))

        print("Extension 2")
        print(print_etree(gpx.waypoints[0].extensions[1]))
        print()
        self.assertTrue(elements_equal(gpx.waypoints[0].extensions[1], root2))

    def test_write_read_extensions(self):
        namespace = '{gpx.py}'
        nsmap = {'ext': namespace[1:-1]}
        root = mod_etree.Element(namespace + 'ccc')
        root.text = ''
        root.tail = ''

        subnode1 = mod_etree.SubElement(root, namespace + 'ddd')
        subnode1.text = 'eee'
        subnode1.tail = ''
        subnode1.attrib[namespace + 'lll'] = 'mmm'
        subnode1.attrib[namespace + 'nnn'] = 'ooo'

        subnode2 = mod_etree.SubElement(subnode1, namespace + 'fff')
        subnode2.text = 'ggg'
        subnode2.tail = 'iii'

        subnode3 = mod_etree.SubElement(root, namespace + 'aaa')
        subnode3.text = 'bbb'

        gpx = mod_gpx.GPX()
        gpx.nsmap = nsmap

        print("Inserting Waypoint Extension")
        gpx.waypoints.append(mod_gpx.GPXWaypoint())
        gpx.waypoints[0].latitude = 5
        gpx.waypoints[0].longitude = 10
        gpx.waypoints[0].extensions.append(root)

        print("Inserting Metadata Extension")
        gpx.metadata_extensions.append(root)

        print("Inserting GPX Extension")
        gpx.extensions.append(root)

        print("Inserting Route Extension")
        gpx.routes.append(mod_gpx.GPXRoute())
        gpx.routes[0].extensions.append(root)

        print("Inserting Track Extension")
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].extensions.append(root)

        print("Inserting Track Segment Extension")
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].extensions.append(root)

        print("Inserting Track Point Extension")
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13))
        gpx.tracks[0].segments[0].points[0].extensions.append(root)

        xml = gpx.to_xml('1.1')
        mod_gpxpy.parse(xml)

        print("Reading Waypoint Extension")
        print(print_etree(gpx.waypoints[0].extensions[0]))
        print()
        self.assertTrue(elements_equal(gpx.waypoints[0].extensions[0], root))

        print("Reading Metadata Extension")
        self.assertTrue(elements_equal(gpx.metadata_extensions[0], root))

        print("Reading GPX Extension")
        self.assertTrue(elements_equal(gpx.extensions[0], root))

        print("Reading Route Extension")
        self.assertTrue(elements_equal(gpx.routes[0].extensions[0], root))

        print("Reading Track Extension")
        self.assertTrue(elements_equal(gpx.tracks[0].extensions[0], root))

        print("Reading Track Segment Extension")
        self.assertTrue(elements_equal(gpx.tracks[0].segments[0].extensions[0], root))

        print("Reading Track Point Extension")
        self.assertTrue(elements_equal(gpx.tracks[0].segments[0].points[0].extensions[0], root))

    def test_no_10_extensions(self):
        namespace = '{gpx.py}'
        nsmap = {'ext': namespace[1:-1]}
        root = mod_etree.Element(namespace + 'tag')
        root.text = 'text'
        root.tail = 'tail'

        gpx = mod_gpx.GPX()
        gpx.nsmap = nsmap

        print("Inserting Waypoint Extension")
        gpx.waypoints.append(mod_gpx.GPXWaypoint())
        gpx.waypoints[0].latitude = 5
        gpx.waypoints[0].longitude = 10
        gpx.waypoints[0].extensions.append(root)

        print("Inserting Metadata Extension")
        gpx.metadata_extensions.append(root)

        print("Inserting GPX Extension")
        gpx.extensions.append(root)

        print("Inserting Route Extension")
        gpx.routes.append(mod_gpx.GPXRoute())
        gpx.routes[0].extensions.append(root)

        print("Inserting Track Extension")
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].extensions.append(root)

        print("Inserting Track Segment Extension")
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].extensions.append(root)

        print("Inserting Track Point Extension")
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13))
        gpx.tracks[0].segments[0].points[0].extensions.append(root)

        xml = gpx.to_xml('1.0')
        self.assertFalse('extension' in xml)

    def test_extension_without_namespaces(self):
        f = open('test_files/gpx1.1_with_extensions_without_namespaces.gpx', 'r')
        gpx = mod_gpxpy.parse(f)
        self.assertEqual(2, len(gpx.waypoints[0].extensions))
        self.assertEqual("bbb", gpx.waypoints[0].extensions[0].text)
        self.assertEqual("eee", gpx.waypoints[0].extensions[1].getchildren()[0].text.strip())

    def test_with_ns_namespace(self):
        gpx_with_ns = mod_gpxpy.parse("""<?xml version="1.0" encoding="UTF-8"?>
        <gpx creator="Garmin Connect" version="1.1"
          xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/11.xsd"
          xmlns:ns3="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
          xmlns="http://www.topografix.com/GPX/1/1"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
          <metadata>
          </metadata>
          <trk>
            <name>Foo Bar</name>
            <type>running</type>
            <trkseg>
              <trkpt lat="51.43788929097354412078857421875" lon="6.617012657225131988525390625">
                <ele>23.6000003814697265625</ele>
                <time>2018-02-21T14:30:50.000Z</time>
                <extensions>
                  <ns3:TrackPointExtension>
                    <ns3:hr>125</ns3:hr>
                    <ns3:cad>75</ns3:cad>
                  </ns3:TrackPointExtension>
                </extensions>
              </trkpt>
            </trkseg>
          </trk>
        </gpx>""")

        reparsed = mod_gpxpy.parse(gpx_with_ns.to_xml("1.1"))

        for gpx in [gpx_with_ns, reparsed]:
            extensions = gpx.tracks[0].segments[0].points[0].extensions
            self.assertEqual(1, len(extensions))
            self.assertEqual("125", extensions[0].getchildren()[0].text.strip())
            self.assertEqual("75", extensions[0].getchildren()[1].text.strip())
