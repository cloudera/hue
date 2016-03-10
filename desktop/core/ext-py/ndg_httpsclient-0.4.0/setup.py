try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

_long_description = '''
This is a HTTPS client implementation for httplib and urllib2 based on
PyOpenSSL.  PyOpenSSL provides a more fully featured SSL implementation over the
default provided with Python and importantly enables full verification of the
SSL peer.

Releases
========
0.4.0
-----
 * Made dual compatible with Python 2 / 3.
 
0.3.3
-----
 * Fix to add in AnotherName for ``subjectAltNames`` field - added for support for CACert issued
   certs (thanks to Gu1).
 * Fix to HTTP Basic Auth option for ``ndg.httpsclient.utils.main``
 * Fix to ``ServerSSLCertVerification`` so that it can pass a function-based callback instead of using ``__call__``. In newer versions of OpenSSL (>= 0.14) the latter failed because of a request for ``__name__`` attribute.

0.3.2
-----
 * Fix to SubjectAltNames support check - should only be enabled if pyasn1 is 
   installed.
 * Fix to open_url: HTTP Request object was being created inside if headers is 
   None block - now corrected to create regardless.
 * Added http basic auth support to script. (Thanks to Willem van Engen)
 
0.3.1
-----
 * extended utils functions to support keyword for passing additional urllib2
   handlers.

0.3.0
-----
 * Added ndg.httpsclient.utils.fetch_stream_from_url function and added
   parameter for data to post in open_url and fetch_* methods.
 * fix to ndg.httpsclient.utils module _should_use_proxy and open_url functions

0.2.0
-----
 * added support for SSL verification with subjectAltNames using pyasn1
 * fixed minor bug - SSL cert DN prefix matching

0.1.0
-----
Initial release

Prerequisites
=============
This has been developed and tested for Python 2.6 and 2.7 with pyOpenSSL 0.13 and 0.14.  
Version 0.4.0 tested with pyOpenSSL 0.15.1 and Python 2.7 and 3.4.  Note that proxy support 
is only available from Python 2.6.2 onwards.  pyasn1 is required for correct SSL 
verification with subjectAltNames.

Installation
============
Installation can be performed using easy_install or pip.

Running ndg_httpclient
======================
A simple script for fetching data using HTTP or HTTPS GET from a specified URL.

Parameter:

``url``
  The URL of the resource to be fetched

Options:

``-h, --help``
  Show help message and exit.

``-c FILE, --certificate=FILE``
  Certificate file - defaults to ``$HOME/credentials.pem``

``-k FILE, --private-key=FILE``
  Private key file - defaults to the certificate file

``-t DIR, --ca-certificate-dir=DIR``
  Trusted CA certificate file directory.

``-d, --debug``
  Print debug information - this may be useful in solving problems with HTTP or 
  HTTPS access to a server.
    
``-p FILE, --post-data-file=FILE``
  POST data file
    
``-f FILE, --fetch=FILE``
  Output file
    
``-n, --no-verify-peer``
  Skip verification of peer certificate.
'''
    
setup(
    name='ndg_httpsclient',
    version="0.4.0",
    description='Provides enhanced HTTPS support for httplib and urllib2 using '
                'PyOpenSSL',
    author='Richard Wilkinson and Philip Kershaw',
    author_email='Philip.Kershaw@stfc.ac.uk',
    url='https://github.com/cedadev/ndg_httpsclient/',
    long_description=_long_description,
    license='BSD - See LICENCE file for details',
    namespace_packages=['ndg'],
    packages=find_packages(),
    package_dir={'ndg.httpsclient': 'ndg/httpsclient'},
    package_data={
        'ndg.httpsclient': [
            'test/README', 
            'test/scripts/*.sh',
            'test/pki/localhost.*',
            'test/pki/ca/*.0'
            ],
    },
    install_requires = ['PyOpenSSL'],
    extras_require = {'subjectAltName_support': 'pyasn1'},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe = False,
    entry_points = {
        'console_scripts': ['ndg_httpclient = ndg.httpsclient.utils:main',
                            ],
        }
)
