:mod:`repoze.who` Use Cases
===========================

How should an application interact with :mod:`repoze.who`?  There are three
main scenarios:

Middleware-Only Use Cases
-------------------------

Examples of using the :mod:`repoze.who` middleware, without explicitly
using its API.


Simple:  Bug Tracker with ``REMOTE_USER``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This application expects the ``REMOTE_USER`` variable to be set by
the middleware for authenticated requests.  It allows the middleware to
handle challenging the user when needed.

In protected views, such as those which allow creating or following up
to bug reports:

- Check ``environ['REMOTE_USER']`` to get the authenticated user, and apply
  any application-specific policy (who is allowed to edit).

  - If the access check fails because the user is not yet authenticated,
    return an 401 Unauthorized response.

  - If the access check fails for authenticated users, return a
    403 Forbidden response.

Note that the application here doesn't depend on :mod:`repoze.who` at
all:  it would work identically if run behind Apache's ``mod_auth``.  The
``Trac`` application works exactly this way.

The middleware can be configured to suit the policy required for the
site, e.g.:

- challenge / identify using HTTP basic authentication

- authorize via an ``.htaccces``-style file.


More complex:  Wiki with ``repoze.who.identity``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This application use the ``repoze.who.identity`` variable set in the
WSGI environment by the middleware for authenticated requests.  The application
still allows the middleware to handle challenging the user when needed.

The only difference from the previous example is that protected views,
such as those which allow adding or editing wiki pages, can use the extra
metadata stored inside ``environ['repoze.who.identity']`` (a mapping) to
make authorization decisions:  such metadata might include groups or roles
mapped by the middleware onto the user.


API-Only Use Cases
------------------

Examples of using the :mod:`repoze.who` API without its middleware.


Simple:   Wiki with its own login and logout views.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This application uses the :mod:`repoze.who` API to compute the authenticated
user, as well as using its ``remember`` API to set headers for cookie-based
authentication.

In each view:

- Call ``api.authenticate`` to get the authenticated user.

- Show a ``login`` link for non-authenticated requests.

- Show a ``logout`` link for authenticated requests.

- Don't show "protected" links for non-authenticated requests.

In protected views, such as those which allow adding or editing
wiki pages:

- Call ``api.authenticate`` to get the authenticated user;  check
  the metadata about the user (e.g., any appropriate roles or groups)
  to verify access.

  - If the access check fails because the user is not yet authenticated,
    redirect to the ``login`` view, with a ``came_from`` value of the
    current URL.

  - If the access check fails for authenticated users, return a
    403 Forbidden response.

In the login view:

- For ``GET`` requests, show the login form.

- For ``POST`` requests, validate the login and password from the form.
  If successful, call ``api.remember``, and append the returned headers to
  your response, which may also contain, e.g., a ``Location`` header for
  a redirect to the ``came_from`` URL.  In this case, there will be
  no authenticator plugin which knows about the login / password at all.

In the logout view:

- Call ``api.forget`` and append the headers to your response, which may
  also contain, e.g., a ``Location`` header for a redirect to the
  ``came_from`` URL after logging out.


More complex:  multiple applications with "single sign-on"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this scenario, authentication is "federated" across multiple applications,
which delegate to a central "login application."  This application verifies
credentials from the user, and then uses headers or other tokens to
communicate the verified identity to the delegating application.

In the login application:

- The SSO login application works just like the login view described above:
  the difference is that the configured identifier plugins must emit
  headers from ``remember`` which can be recognized by their counterparts
  in the other apps.

In the non-login applications:

- Challenge plugins here must be configured to implement the specific
  SSO protocol, e.g. redirect to the login app with information in the
  query string (other protocols might differ).

- Identifer plugins must be able to "crack" / consume whatever tokens are
  returned by the SSO login app.

- Authenticators will normally be no-ops (e.g., the ``auth_tkt`` plugin
  used as an authenticator).

Hybrid Use Cases
----------------

Examples of using the :mod:`repoze.who` API in conjuntion with its middleware.

Most complex:  integrate Trac and the wiki behind SSO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example extends the previous one, but adds into the mix the
requirement that one or more of the non-login applications (e.g., Trac)
be used "off the shelf," without modifying them.  Such applications can
be plugged into the same SSO regime, with the addition of the
:mod:``repoze.who`` middleware as an adapter to bridge the gap (e.g.,
to turn the SSO tokens into the ``REMOTE_USER`` required by Trac).

In this scenario, the middleware would be configured identically to the
API used in applications which do not need the middleware shim.
