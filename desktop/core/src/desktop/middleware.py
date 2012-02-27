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

import logging

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core import exceptions
import django.db
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.utils.http import urlquote
from django.utils.encoding import iri_to_uri
import django.views.static
import django.views.generic.simple
import django.contrib.auth.views

import desktop.conf
from desktop.lib import apputil
from desktop.lib.django_util import render_json, is_jframe_request, PopupException
from desktop.log.access import access_log, log_page_hit
from desktop import appmanager
from hadoop import cluster
import simplejson

MIDDLEWARE_HEADER = "X-Hue-Middleware-Response"

# Views inside Django that don't require login
# (see LoginAndPermissionMiddleware)
DJANGO_VIEW_AUTH_WHITELIST = [
  django.views.static.serve,
  django.views.generic.simple.redirect_to,
]

class AjaxMiddleware(object):
  """
  Middleware that augments request to set request.ajax
  for either is_ajax() (looks at HTTP headers) or ?format=json
  GET parameters.
  """
  def process_request(self, request):
    request.ajax = request.is_ajax() or request.REQUEST.get("format", "") == "json"
    return None

class ExceptionMiddleware(object):
  """
  If exceptions know how to render themselves, use that.
  """
  def process_exception(self, request, exception):
    import traceback
    logging.info("Processing exception: %s: %s" % (exception, traceback.format_exc()))

    if hasattr(exception, "response"):
      return exception.response(request)

    if hasattr(exception, "response_data"):
      if request.ajax:
        response = render_json(exception.response_data)
        response[MIDDLEWARE_HEADER] = 'EXCEPTION'
        return response
      else:
        return render_to_response("error.html", dict(error=exception.response_data.get("message")))

    # We didn't handle it as a special exception, but if we're ajax we still
    # need to do some kind of nicer handling than the built-in page
    # Note that exception may actually be an Http404 or similar.
    if request.ajax:
      err = "An error occurred: %s" % (exception,)
      logging.exception("Middleware caught an exception")
      return PopupException(err, detail=None).response(request)

    return None

class JFrameMiddleware(object):
  """
  Updates JFrame headers to update path and push flash messages into headers.
  """
  def process_response(self, request, response):
    path = request.path
    if request.GET:
      get_params = request.GET.copy()
      if "noCache" in get_params:
        del get_params["noCache"]
      query_string = get_params.urlencode()
      if query_string:
        path = request.path + "?" + query_string
    response['X-Hue-JFrame-Path'] = iri_to_uri(path)
    if response.status_code == 200:
      if is_jframe_request(request):
        if hasattr(request, "flash"):
          flashes = request.flash.get()
          if flashes:
            response['X-Hue-Flash-Messages'] = simplejson.dumps(flashes)

    return response

class ClusterMiddleware(object):
  """
  Manages setting request.fs and request.jt
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    Sets request.fs and request.jt on every request to point to the
    configured filesystem.
    """
    has_hadoop = apputil.has_hadoop()

    request.fs_ref = request.REQUEST.get('fs', view_kwargs.get('fs', 'default'))
    if "fs" in view_kwargs:
      del view_kwargs["fs"]

    try:
      request.fs = cluster.get_hdfs(request.fs_ref)
    except KeyError:
      raise KeyError('Cannot find HDFS called "%s"' % (request.fs_ref,))

    if request.user.is_authenticated() and request.fs is not None:
      request.fs.setuser(request.user.username)

    if request.user.is_authenticated() and has_hadoop:
      request.jt = cluster.get_default_mrcluster()
      if request.jt is not None:
        request.jt.setuser(request.user.username)
    else:
      request.jt = None


class AppSpecificMiddleware(object):
  @classmethod
  def augment_request_with_app(cls, request, view_func):
    """ Stuff the app into the request for use in later-stage middleware """
    if not hasattr(request, "_desktop_app"):
      module = apputil.getmodule_wrapper(view_func)
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
    """View middleware"""
    self.augment_request_with_app(request, view_func)
    if not request._desktop_app:
      return None

    # Run the middlewares
    ret = None
    for middleware in self._get_middlewares(request._desktop_app, 'view'):
      ret = middleware(request, view_func, view_args, view_kwargs)
      if ret: return ret # short circuit
    return ret

  def process_response(self, request, response):
    """Response middleware"""
    # We have the app that we stuffed in there
    if not hasattr(request, '_desktop_app'):
      logging.debug("No desktop_app known for request.")
      return response

    for middleware in reversed(self._get_middlewares(request._desktop_app, 'response')):
      response = middleware(request, response)
    return response

  def process_exception(self, request, exception):
    """Exception middleware"""
    # We have the app that we stuffed in there
    if not hasattr(request, '_desktop_app'):
      logging.debug("No desktop_app known for exception.")
      return None

    # Run the middlewares
    ret = None
    for middleware in self._get_middlewares(request._desktop_app, 'exception'):
      ret = middleware(request, exception)
      if ret: return ret # short circuit
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
          raise exceptions.ImproperlyConfigured, '%s isn\'t a middleware module' % middleware_path
      mw_module, mw_classname = middleware_path[:dot], middleware_path[dot+1:]
      try:
          mod = __import__(mw_module, {}, {}, [''])
      except ImportError, e:
          raise exceptions.ImproperlyConfigured, 'Error importing middleware %s: "%s"' % (mw_module, e)
      try:
          mw_class = getattr(mod, mw_classname)
      except AttributeError:
          raise exceptions.ImproperlyConfigured, 'Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname)

      try:
        mw_instance = mw_class()
      except exceptions.MiddlewareNotUsed:
        continue
      # End brutal code lift

      # We need to make sure we don't have a process_request function because we don't know what
      # application will handle the request at the point process_request is called
      if hasattr(mw_instance, 'process_request'):
        raise exceptions.ImproperlyConfigured, \
              ('AppSpecificMiddleware module "%s" has a process_request function' + \
              ' which is impossible.') % middleware_path
      if hasattr(mw_instance, 'process_view'):
        result['view'].append(mw_instance.process_view)
      if hasattr(mw_instance, 'process_response'):
        result['response'].insert(0, mw_instance.process_response)
      if hasattr(mw_instance, 'process_exception'):
        result['exception'].insert(0, mw_instance.process_exception)
    return result

class LoginAndPermissionMiddleware(object):
  """
  Middleware that forces all views (except those that opt out) through authentication.
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    We also perform access logging in ``process_view()`` since we have the view function,
    which tells us the log level. The downside is that we don't have the status code,
    which isn't useful for status logging anyways.
    """
    access_log_level = getattr(view_func, 'access_log_level', None)
    # First, skip views not requiring login

    # If the view has "opted out" of login required, skip
    if hasattr(view_func, "login_notrequired"):
      log_page_hit(request, view_func, level=access_log_level or logging.DEBUG)
      return None

    # There are certain django views which are also opt-out, but
    # it would be evil to go add attributes to them
    if view_func in DJANGO_VIEW_AUTH_WHITELIST:
      log_page_hit(request, view_func, level=access_log_level or logging.DEBUG)
      return None

    # If user is logged in, check that he has permissions to access the
    # app.
    if request.user.is_active and request.user.is_authenticated():
      AppSpecificMiddleware.augment_request_with_app(request, view_func)
      if request._desktop_app and \
          request._desktop_app != "desktop" and \
          not request.user.has_hue_permission(action="access", app=request._desktop_app):
        access_log(request, 'permission denied', level=access_log_level)
        return PopupException("You do not have permission to access the %s application." % (request._desktop_app.capitalize())).response(request)
      else:
        log_page_hit(request, view_func, level=access_log_level)
        return None

    logging.info("Redirecting to login page: %s", request.get_full_path())
    access_log(request, 'login redirection', level=access_log_level)
    if request.ajax:
      # Send back a magic header which causes Hue.Request to interpose itself
      # in the ajax request and make the user login before resubmitting the
      # request.
      response = HttpResponse("/* login required */", content_type="text/javascript")
      response[MIDDLEWARE_HEADER] = 'LOGIN_REQUIRED'
      return response
    else:
      return HttpResponseRedirect("%s?%s=%s" % (settings.LOGIN_URL,
        REDIRECT_FIELD_NAME,
        urlquote(request.get_full_path())))


class SessionOverPostMiddleware(object):
  """
  Django puts session info in cookies, which is reasonable.
  Unfortunately, the plugin we use for file-uploading
  doesn't forward the cookies, though it can do so over
  POST.  So we push the POST data back in.

  This is the issue discussed at
  http://www.stereoplex.com/two-voices/cookieless-django-sessions-and-authentication-without-cookies
  and
  http://digitarald.de/forums/topic.php?id=20

  The author of fancyupload says (http://digitarald.de/project/fancyupload/):
    Flash-request forgets cookies and session ID

    See option appendCookieData. Flash FileReference is not an intelligent
    upload class, the request will not have the browser cookies, Flash saves
    his own cookies. When you have sessions, append them as get-data to the the
    URL (e.g. "upload.php?SESSID=123456789abcdef"). Of course your session-name
    can be different.

  and, indeed, folks are whining about it: http://bugs.adobe.com/jira/browse/FP-78

  There seem to be some other solutions:
  http://robrosenbaum.com/flash/using-flash-upload-with-php-symfony/
  and it may or may not be browser and plugin-dependent.

  In the meanwhile, this is pretty straight-forward.
  """
  def process_request(self, request):
    cookie_key = settings.SESSION_COOKIE_NAME
    if cookie_key not in request.COOKIES and cookie_key in request.POST:
      request.COOKIES[cookie_key] = request.POST[cookie_key]
      del request.POST[cookie_key]

class FlashMessageMiddleware(object):
  """
  Builds request.flash for manipulating flash messages.
  request.flash is an instance of the FlashMessenger object.
  """
  def process_request(self, request):
    assert not hasattr(request, "flash")
    request.flash = FlashMessenger(request)
    return None

  def process_exception(self, request, exception):
    request.flash.warn_if_non_empty()
    return None

  def process_response(self, request, response):
    # This seems to happen if common middleware's "trailing slash" support gets
    # activated.
    if not hasattr(request, "flash"):
      return response

    request.flash.warn_if_non_empty()
    return response

class FlashMessenger(object):
  """
  Manages storing and rendering flash messages.
  """

  def __init__(self,request):
    self.request = request

  def put(self, text):
    """
    Places flash messages to be rendered. Note that this will not be HTML-escaped.
    """
    self.request.session.setdefault("flashMessages", []).append(text)
    self.request.session.modified = True

  def get(self):
    """
    Gets messages to be displayed, only messages that have not been displayed prior.
    Always returns a list, though that list may be empty.
    """
    messages = self.request.session.get('flashMessages')
    if messages is not None:
      del self.request.session['flashMessages']
      return messages
    else:
      return []

  def warn_if_non_empty(self):
    if self.request.session.get('flashMessages') is not None and len(self.request.session['flashMessages']) > 0:
      logging.warning("Returning request with unmaterialized flash messages: %s" % repr(self.request.session['flashMessages']))

class DatabaseLoggingMiddleware(object):
  """
  If configured, logs database queries for every request.
  """
  DATABASE_LOG = logging.getLogger("desktop.middleware.DatabaseLoggingMiddleware")
  def process_response(self, request, response):
    if desktop.conf.DATABASE_LOGGING.get():
      if self.DATABASE_LOG.isEnabledFor(logging.INFO):
          # This only exists if desktop.settings.DEBUG is true, hence the use of getattr
          for query in getattr(django.db.connection, "queries", []):
            self.DATABASE_LOG.info("(%s) %s" % (query["time"], query["sql"]))
    return response
