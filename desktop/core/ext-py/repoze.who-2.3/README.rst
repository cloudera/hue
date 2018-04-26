``repoze.who``
==============

.. image:: https://travis-ci.org/repoze/repoze.who.png?branch=master
        :target: https://travis-ci.org/repoze/repoze.who

.. image:: https://readthedocs.org/projects/repozewho/badge/?version=latest
        :target: http://repozewho.readthedocs.org/en/latest/
        :alt: Documentation Status

Overview
--------

``repoze.who`` is an identification and authentication framework
for arbitrary WSGI applications.  ``repoze.who`` can be configured
either as WSGI middleware or as an API for use by an application.

``repoze.who`` is inspired by Zope 2's Pluggable Authentication
Service (PAS) (but ``repoze.who`` is not dependent on Zope in any
way; it is useful for any WSGI application).  It provides no facility
for authorization (ensuring whether a user can or cannot perform the
operation implied by the request).  This is considered to be the
domain of the WSGI application.
