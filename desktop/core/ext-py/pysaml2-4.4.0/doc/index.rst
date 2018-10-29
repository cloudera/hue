:Release: |release|
:Date: |today|

About SAML 2.0
==============

SAML 2.0 or Security Assertion Markup Language 2.0 is a version of the SAML standard for exchanging authentication and authorization data between security domains.

About PySAML2
=============

PySAML2 is a pure python implementation of SAML2. It contains all
necessary pieces for building a SAML2 service provider or an identity provider.
The distribution contains examples of both.
Originally written to work in a WSGI environment there are extensions that
allow you to use it with other frameworks.


How to use PySAML2
===================

Before you can use Pysaml2, you'll need to get it installed.
If you have not done it yet, read the :ref:`install`

Well, now you have it installed and you want to do something.

And I'm sorry to tell you this; but there isn't really a lot you can do with
this code on it's own.

Sure you can send a AuthenticationRequest to an IdentityProvider or a
AttributeQuery to an AttributeAuthority but in order to get what they
return you have to sit behind a Web server. Well that is not really true since
the AttributeQuery would be over SOAP and you would get the result over the
connection you have to the AttributeAuthority.

But anyway, you may get my point. This is middleware stuff !

PySAML2 is built to fit into a
`WSGI  <http://www.python.org/dev/peps/pep-0333/>`_ application

But it can be used in a non-WSGI environment too.

So you will find descriptions of both cases here.

The configuration is the same disregarding whether you are using PySAML2 in a
WSGI or non-WSGI environment.

Table of contents
==================

.. toctree::
   :maxdepth: 2

   install
   examples/index
   howto/index
   sp_test/internal



* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

