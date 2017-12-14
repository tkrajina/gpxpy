# -*- coding: utf-8 -*-

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



from __future__ import print_function

import logging as mod_logging
import os as mod_os
import time as mod_time
import codecs as mod_codecs
import copy as mod_copy
import datetime as mod_datetime
import random as mod_random
import math as mod_math
import sys as mod_sys
import xml.dom.minidom as mod_minidom

try:
    import xml.etree.cElementTree as mod_etree
    #import lxml.etree as mod_etree  # Load LXML or fallback to cET or ET
except:
    try:
        import xml.etree.cElementTree as mod_etree
    except:
        import xml.etree.ElementTree as mod_etree

try:
    import unittest2 as mod_unittest
except ImportError:
    import unittest as mod_unittest

import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx
import gpxpy.gpxfield as mod_gpxfield
import gpxpy.parser as mod_parser
import gpxpy.geo as mod_geo

from gpxpy.utils import make_str

PYTHON_VERSION = mod_sys.version.split(' ')[0]

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')


def equals(object1, object2, ignore=None):
    """ Testing purposes only """

    if not object1 and not object2:
        return True

    if not object1 or not object2:
        print('Not obj2')
        return False

    if not object1.__class__ == object2.__class__:
        print('Not obj1')
        return False

    attributes = []
    for attr in dir(object1):
        if not ignore or not attr in ignore:
            if not hasattr(object1, '__call__') and not attr.startswith('_'):
                if not attr in attributes:
                    attributes.append(attr)

    for attr in attributes:
        attr1 = getattr(object1, attr)
        attr2 = getattr(object2, attr)

        if attr1 == attr2:
            return True

        if not attr1 and not attr2:
            return True
        if not attr1 or not attr2:
            print('Object differs in attribute %s (%s - %s)' % (attr, attr1, attr2))
            return False

        if not equals(attr1, attr2):
            print('Object differs in attribute %s (%s - %s)' % (attr, attr1, attr2))
            return None

    return True


def custom_open(filename, encoding=None):
    if PYTHON_VERSION[0] == '3':
        return open(filename, encoding=encoding)
    elif encoding == 'utf-8':
        mod_codecs.open(filename, encoding='utf-7')
    return open(filename)


def cca(number1, number2):
    return 1 - number1 / number2 < 0.999


def get_dom_node(dom, path):
    path_parts = path.split('/')
    result = dom
    for path_part in path_parts:
        if '[' in path_part:
            tag_name = path_part.split('[')[0]
            n = int(path_part.split('[')[1].replace(']', ''))
        else:
            tag_name = path_part
            n = 0

        candidates = []
        for child in result.childNodes:
            if child.nodeName == tag_name:
                candidates.append(child)

        try:
            result = candidates[n]
        except Exception:
            raise Exception('Can\'t fint %sth child of %s' % (n, path_part))

    return result


def pretty_print_xml(xml):
    dom = mod_minidom.parseString(xml)
    print(dom.toprettyxml())


class GPXTests(mod_unittest.TestCase):
    """
    Add tests here.

    Tests will be run twice (once with Lxml and once with Minidom Parser).

    If you run 'make test' then all tests will be run with python2 and python3

    To be even more sure that everything works as expected -- try...
        python -m unittest test.MinidomTests
    ...with python-lxml and without python-lxml installed.
    """

    def parse(self, file, encoding=None, version = None):
        f = custom_open('test_files/%s' % file, encoding=encoding)

        parser = mod_parser.GPXParser(f)
        gpx = parser.parse(version)
        f.close()

        if not gpx:
            print('Parser error: %s' % parser.get_error())

        return gpx

    def reparse(self, gpx):
        xml = gpx.to_xml()

        parser = mod_parser.GPXParser(xml)
        gpx = parser.parse()

        if not gpx:
            print('Parser error while reparsing: %s' % parser.get_error())

        return gpx

    def elements_equal(e1, e2):
        if e1.tag != e2.tag: return False
        if e1.text != e2.text: return False
        if e1.tail != e2.tail: return False
        if e1.attrib != e2.attrib: return False
        if len(e1) != len(e2): return False
        return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

    def test_extensions(self):
        """ Test extensions """

        with open('test_files/gpx1.1_with_extensions.gpx') as f:
            xml = f.read()

        gpx = mod_gpxpy.parse(xml)
        print(gpx.to_xml('1.1', prettyprint=False))

        with open('test_files/gpx1.1_with_all_fields.gpx') as f:
            xml = f.read()
        gpx = mod_gpxpy.parse(xml)
        print(gpx.to_xml('1.1', prettyprint=False))
    
    @mod_unittest.skipIf(True, "Because I said")
    def test_gpx_11_fields(self):
        """ Test (de) serialization all gpx1.0 fields """

        with open('test_files/gpx1.1_with_all_fields.gpx') as f:
            xml = f.read()

        original_gpx = mod_gpxpy.parse(xml)

        # Serialize and parse again to be sure that all is preserved:
        reparsed_gpx = mod_gpxpy.parse(original_gpx.to_xml('1.1'))

        original_dom = mod_minidom.parseString(xml)
        reparsed_dom = mod_minidom.parseString(reparsed_gpx.to_xml('1.1'))

        for gpx in (original_gpx, reparsed_gpx):
            for dom in (original_dom, reparsed_dom):
                self.assertEquals(gpx.version, '1.1')
                self.assertEquals(get_dom_node(dom, 'gpx').attributes['version'].nodeValue, '1.1')

                self.assertEquals(gpx.creator, '...')
                self.assertEquals(get_dom_node(dom, 'gpx').attributes['creator'].nodeValue, '...')

                self.assertEquals(gpx.name, 'example name')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/name').firstChild.nodeValue, 'example name')

                self.assertEquals(gpx.description, 'example description')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/desc').firstChild.nodeValue, 'example description')

                self.assertEquals(gpx.author_name, 'author name')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/author/name').firstChild.nodeValue, 'author name')

                self.assertEquals(gpx.author_email, 'aaa@bbb.com')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/author/email').attributes['id'].nodeValue, 'aaa')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/author/email').attributes['domain'].nodeValue, 'bbb.com')

                self.assertEquals(gpx.author_link, 'http://link')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/author/link').attributes['href'].nodeValue, 'http://link')

                self.assertEquals(gpx.author_link_text, 'link text')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/author/link/text').firstChild.nodeValue, 'link text')

                self.assertEquals(gpx.author_link_type, 'link type')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/author/link/type').firstChild.nodeValue, 'link type')

                self.assertEquals(gpx.copyright_author, 'gpxauth')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/copyright').attributes['author'].nodeValue, 'gpxauth')

                self.assertEquals(gpx.copyright_year, '2013')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/copyright/year').firstChild.nodeValue, '2013')

                self.assertEquals(gpx.copyright_license, 'lic')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/copyright/license').firstChild.nodeValue, 'lic')

                self.assertEquals(gpx.link, 'http://link2')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/link').attributes['href'].nodeValue, 'http://link2')

                self.assertEquals(gpx.link_text, 'link text2')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/link/text').firstChild.nodeValue, 'link text2')

                self.assertEquals(gpx.link_type, 'link type2')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/link/type').firstChild.nodeValue, 'link type2')

                self.assertEquals(gpx.time, mod_datetime.datetime(2013, 1, 1, 12, 0))
                self.assertTrue(get_dom_node(dom, 'gpx/metadata/time').firstChild.nodeValue in ('2013-01-01T12:00:00Z', '2013-01-01T12:00:00'))

                self.assertEquals(gpx.keywords, 'example keywords')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/keywords').firstChild.nodeValue, 'example keywords')

                self.assertEquals(gpx.bounds.min_latitude, 1.2)
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/bounds').attributes['minlat'].value, '1.2')

                # TODO

                self.assertEquals(len(gpx.metadata_extensions), 3)
                self.assertEquals(gpx.metadata_extensions['aaa'], 'bbb')
                self.assertEquals(gpx.metadata_extensions['bbb'], 'ccc')
                self.assertEquals(gpx.metadata_extensions['ccc'], 'ddd')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/extensions/aaa').firstChild.nodeValue, 'bbb')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/extensions/bbb').firstChild.nodeValue, 'ccc')
                self.assertEquals(get_dom_node(dom, 'gpx/metadata/extensions/ccc').firstChild.nodeValue, 'ddd')

                self.assertEquals(2, len(gpx.waypoints))

                self.assertEquals(gpx.waypoints[0].latitude, 12.3)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]').attributes['lat'].value, '12.3')

                self.assertEquals(gpx.waypoints[0].longitude, 45.6)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]').attributes['lon'].value, '45.6')

                self.assertEquals(gpx.waypoints[0].longitude, 45.6)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]').attributes['lon'].value, '45.6')

                self.assertEquals(gpx.waypoints[0].elevation, 75.1)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/ele').firstChild.nodeValue, '75.1')

                self.assertEquals(gpx.waypoints[0].time, mod_datetime.datetime(2013, 1, 2, 2, 3))
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/time').firstChild.nodeValue, '2013-01-02T02:03:00Z')

                self.assertEquals(gpx.waypoints[0].magnetic_variation, 1.1)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/magvar').firstChild.nodeValue, '1.1')

                self.assertEquals(gpx.waypoints[0].geoid_height, 2.0)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/geoidheight').firstChild.nodeValue, '2.0')

                self.assertEquals(gpx.waypoints[0].name, 'example name')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/name').firstChild.nodeValue, 'example name')

                self.assertEquals(gpx.waypoints[0].comment, 'example cmt')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEquals(gpx.waypoints[0].description, 'example desc')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEquals(gpx.waypoints[0].source, 'example src')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/src').firstChild.nodeValue, 'example src')

                self.assertEquals(gpx.waypoints[0].link, 'http://link3')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/link').attributes['href'].nodeValue, 'http://link3')

                self.assertEquals(gpx.waypoints[0].link_text, 'link text3')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/link/text').firstChild.nodeValue, 'link text3')

                self.assertEquals(gpx.waypoints[0].link_type, 'link type3')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/link/type').firstChild.nodeValue, 'link type3')

                self.assertEquals(gpx.waypoints[1].latitude, 13.4)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[1]').attributes['lat'].value, '13.4')

                self.assertEquals(gpx.waypoints[1].longitude, 46.7)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[1]').attributes['lon'].value, '46.7')

                self.assertEquals(2, len(gpx.waypoints[0].extensions))
                self.assertEquals('bbb', gpx.waypoints[0].extensions['aaa'])
                self.assertEquals('ddd', gpx.waypoints[0].extensions['ccc'])

                # 1. rte

                self.assertEquals(gpx.routes[0].name, 'example name')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/name').firstChild.nodeValue, 'example name')

                self.assertEquals(gpx.routes[0].comment, 'example cmt')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEquals(gpx.routes[0].description, 'example desc')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEquals(gpx.routes[0].source, 'example src')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/src').firstChild.nodeValue, 'example src')

                self.assertEquals(gpx.routes[0].link, 'http://link3')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/link').attributes['href'].nodeValue, 'http://link3')

                self.assertEquals(gpx.routes[0].link_text, 'link text3')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/link/text').firstChild.nodeValue, 'link text3')

                self.assertEquals(gpx.routes[0].link_type, 'link type3')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/link/type').firstChild.nodeValue, 'link type3')

                self.assertEquals(gpx.routes[0].number, 7)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/number').firstChild.nodeValue, '7')

                self.assertEquals(gpx.routes[0].type, 'rte type')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/type').firstChild.nodeValue, 'rte type')

                self.assertEquals(2, len(gpx.routes[0].extensions))
                self.assertEquals(gpx.routes[0].extensions['rtee1'], '1')
                self.assertEquals(gpx.routes[0].extensions['rtee2'], '2')


                # 2. rte

                self.assertEquals(gpx.routes[1].name, 'second route')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[1]/name').firstChild.nodeValue, 'second route')

                self.assertEquals(gpx.routes[1].description, 'example desc 2')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[1]/desc').firstChild.nodeValue, 'example desc 2')

                self.assertEquals(gpx.routes[1].link, None)

                self.assertEquals(gpx.routes[0].number, 7)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/number').firstChild.nodeValue, '7')

                self.assertEquals(len(gpx.routes[0].points), 3)
                self.assertEquals(len(gpx.routes[1].points), 2)

                # Rtept

                self.assertEquals(gpx.routes[0].points[0].latitude, 10)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]').attributes['lat'].value in ('10.0', '10'))

                self.assertEquals(gpx.routes[0].points[0].longitude, 20)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]').attributes['lon'].value in ('20.0', '20'))

                self.assertEquals(gpx.routes[0].points[0].elevation, 75.1)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/ele').firstChild.nodeValue, '75.1')

                self.assertEquals(gpx.routes[0].points[0].time, mod_datetime.datetime(2013, 1, 2, 2, 3, 3))
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/time').firstChild.nodeValue, '2013-01-02T02:03:03Z')

                self.assertEquals(gpx.routes[0].points[0].magnetic_variation, 1.2)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/magvar').firstChild.nodeValue, '1.2')

                self.assertEquals(gpx.routes[0].points[0].geoid_height, 2.1)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/geoidheight').firstChild.nodeValue, '2.1')

                self.assertEquals(gpx.routes[0].points[0].name, 'example name r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/name').firstChild.nodeValue, 'example name r')

                self.assertEquals(gpx.routes[0].points[0].comment, 'example cmt r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/cmt').firstChild.nodeValue, 'example cmt r')

                self.assertEquals(gpx.routes[0].points[0].description, 'example desc r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/desc').firstChild.nodeValue, 'example desc r')

                self.assertEquals(gpx.routes[0].points[0].source, 'example src r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/src').firstChild.nodeValue, 'example src r')

                self.assertEquals(gpx.routes[0].points[0].link, 'http://linkrtept')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/link').attributes['href'].nodeValue, 'http://linkrtept')

                self.assertEquals(gpx.routes[0].points[0].link_text, 'rtept link')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/link/text').firstChild.nodeValue, 'rtept link')

                self.assertEquals(gpx.routes[0].points[0].link_type, 'rtept link type')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/link/type').firstChild.nodeValue, 'rtept link type')

                self.assertEquals(gpx.routes[0].points[0].symbol, 'example sym r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/sym').firstChild.nodeValue, 'example sym r')

                self.assertEquals(gpx.routes[0].points[0].type, 'example type r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/type').firstChild.nodeValue, 'example type r')

                self.assertEquals(gpx.routes[0].points[0].type_of_gpx_fix, '3d')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/fix').firstChild.nodeValue, '3d')

                self.assertEquals(gpx.routes[0].points[0].satellites, 6)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/sat').firstChild.nodeValue, '6')

                self.assertEquals(gpx.routes[0].points[0].vertical_dilution, 8)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/vdop').firstChild.nodeValue in ('8.0', '8'))

                self.assertEquals(gpx.routes[0].points[0].horizontal_dilution, 7)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/hdop').firstChild.nodeValue in ('7.0', '7'))

                self.assertEquals(gpx.routes[0].points[0].position_dilution, 9)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/pdop').firstChild.nodeValue in ('9.0', '9'))

                self.assertEquals(gpx.routes[0].points[0].age_of_dgps_data, 10)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/ageofdgpsdata').firstChild.nodeValue in ('10.0', '10'))

                self.assertEquals(gpx.routes[0].points[0].dgps_id, '99')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/dgpsid').firstChild.nodeValue, '99')

                # second rtept:

                self.assertEquals(gpx.routes[0].points[1].latitude, 11)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[1]').attributes['lat'].value in ('11.0', '11'))

                self.assertEquals(gpx.routes[0].points[1].longitude, 21)
                self.assertTrue(get_dom_node(dom, 'gpx/rte[0]/rtept[1]').attributes['lon'].value in ('21.0', '21'))

                # gpx ext:
                self.assertEquals(1, len(gpx.extensions))
                self.assertEquals(gpx.extensions['gpxext'], '...')

                # trk

                self.assertEquals(len(gpx.tracks), 2)

                self.assertEquals(gpx.tracks[0].name, 'example name t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEquals(gpx.tracks[0].comment, 'example cmt t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEquals(gpx.tracks[0].description, 'example desc t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEquals(gpx.tracks[0].source, 'example src t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEquals(gpx.tracks[0].link, 'http://trk')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/link').attributes['href'].nodeValue, 'http://trk')

                self.assertEquals(gpx.tracks[0].link_text, 'trk link')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/link/text').firstChild.nodeValue, 'trk link')

                self.assertEquals(gpx.tracks[0].link_type, 'trk link type')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/link/type').firstChild.nodeValue, 'trk link type')

                self.assertEquals(gpx.tracks[0].number, 1)
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/number').firstChild.nodeValue, '1')

                self.assertEquals(gpx.tracks[0].type, 't')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/type').firstChild.nodeValue, 't')

                self.assertEquals(1, len(gpx.tracks[0].extensions))
                self.assertEquals('2', gpx.tracks[0].extensions['a1'])

                # trkpt:

                self.assertEquals(gpx.tracks[0].segments[0].points[0].elevation, 11.1)
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/ele').firstChild.nodeValue, '11.1')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2013, 1, 1, 12, 0, 4))
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/time').firstChild.nodeValue in ('2013-01-01T12:00:04Z', '2013-01-01T12:00:04'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].magnetic_variation, 12)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/magvar').firstChild.nodeValue in ('12.0', '12'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].geoid_height, 13.0)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/geoidheight').firstChild.nodeValue in ('13.0', '13'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].name, 'example name t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].comment, 'example cmt t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].description, 'example desc t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].source, 'example src t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].link, 'http://trkpt')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/link').attributes['href'].nodeValue, 'http://trkpt')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].link_text, 'trkpt link')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/link/text').firstChild.nodeValue, 'trkpt link')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].link_type, 'trkpt link type')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/link/type').firstChild.nodeValue, 'trkpt link type')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].symbol, 'example sym t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/sym').firstChild.nodeValue, 'example sym t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].type, 'example type t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/type').firstChild.nodeValue, 'example type t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].type_of_gpx_fix, '3d')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/fix').firstChild.nodeValue, '3d')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].satellites, 100)
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/sat').firstChild.nodeValue, '100')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].vertical_dilution, 102.)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/vdop').firstChild.nodeValue in ('102.0', '102'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].horizontal_dilution, 101)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/hdop').firstChild.nodeValue in ('101.0', '101'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].position_dilution, 103)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/pdop').firstChild.nodeValue in ('103.0', '103'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].age_of_dgps_data, 104)
                self.assertTrue(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/ageofdgpsdata').firstChild.nodeValue in ('104.0', '104'))

                self.assertEquals(gpx.tracks[0].segments[0].points[0].dgps_id, '99')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/dgpsid').firstChild.nodeValue, '99')

                self.assertEquals(1, len(gpx.tracks[0].segments[0].points[0].extensions))
                self.assertEquals('true', gpx.tracks[0].segments[0].points[0].extensions['last'])

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

        with open('validation_gpx11.gpx', 'w') as f:
            f.write(reparsed_gpx.to_xml())











 
class LxmlTest(mod_unittest.TestCase):
    @mod_unittest.skipIf(mod_os.environ.get('XMLPARSER')!="LXML", "LXML not installed")
    def test_checklxml(self):
        self.assertEqual('LXML', mod_parser.GPXParser._GPXParser__library())


if __name__ == '__main__':
    mod_unittest.main()
