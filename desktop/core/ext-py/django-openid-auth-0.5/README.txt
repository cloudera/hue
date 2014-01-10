= Django OpenID Authentication Support =

This package provides integration between Django's authentication
system and OpenID authentication.  It also includes support for using
a fixed OpenID server endpoint, which can be useful when implementing
single signon systems.


== Basic Installation ==

 1. Install the Jan Rain Python OpenID library.  It can be found at:

        http://openidenabled.com/python-openid/

    It can also be found in most Linux distributions packaged as
    "python-openid".  You will need version 2.2.0 or later.

 2. Add 'django_openid_auth' to INSTALLED_APPS for your application.
    At a minimum, you'll need the following in there:

        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django_openid_auth',
        )

 3. Add 'django_auth_openid.auth.OpenIDBackend' to
    AUTHENTICATION_BACKENDS.  This should be in addition to the
    default ModelBackend:

        AUTHENTICATION_BACKENDS = (
            'django_openid_auth.auth.OpenIDBackend',
            'django.contrib.auth.backends.ModelBackend',
        )

 4. To create users automatically when a new OpenID is used, add the
    following to the settings:

        OPENID_CREATE_USERS = True

 5. To have user details updated from OpenID Simple Registration or
    Attribute Exchange extension data each time they log in, add the
    following:

        OPENID_UPDATE_DETAILS_FROM_SREG = True

 6. Hook up the login URLs to your application's urlconf with
    something like:

        urlpatterns = patterns('',
            ...
            (r'^openid/', include('django_openid_auth.urls')),
            ...
        )

 7. Configure the LOGIN_URL and LOGIN_REDIRECT_URL appropriately for
    your site:

        LOGIN_URL = '/openid/login/'
        LOGIN_REDIRECT_URL = '/'

    This will allow pages that use the standard @login_required
    decorator to use the OpenID login page.

 8. Rerun "python manage.py syncdb" to add the UserOpenID table to
    your database.


== Configuring Single Sign-On ==

If you only want to accept identities from a single OpenID server and
that server implemnts OpenID 2.0 identifier select mode, add the
following setting to your app:

    OPENID_SSO_SERVER_URL = 'server-endpoint-url'

With this setting enabled, the user will not be prompted to enter
their identity URL, and instead an OpenID authentication request will
be started with the given server URL.

As an example, to use Launchpad accounts for SSO, you'd use:

     OPENID_SSO_SERVER_URL = 'https://login.launchpad.net/'


== Launchpad Teams Support ==

This library supports the Launchpad Teams OpenID extension.  Using
this feature, it is possible to map Launchpad team memberships to
Django group memberships.  It can be configured with:

    OPENID_SSO_SERVER_URL = 'https://login.launchpad.net/'
    OPENID_LAUNCHPAD_TEAMS_MAPPING = {
        'launchpad-team-1': 'django-group-1',
        'launchpad-team-2': 'django-group-2',
        }

When a user logs in, they will be added or removed from the relevant
teams listed in the mapping.

If you have already django-groups and want to map these groups automatically, you can use the OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO variable in your settings.py file.

	OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO = True

If you use OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO, the variable OPENID_LAUNCHPAD_TEAMS_MAPPING will be ignored.
If you want to exclude some groups from the auto mapping, use OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST. This variable has only an effect if OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO is True.

	OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST = ['django-group1', 'django-group2']
	
== External redirect domains ==

By default, redirecting back to an external URL after auth is forbidden. To permit redirection to external URLs on a separate domain, define ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS in your settings.py file as a list of permitted domains:

	ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS = ['example.com', 'example.org']

and redirects to external URLs on those domains will additionally be permitted.

== Use as /admin (django.admin.contrib) login ==

If you require openid authentication into the admin application, add the following setting:

        OPENID_USE_AS_ADMIN_LOGIN = True

It is worth noting that a user needs to be be marked as a "staff user" to be able to access the admin interface.  A new openid user will not normally be a "staff user".  
The easiest way to resolve this is to use traditional authentication (OPENID_USE_AS_ADMIN_LOGIN = False) to sign in as your first user with a password and authorise your 
openid user to be staff.

== Change Django usernames if the nickname changes on the provider ==

If you want your Django username to change when a user updates the nickname on their provider, add the following setting:

        OPENID_FOLLOW_RENAMES = True

If the new nickname is available as a Django username, the user is renamed.
Otherwise the user will be renamed to nickname+i for an incrememnting value of i until no conflict occurs.
If the user has already been renamed to nickname+1 due to a conflict, and the nickname is still not available, the user will keep their existing username.

== Require a valid nickname ==

If you must have a valid, unique nickname in order to create a user accont, add the following setting:

        OPENID_STRICT_USERNAMES = True
        
This will cause an OpenID login attempt to fail if the provider does not return a 'nickname' (username) for the user, or if the nickname conflicts with an existing user with a different openid identiy url.
Without this setting, logins without a nickname will be given the username 'openiduser', and upon conflicts with existing username, an incrementing number will be appended to the username until it is unique.

== Require Physical Multi-Factor Authentication ==

If your users should use a physical multi-factor authentication method, such as RSA tokens or YubiKey, add the following setting:

        OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = True
        
If the user's OpenID provider supports the PAPE extension and provides the Physical Multifactor authentication policy, this will
cause the OpenID login to fail if the user does not provide valid physical authentication to the provider.

== Override Login Failure Handling ==

You can optionally provide your own handler for login failures by adding the following setting:

        OPENID_RENDER_FAILURE = failure_handler_function

Where failure_handler_function is a function reference that will take the following parameters:

        def failure_handler_function(request, message, status=None, template_name=None, exception=None)

This function must return a Django.http.HttpResponse instance.

== Use the user's email for suggested usernames ==

You can optionally strip out non-alphanumeric characters from the user's email
to generate a preferred username, if the server doesn't provide nick
information, by setting the following setting:

        OPENID_USE_EMAIL_FOR_USERNAME = True

Otherwise, and by default, if the server omits nick information and a user is
created it'll receive a username 'openiduser' + a number.
Consider also the OPENID_STRICT_USERNAMES setting (see ``Require a valid nickname``)
