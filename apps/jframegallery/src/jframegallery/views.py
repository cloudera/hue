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

import logging
import os
import threading
import time

from depender.views import depender as dep
from pygments import highlight
from pygments.filters import NameHighlightFilter
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.token import Name
import yaml

from django import forms
from django.core import urlresolvers
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError
from desktop.lib.django_forms import DependencyAwareForm
from desktop.lib.django_util import render, MessageException, PopupException, format_preserving_redirect, render_json


LOG = logging.getLogger(__name__)

_CWD = os.path.dirname(__file__)

_GALLERY_DIR = 'gallery'

EXTERNAL_PATHS = dict(
  jframe_demos = _GALLERY_DIR + '/JFrame_Demos',
  jframe_containers = '/static/art/'
)

# Lock so that we only have one thread sleeping at a time
_sleep_lock = threading.Lock()

def index(request, path):
  """
  Get all the files in a directory path and make an index
  """
  if request.REQUEST.get('project'):
    return show(request, '')
  
  def is_template(name):
    return os.path.splitext(name)[1] in ('.html', '.mako')
  files = []
  dirs = []
  if is_template(path):
    return show(request, path)
  if path == '':
    path = _GALLERY_DIR
  else:
    path = path.rstrip('/')
  if not path.startswith(_GALLERY_DIR):
    raise Exception("Only paths within the gallery can be viewed.")
  def entry(filename):
    name = os.path.splitext(filename)[0]
    return dict(
      filename=os.path.join(path, filename),
      name=name.capitalize().replace('.', ' ').replace('_', ' '),
      id=name.replace(' ', '-').replace('.', '-')
    )
  for filename in os.listdir(os.path.join(_CWD, 'templates', path)):
    if filename.startswith('.'):
      continue
    if is_template(filename):
      files.append(entry(filename))
    elif os.path.isdir(os.path.join(_CWD, 'templates', path, filename)):
      dirs.append(entry(filename))
  files.sort(lambda x, y: cmp(x['name'], y['name']))
  dirs.sort(lambda x, y: cmp(x['name'], y['name']))
  
  parent_dir = path.split('/')
  parent_dir.pop()
  parent_dir = '/'.join(parent_dir)
  
  return render(
    'index.html', request,
    dict(
      subdir = path != _GALLERY_DIR,
      current_path = path.replace(_GALLERY_DIR, ''),
      parent_dir = parent_dir,
      files=files,
      dirs=dirs
    ))

def show(request, path):
  """
  ``path`` is a template name.

  Parameters accepted:
    sleep       - Will sleep this number of seconds before responding.
  """
  if request.REQUEST.get('project'):
    project = request.REQUEST.get('project')
    project_path = request.REQUEST.get('path')
    path = EXTERNAL_PATHS[project] + project_path;

  post_vars = None
  if request.POST:
    post_vars = request.POST.iteritems()
  sleeper(request)

  return render(
    path,
    request,
    dict(
      post_vars = post_vars,
      get_var = request.REQUEST.get,
      get_list = request.REQUEST.getlist,
      get_request = lambda: request,
      request_path = request.path,
      get_asset_url = get_asset_url
    ))

def get_asset_url(project, path):
  return EXTERNAL_PATHS[project] + path

def view_source(request, path):
  """
  Handle view source requests.
  """
  gallery_name, extension = os.path.splitext(path)
  gallery_name = gallery_name.capitalize().replace('.', ' ').replace('_', ' ')

  # Load the template source
  filename = os.path.join(_CWD, 'templates', _GALLERY_DIR, path)
  try:
    data = format_code(extension, file(filename).read())
  except OSError, ex:
    raise PopupException("Cannot read requested gallery template: %s" % (path,))

  # Load the js references
  js_data = { }         # map of { name: js content }
  yml_file = os.path.splitext(filename)[0] + '.yml'
  if os.path.exists(yml_file):
    yml = yaml.load(file(yml_file))
    try:
      for ref in yml['js-references']:
        try:
          js_pkg, js_comp = ref.split('/')
        except ValueError:
          raise PopupException('Invalid line "%s" in file %s' % (ref, yml_file))
        try:
          file_data = dep.get((js_pkg, js_comp))
          js_data[ref] = format_code('.js', file_data.content)
        except:
          raise PopupException(
            'Cannot locate "%s" package "%s" component' % (js_pkg, js_comp))
    except KeyError, ex:
      LOG.warn('%s does not have a "js-references" section' % (yml_file,))

  return render('source.mako', request, {
    'data': data,
    'name': gallery_name,
    'js_data': js_data
  })


def make_gallery_name(template_name):
  """foo_bar.html -> Foo bar"""
  name = os.path.splitext(template_name)[0]
  return name.capitalize().replace('.', ' ').replace('_', ' ')


_LEXER_MAP = {
  '.html': get_lexer_by_name('django', tabsize=2),
  '.js': get_lexer_by_name('js', tabsize=2),
  '.mako': get_lexer_by_name('mako', tabsize=2),
}

def format_code(extension, code_str):
  """Fix indent and highlight code"""
  try:
    lexer = _LEXER_MAP[extension]
    return highlight(code_str, lexer, HtmlFormatter())
  except KeyError:
    LOG.warn('Cannot find lexer for extension %s' % (extension,))
    return "<div><pre>%s</pre></div>" % (code_str,)


def sleeper(req):

  seconds = False
  if req.REQUEST.get('delay'):
      seconds = int(req.REQUEST.get('delay'))
  if req.REQUEST.get('sleep'):
      seconds = int(req.REQUEST.get('sleep'))

  if seconds:
    # To prevent a DOS, only one thread can sleep at a time
    if not _sleep_lock.acquire(False):
      raise PopupException("Only one sleep request at a time. Please try again")
    try:
      time.sleep(seconds)
    finally:
      _sleep_lock.release()

#
# View handlers for specific gallery pages
#

def flash(request):
  sleeper(request)
  request.flash.put('just a test')
  request.flash.put('another growl test')
  request.flash.put('yet another message to bubble up.')

  return render(os.path.join(_GALLERY_DIR, 'JFrame_Demos/Flash_messages/flash.html'), request, dict())

def flash_redirect(request):
  sleeper(request)
  request.flash.put('redirect test')
  return format_preserving_redirect(request, '/jframegallery/')

def forwarding(request):
  sleeper(request)
  letter = request.GET.get("letter", "X");
  request.path = urlresolvers.reverse("jframegallery.views.forwarding") + '?letter=Y'
  return render(os.path.join(_GALLERY_DIR, 'Hue/forwarding.html'),
                request, dict(letter=letter))

def error_404(request):
  sleeper(request)
  raise Http404("This is a 404.")

def error_500(request):
  sleeper(request)
  raise HttpResponseServerError(HttpResponse("Server erra'"))

def error_real_500(request):
  sleeper(request)
  request.ajax = False
  raise HttpResponseServerError(HttpResponse("Server erra'"))

def error_python(request):
  sleeper(request)
  foo.bar()

def error_redirect(request):
  sleeper(request)
  return HttpResponseRedirect("/test/does_not_exist/404")

def redirect_301(request):
  sleeper(request)
  return HttpResponseRedirect("/jframegallery/gallery/Hue/redirect.html")

def error_message_exception(request):
  sleeper(request)
  raise MessageException("This is a message exception.")

def error_popup_exception(request):
  sleeper(request)
  raise PopupException("This is a popup exception.",
    title="Hey there", detail="Some detail")

class DepForm(DependencyAwareForm):
  cond = forms.ChoiceField(required=True, choices=[ ("a", "alpha"), ("b", "beta") ])
  if_a = forms.CharField(required=False)
  if_b = forms.BooleanField(required=False)

  dependencies = [
    ("cond", "a", "if_a"),
    ("cond", "b", "if_b")
  ]

def forms_with_dependencies(request):
  sleeper(request)
  data = None
  if request.method == "POST":
    form = DepForm(request.POST)
    if form.is_valid():
      data = repr(form.cleaned_data)
  else:
    form = DepForm()
  return render(os.path.join(_GALLERY_DIR, "Hue/forms_with_dependencies.mako"),
                request, dict(form=form, data=data))
