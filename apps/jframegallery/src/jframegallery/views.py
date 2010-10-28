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

# Lock so that we only have one thread sleeping at a time
_sleep_lock = threading.Lock()


def index(request):
  """
  Get all the files in the gallery directory to make an index
  """
  def is_template(name):
    return os.path.splitext(name)[1] in ('.html', '.mako')

  static = os.path.join(_CWD, "templates", _GALLERY_DIR)
  files = []
  for filename in filter(is_template, os.listdir(static)):
    # Exclude hidden files
    if filename.startswith('.'):
      continue
    name = os.path.splitext(filename)[0]
    files.append(dict(
      filename=os.path.join(_GALLERY_DIR, filename),
      name=name.capitalize().replace('.', ' ').replace('_', ' '),
      id=name.replace(' ', '-').replace('.', '-')
    ))
  files.sort(lambda x, y: cmp(x['name'], y['name']))
  # render the index, passing along the file list
  return render(
    'index.html', request,
    dict(
      files=files
    ))

def show(request, path):
  """
  ``path`` is a template name.

  Parameters accepted:
    sleep       - Will sleep this number of seconds before responding.
  """
  post_vars = None
  if request.POST:
    post_vars = request.POST.iteritems()
  if request.REQUEST.get('sleep'):
    sleep = int(request.REQUEST.get('sleep'))
    do_sleep(sleep)

  return render(
    os.path.join(_GALLERY_DIR, path),
    request,
    dict(
      post_vars = post_vars,
      get_var = request.REQUEST.get,
      get_list = request.REQUEST.getlist,
      request_path = request.path
    ))

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


def do_sleep(seconds):
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
  request.flash.put('just a test')
  request.flash.put('another growl test')
  request.flash.put('yet another message to bubble up.')

  return render(os.path.join(_GALLERY_DIR, 'flash.html'), request, dict())

def flash_redirect(request):
  request.flash.put('redirect test')
  return format_preserving_redirect(request, '/jframegallery/')

def forwarding(request):
  letter = request.GET.get("letter", "X");
  request.path = urlresolvers.reverse("jframegallery.views.forwarding") + '?letter=Y'
  return render(os.path.join(_GALLERY_DIR, 'forwarding.html'),
                request, dict(letter=letter))

def error_404(request):
  raise Http404("This is a 404.")

def error_500(request):
  raise HttpResponseServerError(HttpResponse("Server erra'"))

def error_real_500(request):
  request.ajax = False
  raise HttpResponseServerError(HttpResponse("Server erra'"))

def error_python(request):
  foo.bar()

def error_redirect(request):
  return HttpResponseRedirect("/test/does_not_exist/404")

def redirect_301(request):
  return HttpResponseRedirect("/jframegallery/redirect.html")

def error_message_exception(request):
  raise MessageException("This is a message exception.")

def error_popup_exception(request):
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
  data = None
  if request.method == "POST":
    form = DepForm(request.POST)
    if form.is_valid():
      data = repr(form.cleaned_data)
  else:
    form = DepForm()
  return render(os.path.join(_GALLERY_DIR, "forms_with_dependencies.mako"),
                request, dict(form=form, data=data))

class PsLine(object):
  def __init__(self, user, pid, ppid, pgid, cputime, command):
    self.user = user
    self.pid = int(pid)
    self.ppid = int(ppid)
    self.pgid = int(pgid)
    self.cputime = cputime
    self.command = command
    self.children = []

def pstree(request):
  """
  Draws 'pstree' by using output from ps command.

  GET arguments:
    subtree: show only pids below this tree
    show_all: expand the entire tree
    paths: slash-separated paths that are expanded
      (can be specified multiple times)

  """
  import subprocess
  import urllib
  import re

  if request.REQUEST.get('sleep'):
    sleep = int(request.REQUEST.get('sleep'))
    time.sleep(sleep)

  # Call ps
  p = subprocess.Popen(args=["ps", "-axwwo", "user,pid,ppid,pgid,cputime,command"], stdout=subprocess.PIPE)

  children = {}
  first = True
  if "subtree" in request.GET:
    subtree = long(request.GET.get("subtree"))
  else:
    subtree = None
  subtree_top = None

  # Parse in the data
  for row in p.stdout:
    if first:
      # skip header line
      first = False
      continue
    data = user, pid, ppid, pgid, cputime, command = re.split("\s+", row.rstrip(), 5)
    ps = PsLine(*data)
    if ps.pid == subtree:
      subtree_top = ps
    if ps.ppid in children:
      children[ps.ppid].append(ps)
    else:
      children[ps.ppid] = [ps]

  # Utility method to create the tree
  def fill(root, current_path):
    root.path = current_path + str(root.pid)
    root.children = children.get(root.pid, [])
    for child in root.children:
      fill(child, root.path + "/")

  # Start with init and create the tree
  # Note that on linux, kthreadd is also a child of pid 0
  top_list = filter(lambda x: 'init' in x.command, children[0])
  assert len(top_list) == 1
  top = top_list[0]
  fill(top, "/")
  tops = [top]

  # If we're only interested in a subtree, pick that out explicitly
  if subtree_top:
    tops = subtree_top.children

  # Methods to manipulate the extant paths list; used by the template.
  def add(p):
    paths = list(request.GET.getlist("paths")) # make a copy
    paths.append(p)
    query = [urllib.urlencode([("paths", x)]) for x in paths]
    if subtree:
      query.append('subtree=' + str(subtree))
    return request.path + "?" + "&".join(query)
  def remove(p):
    paths = list(request.GET.getlist("paths")) # make a copy
    paths.remove(p)
    query = [urllib.urlencode([("paths", x)]) for x in paths]
    if subtree:
      query.append('subtree=' + str(subtree))
    return request.path + "?" + "&".join(query)

  paths = request.GET.getlist("paths")
  return render(
    os.path.join(_GALLERY_DIR, "html-table.treeview.ajax.mako"),
    request,
    dict(
      tops=tops, show_all=request.GET.get("show_all"),
      open_paths=paths, request_path=request.path,
      add=add, remove=remove, depth=request.GET.get('depth', 0)
    ))


def autocomplete(request):
  items = [
    'Afghanistan', 'Aland_Islands', 'Albania', 'Algeria',
    'American_Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica',
    'Antigua_And_Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia',
    'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh',
    'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda',
    'Bhutan', 'Bolivia', 'Bosnia_And_Herzegovina', 'Botswana',
    'Bouvet_Island', 'Brazil', 'British_Indian_Ocean_Territory',
    'Brunei_Darussalam', 'Bulgaria', 'Burkina_Faso', 'Burundi',
    'Cambodia', 'Cameroon', 'Canada', 'Cape_Verde', 'Cayman_Islands',
    'Central_African_Republic', 'Chad', 'Chile', 'China',
    'Christmas_Island', 'Cocos_(Keeling)_Islands', 'Colombia', 'Comoros',
    'Congo', 'Congo, The_Democratic_Republic_Of_The', 'Cook_Islands',
    'Costa_Rica', 'Cote_D\'ivoire', 'Croatia', 'Cuba', 'Cyprus',
    'Czech_Republic', 'Denmark', 'Djibouti', 'Dominica',
    'Dominican_Republic', 'Ecuador', 'Egypt', 'El_Salvador',
    'Equatorial_Guinea', 'Eritrea', 'Estonia', 'Ethiopia',
    'Falkland_Islands_(Malvinas)', 'Faroe_Islands', 'Fiji', 'Finland',
    'France', 'French_Guiana', 'French_Polynesia',
    'French_Southern_Territories', 'Gabon', 'Gambia', 'Georgia',
    'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada',
    'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea',
    'Guinea-Bissau', 'Guyana', 'Haiti',
    'Heard_Island_And_Mcdonald_Islands', 'Holy_See_(Vatican_City_State)',
    'Honduras', 'Hong_Kong', 'Hungary', 'Iceland', 'India', 'Indonesia',
    'Iran, Islamic_Republic_Of', 'Iraq', 'Ireland', 'Isle_Of_Man',
    'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey', 'Jordan',
    'Kazakhstan', 'Kenya', 'Kiribati',
    'Korea, Democratic_People\'s_Republic_Of', 'Korea, Republic_Of', 'Kuwait',
    'Kyrgyzstan', 'Lao_People\'s_Democratic_Republic', 'Latvia',
    'Lebanon', 'Lesotho', 'Liberia', 'Libyan_Arab_Jamahiriya',
    'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao',
    'Macedonia, The_Former_Yugoslav_Republic_Of', 'Madagascar', 'Malawi',
    'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall_Islands',
    'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico',
    'Micronesia, Federated_States_Of', 'Moldova, Republic_Of', 'Monaco',
    'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique',
    'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands',
    'Netherlands_Antilles', 'New_Caledonia', 'New_Zealand', 'Nicaragua',
    'Niger', 'Nigeria', 'Niue', 'Norfolk_Island',
    'Northern_Mariana_Islands', 'Norway', 'Oman', 'Pakistan', 'Palau',
    'Palestinian_Territory, Occupied', 'Panama', 'Papua_New_Guinea',
    'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal',
    'Puerto_Rico', 'Qatar', 'Reunion', 'Romania', 'Russian_Federation',
    'Rwanda', 'Saint_Helena', 'Saint_Kitts_And_Nevis', 'Saint_Lucia',
    'Saint_Pierre_And_Miquelon', 'Saint_Vincent_And_The_Grenadines',
    'Samoa', 'San_Marino', 'Sao_Tome_And_Principe', 'Saudi_Arabia',
    'Senegal', 'Serbia', 'Seychelles', 'Sierra_Leone', 'Singapore',
    'Slovakia', 'Slovenia', 'Solomon_Islands', 'Somalia', 'South_Africa',
    'South_Georgia_And_The_South_Sandwich_Islands', 'Spain', 'Sri_Lanka',
    'Sudan', 'Suriname', 'Svalbard_And_Jan_Mayen', 'Swaziland', 'Sweden',
    'Switzerland', 'Syrian_Arab_Republic', 'Taiwan, Province_Of_China',
    'Tajikistan', 'Tanzania, United_Republic_Of', 'Thailand', 'Timor-Leste',
    'Togo', 'Tokelau', 'Tonga', 'Trinidad_And_Tobago', 'Tunisia', 'Turkey',
    'Turkmenistan', 'Turks_And_Caicos_Islands', 'Tuvalu', 'Uganda', 'Ukraine',
    'United_Arab_Emirates', 'United_Kingdom', 'United_States',
    'United_States_Minor_Outlying_Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu',
    'Venezuela', 'Viet_Nam', 'Virgin_Islands, British', 'Virgin_Islands, U.S.',
    'Wallis_And_Futuna', 'Western_Sahara', 'Yemen', 'Zambia', 'Zimbabwe'
    ]
  term = request.REQUEST.get('term').lower()
  terms = [item for item in items if item.lower().startswith(term)]
  return render_json(terms)
