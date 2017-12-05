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

from __future__ import print_function

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


class LXMLParser:
    """
    Used when lxml is available.
    """

    def __init__(self, xml):
        if not mod_etree:
            raise Exception('Cannot use LXMLParser without lxml installed')

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
        Parser may be lxml of minidom. If you set to None then lxml will be used if installed
        otherwise minidom.
        """
        self.init(xml_or_file)
        self.gpx = mod_gpx.GPX()
        self.xml_parser = None

    def init(self, xml_or_file):
        text = xml_or_file.read() if hasattr(xml_or_file, 'read') else xml_or_file
        if text[:3] == "\xEF\xBB\xBF": #Remove utf-8 Byte Order Mark (BOM) if present
            text = text[3:]
        self.xml = mod_utils.make_str(text)
        self.gpx = mod_gpx.GPX()

    def parse(self, version = None):
        """
        Parses the XML file and returns a GPX object.

        version may be '1.0', '1.1' or None (then it will be read from the gpx
        xml node if possible, if not then version 1.0 will be used).

        It will throw GPXXMLSyntaxException if the XML file is invalid or
        GPXException if the XML file is valid but something is wrong with the
        GPX data.
        """
        try:
            self.xml_parser = LXMLParser(self.xml)
            self.__parse_dom(version)

            return self.gpx
        except Exception as e:
            # The exception here can be a lxml or minidom exception.
            mod_logging.debug('Error in:\n%s\n-----------\n' % self.xml)
            mod_logging.exception(e)

            # The library should work in the same way regardless of the
            # underlying XML parser that's why the exception thrown
            # here is GPXXMLSyntaxException (instead of simply throwing the
            # original minidom or lxml exception e).
            #
            # But, if the user need the original exception (lxml or minidom)
            # it is available with GPXXMLSyntaxException.original_exception:
            raise mod_gpx.GPXXMLSyntaxException('Error parsing XML: %s' % str(e), e)

    def __parse_dom(self, version = None):
        node = self.xml_parser.get_first_child(name='gpx')

        if node is None:
            raise mod_gpx.GPXException('Document must have a `gpx` root node.')

        if version is None:
            version = self.xml_parser.get_node_attribute(node, 'version')

        mod_gpxfield.gpx_fields_from_xml(self.gpx, self.xml_parser, node, version)
