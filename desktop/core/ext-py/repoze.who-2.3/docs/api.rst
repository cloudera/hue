.. _api_narrative:

Using the :mod:`repoze.who` Application Programming Interface (API)
===================================================================

.. _without_middleware:

Using :mod:`repoze.who` without Middleware
------------------------------------------

An application which does not use the :mod:`repoze.who` middleware needs
to perform two separate tasks to use :mod:`repoze.who` machinery:

- At application startup, it must create an :class:`repoze.who.api:APIFactory`
  instance, populating it with a request classifier, a challenge decider,
  and a set of plugins.  It can do this process imperatively
  (see :ref:`imperative_configuration`), or using a declarative
  configuration file (see :ref:`declarative_configuration`).  For the latter
  case, there is a convenience function,
  :func:`repoze.who.config.make_api_factory_with_config`:

.. code-block:: python

   # myapp/run.py
   from repoze.who.config import make_api_factory_with_config
   who_api_factory = None
   def startup(global_conf):
       global who_api_factory
       who_api_factory = make_api_factory_with_config(global_conf,
                                                      '/path/to/who.config')

- When it needs to use the API, it must call the ``APIFactory``, passing
  the WSGI environment to it.  The ``APIFactory`` returns an object
  implementing the :class:`repoze.who.interfaces:IRepozeWhoAPI` interface.

.. code-block:: python

   # myapp/views.py
   from myapp.run import who_api_factory
   def my_view(context, request):
       who_api = who_api_factory(request.environ)

- Calling the ``APIFactory`` multiple times within the same request is
  allowed, and should be very cheap (the API object is cached in the
  request environment).


.. _middleware_api_hybrid:

Mixed Use of :mod:`repoze.who` Middleware and API
-------------------------------------------------

An application which uses the :mod:`repoze.who` middleware may still need
to interact directly with the ``IRepozeWhoAPI`` object for some purposes.
In such cases, it should call :func:`repoze.who.api:get_api`, passing
the WSGI environment.

.. code-block:: python

   from repoze.who.api import get_api
   def my_view(context, request):
       who_api = get_api(request.environ)

Alternately, the application might configure the ``APIFactory`` at startup,
as above, and then use it to find the API object, or create it if it was
not already created for the current request (e.g. perhaps by the middleware):

.. code-block:: python

   def my_view(context, request):
       who_api = context.who_api_factory(request.environ)


.. _writing_custom_login_view:

Writing a Custom Login View
---------------------------

:class:`repoze.who.api.API` provides a helper method to assist developers
who want to control the details of the login view.  The following
BFG example illustrates how this API might be used:

.. code-block:: python
   :linenos:

    def login_view(context, request):
        message = ''

        who_api = get_api(request.environ)
        if 'form.login' in request.POST:
            creds = {}
            creds['login'] = request.POST['login']
            creds['password'] = request.POST['password']
            authenticated, headers = who_api.login(creds)
            if authenticated:
                return HTTPFound(location='/', headers=headers)

            message = 'Invalid login.'
        else:
            # Forcefully forget any existing credentials.
            _, headers = who_api.login({})

        request.response_headerlist = headers
        if 'REMOTE_USER' in request.environ:
            del request.environ['REMOTE_USER']

        return {'message': message}

This application is written as a "hybrid":  the :mod:`repoze.who` middleware
injects the API object into the WSGI enviornment on each request.

- In line 4, this  application extracts the API object from the environ
  using :func:`repoze.who.api:get_api`.

- Lines 6 - 8 fabricate a set of credentials, based on the values the
  user entered in the form.

- In line 9, the application asks the API to authenticate those credentials,
  returning an identity and a set of respones headers.

- Lines 10 and 11 handle the case of successful authentication:  in this
  case, the application redirects to the site root, setting the headers
  returned by the API object, which will "remember" the user across requests.

- Line 13 is reached on failed login.  In this case, the headers returned
  in line 9 will be "forget" headers, clearing any existing cookies or other
  tokens.

- Lines 14 - 16 perform a "fake" login, in order to get the "forget" headers.

- Line 18 sets the "forget" headers to clear any authenticated user for
  subsequent requests.

- Lines 19 - 20 clear any authenticated user for the current request.

- Line 22 returns any message about a failed login to the rendering template.


.. _interfaces:

Interfaces
----------

.. automodule:: repoze.who.interfaces

  .. autointerface:: IAPIFactory
     :members:

  .. autointerface:: IAPI
     :members:

  .. autointerface:: IPlugin
     :members:

  .. autointerface:: IRequestClassifier
     :members:

  .. autointerface:: IChallengeDecider
      :members:

  .. autointerface:: IIdentifier
     :members:

  .. autointerface:: IAuthenticator
     :members:

  .. autointerface:: IChallenger
     :members:

  .. autointerface:: IMetadataProvider
     :members:
