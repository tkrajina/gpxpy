# -*- coding: utf-8 -*-

# Copyright 2014 Tomo Krajina
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

import inspect as mod_inspect
import datetime as mod_datetime
import re as mod_re

from . import utils as mod_utils


class GPXFieldTypeConverter:
    def __init__(self, from_string, to_string):
        self.from_string = from_string
        self.to_string = to_string


def parse_time(string):
    from . import gpx as mod_gpx
    if not string:
        return None
    if 'T' in string:
        string = string.replace('T', ' ')
    if 'Z' in string:
        string = string.replace('Z', '')
    if '.' in string:
        string = string.split('.')[0]
    if len(string) > 19:
        # remove the timezone part
        d = max(string.rfind('+'), string.rfind('-'))
        string = string[0:d]
    if len(string) < 19:
        # string has some single digits
        p = '^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}).*$'
        s = mod_re.findall(p, string)
        if len(s) > 0:
            string = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'\
                .format(*[int(x) for x in s[0]])
    for date_format in mod_gpx.DATE_FORMATS:
        try:
            return mod_datetime.datetime.strptime(string, date_format)
        except ValueError:
            pass
    raise mod_gpx.GPXException('Invalid time: {0}'.format(string))


# ----------------------------------------------------------------------------------------------------
# Type converters used to convert from/to the string in the XML:
# ----------------------------------------------------------------------------------------------------


class FloatConverter:
    def __init__(self):
        self.from_string = lambda string : None if string is None else float(string.strip())
        self.to_string =   lambda flt    : str(flt)


class IntConverter:
    def __init__(self):
        self.from_string = lambda string : None if string is None else int(string.strip())
        self.to_string =   lambda flt    : str(flt)


class TimeConverter:
    def from_string(self, string):
        try:
            return parse_time(string)
        except:
            return None
    def to_string(self, time):
        from . import gpx as mod_gpx
        return time.strftime(mod_gpx.DATE_FORMAT) if time else None


INT_TYPE = IntConverter()
FLOAT_TYPE = FloatConverter()
TIME_TYPE = TimeConverter()


# ----------------------------------------------------------------------------------------------------
# Field converters:
# ----------------------------------------------------------------------------------------------------


class AbstractGPXField:
    def __init__(self, attribute_field=None, is_list=None):
        self.attribute_field = attribute_field
        self.is_list = is_list
        self.attribute = False

    def from_xml(self, node, version):
        raise Exception('Not implemented')

    def to_xml(self, value, version, nsmap):
        raise Exception('Not implemented')


class GPXField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, tag=None, attribute=None, type=None, possible=None, mandatory=None):
        AbstractGPXField.__init__(self)
        self.name = name
        if tag and attribute:
            from . import gpx as mod_gpx
            raise mod_gpx.GPXException('Only tag *or* attribute may be given!')
        if attribute:
            self.tag = None
            self.attribute = name if attribute is True else attribute
        elif tag:
            self.tag = name if tag is True else tag
            self.attribute = None
        else:
            self.tag = name
            self.attribute = None
        self.type_converter = type
        self.possible = possible
        self.mandatory = mandatory

    def from_xml(self, node, version):
        if self.attribute:
            if node is not None:
                result = node.get(self.attribute)
        else:
            __node = node.find(self.tag)
            if __node is not None:
                result = __node.text
            else:
                result = None
        if result is None:
            if self.mandatory:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('{0} is mandatory in {1} (got {2})'.format(self.name, self.tag, result))
            return None

        if self.type_converter:
            try:
                result = self.type_converter.from_string(result)
            except Exception as e:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('Invalid value for <{0}>... {1} ({2})'.format(self.tag, result, e))

        if self.possible:
            if not (result in self.possible):
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('Invalid value "{0}", possible: {1}'.format(result, self.possible))

        return result

    def to_xml(self, value, version, nsmap=None, prettyprint=True, indent=''):
        if value is None:
            return ''
        if not prettyprint:
            indent = ''
        if self.attribute:
            return '{0}="{1}"'.format(self.attribute, mod_utils.make_str(value))
        elif self.type_converter:
            value = self.type_converter.to_string(value)
        return mod_utils.to_xml(self.tag, content=value, escape=True)


class GPXComplexField(AbstractGPXField):
    def __init__(self, name, classs, tag=None, is_list=None):
        AbstractGPXField.__init__(self, is_list=is_list)
        self.name = name
        self.tag = tag or name
        self.classs = classs

    def from_xml(self, node, version):
        if self.is_list:
            result = []
            for child in node:
                if child.tag == self.tag:
                    result.append(gpx_fields_from_xml(self.classs, child, version))
            return result
        else:
            field_node = node.find(self.tag)
            if field_node is None:
                return None
            return gpx_fields_from_xml(self.classs, field_node, version)

    def to_xml(self, value, version, nsmap=None, prettyprint=True, indent=''):
        if not prettyprint:
            indent = ''
        if self.is_list:
            result = []
            for obj in value:
                result.append(gpx_fields_to_xml(obj, self.tag, version, nsmap=nsmap, prettyprint=prettyprint, indent=indent))
            return ''.join(result)
        else:
            return gpx_fields_to_xml(value, self.tag, version, prettyprint=prettyprint, indent=indent)


class GPXEmailField(AbstractGPXField):
    """
    Converts GPX1.1 email tag group from/to string.
    """
    def __init__(self, name, tag=None):
        #Call super().__init__?
        AbstractGPXField.__init__(self, is_list=False)
        #self.attribute = False
        #self.is_list = False
        self.name = name
        self.tag = tag or name

    def from_xml(self, node, version):
        """
        Extract email address.

        Args:
            node: ETree node with child node containing self.tag
            version: str of the gpx output version "1.0" or "1.1"

        Returns:
            A string containing the email address.
        """
        email_node = node.find(self.tag)

        email_id = email_node.get('id')
        email_domain = email_node.get('domain')

        return '{0}@{1}'.format(email_id, email_domain)

    def to_xml(self, value, version, nsmap=None, prettyprint=True, indent=''):
        """
        Write email address to XML

        Args:
            value: str representing an email address
            version: str of the gpx output version "1.0" or "1.1"

        Returns:
            None if value is empty or str of XML representation of the
            address. Representation starts with a \n.
        """
        if not value:
            return ''

        if not prettyprint:
            indent = ''
            
        if '@' in value:
            pos = value.find('@')
            email_id = value[:pos]
            email_domain = value[pos+1:]
        else:
            email_id = value
            email_domain = 'unknown'

        return '\n<' + indent + '{0} id="{1}" domain="{2}" />'.format(self.tag, email_id, email_domain)


class GPXExtensionsField(AbstractGPXField):
    """
    GPX1.1 extensions <extensions>...</extensions> key-value type.
    """
    def __init__(self, name, tag=None):
        # Call super().__init__?
        AbstractGPXField.__init__(self, is_list=False)
        #self.attribute = False
        self.name = name
        #self.is_list = False
        self.tag = tag or 'extensions'

    def from_xml(self, node, version):
        result = []
        extensions_node = node.find(self.tag)

        if extensions_node is None:
            return result
        
        ## change to deepcopy
        for child in extensions_node:
            result.append(child)

        return result

    def _resolve_prefix(self, qname, nsmap):
        if nsmap is not None:
            uri, _, localname = qname.partition("}")
            uri = uri.lstrip("{")
            qname = uri + ':' + localname
            for prefix, namespace in nsmap.items():
                if uri == namespace:
                    qname = prefix + ':' + localname
                    break
        return qname

    def _ETree_to_xml(self, node, nsmap=None, prettyprint=True, indent=''):
        """
        Serialize ETree element and all subelements.

        Creates a string of the ETree and all children. The prefixes are
        resolved through the nsmap for easier to read XML.

        Args:
            node: ETree with the extension data
            version: string of GPX version, must be 1.1
            nsmap: dict of prefixes and URIs
            prettyprint: boolean, when true, indent line
            indent: string prepended to tag, usually 2 spaces per level

        Returns:
            string with all the prefixed tags and data for the node
            and its children as XML.
        
        """
        if not prettyprint:
            indent = ''

        # Build element tag and text
        result = []
        prefixedname = self._resolve_prefix(node.tag, nsmap)
        result.append('\n' + indent + '<' + prefixedname)
        for attrib, value in node.attrib.items():
            attrib = self._resolve_prefix(attrib, nsmap)
            result.append(' {0}="{1}"'.format(attrib, value))
        result.append('>' + node.text.strip())

        # Build subelement nodes
        for child in node:
            result.append(self._ETree_to_xml(child, nsmap, prettyprint=prettyprint, indent=indent+'  '))

        # Add tail and close tag
        tail = node.tail
        if tail is not None:
            tail = tail.strip()
        else:
            tail = ''
        if len(node) > 0:
            result.append('\n' + indent)
        result.append('</' + prefixedname + '>' + tail)
        
        return ''.join(result)

    def to_xml(self, value, version, nsmap=None, prettyprint=True, indent=''):
        """
        Serialize list of ETree.

        Creates a string of all the ETrees in the list. The prefixes are
        resolved through the nsmap for easier to read XML.

        Args:
            value: list of ETrees with the extension data
            version: string of GPX version, must be 1.1
            nsmap: dict of prefixes and URIs
            prettyprint: boolean, when true, indent line
            indent: string prepended to tag, usually 2 spaces per level

        Returns:
            string with all the prefixed tags and data for each node
            as XML.
        """
        if not prettyprint:
            indent = ''
        if not value or version != "1.1":
            return ''
        result = []
        result.append('\n' + indent + '<' + self.tag + '>')
        for extension in value:
            result.append(self._ETree_to_xml(extension, nsmap, prettyprint=prettyprint, indent=indent+'  '))
        result.append('\n' + indent + '</' + self.tag + '>')
        return ''.join(result)
    

        


# ----------------------------------------------------------------------------------------------------
# Utility methods:
# ----------------------------------------------------------------------------------------------------


def gpx_fields_to_xml(instance, tag, version, custom_attributes=None, nsmap=None, prettyprint=True, indent=''):
    fields = instance.gpx_10_fields
    if version == '1.1':
        fields = instance.gpx_11_fields

    tag_open = bool(tag)
    body = []
    if tag:
        body.append('\n<' + tag)
        if tag == 'gpx':  # write nsmap in root node
            body.append(' xmlns="{0}"'.format(nsmap['defaultns']))
            for prefix, URI in nsmap.items():
                if prefix != 'defaultns':
                    body.append(' xmlns:{0}="{1}"'.format(prefix, URI))
        if custom_attributes:
            for key, value in custom_attributes.items():
                body.append(' {0}="{1}"'.format(key, mod_utils.make_str(value)))
    suppressuntil = ''
    for gpx_field in fields:
        if isinstance(gpx_field, str):
            # strings indicate tags with subelements
            if suppressuntil:
                if suppressuntil == gpx_field:
                    suppressuntil = ''
            else:
                if ':' in gpx_field:
                    dependents = gpx_field.split(':')
                    gpx_field = dependents.pop(0)
                    suppressuntil = '/' + gpx_field
                    for dep in dependents:
                        if getattr(instance, dep.lstrip('@')):
                            suppressuntil = ''
                            break
                if not suppressuntil:
                    if tag_open:
                        body.append('>')
                        tag_open = False
                    if gpx_field[0] == '/':
                        body.append('<{0}>'.format(gpx_field))
                    else:
                        body.append('\n<{0}'.format(gpx_field))
                        tag_open = True
        elif not suppressuntil:
            value = getattr(instance, gpx_field.name)
            if gpx_field.attribute:
                body.append(' ' + gpx_field.to_xml(value, version, nsmap))
            elif value is not None:
                if tag_open:
                    body.append('>')
                    tag_open = False
                xml_value = gpx_field.to_xml(value, version, nsmap)
                if xml_value:
                    body.append(xml_value)

    if tag:
        if tag_open:
            body.append('>')
        body.append('</' + tag + '>')

    return ''.join(body)


def gpx_fields_from_xml(class_or_instance, node, version):
    if mod_inspect.isclass(class_or_instance):
        result = class_or_instance()
    else:
        result = class_or_instance

    fields = result.gpx_10_fields
    if version == '1.1':
        fields = result.gpx_11_fields

    node_path = [ node ]

    for gpx_field in fields:
        current_node = node_path[-1]
        if isinstance (gpx_field, str):
            gpx_field = gpx_field.partition(':')[0]
            if gpx_field.startswith('/'):
                node_path.pop()
            else:
                if current_node is None:
                    node_path.append(None)
                else:
                    node_path.append(current_node.find(gpx_field))
        else:
            if current_node is not None:
                value = gpx_field.from_xml(current_node, version)
                setattr(result, gpx_field.name, value)
            elif gpx_field.attribute:
                value = gpx_field.from_xml(node, version)
                setattr(result, gpx_field.name, value)

    return result
