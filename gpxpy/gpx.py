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
import math as mod_math
import datetime as mod_datetime
import collections as mod_collections

import utils as mod_utils
import copy as mod_copy
import geo as mod_geo

"""
GPX related stuff
"""

# GPX date format
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# Used in smoothing, sum must be 1:
SMOOTHING_RATIO = (0.4, 0.2, 0.4)

# When computing stopped time -- this is the miminum speed between two points, if speed is less
# than this value -- we'll assume it is 0
DEFAULT_STOPPED_SPEED_TRESHOLD = 1

# When possible, the result of various methods are named tuples defined here:
Bounds = mod_collections.namedtuple(
        'Bounds',
        ('min_latitude', 'max_latitude', 'min_longitude', 'max_longitude'))
TimeBounds = mod_collections.namedtuple(
        'TimeBounds',
        ('start_time', 'end_time'))
MovingData = mod_collections.namedtuple(
        'MovingData',
        ('moving_time', 'stopped_time', 'moving_distance', 'stopped_distance', 'max_speed'))
UphillDownhill = mod_collections.namedtuple(
        'UphillDownhill',
        ('uphill', 'downhill'))
MinimumMaximum = mod_collections.namedtuple(
        'MinimumMaximum',
        ('minimum', 'maximum'))
NearestLocationData = mod_collections.namedtuple(
        'NearestLocationData',
        ('location', 'track_no', 'segment_no', 'point_no'))
PointData = mod_collections.namedtuple(
        'PointData',
        ('point', 'distance_from_start', 'track_no', 'segment_no', 'point_no'))

class GPXException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class GPXWaypoint(mod_geo.Location):
    time = None
    name = None
    description = None
    symbol = None
    type = None
    comment = None

    # Horizontal dilution of precision
    horizontal_dilution = None
    # Vertical dilution of precision
    vertical_dilution = None
    # Position dilution of precision
    position_dilution = None
	
    def __init__(self, latitude, longitude, elevation=None, time=None,
              name=None, description=None, symbol=None, type=None,
              comment=None, horizontal_dilution=None, vertical_dilution=None,
              position_dilution=None):
        mod_geo.Location.__init__(self, latitude, longitude, elevation)

        self.time = time
        self.name = name
        self.description = description
        self.symbol = symbol
        self.type = type
        self.comment = comment

        self.horizontal_dilution = horizontal_dilution
        self.vertical_dilution = vertical_dilution
        self.position_dilution = position_dilution
		
    def __str__(self):
        return '[wpt{%s}:%s,%s@%s]' % (self.name, self.latitude, self.longitude, self.elevation)

    def to_xml(self, version=None):
        content = ''
        if self.elevation != None:
            content += mod_utils.to_xml('ele', content=self.elevation)
        if self.time:
            content += mod_utils.to_xml('time', content=self.time.strftime(DATE_FORMAT))
        if self.name:
            content += mod_utils.to_xml('name', content=self.name, escape=True)
        if self.description:
            content += mod_utils.to_xml('desc', content=self.description, escape=True)
        if self.symbol:
            content += mod_utils.to_xml('sym', content=self.symbol, escape=True)
        if self.type:
            content += mod_utils.to_xml('type', content=self.type, escape=True)

        if version == '1.1': # TODO
            content += mod_utils.to_xml('cmt', content=self.comment, escape=True)

        if self.horizontal_dilution:
            content += mod_utils.to_xml('hdop', content=self.horizontal_dilution)
        if self.vertical_dilution:
            content += mod_utils.to_xml('vdop', content=self.vertical_dilution)
        if self.position_dilution:
            content += mod_utils.to_xml('pdop', content=self.position_dilution)
		
        return mod_utils.to_xml('wpt', attributes={'lat': self.latitude, 'lon': self.longitude}, content=content)
	
    def get_max_dilution_of_precision(self):
        """
        Only care about the max dop for filtering, no need to go into too much detail
        """
        return max(self.horizontal_dilution, self.vertical_dilution, self.position_dilution)
	
    def __hash__(self):
        return mod_utils.hash_object(self, 'time', 'name', 'description', 'symbol', 'type',
                'comment', 'horizontal_dilution', 'vertical_dilution', 'position_dilution')

class GPXRoute:
    name = None
    description = None
    number = None

    points = []

    def __init__(self, name=None, description=None, number=None):
        self.name = name
        self.description = description
        self.number = number

        self.points = []

    def remove_elevation(self):
        for point in self.points:
            point.remove_elevation()

    def length(self):
        return mod_geo.length_2d(self.points)

    def get_center(self):
        if not self.points:
            return None

        if not self.points:
            return None

        sum_lat = 0.
        sum_lon = 0.
        n = 0.

        for point in self.points:
            n += 1.
            sum_lat += point.latitude
            sum_lon += point.longitude

        if not n:
            return mod_geo.Location(float(0), float(0))

        return mod_geo.Location(latitude=sum_lat / n, longitude=sum_lon / n)

    def walk(self, only_points=False):
        for point_no, point in enumerate(self.points):
            if only_points:
                yield point
            else:
                yield point, point_no

    def get_points_no(self):
        return len(self.points)

    def move(self, latitude_diff, longitude_diff):
        for route_point in self.points:
            route_point.move(latitude_diff, longitude_diff)

    def to_xml(self, version=None):
        content = ''
        if self.name:
            content += mod_utils.to_xml('name', content=self.name, escape=True)
        if self.description:
            content += mod_utils.to_xml('desc', content=self.description, escape=True)
        if self.number:
            content += mod_utils.to_xml('number', content=self.number)
        for route_point in self.points:
            content += route_point.to_xml(version)

        return mod_utils.to_xml('rte', content=content)

    def __hash__(self):
        return mod_utils.hash_object(self, 'name', 'description', 'number', 'points')

class GPXRoutePoint(mod_geo.Location):
    time = None
    name = None
    description = None
    symbol = None
    type = None
    comment = None

    # Horizontal dilution of precision
    horizontal_dilution = None
    # Vertical dilution of precision
    vertical_dilution = None
    # Position dilution of precision
    position_dilution = None

    def __init__(self, latitude, longitude, elevation=None, time=None, name=None,
            description=None, symbol=None, type=None, comment=None,
            horizontal_dilution=None, vertical_dilution=None,
            position_dilution=None):

        mod_geo.Location.__init__(self, latitude, longitude, elevation)

        self.time = time
        self.name = name
        self.description = description
        self.symbol = symbol
        self.type = type
        self.comment = comment

        self.horizontal_dilution = horizontal_dilution
        self.vertical_dilution = vertical_dilution
        self.position_dilution = position_dilution

    def __str__(self):
        return '[rtept{%s}:%s,%s@%s]' % (self.name, self.latitude, self.longitude, self.elevation)

    def to_xml(self, version=None):
        content = ''
        if self.elevation != None:
            content += mod_utils.to_xml('ele', content=self.elevation)
        if self.time:
            content += mod_utils.to_xml('time', content=self.time.strftime(DATE_FORMAT))
        if self.name:
            content += mod_utils.to_xml('name', content=self.name, escape=True)
        if self.comment:
            content += mod_utils.to_xml('cmt', content=self.comment, escape=True)
        if self.description:
            content += mod_utils.to_xml('desc', content=self.description, escape=True)
        if self.symbol:
            content += mod_utils.to_xml('sym', content=self.symbol, escape=True)
        if self.type:
            content += mod_utils.to_xml('type', content=self.type, escape=True)
	
        if self.horizontal_dilution:
            content += mod_utils.to_xml('hdop', content=self.horizontal_dilution)
        if self.vertical_dilution:
            content += mod_utils.to_xml('vdop', content=self.vertical_dilution)
        if self.position_dilution:
            content += mod_utils.to_xml('pdop', content=self.position_dilution)

        return mod_utils.to_xml('rtept', attributes={'lat': self.latitude, 'lon': self.longitude}, content=content)

    def __hash__(self):
        return mod_utils.hash_object(self, 'time', 'name', 'description', 'symbol', 'type', 'comment',
                'horizontal_dilution', 'vertical_dilution', 'position_dilution')

class GPXTrackPoint(mod_geo.Location):
    time = None
    symbol = None
    comment = None

    # Horizontal dilution of precision
    horizontal_dilution = None
    # Vertical dilution of precision
    vertical_dilution = None
    # Position dilution of precision
    position_dilution = None

    def __init__(self, latitude, longitude, elevation=None, time=None, symbol=None, comment=None,
            horizontal_dilution=None, vertical_dilution=None, position_dilution=None):
        mod_geo.Location.__init__(self, latitude, longitude, elevation)

        self.time = time
        self.symbol = symbol
        self.comment = comment

        self.horizontal_dilution = horizontal_dilution
        self.vertical_dilution = vertical_dilution
        self.position_dilution = position_dilution

    def remove_time(self):
        """ Will remove time metadata. """
        self.time = None

    def to_xml(self, version=None):
        content = ''

        if self.elevation != None:
            content += mod_utils.to_xml('ele', content=self.elevation)
        if self.time:
            content += mod_utils.to_xml('time', content=self.time.strftime(DATE_FORMAT))
        if self.comment:
            content += mod_utils.to_xml('cmt', content=self.comment, escape=True)
        if self.symbol:
            content += mod_utils.to_xml('sym', content=self.symbol, escape=True)

        if self.horizontal_dilution:
            content += mod_utils.to_xml('hdop', content=self.horizontal_dilution)
        if self.vertical_dilution:
            content += mod_utils.to_xml('vdop', content=self.vertical_dilution)
        if self.position_dilution:
            content += mod_utils.to_xml('pdop', content=self.position_dilution)

        return mod_utils.to_xml('trkpt', {'lat': self.latitude, 'lon': self.longitude}, content=content)

    def time_difference(self, track_point):
        """ Time distance in seconds beween times fo those two points """
        if not self.time or not track_point or not track_point.time:
            return None
		
        time_1 = self.time
        time_2 = track_point.time

        if time_1 == time_2:
            return 0

        if time_1 > time_2:
            delta = time_1 - time_2
        else:
            delta = time_2 - time_1

        return delta.seconds

    def speed(self, track_point):
        if not track_point:
            return None

        seconds = self.time_difference(track_point)
        length = self.distance_3d(track_point)
        if not length:
            length = self.distance_2d(track_point)

        if not seconds or not length:
            return None

        return length / float(seconds)

    def __str__(self):
        return '[trkpt:%s,%s@%s@%s]' % (self.latitude, self.longitude, self.elevation, self.time)

    def __hash__(self):
        return mod_utils.hash_object(self, 'latitude', 'longitude', 'elevation', 'time', 'symbol', 'comment',
                'horizontal_dilution', 'vertical_dilution', 'position_dilution')

class GPXTrack:
    name = None
    description = None
    number = None

    segments = None

    def __init__(self, name=None, description=None, number=None):
        self.name = name
        self.description = description
        self.number = number

        self.segments = []

    def remove_time(self):
        for segment in self.segments:
            segment.remove_time()

    def remove_elevation(self):
        for segment in self.segments:
            segment.remove_elevation()

    def remove_empty(self):
        """ Removes empty segments and/or routes """
        result = []

        for segment in self.segments:
            if len(segment.points) > 0:
                result.append(segment)

        self.segments = result
	
    def length_2d(self):
        length = 0
        for track_segment in self.segments:
            d = track_segment.length_2d()
            if d:
                length += d
        return length

    def get_time_bounds(self):
        start_time = None
        end_time = None

        for track_segment in self.segments:
            point_start_time, point_end_time = track_segment.get_time_bounds()
            if not start_time and point_start_time:
                start_time = point_start_time
            if point_end_time:
                end_time = point_end_time

        return TimeBounds(start_time, end_time)
	
    def get_bounds(self):
        min_lat = None
        max_lat = None
        min_lon = None
        max_lon = None
        for track_segment in self.segments:
            bounds = track_segment.get_bounds()

            if not mod_utils.is_numeric(min_lat) or bounds.min_latitude < min_lat:
                min_lat = bounds.min_latitude
            if not mod_utils.is_numeric(max_lat) or bounds.max_latitude > max_lat:
                max_lat = bounds.max_latitude
            if not mod_utils.is_numeric(min_lon) or bounds.min_longitude < min_lon:
                min_lon = bounds.min_longitude
            if not mod_utils.is_numeric(max_lon) or bounds.max_longitude > max_lon:
                max_lon = bounds.max_longitude

        return Bounds(min_lat, max_lat, min_lon, max_lon)

    def walk(self, only_points=False):
        for segment_no, segment in enumerate(self.segments):
            for point_no, point in enumerate(segment.points):
                if only_points:
                    yield point
                else:
                    yield point, segment_no, point_no

    def get_points_no(self):
        result = 0

        for track_segment in self.segments:
            result += track_segment.get_points_no()

        return result

    def length_3d(self):
        length = 0
        for track_segment in self.segments:
            d = track_segment.length_3d()
            if d:
                length += d
        return length

    def split(self, track_segment_no, track_point_no):
        """ Splits One of the segments in two parts. If one of the splitted segments is empty
        it will not be added in the result """
        new_segments = []
        for i in range(len(self.segments)):
            segment = self.segments[i]
            if i == track_segment_no:
                segment_1, segment_2 = segment.split(track_point_no)
                if segment_1:
                    new_segments.append(segment_1)
                if segment_2:
                    new_segments.append(segment_2)
            else:
                new_segments.append(segment)
        self.segments = new_segments

    def join(self, track_segment_no, track_segment_no_2=None):
        """ Joins two segments of this track. If track_segment_no_2 the join will be with the
        next segment """

        if not track_segment_no_2:
            track_segment_no_2 = track_segment_no + 1

        if track_segment_no_2 >= len(self.segments):
            return

        new_segments = []
        for i in range(len(self.segments)):
            segment = self.segments[i]
            if i == track_segment_no:
                second_segment = self.segments[track_segment_no_2]
                segment.join(second_segment)

                new_segments.append(segment)
            elif i == track_segment_no_2:
                # Nothing, it is already joined
                pass
            else:
                new_segments.append(segment)
        self.segments = new_segments

    def get_moving_data(self, stopped_speed_treshold=None):
        moving_time = 0.
        stopped_time = 0.

        moving_distance = 0.
        stopped_distance = 0.

        max_speed = 0.

        for segment in self.segments:
            track_moving_time, track_stopped_time, track_moving_distance, track_stopped_distance, track_max_speed = segment.get_moving_data(stopped_speed_treshold)
            moving_time += track_moving_time
            stopped_time += track_stopped_time
            moving_distance += track_moving_distance
            stopped_distance += track_stopped_distance

            if track_max_speed > max_speed:
                max_speed = track_max_speed

        return MovingData(moving_time, stopped_time, moving_distance, stopped_distance, max_speed)

    def add_elevation(self, delta):
        for track_segment in self.segments:
            track_segment.add_elevation(delta)

    def move(self, latitude_diff, longitude_diff):
        for track_segment in self.segments:
            track_segment.move(latitude_diff, longitude_diff)

    def get_duration(self):
        """ Note returns None if one of track segments hasn't time data """
        if not self.segments:
            return 0

        result = 0
        for track_segment in self.segments:
            duration = track_segment.get_duration()
            if duration or duration == 0:
                result += duration
            elif duration == None:
                return None

        return result

    def get_uphill_downhill(self):
        if not self.segments:
            return UphillDownhill(0, 0)

        uphill = 0
        downhill = 0

        for track_segment in self.segments:
            current_uphill, current_downhill = track_segment.get_uphill_downhill()

            uphill += current_uphill
            downhill += current_downhill

        return UphillDownhill(uphill, downhill)

    def get_location_at(self, time):
        """ 
        Get locations for this time. There may be more locations because of 
        time-overlapping track segments.
        """
        result = []
        for track_segment in self.segments:
            location = track_segment.get_location_at(time)
            if location:
                result.append(location)

        return result

    def get_elevation_extremes(self):
        if not self.segments:
            return MinimumMaximum(0, 0)

        elevations = []

        for track_segment in self.segments:
            (_min, _max) = track_segment.get_elevation_extremes()
            elevations.append(_min)
            elevations.append(_max)

        return MinimumMaximum(min(elevations), max(elevations))

    def to_xml(self, version=None):
        content = mod_utils.to_xml('name', content=self.name, escape=True)
        content += mod_utils.to_xml('desc', content=self.description, escape=True)
        if self.number:
            content += mod_utils.to_xml('number', content=self.number)
        for track_segment in self.segments:
            content += track_segment.to_xml(version)

        return mod_utils.to_xml('trk', content=content)

    def get_center(self):
        """ "Average" location for this track """
        if not self.segments:
            return None
        sum_lat = 0
        sum_lon = 0
        n = 0
        for track_segment in self.segments:
            for point in track_segment.points:
                n += 1.
                sum_lat += point.latitude
                sum_lon += point.longitude

        if not n:
            return mod_geo.Location(float(0), float(0))

        return mod_geo.Location(latitude=sum_lat / n, longitude=sum_lon / n)

    def smooth(self, vertical=True, horizontal=False, remove_extreemes=False):
        """ See: GPXTrackSegment.smooth() """
        for track_segment in self.segments:
            track_segment.smooth(vertical, horizontal, remove_extreemes)

    def has_times(self):
        """ See GPXTrackSegment.has_times() """
        if not self.segments:
            return None

        result = True
        for track_segment in self.segments:
            result = result and track_segment.has_times()

        return result

    def get_nearest_location(self, location):
        """ Returns (location, track_segment_no, track_point_no) for nearest location on track """
        if not self.segments:
            return None

        result = None
        distance = None
        result_track_segment_no = None
        result_track_point_no = None

        for i in range(len(self.segments)):
            track_segment = self.segments[i]
            nearest_location, track_point_no = track_segment.get_nearest_location(location)
            nearest_location_distance = None
            if nearest_location:
                nearest_location_distance = nearest_location.distance_2d(location)

            if not distance or nearest_location_distance < distance:
                if nearest_location:
                    distance = nearest_location_distance
                    result = nearest_location
                    result_track_segment_no = i
                    result_track_point_no = track_point_no

        return (result, result_track_segment_no, result_track_point_no)

    def clone(self):
        return mod_copy.deepcopy(self)

    def __hash__(self):
        return mod_utils.hash_object(self, 'name', 'description', 'number', 'segments')

class GPXTrackSegment:
    points = None

    def __init__(self, points=None):
        self.points = points if points else []

    def remove_time(self):
        for track_point in self.points:
            track_point.remove_time()

    def remove_elevation(self):
        for track_point in self.points:
            track_point.remove_elevation()

    def length_2d(self):
        return mod_geo.length_2d(self.points)

    def length_3d(self):
        return mod_geo.length_3d(self.points)

    def move(self, latitude_diff, longitude_diff):
        for track_point in self.points:
            track_point.move(latitude_diff, longitude_diff)

    def walk(self, only_points=False):
        """ Use this to iterate through points """
        for point_no, point in enumerate(self.points):
            if only_points:
                yield point
            else:
                yield point, point_no

    def get_points_no(self):
        """ Number of points """
        if not self.points:
            return 0
        return len(self.points)

    def split(self, point_no):
        """ Splits this segment in two parts. Point #point_no remains in the first part. 
        Returns a list with two GPXTrackSegments """
        part_1 = self.points[: point_no + 1]
        part_2 = self.points[point_no + 1 :]
        return (GPXTrackSegment(part_1), GPXTrackSegment(part_2))

    def join(self, track_segment):
        """ Joins with another segment """
        self.points += track_segment.points

    def remove_point(self, point_no):
        if point_no < 0 or point_no >= len(self.points):
            return

        part_1 = self.points[: point_no]
        part_2 = self.points[point_no + 1 :]

        self.points = part_1 + part_2

    def get_moving_data(self, stopped_speed_treshold=None):
        if not stopped_speed_treshold:
            stopped_speed_treshold = DEFAULT_STOPPED_SPEED_TRESHOLD

        moving_time = 0.
        stopped_time = 0.

        moving_distance = 0.
        stopped_distance = 0.

        max_speed = 0.

        previous = None
        for i in range(1, len(self.points)):

            previous = self.points[i - 1]
            point = self.points[i]

            # Won't compute max_speed for first and last because of common GPS
            # recording errors, and because smoothing don't work well for those
            # points:
            first_or_last = i in [0, 1, len(self.points) - 1]
            if point.time and previous.time:
                timedelta = point.time - previous.time

                if point.elevation and previous.elevation:
                    distance = point.distance_3d(previous)
                else:
                    distance = point.distance_2d(previous)

                seconds = timedelta.seconds
                speed = 0
                if seconds > 0:
                    speed = (distance / 1000.) / (timedelta.seconds / 60. ** 2)

                #print speed, stopped_speed_treshold
                if speed <= stopped_speed_treshold:
                    stopped_time += timedelta.seconds
                    stopped_distance += distance
                else:
                    moving_time += timedelta.seconds
                    moving_distance += distance

                    if distance and moving_time:
                        speed = distance / timedelta.seconds
                        if speed > max_speed and not first_or_last:
                            max_speed = speed
        return MovingData(moving_time, stopped_time, moving_distance, stopped_distance, max_speed)
	
    def get_time_bounds(self):
        start_time = None
        end_time = None

        for point in self.points:
            if point.time:
                if not start_time:
                    start_time = point.time
                if point.time:
                    end_time = point.time

        return TimeBounds(start_time, end_time)

    def get_bounds(self):
        min_lat = None
        max_lat = None
        min_lon = None
        max_lon = None

        for point in self.points:
            if min_lat == None or point.latitude < min_lat:
                min_lat = point.latitude
            if max_lat == None or point.latitude > max_lat:
                max_lat = point.latitude
            if min_lon == None or point.longitude < min_lon:
                min_lon = point.longitude
            if max_lon == None or point.longitude > max_lon:
                max_lon = point.longitude

        return Bounds(min_lat, max_lat, min_lon, max_lon)

    def get_speed(self, point_no):
        """ Get speed at that point. Point may be a GPXTrackPoint instance or integer (point index) """

        point = self.points[point_no]

        previous_point = None
        next_point = None

        if 0 < point_no and point_no < len(self.points):
            previous_point = self.points[point_no - 1]
        if 0 < point_no and point_no < len(self.points) - 1:
            next_point = self.points[point_no + 1]

        #mod_logging.debug('previous: %s' % previous_point)
        #mod_logging.debug('next: %s' % next_point)

        speed_1 = point.speed(previous_point)
        speed_2 = point.speed(next_point)

        if speed_1:
            speed_1 = abs(speed_1)
        if speed_2:
            speed_2 = abs(speed_2)

        if speed_1 and speed_2:
            return (speed_1 + speed_2) / 2.

        if speed_1:
            return speed_1

        return speed_2

    def add_elevation(self, delta):

        mod_logging.debug('delta = %s' % delta)

        if not delta:
            return

        for track_point in self.points:
            track_point.elevation += delta

    def get_duration(self):
        """ Duration in seconds """
        if not self.points:
            return 0

        # Search for start:
        first = self.points[0]
        if not first.time:
            first = self.points[1]

        last = self.points[-1]
        if not last.time:
            last = self.points[-2]

        if not last.time or not first.time:
            mod_logging.debug('Can\'t find time')
            return None

        if last.time < first.time:
            mod_logging.debug('Not enough time data')
            return None

        return (last.time - first.time).seconds

    def get_uphill_downhill(self):
        """ 
        Returns (uphill, downhill). If elevation for some points is not found 
        those are simply ignored.
        """
        if not self.points:
            return UphillDownhill(0, 0)

        uphill = 0
        downhill = 0

        current_elevation = None
        for track_point in self.points:
            if not current_elevation:
                current_elevation = track_point.elevation

            if track_point.elevation and current_elevation:
                if current_elevation > track_point.elevation:
                    downhill += current_elevation - track_point.elevation
                else:
                    uphill += track_point.elevation - current_elevation

            current_elevation = track_point.elevation

        return UphillDownhill(uphill, downhill)

    def get_elevation_extremes(self):
        """ return (min_elevation, max_elevation) """

        if not self.points:
            return MinimumMaximum(0.0, 0.0)

        elevations = [location.elevation for location in self.points]

        return MinimumMaximum(max(elevations), min(elevations))

    def get_location_at(self, time):
        """ 
        Gets approx. location at given time. Note that, at the moment this method returns
        an instance of GPXTrackPoints in the future -- this may be a mod_geo.Location instance
        with approximated latitude, longitude and elevation!
        """
        if not self.points:
            return None

        if not time:
            return None

        first_time = self.points[0].time
        last_time = self.points[-1].time

        if not first_time and not last_time:
            mod_logging.debug('No times for track segment')
            return None

        if time < first_time or time > last_time:
            mod_logging.debug('Not in track (search for:%s, start:%s, end:%s)' % (time, first_time, last_time))
            return None

        for i in range(len(self.points)):
            point = self.points[i]
            if point.time and time < point.time:
                # TODO: If between two points -- approx position!
                # return mod_geo.Location(point.latitude, point.longitude)
                return point

    def to_xml(self, version=None):
        content = ''
        for track_point in self.points:
            content += track_point.to_xml(version)
        return mod_utils.to_xml('trkseg', content=content)

    def get_nearest_location(self, location):
        """ Return the (location, track_point_no) on this track segment """
        if not self.points:
            return (None, None)

        result = None
        current_distance = None
        result_track_point_no = None
        for i in range(len(self.points)):
            track_point = self.points[i]
            if not result:
                result = track_point
            else:
                distance = track_point.distance_2d(location)
                #print current_distance, distance
                if not current_distance or distance < current_distance:
                    current_distance = distance
                    result = track_point
                    result_track_point_no = i

        return (result, result_track_point_no)

    def smooth(self, vertical=True, horizontal=False, remove_extreemes=False):
        """ "Smooths" the elevation graph. Can be called multiple times. """
        if len(self.points) <= 3:
            return

        elevations = []
        latitudes = []
        longitudes = []

        for point in self.points:
            elevations.append(point.elevation)
            latitudes.append(point.latitude)
            longitudes.append(point.longitude)

        remove_elevation_extreemes_treshold = 1000

        avg_distance = 0
        avg_elevation_delta = 1
        if remove_extreemes:
            # compute the average distance between two points:
            distances = []
            elevations_delta = []
            for i in range(len(self.points))[1 :]:
                distances.append(self.points[i].distance_2d(self.points[i - 1]))
                elevation_1 = self.points[i].elevation
                elevation_2 = self.points[i - 1].elevation
                if elevation_1 != None and elevation_2 != None:
                    elevations_delta.append(abs(elevation_1 - elevation_2))
            if distances:
                avg_distance = 1.0 * sum(distances) / len(distances)
            if elevations_delta:
                avg_elevation_delta = 1.0 * sum(elevations_delta) / len(elevations_delta)

        # If The point moved more than this number * the average distance between two
        # points -- then is a candidate for deletion:
        # TODO: Make this a method parameter
        remove_2d_extreemes_treshold = 1.75 * avg_distance
        remove_elevation_extreemes_treshold = avg_elevation_delta * 5 # TODO: Param

        new_track_points = [self.points[0]]

        for i in range(len(self.points))[1 : -1]:
            new_point = None
            point_removed = False
            if vertical and elevations[i - 1] and elevations[i] and elevations[i + 1]:
                old_elevation = self.points[i].elevation
                new_elevation = SMOOTHING_RATIO[0] * elevations[i - 1] + \
                        SMOOTHING_RATIO[1] * elevations[i] + \
                        SMOOTHING_RATIO[2] * elevations[i + 1]

                if not remove_extreemes:
                    self.points[i].elevation = new_elevation

                if remove_extreemes:
                    # The point must be enough distant to *both* neighbours:
                    d1 = abs(old_elevation - elevations[i - 1])
                    d2 = abs(old_elevation - elevations[i + 1])
                    #print d1, d2, remove_2d_extreemes_treshold

                    # TODO: Remove extreemes treshold is meant only for 2D, elevation must be
                    # computed in different way!
                    if min(d1, d2) < remove_elevation_extreemes_treshold and abs(old_elevation - new_elevation) < remove_2d_extreemes_treshold:
                        new_point = self.points[i]
                    else:
                        #print 'removed elevation'
                        point_removed = True
                else:
                    new_point = self.points[i]

            if horizontal:
                old_latitude = self.points[i].latitude
                new_latitude = SMOOTHING_RATIO[0] * latitudes[i - 1] + \
                        SMOOTHING_RATIO[1] * latitudes[i] + \
                        SMOOTHING_RATIO[2] * latitudes[i + 1]
                old_longitude = self.points[i].longitude
                new_longitude = SMOOTHING_RATIO[0] * longitudes[i - 1] + \
                        SMOOTHING_RATIO[1] * longitudes[i] + \
                        SMOOTHING_RATIO[2] * longitudes[i + 1]
				
                if not remove_extreemes:
                    self.points[i].latitude = new_latitude
                    self.points[i].longitude = new_longitude

                # TODO: This is not ideal.. Because if there are points A, B and C on the same
                # line but B is very close to C... This would remove B (and possibly) A even though
                # it is not an extreeme. This is the reason for this algorithm:
                d1 = mod_geo.distance(latitudes[i - 1], longitudes[i - 1], None, latitudes[i], longitudes[i], None)
                d2 = mod_geo.distance(latitudes[i + 1], longitudes[i + 1], None, latitudes[i], longitudes[i], None)
                d = mod_geo.distance(latitudes[i - 1], longitudes[i - 1], None, latitudes[i + 1], longitudes[i + 1], None)

                #print d1, d2, d, remove_extreemes

                if d1 + d2 > d * 1.5 and remove_extreemes:
                    d = mod_geo.distance(old_latitude, old_longitude, None, new_latitude, new_longitude, None)
                    #print "d, treshold = ", d, remove_2d_extreemes_treshold
                    if d < remove_2d_extreemes_treshold:
                        new_point = self.points[i]
                    else:
                        #print 'removed 2d'
                        point_removed = True
                else:
                    new_point = self.points[i]

            if new_point and not point_removed:
                new_track_points.append(new_point)

        new_track_points.append(self.points[- 1])

        #print 'len=', len(new_track_points)

        self.points = new_track_points

    def has_times(self):
        """ 
        Returns if points in this segment contains timestamps.

        At least the first, last points and 75% of others must have times fot this 
        method to return true.
        """
        if not self.points:
            return True
            # ... or otherwise one empty track segment would change the entire 
            # track's "has_times" status!

        has_first = self.points[0]
        has_last = self.points[-1]

        found = 0
        for track_point in self.points:
            if track_point.time:
                found += 1

        found = float(found) / float(len(self.points))

        return has_first and found > .75 and has_last

    def __hash__(self):
        return mod_utils.hash_object(self, 'points')

    def clone(self):
        return mod_copy.deepcopy(self)

class GPX:
    time = None
    name = None
    description = None
    author = None
    email = None
    url = None
    urlname = None
    keywords = None

    waypoints = []
    routes = []
    tracks = []

    min_latitude = None
    max_latitude = None
    min_longitude = None
    max_longitude = None

    def __init__(self, waypoints=None, routes=None, tracks=None):
        self.time = None

        if waypoints: self.waypoints = waypoints
        else: self.waypoints = []

        if routes: self.routes = routes
        else: self.routes = []

        if tracks: self.tracks = tracks
        else: self.tracks = []

        self.name = None
        self.description = None
        self.author = None
        self.email = None
        self.url = None
        self.urlname = None
        self.time = None
        self.keywords = None

        self.min_latitude = None
        self.max_latitude = None
        self.min_longitude = None
        self.max_longitude = None

    def remove_time(self):
        """ Will remove time metadata. """
        for track in self.tracks:
            track.remove_time()

    def remove_elevation(self, tracks=True, routes=False, waypoints=False):
        """ Will remove elevation metadata. """
        if tracks:
            for track in self.tracks:
                track.remove_elevation()
        if routes:
            for route in self.routes:
                route.remove_elevation()
        if waypoints:
            for waypoint in self.waypoints:
                waypoint.remove_elevation()

    def get_time_bounds(self):
        """
        Returns the first and last found time in the track. 
        """
        start_time = None
        end_time = None

        for track in self.tracks:
            track_start_time, track_end_time = track.get_time_bounds()
            if not start_time:
                start_time = track_start_time
            if track_end_time:
                end_time = track_end_time

        return TimeBounds(start_time, end_time)

    def get_bounds(self):
        """
        Get bounds of of this track. Note this method *computes* the bounds i.e. the result may be different
        than the min_latitude, max_latitude, min_longitude and max_longitude properties of this object.
        """
        min_lat = None
        max_lat = None
        min_lon = None
        max_lon = None
        for track in self.tracks:
            bounds = track.get_bounds()

            if not mod_utils.is_numeric(min_lat) or bounds.min_latitude < min_lat:
                min_lat = bounds.min_latitude
            if not mod_utils.is_numeric(max_lat) or bounds.max_latitude > max_lat:
                max_lat = bounds.max_latitude
            if not mod_utils.is_numeric(min_lon) or bounds.min_longitude < min_lon:
                min_lon = bounds.min_longitude
            if not mod_utils.is_numeric(max_lon) or bounds.max_longitude > max_lon:
                max_lon = bounds.max_longitude

        return Bounds(min_lat, max_lat, min_lon, max_lon)
	
    def refresh_bounds(self):
        """
        Compute bounds and reload min_latitude, max_latitude, min_longitude and max_longitude properties
        of this object
        """

        bounds = self.get_bounds()

        self.min_latitude = bounds.min_latitude
        self.max_latitude = bounds.max_latitude
        self.min_longitude = bounds.min_longitude
        self.max_longitude = bounds.max_longitude

    def smooth(self, vertical=True, horizontal=False, remove_extreemes=False):
        """ See GPXTrackSegment.smooth(...) """
        for track in self.tracks:
            track.smooth(vertical=vertical, horizontal=horizontal, remove_extreemes=remove_extreemes)

    def remove_empty(self):
        """ Removes segments, routes """

        routes = []

        for route in self.routes:
            if len(route.points) > 0:
                routes.append(route)

        self.routes = routes

        for track in self.tracks:
            track.remove_empty()

    def get_moving_data(self, stopped_speed_treshold=None):
        """
        Return a tuple of (moving_time, stopped_time, moving_distance, stopped_distance, max_speed)
        that may be used for detecting the time stopped, and max speed. Not that those values are not
        absolutely true, because the "stopped" or "moving" informations aren't saved in the track.

        Because of errors in the GPS recording, it may be good to calculate them on a reduced and
        smoothed version of the track. Something like this:

        cloned_gpx = gpx.clone()
        cloned_gpx.reduce_points(2000, min_distance=10)
        cloned_gpx.smooth(vertical=True, horizontal=True)
        cloned_gpx.smooth(vertical=True, horizontal=False)
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed_ms = cloned_gpx.get_moving_data
        max_speed_kmh = max_speed_ms * 60. ** 2 / 1000.

        Do experiment with your own variatins before you get the values you expect.

        Max speed is in m/s. 
        """
        moving_time = 0.
        stopped_time = 0.

        moving_distance = 0.
        stopped_distance = 0.

        max_speed = 0.

        for track in self.tracks:
            track_moving_time, track_stopped_time, track_moving_distance, track_stopped_distance, track_max_speed = track.get_moving_data(stopped_speed_treshold)
            moving_time += track_moving_time
            stopped_time += track_stopped_time
            moving_distance += track_moving_distance
            stopped_distance += track_stopped_distance

            if track_max_speed > max_speed:
                max_speed = track_max_speed

        return MovingData(moving_time, stopped_time, moving_distance, stopped_distance, max_speed)

    def reduce_points(self, max_points_no, min_distance=None):
        """
        Reduce this track to the desired number of points
        max_points = The maximum number of points after the reduction
        min_distance = The minimum distance between two points
        """

        points_no = list(self.walk())
        if not max_points_no or points_no <= max_points_no:
            return

        length = self.length_3d()

        if not min_distance:
            min_distance = mod_math.ceil(length / float(max_points_no))
            if not min_distance or min_distance < 0:
                min_distance = 100

        for track in self.tracks:
            for track_segment in track.segments:
                reduced_points = []
                previous_point = None
                length = len(track_segment.points)
                for i in range(length):
                    point = track_segment.points[i]
                    if i == 0:
                        # Leave first point:
                        reduced_points.append(point)
                        previous_point = point
                    elif previous_point:
                        distance = previous_point.distance_3d(point)
                        if distance >= min_distance:
                            reduced_points.append(point)
                            previous_point = point

                track_segment.points = reduced_points

        # TODO
        mod_logging.debug('Track reduced to %s points' % self.get_track_points_no())

    def split(self, track_no, track_segment_no, track_point_no):
        track = self.tracks[track_no]

        track.split(track_segment_no=track_segment_no, track_point_no=track_point_no)

    def length_2d(self):
        result = 0
        for track in self.tracks:
            length = track.length_2d()
            if length or length == 0:
                result += length
        return result

    def length_3d(self):
        result = 0
        for track in self.tracks:
            length = track.length_3d()
            if length or length == 0:
                result += length
        return result

    def walk(self, only_points=False):
        """ Use this to iterate through points """
        for track_no, track in enumerate(self.tracks):
            for segment_no, segment in enumerate(track.segments):
                for point_no, point in enumerate(segment.points):
                    if only_points:
                        yield point
                    else:
                        yield point, track_no, segment_no, point_no

    def get_track_points_no(self):
        """ Number of track points, *without* route and waypoints """
        result = 0

        for track in self.tracks:
            for segment in track.segments:
                result += len(segment.points)

        return result

    def get_duration(self):
        """ Note returns None if one of track segments hasn't time data """
        if not self.tracks:
            return 0

        result = 0
        for track in self.tracks:
            duration = track.get_duration()
            if duration or duration == 0:
                result += duration
            elif duration == None:
                return None

        return result

    def get_uphill_downhill(self):
        if not self.tracks:
            return UphillDownhill(0, 0)

        uphill = 0
        downhill = 0

        for track in self.tracks:
            current_uphill, current_downhill = track.get_uphill_downhill()

            uphill += current_uphill
            downhill += current_downhill

        return UphillDownhill(uphill, downhill)

    def get_location_at(self, time):
        """ 
        Same as GPXTrackSegment.get_location_at(time)
        """
        result = []
        for track in self.tracks:
            locations = track.get_location_at(time)
            for location in locations:
                result.append(location)

        return result

    def get_elevation_extremes(self):
        if not self.tracks:
            return MinimumMaximum(0., 0.)

        elevations = []

        for track in self.tracks:
            (_min, _max) = track.get_elevation_extremes()
            elevations.append(_min)
            elevations.append(_max)

        return MinimumMaximum(min(elevations), max(elevations))

    def get_points_data(self, distance_2d=False):
        """
        Returns a list of tuples containing the actual point, its distance from the start,
        track_no, segment_no, and segment_point_no
        """
        distance_from_start = 0
        previous_point = None

        # (point, distance_from_start) pairs:
        points = []

        for track_no in range(len(self.tracks)):
            track = self.tracks[track_no]
            for segment_no in range(len(track.segments)):
                segment = track.segments[segment_no]
                for point_no in range(len(segment.points)):
                    point = segment.points[point_no]
                    if previous_point and point_no > 0:
                        if distance_2d:
                            distance = point.distance_2d(previous_point)
                        else:
                            distance = point.distance_3d(previous_point)

                        distance_from_start += distance

                    points.append(PointData(point, distance_from_start, track_no, segment_no, point_no ))

                    previous_point = point

        return points

    def get_nearest_locations(self, location, treshold_distance=0.01):
        """
        Returns a list of locations of elements like
        consisting of points where the location may be on the track

        treshold_distance is the the minimum distance from the track
        so that the point *may* be counted as to be "on the track".
        For example 0.01 means 1% of the track distance.
        """

        assert location
        assert treshold_distance

        result = []
		
        points = self.get_points_data()

        if not points:
            return ()

        distance = points[- 1][1]

        treshold = distance * treshold_distance

        min_distance_candidate = None
        distance_from_start_candidate = None
        track_no_candidate = None
        segment_no_candidate = None
        point_no_candidate = None

        for point, distance_from_start, track_no, segment_no, point_no in points:
            distance = location.distance_3d(point)
            if distance < treshold:
                if min_distance_candidate == None or distance < min_distance_candidate:
                    min_distance_candidate = distance
                    distance_from_start_candidate = distance_from_start
                    track_no_candidate = track_no
                    segment_no_candidate = segment_no
                    point_no_candidate = point_no
            else:
                if distance_from_start_candidate != None:
                    result.append((distance_from_start_candidate, track_no_candidate, segment_no_candidate, point_no_candidate))
                min_distance_candidate = None
                distance_from_start_candidate = None
                track_no_candidate = None
                segment_no_candidate = None
                point_no_candidate = None

        if distance_from_start_candidate != None:
            result.append(NearestLocationData(distance_from_start_candidate, track_no_candidate, segment_no_candidate, point_no_candidate))

        return result

    def get_nearest_location(self, location):
        """ Returns (location, track_no, track_segment_no, track_point_no) for the
        nearest location on map """
        if not self.tracks:
            return None

        result = None
        distance = None
        result_track_no = None
        result_segment_no = None
        result_point_no = None
        for i in range(len(self.tracks)):
            track = self.tracks[i]
            nearest_location, track_segment_no, track_point_no = track.get_nearest_location(location)
            nearest_location_distance = None
            if nearest_location:
                nearest_location_distance = nearest_location.distance_2d(location)
            if not distance or nearest_location_distance < distance:
                result = nearest_location
                distance = nearest_location_distance
                result_track_no = i
                result_segment_no = track_segment_no
                result_point_no = track_point_no

        return NearestLocationData(result, result_track_no, result_segment_no, result_point_no)

    def add_elevation(self, delta):
        for track in self.tracks:
            track.add_elevation(delta)

    def move(self, latitude_diff, longitude_diff):
        for route in self.routes:
            route.move(latitude_diff, longitude_diff)

        for waypoint in self.waypoints:
            waypoint.move(latitude_diff, longitude_diff)

        for track in self.tracks:
            track.move(latitude_diff, longitude_diff)

    def to_xml(self):

        # TODO: Implement other versions
        version = '1.0'

        content = ''
        if self.name:
            content += mod_utils.to_xml('name', content=self.name, default=' ', escape=True)
        if self.description:
            content += mod_utils.to_xml('desc', content=self.description, default=' ', escape=True)
        if self.author:
            content += mod_utils.to_xml('author', content=self.author, default=' ', escape=True)
        if self.email:
            content += mod_utils.to_xml('email', content=self.email, escape=True)
        if self.url:
            content += mod_utils.to_xml('url', content=self.url, escape=True)
        if self.urlname:
            content += mod_utils.to_xml('urlname', content=self.urlname, escape=True)
        if self.time:
            content += mod_utils.to_xml('time', content=self.time.strftime(DATE_FORMAT))
        if self.keywords:
            content += mod_utils.to_xml('keywords', content=self.keywords, default=' ', escape=True)

        # TODO: bounds

        for waypoint in self.waypoints:
            content += waypoint.to_xml(version)

        for route in self.routes:
            content += route.to_xml(version)

        for track in self.tracks:
            content += track.to_xml(version)

        xml_attributes = {
                'version': '1.0',
                'creator': 'gpx.py -- https://github.com/tkrajina/gpxpy',
                'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xmlns': 'http://www.topografix.com/GPX/1/0',
                'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd',
       }

        return '<?xml version="1.0" encoding="UTF-8"?>\n' + mod_utils.to_xml('gpx', attributes=xml_attributes, content=content).strip()

    def smooth(self, vertical=True, horizontal=False, remove_extreemes=False):
        for track in self.tracks:
            track.smooth(vertical, horizontal, remove_extreemes)

    def has_times(self):
        """ See GPXTrackSegment.has_times() """
        if not self.tracks:
            return None

        result = True
        for track in self.tracks:
            result = result and track.has_times()

        return result

    def __hash__(self):
        return mod_utils.hash_object(self, 'time', 'name', 'description', 'author', 'email', 'url', 'urlname', 'keywords', 'waypoints', 'routes', 'tracks', 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude') 

    def clone(self):
        return mod_copy.deepcopy(self)

