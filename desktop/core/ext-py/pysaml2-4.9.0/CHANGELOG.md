# Changelog

## 4.9.0 (2019-11-03)

- Add mdstore methods to extract mdui uiinfo elements
- Add attribute mapping for umbrellaID attributes
- Fix logic error in pick_binding method for Entity class
- Validate the audience of assertions regardless of a response being unsolicited
- Fix PKCS_9 saml_url prefix
- docs: Fix warnings from docs generation
- docs: Update release instructions regarding branch releases
- docs: Fix list formatting on IdP example page
- docs: Update pysaml2 options doc with `name_id_format_allow_create`
- misc: fix various typos


## 4.8.0 (2019-07-08)

- Refactor the way ForceAuthn is set: check for "true" and "1"
- Allow to set NameQualifier and SPNameQualifier attributes for ePTID
- Parse assertions with Holder-of-Key profile
- Add created_at timestamps to all mongodb documents
- Look for existing persistent id's before creating new ones
- Do not add AllowCreate property for default transient NameID
- Enable entity category import from module search path
- Add SAML subject identifier attributes to saml2_uri attributemap
- Fix deprecation warning regarding the cgi module - use the html module when available
- Misc minor improvements
- tests: Be compatible with latest pytest
- tests: Make tests pass after 2024
- tests: Add py37 as a test target
- docs: Correct instructions to run tests
- docs: Fix misc typos
- examples: Set cherrypy version explicitly


## 4.7.0 (2019-04-02)

- Add support for MDQ signature verification
- Raise XmlsecError if xmlsec1 operations do not succeed
- Handle non standard response error status codes correctly
- Remove the hardcoded warning filter; pass -Wd to the python
  interpreter to enable warnings
- Remove the python-future dependency and only use six
- Minor python2 and python3 compatibility fixes
  (unicode strings and example code)
- Minor documentation fixes


## 4.6.5 (2018-12-04)

- Fix for response status error case handling (introduced in v4.6.5)
- Added assurance-certification support
- Added entity-category-support support

Thanks @rectalogic @skanct


## 4.6.4 (2018-11-22)

- Make use of the sign argument to entity.Entity::apply_binding when binding is
  HTTP-Redirect. Reminder: use [authn_requests_signed configuration option][0]
  to indicate that Authentication Requests sent by the SP must be signed
- Add want_assertions_or_response_signed configuration option - see
  [documentation][1] about the introduced behaviour
- Fix code for idp and sp examples
- Do not require assertion conditions
- Fix response encoding format
- Various code improvements for config, sigver, client_base, client,
  ecp_client, ecp, s2repoze and entity modules
- Support non-ascii attribute values for encryption and decryption

Thanks to @johanlundberg @skoranda @yuqing0708 @erakli

  [0]: https://github.com/IdentityPython/pysaml2/blob/master/docs/howto/config.rst#authn-requests-signed
  [1]: https://github.com/IdentityPython/pysaml2/blob/master/docs/howto/config.rst#want-assertions-or-response-signed


## 4.6.3 (2018-10-08)

Do not map between attribute FriendlyName and attribute Name when no
attributemaps are provided.

## 4.6.2 (2018-09-06)

Refactor AttributeValueBase::set_text method.

- set_text is doing too many things. At least the structure is a bit cleaner;
  though, still complex.
- set_text will set the type if no type has been set.
- set_text should not modify the type if it has already been set,
- set_text should not depend on the type's namespace.
- set_text should not interfere with the 'anyType' type.
- set_text will raise a ValueError if the value cannot be represented by the
  type.
- set_text will raise a ValueError if the type is unknown.

## 4.6.1 (2018-08-29)

- Allow multiple AttributeStatement tags per Assertion
- Raise ValueError for invalid attribute type
- Make NameID element optional
- tests: fix test that depended on actual datetime
- build: Set minimum build-tool version through pyproject.toml

## 4.6.0 (2018-08-07)

- Allow configuration and specification of id attribute name
- Retrieve SLO endpoint by the appropriate service type
- Deprecate AESCipher and aes.py module
- Add saml2.cryptography module
- Always generate a random IV for AES operations / Address CVE-2017-1000246
- Remove unused and broken RSA code
- Add more nameid-format definitions
- Remove invalid nameid-format
- Retrieve pacakge version from pkg_resources
- Fully replace Cryptodome library with cryptography
- Fix SSRF caused by URI attribute of Reference element
- Omit relay state in HTTP-POST response when empty
- Fix eidas natural person attribute URIs
- Add eidas attributes for legal person to saml2_uri attributemap
- Fix deprecation and resource warnings.
- Fix date format to show month, not minutes
- Fix typos
- s2repoze: Define session_info variable before use
- s2repoze: Correctly pull the SAMLRequest from Redirect LogoutRequests
- s2repoze: Include SCRIPT_NAME when checking whether current URL is a logout endpoint
- tests: Document and test all supported Python versions
- tests: Generate and upload coverage reports to codecov
- tests: Include dependencies information in test report
- tests: Run tests in verbose mode
- tests: Clean up unclosed files causing ResourceWarnings
- build: Set minimal version for cryptography package
- build: Set the correct version in the docs
- build: Update build manifest to include the correct files
- build: Switch from setup.py to setup.cfg
- docs: Add editorconfig file with basic rules
- docs: Update gitignore file
- docs: Remove downloads badge as it is no longer available
- docs: Update all pypi.python.org URLs to pypi.org
- docs: Updated license and renamed the file.
- examples: Do not request a signed response - backwards compatibility
- examples: Fix wsgiserver usage for example sp
- examples: Fix cherrypy.wsgiserver usage

## 0.4.2 (2012-03-27)

- Add default attribute mappings

## 0.4.1 (2012-03-18)

- Auto sign authentication and logout requests following config options.
- Add backwards compatibility with ElementTree in python < 2.7.
- Fix minor bugs in the tests.
- Support one more nameid format.
