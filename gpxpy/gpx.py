# -*- coding: utf-8 -*-

import logging as mod_logging
import math as mod_math
import datetime as mod_datetime

import utils as mod_utils
import copy as mod_copy

# One degree in meters:
ONE_DEGREE = 1000. * 10000.8 / 90.

# GPX date format
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# Used in smoothing, sum must be 1:
SMOOTHING_RATIO = ( 0.4, 0.2, 0.4 )

# When computing stopped time -- this is the miminum speed between two points, if speed is less
# than this value -- we'll assume it is 0
DEFAULT_STOPPED_SPEED_TRESHOLD = 1

def length( locations = [], _3d = None ):
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
	""" 3-dimensional length of locations (is uses latitude, longitude and elevation). """
	return length( locations, True )

def distance( latitude_1, longitude_1, elevation_1, latitude_2, longitude_2, elevation_2 ):
	""" Distance between two points. If elevation == None compute a 2d distance """

	coef = mod_math.cos( latitude_1 / 180. * mod_math.pi )
	x = latitude_1 - latitude_2
	y = ( longitude_1 - longitude_2 ) * coef

	distance_2d = mod_math.sqrt( x * x + y * y ) * ONE_DEGREE

	if elevation_1 == None or elevation_2 == None or elevation_1 == elevation_2:
		return distance_2d

	return mod_math.sqrt( distance_2d ** 2 + ( elevation_1 - elevation_2 ) ** 2 )

def length_2d( locations = [] ):
	""" 2-dimensional length of locations (only latitude and longitude, no elevation """
	return length( locations, None )

class Location:

	latitude = None
	longitude = None
	elevation = None

	def __init__( self, latitude, longitude, elevation = None ):
		self.latitude = latitude
		self.longitude = longitude
		self.elevation = elevation

	def has_elevation( self ):
		return self.elevation or self.elevation == 0

	def distance_2d( self, location ):
		if not location:
			return None

		return distance( self.latitude, self.longitude, None, location.latitude, location.longitude, None )

	def distance_3d( self, location ):
		if not location:
			return None

		return distance( self.latitude, self.longitude, self.elevation, location.latitude, location.longitude, location.elevation )

	def move( self, latitude_diff, longitude_diff ):
		self.latitude += latitude_diff
		self.longitude += longitude_diff
		
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
		content = mod_utils.to_xml( 'ele', content = self.elevation )
		if self.time:
			content += mod_utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content += mod_utils.to_xml( 'name', content = self.name, cdata = True )
		content += mod_utils.to_xml( 'desc', content = self.description, cdata = True )
		content += mod_utils.to_xml( 'sym', content = self.symbol, cdata = True )
		content += mod_utils.to_xml( 'type', content = self.type, cdata = True )
		content += mod_utils.to_xml( 'cmt', content = self.comment, cdata = True )

		return mod_utils.to_xml( 'wpt', attributes = { 'lat': self.latitude, 'lon': self.longitude }, content = content )

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

	def move( self, latitude_diff, longitude_diff ):
		for route_point in self.route_points:
			route_point.move( latitude_diff, longitude_diff )

	def to_xml( self ):
		content = mod_utils.to_xml( 'name', content = self.name, cdata = True )
		content += mod_utils.to_xml( 'desc', content = self.description, cdata = True )
		content += mod_utils.to_xml( 'number', content = self.number )
		for route_point in self.route_points:
			content += route_point.to_xml()

		return mod_utils.to_xml( 'rte', content = content )

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
		content = mod_utils.to_xml( 'ele', content = self.elevation )
		if self.time:
			content = mod_utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content = mod_utils.to_xml( 'name', content = self.name, cdata = True )
		content = mod_utils.to_xml( 'cmt', content = self.comment, cdata = True )
		content = mod_utils.to_xml( 'desc', content = self.description, cdata = True )
		content = mod_utils.to_xml( 'sym', content = self.symbol, cdata = True )
		content = mod_utils.to_xml( 'type', content = self.type, cdata = True )

		return mod_utils.to_xml( 'rtept', attributes = { 'lat': self.latitude, 'lon': self.longitude }, content = content )

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
		content = mod_utils.to_xml( 'ele', content = self.elevation )
		if self.time:
			content += mod_utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content += mod_utils.to_xml( 'cmt', content = self.comment, cdata = True )
		content += mod_utils.to_xml( 'sym', content = self.symbol, cdata = True )
		return mod_utils.to_xml( 'trkpt', { 'lat': self.latitude, 'lon': self.longitude }, content = content )

	def time_difference( self, track_point ):
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

	def speed( self, track_point ):
		if not track_point:
			return None

		seconds = self.time_difference( track_point )
		length = self.distance_3d( track_point )
		if not length:
			length = self.distance_2d( track_point )

		if not seconds or not length:
			return None

		return length / float( seconds )

	def __str__( self ):
		return '[trkpt:%s,%s@%s@%s]' % ( self.latitude, self.longitude, self.elevation, self.time )

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

	def remove_empty( self ):
		""" Removes empty segments and/or routes """
		result = []

		for segment in self.track_segments:
			if len( segment.track_points ) > 0:
				result.append( segment )

		self.track_segments = result
	
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

	def split( self, track_segment_no, track_point_no ):
		""" Splits One of the segments in two parts. If one of the splitted segments is empty 
		it will not be added in the result """
		new_segments = []
		for i in range( len( self.track_segments ) ):
			segment = self.track_segments[ i ]
			if i == track_segment_no:
				segment_1, segment_2 = segment.split( track_point_no )
				if segment_1:
					new_segments.append( segment_1 )
				if segment_2:
					new_segments.append( segment_2 )
			else:
				new_segments.append( segment )
		self.track_segments = new_segments

	def join( self, track_segment_no, track_segment_no_2 = None ):
		""" Joins two segments of this track. If track_segment_no_2 the join will be with the
		next segment """

		if not track_segment_no_2:
			track_segment_no_2 = track_segment_no + 1

		if track_segment_no_2 >= len( self.track_segments ):
			return

		new_segments = []
		for i in range( len( self.track_segments ) ):
			segment = self.track_segments[ i ]
			if i == track_segment_no:
				second_segment = self.track_segments[ track_segment_no_2 ]
				segment.join( second_segment )

				new_segments.append( segment )
			elif i == track_segment_no_2:
				# Nothing, it is already joined
				pass
			else:
				new_segments.append( segment )
		self.track_segments = new_segments

	def get_moving_data( self, stopped_speed_treshold = None ):
		moving_time = 0.
		stopped_time = 0.

		moving_distance = 0.
		stopped_distance = 0.

		max_speed = 0.

		for segment in self.track_segments:
			track_moving_time, track_stopped_time, track_moving_distance, track_stopped_distance, track_max_speed = segment.get_moving_data( stopped_speed_treshold )
			moving_time += track_moving_time
			stopped_time += track_stopped_time
			moving_distance += track_moving_distance
			stopped_distance += track_stopped_distance

			if track_max_speed > max_speed:
				max_speed = track_max_speed

		return ( moving_time, stopped_time, moving_distance, stopped_distance, max_speed )

	def move( self, latitude_diff, longitude_diff ):
		for track_segment in self.track_segments:
			track_segment.move( latitude_diff, longitude_diff )

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
		content = mod_utils.to_xml( 'name', content = self.name, cdata = True )
		content += mod_utils.to_xml( 'desc', content = self.description, cdata = True )
		content += mod_utils.to_xml( 'number', content = self.number )
		for track_segment in self.track_segments:
			content += track_segment.to_xml()

		return mod_utils.to_xml( 'trk', content = content )

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

	def smooth( self, vertical = True, horizontal = False, remove_extreemes = False ):
		""" See: GPXTrackSegment.smooth() """
		for track_segment in self.track_segments:
			track_segment.smooth( vertical, horizontal, remove_extreemes )

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
				if nearest_location:
					distance = nearest_location_distance
					result = nearest_location
					result_track_segment_no = i
					result_track_point_no = track_point_no

		return ( result, result_track_segment_no, result_track_point_no )

	def clone( self ):
		return mod_copy.deepcopy( self )

	def __hash__( self ):
		return id( self )

class GPXTrackSegment:
	track_points = None

	def __init__( self, track_points = None ):
		self.track_points = track_points if track_points else []

	def length_2d( self ):
		return length_2d( self.track_points )

	def length_3d( self ):
		return length_3d( self.track_points )

	def move( self, latitude_diff, longitude_diff ):
		for track_point in self.track_points:
			track_point.move( latitude_diff, longitude_diff )
		
	def get_points( self ):
		return self.track_points

	def split( self, point_no ):
		""" Splits this segment in two parts. Point #point_no remains in the first part. 
		Returns a list with two GPXTrackSegments """
		part_1 = self.track_points[ : point_no + 1 ]
		part_2 = self.track_points[ point_no + 1 : ]
		return ( GPXTrackSegment( part_1 ), GPXTrackSegment( part_2 ) )

	def join( self, track_segment ):
		""" Joins with another segment """
		self.track_points += track_segment.track_points

	def remove_point( self, point_no ):
		if point_no < 0 or point_no >= len( self.track_points ):
			return

		part_1 = self.track_points[ : point_no ]
		part_2 = self.track_points[ point_no + 1 : ]

		self.track_points = part_1 + part_2

	def get_moving_data( self, stopped_speed_treshold = None ):
		if not stopped_speed_treshold:
			stopped_speed_treshold = DEFAULT_STOPPED_SPEED_TRESHOLD

		moving_time = 0.
		stopped_time = 0.

		moving_distance = 0.
		stopped_distance = 0.

		max_speed = 0.

		previous = None
		for i in range( 1, len( self.track_points ) ):

			previous = self.track_points[ i - 1 ]
			point = self.track_points[ i ]

			# Won't compute max_speed for first and last because of common GPS
			# recording errors, and because smoothing don't work well for those
			# points:
			first_or_last = i in [ 0, 1, len( self.track_points ) - 1 ]
			if point.time and previous.time:
				timedelta = point.time - previous.time

				if point.elevation and previous.elevation:
					distance = point.distance_3d( previous )
				else:
					distance = point.distance_2d( previous )

				seconds = timedelta.seconds
				speed = 0
				if seconds > 0:
					speed = ( distance / 1000. ) / ( timedelta.seconds / 60. ** 2 )

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
		return ( moving_time, stopped_time, moving_distance, stopped_distance, max_speed )

	def get_speed( self, point_no ):
		""" Get speed at that point. Point may be a GPXTrackPoint instance or integer (point index) """

		point = self.track_points[ point_no ]

		previous_point = None
		next_point = None

		if 0 < point_no and point_no < len( self.track_points ):
			previous_point = self.track_points[ point_no - 1 ]
		if 0 < point_no and point_no < len( self.track_points ) - 1:
			next_point = self.track_points[ point_no + 1 ]

		#mod_logging.debug( 'previous: %s' % previous_point )
		#mod_logging.debug( 'next: %s' % next_point )

		speed_1 = point.speed( previous_point )
		speed_2 = point.speed( next_point )

		if speed_1:
			speed_1 = abs( speed_1 )
		if speed_2:
			speed_2 = abs( speed_2 )

		if speed_1 and speed_2:
			return ( speed_1 + speed_2 ) / 2.

		if speed_1:
			return speed_1

		return speed_2

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
			mod_logging.debug( 'Can\'t find time' )
			return None

		if last.time < first.time:
			mod_logging.debug( 'Not enough time data' )
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
					downhill += current_elevation - track_point.elevation
				else:
					uphill += track_point.elevation - current_elevation

			current_elevation = track_point.elevation

		return ( uphill, downhill )

	def get_elevation_extremes( self ):
		""" return ( min_elevation, max_elevation ) """

		if not self.track_points:
			return ( 0.0, 0.0 )

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
			mod_logging.debug( 'No times for track segment' )
			return None

		if time < first_time or time > last_time:
			mod_logging.debug( 'Not in track (search for:%s, start:%s, end:%s)' % ( time, first_time, last_time ) )
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
		return mod_utils.to_xml( 'trkseg', content = content )

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

	def smooth( self, vertical = True, horizontal = False, remove_extreemes = False ):
		""" "Smooths" the elevation graph. Can be called multiple times. """
		if len( self.track_points ) <= 3:
			return

		elevations = []
		latitudes = []
		longitudes = []

		for point in self.track_points:
			elevations.append( point.elevation )
			latitudes.append( point.latitude )
			longitudes.append( point.longitude )

		# If The point moved more than this number * the average distance between two
		# points -- then is a candidate for deletion:
		# TODO: Make this a method parameter
		remove_extreemes_treshold = 2.

		avg_distance = 0
		if remove_extreemes:
			# compute the average distance between two points:
			distances = []
			for i in range( len( self.track_points ) )[ 1 : ]:
				distances.append( self.track_points[ i ].distance_2d( self.track_points[ i - 1 ] ) )
			if distances:
				avg_distance = 1.0 * sum( distances ) / len( distances )

		remove_extreemes_treshold = remove_extreemes_treshold * avg_distance

		new_track_points = []

		for i in range( len( self.track_points ) )[ 1 : -1 ]:
			if vertical and elevations[ i - 1 ] and elevations[ i ] and elevations[ i + 1 ]:
				old_elevation = self.track_points[ i ].elevation
				new_elevation = SMOOTHING_RATIO[ 0 ] * elevations[ i - 1 ] + \
						SMOOTHING_RATIO[ 1 ] * elevations[ i ] + \
						SMOOTHING_RATIO[ 2 ] * elevations[ i + 1 ]

				self.track_points[ i ].elevation = new_elevation

				if remove_extreemes:
					if abs( old_elevation - new_elevation ) < remove_extreemes_treshold:
						new_track_points.append( self.track_points[ i ] )
				else:
					new_track_points.append( self.track_points[ i ] )

			if horizontal:
				old_latitude = self.track_points[ i ].latitude
				new_latitude = SMOOTHING_RATIO[ 0 ] * latitudes[ i - 1 ] + \
						SMOOTHING_RATIO[ 1 ] * latitudes[ i ] + \
						SMOOTHING_RATIO[ 2 ] * latitudes[ i + 1 ]
				old_longitue = self.track_points[ i ].longitude
				new_longitude = SMOOTHING_RATIO[ 0 ] * longitudes[ i - 1 ] + \
						SMOOTHING_RATIO[ 1 ] * longitudes[ i ] + \
						SMOOTHING_RATIO[ 2 ] * longitudes[ i + 1 ]
				
				self.track_points[ i ].latitude = new_latitude
				self.track_points[ i ].longitude = new_longitude

				if remove_extreemes:
					d = distance( old_latitude, new_latitude, None, old_longitude, new_longitude, None )
					if d < remove_extreemes_treshold:
						new_track_points.append( self.track_points[ i ] )
				else:
					new_track_points.append( self.track_points[ i ] )

		self.track_points = new_track_points

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

	def clone( self ):
		return mod_copy.deepcopy( self )

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

	def smooth( self, vertical = True, horizontal = False, remove_extreemes = False ):
		""" See GPXTrackSegment.smooth( ... ) """
		for track in self.tracks:
			track.smooth( vertical = vertical, horizontal = horizontal, remove_extreemes = remove_extreemes )

	def remove_empty( self ):
		""" Removes segments, routes """

		routes = []

		for route in self.routes:
			if len( route.route_points ) > 0:
				routes.append( route )

		self.routes = routes

		for track in self.tracks:
			track.remove_empty()

	def get_moving_data( self, stopped_speed_treshold = None ):
		"""
		Return a tuple of ( moving_time, stopped_time, moving_distance, stopped_distance, max_speed )
		that may be used for detecting the time stopped, and max speed. Not that those values are not
		absolutely true, because the "stopped" or "moving" informations aren't saved in the track.

		Because of errors in the GPS recording, it may be good to calculate them on a reduced and
		smoothed version of the track. Something like this:

		cloned_gpx = gpx.clone()
		cloned_gpx.reduce_points( 2000, min_distance = 10 )
		cloned_gpx.smooth( vertical = True, horizontal = True )
		cloned_gpx.smooth( vertical = True, horizontal = False )
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
			track_moving_time, track_stopped_time, track_moving_distance, track_stopped_distance, track_max_speed = track.get_moving_data( stopped_speed_treshold )
			moving_time += track_moving_time
			stopped_time += track_stopped_time
			moving_distance += track_moving_distance
			stopped_distance += track_stopped_distance

			if track_max_speed > max_speed:
				max_speed = track_max_speed

		return ( moving_time, stopped_time, moving_distance, stopped_distance, max_speed )

	def reduce_points( self, max_points_no, min_distance = None ):
		"""
		Reduce this track to the desired number of points
		max_points = The maximum number of points after the reduction
		min_distance = The minimum distance between two points
		"""

		points_no = self.get_points()
		if not max_points_no or points_no <= max_points_no:
			return

		length = self.length_3d()

		if not min_distance:
			min_distance = mod_math.ceil( length / float( max_points_no ) )
			if not min_distance or min_distance < 0:
				min_distance = 100

		for track in self.tracks:
			for track_segment in track.track_segments:
				reduced_points = []
				previous_point = None
				length = len( track_segment.track_points )
				for i in range( length ):
					point = track_segment.track_points[ i ]
					if i == 0 or i == length - 1:
						# Leave first and last point
						reduced_points.append( point )
						previous_point = point
					elif previous_point:
						distance = previous_point.distance_3d( point )
						if distance >= min_distance:
							reduced_points.append( point )
							previous_point = point

				track_segment.track_points = reduced_points

		mod_logging.debug( 'Track reduced to %s points' % len( self.get_points() ) )

	def split( self, track_no, track_segment_no, track_point_no ):
		track = self.tracks[ track_no ]

		track.split( track_segment_no = track_segment_no, track_point_no = track_point_no )

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
		""" Returns ( location, track_no, track_segment_no, track_point_no ) for the
		nearest location on map """
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

	def move( self, latitude_diff, longitude_diff ):
		for routes in self.routes:
			waypoint.move( latitude_diff, longitude_diff )

		for waypoint in self.waypoints:
			waypoint.move( latitude_diff, longitude_diff )

		for track in self.tracks:
			track.move( latitude_diff, longitude_diff )

	def to_xml( self ):
		content = mod_utils.to_xml( 'time', content = self.time )
		content += mod_utils.to_xml( 'name', content = self.name, cdata = True )
		content += mod_utils.to_xml( 'desc', content = self.description, cdata = True )
		content += mod_utils.to_xml( 'author', content = self.author, cdata = True )
		content += mod_utils.to_xml( 'email', content = self.email, cdata = True )
		content += mod_utils.to_xml( 'url', content = self.url, cdata = True )
		content += mod_utils.to_xml( 'urlname', content = self.urlname, cdata = True )
		if self.time:
			content = mod_utils.to_xml( 'time', content = self.time.strftime( DATE_FORMAT ) )
		content += mod_utils.to_xml( 'keywords', content = self.keywords, cdata = True )

		for waypoint in self.waypoints:
			content += waypoint.to_xml()

		for track in self.tracks:
			content += track.to_xml()

		for route in self.routes:
			content += route.to_xml()

		return mod_utils.to_xml( 'gpx', attributes = {}, content = content )

	def smooth( self, vertical = True, horizontal = False, remove_extreemes = False ):
		for track in self.tracks:
			track.smooth( vertical, horizontal, remove_extreemes )

	def has_times( self ):
		""" See GPXTrackSegment.has_times() """
		if not self.tracks:
			return None

		result = True
		for track in self.tracks:
			result = result and track.has_times()

		return result

	def clone( self ):
		return mod_copy.deepcopy( self )
