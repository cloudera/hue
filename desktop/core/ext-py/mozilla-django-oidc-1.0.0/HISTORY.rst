.. :changelog:

History
-------

1.0.0 (unreleased)
++++++++++++++++++

* Add OIDC_AUTHENTICATION_CALLBACK_URL as a new configuration parameter
* Fail earlier when JWS algorithm does not OIDC_RP_SIGN_ALGO.
  Thanks `@anlutro`_
* RS256 verification through ``settings.OIDC_OP_JWKS_ENDPOINT``
  Thanks `@GermanoGuerrini`_
* Refactor OIDCAuthenticationBackend so that token retrieval methods can be overridden in a subclass when you need to.

Backwards-incompatible changes:

* ``OIDC_OP_LOGOUT_URL_METHOD`` takes a ``request`` parameter now.
* Changed name of ``RefreshIDToken`` middleware to ``SessionRefresh``.


.. _`@anlutro`: https://github.com/anlutro

0.6.0 (2018-03-27)
++++++++++++++++++

* Add e2e tests and automation
* Add caching for exempt URLs
* Fix logout when session refresh fails

0.5.0 (2018-01-10)
++++++++++++++++++

* Add Django 2.0 support
* Fix tox configuration

Backwards-incompatible changes:

* Drop Django 1.10 support

0.4.2 (2017-11-29)
++++++++++++++++++

* Fix OIDC_USERNAME_ALGO to actually load dotted import path of callback.
* Add verify_claims method for advanced authentication checks

0.4.1 (2017-10-25)
++++++++++++++++++

* Send bytes to josepy. Fixes python3 support.

0.4.0 (2017-10-24)
++++++++++++++++++

Security issues:

* **High**: Replace python-jose with josepy and use pyca/cryptography instead of pycrypto (CVE-2013-7459).

Backwards-incompatible changes:

* ``OIDC_RP_IDP_SIGN_KEY`` no longer uses the JWK json as ``dict`` but PEM or DER keys instead.


0.3.2 (2017-10-03)
++++++++++++++++++

Features:

* Implement RS256 verification
  Thanks `@puiterwijk`_

Bugs:

* Use ``settings.OIDC_VERIFY_SSL`` also when validating the token.
  Thanks `@GermanoGuerrini`_
* Make OpenID Connect scope configurable.
  Thanks `@puiterwijk`_
* Add path host injection unit-test (#171)
* Revisit OIDC_STORE_{ACCESS,ID}_TOKEN config entries
* Allow configuration of additional auth parameters


.. _`@GermanoGuerrini`: https://github.com/GermanoGuerrini
.. _`@puiterwijk`: https://github.com/puiterwijk

0.3.1 (2017-06-15)
++++++++++++++++++

Security issues:

* **Medium**: Sanitize next url for authentication view

0.3.0 (2017-06-13)
++++++++++++++++++

Security issues:

* **Low**: Logout using POST not GET (#126)

Backwards-incompatible changes:

* The ``settings.SITE_URL`` is no longer used. Instead the absolute URL is
  derived from the request's ``get_host()``.
* Only log out by HTTP POST allowed.

Bugs:

* Test suite maintenance (#108, #109, #142)

0.2.0 (2017-06-07)
++++++++++++++++++

Backwards-incompatible changes:

* Drop support for Django 1.9 (#130)

  If you're using Django 1.9, you should update Django first.

* Move middleware to ``mozilla_django_oidc.middleware`` and
  change it to use authentication endpoint with ``prompt=none`` (#94)

  You'll need to update your ``MIDDLEWARE_CLASSES``/``MIDDLEWARE``
  setting accordingly.

* Remove legacy ``base64`` handling of OIDC secret. Now RP secret
  should be plaintext.

Features:

* Add support for Django 1.11 and Python 3.6 (#85)
* Update middleware to work with Django 1.10+ (#90)
* Documentation updates
* Rework test infrastructure so it's tox-based (#100)

Bugs:

* always decode verified token before ``json.load()`` (#116)
* always redirect to logout_url even when logged out (#121)
* Change email matching to be case-insensitive (#102)
* Allow combining OIDCAuthenticationBackend with other backends (#87)
* fix is_authenticated usage for Django 1.10+ (#125)

0.1.0 (2016-10-12)
++++++++++++++++++

* First release on PyPI.
