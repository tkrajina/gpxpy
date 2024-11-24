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
import re as mod_re

from typing import cast, Union, AnyStr, IO, Optional

try:
    import xml.etree.cElementTree as mod_etree
except ImportError:
    import xml.etree.ElementTree as mod_etree # type: ignore

from . import gpx as mod_gpx
from . import utils as mod_utils
from . import gpxfield as mod_gpxfield

log = mod_logging.getLogger(__name__)

class GPXParser:
    """
    Parse the XML and provide new GPX instance.

    Methods:
        __init__: initialize new instance
        init: format XML
        parse: parse XML, build tree, build GPX

    Attributes:
        gpx: GPX instance of the most recently parsed XML
        xml: string containing the XML text

    """

    def __init__(self, xml_or_file: Union[AnyStr, IO[str]]) -> None:
        """
        Initialize new GPXParser instance.

        Arguments:
            xml_or_file: string or file object containing the gpx
                formatted xml

        """
        self.xml = ""
        self.init(xml_or_file)
        self.gpx = mod_gpx.GPX()

    def init(self, xml_or_file: Union[AnyStr, IO[str]]) -> None:
        """
        Store the XML and remove utf-8 Byte Order Mark if present.

        Args:
            xml_or_file: string or file object containing the gpx
                formatted xml

        """
        text = xml_or_file.read() if hasattr(xml_or_file, 'read') else xml_or_file # type: ignore
        if isinstance(text, bytes):
            text = text.decode()
        self.xml = mod_utils.make_str(cast(str, text))

    def parse(self, version: Optional[str]=None) -> mod_gpx.GPX:
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
        # Build prefix map for reserialization and extension handlings
        for namespace in mod_re.findall(r'\sxmlns:?[^=]*="[^"]+"', self.xml):
            prefix, _, URI = namespace[6:].partition('=')
            prefix = prefix.lstrip(':')
            if prefix == '':
                prefix = 'defaultns'  # alias default for easier handling
            else:
                if prefix.startswith("ns"):
                    mod_etree.register_namespace("noglobal_" + prefix, URI.strip('"'))
                else:
                    mod_etree.register_namespace(prefix, URI.strip('"'))
            self.gpx.nsmap[prefix] = URI.strip('"')

        schema_loc = mod_re.search(r'\sxsi:schemaLocation="[^"]+"', self.xml)
        if schema_loc:
            _, _, value = schema_loc.group(0).partition('=')
            self.gpx.schema_locations = value.strip('"').split()

        # Remove default namespace to simplify processing later
        self.xml = mod_re.sub(r"""\sxmlns=(['"])[^'"]+\1""", '', self.xml, count=1)

        # Build tree
        try:
            root = mod_etree.XML(self.xml)
        except Exception as e:
            log.debug('Error in:\n%s\n-----------\n', self.xml, exc_info=True)
            raise mod_gpx.GPXXMLSyntaxException(f'Error parsing XML: {e}', e)

        if root is None or root.tag.lower() != 'gpx':
            raise mod_gpx.GPXException('Document must have a `gpx` root node.')

        if version is None:
            version = root.get('version')
        if not version:
            version = ""

        mod_gpxfield.gpx_fields_from_xml(self.gpx, root, version)
        return self.gpx