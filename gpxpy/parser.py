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


class GPXParser:
    
    @staticmethod
    def strip_namespace(tag):
        if '}' in tag:
            return tag.split('}')[1]
        return tag
##        strippedtag = mod_etree.QName(tag).localname
##        return strippedtag

    @staticmethod
    def first_child(node, pattern):
        for node in node.getchildren():
            if GPXParser.strip_namespace(node.tag) == pattern:
                return node
        return None


    
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
        if text[:3] == "\xEF\xBB\xBF": #Remove utf-8 BOM
            text = text[3:]
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

        if mod_utils.PYTHON_VERSION[0] == '3':
            # In python 3 all strings are unicode and for some reason lxml
            # don't like unicode strings with XMLs declared as UTF-8:
            self.xml = self.xml.encode('utf-8')

        try:
            #self.xml_parser = XMLParser(self.xml)
            if "lxml" in str(mod_etree):
                root = mod_etree.XML(self.xml, mod_etree.XMLParser(remove_comments=True))
            else:
                root = mod_etree.XML(self.xml)

        except Exception as e:
            # The exception here can be a lxml or ElementTree exception.
            mod_logging.debug('Error in:\n%s\n-----------\n' % self.xml)
            mod_logging.exception(e)

            # The library should work in the same way regardless of the
            # underlying XML parser that's why the exception thrown
            # here is GPXXMLSyntaxException (instead of simply throwing the
            # original ElementTree or lxml exception e).
            #
            # But, if the user needs the original exception (lxml or ElementTree)
            # it is available with GPXXMLSyntaxException.original_exception:
            raise mod_gpx.GPXXMLSyntaxException('Error parsing XML: %s' % str(e), e)
        
        # node = self.xml_parser.dom

        if root is None:
            raise mod_gpx.GPXException('Document must have a `gpx` root node.')

        if version is None:
            version = root.attrib.get('version')

        mod_gpxfield.gpx_fields_from_xml(self.gpx, self.xml_parser, root, version)
        return self.gpx

