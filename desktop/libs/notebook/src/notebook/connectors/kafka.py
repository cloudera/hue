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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode
from metadata.kafka_api import get_topics

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class KafkaApi(Api):

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    response = {}

    try:
      response['databases'] = get_topics()
    except Exception, e:
      LOG.warn('Autocomplete data fetching error: %s' % e)
      response['code'] = 500
      response['error'] = e.message

    return response
