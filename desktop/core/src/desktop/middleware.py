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

from __future__ import absolute_import

import re
import json
import time
import socket
import inspect
import logging
import os.path
import tempfile
import mimetypes
import traceback
from builtins import object
from urllib.parse import quote, urlparse

import kerberos
import django.db
import django_prometheus
import django.views.static
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import BACKEND_SESSION_KEY, REDIRECT_FIELD_NAME, authenticate, load_backend, login
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core import exceptions
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _

import desktop.views
from dashboard.conf import IS_ENABLED as DASHBOARD_ENABLED
from desktop import appmanager, metrics
from desktop.auth.backend import ensure_has_a_group, find_or_create_user, is_admin, knox_login_headers, rewrite_user
from desktop.conf import (
  AUDIT_EVENT_LOG_DIR,
  AUTH,
  CUSTOM_CACHE_CONTROL,
  DJANGO_DEBUG_MODE,
  ENABLE_PROMETHEUS,
  HTTP_ALLOWED_METHODS,
  HUE_LOAD_BALANCER,
  KNOX,
  METRICS,
  REDIRECT_WHITELIST,
  SECURE_CONTENT_SECURITY_POLICY,
  SERVER_USER,
  has_connectors,
  is_gunicorn_report_enabled,
)
from desktop.context_processors import get_app_name
from desktop.lib import apputil, fsmanager, i18n
from desktop.lib.django_util import JsonResponse, render, render_json
from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.metrics import global_registry
from desktop.lib.view_util import is_ajax
from desktop.log import get_audit_logger
from desktop.log.access import access_log, access_warn, log_page_hit
from hadoop import cluster
from libsaml.conf import CDP_LOGOUT_URL
from useradmin.models import User

LOG = logging.getLogger()

MIDDLEWARE_HEADER = "X-Hue-Middleware-Response"

# Views inside Django that don't require login
# (see LoginAndPermissionMiddleware)
DJANGO_VIEW_AUTH_WHITELIST = [
  django.views.static.serve,
  desktop.views.is_alive,
]

if ENABLE_PROMETHEUS.get():
  DJANGO_VIEW_AUTH_WHITELIST.append(django_prometheus.exports.ExportToDjangoView)

HUE_LB_HOSTS = [urlparse(hue_lb).netloc for hue_lb in HUE_LOAD_BALANCER.get()] if HUE_LOAD_BALANCER.get() else []


class AjaxMiddleware(MiddlewareMixin):
  """
  Middleware that augments request to set request.ajax
  for either is_ajax() (looks at HTTP headers) or ?format=json
  GET parameters.
  """
  def process_request(self, request):
    request.ajax = is_ajax(request) or request.GET.get("format", "") == "json"
    return None


class ExceptionMiddleware(MiddlewareMixin):
  """
  If exceptions know how to render themselves, use that.
  """
  def process_exception(self, request, exception):
    tb = traceback.format_exc()
    logging.info("Processing exception: %s: %s" % (
      i18n.smart_str(exception), i18n.smart_str(tb))
    )

    if isinstance(exception, PopupException):
      return exception.response(request)

    if isinstance(exception, StructuredException):
      if request.ajax:
        response = render_json(exception.response_data)
        response[MIDDLEWARE_HEADER] = 'EXCEPTION'
        response.status_code = getattr(exception, 'error_code', 500)
        return response
      else:
        response = render("error.mako", request, {
          'error': exception.response_data.get("message"),
          'is_embeddable': request.GET.get('is_embeddable', False),
        })
        response.status_code = getattr(exception, 'error_code', 500)
        return response

    return None


class ClusterMiddleware(MiddlewareMixin):
  """
  Manages setting request.fs and request.jt
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    Sets request.fs and request.jt on every request to point to the configured filesystem.
    """
    request.fs_ref = request.GET.get('fs', view_kwargs.get('fs', 'default'))
    if "fs" in view_kwargs:
      del view_kwargs["fs"]

    request.fs = None

    if request.user.is_authenticated:
      request.fs = fsmanager.get_filesystem(request.fs_ref)

      if request.fs is not None:
        request.fs.setuser(request.user.username)
      else:
        LOG.warning("request.fs user was not set")
    else:
      LOG.warning("request.fs was not set for anonymous user")

    # Deprecated
    request.jt = None


class NotificationMiddleware(MiddlewareMixin):
  """
  Manages setting request.info and request.error
  """
  def process_view(self, request, view_func, view_args, view_kwargs):

    def message(title, detail=None):
      if detail is None:
        detail = ''
      else:
        detail = '<br/>%s' % detail
      return '%s %s' % (title, detail)

    def info(title, detail=None):
      messages.info(request, message(title, detail))

    def error(title, detail=None):
      messages.error(request, message(title, detail))

    def warn(title, detail=None):
      messages.warning(request, message(title, detail))

    request.info = info
    request.error = error
    request.warn = warn


class AppSpecificMiddleware(object):
  @classmethod
  def augment_request_with_app(cls, request, view_func):
    """Inject the app name into the request for use in later-stage middleware"""
    if not hasattr(request, "_desktop_app"):
      module = inspect.getmodule(view_func)
      request._desktop_app = apputil.get_app_for_module(module)
      if not request._desktop_app and not module.__name__.startswith('django.'):
        logging.debug("no app for view func: %s in %s" % (view_func, module))

  def __init__(self):
    self.middlewares_by_app = {}
    for app in appmanager.DESKTOP_APPS:
      self.middlewares_by_app[app.name] = self._load_app_middleware(app)

  def _get_middlewares(self, app, type):
    return self.middlewares_by_app.get(app, {}).get(type, [])

  def process_view(self, request, view_func, view_args, view_kwargs):
    self.augment_request_with_app(request, view_func)
    if not request._desktop_app:
      return None

    # Run the middlewares
    ret = None
    for middleware in self._get_middlewares(request._desktop_app, 'view'):
      ret = middleware(request, view_func, view_args, view_kwargs)
      if ret:
        return ret  # Short circuit
    return ret

  def process_response(self, request, response):
    # We have the app that we stuffed in there
    if not hasattr(request, '_desktop_app'):
      logging.debug("No desktop_app known for request.")
      return response

    for middleware in reversed(self._get_middlewares(request._desktop_app, 'response')):
      response = middleware(request, response)
    return response

  def process_exception(self, request, exception):
    # We have the app that we stuffed in there
    if not hasattr(request, '_desktop_app'):
      logging.debug("No desktop_app known for exception.")
      return None

    # Run the middlewares
    ret = None
    for middleware in self._get_middlewares(request._desktop_app, 'exception'):
      ret = middleware(request, exception)
      if ret:
        return ret  # short circuit
    return ret

  def _load_app_middleware(cls, app):
    app_settings = app.settings
    if not app_settings:
      return
    mw_classes = app_settings.__dict__.get('MIDDLEWARE_CLASSES', [])

    result = {'view': [], 'response': [], 'exception': []}
    for middleware_path in mw_classes:
      # This code brutally lifted from django.core.handlers
      try:
        dot = middleware_path.rindex('.')
      except ValueError:
        raise exceptions.ImproperlyConfigured(_('%(module)s isn\'t a middleware module.') % {'module': middleware_path})
      mw_module, mw_classname = middleware_path[:dot], middleware_path[dot + 1:]
      try:
        mod = __import__(mw_module, {}, {}, [''])
      except ImportError as e:
        raise exceptions.ImproperlyConfigured(
          _('Error importing middleware %(module)s: "%(error)s".') % {'module': mw_module, 'error': e}
        )
      try:
        mw_class = getattr(mod, mw_classname)
      except AttributeError:
        raise exceptions.ImproperlyConfigured(
          _('Middleware module "%(module)s" does not define a "%(class)s" class.') % {'module': mw_module, 'class': mw_classname}
        )

      try:
        mw_instance = mw_class()
      except exceptions.MiddlewareNotUsed:
        continue
      # End brutal code lift

      # We need to make sure we don't have a process_request function because we don't know what
      # application will handle the request at the point process_request is called
      if hasattr(mw_instance, 'process_request'):
        raise exceptions.ImproperlyConfigured(_('AppSpecificMiddleware module "%(module)s" has a process_request function' +
              ' which is impossible.') % {'module': middleware_path})
      if hasattr(mw_instance, 'process_view'):
        result['view'].append(mw_instance.process_view)
      if hasattr(mw_instance, 'process_response'):
        result['response'].insert(0, mw_instance.process_response)
      if hasattr(mw_instance, 'process_exception'):
        result['exception'].insert(0, mw_instance.process_exception)
    return result


class LoginAndPermissionMiddleware(MiddlewareMixin):
  """
  Middleware that forces all views (except those that opt out) through authentication.
  """

  def process_request(self, request):
    # When local user login, oidc middleware refresh token if oidc_id_token_expiration doesn't exists!
    if request.session.get('_auth_user_backend', '') == 'desktop.auth.backend.AllowFirstUserDjangoBackend' \
        and 'desktop.auth.backend.OIDCBackend' in AUTH.BACKEND.get():
      request.session['oidc_id_token_expiration'] = time.time() + 300

  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    We also perform access logging in ``process_view()`` since we have the view function,
    which tells us the log level. The downside is that we don't have the status code,
    which isn't useful for status logging anyways.
    """
    request.ts = time.time()
    request.view_func = view_func
    access_log_level = getattr(view_func, 'access_log_level', None)

    # Skip loop for oidc
    if request.path in ['/oidc/authenticate/', '/oidc/callback/', '/oidc/logout/', '/hue/oidc_failed/']:
      return None

    if AUTH.AUTO_LOGIN_ENABLED.get() and request.path.startswith('/api/v1/token/auth'):
      pass  # allow /api/token/auth can create user or make it active
    elif request.path.startswith('/api/'):
      return None

    # Skip views not requiring login

    # If the view has "opted out" of login required, skip
    if hasattr(view_func, "login_notrequired"):
      log_page_hit(request, view_func, level=access_log_level or logging.DEBUG)
      return None

    # There are certain django views which are also opt-out, but
    # it would be evil to go add attributes to them
    if view_func in DJANGO_VIEW_AUTH_WHITELIST:
      log_page_hit(request, view_func, level=access_log_level or logging.DEBUG)
      return None

    # If user is logged in, check that he has permissions to access the app
    if request.user.is_active and request.user.is_authenticated:
      AppSpecificMiddleware.augment_request_with_app(request, view_func)

      # Until Django 1.3 which resolves returning the URL name, just do a match of the name of the view
      try:
        access_view = 'access_view:%s:%s' % (request._desktop_app, resolve(request.path)[0].__name__)
      except Exception as e:
        access_log(request, 'error checking view perm: %s' % e, level=access_log_level)
        access_view = ''

      app_accessed = request._desktop_app
      app_libs_whitelist = ["desktop", "home", "home2", "about", "hue", "editor", "notebook", "indexer", "404", "500", "403"]
      if has_connectors():
        app_libs_whitelist.append('metadata')
        if DASHBOARD_ENABLED.get():
          app_libs_whitelist.append('dashboard')
      # Accessing an app can access an underlying other app.
      # e.g. impala or spark uses code from beeswax and so accessing impala shows up as beeswax here.
      # Here we trust the URL to be the real app we need to check the perms.
      ui_app_accessed = get_app_name(request)
      if app_accessed != ui_app_accessed and ui_app_accessed not in ('logs', 'accounts', 'login'):
        app_accessed = ui_app_accessed

      if app_accessed and \
          app_accessed not in app_libs_whitelist and \
          not (
              is_admin(request.user) or
              request.user.has_hue_permission(action="access", app=app_accessed) or
              request.user.has_hue_permission(action=access_view, app=app_accessed)):
        access_log(request, 'permission denied', level=access_log_level)
        return PopupException(
            _("You do not have permission to access the %(app_name)s application.") % {'app_name': app_accessed.capitalize()},
            error_code=401
        ).response(request)
      else:
        if not hasattr(request, 'view_func'):
          log_page_hit(request, view_func, level=access_log_level)
        return None

    if AUTH.AUTO_LOGIN_ENABLED.get():
      # Auto-create the hue/hue user if not already present
      user = find_or_create_user(username='hue', password='hue')
      ensure_has_a_group(user)
      user = rewrite_user(user)

      user.is_active = True
      user.save()

      user = authenticate(request, username='hue', password='hue')
      if user is not None:
        login(request, user)
        return None

    logging.info("Redirecting to login page: %s", request.get_full_path())
    access_log(request, 'login redirection', level=access_log_level)
    no_idle_backends = [
        "desktop.auth.backend.SpnegoDjangoBackend",
        "desktop.auth.backend.KnoxSpnegoDjangoBackend"
    ]
    if CDP_LOGOUT_URL.get() == "":
      no_idle_backends.append("libsaml.backend.SAML2Backend")
    if request.ajax and all(no_idle_backend not in AUTH.BACKEND.get() for no_idle_backend in no_idle_backends):
      # Send back a magic header which causes Hue.Request to interpose itself
      # in the ajax request and make the user login before resubmitting the
      # request.
      response = HttpResponse("/* login required */", content_type="text/javascript")
      response[MIDDLEWARE_HEADER] = 'LOGIN_REQUIRED'
      return response
    else:
      if request.GET.get('is_embeddable'):
        return JsonResponse({
          'url': "%s?%s=%s" % (
              settings.LOGIN_URL,
              REDIRECT_FIELD_NAME,
              quote('/hue' + request.get_full_path().replace('is_embeddable=true', '').replace('&&', '&'))
          )
        })  # Remove embeddable so redirect from & to login works. Login page is not embeddable
      else:
        return HttpResponseRedirect("%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, quote(request.get_full_path())))

  def process_response(self, request, response):
    if hasattr(request, 'ts') and hasattr(request, 'view_func'):
      log_page_hit(request, request.view_func, level=logging.INFO, start_time=request.ts, response=response)
    return response


class JsonMessage(object):
  def __init__(self, **kwargs):
    self.kwargs = kwargs

  def __str__(self):
    return json.dumps(self.kwargs)


class AuditLoggingMiddleware(MiddlewareMixin):

  def __init__(self, get_response):
    self.get_response = get_response
    self.impersonator = SERVER_USER.get()

    if not AUDIT_EVENT_LOG_DIR.get():
      LOG.info('Unloading AuditLoggingMiddleware')
      raise exceptions.MiddlewareNotUsed

  def process_response(self, request, response):
    response['audited'] = False
    try:
      if hasattr(request, 'audit') and request.audit is not None:
        self._log_message(request, response)
        response['audited'] = True
    except Exception as e:
      LOG.error('Could not audit the request: %s' % e)

    return response

  def _log_message(self, request, response=None):
    audit_logger = get_audit_logger()

    audit_logger.debug(JsonMessage(**{
      'username': self._get_username(request),
      'impersonator': self.impersonator,
      'ipAddress': self._get_client_ip(request),
      'operation': request.audit['operation'],
      'operationText': request.audit.get('operationText', ''),
      'eventTime': self._milliseconds_since_epoch(),
      'allowed': self._get_allowed(request, response),
      'service': get_app_name(request),
      'url': request.path
    }))

  def _get_client_ip(self, request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
      x_forwarded_for = x_forwarded_for.split(',')[0]
    return request.META.get('HTTP_CLIENT_IP') or x_forwarded_for or request.META.get('REMOTE_ADDR')

  def _get_username(self, request):
    username = 'anonymous'
    if request.audit.get('username', None):
      username = request.audit.get('username')
    elif hasattr(request, 'user') and not request.user.is_anonymous:
      username = request.user.get_username()
    return username

  def _milliseconds_since_epoch(self):
    return int(time.time() * 1000)

  def _get_allowed(self, request, response=None):
    allowed = response.status_code != 401
    if 'allowed' in request.audit:
      return request.audit['allowed']
    return allowed


class ProxyMiddleware(MiddlewareMixin):

  def __init__(self, get_response):
    self.get_response = get_response
    if 'desktop.auth.backend.AllowAllBackend' not in AUTH.BACKEND.get():
      LOG.info('Unloading ProxyMiddleware')
      raise exceptions.MiddlewareNotUsed

  def process_response(self, request, response):
    return response

  def process_request(self, request):
    view_func = resolve(request.path)[0]
    if view_func in DJANGO_VIEW_AUTH_WHITELIST:
      return

    # AuthenticationMiddleware is required so that request.user exists.
    if not hasattr(request, 'user'):
      raise exceptions.ImproperlyConfigured(
        "The Django remote user auth middleware requires the"
        " authentication middleware to be installed.  Edit your"
        " MIDDLEWARE_CLASSES setting to insert"
        " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
        " before the SpnegoUserMiddleware class.")

    if request.GET.get('user.name'):
      try:
        username = request.GET.get('user.name')
        user = authenticate(username=username, password='')
        if user:
          request.user = user
          login(request, user)
          msg = 'Successful login for user: %s' % request.user.username
        else:
          msg = 'Failed login for user: %s' % request.user.username
        request.audit = {
          'operation': 'USER_LOGIN',
          'username': request.user.username,
          'operationText': msg
        }
        return
      except Exception:
        LOG.exception('Unexpected error when authenticating')
        return

  def clean_username(self, username, request):
    """
    Allows the backend to clean the username, if the backend defines a
    clean_username method.
    """
    backend_str = request.session[BACKEND_SESSION_KEY]
    backend = load_backend(backend_str)
    try:
      username = backend.clean_username(username)
    except AttributeError:
      pass
    return username


class SpnegoMiddleware(MiddlewareMixin):
  """
  Based on the WSGI SPNEGO middlware class posted here:
  http://code.activestate.com/recipes/576992/
  """

  def __init__(self, get_response):
    self.get_response = get_response
    if not set(AUTH.BACKEND.get()).intersection(
        set(['desktop.auth.backend.SpnegoDjangoBackend', 'desktop.auth.backend.KnoxSpnegoDjangoBackend'])
      ):
      LOG.info('Unloading SpnegoMiddleware')
      raise exceptions.MiddlewareNotUsed

  def process_request(self, request):
    """
    The process_request() method needs to communicate some state to the
    process_response() method. The two options for this are to return an
    HttpResponse object or to modify the META headers in the request object. In
    order to ensure that all of the middleware is properly invoked, this code
    currently uses the later approach. The following headers are currently used:

    GSS-String:
      This means that GSS authentication was successful and that we need to pass
      this value for the WWW-Authenticate header in the response.

    Return-401:
      This means that the SPNEGO backend is in use, but we didn't get an
      AUTHORIZATION header from the client. The way that the protocol works
      (http://tools.ietf.org/html/rfc4559) is by having the first response to an
      un-authenticated request be a 401 with the WWW-Authenticate header set to
      Negotiate. This will cause the browser to re-try the request with the
      AUTHORIZATION header set.
    """
    view_func = resolve(request.path)[0]
    if view_func in DJANGO_VIEW_AUTH_WHITELIST:
      return

    # AuthenticationMiddleware is required so that request.user exists.
    if not hasattr(request, 'user'):
      raise exceptions.ImproperlyConfigured(
        "The Django remote user auth middleware requires the"
        " authentication middleware to be installed.  Edit your"
        " MIDDLEWARE_CLASSES setting to insert"
        " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
        " before the SpnegoUserMiddleware class.")

    if 'HTTP_AUTHORIZATION' in request.META:
      type, authstr = request.META['HTTP_AUTHORIZATION'].split(' ', 1)

      if type == 'Negotiate':
        try:
          result, context = kerberos.authGSSServerInit('HTTP')
          if result != 1:
            return

          gssstring = ''
          r = kerberos.authGSSServerStep(context, authstr)
          if r == 1:
            gssstring = kerberos.authGSSServerResponse(context)
            request.META['GSS-String'] = 'Negotiate %s' % gssstring
          else:
            kerberos.authGSSServerClean(context)
            return

          username = kerberos.authGSSServerUserName(context)
          kerberos.authGSSServerClean(context)

          # In Trusted knox proxy, Hue must expect following:
          #   Trusted knox user: KNOX_PRINCIPAL
          #   Trusted knox proxy host: KNOX_PROXYHOSTS
          if 'desktop.auth.backend.KnoxSpnegoDjangoBackend' in AUTH.BACKEND.get():
            knox_verification = False
            principals = self.clean_principal(KNOX.KNOX_PRINCIPAL.get())
            principal = self.clean_principal(username)
            if principal.intersection(principals):
              # This may contain chain of reverse proxies, e.g. knox proxy, hue load balancer
              # Compare hostname on both HTTP_X_FORWARDED_HOST & KNOX_PROXYHOSTS+HUE_LB.
              # Both of these can be configured to use either hostname or IPs and we have to normalize to one or the other
              req_hosts = self.clean_host(request.META['HTTP_X_FORWARDED_HOST'])
              allowed_hosts = self.clean_host(KNOX.KNOX_PROXYHOSTS.get() + HUE_LB_HOSTS)
              if req_hosts.intersection(allowed_hosts):
                knox_verification = True
              else:
                access_warn(request, 'Failed to verify provided host %s with %s ' % (req_hosts, allowed_hosts))
            else:
              access_warn(request, 'Failed to verify provided username %s with %s ' % (principal, principals))
            # If knox authentication failed then generate 401 (Unauthorized error)
            if not knox_verification:
              request.META['Return-401'] = ''
              return

          if request.user.is_authenticated:
            if request.user.username == self.clean_username(username, request):
              return

          user = authenticate(username=username, request=request)
          if user:
            request.user = user
            login(request, user)
            knox_login_headers(request)
            msg = 'Successful login for user: %s' % request.user.username
          else:
            msg = 'Failed login for user: %s' % request.user.username
          request.audit = {
            'operation': 'USER_LOGIN',
            'username': request.user.username,
            'operationText': msg
          }
          access_warn(request, msg)
          return
        except Exception:
          LOG.exception('Unexpected error when authenticating against KDC')
          return
      else:
        request.META['Return-401'] = ''
        return
    else:
      if not request.user.is_authenticated:
        request.META['Return-401'] = ''
      return

  def process_response(self, request, response):
    if 'GSS-String' in request.META:
      response['WWW-Authenticate'] = request.META['GSS-String']
    elif 'Return-401' in request.META:
      response = HttpResponse("401 Unauthorized", content_type="text/plain",
        status=401)
      response['WWW-Authenticate'] = 'Negotiate'
      response.status = 401
    return response

  def clean_host(self, pattern):
    hosts = []
    if pattern:
      pattern_list = pattern if isinstance(pattern, list) else pattern.split(',')
      for hostport in pattern_list:
        host = hostport.split(':')[0].strip()
        try:
          hosts.append(socket.gethostbyaddr(host)[0])
        except Exception:
          LOG.exception('Could not resolve host addr %s' % host)
          hosts.append(host)
    return set(hosts)

  def clean_principal(self, pattern):
    principals = []
    if pattern:
      pattern_list = pattern if isinstance(pattern, list) else pattern.split(',')
      for principal_host in pattern_list:
        principal = principal_host.split('/')[0].strip()
      principals.append(principal)
    return set(principals)

  def clean_username(self, username, request):
    """
    Allows the backend to clean the username, if the backend defines a
    clean_username method.
    """
    backend_str = request.session[BACKEND_SESSION_KEY]
    backend = load_backend(backend_str)
    try:
      username = backend.clean_username(username, request)
    except AttributeError:
      pass
    return username


class HueRemoteUserMiddleware(RemoteUserMiddleware):
  """
  Middleware to delegate authentication to a proxy server. The proxy server
  will set an HTTP header (defaults to Remote-User) with the name of the
  authenticated user. This class extends the RemoteUserMiddleware class
  built into Django with the ability to configure the HTTP header and to
  unload the middleware if the RemoteUserDjangoBackend is not currently
  in use.
  """
  def __init__(self, get_response):
    if 'desktop.auth.backend.RemoteUserDjangoBackend' not in AUTH.BACKEND.get():
      LOG.info('Unloading HueRemoteUserMiddleware')
      raise exceptions.MiddlewareNotUsed
    super().__init__(get_response)
    self.header = AUTH.REMOTE_USER_HEADER.get()


class EnsureSafeMethodMiddleware(MiddlewareMixin):
  """
  Middleware to white list configured HTTP request methods.
  """
  def process_request(self, request):
    if request.method not in HTTP_ALLOWED_METHODS.get():
      return HttpResponseNotAllowed(HTTP_ALLOWED_METHODS.get())


class EnsureSafeRedirectURLMiddleware(MiddlewareMixin):
  """
  Middleware to white list configured redirect URLs.
  """
  def process_response(self, request, response):
    if response.status_code in (301, 302, 303, 305, 307, 308) and response.get('Location') and not hasattr(response, 'redirect_override'):
      redirection_patterns = REDIRECT_WHITELIST.get()
      location = response['Location']

      if any(regexp.match(location) for regexp in redirection_patterns):
        return response

      if url_has_allowed_host_and_scheme(location, allowed_hosts={request.get_host()}):
        return response

      if request.path in ['/oidc/authenticate/', '/oidc/callback/', '/oidc/logout/', '/hue/oidc_failed/']:
        return response

      response = render("error.mako", request, {
        'error': _('Redirect to %s is not allowed.') % response['Location'],
        'is_embeddable': request.GET.get('is_embeddable', False),
      })
      response.status_code = 403
      return response
    else:
      return response


class MetricsMiddleware(MiddlewareMixin):
  """
  Middleware to track the number of active requests.
  """

  def process_request(self, request):
    # import threading
    # LOG.debug("===> MetricsMiddleware pid: %d thread: %d" % (os.getpid(), threading.get_ident()))
    self._response_timer = metrics.response_time.time()
    metrics.active_requests.inc()
    if is_gunicorn_report_enabled():
      global_registry().update_metrics_shared_data()

  def process_exception(self, request, exception):
    self._response_timer.stop()
    metrics.request_exceptions.inc()

  def process_response(self, request, response):
    self._response_timer.stop()
    metrics.active_requests.dec()
    if is_gunicorn_report_enabled():
      global_registry().update_metrics_shared_data()
    return response


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
  def __init__(self, get_response):
    self.get_response = get_response
    self.secure_content_security_policy = SECURE_CONTENT_SECURITY_POLICY.get()
    if not self.secure_content_security_policy:
      LOG.info('Unloading ContentSecurityPolicyMiddleware')
      raise exceptions.MiddlewareNotUsed

  def process_response(self, request, response):
    if self.secure_content_security_policy and 'Content-Security-Policy' not in response:
      response["Content-Security-Policy"] = self.secure_content_security_policy

    return response


class MimeTypeJSFileFixStreamingMiddleware(MiddlewareMixin):
  """
  Middleware to detect and fix ".js" mimetype. SLES 11SP4 as example OS which detect js file
  as "text/x-js" and if strict X-Content-Type-Options=nosniff is set then browser fails to
  execute javascript file.
  """
  def __init__(self, get_response):
    self.get_response = get_response
    jsmimetypes = ['application/javascript', 'application/ecmascript']
    if mimetypes.guess_type("dummy.js")[0] in jsmimetypes:
      LOG.info('Unloading MimeTypeJSFileFixStreamingMiddleware')
      raise exceptions.MiddlewareNotUsed

  def process_response(self, request, response):
    if request.path_info.endswith('.js'):
      response['Content-Type'] = "application/javascript"

    return response


class MultipleProxyMiddleware:
  FORWARDED_FOR_FIELDS = [
    'HTTP_X_FORWARDED_FOR',
    'HTTP_X_FORWARDED_HOST',
    'HTTP_X_FORWARDED_SERVER',
  ]

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    """
    Rewrites the proxy headers so that only the most
    recent proxy is used.
    """
    location = -1

    if 'HTTP_X_REAL_IP' in request.META:
      if 'HTTP_X_FORWARDED_FOR' in request.META and \
        request.META['HTTP_X_REAL_IP'] in request.META['HTTP_X_FORWARDED_FOR']:
        location = 0
        for item in request.META['HTTP_X_FORWARDED_FOR'].split(','):
          if request.META['HTTP_X_REAL_IP'].strip() != item.strip():
            location += 1
          else:
            request.META['HTTP_X_FORWARDED_FOR'] = item.strip()
            break

    for field in self.FORWARDED_FOR_FIELDS:
      if field in request.META:
        if ',' in request.META[field]:
          parts = request.META[field].split(',')
          request.META[field] = parts[location].strip()

    if 'HTTP_X_FORWARDED_FOR' not in request.META and 'REMOTE_ADDR' in request.META:
      request.META['HTTP_X_FORWARDED_FOR'] = request.META['REMOTE_ADDR']
    return self.get_response(request)


class CacheControlMiddleware(MiddlewareMixin):
  def __init__(self, get_response):
    self.get_response = get_response
    self.custom_cache_control = CUSTOM_CACHE_CONTROL.get()
    if not self.custom_cache_control:
      LOG.info('Unloading CacheControlMiddleware')
      raise exceptions.MiddlewareNotUsed

  def process_response(self, request, response):
    if self.custom_cache_control:
      response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
      response['Pragma'] = 'no-cache'
      response['Expires'] = '0'
    return response
