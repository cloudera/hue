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
"""
These methods should never be placed in 'desktop.lib.exceptions'.
This file exists to remove circular reference caused by importing django_util.
"""

import logging
import sys
import traceback

if sys.version_info[0] > 2:
  from django.utils.encoding import force_str
else:
  from django.utils.encoding import force_unicode as force_str

import desktop.lib.django_util


LOG = logging.getLogger()


def raise_popup_exception(message, title="Error", detail=None, error_code=500):
  tb = sys.exc_info()
  raise PopupException(message, title=title, detail=detail, error_code=error_code, tb=traceback.extract_tb(tb[2]))

class PopupException(Exception):
  """
  Middleware will render this exception; and the template renders it as a pop-up.
  """
  def __init__(self, message, title="Error", detail=None, error_code=500, tb=None):
    Exception.__init__(self, message)
    self.message = message
    self.title = title
    self.detail = detail
    self.error_code = error_code

    if self.detail:
      LOG.error('Potential detail: %s' % self.detail)

    if tb:
      self.traceback = tb
    else: # At this point the previous trace is already lost
      # Traceback is only relevant if an exception was thrown, caught, and we reraise with this exception.
      tb = sys.exc_info()
      self.traceback = traceback.extract_tb(tb[2])

    if self.traceback:
      LOG.error('Potential trace: %s' % self.traceback)

  def response(self, request):
    data = {
      'title': force_str(self.title),
      'message': force_str(self.message),
      'detail': force_str(self.detail) if self.detail else None,
      'traceback': self.traceback,
      'is_embeddable': request.GET.get('is_embeddable', False)
    }

    if not request.ajax:
      data['request'] = request
    else:
      data['traceback'] = traceback.format_list(data['traceback'])

    response = desktop.lib.django_util.render("popup_error.mako", request, data)
    if self.error_code == 500 and data['is_embeddable']: # Hue 4
      response.status_code = 200
    else:
      response.status_code = self.error_code

    return response