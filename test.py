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

import unittest as mod_unittest
import time as mod_time
import copy as mod_copy
import datetime as mod_datetime
import random as mod_random
import math as mod_math

import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx
import gpxpy.parser as mod_parser
import gpxpy.geo as mod_geo

def equals(object1, object2, ignore=None):
    """ Testing purposes only """

    if not object1 and not object2:
        return True

    if not object1 or not object2:
        print 'Not obj2'
        return False

    if not object1.__class__ == object2.__class__:
        print 'Not obj1'
        return False

    attributes = []
    for attr in dir(object1):
        if not ignore or not attr in ignore:
            if not callable(getattr(object1, attr)) and not attr.startswith('_'):
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
            print 'Object differs in attribute %s (%s - %s)' % (attr, attr1, attr2)
            return False

        if not equals(attr1, attr2):
            print 'Object differs in attribute %s (%s - %s)' % (attr, attr1, attr2)
            return None

    return True

# TODO: Track segment speed in point test

class Tests(mod_unittest.TestCase):

    def __parse(self, file):
        f = open('test_files/%s' % file)
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        if not gpx:
            print 'Parser error: %s' % parser.get_error()

        return gpx
		
    def __reparse(self, gpx):
        xml = gpx.to_xml()

        parser = mod_parser.GPXParser(xml)
        gpx = parser.parse()

        if not gpx:
            print 'Parser error while reparsing: %s' % parser.get_error()

        return gpx

    def test_simple_parse_function(self):
        # Must not throw any exception:
        mod_gpxpy.parse(open('test_files/korita-zbevnica.gpx'))

    def test_simple_parse_function_invalid_xml(self):
        try:
            mod_gpxpy.parse('<gpx></gpx')
            self.fail()
        except mod_gpx.GPXException, e:
            self.assertTrue('unclosed token: line 1, column 5' in e.message)

    def test_waypoints_equality_after_reparse(self):
        gpx = self.__parse('cerknicko-jezero.gpx')
        gpx2 = self.__reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

    def test_remove_elevation(self):
        gpx = self.__parse('cerknicko-jezero.gpx')

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.elevation != None)

        gpx.remove_elevation(tracks=True, waypoints=True, routes=True)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.elevation == None)

        xml = gpx.to_xml()

        self.assertFalse('<ele>' in xml)

    def test_remove_time(self):
        gpx = self.__parse('cerknicko-jezero.gpx')

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time != None)

        gpx.remove_time()

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point.time == None)

    def test_has_times_false(self):
        gpx = self.__parse('cerknicko-without-times.gpx')
        self.assertFalse(gpx.has_times())

    def test_has_times(self):
        gpx = self.__parse('korita-zbevnica.gpx')
        self.assertTrue(len(gpx.tracks) == 4)
        # Empty -- True
        self.assertTrue(gpx.tracks[0].has_times())
        # Not times ...
        self.assertTrue(not gpx.tracks[1].has_times())

        # Times OK
        self.assertTrue(gpx.tracks[2].has_times())
        self.assertTrue(gpx.tracks[3].has_times())

    def test_unicode(self):
        gpx = self.__parse('unicode.gpx')

        name = gpx.waypoints[0].name

        self.assertTrue(name.encode('utf-8') == 'šđčćž')

    def test_nearest_location_1(self):
        gpx = self.__parse('korita-zbevnica.gpx')

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
        gpx = self.__parse('Mojstrovka.gpx')

        # %Y-%m-%dT%H:%M:%SZ'

    def test_reduce_gpx_file(self):
        f = open('test_files/Mojstrovka.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        max_reduced_points_no = 200

        started = mod_time.time()
        gpx = parser.parse()
        points_original = gpx.get_track_points_no()
        time_original = mod_time.time() - started

        gpx.reduce_points(max_reduced_points_no)

        points_reduced = gpx.get_track_points_no()

        result = gpx.to_xml()
        result = result.encode('utf-8')

        started = mod_time.time()
        parser = mod_parser.GPXParser(result)
        parser.parse()
        time_reduced = mod_time.time() - started

        print time_original
        print points_original

        print time_reduced
        print points_reduced

        self.assertTrue(time_reduced < time_original)
        self.assertTrue(points_reduced < points_original)
        self.assertTrue(points_reduced < max_reduced_points_no)

    def test_clone_and_smooth(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        original_2d = gpx.length_2d()
        original_3d = gpx.length_3d()

        cloned_gpx = gpx.clone()

        self.assertTrue(hash(gpx) == hash(cloned_gpx))

        cloned_gpx.reduce_points(2000, min_distance=10)
        cloned_gpx.smooth(vertical=True, horizontal=True)
        cloned_gpx.smooth(vertical=True, horizontal=False)

        print '2d:', gpx.length_2d()
        print '2d cloned and smoothed:', cloned_gpx.length_2d()

        print '3d:', gpx.length_3d()
        print '3d cloned and smoothed:', cloned_gpx.length_3d()

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
                print point.distance_3d(previous_point)
                if point.distance_3d(previous_point) < min_distance_before_reduce:
                    min_distance_before_reduce = point.distance_3d(previous_point)

        gpx.reduce_points(100000, min_distance=10)

        min_distance_after_reduce = 1000000
        for point, track_no, segment_no, point_no in gpx.walk():
            if point_no > 0:
                previous_point = gpx.tracks[track_no].segments[segment_no].points[point_no - 1]
                d = point.distance_3d(previous_point)
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

        print gpx.get_track_points_no()

        #gpx.reduce_points(1000, min_distance=5)

        print gpx.get_track_points_no()

        length = gpx.length_3d()
        print 'Distance: %s' % length

        gpx.reduce_points(2000, min_distance=10)

        gpx.smooth(vertical=True, horizontal=True)
        gpx.smooth(vertical=True, horizontal=False)

        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx.get_moving_data(stopped_speed_treshold=0.1)
        print '-----'
        print 'Length: %s' % length
        print 'Moving time: %s (%smin)' % (moving_time, moving_time / 60.)
        print 'Stopped time: %s (%smin)' % (stopped_time, stopped_time / 60.)
        print 'Moving distance: %s' % moving_distance
        print 'Stopped distance: %s' % stopped_distance
        print 'Max speed: %sm/s' % max_speed
        print '-----'

        # TODO: More tests and checks
        self.assertTrue(moving_distance < length)
        print 'Dakle:', moving_distance, length
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
        print 'Points in first (splitted) part:', len(track.segments[0].points)

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

        # Check that this splitted and joined track is the same as the original one:
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
        print segment.points[0]
        print original_segment.points[0]
        self.assertTrue(equals(segment.points[0], original_segment.points[0]))
        self.assertTrue(equals(segment.points[1], original_segment.points[1]))
        self.assertTrue(equals(segment.points[2], original_segment.points[2]))
        # ...but:
        self.assertTrue(equals(segment.points[3], original_segment.points[4]))

        self.assertTrue(len(segment.points) + 1 == len(original_segment.points))

    def test_distance(self):
        distance = mod_geo.distance(48.56806,21.43467, None, 48.599214,21.430878, None)
        print distance
        self.assertTrue(distance > 3450 and distance < 3500)

    def test_horizontal_smooth_remove_extreemes(self):
        f = open('test_files/track-with-extreemes.gpx', 'r')

        parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=False, horizontal=True, remove_extreemes=True)
        points_after = gpx.get_track_points_no()

        print points_before
        print points_after

        self.assertTrue(points_before - 2 == points_after)

    def test_vertical_smooth_remove_extreemes(self):
        f = open('test_files/track-with-extreemes.gpx', 'r')

        parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=True, horizontal=False, remove_extreemes=True)
        points_after = gpx.get_track_points_no()

        print points_before
        print points_after


        self.assertTrue(points_before - 1 == points_after)

    def test_horizontal_and_vertical_smooth_remove_extreemes(self):
        f = open('test_files/track-with-extreemes.gpx', 'r')

        parser = mod_parser.GPXParser(f)

        gpx = parser.parse()

        points_before = gpx.get_track_points_no()
        gpx.smooth(vertical=True, horizontal=True, remove_extreemes=True)
        points_after = gpx.get_track_points_no()

        print points_before
        print points_after

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

        print 'Found', result

        self.assertTrue(len(result) == 2)

    def test_hash_location(self):
        location_1 = mod_geo.Location(latitude=12, longitude=13, elevation=19)
        location_2 = mod_geo.Location(latitude=12, longitude=13, elevation=19)

        self.assertTrue(hash(location_1) == hash(location_2))

        location_2.elevation *= 2
        location_2.latitude *= 2
        location_2.longitude *= 2

        self.assertTrue(hash(location_1) != hash(location_2))

        location_2.elevation /= 2
        location_2.latitude /= 2
        location_2.longitude /= 2

        self.assertTrue(hash(location_1) == hash(location_2))

    def test_hash_gpx_track_point(self):
        point_1 = mod_gpx.GPXTrackPoint(latitude=12, longitude=13, elevation=19)
        point_2 = mod_gpx.GPXTrackPoint(latitude=12, longitude=13, elevation=19)

        self.assertTrue(hash(point_1) == hash(point_2))

        point_2.elevation *= 2
        point_2.latitude *= 2
        point_2.longitude *= 2

        self.assertTrue(hash(point_1) != hash(point_2))

        point_2.elevation /= 2
        point_2.latitude /= 2
        point_2.longitude /= 2

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

        self.assertEquals(bounds.min_latitude, -100)
        self.assertEquals(bounds.max_latitude, 100)
        self.assertEquals(bounds.min_longitude, -100)
        self.assertEquals(bounds.max_longitude, 100)

        # Test refresh bounds:

        gpx.refresh_bounds()
        self.assertEquals(gpx.min_latitude, -100)
        self.assertEquals(gpx.max_latitude, 100)
        self.assertEquals(gpx.min_longitude, -100)
        self.assertEquals(gpx.max_longitude, 100)

    def test_time_bounds(self):
        gpx = mod_gpx.GPX()

        track = mod_gpx.GPXTrack()

        segment_1 = mod_gpx.GPXTrackSegment()
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=13))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=-100, longitude=-5, time=mod_datetime.datetime(2001, 1, 12) ))
        segment_1.points.append(mod_gpx.GPXTrackPoint(latitude=100, longitude=-13 , time=mod_datetime.datetime(2003, 1, 12)))
        track.segments.append(segment_1)

        segment_2 = mod_gpx.GPXTrackSegment()
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-12, longitude=100, time=mod_datetime.datetime(2010, 1, 12)))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=-10, longitude=-5, time=mod_datetime.datetime(2011, 1, 12)))
        segment_2.points.append(mod_gpx.GPXTrackPoint(latitude=10, longitude=-100))
        track.segments.append(segment_2)

        gpx.tracks.append(track)

        bounds = gpx.get_time_bounds()

        self.assertEquals(bounds.start_time, mod_datetime.datetime(2001, 1, 12))
        self.assertEquals(bounds.end_time, mod_datetime.datetime(2011, 1, 12))

    def test_speed(self):
        gpx = self.__parse('track_with_speed.gpx')
        gpx2 = self.__reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

        self.assertEquals(gpx.tracks[0].segments[0].points[0].speed, 1.2)
        self.assertEquals(gpx.tracks[0].segments[0].points[1].speed, 2.2)
        self.assertEquals(gpx.tracks[0].segments[0].points[2].speed, 3.2)

    def test_dilutions(self):
        gpx = self.__parse('track_with_dilution_errors.gpx')
        gpx2 = self.__reparse(gpx)

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

        print latitudes
        print longitudes

        self.assertEquals(bounds.min_latitude, min(latitudes))
        self.assertEquals(bounds.max_latitude, max(latitudes))
        self.assertEquals(bounds.min_longitude, min(longitudes))
        self.assertEquals(bounds.max_longitude, max(longitudes))

        gpx.refresh_bounds()

        self.assertEquals(gpx.min_latitude, min(latitudes))
        self.assertEquals(gpx.max_latitude, max(latitudes))
        self.assertEquals(gpx.min_longitude, min(longitudes))
        self.assertEquals(gpx.max_longitude, max(longitudes))

    def test_named_tuples_values_bounds(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        bounds = gpx.get_bounds()
        min_lat, max_lat, min_lon, max_lon=gpx.get_bounds()

        self.assertEquals(min_lat, bounds.min_latitude)
        self.assertEquals(min_lon, bounds.min_longitude)
        self.assertEquals(max_lat, bounds.max_latitude)
        self.assertEquals(max_lon, bounds.max_longitude)

    def test_named_tuples_values_time_bounds(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        time_bounds = gpx.get_time_bounds()
        start_time, end_time = gpx.get_time_bounds()

        self.assertEquals(start_time, time_bounds.start_time)
        self.assertEquals(end_time, time_bounds.end_time)

    def test_named_tuples_values_moving_data(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        moving_data = gpx.get_moving_data()
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed=gpx.get_moving_data()
        self.assertEquals(moving_time, moving_data.moving_time)
        self.assertEquals(stopped_time, moving_data.stopped_time)
        self.assertEquals(moving_distance, moving_data.moving_distance)
        self.assertEquals(stopped_distance, moving_data.stopped_distance)
        self.assertEquals(max_speed, moving_data.max_speed)

    def test_named_tuples_values_uphill_downhill(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        uphill_downhill = gpx.get_uphill_downhill()
        uphill, downhill = gpx.get_uphill_downhill()
        self.assertEquals(uphill, uphill_downhill.uphill)
        self.assertEquals(downhill, uphill_downhill.downhill)

    def test_named_tuples_values_elevation_extreemes(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        elevation_extreemes = gpx.get_elevation_extremes()
        minimum, maximum = gpx.get_elevation_extremes()
        self.assertEquals(minimum, elevation_extreemes.minimum)
        self.assertEquals(maximum, elevation_extreemes.maximum)

    def test_named_tuples_values_nearest_location_data(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        location = gpx.tracks[1].segments[0].points[2]
        location.latitude *= 1.00001
        location.longitude *= 0.99999
        nearest_location_data = gpx.get_nearest_location(location)
        found_location, track_no, segment_no, point_no=gpx.get_nearest_location(location)
        self.assertEquals(found_location, nearest_location_data.location)
        self.assertEquals(track_no, nearest_location_data.track_no)
        self.assertEquals(segment_no, nearest_location_data.segment_no)
        self.assertEquals(point_no, nearest_location_data.point_no)

    def test_named_tuples_values_point_data(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        points_datas = gpx.get_points_data()

        for point_data in points_datas:
            point, distance_from_start, track_no, segment_no, point_no=point_data
            self.assertEquals(point, point_data.point)
            self.assertEquals(distance_from_start, point_data.distance_from_start)
            self.assertEquals(track_no, point_data.track_no)
            self.assertEquals(segment_no, point_data.segment_no)
            self.assertEquals(point_no, point_data.point_no)

    def test_track_points_data(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        points_data_2d = gpx.get_points_data(distance_2d=True)

        point, distance_from_start, track_no, segment_no, point_no=points_data_2d[-1]
        self.assertEquals(track_no, len(gpx.tracks) - 1)
        self.assertEquals(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEquals(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)
        self.assertTrue(abs(distance_from_start - gpx.length_2d()) < 0.0001)

        points_data_3d = gpx.get_points_data(distance_2d=False)
        point, distance_from_start, track_no, segment_no, point_no=points_data_3d[-1]
        self.assertEquals(track_no, len(gpx.tracks) - 1)
        self.assertEquals(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEquals(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)
        self.assertTrue(abs(distance_from_start - gpx.length_3d()) < 0.0001)

        self.assertTrue(gpx.length_2d() != gpx.length_3d())

    def test_walk_route_points(self):
        gpx = mod_gpxpy.parse(file('test_files/route.gpx'))

        for point in gpx.routes[0].walk(only_points=True):
            self.assertTrue(point)

        for point, point_no in gpx.routes[0].walk():
            self.assertTrue(point)

        self.assertEquals(point_no, len(gpx.routes[0].points) - 1)

    def test_walk_gpx_points(self):
        gpx = self.__parse('korita-zbevnica.gpx')

        for point in gpx.walk():
            self.assertTrue(point)

        for point, track_no, segment_no, point_no in gpx.walk():
            self.assertTrue(point)

        self.assertEquals(track_no, len(gpx.tracks) - 1)
        self.assertEquals(segment_no, len(gpx.tracks[-1].segments) - 1)
        self.assertEquals(point_no, len(gpx.tracks[-1].segments[-1].points) - 1)

    def test_walk_gpx_points(self):
        gpx = self.__parse('korita-zbevnica.gpx')
        track = gpx.tracks[1]

        for point in track.walk():
            self.assertTrue(point)

        for point, segment_no, point_no in track.walk():
            self.assertTrue(point)

        self.assertEquals(segment_no, len(track.segments) - 1)
        self.assertEquals(point_no, len(track.segments[-1].points) - 1)

    def test_walk_segment_points(self):
        gpx = self.__parse('korita-zbevnica.gpx')
        track = gpx.tracks[1]
        segment = track.segments[0]

        assert len(segment.points) > 0

        for point in segment.walk():
            self.assertTrue(point)

        """
        for point, segment_no, point_no in track.walk():
            self.assertTrue(point)

        self.assertEquals(segment_no, len(track.segments) - 1)
        self.assertEquals(point_no, len(track.segments[-1].points) - 1)
        """

    def test_angle_0(self):
        loc1 = mod_geo.Location(0, 0)
        loc2 = mod_geo.Location(0, 1)

        loc1.elevation = 100
        loc2.elevation = 100

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEquals(angle_radians, 0)
        self.assertEquals(angle_degrees, 0)

    def test_angle(self):
        loc1 = mod_geo.Location(0, 0)
        loc2 = mod_geo.Location(0, 1)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEquals(angle_radians, mod_math.pi / 4)
        self.assertEquals(angle_degrees, 45)

    def test_angle_2(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + 0.5 * loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertTrue(angle_radians < mod_math.pi / 4)
        self.assertTrue(angle_degrees < 45)

    def test_angle_2(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation + 1.5 * loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertTrue(angle_radians > mod_math.pi / 4)
        self.assertTrue(angle_degrees > 45)

    def test_angle_3(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        loc1.elevation = 100
        loc2.elevation = loc1.elevation - loc1.distance_2d(loc2)

        angle_radians = mod_geo.elevation_angle(loc1, loc2, radians=True)
        angle_degrees = mod_geo.elevation_angle(loc1, loc2, radians=False)

        self.assertEquals(angle_radians, - mod_math.pi / 4)
        self.assertEquals(angle_degrees, - 45)

    def test_angle_loc(self):
        loc1 = mod_geo.Location(45, 45)
        loc2 = mod_geo.Location(46, 45)

        self.assertEquals(loc1.elevation_angle(loc2), mod_geo.elevation_angle(loc1, loc2))
        self.assertEquals(loc1.elevation_angle(loc2, radians=True), mod_geo.elevation_angle(loc1, loc2, radians=True))
        self.assertEquals(loc1.elevation_angle(loc2, radians=False), mod_geo.elevation_angle(loc1, loc2, radians=False))

if __name__ == '__main__':
    mod_unittest.main()
als
