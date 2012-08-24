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

import math as mod_math
import utils as mod_utils

# Generic geo related function and class(es)

# One degree in meters:
ONE_DEGREE = 1000. * 10000.8 / 90.

def length(locations=[], _3d=None):
    if not locations:
        return 0
    length = 0
    for i in range(len(locations)):
        if i > 0:
            previous_location = locations[i - 1]
            location = locations[i]

            if _3d:
                d = location.distance_3d(previous_location)
            else:
                d = location.distance_2d(previous_location)
            if d != 0 and not d:
                pass
            else:
                length += d
    return length

def length_2d(locations=[]):
    """ 2-dimensional length of locations (only latitude and longitude, no elevation """
    return length(locations, False)

def length_3d(locations=[]):
    """ 3-dimensional length of locations (is uses latitude, longitude and elevation). """
    return length(locations, True)

def distance(latitude_1, longitude_1, elevation_1, latitude_2, longitude_2, elevation_2):
    """ Distance between two points. If elevation == None compute a 2d distance """

    coef = mod_math.cos(latitude_1 / 180. * mod_math.pi)
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    distance_2d = mod_math.sqrt(x * x + y * y) * ONE_DEGREE

    if elevation_1 == None or elevation_2 == None or elevation_1 == elevation_2:
        return distance_2d

    return mod_math.sqrt(distance_2d ** 2 + (elevation_1 - elevation_2) ** 2)

def elevation_angle(location1, location2, radians=False):
    """ Uphill/downhill angle between two locations. """
    if location1.elevation == None or location2.elevation == None:
        return None

    b = float(location2.elevation - location1.elevation)
    a = location2.distance_2d(location1)

    if a == 0:
        return 0

    angle = mod_math.atan(b / a)

    if radians:
        return angle

    return 180 * angle / mod_math.pi

class Location:
    """ Generic geographical location """

    latitude = None
    longitude = None
    elevation = None

    def __init__(self, latitude, longitude, elevation=None):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation

    def has_elevation(self):
        return self.elevation or self.elevation == 0

    def remove_elevation(self):
        self.elevation = None

    def distance_2d(self, location):
        if not location:
            return None

        return distance(self.latitude, self.longitude, None, location.latitude, location.longitude, None)

    def distance_3d(self, location):
        if not location:
            return None

        return distance(self.latitude, self.longitude, self.elevation, location.latitude, location.longitude, location.elevation)

    def elevation_angle(self, location, radians=False):
        return elevation_angle(self, location, radians)

    def move(self, latitude_diff, longitude_diff):
        self.latitude += latitude_diff
        self.longitude += longitude_diff
		
    def __str__(self):
        return '[loc:%s,%s@%s]' % (self.latitude, self.longitude, self.elevation)

    def __hash__(self):
                return mod_utils.hash_object(self, 'latitude', 'longitude', 'elevation') 


