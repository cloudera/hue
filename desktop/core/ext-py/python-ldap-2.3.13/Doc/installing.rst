.. % $Id: ldap-dn.tex,v 1.8 2008/03/26 12:10:12 stroeder Exp 

***********************
Building and installing
***********************

Prerequisites
=============

The following software packages are required to be installed
on the local system when building python-ldap:

- Python version 2.3 or later including its development files: http://www.python.org/
- OpenLDAP client libs version 2.3 or later: http://www.openldap.org/
  It is not possible and not supported to build with prior versions.
- OpenSSL (optional): http://www.openssl.org/
- cyrus-sasl (optional): http://asg.web.cmu.edu/sasl/sasl-library.html
- Kerberos libs, MIT or heimdal (optional)

setup.cfg
=========

The file setup.cfg allows to set some build and installation
parameters for reflecting the local installation of required
software packages. Only section [_ldap] is described here.
More information about other sections can be found in the
documentation of Python's DistUtils.

.. data:: library_dirs

   Specifies in which directories to search for required libraries.

.. data:: include_dirs

   Specifies in which directories to search for include files of required libraries.

.. data:: libs

   A space-separated list of library names to link to (see :ref:`libs-used-label`).

.. data:: extra_compile_args

   Compiler options.

.. data:: extra_objects

.. _libs-used-label:

Libs used
---------

.. data:: ldap
.. data:: ldap_r

   The LDAP protocol library of OpenLDAP. ldap_r is the reentrant version
   and should be preferred.

.. data:: lber

   The BER encoder/decoder library of OpenLDAP.

.. data:: sasl2

   The Cyrus-SASL library if needed and present during build

.. data:: ssl

   The SSL/TLS library of OpenSSL if needed and present during build

.. data:: crypto

   The basic cryptographic library of OpenSSL if needed and present during build

Example
=============

The following example is for a full-featured build (including SSL and SASL support)
of python-ldap with OpenLDAP installed in a different prefix directory
(here /opt/openldap-2.3) and SASL header files found in /usr/include/sasl.
Debugging symbols are preserved with compile option -g. ::

  [_ldap]
  library_dirs = /opt/openldap-2.3/lib
  include_dirs = /opt/openldap-2.3/include /usr/include/sasl

  extra_compile_args = -g
  extra_objects =

  libs = ldap_r lber sasl2 ssl crypto

