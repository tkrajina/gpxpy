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

import pdb

import re as mod_re
import logging as mod_logging
import datetime as mod_datetime
import xml.dom.minidom as mod_minidom

try:
    import lxml.etree as mod_etree
except:
    mod_etree = None
    pass  # LXML not available

from . import gpx as mod_gpx
from . import utils as mod_utils


class XMLParser:
    """
    Used when lxml is not available. Uses standard minidom.
    """

    def __init__(self, xml):
        self.xml = xml
        self.dom = mod_minidom.parseString(xml)

    def get_first_child(self, node=None, name=None):
        # TODO: Remove find_first_node from utils!
        if not node:
            node = self.dom

        children = node.childNodes
        if not children:
            return None

        if not name:
            return children[0]

        for tmp_node in children:
            if tmp_node.nodeName == name:
                return tmp_node

        return None

    def get_node_name(self, node):
        if not node:
            return None
        return node.nodeName

    def get_children(self, node=None):
        if not node:
            node = self.dom

        return node.childNodes

    def get_node_data(self, node):
        if node is None:
            return None

        child_nodes = self.get_children(node)
        if not child_nodes or len(child_nodes) == 0:
            return None

        return child_nodes[0].nodeValue

    def get_node_attribute(self, node, attribute):
        if attribute in node.attributes.keys():
            return node.attributes[attribute].nodeValue
        return None


class LXMLParser:
    """
    Used when lxml is available.
    """

    def __init__(self, xml):
        if not mod_etree:
            raise Exception('Cannot use LXMLParser without lxml installed')

        if mod_utils.PYTHON_VERSION[0] == '3':
            # In python 3 all strings are unicode and for some reason lxml
            # don't like unicode strings with XMLs declared as UTF-8:
            self.xml = xml.encode('utf-8')
        else:
            self.xml = xml

        self.dom = mod_etree.XML(self.xml)
        # get the namespace
        self.ns = self.dom.nsmap.get(None)

    def get_first_child(self, node=None, name=None):
        if node is None:
            if name:
                if self.get_node_name(self.dom) == name:
                    return self.dom
            return self.dom

        children = node.getchildren()

        if not children:
            return None

        if name:
            for node in children:
                if self.get_node_name(node) == name:
                    return node
            return None

        return children[0]

    def get_node_name(self, node):
        if '}' in node.tag:
            return node.tag.split('}')[1]
        return node.tag

    def get_children(self, node=None):
        if node is None:
            node = self.dom
        return node.getchildren()

    def get_node_data(self, node):
        if node is None:
            return None

        return node.text

    def get_node_attribute(self, node, attribute):
        return node.attrib.get(attribute)


def parse_time(string):
    if not string:
        return None
    if 'T' in string:
        string = string.replace('T', ' ')
    if 'Z' in string:
        string = string.replace('Z', '')
    for date_format in mod_gpx.DATE_FORMATS:
        try:
            return mod_datetime.datetime.strptime(string, date_format)
        except ValueError as e:
            pass
    return None


class GPXParser:
    def __init__(self, xml_or_file=None, parser=None):
        """
        Parser may be lxml of minidom. If you set to None then lxml will be used if installed
        otherwise minidom.
        """
        self.init(xml_or_file)
        self.gpx = mod_gpx.GPX()
        self.xml_parser_type = parser
        self.xml_parser = None

    def init(self, xml_or_file):
        text = xml_or_file.read() if hasattr(xml_or_file, 'read') else xml_or_file
        self.xml = mod_utils.make_str(text)
        self.gpx = mod_gpx.GPX()

    def get_gpx(self):
        return self.gpx

    def parse(self):
        """
        Parses the XML file and returns a GPX object.

        It will throw GPXXMLSyntaxException if the XML file is invalid or
        GPXException if the XML file is valid but something is wrong with the
        GPX data.
        """
        try:
            if self.xml_parser_type is None:
                if mod_etree:
                    self.xml_parser = LXMLParser(self.xml)
                else:
                    self.xml_parser = XMLParser(self.xml)
            elif self.xml_parser_type == 'lxml':
                self.xml_parser = LXMLParser(self.xml)
            elif self.xml_parser_type == 'minidom':
                self.xml_parser = XMLParser(self.xml)
            else:
                raise mod_gpx.GPXException('Invalid parser type: %s' % self.xml_parser_type)

            self.__parse_dom()

            return self.gpx
        except Exception as e:
            # The exception here can be a lxml or minidom exception.
            mod_logging.debug('Error in:\n%s\n-----------\n' % self.xml)
            mod_logging.exception(e)

            # The library should work in the same way regardless of the
            # underlying XML parser that's why the exception thrown
            # here is GPXXMLSyntaxException (instead of simply throwing the
            # original minidom or lxml exception e).
            #
            # But, if the user need the original exception (lxml or minidom)
            # it is available with GPXXMLSyntaxException.original_exception:
            raise mod_gpx.GPXXMLSyntaxException('Error parsing XML: %s' % str(e), e)

    def __parse_dom(self):
        node = self.xml_parser.get_first_child(name='gpx')
        if node is None:
            raise mod_gpx.GPXException('Document must have a `gpx` root node.')
        if self.xml_parser.get_node_attribute(node, "creator"):
            self.gpx.creator = self.xml_parser.get_node_attribute(node, "creator")

        for node in self.xml_parser.get_children(node):
            node_name = self.xml_parser.get_node_name(node)
            if node_name == 'time':
                time_str = self.xml_parser.get_node_data(node)
                self.gpx.time = parse_time(time_str)
            elif node_name == 'name':
                self.gpx.name = self.xml_parser.get_node_data(node)
            elif node_name == 'desc':
                self.gpx.description = self.xml_parser.get_node_data(node)
            elif node_name == 'author':
                self.gpx.author = self.xml_parser.get_node_data(node)
            elif node_name == 'email':
                self.gpx.email = self.xml_parser.get_node_data(node)
            elif node_name == 'url':
                self.gpx.url = self.xml_parser.get_node_data(node)
            elif node_name == 'urlname':
                self.gpx.urlname = self.xml_parser.get_node_data(node)
            elif node_name == 'keywords':
                self.gpx.keywords = self.xml_parser.get_node_data(node)
            elif node_name == 'bounds':
                self._parse_bounds(node)
            elif node_name == 'wpt':
                self.gpx.waypoints.append(self._parse_waypoint(node))
            elif node_name == 'rte':
                self.gpx.routes.append(self._parse_route(node))
            elif node_name == 'trk':
                self.gpx.tracks.append(self.__parse_track(node))
            else:
                #print 'unknown %s' % node
                pass

        self.valid = True

    def _parse_bounds(self, node):
        minlat = self.xml_parser.get_node_attribute(node, 'minlat')
        if minlat:
            self.gpx.min_latitude = mod_utils.to_number(minlat)

        maxlat = self.xml_parser.get_node_attribute(node, 'maxlat')
        if maxlat:
            self.gpx.min_latitude = mod_utils.to_number(maxlat)

        minlon = self.xml_parser.get_node_attribute(node, 'minlon')
        if minlon:
            self.gpx.min_longitude = mod_utils.to_number(minlon)

        maxlon = self.xml_parser.get_node_attribute(node, 'maxlon')
        if maxlon:
            self.gpx.min_longitude = mod_utils.to_number(maxlon)

    def _parse_waypoint(self, node):
        lat = self.xml_parser.get_node_attribute(node, 'lat')
        if not lat:
            raise mod_gpx.GPXException('Waypoint without latitude')

        lon = self.xml_parser.get_node_attribute(node, 'lon')
        if not lon:
            raise mod_gpx.GPXException('Waypoint without longitude')

        lat = mod_utils.to_number(lat)
        lon = mod_utils.to_number(lon)

        elevation_node = self.xml_parser.get_first_child(node, 'ele')
        elevation = mod_utils.to_number(self.xml_parser.get_node_data(elevation_node),
                                        default=None, nan_value=None)

        time_node = self.xml_parser.get_first_child(node, 'time')
        time_str = self.xml_parser.get_node_data(time_node)
        time = parse_time(time_str)

        name_node = self.xml_parser.get_first_child(node, 'name')
        name = self.xml_parser.get_node_data(name_node)

        desc_node = self.xml_parser.get_first_child(node, 'desc')
        desc = self.xml_parser.get_node_data(desc_node)

        sym_node = self.xml_parser.get_first_child(node, 'sym')
        sym = self.xml_parser.get_node_data(sym_node)

        type_node = self.xml_parser.get_first_child(node, 'type')
        type = self.xml_parser.get_node_data(type_node)

        comment_node = self.xml_parser.get_first_child(node, 'cmt')
        comment = self.xml_parser.get_node_data(comment_node)

        hdop_node = self.xml_parser.get_first_child(node, 'hdop')
        hdop = mod_utils.to_number(self.xml_parser.get_node_data(hdop_node))

        vdop_node = self.xml_parser.get_first_child(node, 'vdop')
        vdop = mod_utils.to_number(self.xml_parser.get_node_data(vdop_node))

        pdop_node = self.xml_parser.get_first_child(node, 'pdop')
        pdop = mod_utils.to_number(self.xml_parser.get_node_data(pdop_node))

        return mod_gpx.GPXWaypoint(latitude=lat, longitude=lon, elevation=elevation,
                                   time=time, name=name, description=desc, symbol=sym,
                                   type=type, comment=comment, horizontal_dilution=hdop,
                                   vertical_dilution=vdop, position_dilution=pdop)

    def _parse_route(self, node):
        name_node = self.xml_parser.get_first_child(node, 'name')
        name = self.xml_parser.get_node_data(name_node)

        description_node = self.xml_parser.get_first_child(node, 'desc')
        description = self.xml_parser.get_node_data(description_node)

        number_node = self.xml_parser.get_first_child(node, 'number')
        number = mod_utils.to_number(self.xml_parser.get_node_data(number_node))

        route = mod_gpx.GPXRoute(name, description, number)

        child_nodes = self.xml_parser.get_children(node)
        for child_node in child_nodes:
            if self.xml_parser.get_node_name(child_node) == 'rtept':
                route_point = self._parse_route_point(child_node)
                route.points.append(route_point)

        return route

    def _parse_route_point(self, node):
        lat = self.xml_parser.get_node_attribute(node, 'lat')
        if not lat:
            raise mod_gpx.GPXException('Waypoint without latitude')

        lon = self.xml_parser.get_node_attribute(node, 'lon')
        if not lon:
            raise mod_gpx.GPXException('Waypoint without longitude')

        lat = mod_utils.to_number(lat)
        lon = mod_utils.to_number(lon)

        elevation_node = self.xml_parser.get_first_child(node, 'ele')
        elevation = mod_utils.to_number(self.xml_parser.get_node_data(elevation_node),
                                        default=None, nan_value=None)

        time_node = self.xml_parser.get_first_child(node, 'time')
        time_str = self.xml_parser.get_node_data(time_node)
        time = parse_time(time_str)

        name_node = self.xml_parser.get_first_child(node, 'name')
        name = self.xml_parser.get_node_data(name_node)

        desc_node = self.xml_parser.get_first_child(node, 'desc')
        desc = self.xml_parser.get_node_data(desc_node)

        sym_node = self.xml_parser.get_first_child(node, 'sym')
        sym = self.xml_parser.get_node_data(sym_node)

        type_node = self.xml_parser.get_first_child(node, 'type')
        type = self.xml_parser.get_node_data(type_node)

        comment_node = self.xml_parser.get_first_child(node, 'cmt')
        comment = self.xml_parser.get_node_data(comment_node)

        hdop_node = self.xml_parser.get_first_child(node, 'hdop')
        hdop = mod_utils.to_number(self.xml_parser.get_node_data(hdop_node))

        vdop_node = self.xml_parser.get_first_child(node, 'vdop')
        vdop = mod_utils.to_number(self.xml_parser.get_node_data(vdop_node))

        pdop_node = self.xml_parser.get_first_child(node, 'pdop')
        pdop = mod_utils.to_number(self.xml_parser.get_node_data(pdop_node))

        return mod_gpx.GPXRoutePoint(lat, lon, elevation, time, name, desc, sym, type, comment,
                                     horizontal_dilution=hdop, vertical_dilution=vdop, position_dilution=pdop)

    def __parse_track(self, node):
        name_node = self.xml_parser.get_first_child(node, 'name')
        name = self.xml_parser.get_node_data(name_node)

        type_node = self.xml_parser.get_first_child(node, 'type')
        type = self.xml_parser.get_node_data(type_node)

        description_node = self.xml_parser.get_first_child(node, 'desc')
        description = self.xml_parser.get_node_data(description_node)

        number_node = self.xml_parser.get_first_child(node, 'number')
        number = mod_utils.to_number(self.xml_parser.get_node_data(number_node))

        track = mod_gpx.GPXTrack(name, description, number)
        track.type = type

        child_nodes = self.xml_parser.get_children(node)
        for child_node in child_nodes:
            if self.xml_parser.get_node_name(child_node) == 'trkseg':
                track_segment = self.__parse_track_segment(child_node)
                track.segments.append(track_segment)

        return track

    def __parse_track_segment(self, node):
        track_segment = mod_gpx.GPXTrackSegment()
        child_nodes = self.xml_parser.get_children(node)
        n = 0
        for child_node in child_nodes:
            if self.xml_parser.get_node_name(child_node) == 'trkpt':
                track_point = self.__parse_track_point(child_node)
                track_segment.points.append(track_point)
                n += 1

        return track_segment

    def __parse_track_point(self, node):
        latitude = self.xml_parser.get_node_attribute(node, 'lat')
        if latitude:
            latitude = mod_utils.to_number(latitude)

        longitude = self.xml_parser.get_node_attribute(node, 'lon')
        if longitude:
            longitude = mod_utils.to_number(longitude)

        time_node = self.xml_parser.get_first_child(node, 'time')
        time_str = self.xml_parser.get_node_data(time_node)
        time = parse_time(time_str)

        elevation_node = self.xml_parser.get_first_child(node, 'ele')
        elevation = mod_utils.to_number(self.xml_parser.get_node_data(elevation_node),
                                        default=None, nan_value=None)

        sym_node = self.xml_parser.get_first_child(node, 'sym')
        symbol = self.xml_parser.get_node_data(sym_node)

        comment_node = self.xml_parser.get_first_child(node, 'cmt')
        comment = self.xml_parser.get_node_data(comment_node)

        name_node = self.xml_parser.get_first_child(node, 'name')
        name = self.xml_parser.get_node_data(name_node)

        hdop_node = self.xml_parser.get_first_child(node, 'hdop')
        hdop = mod_utils.to_number(self.xml_parser.get_node_data(hdop_node))

        vdop_node = self.xml_parser.get_first_child(node, 'vdop')
        vdop = mod_utils.to_number(self.xml_parser.get_node_data(vdop_node))

        pdop_node = self.xml_parser.get_first_child(node, 'pdop')
        pdop = mod_utils.to_number(self.xml_parser.get_node_data(pdop_node))

        speed_node = self.xml_parser.get_first_child(node, 'speed')
        speed = mod_utils.to_number(self.xml_parser.get_node_data(speed_node))

        return mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation, time=time,
                                     symbol=symbol, comment=comment, horizontal_dilution=hdop, vertical_dilution=vdop,
                                     position_dilution=pdop, speed=speed, name=name)


if __name__ == '__main__':

    file_name = 'test_files/aaa.gpx'
    #file_name = 'test_files/blue_hills.gpx'
    #file_name = 'test_files/test.gpx'
    file = open(file_name, 'r')
    gpx_xml = file.read()
    file.close()

    parser = GPXParser(gpx_xml)
    gpx = parser.parse()

    print(gpx.to_xml())

    print('TRACKS:')
    for track in gpx.tracks:
        print('name%s, 2d:%s, 3d:%s' % (track.name, track.length_2d(), track.length_3d()))
        print('\tTRACK SEGMENTS:')
        for track_segment in track.segments:
            print('\t2d:%s, 3d:%s' % (track_segment.length_2d(), track_segment.length_3d()))

    print('ROUTES:')
    for route in gpx.routes:
        print(route.name)
