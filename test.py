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

import unittest

import gpxpy.gpx as mod_gpx
import gpxpy.parser as mod_parser
import gpxpy.geo as mod_geo
import time as mod_time
import copy as mod_copy

def equals( object1, object2, ignore = None ):
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
	for attr in dir( object1 ):
		if not ignore or not attr in ignore:
			if not callable( getattr( object1, attr ) ) and not attr.startswith( '_' ):
				if not attr in attributes:
					attributes.append( attr )

	for attr in attributes:
		attr1 = getattr( object1, attr )
		attr2 = getattr( object2, attr )

		if attr1 == attr2:
			return True

		if not attr1 and not attr2:
			return True
		if not attr1 or not attr2:
			print 'Object differs in attribute %s (%s - %s)' % ( attr, attr1, attr2 )
			return False

		if not equals( attr1, attr2 ):
			print 'Object differs in attribute %s (%s - %s)' % ( attr, attr1, attr2 )
			return None

	return True

# TODO: Track segment speed in point test

class TestWaypoint( unittest.TestCase ):

	def _parse( self, file ):
		f = open( 'test_files/%s' % file )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		if not gpx:
			print 'Parser error: %s' % parser.get_error()

		return gpx
		
	def _reparse( self, gpx ):
		xml = gpx.to_xml()

		parser = mod_parser.GPXParser( xml )
		gpx = parser.parse()

		if not gpx:
			print 'Parser error while reparsing: %s' % parser.get_error()

		return gpx

	def test_waypoints_equality_after_reparse( self ):
		gpx = self._parse( 'cerknicko-jezero.gpx' )
		gpx2 = self._reparse( gpx )

		self.assertTrue( equals( gpx.waypoints, gpx2.waypoints ) )
		self.assertTrue( equals( gpx.routes, gpx2.routes ) )
		self.assertTrue( equals( gpx.tracks, gpx2.tracks ) )
		self.assertTrue( equals( gpx, gpx2 ) )

	def test_has_times_false( self ):
		gpx = self._parse( 'cerknicko-without-times.gpx' )
		self.assertFalse( gpx.has_times() )

	def test_has_times( self ):
		gpx = self._parse( 'korita-zbevnica.gpx' )
		self.assertTrue( len( gpx.tracks ) == 4 )
		# Empty -- True
		self.assertTrue( gpx.tracks[ 0 ].has_times() )
		# Not times ...
		self.assertTrue( not gpx.tracks[ 1 ].has_times() )

		# Times OK
		self.assertTrue( gpx.tracks[ 2 ].has_times() )
		self.assertTrue( gpx.tracks[ 3 ].has_times() )

	def test_unicode( self ):
		gpx = self._parse( 'unicode.gpx' )

		name = gpx.waypoints[ 0 ].name

		self.assertTrue( name.encode( 'utf-8' ) == 'šđčćž' )

	def test_nearest_location_1( self ):
		gpx = self._parse( 'korita-zbevnica.gpx' )

		location = mod_geo.Location( 45.451058791, 14.027903696 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].segments[ track_segment_no ].points[ track_point_no ]
		self.assertTrue( point.distance_2d( location ) < 0.001 )
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = mod_geo.Location( 1, 1 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].segments[ track_segment_no ].points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = mod_geo.Location( 50, 50 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].segments[ track_segment_no ].points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

	def test_long_timestamps( self ):
		# Check if timestamps in format: 1901-12-13T20:45:52.2073437Z work
		gpx = self._parse( 'Mojstrovka.gpx' )

		# %Y-%m-%dT%H:%M:%SZ'

	def test_reduce_gpx_file( self ):
		f = open( 'test_files/Mojstrovka.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		max_reduced_points_no = 200

		started = mod_time.time()
		gpx = parser.parse()
		points_original = len( gpx.get_points() )
		time_original = mod_time.time() - started

		gpx.reduce_points( max_reduced_points_no )

		points_reduced = len( gpx.get_points() )

		result = gpx.to_xml()
		result = result.encode( 'utf-8' )

		started = mod_time.time()
		parser = mod_parser.GPXParser( result )
		parser.parse()
		time_reduced = mod_time.time() - started

		print time_original
		print points_original

		print time_reduced
		print points_reduced

		self.assertTrue( time_reduced < time_original )
		self.assertTrue( points_reduced < points_original )
		self.assertTrue( points_reduced < max_reduced_points_no )

	def test_clone_and_smooth( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		original_2d = gpx.length_2d()
		original_3d = gpx.length_3d()

		cloned_gpx = gpx.clone()

		self.assertTrue( hash( gpx ) == hash( cloned_gpx ) )

		cloned_gpx.reduce_points( 2000, min_distance = 10 )
		cloned_gpx.smooth( vertical = True, horizontal = True )
		cloned_gpx.smooth( vertical = True, horizontal = False )

		print '2d:', gpx.length_2d()
		print '2d cloned and smoothed:', cloned_gpx.length_2d()

		print '3d:', gpx.length_3d()
		print '3d cloned and smoothed:', cloned_gpx.length_3d()

		self.assertTrue( gpx.length_3d() == original_3d )
		self.assertTrue( gpx.length_2d() == original_2d )

		self.assertTrue( gpx.length_3d() > cloned_gpx.length_3d() )
		self.assertTrue( gpx.length_2d() > cloned_gpx.length_2d() )
		
	def test_moving_stopped_times( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		print len( gpx.get_points() )

		#gpx.reduce_points( 1000, min_distance = 5 )

		print len( gpx.get_points() )

		length = gpx.length_3d()
		print 'Distance: %s' % length

		gpx.reduce_points( 2000, min_distance = 10 )
		gpx.smooth( vertical = True, horizontal = True )
		gpx.smooth( vertical = True, horizontal = False )

		moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx.get_moving_data( stopped_speed_treshold = 0.1 )
		print '-----'
		print 'Length: %s' % length
		print 'Moving time: %s (%smin)' % ( moving_time, moving_time / 60. )
		print 'Stopped time: %s (%smin)' % ( stopped_time, stopped_time / 60. )
		print 'Moving distance: %s' % moving_distance
		print 'Stopped distance: %s' % stopped_distance
		print 'Max speed: %sm/s' % max_speed
		print '-----'

		# TODO: More tests and checks
		self.assertTrue( moving_distance < length )
		print 'Dakle:', moving_distance, length
		self.assertTrue( moving_distance > 0.75 * length )
		self.assertTrue( stopped_distance < 0.1 * length )

	def test_split_on_impossible_index( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 0 ]

		before = len( track.segments )
		track.split( 1000, 10 )
		after = len( track.segments )

		self.assertTrue( before == after )

	def test_split( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 1 ]

		track_points_no = track.get_points_no()

		before = len( track.segments )
		track.split( 0, 10 )
		after = len( track.segments )

		self.assertTrue( before + 1 == after )
		print 'Points in first (splitted) part:', len( track.segments[ 0 ].points )

		# From 0 to 10th point == 11 points:
		self.assertTrue( len( track.segments[ 0 ].points ) == 11 )
		self.assertTrue( len( track.segments[ 0 ].points ) + len( track.segments[ 1 ].points ) == track_points_no )

		# Now split the second track
		track.split( 1, 20 )
		self.assertTrue( len( track.segments[ 1 ].points ) == 21 )
		self.assertTrue( len( track.segments[ 0 ].points ) + len( track.segments[ 1 ].points ) + len( track.segments[ 2 ].points ) == track_points_no )

	def test_split_and_join( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 1 ]

		original_track = track.clone()

		track.split( 0, 10 )
		track.split( 1, 20 )

		self.assertTrue( len( track.segments ) == 3 )
		track.join( 1 )
		self.assertTrue( len( track.segments ) == 2 )
		track.join( 0 )
		self.assertTrue( len( track.segments ) == 1 )

		# Check that this splitted and joined track is the same as the original one:
		self.assertTrue( equals( track, original_track ) )

	def test_remove_point_from_segment( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 1 ]
		segment = track.segments[ 0 ]
		original_segment = segment.clone()

		segment.remove_point( 3 )
		print segment.points[ 0 ]
		print original_segment.points[ 0 ]
		self.assertTrue( equals( segment.points[ 0 ], original_segment.points[ 0 ] ) )
		self.assertTrue( equals( segment.points[ 1 ], original_segment.points[ 1 ] ) )
		self.assertTrue( equals( segment.points[ 2 ], original_segment.points[ 2 ] ) )
		# ...but:
		self.assertTrue( equals( segment.points[ 3 ], original_segment.points[ 4 ] ) )

		self.assertTrue( len( segment.points ) + 1 == len( original_segment.points ) )

	def test_distance( self ):
		distance = mod_geo.distance( 48.56806,21.43467, None, 48.599214,21.430878, None )
		print distance
		self.assertTrue( distance > 3450 and distance < 3500 )

	def test_horizontal_smooth_remove_extreemes( self ):
		f = open( 'test_files/track-with-extreemes.gpx', 'r' )

		parser = mod_parser.GPXParser( f )

		gpx = parser.parse()

		points_before = len( gpx.get_points() )
		gpx.smooth( vertical = False, horizontal = True, remove_extreemes = True )
		points_after = len( gpx.get_points() )

		print points_before
		print points_after

		self.assertTrue( points_before - 2 == points_after )

	def test_vertical_smooth_remove_extreemes( self ):
		f = open( 'test_files/track-with-extreemes.gpx', 'r' )

		parser = mod_parser.GPXParser( f )

		gpx = parser.parse()

		points_before = len( gpx.get_points() )
		gpx.smooth( vertical = True, horizontal = False, remove_extreemes = True )
		points_after = len( gpx.get_points() )

		print points_before
		print points_after


		self.assertTrue( points_before - 1 == points_after )

	def test_horizontal_and_vertical_smooth_remove_extreemes( self ):
		f = open( 'test_files/track-with-extreemes.gpx', 'r' )

		parser = mod_parser.GPXParser( f )

		gpx = parser.parse()

		points_before = len( gpx.get_points() )
		gpx.smooth( vertical = True, horizontal = True, remove_extreemes = True )
		points_after = len( gpx.get_points() )

		print points_before
		print points_after

		self.assertTrue( points_before - 3 == points_after )

	def test_positions_on_track( self ):
		gpx = mod_gpx.GPX()
		track = mod_gpx.GPXTrack()
		gpx.tracks.append( track )
		segment = mod_gpx.GPXTrackSegment()
		track.segments.append( segment )

		location_to_find_on_track = None

		for i in range( 1000 ):
			latitude = 45 + i * 0.001
			longitude = 45 + i * 0.001
			elevation = 100 + i * 2
			point = mod_gpx.GPXTrackPoint( latitude = latitude, longitude = longitude, elevation = elevation )
			segment.points.append( point )

			if i == 500:
				location_to_find_on_track = mod_gpx.GPXWaypoint( latitude = latitude, longitude = longitude )

		result = gpx.get_nearest_locations( location_to_find_on_track )

		self.assertTrue( len( result ) == 1 )

	def test_positions_on_track_2( self ):
		gpx = mod_gpx.GPX()
		track = mod_gpx.GPXTrack()
		gpx.tracks.append( track )

		location_to_find_on_track = None

		# first segment:
		segment = mod_gpx.GPXTrackSegment()
		track.segments.append( segment )
		for i in range( 1000 ):
			latitude = 45 + i * 0.001
			longitude = 45 + i * 0.001
			elevation = 100 + i * 2
			point = mod_gpx.GPXTrackPoint( latitude = latitude, longitude = longitude, elevation = elevation )
			segment.points.append( point )

			if i == 500:
				location_to_find_on_track = mod_gpx.GPXWaypoint( latitude = latitude, longitude = longitude )

		# second segment
		segment = mod_gpx.GPXTrackSegment()
		track.segments.append( segment )
		for i in range( 1000 ):
			latitude = 45.0000001 + i * 0.001
			longitude = 45.0000001 + i * 0.001
			elevation = 100 + i * 2
			point = mod_gpx.GPXTrackPoint( latitude = latitude, longitude = longitude, elevation = elevation )
			segment.points.append( point )

		result = gpx.get_nearest_locations( location_to_find_on_track )

		print 'Found', result

		self.assertTrue( len( result ) == 2 )

	def test_hash_location( self ):
		location_1 = mod_geo.Location( latitude = 12, longitude = 13, elevation = 19 )
		location_2 = mod_geo.Location( latitude = 12, longitude = 13, elevation = 19 )

		self.assertTrue( hash( location_1 ) == hash( location_2 ) )

		location_2.elevation *= 2
		location_2.latitude *= 2
		location_2.longitude *= 2

		self.assertTrue( hash( location_1 ) != hash( location_2 ) )

		location_2.elevation /= 2
		location_2.latitude /= 2
		location_2.longitude /= 2

		self.assertTrue( hash( location_1 ) == hash( location_2 ) )

	def test_hash_gpx_track_point( self ):
		point_1 = mod_gpx.GPXTrackPoint( latitude = 12, longitude = 13, elevation = 19 )
		point_2 = mod_gpx.GPXTrackPoint( latitude = 12, longitude = 13, elevation = 19 )

		self.assertTrue( hash( point_1 ) == hash( point_2 ) )

		point_2.elevation *= 2
		point_2.latitude *= 2
		point_2.longitude *= 2

		self.assertTrue( hash( point_1 ) != hash( point_2 ) )

		point_2.elevation /= 2
		point_2.latitude /= 2
		point_2.longitude /= 2

		self.assertTrue( hash( point_1 ) == hash( point_2 ) )

	def test_hash_track( self ):
		gpx = mod_gpx.GPX()
		track = mod_gpx.GPXTrack()
		gpx.tracks.append( track )

		segment = mod_gpx.GPXTrackSegment()
		track.segments.append( segment )
		for i in range( 1000 ):
			latitude = 45 + i * 0.001
			longitude = 45 + i * 0.001
			elevation = 100 + i * 2.
			point = mod_gpx.GPXTrackPoint( latitude = latitude, longitude = longitude, elevation = elevation )
			segment.points.append( point )

		self.assertTrue( hash( gpx ) )
		self.assertTrue( len( gpx.tracks ) == 1 )
		self.assertTrue( len( gpx.tracks[ 0 ].segments ) == 1 )
		self.assertTrue( len( gpx.tracks[ 0 ].segments[ 0 ].points ) == 1000 )

		cloned_gpx = mod_copy.deepcopy( gpx )

		self.assertTrue( hash( gpx ) == hash( cloned_gpx ) )

		gpx.tracks[ 0 ].segments[ 0 ].points[ 17 ].elevation *= 2.
		self.assertTrue( hash( gpx ) != hash( cloned_gpx ) )

		gpx.tracks[ 0 ].segments[ 0 ].points[ 17 ].elevation /= 2.
		self.assertTrue( hash( gpx ) == hash( cloned_gpx ) )

		gpx.tracks[ 0 ].segments[ 0 ].points[ 17 ].latitude /= 2.
		self.assertTrue( hash( gpx ) != hash( cloned_gpx ) )

		gpx.tracks[ 0 ].segments[ 0 ].points[ 17 ].latitude *= 2.
		self.assertTrue( hash( gpx ) == hash( cloned_gpx ) )

		del gpx.tracks[ 0 ].segments[ 0 ].points[ 17 ]
		self.assertTrue( hash( gpx ) != hash( cloned_gpx ) )

	def test_bounds( self ):
		gpx = mod_gpx.GPX()

		track = mod_gpx.GPXTrack()

		segment_1 = mod_gpx.GPXTrackSegment()
		segment_1.points.append( mod_gpx.GPXTrackPoint( latitude = -12, longitude = 13 ) )
		segment_1.points.append( mod_gpx.GPXTrackPoint( latitude = -100, longitude = -5 ) )
		segment_1.points.append( mod_gpx.GPXTrackPoint( latitude = 100, longitude = -13 ) )
		track.segments.append( segment_1 )

		segment_2 = mod_gpx.GPXTrackSegment()
		segment_2.points.append( mod_gpx.GPXTrackPoint( latitude = -12, longitude = 100 ) )
		segment_2.points.append( mod_gpx.GPXTrackPoint( latitude = -10, longitude = -5 ) )
		segment_2.points.append( mod_gpx.GPXTrackPoint( latitude = 10, longitude = -100 ) )
		track.segments.append( segment_2 )

		gpx.tracks.append( track )

		bounds = gpx.get_bounds()

		self.assertEquals( bounds.min_latitude, -100 )
		self.assertEquals( bounds.max_latitude, 100 )
		self.assertEquals( bounds.min_longitude, -100 )
		self.assertEquals( bounds.max_longitude, 100 )

		# Test refresh bounds:

		gpx.refresh_bounds()
		self.assertEquals( gpx.min_latitude, -100 )
		self.assertEquals( gpx.max_latitude, 100 )
		self.assertEquals( gpx.min_longitude, -100 )
		self.assertEquals( gpx.max_longitude, 100 )

if __name__ == '__main__':
	unittest.main()
