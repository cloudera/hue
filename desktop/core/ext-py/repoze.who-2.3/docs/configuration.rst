.. _configuration_points:

Configuring :mod:`repoze.who`
=============================

Configuration Points
--------------------

Classifiers
+++++++++++

:mod:`repoze.who` "classifies" the request on middleware ingress.
Request classification happens before identification and
authentication.  A request from a browser might be classified a
different way than a request from an XML-RPC client.
:mod:`repoze.who` uses request classifiers to decide which other
components to consult during subsequent identification,
authentication, and challenge steps.  Plugins are free to advertise
themselves as willing to participate in identification and
authorization for a request based on this classification.  The request
classification system is pluggable.  :mod:`repoze.who` provides a
default classifier that you may use.

You may extend the classification system by making :mod:`repoze.who` aware
of a different request classifier implementation.

Challenge Deciders
++++++++++++++++++

:mod:`repoze.who` uses a "challenge decider" to decide whether the
response returned from a downstream application requires a challenge
plugin to fire.  When using the default challenge decider, only the
status is used (if it starts with ``401``, a challenge is required).

:mod:`repoze.who` also provides an alternate challenge decider,
``repoze.who.classifiers.passthrough_challenge_decider``, which avoids
challenging ``401`` responses which have been "pre-challenged" by the
application.

You may supply a different challenge decider as necessary.

Plugins
+++++++

:mod:`repoze.who` has core functionality designed around the concept
of plugins.  Plugins are instances that are willing to perform one or
more identification- and/or authentication-related duties.  Each
plugin can be configured arbitrarily.

:mod:`repoze.who` consults the set of configured plugins when it
intercepts a WSGI request, and gives some subset of them a chance to
influence what :mod:`repoze.who` does for the current request.

.. note:: As of :mod:`repoze.who` 1.0.7, the ``repoze.who.plugins``
   package is a namespace package, intended to make it possible for
   people to ship eggs which are who plugins as,
   e.g. ``repoze.who.plugins.mycoolplugin``.


.. _imperative_configuration:

Configuring :mod:`repoze.who` via Python Code
---------------------------------------------

.. module:: repoze.who.middleware

.. class:: PluggableAuthenticationMiddleware(app, identifiers, challengers, authenticators, mdproviders, classifier, challenge_decider [, log_stream=None [, log_level=logging.INFO[, remote_user_key='REMOTE_USER']]])

  The primary method of configuring the :mod:`repoze.who` middleware is
  to use straight Python code, meant to be consumed by frameworks
  which construct and compose middleware pipelines without using a
  configuration file.

  In the middleware constructor: *app* is the "next" application in
  the WSGI pipeline. *identifiers* is a sequence of ``IIdentifier``
  plugins, *challengers* is a sequence of ``IChallenger`` plugins,
  *mdproviders* is a sequence of ``IMetadataProvider`` plugins.  Any
  of these can be specified as the empty sequence.  *classifier* is a
  request classifier callable, *challenge_decider* is a challenge
  decision callable.  *log_stream* is a stream object (an object with
  a ``write`` method) *or* a ``logging.Logger`` object, *log_level* is
  a numeric value that maps to the ``logging`` module's notion of log
  levels, *remote_user_key* is the key in which the ``REMOTE_USER``
  (userid) value should be placed in the WSGI environment for
  consumption by downstream applications.

An example configuration which uses the default plugins follows::

    from repoze.who.middleware import PluggableAuthenticationMiddleware
    from repoze.who.interfaces import IIdentifier
    from repoze.who.interfaces import IChallenger
    from repoze.who.plugins.basicauth import BasicAuthPlugin
    from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
    from repoze.who.plugins.redirector import RedirectorPlugin
    from repoze.who.plugins.htpasswd import HTPasswdPlugin

    io = StringIO()
    salt = 'aa'
    for name, password in [ ('admin', 'admin'), ('chris', 'chris') ]:
        io.write('%s:%s\n' % (name, password))
    io.seek(0)
    def cleartext_check(password, hashed):
        return password == hashed
    htpasswd = HTPasswdPlugin(io, cleartext_check)
    basicauth = BasicAuthPlugin('repoze.who')
    auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt', digest_algo="sha512")
    redirector = RedirectorPlugin('/login.html')
    redirector.classifications = {IChallenger:['browser'],} # only for browser
    identifiers = [('auth_tkt', auth_tkt),
                   ('basicauth', basicauth)]
    authenticators = [('auth_tkt', auth_tkt),
                      ('htpasswd', htpasswd)]
    challengers = [('redirector', redirector),
                   ('basicauth', basicauth)]
    mdproviders = []

    from repoze.who.classifiers import default_request_classifier
    from repoze.who.classifiers import default_challenge_decider
    log_stream = None
    import os
    if os.environ.get('WHO_LOG'):
        log_stream = sys.stdout

    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream = log_stream,
        log_level = logging.DEBUG
        )

The above example configures the repoze.who middleware with:

- Two ``IIdentifier`` plugins (auth_tkt cookie, and a
  basic auth plugin).  In this setup, when "identification" needs to
  be performed, the auth_tkt plugin will be checked first, then
  the basic auth plugin.  The application is responsible for handling
  login via a form:  this view would use the API (via :method:`remember`)
  to generate apprpriate response headers.

- Two ``IAuthenticator`` plugins: the auth_tkt plugin and an htpasswd plugin.
  The auth_tkt plugin performs both ``IIdentifier`` and ``IAuthenticator``
  functions.  The htpasswd plugin is configured with two valid username /
  password combinations: chris/chris, and admin/admin.  When an username
  and password is found via any identifier, it will be checked against this
  authenticator.

- Two ``IChallenger`` plugins: the redirector plugin, then the basic auth
  plugin.  The redirector auth will fire if the request is a ``browser``
  request, otherwise the basic auth plugin will fire.

The rest of the middleware configuration is for values like logging
and the classifier and decider implementations.  These use the "stock"
implementations.

.. note:: The ``app`` referred to in the example is the "downstream"
   WSGI application that who is wrapping.


.. _declarative_configuration:

Configuring :mod:`repoze.who` via Config File
---------------------------------------------

:mod:`repoze.who` may be configured using a ConfigParser-style .INI
file.  The configuration file has five main types of sections: plugin
sections, a general section, an identifiers section, an authenticators
section, and a challengers section.  Each "plugin" section defines a
configuration for a particular plugin.  The identifiers,
authenticators, and challengers sections refer to these plugins to
form a site configuration.  The general section is general middleware
configuration.

To configure :mod:`repoze.who` in Python, using an .INI file, call
the `make_middleware_with_config` entry point, passing the right-hand
application, the global configuration dictionary, and the path to the
config file. The global configuration dictionary is a dictonary passed 
by PasteDeploy. The only key 'make_middleware_with_config' needs is 
'here' pointing to the config file directory. For debugging people
might find it useful to enable logging by adding the log_file argument,
e.g. log_file="repoze_who.log" ::

    from repoze.who.config import make_middleware_with_config
    global_conf = {"here": "."}  # if this is not defined elsewhere
    who = make_middleware_with_config(app, global_conf, 'who.ini')

:mod:`repoze.who`'s configuration file can be pointed to within a PasteDeploy
configuration file ::

    [filter:who]
    use = egg:repoze.who#config
    config_file = %(here)s/who.ini
    log_file = stdout
    log_level = debug

Below is an example of a configuration file (what ``config_file``
might point at above ) that might be used to configure the
:mod:`repoze.who` middleware.  A set of plugins are defined, and they
are referred to by following non-plugin sections.

In the below configuration, five plugins are defined.  The form, and
basicauth plugins are nominated to act as challenger plugins.  The
form, cookie, and basicauth plugins are nominated to act as
identification plugins.  The htpasswd and sqlusers plugins are
nominated to act as authenticator plugins. ::

    [plugin:redirector]
    # identificaion and challenge
    use = repoze.who.plugins.redirector:make_plugin
    login_url = /login.html

    [plugin:auth_tkt]
    # identification and authentication
    use = repoze.who.plugins.auth_tkt:make_plugin
    secret = s33kr1t
    cookie_name = oatmeal
    secure = False
    include_ip = False
    digest_algo = sha512

    [plugin:basicauth]
    # identification and challenge
    use = repoze.who.plugins.basicauth:make_plugin
    realm = 'sample'

    [plugin:htpasswd]
    # authentication
    use = repoze.who.plugins.htpasswd:make_plugin
    filename = %(here)s/passwd
    check_fn = repoze.who.plugins.htpasswd:crypt_check

    [plugin:sqlusers]
    # authentication
    use = repoze.who.plugins.sql:make_authenticator_plugin
    # Note the double %%:  we have to escape it from the config parser in
    # order to preserve it as a template for the psycopg2, whose 'paramstyle'
    # is 'pyformat'.
    query = SELECT userid, password FROM users where login = %%(login)s
    conn_factory = repoze.who.plugins.sql:make_psycopg_conn_factory
    compare_fn = repoze.who.plugins.sql:default_password_compare

    [plugin:sqlproperties]
    name = properties
    use = repoze.who.plugins.sql:make_metadata_plugin
    # Note the double %%:  we have to escape it from the config parser in
    # order to preserve it as a template for the psycopg2, whose 'paramstyle'
    # is 'pyformat'.
    query = SELECT firstname, lastname FROM users where userid = %%(__userid)s
    filter = my.package:filter_propmd
    conn_factory = repoze.who.plugins.sql:make_psycopg_conn_factory

    [general]
    request_classifier = repoze.who.classifiers:default_request_classifier
    challenge_decider = repoze.who.classifiers:default_challenge_decider
    remote_user_key = REMOTE_USER

    [identifiers]
    # plugin_name;classifier_name:.. or just plugin_name (good for any)
    plugins =
          auth_tkt
          basicauth

    [authenticators]
    # plugin_name;classifier_name.. or just plugin_name (good for any)
    plugins =
          auth_tkt
          htpasswd
          sqlusers

    [challengers]
    # plugin_name;classifier_name:.. or just plugin_name (good for any)
    plugins =
          redirector;browser
          basicauth

    [mdproviders]
    plugins =
          sqlproperties

The basicauth section configures a plugin that does identification and
challenge for basic auth credentials.  The redirector section configures a
plugin that does challenges.  The auth_tkt section configures a plugin that
does identification for cookie auth credentials, as well as authenticating
them.  The htpasswd plugin obtains its user info from a file.  The sqlusers
plugin obtains its user info from a Postgres database.

The identifiers section provides an ordered list of plugins that are
willing to provide identification capability.  These will be consulted
in the defined order.  The tokens on each line of the ``plugins=`` key
are in the form "plugin_name;requestclassifier_name:..."  (or just
"plugin_name" if the plugin can be consulted regardless of the
classification of the request).  The configuration above indicates
that the system will look for credentials using the auth_tkt cookie
identifier (unconditionally), then the basic auth plugin
(unconditionally).

The authenticators section provides an ordered list of plugins that
provide authenticator capability.  These will be consulted in the
defined order, so the system will look for users in the file, then in
the sql database when attempting to validate credentials.  No
classification prefixes are given to restrict which of the two plugins
are used, so both plugins are consulted regardless of the
classification of the request.  Each authenticator is called with each
set of identities found by the identifier plugins.  The first identity
that can be authenticated is used to set ``REMOTE_USER``.

The mdproviders section provides an ordered list of plugins that
provide metadata provider capability.  These will be consulted in the
defined order.  Each will have a chance (on ingress) to provide add
metadata to the authenticated identity.  Our example mdproviders
section shows one plugin configured: "sqlproperties".  The
sqlproperties plugin will add information related to user properties
(e.g. first name and last name) to the identity dictionary.

The challengers section provides an ordered list of plugins that
provide challenger capability.  These will be consulted in the defined
order, so the system will consult the cookie auth plugin first, then
the basic auth plugin.  Each will have a chance to initiate a
challenge.  The above configuration indicates that the redirector challenger
will fire if it's a browser request, and the basic auth challenger
will fire if it's not (fallback).
