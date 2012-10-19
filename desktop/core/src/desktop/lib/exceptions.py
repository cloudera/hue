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

import sys
import traceback

from thrift.transport.TTransport import TTransportException

# Need full import statement
import desktop.lib.django_util


class StructuredException(Exception):
  """
  Many exceptions in this application are a string and some data
  that applies to.  The middleware will take these exceptions
  and render them.
  """
  def __init__(self, code, message, data=None, error_code=500):
    Exception.__init__(self, message)
    self.code = code
    self.message = message
    self.data = data
    self.error_code = error_code

    # Traceback is only relevant if an exception was thrown, caught, and we reraise with this exception.
    (type, value, tb) = sys.exc_info()
    self.traceback = traceback.extract_tb(tb)

  def __str__(self):
    return "%s (code %s): %s" % (self.message, self.code, repr(self.data))

  @property
  def response_data(self):
    return dict(code=self.code,
                message=self.message,
                data=self.data,
                traceback=self.traceback)

class MessageException(StructuredException):
  """
  Explicitly specified msg/filename exception.

  This has been superceded by PopupException.
  """
  def __init__(self, msg, filename=None, error_code=500):
    StructuredException.__init__(self,
      code="GENERIC_MESSAGE",
      message=msg,
      data=dict(filename=filename),
      error_code=error_code)

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

  def response(self, request):
    data = dict(title=self.title, message=self.message, detail=self.detail, traceback=self.traceback)
    if not request.ajax:
      data['request'] = request
    response = desktop.lib.django_util.render("popup_error.mako", request, data)
    response.status_code = self.error_code
    return response

class StructuredThriftTransportException(StructuredException, TTransportException):
  def __init__(self, ex, *args, **kwargs):
    kwargs['data'] = ex
    kwargs['message'] = ex.message
    kwargs['code'] = "THRIFTTRANSPORT"
    StructuredException.__init__(self, *args, **kwargs)
