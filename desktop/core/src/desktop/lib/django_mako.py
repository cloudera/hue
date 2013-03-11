#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Adapted from http://code.google.com/p/django-mako/source/browse/trunk/djangomako/shortcuts.py

from django.http import HttpResponse
from desktop.lib import apputil, i18n
import os
import tempfile
from mako.lookup import TemplateLookup, TemplateCollection
import django.template

ENCODING_ERRORS = 'replace'

# Things to automatically import into all template namespaces
IMPORTS=[
  "from desktop.lib.django_mako import url",
  "from django.utils.html import escape"
]

class DesktopLookup(TemplateCollection):
  """
  Template loader for Mako which uses the app-specific
  template directories, and sets up our default options.

  The core desktop template dir is automatically searched for templates.
  """
  def __init__(self):
    self.loaders = {}
    self.module_dir = None
    self.desktop_template_dir = os.path.join(os.path.dirname(__file__), '../templates')

  def _get_loader(self, app):
    if app in self.loaders:
      return self.loaders[app]

    # Lazily find a temp dir for module_dir.
    # This laziness is important because at initialization time
    # we might still be running as root during desktop startup
    # and thus the temp dir would be owned as root, not the
    # unpriveleged user!
    if self.module_dir is None:
      self.module_dir = tempfile.mkdtemp() # TODO(todd) configurable?
    app_module = __import__(app)
    app_dir = os.path.dirname(app_module.__file__)
    app_template_dir = os.path.join(app_dir, 'templates')

    loader = TemplateLookup(directories=[app_template_dir, self.desktop_template_dir],
                            module_directory=os.path.join(self.module_dir, app),
                            output_encoding=i18n.get_site_encoding(),
                            input_encoding=i18n.get_site_encoding(),
                            encoding_errors=ENCODING_ERRORS,
                            default_filters=['unicode', 'escape'], 
                            imports=IMPORTS)
    # TODO(philip): Make a django_aware default filter, that understands
    # django safe strings.  See http://www.makotemplates.org/docs/filtering.html.
    self.loaders[app] = loader
    return loader

  def get_template(self, uri):
    app = apputil.get_current_app()
    if not app:
      raise Exception("no app!")

    real_loader = self._get_loader(app)
    return real_loader.get_template(uri)

lookup = DesktopLookup()


def render_to_string_test(template_name, django_context):
  """
  In tests, send a template rendered signal.  This puts
  the template context into HttpResponse.context when
  you use Client.get().  Django's templating libraries
  do similar work (search for template_rendered).
  """
  from django.test import signals
  signals.template_rendered.send(sender=None, template=template_name, context=django_context)
  return render_to_string_normal(template_name, django_context)

def render_to_string_normal(template_name, django_context):
  data_dict = dict()
  if isinstance(django_context, django.template.Context):
    for d in reversed(django_context.dicts):
      data_dict.update(d)
  else:
    data_dict = django_context

  template = lookup.get_template(template_name)
  data_dict = dict(map(lambda k: (str(k), data_dict.get(k)), data_dict.keys()))
  result = template.render(**data_dict)
  return i18n.smart_unicode(result)

# This variable is overridden in test code.
render_to_string = render_to_string_normal

def render_to_response(template_name, data_dictionary, **kwargs):
  """
  Returns a HttpResponse whose content is filled with the result of calling
  lookup.get_template(args[0]).render with the passed arguments.
  """
  return HttpResponse(render_to_string(template_name, data_dictionary), **kwargs)


def url(view_name, *args, **view_args):
  """URL tag for use in templates - like {% url ... %} in django"""
  from django.core.urlresolvers import reverse
  return reverse(view_name, args=args, kwargs=view_args)
