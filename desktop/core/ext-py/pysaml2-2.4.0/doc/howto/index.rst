.. _howto:

How to use PySAML2
===================

:Release: |release|
:Date: |today|

Before you can use Pysaml2, you'll need to get it installed. 
If you have not done it yet, read the :ref:`install`

Well, now you have it installed and you want to do something.

And I'm sorry to tell you this; but there isn't really a lot you can do with 
this code on its own.

Sure you can send a AuthenticationRequest to an IdentityProvider or a 
AttributeQuery to an AttributeAuthority, but in order to get what they
return you have to sit behind a Web server. Well that is not really true since
the AttributeQuery would be over SOAP and you would get the result over the
connection you have to the AttributeAuthority.

But anyway, you may get my point. This is middleware stuff !

PySAML2 is built to fit into a 
`WSGI  <http://www.python.org/dev/peps/pep-0333/>`_ application

But it can be used in a non-WSGI environment too. 

So you will find descriptions of both cases here.

The configuration is the same regardless of whether you are using PySAML2 in a 
WSGI or non-WSGI environment.

.. toctree::
   :maxdepth: 1

   config

   
