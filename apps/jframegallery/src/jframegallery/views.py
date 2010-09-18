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

from django import forms
from django.core import urlresolvers
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError
from desktop.lib.django_forms import DependencyAwareForm
from desktop.lib.django_util import render, MessageException, PopupException, format_preserving_redirect
import os, time

LOG = logging.getLogger(__name__)

def index(request):
  #get all the files in the static directory to make an index
  static = os.path.join(os.path.dirname(__file__), "templates/")
  files = []
  for filename in os.listdir(static):
    if (filename != "index.html"):
      name = filename.replace('.html', '').replace('.mako', '')
      files.append(dict(
        filename=filename,
        name= name.capitalize().replace('.', ' ').replace('_', ' '),
        id=name.replace(' ', '-').replace('.', '-')
      ))
  #render the index, passing along the file list
  return render(
    'index.html', request,
    dict(
      files=files
    ))

def show(request, path):
  post_vars = None
  if (request.POST): post_vars = request.POST.iteritems()
  if request.REQUEST.get('sleep'):
    sleep = int(request.REQUEST.get('sleep'))
    time.sleep(sleep)
  return render(path, request, dict(
    post_vars = post_vars
  ))
  
def flash(request):
  request.flash.put('just a test')
  request.flash.put('another growl test')
  request.flash.put('yet another message to bubble up.')
   
  return render('flash.html', request, dict())

def flash_redirect(request):
  request.flash.put('redirect test')
  return format_preserving_redirect(request, '/jframegallery/')
   
def forwarding(request):
  letter = request.GET.get("letter", "X");
  request.path = urlresolvers.reverse("jframegallery.views.forwarding") + '?letter=Y'
  return render('forwarding.html', request, dict(letter=letter))

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
  return render("forms_with_dependencies.mako", request, dict(form=form, data=data))

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
  assert len(children[0]) == 1
  top = children[0][0]
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
  return render("html-table.treeview.ajax.mako", request, dict(
    tops=tops, show_all=request.GET.get("show_all"), 
    open_paths=paths, request_path=request.path,
    add=add, remove=remove, depth=request.GET.get('depth', 0)))
