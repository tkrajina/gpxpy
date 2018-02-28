# -*- coding: utf-8 -*-

# Copyright 2011 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging as mod_logging

try:
    import lxml.etree as mod_etree
except:
    try:
        import xml.etree.cElementTree as mod_etree
    except:
        import xml.etree.ElementTree as mod_etree

from . import gpx as mod_gpx
from . import utils as mod_utils
from . import gpxfield as mod_gpxfield

log = mod_logging.getLogger(__name__)

class XMLParser:
    """
    Used when lxml is available.
    """

    def __init__(self, xml):
        if mod_utils.PYTHON_VERSION[0] == '3':
            # In python 3 all strings are unicode and for some reason lxml
            # don't like unicode strings with XMLs declared as UTF-8:
            self.xml = xml.encode('utf-8')
        else:
            self.xml = xml

        self.dom = mod_etree.XML(self.xml)
        # get the namespace
        # self.ns = self.dom.nsmap.get(None)

    def get_first_child(self, node=None, name=None):
        if node is None:
            if name:
                if self.get_node_name(self.dom) == name:
                    return self.dom
            return self.dom

        children = node.getchildren()

        if not children:
            return None

        if name:
            for node in children:
                if self.get_node_name(node) == name:
                    return node
            return None

        return children[0]

    def get_node_name(self, node):
        if callable(node.tag):
            tag = str(node.tag())
        else:
            tag = str(node.tag)
        if '}' in tag:
            return tag.split('}')[1]
        return tag

    def get_children(self, node=None):
        if node is None:
            node = self.dom
        return node.getchildren()

    def get_node_data(self, node):
        if node is None:
            return None

        return node.text

    def get_node_attribute(self, node, attribute):
        if node is None:
            return None
        return node.attrib.get(attribute)


class GPXParser:
    def __init__(self, xml_or_file=None):
        """
        Initialize new GPXParser instance.

        Arguments:
            xml_or_file: string or file object containing the gpx
                formatted xml
            
        """
        self.init(xml_or_file)
        self.gpx = mod_gpx.GPX()
        self.xml_parser = None

    def init(self, xml_or_file):
        """
        Store the XML and remove utf-8 Byte Order Mark if present.

        Args:
            xml_or_file: string or file object containing the gpx
                formatted xml
            
        """
        text = xml_or_file.read() if hasattr(xml_or_file, 'read') else xml_or_file
        self.xml = mod_utils.make_str(text)

    def parse(self, version = None):
        """
        Parse the XML and return a GPX object.

        Args:
            version: str or None indicating the GPX Schema to use.
                Options are '1.0', '1.1' and None. When version is None
                the version is read from the file or falls back on 1.0. 
            
        Returns:
            A GPX object loaded from the xml

        Raises:
            GPXXMLSyntaxException: XML file is invalid
            GPXException: XML is valid but GPX data contains errors
            
        """
        try:
            self.xml_parser = XMLParser(self.xml)

        except Exception as e:
            # The exception here can be a lxml or ElementTree exception.
            log.debug('Error in:\n%s\n-----------\n' % self.xml)
            log.exception(e)

            # The library should work in the same way regardless of the
            # underlying XML parser that's why the exception thrown
            # here is GPXXMLSyntaxException (instead of simply throwing the
            # original ElementTree or lxml exception e).
            #
            # But, if the user needs the original exception (lxml or ElementTree)
            # it is available with GPXXMLSyntaxException.original_exception:
            raise mod_gpx.GPXXMLSyntaxException('Error parsing XML: %s' % str(e), e)
        
        node = self.xml_parser.get_first_child(name='gpx')

        if node is None:
            raise mod_gpx.GPXException('Document must have a `gpx` root node.')

        if version is None:
            version = self.xml_parser.get_node_attribute(node, 'version')

        mod_gpxfield.gpx_fields_from_xml(self.gpx, self.xml_parser, node, version)
        return self.gpx

