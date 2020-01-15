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

from crequest.middleware import CrequestMiddleware

from django.db import connection, models, transaction

from desktop.conf import ENABLE_ORGANIZATIONS



def default_organization():
  from useradmin.models import Organization
  default_organization, created = Organization.objects.get_or_create(name='default', domain='default')
  return default_organization


def get_user_request_organization():
  request = CrequestMiddleware.get_request()
  return request.user.organization if request and hasattr(request, 'user') and request.user.is_authenticated() else default_organization()


def _fitered_queryset(queryset, by_owner=False):
  request = CrequestMiddleware.get_request()

  # Avoid infinite recursion on very first retrieval of the user
  if request and hasattr(request, 'user') and hasattr(request.user, '_wrapped') and type(request.user._wrapped) is not object and request.user.is_authenticated():
    if by_owner:
      filters = {'owner__organization': request.user.organization}
    else:
      filters = {'organization': request.user.organization}

    queryset = queryset.filter(**filters)

  return queryset


if ENABLE_ORGANIZATIONS.get():
  class OrganizationConnectorPermissionManager(models.Manager):

    def get_queryset(self):
      """Restrict to only organization"""
      queryset = super(OrganizationConnectorPermissionManager, self).get_queryset()
      return _fitered_queryset(queryset)

  class OrganizationConnectorPermission(ConnectorPermission):
    organization = models.ForeignKey(Organization)

    objects = OrganizationConnectorPermissionManager()

    def __init__(self, *args, **kwargs):
      if not kwargs.get('organization'):
        kwargs['organization'] = get_user_request_organization()

      super(OrganizationConnectorPermission, self).__init__(*args, **kwargs)

    class Meta(ConnectorPermission.Meta):
      abstract = True
      unique_together = ('connector', 'action', 'organization',)
