gpxpy -- GPX file parser
========================

This is a simple python library for parsing and manipulating GPX files. GPX is an XML based format for GPS tracks.

You can see it in action on [my online GPS track editor and organizer](http://www.trackprofiler.com).

Usage
-----

    import gpxpy
    import gpxpy.gpx

    # Parsing an existing file:
    # -------------------------

    gpx_file = open('test_files/cerknicko-jezero.gpx', 'r')

    gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)

    for waypoint in gpx.waypoints:
        print 'waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude)
        
    for route in gpx.routes:
        print 'Route:'
        for point in route:
            print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)

    # There are many more utility methods and functions:
    # You can manipulate/add/remove tracks, segments, points, waypoints and routes and
    # get the GPX XML file from the resulting object:

    print 'GPX:', gpx.to_xml()

    # Creating a new file:
    # --------------------

    gpx = gpxpy.gpx.GPX()

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Create points:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=1234))
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=1235))
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=1236))

    # You can add routes and waypoints, too...

    print 'Created GPX:', gpx.to_xml()

XML parsing
-----------

If lxml is available, then it will be used for XML parsing.
Otherwise minidom is used.
Note that lxml is 2-3 times faster so, if you can choose -- use it :)

Pull requests
-------------

OK, so you found a bug and fixed it. Before sending a pull request -- check that all tests are OK with python 2.6+ and python 3+.

Run all tests with:

    $ python -m unittest test
    $ python3 -m unittest test

Run only minidom parser tests with:

    $ python -m unittest test.MinidomTests
    $ python3 -m unittest test.MinidomTests

Run only lxml parser tests with:

    $ python -m unittest test.LxmlTests
    $ python3 -m unittest test.LxmlTests

Run a single test with:

    $ python -m unittest test.LxmlTests.test_method
    $ python3 -m unittest test.LxmlTests.test_method

GPX Version:
------------

gpx.py can parse and generate GPX 1.0 files. Note that the generated file will always be a valid XML document, but it may not be (strictly speaking) a valid GPX document. For example, if you set gpx.email to "my.email AT mail.com" the generated GPX tag won't confirm to the regex pattern. And the file won't be valid. Most applications will ignore such errors, but... Be aware of this!

License
-------

GPX.py is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

