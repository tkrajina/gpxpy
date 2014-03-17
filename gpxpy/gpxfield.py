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

from . import utils as mod_utils

class AbstractGPXField:
    def __init__(self, attribute_field=None):
        self.attribute_field = attribute_field

class GPXField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, tag=None):
        AbstractGPXField.__init__(self)
        self.name = name
        self.tag = tag or name

    def from_xml(self, parser, node):
        __node = parser.get_first_child(node, self.tag)
        return parser.get_node_data(__node)

    def to_xml(self, value):
        return mod_utils.to_xml(self.tag, content=value)

class GPXAttributeField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, attribute=None, type=None):
        AbstractGPXField.__init__(self, attribute_field=True)
        self.name = name
        self.attribute = attribute or name
        self.type = type

    def from_xml(self, parser, node):
        result = parser.get_node_attribute(node, self.attribute)
        if self.type:
            return self.type(result)
        return result

    def to_xml(self, value):
        return '%s="%s"' % (self.attribute, value)

class GPXDecimalField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, tag=None):
        AbstractGPXField.__init__(self)
        self.name = name
        self.tag = tag or name
        # TODO: Use value type like in GPXAttributeField!

    def from_xml(self, parser, node):
        __node = parser.get_first_child(node, self.tag)
        result = parser.get_node_data(__node)
        if result is None:
            return result
        return float(result)

    def to_xml(self, value):
        return mod_utils.to_xml(self.tag, content=str(value))

class GPXTimeField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, tag=None):
        AbstractGPXField.__init__(self)
        self.name = name
        self.tag = tag or name

    def from_xml(self, parser, node):
        from . import parser as mod_parser
        __node = parser.get_first_child(node, self.tag)
        return mod_parser.parse_time(parser.get_node_data(__node))

    def to_xml(self, value):
        from . import gpx as mod_gpx
        if value:
            return mod_utils.to_xml(self.tag, content=value.strftime(mod_gpx.DATE_FORMAT))
        return ''

class GPXComplexField(AbstractGPXField):
    def __init__(self, name, classs, tag=None):
        AbstractGPXField.__init__(self)
        self.name = name
        self.tag = tag or name
        self.classs = classs

    def from_xml(self, parser, node):
        result = self.classs()
        __node = parser.get_first_child(node, self.tag)
        gpx_fields_from_xml(result, parser, __node)
        return result

    def to_xml(self, value):
        return gpx_fields_to_xml(value, self.tag, value)

def init_gpx_fields(instance):
    for gpx_field in instance.__gpx_fields__:
        setattr(instance, gpx_field.name, None)

def gpx_fields_to_xml(instance, tag, xml):
    attributes = ''
    body = ''
    for gpx_field in instance.__gpx_fields__:
        value = getattr(instance, gpx_field.name)
        if gpx_field.attribute_field:
            attributes += ' ' + gpx_field.attribute + '="' + str(value) + '"'
        else:
            if value:
                body += gpx_field.to_xml(value)
    if tag:
        return '<' + tag + ( (' ' + attributes + '>') if attributes else '>' ) \
               + body \
               + '</' + tag + '>'
    return body

def gpx_fields_from_xml(instance, parser, node):
    for gpx_field in instance.__gpx_fields__:
        value = gpx_field.from_xml(parser, node)
        setattr(instance, gpx_field.name, value)
