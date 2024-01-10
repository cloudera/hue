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
import sys
import uuid

from crequest.middleware import CrequestMiddleware

from django.contrib.auth.models import models, AbstractUser, BaseUserManager
from django.utils.functional import SimpleLazyObject

from desktop.conf import ENABLE_ORGANIZATIONS

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t
else:
  from django.utils.translation import ugettext_lazy as _t


LOG = logging.getLogger()


def get_user_request_organization():
  request = CrequestMiddleware.get_request()
  return request.user.organization if request and hasattr(request, 'user') and request.user.is_authenticated else None


def _fitered_queryset(queryset, by_owner=False):
  request = CrequestMiddleware.get_request()

  # Avoid infinite recursion on very first retrieval of the user
  if ENABLE_ORGANIZATIONS.get() and \
      request and hasattr(request, 'user') and hasattr(request.user, '_wrapped') and type(request.user._wrapped) is not object and \
      request.user.is_authenticated:
    if by_owner:
      filters = {'owner__organization': request.user.organization}
    else:
      filters = {'organization': request.user.organization}

    queryset = queryset.filter(**filters)

  return queryset


def get_organization(email, is_multi_user=False):
  if email is None:
    organization = Organization.objects.first()
    LOG.warning('Returning first organization: %s' % organization)
  else:
    domain = email.split('@')[1] if is_multi_user else email

    if domain:
      organization, created = Organization.objects.get_or_create(name=domain, domain=domain, is_multi_user=is_multi_user)
      LOG.info("Materializing organization %s in the database, is_multi_user=%s" % (domain, is_multi_user))
    else:
      LOG.warning('No organization domain found for email %s' % email)  # For Backends without emails or when organization enabled by default
      organization = None

  return organization


def uuid_default():
  return str(uuid.uuid4())



class OrganizationManager(models.Manager):
  use_in_migrations = True

  def get_by_natural_key(self, name):
    return self.get(name=name)


if ENABLE_ORGANIZATIONS.get():
  class Organization(models.Model):
    """
    Organizations handle contained sets of setups (user, group, connectors...).

    An external user create an account and gets attached to its single user organization and becomes its admin. The organization can
    be later converted to a multi user organization (if the domain name is owned by the first user).

    An organization admin is not a Hue admin. The later is the true super user and has access to the server logs and metrics.
    """
    name = models.CharField(max_length=200, help_text=_t("The name of the organization"), unique=True)
    uuid = models.CharField(default=uuid_default, max_length=36, unique=True)
    domain = models.CharField(max_length=200, help_text=_t("The domain name of the organization, e.g. gethue.com"), unique=True)
    customer_id = models.CharField(_t('Customer id'), max_length=128, default=None, null=True)
    is_active = models.BooleanField(default=True)
    is_multi_user = models.BooleanField(default=True)

    objects = OrganizationManager()

    def __str__(self):
      return self.name or self.domain

    def natural_key(self):
      return (self.name,)


class OrganizationGroupManager(models.Manager):

  def get_queryset(self):
    """Make sure to restrict to only organization's groups"""
    queryset = super(OrganizationGroupManager, self).get_queryset()
    return _fitered_queryset(queryset)


if ENABLE_ORGANIZATIONS.get():
  class OrganizationGroup(models.Model):
    name = models.CharField(_t('name'), max_length=80, unique=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    permissions = models.ManyToManyField(
        'HuePermission',
        verbose_name=_t('permissions'),
        blank=True,
    )
    # Could also have a set of Roles at some point.

    objects = OrganizationGroupManager()

    def __init__(self, *args, **kwargs):
      if not kwargs.get('organization'):
        kwargs['organization'] = get_user_request_organization()

      super(OrganizationGroup, self).__init__(*args, **kwargs)

    class Meta:
      verbose_name = _t('organization group')
      verbose_name_plural = _t('organization groups')
      unique_together = ('name', 'organization',)

    def __str__(self):
      return '%s @ %s' % (self.name, self.organization)

    def natural_key(self):
      return (self.organization, self.name,)


class UserManager(BaseUserManager):
  """Define a model manager for User model with no username field."""

  use_in_migrations = True

  def get_queryset(self):
    """Make sure to restrict to only organization's user"""
    queryset = super(UserManager, self).get_queryset()
    return _fitered_queryset(queryset)

  def get(self, *args, **kwargs):
    if kwargs.get('username'):
      kwargs['email'] = kwargs.pop('username')

    request = CrequestMiddleware.get_request()

    # Avoid infinite recursion
    if request and hasattr(request, 'user') and hasattr(request.user, '_wrapped') and type(request.user._wrapped) is not object:
      organization = get_user_request_organization()
      if organization:
        kwargs['organization'] = organization

    return super(UserManager, self).get(*args, **kwargs)

  def order_by(self, *args, **kwargs):
    if 'username' in args:
      args = list(args)
      args.remove('username')
      args.append('email')

    return super(UserManager, self).order_by(*args, **kwargs)

  def filter(self, *args, **kwargs):
    f = super(UserManager, self).filter(*args, **kwargs)
    # f.values_list = self.values_list  # Patch so that chaining after a filter is backward compatible. However creates wrong result.
    return f

  def values_list(self, *args, **kwargs):
    if 'username' in args:
      args = list(args)
      args.remove('username')
      args.append('email')

    return super(UserManager, self).values_list(*args, **kwargs)

  def _create_user(self, email, password, **extra_fields):
    """Create and save a User with the given email and password."""
    if not extra_fields.get('organization'):
      extra_fields['organization'] = get_user_request_organization()
      if not extra_fields['organization']:
        extra_fields['organization'] = get_organization(email=email)

    if not email:
      raise ValueError('The given email must be set')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email=None, password=None, **extra_fields):
    """Create and save a regular User with the given email and password."""
    if extra_fields.get('username'):
      email = extra_fields.pop('username')

    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    extra_fields.setdefault('is_admin', False)

    return self._create_user(email, password, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    """Create and save a SuperUser with the given email and password."""
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    extra_fields.setdefault('is_admin', True)

    if extra_fields.get('is_staff') is not False:
      raise ValueError('Organization superuser must have is_staff=False.')
    if extra_fields.get('is_superuser') is not False:
      raise ValueError('Organization superuser must have is_superuser=False.')
    if extra_fields.get('is_admin') is not True:
      raise ValueError('Organization superuser must have is_admin=True.')

    return self._create_user(email, password, **extra_fields)


if ENABLE_ORGANIZATIONS.get():
  class OrganizationUser(AbstractUser):
    """User model in a multi tenant setup."""

    username = None
    email = models.EmailField(_t('Email address'), unique=True)
    token = models.CharField(_t('Token'), max_length=128, default=None, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        OrganizationGroup,
        verbose_name=_t('groups'),
        blank=True,
        help_text=_t(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
      return '%s @ %s' % (self.email, self.organization)

    @property
    def username(self):
      return self.email

    @property
    def username_short(self):
      return self.email.split('@')[0]

    @username.setter
    def username(self, value):
      pass
