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

import StringIO
import json
import logging
import os
import re
import socket
import sys
import tempfile
import time
import traceback
import zipfile
import validate

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.urls import reverse
from wsgiref.util import FileWrapper
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from configobj import ConfigObj, get_extra_values, ConfigObjError

import django.views.debug

from aws.conf import is_enabled as is_s3_enabled, has_s3_access
from azure.conf import is_adls_enabled, has_adls_access

import desktop.conf
import desktop.log.log_buffer

from desktop import appmanager
from desktop.api import massaged_tags_for_json, massaged_documents_for_json, _get_docs
from desktop.auth.backend import is_admin
from desktop.conf import USE_NEW_EDITOR, HUE_LOAD_BALANCER, get_clusters
from desktop.lib import django_mako
from desktop.lib.conf import GLOBAL_CONFIG, BoundConfig, _configs_from_dir
from desktop.lib.config_spec_dump import ConfigSpec
from desktop.lib.django_util import JsonResponse, login_notrequired, render
from desktop.lib.i18n import smart_str
from desktop.lib.metrics.registry import global_registry
from desktop.lib.paths import get_desktop_root
from desktop.lib.thread_util import dump_traceback
from desktop.log.access import access_log_level, access_warn, AccessInfo
from desktop.log import set_all_debug as _set_all_debug, reset_all_debug as _reset_all_debug, get_all_debug as _get_all_debug
from desktop.models import Settings, hue_version, _get_apps, UserPreferences


LOG = logging.getLogger(__name__)


def is_alive(request):
  metrics = global_registry().dump_metrics()

  if 'requests.response-time' in metrics:
    LOG.info('Is Alive Metrics [request.response-time]: %(requests.response-time)s' % metrics)

  return HttpResponse('')


def hue(request):
  current_app, other_apps, apps_list = _get_apps(request.user, '')
  clusters = get_clusters(request.user).values()

  return render('hue.mako', request, {
    'apps': apps_list,
    'other_apps': other_apps,
    'is_s3_enabled': is_s3_enabled() and has_s3_access(request.user),
    'is_adls_enabled': is_adls_enabled() and has_adls_access(request.user),
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
  ai.log(level=logging.INFO, msg='PAGE: ' + request.POST.get('page'))

  return JsonResponse({'status': 0})


@access_log_level(logging.WARN)
def log_view(request):
  """
  We have a log handler that retains the last X characters of log messages.
  If it is attached to the root logger, this view will display that history,
  otherwise it will report that it can't be found.
  """
  if not is_admin(request.user):
    return HttpResponse(_("You must be a superuser."))

  hostname = socket.gethostname()
  l = logging.getLogger()
  for h in l.handlers:
    if isinstance(h, desktop.log.log_buffer.FixedBufferHandler):
      return render('logs.mako', request, dict(log=[l for l in h.buf], query=request.GET.get("q", ""), hostname=hostname, is_embeddable=request.GET.get('is_embeddable', False)))

  return render('logs.mako', request, dict(log=[_("No logs found!")], query='', hostname=hostname, is_embeddable=request.GET.get('is_embeddable', False)))


@access_log_level(logging.WARN)
def download_log_view(request):
  """
  Zip up the log buffer and then return as a file attachment.
  """
  if not is_admin(request.user):
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
          log_tmp.write(smart_str(l, errors='replace') + '\n')
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
        LOG.exception("Couldn't construct zip file to write logs")
        return log_view(request)

  return render_to_response("logs.mako", dict(log=[_("No logs found.")], is_embeddable=request.GET.get('is_embeddable', False)))


def bootstrap(request):
  """Concatenates bootstrap.js files from all installed Hue apps."""

  # Has some None's for apps that don't have bootsraps.
  all_bootstraps = [(app, app.get_bootstrap_file()) for app in appmanager.DESKTOP_APPS if request.user.has_hue_permission(action="access", app=app.name)]

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
  resp = ""
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

def dump_config(request):
  # Note that this requires login (as do most apps).
  show_private = False
  conf_dir = os.path.realpath(os.getenv("HUE_CONF_DIR", get_desktop_root("conf")))

  if not is_admin(request.user):
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
    is_embeddable=request.GET.get('is_embeddable', False),
    apps=apps))

@access_log_level(logging.WARN)
def threads(request):
  """Dumps out server threads. Useful for debugging."""
  out = StringIO.StringIO()
  dump_traceback(file=out)

  if not is_admin(request.user):
    return HttpResponse(_("You must be a superuser."))

  if request.is_ajax():
    return HttpResponse(out.getvalue(), content_type="text/plain")
  else:
    return render("threads.mako", request, {'text': out.getvalue(), 'is_embeddable': request.GET.get('is_embeddable', False)})


@access_log_level(logging.WARN)
def memory(request):
  """Dumps out server threads. Useful for debugging."""
  if not is_admin(request.user):
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


def global_js_constants(request):
  return HttpResponse(render('global_js_constants.mako', request, {
    'is_s3_enabled': is_s3_enabled() and has_s3_access(request.user),
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
    'is_s3_enabled': is_s3_enabled() and has_s3_access(user),
    'is_adls_enabled': is_adls_enabled() and has_adls_access(request.user),
    'banner_message': get_banner_message(request)
  })

def get_banner_message(request):
  banner_message = None
  forwarded_host = request.get_host()

  message = None
  path_info = request.environ.get("PATH_INFO")
  if path_info.find("/hue") < 0 and path_info.find("accounts/login") < 0:
    url = request.build_absolute_uri("/hue")
    link = '<a href="%s" style="color: #FFF; font-weight: bold">%s</a>' % (url, url)
    message = _('You are accessing an older version of Hue, please switch to the latest version: %s.') % link
    LOG.warn('User %s is using Hue 3 UI' % request.user.username)

  if HUE_LOAD_BALANCER.get() and HUE_LOAD_BALANCER.get() != [''] and \
    (not forwarded_host or not any(forwarded_host in lb for lb in HUE_LOAD_BALANCER.get())):
    message = _('You are accessing a non-optimized Hue, please switch to one of the available addresses: %s') % \
      (", ".join(['<a href="%s" style="color: #FFF; font-weight: bold">%s</a>' % (host, host) for host in HUE_LOAD_BALANCER.get()]))
    LOG.warn('User %s is bypassing the load balancer' % request.user.username)

  if message:
    banner_message = '<div style="padding: 4px; text-align: center; background-color: #003F6C; height: 24px; color: #DBE8F1">%s</div>' % message

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
        for confvar, error in validator(request.user):
          error = {
            'name': confvar if isinstance(confvar, str) else confvar.get_fully_qualifying_key(),
            'message': error,
          }

          if isinstance(confvar, BoundConfig):
            error['value'] = confvar.get()

          error_list.append(error)
      except Exception, ex:
        LOG.exception("Error in config validation by %s: %s" % (module.nice_name, ex))

    validate_by_spec(error_list)

    _CONFIG_ERROR_LIST = error_list

  if _CONFIG_ERROR_LIST:
    LOG.warn("Errors in config : %s" % _CONFIG_ERROR_LIST)

  return _CONFIG_ERROR_LIST

def validate_by_spec(error_list):
  try:
    # Generate the spec file
    configspec = generate_configspec()
    config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))
    # Load the .ini files
    conf = load_confs(configspec.name, _configs_from_dir(config_dir))
    # Validate after merging all the confs
    collect_validation_messages(conf, error_list)
  finally:
    os.remove(configspec.name)

def load_confs(configspecpath, conf_source=None):
  """Loads and merges all of the configurations passed in,
  returning a ConfigObj for the result.

  @param conf_source if not specified, reads conf/ from
                     desktop/conf/. Otherwise should be a generator
                     of ConfigObjs
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
    'remote_data_dir': [('liboozie', )],
    'shell': [()]
  }
  whitelist_extras = ((sections, name) for sections, name in get_extra_values(conf) if not (name in desktop.conf.APP_BLACKLIST.get() or (name in cm_extras.keys() and sections in cm_extras[name])))

  for sections, name in whitelist_extras:
    the_section = conf
    hierarchy_sections_string = ''
    try:
      parent = conf
      for section in sections:
        the_section = parent[section]
        hierarchy_sections_string += "[" * the_section.depth + section + "]" * the_section.depth + " "
        parent = the_section
    except KeyError, ex:
      LOG.warn("Section %s not found: %s" % (section, str(ex)))

    the_value = ''
    try:
      # the_value may be a section or a value
      the_value = the_section[name]
    except KeyError, ex:
      LOG.warn("Error in accessing Section or Value %s: %s" % (name, str(ex)))

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


def check_config(request):
  """Check config and view for the list of errors"""
  if not is_admin(request.user):
    return HttpResponse(_("You must be a superuser."))

  context = {
    'conf_dir': os.path.realpath(os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))),
    'error_list': _get_config_errors(request, cache=False),
  }

  if request.GET.get('format') == 'json':
    return JsonResponse(context)
  else:
    return render('check_config.mako', request, context, force_template=True)


def check_config_ajax(request):
  """Alert administrators about configuration problems."""
  if not is_admin(request.user):
    return HttpResponse('')

  error_list = _get_config_errors(request)
  if not error_list:
    # Return an empty response, rather than using the mako template, for performance.
    return HttpResponse('')
  return render('config_alert_dock.mako',
                request,
                dict(error_list=error_list),
                force_template=True)


def get_debug_level(request):
  return JsonResponse({'status': 0, 'debug_all': _get_all_debug()})


@require_POST
def set_all_debug(request):
  if not is_admin(request.user):
    return JsonResponse({'status': 1, 'message': _('You must be a superuser.')})

  _set_all_debug()

  return JsonResponse({'status': 0, 'debug_all': True})


@require_POST
def reset_all_debug(request):
  if not is_admin(request.user):
    return JsonResponse({'status': 1, 'message': _('You must be a superuser.')})

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
