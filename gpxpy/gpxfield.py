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
    for date_format in mod_gpx.DATE_FORMATS:
        try:
            return mod_datetime.datetime.strptime(string, date_format)
        except ValueError as e:
            pass
    raise GPXException('Invalid time: %s' % string)

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
        from . import gpx as mod_gpx
        if not string:
            return None
        if 'T' in string:
            string = string.replace('T', ' ')
        if 'Z' in string:
            string = string.replace('Z', '')
        for date_format in mod_gpx.DATE_FORMATS:
            try:
                return mod_datetime.datetime.strptime(string, date_format)
            except ValueError as e:
                pass
        return None
    def to_string(self, time):
        from . import gpx as mod_gpx
        return time.strftime(mod_gpx.DATE_FORMAT) if time else None

INT_TYPE = IntConverter()
FLOAT_TYPE = FloatConverter()
TIME_TYPE = TimeConverter()

class AbstractGPXField:
    def __init__(self, attribute_field=None, is_list=None):
        self.attribute_field = attribute_field
        self.is_list = is_list
        self.attribute = False

# TODO: better hierarchy for GPXFields

class GPXField(AbstractGPXField):
    """
    Used for to (de)serialize fields with simple field<->xml_tag mapping.
    """
    def __init__(self, name, tag=None, attribute=None, type=None, possible=None, mandatory=None):
        AbstractGPXField.__init__(self)
        self.name = name
        if tag and attribute:
            raise GPXException('Only tag *or* attribute may be given!')
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

    def from_xml(self, parser, node, version):
        if self.attribute:
            result = parser.get_node_attribute(node, self.attribute)
        else:
            __node = parser.get_first_child(node, self.tag)
            result = parser.get_node_data(__node)

        if result is None:
            if self.mandatory:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('%s is mandatory in %s' % (self.name, self.tag))
            return None

        if self.type_converter:
            try:
                result = self.type_converter.from_string(result)
            except Exception as e:
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('Invalid value for <%s>... %s (%s)' % (self.tag, result, e))

        if self.possible:
            if not (result in self.possible):
                from . import gpx as mod_gpx
                raise mod_gpx.GPXException('Invalid value "%s", possible: %s' % (result, self.possible))

        return result

    def to_xml(self, value):
        if self.attribute:
            return '%s="%s"' % (self.attribute, value)
        else:
            if self.type_converter:
                value = self.type_converter.to_string(value)
            return mod_utils.to_xml(self.tag, content=value)

class GPXComplexField(AbstractGPXField):
    # This class should probably be broken into GPXComplexField and 
    # GPXComplexListFielt depending on self.is_list

    def __init__(self, name, classs, tag=None, is_list=None):
        AbstractGPXField.__init__(self, is_list=is_list)
        self.name = name
        self.tag = tag or name
        self.classs = classs

    def from_xml(self, parser, node, version):
        if self.is_list:
            result = []
            for child_node in parser.get_children(node):
                if parser.get_node_name(child_node) == self.tag:
                    result.append(gpx_fields_from_xml(self.classs, parser, child_node, version))
            return result
        else:
            __node = parser.get_first_child(node, self.tag)
            if __node is None:
                return None
            return gpx_fields_from_xml(self.classs, parser, __node, version)

    def to_xml(self, value):
        if self.is_list:
            result = ''
            for obj in value:
                result += gpx_fields_to_xml(obj, self.tag)
            return result
        else:
            return gpx_fields_to_xml(value, self.tag)

def init_gpx_fields(instance):
    for gpx_field in instance.gpx_10_fields:
        setattr(instance, gpx_field.name, None)

def gpx_fields_to_xml(instance, tag):
    attributes = ''
    body = ''
    for gpx_field in instance.gpx_10_fields:
        value = getattr(instance, gpx_field.name)
        if gpx_field.attribute:
            attributes += ' %s="%s"' % (gpx_field.attribute, mod_utils.make_str(value))
        else:
            if value:
                body += gpx_field.to_xml(value)
    if tag:
        return '<' + tag + ( (' ' + attributes + '>') if attributes else '>' ) \
               + body \
               + '</' + tag + '>'
    return body

def gpx_fields_from_xml(class_or_instance, parser, node, version):
    if mod_inspect.isclass(class_or_instance):
        result = class_or_instance()
    else:
        result = class_or_instance

    fields = result.gpx_10_fields
    if version == '1.1':
        fields = result.gpx_11_fields

    for gpx_field in fields:
        value = gpx_field.from_xml(parser, node, version)
        setattr(result, gpx_field.name, value)

    return result

def gpx_fields_fill_default_values(classs):
    for field in classs.gpx_10_fields:
        if field.is_list:
            setattr(classs, field.name, [])
        else:
            setattr(classs, field.name, None)
