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
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import DatabaseError
from django.db.models import Q
from django.utils.translation import ugettext as _

from desktop.auth.views import dt_logout
from desktop.conf import AUTH, LDAP, SESSION

from models import UserProfile, get_profile
from views import import_ldap_users

import ldap_access


LOG = logging.getLogger(__name__)


class LdapSynchronizationMiddleware(object):
  """
  Synchronize against LDAP authority.
  """
  USER_CACHE_NAME = 'ldap_use_group_sync_cache'

  def process_request(self, request):
    user = request.user
    server = None

    # Used by tests only
    if request.method == "GET":
      server = request.GET.get('server')

    if not user or not user.is_authenticated():
      return

    if not User.objects.filter(username=user.username, userprofile__creation_method=UserProfile.CreationMethod.EXTERNAL.name).exists():
      LOG.warn("User %s is not an Ldap user" % user.username)
      return

    # Cache should be cleared when user logs out.
    if self.USER_CACHE_NAME not in request.session:
      if LDAP.LDAP_SERVERS.get():
        connection = ldap_access.get_connection_from_server(next(LDAP.LDAP_SERVERS.__iter__()))
      else:
        connection = ldap_access.get_connection_from_server()

      import_ldap_users(connection, user.username, sync_groups=True, import_by_dn=False, server=server)

      request.session[self.USER_CACHE_NAME] = True
      request.session.modified = True


class LastActivityMiddleware(object):
  """
  Middleware to track the last activity of a user and automatically log out the user after a specified period of inactivity
  """

  def process_request(self, request):
    user = request.user

    if not user or not user.is_authenticated():
      return

    profile = get_profile(user)
    expires_after = AUTH.IDLE_SESSION_TIMEOUT.get()
    now = datetime.now()
    logout = False

    if profile.last_activity and expires_after > 0 and self._total_seconds(now - profile.last_activity) > expires_after:
      logout = True

    # Save last activity for user except when polling
    if not (request.path.strip('/') == 'notebook/api/check_status') \
        and not (request.path.strip('/').startswith('jobbrowser/api/job')) \
        and not (request.path.strip('/') == 'jobbrowser/jobs' and request.POST.get('format') == 'json') \
        and not (request.path.strip('/') == 'desktop/debug/is_idle') \
        and not (request.path.strip('/').startswith('oozie/list_oozie_')):
      try:
        profile.last_activity = datetime.now()
        profile.save()
      except DatabaseError:
        LOG.exception('Error saving profile information')

    if logout:
      dt_logout(request, next_page='/')


  def _total_seconds(self, dt):
    # Keep backward compatibility with Python 2.6 which doesn't support total_seconds()
    if hasattr(dt, 'total_seconds'):
      return dt.total_seconds()
    else:
      return (dt.microseconds + (dt.seconds + dt.days * 24 * 3600) * 10**6) / 10**6

class ConcurrentUserSessionMiddleware(object):
  """
  Middleware that remove concurrent user sessions when configured
  """
  def process_response(self, request, response):
    try:
      user = request.user
    except AttributeError: # When the request does not store user. We care only about the login request which does store the user.
      return response

    if request.user.is_authenticated() and request.session.modified and request.user.id: # request.session.modified checks if a user just logged in
      limit = SESSION.CONCURRENT_USER_SESSION_LIMIT.get()
      if limit:
        count = 1;
        for session in Session.objects.filter(~Q(session_key=request.session.session_key), expire_date__gte=datetime.now()).order_by('-expire_date'):
          data = session.get_decoded()
          if data.get('_auth_user_id') == request.user.id:
            if count >= limit:
              LOG.info('Expiring concurrent user session %s' % request.user.username)
              session.expire_date = datetime.now()
              session.save()
            else:
              count += 1
    return response
