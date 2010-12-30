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
# Utilities for django operations.

import logging
import re
import simplejson
import socket
import datetime

from django.utils.tzinfo import LocalTimezone
from django.utils.translation import ungettext, ugettext
from django.core import urlresolvers, serializers
from django.conf import settings
from django.utils.http import urlencode # this version is unicode-friendly
from django.http import QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response as django_render_to_response
from django.template.loader import render_to_string as django_render_to_string
from django.template import RequestContext
from django.db import models

from desktop.lib import django_mako
import desktop.conf
import desktop.lib.thrift_util

# Values for template_lib parameter
DJANGO = 'django'
MAKO = 'mako'

class Encoder(simplejson.JSONEncoder):
  """
  Automatically encodes JSON for Django models and
  Thrift objects, as well as objects that have
  "to_json" operations.
  """
  def default(self, o):
    if hasattr(o, "to_jsonable") and callable(o.to_jsonable):
      return o.to_jsonable()
    if desktop.lib.thrift_util.is_thrift_struct(o):
      return desktop.lib.thrift_util.thrift2json(o)
    if isinstance(o, models.Model):
      # Django serialization requires an iterable, so we wrap o in an array.
      x = serializers.serialize("python", [o])
      assert len(x) == 1
      return x[0]

    return simplejson.JSONEncoder.default(self, o)


def login_notrequired(func):
  """A decorator for view functions to allow access without login"""
  func.login_notrequired = True
  return func

_uri_prefix = None
def get_desktop_uri_prefix():
  """
  Return the uri prefix where desktop is generally accessible.

  This is useful when contructing a generic link. We can't trust the request, since
  the request could have come from localhost.
  Note there is no sure way to do it 100% correct. We use the FQDN, which might not
  be the right uri for some client.
  """
  global _uri_prefix
  if _uri_prefix is None:
    dt_host = desktop.conf.HTTP_HOST.get()
    if dt_host == '0.0.0.0':
      dt_host = socket.getfqdn()
    protocol = desktop.conf.is_https_enabled() and "https" or "http"
    _uri_prefix = '%s://%s:%s' % (protocol, dt_host, desktop.conf.HTTP_PORT.get())
  return _uri_prefix


def copy_query_dict(query_dict, attr_list):
  """
  copy_query_dict(query_dict ,attr_list) -> QueryDict object
  Copy the specified attributes to a new QueryDict.
  """
  res = QueryDict('', mutable=True)
  for attr in attr_list:
    if query_dict.has_key(attr):
      res[attr] = query_dict.get(attr)
  return res


def make_absolute(request, view_name, kwargs=None):
  """
  Magic to make an absolute url.  In the template world,
  this is done with {% url %}.
  """
  return request.build_absolute_uri(urlresolvers.reverse(view_name, kwargs=kwargs))

def _get_template_lib(template, kwargs):
  template_lib = kwargs.get('template_lib')
  if 'template_lib' in kwargs:
    del kwargs['template_lib']

  # Default based on file extension
  if template_lib == None:
    if template.endswith('.mako'):
      return MAKO
    else:
      return DJANGO
  return template_lib


def _render_to_response(template, *args, **kwargs):
  template_lib = _get_template_lib(template, kwargs)

  if template_lib == DJANGO:
    return django_render_to_response(template, *args, **kwargs)
  elif template_lib == MAKO:
    return django_mako.render_to_response(template, *args, **kwargs)
  else:
    raise Exception("Bad template lib: %s" % template_lib)

def render_to_string(template, *args, **kwargs):
  """Wrapper around django.template.loader.render_to_string which supports
  different template libraries."""
  template_lib = _get_template_lib(template, kwargs)
  if template_lib == DJANGO:
    return django_render_to_string(template, *args, **kwargs)
  elif template_lib == MAKO:
    return django_mako.render_to_string(template, *args, **kwargs)
  else:
    raise Exception("Bad template lib: %s" % template_lib)

def format_preserving_redirect(request, target, get_dict=None):
  """
  If request represents an ajax or embeddable "format", tries
  to preserve that for redirects.

  Any GET params may be passed through the QueryDict get_dict,
  which should be mutable.
  """
  my_get_dict = QueryDict('', mutable=True)
  if get_dict:
    my_get_dict.update(get_dict)

  if is_jframe_request(request):
    logging.info("JFrame redirection" +  target)
    my_get_dict['format'] = 'embed'
  elif request.ajax:
    my_get_dict['format'] = 'json'

  param = my_get_dict.urlencode()
  if param:
    if '?' not in target:
      param = '?' + param
    else:
      param = '&' + param

  return HttpResponseRedirect(target + param)

def is_jframe_request(request):
  """
  The JFrame container uses ?format=embed to request
  embeddable contents, and expects an HTTP response
  with some extra headers set in return.
  The extra headers are set in JFrameMiddleware.
  See also Hue.JFrame.js.
  """
  return request.META.get('HTTP_X_HUE_JFRAME') or \
      request.GET.get("format") == "embed"

def render(template, request, data, json=None, template_lib=None, force_template=False, **kwargs):
  """
  Render() is the main shortcut/workhorse for rendering view responses.
  It takes a template (either ".mako" or ".html", or influenced by
  template_lib), as well as as arbitrary data.

  It typically renders to an HttpResponse.  If the request is a non-JFrame
  AJAX reqeust (or if data is None), it renders into JSON.

  if force-template is True, will render the non-AJAX template response even if the
  request is via AJAX. This is to facilitate fetching HTML fragments.
  """
  if not force_template and not is_jframe_request(request) and (request.ajax or template is None):
    if json is not None:
      return render_json(json, request.GET.get("callback"))
    else:
      return render_json(data, request.GET.get("callback"))
  else:
    return _render_to_response(template,
                               RequestContext(request=request, dict=data),
                               template_lib=template_lib,
                               **kwargs)


def render_injected(http_resp, extra_html):
  """
  render_injected(http_resp, extra_html) -> HttpResponse

  Inject the extra html into the content of the http_resp.
  ``extra_html`` can be a string or an object with an ``html`` method/field.
  """
  assert isinstance(http_resp, HttpResponse)
  if 'text/html' not in http_resp.get('content-type', ''):
    return http_resp

  # Look for the </body> tag and inject the popup <div>
  markers = ('</body>', '</BODY>')
  content = http_resp.content
  for marker in markers:
    pos = content.rfind(marker)
    if pos != -1:
      break
  else:
    # No </body>
    return http_resp

  if hasattr(extra_html, 'html'):
    extra_html = extra_html.html
  if callable(extra_html):
    extra_html = extra_html()
  http_resp.content = ''.join((content[:pos], extra_html, content[pos:]))
  return http_resp


def encode_json(data, indent=None):
  """
  Converts data into a JSON string.

  Typically this is used from render_json, but it's the natural
  endpoint to test the Encoder logic, so it's separated out.
  """
  return simplejson.dumps(data, indent=indent, cls=Encoder)

VALID_JSON_IDENTIFIER = re.compile("^[a-zA-Z_$][a-zA-Z0-9_$]*$")

class IllegalJsonpCallbackNameException(Exception):
  pass

def render_json(data, jsonp_callback=None):
  """
  Renders data as json.  If jsonp is specified, wraps
  the result in a function.
  """
  if settings.DEBUG:
    indent = 2
  else:
    indent = 0
  json = encode_json(data, indent)
  if jsonp_callback is not None:
    if not VALID_JSON_IDENTIFIER.match(jsonp_callback):
      raise IllegalJsonpCallbackNameException("Invalid jsonp callback name: %s" % jsonp_callback)
    json = "%s(%s);" % (jsonp_callback, json)
  return HttpResponse(json, mimetype='text/javascript')

def update_if_dirty(model_instance, **kwargs):
  """
  Updates an instance of a model with kwargs.
  saves only if there's been a change.
  """
  dirty = False
  for key, value in kwargs.items():
    if getattr(model_instance, key) != value:
      setattr(model_instance, key, value)
      dirty = True

  if dirty:
    model_instance.save()

def extract_field_data(field):
  """
  given a form field, return its value
  """
  if not field.form.is_bound:
    res = field.form.initial.get(field.name, field.field.initial)
    if callable(res):
      return res()
    return res
  else:
    return field.data

def get_app_nice_name(app_name):
  try:
    return desktop.appmanager.get_desktop_module(app_name).settings.NICE_NAME
  except:
    return app_name

class StructuredException(Exception):
  """
  Many exceptions in this application are a string and a filename
  that applies to.  The middleware will take these exceptions
  and render them.
  """
  def __init__(self, code, message, data=None):
    Exception.__init__(self, message)
    self.code = code
    self.message = message
    self.data = data

  def __str__(self):
    return "%s (code %s): %s" % (self.message, self.code, repr(self.data))

  @property
  def response_data(self):
    return dict(code=self.code,
                message=self.message,
                data=self.data)

class MessageException(StructuredException):
  """
  Explicitly specified msg/filename exception.

  This has been superceded by PopupException.
  """
  def __init__(self, msg, filename=None):
    StructuredException.__init__(self,
      code="GENERIC_MESSAGE",
      message=msg,
      data=dict(filename=filename))

class PopupException(Exception):
  """
  Middleware will render this exception; and the template
  renders it as a pop-up.
  """
  def __init__(self, message, title="Error", detail=None):
    Exception.__init__(self, message)
    self.message = message
    self.title = title
    self.detail = detail

  def response(self, request):
    return render("popup_error.mako", request,
      dict(title=self.title, message=self.message, detail=self.detail, request=request))


class PopupWithJframe(object):
  """A popup container, intended to be rendered with a regular HttpResponse."""
  def __init__(self, message, launch_app_name=None, launch_app_url=None):
    """
    PopupWithJframe(message, launch_app_name=None, launch_app_url=None)

    It can simply display a message. It can also show a link to launch an app.
    """
    self.message = message
    self.app = launch_app_name
    self.app_url = launch_app_url

  def html(self):
    return django_mako.render_to_string('popup_with_jframe.mako', {
      'msg': self.message,
      'app': self.app,
      'app_url': self.app_url,
    })

class TruncatingModel(models.Model):
  """
  Abstract class which truncates Text and Char fields to their configured
  maximum lengths, to avoid database field overflow errors.
  """
  class Meta:
    abstract = True

  def __setattr__(self, name, value):
    try:
      field = self._meta.get_field(name)
      if type(field) in [models.CharField, models.TextField] and type(value) == str:
        value = value[:field.max_length]
    except models.fields.FieldDoesNotExist:
      pass # This happens with foreign keys.

    super.__setattr__(self, name, value)

def reverse_with_get(view, args=None, kwargs=None, get=None):
  """
  Version of urlresolvers.reverse that also manages get parameters.

  view, args and kwargs are arguments passed to urlresolvers.reverse.
  Typically only one of args and kwargs are specified.

  get is a dictionary of extra get parameters.
  """
  if args is None:
    args = dict()
  url = urlresolvers.reverse(view, args=args, kwargs=kwargs)
  if get is not None and len(get) > 0:
    params = urlencode(get)
    url = url + "?" + params
  return url

def humanize_duration(seconds, abbreviate=False):
  d = datetime.datetime.fromtimestamp(0)
  now = datetime.datetime.fromtimestamp(seconds)
  return timesince(d, now, abbreviate)

def timesince(d=None, now=None, abbreviate=False):
  """
  Takes two datetime objects and returns the time between d and now
  as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
  then "0 seconds" is returned. If abbreviate is True, it truncates values to,
  for example, "10m" or "4m 30s". Alternately it can take a second value
  and return the proper count.

  Units used are years, months, weeks, days, hours, minutes, and seconds.
  Microseconds are ignored.  Up to two adjacent units will be
  displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
  possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.

  Adapted from the timesince filter in Django:
  http://docs.djangoproject.com/en/dev/ref/templates/builtins/#timesince
  """

  if abbreviate:
    chunks = (
      (60 * 60 * 24 * 365, lambda n: 'y'),
      (60 * 60 * 24 * 30, lambda n: 'm'),
      (60 * 60 * 24 * 7, lambda n : 'w'),
      (60 * 60 * 24, lambda n : 'd'),
      (60 * 60, lambda n: 'h'),
      (60, lambda n: 'm'),
      (1, lambda n : 's'),
    )
  else:
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
      (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n)),
      (1, lambda n : ungettext('second', 'seconds', n)),
    )

  # Convert datetime.date to datetime.datetime for comparison.
  if not isinstance(d, datetime.datetime):
    d = datetime.datetime(d.year, d.month, d.day)
  if now and not isinstance(now, datetime.datetime):
    now = datetime.datetime(now.year, now.month, now.day)

  if not now:
    if d.tzinfo:
      now = datetime.datetime.now(LocalTimezone(d))
    else:
      now = datetime.datetime.now()

  # ignore microsecond part of 'd' since we removed it from 'now'
  delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
  since = delta.days * 24 * 60 * 60 + delta.seconds
  if since <= 0:
    # d is in the future compared to now, stop processing.
    if abbreviate:
      return u'0' + ugettext('s')
    else:
      return u'0 ' + ugettext('seconds')
  for i, (seconds, name) in enumerate(chunks):
    count = since // seconds
    if count != 0:
      break
  if abbreviate:
    s = ugettext('%(number)d%(type)s') % {'number': count, 'type': name(count)}
  else:
    s = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
  if i + 1 < len(chunks):
    # Now get the second item
    seconds2, name2 = chunks[i + 1]
    count2 = (since - (seconds * count)) // seconds2
    if count2 != 0:
      if abbreviate:
        s += ugettext(', %(number)d%(type)s') % {'number': count2, 'type': name2(count2)}
      else:
        s += ugettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
  return s
