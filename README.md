[![Build Status](https://travis-ci.org/tkrajina/gpxpy.svg?branch=master)](https://travis-ci.org/tkrajina/gpxpy)
[![Coverage Status](https://coveralls.io/repos/github/tkrajina/gpxpy/badge.svg?branch=master)](https://coveralls.io/github/tkrajina/gpxpy?branch=master)

# gpxpy -- GPX file parser

This is a simple Python library for parsing and manipulating GPX files. GPX is an XML based format for GPS tracks.

You can see it in action on [my online GPS track editor and organizer](http://www.trackprofiler.com).

There is also a Golang port of gpxpy: [gpxgo](http://github.com/tkrajina/gpxgo).

See also [srtm.py](https://github.com/tkrajina/srtm.py) if your track lacks elevation data.

## Usage

```python
import gpxpy
import gpxpy.gpx

# Parsing an existing file:
# -------------------------

with open('tests/testdata/cerknicko-jezero.gpx', 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

for waypoint in gpx.waypoints:
    print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))

for route in gpx.routes:
    print('Route:')
    for point in route.points:
        print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

# There are many more utility methods and functions:
# You can manipulate/add/remove tracks, segments, points, waypoints and routes and
# get the GPX XML file from the resulting object:

print('GPX:', gpx.to_xml())

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

print('Created GPX:', gpx.to_xml())
```

## GPX version

gpx.py can parse and generate GPX 1.0 and 1.1 files. The generated file will always be a valid XML document, but it may not be (strictly speaking) a valid GPX document. For example, if you set gpx.email to "my.email AT mail.com" the generated GPX tag won't confirm to the regex pattern. And the file won't be valid. Most applications will ignore such errors, but... Be aware of this!

Be aware that the gpxpy object model *is not 100% equivalent* with the underlying GPX XML file schema. That's because the library object model works with both GPX 1.0 and 1.1.

For example, GPX 1.0 specified a `speed` attribute for every track point, but that was removed in GPX 1.1. If you parse GPX 1.0 and serialize back with `gpx.to_xml()` everything will work fine. But if you have a GPX 1.1 object, changes in the `speed` attribute will be lost after `gpx.to_xml()`. If you want to force using 1.0, you can `gpx.to_xml(version="1.0")`. Another possibility is to use `extensions` to save the speed in GPX 1.1.

## GPX extensions

gpx.py preserves GPX extensions. They are stored as [ElementTree](https://docs.python.org/2/library/xml.etree.elementtree.html#module-xml.etree.ElementTree) DOM objects. Extensions are part of GPX 1.1, and will be ignored when serializing a GPX object in a GPX 1.0 file.

## XML parsing

If lxml is available, then it will be used for XML parsing, otherwise minidom is used. Lxml is 2-3 times faster so, if you can choose -- use it.

The GPX version is automatically determined when parsing by reading the version attribute in the gpx node. If this attribute is not present then the version is assumed to be 1.0. A specific version can be forced by setting the `version` parameter in the parse function. Possible values for the 'version' parameter are `1.0`, `1.1` and `None`.

## GPX max speed

Gpxpy is a GPX parser and by using it you have acess to all the data from the original GPX file. The additional methods to calculate stats have some additional heuristics to remove common GPS errors. For example, to calculate `max_speed` it removes the top `5%` of speeds and points with nonstandard distance (those are usually GPS errors).

"Raw" max speed can be calculated with:

    moving_data = gpx.get_moving_data(raw=True)

## Pull requests

Branches:

* `master` contains the code of the latest release
* `dev` branch is where code for the next release should go.

Send your pull request against `dev`, not `master`!

Before sending a pull request -- check that all tests are OK.  Run all the static typing checks and unit tests with:

    $ make mypy-and-tests

Run a single test with:

    $ python3 -m unittest test.GPXTests.test_haversine_and_nonhaversine

Gpxpy runs only with python 3.6+. The code must have type hints and must pass all the mypy checks.

## GPX tools

Additional command-line tools for GPX files can be downloaded here <https://github.com/tkrajina/gpx-cmd-tools> or installed with:

```
pip install gpx-cmd-tools
```

## License

GPX.py is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

