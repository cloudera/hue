django-oidc-auth
================

An OpenID Connect Client for Django.


HOW TO USE
----------

First things first, so:

    $ pip install django-oidc-auth

Then add this to your settings:

    INSTALLED_APPS = (
        # ...
        'oidc_auth',
        # ...
    )

    # Put all custom configurations inside this dict
    OIDC_AUTH = {
        'SCOPES': ('openid', 'preferred_username', 'email', 'profile'),
    }

    LOGIN_URL = 'oidc-login'
    LOGIN_REDIRECT_URL = '/'

    AUTHENTICATION_BACKENDS = (
        'oidc_auth.auth.OpenIDConnectBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

Finally, add this to your *urls.py*:

    urlpatterns = patterns('your.views',
        # ...
        url(r'oidc/', include('oidc_auth.urls')),
    )

Run `python manage.py migrate` and you're ready (*kinda*).

<!--
#TODO
#----
#
#Primeiro, faz o discovery e obtem todos os dados do sistema.
#
#Grava os endpoints.
#
#Segundo, faz o register e então inicia o trabalho de autenticação
-->
