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

