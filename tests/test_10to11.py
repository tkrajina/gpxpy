import unittest
import datetime as mod_datetime
import xml.dom.minidom as mod_minidom
try:
    import lxml.etree as mod_etree  # Load LXML or fallback to cET or ET
except:
    try:
        import xml.etree.cElementTree as mod_etree
    except:
        import xml.etree.ElementTree as mod_etree

from .helper import get_dom_node, elements_equal
import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx


class Test10to11(unittest.TestCase):
    def test_gpx_10_fields(self):
        """ Test (de) serialization all gpx1.0 fields """

        with open('test_files/gpx1.0_with_all_fields.gpx') as f:
            xml = f.read()

        original_gpx = mod_gpxpy.parse(xml)

        # Serialize and parse again to be sure that all is preserved:
        reparsed_gpx = mod_gpxpy.parse(original_gpx.to_xml())

        original_dom = mod_minidom.parseString(xml)
        reparsed_dom = mod_minidom.parseString(reparsed_gpx.to_xml())

        # Validated  with SAXParser in "make test"
        with open('test_files/validation_gpx10.gpx', 'w') as f:
            f.write(reparsed_gpx.to_xml())

        for gpx in (original_gpx, reparsed_gpx):
            for dom in (original_dom, reparsed_dom):
                self.assertEqual(gpx.version, '1.0')
                self.assertEqual(get_dom_node(dom, 'gpx').attributes['version'].nodeValue, '1.0')

                self.assertEqual(gpx.creator, '...')
                self.assertEqual(get_dom_node(dom, 'gpx').attributes['creator'].nodeValue, '...')

                self.assertEqual(gpx.name, 'example name')
                self.assertEqual(get_dom_node(dom, 'gpx/name').firstChild.nodeValue, 'example name')

                self.assertEqual(gpx.description, 'example description')
                self.assertEqual(get_dom_node(dom, 'gpx/desc').firstChild.nodeValue, 'example description')

                self.assertEqual(gpx.author_name, 'example author')
                self.assertEqual(get_dom_node(dom, 'gpx/author').firstChild.nodeValue, 'example author')

                self.assertEqual(gpx.author_email, 'example@email.com')
                self.assertEqual(get_dom_node(dom, 'gpx/email').firstChild.nodeValue, 'example@email.com')

                self.assertEqual(gpx.link, 'http://example.url')
                self.assertEqual(get_dom_node(dom, 'gpx/url').firstChild.nodeValue, 'http://example.url')

                self.assertEqual(gpx.link_text, 'example urlname')
                self.assertEqual(get_dom_node(dom, 'gpx/urlname').firstChild.nodeValue, 'example urlname')

                self.assertEqual(gpx.time, mod_datetime.datetime(2013, 1, 1, 12, 0))
                self.assertTrue(get_dom_node(dom, 'gpx/time').firstChild.nodeValue in ('2013-01-01T12:00:00Z', '2013-01-01T12:00:00'))

                self.assertEqual(gpx.keywords, 'example keywords')
                self.assertEqual(get_dom_node(dom, 'gpx/keywords').firstChild.nodeValue, 'example keywords')

                self.assertEqual(gpx.bounds.min_latitude, 1.2)
                self.assertEqual(get_dom_node(dom, 'gpx/bounds').attributes['minlat'].value, '1.2')

                # Waypoints:

                self.assertEqual(len(gpx.waypoints), 2)

                self.assertEqual(gpx.waypoints[0].latitude, 12.3)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]').attributes['lat'].value, '12.3')

                self.assertEqual(gpx.waypoints[0].longitude, 45.6)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]').attributes['lon'].value, '45.6')

                self.assertEqual(gpx.waypoints[0].longitude, 45.6)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]').attributes['lon'].value, '45.6')

                self.assertEqual(gpx.waypoints[0].elevation, 75.1)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/ele').firstChild.nodeValue, '75.1')

                self.assertEqual(gpx.waypoints[0].time, mod_datetime.datetime(2013, 1, 2, 2, 3))
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/time').firstChild.nodeValue, '2013-01-02T02:03:00Z')

                self.assertEqual(gpx.waypoints[0].magnetic_variation, 1.1)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/magvar').firstChild.nodeValue, '1.1')

                self.assertEqual(gpx.waypoints[0].geoid_height, 2.0)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/geoidheight').firstChild.nodeValue, '2.0')

                self.assertEqual(gpx.waypoints[0].name, 'example name')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/name').firstChild.nodeValue, 'example name')

                self.assertEqual(gpx.waypoints[0].comment, 'example cmt')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEqual(gpx.waypoints[0].description, 'example desc')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEqual(gpx.waypoints[0].source, 'example src')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/src').firstChild.nodeValue, 'example src')

                self.assertEqual(gpx.waypoints[0].link, 'example url')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/url').firstChild.nodeValue, 'example url')

                self.assertEqual(gpx.waypoints[0].link_text, 'example urlname')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/urlname').firstChild.nodeValue, 'example urlname')

                self.assertEqual(gpx.waypoints[1].latitude, 13.4)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[1]').attributes['lat'].value, '13.4')

                self.assertEqual(gpx.waypoints[1].longitude, 46.7)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[1]').attributes['lon'].value, '46.7')

                self.assertEqual(len(gpx.routes), 2)

                self.assertEqual(gpx.routes[0].name, 'example name')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/name').firstChild.nodeValue, 'example name')

                self.assertEqual(gpx.routes[0].comment, 'example cmt')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEqual(gpx.routes[0].description, 'example desc')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEqual(gpx.routes[0].source, 'example src')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/src').firstChild.nodeValue, 'example src')

                self.assertEqual(gpx.routes[0].link, 'example url')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/url').firstChild.nodeValue, 'example url')

                # Rte pt:

                self.assertEqual(gpx.routes[0].points[0].latitude, 10)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]').attributes['lat'].value in ('10.0', '10'))

                self.assertEqual(gpx.routes[0].points[0].longitude, 20)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]').attributes['lon'].value in ('20.0', '20'))

                self.assertEqual(gpx.routes[0].points[0].elevation, 75.1)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/ele').firstChild.nodeValue, '75.1')

                self.assertEqual(gpx.routes[0].points[0].time, mod_datetime.datetime(2013, 1, 2, 2, 3, 3))
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/time').firstChild.nodeValue, '2013-01-02T02:03:03Z')

                self.assertEqual(gpx.routes[0].points[0].magnetic_variation, 1.2)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/magvar').firstChild.nodeValue, '1.2')

                self.assertEqual(gpx.routes[0].points[0].geoid_height, 2.1)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/geoidheight').firstChild.nodeValue, '2.1')

                self.assertEqual(gpx.routes[0].points[0].name, 'example name r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/name').firstChild.nodeValue, 'example name r')

                self.assertEqual(gpx.routes[0].points[0].comment, 'example cmt r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/cmt').firstChild.nodeValue, 'example cmt r')

                self.assertEqual(gpx.routes[0].points[0].description, 'example desc r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/desc').firstChild.nodeValue, 'example desc r')

                self.assertEqual(gpx.routes[0].points[0].source, 'example src r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/src').firstChild.nodeValue, 'example src r')

                self.assertEqual(gpx.routes[0].points[0].link, 'example url r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/url').firstChild.nodeValue, 'example url r')

                self.assertEqual(gpx.routes[0].points[0].link_text, 'example urlname r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/urlname').firstChild.nodeValue, 'example urlname r')

                self.assertEqual(gpx.routes[0].points[0].symbol, 'example sym r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/sym').firstChild.nodeValue, 'example sym r')

                self.assertEqual(gpx.routes[0].points[0].type, 'example type r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/type').firstChild.nodeValue, 'example type r')

                self.assertEqual(gpx.routes[0].points[0].type_of_gpx_fix, '3d')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/fix').firstChild.nodeValue, '3d')

                self.assertEqual(gpx.routes[0].points[0].satellites, 6)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/sat').firstChild.nodeValue, '6')

                self.assertEqual(gpx.routes[0].points[0].vertical_dilution, 8)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/vdop').firstChild.nodeValue in ('8.0', '8'))

                self.assertEqual(gpx.routes[0].points[0].horizontal_dilution, 7)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/hdop').firstChild.nodeValue in ('7.0', '7'))

                self.assertEqual(gpx.routes[0].points[0].position_dilution, 9)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/pdop').firstChild.nodeValue in ('9.0', '9'))

                self.assertEqual(gpx.routes[0].points[0].age_of_dgps_data, 10)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/ageofdgpsdata').firstChild.nodeValue in ('10.0', '10'))

                self.assertEqual(gpx.routes[0].points[0].dgps_id, '99')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/dgpsid').firstChild.nodeValue, '99')

                # second rtept:

                self.assertEqual(gpx.routes[0].points[1].latitude, 11)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[1]').attributes['lat'].value in ('11.0', '11'))

                self.assertEqual(gpx.routes[0].points[1].longitude, 21)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[1]').attributes['lon'].value in ('21.0', '21'))

                # Rte

                self.assertEqual(gpx.routes[1].name, 'second route')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[1]/name').firstChild.nodeValue, 'second route')

                self.assertEqual(gpx.routes[1].description, 'example desc 2')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[1]/desc').firstChild.nodeValue, 'example desc 2')

                self.assertEqual(gpx.routes[0].link_text, 'example urlname')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/urlname').firstChild.nodeValue, 'example urlname')

                self.assertEqual(gpx.routes[0].number, 7)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/number').firstChild.nodeValue, '7')

                self.assertEqual(len(gpx.routes[0].points), 3)
                self.assertEqual(len(gpx.routes[1].points), 2)

                # trk:

                self.assertEqual(len(gpx.tracks), 2)

                self.assertEqual(gpx.tracks[0].name, 'example name t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEqual(gpx.tracks[0].comment, 'example cmt t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEqual(gpx.tracks[0].description, 'example desc t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEqual(gpx.tracks[0].source, 'example src t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEqual(gpx.tracks[0].link, 'example url t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/url').firstChild.nodeValue, 'example url t')

                self.assertEqual(gpx.tracks[0].link_text, 'example urlname t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/urlname').firstChild.nodeValue, 'example urlname t')

                self.assertEqual(gpx.tracks[0].number, 1)
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/number').firstChild.nodeValue, '1')

                # trkpt:

                self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 11.1)
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/ele').firstChild.nodeValue, '11.1')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2013, 1, 1, 12, 0, 4))
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/time').firstChild.nodeValue in ('2013-01-01T12:00:04Z', '2013-01-01T12:00:04'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].magnetic_variation, 12)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/magvar').firstChild.nodeValue in ('12.0', '12'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].geoid_height, 13.0)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/geoidheight').firstChild.nodeValue in ('13.0', '13'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].name, 'example name t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].comment, 'example cmt t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].description, 'example desc t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].source, 'example src t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].link, 'example url t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/url').firstChild.nodeValue, 'example url t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].link_text, 'example urlname t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/urlname').firstChild.nodeValue, 'example urlname t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].symbol, 'example sym t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/sym').firstChild.nodeValue, 'example sym t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].type, 'example type t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/type').firstChild.nodeValue, 'example type t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].type_of_gpx_fix, '3d')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/fix').firstChild.nodeValue, '3d')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].satellites, 100)
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/sat').firstChild.nodeValue, '100')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].vertical_dilution, 102.)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/vdop').firstChild.nodeValue in ('102.0', '102'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].horizontal_dilution, 101)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/hdop').firstChild.nodeValue in ('101.0', '101'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].position_dilution, 103)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/pdop').firstChild.nodeValue in ('103.0', '103'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].age_of_dgps_data, 104)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/ageofdgpsdata').firstChild.nodeValue in ('104.0', '104'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].dgps_id, '99')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/dgpsid').firstChild.nodeValue, '99')

    def test_gpx_11_fields(self):
        """ Test (de) serialization all gpx1.0 fields """

        with open('test_files/gpx1.1_with_all_fields.gpx') as f:
            xml = f.read()

        original_gpx = mod_gpxpy.parse(xml)

        # Serialize and parse again to be sure that all is preserved:
        reparsed_gpx = mod_gpxpy.parse(original_gpx.to_xml('1.1'))

        original_dom = mod_minidom.parseString(xml)
        reparsed_dom = mod_minidom.parseString(reparsed_gpx.to_xml('1.1'))
        namespace = '{https://github.com/tkrajina/gpxpy}'
        for gpx in (original_gpx, reparsed_gpx):
            for dom in (original_dom, reparsed_dom):
                self.assertEqual(gpx.version, '1.1')
                self.assertEqual(get_dom_node(dom, 'gpx').attributes['version'].nodeValue, '1.1')

                self.assertEqual(gpx.creator, '...')
                self.assertEqual(get_dom_node(dom, 'gpx').attributes['creator'].nodeValue, '...')

                self.assertEqual(gpx.name, 'example name')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/name').firstChild.nodeValue, 'example name')

                self.assertEqual(gpx.description, 'example description')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/desc').firstChild.nodeValue, 'example description')

                self.assertEqual(gpx.author_name, 'author name')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/author/name').firstChild.nodeValue, 'author name')

                self.assertEqual(gpx.author_email, 'aaa@bbb.com')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/author/email').attributes['id'].nodeValue, 'aaa')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/author/email').attributes['domain'].nodeValue, 'bbb.com')

                self.assertEqual(gpx.author_link, 'http://link')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/author/link').attributes['href'].nodeValue, 'http://link')

                self.assertEqual(gpx.author_link_text, 'link text')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/author/link/text').firstChild.nodeValue, 'link text')

                self.assertEqual(gpx.author_link_type, 'link type')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/author/link/type').firstChild.nodeValue, 'link type')

                self.assertEqual(gpx.copyright_author, 'gpxauth')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/copyright').attributes['author'].nodeValue, 'gpxauth')

                self.assertEqual(gpx.copyright_year, '2013')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/copyright/year').firstChild.nodeValue, '2013')

                self.assertEqual(gpx.copyright_license, 'lic')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/copyright/license').firstChild.nodeValue, 'lic')

                self.assertEqual(gpx.link, 'http://link2')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/link').attributes['href'].nodeValue, 'http://link2')

                self.assertEqual(gpx.link_text, 'link text2')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/link/text').firstChild.nodeValue, 'link text2')

                self.assertEqual(gpx.link_type, 'link type2')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/link/type').firstChild.nodeValue, 'link type2')

                self.assertEqual(gpx.time, mod_datetime.datetime(2013, 1, 1, 12, 0))
                self.assertTrue(get_dom_node(dom, 'gpx/metadata/time').firstChild.nodeValue in ('2013-01-01T12:00:00Z', '2013-01-01T12:00:00'))

                self.assertEqual(gpx.keywords, 'example keywords')
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/keywords').firstChild.nodeValue, 'example keywords')

                self.assertEqual(gpx.bounds.min_latitude, 1.2)
                self.assertEqual(get_dom_node(dom, 'gpx/metadata/bounds').attributes['minlat'].value, '1.2')

                # TODO

                self.assertEqual(len(gpx.metadata_extensions), 3)
                aaa = mod_etree.Element(namespace+'aaa')
                aaa.text = 'bbb'
                aaa.tail = ''
                self.assertTrue(elements_equal(gpx.metadata_extensions[0], aaa))
                bbb = mod_etree.Element(namespace+'bbb')
                bbb.text = 'ccc'
                bbb.tail = ''
                self.assertTrue(elements_equal(gpx.metadata_extensions[1], bbb))
                ccc = mod_etree.Element(namespace+'ccc')
                ccc.text = 'ddd'
                ccc.tail = ''
                self.assertTrue(elements_equal(gpx.metadata_extensions[2], ccc))

                # get_dom_node function is not escaped and so fails on proper namespaces
                #self.assertEqual(get_dom_node(dom, 'gpx/metadata/extensions/{}aaa'.format(namespace)).firstChild.nodeValue, 'bbb')
                #self.assertEqual(get_dom_node(dom, 'gpx/metadata/extensions/bbb').firstChild.nodeValue, 'ccc')
                #self.assertEqual(get_dom_node(dom, 'gpx/metadata/extensions/ccc').firstChild.nodeValue, 'ddd')

                self.assertEqual(2, len(gpx.waypoints))

                self.assertEqual(gpx.waypoints[0].latitude, 12.3)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]').attributes['lat'].value, '12.3')

                self.assertEqual(gpx.waypoints[0].longitude, 45.6)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]').attributes['lon'].value, '45.6')

                self.assertEqual(gpx.waypoints[0].longitude, 45.6)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]').attributes['lon'].value, '45.6')

                self.assertEqual(gpx.waypoints[0].elevation, 75.1)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/ele').firstChild.nodeValue, '75.1')

                self.assertEqual(gpx.waypoints[0].time, mod_datetime.datetime(2013, 1, 2, 2, 3))
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/time').firstChild.nodeValue, '2013-01-02T02:03:00Z')

                self.assertEqual(gpx.waypoints[0].magnetic_variation, 1.1)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/magvar').firstChild.nodeValue, '1.1')

                self.assertEqual(gpx.waypoints[0].geoid_height, 2.0)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/geoidheight').firstChild.nodeValue, '2.0')

                self.assertEqual(gpx.waypoints[0].name, 'example name')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/name').firstChild.nodeValue, 'example name')

                self.assertEqual(gpx.waypoints[0].comment, 'example cmt')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEqual(gpx.waypoints[0].description, 'example desc')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEqual(gpx.waypoints[0].source, 'example src')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/src').firstChild.nodeValue, 'example src')

                self.assertEqual(gpx.waypoints[0].link, 'http://link3')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/link').attributes['href'].nodeValue, 'http://link3')

                self.assertEqual(gpx.waypoints[0].link_text, 'link text3')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/link/text').firstChild.nodeValue, 'link text3')

                self.assertEqual(gpx.waypoints[0].link_type, 'link type3')
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[0]/link/type').firstChild.nodeValue, 'link type3')

                self.assertEqual(gpx.waypoints[1].latitude, 13.4)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[1]').attributes['lat'].value, '13.4')

                self.assertEqual(gpx.waypoints[1].longitude, 46.7)
                self.assertEqual(get_dom_node(dom, 'gpx/wpt[1]').attributes['lon'].value, '46.7')

                self.assertEqual(2, len(gpx.waypoints[0].extensions))

                self.assertTrue(elements_equal(gpx.waypoints[0].extensions[0], aaa))
                self.assertTrue(elements_equal(gpx.waypoints[0].extensions[1], ccc))

                # 1. rte

                self.assertEqual(gpx.routes[0].name, 'example name')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/name').firstChild.nodeValue, 'example name')

                self.assertEqual(gpx.routes[0].comment, 'example cmt')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEqual(gpx.routes[0].description, 'example desc')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEqual(gpx.routes[0].source, 'example src')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/src').firstChild.nodeValue, 'example src')

                self.assertEqual(gpx.routes[0].link, 'http://link3')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/link').attributes['href'].nodeValue, 'http://link3')

                self.assertEqual(gpx.routes[0].link_text, 'link text3')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/link/text').firstChild.nodeValue, 'link text3')

                self.assertEqual(gpx.routes[0].link_type, 'link type3')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/link/type').firstChild.nodeValue, 'link type3')

                self.assertEqual(gpx.routes[0].number, 7)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/number').firstChild.nodeValue, '7')

                self.assertEqual(gpx.routes[0].type, 'rte type')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/type').firstChild.nodeValue, 'rte type')

                self.assertEqual(2, len(gpx.routes[0].extensions))

                rtee1 = mod_etree.Element(namespace+'rtee1')
                rtee1.text = '1'
                rtee1.tail = ''
                self.assertTrue(elements_equal(gpx.routes[0].extensions[0], rtee1))
                rtee2 = mod_etree.Element(namespace+'rtee2')
                rtee2.text = '2'
                rtee2.tail = ''
                self.assertTrue(elements_equal(gpx.routes[0].extensions[1], rtee2))


                # 2. rte

                self.assertEqual(gpx.routes[1].name, 'second route')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[1]/name').firstChild.nodeValue, 'second route')

                self.assertEqual(gpx.routes[1].description, 'example desc 2')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[1]/desc').firstChild.nodeValue, 'example desc 2')

                self.assertEqual(gpx.routes[1].link, None)

                self.assertEqual(gpx.routes[0].number, 7)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/number').firstChild.nodeValue, '7')

                self.assertEqual(len(gpx.routes[0].points), 3)
                self.assertEqual(len(gpx.routes[1].points), 2)

                # Rtept

                self.assertEqual(gpx.routes[0].points[0].latitude, 10)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]').attributes['lat'].value in ('10.0', '10'))

                self.assertEqual(gpx.routes[0].points[0].longitude, 20)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]').attributes['lon'].value in ('20.0', '20'))

                self.assertEqual(gpx.routes[0].points[0].elevation, 75.1)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/ele').firstChild.nodeValue, '75.1')

                self.assertEqual(gpx.routes[0].points[0].time, mod_datetime.datetime(2013, 1, 2, 2, 3, 3))
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/time').firstChild.nodeValue, '2013-01-02T02:03:03Z')

                self.assertEqual(gpx.routes[0].points[0].magnetic_variation, 1.2)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/magvar').firstChild.nodeValue, '1.2')

                self.assertEqual(gpx.routes[0].points[0].geoid_height, 2.1)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/geoidheight').firstChild.nodeValue, '2.1')

                self.assertEqual(gpx.routes[0].points[0].name, 'example name r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/name').firstChild.nodeValue, 'example name r')

                self.assertEqual(gpx.routes[0].points[0].comment, 'example cmt r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/cmt').firstChild.nodeValue, 'example cmt r')

                self.assertEqual(gpx.routes[0].points[0].description, 'example desc r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/desc').firstChild.nodeValue, 'example desc r')

                self.assertEqual(gpx.routes[0].points[0].source, 'example src r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/src').firstChild.nodeValue, 'example src r')

                self.assertEqual(gpx.routes[0].points[0].link, 'http://linkrtept')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/link').attributes['href'].nodeValue, 'http://linkrtept')

                self.assertEqual(gpx.routes[0].points[0].link_text, 'rtept link')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/link/text').firstChild.nodeValue, 'rtept link')

                self.assertEqual(gpx.routes[0].points[0].link_type, 'rtept link type')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/link/type').firstChild.nodeValue, 'rtept link type')

                self.assertEqual(gpx.routes[0].points[0].symbol, 'example sym r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/sym').firstChild.nodeValue, 'example sym r')

                self.assertEqual(gpx.routes[0].points[0].type, 'example type r')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/type').firstChild.nodeValue, 'example type r')

                self.assertEqual(gpx.routes[0].points[0].type_of_gpx_fix, '3d')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/fix').firstChild.nodeValue, '3d')

                self.assertEqual(gpx.routes[0].points[0].satellites, 6)
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/sat').firstChild.nodeValue, '6')

                self.assertEqual(gpx.routes[0].points[0].vertical_dilution, 8)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/vdop').firstChild.nodeValue in ('8.0', '8'))

                self.assertEqual(gpx.routes[0].points[0].horizontal_dilution, 7)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/hdop').firstChild.nodeValue in ('7.0', '7'))

                self.assertEqual(gpx.routes[0].points[0].position_dilution, 9)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/pdop').firstChild.nodeValue in ('9.0', '9'))

                self.assertEqual(gpx.routes[0].points[0].age_of_dgps_data, 10)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/ageofdgpsdata').firstChild.nodeValue in ('10.0', '10'))

                self.assertEqual(gpx.routes[0].points[0].dgps_id, '99')
                self.assertEqual(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/dgpsid').firstChild.nodeValue, '99')

                # second rtept:

                self.assertEqual(gpx.routes[0].points[1].latitude, 11)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[1]').attributes['lat'].value in ('11.0', '11'))

                self.assertEqual(gpx.routes[0].points[1].longitude, 21)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[1]').attributes['lon'].value in ('21.0', '21'))

                # gpx ext:
                self.assertEqual(1, len(gpx.extensions))
                gpxext = mod_etree.Element(namespace+'gpxext')
                gpxext.text = '...'
                gpxext.tail = ''
                self.assertTrue(elements_equal(gpx.extensions[0], gpxext))

                # trk

                self.assertEqual(len(gpx.tracks), 2)

                self.assertEqual(gpx.tracks[0].name, 'example name t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEqual(gpx.tracks[0].comment, 'example cmt t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEqual(gpx.tracks[0].description, 'example desc t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEqual(gpx.tracks[0].source, 'example src t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEqual(gpx.tracks[0].link, 'http://trk')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/link').attributes['href'].nodeValue, 'http://trk')

                self.assertEqual(gpx.tracks[0].link_text, 'trk link')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/link/text').firstChild.nodeValue, 'trk link')

                self.assertEqual(gpx.tracks[0].link_type, 'trk link type')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/link/type').firstChild.nodeValue, 'trk link type')

                self.assertEqual(gpx.tracks[0].number, 1)
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/number').firstChild.nodeValue, '1')

                self.assertEqual(gpx.tracks[0].type, 't')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/type').firstChild.nodeValue, 't')

                self.assertEqual(1, len(gpx.tracks[0].extensions))
                a1 = mod_etree.Element(namespace+'a1')
                a1.text = '2'
                a1.tail = ''
                self.assertTrue(elements_equal(gpx.tracks[0].extensions[0], a1))


                # trkpt:

                self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 11.1)
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/ele').firstChild.nodeValue, '11.1')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2013, 1, 1, 12, 0, 4))
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/time').firstChild.nodeValue in ('2013-01-01T12:00:04Z', '2013-01-01T12:00:04'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].magnetic_variation, 12)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/magvar').firstChild.nodeValue in ('12.0', '12'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].geoid_height, 13.0)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/geoidheight').firstChild.nodeValue in ('13.0', '13'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].name, 'example name t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].comment, 'example cmt t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].description, 'example desc t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].source, 'example src t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].link, 'http://trkpt')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/link').attributes['href'].nodeValue, 'http://trkpt')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].link_text, 'trkpt link')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/link/text').firstChild.nodeValue, 'trkpt link')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].link_type, 'trkpt link type')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/link/type').firstChild.nodeValue, 'trkpt link type')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].symbol, 'example sym t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/sym').firstChild.nodeValue, 'example sym t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].type, 'example type t')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/type').firstChild.nodeValue, 'example type t')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].type_of_gpx_fix, '3d')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/fix').firstChild.nodeValue, '3d')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].satellites, 100)
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/sat').firstChild.nodeValue, '100')

                self.assertEqual(gpx.tracks[0].segments[0].points[0].vertical_dilution, 102.)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/vdop').firstChild.nodeValue in ('102.0', '102'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].horizontal_dilution, 101)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/hdop').firstChild.nodeValue in ('101.0', '101'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].position_dilution, 103)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/pdop').firstChild.nodeValue in ('103.0', '103'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].age_of_dgps_data, 104)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/ageofdgpsdata').firstChild.nodeValue in ('104.0', '104'))

                self.assertEqual(gpx.tracks[0].segments[0].points[0].dgps_id, '99')
                self.assertEqual(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/dgpsid').firstChild.nodeValue, '99')

                self.assertEqual(1, len(gpx.tracks[0].segments[0].points[0].extensions))
                last = mod_etree.Element(namespace+'last')
                last.text = 'true'
                last.tail = ''
                self.assertTrue(elements_equal(gpx.tracks[0].segments[0].points[0].extensions[0], last))


        # Validated with SAXParser in "make test"

        # Clear extensions because those should be declared in the <gpx> but
        # gpxpy don't have support for this (yet):
        reparsed_gpx.extensions = {}
        reparsed_gpx.metadata_extensions = {}
        for waypoint in reparsed_gpx.waypoints:
            waypoint.extensions = {}
        for route in reparsed_gpx.routes:
            route.extensions = {}
            for point in route.points:
                point.extensions = {}
        for track in reparsed_gpx.tracks:
            track.extensions = {}
            for segment in track.segments:
                segment.extensions = {}
                for point in segment.points:
                    point.extensions = {}

        with open('test_files/validation_gpx11.gpx', 'w') as f:
            f.write(reparsed_gpx.to_xml())

    def test_10_to_11_conversion(self):
        """
        This test checks that reparsing from 1.0 to 1.1 and from 1.1 to 1.0
        will preserve all fields common for both versions.
        """
        original_gpx = mod_gpx.GPX()
        original_gpx.creator = 'cr'
        original_gpx.name = 'q'
        original_gpx.description = 'w'
        original_gpx.time = mod_datetime.datetime(2014, 4, 7, 21, 17, 39)
        original_gpx.bounds = mod_gpx.GPXBounds(1, 2, 3, 4)
        original_gpx.author_name = '789'
        original_gpx.author_email = '256@aaa'
        original_gpx.link = 'http://9890'
        original_gpx.link_text = '77888'
        original_gpx.keywords = 'kw'

        original_waypoint = mod_gpx.GPXWaypoint()
        original_waypoint.latitude = 12.3
        original_waypoint.longitude = 13.4
        original_waypoint.elevation = 121.89
        original_waypoint.time = mod_datetime.datetime(2015, 5, 8, 21, 17, 39)
        original_waypoint.magnetic_variation = 1
        original_waypoint.geoid_height = 1
        original_waypoint.name = 'n'
        original_waypoint.comment = 'cm'
        original_waypoint.description = 'des'
        original_waypoint.source = 'src'
        original_waypoint.symbol = 'sym'
        original_waypoint.type = 'ty'
        original_waypoint.type_of_gpx_fix = 'dgps'
        original_waypoint.satellites = 13
        original_waypoint.horizontal_dilution = 14
        original_waypoint.vertical_dilution = 15
        original_waypoint.position_dilution = 16
        original_waypoint.age_of_dgps_data = 16
        original_waypoint.dgps_id = '17'
        original_gpx.waypoints.append(original_waypoint)

        original_route = mod_gpx.GPXRoute()
        original_route.name = 'rten'
        original_route.comment = 'rtecm'
        original_route.description = 'rtedesc'
        original_route.source = 'rtesrc'
        # TODO url
        original_route.number = 101

        original_route_points = mod_gpx.GPXRoutePoint()
        original_route_points.latitude = 34.5
        original_route_points.longitude = 56.6
        original_route_points.elevation = 1001
        original_route_points.time = mod_datetime.datetime(2015, 5, 8, 21, 17, 17)
        original_route_points.magnetic_variation = 12
        original_route_points.geoid_height = 13
        original_route_points.name = 'aaaaa'
        original_route_points.comment = 'wwww'
        original_route_points.description = 'cccc'
        original_route_points.source = 'qqq'
        # TODO url
        original_route_points.symbol = 'a.png'
        original_route_points.type = '2'
        original_route_points.type_of_gpx_fix = 'pps'
        original_route_points.satellites = 23
        original_route_points.horizontal_dilution = 19
        original_route_points.vertical_dilution = 20
        original_route_points.position_dilution = 21
        original_route_points.age_of_dgps_data = 22
        original_route_points.dgps_id = '23'
        original_route.points.append(original_route_points)
        original_gpx.routes.append(original_route)

        original_track = mod_gpx.GPXTrack()
        original_track.name = 'rten'
        original_track.comment = 'rtecm'
        original_track.description = 'rtedesc'
        original_track.source = 'rtesrc'
        # TODO url
        original_track.number = 101

        original_track_point = mod_gpx.GPXTrackPoint()
        original_track_point.latitude = 34.6
        original_track_point.longitude = 57.6
        original_track_point.elevation = 1002
        original_track_point.time = mod_datetime.datetime(2016, 5, 8, 21, 17, 17)
        original_track_point.magnetic_variation = 13
        original_track_point.geoid_height = 14
        original_track_point.name = 'aaaaajkjk'
        original_track_point.comment = 'wwwwii'
        original_track_point.description = 'ciccc'
        original_track_point.source = 'qssqq'
        # TODO url
        original_track_point.symbol = 'ai.png'
        original_track_point.type = '3'
        original_track_point.type_of_gpx_fix = 'pps'
        original_track_point.satellites = 24
        original_track_point.horizontal_dilution = 20
        original_track_point.vertical_dilution = 21
        original_track_point.position_dilution = 22
        original_track_point.age_of_dgps_data = 23
        original_track_point.dgps_id = '22'

        original_track.segments.append(mod_gpx.GPXTrackSegment())
        original_track.segments[0].points.append(original_track_point)

        original_gpx.tracks.append(original_track)

        # Convert do GPX1.0:
        xml_10 = original_gpx.to_xml('1.0')
        print(xml_10)
        self.assertTrue('http://www.topografix.com/GPX/1/0' in xml_10)
        #pretty_print_xml(xml_10)
        gpx_1 = mod_gpxpy.parse(xml_10)

        # Convert do GPX1.1:
        xml_11 = gpx_1.to_xml('1.1')
        print(xml_11)
        self.assertTrue('http://www.topografix.com/GPX/1/1' in xml_11 and 'metadata' in xml_11)
        #pretty_print_xml(xml_11)
        gpx_2 = mod_gpxpy.parse(xml_11)

        # Convert do GPX1.0 again:
        xml_10 = gpx_2.to_xml('1.0')
        self.assertTrue('http://www.topografix.com/GPX/1/0' in xml_10)
        #pretty_print_xml(xml_10)
        gpx_3 = mod_gpxpy.parse(xml_10)

        for gpx in (gpx_1, gpx_2, gpx_3, ):
            self.assertTrue(gpx.creator is not None)
            self.assertEqual(original_gpx.creator, gpx.creator)

            self.assertTrue(gpx.name is not None)
            self.assertEqual(original_gpx.name, gpx.name)

            self.assertTrue(gpx.description is not None)
            self.assertEqual(original_gpx.description, gpx.description)

            self.assertTrue(gpx.keywords is not None)
            self.assertEqual(original_gpx.keywords, gpx.keywords)

            self.assertTrue(gpx.time is not None)
            self.assertEqual(original_gpx.time, gpx.time)

            self.assertTrue(gpx.author_name is not None)
            self.assertEqual(original_gpx.author_name, gpx.author_name)

            self.assertTrue(gpx.author_email is not None)
            self.assertEqual(original_gpx.author_email, gpx.author_email)

            self.assertTrue(gpx.link is not None)
            self.assertEqual(original_gpx.link, gpx.link)

            self.assertTrue(gpx.link_text is not None)
            self.assertEqual(original_gpx.link_text, gpx.link_text)

            self.assertTrue(gpx.bounds is not None)
            self.assertEqual(tuple(original_gpx.bounds), tuple(gpx.bounds))

            self.assertEqual(1, len(gpx.waypoints))

            self.assertTrue(gpx.waypoints[0].latitude is not None)
            self.assertEqual(original_gpx.waypoints[0].latitude, gpx.waypoints[0].latitude)

            self.assertTrue(gpx.waypoints[0].longitude is not None)
            self.assertEqual(original_gpx.waypoints[0].longitude, gpx.waypoints[0].longitude)

            self.assertTrue(gpx.waypoints[0].elevation is not None)
            self.assertEqual(original_gpx.waypoints[0].elevation, gpx.waypoints[0].elevation)

            self.assertTrue(gpx.waypoints[0].time is not None)
            self.assertEqual(original_gpx.waypoints[0].time, gpx.waypoints[0].time)

            self.assertTrue(gpx.waypoints[0].magnetic_variation is not None)
            self.assertEqual(original_gpx.waypoints[0].magnetic_variation, gpx.waypoints[0].magnetic_variation)

            self.assertTrue(gpx.waypoints[0].geoid_height is not None)
            self.assertEqual(original_gpx.waypoints[0].geoid_height, gpx.waypoints[0].geoid_height)

            self.assertTrue(gpx.waypoints[0].name is not None)
            self.assertEqual(original_gpx.waypoints[0].name, gpx.waypoints[0].name)

            self.assertTrue(gpx.waypoints[0].comment is not None)
            self.assertEqual(original_gpx.waypoints[0].comment, gpx.waypoints[0].comment)

            self.assertTrue(gpx.waypoints[0].description is not None)
            self.assertEqual(original_gpx.waypoints[0].description, gpx.waypoints[0].description)

            self.assertTrue(gpx.waypoints[0].source is not None)
            self.assertEqual(original_gpx.waypoints[0].source, gpx.waypoints[0].source)

            # TODO: Link/url

            self.assertTrue(gpx.waypoints[0].symbol is not None)
            self.assertEqual(original_gpx.waypoints[0].symbol, gpx.waypoints[0].symbol)

            self.assertTrue(gpx.waypoints[0].type is not None)
            self.assertEqual(original_gpx.waypoints[0].type, gpx.waypoints[0].type)

            self.assertTrue(gpx.waypoints[0].type_of_gpx_fix is not None)
            self.assertEqual(original_gpx.waypoints[0].type_of_gpx_fix, gpx.waypoints[0].type_of_gpx_fix)

            self.assertTrue(gpx.waypoints[0].satellites is not None)
            self.assertEqual(original_gpx.waypoints[0].satellites, gpx.waypoints[0].satellites)

            self.assertTrue(gpx.waypoints[0].horizontal_dilution is not None)
            self.assertEqual(original_gpx.waypoints[0].horizontal_dilution, gpx.waypoints[0].horizontal_dilution)

            self.assertTrue(gpx.waypoints[0].vertical_dilution is not None)
            self.assertEqual(original_gpx.waypoints[0].vertical_dilution, gpx.waypoints[0].vertical_dilution)

            self.assertTrue(gpx.waypoints[0].position_dilution is not None)
            self.assertEqual(original_gpx.waypoints[0].position_dilution, gpx.waypoints[0].position_dilution)

            self.assertTrue(gpx.waypoints[0].age_of_dgps_data is not None)
            self.assertEqual(original_gpx.waypoints[0].age_of_dgps_data, gpx.waypoints[0].age_of_dgps_data)

            self.assertTrue(gpx.waypoints[0].dgps_id is not None)
            self.assertEqual(original_gpx.waypoints[0].dgps_id, gpx.waypoints[0].dgps_id)

            # route(s):

            self.assertTrue(gpx.routes[0].name is not None)
            self.assertEqual(original_gpx.routes[0].name, gpx.routes[0].name)

            self.assertTrue(gpx.routes[0].comment is not None)
            self.assertEqual(original_gpx.routes[0].comment, gpx.routes[0].comment)

            self.assertTrue(gpx.routes[0].description is not None)
            self.assertEqual(original_gpx.routes[0].description, gpx.routes[0].description)

            self.assertTrue(gpx.routes[0].source is not None)
            self.assertEqual(original_gpx.routes[0].source, gpx.routes[0].source)

            self.assertTrue(gpx.routes[0].number is not None)
            self.assertEqual(original_gpx.routes[0].number, gpx.routes[0].number)

            self.assertTrue(gpx.routes[0].points[0].latitude is not None)
            self.assertEqual(original_gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].latitude)

            self.assertTrue(gpx.routes[0].points[0].longitude is not None)
            self.assertEqual(original_gpx.routes[0].points[0].longitude, gpx.routes[0].points[0].longitude)

            self.assertTrue(gpx.routes[0].points[0].elevation is not None)
            self.assertEqual(original_gpx.routes[0].points[0].elevation, gpx.routes[0].points[0].elevation)

            self.assertTrue(gpx.routes[0].points[0].time is not None)
            self.assertEqual(original_gpx.routes[0].points[0].time, gpx.routes[0].points[0].time)

            self.assertTrue(gpx.routes[0].points[0].magnetic_variation is not None)
            self.assertEqual(original_gpx.routes[0].points[0].magnetic_variation, gpx.routes[0].points[0].magnetic_variation)

            self.assertTrue(gpx.routes[0].points[0].geoid_height is not None)
            self.assertEqual(original_gpx.routes[0].points[0].geoid_height, gpx.routes[0].points[0].geoid_height)

            self.assertTrue(gpx.routes[0].points[0].name is not None)
            self.assertEqual(original_gpx.routes[0].points[0].name, gpx.routes[0].points[0].name)

            self.assertTrue(gpx.routes[0].points[0].comment is not None)
            self.assertEqual(original_gpx.routes[0].points[0].comment, gpx.routes[0].points[0].comment)

            self.assertTrue(gpx.routes[0].points[0].description is not None)
            self.assertEqual(original_gpx.routes[0].points[0].description, gpx.routes[0].points[0].description)

            self.assertTrue(gpx.routes[0].points[0].source is not None)
            self.assertEqual(original_gpx.routes[0].points[0].source, gpx.routes[0].points[0].source)

            self.assertTrue(gpx.routes[0].points[0].symbol is not None)
            self.assertEqual(original_gpx.routes[0].points[0].symbol, gpx.routes[0].points[0].symbol)

            self.assertTrue(gpx.routes[0].points[0].type is not None)
            self.assertEqual(original_gpx.routes[0].points[0].type, gpx.routes[0].points[0].type)

            self.assertTrue(gpx.routes[0].points[0].type_of_gpx_fix is not None)
            self.assertEqual(original_gpx.routes[0].points[0].type_of_gpx_fix, gpx.routes[0].points[0].type_of_gpx_fix)

            self.assertTrue(gpx.routes[0].points[0].satellites is not None)
            self.assertEqual(original_gpx.routes[0].points[0].satellites, gpx.routes[0].points[0].satellites)

            self.assertTrue(gpx.routes[0].points[0].horizontal_dilution is not None)
            self.assertEqual(original_gpx.routes[0].points[0].horizontal_dilution, gpx.routes[0].points[0].horizontal_dilution)

            self.assertTrue(gpx.routes[0].points[0].vertical_dilution is not None)
            self.assertEqual(original_gpx.routes[0].points[0].vertical_dilution, gpx.routes[0].points[0].vertical_dilution)

            self.assertTrue(gpx.routes[0].points[0].position_dilution is not None)
            self.assertEqual(original_gpx.routes[0].points[0].position_dilution, gpx.routes[0].points[0].position_dilution)

            self.assertTrue(gpx.routes[0].points[0].age_of_dgps_data is not None)
            self.assertEqual(original_gpx.routes[0].points[0].age_of_dgps_data, gpx.routes[0].points[0].age_of_dgps_data)

            self.assertTrue(gpx.routes[0].points[0].dgps_id is not None)
            self.assertEqual(original_gpx.routes[0].points[0].dgps_id, gpx.routes[0].points[0].dgps_id)

            # track(s):

            self.assertTrue(gpx.tracks[0].name is not None)
            self.assertEqual(original_gpx.tracks[0].name, gpx.tracks[0].name)

            self.assertTrue(gpx.tracks[0].comment is not None)
            self.assertEqual(original_gpx.tracks[0].comment, gpx.tracks[0].comment)

            self.assertTrue(gpx.tracks[0].description is not None)
            self.assertEqual(original_gpx.tracks[0].description, gpx.tracks[0].description)

            self.assertTrue(gpx.tracks[0].source is not None)
            self.assertEqual(original_gpx.tracks[0].source, gpx.tracks[0].source)

            self.assertTrue(gpx.tracks[0].number is not None)
            self.assertEqual(original_gpx.tracks[0].number, gpx.tracks[0].number)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].latitude is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].latitude)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].longitude is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].longitude, gpx.tracks[0].segments[0].points[0].longitude)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].elevation is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].elevation, gpx.tracks[0].segments[0].points[0].elevation)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].time is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].time, gpx.tracks[0].segments[0].points[0].time)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].magnetic_variation is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].magnetic_variation, gpx.tracks[0].segments[0].points[0].magnetic_variation)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].geoid_height is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].geoid_height, gpx.tracks[0].segments[0].points[0].geoid_height)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].name is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].name, gpx.tracks[0].segments[0].points[0].name)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].comment is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].comment, gpx.tracks[0].segments[0].points[0].comment)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].description is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].description, gpx.tracks[0].segments[0].points[0].description)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].source is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].source, gpx.tracks[0].segments[0].points[0].source)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].symbol is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].symbol, gpx.tracks[0].segments[0].points[0].symbol)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].type is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].type, gpx.tracks[0].segments[0].points[0].type)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].type_of_gpx_fix is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].type_of_gpx_fix, gpx.tracks[0].segments[0].points[0].type_of_gpx_fix)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].satellites is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].satellites, gpx.tracks[0].segments[0].points[0].satellites)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].horizontal_dilution is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].horizontal_dilution, gpx.tracks[0].segments[0].points[0].horizontal_dilution)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].vertical_dilution is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].vertical_dilution, gpx.tracks[0].segments[0].points[0].vertical_dilution)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].position_dilution is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].position_dilution, gpx.tracks[0].segments[0].points[0].position_dilution)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].age_of_dgps_data is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].age_of_dgps_data, gpx.tracks[0].segments[0].points[0].age_of_dgps_data)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].dgps_id is not None)
            self.assertEqual(original_gpx.tracks[0].segments[0].points[0].dgps_id, gpx.tracks[0].segments[0].points[0].dgps_id)
