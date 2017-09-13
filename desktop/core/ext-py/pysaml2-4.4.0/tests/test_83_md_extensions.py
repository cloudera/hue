from saml2.config import Config
from saml2.metadata import entity_descriptor

__author__ = 'roland'

fil = "sp_mdext_conf.py"

cnf = Config().load_file(fil, metadata_construction=True)
ed = entity_descriptor(cnf)

print(ed)

assert ed.spsso_descriptor.extensions
assert len(ed.spsso_descriptor.extensions.extension_elements) == 3

assert ed.extensions
assert len(ed.extensions.extension_elements) > 1