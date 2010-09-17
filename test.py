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

		self.assertTrue( len( gpx.waypoints ) > 0 )
		self.assertTrue( len( gpx2.waypoints ) > 0 )
		self.assertTrue( len( gpx.waypoints ) == len( gpx2.waypoints ) )
		for i in range( len( gpx.waypoints ) ):
			wpt1 = gpx.waypoints[ i ]
			wpt2 = gpx.waypoints[ i ]
			self.assertTrue( wpt1.name )
			self.assertTrue( wpt1.description )
			self.assertTrue( wpt1.comment )
			self.assertTrue( wpt1.symbol )
			self.assertTrue( wpt1.name == wpt2.name )
			self.assertTrue( wpt1.description == wpt2.description )
			self.assertTrue( wpt1.comment == wpt2.comment )
			self.assertTrue( wpt1.symbol == wpt2.symbol )

if __name__ == '__main__':
	unittest.main()
