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

from future import standard_library

standard_library.install_aliases()
import json
import logging
import os
import re
import six
import socket
import sys
import tempfile
import time
import traceback
import zipfile
import validate

from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import render as django_render
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from configobj import ConfigObj, get_extra_values, ConfigObjError
from wsgiref.util import FileWrapper
from webpack_loader.utils import get_static
import django.views.debug

import desktop.conf
import desktop.log.log_buffer

from desktop import appmanager
from desktop.api import massaged_tags_for_json, massaged_documents_for_json, _get_docs
from desktop.auth.backend import is_admin
from desktop.auth.decorators import admin_required, hue_admin_required
from desktop.conf import USE_NEW_EDITOR, HUE_LOAD_BALANCER, get_clusters, ENABLE_CONNECTORS
from desktop.lib import django_mako, fsmanager
from desktop.lib.conf import GLOBAL_CONFIG, BoundConfig, _configs_from_dir
from desktop.lib.config_spec_dump import ConfigSpec
from desktop.lib.django_util import JsonResponse, login_notrequired, render
from desktop.lib.i18n import smart_str
from desktop.lib.paths import get_desktop_root
from desktop.lib.thread_util import dump_traceback
from desktop.lib.view_util import is_ajax
from desktop.log.access import access_log_level, access_warn, AccessInfo
from desktop.log import set_all_debug as _set_all_debug, reset_all_debug as _reset_all_debug, \
                        get_all_debug as _get_all_debug, DEFAULT_LOG_DIR
from desktop.models import Settings, hue_version, _get_apps, UserPreferences
from libsaml.conf import REQUIRED_GROUPS, REQUIRED_GROUPS_ATTRIBUTE
from useradmin.models import get_profile

if sys.version_info[0] > 2:
  from io import StringIO as string_io
  from django.utils.translation import gettext as _
else:
  from StringIO import StringIO as string_io
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()


def is_alive(request):
  return HttpResponse('')

def samlgroup_check(request):
  if 'SAML2Backend' in desktop.auth.forms.get_backend_names():
    if REQUIRED_GROUPS.get():
      try:
        userprofile = get_profile(request.user)
      except:
        return False

      json_data = json.loads(userprofile.json_data)
      if not json_data:
        LOG.info("Empty userprofile data for %s user" % (request.user.username))
        return False

      if not json_data.get('saml_attributes', False):
        LOG.info("Empty saml_attributes data for %s user" % request.user.username)
        return False

      if not json_data['saml_attributes'].get(REQUIRED_GROUPS_ATTRIBUTE.get(), False):
        LOG.info("Missing %s in SAMLResponse for %s user" % (REQUIRED_GROUPS_ATTRIBUTE.get(), request.user.username))
        return False

      # Earlier we had AND condition, It means user has to be there in all given groups.
      # Now we are doing OR condition, which means user must be in one of the given groups.
      saml_group_found = set(REQUIRED_GROUPS.get()).intersection(
                         set(json_data['saml_attributes'].get(REQUIRED_GROUPS_ATTRIBUTE.get())))
      if not saml_group_found:
        LOG.info("User %s not found in required SAML groups, %s" % (request.user.username, REQUIRED_GROUPS.get()))
        return False

      LOG.info("User %s found in the required SAML groups %s" % (request.user.username, ",".join(saml_group_found)))
  return True

def saml_login_headers(request):
  userprofile = get_profile(request.user)
  try:
    userprofile.update_data({'X-Forwarded-For': request.META['HTTP_X_FORWARDED_FOR']})
    userprofile.save()
  except KeyError as e:
    LOG.error('X-FORWARDED-FOR header not found: %s' % smart_str(e))

def hue(request):
  current_app, other_apps, apps_list = _get_apps(request.user, '')
  clusters = list(get_clusters(request.user).values())

  user_permitted = request.session.get('samlgroup_permitted_flag')

  if (not user_permitted) and (not samlgroup_check(request)):
    return render('403.mako', request, {
      'is_embeddable': True
    })

  return render('hue.mako', request, {
    'apps': apps_list,
    'other_apps': other_apps,
    'is_s3_enabled': fsmanager.is_enabled('s3a') and fsmanager.has_access('s3a', request.user),
    'is_adls_enabled': fsmanager.is_enabled('adl') and fsmanager.has_access('adl', request.user),
    'is_ldap_setup': 'desktop.auth.backend.LdapBackend' in desktop.conf.AUTH.BACKEND.get(),
    'leaflet': {
      'layer': desktop.conf.LEAFLET_TILE_LAYER.get(),
      'attribution': desktop.conf.LEAFLET_TILE_LAYER_ATTRIBUTION.get(),
      'map_options': json.dumps(desktop.conf.LEAFLET_MAP_OPTIONS.get()),
      'layer_options': json.dumps(desktop.conf.LEAFLET_TILE_LAYER_OPTIONS.get()),
    },
    'is_demo': desktop.conf.DEMO_ENABLED.get(),
    'banner_message': get_banner_message(request),
    'user_preferences': dict((x.key, x.value) for x in UserPreferences.objects.filter(user=request.user)),
    'cluster': clusters[0]['type'] if clusters else None
  })


def ko_editor(request):
  apps = appmanager.get_apps_dict(request.user)

  return render('ko_editor.mako', request, {
    'apps': apps,
  })


def ko_metastore(request):
  apps = appmanager.get_apps_dict(request.user)

  return render('ko_metastore.mako', request, {
    'apps': apps,
  })


def home(request):
  docs = _get_docs(request.user)

  apps = appmanager.get_apps_dict(request.user)

  return render('home.mako', request, {
    'apps': apps,
    'json_documents': json.dumps(massaged_documents_for_json(docs, request.user)),
    'json_tags': json.dumps(massaged_tags_for_json(docs, request.user)),
  })


def home2(request, is_embeddable=False):
  apps = appmanager.get_apps_dict(request.user)

  return render('home2.mako', request, {
    'apps': apps,
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def catalog(request, is_embeddable=False):
  apps = appmanager.get_apps_dict(request.user)

  return render('catalog.mako', request, {
    'apps': apps,
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def home_embeddable(request):
  return home2(request, True)


def not_found(request):
  return render('404.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def server_error(request):
  return render('500.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def path_forbidden(request):
  return render('403.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def log_js_error(request):
  ai = AccessInfo(request)
  ai.log(level=logging.ERROR, msg='JS ERROR: ' + request.POST.get('jserror', 'Unspecified JS error'))

  return JsonResponse({'status': 0})


def log_analytics(request):
  ai = AccessInfo(request)
  area = request.POST.get('area')
  action = request.POST.get('action')

  if area is not None and action is not None:
    ai.log(level=logging.INFO, msg='UI INTERACTION: ' + area + ' > ' + action)

  return JsonResponse({'status': 0})


@hue_admin_required
@access_log_level(logging.WARN)
def log_view(request):
  """
  We have a log handler that retains the last X characters of log messages.
  If it is attached to the root logger, this view will display that history,
  otherwise it will report that it can't be found.
  """
  hostname = socket.gethostname()
  BUF_SIZE = 32 * 1024

  buffer = []
  log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  log_file = "%s/rungunicornserver.log" % (log_dir)
  prev_log_file = "%s/rungunicornserver.log.1" % (log_dir)

  if log_dir and os.path.exists(log_file):
    log_file_size = os.path.getsize(log_file)

    # log file might get rotated or fresh start of server
    if log_file_size < BUF_SIZE:
      # search the previous file
      if os.path.exists(prev_log_file):
        prev_log_file_size = os.path.getsize(prev_log_file)
        with open(prev_log_file, 'rb') as fh1:
          fh1.seek(prev_log_file_size - BUF_SIZE - log_file_size)
          for l in fh1.readlines(): buffer.append(l)
      # read the current log file
      with open(log_file, 'rb') as fh:
        fh.seek(0)
        for l in fh.readlines(): buffer.append(l)
    else:
      with open(log_file, 'rb') as fh:
        fh.seek(log_file_size - BUF_SIZE)
        for l in fh.readlines(): buffer.append(l)
    return render('logs.mako', request, dict(
        log=buffer,
        query=request.GET.get("q", ""),
        hostname=hostname, is_embeddable=request.GET.get('is_embeddable', False)
      )
    )
  return render('logs.mako', request, dict(
      log=[_("No logs found!")], query='', hostname=hostname, is_embeddable=request.GET.get('is_embeddable', False)
    )
  )


@hue_admin_required
@access_log_level(logging.WARN)
def download_log_view(request):
  """
  Zip up the log buffer and then return as a file attachment.
  """
  # Download 1MB log
  BUF_SIZE = 1024 * 1024

  buffer = []
  log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  log_file = "%s/rungunicornserver.log" % (log_dir)
  prev_log_file = "%s/rungunicornserver.log.1" % (log_dir)

  if log_dir and os.path.exists(log_file):
    log_file_size = os.path.getsize(log_file)

    # log file might get rotated or fresh start of server
    if log_file_size < BUF_SIZE:
      # search the previous file
      if os.path.exists(prev_log_file):
        prev_log_file_size = os.path.getsize(prev_log_file)
        with open(prev_log_file, 'rb') as fh1:
          fh1.seek(prev_log_file_size - BUF_SIZE - log_file_size)
          for l in fh1.readlines(): buffer.append(l)
      # read the current log file
      with open(log_file, 'rb') as fh:
        fh.seek(0)
        for l in fh.readlines(): buffer.append(l)
    else:
      with open(log_file, 'rb') as fh:
        fh.seek(log_file_size - BUF_SIZE)
        for l in fh.readlines(): buffer.append(l)
    try:
      # We want to avoid doing a '\n'.join of the entire log in memory
      # in case it is rather big. So we write it to a file line by line
      # and pass that file to zipfile, which might follow a more efficient path.
      tmp = tempfile.NamedTemporaryFile()
      log_tmp = tempfile.NamedTemporaryFile("w+t") if sys.version_info[0] == 2 else tempfile.NamedTemporaryFile("w+t", encoding='utf-8')
      for l in buffer:
        log_tmp.write(smart_str(l, errors='replace'))
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
    except Exception as e:
      LOG.exception("Couldn't construct zip file to write logs")
      return log_view(request)

  return django_render(request, "logs.mako", dict(log=[_("No logs found.")], is_embeddable=request.GET.get('is_embeddable', False)))


def bootstrap(request):
  """Concatenates bootstrap.js files from all installed Hue apps."""

  # Has some None's for apps that don't have bootsraps.
  all_bootstraps = [
    (app, app.get_bootstrap_file()) for app in appmanager.DESKTOP_APPS if request.user.has_hue_permission(action="access", app=app.name)
  ]

  # Iterator over the streams.
  concatenated = ["\n/* %s */\n%s" % (app.name, b.read()) for app, b in all_bootstraps if b is not None]

  # HttpResponse can take an iteratable as the first argument, which
  # is what happens here.
  return HttpResponse(concatenated, content_type='text/javascript')


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
  resp = b""
  for view in _status_bar_views:
    try:
      r = view(request)
      if r and r.status_code == 200:
        resp += r.content
      else:
        LOG.warning("Failed to execute status_bar view %s" % (view,))
    except:
      LOG.exception("Failed to execute status_bar view %s" % (view,))
  return HttpResponse(resp)


@hue_admin_required
def dump_config(request):
  if not is_admin(request.user):
    return HttpResponse(_("You must be a superuser."))

  return render("dump_config.mako", request, {})


@hue_admin_required
@access_log_level(logging.WARN)
def threads(request):
  """Dumps out server threads. Useful for debugging."""
  out = string_io()
  dump_traceback(file=out)

  if is_ajax(request):
    return HttpResponse(out.getvalue(), content_type="text/plain")
  else:
    return render("threads.mako", request, {'text': out.getvalue(), 'is_embeddable': request.GET.get('is_embeddable', False)})


@hue_admin_required
@access_log_level(logging.WARN)
def memory(request):
  """Dumps out server threads. Useful for debugging."""

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


def global_js_constants(request):
  return HttpResponse(render('global_js_constants.mako', request, {
    'is_s3_enabled': fsmanager.is_enabled('s3a') and fsmanager.has_access('s3a', request.user),
    'leaflet': {
      'layer': desktop.conf.LEAFLET_TILE_LAYER.get(),
      'attribution': desktop.conf.LEAFLET_TILE_LAYER_ATTRIBUTION.get(),
      'map_options': json.dumps(desktop.conf.LEAFLET_MAP_OPTIONS.get()),
      'layer_options': json.dumps(desktop.conf.LEAFLET_TILE_LAYER_OPTIONS.get()),
    }
  }), content_type="application/javascript")


def ace_sql_location_worker(request):
  return HttpResponse(render('ace_sql_location_worker.mako', request, None), content_type="application/javascript")

def ace_sql_syntax_worker(request):
  return HttpResponse(render('ace_sql_syntax_worker.mako', request, None), content_type="application/javascript")

#Redirect to static resources no need for auth. Fails with 401 with Knox.
@login_notrequired
def dynamic_bundle(request, config, bundle_name):
  try:
    static_path = get_static(bundle_name, config.upper())
    webpack_app = config if config != 'default' else 'hue'
    static_path = static_path.replace('static/', 'static/desktop/js/bundles/%s/' % webpack_app)
    return HttpResponseRedirect(static_path)
  except Exception as ex:
    LOG.exception("Failed loading dynamic bundle %s: %s" % (bundle_name, ex))
  return render("404.mako", request, dict(uri=request.build_absolute_uri()), status=404)

def assist_m(request):
  return render('assist_m.mako', request, None)

@login_notrequired
def unsupported(request):
  return render('unsupported.mako', request, None)

def index(request):
  return redirect('desktop_views_hue')

def csrf_failure(request, reason=None):
  """Registered handler for CSRF."""
  access_warn(request, reason)
  return render("403_csrf.mako", request, dict(uri=request.build_absolute_uri()), status=403)

@login_notrequired
def serve_403_error(request, *args, **kwargs):
  """Registered handler for 403. We just return a simple error"""
  access_warn(request, "403 access forbidden")
  return render("403.mako", request, dict(uri=request.build_absolute_uri()), status=403)

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
        tb = traceback.extract_tb(exc_info[2])
        if is_ajax(request):
          tb = '\n'.join(tb.format() if sys.version_info[0] > 2 else [str(t) for t in tb])
        return render("500.mako", request, {'traceback': tb})
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
    return request.GET.get(param, default)

  level = _LOG_LEVELS.get(get("level"), logging.INFO)
  msg = "Untrusted log event from user %s: %s" % (
    request.user,
    get("message", "")[:_MAX_LOG_FRONTEND_EVENT_LENGTH])
  _LOG_FRONTEND_LOGGER.log(level, msg)
  return HttpResponse("")


def commonheader_m(title, section, user, request=None, padding="90px", skip_topbar=False, skip_idle_timeout=False):
  return commonheader(title, section, user, request, padding, skip_topbar, skip_idle_timeout, True)


def commonheader(title, section, user, request=None, padding="90px", skip_topbar=False, skip_idle_timeout=False, is_mobile=False):
  """
  Returns the rendered common header
  """
  current_app, other_apps, apps_list = _get_apps(user, section)

  template = 'common_header.mako'
  if is_mobile:
    template = 'common_header_m.mako'

  return django_mako.render_to_string(template, {
    'current_app': current_app,
    'apps': apps_list,
    'other_apps': other_apps,
    'title': title,
    'section': section,
    'padding': padding,
    'user': user,
    'request': request,
    'skip_topbar': skip_topbar,
    'skip_idle_timeout': skip_idle_timeout,
    'leaflet': {
      'layer': desktop.conf.LEAFLET_TILE_LAYER.get(),
      'attribution': desktop.conf.LEAFLET_TILE_LAYER_ATTRIBUTION.get(),
      'map_options': json.dumps(desktop.conf.LEAFLET_MAP_OPTIONS.get()),
      'layer_options': json.dumps(desktop.conf.LEAFLET_TILE_LAYER_OPTIONS.get()),
    },
    'is_demo': desktop.conf.DEMO_ENABLED.get(),
    'is_ldap_setup': 'desktop.auth.backend.LdapBackend' in desktop.conf.AUTH.BACKEND.get(),
    'is_s3_enabled': fsmanager.is_enabled('s3a') and fsmanager.has_access('s3a', request.user),
    'is_adls_enabled': fsmanager.is_enabled('adl') and fsmanager.has_access('adl', request.user),
    'banner_message': get_banner_message(request)
  })

def get_banner_message(request):
  banner_message = None
  forwarded_host = request.get_host()

  if hasattr(request, 'environ'):
    path_info = request.environ.get("PATH_INFO")
    if path_info.find("/hue") < 0 and path_info.find("accounts/login") < 0 and not request.path.startswith('/api/'):
      url = request.build_absolute_uri("/hue")
      link = '<a href="%s">%s</a>' % (url, url)
      banner_message = _('You are accessing an older version of Hue, please switch to the latest version: %s.') % link
      LOG.warning('User %s is using Hue 3 UI' % request.user.username)

    if HUE_LOAD_BALANCER.get() and HUE_LOAD_BALANCER.get() != [''] and \
      (not forwarded_host or not any(forwarded_host in lb for lb in HUE_LOAD_BALANCER.get())):
      banner_message = _('You are accessing a non-optimized Hue, please switch to one of the available addresses: %s') % \
        (", ".join(['<a href="%s">%s</a>' % (host, host) for host in HUE_LOAD_BALANCER.get()]))
      LOG.warning('User %s is bypassing the load balancer' % request.user.username)

  return banner_message

def commonshare():
  return django_mako.render_to_string("common_share.mako", {})

def commonshare2():
  return django_mako.render_to_string("common_share2.mako", {})

def commonimportexport(request):
  return django_mako.render_to_string("common_import_export.mako", {'request': request})

def login_modal(request):
  return desktop.auth.views.dt_login(request, True)

def is_idle(request):
  return HttpResponse("no!")

def commonfooter_m(request, messages=None):
  return commonfooter(request, messages, True)

def commonfooter(request, messages=None, is_mobile=False):
  """
  Returns the rendered common footer
  """
  if messages is None:
    messages = {}

  hue_settings = Settings.get_settings()

  template = 'common_footer.mako'
  if is_mobile:
    template = 'common_footer_m.mako'

  return django_mako.render_to_string(template, {
    'request': request,
    'messages': messages,
    'version': hue_version(),
    'collect_usage': collect_usage(),
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
    error_list = []
    for module in appmanager.DESKTOP_MODULES:
      # Get the config_validator() function
      try:
        validator = getattr(module.conf, CONFIG_VALIDATOR)
      except AttributeError:
        continue

      if not callable(validator):
        LOG.warning("Auto config validation: %s.%s is not a function" % (module.conf.__name__, CONFIG_VALIDATOR))
        continue

      try:
        for confvar, error in validator(request.user):
          error = {
            'name': confvar if isinstance(confvar, six.string_types) else confvar.get_fully_qualifying_key(),
            'message': error,
          }

          if isinstance(confvar, BoundConfig):
            error['value'] = confvar.get()

          error_list.append(error)
      except Exception as ex:
        LOG.exception("Error in config validation by %s: %s" % (module.nice_name, ex))

    validate_by_spec(error_list)

    _CONFIG_ERROR_LIST = error_list

  if _CONFIG_ERROR_LIST:
    LOG.warning("Errors in config : %s" % _CONFIG_ERROR_LIST)

  return _CONFIG_ERROR_LIST


def validate_by_spec(error_list):
  configspec = None
  try:
    # Generate the spec file
    configspec = generate_configspec()
    config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))
    # Load the .ini files
    conf = load_confs(configspec.name, _configs_from_dir(config_dir))
    # Validate after merging all the confs
    collect_validation_messages(conf, error_list)
  finally:
    if configspec:
      os.remove(configspec.name)

def load_confs(configspecpath, conf_source=None):
  """Loads and merges all of the configurations passed in,
  returning a ConfigObj for the result.

  @param conf_source if not specified, reads conf/ from desktop/conf/. Otherwise should be a generator of ConfigObjs
  """
  if conf_source is None:
    conf_source = _configs_from_dir(get_desktop_root("conf"))

  conf = ConfigObj(configspec=configspecpath)

  for in_conf in conf_source:
    conf.merge(in_conf)
  return conf


def generate_configspec():
  configspec = tempfile.NamedTemporaryFile(delete=False)
  cs = ConfigSpec(configspec)
  cs.generate()
  return configspec


def collect_validation_messages(conf, error_list):
  validator = validate.Validator()
  conf.validate(validator, preserve_errors=True)
  message = []
  cm_extras = {
    'hadoop_hdfs_home': [('hadoop', 'hdfs_clusters', 'default')],
    'hadoop_bin': [('hadoop', 'hdfs_clusters', 'default'), ('hadoop', 'yarn_clusters', 'default'), ('hadoop', 'yarn_clusters', 'ha')],
    'hadoop_mapred_home': [('hadoop', 'yarn_clusters', 'default'), ('hadoop', 'yarn_clusters', 'ha')],
    'hadoop_conf_dir': [('hadoop', 'yarn_clusters', 'default'), ('hadoop', 'yarn_clusters', 'ha')],
    'ssl_cacerts': [('beeswax', 'ssl'), ('impala', 'ssl')],
    'remote_data_dir': [('liboozie',)],
    'shell': [()],
  }

  whitelist_extras = (
      (sections, name)
      for sections, name in get_extra_values(conf)
      if not (name in desktop.conf.APP_BLACKLIST.get() or (name in list(cm_extras.keys()) and sections in cm_extras[name]))
  )

  for sections, name in whitelist_extras:
    the_section = conf
    hierarchy_sections_string = ''

    try:
      parent = conf
      for section in sections:
        the_section = parent[section]
        hierarchy_sections_string += "[" * the_section.depth + section + "]" * the_section.depth + " "
        parent = the_section
    except KeyError as ex:
      LOG.warning("Section %s not found: %s" % (section, str(ex)))

    the_value = ''
    try:
      # the_value may be a section or a value
      the_value = the_section[name]
    except KeyError as ex:
      LOG.warning("Error in accessing Section or Value %s: %s" % (name, str(ex)))

    section_or_value = 'keyvalue'
    if isinstance(the_value, dict):
      # Sections are subclasses of dict
      section_or_value = 'section'

    section_string = hierarchy_sections_string or "top level"
    message.append('Extra %s, %s in the section: %s' % (section_or_value, name, section_string))

  if message:
    error = {
      'name': 'ini configuration',
      'message': ', '.join(message),
    }
    error_list.append(error)


@admin_required
def check_config(request):
  """Check config and view for the list of errors"""

  context = {
    'conf_dir': os.path.realpath(os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))),
    'error_list': _get_config_errors(request, cache=False),
  }

  if request.GET.get('format') == 'json':
    return JsonResponse(context)
  else:
    return render('check_config.mako', request, context, force_template=True)


@admin_required
def check_config_ajax(request):
  """Alert administrators about configuration problems."""

  error_list = _get_config_errors(request)
  if not error_list:
    # Return an empty response, rather than using the mako template, for performance.
    return HttpResponse('')
  else:
    return render('config_alert_dock.mako',
        request,
        dict(error_list=error_list),
        force_template=True
    )


def get_debug_level(request):
  return JsonResponse({'status': 0, 'debug_all': _get_all_debug()})


@require_POST
@admin_required
def set_all_debug(request):
  _set_all_debug()

  return JsonResponse({'status': 0, 'debug_all': True})


@require_POST
@admin_required
def reset_all_debug(request):
  _reset_all_debug()

  return JsonResponse({'status': 0, 'debug_all': False})


# This is a global non-view for inline KO i18n
def _ko(str=""):
  return _(str).replace("'", "\\'")

# This global Mako filtering option, use it with ${ yourvalue | n,antixss }
def antixss(value):
  xss_regex = re.compile(r'<[^>]+>')
  return xss_regex.sub('', value)


def topo(request, location='world'):
  file_path = os.path.join('desktop', 'ext', 'topo', location + '.topo.json')
  response = StreamingHttpResponse(streaming_content=staticfiles_storage.open(file_path))
  #//return settings.STATIC_URL + path
  return response
