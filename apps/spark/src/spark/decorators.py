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

from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from spark.models import QueryExpired, QueryError, SessionExpired


LOG = logging.getLogger(__name__)


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}
    
    try:
      return func(*args, **kwargs)
    except SessionExpired, e:
      response['status'] = -2    
    except QueryExpired, e:
      response['status'] = -3
    except QueryError, e:
      response['status'] = 1
      response['message'] = force_unicode(str(e))
    except Exception, e:
      response['status'] = -1
      response['message'] = force_unicode(str(e))
    finally:
      if response:
        return HttpResponse(json.dumps(response), mimetype="application/json")
    
  return decorator


def json_error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Http404, e:
      raise e
    except Exception, e:
      response = {
        'error': str(e)
      }
      return HttpResponse(json.dumps(response), mimetype="application/json", status=500)
  return decorator
