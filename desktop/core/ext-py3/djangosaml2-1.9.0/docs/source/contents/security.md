Introduction
============

Authentication and Authorization are quite security relevant topics on its own.
Make sure you understand SAML2 and its implications, specifically the
separation of duties between Service Provider (SP) and Identity Provider (IdP):
this library aims to support a Service Provider in getting authenticated with
with one or more Identity Provider.

Communication between SP and IdP is routed via the Browser, eliminating the
need for direct communication between SP and IdP. However, for security the use
of cryptographic signatures (both while sending and receiving messages) must be
examined and the private keys in use must be kept closely guarded.

Content Security Policy
=======================

When using POST-Bindings, the Browser is presented with a small HTML-Form for
every redirect (both Login and Logout), which is sent using JavaScript and
sends the Data to the selected IdP. If your application uses technices such as
Content Security Policy, this might affect the calls. Since Version 1.9.0
djangosaml2 will detect if django-csp is installed and update the Content
Security Policy accordingly.

[Content Security Policy](https://content-security-policy.com/) is an important
HTTP-Extension to prevent User Input or other harmful sources from manipulating
application data. Usage is strongly advised, see
[OWASP Control](https://owasp.org/www-community/controls/Content_Security_Policy).

To enable CSP with [django-csp](https://django-csp.readthedocs.io/), simply
follow their [installation](https://django-csp.readthedocs.io/en/latest/installation.html)
and [configuration](https://django-csp.readthedocs.io/en/latest/configuration.html)
guides: djangosaml2 will automatically blend in and update the headers for
POST-bindings, so you must not include exceptions for djangosaml2 in your
global configuration.

Note that to enable autosubmit of post-bindings inline-javascript is used. To
allow execution of this autosubmit-code a nonce is included, which works in
default configuration but may not work if you modify `CSP_INCLUDE_NONCE_IN`
to exclude `script-src`.

You can specify a custom CSP handler via the `SAML_CSP_HANDLER` setting and the
warning can be disabled by setting `SAML_CSP_HANDLER=''`. See the 
[djangosaml2](https://djangosaml2.readthedocs.io/) documentation for more 
information.
