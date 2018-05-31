from django.conf.urls import patterns, url, include
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('views',
    url(r'^$', 'index'),
    url(r'^oidc/', include('oidc_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
