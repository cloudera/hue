from saml2 import create_class_from_xml_string as parse_str_as
from saml2.config import Config
from saml2.extension.sp_type import SPType
from saml2.metadata import Attribute
from saml2.metadata import entity_descriptor


class TestMDExt:
    def test_sp_type_true(self):
        fil = "sp_mdext_conf.py"
        cnf = Config().load_file(fil)
        ed = entity_descriptor(cnf)

        assert ed.spsso_descriptor.extensions
        assert len(ed.spsso_descriptor.extensions.extension_elements) == 3
        assert ed.extensions
        assert len(ed.extensions.extension_elements) > 1
        assert any(e.tag is SPType.c_tag for e in ed.extensions.extension_elements)

    def test_sp_type_false(self):
        fil = "sp_mdext_conf.py"
        cnf = Config().load_file(fil)
        cnf.setattr("sp", "sp_type_in_metadata", False)
        ed = entity_descriptor(cnf)

        assert all(e.tag is not SPType.c_tag for e in ed.extensions.extension_elements)

    def test_entity_attributes(self):
        fil = "sp_mdext_conf.py"
        cnf = Config().load_file(fil)
        ed = entity_descriptor(cnf)

        entity_attributes = next(e for e in ed.extensions.extension_elements if e.tag == "EntityAttributes")
        attributes = [parse_str_as(Attribute, e.to_string()) for e in entity_attributes.children]
        assert all(
            a.name
            in [
                "urn:oasis:names:tc:SAML:profiles:subject-id:req",
                "somename",
            ]
            for a in attributes
        )

        import saml2.attribute_converter

        attrc = saml2.attribute_converter.ac_factory()

        import saml2.mdstore

        mds = saml2.mdstore.MetadataStore(attrc, cnf)

        mds.load("inline", ed.to_string())
        entityid = ed.entity_id
        entity_attributes = mds.entity_attributes(entityid)
        assert entity_attributes == {
            "urn:oasis:names:tc:SAML:profiles:subject-id:req": ["any"],
            "somename": ["x", "y", "z"],
        }
