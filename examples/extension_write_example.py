#!/usr/bin/env python3

"""
Example File for gpxpy waypoints

@author: Marcel verpaalen
"""

import gpxpy
import gpxpy.gpx

try:
    # Load LXML or fallback to cET or ET 
    import lxml.etree as mod_etree  # type: ignore
except:
    try:
        import xml.etree.cElementTree as mod_etree # type: ignore
    except:
        import xml.etree.ElementTree as mod_etree # type: ignore

gpx = gpxpy.gpx.GPX()
gpx.name = 'Aanlegplaatsen'
gpx.description = 'Marrekrite aanlegplaatsen'

#definition of extension
namespace = '{opencpn}'

#create extension element
root = mod_etree.Element(namespace + 'scale_min_max')
#mod_etree.SubElement(root, namespace + 'UseScale')
root.attrib['UseScale'] = "true"
root.attrib['ScaleMin'] = "50000"
root.attrib['ScaleMax'] = "0"
rootElement2 = mod_etree.Element(namespace + 'arrival_radius')
rootElement2.text = '0.050'

#add extension to header
nsmap = {namespace[1:-1]:'http://www.opencpn.org'}
gpx.nsmap =nsmap

# adding 2 waypoints
gpx_wps = gpxpy.gpx.GPXWaypoint()
gpx_wps.latitude = 52.966346
gpx_wps.longitude = 5.515595
gpx_wps.symbol = "Marks-Mooring-Float"
gpx_wps.name = "FL16A Hammigegreft (Damwand)"
gpx_wps.description = "Vaarwater GRUTTE GAASTMAR"
#add the extension to the waypoint
gpx_wps.extensions.append(root)
gpx.waypoints.append(gpx_wps)

gpx_wps2 = gpxpy.gpx.GPXWaypoint()
gpx_wps2.latitude = 52.967148
gpx_wps2.longitude = 5.631813
gpx_wps2.symbol = "Marks-Mooring-Float"
gpx_wps2.name = "L20 Moalsek (Damwand))"
gpx_wps2.description = "Vaarwater JELTESLEAT"

#add the extensions to the waypoint
gpx_wps2.extensions.append(root)
gpx_wps2.extensions.append(rootElement2)
gpx.waypoints.append(gpx_wps2)

print('Created GPX:', gpx.to_xml())