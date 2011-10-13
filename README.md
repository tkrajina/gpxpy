gpxpy -- GPX file parser
========================

This is a simple python library for parsing and manipulating GPX files. GPX is an XML based format for GPS tracks.

You can see it in action on [my online GPS track editor and organizer](http://www.trackprofiler.com).

Usage
-----

    import gpxpy.parser as parser
    
    gpx_file = open( 'test_files/cerknicko-jezero.gpx', 'r' )
    
    gpx_parser = parser.GPXParser( gpx_file )
    gpx_parser.parse()
    
    gpx_file.close()
    
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
    
    # There are more utility methods and functions...
    
    # You can manipulate/add/remove tracks, segments, points, waypoints and routes and
    # get the GPX XML file from the resulting object:
    
    print 'GPX:', gpx.to_xml()

