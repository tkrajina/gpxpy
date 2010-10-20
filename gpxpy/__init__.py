# -*- coding: utf-8 -*-

import logging
import math
import datetime

from xml.dom import minidom

import utils

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def _parse_time( str ):
	if not str:
		return None
	return datetime.datetime.strptime( str, DATE_FORMAT )

def _length( locations = [], _3d = None ):
	if not locations:
		return 0
	length = 0
	for i in range( len( locations ) ):
		if i > 0:
			previous_location = locations[ i - 1 ]
			location = locations[ i ]

			if _3d:
				d = location.distance_3d( previous_location )
			else:
				d = location.distance_2d( previous_location )
			if d != 0 and not d:
				#print( 'došli do null %s <-> %s _3d:%s' % ( location, previous_location, _3d ) )
				pass
			else:
				length += d
				#print '#%s length (%s) -> %s' % ( i, _3d, length )
	return length

def length_3d( locations = [] ):
	return _length( locations, True )

def length_2d( locations = [] ):
	return _length( locations, None )

class Location:

	# One degree in meters:
	ONE_DEGREE = 1000. * 10000.8 / 90.

	latitude = None
	longitude = None
	elevation = None

	def __init__( self, latitude, longitude, elevation = None ):
		self.latitude = latitude
		self.longitude = longitude
		self.elevation = elevation

	def has_elevation( self ):
		# TODO ?
		return self.elevation or self.elevation == 0

	def distance_2d( self, location ):
		if not location:
			return None

		coef = math.cos( self.latitude / 180. * math.pi )
		x = self.latitude - location.latitude
		y = ( self.longitude - location.longitude ) * coef

		return math.sqrt( x * x + y * y ) * self.ONE_DEGREE

	def distance_3d( self, location ):
		distance = self.distance_2d( location )

		if distance == 0:
			return 0

		if not distance or not location.has_elevation() or not self.has_elevation():
			return None

		h = location.elevation - self.elevation

		return math.sqrt( distance * distance + h * h )

	def __str__( self ):
		return '[loc:%s,%s@%s]' % ( self.latitude, self.longitude, self.elevation )

class GPXWaypoint( Location ):

	time = None
	name = None
	description = None
	symbol = None
	type = None
	comment = None

	def __init__( self, latitude, longitude, elevation = None, time = None, name = None, description = None, symbol = None, type = None, comment = None ):
		Location.__init__( self, latitude, longitude, elevation )

		self.time = time
		self.name = name
		self.description = description
		self.symbol = symbol
		self.type = type
		self.comment = comment

	def __str__( self ):
		return '[wpt{%s}:%s,%s@%s]' % ( self.name, self.latitude, self.longitude, self.elevation )

	def to_xml( self ):
		content = utils.to_xml( 'ele', content = self.elevation )
		if self.time:
			content += utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content += utils.to_xml( 'name', content = self.name, cdata = True )
		content += utils.to_xml( 'desc', content = self.description, cdata = True )
		content += utils.to_xml( 'sym', content = self.symbol, cdata = True )
		content += utils.to_xml( 'type', content = self.type, cdata = True )
		content += utils.to_xml( 'cmt', content = self.comment, cdata = True )

		return utils.to_xml( 'wpt', attributes = { 'lat': self.latitude, 'lon': self.longitude }, content = content )

	def __eq__( self, waypoint ):
		return utils.attributes_and_classes_equals( self, waypoint )

	def __ne__( self, waypoint ):
		return not self.__eq__( waypoint )

	def __hash__( self ):
		return id( self )

class GPXRoute:

	name = None
	description = None
	number = None

	route_points = []

	def __init__( self, name = None, description = None, number = None ):
		self.name = name
		self.description = description
		self.number = number

		self.route_points = []

	def length( self ):
		return length_2d( route_points )

	def to_xml( self ):
		content = utils.to_xml( 'name', content = self.name, cdata = True )
		content += utils.to_xml( 'desc', content = self.description, cdata = True )
		content += utils.to_xml( 'number', content = self.number )
		for route_point in self.route_points:
			content += route_point.to_xml()

		return utils.to_xml( 'rte', content = content )

	def __eq__( self, route ):
		return utils.attributes_and_classes_equals( self, route )

	def __ne__( self, route ):
		return not self.__eq__( route )

	def __hash__( self ):
		return id( self )

class GPXRoutePoint( Location ):

	time = None
	name = None
	description = None
	symbol = None
	type = None
	comment = None

	def __init__( self, latitude, longitude, elevation = None, time = None, name = None, description = None, symbol = None, type = None, comment = None ):
		Location.__init__( self, latitude, longitude, elevation )

		self.time = time
		self.name = name
		self.description = description
		self.symbol = symbol
		self.type = type
		self.comment = comment

	def __str__( self ):
		return '[rtept{%s}:%s,%s@%s]' % ( self.name, self.latitude, self.longitude, self.elevation )

	def to_xml( self ):
		content = utils.to_xml( 'ele', content = self.elevation )
		if self.time:
			content = utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content = utils.to_xml( 'name', content = self.name, cdata = True )
		content = utils.to_xml( 'cmt', content = self.comment, cdata = True )
		content = utils.to_xml( 'desc', content = self.description, cdata = True )
		content = utils.to_xml( 'sym', content = self.symbol, cdata = True )
		content = utils.to_xml( 'type', content = self.type, cdata = True )

		return utils.to_xml( 'rtept', attributes = { 'lat': self.latitude, 'lon': self.longitude }, content = content )

	def __eq__( self, location ):
		return utils.attributes_and_classes_equals( self, location )

	def __ne__( self, location ):
		return not self.__eq__( location )

	def __hash__( self ):
		return id( self )

class GPXTrackPoint( Location ):

	time = None
	symbol = None
	comment = None

	def __init__( self, latitude, longitude, elevation = None, time = None, symbol = None, comment = None ):
		Location.__init__( self, latitude, longitude, elevation )

		self.time = time
		self.symbol = symbol
		self.comment = comment

	def to_xml( self ):
		content = utils.to_xml( 'ele', content = self.elevation )
		if self.time:
			content += utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content += utils.to_xml( 'cmt', content = self.comment, cdata = True )
		content += utils.to_xml( 'sym', content = self.symbol, cdata = True )
		return utils.to_xml( 'trkpt', { 'lat': self.latitude, 'lon': self.longitude }, content = content )

	def __str__( self ):
		return '[trkpt:%s,%s@%s@%s]' % ( self.latitude, self.longitude, self.elevation, self.time )

	def __eq__( self, point ):
		return utils.attributes_and_classes_equals( self, point )

	def __ne__( self, point ):
		return not self.__eq__( point )

	def __hash__( self ):
		return id( self )

class GPXTrack:

	name = None
	description = None
	number = None

	track_segments = None

	def __init__( self, name = None, description = None, number = None ):
		self.name = name
		self.description = description
		self.number = number

		self.track_segments = []
	
	def length_2d( self ):
		length = 0
		for track_segment in self.track_segments:
			d = track_segment.length_2d()
			if d:
				length += d
		return length

	def get_points( self ):
		result = []

		for track_segment in self.track_segments:
			result += track_segment.get_points()

		return result

	def length_3d( self ):
		length = 0
		for track_segment in self.track_segments:
			d = track_segment.length_3d()
			if d:
				length += d
		return length

	def get_duration( self ):
		""" Note returns None if one of track segments hasn't time data """
		if not self.track_segments:
			return 0

		result = 0
		for track_segment in self.track_segments:
			duration = track_segment.get_duration()
			if duration or duration == 0:
				result += duration
			elif duration == None:
				return None

		return result

	def get_uphill_downhill( self ):
		if not self.track_segments:
			return ( 0, 0 )

		uphill = 0
		downhill = 0

		for track_segment in self.track_segments:
			current_uphill, current_downhill = track_segment.get_uphill_downhill()

			uphill += current_uphill
			downhill += current_downhill

		return ( uphill, downhill )

	def get_location_at( self, time ):
		""" 
		Get locations for this time. There may be more locations because of 
		time-overlapping track segments.
		"""
		result = []
		for track_segment in self.track_segments:
			location = track_segment.get_location_at( time )
			if location:
				result.append( location )

		return result

	def get_elevation_extremes( self ):
		if not self.track_segments:
			return ( 0, 0 )

		elevations = []

		for track_segment in self.track_segments:
			( _min, _max ) = track_segment.get_elevation_extremes()
			elevations.append( _min )
			elevations.append( _max )

		return ( min( elevations ), max( elevations ) )

	def to_xml( self ):
		content = utils.to_xml( 'name', content = self.name, cdata = True )
		content += utils.to_xml( 'desc', content = self.description, cdata = True )
		content += utils.to_xml( 'number', content = self.number )
		for track_segment in self.track_segments:
			content += track_segment.to_xml()

		return utils.to_xml( 'trk', content = content )

	def get_center( self ):
		""" "Average" location for this track """
		if not self.track_segments:
			return None
		sum_lat = 0
		sum_lon = 0
		n = 0
		for track_segment in self.track_segments:
			for point in track_segment.track_points:
				n += 1.
				sum_lat += point.latitude
				sum_lon += point.longitude

		if not n:
			return Location( float( 0 ), float( 0 ) )

		return Location( latitude = sum_lat / n, longitude = sum_lon / n )

	def get_points_no( self ):
		result = 0

		for track_segment in self.track_segments:
			result += track_segment.get_points_no()

		return result

	def smooth( self ):
		""" See: GPXTrackSegment.smooth() """
		for track_segment in self.track_segments:
			track_segment.smooth()

	def has_times( self ):
		""" See GPXTrackSegment.has_times() """
		if not self.track_segments:
			return None

		result = True
		for track_segment in self.track_segments:
			result = result and track_segment.has_times()

		return result

	def get_nearest_location( self, location ):
		""" Returns ( location, track_segment_no, track_point_no ) for nearest location on track """
		if not self.track_segments:
			return None

		result = None
		distance = None
		result_track_segment_no = None
		result_track_point_no = None
		for i in range( len( self.track_segments ) ):
			track_segment = self.track_segments[ i ]
			nearest_location, track_point_no = track_segment.get_nearest_location( location )
			nearest_location_distance = None
			if nearest_location:
				nearest_location_distance = nearest_location.distance_2d( location )
			if not distance or nearest_location_distance < distance:
				result = nearest_location
				distance = nearest_location_distance
				result_track_segment_no = i
				result_track_point_no = track_point_no

		return ( result, result_track_segment_no, result_track_point_no )

	def __eq__( self, track ):
		return utils.attributes_and_classes_equals( self, track )

	def __ne__( self, track ):
		return not self.__eq__( track )

	def __hash__( self ):
		return id( self )

class GPXTrackSegment:

	track_points = None

	def __init__( self ):
		self.track_points = []

	def length_2d( self ):
		return length_2d( self.track_points )

	def length_3d( self ):
		return length_3d( self.track_points )

	def get_points( self ):
		return self.track_points

	def get_duration_times( self, ignore_slower_than = None ):
		""" 
		Returns a pair of ( track_time, stopped_time ) where stopped time is
		counted for track points where the speed between them is slower than
		ignore_slower_than.
		"""
		# TODO
		pass

	def get_duration( self ):
		""" Duration in seconds """
		if not self.track_points:
			return 0

		# Search for start:
		first = self.track_points[ 0 ]
		if not first.time:
			first = self.track_points[ 1 ]

		last = self.track_points[ -1 ]
		if not last.time:
			last = self.track_points[ -2 ]

		if not last.time or not first.time:
			logging.debug( 'Can\'t find time' )
			return None

		if last.time < first.time:
			logging.debug( 'Not enough time data' )
			return None

		return ( last.time - first.time ).seconds

	def get_uphill_downhill( self ):
		""" 
		Returns ( uphill, downhill ). If elevation for some points is not found 
		those are simply ignored.
		"""
		if not self.track_points:
			return ( 0, 0 )

		uphill = 0
		downhill = 0

		current_elevation = None
		for track_point in self.track_points:
			if not current_elevation:
				current_elevation = track_point.elevation

			if track_point.elevation and current_elevation:
				if current_elevation > track_point.elevation:
					uphill += current_elevation - track_point.elevation
				else:
					downhill += track_point.elevation - current_elevation

			current_elevation = track_point.elevation

		return ( uphill, downhill )

	def get_elevation_extremes( self ):
		""" return ( min_elevation, max_elevation ) """

		if not self.track_points:
			return ( 0, 0 )

		elevations = [ location.elevation for location in self.track_points ]

		return ( max( elevations ), min( elevations ) )

	def get_location_at( self, time ):
		""" 
		Gets approx. location at given time. Note that, at the moment this method returns
		an instance of GPXTrackPoints in the future -- this may be a Location instance
		with approximated latitude, longitude and elevation!
		"""
		if not self.track_points:
			return None

		if not time:
			return None

		first_time = self.track_points[ 0 ].time
		last_time = self.track_points[ -1 ].time

		if not first_time and not last_time:
			logging.debug( 'No times for track segment' )
			return None

		if time < first_time or time > last_time:
			logging.debug( 'Not in track (search for:%s, start:%s, end:%s)' % ( time, first_time, last_time ) )
			return None

		for i in range( len( self.track_points ) ):
			point = self.track_points[ i ]
			if point.time and time < point.time:
				# TODO: If between two points -- approx position!
				# return Location( point.latitude, point.longitude )
				return point

	def to_xml( self ):
		content = ''
		for track_point in self.track_points:
			content += track_point.to_xml()
		return utils.to_xml( 'trkseg', content = content )

	def get_points_no( self ):
		""" Number of points """
		if not self.track_points:
			return 0
		return len( self.track_points )

	def get_nearest_location( self, location ):
		""" Return the ( location, track_point_no ) on this track segment """
		if not self.track_points:
			return ( None, None )

		result = None
		current_distance = None
		result_track_point_no = None
		for i in range( len( self.track_points ) ):
			track_point = self.track_points[ i ]
			if not result:
				result = track_point
			else:
				distance = track_point.distance_2d( location )
				# print current_distance, distance
				if not current_distance or distance < current_distance:
					current_distance = distance
					result = track_point
					result_track_point_no = i

		return ( result, result_track_point_no )

	def smooth( self ):
		""" "Smooths" the elevation graph. Can be called multiple times. """
		if len( self.track_points ) <= 3:
			return

		# First point
		first = self.track_points[ 0 ]
		second = self.track_points[ 1 ]
		first.elevation = ( 0.3 * second.elevation + 0.4 * first.elevation ) / 0.7

		# Last point
		last = self.track_points[ -1 ]
		penultimate = self.track_points[ -2 ]
		last.elevation = ( 0.3 * penultimate.elevation + 0.4 * last.elevation ) / 0.7

		for i in range( len( self.track_points ) )[ 1 : -1 ]:
			self.track_points[ i ].elevation = \
					0.3 * self.track_points[ i - 1 ].elevation + \
					0.4 * self.track_points[ i ].elevation + \
					0.3 * self.track_points[ i + 1 ].elevation

	def has_times( self ):
		""" 
		Returns if points in this segment contains timestamps.

		At least the first, last points and 75% of others must have times fot this 
		method to return true.
		"""
		if not self.track_points:
			return True
			# ... or otherwise one empty track segment would change the entire 
			# track's "has_times" status!

		has_first = self.track_points[ 0 ]
		has_last = self.track_points[ -1 ]

		found = 0
		for track_point in self.track_points:
			if track_point.time:
				found += 1

		found = float( found ) / float( len( self.track_points ) )

		return has_first and found > .75 and has_last

	def __eq__( self, segment ):
		return utils.attributes_and_classes_equals( self, segment )

class GPX:

	time = None
	name = None
	description = None
	author = None
	email = None
	url = None
	urlname = None
	time = None
	keywords = None

	waypoints = []
	routes = []
	tracks = []

	min_latitude = None
	max_latitude = None
	min_longitude = None
	max_longitude = None

	def __init__( self, waypoints = None, routes = None, tracks = None ):
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

	def length_2d( self ):
		result = 0
		for track in self.tracks:
			length = track.length_2d()
			if length or length == 0:
				result += length
		return result

	def length_3d( self ):
		result = 0
		for track in self.tracks:
			length = track.length_3d()
			if length or length == 0:
				result += length
		return result

	def get_points( self ):
		result = []

		for track in self.tracks:
			result += track.get_points()

		return result

	def get_duration( self ):
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

	def get_uphill_downhill( self ):
		if not self.tracks:
			return ( 0, 0 )

		uphill = 0
		downhill = 0

		for track in self.tracks:
			current_uphill, current_downhill = track.get_uphill_downhill()

			uphill += current_uphill
			downhill += current_downhill

		return ( uphill, downhill )

	def get_location_at( self, time ):
		""" 
		Same as GPXTrackSegment.get_location_at( time )
		"""
		result = []
		for track in self.tracks:
			locations = track.get_location_at( time )
			for location in locations:
				result.append( location )

		return result

	def get_elevation_extremes( self ):
		if not self.tracks:
			return ( 0, 0 )

		elevations = []

		for track in self.tracks:
			( _min, _max ) = track.get_elevation_extremes()
			elevations.append( _min )
			elevations.append( _max )

		return ( min( elevations ), max( elevations ) )

	def get_nearest_location( self, location ):
		""" Returns ( location, track_no, track_segment_no ) for nearest location on map """
		if not self.tracks:
			return None

		result = None
		distance = None
		result_track_no = None
		result_segment_no = None
		result_point_no = None
		for i in range( len( self.tracks ) ):
			track = self.tracks[ i ]
			nearest_location, track_segment_no, track_point_no = track.get_nearest_location( location )
			nearest_location_distance = None
			if nearest_location:
				nearest_location_distance = nearest_location.distance_2d( location )
			if not distance or nearest_location_distance < distance:
				result = nearest_location
				distance = nearest_location_distance
				result_track_no = i
				result_segment_no = track_segment_no
				result_point_no = track_point_no

		return ( result, result_track_no, result_segment_no, result_point_no )

	def to_xml( self ):
		content = utils.to_xml( 'time', content = self.time )
		content += utils.to_xml( 'name', content = self.name, cdata = True )
		content += utils.to_xml( 'desc', content = self.description, cdata = True )
		content += utils.to_xml( 'author', content = self.author, cdata = True )
		content += utils.to_xml( 'email', content = self.email, cdata = True )
		content += utils.to_xml( 'url', content = self.url, cdata = True )
		content += utils.to_xml( 'urlname', content = self.urlname, cdata = True )
		if self.time:
			content = utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content += utils.to_xml( 'keywords', content = self.keywords, cdata = True )

		for waypoint in self.waypoints:
			content += waypoint.to_xml()

		for track in self.tracks:
			content += track.to_xml()

		for route in self.routes:
			content += route.to_xml()

		return utils.to_xml( 'gpx', attributes = {}, content = content )

	def smooth( self ):
		for track in self.tracks:
			track.smooth()

	def has_times( self ):
		""" See GPXTrackSegment.has_times() """
		if not self.tracks:
			return None

		result = True
		for track in self.tracks:
			result = result and track.has_times()

		return result

	def __eq__( self, route ):
		return utils.attributes_and_classes_equals( self, route, ignore = ( 'min_latitude', 'max_latitude', 'min_longitude', 'max_longitude' ) )

class GPXParser:

	xml = None

	valid = None
	error = None

	gpx = None

	def __init__( self, xml_or_file = None ):
		if hasattr( xml_or_file, 'read' ):
			self.xml = xml_or_file.read()
		else:
			self.xml = str( xml_or_file )

		self.valid = False
		self.error = None

		self.gpx = GPX()

	def parse( self ):
		try:
			dom = minidom.parseString( self.xml )
			self._parse_dom( dom )

			return self.gpx
		except Exception, e:
			logging.debug( 'Error in:\n%s\n-----------\n' % self.xml )
			logging.exception( e )
			self.error = str( e )

			return None

	def _parse_dom( self, dom ):
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
				time_str = self.get_node_data( node )
				self.gpx.time = _parse_time( time_str )
			elif node_name == 'name':
				self.gpx.name = self.get_node_data( node )
			elif node_name == 'desc':
				self.gpx.description = self.get_node_data( node )
			elif node_name == 'author':
				self.gpx.author = self.get_node_data( node )
			elif node_name == 'email':
				self.gpx.email = self.get_node_data( node )
			elif node_name == 'url':
				self.gpx.url = self.get_node_data( node )
			elif node_name == 'urlname':
				self.gpx.urlname = self.get_node_data( node )
			elif node_name == 'keywords':
				self.gpx.keywords = self.get_node_data( node )
			elif node_name == 'bounds':
				self._parse_bounds( node )
			elif node_name == 'wpt':
				self.gpx.waypoints.append( self._parse_waypoint( node ) )
			elif node_name == 'rte':
				self.gpx.routes.append( self._parse_route( node ) )
			elif node_name == 'trk':
				self.gpx.tracks.append( self.__parse_track( node ) )
			else:
				#print 'unknown %s' % node
				pass

		self.valid = True

	def _parse_bounds( self, node ):
		if node.attributes.has_key( 'minlat' ):
			self.gpx.min_latitude = utils.to_number( node.attributes[ 'minlat' ].nodeValue )
		if node.attributes.has_key( 'maxlat' ):
			self.gpx.min_latitude = utils.to_number( node.attributes[ 'maxlat' ].nodeValue )
		if node.attributes.has_key( 'minlon' ):
			self.gpx.min_longitude = utils.to_number( node.attributes[ 'minlon' ].nodeValue )
		if node.attributes.has_key( 'maxlon' ):
			self.gpx.min_longitude = utils.to_number( node.attributes[ 'maxlon' ].nodeValue )

	def _parse_waypoint( self, node ):
		if not node.attributes.has_key( 'lat' ):
			raise Exception( 'Waypoint without latitude' )
		if not node.attributes.has_key( 'lon' ):
			raise Exception( 'Waypoint without longitude' )

		lat = utils.to_number( node.attributes[ 'lat' ].nodeValue )
		lon = utils.to_number( node.attributes[ 'lon' ].nodeValue )

		elevation_node = utils.find_first_node( node, 'ele' )
		elevation = utils.to_number( self.get_node_data( elevation_node ), 0 )

		time_node = utils.find_first_node( node, 'time' )
		time_str = self.get_node_data( time_node )
		time = _parse_time( time_str )

		name_node = utils.find_first_node( node, 'name' )
		name = self.get_node_data( name_node )

		desc_node = utils.find_first_node( node, 'desc' )
		desc = self.get_node_data( desc_node )

		sym_node = utils.find_first_node( node, 'sym' )
		sym = self.get_node_data( sym_node )

		type_node = utils.find_first_node( node, 'type' )
		type = self.get_node_data( type_node )

		comment_node = utils.find_first_node( node, 'cmt' )
		comment = self.get_node_data( comment_node )

		return GPXWaypoint( latitude = lat, longitude = lon, elevation = elevation, time = time, name = name, description = desc, symbol = sym, type = type, comment = comment )

	def _parse_route( self, node ):
		name_node = utils.find_first_node( node, 'name' )
		name = self.get_node_data( name_node )

		description_node = utils.find_first_node( node, 'desc' )
		description = self.get_node_data( description_node )

		number_node = utils.find_first_node( node, 'number' )
		number = utils.to_number( self.get_node_data( number_node ) )

		route = GPXRoute( name, description, number )

		child_nodes = node.childNodes
		for child_node in child_nodes:
			node_name = child_node.nodeName
			if node_name == 'rtept':
				route_point = self._parse_route_point( child_node )
				route.route_points.append( route_point )

		return route

	def _parse_route_point( self, node ):
		if not node.attributes.has_key( 'lat' ):
			raise Exception( 'Waypoint without latitude' )
		if not node.attributes.has_key( 'lon' ):
			raise Exception( 'Waypoint without longitude' )

		lat = utils.to_number( node.attributes[ 'lat' ].nodeValue )
		lon = utils.to_number( node.attributes[ 'lon' ].nodeValue )

		elevation_node = utils.find_first_node( node, 'ele' )
		elevation = utils.to_number( self.get_node_data( elevation_node ), 0 )

		time_node = utils.find_first_node( node, 'time' )
		time_str = self.get_node_data( time_node )
		time = _parse_time( time_str )

		name_node = utils.find_first_node( node, 'name' )
		name = self.get_node_data( name_node )

		desc_node = utils.find_first_node( node, 'desc' )
		desc = self.get_node_data( desc_node )

		sym_node = utils.find_first_node( node, 'sym' )
		sym = self.get_node_data( sym_node )

		type_node = utils.find_first_node( node, 'type' )
		type = self.get_node_data( type_node )

		comment_node = utils.find_first_node( node, 'cmt' )
		comment = self.get_node_data( comment_node )

		return GPXRoutePoint( lat, lon, elevation, time, name, desc, sym, type, comment )

	def __parse_track( self, node ):
		name_node = utils.find_first_node( node, 'name' )
		name = self.get_node_data( name_node )

		description_node = utils.find_first_node( node, 'desc' )
		description = self.get_node_data( description_node )

		number_node = utils.find_first_node( node, 'number' )
		number = utils.to_number( self.get_node_data( number_node ) )

		track = GPXTrack( name, description, number )

		child_nodes = node.childNodes
		for child_node in child_nodes:
			if child_node.nodeName == 'trkseg':
				track_segment = self.__parse_track_segment( child_node )

				track.track_segments.append( track_segment )

		return track

	def __parse_track_segment( self, node ):
		track_segment = GPXTrackSegment()
		child_nodes = node.childNodes
		n = 0
		for child_node in child_nodes:
			if child_node.nodeName == 'trkpt':
				track_point = self.__parse_track_point( child_node )
				track_segment.track_points.append( track_point )
				n += 1

		return track_segment

	def __parse_track_point( self, node ):
		latitude = None
		if node.attributes.has_key( 'lat' ):
			latitude = utils.to_number( node.attributes[ 'lat' ].nodeValue )

		longitude = None
		if node.attributes.has_key( 'lon' ):
			longitude = utils.to_number( node.attributes[ 'lon' ].nodeValue )

		time_node = utils.find_first_node( node, 'time' )
		time = _parse_time( self.get_node_data( time_node ) )

		elevation_node = utils.find_first_node( node, 'ele' )
		elevation = utils.to_number( self.get_node_data( elevation_node ) )

		symbol_node = utils.find_first_node( node, 'sym' )
		symbol = self.get_node_data( symbol_node )

		comment_node = utils.find_first_node( node, 'cmt' )
		comment = self.get_node_data( comment_node )

		return GPXTrackPoint( latitude = latitude, longitude = longitude, elevation = elevation, time = time, symbol = symbol, comment = comment )

	def is_valid( self ):
		return self.valid

	def get_error( self ):
		return self.error

	def get_gpx( self ):
		return self.gpx

	def get_node_data( self, node ):
		if not node:
			return None
		child_nodes = node.childNodes
		if not child_nodes or len( child_nodes ) == 0:
			return None
		return child_nodes[ 0 ].data

if __name__ == '__main__':

	file_name = 'test_files/aaa.gpx'
	#file_name = 'test_files/blue_hills.gpx'
	#file_name = 'test_files/test.gpx'
	file = open( file_name, 'r' )
	gpx_xml = file.read()
	file.close()

	parser = GPXParser( gpx_xml )
	gpx = parser.parse()

	print gpx.to_xml()

	if parser.is_valid():
		print 'TRACKS:'
		for track in gpx.tracks:
			print 'name%s, 2d:%s, 3d:%s' % ( track.name, track.length_2d(), track.length_3d() )
			print '\tTRACK SEGMENTS:'
			for track_segment in track.track_segments:
				print '\t2d:%s, 3d:%s' % ( track_segment.length_2d(), track_segment.length_3d() )

		print 'ROUTES:'
		for route in gpx.routes:
			print route.name
	else:
		print 'error: %s' % parser.get_error()
