# -*- coding: utf-8 -*-

import unittest

import gpxpy

class TestWaypoint( unittest.TestCase ):

	def __parse( self, file ):
		f = open( 'test_files/%s' % file )
		parser = gpxpy.GPXParser( f )
		gpx = parser.parse()
		f.close()

		if not gpx:
			print 'Parser error: %s' % parser.get_error()

		return gpx
		
	def __reparse( self, gpx ):
		xml = gpx.to_xml()

		parser = gpxpy.GPXParser( xml )
		gpx = parser.parse()

		if not gpx:
			print 'Parser error while reparsing: %s' % parser.get_error()

		return gpx

	def test_waypoints_equality_after_reparse( self ):
		gpx = self.__parse( 'cerknicko-jezero.gpx' )
		gpx2 = self.__reparse( gpx )

		self.assertTrue( gpx.waypoints == gpx2.waypoints )
		self.assertTrue( gpx.routes == gpx2.routes )
		self.assertTrue( gpx.tracks == gpx2.tracks )
		self.assertTrue( gpx == gpx2 )

	def test_has_times_false( self ):
		gpx = self.__parse( 'cerknicko-without-times.gpx' )
		self.assertFalse( gpx.has_times() )

	def test_has_times( self ):
		gpx = self.__parse( 'korita-zbevnica.gpx' )
		self.assertTrue( len( gpx.tracks ) == 4 )
		# Empty -- True
		self.assertTrue( gpx.tracks[ 0 ].has_times() )
		# Not times ...
		self.assertTrue( not gpx.tracks[ 1 ].has_times() )

		# Times OK
		self.assertTrue( gpx.tracks[ 2 ].has_times() )
		self.assertTrue( gpx.tracks[ 3 ].has_times() )

	def test_unicode( self ):
		gpx = self.__parse( 'unicode.gpx' )

		name = gpx.waypoints[ 0 ].name

		self.assertTrue( name.encode( 'utf-8' ) == 'šđčćž' )

	def test_nearest_location_1( self ):
		gpx = self.__parse( 'korita-zbevnica.gpx' )

		location = gpxpy.Location( 45.451058791, 14.027903696 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( location ) < 0.001 )
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = gpxpy.Location( 1, 1 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

		location = gpxpy.Location( 50, 50 )
		nearest_location, track_no, track_segment_no, track_point_no = gpx.get_nearest_location( location )
		point = gpx.tracks[ track_no ].track_segments[ track_segment_no ].track_points[ track_point_no ]
		self.assertTrue( point.distance_2d( nearest_location ) < 0.001 )

if __name__ == '__main__':
	unittest.main()
