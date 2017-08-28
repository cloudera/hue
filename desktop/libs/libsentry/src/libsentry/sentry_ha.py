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
import time

from django.utils.translation import ugettext as _

from desktop.lib.exceptions import StructuredThriftTransportException
from desktop.lib.exceptions_renderable import PopupException

from libsentry.client2 import SentryClient
from libsentry.sentry_site import get_sentry_server


LOG = logging.getLogger(__name__)


def create_client(client_class, username, server, component=None):
  if server is not None:
    kwargs = {
      'host': server['hostname'],
      'port': server['port'],
      'username': username
    }

    if client_class == SentryClient:
      kwargs.update({'component': component})

    return client_class(**kwargs)
  else:
    raise PopupException(_('Cannot create a Sentry client without server hostname and port.'))


def get_next_available_server(client_class, username, failed_host=None, component=None, create_client_fn=create_client):
  '''
  Given a failed host, attempts to find the next available host and returns a Sentry server if found, as well as a list
  of all Sentry hosts attempted.
  '''
  current_host = failed_host
  has_next = True
  attempted_hosts = []

  while has_next:
    LOG.warn('Could not connect to Sentry server %s, attempting to fetch next available client.' % current_host)
    next_server = get_sentry_server(current_host=current_host)
    time.sleep(1)
    try:
      client = create_client_fn(client_class, username, next_server, component)
      client.list_sentry_roles_by_group(groupName='*')
      # If above operation succeeds, return client
      LOG.info('Successfully connected to Sentry server %s, after attempting [%s], returning client.' % (client.host, ', '.join(attempted_hosts)))
      return next_server, attempted_hosts
    except StructuredThriftTransportException, e:
      # If we have come back around to the original failed client, exit
      if client.host == failed_host:
        has_next = False
      else:
        current_host = client.host
        attempted_hosts.append(current_host)
    except Exception, e:
      raise PopupException(_('Encountered unexpected error while trying to find available Sentry client: %s' % e))

  return None, attempted_hosts
