gpxpy -- GPX file parser
========================

This is a simple python library for parsing and manipulating GPX files. GPX is an XML based format for GPS tracks.

You can see it in action on [my online GPS track editor and organizer](http://www.trackprofiler.com).

Usage
-----

    import gpxpy
    
    gpx_file = open( 'test_files/cerknicko-jezero.gpx', 'r' )
    
    gpx_parser = gpxpy.parse( gpx_file )
    
    gpx = gpx_parser.get_gpx()
    
    for track in gpx.tracks:
    	for segment in track.segments:
    		for point in segment.points:
    			print 'Point at ({0},{1}) -> {2}'.format( point.latitude, point.longitude, point.elevation )
    
    for waypoint in gpx.waypoints:
    	print 'waypoint {0} -> ({1},{2})'.format( waypoint.name, waypoint.latitude, waypoint.longitude )
    	
    for route in gpx.routes:
    	print 'Route:'
    	for point in route:
    		print 'Point at ({0},{1}) -> {2}'.format( point.latitude, point.longitude, point.elevation )
    
    # There are many more utility methods and functions:
    # You can manipulate/add/remove tracks, segments, points, waypoints and routes and
    # get the GPX XML file from the resulting object:
    
    print 'GPX:', gpx.to_xml()

GPX Version:
------------

gpx.py can parse and generate GPX 1.0 files. Note that the generated file will always be a valid XML document, but it may not be (strictly speaking) a valid GPX document. For example, if you set gpx.email to "my.email AT mail.com" the generated GPX tag won't confirm to the regex pattern. And the file won't be valid. Most applications will ignore such errors, but... Be aware of this!

License
-------

GPX.py is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

