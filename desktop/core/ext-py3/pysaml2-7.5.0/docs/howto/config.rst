.. _howto_config:

Configuration of PySAML2 entities
=================================

Whether you plan to run a PySAML2 Service Provider, Identity Provider or an
attribute authority, you have to configure it. The format of the configuration
file is the same regardless of which type of service you plan to run.
What differs are some of the directives.
Below you will find a list of all the used directives in alphabetical order.
The configuration is written as a python module which contains a named
dictionary ("CONFIG") that contains the configuration directives.

The basic structure of the configuration file is therefore like this::

    from saml2 import BINDING_HTTP_REDIRECT

    CONFIG = {
        "entityid": "http://saml.example.com:saml/idp.xml",
        "name": "Rolands IdP",
        "service": {
            "idp": {
                "endpoints": {
                    "single_sign_on_service": [
                        (
                            "http://saml.example.com:saml:8088/sso",
                            BINDING_HTTP_REDIRECT,
                        ),
                    ],
                    "single_logout_service": [
                        (
                            "http://saml.example.com:saml:8088/slo",
                            BINDING_HTTP_REDIRECT,
                        ),
                    ],
                },
                ...
            }
        },
        "key_file": "my.key",
        "cert_file": "ca.pem",
        "xmlsec_binary": "/usr/local/bin/xmlsec1",
        "delete_tmpfiles": True,
        "metadata": {
            "local": [
                "edugain.xml",
            ],
        },
        "attribute_map_dir": "attributemaps",
        ...
    }

.. note:: You can build the metadata file for your services directly from the
    configuration. The make_metadata.py script in the PySAML2 tools directory
    will do that for you.

Configuration directives
::::::::::::::::::::::::

.. contents::
    :local:
    :backlinks: entry

General directives
------------------

logging
^^^^^^^

The logging configuration format is the python logging format.
The configuration is passed to the python logging dictionary configuration handler,
directly.

Example::

    "logging": {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] %(message)s",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "DEBUG",
                "formatter": "simple",
            },
        },
        "loggers": {
            "saml2": {
                "level": "DEBUG"
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": [
                "stdout",
            ],
        },
    },

The example configuration above will enable DEBUG logging to stdout.


debug
^^^^^

Example::

    debug: 1

Whether debug information should be sent to the log file.

http_client_timeout
^^^^^^^^^^^^^^^^^^^

Example::

    http_client_timeout: 10

The timeout of HTTP requests, in seconds. Defaults to None.

additional_cert_files
^^^^^^^^^^^^^^^^^^^^^

Example::

    additional_cert_files: ["other-cert.pem", "another-cert.pem"]

Additional public certs that will be listed.  Useful during cert/key rotation or
if you need to include a certificate chain.

Each entry in *additional_cert_files* must be a PEM formatted file with a single certificate.

entity_attributes
^^^^^^^^^^^^^^^^^

Generates an ``Attribute`` element with the given NameFormat, Name, FriendlyName and
values, each as an ``AttributeValue`` element.

The element is added under the generated metadata ``EntityDescriptor`` as an
``Extension`` element under the ``EntityAttributes`` element.

And omit

Example::

    "entity_attributes": [
      {
        "name_format": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
        "name": "urn:oasis:names:tc:SAML:profiles:subject-id:req",
        # "friendly_name" is not set
        "values": ["any"],
      },
    ]


assurance_certification
^^^^^^^^^^^^^^^^^^^^^^^

Example::

    "assurance_certification": [
        "https://refeds.org/sirtfi",
    ]

Generates an ``Attribute`` element with name-format
``urn:oasis:names:tc:SAML:2.0:attrname-format:uri`` and name
``urn:oasis:names:tc:SAML:attribute:assurance-certification`` that contains
``AttributeValue`` elements with the given values from the list.
The element is added under the generated metadata ``EntityDescriptor`` as an
``Extension`` element under the ``EntityAttributes`` element.

Read more about `representing assurance information at the specification <https://wiki.oasis-open.org/security/SAML2IDAssuranceProfile>`_.

attribute_map_dir
^^^^^^^^^^^^^^^^^

Points to a directory which has the attribute maps in Python modules.

Example::

    "attribute_map_dir": "attribute-maps"

A typical map file will look like this::

    MAP = {
        "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
        "fro": {
            'urn:mace:dir:attribute-def:aRecord': 'aRecord',
            'urn:mace:dir:attribute-def:aliasedEntryName': 'aliasedEntryName',
            'urn:mace:dir:attribute-def:aliasedObjectName': 'aliasedObjectName',
            'urn:mace:dir:attribute-def:associatedDomain': 'associatedDomain',
            'urn:mace:dir:attribute-def:associatedName': 'associatedName',
            ...
        },
        "to": {
            'aRecord': 'urn:mace:dir:attribute-def:aRecord',
            'aliasedEntryName': 'urn:mace:dir:attribute-def:aliasedEntryName',
            'aliasedObjectName': 'urn:mace:dir:attribute-def:aliasedObjectName',
            'associatedDomain': 'urn:mace:dir:attribute-def:associatedDomain',
            'associatedName': 'urn:mace:dir:attribute-def:associatedName',
            ...
        }
    }

The attribute map module contains a MAP dictionary with three items.  The
`identifier` item is the name-format you expect to support.
The *to* and *fro* sub-dictionaries then contain the mapping between the names.

As you see the format is again a python dictionary where the key is the
name to convert from, and the value is the name to convert to.

Since *to* in most cases is the inverse of the *fro* file, the
software allows you only to specify one of them, and it will
automatically create the other.

contact_person
^^^^^^^^^^^^^^

This is only used by *make_metadata.py* when it constructs the metadata for
the service described by the configuration file.
This is where you describe who can be contacted if questions arise
about the service or if support is needed. The possible types are according to
the standard **technical**, **support**, **administrative**, **billing**
and **other**.::

    contact_person: [
        {
            "givenname": "Derek",
            "surname": "Jeter",
            "company": "Example Co.",
            "mail": ["jeter@example.com"],
            "type": "technical",
        },
        {
            "givenname": "Joe",
            "surname": "Girardi",
            "company": "Example Co.",
            "mail": "girardi@example.com",
            "type": "administrative",
        },
    ]

entityid
^^^^^^^^

Example::

    entityid: "http://saml.example.com/sp"

The globally unique identifier of the entity.

.. note:: It is recommended that the entityid should point to a real
    webpage where the metadata for the entity can be found.

name
^^^^

A string value that sets the name of the PySAML2 entity.

Example::

    "name": "Example IdP"

description
^^^^^^^^^^^

A string value that sets the description of the PySAML2 entity.

Example::

    "description": "My IdP",

verify_ssl_cert
^^^^^^^^^^^^^^^

Specifies if the SSL certificates should be verified. Can be ``True`` or ``False``.
The default configuration is ``False``.

Example::

    "verify_ssl_cert": True

key_file
^^^^^^^^

Example::

    key_file: "key.pem"

*key_file* is the name of a PEM formatted file that contains the private key
of the service. This is currently used both to encrypt/sign assertions and as
the client key in an HTTPS session.

cert_file
^^^^^^^^^

Example::

    cert_file: "cert.pem"

This is the public part of the service private/public key pair.
*cert_file* must be a PEM formatted file with a single certificate.

tmp_cert_file
^^^^^^^^^^^^^

Example::
    "tmp_cert_file": "tmp_cert.pem"

*tmp_cert_file* is a PEM formatted certificate file

tmp_key_file
^^^^^^^^^^^^

Example::
    "tmp_key_file": "tmp_key.pem"

*tmp_key_file* is a PEM formatted key file.

encryption_keypairs
^^^^^^^^^^^^^^^^^^^

Indicates which certificates will be used for encryption capabilities::

    # Encryption
    'encryption_keypairs': [
        {
            'key_file': BASE_DIR + '/certificates/private.key',
            'cert_file': BASE_DIR + '/certificates/public.cert',
        },
    ],

generate_cert_info
^^^^^^^^^^^^^^^^^^

Specifies if information about the certificate should be generated.
A boolean value can be ``True`` or ``False``.

Example::

    "generate_cert_info": False


ca_certs
^^^^^^^^

This is the path to a file containing root CA certificates for SSL server certificate validation.

Example::

    "ca_certs": full_path("cacerts.txt"),


metadata
^^^^^^^^

Contains a list of places where metadata can be found. This can be

* a local directory accessible on the server the service runs on
* a local file accessible on the server the service runs on
* a remote URL serving aggregate metadata
* a metadata query protocol (MDQ) service URL

For example::

    "metadata": {
        "local": [
            "/opt/metadata"
            "metadata.xml",
            "vo_metadata.xml",
        ],
        "remote": [
            {
                "url": "https://kalmar2.org/simplesaml/module.php/aggregator/?id=kalmarcentral2&set=saml2",
                "cert": "kalmar2.cert",
            },
        ],
        "mdq": [
            {
                "url": "http://mdq.ukfederation.org.uk/",
                "cert": "ukfederation-mdq.pem",
                "freshness_period": "P0Y0M0DT2H0M0S",
            },
            {
                "url": "https://mdq.thaturl.org/",
                "disable_ssl_certificate_validation": True,
                "check_validity": False,
            },
        ],
    },

The above configuration means that the service should read two aggregate local
metadata files, one aggregate metadata file from a remote server, and query a
remote MDQ server. To verify the authenticity of the metadata aggregate
downloaded from the remote server and the MDQ server local copies of the
metadata signing certificates should be used.  These public keys must be
acquired by some secure out-of-band method before being placed on the local
file system.

When the parameter *check_validity* is set to False metadata that have expired
will be accepted as valid.

When the paramenter *disable_ssl_certificate_validation* is set to True the
validity of ssl certificate will be skipped.

When using a remote metadata source, the `node_name` option can be set to
define the name of the root node of the XML document, if needed. Usually,
the node name will be `urn:oasis:names:tc:SAML:2.0:metadata:EntityDescriptor`
or `urn:oasis:names:tc:SAML:2.0:metadata:EntityDescriptor` (node namespace
and node tag name).

When using MDQ, the `freshness_period` option can be set to define a period for
which the metadata fetched from the the MDQ server are considered fresh. After
that period has passed the metadata are not valid anymore and must be fetched
again. The period must be in the format defined in
`ISO 8601 <https://www.iso.org/iso-8601-date-and-time-format.html>`_
or `RFC3999 <https://tools.ietf.org/html/rfc3339#appendix-A>`_.

By default, if `freshness_period` is not defined, the metadata are refreshed
every 12 hours (`P0Y0M0DT12H0M0S`).


organization
^^^^^^^^^^^^

Only used by *make_metadata.py*.
Where you describe the organization responsible for the service.::

    "organization": {
        "name": [
            ("Example Company", "en"),
            ("Exempel AB", "se")
        ],
        "display_name": ["Exempel AB"],
        "url": [
            ("http://example.com", "en"),
            ("http://exempel.se", "se"),
        ],
    }

.. note:: You can specify the language of the name, or the language used on
    the webpage, by entering a tuple, instead of a simple string,
    where the second part is the language code. If you don't specify a
    language, the default is "en" (English).

preferred_binding
^^^^^^^^^^^^^^^^^

Which binding should be preferred for a service.
Example configuration::

    "preferred_binding" = {
        "single_sign_on_service": [
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact',
        ],
        "single_logout_service": [
            'urn:oasis:names:tc:SAML:2.0:bindings:SOAP',
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
            'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact',
        ],
    }

The available services are:

* manage_name_id_service
* assertion_consumer_service
* name_id_mapping_service
* authn_query_service
* attribute_service
* authz_service
* assertion_id_request_service
* artifact_resolution_service
* attribute_consuming_service
* single_logout_service


service
^^^^^^^

Which services the server will provide; those are combinations of "idp", "sp"
and "aa".
So if a server is a Service Provider (SP) then the configuration
could look something like this::

    "service": {
        "sp": {
            "name": "Rolands SP",
            "endpoints": {
                "assertion_consumer_service": ["http://localhost:8087/"],
                "single_logout_service": [
                    (
                        "http://localhost:8087/slo",
                        'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
                    ),
                ],
            },
            "required_attributes": [
                "surname",
                "givenname",
                "edupersonaffiliation",
            ],
            "optional_attributes": ["title"],
            "idp": {
                "urn:mace:umu.se:saml:roland:idp": None,
            },
        }
    },

There are two options common to all services: 'name' and 'endpoints'.
The remaining options are specific to one or the other of the service types.
Which one is specified alongside the name of the option.

accepted_time_diff
^^^^^^^^^^^^^^^^^^

If your computer and another computer that you are communicating with are not
in sync regarding the computer clock, then here you can state how big a
difference you are prepared to accept.

.. note:: This will indiscriminately affect all time comparisons.
    Hence your server may accept a statement that in fact is too old.

allow_unknown_attributes
^^^^^^^^^^^^^^^^^^^^^^^^

Indicates that attributes that are not recognized (they are not configured in
attribute-mapping), will not be discarded.
Default to False.

xmlsec_binary
^^^^^^^^^^^^^

Currently xmlsec1 binaries are used for all the signing and encryption stuff.
This option defines where the binary is situated.

Example::

    "xmlsec_binary": "/usr/local/bin/xmlsec1",

xmlsec_path
^^^^^^^^^^^

This option is used to define non-system paths where the xmlsec1 binary can be located.
It can be used when the xmlsec_binary option is not defined.

Example::

    "xmlsec_path": ["/usr/local/bin", "/opt/local/bin"],

OR::

    from saml2.sigver import get_xmlsec_binary

    if get_xmlsec_binary:
        xmlsec_path = get_xmlsec_binary(["/opt/local/bin","/usr/local/bin"])
    else:
        xmlsec_path = '/usr/bin/xmlsec1'

    "xmlsec_binary": xmlsec_path,


delete_tmpfiles
^^^^^^^^^^^^^^^

In many cases temporary files will have to be created during the
encryption/decryption/signing/validation process.
This option defines whether these temporary files will be automatically deleted when
they are no longer needed. Setting this to False, will keep these files until they are
manually deleted or automatically deleted by the OS (i.e Linux rules for /tmp).
Absence of this option, defaults to True.


valid_for
^^^^^^^^^

How many *hours* this configuration is expected to be accurate.::

    "valid_for": 24

This, of course, is only used by *make_metadata.py*.
The server will not stop working when this amount of time has elapsed :-).


metadata_key_usage
^^^^^^^^^^^^^^^^^^^

This specifies the purpose of the entity's cryptographic keys used to sign data.
If this option is not configured it will default to ``"both"``.

The possible options for this configuration are ``both``, ``signing``, ``encryption``.

If metadata_key_usage is set to ``"signing"`` or ``"both"``, and a cert_file is provided
the value of use in the KeyDescriptor element will be set to ``"signing"``.

If metadata_key_usage is set to ``"both"`` or ``"encryption"`` and a enc_cert is provided
the value of ``"use"`` in the KeyDescriptor will be set to ``"encryption"``.

Example::

    "metadata_key_usage" : "both",


secret
^^^^^^

A string value that is used in the generation of the RelayState.

Example::

    "secret": "0123456789",

crypto_backend
^^^^^^^^^^^^^^
Defines the crypto backend used for signing and encryption. The default is ``xmlsec1``.
The options are ``xmlsec1`` and ``XMLSecurity``.

If set to "XMLSecurity", the crypto backend will be pyXMLSecurity.

Example::

    "crypto_backend": "xmlsec1",

verify_encrypt_advice
^^^^^^^^^^^^^^^^^^^^^

Specifies if the encrypted assertions in the advice element should be verified.
Can be ``True`` or ``False``.

Example::

    def verify_encrypt_cert(cert_str):
        osw = OpenSSLWrapper()
        ca_cert_str = osw.read_str_from_file(full_path("root_cert/localhost.ca.crt"))
        valid, mess = osw.verify(ca_cert_str, cert_str)
        return valid

::

    "verify_encrypt_cert_advice": verify_encrypt_cert,


verify_encrypt_cert_assertion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specifies if the encrypted assertions should be verified.
Can be ``True`` or ``False``.

Example::

    "verify_encrypt_cert_assertion": verify_encrypt_cert


Specific directives
-------------------

Directives that are specific to a certain type of service.

idp/aa
^^^^^^

Directives that are specific to an IdP or AA service instance.

sign_assertion
""""""""""""""

Specifies if the IdP should sign the assertion in an authentication response
or not. Can be True or False. Default is False.

sign_response
"""""""""""""

Specifies if the IdP should sign the authentication response or not. Can be
True or False. Default is False.

encrypt_assertion
"""""""""""""""""

Specifies if the IdP should encrypt the assertions. Can be ``True`` or ``False``.
Default is ``False``.

encrypted_advice_attributes
"""""""""""""""""""""""""""
Specifies if assertions in the advice element should be encrypted.
Can be ``True`` or ``False``. Default is ``False``.

encrypt_assertion_self_contained
""""""""""""""""""""""""""""""""

Specifies if all encrypted assertions should have all namespaces self contained.
Can be ``True`` or ``False``. Default is ``True``.

want_authn_requests_signed
""""""""""""""""""""""""""

Indicates that the AuthnRequest received by this IdP should be signed. Can be ``True`` or ``False``.
The default value is ``False``.

want_authn_requests_only_with_valid_cert
""""""""""""""""""""""""""""""""""""""""

When verifying a signed AuthnRequest ignore the signature and verify the
certificate.

policy
""""""

If the server is an IdP and/or an AA, then there might be reasons to do things
differently depending on who is asking (which is the requesting service); the
policy is where this behaviour is specified.

The keys are SP entity identifiers, Registration Authority names, or 'default'.
First, the policy for the requesting service is looked up using the SP entityID.
If no such policy is found, and if the SP metadata includes a Registration
Authority then a policy for the registration authority is looked up using the
Registration Authority name. If no policy is found, then the 'default' is looked
up. If there is no default and only SP entity identifiers as keys, then the
server will only accept connections from the specified SPs.

An example might be::

    "service": {
        "idp": {
            "policy": {
                # a policy for a service
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "attribute_restrictions": {
                        "givenName": None,
                        "surName": None,
                    },
                },

                # a policy for a registration authority
                "http://www.swamid.se/": {
                    "attribute_restrictions": {
                        "givenName": None,
                    },
                },

                # the policy for all other services
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None, # means all I have
                    "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                    "entity_categories": [
                        "edugain",
                    ],
                },
            }
        }
    }

*lifetime*
    This is the maximum amount of time before the information should be
    regarded as stale. In an Assertion, this is represented in the NotOnOrAfter
    attribute.
*attribute_restrictions*
    By default, there are no restrictions as to which attributes should be
    returned. Instead, all the attributes and values that are gathered by the
    database backends will be returned if nothing else is stated.
    In the example above the SP with the entity identifier
    "urn:mace:umu.se:saml:roland:sp"
    has an attribute restriction: only the attributes
    'givenName' and 'surName' are to be returned. There are no limitations as to
    what values on these attributes that can be returned.
*name_form*
    Which name-form that should be used when sending assertions.
    Using this information, the attribute name in the data source will be mapped to
    the friendly name, and the saml attribute name will be taken from the uri/oid
    defined in the attribute map.
*nameid_format*
    Which nameid format that should be used. Defaults to
    `urn:oasis:names:tc:SAML:2.0:nameid-format:transient`.
*entity_categories*
    Entity categories to apply.
*sign*
    Possible choices: "response", "assertion", "on_demand"

If restrictions on values are deemed necessary, those are represented by
regular expressions.::

    "service": {
        "aa": {
            "policy": {
                "urn:mace:umu.se:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "attribute_restrictions": {
                         "mail": [".*\.umu\.se$"],
                    }
                }
            }
        }
    }

Here only mail addresses that end with ".umu.se" will be returned.

scope
"""""

A list of string values that will be used to set the ``<Scope>`` element
The default value of regexp is ``False``.

Example::

    "scope": ["example.org", "example.com"],


ui_info
""""""""

This determines what information to display about an entity by
configuring its mdui:UIInfo element. The configurable options include;

*privacy_statement_url*
    The URL to information about the privacy practices of the entity.
*information_url*
    Which URL contains localized information about the entity.
*logo*
    The logo image for the entity. The value is a dictionary with keys
    height, width and text.
*display_name*
    The localized name for the entity.
*description*
    The localized description of the entity. The value is a dictionary with keys
    text and lang.
*keywords*
    The localized search keywords for the entity. The value is a dictionary with keys
    lang and text.

Example::

    "ui_info": {
    "privacy_statement_url": "http://example.com/saml2/privacyStatement.html",
    "information_url": "http://example.com/saml2/info.html",
    "logo": {
        "height": "40",
        "width" : "30",
        "text": "http://example.com/logo.jpg"
    },
    "display_name": "Example Co.",
    "description" : {"text":"Exempel Bolag","lang":"se"},
    "keywords": {"lang":"en", "text":["foo", "bar"]}
    }


name_qualifier
""""""""""""""

A string value that sets the ``NameQualifier`` attribute of the ``<NameIdentifier>`` element.

Example::

    "name_qualifier": "http://authentic.example.com/saml/metadata",


session_storage
"""""""""""""""

Example::

    "session_storage": ("mongodb", "session")

domain
""""""

Example::

    "domain": "umu.se",

sp
^^

Directives specific to SP instances

authn_requests_signed
"""""""""""""""""""""

Indicates if the Authentication Requests sent by this SP should be signed
by default. This can be overridden by application code for a specific call.

This sets the AuthnRequestsSigned attribute of the SPSSODescriptor node
of the metadata so the IdP will know this SP preference.

Valid values are True or False. Default value is True.

Example::

    "service": {
        "sp": {
            "authn_requests_signed": True,
        }
    }


want_response_signed
""""""""""""""""""""

Indicates that Authentication Responses to this SP must be signed. If set to
True, the SP will not consume any SAML Responses that are not signed.

Valid values are True or False. Default value is True.

Example::

    "service": {
        "sp": {
            "want_response_signed": True,
        }
    }


force_authn
"""""""""""

Mandates that the identity provider MUST authenticate the presenter directly
rather than rely on a previous security context.

Example::

    "service": {
        "sp": {
            "force_authn": True,
        }
    }


name_id_policy_format
"""""""""""""""""""""

A string value that will be used to set the ``Format`` attribute of the
``<NameIDPolicy>`` element of an ``<AuthnRequest>``.

Example::

    "service": {
        "sp": {
            "name_id_policy_format": "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
        }
    }


name_id_format_allow_create
"""""""""""""""""""""""""""

A boolean value (``True`` or ``False``) that will be used to set the ``AllowCreate``
attribute of the ``<NameIDPolicy>`` element of an ``<AuthnRequest>``.

Example::

    "service": {
        "sp": {
            "name_id_format_allow_create": True,
        }
    }


name_id_format
""""""""""""""

A list of string values that will be used to set the ``<NameIDFormat>`` element of the
metadata of an entity.

Example::

    "service": {
        "sp": {
            "name_id_format": [
                "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
                "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
            ]
        }
    }


allow_unsolicited
"""""""""""""""""

When set to true, the SP will consume unsolicited SAML Responses, i.e. SAML
Responses for which it has not sent a respective SAML Authentication Request.

Example::

    "service": {
        "sp": {
            "allow_unsolicited": True,
        }
    }

hide_assertion_consumer_service
"""""""""""""""""""""""""""""""

When set to true the AuthnRequest will not include the
AssertionConsumerServiceURL and ProtocolBinding attributes.

Example::

    "service": {
        "sp": {
            "hide_assertion_consumer_service": True,
        }
    }

This kind of functionality is required for the eIDAS SAML profile.

> eIDAS-Connectors SHOULD NOT provide AssertionConsumerServiceURL.

.. note::
    This is relevant only for the eIDAS SAML profile.


sp_type
"""""""

Sets the value for the eIDAS SPType node. By the eIDAS specification the value
can be one of *public* and *private*.

Example::

    "service": {
        "sp": {
            "sp_type": "private",
        }
    }

.. note::
    This is relevant only for the eIDAS SAML profile.


sp_type_in_metadata
"""""""""""""""""""

Whether the SPType node should appear in the metadata document
or as part of each AuthnRequest.

Example::

    "service": {
        "sp": {
            "sp_type_in_metadata": True,
        }
    }

.. note::
    This is relevant only for the eIDAS SAML profile.


requested_attributes
""""""""""""""""""""

A list of attributes that the SP requires from an eIDAS-Service (IdP).
Each attribute is an object with the following attributes:

* friendly_name
* name
* required
* name_format

Where friendly_name is an attribute name such as *DateOfBirth*, name is the
full attribute name such as
*http://eidas.europa.eu/attributes/naturalperson/DateOfBirth*, required
indicates whether this attributed is required for authentication, and
name_format indicates the name format for that attribute, such as
*urn:oasis:names:tc:SAML:2.0:attrname-format:uri*.

It is mandatory that at least name or friendly_name is set.
By default attributes are assumed to be required.
Missing attributes are inferred based on the attribute maps data.

Example::

    "service": {
        "sp": {
            "requested_attributes": [
                {
                    "name": "http://eidas.europa.eu/attributes/naturalperson/PersonIdentifier",
                },
                {
                    "friendly_name": "DateOfBirth",
                    "required": False,
                },
            ],
        }
    }

.. note::
    This is relevant only for the eIDAS SAML profile.

    This option is different from the required_attributes and
    optional_attributes parameters that control the requested
    attributes in the metadata of an SP.


idp
"""

Defines the set of IdPs that this SP is allowed to use; if unset, all listed
IdPs may be used.  If set, then the value is expected to be a list with entity
identifiers for the allowed IdPs.
A typical configuration, when the allowed set of IdPs are limited, would look
something like this::

    "service": {
        "sp": {
            "idp": ["urn:mace:umu.se:saml:roland:idp"],
        }
    }

In this case, the SP has only one IdP it can use.

optional_attributes
"""""""""""""""""""

Attributes that this SP would like to receive from IdPs.

Example::

    "service": {
        "sp": {
            "optional_attributes": ["title"],
        }
    }

Since the attribute names used here are the user-friendly ones an attribute map
must exist, so that the server can use the full name when communicating
with other servers.

required_attributes
"""""""""""""""""""

Attributes that this SP demands to receive from IdPs.

Example::

    "service": {
        "sp": {
            "required_attributes": [
                "surname",
                "givenName",
                "mail",
            ],
        }
    }

Again as for *optional_attributes* the names given are expected to be
the user-friendly names.

want_assertions_signed
""""""""""""""""""""""

Indicates if this SP wants the IdP to send the assertions signed. This
sets the WantAssertionsSigned attribute of the SPSSODescriptor node
of the metadata so the IdP will know this SP preference.

Valid values are True or False. Default value is False.

Example::

    "service": {
        "sp": {
            "want_assertions_signed": True,
        }
    }

want_assertions_or_response_signed
""""""""""""""""""""""""""""""""""

Indicates that *either* the Authentication Response *or* the assertions
contained within the response to this SP must be signed.

Valid values are True or False. Default value is False.

This configuration directive **does not** override ``want_response_signed``
or ``want_assertions_signed``. For example, if ``want_response_signed`` is True
and the Authentication Response is not signed an exception will be thrown
regardless of the value for this configuration directive.

Thus to configure the SP to accept either a signed response or signed assertions
set ``want_response_signed`` and ``want_assertions_signed`` both to False and
this directive to True.

Example::

    "service": {
        "sp": {
            "want_response_signed": False,
            "want_assertions_signed": False,
            "want_assertions_or_response_signed": True,
        }
    }

discovery_response
""""""""""""""""""

This configuration allows the SP to include one or more Discovery Response Endpoints.
The discovery_response can be the just the URL::

    "discovery_response":["http://example.com/sp/ds"],

or it can be a 2 tuple of the URL+Binding::

    from saml2.extension.idpdisc import BINDING_DISCO

    "discovery_response": [("http://example.com/sp/ds", BINDING_DISCO)]

ecp
"""

This configuration option takes a dictionary with the ecp client IP address as the
key and the entity ID as the value.

Example::

    "ecp": {
        "203.0.113.254": "http://example.com/idp",
    }

requested_attribute_name_format
"""""""""""""""""""""""""""""""

This sets the NameFormat attribute in the ``<RequestedAttribute>`` element.
The name formats are defined in saml2.saml.py. If not configured the default is ``NAME_FORMAT_URI``
which corresponds to ``urn:oasis:names:tc:SAML:2.0:attrname-format:uri``.

Example::

    from saml2.saml import NAME_FORMAT_BASIC

::

    "requested_attribute_name_format": NAME_FORMAT_BASIC


requested_authn_context
"""""""""""""""""""""""

This configuration option defines the ``<RequestedAuthnContext>`` for an AuthnRequest by
a client. The value is a dictionary with two fields

- ``authn_context_class_ref`` a list of string values representing
  ``<AuthnContextClassRef>`` elements.

- ``comparison`` a string representing the Comparison xml-attribute value of the
  ``<RequestedAuthnContext>`` element. Per the SAML core specificiation the value should
  be one of "exact", "minimum", "maximum", or "better". The default is "exact".

Example::

    "service": {
        "sp": {
            "requested_authn_context": {
                "authn_context_class_ref": [
                    "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
                    "urn:oasis:names:tc:SAML:2.0:ac:classes:TLSClient",
                ],
                "comparison": "minimum",
            }
        }
    }


idp/aa/sp
^^^^^^^^^

If the configuration is covering both two or three different service types
(like if one server is actually acting as both an IdP and an SP) then in some
cases you might want to have these below different for the different services.

endpoints
"""""""""

Where the endpoints for the services provided are.
This directive has as value a dictionary with one or more of the following keys:

* artifact_resolution_service (aa, idp and sp)
* `assertion_consumer_service <https://wiki.shibboleth.net/confluence/display/CONCEPT/AssertionConsumerService>`_ (sp)
* assertion_id_request_service (aa, idp)
* attribute_service (aa)
* manage_name_id_service (aa, idp)
* name_id_mapping_service (idp)
* single_logout_service (aa, idp, sp)
* single_sign_on_service (idp)

The value per service is a list of endpoint specifications.
An endpoint specification can either be just the URL::

  ”http://localhost:8088/A"

or it can be a 2-tuple (URL+binding)::

  from saml2 import BINDING_HTTP_POST
  (”http://localhost:8087/A”, BINDING_HTTP_POST)

or a 3-tuple (URL+binding+index)::

  from saml2 import BINDING_HTTP_POST
  (”http://lingon.catalogix.se:8087/A”, BINDING_HTTP_POST, 1)

If no binding is specified, no index can be set.
If no index is specified, the index is set based on the position in the list.

Example::

    "service":
        "idp": {
            "endpoints": {
                "single_sign_on_service": [
                    ("http://localhost:8088/sso", BINDING_HTTP_REDIRECT),
                ],
                "single_logout_service": [
                    ("http://localhost:8088/slo", BINDING_HTTP_REDIRECT),
                ],
            },
        },
    },

error_url
"""""""""

The URL to which the user's browser may be redirected in the event of a failure.

Example::

    "service":
        "idp": {
            "error_url": "http://localhost:8088/error_page",
        },
    }

only_use_keys_in_metadata
"""""""""""""""""""""""""

If set to False, the certificate contained in a SAML message will be used for
signature verification.
Default True.

validate_certificate
""""""""""""""""""""

Indicates that the certificate used in sign SAML messages must be valid.
Default to False.

logout_requests_signed
""""""""""""""""""""""

Indicates if this entity will sign the Logout Requests originated from it.

This can be overridden by application code for a specific call.

Valid values are True or False. Default value is False.

Example::

    "service": {
        "sp": {
            "logout_requests_signed": False,
        }
    }


signing_algorithm
"""""""""""""""""

Default algorithm to be used. Example::

    "service": {
        "sp": {
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha512",
            "digest_algorithm": "http://www.w3.org/2001/04/xmlenc#sha512",
        }
    }


digest_algorithm
"""""""""""""""""

Default algorithm to be used. Example::

    "service": {
        "idp": {
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha512",
            "digest_algorithm": "http://www.w3.org/2001/04/xmlenc#sha512",
        }
    }


logout_responses_signed
"""""""""""""""""""""""

Indicates if this entity will sign the Logout Responses while processing
a Logout Request.

This can be overridden by application code when calling ``handle_logout_request``.

Valid values are True or False. Default value is False.

Example::

    "service": {
        "sp": {
            "logout_responses_signed": False,
        }
    }


subject_data
""""""""""""

The name of a database where the map between a local identifier and
a distributed identifier is kept. By default, this is a shelve database.
So if you just specify a name, then a shelve database with that name
is created. On the other hand, if you specify a tuple, then the first
element in the tuple specifies which type of database you want to use
and the second element is the address of the database.

Example::

    "subject_data": "./idp.subject.db",

or if you want to use for instance memcache::

    "subject_data": ("memcached", "localhost:12121"),

*shelve* and *memcached* are the only database types that are currently
supported.


virtual_organization
""""""""""""""""""""

Gives information about common identifiers for virtual_organizations::

    "virtual_organization": {
        "urn:mace:example.com:it:tek": {
            "nameid_format": "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
            "common_identifier": "umuselin",
        }
    },

Keys in this dictionary are the identifiers for the virtual organizations.
The arguments per organization are 'nameid_format' and 'common_identifier'.
Useful if all the IdPs and AAs that are involved in a virtual organization
have common attribute values for users that are part of the VO.

Complete example
----------------

We start with a simple but fairly complete Service provider configuration::

    from saml2 import BINDING_HTTP_REDIRECT

    CONFIG = {
        "entityid": "http://example.com/sp/metadata.xml",
        "service": {
            "sp": {
                "name": "Example SP",
                "endpoints": {
                    "assertion_consumer_service": ["http://example.com/sp"],
                    "single_logout_service": [
                        ("http://example.com/sp/slo", BINDING_HTTP_REDIRECT),
                    ],
                },
            }
        },
        "key_file": "./mykey.pem",
        "cert_file": "./mycert.pem",
        "xmlsec_binary": "/usr/local/bin/xmlsec1",
        "delete_tmpfiles": True,
        "attribute_map_dir": "./attributemaps",
        "metadata": {
            "local": ["idp.xml"]
        }
        "organization": {
            "display_name": ["Example identities"]
        }
        "contact_person": [
            {
                "givenname": "Roland",
                "surname": "Hedberg",
                "phone": "+46 90510",
                "mail": "roland@example.com",
                "type": "technical",
            },
        ]
    }

This is the typical setup for an SP.
A metadata file to load is *always* needed, but it can, of course,
contain anything from 1 up to many entity descriptions.

------

A slightly more complex configuration::

    from saml2 import BINDING_HTTP_REDIRECT

    CONFIG = {
        "entityid": "http://sp.example.com/metadata.xml",
        "service": {
            "sp": {
                "name": "Example SP",
                "endpoints": {
                    "assertion_consumer_service": ["http://sp.example.com/"],
                    "single_logout_service": [
                        ("http://sp.example.com/slo", BINDING_HTTP_REDIRECT),
                    ],
                },
                "subject_data": ("memcached", "localhost:12121"),
                "virtual_organization": {
                    "urn:mace:example.com:it:tek": {
                        "nameid_format": "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
                        "common_identifier": "eduPersonPrincipalName",
                    }
                },
            }
        },
        "key_file": "./mykey.pem",
        "cert_file": "./mycert.pem",
        "xmlsec_binary": "/usr/local/bin/xmlsec1",
        "delete_tmpfiles": True,
        "metadata": {
            "local": ["example.xml"],
            "remote": [
                {
                    "url":"https://kalmar2.org/simplesaml/module.php/aggregator/?id=kalmarcentral2&set=saml2",
                    "cert":"kalmar2.pem",
                }
            ]
        },
        "attribute_maps": "attributemaps",
        "organization": {
            "display_name": ["Example identities"]
        }
        "contact_person": [
            {
                "givenname": "Roland",
                "surname": "Hedberg",
                "phone": "+46 90510",
                "mail": "roland@example.com",
                "type": "technical",
            },
        ]
    }

Uses metadata files, both local and remote, and will talk to whatever
IdP that appears in any of the metadata files.

Other considerations
::::::::::::::::::::

Entity Categories
-----------------

Entity categories and their attributes are defined in
src/saml2/entity_category/<registrar-of-entity-category>.py.
We can configure Entity Categories in PySAML2 in two ways:

1. Using the configuration options *entity_category_support* or
   *entity_category*, to generate the appropriate EntityAttribute metadata
   elements.
2. Using the configuration option *entity_categories* as part of the policy
   configuration, to make the entity category work as a filter on the
   attributes that will be released.

If the entity categories are configured as metadata, as follow::

    'debug' : True,
    'xmlsec_binary': get_xmlsec_binary([/usr/bin/xmlsec1']),
    'entityid': '%s/metadata' % BASE_URL,

    # or entity_category: [ ... ]
    'entity_category_support': [
        edugain.COCO, # "http://www.geant.net/uri/dataprotection-code-of-conduct/v1"
        refeds.RESEARCH_AND_SCHOLARSHIP,
    ],

    'attribute_map_dir': 'data/attribute-maps',
    'description': 'SAML2 IDP',

    'service': {
        'idp': {
    ...

In the metadata we'll then have::

    <md:Extensions>
      <mdattr:EntityAttributes>
        <saml:Attribute Name="http://macedir.org/entity-category-support" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
          <saml:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xsi:type="xs:string">http://www.geant.net/uri/dataprotection-code-of-conduct/v1</saml:AttributeValue>
          <saml:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xsi:type="xs:string">http://refeds.org/category/research-and-scholarship</saml:AttributeValue>
        </saml:Attribute>
      </mdattr:EntityAttributes>

If the entity categories are configurated in the policy section, they will act
as filters on the released attributes.

Example::

    "policy": {
      "default": {
        "lifetime": {"minutes": 15},
        # if the SP is not conform to entity_categories
        # the attributes will not be released
        "entity_categories": ["refeds",],
