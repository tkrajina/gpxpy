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

import xml.dom.minidom as mod_minidom

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
        if not node:
            return None
        child_nodes = node.childNodes
        if not child_nodes or len(child_nodes) == 0:
            return None
        return child_nodes[0].data

class GPXParser(AbstractXMLParser):

    def __init__(self, xml_or_file=None):
        self.init(xml_or_file)

        self.gpx = mod_gpx.GPX()

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

    def __parse_dom(self, dom):
        root_nodes = dom.childNodes

        root_node = None

        for node in root_nodes:
            if not root_node:
                node_name = node.nodeName
                if node_name == 'gpx':
                    root_node = node

        for node in root_node.childNodes:
            node_name = node.nodeName
            if node_name == 'time':
                time_str = self.get_node_data(node)
                self.gpx.time = parse_time(time_str)
            elif node_name == 'name':
                self.gpx.name = self.get_node_data(node)
            elif node_name == 'desc':
                self.gpx.description = self.get_node_data(node)
            elif node_name == 'author':
                self.gpx.author = self.get_node_data(node)
            elif node_name == 'email':
                self.gpx.email = self.get_node_data(node)
            elif node_name == 'url':
                self.gpx.url = self.get_node_data(node)
            elif node_name == 'urlname':
                self.gpx.urlname = self.get_node_data(node)
            elif node_name == 'keywords':
                self.gpx.keywords = self.get_node_data(node)
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
        if node.attributes.has_key('minlat'):
            self.gpx.min_latitude = mod_utils.to_number(node.attributes['minlat'].nodeValue)
        if node.attributes.has_key('maxlat'):
            self.gpx.min_latitude = mod_utils.to_number(node.attributes['maxlat'].nodeValue)
        if node.attributes.has_key('minlon'):
            self.gpx.min_longitude = mod_utils.to_number(node.attributes['minlon'].nodeValue)
        if node.attributes.has_key('maxlon'):
            self.gpx.min_longitude = mod_utils.to_number(node.attributes['maxlon'].nodeValue)

    def _parse_waypoint(self, node):
        if not node.attributes.has_key('lat'):
            raise mod_gpx.GPXException('Waypoint without latitude')
        if not node.attributes.has_key('lon'):
            raise mod_gpx.GPXException('Waypoint without longitude')

        lat = mod_utils.to_number(node.attributes['lat'].nodeValue)
        lon = mod_utils.to_number(node.attributes['lon'].nodeValue)

        elevation_node = mod_utils.find_first_node(node, 'ele')
        elevation = mod_utils.to_number(self.get_node_data(elevation_node), 0)

        time_node = mod_utils.find_first_node(node, 'time')
        time_str = self.get_node_data(time_node)
        time = parse_time(time_str)

        name_node = mod_utils.find_first_node(node, 'name')
        name = self.get_node_data(name_node)

        desc_node = mod_utils.find_first_node(node, 'desc')
        desc = self.get_node_data(desc_node)

        sym_node = mod_utils.find_first_node(node, 'sym')
        sym = self.get_node_data(sym_node)

        type_node = mod_utils.find_first_node(node, 'type')
        type = self.get_node_data(type_node)

        comment_node = mod_utils.find_first_node(node, 'cmt')
        comment = self.get_node_data(comment_node)
		
        hdop_node = mod_utils.find_first_node(node, 'hdop')
        hdop = mod_utils.to_number(self.get_node_data(hdop_node))
		
        vdop_node = mod_utils.find_first_node(node, 'vdop')
        vdop = mod_utils.to_number(self.get_node_data(vdop_node))
		
        pdop_node = mod_utils.find_first_node(node, 'pdop')
        pdop = mod_utils.to_number(self.get_node_data(pdop_node))
		
        return mod_gpx.GPXWaypoint(latitude=lat, longitude=lon, elevation=elevation, 
                        time=time, name=name, description=desc, symbol=sym, 
                        type=type, comment=comment, horizontal_dilution=hdop,
                        vertical_dilution=vdop, position_dilution=pdop)

    def _parse_route(self, node):
        name_node = mod_utils.find_first_node(node, 'name')
        name = self.get_node_data(name_node)

        description_node = mod_utils.find_first_node(node, 'desc')
        description = self.get_node_data(description_node)

        number_node = mod_utils.find_first_node(node, 'number')
        number = mod_utils.to_number(self.get_node_data(number_node))

        route = mod_gpx.GPXRoute(name, description, number)

        child_nodes = node.childNodes
        for child_node in child_nodes:
            node_name = child_node.nodeName
            if node_name == 'rtept':
                route_point = self._parse_route_point(child_node)
                route.points.append(route_point)

        return route

    def _parse_route_point(self, node):
        if not node.attributes.has_key('lat'):
            raise mod_gpx.GPXException('Waypoint without latitude')
        if not node.attributes.has_key('lon'):
            raise mod_gpx.GPXException('Waypoint without longitude')

        lat = mod_utils.to_number(node.attributes['lat'].nodeValue)
        lon = mod_utils.to_number(node.attributes['lon'].nodeValue)

        elevation_node = mod_utils.find_first_node(node, 'ele')
        elevation = mod_utils.to_number(self.get_node_data(elevation_node), 0)

        time_node = mod_utils.find_first_node(node, 'time')
        time_str = self.get_node_data(time_node)
        time = parse_time(time_str)

        name_node = mod_utils.find_first_node(node, 'name')
        name = self.get_node_data(name_node)

        desc_node = mod_utils.find_first_node(node, 'desc')
        desc = self.get_node_data(desc_node)

        sym_node = mod_utils.find_first_node(node, 'sym')
        sym = self.get_node_data(sym_node)

        type_node = mod_utils.find_first_node(node, 'type')
        type = self.get_node_data(type_node)

        comment_node = mod_utils.find_first_node(node, 'cmt')
        comment = self.get_node_data(comment_node)

        hdop_node = mod_utils.find_first_node(node, 'hdop')
        hdop = mod_utils.to_number(self.get_node_data(hdop_node))
		
        vdop_node = mod_utils.find_first_node(node, 'vdop')
        vdop = mod_utils.to_number(self.get_node_data(vdop_node))
		
        pdop_node = mod_utils.find_first_node(node, 'pdop')
        pdop = mod_utils.to_number(self.get_node_data(pdop_node))

        return mod_gpx.GPXRoutePoint(lat, lon, elevation, time, name, desc, sym, type, comment,
                horizontal_dilution = hdop, vertical_dilution = vdop, position_dilution = pdop)

    def __parse_track(self, node):
        name_node = mod_utils.find_first_node(node, 'name')
        name = self.get_node_data(name_node)

        description_node = mod_utils.find_first_node(node, 'desc')
        description = self.get_node_data(description_node)

        number_node = mod_utils.find_first_node(node, 'number')
        number = mod_utils.to_number(self.get_node_data(number_node))

        track = mod_gpx.GPXTrack(name, description, number)

        child_nodes = node.childNodes
        for child_node in child_nodes:
            if child_node.nodeName == 'trkseg':
                track_segment = self.__parse_track_segment(child_node)

                track.segments.append(track_segment)

        return track

    def __parse_track_segment(self, node):
        track_segment = mod_gpx.GPXTrackSegment()
        child_nodes = node.childNodes
        n = 0
        for child_node in child_nodes:
            if child_node.nodeName == 'trkpt':
                track_point = self.__parse_track_point(child_node)
                track_segment.points.append(track_point)
                n += 1

        return track_segment

    def __parse_track_point(self, node):
        latitude = None
        if node.attributes.has_key('lat'):
            latitude = mod_utils.to_number(node.attributes['lat'].nodeValue)

        longitude = None
        if node.attributes.has_key('lon'):
            longitude = mod_utils.to_number(node.attributes['lon'].nodeValue)

        time_node = mod_utils.find_first_node(node, 'time')
        time = parse_time(self.get_node_data(time_node))

        elevation_node = mod_utils.find_first_node(node, 'ele')
        elevation = mod_utils.to_number(self.get_node_data(elevation_node))

        symbol_node = mod_utils.find_first_node(node, 'sym')
        symbol = self.get_node_data(symbol_node)

        comment_node = mod_utils.find_first_node(node, 'cmt')
        comment = self.get_node_data(comment_node)

        hdop_node = mod_utils.find_first_node(node, 'hdop')
        hdop = mod_utils.to_number(self.get_node_data(hdop_node))
		
        vdop_node = mod_utils.find_first_node(node, 'vdop')
        vdop = mod_utils.to_number(self.get_node_data(vdop_node))
		
        pdop_node = mod_utils.find_first_node(node, 'pdop')
        pdop = mod_utils.to_number(self.get_node_data(pdop_node))

        speed_node = mod_utils.find_first_node(node, 'speed')
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


