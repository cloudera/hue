#!/usr/bin/env python

from django.conf.urls.defaults import patterns, url
import os

urlpatterns = patterns('',
  url(r'^build$', 'depender.views.build'),
  url(r'^test$', 'depender.views.test'),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': os.path.join(os.path.dirname(__file__), '..', '..', '..', 'styles')}),
)
