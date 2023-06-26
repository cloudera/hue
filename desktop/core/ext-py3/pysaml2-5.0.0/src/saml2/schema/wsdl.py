#!!!! 'NoneType' object has no attribute 'py_class'
#!!!! 'NoneType' object has no attribute 'py_class'
#!/usr/bin/env python

#
# Generated Fri May 27 17:23:24 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase


NAMESPACE = 'http://schemas.xmlsoap.org/wsdl/'

class TDocumentation_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/:tDocumentation element """

    c_tag = 'tDocumentation'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def t_documentation__from_string(xml_string):
    return saml2.create_class_from_xml_string(TDocumentation_, xml_string)


class TDocumented_documentation(TDocumentation_):

    c_tag = 'documentation'
    c_namespace = NAMESPACE
    c_children = TDocumentation_.c_children.copy()
    c_attributes = TDocumentation_.c_attributes.copy()
    c_child_order = TDocumentation_.c_child_order[:]
    c_cardinality = TDocumentation_.c_cardinality.copy()

def t_documented_documentation_from_string(xml_string):
    return saml2.create_class_from_xml_string(TDocumented_documentation, xml_string)


class TDocumented_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/:tDocumented element """

    c_tag = 'tDocumented'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}documentation'] = ('documentation', TDocumented_documentation)
    c_cardinality['documentation'] = {"min":0, "max":1}
    c_child_order.extend(['documentation'])

    def __init__(self,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.documentation=documentation

def t_documented__from_string(xml_string):
    return saml2.create_class_from_xml_string(TDocumented_, xml_string)


class TExtensibleAttributesDocumented_(TDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tExtensibleAttributesDocumented element """

    c_tag = 'tExtensibleAttributesDocumented'
    c_namespace = NAMESPACE
    c_children = TDocumented_.c_children.copy()
    c_attributes = TDocumented_.c_attributes.copy()
    c_child_order = TDocumented_.c_child_order[:]
    c_cardinality = TDocumented_.c_cardinality.copy()


class TExtensibleDocumented_(TDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tExtensibleDocumented element """

    c_tag = 'tExtensibleDocumented'
    c_namespace = NAMESPACE
    c_children = TDocumented_.c_children.copy()
    c_attributes = TDocumented_.c_attributes.copy()
    c_child_order = TDocumented_.c_child_order[:]
    c_cardinality = TDocumented_.c_cardinality.copy()


class TImport_(TExtensibleAttributesDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tImport element """

    c_tag = 'tImport'
    c_namespace = NAMESPACE
    c_children = TExtensibleAttributesDocumented_.c_children.copy()
    c_attributes = TExtensibleAttributesDocumented_.c_attributes.copy()
    c_child_order = TExtensibleAttributesDocumented_.c_child_order[:]
    c_cardinality = TExtensibleAttributesDocumented_.c_cardinality.copy()
    c_attributes['namespace'] = ('namespace', 'anyURI', True)
    c_attributes['location'] = ('location', 'anyURI', True)

    def __init__(self,
            namespace=None,
            location=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleAttributesDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.namespace=namespace
        self.location=location

def t_import__from_string(xml_string):
    return saml2.create_class_from_xml_string(TImport_, xml_string)


class TTypes_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tTypes element """

    c_tag = 'tTypes'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()

def t_types__from_string(xml_string):
    return saml2.create_class_from_xml_string(TTypes_, xml_string)


class TPart_(TExtensibleAttributesDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tPart element """

    c_tag = 'tPart'
    c_namespace = NAMESPACE
    c_children = TExtensibleAttributesDocumented_.c_children.copy()
    c_attributes = TExtensibleAttributesDocumented_.c_attributes.copy()
    c_child_order = TExtensibleAttributesDocumented_.c_child_order[:]
    c_cardinality = TExtensibleAttributesDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', True)
    c_attributes['element'] = ('element', 'QName', False)
    c_attributes['type'] = ('type', 'QName', False)

    def __init__(self,
            name=None,
            element=None,
            type=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleAttributesDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name
        self.element=element
        self.type=type

def t_part__from_string(xml_string):
    return saml2.create_class_from_xml_string(TPart_, xml_string)


class TOperation_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tOperation element """

    c_tag = 'tOperation'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', True)
    c_attributes['parameterOrder'] = ('parameter_order', 'NMTOKENS', False)

    def __init__(self,
            name=None,
            parameter_order=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name
        self.parameter_order=parameter_order

def t_operation__from_string(xml_string):
    return saml2.create_class_from_xml_string(TOperation_, xml_string)


class TParam_(TExtensibleAttributesDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tParam element """

    c_tag = 'tParam'
    c_namespace = NAMESPACE
    c_children = TExtensibleAttributesDocumented_.c_children.copy()
    c_attributes = TExtensibleAttributesDocumented_.c_attributes.copy()
    c_child_order = TExtensibleAttributesDocumented_.c_child_order[:]
    c_cardinality = TExtensibleAttributesDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', False)
    c_attributes['message'] = ('message', 'QName', True)

    def __init__(self,
            name=None,
            message=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleAttributesDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name
        self.message=message

def t_param__from_string(xml_string):
    return saml2.create_class_from_xml_string(TParam_, xml_string)


class TFault_(TExtensibleAttributesDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tFault element """

    c_tag = 'tFault'
    c_namespace = NAMESPACE
    c_children = TExtensibleAttributesDocumented_.c_children.copy()
    c_attributes = TExtensibleAttributesDocumented_.c_attributes.copy()
    c_child_order = TExtensibleAttributesDocumented_.c_child_order[:]
    c_cardinality = TExtensibleAttributesDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', True)
    c_attributes['message'] = ('message', 'QName', True)

    def __init__(self,
            name=None,
            message=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleAttributesDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name
        self.message=message

def t_fault__from_string(xml_string):
    return saml2.create_class_from_xml_string(TFault_, xml_string)


class TBindingOperationMessage_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tBindingOperationMessage element """

    c_tag = 'tBindingOperationMessage'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', False)

    def __init__(self,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name

def t_binding_operation_message__from_string(xml_string):
    return saml2.create_class_from_xml_string(TBindingOperationMessage_, xml_string)


class TBindingOperationFault_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tBindingOperationFault element """

    c_tag = 'tBindingOperationFault'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', True)

    def __init__(self,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name

def t_binding_operation_fault__from_string(xml_string):
    return saml2.create_class_from_xml_string(TBindingOperationFault_, xml_string)


class TBindingOperation_input(TBindingOperationMessage_):

    c_tag = 'input'
    c_namespace = NAMESPACE
    c_children = TBindingOperationMessage_.c_children.copy()
    c_attributes = TBindingOperationMessage_.c_attributes.copy()
    c_child_order = TBindingOperationMessage_.c_child_order[:]
    c_cardinality = TBindingOperationMessage_.c_cardinality.copy()

def t_binding_operation_input_from_string(xml_string):
    return saml2.create_class_from_xml_string(TBindingOperation_input, xml_string)


class TBindingOperation_output(TBindingOperationMessage_):

    c_tag = 'output'
    c_namespace = NAMESPACE
    c_children = TBindingOperationMessage_.c_children.copy()
    c_attributes = TBindingOperationMessage_.c_attributes.copy()
    c_child_order = TBindingOperationMessage_.c_child_order[:]
    c_cardinality = TBindingOperationMessage_.c_cardinality.copy()

def t_binding_operation_output_from_string(xml_string):
    return saml2.create_class_from_xml_string(TBindingOperation_output, xml_string)


class TBindingOperation_fault(TBindingOperationFault_):

    c_tag = 'fault'
    c_namespace = NAMESPACE
    c_children = TBindingOperationFault_.c_children.copy()
    c_attributes = TBindingOperationFault_.c_attributes.copy()
    c_child_order = TBindingOperationFault_.c_child_order[:]
    c_cardinality = TBindingOperationFault_.c_cardinality.copy()

def t_binding_operation_fault_from_string(xml_string):
    return saml2.create_class_from_xml_string(TBindingOperation_fault, xml_string)


class TBindingOperation_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tBindingOperation element """

    c_tag = 'tBindingOperation'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}input'] = ('input', TBindingOperation_input)
    c_cardinality['input'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}output'] = ('output', TBindingOperation_output)
    c_cardinality['output'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}fault'] = ('fault', [TBindingOperation_fault])
    c_cardinality['fault'] = {"min":0}
    c_attributes['name'] = ('name', 'NCName', True)
    c_child_order.extend(['input', 'output', 'fault'])

    def __init__(self,
            input=None,
            output=None,
            fault=None,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.input=input
        self.output=output
        self.fault=fault or []
        self.name=name

def t_binding_operation__from_string(xml_string):
    return saml2.create_class_from_xml_string(TBindingOperation_, xml_string)


class TPort_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tPort element """

    c_tag = 'tPort'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_attributes['name'] = ('name', 'NCName', True)
    c_attributes['binding'] = ('binding', 'QName', True)

    def __init__(self,
            name=None,
            binding=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name
        self.binding=binding

def t_port__from_string(xml_string):
    return saml2.create_class_from_xml_string(TPort_, xml_string)


class TExtensibilityElement_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/:tExtensibilityElement element """

    c_tag = 'tExtensibilityElement'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['required'] = ('required', 'None', False)

    def __init__(self,
            required=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.required=required


class Import(TImport_):
    """The http://schemas.xmlsoap.org/wsdl/:import element """

    c_tag = 'import'
    c_namespace = NAMESPACE
    c_children = TImport_.c_children.copy()
    c_attributes = TImport_.c_attributes.copy()
    c_child_order = TImport_.c_child_order[:]
    c_cardinality = TImport_.c_cardinality.copy()

def import_from_string(xml_string):
    return saml2.create_class_from_xml_string(Import, xml_string)


class Types(TTypes_):
    """The http://schemas.xmlsoap.org/wsdl/:types element """

    c_tag = 'types'
    c_namespace = NAMESPACE
    c_children = TTypes_.c_children.copy()
    c_attributes = TTypes_.c_attributes.copy()
    c_child_order = TTypes_.c_child_order[:]
    c_cardinality = TTypes_.c_cardinality.copy()

def types_from_string(xml_string):
    return saml2.create_class_from_xml_string(Types, xml_string)


class TMessage_part(TPart_):

    c_tag = 'part'
    c_namespace = NAMESPACE
    c_children = TPart_.c_children.copy()
    c_attributes = TPart_.c_attributes.copy()
    c_child_order = TPart_.c_child_order[:]
    c_cardinality = TPart_.c_cardinality.copy()

def t_message_part_from_string(xml_string):
    return saml2.create_class_from_xml_string(TMessage_part, xml_string)


class TMessage_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tMessage element """

    c_tag = 'tMessage'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}part'] = ('part', [TMessage_part])
    c_cardinality['part'] = {"min":0}
    c_attributes['name'] = ('name', 'NCName', True)
    c_child_order.extend(['part'])

    def __init__(self,
            part=None,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.part=part or []
        self.name=name

def t_message__from_string(xml_string):
    return saml2.create_class_from_xml_string(TMessage_, xml_string)


class TPortType_operation(TOperation_):

    c_tag = 'operation'
    c_namespace = NAMESPACE
    c_children = TOperation_.c_children.copy()
    c_attributes = TOperation_.c_attributes.copy()
    c_child_order = TOperation_.c_child_order[:]
    c_cardinality = TOperation_.c_cardinality.copy()

def t_port_type_operation_from_string(xml_string):
    return saml2.create_class_from_xml_string(TPortType_operation, xml_string)


class TPortType_(TExtensibleAttributesDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tPortType element """

    c_tag = 'tPortType'
    c_namespace = NAMESPACE
    c_children = TExtensibleAttributesDocumented_.c_children.copy()
    c_attributes = TExtensibleAttributesDocumented_.c_attributes.copy()
    c_child_order = TExtensibleAttributesDocumented_.c_child_order[:]
    c_cardinality = TExtensibleAttributesDocumented_.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}operation'] = ('operation', [TPortType_operation])
    c_cardinality['operation'] = {"min":0}
    c_attributes['name'] = ('name', 'NCName', True)
    c_child_order.extend(['operation'])

    def __init__(self,
            operation=None,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleAttributesDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.operation=operation or []
        self.name=name

def t_port_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TPortType_, xml_string)


class TBinding_operation(TBindingOperation_):

    c_tag = 'operation'
    c_namespace = NAMESPACE
    c_children = TBindingOperation_.c_children.copy()
    c_attributes = TBindingOperation_.c_attributes.copy()
    c_child_order = TBindingOperation_.c_child_order[:]
    c_cardinality = TBindingOperation_.c_cardinality.copy()

def t_binding_operation_from_string(xml_string):
    return saml2.create_class_from_xml_string(TBinding_operation, xml_string)


class TBinding_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tBinding element """

    c_tag = 'tBinding'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}operation'] = ('operation', [TBinding_operation])
    c_cardinality['operation'] = {"min":0}
    c_attributes['name'] = ('name', 'NCName', True)
    c_attributes['type'] = ('type', 'QName', True)
    c_child_order.extend(['operation'])

    def __init__(self,
            operation=None,
            name=None,
            type=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.operation=operation or []
        self.name=name
        self.type=type

def t_binding__from_string(xml_string):
    return saml2.create_class_from_xml_string(TBinding_, xml_string)


class TService_port(TPort_):

    c_tag = 'port'
    c_namespace = NAMESPACE
    c_children = TPort_.c_children.copy()
    c_attributes = TPort_.c_attributes.copy()
    c_child_order = TPort_.c_child_order[:]
    c_cardinality = TPort_.c_cardinality.copy()

def t_service_port_from_string(xml_string):
    return saml2.create_class_from_xml_string(TService_port, xml_string)


class TService_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tService element """

    c_tag = 'tService'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}port'] = ('port', [TService_port])
    c_cardinality['port'] = {"min":0}
    c_attributes['name'] = ('name', 'NCName', True)
    c_child_order.extend(['port'])

    def __init__(self,
            port=None,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.port=port or []
        self.name=name

def t_service__from_string(xml_string):
    return saml2.create_class_from_xml_string(TService_, xml_string)


class Message(TMessage_):
    """The http://schemas.xmlsoap.org/wsdl/:message element """

    c_tag = 'message'
    c_namespace = NAMESPACE
    c_children = TMessage_.c_children.copy()
    c_attributes = TMessage_.c_attributes.copy()
    c_child_order = TMessage_.c_child_order[:]
    c_cardinality = TMessage_.c_cardinality.copy()

def message_from_string(xml_string):
    return saml2.create_class_from_xml_string(Message, xml_string)


class PortType(TPortType_):
    """The http://schemas.xmlsoap.org/wsdl/:portType element """

    c_tag = 'portType'
    c_namespace = NAMESPACE
    c_children = TPortType_.c_children.copy()
    c_attributes = TPortType_.c_attributes.copy()
    c_child_order = TPortType_.c_child_order[:]
    c_cardinality = TPortType_.c_cardinality.copy()

def port_type_from_string(xml_string):
    return saml2.create_class_from_xml_string(PortType, xml_string)


class Binding(TBinding_):
    """The http://schemas.xmlsoap.org/wsdl/:binding element """

    c_tag = 'binding'
    c_namespace = NAMESPACE
    c_children = TBinding_.c_children.copy()
    c_attributes = TBinding_.c_attributes.copy()
    c_child_order = TBinding_.c_child_order[:]
    c_cardinality = TBinding_.c_cardinality.copy()

def binding_from_string(xml_string):
    return saml2.create_class_from_xml_string(Binding, xml_string)


class Service(TService_):
    """The http://schemas.xmlsoap.org/wsdl/:service element """

    c_tag = 'service'
    c_namespace = NAMESPACE
    c_children = TService_.c_children.copy()
    c_attributes = TService_.c_attributes.copy()
    c_child_order = TService_.c_child_order[:]
    c_cardinality = TService_.c_cardinality.copy()

def service_from_string(xml_string):
    return saml2.create_class_from_xml_string(Service, xml_string)


class TDefinitions_(TExtensibleDocumented_):
    """The http://schemas.xmlsoap.org/wsdl/:tDefinitions element """

    c_tag = 'tDefinitions'
    c_namespace = NAMESPACE
    c_children = TExtensibleDocumented_.c_children.copy()
    c_attributes = TExtensibleDocumented_.c_attributes.copy()
    c_child_order = TExtensibleDocumented_.c_child_order[:]
    c_cardinality = TExtensibleDocumented_.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/wsdl/}import'] = ('import', Import)
    c_cardinality['import'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}types'] = ('types', Types)
    c_cardinality['types'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}message'] = ('message', Message)
    c_cardinality['message'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}portType'] = ('port_type', PortType)
    c_cardinality['port_type'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}binding'] = ('binding', Binding)
    c_cardinality['binding'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/wsdl/}service'] = ('service', Service)
    c_cardinality['service'] = {"min":0, "max":1}
    c_attributes['targetNamespace'] = ('target_namespace', 'anyURI', False)
    c_attributes['name'] = ('name', 'NCName', False)
    c_child_order.extend(['import', 'types', 'message', 'port_type', 'binding', 'service'])

    def __init__(self,
            import_=None,
            types=None,
            message=None,
            port_type=None,
            binding=None,
            service=None,
            target_namespace=None,
            name=None,
            documentation=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        TExtensibleDocumented_.__init__(self,
                documentation=documentation,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.import_=import_
        self.types=types
        self.message=message
        self.port_type=port_type
        self.binding=binding
        self.service=service
        self.target_namespace=target_namespace
        self.name=name

def t_definitions__from_string(xml_string):
    return saml2.create_class_from_xml_string(TDefinitions_, xml_string)


class Definitions(TDefinitions_):
    """The http://schemas.xmlsoap.org/wsdl/:definitions element """

    c_tag = 'definitions'
    c_namespace = NAMESPACE
    c_children = TDefinitions_.c_children.copy()
    c_attributes = TDefinitions_.c_attributes.copy()
    c_child_order = TDefinitions_.c_child_order[:]
    c_cardinality = TDefinitions_.c_cardinality.copy()

def definitions_from_string(xml_string):
    return saml2.create_class_from_xml_string(Definitions, xml_string)


#..................
# []
ELEMENT_FROM_STRING = {
    TDocumentation_.c_tag: t_documentation__from_string,
    TDocumented_.c_tag: t_documented__from_string,
    Definitions.c_tag: definitions_from_string,
    TDefinitions_.c_tag: t_definitions__from_string,
    TImport_.c_tag: t_import__from_string,
    TTypes_.c_tag: t_types__from_string,
    TMessage_.c_tag: t_message__from_string,
    TPart_.c_tag: t_part__from_string,
    TPortType_.c_tag: t_port_type__from_string,
    TOperation_.c_tag: t_operation__from_string,
    TParam_.c_tag: t_param__from_string,
    TFault_.c_tag: t_fault__from_string,
    TBinding_.c_tag: t_binding__from_string,
    TBindingOperationMessage_.c_tag: t_binding_operation_message__from_string,
    TBindingOperationFault_.c_tag: t_binding_operation_fault__from_string,
    TBindingOperation_.c_tag: t_binding_operation__from_string,
    TService_.c_tag: t_service__from_string,
    TPort_.c_tag: t_port__from_string,
    TDocumented_documentation.c_tag: t_documented_documentation_from_string,
    TBindingOperation_input.c_tag: t_binding_operation_input_from_string,
    TBindingOperation_output.c_tag: t_binding_operation_output_from_string,
    TBindingOperation_fault.c_tag: t_binding_operation_fault_from_string,
    Import.c_tag: import_from_string,
    Types.c_tag: types_from_string,
    TMessage_part.c_tag: t_message_part_from_string,
    TPortType_operation.c_tag: t_port_type_operation_from_string,
    TService_port.c_tag: t_service_port_from_string,
    Message.c_tag: message_from_string,
    PortType.c_tag: port_type_from_string,
    Binding.c_tag: binding_from_string,
    Service.c_tag: service_from_string,
}

ELEMENT_BY_TAG = {
    'tDocumentation': TDocumentation_,
    'tDocumented': TDocumented_,
    'definitions': Definitions,
    'tDefinitions': TDefinitions_,
    'tImport': TImport_,
    'tTypes': TTypes_,
    'tMessage': TMessage_,
    'tPart': TPart_,
    'tPortType': TPortType_,
    'tOperation': TOperation_,
    'tParam': TParam_,
    'tFault': TFault_,
    'tBinding': TBinding_,
    'tBindingOperationMessage': TBindingOperationMessage_,
    'tBindingOperationFault': TBindingOperationFault_,
    'tBindingOperation': TBindingOperation_,
    'tService': TService_,
    'tPort': TPort_,
    'documentation': TDocumented_documentation,
    'input': TBindingOperation_input,
    'output': TBindingOperation_output,
    'fault': TBindingOperation_fault,
    'import': Import,
    'types': Types,
    'part': TMessage_part,
    'operation': TPortType_operation,
    'port': TService_port,
    'message': Message,
    'portType': PortType,
    'binding': Binding,
    'service': Service,
    'tExtensibleAttributesDocumented': TExtensibleAttributesDocumented_,
    'tExtensibleDocumented': TExtensibleDocumented_,
    'tExtensibilityElement': TExtensibilityElement_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

