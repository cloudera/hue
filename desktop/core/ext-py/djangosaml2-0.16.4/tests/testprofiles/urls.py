from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^saml2/', include('djangosaml2.urls')),
    url(r'^admin/', admin.site.urls),
]
