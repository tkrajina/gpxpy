import xml.dom.minidom as mod_minidom

def get_children_by_tag_name(node, tag_name):
    result = []
    for child in node.childNodes:
        if child.nodeName == tag_name:
            result.append(child)
    return result

def get_indented(indentation, string):
    result = ''
    for i in range(indentation):
        result += '    '
    return result + str(string) + '\n'

def parse_1_1(dom):
    root_node = dom.childNodes[0]
    complex_type_nodes = parse_1_1_find_complex_type(root_node)
    gpx_element_nodes = parse_1_1_find_elements(root_node)
    result = ''
    for gpx_element_node in gpx_element_nodes:
        result += parse_1_1_element_node(gpx_element_node, complex_type_nodes)
    return result

def parse_1_1_element_node(gpx_element_node, complex_type_nodes, depth=0):
    result = ''
    node_type = gpx_element_node.attributes['type'].value
    node_name = gpx_element_node.attributes['name'].value
    result += get_indented(depth, '%s (%s)' % (node_name, node_type))
    if node_type in complex_type_nodes:
        # Complex node => parse:
        attribute_nodes = get_children_by_tag_name(complex_type_nodes[node_type], 'xsd:attribute')
        for attribute_node in attribute_nodes:
            attribute_node_name = attribute_node.attributes['name'].value
            attribute_node_type = attribute_node.attributes['type'].value
            attribute_node_required = attribute_node.attributes['required'].value if attribute_node.attributes.has_key('required') else None
            result += get_indented(depth + 1, '- attr: %s (%s) %s' % (attribute_node_name, attribute_node_type, attribute_node_required))
        sequence_nodes = get_children_by_tag_name(complex_type_nodes[node_type], 'xsd:sequence')
        if len(sequence_nodes) > 0:
            sequence_node = sequence_nodes[0]
            for element_node in get_children_by_tag_name(sequence_node, 'xsd:element'):
                result += parse_1_1_element_node(element_node, complex_type_nodes, depth=depth+1)
    return result

def parse_1_1_find_elements(node):
    result = []
    for node in node.childNodes:
        if node.nodeName == 'xsd:element':
            #import ipdb;ipdb.set_trace()
            result.append(node)
    return result

def parse_1_1_find_complex_type(root_node):
    result = {}
    for node in root_node.childNodes:
        if node.nodeName == 'xsd:complexType':
            node_name = node.attributes['name'].value
            result[node_name] = node
    return result

def parse_1_0(dom):
    root_node = dom.getElementsByTagName('xsd:element')[0]
    return parse_1_0_elements(root_node)

def parse_1_0_elements(element, depth=0):
    result = ''
    result += get_indented(depth, element.attributes['name'].value)
    complex_types = get_children_by_tag_name(element, 'xsd:complexType')
    if len(complex_types) > 0:
        print(complex_types)
        complex_type = complex_types[0]
        for attribute_node in get_children_by_tag_name(complex_type, 'xsd:attribute'):
            attribute_node_name = attribute_node.attributes['name'].value
            attribute_node_type = attribute_node.attributes['type'].value
            attribute_node_use = attribute_node.attributes['use'].value if attribute_node.attributes.has_key('use') else None
            result += get_indented(depth + 1, '- attr: %s (%s) %s' % (attribute_node_name, attribute_node_type, attribute_node_use))
        sequences = get_children_by_tag_name(complex_type, 'xsd:sequence')
        if len(sequences) > 0:
            sequence = sequences[0]
            for sub_element in get_children_by_tag_name(sequence, 'xsd:element'):
                result += parse_1_0_elements(sub_element, depth=depth+1)
    return result

dom = mod_minidom.parseString(open('gpx1.0.xsd').read())
prety_print_1_0 = parse_1_0(dom)
with open('gpx1.0.txt', 'w') as f:
    f.write(prety_print_1_0)
    print '1.0 written'

dom = mod_minidom.parseString(open('gpx1.1.xsd').read())
prety_print_1_1 = parse_1_1(dom)
with open('gpx1.1.txt', 'w') as f:
    f.write(prety_print_1_1)
    print '1.1 written'
