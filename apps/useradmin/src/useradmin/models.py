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
The core of this module adds permissions functionality to Hue applications.

A "Hue Permission" (colloquially, appname.action, but stored in the HuePermission model) is a way to specify some action whose
control may be restricted. Every Hue application, by default, has an "access" action. To specify extra actions, applications
can specify them in appname.settings.PERMISSION_ACTIONS, as pairs of (action_name, description).

Several mechanisms enforce permission. First of all, the "access" permission
is controlled by LoginAndPermissionMiddleware. For eligible views within an application, the access permission is checked. Second,
views may use @desktop.decorators.hue_permission_required("action", "app") to annotate their function, and this decorator will
check a permission. Thirdly, you may wish to do so manually, by using something akin to:

  app = desktop.lib.apputil.get_current_app() # a string
  dp = HuePermission.objects.get(app=pp, action=action)
  request.user.has_hue_permission(dp)

Permissions may be granted to groups, but not, currently, to users. A user's abilities is the union of all permissions the group
has access to.

Note that Django itself has a notion of users, groups, and permissions. We re-use Django's notion of users and groups, but ignore its
notion of permissions. The permissions notion in Django is strongly tied to what models you may or may not edit, and there are
elaborations to manipulate this row by row. This does not map nicely onto actions which may not relate to database models.
"""
import collections
import json
import logging
import sys

from datetime import datetime
from enum import Enum

from django.db import connection, models, transaction
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.cache import cache
from django.utils import timezone as dtz

from desktop import appmanager
from desktop.conf import ENABLE_ORGANIZATIONS, ENABLE_CONNECTORS
from desktop.lib.connectors.models import _get_installed_connectors, Connector
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.idbroker.conf import is_idbroker_enabled
from desktop.monkey_patches import monkey_patch_username_validator

from useradmin.conf import DEFAULT_USER_GROUP
from useradmin.permissions import HuePermission, GroupPermission, LdapGroup

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t
else:
  from django.utils.translation import ugettext_lazy as _t

if ENABLE_ORGANIZATIONS.get():
  from useradmin.organization import OrganizationUser as User, OrganizationGroup as Group, get_organization, Organization
else:
  from django.contrib.auth.models import User, Group
  def get_organization(): pass
  class Organization(): pass

  monkey_patch_username_validator()


LOG = logging.getLogger()


class UserProfile(models.Model):
  """
  Extra settings / properties to store for each user.
  """
  class CreationMethod(Enum):
    HUE = 1
    EXTERNAL = 2

  user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
  home_directory = models.CharField(editable=True, max_length=1024, null=True)
  creation_method = models.CharField(editable=True, null=False, max_length=64, default=CreationMethod.HUE.name)
  first_login = models.BooleanField(default=True, verbose_name=_t('First Login'), help_text=_t('If this is users first login.'))
  last_activity = models.DateTimeField(auto_now=True, db_index=True)
  hostname = models.CharField(editable=True, max_length=255, null=True)
  json_data = models.TextField(default='{}')

  def get_groups(self):
    return self.user.groups.all()

  def _lookup_permission(self, app, action):
    # We cache it instead of doing HuePermission.objects.get(app=app, action=action). To revert with Django 1.6
    perms = cache.get('perms')
    if not perms:
      perms = dict([('%s:%s' % (p.app, p.action), p) for p in HuePermission.objects.all()])
      cache.set('perms', perms, 60 * 60)
    return perms.get('%s:%s' % (app, action))

  def has_hue_permission(self, action=None, app=None, perm=None):
    if perm is None:
      try:
        perm = self._lookup_permission(app, action)
      except HuePermission.DoesNotExist:
        LOG.exception("Permission object %s - %s not available. Was Django migrate command run after installation?" % (app, action))
        return self.user.is_superuser
    if self.user.is_superuser:
      return True
    if ENABLE_CONNECTORS.get() and app in ('jobbrowser', 'metastore', 'filebrowser', 'indexer', 'useradmin', 'notebook'):
      if app == 'useradmin' and action in ('superuser', 'access_view:useradmin:edit_user'):  # Not implemented yet
        return False
      else:
        return True

    group_ids = self.user.groups.values_list('id', flat=True)
    return GroupPermission.objects.filter(group__id__in=group_ids, hue_permission=perm).exists()

  def get_permissions(self):
    return HuePermission.objects.filter(groups__user=self.user)

  def check_hue_permission(self, perm=None, app=None, action=None):
    """
    Raises a PopupException if permission is denied.

    Either perm or both app and action are required.
    """
    if perm is None:
      perm = self._lookup_permission(app, action)
    if self.has_hue_permission(perm):
      return
    else:
      raise PopupException(_t("You do not have permissions to %(description)s.") % {'description': perm.description})

  @property
  def data(self):
    if not self.json_data:
      self.json_data = json.dumps({})
    return json.loads(self.json_data)

  def update_data(self, val):
    data_dict = self.data
    data_dict.update(val)
    self.json_data = json.dumps(data_dict)


def get_profile(user):
  """
  Caches the profile, to avoid DB queries at every call.
  """
  if hasattr(user, "_cached_userman_profile"):
    return user._cached_userman_profile
  else:
    # Lazily create profile.
    try:
      profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as e:
      profile = create_profile_for_user(user)
    user._cached_userman_profile = profile
    return profile

def group_has_permission(group, perm):
  return GroupPermission.objects.filter(group=group, hue_permission=perm).exists()

def group_permissions(group):
  return HuePermission.objects.filter(grouppermission__group=group).all()


def create_profile_for_user(user):
  p = UserProfile()
  p.user = user
  p.last_activity = dtz.now()
  p.home_directory = "/user/%s" % p.user.username
  try:
    p.save()
    return p
  except:
    LOG.exception("Failed to automatically create user profile.")
    return None


def get_default_user_group(**kwargs):
  default_user_group = DEFAULT_USER_GROUP.get()
  if default_user_group is None:
    return None

  attributes = {
    'name': default_user_group
  }
  if ENABLE_ORGANIZATIONS.get() and kwargs.get('user'):
    attributes['organization'] = kwargs['user'].organization

  group, created = Group.objects.get_or_create(**attributes)

  if created:
    group.save()

  return group


def update_app_permissions(**kwargs):
  """
  Keep in sync apps and connectors permissions into the database table.
  Map app + action to a HuePermission.

  v2
  Based on the connectors.
  Permissions are either based on connectors instances or Hue specific actions.
  Permissions can be deleted or added dynamically.

  v1
  This is a 'migrate' callback.

  We never delete permissions automatically, because apps might come and go.

  Note that signing up to the "migrate" signal is not necessarily the best thing we can do, since some apps might not
  have models, but nonetheless, "migrate" is typically run when apps are installed.
  """
  created_tables = connection.introspection.table_names()

  if ENABLE_ORGANIZATIONS.get() and 'useradmin_organization' not in created_tables:
    return

  if u'useradmin_huepermission' in created_tables:  # Check if Useradmin has been installed.
    current = {}

    try:
      for dp in HuePermission.objects.all():
        current.setdefault(dp.app, {})[dp.action] = dp
    except:
      LOG.exception('failed to get permissions')
      return

    updated = 0
    uptodate = 0
    added = []

    if ENABLE_CONNECTORS.get():
      old_apps = list(current.keys())
      ConnectorPerm = collections.namedtuple('ConnectorPerm', 'name nice_name settings')
      apps = [
        ConnectorPerm(name=connector['name'], nice_name=connector['nice_name'], settings=[])
        for connector in _get_installed_connectors()
      ]
    else:
      old_apps = []
      apps = appmanager.DESKTOP_APPS

    for app in apps:
      app_name = app.name
      permission_description = "Access the %s connection" % app.nice_name if ENABLE_CONNECTORS.get() else "Launch this application"
      actions = set([("access", permission_description)])
      actions.update(getattr(app.settings, "PERMISSION_ACTIONS", []))

      if app_name not in current:
        current[app_name] = {}
      if app_name in old_apps:
        old_apps.remove(app_name)

      for action, description in actions:
        c = current[app_name].get(action)
        if c:
          if c.description != description:
            c.description = description
            c.save()
            updated += 1
          else:
            uptodate += 1
        else:
          new_dp = HuePermission(app=app_name, action=action, description=description)
          if ENABLE_CONNECTORS.get():
            new_dp.connector = Connector.objects.get(id=app_name)
          new_dp.save()
          added.append(new_dp)

    # Only with v2
    deleted, _ = HuePermission.objects.filter(app__in=old_apps).delete()

    # Add all permissions to default group except some.
    default_group = get_default_user_group()
    if default_group:
      for new_dp in added:
        if not (new_dp.app == 'useradmin' and new_dp.action == 'access') and \
            not (new_dp.app == 'useradmin' and new_dp.action == 'superuser') and \
            not (new_dp.app == 'metastore' and new_dp.action == 'write') and \
            not (new_dp.app == 'hbase' and new_dp.action == 'write') and \
            not (new_dp.app == 'security' and new_dp.action == 'impersonate') and \
            not (new_dp.app == 'filebrowser' and new_dp.action == 's3_access' and not is_idbroker_enabled('s3a')) and \
            not (new_dp.app == 'filebrowser' and new_dp.action == 'gs_access' and not is_idbroker_enabled('gs')) and \
            not (new_dp.app == 'filebrowser' and new_dp.action == 'adls_access') and \
            not (new_dp.app == 'filebrowser' and new_dp.action == 'abfs_access') and \
            not (new_dp.app == 'filebrowser' and new_dp.action == 'ofs_access') and \
            not (new_dp.app == 'oozie' and new_dp.action == 'disable_editor_access'):
          GroupPermission.objects.create(group=default_group, hue_permission=new_dp)

    available = HuePermission.objects.count()
    stale = available - len(added) - updated - uptodate

    if len(added) or updated or stale or deleted:
      LOG.info("HuePermissions: %d added, %d updated, %d up to date, %d stale, %d deleted" % (
          len(added), updated, uptodate, stale, deleted
        )
      )


if not ENABLE_CONNECTORS.get():
  models.signals.post_migrate.connect(update_app_permissions)
# models.signals.post_migrate.connect(get_default_user_group)


def install_sample_user(django_user=None):
  """
  Setup the de-activated sample user with a certain id. Do not create a user profile.
  """
  from desktop.models import SAMPLE_USER_ID, get_sample_user_install
  from hadoop import cluster

  user = None
  django_username = get_sample_user_install(django_user)

  if ENABLE_ORGANIZATIONS.get():
    lookup = {'email': django_username}
    django_username_short = django_user.username_short if django_user else 'hue'
  else:
    lookup = {'username': django_username}
    django_username_short = django_username

  try:
    if User.objects.filter(id=SAMPLE_USER_ID).exists() and not ENABLE_ORGANIZATIONS.get():
      user = User.objects.get(id=SAMPLE_USER_ID)
      LOG.info('Sample user found with username "%s" and User ID: %s' % (user.username, user.id))
    elif User.objects.filter(**lookup).exists():
      user = User.objects.get(**lookup)
      LOG.info('Sample user found: %s' % lookup)
    else:
      user_attributes = lookup.copy()
      if ENABLE_ORGANIZATIONS.get():
        user_attributes['organization'] = get_organization(email=django_username)
      else:
        user_attributes['id'] = SAMPLE_USER_ID

      user_attributes.update({
        'password': '!',
        'is_active': False,
        'is_superuser': False,
      })
      user, created = User.objects.get_or_create(**user_attributes)

      if created:
        LOG.info('Installed a user "%s"' % lookup)

    if user.username != django_username and not ENABLE_ORGANIZATIONS.get():
      LOG.warning('Sample user does not have username "%s", will attempt to modify the username.' % django_username)
      with transaction.atomic():
        user = User.objects.get(id=SAMPLE_USER_ID)
        user.username = django_username
        user.save()
  except:
    LOG.exception('Failed to get or create sample user')

  # If sample user doesn't belong to default group, add to default group
  default_group = get_default_user_group(user=user)
  if user is not None and default_group is not None and default_group not in user.groups.all():
    user.groups.add(default_group)
    user.save()

  # If home directory doesn't exist for sample user, create it
  fs = cluster.get_hdfs()
  try:
    if not fs:
      LOG.info('No fs configured, skipping home directory creation for user: %s' % django_username_short)
    elif not fs.do_as_user(django_username_short, fs.get_home_dir):
      fs.do_as_user(django_username_short, fs.create_home_dir)
      LOG.info('Created home directory for user: %s' % django_username_short)
    else:
      LOG.info('Home directory already exists for user: %s' % django_username)
  except Exception as ex:
    LOG.exception('Failed to create home directory for user %s: %s' % (django_username, str(ex)))

  return user
