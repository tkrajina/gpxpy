# -*- coding: utf-8 -*-

import xml.dom.minidom as mod_minidom


def join_gpxs(xmls):
    """
    Utility to join GPX files without parsing them with gpxpy
    """
    result = None

    wpt_elements = []
    rte_elements = []
    trk_elements = []

    for xml in xmls:
        dom = mod_minidom.parseString(xml)
        if not result:
            result = dom

        gpx_node = _find_gpx_node(dom)
        if gpx_node:
            for child_node in gpx_node.childNodes:
                if child_node.nodeName == 'wpt':
                    wpt_elements.append(child_node)
                    gpx_node.removeChild(child_node)
                elif child_node.nodeName == 'rte':
                    rte_elements.append(child_node)
                    gpx_node.removeChild(child_node)
                elif child_node.nodeName == 'trk':
                    trk_elements.append(child_node)
                    gpx_node.removeChild(child_node)

    gpx_node = _find_gpx_node(result)
    if gpx_node:
        for wpt_element in wpt_elements:
            gpx_node.appendChild(wpt_element)
        for rte_element in rte_elements:
            gpx_node.appendChild(rte_element)
        for trk_element in trk_elements:
            gpx_node.appendChild(trk_element)

    return result.toxml()


def _find_gpx_node(dom):
    for gpx_candidate_node in dom.childNodes:
        if gpx_candidate_node.nodeName == 'gpx':
            return gpx_candidate_node
    return None
