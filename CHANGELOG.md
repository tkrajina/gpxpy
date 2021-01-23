# Changelog


## v1.4.2

* get_nearest_location(location) has the property that if 'location' is a point on the track, the point after 'location' on the track is returned <https://github.com/tkrajina/gpxpy/pull/203>
* parse bytes <https://github.com/tkrajina/gpxpy/issues/175#issuecomment-645074781>

## v1.4.1

* Division by zero fixed <https://github.com/tkrajina/gpxpy/issues/197>
* Consider microseconds when total_seconds o timedelta is requested <https://github.com/tkrajina/gpxpy/pull/196>
* Use list instead of getchildren for Python 3.9 compatibility <https://github.com/tkrajina/gpxpy/pull/192>
* utils.total_seconds() ignores microseconds <https://github.com/tkrajina/gpxpy/issues/201>

## v1.4.0

* Removed support for python2.* and python3.5
* Added typehints and with mypy checks
* Course computation <https://github.com/tkrajina/gpxpy/pull/156> <https://github.com/tkrajina/gpxpy/issues/155>
* Refactored haversine_distance for speed and use math.radians <https://github.com/tkrajina/gpxpy/pull/180>

## v1.3.5

* Rewrite parse_time so it understands time zones and microseconds <https://github.com/tkrajina/gpxpy/pull/152>
* Package version <https://github.com/tkrajina/gpxpy/pull/157>
* fix debug message <https://github.com/tkrajina/gpxpy/pull/166>
* Avoid the deprecated TestCase.assertEquals() API <https://github.com/tkrajina/gpxpy/pull/161>
* Add brackets for last print statement <https://github.com/tkrajina/gpxpy/pull/151>
* Add Python 3.7 classifier and test on CI <https://github.com/tkrajina/gpxpy/pull/147>
* Fixed problems with single quotes in xmlns

## v1.3.4

* Added custom schemaLocation support <https://github.com/tkrajina/gpxpy/pull/141>
* Division by zero in gpxinfo
* Missing tag(s) during parsing <https://github.com/tkrajina/gpxpy/issues/135>
* to_xml() fails with an empty extension element <https://github.com/tkrajina/gpxpy/issues/140>
* Setup.py: update classifiers, add python_requires and long_description <https://github.com/tkrajina/gpxpy/pull/142>

## v1.3.3

* Added avg time to gpxpnfo
* gpx.adjust_times for waypoints and routes <https://github.com/tkrajina/gpxpy/pull/129>
* added gpx.fill_time_data_with_regular_intervals <https://github.com/tkrajina/gpxpy/pull/127>

## v1.3.2

* Fix #123 by using Earth semi-major axis with 6378.137 km (WGS84) <https://github.com/tkrajina/gpxpy/issues/123>
* No assert error if can't calculate missing elevations <https://github.com/tkrajina/srtm.py/issues/25>

## v1.3.1

* Prefix format reserved for internal use <https://github.com/tkrajina/gpxpy/issues/117>

## v.1.3.0

* Logging exception fix <https://github.com/tkrajina/gpxpy/pull/112>
* Extension handling <https://github.com/tkrajina/gpxpy/pull/105>
* simplify polyline <https://github.com/tkrajina/gpxpy/pull/100>

## v1.2.0

* Remove timezone from timestam string <https://github.com/tkrajina/gpxpy/pull/77>
* gpxinfo: output times in seconds <https://github.com/tkrajina/gpxpy/pull/74>
* gpxinfo: `-m` for miles/feet <https://github.com/tkrajina/gpxpy/pull/108>
* Minor `get_speed` fix <https://github.com/tkrajina/gpxpy/pull/97>
* Lat/Lon must not have scientific notation <https://github.com/tkrajina/gpxpy/pull/96>
* Simplify polyline fix <https://github.com/tkrajina/gpxpy/pull/100>
* Fix unicode BOM behavior <https://github.com/tkrajina/gpxpy/pull/90>
* Named logger <https://github.com/tkrajina/gpxpy/pull/106>
* Remove minidom <https://github.com/tkrajina/gpxpy/pull/103>

## v.1.1.0

...
