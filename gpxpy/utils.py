# -*- coding: utf-8 -*-

def attributes_and_classes_equals( object1, object2, attributes = None ):

	if not object1 and not object2:
		return True

	if not object1 or not object2:
		return None

	if not object1.__class__ == object2.__class__:
		return None

	if not attributes:
		attributes = []
		for attr in dir( object1 ) + dir( object2 ):
			if not callable( attr ) and not attr.startswith( '_' ):
				if not attr in attributes:
					attributes.append( attr )
	
	for attr in attributes:
		attr1 = getattr( object1, attr )
		attr2 = getattr( object2, attr )

		if not attr1 == attr2:
			return None

	return True
