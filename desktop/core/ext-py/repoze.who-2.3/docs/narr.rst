:mod:`repoze.who` Narrative Documentation
=========================================

Using :mod:`repoze.who` as WSGI Middleware
------------------------------------------

:mod:`repoze.who` was originally developed for use as authentication
middleware in a WSGI pipeline, for use by applications which only
needed to obtain an "authenticated user" to enforce a given security
policy.

See :ref:`middleware_responsibilities` for a description of this use case.


Using :mod:`repoze.who` without WSGI Middleware
-----------------------------------------------

Some applications might want to use a configured set of
:mod:`repoze.who` plugins to do identification and authentication for
a request, outside the context of using :mod:`repoze.who` middleware.
For example, a performance-sensitive application might wish to defer
the effort of identifying and authenticating a user until the point at
which authorization is required, knowing that some code paths will not
need to do the work.

See :ref:`api_narrative` for a description of this use case.


Mixing Middleware and API Uses
------------------------------

Some applications might use the :mod:`repoze.who` middleware for most
authentication purposes, but need to participate more directly in the
mechanics of identification and authorization for some portions of the
application.  For example, consider a system which allows users to
sign up online for membrship in a site: once the user completes
registration, such an application might wish to log the user in
transparently, and thus needs to interact with the configured
:mod:`repoze.who` middleware to generate response headers, ensuring
that the user's next request is properly authenticated.

See :ref:`middleware_api_hybrid` for a description of this use case.


Configuring :mod:`repoze.who`
-----------------------------

Developers and integrators can configure :mod:`repoze.who` using either
imperative Python code (see :ref:`imperative_configuration`) or using an
INI-style declarative configuration file (see :ref:`declarative_configuration`).
In either case, the result of the configuration will be a
:class:`repoze.who.api:APIFactory` instance, complete with a request
classifier, a challenge decider, and a set of plugins for each plugin
interface.
