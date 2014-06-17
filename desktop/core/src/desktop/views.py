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

import json
import logging
import os
import re
import sys
import tempfile
import time
import traceback
import zipfile

from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
import django.views.debug

import desktop.conf
import desktop.log.log_buffer

from desktop.api import massaged_tags_for_json, massaged_documents_for_json,\
  _get_docs
from desktop.lib import django_mako
from desktop.lib.conf import GLOBAL_CONFIG
from desktop.lib.django_util import login_notrequired, render_json, render
from desktop.lib.i18n import smart_str
from desktop.lib.paths import get_desktop_root
from desktop.log.access import access_log_level, access_warn
from desktop.models import UserPreferences, Settings
from desktop import appmanager


LOG = logging.getLogger(__name__)


def home(request):
  docs = _get_docs(request.user)

  apps = appmanager.get_apps_dict(request.user)

  return render('home.mako', request, {
    'apps': apps,
    'json_documents': json.dumps(massaged_documents_for_json(docs, request.user)),
    'json_tags': json.dumps(massaged_tags_for_json(docs, request.user)),
    'tours_and_tutorials': Settings.get_settings().tours_and_tutorials
  })


@access_log_level(logging.WARN)
def log_view(request):
  """
  We have a log handler that retains the last X characters of log messages.
  If it is attached to the root logger, this view will display that history,
  otherwise it will report that it can't be found.
  """
  if not request.user.is_superuser:
    return HttpResponse(_("You must be a superuser."))

  l = logging.getLogger()
  for h in l.handlers:
    if isinstance(h, desktop.log.log_buffer.FixedBufferHandler):
      return render('logs.mako', request, dict(log=[l for l in h.buf], query=request.GET.get("q", "")))

  return render('logs.mako', request, dict(log=[_("No logs found!")]))

@access_log_level(logging.WARN)
def download_log_view(request):
  """
  Zip up the log buffer and then return as a file attachment.
  """
  if not request.user.is_superuser:
    return HttpResponse(_("You must be a superuser."))

  l = logging.getLogger()
  for h in l.handlers:
    if isinstance(h, desktop.log.log_buffer.FixedBufferHandler):
      try:
        # We want to avoid doing a '\n'.join of the entire log in memory
        # in case it is rather big. So we write it to a file line by line
        # and pass that file to zipfile, which might follow a more efficient path.
        tmp = tempfile.NamedTemporaryFile()
        log_tmp = tempfile.NamedTemporaryFile("w+t")
        for l in h.buf:
          log_tmp.write(smart_str(l) + '\n')
        # This is not just for show - w/out flush, we often get truncated logs
        log_tmp.flush()
        t = time.time()

        zip = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
        zip.write(log_tmp.name, "hue-logs/hue-%s.log" % t)
        zip.close()
        length = tmp.tell()

        # if we don't seek to start of file, no bytes will be written
        tmp.seek(0)
        wrapper = FileWrapper(tmp)
        response = HttpResponse(wrapper, content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=hue-logs-%s.zip' % t
        response['Content-Length'] = length
        return response
      except Exception, e:
        logging.exception("Couldn't construct zip file to write logs to: %s") % e
        return log_view(request)

  return render_to_response("logs.mako", dict(log=[_("No logs found.")]))


@access_log_level(logging.DEBUG)
def prefs(request, key=None):
  """Get or set preferences."""
  if key is None:
    d = dict( (x.key, x.value) for x in UserPreferences.objects.filter(user=request.user))
    return render_json(d)
  else:
    if "set" in request.REQUEST:
      try:
        x = UserPreferences.objects.get(user=request.user, key=key)
      except UserPreferences.DoesNotExist:
        x = UserPreferences(user=request.user, key=key)
      x.value = request.REQUEST["set"]
      x.save()
      return render_json(True)
    if "delete" in request.REQUEST:
      try:
        x = UserPreferences.objects.get(user=request.user, key=key)
        x.delete()
        return render_json(True)
      except UserPreferences.DoesNotExist:
        return render_json(False)
    else:
      try:
        x = UserPreferences.objects.get(user=request.user, key=key)
        return render_json(x.value)
      except UserPreferences.DoesNotExist:
        return render_json(None)


def bootstrap(request):
  """Concatenates bootstrap.js files from all installed Hue apps."""

  # Has some None's for apps that don't have bootsraps.
  all_bootstraps = [ (app, app.get_bootstrap_file()) for app in appmanager.DESKTOP_APPS if request.user.has_hue_permission(action="access", app=app.name) ]

  # Iterator over the streams.
  concatenated = [ "\n/* %s */\n%s" % (app.name, b.read()) for app, b in all_bootstraps if b is not None ]

  # HttpResponse can take an iteratable as the first argument, which
  # is what happens here.
  return HttpResponse(concatenated, mimetype='text/javascript')


_status_bar_views = []
def register_status_bar_view(view):
  global _status_bar_views
  _status_bar_views.append(view)


@access_log_level(logging.DEBUG)
def status_bar(request):
  """
  Concatenates multiple views together to build up a "status bar"/"status_bar".
  These views are registered using register_status_bar_view above.
  """
  resp = ""
  for view in _status_bar_views:
    try:
      r = view(request)
      if r.status_code == 200:
        resp += r.content
      else:
        LOG.warning("Failed to execute status_bar view %s" % (view,))
    except:
      LOG.exception("Failed to execute status_bar view %s" % (view,))
  return HttpResponse(resp)

def dump_config(request):
  # Note that this requires login (as do most apps).
  show_private = False
  conf_dir = os.path.realpath(os.getenv("HUE_CONF_DIR", get_desktop_root("conf")))

  if not request.user.is_superuser:
    return HttpResponse(_("You must be a superuser."))

  if request.GET.get("private"):
    show_private = True

  apps = sorted(appmanager.DESKTOP_MODULES, key=lambda app: app.name)
  apps_names = [app.name for app in apps]
  top_level = sorted(GLOBAL_CONFIG.get().values(), key=lambda obj: apps_names.index(obj.config.key))

  return render("dump_config.mako", request, dict(
    show_private=show_private,
    top_level=top_level,
    conf_dir=conf_dir,
    apps=apps))

if sys.version_info[0:2] <= (2,4):
  def _threads():
    import threadframe
    return threadframe.dict().iteritems()
else:
  def _threads():
    return sys._current_frames().iteritems()

@access_log_level(logging.WARN)
def threads(request):
  """Dumps out server threads.  Useful for debugging."""
  if not request.user.is_superuser:
    return HttpResponse(_("You must be a superuser."))

  out = []
  for thread_id, stack in _threads():
    out.append("Thread id: %s" % thread_id)
    for filename, lineno, name, line in traceback.extract_stack(stack):
      out.append("  %-20s %s(%d)" % (name, filename, lineno))
      out.append("    %-80s" % (line))
    out.append("")
  return HttpResponse("\n".join(out), content_type="text/plain")

@access_log_level(logging.WARN)
def memory(request):
  """Dumps out server threads.  Useful for debugging."""
  if not request.user.is_superuser:
    return HttpResponse(_("You must be a superuser."))

  if not hasattr(settings, 'MEMORY_PROFILER'):
    return HttpResponse(_("You must enable the memory profiler via the memory_profiler config in the hue.ini."))

  # type, from, to, index
  command_order = {
    'type': 0,
    'from': 1,
    'to': 2,
    'index': 3
  }
  default_command = [None, None, None, None]
  commands = []

  for item in request.GET:
    res = re.match(r'(?P<command>\w+)\.(?P<count>\d+)', item)
    if res:
      d = res.groupdict()
      count = int(d['count'])
      command = str(d['command'])
      while len(commands) <= count:
        commands.append(default_command[:])
      commands[count][command_order.get(command)] = request.GET.get(item)

  heap = settings.MEMORY_PROFILER.heap()
  for command in commands:
    if command[0] is not None:
      heap = getattr(heap, command[0])
    if command[1] is not None and command[2] is not None:
      heap = heap[int(command[1]):int(command[2])]
    if command[3] is not None:
      heap = heap[int(command[3])]
  return HttpResponse(str(heap), content_type="text/plain")

def jasmine(request):
  return render('jasmine.mako', request, None)

@login_notrequired
def unsupported(request):
  return render('unsupported.mako', request, None)

def index(request):
  if request.user.is_superuser and request.COOKIES.get('hueLandingPage') != 'home':
    return redirect(reverse('about:index'))
  else:
    return home(request)

def serve_404_error(request, *args, **kwargs):
  """Registered handler for 404. We just return a simple error"""
  access_warn(request, "404 not found")
  return render("404.mako", request, dict(uri=request.build_absolute_uri()), status=404)

def serve_500_error(request, *args, **kwargs):
  """Registered handler for 500. We use the debug view to make debugging easier."""
  try:
    exc_info = sys.exc_info()
    if exc_info:
      if desktop.conf.HTTP_500_DEBUG_MODE.get() and exc_info[0] and exc_info[1]:
        # If (None, None, None), default server error describing why this failed.
        return django.views.debug.technical_500_response(request, *exc_info)
      else:
        # Could have an empty traceback
        return render("500.mako", request, {'traceback': traceback.extract_tb(exc_info[2])})
    else:
      # exc_info could be empty
      return render("500.mako", request, {})
  finally:
    # Fallback to default 500 response if ours fails
    # Will end up here:
    #   - Middleware or authentication backends problems
    #   - Certain missing imports
    #   - Packaging and install issues
    pass

_LOG_LEVELS = {
  "critical": logging.CRITICAL,
  "error": logging.ERROR,
  "warning": logging.WARNING,
  "info": logging.INFO,
  "debug": logging.DEBUG
}

_MAX_LOG_FRONTEND_EVENT_LENGTH = 1024

_LOG_FRONTEND_LOGGER = logging.getLogger("desktop.views.log_frontend_event")

@login_notrequired
def log_frontend_event(request):
  """
  Logs arguments to server's log.  Returns an
  empty string.

  Parameters (specified via either GET or POST) are
  "logname", "level" (one of "debug", "info", "warning",
  "error", or "critical"), and "message".
  """
  def get(param, default=None):
    return request.REQUEST.get(param, default)

  level = _LOG_LEVELS.get(get("level"), logging.INFO)
  msg = "Untrusted log event from user %s: %s" % (
    request.user,
    get("message", "")[:_MAX_LOG_FRONTEND_EVENT_LENGTH])
  _LOG_FRONTEND_LOGGER.log(level, msg)
  return HttpResponse("")

def who_am_i(request):
  """
  Returns username and FS username, and optionally sleeps.
  """
  try:
    sleep = float(request.REQUEST.get("sleep") or 0.0)
  except ValueError:
    sleep = 0.0
  time.sleep(sleep)
  return HttpResponse(request.user.username + "\t" + request.fs.user + "\n")

def commonheader(title, section, user, padding="90px"):
  """
  Returns the rendered common header
  """
  current_app = None
  other_apps = []
  if user.is_authenticated():
    apps = appmanager.get_apps(user)
    apps_list = appmanager.get_apps_dict(user)
    for app in apps:
      if app.display_name not in [
          'beeswax', 'impala', 'pig', 'jobsub', 'jobbrowser', 'metastore', 'hbase', 'sqoop', 'oozie', 'filebrowser',
          'useradmin', 'search', 'help', 'about', 'zookeeper', 'proxy', 'rdbms', 'spark', 'indexer', 'security']:
        other_apps.append(app)
      if section == app.display_name:
        current_app = app
  else:
    apps_list = []

  return django_mako.render_to_string("common_header.mako", {
    'current_app': current_app,
    'apps': apps_list,
    'other_apps': other_apps,
    'title': title,
    'section': section,
    'padding': padding,
    'user': user,
    'is_demo': desktop.conf.DEMO_ENABLED.get()
  })

def commonfooter(messages=None):
  """
  Returns the rendered common footer
  """
  if messages is None:
    messages = {}

  hue_settings = Settings.get_settings()

  return django_mako.render_to_string("common_footer.mako", {
    'messages': messages,
    'version': settings.HUE_DESKTOP_VERSION,
    'collect_usage': collect_usage(),
    'tours_and_tutorials': hue_settings.tours_and_tutorials
  })


def collect_usage():
  return desktop.conf.COLLECT_USAGE.get() and Settings.get_settings().collect_usage


# If the app's conf.py has a config_validator() method, call it.
CONFIG_VALIDATOR = 'config_validator'

#
# Cache config errors because (1) they mostly don't go away until restart,
# and (2) they can be costly to compute. So don't stress the system just because
# the dock bar wants to refresh every n seconds.
#
# The actual viewing of all errors may choose to disregard the cache.
#
_CONFIG_ERROR_LIST = None

def _get_config_errors(request, cache=True):
  """Returns a list of (confvar, err_msg) tuples."""
  global _CONFIG_ERROR_LIST

  if not cache or _CONFIG_ERROR_LIST is None:
    error_list = [ ]
    for module in appmanager.DESKTOP_MODULES:
      # Get the config_validator() function
      try:
        validator = getattr(module.conf, CONFIG_VALIDATOR)
      except AttributeError:
        continue

      if not callable(validator):
        LOG.warn("Auto config validation: %s.%s is not a function" %
                 (module.conf.__name__, CONFIG_VALIDATOR))
        continue

      try:
        error_list.extend(validator(request.user))
      except Exception, ex:
        LOG.exception("Error in config validation by %s: %s" % (module.nice_name, ex))
    _CONFIG_ERROR_LIST = error_list
  return _CONFIG_ERROR_LIST


def check_config(request):
  """Check config and view for the list of errors"""
  if not request.user.is_superuser:
    return HttpResponse(_("You must be a superuser."))

  conf_dir = os.path.realpath(os.getenv("HUE_CONF_DIR", get_desktop_root("conf")))
  return render('check_config.mako', request, {
                  'error_list': _get_config_errors(request, cache=False),
                  'conf_dir': conf_dir
              },
              force_template=True)


def check_config_ajax(request):
  """Alert administrators about configuration problems."""
  if not request.user.is_superuser:
    return HttpResponse('')

  error_list = _get_config_errors(request)
  if not error_list:
    # Return an empty response, rather than using the mako template, for performance.
    return HttpResponse('')
  return render('config_alert_dock.mako',
                request,
                dict(error_list=error_list),
                force_template=True)
