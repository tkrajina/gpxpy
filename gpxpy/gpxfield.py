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

from . import utils as mod_utils

class AbstractGPXField:
    def __init__(self, attribute_field=None, is_list=None):
        self.attribute_field = attribute_field
        self.is_list = is_list

# TODO: better hierarchy for GPXFields

class GPXField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, tag=None, type=None, possible=None, mandatory=None):
        AbstractGPXField.__init__(self)
        self.name = name
        self.tag = tag or name
        self.type = type
        self.possible = possible
        self.mandatory = mandatory

    def from_xml(self, parser, node):
        __node = parser.get_first_child(node, self.tag)
        result = parser.get_node_data(__node)

        if result is None:
            if self.mandatory:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('%s is mandatory in %s' % (self.name, self.tag))
            return None

        if self.type:
            try:
                result = self.type(result)
            except Exception as e:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('Invalid value for <%s>... %s (%s)' % (self.tag, result, e))

        if self.possible:
            if not (result in self.possible):
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('Invalid value "%s", possible: %s' % (result, self.possible))

        return result

    def to_xml(self, value):
        return mod_utils.to_xml(self.tag, content=value)

class GPXAttributeField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, attribute=None, type=None, mandatory=None):
        AbstractGPXField.__init__(self, attribute_field=True)
        self.name = name
        self.attribute = attribute or name
        self.type = type
        self.mandatory = mandatory

    def from_xml(self, parser, node):
        result = parser.get_node_attribute(node, self.attribute)

        if result is None:
            if self.mandatory:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('%s is mandatory in element=%s' % (self.attribute, node))
            return None

        if self.type:
            result = self.type(result)

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
    # This class should probably be broken into GPXComplexField and 
    # GPXComplexListFielt depending on self.is_list

    def __init__(self, name, classs, tag=None, is_list=None):
        AbstractGPXField.__init__(self, is_list=is_list)
        self.name = name
        self.tag = tag or name
        self.classs = classs

    def from_xml(self, parser, node):
        if self.is_list:
            result = []
            for child_node in parser.get_children(node):
                if parser.get_node_name(child_node) == self.tag:
                    result.append(gpx_fields_from_xml(self.classs, parser, child_node))
            return result
        else:
            __node = parser.get_first_child(node, self.tag)
            return gpx_fields_from_xml(self.classs, parser, __node)

    def to_xml(self, value):
        if self.is_list:
            result = ''
            for obj in value:
                result += gpx_fields_to_xml(obj, self.tag)
            return result
        else:
            return gpx_fields_to_xml(value, self.tag)

def init_gpx_fields(instance):
    for gpx_field in instance.__gpx_fields__:
        setattr(instance, gpx_field.name, None)

def gpx_fields_to_xml(instance, tag):
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

def gpx_fields_from_xml(class_or_instance, parser, node):
    if mod_inspect.isclass(class_or_instance):
        result = class_or_instance()
    else:
        result = class_or_instance
    for gpx_field in result.__gpx_fields__:
        value = gpx_field.from_xml(parser, node)
        setattr(result, gpx_field.name, value)
    return result
