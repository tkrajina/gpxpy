import sys
import codecs as mod_codecs

import gpxpy.parser as mod_parser


PYTHON_VERSION = sys.version.split(' ')[0]


def custom_open(filename, encoding=None):
    if PYTHON_VERSION[0] == '3':
        return open(filename, encoding=encoding)
    elif encoding == 'utf-8':
        mod_codecs.open(filename, encoding='utf-8')
    return open(filename)


def parse(file, encoding=None, version=None):
    f = custom_open('test_files/%s' % file, encoding=encoding)

    parser = mod_parser.GPXParser(f)
    gpx = parser.parse(version)
    f.close()

    if not gpx:
        print('Parser error: %s' % parser.get_error())

    return gpx


def reparse(gpx):
    xml = gpx.to_xml()

    parser = mod_parser.GPXParser(xml)
    gpx = parser.parse()

    if not gpx:
        print('Parser error while reparsing: %s' % parser.get_error())

    return gpx


def equals(object1, object2, ignore=None):
    """ Testing purposes only """

    if not object1 and not object2:
        return True

    if not object1 or not object2:
        print('Not obj2')
        return False

    if not object1.__class__ == object2.__class__:
        print('Not obj1')
        return False

    attributes = []
    for attr in dir(object1):
        if not ignore or attr not in ignore:
            if not hasattr(object1, '__call__') and not attr.startswith('_'):
                if attr not in attributes:
                    attributes.append(attr)

    for attr in attributes:
        attr1 = getattr(object1, attr)
        attr2 = getattr(object2, attr)

        if attr1 == attr2:
            return True

        if not attr1 and not attr2:
            return True
        if not attr1 or not attr2:
            print('Object differs in attribute %s (%s - %s)' % (attr, attr1, attr2))
            return False

        if not equals(attr1, attr2):
            print('Object differs in attribute %s (%s - %s)' % (attr, attr1, attr2))
            return None

    return True


def elements_equal(e1, e2):

    if node_strip(e1.tag) != node_strip(e2.tag):
        return False
    if node_strip(e1.text) != node_strip(e2.text):
        return False
    if node_strip(e1.tail) != node_strip(e2.tail):
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))


def print_etree(e1, indent=''):
    tag = ['{0}tag: |{1}|\n'.format(indent, e1.tag)]
    for att, value in e1.attrib.items():
        tag.append('{0}-att: |{1}| = |{2}|\n'.format(indent, att, value))
    tag.append('{0}-text: |{1}|\n'.format(indent, e1.text))
    tag.append('{0}-tail: |{1}|\n'.format(indent, e1.tail))
    for subelem in e1:
        tag.append(print_etree(subelem, indent + '__|'))
    return ''.join(tag)


def node_strip(text):
    if text is None:
        return ''
    return text.strip()


def get_dom_node(dom, path):
    path_parts = path.split('/')
    result = dom
    for path_part in path_parts:
        if '[' in path_part:
            tag_name = path_part.split('[')[0]
            n = int(path_part.split('[')[1].replace(']', ''))
        else:
            tag_name = path_part
            n = 0

        candidates = []
        for child in result.childNodes:
            if child.nodeName == tag_name:
                candidates.append(child)

        try:
            result = candidates[n]
        except Exception:
            raise Exception('Can\'t fint %sth child of %s' % (n, path_part))

    return result
