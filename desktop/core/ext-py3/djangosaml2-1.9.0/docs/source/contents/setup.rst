Setup
-----

Prepare Environment and Install Requirements
============================================

PySAML2 uses xmlsec1_ binary to sign SAML assertions so you need to install
it either through your operating system package or by compiling the source
code. It doesn't matter where the final executable is installed because
you will need to set the full path to it in the configuration stage.

.. _xmlsec1: http://www.aleksey.com/xmlsec/

Now you can install the djangosaml2 package using pip. This
will also install PySAML2 and its dependencies automatically::

  apt install python3-pip xmlsec1 python3-dev libssl-dev libsasl2-dev
  pip3 install virtualenv
  mkdir djangosaml2_project && cd "$_"
  virtualenv -ppython3 env
  source env/bin/activate
  pip install djangosaml2


Configuration
-------------

There are three things you need to setup to make djangosaml2 work in your
Django project:

1. **settings.py** as you may already know, it is the main Django
   configuration file.
2. **urls.py** is the file where you will include djangosaml2 urls.
3. **pysaml2** specific files such as an attribute map directory and a
   certificates involved in SAML2 signature and encryption operations.

The first thing you need to do is add ``djangosaml2`` to the list of
installed apps::

  INSTALLED_APPS = (
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.sites',
      'django.contrib.messages',
      'django.contrib.admin',

      'djangosaml2',  # new application
  )


SameSite cookie
===============

Add the SAML Session Middleware as follow, this is needed for SameSite Cookies::

  MIDDLEWARE.append('djangosaml2.middleware.SamlSessionMiddleware')

By default, djangosaml2 handle the saml2 session in a separate cookie.
The storage linked to it is accessible by default at `request.saml_session`.
You can even configure the SAML cookie name as follows::

  SAML_SESSION_COOKIE_NAME = 'saml_session'

By default, djangosaml2 will set "SameSite=None" for the SAML session cookie. This value can be configured as follows::

  SAML_SESSION_COOKIE_SAMESITE = 'Lax'

Remember that in your browser "SameSite=None" attribute MUST also
have the "Secure" attribute, which is required in order to use "SameSite=None", otherwise the cookie will be blocked, so you must also set::

  SESSION_COOKIE_SECURE = True

.. Note::

  djangosaml2 will by default attempt to set the ``SameSite`` attribute of the SAML session cookie to ``None`` so that it can be
  used in cross-site requests, but this is only possible with Django 3.1 or higher. If you are experiencing issues with
  unsolicited requests or cookies not being sent (particularly when using the HTTP-POST binding), consider upgrading
  to Django 3.1 or higher. If you can't do that, configure "allow_unsolicited" to True in pySAML2 configuration.

Authentication backend
======================

Then you have to add the ``djangosaml2.backends.Saml2Backend``
authentication backend to the list of authentications backends.
By default only the ModelBackend included in Django is configured.
A typical configuration would look like this::

  AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.ModelBackend',
      'djangosaml2.backends.Saml2Backend',
  )

It is possible to subclass the provided Saml2Backend and customize the behaviour
by overriding some methods. This way you can perform your custom cleaning or authorization
policy, and modify the way users are looked up and created.

Default Login path
==================

Finally we have to tell Django what the new login url we want to use is::

  LOGIN_URL = '/saml2/login/'
  SESSION_EXPIRE_AT_BROWSER_CLOSE = True

Here we are telling Django that any view that requires an authenticated
user should redirect the user browser to that url if the user has not
been authenticated before. We are also telling that when the user closes
his browser, the session should be terminated. This is useful in SAML2
federations where the logout protocol is not always available.

.. Note::

  The login url starts with ``/saml2/`` as an example but you can change that
  if you want. Check the section about changes in the ``urls.py``
  file for more information.

If you want to allow several authentication mechanisms in your project
you should set the LOGIN_URL option to another view and put a link in such
view to djangosaml2 wb path, like ``/saml2/login/``.

Handling Post-Login Redirects
=============================

It is often desirable for the client to maintain the URL state (or at least manage it) so that
the URL once authentication has completed is consistent with the desired application state (such
as retaining query parameters, etc.)  By default, the HttpRequest objects get_host() method is used
to determine the hostname of the server, and redirect URL's are allowed so long as the destination
host matches the output of get_host().  However, in some cases it becomes desirable for additional
hostnames to be used for the post-login redirect.  In such cases, the setting::

  SAML_ALLOWED_HOSTS = []

May be set to a list of allowed post-login redirect hostnames (note, the URL components beyond the hostname
may be specified by the client - typically with the ?next= parameter.)

In the absence of a ``?next=parameter``, the ``ACS_DEFAULT_REDIRECT_URL`` or ``LOGIN_REDIRECT_URL`` setting will
be used (assuming the destination hostname either matches the output of get_host() or is included in the
``SAML_ALLOWED_HOSTS`` setting)

Redirect URL validation
=======================

Djangosaml2 will validate the redirect URL before redirecting to its value. In
some edge-cases, valid redirect targets will fail to pass this check. This is
limited to URLs that are a single 'word' without slashes. (For example, 'home'
but also 'page-with-dashes').

In this situation, the best solution would be to add a slash to the URL. For
example: 'home' could be '/home' or 'home/'.
If this is unfeasible, this strict validation can be turned off by setting
``SAML_STRICT_URL_VALIDATION`` to ``False`` in settings.py.

During validation, `Django named URL patterns <https://docs.djangoproject.com/en/dev/topics/http/urls/#naming-url-patterns>`_
will also be resolved. Turning off strict validation will prevent this from happening.

Preferred sso binding
=====================

Use the following setting to choose your preferred binding for SP initiated sso requests::

  SAML_DEFAULT_BINDING

For example::

  import saml2
  SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_POST

Preferred Logout binding
========================

Use the following setting to choose your preferred binding for SP initiated logout requests::

  SAML_LOGOUT_REQUEST_PREFERRED_BINDING

For example::

  import saml2
  SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_POST

Ignore Logout errors
====================

When logging out, a SAML IDP will return an error on invalid conditions, such as the IDP-side session being expired.
Use the following setting to ignore these errors and perform a local Django logout nonetheless::

  SAML_IGNORE_LOGOUT_ERRORS = True


Discovery Service
=================
If you want to use a SAML Discovery Service, all you need is adding::

  SAML2_DISCO_URL = 'https://your.ds.example.net/'

Of course, with the real URL of your preferred Discovery Service.


Idp hinting
===========
If the SP uses an AIM Proxy it is possible to suggest the authentication IDP by adopting the `idphint` parameter. The name of the `idphint` parameter is default, but it can also be changed using this parameter::

  SAML2_IDPHINT_PARAM = 'idphint'

This will ensure that the user will not get a possible discovery service page for the selection of the IdP to use for the SSO.
When Djagosaml2 receives an HTTP request at the resource, web path, configured for the saml2 login, it will detect the presence of the `idphint` parameter. If this is present, the authentication request will report this URL parameter within the http request relating to the SAML2 SSO binding.

For example::

  import requests
  import urllib
  idphint = {'idphint': [
               urllib.parse.quote_plus(b'https://that.idp.example.org/metadata'),
               urllib.parse.quote_plus(b'https://another.entitydi.org')]
            }
  param = urllib.parse.urlencode(idphint)
  # param is "idphint=%5B%27https%253A%252F%252Fthat.idp.example.org%252Fmetadata%27%2C+%27https%253A%252F%252Fanother.entitydi.org%27%5D"
  requests.get(f'http://djangosaml2.sp.fqdn.org/saml2/login/?{param}')

see AARC Blueprint specs `here <https://zenodo.org/record/4596667/files/AARC-G061-A_specification_for_IdP_hinting.pdf>`_.


IdP scoping
===========
The SP can suggest an IdP to a proxy by using the Scoping and IDPList elements in a SAML AuthnRequest. This is done using the `scoping` parameter to the login URL. ::

  https://sp.example.org/saml2/login/?scoping=https://idp.example.org

This parameter can be combined with the IdP parameter if multiple IdPs are present in the metadata, otherwise the first is used. ::

  https://sp.example.org/saml2/login/?scoping=https://idp.example.org&idp=https://proxy.example.com/metadata

Currently there is support for a single IDPEntry in the IDPList.


Authn Context
=============

We can define the authentication context in settings.SAML_CONFIG['service']['sp'] as follows::

    "requested_authn_context": {
        "authn_context_class_ref": [
            "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
            "urn:oasis:names:tc:SAML:2.0:ac:classes:TLSClient",
        ],
        "comparison": "minimum",
    }


Custom and dynamic configuration loading
========================================

By default, djangosaml2 reads the pysaml2 configuration options from the
SAML_CONFIG setting but sometimes you want to read this information from
another place, like a file or a database. Sometimes you even want this
configuration to be different depending on the request.

Starting from djangosaml2 0.5.0 you can define your own configuration
loader which is a callable that accepts a request parameter and returns
a saml2.config.SPConfig object. In order to do so you set the following
setting::

  SAML_CONFIG_LOADER = 'python.path.to.your.callable'

Bearer Assertion Replay Attack Prevention
=========================================
In SAML standard doc, section 4.1.4.5 it states

The service provider MUST ensure that bearer assertions are not replayed, by maintaining the set of used ID values for the length of time for which the assertion would be considered valid based on the NotOnOrAfter attribute in the <SubjectConfirmationData>

djangosaml2 provides a hook 'is_authorized' for the SP to store assertion IDs and implement replay prevention with your choice of storage.
::

    def is_authorized(self, attributes: dict, attribute_mapping: dict, idp_entityid: str, assertion: object, **kwargs) -> bool:
        if not assertion:
            return True

        # Get your choice of storage
        cache_storage = storage.get_cache()
        assertion_id = assertion.get('assertion_id')

        if cache.get(assertion_id):
            logger.warn("Received SAMLResponse assertion has been already used.")
            return False

        expiration_time = assertion.get('not_on_or_after')
        time_delta = isoparse(expiration_time) - datetime.now(timezone.utc)
        cache_storage.set(assertion_id, 'True', ex=time_delta)
        return True

CSP Configuration
=================
By default djangosaml2 will use `django-csp <https://django-csp.readthedocs.io>`_ 
to configure CSP if available otherwise a warning will be logged.

The warning can be disabled by setting::

  SAML_CSP_HANDLER = ''

A custom handler can similary be specified::

  # Django settings
  SAML_CSP_HANDLER = 'myapp.utils.csp_handler'

  # myapp/utils.py
  def csp_handler(response):
      response.headers['Content-Security-Policy'] = ...
      return response

A value of `None` is the default and will use `django-csp <https://django-csp.readthedocs.io>`_ if available.


Users, attributes and account linking
-------------------------------------

In the SAML 2.0 authentication process the Identity Provider (IdP) will
send a security assertion to the Service Provider (SP) upon a successful
authentication. This assertion contains attributes about the user that
was authenticated. It depends on the IdP configuration what exact
attributes are sent to each SP it can talk to.

When such assertion is received on the Django side it is used to find a Django
user and create a session for it. By default djangosaml2 will do a query on the
User model with the USERNAME_FIELD_ attribute but you can change it to any
other attribute of the User model. For example, you can do this lookup using
the 'email' attribute. In order to do so you should set the following setting::

  SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'

.. _USERNAME_FIELD: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD

Please, use an unique attribute when setting this option. Otherwise
the authentication process may fail because djangosaml2 will not know
which Django user it should pick.

If your main attribute is something inherently case-insensitive (such as
an email address), you may set::

  SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'

(This is simply appended to the main attribute name to form a Django
query. Your main attribute must be unique even given this lookup.)

Another option is to use the SAML2 name id as the username by setting::

  SAML_USE_NAME_ID_AS_USERNAME = True

You can configure djangosaml2 to create such user if it is not already in
the Django database or maybe you don't want to allow users that are not
in your database already. For this purpose there is another option you
can set in the settings.py file::

  SAML_CREATE_UNKNOWN_USER = True

This setting is True by default.

The following setting lets you specify a URL for redirection after a successful
authentication::

  ACS_DEFAULT_REDIRECT_URL = reverse_lazy('some_url_name')

Particularly useful when you only plan to use
IdP initiated login and the IdP does not have a configured RelayState
parameter. If not set Django's ``LOGIN_REDIRECT_URL`` or ``/`` will be used.

The other thing you will probably want to configure is the mapping of
SAML2 user attributes to Django user attributes. By default only the
User.username attribute is mapped but you can add more attributes or
change that one. In order to do so you need to change the
SAML_ATTRIBUTE_MAPPING option in your settings.py::

  SAML_ATTRIBUTE_MAPPING = {
      'uid': ('username', ),
      'mail': ('email', ),
      'cn': ('first_name', ),
      'sn': ('last_name', ),
  }

where the keys of this dictionary are SAML user attributes and the values
are Django User attributes.

If you are using Django user profile objects to store extra attributes
about your user you can add those attributes to the SAML_ATTRIBUTE_MAPPING
dictionary. For each (key, value) pair, djangosaml2 will try to store the
attribute in the User model if there is a matching field in that model.
Otherwise it will try to do the same with your profile custom model. For
multi-valued attributes only the first value is assigned to the destination field.

Alternatively, custom processing of attributes can be achieved by setting the
value(s) in the SAML_ATTRIBUTE_MAPPING, to name(s) of method(s) defined on a
custom django User object. In this case, each method is called by djangosaml2,
passing the full list of attribute values extracted from the <saml:AttributeValue>
elements of the <saml:Attribute>. Among other uses, this is a useful way to process
multi-valued attributes such as lists of user group names.

For example:

Saml assertion snippet::

  <saml:Attribute Name="groups" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <saml:AttributeValue>group1</saml:AttributeValue>
        <saml:AttributeValue>group2</saml:AttributeValue>
        <saml:AttributeValue>group3</saml:AttributeValue>
  </saml:Attribute>

Custom User object::

  from django.contrib.auth.models import AbstractUser

  class User(AbstractUser):

    def process_groups(self, groups):
      # process list of group names in argument 'groups'
      pass;

settings.py::

  SAML_ATTRIBUTE_MAPPING = {
      'groups': ('process_groups', ),
  }


Learn more about Django profile models at:

https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model


Custom user attributes processing
---------------------------------

Sometimes you need to use special logic to update the user object
depending on the SAML2 attributes and the mapping described above
is simply not enough. For these cases djangosaml2 provides hooks_
that can be overriden with custom functionality.

First of all reference the modified Saml2Backend in settings.py file::


    AUTHENTICATION_BACKENDS = [
        'your_package.authentication.ModifiedSaml2Backend',
    ]


For example::

    from djangosaml2.backends import Saml2Backend


    class ModifiedSaml2Backend(Saml2Backend):
        def save_user(self, user, *args, **kwargs):
            user.save()
            user_group = Group.objects.get(name='Default')
            user.groups.add(user_group)
            return super().save_user(user, *args, **kwargs)

Keep in mind save_user is only called when there was a reason to save the User model (ie. first login), and it has no access to SAML attributes for authorization. If this is required, it can be achieved by overriding the _update_user::

    from djangosaml2.backends import Saml2Backend

    class ModifiedSaml2Backend(Saml2Backend):
        def _update_user(self, user, attributes: dict, attribute_mapping: dict, force_save: bool = False):
            if 'eduPersonEntitlement' in attributes:
                if 'some-entitlement' in attributes['eduPersonEntitlement']:
                    user.is_staff = True
                    force_save = True
                else:
                    user.is_staff = False
                    force_save = True
            return super()._update_user(user, attributes, attribute_mapping, force_save)

.. _hooks: https://github.com/identitypython/djangosaml2/blob/master/djangosaml2/backends.py#L181



URLs
----

Changes in the urls.py file.
 The next thing you need to do is to include ``djangosaml2.urls`` module in your main ``urls.py`` module::

  urlpatterns = patterns(
      '',
      #  lots of url definitions here

      (r'saml2/', include('djangosaml2.urls')),

      #  more url definitions
  )

PySAML2 specific files and configuration
----------------------------------------
Once you have finished configuring your Django project you have to
start configuring PySAML2, please consult its `official documentation <https://pysaml2.readthedocs.io/en/latest/>`_ before start.
If you use just that library you have to put your configuration options in a file and initialize PySAML2 with
the path to that file. In djangosaml2 you just put the same information in the Django
settings.py file under the SAML_CONFIG option. We will see a typical configuration for protecting a Django project::

  from os import path
  import saml2
  import saml2.saml
  BASEDIR = path.dirname(path.abspath(__file__))

  SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': 'http://localhost:8000/saml2/metadata/',

    # directory with attribute mapping
    'attribute_map_dir': path.join(BASEDIR, 'attribute-maps'),

    # Permits to have attributes not configured in attribute-mappings
    # otherwise...without OID will be rejected
    'allow_unknown_attributes': True,

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp' : {
            'name': 'Federated Django sample SP',
            'name_id_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,

            # For Okta add signed logout requests. Enable this:
            # "logout_requests_signed": True,

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
                    # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                    ('http://localhost:8000/saml2/ls/',
                     saml2.BINDING_HTTP_REDIRECT),
                    ('http://localhost:8000/saml2/ls/post',
                     saml2.BINDING_HTTP_POST),
                    ],
                },

            'signing_algorithm':  saml2.xmldsig.SIG_RSA_SHA256,
            'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,

             # Mandates that the identity provider MUST authenticate the
             # presenter directly rather than rely on a previous security context.
            'force_authn': False,

             # Enable AllowCreate in NameIDPolicy.
            'name_id_format_allow_create': False,

             # attributes that this project need to identify a user
            'required_attributes': ['givenName',
                                    'sn',
                                    'mail'],

             # attributes that may be useful to have but not required
            'optional_attributes': ['eduPersonAffiliation'],

            'want_response_signed': True,
            'authn_requests_signed': True,
            'logout_requests_signed': True,
            # Indicates that Authentication Responses to this SP must
            # be signed. If set to True, the SP will not consume
            # any SAML Responses that are not signed.
            'want_assertions_signed': True,

            'only_use_keys_in_metadata': True,

            # When set to true, the SP will consume unsolicited SAML
            # Responses, i.e. SAML Responses for which it has not sent
            # a respective SAML Authentication Request.
            'allow_unsolicited': False,

            # in this section the list of IdPs we talk to are defined
            # This is not mandatory! All the IdP available in the metadata will be considered instead.
            'idp': {
                # we do not need a WAYF service since there is
                # only an IdP defined here. This IdP should be
                # present in our metadata

                # the keys of this dictionary are entity ids
                'https://localhost/simplesaml/saml2/idp/metadata.php': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SSOService.php',
                        },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SingleLogoutService.php',
                        },
                    },
                },
            },
        },

    # where the remote metadata is stored, local, remote or mdq server.
    # One metadatastore or many ...
    'metadata': {
        'local': [path.join(BASEDIR, 'remote_metadata.xml')],
        'remote': [{"url": "https://idp.testunical.it/idp/shibboleth"},],
        'mdq': [{"url": "https://ds.testunical.it",
                 "cert": "certficates/others/ds.testunical.it.cert",
                }]
        },

    # set to 1 to output debugging information
    'debug': 1,

    # Signing
    'key_file': path.join(BASEDIR, 'private.key'),  # private part
    'cert_file': path.join(BASEDIR, 'public.pem'),  # public part

    # Encryption
    'encryption_keypairs': [{
        'key_file': path.join(BASEDIR, 'private.key'),  # private part
        'cert_file': path.join(BASEDIR, 'public.pem'),  # public part
    }],

    # own metadata settings
    'contact_person': [
        {'given_name': 'Lorenzo',
         'sur_name': 'Gil',
         'company': 'Yaco Sistemas',
         'email_address': 'lorenzo.gil.sanchez@gmail.com',
         'contact_type': 'technical'},
        {'given_name': 'Angel',
         'sur_name': 'Fernandez',
         'company': 'Yaco Sistemas',
         'email_address': 'angel@yaco.es',
         'contact_type': 'administrative'},
        ],
    # you can set multilanguage information here
    'organization': {
        'name': [('Yaco Sistemas', 'es'), ('Yaco Systems', 'en')],
        'display_name': [('Yaco', 'es'), ('Yaco', 'en')],
        'url': [('http://www.yaco.es', 'es'), ('http://www.yaco.com', 'en')],
        },
    }

.. note::

  Please check the `PySAML2 documentation`_ for more information about
  these and other configuration options.

.. _`PySAML2 documentation`: http://pysaml2.readthedocs.io/en/latest/


There are several external files and directories you have to create according
to this configuration.

The xmlsec1 binary was mentioned in the installation section. Here, in the
configuration part you just need to put the full path to xmlsec1 so PySAML2
can call it as it needs.

Signed Logout Request
=====================

Idp's like Okta require a signed logout response to validate and logout a user. Here's a sample config with all required SP/IDP settings::

   "logout_requests_signed": True,

Attribute Map
=============

The ``attribute_map_dir`` points to a directory with attribute mappings that
are used to translate user attribute names from several standards. It's usually
safe to just copy the default PySAML2 attribute maps that you can find in the
``tests/attributemaps`` directory of the source distribution.

Metadata
========

The ``metadata`` option is a dictionary where you can define several types of
metadata for remote entities. Usually the easiest type is the ``local`` where
you just put the name of a local XML file with the contents of the remote
entities metadata. This XML file should be in the SAML2 metadata format.

.. Note::

  Don't use ``remote`` option for fetching metadata in production.
  Try to use ``mdq`` and introduce a MDQ server instead, it's more efficient.


Certificates
============

The ``key_file`` and ``cert_file`` options reference the two parts of a
standard x509 certificate. You need it to sign your metadata. For assertion
encryption/decryption support please configure another set of ``key_file`` and
``cert_file``, but as inner attributes of ``encryption_keypairs`` option.

.. Note::

  Check your openssl documentation to generate a certificate suitable for SAML2 operations.

SAML2 certificate creation example::

  openssl req -nodes -new -x509 -newkey rsa:2048 -days 3650 -keyout private.key -out public.cert


PySAML2 certificates are files, in the form of strings that contains a filesystem path.
What about configuring the certificates in a different way, in case we are using a container based deploy?

- You could supply the cert & key as environment variables (base64 encoded) then create the files when the container starts, either in an entry point shell script or in your settings.py file.

- Using `Python Tempfile <https://docs.python.org/3/library/tempfile.html>`_ In the settings create two temp files, then write the content configured in environment variables in them, then use tmpfile.name as key/cert values in pysaml2 configuration.
