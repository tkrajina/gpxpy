# -*- coding: utf-8 -*-

import logging
import datetime

from xml.dom import minidom

import gpx as _gpx
import utils
import re

def parse_time( string ):
	if not string:
		return None
	try:
		return datetime.datetime.strptime( string, _gpx.DATE_FORMAT )
	except Exception, e:
		if re.match( '^.*\.\d+Z$', string ):
			string = re.sub( '\.\d+Z', 'Z', string )
		return datetime.datetime.strptime( string, _gpx.DATE_FORMAT )

class GPXParser:

	xml = None

	valid = None
	error = None

	gpx = None

	def __init__( self, xml_or_file = None ):
		if hasattr( xml_or_file, 'read' ):
			self.xml = xml_or_file.read()
		else:
			if isinstance( xml_or_file, unicode ):
				self.xml = xml_or_file.encode( 'utf-8' )
			else:
				self.xml = str( xml_or_file )

		self.valid = False
		self.error = None

		self.gpx = _gpx.GPX()

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
				self.gpx.time = parse_time( time_str )
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
		time = parse_time( time_str )

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

		return _gpx.GPXWaypoint( latitude = lat, longitude = lon, elevation = elevation, time = time, name = name, description = desc, symbol = sym, type = type, comment = comment )

	def _parse_route( self, node ):
		name_node = utils.find_first_node( node, 'name' )
		name = self.get_node_data( name_node )

		description_node = utils.find_first_node( node, 'desc' )
		description = self.get_node_data( description_node )

		number_node = utils.find_first_node( node, 'number' )
		number = utils.to_number( self.get_node_data( number_node ) )

		route = _gpx.GPXRoute( name, description, number )

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
		time = parse_time( time_str )

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

		return _gpx.GPXRoutePoint( lat, lon, elevation, time, name, desc, sym, type, comment )

	def __parse_track( self, node ):
		name_node = utils.find_first_node( node, 'name' )
		name = self.get_node_data( name_node )

		description_node = utils.find_first_node( node, 'desc' )
		description = self.get_node_data( description_node )

		number_node = utils.find_first_node( node, 'number' )
		number = utils.to_number( self.get_node_data( number_node ) )

		track = _gpx.GPXTrack( name, description, number )

		child_nodes = node.childNodes
		for child_node in child_nodes:
			if child_node.nodeName == 'trkseg':
				track_segment = self.__parse_track_segment( child_node )

				track.track_segments.append( track_segment )

		return track

	def __parse_track_segment( self, node ):
		track_segment = _gpx.GPXTrackSegment()
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
		time = parse_time( self.get_node_data( time_node ) )

		elevation_node = utils.find_first_node( node, 'ele' )
		elevation = utils.to_number( self.get_node_data( elevation_node ) )

		symbol_node = utils.find_first_node( node, 'sym' )
		symbol = self.get_node_data( symbol_node )

		comment_node = utils.find_first_node( node, 'cmt' )
		comment = self.get_node_data( comment_node )

		return _gpx.GPXTrackPoint( latitude = latitude, longitude = longitude, elevation = elevation, time = time, symbol = symbol, comment = comment )

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

	parser = _gpx.GPXParser( gpx_xml )
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
