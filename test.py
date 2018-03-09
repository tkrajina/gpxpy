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

"""
Run all tests with:
    $ python -m unittest test

Run lxml parser test with:
    $ python -m unittest test.LxmlTest

Run single test with:
    $ python -m unittest test.GPXTests.test_method
"""

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
        mod_codecs.open(filename, encoding='utf-8')
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

    def test_simple_parse_function(self):
        # Must not throw any exception:
        mod_gpxpy.parse(custom_open('test_files/korita-zbevnica.gpx', encoding='utf-8'))

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
                self.assertTrue(isinstance(e.__cause__, mod_etree.XMLSyntaxError)
                                or isinstance(e.__cause__, mod_expat.ExpatError))
            except:
                pass

    def test_creator_field(self):
        gpx = self.parse('cerknicko-jezero.gpx')
        self.assertEquals(gpx.creator, "GPSBabel - http://www.gpsbabel.org")

    def test_no_creator_field(self):
        gpx = self.parse('cerknicko-jezero-no-creator.gpx')
        self.assertEquals(gpx.creator, None)

    def test_to_xml_creator(self):
        gpx = self.parse('cerknicko-jezero.gpx')
        xml = gpx.to_xml()
        self.assertTrue('creator="GPSBabel - http://www.gpsbabel.org"' in xml)

        gpx2 = self.reparse(gpx)
        self.assertEquals(gpx2.creator, "GPSBabel - http://www.gpsbabel.org")

    def test_waypoints_equality_after_reparse(self):
        gpx = self.parse('cerknicko-jezero.gpx')
        gpx2 = self.reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

    def test_waypoint_time(self):
        gpx = self.parse('cerknicko-jezero.gpx')

        self.assertTrue(gpx.waypoints[0].time)
        self.assertTrue(isinstance(gpx.waypoints[0].time, mod_datetime.datetime))

    def test_add_elevation(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13, elevation=100))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13))

        gpx.add_elevation(10)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 110)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].elevation, None)

        gpx.add_elevation(-20)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 90)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].elevation, None)

    def test_get_duration(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      time=mod_datetime.datetime(2013, 1, 1, 12, 30)))
        self.assertEqual(gpx.get_duration(), 0)

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[1].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13))
        self.assertEqual(gpx.get_duration(), 0)

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[2].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      time=mod_datetime.datetime(2013, 1, 1, 12, 30)))
        gpx.tracks[0].segments[2].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      time=mod_datetime.datetime(2013, 1, 1, 12, 31)))
        self.assertEqual(gpx.get_duration(), 60)

    def test_remove_elevation(self):
        gpx = self.parse('cerknicko-jezero.gpx')

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.elevation is not None)

        gpx.remove_elevation(tracks=True, waypoints=True, routes=True)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.elevation is None)

        xml = gpx.to_xml()

        self.assertFalse('<ele>' in xml)

    def test_remove_time(self):
        gpx = self.parse('cerknicko-jezero.gpx')

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time is not None)

        gpx.remove_time()

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time is None)

    def test_has_times_false(self):
        gpx = self.parse('cerknicko-without-times.gpx')
        self.assertFalse(gpx.has_times())

    def test_has_times(self):
        gpx = self.parse('korita-zbevnica.gpx')
        self.assertTrue(len(gpx.tracks) == 4)
        # Empty -- True
        self.assertTrue(gpx.tracks[0].has_times())
        # Not times ...
        self.assertTrue(not gpx.tracks[1].has_times())

        # Times OK
        self.assertTrue(gpx.tracks[2].has_times())
        self.assertTrue(gpx.tracks[3].has_times())

    def test_unicode_name(self):
        gpx = self.parse('unicode.gpx', encoding='utf-8')
        name = gpx.waypoints[0].name
        self.assertTrue(make_str(name) == 'šđčćž')

    def test_unicode_2(self):
        parser = mod_parser.GPXParser(custom_open('test_files/unicode2.gpx', encoding='utf-8'))
        gpx = parser.parse()
        gpx.to_xml()

    def test_unicode_bom(self):
        gpx = self.parse('unicode_with_bom.gpx', encoding='utf-8')

        name = gpx.waypoints[0].name

        self.assertTrue(make_str(name) == 'test')

    def test_unicode_bom_noencoding(self):
        gpx = self.parse('unicode_with_bom_noencoding.gpx', encoding='utf-8')

        name = gpx.waypoints[0].name

        self.assertTrue(make_str(name) == 'bom noencoding ő')

    def test_force_version(self):
        gpx = self.parse('unicode_with_bom.gpx', version = '1.1', encoding='utf-8')

        security = gpx.waypoints[0].extensions['security']

        self.assertTrue(make_str(security) == 'Open')

    def test_nearest_location_1(self):
        gpx = self.parse('korita-zbevnica.gpx')

        location = mod_geo.Location(45.451058791, 14.027903696)
        nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location(location)
        point = gpx.tracks[track_no].segments[track_segment_no].points[track_point_no]
        self.assertTrue(point.distance_2d(location) < 0.001)
        self.assertTrue(point.distance_2d(nearest_location) < 0.001)

        location = mod_geo.Location(1, 1)
        nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location(location)
        point = gpx.tracks[track_no].segments[track_segment_no].points[track_point_no]
        self.assertTrue(point.distance_2d(nearest_location) < 0.001)

        location = mod_geo.Location(50, 50)
        nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location(location)
        point = gpx.tracks[track_no].segments[track_segment_no].points[track_point_no]
        self.assertTrue(point.distance_2d(nearest_location) < 0.001)

    def test_long_timestamps(self):
        # Check if timestamps in format: 1901-12-13T20:45:52.2073437Z work
        gpx = self.parse('Mojstrovka.gpx')

        # %Y-%m-%dT%H:%M:%SZ'
        self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 1614.678000)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(1901, 12, 13, 20, 45, 52))

    def test_reduce_gpx_file(self):
        f = open('test_files/Mojstrovka.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        max_reduced_points_no = 50

        started = mod_time.time()
        points_original = gpx.get_track_points_no()
        time_original = mod_time.time() - started

        gpx.reduce_points(max_reduced_points_no)

        points_reduced = gpx.get_track_points_no()

        result = gpx.to_xml()
        if mod_sys.version_info[0] != 3:
            result = result.encode('utf-8')

        started = mod_time.time()
        parser = mod_parser.GPXParser(result)
        parser.parse()
        time_reduced = mod_time.time() - started

        print(time_original)
        print(points_original)

        print(time_reduced)
        print(points_reduced)

        self.assertTrue(points_reduced < points_original)
        self.assertTrue(points_reduced < max_reduced_points_no)

    def test_smooth_without_removing_extreemes_preserves_point_count(self):
        gpx = self.parse('first_and_last_elevation.gpx')
        l = len(list(gpx.walk()))
        gpx.smooth(vertical=True, horizontal=False)
        self.assertEquals(l, len(list(gpx.walk())))

    def test_smooth_without_removing_extreemes_preserves_point_count_2(self):
        gpx = self.parse('first_and_last_elevation.gpx')
        l = len(list(gpx.walk()))
        gpx.smooth(vertical=False, horizontal=True)
        self.assertEquals(l, len(list(gpx.walk())))

    def test_smooth_without_removing_extreemes_preserves_point_count_3(self):
        gpx = self.parse('first_and_last_elevation.gpx')
        l = len(list(gpx.walk()))
        gpx.smooth(vertical=True, horizontal=True)
        self.assertEquals(l, len(list(gpx.walk())))

    def test_clone_and_hash(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        cloned_gpx = gpx.clone()

        self.assertTrue(hash(gpx) == hash(cloned_gpx))

    def test_clone_and_smooth(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        original_2d = gpx.length_2d()
        original_3d = gpx.length_3d()

        cloned_gpx = gpx.clone()

        cloned_gpx.reduce_points(2000, min_distance=10)
        cloned_gpx.smooth(vertical=True, horizontal=True)
        cloned_gpx.smooth(vertical=True, horizontal=False)

        print('2d:', gpx.length_2d())
        print('2d cloned and smoothed:', cloned_gpx.length_2d())

        print('3d:', gpx.length_3d())
        print('3d cloned and smoothed:', cloned_gpx.length_3d())

        self.assertTrue(gpx.length_3d() == original_3d)
        self.assertTrue(gpx.length_2d() == original_2d)

        self.assertTrue(gpx.length_3d() > cloned_gpx.length_3d())
        self.assertTrue(gpx.length_2d() > cloned_gpx.length_2d())

    def test_reduce_by_min_distance(self):
        gpx = mod_gpxpy.parse(open('test_files/cerknicko-jezero.gpx'))

        min_distance_before_reduce = 1000000
        for point, track_no, segment_no, point_no in gpx.walk():
            if point_no > 0:
                previous_point = gpx.tracks[track_no].segments[segment_no].points[point_no - 1]
                print(point.distance_3d(previous_point))
                if point.distance_3d(previous_point) < min_distance_before_reduce:
                    min_distance_before_reduce = point.distance_3d(previous_point)

        gpx.reduce_points(min_distance=10)

        min_distance_after_reduce = 1000000
        for point, track_no, segment_no, point_no in gpx.walk():
            if point_no > 0:
                previous_point = gpx.tracks[track_no].segments[segment_no].points[point_no - 1]
                if point.distance_3d(previous_point) < min_distance_after_reduce:
                    min_distance_after_reduce = point.distance_3d(previous_point)

        self.assertTrue(min_distance_before_reduce < min_distance_after_reduce)
        self.assertTrue(min_distance_before_reduce < 10)
        self.assertTrue(10 < min_distance_after_reduce)

    def test_moving_stopped_times(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        print(gpx.get_track_points_no())

        #gpx.reduce_points(1000, min_distance=5)

        print(gpx.get_track_points_no())

        length = gpx.length_3d()
        print('Distance: %s' % length)

        gpx.reduce_points(2000, min_distance=10)

        gpx.smooth(vertical=True, horizontal=True)
        gpx.smooth(vertical=True, horizontal=False)

        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx.get_moving_data(stopped_speed_threshold=0.1)
        print('-----')
        print('Length: %s' % length)
        print('Moving time: %s (%smin)' % (moving_time, moving_time / 60.))
        print('Stopped time: %s (%smin)' % (stopped_time, stopped_time / 60.))
        print('Moving distance: %s' % moving_distance)
        print('Stopped distance: %s' % stopped_distance)
        print('Max speed: %sm/s' % max_speed)
        print('-----')

        # TODO: More tests and checks
        self.assertTrue(moving_distance < length)
        print('Dakle:', moving_distance, length)
        self.assertTrue(moving_distance > 0.75 * length)
        self.assertTrue(stopped_distance < 0.1 * length)

    def test_split_on_impossible_index(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        track = gpx.tracks[0]

        before = len(track.segments)
        track.split(1000, 10)
        after = len(track.segments)

        self.assertTrue(before == after)

    def test_split(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        track = gpx.tracks[1]

        track_points_no = track.get_points_no()

        before = len(track.segments)
        track.split(0, 10)
        after = len(track.segments)

        self.assertTrue(before + 1 == after)
        print('Points in first (splitted) part:', len(track.segments[0].points))

        # From 0 to 10th point == 11 points:
        self.assertTrue(len(track.segments[0].points) == 11)
        self.assertTrue(len(track.segments[0].points) + len(track.segments[1].points) == track_points_no)

        # Now split the second track
        track.split(1, 20)
        self.assertTrue(len(track.segments[1].points) == 21)
        self.assertTrue(len(track.segments[0].points) + len(track.segments[1].points) + len(track.segments[2].points) == track_points_no)

    def test_split_and_join(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        track = gpx.tracks[1]

        original_track = track.clone()

        track.split(0, 10)
        track.split(1, 20)

        self.assertTrue(len(track.segments) == 3)
        track.join(1)
        self.assertTrue(len(track.segments) == 2)
        track.join(0)
        self.assertTrue(len(track.segments) == 1)

        # Check that this split and joined track is the same as the original one:
        self.assertTrue(equals(track, original_track))

    def test_remove_point_from_segment(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        track = gpx.tracks[1]
        segment = track.segments[0]
        original_segment = segment.clone()

        segment.remove_point(3)
        print(segment.points[0])
        print(original_segment.points[0])
        self.assertTrue(equals(segment.points[0], original_segment.points[0]))
        self.assertTrue(equals(segment.points[1], original_segment.points[1]))
        self.assertTrue(equals(segment.points[2], original_segment.points[2]))
        # ...but:
        self.assertTrue(equals(segment.points[3], original_segment.points[4]))

        self.assertTrue(len(segment.points) + 1 == len(original_segment.points))

    def test_distance(self):
        distance = mod_geo.distance(48.56806, 21.43467, None, 48.599214, 21.430878, None)
        print(distance)
        self.assertTrue(distance > 3450 and distance < 3500)

    def test_haversine_distance(self):
        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(2, 3)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.distance(loc1.latitude, loc1.longitude, None, loc2.latitude, loc2.longitude, None))

        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(3, 4)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.distance(loc1.latitude, loc1.longitude, None, loc2.latitude, loc2.longitude, None))

        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(3.1, 4)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.haversine_distance(loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude))

        loc1 = mod_geo.Location(1, 2)
        loc2 = mod_geo.Location(2, 4.1)

        self.assertEqual(loc1.distance_2d(loc2),
                         mod_geo.haversine_distance(loc1.latitude, loc1.longitude, loc2.latitude, loc2.longitude))

    def test_horizontal_smooth_remove_extremes(self):
        f = open('test_files/track-with-extremes.gpx', 'r')

        parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=False, horizontal=True, remove_extremes=True)
        points_after = gpx.get_track_points_no()

        print(points_before)
        print(points_after)

        self.assertTrue(points_before - 2 == points_after)

    def test_vertical_smooth_remove_extremes(self):
        f = open('test_files/track-with-extremes.gpx', 'r')

        parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=True, horizontal=False, remove_extremes=True)
        points_after = gpx.get_track_points_no()

        print(points_before)
        print(points_after)

        self.assertTrue(points_before - 1 == points_after)

    def test_horizontal_and_vertical_smooth_remove_extremes(self):
        f = open('test_files/track-with-extremes.gpx', 'r')

        parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=True, horizontal=True, remove_extremes=True)
        points_after = gpx.get_track_points_no()

        print(points_before)
        print(points_after)

        self.assertTrue(points_before - 3 == points_after)

    def test_positions_on_track(self):
        gpx = mod_gpx.GPX()
        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)
        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)

        location_to_find_on_track = None

        for i in range(1000):
            latitude = 45 + i * 0.001
            longitude = 45 + i * 0.001
            elevation = 100 + i * 2
            point = mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation)
            segment.points.append(point)

            if i == 500:
                location_to_find_on_track = mod_gpx.GPXWaypoint(latitude=latitude, longitude=longitude)

        result = gpx.get_nearest_locations(location_to_find_on_track)

        self.assertTrue(len(result) == 1)

    def test_positions_on_track_2(self):
        gpx = mod_gpx.GPX()
        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        location_to_find_on_track = None

        # first segment:
        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)
        for i in range(1000):
            latitude = 45 + i * 0.001
            longitude = 45 + i * 0.001
            elevation = 100 + i * 2
            point = mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation)
            segment.points.append(point)

            if i == 500:
                location_to_find_on_track = mod_gpx.GPXWaypoint(latitude=latitude, longitude=longitude)

        # second segment
        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)
        for i in range(1000):
            latitude = 45.0000001 + i * 0.001
            longitude = 45.0000001 + i * 0.001
            elevation = 100 + i * 2
            point = mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation)
            segment.points.append(point)

        result = gpx.get_nearest_locations(location_to_find_on_track)

        print('Found', result)

        self.assertTrue(len(result) == 2)

    def test_hash_location(self):
        location_1 = mod_geo.Location(latitude=12, longitude=13, elevation=19)
        location_2 = mod_geo.Location(latitude=12, longitude=13, elevation=19)

        self.assertTrue(hash(location_1) == hash(location_2))

        location_2.elevation *= 2.0
        location_2.latitude *= 2.0
        location_2.longitude *= 2.0

        self.assertTrue(hash(location_1) != hash(location_2))

        location_2.elevation /= 2.0
        location_2.latitude /= 2.0
        location_2.longitude /= 2.0

        self.assertTrue(hash(location_1) == hash(location_2))

    def test_hash_gpx_track_point(self):
        point_1 = mod_gpx.GPXTrackPoint(latitude=12, longitude=13, elevation=19)
        point_2 = mod_gpx.GPXTrackPoint(latitude=12, longitude=13, elevation=19)

        self.assertTrue(hash(point_1) == hash(point_2))

        point_2.elevation *= 2.0
        point_2.latitude *= 2.0
        point_2.longitude *= 2.0

        self.assertTrue(hash(point_1) != hash(point_2))

        point_2.elevation /= 2.0
        point_2.latitude /= 2.0
        point_2.longitude /= 2.0

        self.assertTrue(hash(point_1) == hash(point_2))

    def test_hash_track(self):
        gpx = mod_gpx.GPX()
        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)
        for i in range(1000):
            latitude = 45 + i * 0.001
            longitude = 45 + i * 0.001
            elevation = 100 + i * 2.
            point = mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation)
            segment.points.append(point)

        self.assertTrue(hash(gpx))
        self.assertTrue(len(gpx.tracks) == 1)
        self.assertTrue(len(gpx.tracks[0].segments) == 1)
        self.assertTrue(len(gpx.tracks[0].segments[0].points) == 1000)

        cloned_gpx = mod_copy.deepcopy(gpx)

        self.assertTrue(hash(gpx) == hash(cloned_gpx))

        gpx.tracks[0].segments[0].points[17].elevation *= 2.
        self.assertTrue(hash(gpx) != hash(cloned_gpx))

        gpx.tracks[0].segments[0].points[17].elevation /= 2.
        self.assertTrue(hash(gpx) == hash(cloned_gpx))

        gpx.tracks[0].segments[0].points[17].latitude /= 2.
        self.assertTrue(hash(gpx) != hash(cloned_gpx))

        gpx.tracks[0].segments[0].points[17].latitude *= 2.
        self.assertTrue(hash(gpx) == hash(cloned_gpx))

        del gpx.tracks[0].segments[0].points[17]
        self.assertTrue(hash(gpx) != hash(cloned_gpx))

    def test_bounds(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()

        segment_1 = mod_gpx.GPXTrackSegment()
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=13))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-100, longitude=-5))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=100, longitude=-13))
        track.segments.append(segment_1)

        segment_2 = mod_gpx.GPXTrackSegment()
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=100))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-10, longitude=-5))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=10, longitude=-100))
        track.segments.append(segment_2)

        gpx.tracks.append(track)

        bounds = gpx.get_bounds()

        self.assertEqual(bounds.min_latitude, -100)
        self.assertEqual(bounds.max_latitude, 100)
        self.assertEqual(bounds.min_longitude, -100)
        self.assertEqual(bounds.max_longitude, 100)

        # Test refresh bounds:

        gpx.refresh_bounds()
        self.assertEqual(gpx.bounds.min_latitude, -100)
        self.assertEqual(gpx.bounds.max_latitude, 100)
        self.assertEqual(gpx.bounds.min_longitude, -100)
        self.assertEqual(gpx.bounds.max_longitude, 100)

    def test_time_bounds(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()

        segment_1 = mod_gpx.GPXTrackSegment()
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=13))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-100, longitude=-5, time=mod_datetime.datetime(2001, 1, 12)))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=100, longitude=-13, time=mod_datetime.datetime(2003, 1, 12)))
        track.segments.append(segment_1)

        segment_2 = mod_gpx.GPXTrackSegment()
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=100, time=mod_datetime.datetime(2010, 1, 12)))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-10, longitude=-5, time=mod_datetime.datetime(2011, 1, 12)))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=10, longitude=-100))
        track.segments.append(segment_2)

        gpx.tracks.append(track)

        bounds = gpx.get_time_bounds()

        self.assertEqual(bounds.start_time, mod_datetime.datetime(2001, 1, 12))
        self.assertEqual(bounds.end_time, mod_datetime.datetime(2011, 1, 12))

    def test_speed(self):
        gpx = self.parse('track_with_speed.gpx')
        gpx2 = self.reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

        self.assertEqual(gpx.tracks[0].segments[0].points[0].speed, 1.2)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].speed, 2.2)
        self.assertEqual(gpx.tracks[0].segments[0].points[2].speed, 3.2)

    def test_dilutions(self):
        gpx = self.parse('track_with_dilution_errors.gpx')
        gpx2 = self.reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

        self.assertTrue(hash(gpx) == hash(gpx2))

        for test_gpx in (gpx, gpx2):
            self.assertTrue(test_gpx.waypoints[0].horizontal_dilution == 100.1)
            self.assertTrue(test_gpx.waypoints[0].vertical_dilution == 101.1)
            self.assertTrue(test_gpx.waypoints[0].position_dilution == 102.1)

            self.assertTrue(test_gpx.routes[0].points[0].horizontal_dilution == 200.1)
            self.assertTrue(test_gpx.routes[0].points[0].vertical_dilution == 201.1)
            self.assertTrue(test_gpx.routes[0].points[0].position_dilution == 202.1)

            self.assertTrue(test_gpx.tracks[0].segments[0].points[0].horizontal_dilution == 300.1)
            self.assertTrue(test_gpx.tracks[0].segments[0].points[0].vertical_dilution == 301.1)
            self.assertTrue(test_gpx.tracks[0].segments[0].points[0].position_dilution == 302.1)

    def test_name_comment_and_symbol(self):
        gpx = mod_gpx.GPX()
        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)
        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)
        point = mod_gpx.GPXTrackPoint(12, 13, name='aaa', comment='ccc', symbol='sss')
        segment.points.append(point)

        xml = gpx.to_xml()

        self.assertTrue('<name>aaa' in xml)

        gpx2 = self.reparse(gpx)

        self.assertEquals(gpx2.tracks[0].segments[0].points[0].name, 'aaa')
        self.assertEquals(gpx2.tracks[0].segments[0].points[0].comment, 'ccc')
        self.assertEquals(gpx2.tracks[0].segments[0].points[0].symbol, 'sss')

    def test_get_bounds_and_refresh_bounds(self):
        gpx = mod_gpx.GPX()

        latitudes = []
        longitudes = []

        for i in range(2):
            track = mod_gpx.GPXTrack()
            for i in range(2):
                segment = mod_gpx.GPXTrackSegment()
                for i in range(10):
                    latitude = 50. * (mod_random.random() - 0.5)
                    longitude = 50. * (mod_random.random() - 0.5)
                    point = mod_gpx.GPXTrackPoint(latitude=latitude, longitude=longitude)
                    segment.points.append(point)
                    latitudes.append(latitude)
                    longitudes.append(longitude)
                track.segments.append(segment)
            gpx.tracks.append(track)

        bounds = gpx.get_bounds()

        print(latitudes)
        print(longitudes)

        self.assertEqual(bounds.min_latitude, min(latitudes))
        self.assertEqual(bounds.max_latitude, max(latitudes))
        self.assertEqual(bounds.min_longitude, min(longitudes))
        self.assertEqual(bounds.max_longitude, max(longitudes))

        gpx.refresh_bounds()

        self.assertEqual(gpx.bounds.min_latitude, min(latitudes))
        self.assertEqual(gpx.bounds.max_latitude, max(latitudes))
        self.assertEqual(gpx.bounds.min_longitude, min(longitudes))
        self.assertEqual(gpx.bounds.max_longitude, max(longitudes))

    def test_named_tuples_values_time_bounds(self):
        gpx = self.parse('korita-zbevnica.gpx')

        time_bounds = gpx.get_time_bounds()
        start_time, end_time = gpx.get_time_bounds()

        self.assertEqual(start_time, time_bounds.start_time)
        self.assertEqual(end_time, time_bounds.end_time)

    def test_named_tuples_values_moving_data(self):
        gpx = self.parse('korita-zbevnica.gpx')

        moving_data = gpx.get_moving_data()
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx.get_moving_data()
        self.assertEqual(moving_time, moving_data.moving_time)
        self.assertEqual(stopped_time, moving_data.stopped_time)
        self.assertEqual(moving_distance, moving_data.moving_distance)
        self.assertEqual(stopped_distance, moving_data.stopped_distance)
        self.assertEqual(max_speed, moving_data.max_speed)

    def test_named_tuples_values_uphill_downhill(self):
        gpx = self.parse('korita-zbevnica.gpx')

        uphill_downhill = gpx.get_uphill_downhill()
        uphill, downhill = gpx.get_uphill_downhill()
        self.assertEqual(uphill, uphill_downhill.uphill)
        self.assertEqual(downhill, uphill_downhill.downhill)

    def test_named_tuples_values_elevation_extremes(self):
        gpx = self.parse('korita-zbevnica.gpx')

        elevation_extremes = gpx.get_elevation_extremes()
        minimum, maximum = gpx.get_elevation_extremes()
        self.assertEqual(minimum, elevation_extremes.minimum)
        self.assertEqual(maximum, elevation_extremes.maximum)

    def test_named_tuples_values_nearest_location_data(self):
        gpx = self.parse('korita-zbevnica.gpx')

        location = gpx.tracks[1].segments[0].points[2]
        location.latitude *= 1.00001
        location.longitude *= 0.99999
        nearest_location_data = gpx.get_nearest_location(location)
        found_location, track_no, segment_no, point_no = gpx.get_nearest_location(location)
        self.assertEqual(found_location, nearest_location_data.location)
        self.assertEqual(track_no, nearest_location_data.track_no)
        self.assertEqual(segment_no, nearest_location_data.segment_no)
        self.assertEqual(point_no, nearest_location_data.point_no)

    def test_named_tuples_values_point_data(self):
        gpx = self.parse('korita-zbevnica.gpx')

        points_datas = gpx.get_points_data()

        for point_data in points_datas:
            point, distance_from_start, track_no, segment_no, point_no = point_data
            self.assertEqual(point, point_data.point)
            self.assertEqual(distance_from_start, point_data.distance_from_start)
            self.assertEqual(track_no, point_data.track_no)
            self.assertEqual(segment_no, point_data.segment_no)
            self.assertEqual(point_no, point_data.point_no)

    def test_track_points_data(self):
        gpx = self.parse('korita-zbevnica.gpx')

        points_data_2d = gpx.get_points_data(distance_2d=True)

        point, distance_from_start, track_no, segment_no, point_no = points_data_2d[-1]
        self.assertEqual(track_no, len(gpx.tracks) - 1)
        self.assertEqual(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEqual(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)
        self.assertTrue(abs(distance_from_start - gpx.length_2d()) < 0.0001)

        points_data_3d = gpx.get_points_data(distance_2d=False)
        point, distance_from_start, track_no, segment_no, point_no = points_data_3d[-1]
        self.assertEqual(track_no, len(gpx.tracks) - 1)
        self.assertEqual(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEqual(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)
        self.assertTrue(abs(distance_from_start - gpx.length_3d()) < 0.0001)

        self.assertTrue(gpx.length_2d() != gpx.length_3d())

    def test_walk_route_points(self):
        gpx = mod_gpxpy.parse(open('test_files/route.gpx'))

        for point in gpx.routes[0].walk(only_points=True):
            self.assertTrue(point)

        for point, point_no in gpx.routes[0].walk():
            self.assertTrue(point)

        self.assertEqual(point_no, len(gpx.routes[0].points) - 1)

    def test_walk_gpx_points(self):
        gpx = self.parse('korita-zbevnica.gpx')

        for point in gpx.walk():
            self.assertTrue(point)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point)

        self.assertEqual(track_no, len(gpx.tracks) - 1)
        self.assertEqual(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEqual(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)

    def test_walk_gpx_points2(self):
        gpx = self.parse('korita-zbevnica.gpx')
        track = gpx.tracks[1]

        for point in track.walk():
            self.assertTrue(point)

        for point, segment_no, point_no in track.walk():
            self.assertTrue(point)

        self.assertEqual(segment_no, len(track.segments) - 1)
        self.assertEqual(point_no, len(track.segments[-1].points) - 1)

    def test_walk_segment_points(self):
        gpx = self.parse('korita-zbevnica.gpx')
        track = gpx.tracks[1]
        segment = track.segments[0]

        assert len(segment.points) > 0

        for point in segment.walk():
            self.assertTrue(point)

        """
        for point, segment_no, point_no in track.walk():
            self.assertTrue(point)

        self.assertEqual(segment_no, len(track.segments) - 1)
        self.assertEqual(point_no, len(track.segments[-1].points) - 1)
        """

    def test_angle_0(self):
        loc1 = mod_geo.Location(0, 0)
        loc2 = mod_geo.Location(0, 1)

        loc1.elevation = 100
        loc2.elevation = 100

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEqual(angle_radians, 0)
        self.assertEqual(angle_degrees, 0)

    def test_angle(self):
        loc1 = mod_geo.Location(0, 0)
        loc2 = mod_geo.Location(0, 1)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEqual(angle_radians, mod_math.pi / 4)
        self.assertEqual(angle_degrees, 45)

    def test_angle_2(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + 0.5 * loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertTrue(angle_radians < mod_math.pi / 4)
        self.assertTrue(angle_degrees < 45)

    def test_angle_3(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + 1.5 * loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertTrue(angle_radians > mod_math.pi / 4)
        self.assertTrue(angle_degrees > 45)

    def test_angle_4(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation - loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEqual(angle_radians, - mod_math.pi / 4)
        self.assertEqual(angle_degrees, - 45)

    def test_angle_loc(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        self.assertEqual(loc1.elevation_angle(loc2), mod_geo.elevation_angle(loc1, loc2))
        self.assertEqual(loc1.elevation_angle(loc2, radians=True), mod_geo.elevation_angle(loc1, loc2, radians=True))
        self.assertEqual(loc1.elevation_angle(loc2, radians=False), mod_geo.elevation_angle(loc1, loc2, radians=False))

    def test_ignore_maximums_for_max_speed(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        tmp_time = mod_datetime.datetime.now()

        tmp_longitude = 0
        segment_1 = mod_gpx.GPXTrackSegment()
        for i in range(4):
            segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=tmp_longitude, time=tmp_time))
            tmp_longitude += 0.01
            tmp_time += mod_datetime.timedelta(hours=1)
        track.segments.append(segment_1)

        moving_time, stopped_time, moving_distance, stopped_distance, max_speed_with_too_small_segment = gpx.get_moving_data()

        # Too few points:
        mod_logging.debug('max_speed = %s', max_speed_with_too_small_segment)
        self.assertFalse(max_speed_with_too_small_segment)

        tmp_longitude = 0.
        segment_2 = mod_gpx.GPXTrackSegment()
        for i in range(55):
            segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=tmp_longitude, time=tmp_time))
            tmp_longitude += 0.01
            tmp_time += mod_datetime.timedelta(hours=1)
        track.segments.append(segment_2)

        moving_time, stopped_time, moving_distance, stopped_distance, max_speed_with_equal_speeds = gpx.get_moving_data()

        mod_logging.debug('max_speed = %s', max_speed_with_equal_speeds)
        self.assertTrue(max_speed_with_equal_speeds > 0)

        # When we add too few extremes, they should be ignored:
        for i in range(10):
            segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=tmp_longitude, time=tmp_time))
            tmp_longitude += 0.7
            tmp_time += mod_datetime.timedelta(hours=1)
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed_with_extreemes = gpx.get_moving_data()

        self.assertTrue(abs(max_speed_with_extreemes - max_speed_with_equal_speeds) < 0.001)

        # But if there are many extremes (they are no more extremes):
        for i in range(100):
            # Sometimes add on start, sometimes on end:
            if i % 2 == 0:
                segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=tmp_longitude, time=tmp_time))
            else:
                segment_2.points.insert(0, mod_gpx.GPXTrackPoint(latitude=0, longitude=tmp_longitude, time=tmp_time))
            tmp_longitude += 0.5
            tmp_time += mod_datetime.timedelta(hours=1)
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed_with_more_extreemes = gpx.get_moving_data()

        mod_logging.debug('max_speed_with_more_extreemes = %s', max_speed_with_more_extreemes)
        mod_logging.debug('max_speed_with_extreemes = %s', max_speed_with_extreemes)
        self.assertTrue(max_speed_with_more_extreemes - max_speed_with_extreemes > 10)

    def test_track_with_elevation_zero(self):
        with open('test_files/cerknicko-jezero-with-elevations-zero.gpx') as f:
            gpx = mod_gpxpy.parse(f)

            minimum, maximum = gpx.get_elevation_extremes()
            self.assertEqual(minimum, 0)
            self.assertEqual(maximum, 0)

            uphill, downhill = gpx.get_uphill_downhill()
            self.assertEqual(uphill, 0)
            self.assertEqual(downhill, 0)

    def test_track_without_elevation(self):
        with open('test_files/cerknicko-jezero-without-elevations.gpx') as f:
            gpx = mod_gpxpy.parse(f)

            minimum, maximum = gpx.get_elevation_extremes()
            self.assertEqual(minimum, None)
            self.assertEqual(maximum, None)

            uphill, downhill = gpx.get_uphill_downhill()
            self.assertEqual(uphill, 0)
            self.assertEqual(downhill, 0)

    def test_has_elevation_false(self):
        with open('test_files/cerknicko-jezero-without-elevations.gpx') as f:
            gpx = mod_gpxpy.parse(f)
            self.assertFalse(gpx.has_elevations())

    def test_has_elevation_true(self):
        with open('test_files/cerknicko-jezero.gpx') as f:
            gpx = mod_gpxpy.parse(f)
            self.assertFalse(gpx.has_elevations())

    def test_track_with_some_points_are_without_elevations(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        tmp_latlong = 0
        segment_1 = mod_gpx.GPXTrackSegment()
        for i in range(4):
            point = mod_gpx.GPXTrackPoint(latitude=tmp_latlong, longitude=tmp_latlong)
            segment_1.points.append(point)
            if i % 3 == 0:
                point.elevation = None
            else:
                point.elevation = 100 / (i + 1)

        track.segments.append(segment_1)

        minimum, maximum = gpx.get_elevation_extremes()
        self.assertTrue(minimum is not None)
        self.assertTrue(maximum is not None)

        uphill, downhill = gpx.get_uphill_downhill()
        self.assertTrue(uphill is not None)
        self.assertTrue(downhill is not None)

    def test_track_with_empty_segment(self):
        with open('test_files/track-with-empty-segment.gpx') as f:
            gpx = mod_gpxpy.parse(f)
            self.assertIsNotNone(gpx.tracks[0].get_bounds().min_latitude)
            self.assertIsNotNone(gpx.tracks[0].get_bounds().min_longitude)

    def test_add_missing_data_no_intervals(self):
        # Test only that the add_missing_function is called with the right data
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=14,
                                                                      elevation=100))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=15,
                                                                      elevation=20))

        # Shouldn't be called because all points have elevation
        def _add_missing_function(interval, start_point, end_point, ratios):
            raise Exception()

        gpx.add_missing_data(get_data_function=lambda point: point.elevation,
                             add_missing_function=_add_missing_function)

    def test_add_missing_data_one_interval(self):
        # Test only that the add_missing_function is called with the right data
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=14,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=15,
                                                                      elevation=20))

        # Shouldn't be called because all points have elevation
        def _add_missing_function(interval, start_point, end_point, ratios):
            assert start_point
            assert start_point.latitude == 12 and start_point.longitude == 13
            assert end_point
            assert end_point.latitude == 12 and end_point.longitude == 15
            assert len(interval) == 1
            assert interval[0].latitude == 12 and interval[0].longitude == 14
            assert ratios
            interval[0].elevation = 314

        gpx.add_missing_data(get_data_function=lambda point: point.elevation,
                             add_missing_function=_add_missing_function)

        self.assertEquals(314, gpx.tracks[0].segments[0].points[1].elevation)

    def test_add_missing_data_one_interval_and_empty_points_on_start_and_end(self):
        # Test only that the add_missing_function is called with the right data
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=14,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=15,
                                                                      elevation=20))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=12, longitude=13,
                                                                      elevation=None))

        # Shouldn't be called because all points have elevation
        def _add_missing_function(interval, start_point, end_point, ratios):
            assert start_point
            assert start_point.latitude == 12 and start_point.longitude == 13
            assert end_point
            assert end_point.latitude == 12 and end_point.longitude == 15
            assert len(interval) == 1
            assert interval[0].latitude == 12 and interval[0].longitude == 14
            assert ratios
            interval[0].elevation = 314

        gpx.add_missing_data(get_data_function=lambda point: point.elevation,
                             add_missing_function=_add_missing_function)

        # Points at start and end should not have elevation 314 because have
        # no two bounding points with elevations:
        self.assertEquals(None, gpx.tracks[0].segments[0].points[0].elevation)
        self.assertEquals(None, gpx.tracks[0].segments[0].points[-1].elevation)

        self.assertEquals(314, gpx.tracks[0].segments[0].points[2].elevation)

    def test_add_missing_speeds(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0,
                                                                      time=mod_datetime.datetime(2013, 1, 2, 12, 0),
                                                                      speed=0))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.00899, # 1 km/h over 1 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 13, 0)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.02697, # 2 km/h over 2 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 14, 0)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.03596, # 3 km/h over 1 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 14, 20)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=0, longitude=0.06293, # 9 km/h over 3 km
                                                                      time=mod_datetime.datetime(2013, 1, 2, 14, 40),
                                                                      speed=0))
        gpx.add_missing_speeds()

        self.assertTrue(abs(3000./(2*3600) - gpx.tracks[0].segments[0].points[1].speed) < 0.01)
        self.assertTrue(abs(3000./(80*60) - gpx.tracks[0].segments[0].points[2].speed) < 0.01)
        self.assertTrue(abs(4000./(40*60) - gpx.tracks[0].segments[0].points[3].speed) < 0.01)

    def test_add_missing_elevations(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                                                      elevation=10))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.25, longitude=12,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.5, longitude=12,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.9, longitude=12,
                                                                      elevation=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=14, longitude=12,
                                                                      elevation=20))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=15, longitude=12,
                                                                      elevation=None))

        gpx.add_missing_elevations()

        self.assertTrue(abs(12.5 - gpx.tracks[0].segments[0].points[1].elevation) < 0.01)
        self.assertTrue(abs(15 - gpx.tracks[0].segments[0].points[2].elevation) < 0.01)
        self.assertTrue(abs(19 - gpx.tracks[0].segments[0].points[3].elevation) < 0.01)

    def test_add_missing_times(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                                                      time=mod_datetime.datetime(2013, 1, 2, 12, 0)))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.25, longitude=12,
                                                                      time=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.5, longitude=12,
                                                                      time=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.75, longitude=12,
                                                                      time=None))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=14, longitude=12,
                                                                      time=mod_datetime.datetime(2013, 1, 2, 13, 0)))

        gpx.add_missing_times()

        time_1 = gpx.tracks[0].segments[0].points[1].time
        time_2 = gpx.tracks[0].segments[0].points[2].time
        time_3 = gpx.tracks[0].segments[0].points[3].time

        self.assertEqual(2013, time_1.year)
        self.assertEqual(1, time_1.month)
        self.assertEqual(2, time_1.day)
        self.assertEqual(12, time_1.hour)
        self.assertEqual(15, time_1.minute)

        self.assertEqual(2013, time_2.year)
        self.assertEqual(1, time_2.month)
        self.assertEqual(2, time_2.day)
        self.assertEqual(12, time_2.hour)
        self.assertEqual(30, time_2.minute)

        self.assertEqual(2013, time_3.year)
        self.assertEqual(1, time_3.month)
        self.assertEqual(2, time_3.day)
        self.assertEqual(12, time_3.hour)
        self.assertEqual(45, time_3.minute)

    def test_add_missing_times_2(self):
        xml = ''
        xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<gpx>\n'
        xml += '<trk>\n'
        xml += '<trkseg>\n'
        xml += '<trkpt lat="35.794159" lon="-5.832745"><time>2014-02-02T10:23:18Z</time></trkpt>\n'
        xml += '<trkpt lat="35.7941046982" lon="-5.83285637909"></trkpt>\n'
        xml += '<trkpt lat="35.7914309254" lon="-5.83378314972"></trkpt>\n'
        xml += '<trkpt lat="35.791014" lon="-5.833826"><time>2014-02-02T10:25:30Z</time><ele>18</ele></trkpt>\n'
        xml += '</trkseg></trk></gpx>\n'
        gpx = mod_gpxpy.parse(xml)

        gpx.add_missing_times()

        previous_time = None
        for point in gpx.walk(only_points=True):
            if point.time:
                if previous_time:
                    print('point.time=', point.time, 'previous_time=', previous_time)
                    self.assertTrue(point.time > previous_time)
            previous_time = point.time

    def test_distance_from_line(self):
        d = mod_geo.distance_from_line(mod_geo.Location(1, 1),
                                       mod_geo.Location(0, -1),
                                       mod_geo.Location(0, 1))
        self.assertTrue(abs(d - mod_geo.ONE_DEGREE) < 100)

    def test_simplify(self):
        for gpx_file in mod_os.listdir('test_files'):
            print('Parsing:', gpx_file)
            gpx = mod_gpxpy.parse(custom_open('test_files/%s' % gpx_file, encoding='utf-8'))

            length_2d_original = gpx.length_2d()

            gpx = mod_gpxpy.parse(custom_open('test_files/%s' % gpx_file, encoding='utf-8'))
            gpx.simplify(max_distance=50)
            length_2d_after_distance_50 = gpx.length_2d()

            gpx = mod_gpxpy.parse(custom_open('test_files/%s' % gpx_file, encoding='utf-8'))
            gpx.simplify(max_distance=10)
            length_2d_after_distance_10 = gpx.length_2d()

            print(length_2d_original, length_2d_after_distance_10, length_2d_after_distance_50)

            # When simplifying the resulting distance should alway be less than the original:
            self.assertTrue(length_2d_original >= length_2d_after_distance_10)
            self.assertTrue(length_2d_original >= length_2d_after_distance_50)

            # Simplify with bigger max_distance and => bigger error from original
            self.assertTrue(length_2d_after_distance_10 >= length_2d_after_distance_50)

            # The resulting distance usually shouldn't be too different from
            # the orignial (here check for 80% and 70%)
            self.assertTrue(length_2d_after_distance_10 >= length_2d_original * .6)
            self.assertTrue(length_2d_after_distance_50 >= length_2d_original * .5)

    def test_simplify_circular_gpx(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13, longitude=12))
        gpx.tracks[0].segments[0].points.append(mod_gpx.GPXTrackPoint(latitude=13.25, longitude=12))

        # Then the first point again:
        gpx.tracks[0].segments[0].points.append(gpx.tracks[0].segments[0].points[0])

        gpx.simplify()

    def test_nan_elevation(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?><gpx> <wpt lat="12" lon="13"> <ele>nan</ele></wpt> <rte> <rtept lat="12" lon="13"> <ele>nan</ele></rtept></rte> <trk> <name/> <desc/> <trkseg> <trkpt lat="12" lon="13"> <ele>nan</ele></trkpt></trkseg></trk></gpx>'
        gpx = mod_gpxpy.parse(xml)

        self.assertTrue(mod_math.isnan(gpx.tracks[0].segments[0].points[0].elevation))
        self.assertTrue(mod_math.isnan(gpx.routes[0].points[0].elevation))
        self.assertTrue(mod_math.isnan(gpx.waypoints[0].elevation))

    def test_time_difference(self):
        point_1 = mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                        time=mod_datetime.datetime(2013, 1, 2, 12, 31))
        point_2 = mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                        time=mod_datetime.datetime(2013, 1, 3, 12, 32))

        seconds = point_1.time_difference(point_2)
        self.assertEquals(seconds, 60 * 60 * 24 + 60)

    def test_parse_time(self):
        timestamps = [
            '2001-10-26T21:32:52',
            #'2001-10-26T21:32:52+0200',
            '2001-10-26T19:32:52Z',
            #'2001-10-26T19:32:52+00:00',
            #'-2001-10-26T21:32:52',
            '2001-10-26T21:32:52.12679',
            '2001-10-26T21:32:52',
            #'2001-10-26T21:32:52+02:00',
            '2001-10-26T19:32:52Z',
            #'2001-10-26T19:32:52+00:00',
            #'-2001-10-26T21:32:52',
            '2001-10-26T21:32:52.12679',
        ]
        timestamps_without_tz = list(map(lambda x: x.replace('T', ' ').replace('Z', ''), timestamps))
        for t in timestamps_without_tz:
            timestamps.append(t)
        for timestamp in timestamps:
            print('Parsing: %s' % timestamp)
            self.assertTrue(mod_gpxfield.parse_time(timestamp) is not None)

    def test_get_location_at(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0, time=mod_datetime.datetime(2013, 1, 2, 12, 30, 0))
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1, time=mod_datetime.datetime(2013, 1, 2, 12, 31, 0))
        gpx.tracks[0].segments[0].points.append(p0)
        gpx.tracks[0].segments[0].points.append(p1)

        self.assertEquals(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 29, 30)), [])
        self.assertEquals(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 30, 0))[0], p0)
        self.assertEquals(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 30, 30))[0], p1)
        self.assertEquals(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 31, 0))[0], p1)
        self.assertEquals(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 31, 30)), [])

    def test_adjust_time(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0)
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1)
        gpx.tracks[0].segments[0].points.append(p0)
        gpx.tracks[0].segments[0].points.append(p1)

        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0, time=mod_datetime.datetime(2013, 1, 2, 12, 30, 0))
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1, time=mod_datetime.datetime(2013, 1, 2, 12, 31, 0))
        gpx.tracks[0].segments[1].points.append(p0)
        gpx.tracks[0].segments[1].points.append(p1)

        d1 = mod_datetime.timedelta(-1, -1)
        d2 = mod_datetime.timedelta(1, 2)
        # move back and forward to add a total of 1 second
        gpx.adjust_time(d1)
        gpx.adjust_time(d2)

        self.assertEquals(gpx.tracks[0].segments[0].points[0].time, None)
        self.assertEquals(gpx.tracks[0].segments[0].points[1].time, None)
        self.assertEquals(gpx.tracks[0].segments[1].points[0].time, mod_datetime.datetime(2013, 1, 2, 12, 30, 1))
        self.assertEquals(gpx.tracks[0].segments[1].points[1].time, mod_datetime.datetime(2013, 1, 2, 12, 31, 1))

    def test_unicode(self):
        parser = mod_parser.GPXParser(custom_open('test_files/unicode2.gpx', encoding='utf-8'))
        gpx = parser.parse()
        gpx.to_xml()

    def test_location_delta(self):
        location = mod_geo.Location(-20, -50)

        location_2 = location + mod_geo.LocationDelta(angle=45, distance=100)
        self.assertTrue(cca(location_2.latitude - location.latitude, location_2.longitude - location.longitude))

    def test_location_equator_delta_distance_111120(self):
        self.__test_location_delta(mod_geo.Location(0, 13), 111120)

    def test_location_equator_delta_distance_50(self):
        self.__test_location_delta(mod_geo.Location(0, -50), 50)

    def test_location_nonequator_delta_distance_111120(self):
        self.__test_location_delta(mod_geo.Location(45, 13), 111120)

    def test_location_nonequator_delta_distance_50(self):
        self.__test_location_delta(mod_geo.Location(-20, -50), 50)

    def test_delta_add_and_move(self):
        location = mod_geo.Location(45.1, 13.2)
        delta = mod_geo.LocationDelta(angle=20, distance=1000)
        location_2 = location + delta
        location.move(delta)

        self.assertTrue(cca(location.latitude, location_2.latitude))
        self.assertTrue(cca(location.longitude, location_2.longitude))

    def test_parse_gpx_with_node_with_comments(self):
        self.assertTrue(mod_gpxpy.parse(open('test_files/gpx-with-node-with-comments.gpx')))

    def __test_location_delta(self, location, distance):
        angles = [ x * 15 for x in range(int(360 / 15)) ]
        print(angles)

        previous_location = None

        distances_between_points = []

        for angle in angles:
            new_location = location + mod_geo.LocationDelta(angle=angle, distance=distance)
            # All locations same distance from center
            self.assertTrue(cca(location.distance_2d(new_location), distance))
            if previous_location:
                distances_between_points.append(new_location.distance_2d(previous_location))
            previous_location = new_location

        print(distances_between_points)
        # All points should be equidistant on a circle:
        for i in range(1, len(distances_between_points)):
            self.assertTrue(cca(distances_between_points[0], distances_between_points[i]))

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
                self.assertEquals(gpx.version, '1.0')
                self.assertEquals(get_dom_node(dom, 'gpx').attributes['version'].nodeValue, '1.0')

                self.assertEquals(gpx.creator, '...')
                self.assertEquals(get_dom_node(dom, 'gpx').attributes['creator'].nodeValue, '...')

                self.assertEquals(gpx.name, 'example name')
                self.assertEquals(get_dom_node(dom, 'gpx/name').firstChild.nodeValue, 'example name')

                self.assertEquals(gpx.description, 'example description')
                self.assertEquals(get_dom_node(dom, 'gpx/desc').firstChild.nodeValue, 'example description')

                self.assertEquals(gpx.author_name, 'example author')
                self.assertEquals(get_dom_node(dom, 'gpx/author').firstChild.nodeValue, 'example author')

                self.assertEquals(gpx.author_email, 'example@email.com')
                self.assertEquals(get_dom_node(dom, 'gpx/email').firstChild.nodeValue, 'example@email.com')

                self.assertEquals(gpx.link, 'http://example.url')
                self.assertEquals(get_dom_node(dom, 'gpx/url').firstChild.nodeValue, 'http://example.url')

                self.assertEquals(gpx.link_text, 'example urlname')
                self.assertEquals(get_dom_node(dom, 'gpx/urlname').firstChild.nodeValue, 'example urlname')

                self.assertEquals(gpx.time, mod_datetime.datetime(2013, 1, 1, 12, 0))
                self.assertTrue(get_dom_node(dom, 'gpx/time').firstChild.nodeValue in ('2013-01-01T12:00:00Z', '2013-01-01T12:00:00'))

                self.assertEquals(gpx.keywords, 'example keywords')
                self.assertEquals(get_dom_node(dom, 'gpx/keywords').firstChild.nodeValue, 'example keywords')

                self.assertEquals(gpx.bounds.min_latitude, 1.2)
                self.assertEquals(get_dom_node(dom, 'gpx/bounds').attributes['minlat'].value, '1.2')

                # Waypoints:

                self.assertEquals(len(gpx.waypoints), 2)

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

                self.assertEquals(gpx.waypoints[0].link, 'example url')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/url').firstChild.nodeValue, 'example url')

                self.assertEquals(gpx.waypoints[0].link_text, 'example urlname')
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[0]/urlname').firstChild.nodeValue, 'example urlname')

                self.assertEquals(gpx.waypoints[1].latitude, 13.4)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[1]').attributes['lat'].value, '13.4')

                self.assertEquals(gpx.waypoints[1].longitude, 46.7)
                self.assertEquals(get_dom_node(dom, 'gpx/wpt[1]').attributes['lon'].value, '46.7')

                self.assertEquals(len(gpx.routes), 2)

                self.assertEquals(gpx.routes[0].name, 'example name')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/name').firstChild.nodeValue, 'example name')

                self.assertEquals(gpx.routes[0].comment, 'example cmt')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/cmt').firstChild.nodeValue, 'example cmt')

                self.assertEquals(gpx.routes[0].description, 'example desc')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/desc').firstChild.nodeValue, 'example desc')

                self.assertEquals(gpx.routes[0].source, 'example src')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/src').firstChild.nodeValue, 'example src')

                self.assertEquals(gpx.routes[0].link, 'example url')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/url').firstChild.nodeValue, 'example url')

                # Rte pt:

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

                self.assertEquals(gpx.routes[0].points[0].link, 'example url r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/url').firstChild.nodeValue, 'example url r')

                self.assertEquals(gpx.routes[0].points[0].link_text, 'example urlname r')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/rtept[0]/urlname').firstChild.nodeValue, 'example urlname r')

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

                # Rte

                self.assertEquals(gpx.routes[1].name, 'second route')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[1]/name').firstChild.nodeValue, 'second route')

                self.assertEquals(gpx.routes[1].description, 'example desc 2')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[1]/desc').firstChild.nodeValue, 'example desc 2')

                self.assertEquals(gpx.routes[0].link_text, 'example urlname')
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/urlname').firstChild.nodeValue, 'example urlname')

                self.assertEquals(gpx.routes[0].number, 7)
                self.assertEquals(get_dom_node(dom, 'gpx/rte[0]/number').firstChild.nodeValue, '7')

                self.assertEquals(len(gpx.routes[0].points), 3)
                self.assertEquals(len(gpx.routes[1].points), 2)

                # trk:

                self.assertEquals(len(gpx.tracks), 2)

                self.assertEquals(gpx.tracks[0].name, 'example name t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/name').firstChild.nodeValue, 'example name t')

                self.assertEquals(gpx.tracks[0].comment, 'example cmt t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/cmt').firstChild.nodeValue, 'example cmt t')

                self.assertEquals(gpx.tracks[0].description, 'example desc t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/desc').firstChild.nodeValue, 'example desc t')

                self.assertEquals(gpx.tracks[0].source, 'example src t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/src').firstChild.nodeValue, 'example src t')

                self.assertEquals(gpx.tracks[0].link, 'example url t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/url').firstChild.nodeValue, 'example url t')

                self.assertEquals(gpx.tracks[0].link_text, 'example urlname t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/urlname').firstChild.nodeValue, 'example urlname t')

                self.assertEquals(gpx.tracks[0].number, 1)
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/number').firstChild.nodeValue, '1')

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

                self.assertEquals(gpx.tracks[0].segments[0].points[0].link, 'example url t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/url').firstChild.nodeValue, 'example url t')

                self.assertEquals(gpx.tracks[0].segments[0].points[0].link_text, 'example urlname t')
                self.assertEquals(get_dom_node(dom, 'gpx/trk[0]/trkseg[0]/trkpt[0]/urlname').firstChild.nodeValue, 'example urlname t')

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

        with open('test_files/validation_gpx11.gpx', 'w') as f:
            f.write(reparsed_gpx.to_xml())

    def test_xml_chars_encode_decode(self):
        gpx = mod_gpxpy.gpx.GPX()
        gpx.name = "Test<a>jkljkl</gpx>"

        print(gpx.to_xml())

        gpx_2 = mod_gpxpy.parse(gpx.to_xml())

        self.assertTrue('<name>Test&lt;a&gt;jkljkl&lt;/gpx&gt;</name>' in gpx_2.to_xml())

    def test_10_to_11_conversion(self):
        """
        This tests checks that reparsing from 1.0 to 1.1 and from 1.1 to 1.0
        will preserver all fields common for both versions.
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
        self.assertTrue('http://www.topografix.com/GPX/1/0' in xml_10)
        #pretty_print_xml(xml_10)
        gpx_1 = mod_gpxpy.parse(xml_10)

        # Convert do GPX1.1:
        xml_11 = gpx_1.to_xml('1.1')
        self.assertTrue('http://www.topografix.com/GPX/1/1' in xml_11 and 'metadata' in xml_11)
        pretty_print_xml(xml_11)
        gpx_2 = mod_gpxpy.parse(xml_11)

        # Convert do GPX1.0 again:
        xml_10 = gpx_2.to_xml('1.0')
        self.assertTrue('http://www.topografix.com/GPX/1/0' in xml_10)
        #pretty_print_xml(xml_10)
        gpx_3 = mod_gpxpy.parse(xml_10)

        for gpx in (gpx_1, gpx_2, gpx_3, ):
            self.assertTrue(gpx.creator is not None)
            self.assertEquals(original_gpx.creator, gpx.creator)

            self.assertTrue(gpx.name is not None)
            self.assertEquals(original_gpx.name, gpx.name)

            self.assertTrue(gpx.description is not None)
            self.assertEquals(original_gpx.description, gpx.description)

            self.assertTrue(gpx.keywords is not None)
            self.assertEquals(original_gpx.keywords, gpx.keywords)

            self.assertTrue(gpx.time is not None)
            self.assertEquals(original_gpx.time, gpx.time)

            self.assertTrue(gpx.author_name is not None)
            self.assertEquals(original_gpx.author_name, gpx.author_name)

            self.assertTrue(gpx.author_email is not None)
            self.assertEquals(original_gpx.author_email, gpx.author_email)

            self.assertTrue(gpx.link is not None)
            self.assertEquals(original_gpx.link, gpx.link)

            self.assertTrue(gpx.link_text is not None)
            self.assertEquals(original_gpx.link_text, gpx.link_text)

            self.assertTrue(gpx.bounds is not None)
            self.assertEquals(hash(original_gpx.bounds), hash(gpx.bounds))

            self.assertEquals(1, len(gpx.waypoints))

            self.assertTrue(gpx.waypoints[0].latitude is not None)
            self.assertEquals(original_gpx.waypoints[0].latitude, gpx.waypoints[0].latitude)

            self.assertTrue(gpx.waypoints[0].longitude is not None)
            self.assertEquals(original_gpx.waypoints[0].longitude, gpx.waypoints[0].longitude)

            self.assertTrue(gpx.waypoints[0].elevation is not None)
            self.assertEquals(original_gpx.waypoints[0].elevation, gpx.waypoints[0].elevation)

            self.assertTrue(gpx.waypoints[0].time is not None)
            self.assertEquals(original_gpx.waypoints[0].time, gpx.waypoints[0].time)

            self.assertTrue(gpx.waypoints[0].magnetic_variation is not None)
            self.assertEquals(original_gpx.waypoints[0].magnetic_variation, gpx.waypoints[0].magnetic_variation)

            self.assertTrue(gpx.waypoints[0].geoid_height is not None)
            self.assertEquals(original_gpx.waypoints[0].geoid_height, gpx.waypoints[0].geoid_height)

            self.assertTrue(gpx.waypoints[0].name is not None)
            self.assertEquals(original_gpx.waypoints[0].name, gpx.waypoints[0].name)

            self.assertTrue(gpx.waypoints[0].comment is not None)
            self.assertEquals(original_gpx.waypoints[0].comment, gpx.waypoints[0].comment)

            self.assertTrue(gpx.waypoints[0].description is not None)
            self.assertEquals(original_gpx.waypoints[0].description, gpx.waypoints[0].description)

            self.assertTrue(gpx.waypoints[0].source is not None)
            self.assertEquals(original_gpx.waypoints[0].source, gpx.waypoints[0].source)

            # TODO: Link/url

            self.assertTrue(gpx.waypoints[0].symbol is not None)
            self.assertEquals(original_gpx.waypoints[0].symbol, gpx.waypoints[0].symbol)

            self.assertTrue(gpx.waypoints[0].type is not None)
            self.assertEquals(original_gpx.waypoints[0].type, gpx.waypoints[0].type)

            self.assertTrue(gpx.waypoints[0].type_of_gpx_fix is not None)
            self.assertEquals(original_gpx.waypoints[0].type_of_gpx_fix, gpx.waypoints[0].type_of_gpx_fix)

            self.assertTrue(gpx.waypoints[0].satellites is not None)
            self.assertEquals(original_gpx.waypoints[0].satellites, gpx.waypoints[0].satellites)

            self.assertTrue(gpx.waypoints[0].horizontal_dilution is not None)
            self.assertEquals(original_gpx.waypoints[0].horizontal_dilution, gpx.waypoints[0].horizontal_dilution)

            self.assertTrue(gpx.waypoints[0].vertical_dilution is not None)
            self.assertEquals(original_gpx.waypoints[0].vertical_dilution, gpx.waypoints[0].vertical_dilution)

            self.assertTrue(gpx.waypoints[0].position_dilution is not None)
            self.assertEquals(original_gpx.waypoints[0].position_dilution, gpx.waypoints[0].position_dilution)

            self.assertTrue(gpx.waypoints[0].age_of_dgps_data is not None)
            self.assertEquals(original_gpx.waypoints[0].age_of_dgps_data, gpx.waypoints[0].age_of_dgps_data)

            self.assertTrue(gpx.waypoints[0].dgps_id is not None)
            self.assertEquals(original_gpx.waypoints[0].dgps_id, gpx.waypoints[0].dgps_id)

            # route(s):

            self.assertTrue(gpx.routes[0].name is not None)
            self.assertEquals(original_gpx.routes[0].name, gpx.routes[0].name)

            self.assertTrue(gpx.routes[0].comment is not None)
            self.assertEquals(original_gpx.routes[0].comment, gpx.routes[0].comment)

            self.assertTrue(gpx.routes[0].description is not None)
            self.assertEquals(original_gpx.routes[0].description, gpx.routes[0].description)

            self.assertTrue(gpx.routes[0].source is not None)
            self.assertEquals(original_gpx.routes[0].source, gpx.routes[0].source)

            self.assertTrue(gpx.routes[0].number is not None)
            self.assertEquals(original_gpx.routes[0].number, gpx.routes[0].number)

            self.assertTrue(gpx.routes[0].points[0].latitude is not None)
            self.assertEquals(original_gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].latitude)

            self.assertTrue(gpx.routes[0].points[0].longitude is not None)
            self.assertEquals(original_gpx.routes[0].points[0].longitude, gpx.routes[0].points[0].longitude)

            self.assertTrue(gpx.routes[0].points[0].elevation is not None)
            self.assertEquals(original_gpx.routes[0].points[0].elevation, gpx.routes[0].points[0].elevation)

            self.assertTrue(gpx.routes[0].points[0].time is not None)
            self.assertEquals(original_gpx.routes[0].points[0].time, gpx.routes[0].points[0].time)

            self.assertTrue(gpx.routes[0].points[0].magnetic_variation is not None)
            self.assertEquals(original_gpx.routes[0].points[0].magnetic_variation, gpx.routes[0].points[0].magnetic_variation)

            self.assertTrue(gpx.routes[0].points[0].geoid_height is not None)
            self.assertEquals(original_gpx.routes[0].points[0].geoid_height, gpx.routes[0].points[0].geoid_height)

            self.assertTrue(gpx.routes[0].points[0].name is not None)
            self.assertEquals(original_gpx.routes[0].points[0].name, gpx.routes[0].points[0].name)

            self.assertTrue(gpx.routes[0].points[0].comment is not None)
            self.assertEquals(original_gpx.routes[0].points[0].comment, gpx.routes[0].points[0].comment)

            self.assertTrue(gpx.routes[0].points[0].description is not None)
            self.assertEquals(original_gpx.routes[0].points[0].description, gpx.routes[0].points[0].description)

            self.assertTrue(gpx.routes[0].points[0].source is not None)
            self.assertEquals(original_gpx.routes[0].points[0].source, gpx.routes[0].points[0].source)

            self.assertTrue(gpx.routes[0].points[0].symbol is not None)
            self.assertEquals(original_gpx.routes[0].points[0].symbol, gpx.routes[0].points[0].symbol)

            self.assertTrue(gpx.routes[0].points[0].type is not None)
            self.assertEquals(original_gpx.routes[0].points[0].type, gpx.routes[0].points[0].type)

            self.assertTrue(gpx.routes[0].points[0].type_of_gpx_fix is not None)
            self.assertEquals(original_gpx.routes[0].points[0].type_of_gpx_fix, gpx.routes[0].points[0].type_of_gpx_fix)

            self.assertTrue(gpx.routes[0].points[0].satellites is not None)
            self.assertEquals(original_gpx.routes[0].points[0].satellites, gpx.routes[0].points[0].satellites)

            self.assertTrue(gpx.routes[0].points[0].horizontal_dilution is not None)
            self.assertEquals(original_gpx.routes[0].points[0].horizontal_dilution, gpx.routes[0].points[0].horizontal_dilution)

            self.assertTrue(gpx.routes[0].points[0].vertical_dilution is not None)
            self.assertEquals(original_gpx.routes[0].points[0].vertical_dilution, gpx.routes[0].points[0].vertical_dilution)

            self.assertTrue(gpx.routes[0].points[0].position_dilution is not None)
            self.assertEquals(original_gpx.routes[0].points[0].position_dilution, gpx.routes[0].points[0].position_dilution)

            self.assertTrue(gpx.routes[0].points[0].age_of_dgps_data is not None)
            self.assertEquals(original_gpx.routes[0].points[0].age_of_dgps_data, gpx.routes[0].points[0].age_of_dgps_data)

            self.assertTrue(gpx.routes[0].points[0].dgps_id is not None)
            self.assertEquals(original_gpx.routes[0].points[0].dgps_id, gpx.routes[0].points[0].dgps_id)

            # track(s):

            self.assertTrue(gpx.tracks[0].name is not None)
            self.assertEquals(original_gpx.tracks[0].name, gpx.tracks[0].name)

            self.assertTrue(gpx.tracks[0].comment is not None)
            self.assertEquals(original_gpx.tracks[0].comment, gpx.tracks[0].comment)

            self.assertTrue(gpx.tracks[0].description is not None)
            self.assertEquals(original_gpx.tracks[0].description, gpx.tracks[0].description)

            self.assertTrue(gpx.tracks[0].source is not None)
            self.assertEquals(original_gpx.tracks[0].source, gpx.tracks[0].source)

            self.assertTrue(gpx.tracks[0].number is not None)
            self.assertEquals(original_gpx.tracks[0].number, gpx.tracks[0].number)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].latitude is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].latitude)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].longitude is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].longitude, gpx.tracks[0].segments[0].points[0].longitude)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].elevation is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].elevation, gpx.tracks[0].segments[0].points[0].elevation)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].time is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].time, gpx.tracks[0].segments[0].points[0].time)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].magnetic_variation is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].magnetic_variation, gpx.tracks[0].segments[0].points[0].magnetic_variation)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].geoid_height is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].geoid_height, gpx.tracks[0].segments[0].points[0].geoid_height)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].name is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].name, gpx.tracks[0].segments[0].points[0].name)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].comment is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].comment, gpx.tracks[0].segments[0].points[0].comment)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].description is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].description, gpx.tracks[0].segments[0].points[0].description)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].source is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].source, gpx.tracks[0].segments[0].points[0].source)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].symbol is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].symbol, gpx.tracks[0].segments[0].points[0].symbol)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].type is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].type, gpx.tracks[0].segments[0].points[0].type)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].type_of_gpx_fix is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].type_of_gpx_fix, gpx.tracks[0].segments[0].points[0].type_of_gpx_fix)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].satellites is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].satellites, gpx.tracks[0].segments[0].points[0].satellites)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].horizontal_dilution is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].horizontal_dilution, gpx.tracks[0].segments[0].points[0].horizontal_dilution)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].vertical_dilution is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].vertical_dilution, gpx.tracks[0].segments[0].points[0].vertical_dilution)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].position_dilution is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].position_dilution, gpx.tracks[0].segments[0].points[0].position_dilution)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].age_of_dgps_data is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].age_of_dgps_data, gpx.tracks[0].segments[0].points[0].age_of_dgps_data)

            self.assertTrue(gpx.tracks[0].segments[0].points[0].dgps_id is not None)
            self.assertEquals(original_gpx.tracks[0].segments[0].points[0].dgps_id, gpx.tracks[0].segments[0].points[0].dgps_id)

    def test_min_max(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)

        segment.points.append(mod_gpx.GPXTrackPoint(12, 13, elevation=100))
        segment.points.append(mod_gpx.GPXTrackPoint(12, 13, elevation=200))

        # Check for segment:
        elevation_min, elevation_max = segment.get_elevation_extremes()
        self.assertEquals(100, elevation_min)
        self.assertEquals(200, elevation_max)

        # Check for track:
        elevation_min, elevation_max = track.get_elevation_extremes()
        self.assertEquals(100, elevation_min)
        self.assertEquals(200, elevation_max)

        # Check for gpx:
        elevation_min, elevation_max = gpx.get_elevation_extremes()
        self.assertEquals(100, elevation_min)
        self.assertEquals(200, elevation_max)

    def test_distance_between_points_near_0_longitude(self):
        """ Make sure that the distance function works properly when points have longitudes on opposite sides of the 0-longitude meridian """
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=-0.1, elevation_2=0, haversine=True)
        print(distance)
        self.assertTrue(distance < 230000)
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=-0.1, elevation_2=0, haversine=False)
        print(distance)
        self.assertTrue(distance < 230000)
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=360-0.1, elevation_2=0, haversine=True)
        print(distance)
        self.assertTrue(distance < 230000)
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=360-0.1, elevation_2=0, haversine=False)
        print(distance)
        self.assertTrue(distance < 230000)

    def test_zero_latlng(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()
        gpx.tracks.append(track)

        segment = mod_gpx.GPXTrackSegment()
        track.segments.append(segment)

        segment.points.append(mod_gpx.GPXTrackPoint(0, 0, elevation=0))
        xml = gpx.to_xml()
        print(xml)

        self.assertEquals(1, len(gpx.tracks))
        self.assertEquals(1, len(gpx.tracks[0].segments))
        self.assertEquals(1, len(gpx.tracks[0].segments[0].points))
        self.assertEquals(0, gpx.tracks[0].segments[0].points[0].latitude)
        self.assertEquals(0, gpx.tracks[0].segments[0].points[0].longitude)
        self.assertEquals(0, gpx.tracks[0].segments[0].points[0].elevation)

        gpx2 = mod_gpxpy.parse(xml)

        self.assertEquals(1, len(gpx2.tracks))
        self.assertEquals(1, len(gpx2.tracks[0].segments))
        self.assertEquals(1, len(gpx2.tracks[0].segments[0].points))
        self.assertEquals(0, gpx2.tracks[0].segments[0].points[0].latitude)
        self.assertEquals(0, gpx2.tracks[0].segments[0].points[0].longitude)
        self.assertEquals(0, gpx2.tracks[0].segments[0].points[0].elevation)

    def test_remove_timezone_from_timestamp(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<gpx>\n'
        xml += '<trk>\n'
        xml += '<trkseg>\n'
        xml += '<trkpt lat="35.794159" lon="-5.832745"><time>2014-02-02T10:23:18Z+01:00</time></trkpt>\n'
        xml += '</trkseg></trk></gpx>\n'
        gpx = mod_gpxpy.parse(xml)
        self.assertEquals(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2014, 2, 2, 10, 23, 18))

    def test_timestamp_with_single_digits(self):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<gpx>\n'
        xml += '<trk>\n'
        xml += '<trkseg>\n'
        xml += '<trkpt lat="35.794159" lon="-5.832745"><time>2014-2-2T2:23:18Z-02:00</time></trkpt>\n'
        xml += '</trkseg></trk></gpx>\n'
        gpx = mod_gpxpy.parse(xml)
        self.assertEquals(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(2014, 2, 2, 2, 23, 18))

    def test_join_gpx_xml_files(self):
        import gpxpy.gpxxml

        files = [
                'test_files/cerknicko-jezero.gpx',
                'test_files/first_and_last_elevation.gpx',
                'test_files/korita-zbevnica.gpx',
                'test_files/Mojstrovka.gpx',
        ]

        rtes = 0
        wpts = 0
        trcks = 0
        points = 0

        xmls = []
        for file_name in files:
            with open(file_name) as f:
                contents = f.read()
                gpx = mod_gpxpy.parse(contents)
                wpts += len(gpx.waypoints)
                rtes += len(gpx.routes)
                trcks += len(gpx.tracks)
                points += gpx.get_points_no()
                xmls.append(contents)

        result_xml = gpxpy.gpxxml.join_gpxs(xmls)
        result_gpx = mod_gpxpy.parse(result_xml)

        self.assertEquals(rtes, len(result_gpx.routes))
        self.assertEquals(wpts, len(result_gpx.waypoints))
        self.assertEquals(trcks, len(result_gpx.tracks))
        self.assertEquals(points, result_gpx.get_points_no())

    def test_small_floats(self):
        """GPX 1/1 does not allow scientific notation but that is what gpxpy writes right now."""
        f = open('test_files/track-with-small-floats.gpx', 'r')

        gpx = mod_gpxpy.parse(f)

        xml = gpx.to_xml()
        self.assertNotIn('e-', xml)

class LxmlTest(mod_unittest.TestCase):
    @mod_unittest.skipIf(mod_os.environ.get('XMLPARSER')!="LXML", "LXML not installed")
    def test_checklxml(self):
        self.assertIn('lxml.etree._Element', str(mod_parser.XMLParser('<_/>').dom.__class__))

if __name__ == '__main__':
    mod_unittest.main()
