# -*- coding: utf-8 -*-

import logging

def attributes_and_classes_equals( object1, object2, ignore = None ):

	if not object1 and not object2:
		return True

	if not object1 or not object2:
		return None

	if not object1.__class__ == object2.__class__:
		return None

	attributes = []
	for attr in dir( object1 ):
		if not ignore or not attr in ignore:
			if not callable( getattr( object1, attr ) ) and not attr.startswith( '_' ):
				if not attr in attributes:
					attributes.append( attr )

	for attr in attributes:
		attr1 = getattr( object1, attr )
		attr2 = getattr( object2, attr )

		if not attr1 == attr2:
			logging.debug( 'Object differs in attribute %s (%s - %s)' % ( attr, attr1, attr2 ) )
			return None

	return True

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

