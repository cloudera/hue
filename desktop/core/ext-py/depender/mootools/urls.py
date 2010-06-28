from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    (r'^depender/', include('depender.urls')),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': 'depender/'})
)
