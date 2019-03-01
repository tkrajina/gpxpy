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
import datetime as mod_datetime
import unittest as mod_unittest

from .helper import parse, reparse, equals, custom_open
import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx
import gpxpy.parser as mod_parser
import gpxpy.geo as mod_geo

from gpxpy.utils import parse_time

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')


def cca(number1, number2):
    return 1 - number1 / number2 < 0.999


class GPXTests(mod_unittest.TestCase):
    """
    Add tests here.
    """

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

    def test_has_times_false(self):
        gpx = parse('cerknicko-without-times.gpx')
        self.assertFalse(gpx.has_times())

    def test_has_times(self):
        gpx = parse('korita-zbevnica.gpx')
        self.assertTrue(len(gpx.tracks) == 4)
        # Empty -- True
        self.assertTrue(gpx.tracks[0].has_times())
        # Not times ...
        self.assertTrue(not gpx.tracks[1].has_times())

        # Times OK
        self.assertTrue(gpx.tracks[2].has_times())
        self.assertTrue(gpx.tracks[3].has_times())

    def test_force_version(self):
        parse('unicode_with_bom.gpx', version='1.1', encoding='utf-8')
        # TODO: Implement new test. Current gpx is not valid (extensions using default namespace).
        # I don't want to edit this file without easy verification that it has the BOM and is unicode

        # security = gpx.waypoints[0].extensions['security']
        # self.assertTrue(make_str(security) == 'Open')

    def test_nearest_location_1(self):
        gpx = parse('korita-zbevnica.gpx')

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
        gpx = parse('Mojstrovka.gpx')

        # %Y-%m-%dT%H:%M:%SZ'
        self.assertEqual(gpx.tracks[0].segments[0].points[0].elevation, 1614.678000)
        self.assertEqual(gpx.tracks[0].segments[0].points[0].time, mod_datetime.datetime(1901, 12, 13, 20, 45, 52))

    def test_moving_stopped_times(self):
        f = open('test_files/cerknicko-jezero.gpx')
        parser = mod_parser.GPXParser(f)
        gpx = parser.parse()
        f.close()

        print(gpx.get_track_points_no())

        # gpx.reduce_points(1000, min_distance=5)

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

    def test_distance(self):
        distance = mod_geo.distance(48.56806, 21.43467, None, 48.599214, 21.430878, None)
        print(distance)
        self.assertTrue(distance > 3450 and distance < 3500)

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

    def test_speed(self):
        gpx = parse('track_with_speed.gpx')
        gpx2 = reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

        self.assertEqual(gpx.tracks[0].segments[0].points[0].speed, 1.2)
        self.assertEqual(gpx.tracks[0].segments[0].points[1].speed, 2.2)
        self.assertEqual(gpx.tracks[0].segments[0].points[2].speed, 3.2)

    def test_dilutions(self):
        gpx = parse('track_with_dilution_errors.gpx')
        gpx2 = reparse(gpx)

        self.assertTrue(equals(gpx.waypoints, gpx2.waypoints))
        self.assertTrue(equals(gpx.routes, gpx2.routes))
        self.assertTrue(equals(gpx.tracks, gpx2.tracks))
        self.assertTrue(equals(gpx, gpx2))

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

        gpx2 = reparse(gpx)

        self.assertEqual(gpx2.tracks[0].segments[0].points[0].name, 'aaa')
        self.assertEqual(gpx2.tracks[0].segments[0].points[0].comment, 'ccc')
        self.assertEqual(gpx2.tracks[0].segments[0].points[0].symbol, 'sss')

    def test_track_points_data(self):
        gpx = parse('korita-zbevnica.gpx')

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

    def test_track_with_empty_segment(self):
        with open('test_files/track-with-empty-segment.gpx') as f:
            gpx = mod_gpxpy.parse(f)
            self.assertIsNotNone(gpx.tracks[0].get_bounds().min_latitude)
            self.assertIsNotNone(gpx.tracks[0].get_bounds().min_longitude)

    def test_distance_from_line(self):
        d = mod_geo.distance_from_line(mod_geo.Location(1, 1),
                                       mod_geo.Location(0, -1),
                                       mod_geo.Location(0, 1))
        self.assertTrue(abs(d - mod_geo.ONE_DEGREE) < 100)

    def test_time_difference(self):
        point_1 = mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                        time=mod_datetime.datetime(2013, 1, 2, 12, 31))
        point_2 = mod_gpx.GPXTrackPoint(latitude=13, longitude=12,
                                        time=mod_datetime.datetime(2013, 1, 3, 12, 32))

        seconds = point_1.time_difference(point_2)
        self.assertEqual(seconds, 60 * 60 * 24 + 60)

    def test_parse_time(self):
        timestamps = [
            '2001-10-26T21:32:52',
            # '2001-10-26T21:32:52+0200',
            '2001-10-26T19:32:52Z',
            # '2001-10-26T19:32:52+00:00',
            # '-2001-10-26T21:32:52',
            '2001-10-26T21:32:52.12679',
            '2001-10-26T21:32:52',
            # '2001-10-26T21:32:52+02:00',
            '2001-10-26T19:32:52Z',
            # '2001-10-26T19:32:52+00:00',
            # '-2001-10-26T21:32:52',
            '2001-10-26T21:32:52.12679',
        ]
        timestamps_without_tz = list(map(lambda x: x.replace('T', ' ').replace('Z', ''), timestamps))
        for t in timestamps_without_tz:
            timestamps.append(t)
        for timestamp in timestamps:
            print('Parsing: %s' % timestamp)
            self.assertTrue(parse_time(timestamp) is not None)

    def test_get_location_at(self):
        gpx = mod_gpx.GPX()
        gpx.tracks.append(mod_gpx.GPXTrack())
        gpx.tracks[0].segments.append(mod_gpx.GPXTrackSegment())
        p0 = mod_gpx.GPXTrackPoint(latitude=13.0, longitude=13.0, time=mod_datetime.datetime(2013, 1, 2, 12, 30, 0))
        p1 = mod_gpx.GPXTrackPoint(latitude=13.1, longitude=13.1, time=mod_datetime.datetime(2013, 1, 2, 12, 31, 0))
        gpx.tracks[0].segments[0].points.append(p0)
        gpx.tracks[0].segments[0].points.append(p1)

        self.assertEqual(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 29, 30)), [])
        self.assertEqual(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 30, 0))[0], p0)
        self.assertEqual(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 30, 30))[0], p1)
        self.assertEqual(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 31, 0))[0], p1)
        self.assertEqual(gpx.tracks[0].get_location_at(mod_datetime.datetime(2013, 1, 2, 12, 31, 30)), [])

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
        with open('test_files/gpx-with-node-with-comments.gpx') as f:
            self.assertTrue(mod_gpxpy.parse(f))

    def __test_location_delta(self, location, distance):
        angles = [x * 15 for x in range(int(360 / 15))]
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

    def test_xml_chars_encode_decode(self):
        gpx = mod_gpxpy.gpx.GPX()
        gpx.name = "Test<a>jkljkl</gpx>"

        print(gpx.to_xml())

        gpx_2 = mod_gpxpy.parse(gpx.to_xml())

        self.assertTrue('<name>Test&lt;a&gt;jkljkl&lt;/gpx&gt;</name>' in gpx_2.to_xml())

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
        self.assertEqual(100, elevation_min)
        self.assertEqual(200, elevation_max)

        # Check for track:
        elevation_min, elevation_max = track.get_elevation_extremes()
        self.assertEqual(100, elevation_min)
        self.assertEqual(200, elevation_max)

        # Check for gpx:
        elevation_min, elevation_max = gpx.get_elevation_extremes()
        self.assertEqual(100, elevation_min)
        self.assertEqual(200, elevation_max)

    def test_distance_between_points_near_0_longitude(self):
        """ Make sure that the distance function works properly when points have longitudes on opposite sides of the 0-longitude meridian """
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=-0.1, elevation_2=0, haversine=True)
        print(distance)
        self.assertTrue(distance < 230000)
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=-0.1, elevation_2=0, haversine=False)
        print(distance)
        self.assertTrue(distance < 230000)
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=360 - 0.1, elevation_2=0, haversine=True)
        print(distance)
        self.assertTrue(distance < 230000)
        distance = mod_geo.distance(latitude_1=0, longitude_1=0.1, elevation_1=0, latitude_2=0, longitude_2=360 - 0.1, elevation_2=0, haversine=False)
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

        self.assertEqual(1, len(gpx.tracks))
        self.assertEqual(1, len(gpx.tracks[0].segments))
        self.assertEqual(1, len(gpx.tracks[0].segments[0].points))
        self.assertEqual(0, gpx.tracks[0].segments[0].points[0].latitude)
        self.assertEqual(0, gpx.tracks[0].segments[0].points[0].longitude)
        self.assertEqual(0, gpx.tracks[0].segments[0].points[0].elevation)

        gpx2 = mod_gpxpy.parse(xml)

        self.assertEqual(1, len(gpx2.tracks))
        self.assertEqual(1, len(gpx2.tracks[0].segments))
        self.assertEqual(1, len(gpx2.tracks[0].segments[0].points))
        self.assertEqual(0, gpx2.tracks[0].segments[0].points[0].latitude)
        self.assertEqual(0, gpx2.tracks[0].segments[0].points[0].longitude)
        self.assertEqual(0, gpx2.tracks[0].segments[0].points[0].elevation)

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

        self.assertEqual(rtes, len(result_gpx.routes))
        self.assertEqual(wpts, len(result_gpx.waypoints))
        self.assertEqual(trcks, len(result_gpx.tracks))
        self.assertEqual(points, result_gpx.get_points_no())

    def test_small_floats(self):
        """GPX 1/1 does not allow scientific notation but that is what gpxpy writes right now."""
        f = open('test_files/track-with-small-floats.gpx', 'r')

        gpx = mod_gpxpy.parse(f)

        xml = gpx.to_xml()
        self.assertNotIn('e-', xml)

    def test_single_quotes_xmlns(self):
        gpx = mod_gpxpy.parse("""<?xml version='1.0' encoding='UTF-8'?>
<gpx version='1.1' creator='GPSMID' xmlns='http://www.topografix.com/GPX/1/1'>
<trk>
<trkseg>
<trkpt lat='40.61262' lon='10.592117'><ele>100</ele><time>2018-01-01T09:00:00Z</time>
</trkpt>
</trkseg>
</trk>
</gpx>""")

        self.assertEqual(1, len(gpx.tracks))
        self.assertEqual(1, len(gpx.tracks[0].segments))
        self.assertEqual(1, len(gpx.tracks[0].segments[0].points))

    def test_default_schema_locations(self):
        gpx = mod_gpx.GPX()
        with custom_open('test_files/default_schema_locations.gpx') as f:
            self.assertEqual(gpx.to_xml(), f.read())

    def test_custom_schema_locations(self):
        gpx = mod_gpx.GPX()
        gpx.nsmap = {
            'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
        }
        gpx.schema_locations = [
            'http://www.topografix.com/GPX/1/1',
            'http://www.topografix.com/GPX/1/1/gpx.xsd',
            'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
            'http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd',
        ]
        with custom_open('test_files/custom_schema_locations.gpx') as f:
            self.assertEqual(gpx.to_xml(), f.read())

    def test_parse_custom_schema_locations(self):
        gpx = parse('custom_schema_locations.gpx')
        self.assertEqual(
            [
                'http://www.topografix.com/GPX/1/1',
                'http://www.topografix.com/GPX/1/1/gpx.xsd',
                'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
                'http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd',
            ],
            gpx.schema_locations
        )

    def test_no_track(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:om="http://www.oruxmaps.com/oruxmapsextensions/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="OruxMaps v.6.5.10">
    <extensions>
      <om:oruxmapsextensions></om:oruxmapsextensions>
    </extensions>
</gpx>"""
        gpx = mod_gpxpy.parse(xml)
        self.assertEqual(0, len(gpx.tracks))
        gpx2 = reparse(gpx)
        self.assertEqual(0, len(gpx2.tracks))


class LxmlTest(mod_unittest.TestCase):
    @mod_unittest.skipIf(mod_os.environ.get('XMLPARSER') != "LXML", "LXML not installed")
    def test_checklxml(self):
        self.assertEqual('LXML', mod_parser.GPXParser._GPXParser__library())


if __name__ == '__main__':
    mod_unittest.main()
