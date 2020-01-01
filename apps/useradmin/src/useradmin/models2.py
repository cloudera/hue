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
import uuid

from django.contrib.auth.models import models, AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _t

from desktop.models import uuid_default


LOG = logging.getLogger(__name__)


'''
Organizations handle contained sets of setups (user, group, connectors).
'''

def default_organization():
  default_organization, created = Organization.objects.get_or_create(name='default')
  return default_organization

def get_organization(user):
  # TODO: depends on the logged-in user and its organization
  return default_organization()


def uuid_default():
  return str(uuid.uuid4())


class OrganizationManager(models.Manager):
  use_in_migrations = True

  def get_by_natural_key(self, name):
    return self.get(name=name)


class Organization(models.Model):
  name = models.CharField(max_length=200, help_text=_t("The name of the organization"), unique=True)
  uuid = models.CharField(default=uuid_default, max_length=36, unique=True)
  domain = models.CharField(max_length=200, help_text=_t("The domain name of the organization, e.g. gethue.com"), unique=True)
  is_active = models.BooleanField(default=True)
  is_multi_user = models.BooleanField(default=True)

  objects = OrganizationManager()

  def __str__(self):
    return self.name


class OrganizationGroupManager(models.Manager):

  def natural_key(self):
    return (self.organization, self.name,)


class OrganizationGroup(models.Model):
  name = models.CharField(_t('name'), max_length=80, unique=False)
  organization = models.ForeignKey(Organization)

  permissions = models.ManyToManyField(
      'HuePermission',
      verbose_name=_t('permissions'),
      blank=True,
  )

  objects = OrganizationGroupManager()

  class Meta:
    verbose_name = _t('organization group')
    verbose_name_plural = _t('organization groups')
    unique_together = ('name', 'organization',)

  def __str__(self):
    return '%s %s' % (self.organization, self.name)


class UserManager(BaseUserManager):
  """Define a model manager for User model with no username field."""

  use_in_migrations = True

  def _create_user(self, email, password, **extra_fields):
    """Create and save a User with the given email and password."""
    if not email:
      raise ValueError('The given email must be set')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password=None, **extra_fields):
    """Create and save a regular User with the given email and password."""
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
          'The groups this user belongs to. A user will get all permissions '
          'granted to each of their groups.'
      ),
      related_name="user_set",
      related_query_name="user",
  )

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  objects = UserManager()

  @property
  def username(self):
    return self.email

  @property
  def username_short(self):
    return self.email.split('@')[0]

  @username.setter
  def username(self, value):
    pass
