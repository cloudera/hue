.. _about_plugins:

About :mod:`repoze.who` Plugins
===============================

Plugin Types
------------

Identifier Plugins
++++++++++++++++++

You can register a plugin as willing to act as an "identifier".  An
identifier examines the WSGI environment and attempts to extract
credentials from the environment.  These credentials are used by
authenticator plugins to perform authentication.


Authenticator Plugins
+++++++++++++++++++++

You may register a plugin as willing to act as an "authenticator".
Authenticator plugins are responsible for resolving a set of
credentials provided by an identifier plugin into a user id.
Typically, authenticator plugins will perform a lookup into a database
or some other persistent store, check the provided credentials against
the stored data, and return a user id if the credentials can be
validated.

The user id provided by an authenticator is eventually passed to
downstream WSGI applications in the "REMOTE_USER' environment
variable.  Additionally, the "identity" of the user (as provided by
the identifier from whence the identity came) is passed along to
downstream application in the ``repoze.who.identity`` environment
variable.


Metadata Provider Plugins
+++++++++++++++++++++++++

You may register a plugin as willing to act as a "metadata provider"
(aka mdprovider).  Metadata provider plugins are responsible for
adding arbitrary information to the identity dictionary for
consumption by downstream applications.  For instance, a metadata
provider plugin may add "group" information to the the identity.


Challenger Plugins
++++++++++++++++++

You may register a plugin as willing to act as a "challenger".
Challenger plugins are responsible for initiating a challenge to the
requesting user.  Challenger plugins are invoked by :mod:`repoze.who` when it
decides a challenge is necessary. A challenge might consist of
displaying a form or presenting the user with a basic or digest
authentication dialog.


.. _default_plugins:

Default Plugin Implementations
------------------------------

:mod:`repoze.who` ships with a variety of default plugins that do
authentication, identification, challenge and metadata provision.

.. module:: repoze.who.plugins.auth_tkt

.. class:: AuthTktCookiePlugin(secret [, cookie_name='auth_tkt' [, secure=False [, include_ip=False]]])

  An :class:`AuthTktCookiePlugin` is an ``IIdentifier`` and ``IAuthenticator``
  plugin which remembers its identity state in a client-side cookie.
  This plugin uses the ``paste.auth.auth_tkt``"auth ticket" protocol and
  is compatible with Apache's mod_auth_tkt.
  It should be instantiated passing a *secret*, which is used to encrypt the
  cookie on the client side and decrypt the cookie on the server side.
  The cookie name used to store the cookie value can be specified
  using the *cookie_name* parameter.  If *secure* is False, the cookie
  will be sent across any HTTP or HTTPS connection; if it is True, the
  cookie will be sent only across an HTTPS connection.  If
  *include_ip* is True, the ``REMOTE_ADDR`` of the WSGI environment
  will be placed in the cookie.

  Normally, using the plugin as an identifier requires also using it as
  an authenticator.

.. note::
   Using the *include_ip* setting for public-facing applications may
   cause problems for some users.  `One study
   <http://westpoint.ltd.uk/advisories/Paul_Johnston_GSEC.pdf>`_ reports
   that as many as 3% of users change their IP addresses legitimately
   during a session.
   
.. note::
   Plugin supports remembering user data in the cookie by saving user dict into ``identity['userdata']``
   parameter of ``remember`` method. They are sent unencrypted and protected by checksum.
   Data will then be returned every time by ``identify``. This dict must be compatible with
   ``urllib.urlencode`` function (``urllib.urlparse.urlencode`` in python 3).
   Saving keys/values with unicode characters is supported only under python 3.

.. note::
   Plugin supports multiple digest algorithms. It defaults to md5 to match
   the default for mod_auth_tkt and paste.auth.auth_tkt. However md5 is not
   recommended as there are viable attacks against the hash. Any algorithm
   from the hashlib library can be specified, currently only sha256 and sha512
   are supported by mod_auth_tkt.

.. module:: repoze.who.plugins.basicauth

.. class:: BasicAuthPlugin(realm)

  A :class:`BasicAuthPlugin` plugin is both an ``IIdentifier`` and
  ``IChallenger`` plugin that implements the Basic Access
  Authentication scheme described in :rfc:`2617`.  It looks for
  credentials within the ``HTTP-Authorization`` header sent by
  browsers.  It challenges by sending an ``WWW-Authenticate`` header
  to the browser.  The single argument *realm* indicates the basic
  auth realm that should be sent in the ``WWW-Authenticate`` header.

.. module:: repoze.who.plugins.htpasswd

.. class:: HTPasswdPlugin(filename, check)

  A :class:`HTPasswdPlugin` is an ``IAuthenticator`` implementation
  which compares identity information against an Apache-style htpasswd
  file.  The *filename* argument should be an absolute path to the
  htpasswd file' the *check* argument is a callable which takes two
  arguments: "password" and "hashed", where the "password" argument is
  the unencrypted password provided by the identifier plugin, and the
  hashed value is the value stored in the htpasswd file.  If the
  hashed value of the password matches the hash, this callable should
  return True.  A default implementation named ``crypt_check`` is
  available for use as a check function (on UNIX) as
  ``repoze.who.plugins.htpasswd:crypt_check``; it assumes the values
  in the htpasswd file are encrypted with the UNIX ``crypt`` function.

.. module:: repoze.who.plugins.redirector

.. class:: RedirectorPlugin(login_url, came_from_param, reason_param, reason_header)

  A :class:`RedirectorPlugin` is an ``IChallenger`` plugin.
  It redirects to a configured login URL at egress if a challenge is
  required .
  *login_url* is the URL that should be redirected to when a
  challenge is required.  *came_from_param* is the name of an optional
  query string parameter:  if configured, the plugin provides the current
  request URL in the redirected URL's query string, using the supplied
  parameter name.  *reason_param* is the name of an optional
  query string parameter:  if configured, and the application supplies
  a header matching *reason_header* (defaulting to
  ``X-Authorization-Failure-Reason``), the plugin includes that reason in
  the query string of the redirected URL, using the supplied parameter name.
  *reason_header* is an optional parameter overriding the default response
  header name (``X-Authorization-Failure-Reason``) which
  the plugin checks to find the application-supplied reason for the challenge.
  *reason_header* cannot be set unless *reason_param* is also set.

.. module:: repoze.who.plugins.sql

.. class:: SQLAuthenticatorPlugin(query, conn_factory, compare_fn)

  A :class:`SQLAuthenticatorPlugin` is an ``IAuthenticator``
  implementation which compares login-password identity information
  against data in an arbitrary SQL database.  The *query* argument
  should be a SQL query that returns two columns in a single row
  considered to be the user id and the password respectively.  The SQL
  query should contain Python-DBAPI style substitution values for
  ``%(login)``, e.g. ``SELECT user_id, password FROM users WHERE login
  = %(login)``.  The *conn_factory* argument should be a callable that
  returns a DBAPI database connection.  The *compare_fn* argument
  should be a callable that accepts two arguments: ``cleartext`` and
  ``stored_password_hash``.  It should compare the hashed version of
  cleartext and return True if it matches the stored password hash,
  otherwise it should return False.  A comparison function named
  ``default_password_compare`` exists in the
  ``repoze.who.plugins.sql`` module demonstrating this.  The
  :class:`SQLAuthenticatorPlugin`\'s ``authenticate`` method will
  return the user id of the user unchanged to :mod:`repoze.who`.

.. class:: SQLMetadataProviderPlugin(name, query, conn_factory, filter)

  A :class:`SQLMetatadaProviderPlugin` is an ``IMetadataProvider``
  implementation which adds arbitrary metadata to the identity on
  ingress using data from an arbitrary SQL database.  The *name*
  argument should be a string.  It will be used as a key in the
  identity dictionary.  The *query* argument should be a SQL query
  that returns arbitrary data from the database in a form that accepts
  Python-binding style DBAPI arguments.  It should expect that a
  ``__userid`` value will exist in the dictionary that is bound.  The
  SQL query should contain Python-DBAPI style substitution values for
  (at least) ``%(__userid)``, e.g. ``SELECT group FROM groups WHERE
  user_id = %(__userid)``.  The *conn_factory* argument should be a
  callable that returns a DBAPI database connection.  The *filter*
  argument should be a callable that accepts the result of the DBAPI
  ``fetchall`` based on the SQL query.  It should massage the data
  into something that will be set in the environment under the *name*
  key.  


Writing :mod:`repoze.who` Plugins
---------------------------------

:mod:`repoze.who` can be extended arbitrarily through the creation of
plugins.  Plugins are of one of four types: identifier plugins,
authenticator plugins, metadata provider plugins, and challenge
plugins.


Writing An Identifier Plugin
++++++++++++++++++++++++++++

An identifier plugin (aka an ``IIdentifier`` plugin) must do three
things: extract credentials from the request and turn them into an
"identity", "remember" credentials, and "forget" credentials.

Here's a simple cookie identification plugin that does these three
things ::

    class InsecureCookiePlugin(object):

        def __init__(self, cookie_name):
            self.cookie_name = cookie_name

        def identify(self, environ):
            from paste.request import get_cookies
            cookies = get_cookies(environ)
            cookie = cookies.get(self.cookie_name)

            if cookie is None:
                return None

            import binascii
            try:
                auth = cookie.value.decode('base64')
            except binascii.Error: # can't decode
                return None

            try:
                login, password = auth.split(':', 1)
                return {'login':login, 'password':password}
            except ValueError: # not enough values to unpack
                return None

        def remember(self, environ, identity):
            cookie_value = '%(login)s:%(password)s' % identity
            cookie_value = cookie_value.encode('base64').rstrip()
            from paste.request import get_cookies
            cookies = get_cookies(environ)
            existing = cookies.get(self.cookie_name)
            value = getattr(existing, 'value', None)
            if value != cookie_value:
                # return a Set-Cookie header
                set_cookie = '%s=%s; Path=/;' % (self.cookie_name, cookie_value)
                return [('Set-Cookie', set_cookie)]

        def forget(self, environ, identity):
            # return a expires Set-Cookie header
            expired = ('%s=""; Path=/; Expires=Sun, 10-May-1971 11:59:00 GMT' %
                       self.cookie_name)
            return [('Set-Cookie', expired)]
        
        def __repr__(self):
            return '<%s %s>' % (self.__class__.__name__, id(self))


.identify
~~~~~~~~~

The ``identify`` method of our InsecureCookiePlugin accepts a single
argument "environ".  This will be the WSGI environment dictionary.
Our plugin attempts to grub through the cookies sent by the client,
trying to find one that matches our cookie name.  If it finds one that
matches, it attempts to decode it and turn it into a login and a
password, which it returns as values in a dictionary.  This dictionary
is thereafter known as an "identity".  If it finds no credentials in
cookies, it returns None (which is not considered an identity).

More generally, the ``identify`` method of an ``IIdentifier`` plugin
is called once on WSGI request "ingress", and it is expected to grub
arbitrarily through the WSGI environment looking for credential
information.  In our above plugin, the credential information is
expected to be in a cookie but credential information could be in a
cookie, a form field, basic/digest auth information, a header, a WSGI
environment variable set by some upstream middleware or whatever else
someone might use to stash authentication information.  If the plugin
finds credentials in the request, it's expected to return an
"identity": this must be a dictionary.  The dictionary is not required
to have any particular keys or value composition, although it's wise
if the identification plugin looks for both a login name and a
password information to return at least {'login':login_name,
'password':password}, as some authenticator plugins may depend on
presence of the names "login" and "password" (e.g. the htpasswd and
sql ``IAuthenticator`` plugins).  If an ``IIdentifier`` plugin finds
no credentials, it is expected to return None.


.remember
~~~~~~~~~

If we've passed a REMOTE_USER to the WSGI application during ingress
(as a result of providing an identity that could be authenticated),
and the downstream application doesn't kick back with an unauthorized
response, on egress we want the requesting client to "remember" the
identity we provided if there's some way to do that and if he hasn't
already, in order to ensure he will pass it back to us on subsequent
requests without requiring another login.  The remember method of an
``IIdentifier`` plugin is called for each non-unauthenticated
response.  It is the responsibility of the ``IIdentifier`` plugin to
conditionally return HTTP headers that will cause the client to
remember the credentials implied by "identity".
    
Our InsecureCookiePlugin implements the "remember" method by returning
headers which set a cookie if and only if one is not already set with
the same name and value in the WSGI environment.  These headers will
be tacked on to the response headers provided by the downstream
application during the response.

When you write a remember method, most of the work involved is
determining *whether or not* you need to return headers.  It's typical
to see remember methods that compute an "old state" and a "new state"
and compare the two against each other in order to determine if
headers need to be returned.  In our example InsecureCookiePlugin, the
"old state" is ``cookie_value`` and the "new state" is ``value``.


.forget
~~~~~~~

Eventually the WSGI application we're serving will issue a "401
 Unauthorized" or another status signifying that the request could not
 be authorized.  :mod:`repoze.who` intercepts this status and calls
 ``IIdentifier`` plugins asking them to "forget" the credentials
 implied by the identity.  It is the "forget" method's job at this
 point to return HTTP headers that will effectively clear any
 credentials on the requesting client implied by the "identity"
 argument.

 Our InsecureCookiePlugin implements the "forget" method by returning
 a header which resets the cookie that was set earlier by the remember
 method to one that expires in the past (on my birthday, in fact).
 This header will be tacked onto the response headers provided by the
 downstream application.


Writing an Authenticator Plugin
+++++++++++++++++++++++++++++++

An authenticator plugin (aka an ``IAuthenticator`` plugin) must do
only one thing (on "ingress"): accept an identity and check if the
identity is "good".  If the identity is good, it should return a "user
id".  This user id may or may not be the same as the "login" provided
by the user.  An ``IAuthenticator`` plugin will be called for each
identity found during the identification phase (there may be multiple
identities for a single request, as there may be multiple
``IIdentifier`` plugins active at any given time), so it may be called
multiple times in the same request.

Here's a simple authenticator plugin that attempts to match an
identity against ones defined in an "htpasswd" file that does just
that::

    class SimpleHTPasswdPlugin(object):

        def __init__(self, filename):
            self.filename = filename

        # IAuthenticatorPlugin
        def authenticate(self, environ, identity):
            try:
                login = identity['login']
                password = identity['password']
            except KeyError:
                return None

            f = open(self.filename, 'r')

            for line in f:
                try:
                    username, hashed = line.rstrip().split(':', 1)
                except ValueError:
                    continue
                if username == login:
                    if crypt_check(password, hashed):
                        return username
            return None

    def crypt_check(password, hashed):
        from crypt import crypt
        salt = hashed[:2]
        return hashed == crypt(password, salt)

An ``IAuthenticator`` plugin implements one "interface" method:
"authentictate".  The formal specification for the arguments and
return values expected from these methods are available in the
``interfaces.py`` file in :mod:`repoze.who` as the ``IAuthenticator``
interface, but let's examine this method here less formally.


.authenticate
~~~~~~~~~~~~~

The ``authenticate`` method accepts two arguments: the WSGI
environment and an identity.  Our SimpleHTPasswdPlugin
``authenticate`` implementation grabs the login and password out of
the identity and attempts to find the login in the htpasswd file.  If
it finds it, it compares the crypted version of the password provided
by the user to the crypted version stored in the htpasswd file, and
finally, if they match, it returns the login.  If they do not match,
it returns None.

.. note::

   Our plugin's ``authenticate`` method does not assume that the keys
   ``login`` or ``password`` exist in the identity; although it
   requires them to do "real work" it returns None if they are not
   present instead of raising an exception.  This is required by the
   ``IAuthenticator`` interface specification.


Writing a Challenger Plugin
+++++++++++++++++++++++++++

A challenger plugin (aka an ``IChallenger`` plugin) must do only one
thing on "egress": return a WSGI application which performs a
"challenge".  A WSGI application is a callable that accepts an
"environ" and a "start_response" as its parameters; see "PEP 333" for
further definition of what a WSGI application is.  A challenge asks
the user for credentials.

Here's an example of a simple challenger plugin::

    from paste.httpheaders import WWW_AUTHENTICATE
    from paste.httpexceptions import HTTPUnauthorized

    class BasicAuthChallengerPlugin(object):

        def __init__(self, realm):
            self.realm = realm

        # IChallenger
        def challenge(self, environ, status, app_headers, forget_headers):
            head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
            if head[0] not in forget_headers:
                head = head + forget_headers
            return HTTPUnauthorized(headers=head)

Note that the plugin implements a single "interface" method:
"challenge".  The formal specification for the arguments and return
values expected from this method is available in the "interfaces.py"
file in :mod:`repoze.who` as the ``IChallenger`` interface.  This method
is called when :mod:`repoze.who` determines that the application has
returned an "unauthorized" response (e.g. a 401).  Only one challenger
will be consulted during "egress" as necessary (the first one to
return a non-None response).


.challenge
~~~~~~~~~~

The challenge method takes environ (the WSGI environment), 'status'
(the status as set by the downstream application), the "app_headers"
(headers returned by the application), and the "forget_headers"
(headers returned by all participating ``IIdentifier`` plugins whom
were asked to "forget" this user).

Our BasicAuthChallengerPlugin takes advantage of the fact that the
HTTPUnauthorized exception imported from paste.httpexceptions can be
used as a WSGI application.  It first makes sure that we don't repeat
headers if an identification plugin has already set a
"WWW-Authenticate" header like ours, then it returns an instance of
HTTPUnauthorized, passing in merged headers.  This will cause a basic
authentication dialog to be presented to the user.


Writing a Metadata Provider Plugin
++++++++++++++++++++++++++++++++++

A metadata provider plugin (aka an ``IMetadataProvider`` plugin) must
do only one thing (on "ingress"): "scribble" on the identity
dictionary provided to it when it is called.  An ``IMetadataProvider``
plugin will be called with the final "best" identity found during the
authentication phase, or not at all if no "best" identity could be
authenticated.  Thus, each ``IMetadataProvider`` plugin will be called
exactly zero or one times during a request.

Here's a simple metadata provider plugin that provides "property"
information from a dictionary::

    _DATA = {    
        'chris': {'first_name':'Chris', 'last_name':'McDonough'} ,
        'whit': {'first_name':'Whit', 'last_name':'Morriss'} 
        }

    class SimpleMetadataProvider(object):

        def add_metadata(self, environ, identity):
            userid = identity.get('repoze.who.userid')
            info = _DATA.get(userid)
            if info is not None:
                identity.update(info)


.add_metadata
~~~~~~~~~~~~~

Arbitrarily add information to the identity dict based in other data
in the environment or identity.  Our plugin adds ``first_name`` and
``last_name`` values to the identity if the userid matches ``chris``
or ``whit``.


Known Plugins for :mod:`repoze.who`
===================================


Plugins shipped with :mod:`repoze.who`
--------------------------------------

See :ref:`default_plugins`.


Deprecated plugins
------------------

The :mod:`repoze.who.deprecatedplugins` distribution bundles the following
plugin implementations which were shipped with :mod:`repoze.who` prior
to version 2.0a3.  These plugins are deprecated, and should only be used
while migrating an existing deployment to replacement versions.

:class:`repoze.who.plugins.cookie.InsecureCookiePlugin`
  An ``IIdentifier`` plugin which stores identification information in an
  insecure form (the base64 value of the username and password separated by
  a colon) in a client-side cookie.  Please use the
  :class:`AuthTktCookiePlugin` instead.

:class:`repoze.who.plugins.form.FormPlugin`

  An ``IIdentifier`` and ``IChallenger`` plugin,  which intercepts form POSTs
  to gather identification at ingress and conditionally displays a login form
  at egress if challenge is required.
  
  Applications should supply their
  own login form, and use :class:`repoze.who.api.API` to authenticate
  and remember users.  To replace the challenger role, please use
  :class:`repoze.who.plugins.redirector.RedirectorPlugin`, configured with
  the URL of your application's login form.

:class:`repoze.who.plugins.form.RedirectingFormPlugin`

  An ``IIdentifier`` and ``IChallenger`` plugin, which intercepts form POSTs
  to gather identification at ingress and conditionally redirects a login form
  at egress if challenge is required.
  
  Applications should supply their
  own login form, and use :class:`repoze.who.api.API` to authenticate
  and remember users.  To replace the challenger role, please use
  :class:`repoze.who.plugins.redirector.RedirectorPlugin`, configured with
  the URL of your application's login form.


Third-party Plugins
-------------------

:class:`repoze.who.plugins.zodb.ZODBPlugin`
    This class implements the :class:`repoze.who.interfaces.IAuthenticator`
    and :class:`repoze.who.interfaces.IMetadataProvider` plugin interfaces
    using ZODB database lookups.  See
    http://pypi.python.org/pypi/repoze.whoplugins.zodb/

:class:`repoze.who.plugins.ldap.LDAPAuthenticatorPlugin`
    This class implements the :class:`repoze.who.interfaces.IAuthenticator`
    plugin interface using the :mod:`python-ldap` library to query an LDAP
    database.  See http://code.gustavonarea.net/repoze.who.plugins.ldap/

:class:`repoze.who.plugins.ldap.LDAPAttributesPlugin`
    This class implements the :class:`repoze.who.interfaces.IMetadataProvider`
    plugin interface using the :mod:`python-ldap` library to query an LDAP
    database.  See http://code.gustavonarea.net/repoze.who.plugins.ldap/

:class:`repoze.who.plugins.friendlyform.FriendlyFormPlugin`
    This class implements the :class:`repoze.who.interfaces.IIdentifier` and 
    :class:`repoze.who.interfaces.IChallenger` plugin interfaces.  It is
    similar to :class:`repoze.who.plugins.form.RedirectingFormPlugin`,
    bt with with additional features:

    - Users are not challenged on logout, unless the referrer URL is a
      private one (but that’s up to the application).

    - Developers may define post-login and/or post-logout pages.

    - In the login URL, the amount of failed logins is available in the
      environ. It’s also increased by one on every login try. This counter
      will allow developers not using a post-login page to handle logins that
      fail/succeed.

    See http://code.gustavonarea.net/repoze.who-friendlyform/ 

:func:`repoze.who.plugins.openid.identifiers.OpenIdIdentificationPlugin`
    This class implements the :class:`repoze.who.interfaces.IIdentifier`,
    :class:`repoze.who.interfaces.IAuthenticator`, and 
    :class:`repoze.who.interfaces.IChallenger` plugin interfaces using OpenId.
    See http://quantumcore.org/docs/repoze.who.plugins.openid/

:func:`repoze.who.plugins.openid.classifiers.openid_challenge_decider`
    This function provides the :class:`repoze.who.interfaces.IChallengeDecider`
    interface using OpenId.  See
    http://quantumcore.org/docs/repoze.who.plugins.openid/

:class:`repoze.who.plugins.use_beaker.UseBeakerPlugin`
    This packkage provids a :class:`repoze.who.interfaces.IIdentifier` plugin
    using :mod:`beaker.session` cache.  See
    http://pypi.python.org/pypi/repoze.who-use_beaker/

:class:`repoze.who.plugins.cas.main_plugin.CASChallengePlugin`
    This class implements the :class:`repoze.who.interfaces.IIdentifier`
    :class:`repoze.who.interfaces.IAuthenticator`, and 
    :class:`repoze.who.interfaces.IChallenger` plugin interfaces using CAS.
    See http://pypi.python.org/pypi/repoze.who.plugins.cas

:class:`repoze.who.plugins.cas.challenge_decider.my_challenge_decider`
    This function provides the :class:`repoze.who.interfaces.IChallengeDecider`
    interface using CAS.  See
    http://pypi.python.org/pypi/repoze.who.plugins.cas/

:class:`repoze.who.plugins.recaptcha.captcha.RecaptchaPlugin`
    This class implements the :class:`repoze.who.interfaces.IAuthenticator`
    plugin interface, using the recaptch API.
    See http://pypi.python.org/pypi/repoze.who.plugins.recaptcha/

:class:`repoze.who.plugins.sa.SQLAlchemyUserChecker`
    User existence checker for
    :class:`repoze.who.plugins.auth_tkt.AuthTktCookiePlugin`, based on
    the SQLAlchemy ORM. See http://pypi.python.org/pypi/repoze.who.plugins.sa/

:class:`repoze.who.plugins.sa.SQLAlchemyAuthenticatorPlugin`
    This class implements the :class:`repoze.who.interfaces.IAuthenticator`
    plugin interface, using the the SQLAlchemy ORM.
    See http://pypi.python.org/pypi/repoze.who.plugins.sa/
    
:class:`repoze.who.plugins.sa.SQLAlchemyUserMDPlugin`
    This class implements the :class:`repoze.who.interfaces.IMetadataProvider`
    plugin interface, using the the SQLAlchemy ORM.
    See http://pypi.python.org/pypi/repoze.who.plugins.sa/

:class:`repoze.who.plugins.formcookie.CookieRedirectingFormPlugin`
    This class implements the :class:`repoze.who.interfaces.IIdentifier` and 
    :class:`repoze.who.interfaces.IChallenger` plugin interfaces, similar
    to :class:`repoze.who.plugins.form.RedirectingFormPlugin`.  The
    plugin tracks the ``came_from`` URL via a cookie, rather than the query
    string.  See http://pypi.python.org/pypi/repoze.who.plugins.formcookie/
