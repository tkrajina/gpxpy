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

import pdb

import logging as mod_logging
import datetime as mod_datetime

from lxml import etree

import gpx as mod_gpx
import utils as mod_utils
import re as mod_re


def parse_time(string):
    if not string:
        return None
    try:
        return mod_datetime.datetime.strptime(string, mod_gpx.DATE_FORMAT)
    except Exception, e:
        if mod_re.match('^.*\.\d+Z$', string):
            string = mod_re.sub('\.\d+Z', 'Z', string)
        try:
            return mod_datetime.datetime.strptime(string, mod_gpx.DATE_FORMAT)
        except Exception, e:
            mod_logging.error('Invalid timestemp %s' % string)
            return None


class AbstractXMLParser:
    """ Common methods used in GPXParser and KMLParser """

    gpx = None
    xml = None

    valid = None
    error = None

    def init(self, xml_or_file):
        if hasattr(xml_or_file, 'read'):
            self.xml = xml_or_file.read()
        else:
            if isinstance(xml_or_file, unicode):
                self.xml = xml_or_file.encode('utf-8')
            else:
                self.xml = str(xml_or_file)

        self.valid = False
        self.error = None

        self.gpx = mod_gpx.GPX()

    def is_valid(self):
        return self.valid

    def get_error(self):
        return self.error

    def get_gpx(self):
        return self.gpx

    def get_node_data(self, node):
        if node is None:
            return None
        child_nodes = node.getchildren()
        if not child_nodes or len(child_nodes) == 0:
            return None
        return child_nodes[0].text


class GPXParser(AbstractXMLParser):

    def __init__(self, xml_or_file=None):
        self.init(xml_or_file)

        self.gpx = mod_gpx.GPX()

    def parse(self):
        try:
            dom = etree.XML(self.xml)
            self.__parse_dom(dom)

            return self.gpx
        except Exception, e:
            mod_logging.debug('Error in:\n%s\n-----------\n' % self.xml)
            mod_logging.exception(e)
            self.error = str(e)

            return None

    def __parse_dom(self, dom):
        # get the namespace
        self.ns = dom.nsmap.get(None)

        if dom.tag != mod_utils.tag('gpx',self.ns):
            raise mod_gpx.GPXException('Document must have a `gpx` root node.')

        for node in dom.getchildren():
            if node.tag == mod_utils.tag('time',self.ns):
                time_str = self.get_node_data(node)
                self.gpx.time = parse_time(time_str)
            elif node.tag == mod_utils.tag('name',self.ns):
                self.gpx.name = self.get_node_data(node)
            elif node.tag == mod_utils.tag('desc',self.ns):
                self.gpx.description = self.get_node_data(node)
            elif node.tag == mod_utils.tag('author',self.ns):
                self.gpx.author = self.get_node_data(node)
            elif node.tag == mod_utils.tag('email',self.ns):
                self.gpx.email = self.get_node_data(node)
            elif node.tag == mod_utils.tag('url',self.ns):
                self.gpx.url = self.get_node_data(node)
            elif node.tag == mod_utils.tag('urlname',self.ns):
                self.gpx.urlname = self.get_node_data(node)
            elif node.tag == mod_utils.tag('keywords',self.ns):
                self.gpx.keywords = self.get_node_data(node)
            elif node.tag == mod_utils.tag('bounds',self.ns):
                self._parse_bounds(node)
            elif node.tag == mod_utils.tag('wpt',self.ns):
                self.gpx.waypoints.append(self._parse_waypoint(node))
            elif node.tag == mod_utils.tag('rte',self.ns):
                self.gpx.routes.append(self._parse_route(node))
            elif node.tag == mod_utils.tag('trk',self.ns):
                self.gpx.tracks.append(self.__parse_track(node))
            else:
                #print 'unknown %s' % node
                pass

        self.valid = True

    def _parse_bounds(self, node):
        if node.attrib.get('minlat'):
            self.gpx.min_latitude = mod_utils.to_number(node.attrib.get('minlat'))
        if node.attrib.get('maxlat'):
            self.gpx.min_latitude = mod_utils.to_number(node.attrib.get('maxlat'))
        if node.attrib.get('minlon'):
            self.gpx.min_longitude = mod_utils.to_number(node.attrib.get('minlon'))
        if node.attrib.get('maxlon'):
            self.gpx.min_longitude = mod_utils.to_number(node.attrib.get('maxlon'))

    def _parse_waypoint(self, node):
        if not node.attrib.get('lat'):
            raise mod_gpx.GPXException('Waypoint without latitude')
        if not node.attrib.get('lon'):
            raise mod_gpx.GPXException('Waypoint without longitude')

        lat = mod_utils.to_number(node.attrib.get('lat'))
        lon = mod_utils.to_number(node.attrib.get('lon'))

        elevation_node = mod_utils.find_first_node(node, mod_utils.tag('ele',self.ns))
        elevation = mod_utils.to_number(self.get_node_data(elevation_node), 0)

        time_node = mod_utils.find_first_node(node, mod_utils.tag('time',self.ns))
        time_str = self.get_node_data(time_node)
        time = parse_time(time_str)

        name_node = mod_utils.find_first_node(node, mod_utils.tag('name',self.ns))
        name = self.get_node_data(name_node)

        desc_node = mod_utils.find_first_node(node, mod_utils.tag('desc',self.ns))
        desc = self.get_node_data(desc_node)

        sym_node = mod_utils.find_first_node(node, mod_utils.tag('sym',self.ns))
        sym = self.get_node_data(sym_node)

        type_node = mod_utils.find_first_node(node, mod_utils.tag('type',self.ns))
        type = self.get_node_data(type_node)

        comment_node = mod_utils.find_first_node(node, mod_utils.tag('cmt',self.ns))
        comment = self.get_node_data(comment_node)

        hdop_node = mod_utils.find_first_node(node, mod_utils.tag('hdop',self.ns))
        hdop = mod_utils.to_number(self.get_node_data(hdop_node))

        vdop_node = mod_utils.find_first_node(node, mod_utils.tag('vdop',self.ns))
        vdop = mod_utils.to_number(self.get_node_data(vdop_node))

        pdop_node = mod_utils.find_first_node(node, mod_utils.tag('pdop',self.ns))
        pdop = mod_utils.to_number(self.get_node_data(pdop_node))

        return mod_gpx.GPXWaypoint(latitude=lat, longitude=lon, elevation=elevation,
            time=time, name=name, description=desc, symbol=sym,
            type=type, comment=comment, horizontal_dilution=hdop,
            vertical_dilution=vdop, position_dilution=pdop)

    def _parse_route(self, node):
        name_node = mod_utils.find_first_node(node, mod_utils.tag('name',self.ns))
        name = self.get_node_data(name_node)

        description_node = mod_utils.find_first_node(node, mod_utils.tag('desc',self.ns))
        description = self.get_node_data(description_node)

        number_node = mod_utils.find_first_node(node, mod_utils.tag('number',self.ns))
        number = mod_utils.to_number(self.get_node_data(number_node))

        route = mod_gpx.GPXRoute(name, description, number)

        child_nodes = node.getchildren()
        for child_node in child_nodes:
            if child_node.tag == mod_utils.tag('rtept',self.ns):
                route_point = self._parse_route_point(child_node)
                route.points.append(route_point)

        return route

    def _parse_route_point(self, node):
        if not node.attrib.get('lat'):
            raise mod_gpx.GPXException('Waypoint without latitude')
        if not node.attrib.get('lon'):
            raise mod_gpx.GPXException('Waypoint without longitude')

        lat = mod_utils.to_number(node.attrib.get('lat'))
        lon = mod_utils.to_number(node.attrib.get('lon'))

        elevation_node = mod_utils.find_first_node(node, mod_utils.tag('ele',self.ns))
        elevation = mod_utils.to_number(self.get_node_data(elevation_node), 0)

        time_node = mod_utils.find_first_node(node, mod_utils.tag('time',self.ns))
        time_str = self.get_node_data(time_node)
        time = parse_time(time_str)

        name_node = mod_utils.find_first_node(node, mod_utils.tag('name',self.ns))
        name = self.get_node_data(name_node)

        desc_node = mod_utils.find_first_node(node, mod_utils.tag('desc',self.ns))
        desc = self.get_node_data(desc_node)

        sym_node = mod_utils.find_first_node(node, mod_utils.tag('sym',self.ns))
        sym = self.get_node_data(sym_node)

        type_node = mod_utils.find_first_node(node, mod_utils.tag('type',self.ns))
        type = self.get_node_data(type_node)

        comment_node = mod_utils.find_first_node(node, mod_utils.tag('cmt',self.ns))
        comment = self.get_node_data(comment_node)

        hdop_node = mod_utils.find_first_node(node, mod_utils.tag('hdop',self.ns))
        hdop = mod_utils.to_number(self.get_node_data(hdop_node))

        vdop_node = mod_utils.find_first_node(node, mod_utils.tag('vdop',self.ns))
        vdop = mod_utils.to_number(self.get_node_data(vdop_node))

        pdop_node = mod_utils.find_first_node(node, mod_utils.tag('pdop',self.ns))
        pdop = mod_utils.to_number(self.get_node_data(pdop_node))

        return mod_gpx.GPXRoutePoint(lat, lon, elevation, time, name, desc, sym, type, comment,
            horizontal_dilution = hdop, vertical_dilution = vdop, position_dilution = pdop)

    def __parse_track(self, node):
        name_node = mod_utils.find_first_node(node, mod_utils.tag('name',self.ns))
        name = self.get_node_data(name_node)

        description_node = mod_utils.find_first_node(node, mod_utils.tag('desc',self.ns))
        description = self.get_node_data(description_node)

        number_node = mod_utils.find_first_node(node, mod_utils.tag('number',self.ns))
        number = mod_utils.to_number(self.get_node_data(number_node))

        track = mod_gpx.GPXTrack(name, description, number)

        child_nodes = node.getchildren()
        for child_node in child_nodes:
            if child_node.tag == mod_utils.tag('trkseg',self.ns):
                track_segment = self.__parse_track_segment(child_node)
                track.segments.append(track_segment)

        return track

    def __parse_track_segment(self, node):
        track_segment = mod_gpx.GPXTrackSegment()
        child_nodes = node.getchildren()
        n = 0
        for child_node in child_nodes:
            if child_node.tag == mod_utils.tag('trkpt',self.ns):
                track_point = self.__parse_track_point(child_node)
                track_segment.points.append(track_point)
                n += 1

        return track_segment

    def __parse_track_point(self, node):
        latitude = None
        if node.attrib.get('lat'):
            latitude = mod_utils.to_number(node.attrib.get('lat'))

        longitude = None
        if node.attrib.get('lon'):
            longitude = mod_utils.to_number(node.attrib.get('lon'))

        time_node = mod_utils.find_first_node(node, mod_utils.tag('time',self.ns))
        time_str = self.get_node_data(time_node)
        time = parse_time(time_str)

        elevation_node = mod_utils.find_first_node(node, mod_utils.tag('ele',self.ns))
        elevation = mod_utils.to_number(self.get_node_data(elevation_node), 0)

        sym_node = mod_utils.find_first_node(node, mod_utils.tag('sym',self.ns))
        symbol = self.get_node_data(sym_node)

        comment_node = mod_utils.find_first_node(node, mod_utils.tag('cmt',self.ns))
        comment = self.get_node_data(comment_node)

        hdop_node = mod_utils.find_first_node(node, mod_utils.tag('hdop',self.ns))
        hdop = mod_utils.to_number(self.get_node_data(hdop_node))

        vdop_node = mod_utils.find_first_node(node, mod_utils.tag('vdop',self.ns))
        vdop = mod_utils.to_number(self.get_node_data(vdop_node))

        pdop_node = mod_utils.find_first_node(node, mod_utils.tag('pdop',self.ns))
        pdop = mod_utils.to_number(self.get_node_data(pdop_node))

        speed_node = mod_utils.find_first_node(node, mod_utils.tag('speed',self.ns))
        speed = mod_utils.to_number(self.get_node_data(speed_node))

        return mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation, time=time,
            symbol=symbol, comment=comment, horizontal_dilution=hdop, vertical_dilution=vdop,
            position_dilution=pdop, speed=speed)



class KMLParser(AbstractXMLParser):
    """
    Generic KML parser. Note that KML is a very generic format with much more than simple GPS tracks.

    Since this library is meant for GPS tracks, this parser will try to parse only tracks and waypoints
    from the KML file. Note, also, that KML doesn't know about routes.

    The result is a GPX object.

    NOTE THAT THIS IS AN EXPERIMENTAL FEATURE.

    See http://code.google.com/apis/kml/documentation/kmlreference.html for more details.
    """

    gpx = None

    def __init__(self, xml_or_file=None):
        self.init(xml_or_file)

    def parse(self):
        try:
            dom = mod_minidom.parseString(self.xml)
            self.__parse_dom(dom)

            return self.gpx
        except Exception, e:
            mod_logging.debug('Error in:\n%s\n-----------\n' % self.xml)
            mod_logging.exception(e)
            self.error = str(e)

            return None

    def __parse_dom(self, xml):
        # TODO
        pass


if __name__ == '__main__':

    file_name = 'test_files/aaa.gpx'
    #file_name = 'test_files/blue_hills.gpx'
    #file_name = 'test_files/test.gpx'
    file = open(file_name, 'r')
    gpx_xml = file.read()
    file.close()

    parser = mod_gpx.GPXParser(gpx_xml)
    gpx = parser.parse()

    print gpx.to_xml()

    if parser.is_valid():
        print 'TRACKS:'
        for track in gpx.tracks:
            print 'name%s, 2d:%s, 3d:%s' % (track.name, track.length_2d(), track.length_3d())
            print '\tTRACK SEGMENTS:'
            for track_segment in track.segments:
                print '\t2d:%s, 3d:%s' % (track_segment.length_2d(), track_segment.length_3d())

        print 'ROUTES:'
        for route in gpx.routes:
            print route.name
    else:
        print 'error: %s' % parser.get_error()