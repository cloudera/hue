from django.conf.urls import url
from oidc_auth.views import login_begin, login_complete

"""
urlpatterns = patterns('oidc_auth.views',
    url(r'^login/$', 'login_begin', name='oidc-login'),
    url(r'^complete/$', 'login_complete', name='oidc-complete'),
)
"""

# Modified for Django 1.11

urlpatterns = [
    'oidc_auth.views',
    url(r'^login/$', login_begin, name='oidc-login'),
    url(r'^complete/$', login_complete, name='oidc-complete'),
]
