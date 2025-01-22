SimpleSAMLphp issues
--------------------
As of SimpleSAMLphp 1.8.2 there is a problem if you specify attributes in
the SP configuration. When the SimpleSAMLphp metadata parser converts the
XML into its custom php format it puts the following option::

  'attributes.NameFormat' => 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri'

But it need to be replaced by this one::

  'AttributeNameFormat' => 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri'

Otherwise the Assertions sent from the IdP to the SP will have a wrong
Attribute Name Format and pysaml2 will be confused.

Furthermore if you have a AttributeLimit filter in your SimpleSAMLphp
configuration  you will need to enable another attribute filter just
before to make sure that the AttributeLimit does not remove the attributes
from the authentication source. The filter you need to add is an AttributeMap
filter like this::

  10 => array(
             'class' => 'core:AttributeMap', 'name2oid'
        ),

Okta federation
---------------

Okta settings to configure on your Idp's SAML app advanced settings::

    Single Logout URL: http://localhost:8000/saml2/ls/post/
    SP Issuer : http://localhost:8000/saml2/metadata/

Okta sample configuration for setting up an Okta SSO with Django::

        'service': {
        # we are just a lonely SP
        'sp': {
            'name': 'XXX',
            'allow_unsolicited': True,
            'want_assertions_signed': True,  # assertion signing (default=True)
            'want_response_signed': True,
            "want_assertions_or_response_signed": True,  # is response signing required
            'name_id_format': NAMEID_FORMAT_UNSPECIFIED,

            # Must for signed logout requests
            "logout_requests_signed": True,
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('http://localhost:8000/saml2/acs/',
                     saml2.BINDING_HTTP_POST),
                ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    # ('http://localhost:8000/saml2/ls/',
                    #  saml2.BINDING_HTTP_REDIRECT),
                    ('http://localhost:8000/saml2/ls/post/',
                     saml2.BINDING_HTTP_POST),
                ],
            },
            # Mandates that the identity provider MUST authenticate the
            # presenter directly rather than rely on a previous security context.
            'force_authn': False,

            "allow_unsolicited": True,

            # Enable AllowCreate in NameIDPolicy.
            'name_id_format_allow_create': False,

            # attributes that this project need to identify a user
            'required_attributes': ['email'],

            # in this section the list of IdPs we talk to are defined
            'idp': {
                # we do not need a WAYF service since there is
                # only an IdP defined here. This IdP should be
                # present in our metadata

                # the keys of this dictionary are entity ids
                'https://xxx.okta.com/app/XXXXXXXXXX/sso/saml/metadata': {
                    # Okta only uses HTTP_POST disable this
                    # 'single_sign_on_service': {
                    #     saml2.BINDING_HTTP_REDIRECT: 'https://xxx.okta.com/app/APPNAME/xxxxxxxxx/sso/saml',
                    # },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_POST: 'https://xxx.okta.com/app/APPNAME/xxxxxxxxxx/slo/saml',
                    },
                },
            },

        },
       },
