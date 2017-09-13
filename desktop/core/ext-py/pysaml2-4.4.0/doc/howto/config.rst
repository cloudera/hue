.. _howto_config:

Configuration of pySAML2 entities
=================================

Whether you plan to run a pySAML2 Service Provider, Identity Provider or an
attribute authority you have to configure it. The format of the configuration
file is the same regardless of which type of service you plan to run.
What differs are some of the directives.
Below you will find a list of all the used directives in alphabetical order.
The configuration is written as a python module which contains a named
dictionary ("CONFIG") that contains the configuration directives.

The basic structure of the configuration file is therefore like this::

    from saml2 import BINDING_HTTP_REDIRECT

    CONFIG = {
        "entityid" : "http://saml.example.com:saml/idp.xml",
        "name" : "Rolands IdP",
        "service": {
            "idp": {
                "endpoints" : {
                    "single_sign_on_service" : [
                            ("http://saml.example.com:saml:8088/sso",
                                BINDING_HTTP_REDIRECT)],
                    "single_logout_service": [
                            ("http://saml.example.com:saml:8088/slo",
                                BINDING_HTTP_REDIRECT)]
                },
                ...
            }
        },
        "key_file" : "my.key",
        "cert_file" : "ca.pem",
        "xmlsec_binary" : "/usr/local/bin/xmlsec1",
        "metadata": {
            "local": ["edugain.xml"],
        },
        "attribute_map_dir" : "attributemaps",
        ...
    }

.. note:: You can build the metadata file for your services directly from the
    configuration.The make_metadata.py script in the pySAML2 tools directory
    will do that for you.

Configuration directives
::::::::::::::::::::::::

.. contents::
    :local:
    :backlinks: entry

General directives
------------------

attribute_map_dir
^^^^^^^^^^^^^^^^^

Format::

    "attribute_map_dir": "attribute-maps"
    
Points to a directory which has the attribute maps in Python modules.
A typical map file will looks like this::

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
software allowes you to only specify one of them and it will 
automatically create the other.

cert_file
^^^^^^^^^

Format::

    cert_file: "cert.pem"

This is the public part of the service private/public key pair.
*cert_file* must be a PEM formatted certificate chain file.

contact_person
^^^^^^^^^^^^^^

This is only used by *make_metadata.py* when it constructs the metadata for 
the service described by the configuration file.
This is where you describe who can be contacted if questions arise
about the service or if support is needed. The possible types are according to
the standard **technical**, **support**, **administrative**, **billing** 
and **other**.::

    contact_person: [{
        "givenname": "Derek",
        "surname": "Jeter",
        "company": "Example Co.",
        "mail": ["jeter@example.com"],
        "type": "technical",
    },{
        "givenname": "Joe",
        "surname": "Girardi",
        "company": "Example Co.",
        "mail": "girardi@example.com",
        "type": "administrative",
    }]

debug
^^^^^

Format::

    debug: 1

Whether debug information should be sent to the log file.

entityid
^^^^^^^^

Format::

    entityid: "http://saml.example.com/sp"

The globally unique identifier of the entity.

.. note:: It is recommended that the entityid should point to a real
    webpage where the metadata for the entity can be found.

key_file
^^^^^^^^

Format::

    key_file: "key.pem"

*key_file* is the name of a PEM formatted file that contains the private key
of the service. This is presently used both to encrypt/sign assertions and as
the client key in an HTTPS session.

metadata
^^^^^^^^

Contains a list of places where metadata can be found. This can be either
a file accessible on the server the service runs on, or somewhere on the net.::

    "metadata" : {
        "local": [
            "metadata.xml", "vo_metadata.xml"
            ],
        "remote": [
            {
                "url":"https://kalmar2.org/simplesaml/module.php/aggregator/?id=kalmarcentral2&set=saml2",
                "cert":"kalmar2.cert"
            }],
    },

The above configuration means that the service should read two local 
metadata files, and on top of that load one from the net. To verify the
authenticity of the file downloaded from the net, the local copy of the 
public key should be used.
This public key must be acquired by some out-of-band method.

organization
^^^^^^^^^^^^

Only used by *make_metadata.py*.
Where you describe the organization responsible for the service.::

    "organization": {
        "name": [("Example Company","en"), ("Exempel AB","se")],
        "display_name": ["Exempel AB"],
        "url": [("http://example.com","en"),("http://exempel.se","se")],
    }

.. note:: You can specify the language of the name, or the language used on
    the webpage, by entering a tuple, instead of a simple string, 
    where the second part is the language code. If you don't specify a
    language the default is "en" (English).

service
^^^^^^^

Which services the server will provide; those are combinations of "idp", "sp" 
and "aa".
So if a server is a Service Provider (SP) then the configuration 
could look something like this::

    "service": {
        "sp":{
            "name" : "Rolands SP",
            "endpoints":{
                "assertion_consumer_service": ["http://localhost:8087/"],
                "single_logout_service" : [("http://localhost:8087/slo",
                               'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect')],
            },
            "required_attributes": ["surname", "givenname", "edupersonaffiliation"],
            "optional_attributes": ["title"],
            "idp": {
                "urn:mace:umu.se:saml:roland:idp": None,
            },
        }
    },
    
There are two options common to all services: 'name' and 'endpoints'.
The remaining options are specific to one or the other of the service types.
Which one is specified along side the name of the option.

accepted_time_diff
^^^^^^^^^^^^^^^^^^

If your computer and another computer that you are communicating with are not
in synch regarding the computer clock, then here you can state how big a
difference you are prepared to accept.

.. note:: This will indiscriminately effect all time comparisons.
    Hence your server my accept a statement that in fact is to old.

xmlsec_binary
^^^^^^^^^^^^^

Presently xmlsec1 binaries are used for all the signing and encryption stuff.
This option defines where the binary is situated.

Example::

    "xmlsec_binary": "/usr/local/bin/xmlsec1",

valid_for
^^^^^^^^^

How many *hours* this configuration is expected to be accurate.::

    "valid_for": 24

This of course is only used by *make_metadata.py*.
The server will not stop working when this amount of time has elapsed :-).

Specific directives
-------------------

Directives that are specific to a certain type of service.

idp/aa
^^^^^^

Directives that are specific to an IdP or AA service instance

sign_assertion
""""""""""""""

Specifies if the IdP should sign the assertion in an authentication response
or not. Can be True or False. Default is False.

sign_response
"""""""""""""

Specifies if the IdP should sign the authentication response or not. Can be
True or False. Default is False.


policy
""""""

If the server is an IdP and/or an AA then there might be reasons to do things
differently depending on who is asking; this is where that is specified.
The keys are 'default' and SP entity identifiers.  Default is used whenever
there is no entry for a specific SP. The reasoning is also that if there is
no default and only SP entity identifiers as keys, then the server will only
except connections from the specified SPs.
An example might be::

    "service": {
        "idp": {
            "policy": {
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None, # means all I have
                    "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
                },
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "attribute_restrictions":{
                        "givenName": None,
                        "surName": None,
                    }
                }
            }
        }
    }
    
*lifetime* 
    This is the maximum amount of time before the information should be 
    regarded as stale. In an Assertion this is represented in the NotOnOrAfter 
    attribute.    
*attribute_restrictions*
    By default there is no restrictions as to which attributes should be
    return. Instead all the attributes and values that are gathered by the 
    database backends will be returned if nothing else is stated.
    In the example above the SP with the entity identifier
    "urn:mace:umu.se:saml:roland:sp" 
    has an attribute restriction: only the attributes
    'givenName' and 'surName' are to be returned. There is no limitations as to
    what values on these attributes that can be returned.
*name_form*
    Which name-form that should be used when sending assertions.
    Using this information the attribute name in the data source will be mapped to
    the friendly name, and the saml attribute name will be taken from the uri/oid
    defined in the attribute map.

If restrictions on values are deemed necessary those are represented by 
regular expressions.::

    "service": {
        "aa": {
            "policy": {
                "urn:mace:umu.se:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "attribute_restrictions":{
                         "mail": [".*\.umu\.se$"],
                    }
                }
            }
        }
    }

Here only mail addresses that end with ".umu.se" will be returned.

sp
^^

Directives specific to SP instances

authn_requests_signed
"""""""""""""""""""""

Indicates if the Authentication Requests sent by this SP should be signed
by default. This can be overriden by application code for a specific call.

This sets the AuthnRequestsSigned attribute of the SPSSODescriptor node
of the metadata so the IdP will know this SP preference.

Valid values are True or False. Default value is True.

Example::

    "service": {
        "sp": {
            "authn_requests_signed": True,
        }
    }


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

In this case the SP has only one IdP it can use.

optional_attributes
"""""""""""""""""""

Attributes that this SP would like to receive from IdPs.

Example::

    "service": {
        "sp": {
            "optional_attributes": ["title"],
        }
    }
    
Since the attribute names used here are the user friendly ones an attribute map
must exist, so that the server can use the full name when communicating
with other servers.

required_attributes
"""""""""""""""""""

Attributes that this SP demands to receive from IdPs.

Example::

    "service": {
        "sp": {
            "required_attributes": ["surname", "givenName", "mail"],
        }
    }

Again as for *optional_attributes* the names given are expected to be 
the user friendly names.

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


idp/aa/sp
^^^^^^^^^ 

If the configuration is covering both two or three different service types
(like if one server is actually acting as both an IdP and a SP) then in some
cases you might want to have these below different for the different services.

endpoints
"""""""""

Where the endpoints for the services provided are.
This directive has as value a dictionary with one or more of the following keys:

* artifact_resolution_service (aa, idp and sp)
* assertion_consumer_service (sp)
* assertion_id_request_service (aa, idp)
* attribute_service (aa)
* manage_name_id_service (aa, idp)
* name_id_mapping_service (idp)
* single_logout_service (aa, idp, sp)
* single_sign_on_service (idp)

The values per service is a list of endpoint specifications.
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
            "endpoints" : {
                "single_sign_on_service" : [
                        ("http://localhost:8088/sso", BINDING_HTTP_REDIRECT)],
                "single_logout_service": [
                        ("http://localhost:8088/slo", BINDING_HTTP_REDIRECT)]
            },
        },
    },

logout_requests_signed
""""""""""""""""""""""

Indicates if this entity will sign the Logout Requests originated from it.

This can be overriden by application code for a specific call.

Valid values are True or False. Default value is False.

Example::

    "service": {
        "sp": {
            "logout_requests_signed": False,
        }
    }

subject_data
""""""""""""

The name of a database where the map between a local identifier and 
a distributed identifier is kept. By default this is a shelve database.
So if you just specify name, then a shelve database with that name
is created. On the other hand if you specify a tuple then the first
element in the tuple specifies which type of database you want to use
and the second element is the address of the database.

Example::

    "subject_data": "./idp.subject.db",

or if you want to use for instance memcache::

    "subject_data": ("memcached", "localhost:12121"),

*shelve* and *memcached* are the only database types that are presently
supported.


virtual_organization
""""""""""""""""""""

Gives information about common identifiers for virtual_organizations::

    "virtual_organization" : {
        "urn:mace:example.com:it:tek":{
            "nameid_format" : "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
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
        "entityid" : "http://example.com/sp/metadata.xml",
        "service": {
            "sp":{
                "name" : "Example SP",
                "endpoints":{
                    "assertion_consumer_service": ["http://example.com/sp"],
                    "single_logout_service" : [("http://example.com/sp/slo",
                                                BINDING_HTTP_REDIRECT)],
                },
            }
        },
        "key_file" : "./mykey.pem",
        "cert_file" : "./mycert.pem",
        "xmlsec_binary" : "/usr/local/bin/xmlsec1",
        "attribute_map_dir": "./attributemaps",
        "metadata": {
            "local": ["idp.xml"]
        }
        "organization": {
            "display_name":["Example identities"]
        }
        "contact_person": [{
            "givenname": "Roland",
            "surname": "Hedberg",
            "phone": "+46 90510",
            "mail": "roland@example.com",
            "type": "technical",
            }]
    }

This is the typical setup for a SP.
A metadata file to load is *always* needed, but it can of course
contain anything from 1 up to many entity descriptions.

------

A slightly more complex configuration::

    from saml2 import BINDING_HTTP_REDIRECT

    CONFIG = {
        "entityid" : "http://sp.example.com/metadata.xml",
        "service": {
            "sp":{
                "name" : "Example SP",
                "endpoints":{
                    "assertion_consumer_service": ["http://sp.example.com/"],
                    "single_logout_service" : [("http://sp.example.com/slo",
                                   BINDING_HTTP_REDIRECT)],
                },
                "subject_data": ("memcached", "localhost:12121"),
                "virtual_organization" : {
                    "urn:mace:example.com:it:tek":{
                        "nameid_format" : "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
                        "common_identifier": "eduPersonPrincipalName",
                    }
                },
            }
        },
        "key_file" : "./mykey.pem",
        "cert_file" : "./mycert.pem",
        "xmlsec_binary" : "/usr/local/bin/xmlsec1",
        "metadata" : { 
            "local": ["example.xml"],
            "remote": [{ 
                "url":"https://kalmar2.org/simplesaml/module.php/aggregator/?id=kalmarcentral2&set=saml2",
                "cert":"kalmar2.pem"}]
        },
        "attribute_maps" : "attributemaps",
        "organization": {
            "display_name":["Example identities"]
        }
        "contact_person": [{
            "givenname": "Roland",
            "surname": "Hedberg",
            "phone": "+46 90510",
            "mail": "roland@example.com",
            "type": "technical",
            }]
    }
    
Uses metadata files, both local and remote, and will talk to whatever 
IdP that appears in any of the metadata files. 

Other considerations
::::::::::::::::::::

Entity Categories
-----------------
Entity categories and their attributes are defined in src/saml2/entity_category/<registrar of entcat>.py
