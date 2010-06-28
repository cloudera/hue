# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
RELEASE = False

__version__ = '1.7.2'

from setuptools import setup, find_packages
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                'paste', 'util'))
import finddata

setup(name="Paste",
      version=__version__,
      description="Tools for using a Web Server Gateway Interface stack",
      long_description="""\
These provide several pieces of "middleware" (or filters) that can be nested to build web applications.  Each
piece of middleware uses the WSGI (`PEP 333`_) interface, and should
be compatible with other middleware based on those interfaces.

.. _PEP 333: http://www.python.org/peps/pep-0333.html

Includes these features...

Testing
-------

* A fixture for testing WSGI applications conveniently and in-process,
  in ``paste.fixture``

* A fixture for testing command-line applications, also in
  ``paste.fixture``

* Check components for WSGI-compliance in ``paste.lint``

Dispatching
-----------

* Chain and cascade WSGI applications (returning the first non-error
  response) in ``paste.cascade``

* Dispatch to several WSGI applications based on URL prefixes, in
  ``paste.urlmap``

* Allow applications to make subrequests and forward requests
  internally, in ``paste.recursive``

Web Application
---------------

* Run CGI programs as WSGI applications in ``paste.cgiapp``

* Traverse files and load WSGI applications from ``.py`` files (or
  static files), in ``paste.urlparser``

* Serve static directories of files, also in ``paste.urlparser``; also
  in that module serving from Egg resources using ``pkg_resources``.

Tools
-----

* Catch HTTP-related exceptions (e.g., ``HTTPNotFound``) and turn them
  into proper responses in ``paste.httpexceptions``

* Several authentication techniques, including HTTP (Basic and
  Digest), signed cookies, and CAS single-signon, in the
  ``paste.auth`` package.

* Create sessions in ``paste.session`` and ``paste.flup_session``

* Gzip responses in ``paste.gzip``

* A wide variety of routines for manipulating WSGI requests and
  producing responses, in ``paste.request``, ``paste.response`` and
  ``paste.wsgilib``

Debugging Filters
-----------------

* Catch (optionally email) errors with extended tracebacks (using
  Zope/ZPT conventions) in ``paste.exceptions``

* Catch errors presenting a `cgitb
  <http://python.org/doc/current/lib/module-cgitb.html>`_-based
  output, in ``paste.cgitb_catcher``.

* Profile each request and append profiling information to the HTML,
  in ``paste.debug.profile``

* Capture ``print`` output and present it in the browser for
  debugging, in ``paste.debug.prints``

* Validate all HTML output from applications using the `WDG Validator
  <http://www.htmlhelp.com/tools/validator/>`_, appending any errors
  or warnings to the page, in ``paste.debug.wdg_validator``

Other Tools
-----------

* A file monitor to allow restarting the server when files have been
  updated (for automatic restarting when editing code) in
  ``paste.reloader``

* A class for generating and traversing URLs, and creating associated
  HTML code, in ``paste.url``

The latest version is available in a `Subversion repository
<http://svn.pythonpaste.org/Paste/trunk#egg=Paste-dev>`_.

For the latest changes see the `news file
<http://pythonpaste.org/news.html>`_.

""",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Framework :: Paste",
        ],
      keywords='web application server wsgi',
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://pythonpaste.org",
      license="MIT",
      packages=find_packages(exclude=['ez_setup', 'examples', 'packages']),
      package_data=finddata.find_package_data(),
      namespace_packages=['paste'],
      zip_safe=False,
      extras_require={
        'subprocess': [],
        'hotshot': [],
        'Flup': ['flup'],
        'Paste': [],
        'openid': ['python-openid'],
        },
      entry_points="""
      [paste.app_factory]
      cgi = paste.cgiapp:make_cgi_application [subprocess]
      static = paste.urlparser:make_static
      pkg_resources = paste.urlparser:make_pkg_resources
      urlparser = paste.urlparser:make_url_parser
      proxy = paste.proxy:make_proxy
      test = paste.debug.debugapp:make_test_app
      test_slow = paste.debug.debugapp:make_slow_app
      transparent_proxy = paste.proxy:make_transparent_proxy
      watch_threads = paste.debug.watchthreads:make_watch_threads

      [paste.composite_factory]
      urlmap = paste.urlmap:urlmap_factory
      cascade = paste.cascade:make_cascade

      [paste.filter_app_factory]
      error_catcher = paste.exceptions.errormiddleware:make_error_middleware
      cgitb = paste.cgitb_catcher:make_cgitb_middleware
      flup_session = paste.flup_session:make_session_middleware [Flup]
      gzip = paste.gzipper:make_gzip_middleware
      httpexceptions = paste.httpexceptions:make_middleware
      lint = paste.lint:make_middleware
      printdebug = paste.debug.prints:PrintDebugMiddleware 
      profile = paste.debug.profile:make_profile_middleware [hotshot]
      recursive = paste.recursive:make_recursive_middleware
      # This isn't good enough to deserve the name egg:Paste#session:
      paste_session = paste.session:make_session_middleware
      wdg_validate = paste.debug.wdg_validate:make_wdg_validate_middleware [subprocess]
      evalerror = paste.evalexception.middleware:make_eval_exception
      auth_tkt = paste.auth.auth_tkt:make_auth_tkt_middleware
      auth_basic = paste.auth.basic:make_basic
      auth_digest = paste.auth.digest:make_digest
      auth_form = paste.auth.form:make_form
      grantip = paste.auth.grantip:make_grantip
      openid = paste.auth.open_id:make_open_id_middleware [openid]
      pony = paste.pony:make_pony
      errordocument = paste.errordocument:make_errordocument
      auth_cookie = paste.auth.cookie:make_auth_cookie
      translogger = paste.translogger:make_filter
      config = paste.config:make_config_filter
      registry = paste.registry:make_registry_manager

      [paste.server_runner]
      http = paste.httpserver:server_runner
      """,
      )


