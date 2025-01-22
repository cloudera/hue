FAQ
===

**Why can't SAML be implemented as an Django Authentication Backend?**

well SAML authentication is not that simple as a set of credentials you can
put on a login form and get a response back. Actually the user password is
not given to the service provider at all. This is by design. You have to
delegate the task of authentication to the IdP and then get an asynchronous
response from it.

Given said that, djangosaml2 does use a Django Authentication Backend to
transform the SAML assertion about the user into a Django user object.

**Why not put everything in a Django middleware class and make our lifes
easier?**

Yes, that was an option I did evaluate but at the end the current design
won. In my opinion putting this logic into a middleware has the advantage
of making it easier to configure but has a couple of disadvantages: first,
the middleware would need to check if the request path is one of the
SAML endpoints for every request. Second, it would be too magical and in
case of a problem, much harder to debug.

**Why not call this package django-saml as many other Django applications?**

Following that pattern then I should import the application with
import saml but unfortunately that module name is already used in pysaml2.

**saml2.response.UnsolicitedResponse: Unsolicited response**

If you are experiencing issues with unsolicited requests this is due to the fact that
 cookies not being sent when using the HTTP-POST binding. You have to configure samesite
 djangosaml2 middleware (see setup documentation) and also consider upgrading
 to Django 3.1 or higher.
If you can't do that, configure "allow_unsolicited" to True in pySAML2 configuration.
