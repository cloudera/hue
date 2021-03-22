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

from crequest.middleware import CrequestMiddleware

from django.db import connection, models, transaction

from desktop.conf import ENABLE_ORGANIZATIONS, ENABLE_CONNECTORS
from desktop.lib.connectors.models import Connector

from useradmin.organization import _fitered_queryset, get_user_request_organization

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t
else:
  from django.utils.translation import ugettext_lazy as _t

if ENABLE_ORGANIZATIONS.get():
  from useradmin.organization import OrganizationGroup as Group, Organization
else:
  from django.contrib.auth.models import Group


class LdapGroup(models.Model):
  """
  Groups that come from LDAP originally will have an LdapGroup
  record generated at creation time.
  """
  group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group")


class GroupPermission(models.Model):
  """
  Represents the permissions a group has.
  """
  group = models.ForeignKey(Group, on_delete=models.CASCADE)
  hue_permission = models.ForeignKey("HuePermission", on_delete=models.CASCADE)


class BasePermission(models.Model):
  """
  Set of non-object specific permissions that an app supports.

  Currently only assign permissions to groups (not users or roles).
  Could someday support external permissions of Apache Ranger permissions, AWS IAM...
  This could be done via subclasses or creating new types of connectors.
  """
  app = models.CharField(max_length=30)
  action = models.CharField(max_length=100)
  description = models.CharField(max_length=255)

  groups = models.ManyToManyField(Group, through=GroupPermission)

  def __str__(self):
    return "%s.%s:%s(%d)" % (self.app, self.action, self.description, self.pk)

  @classmethod
  def get_app_permission(cls, hue_app, action):
    return BasePermission.objects.get(app=hue_app, action=action)

  class Meta(object):
    abstract = True


class ConnectorPermission(BasePermission):
  connector = models.ForeignKey(Connector, on_delete=models.CASCADE)

  class Meta(object):
    abstract = True
    verbose_name = _t('Connector permission')
    verbose_name_plural = _t('Connector permissions')
    unique_together = ('connector', 'action',)



if ENABLE_ORGANIZATIONS.get():
  class OrganizationConnectorPermissionManager(models.Manager):

    def get_queryset(self):
      """Restrict to only organization"""
      queryset = super(OrganizationConnectorPermissionManager, self).get_queryset()
      return _fitered_queryset(queryset)

  class OrganizationConnectorPermission(ConnectorPermission):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    objects = OrganizationConnectorPermissionManager()

    def __init__(self, *args, **kwargs):
      if not kwargs.get('organization'):
        kwargs['organization'] = get_user_request_organization()

      super(OrganizationConnectorPermission, self).__init__(*args, **kwargs)

    class Meta(ConnectorPermission.Meta):
      abstract = True
      unique_together = ('connector', 'action', 'organization',)


if ENABLE_CONNECTORS.get():
  if ENABLE_ORGANIZATIONS.get():
    class HuePermission(OrganizationConnectorPermission): pass
  else:
    class HuePermission(ConnectorPermission): pass
else:
  class HuePermission(BasePermission): pass
