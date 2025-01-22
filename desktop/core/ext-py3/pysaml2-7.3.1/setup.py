# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src', 'saml2test': 'src/saml2test', 'utility': 'src/utility'}

packages = \
['saml2',
 'saml2.attributemaps',
 'saml2.authn_context',
 'saml2.cryptography',
 'saml2.data',
 'saml2.data.schemas',
 'saml2.data.templates',
 'saml2.entity_category',
 'saml2.extension',
 'saml2.profile',
 'saml2.s2repoze',
 'saml2.s2repoze.plugins',
 'saml2.schema',
 'saml2.tools',
 'saml2.userinfo',
 'saml2.ws',
 'saml2.xml',
 'saml2.xml.schema',
 'saml2.xmldsig',
 'saml2.xmlenc',
 'saml2test',
 'utility']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.1',
 'defusedxml',
 'pyopenssl',
 'python-dateutil',
 'pytz',
 'requests>=2,<3',
 'xmlschema>=1.2.1']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.7.0'],
 ':python_version < "3.9"': ['importlib-resources'],
 's2repoze': ['paste', 'repoze.who', 'zope.interface']}

entry_points = \
{'console_scripts': ['make_metadata = saml2.tools.make_metadata:main',
                     'mdexport = saml2.tools.mdexport:main',
                     'merge_metadata = saml2.tools.merge_metadata:main',
                     'parse_xsd2 = saml2.tools.parse_xsd2:main']}

setup_kwargs = {
    'name': 'pysaml2',
    'version': '7.3.1',
    'description': 'Python implementation of SAML Version 2 Standard',
    'long_description': "# PySAML2 - SAML2 for Python\n\n[![Version](https://img.shields.io/pypi/v/pysaml2)](https://pypi.org/project/pysaml2/)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/pysaml2)](https://pypi.org/project/pysaml2/)\n[![Total downloads](https://pepy.tech/badge/pysaml2)](https://pepy.tech/project/pysaml2)\n[![Weekly downloads](https://pepy.tech/badge/pysaml2/week)](https://pepy.tech/project/pysaml2)\n[![License](https://img.shields.io/github/license/IdentityPython/pysaml2)](https://github.com/IdentityPython/pysaml2/blob/master/LICENSE)\n\nPySAML2 is a pure python implementation of SAML Version 2 Standard.\nIt contains all necessary pieces for building a SAML2 service provider\nor an identity provider. The distribution contains examples of both.\nOriginally written to work in a WSGI environment\nthere are extensions that allow you to use it with other frameworks.\n\n**Website**: https://idpy.org/\n\n**Documentation**: https://pysaml2.readthedocs.io/\n\n**Contribution guidelines**: [CONTRIBUTING.md][contributing]\n\n**Security policies**: [SECURITY.md][sec]\n\n**Source code**: https://github.com/IdentityPython/pysaml2/\n\n**Developer guidelines**: [DEVELOPERS.md][dev]\n\n**PyPI project**: https://pypi.org/project/pysaml2/\n\n**License**: [LICENSE][license]\n\n\n## Specifications\n\nRetrieved from https://wiki.oasis-open.org/security/FrontPage\n\n#### SAML V2.0 Standard\n\n- SAML2 Core (aka Assertions and Protocols): http://www.oasis-open.org/committees/download.php/56776/sstc-saml-core-errata-2.0-wd-07.pdf\n  - Assertion schema: http://docs.oasis-open.org/security/saml/v2.0/saml-schema-assertion-2.0.xsd\n  - Protocols schema: http://docs.oasis-open.org/security/saml/v2.0/saml-schema-protocol-2.0.xsd\n- Bindings: http://www.oasis-open.org/committees/download.php/56779/sstc-saml-bindings-errata-2.0-wd-06.pdf\n- Profiles: http://www.oasis-open.org/committees/download.php/56782/sstc-saml-profiles-errata-2.0-wd-07.pdf\n- Metadata: http://www.oasis-open.org/committees/download.php/56785/sstc-saml-metadata-errata-2.0-wd-05.pdf\n  - Metadata schema: http://docs.oasis-open.org/security/saml/v2.0/saml-schema-metadata-2.0.xsd\n- Authentication Context: http://docs.oasis-open.org/security/saml/v2.0/saml-authn-context-2.0-os.pdf\n- Conformance Requirements: https://docs.oasis-open.org/security/saml/v2.0/saml-conformance-2.0-os.pdf\n- Security and Privacy Considerations: http://docs.oasis-open.org/security/saml/v2.0/saml-sec-consider-2.0-os.pdf\n- Glossary: http://docs.oasis-open.org/security/saml/v2.0/saml-glossary-2.0-os.pdf\n\n#### Profiles and extensions\n\n- Metadata Extension for SAML V2.0 and V1.x Query Requesters: http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-metadata-ext-query-os.pdf\n- SAML V2.0 Metadata Interoperability Profile: https://docs.oasis-open.org/security/saml/Post2.0/sstc-metadata-iop-os.pdf\n- SAML V2.0 Metadata Extensions for Login and Discovery User Interface Version 1.0: https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-metadata-ui/v1.0/os/sstc-saml-metadata-ui-v1.0-os.pdf\n- SAML V2.0 LDAP/X.500 Attribute Profile: http://www.oasis-open.org/committees/download.php/28042/sstc-saml-attribute-x500-cs-01.pdf\n- SAML V2.0 Enhanced Client or Proxy Profile Version 2.0: https://docs.oasis-open.org/security/saml/Post2.0/saml-ecp/v2.0/cs01/saml-ecp-v2.0-cs01.pdf\n\n#### Committee Specifications\n\n- SAML V2.0 Subject Identifier Attributes Profile Version 1.0: https://docs.oasis-open.org/security/saml-subject-id-attr/v1.0/cs01/saml-subject-id-attr-v1.0-cs01.pdf\n\n\n## Installation\n\nYou can install PySAML2 through pip:\n\n```shell\npip install pysaml2\n```\n\n### External dependencies\n\nPySAML2 works with the [`xmlsec`][xmlsec] binary.\nThis should be readily available in most Linux distributions:\n\n```shell\n$ apt-get install xmlsec1\n$ dnf install xmlsec1-openssl\n$ yum install xmlsec1-openssl\n$ pacman -S xmlsec\n...\n```\n\nand on MacOS through [`homebrew`][brew]\n\n```shell\n$ brew install libxmlsec1\n```\n\n\n## Changelog\n\nSee the [CHANGELOG][clog] to learn about the latest developments.\n\n\n## Contributing\n\nWe've set up a separate document for our [contribution guidelines][contributing].\n\n\n## Community\n\n[IdentityPython][idpy] is a community around\na collection of libraries and tools to manage identity related concepts with Python code.\nYou can interact with the community though the [mailing list](https://lists.sunet.se/postorius/lists/idpy-discuss.lists.sunet.se/)\nor on the [Slack workspace](https://identity-python.slack.com/) ([invitation](https://join.slack.com/t/identity-python/shared_invite/enQtNzEyNjU1NDI1MjUyLTM2MWI5ZGNhMTk1ZThiOTIxNWY2OTY1ODVmMWNjMzUzMTYxNTY5MzE5N2RlYjExZTIyM2MwYjBjZGE4MGVlMTM)).\n\n\n## Development\n\nWe've set up a separate document for [developers][dev].\n\n\n### Releasing\n\nWe've set up a separate document for our [release process][rel].\n\n\n### Pre-commit\n\n(TODO)\n\n\n  [idpy]: https://idpy.org/\n  [docs]: https://pysaml2.readthedocs.io/\n  [contributing]: https://github.com/IdentityPython/pysaml2/blob/master/CONTRIBUTING.md\n  [sec]: https://github.com/IdentityPython/pysaml2/blob/master/SECURITY.md\n  [repo]: https://github.com/IdentityPython/pysaml2/\n  [dev]: https://github.com/IdentityPython/pysaml2/blob/master/DEVELOPERS.md\n  [pypi]: https://pypi.org/project/pysaml2/\n  [license]: https://github.com/IdentityPython/pysaml2/blob/master/LICENSE\n  [clog]: https://github.com/IdentityPython/pysaml2/blob/master/CHANGELOG.md\n  [rel]: https://github.com/IdentityPython/pysaml2/blob/master/RELEASE.md\n  [xmlsec]: http://www.aleksey.com/xmlsec/\n  [brew]: https://brew.sh/\n",
    'author': 'IdentityPython',
    'author_email': 'discuss@idpy.org',
    'maintainer': 'IdentityPython',
    'maintainer_email': 'discuss@idpy.org',
    'url': 'https://idpy.org',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
