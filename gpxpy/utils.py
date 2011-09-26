# -*- coding: utf-8 -*-

import logging

def to_cdata( str ):
	if not str:
		return '<![CDATA[]]>'
	return '<![CDATA[%s]]>' % str.replace( ']]>', '???' )

def to_xml( tag, attributes = {}, content = None, cdata = None ):
	result = '\n<%s' % tag
	if attributes:
		for attribute in attributes.keys():
			result += ' %s="%s"' % ( attribute, attributes[ attribute ] )
	if content:
		if cdata:
			result += '>%s</%s>' % ( to_cdata( content ), tag )
		else:
			result += '>%s</%s>' % ( content, tag )
	else:
		result += ' />'

	result += ''

	if isinstance( result, unicode ):
		result = result.encode( 'utf-8' )
	
	return result

def to_number( str, default = 0 ):
	if not str:
		return None
	return float( str )

def find_first_node( node, child_node_name ):
	if not node or not child_node_name:
		return None
	child_nodes = node.childNodes
	for child_node in child_nodes:
		if child_node.nodeName == child_node_name:
			return child_node
	return None

# Hash utilities:

def __hash( obj ):
	result = 0

	if obj == None:
		return result
	elif isinstance( obj, dict ):
		raise Error( '__hash_single_object for dict not yet implemented' )
	elif isinstance( obj, list ) or isinstance( obj, tuple ):
		return hash_list_or_tuple( obj )

	return hash( obj )

def hash_list_or_tuple( iteration ):
	result = 17

	for obj in iteration:
		result = result * 31 + __hash( obj )

	return result

def hash_object( obj, *attributes ):
	result = 19

	for attribute in attributes:
		result = result * 31 + __hash( getattr( obj, attribute ) )
	
	return result

