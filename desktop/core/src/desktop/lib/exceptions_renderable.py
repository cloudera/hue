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

from django.utils.encoding import force_unicode

import desktop.lib.django_util


LOG = logging.getLogger(__name__)


class PopupException(Exception):
  """
  Middleware will render this exception; and the template
  renders it as a pop-up.
  """
  def __init__(self, message, title="Error", detail=None, error_code=500):
    Exception.__init__(self, message)
    self.message = message
    self.title = title
    self.detail = detail
    self.error_code = error_code

    # Traceback is only relevant if an exception was thrown, caught, and we reraise with this exception.
    (type, value, tb) = sys.exc_info()
    self.traceback = traceback.extract_tb(tb)
    if self.traceback:
      LOG.error('Potential trace: %s' % self.traceback)

  def response(self, request):
    data = dict(title=force_unicode(self.title), message=force_unicode(self.message), detail=force_unicode(self.detail) if self.detail else None, traceback=self.traceback)
    if not request.ajax:
      data['request'] = request
    response = desktop.lib.django_util.render("popup_error.mako", request, data)
    response.status_code = self.error_code
    return response
