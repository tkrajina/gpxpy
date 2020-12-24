#!/usr/bin/env python3

"""
Example File for gpxpy waypoints

@author: Marcel verpaalen
"""

import gpxpy
import gpxpy.gpx

from typing import *

gpx = gpxpy.gpx.GPX()
gpx.name = 'Aanlegplaatsen'
gpx.description = 'Marrekrite aanlegplaatsen'

# adding 2 waypoints
gpx_wps = gpxpy.gpx.GPXWaypoint()
gpx_wps.latitude = 52.966346
gpx_wps.longitude = 5.515595
gpx_wps.symbol = "Marks-Mooring-Float"
gpx_wps.name = "FL16A Hammigegreft (Damwand)"
gpx_wps.description = "Vaarwater GRUTTE GAASTMAR"
gpx.waypoints.append(gpx_wps)

gpx_wps2 = gpxpy.gpx.GPXWaypoint()
gpx_wps2.latitude = 52.967148
gpx_wps2.longitude = 5.631813
gpx_wps2.symbol = "Marks-Mooring-Float"
gpx_wps2.name = "L20 Moalsek (Damwand))"
gpx_wps2.description = "Vaarwater JELTESLEAT"
gpx.waypoints.append(gpx_wps2)


print('Created GPX:', gpx.to_xml())