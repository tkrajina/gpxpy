import xml.dom.minidom as mod_minidom

def print_indented(indentation, string):
    result = ''
    for i in range(indentation):
        result += '    '
    print result + str(string)

def parse_1_1(dom):
    root_node = dom.childNodes[0]
    complex_type_nodes = parse_1_1_find_complex_type(root_node)
    gpx_element_nodes = parse_1_1_find_elements(root_node)
    for gpx_element_node in gpx_element_nodes:
        parse_1_1_element_node(gpx_element_node, complex_type_nodes)

def parse_1_1_element_node(gpx_element_node, complex_type_nodes, depth=0):
    node_type = gpx_element_node.attributes['type'].value
    node_name = gpx_element_node.attributes['name'].value
    print_indented(depth, '%s (%s)' % (node_name, node_type))
    if node_type in complex_type_nodes:
        # Complex node => parse:
        attribute_nodes = complex_type_nodes[node_type].getElementsByTagName('xsd:attribute')
        for attribute_node in attribute_nodes:
            attribute_node_name = attribute_node.attributes['name'].value
            attribute_node_type = attribute_node.attributes['type'].value
            attribute_node_required = attribute_node.attributes['required'].value if attribute_node.attributes.has_key('required') else None
            print_indented(depth + 2, 'attr: %s (%s) %s' % (attribute_node_name, attribute_node_type, attribute_node_required))
        sequence_nodes = complex_type_nodes[node_type].getElementsByTagName('xsd:sequence')
        if len(sequence_nodes) > 0:
            sequence_node = sequence_nodes[0]
            for element_node in sequence_node.getElementsByTagName('xsd:element'):
                parse_1_1_element_node(element_node, complex_type_nodes, depth=depth+1)

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

dom = mod_minidom.parseString(open('gpx1.1.xsd').read())
parse_1_1(dom)
