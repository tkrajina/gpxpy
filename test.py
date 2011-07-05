# -*- coding: utf-8 -*-

import unittest

import gpxpy.gpx as mod_gpx
import gpxpy.parser as mod_parser
import time as mod_time

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

		location = mod_gpx.Location( 45.451058791, 14.027903696 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( location ) < 0.001 )
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = mod_gpx.Location( 1, 1 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = mod_gpx.Location( 50, 50 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
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

		before = len( track.track_segments )
		track.split( 1000, 10 )
		after = len( track.track_segments )

		self.assertTrue( before == after )

	def test_split( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 1 ]

		track_points_no = track.get_points_no()

		before = len( track.track_segments )
		track.split( 0, 10 )
		after = len( track.track_segments )

		self.assertTrue( before + 1 == after )
		print 'Points in first (splitted) part:', len( track.track_segments[ 0 ].track_points )

		# From 0 to 10th point == 11 points:
		self.assertTrue( len( track.track_segments[ 0 ].track_points ) == 11 )
		self.assertTrue( len( track.track_segments[ 0 ].track_points ) + len( track.track_segments[ 1 ].track_points ) == track_points_no )

		# Now split the second track
		track.split( 1, 20 )
		self.assertTrue( len( track.track_segments[ 1 ].track_points ) == 21 )
		self.assertTrue( len( track.track_segments[ 0 ].track_points ) + len( track.track_segments[ 1 ].track_points ) + len( track.track_segments[ 2 ].track_points ) == track_points_no )

	def test_split_and_join( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 1 ]

		original_track = track.clone()

		track.split( 0, 10 )
		track.split( 1, 20 )

		self.assertTrue( len( track.track_segments ) == 3 )
		track.join( 1 )
		self.assertTrue( len( track.track_segments ) == 2 )
		track.join( 0 )
		self.assertTrue( len( track.track_segments ) == 1 )

		# Check that this splitted and joined track is the same as the original one:
		self.assertTrue( equals( track, original_track ) )

	def test_remove_point_from_segment( self ):
		f = open( 'test_files/cerknicko-jezero.gpx' )
		parser = mod_parser.GPXParser( f )
		gpx = parser.parse()
		f.close()

		track = gpx.tracks[ 1 ]
		segment = track.track_segments[ 0 ]
		original_segment = segment.clone()

		segment.remove_point( 3 )
		print segment.track_points[ 0 ]
		print original_segment.track_points[ 0 ]
		self.assertTrue( equals( segment.track_points[ 0 ], original_segment.track_points[ 0 ] ) )
		self.assertTrue( equals( segment.track_points[ 1 ], original_segment.track_points[ 1 ] ) )
		self.assertTrue( equals( segment.track_points[ 2 ], original_segment.track_points[ 2 ] ) )
		# ...but:
		self.assertTrue( equals( segment.track_points[ 3 ], original_segment.track_points[ 4 ] ) )

		self.assertTrue( len( segment.track_points ) + 1 == len( original_segment.track_points ) )

	def test_distance( self ):
		distance = mod_gpx.distance( 48.56806,21.43467, None, 48.599214,21.430878, None )
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

if __name__ == '__main__':
	unittest.main()
