import sys


# importlib.resources was introduced in python 3.7
# files API from importlib.resources introduced in python 3.9
if sys.version_info[:2] >= (3, 9):
    from importlib.resources import files as _resource_files
else:
    from importlib_resources import files as _resource_files

from xmlschema import XMLSchema as _XMLSchema
from xmlschema.exceptions import XMLSchemaException as _XMLSchemaException

import saml2.data.schemas as _data_schemas


class XMLSchemaError(Exception):
    """Generic error raised when the schema does not validate with a document"""


def _create_xml_schema_validator(source=None, **kwargs):
    schema_resources = _resource_files(_data_schemas)
    path_schema_xml = str(schema_resources.joinpath("xml.xsd"))
    path_schema_envelope = str(schema_resources.joinpath("envelope.xsd"))
    path_schema_xenc = str(schema_resources.joinpath("xenc-schema.xsd"))
    path_schema_xmldsig_core = str(schema_resources.joinpath("xmldsig-core-schema.xsd"))
    path_schema_saml_assertion = str(schema_resources.joinpath("saml-schema-assertion-2.0.xsd"))
    path_schema_saml_metadata = str(schema_resources.joinpath("saml-schema-metadata-2.0.xsd"))
    path_schema_saml_protocol = str(schema_resources.joinpath("saml-schema-protocol-2.0.xsd"))
    path_schema_eidas_metadata_servicelist = str(schema_resources.joinpath("eidas-schema-metadata-servicelist.xsd"))
    path_schema_eidas_saml_extensions = str(schema_resources.joinpath("eidas-schema-saml-extensions.xsd"))
    path_schema_eidas_attribute_naturalperson = str(
        schema_resources.joinpath("eidas-schema-attribute-naturalperson.xsd")
    )
    path_schema_eidas_attribute_legalperson = str(schema_resources.joinpath("eidas-schema-attribute-legalperson.xsd"))

    source = source if source else path_schema_saml_protocol
    locations = {
        "http://www.w3.org/XML/1998/namespace": path_schema_xml,
        "http://schemas.xmlsoap.org/soap/envelope/": path_schema_envelope,
        "http://www.w3.org/2001/04/xmlenc#": path_schema_xenc,
        "http://www.w3.org/2000/09/xmldsig#": path_schema_xmldsig_core,
        "urn:oasis:names:tc:SAML:2.0:assertion": path_schema_saml_assertion,
        "urn:oasis:names:tc:SAML:2.0:metadata": path_schema_saml_metadata,
        "urn:oasis:names:tc:SAML:2.0:protocol": path_schema_saml_protocol,
        "http://eidas.europa.eu/metadata/servicelist": path_schema_eidas_metadata_servicelist,
        "http://eidas.europa.eu/saml-extensions": path_schema_eidas_saml_extensions,
        "http://eidas.europa.eu/attributes/naturalperson": path_schema_eidas_attribute_naturalperson,
        "http://eidas.europa.eu/attributes/legalperson": path_schema_eidas_attribute_legalperson,
    }

    kwargs = {
        **kwargs,
        "validation": "strict",
        "locations": locations,
        "base_url": source,
        "allow": "sandbox",
        "use_fallback": False,
    }
    return _XMLSchema(source, **kwargs)


_schema_validator_default = _create_xml_schema_validator()


def validate(doc, validator=None):
    validator = _schema_validator_default if validator is None else validator
    try:
        validator.validate(doc)
    except _XMLSchemaException as e:
        error_context = {
            "doc": doc,
            "error": str(e),
        }
        raise XMLSchemaError(error_context) from e
    except Exception as e:
        error_context = {
            "doc": doc,
            "error": str(e),
        }
        raise XMLSchemaError(error_context) from e
