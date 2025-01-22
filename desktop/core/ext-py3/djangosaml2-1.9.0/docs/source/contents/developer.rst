Testing
=======

One way to check if everything is working as expected is to enable the
following url::

  urlpatterns = patterns(
      '',
      #  lots of url definitions here

      (r'saml2/', include('djangosaml2.urls')),
      (r'test/', 'djangosaml2.views.EchoAttributesView.as_view()'),

      #  more url definitions
  )


Now if you go to the /test/ url you will see your SAML attributes and also
a link to do a global logout.

Unit tests
==========

Djangosaml2 have a legacy way to do tests, using an example project in `tests` directory.
This means that to run tests you have to clone the repository, then install djangosaml2, then run tests using the example project.

example::

  pip install -r requirements-dev.txt
  # or
  pip install djangosaml2[test]


then::
  cd tests
  ./manage.py migrate
  ./manage.py test djangosaml2


If you have `tox`_ installed you can simply call `tox` inside the root directory
and it will run the tests in multiple versions of Python.

.. _`tox`: http://pypi.python.org/pypi/tox


Code Coverage
=============

example::

  cd tests/
  coverage erase
  coverage run ./manage.py test djangosaml2 testprofiles
  coverage report -m


Custom error handler
====================

When an error occurs during the authentication flow, djangosaml2 will render
a simple error page with an error message and status code. You can customize
this behaviour by specifying the path to your own error handler in the settings::

  SAML_ACS_FAILURE_RESPONSE_FUNCTION = 'python.path.to.your.view'

This should be a view which takes a request, optional exception which occured
and status code, and returns a response to serve the user. E.g. The default
implementation looks like this::

  def template_failure(request, exception=None, status=403, **kwargs):
      """ Renders a simple template with an error message. """
      return render(request, 'djangosaml2/login_error.html', {'exception': exception}, status=status)


Contributing
============

Please open Issues to start debate regarding the requested
features, or the patch that you would apply. We do not use
a strict submission format, please try to be more concise as possibile.

The Pull Request MUST be done on the dev branch, please don't
push code directly on the master branch.
