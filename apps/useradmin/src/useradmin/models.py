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

A "Hue Permission" (colloquially, appname.action, but stored in the
HuePermission model) is a way to specify some action whose
control may be restricted.  Every Hue application, by default,
has an "access" action.  To specify extra actions, applications
can specify them in appname.settings.PERMISSION_ACTIONS, as
pairs of (action_name, description).

Several mechanisms enforce permission.  First of all, the "access" permission
is controlled by LoginAndPermissionMiddleware.  For eligible views
within an application, the access permission is checked.  Second,
views may use @desktop.decorators.hue_permission_required("action", "app")
to annotate their function, and this decorator will check a permission.
Thirdly, you may wish to do so manually, by using something akin to:

  app = desktop.lib.apputil.get_current_app() # a string
  dp = HuePermission.objects.get(app=pp, action=action)
  request.user.has_hue_permission(dp)

[Design note: it is questionable that a Hue permission is
a model, instead of just being a string.  Could go either way.]

Permissions may be granted to groups, but not, currently, to users.
A user's abilities is the union of all permissions the group
has access to.

Note that Django itself has a notion of users, groups, and permissions.
We re-use Django's notion of users and groups, but ignore its notion of
permissions.  The permissions notion in Django is strongly tied to
what models you may or may not edit, and there are elaborations (especially
in Django 1.2) to manipulate this row by row.  This does not map nicely
onto actions which may not relate to database models.
"""
import logging
from datetime import datetime
from enum import Enum

from django.db import connection, models, transaction
from django.contrib.auth import models as auth_models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _t
import django.utils.timezone as dtz

from desktop import appmanager
from desktop.lib.exceptions_renderable import PopupException
from hadoop import cluster

import useradmin.conf

LOG = logging.getLogger(__name__)

class UserProfile(models.Model):
  """
  WARNING: Some of the columns in the UserProfile object have been added
  via south migration scripts. During an upgrade that modifies this model,
  the columns in the django ORM database will not match the
  actual object defined here, until the latest migration has been executed.
  The code that does the actual UserProfile population must reside in the most
  recent migration that modifies the UserProfile model.

  for user in User.objects.all():
    try:
      p = orm.UserProfile.objects.get(user=user)
    except orm.UserProfile.DoesNotExist:
      create_profile_for_user(user)

  IF ADDING A MIGRATION THAT MODIFIES THIS MODEL, MAKE SURE TO MOVE THIS CODE
  OUT OF THE CURRENT MIGRATION, AND INTO THE NEW ONE, OR UPGRADES WILL NOT WORK
  PROPERLY
  """
  # Enum for describing the creation method of a user.
  class CreationMethod(Enum):
    HUE = 1
    EXTERNAL = 2

  user = models.OneToOneField(auth_models.User, unique=True)
  home_directory = models.CharField(editable=True, max_length=1024, null=True)
  creation_method = models.CharField(editable=True, null=False, max_length=64, default=CreationMethod.HUE.name)
  first_login = models.BooleanField(default=True, verbose_name=_t('First Login'),
                                   help_text=_t('If this is users first login.'))
  last_activity = models.DateTimeField(auto_now=True, db_index=True)

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
        LOG.exception("Permission object %s - %s not available. Was syncdb run after installation?" % (app, action))
        return self.user.is_superuser
    if self.user.is_superuser:
      return True

    group_ids = self.user.groups.values_list('id', flat=True)
    return GroupPermission.objects.filter(group__id__in=group_ids, hue_permission=perm).exists()

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
      raise PopupException(_t("You do not have permissions to %(description)s.") % dict(description=perm.description))

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
    except UserProfile.DoesNotExist, e:
      profile = create_profile_for_user(user)
    user._cached_userman_profile = profile
    return profile

def group_has_permission(group, perm):
  return GroupPermission.objects.filter(group=group, hue_permission=perm).count() > 0

def group_permissions(group):
  return HuePermission.objects.filter(grouppermission__group=group).all()

# Create a user profile for the given user
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

class LdapGroup(models.Model):
  """
  Groups that come from LDAP originally will have an LdapGroup
  record generated at creation time.
  """
  group = models.ForeignKey(auth_models.Group, related_name="group")

class GroupPermission(models.Model):
  """
  Represents the permissions a group has.
  """
  group = models.ForeignKey(auth_models.Group)
  hue_permission = models.ForeignKey("HuePermission")


# Permission Management
class HuePermission(models.Model):
  """
  Set of non-object specific permissions that an app supports.

  For now, we only assign permissions to groups, though that may change.
  """
  app = models.CharField(max_length=30)
  action = models.CharField(max_length=100)
  description = models.CharField(max_length=255)

  groups = models.ManyToManyField(auth_models.Group, through=GroupPermission)

  def __str__(self):
    return "%s.%s:%s(%d)" % (self.app, self.action, self.description, self.pk)

  @classmethod
  def get_app_permission(cls, hue_app, action):
    return HuePermission.objects.get(app=hue_app, action=action)

def get_default_user_group(**kwargs):
  default_user_group = useradmin.conf.DEFAULT_USER_GROUP.get()
  if default_user_group is None:
    return None

  group, created = auth_models.Group.objects.get_or_create(name=default_user_group)
  if created:
    group.save()

  return group

def update_app_permissions(**kwargs):
  """
  Inserts missing permissions into the database table.
  This is a 'syncdb' callback.

  We never delete permissions automatically, because apps might come and go.

  Note that signing up to the "syncdb" signal is not necessarily
  the best thing we can do, since some apps might not
  have models, but nonetheless, "syncdb" is typically
  run when apps are installed.
  """
  # Map app->action->HuePermission.

  # The HuePermission model needs to be sync'd for the following code to work
  # The point of 'if u'useradmin_huepermission' in connection.introspection.table_names():'
  # is to check if Useradmin has been installed.
  # It is okay to follow appmanager.DESKTOP_APPS before they've been sync'd
  # because apps are referenced by app name in Hue permission and not by model ID.
  if u'useradmin_huepermission' in connection.introspection.table_names():
    current = {}

    try:
      for dp in HuePermission.objects.all():
        current.setdefault(dp.app, {})[dp.action] = dp
    except:
      LOG.exception('failed to get permissions')
      return

    updated = 0
    uptodate = 0
    added = [ ]

    for app_obj in appmanager.DESKTOP_APPS:
      app = app_obj.name
      actions = set([("access", "Launch this application")])
      actions.update(getattr(app_obj.settings, "PERMISSION_ACTIONS", []))

      if app not in current:
        current[app] = {}

      for action, description in actions:
        c = current[app].get(action)
        if c:
          if c.description != description:
            c.description = description
            c.save()
            updated += 1
          else:
            uptodate += 1
        else:
          new_dp = HuePermission(app=app, action=action, description=description)
          new_dp.save()
          added.append(new_dp)

    # Add all hue permissions to default group.
    default_group = get_default_user_group()
    if default_group:
      for new_dp in added:
        if not (new_dp.app == 'useradmin' and new_dp.action == 'access') and \
           not (new_dp.app == 'useradmin' and new_dp.action == 'superuser') and \
           not (new_dp.app == 'metastore' and new_dp.action == 'write') and \
           not (new_dp.app == 'hbase' and new_dp.action == 'write') and \
           not (new_dp.app == 'security' and new_dp.action == 'impersonate') and \
           not (new_dp.app == 'filebrowser' and new_dp.action == 's3_access') and \
           not (new_dp.app == 'filebrowser' and new_dp.action == 'adls_access') and \
           not (new_dp.app == 'oozie' and new_dp.action == 'disable_editor_access'):
          GroupPermission.objects.create(group=default_group, hue_permission=new_dp)

    available = HuePermission.objects.count()

    LOG.info("HuePermissions: %d added, %d updated, %d up to date, %d stale" %
           (len(added),
            updated,
            uptodate,
            available - len(added) - updated - uptodate))

models.signals.post_migrate.connect(update_app_permissions)
models.signals.post_migrate.connect(get_default_user_group)


def install_sample_user():
  """
  Setup the de-activated sample user with a certain id. Do not create a user profile.
  """
  #Moved to avoid circular import with is_admin
  from desktop.models import SAMPLE_USER_ID, SAMPLE_USER_INSTALL
  user = None

  try:
    if auth_models.User.objects.filter(id=SAMPLE_USER_ID).exists():
      user = auth_models.User.objects.get(id=SAMPLE_USER_ID)
      LOG.info('Sample user found with username "%s" and User ID: %s' % (user.username, user.id))
    elif auth_models.User.objects.filter(username=SAMPLE_USER_INSTALL).exists():
      user = auth_models.User.objects.get(username=SAMPLE_USER_INSTALL)
      LOG.info('Sample user found: %s' % user.username)
    else:
      user, created = auth_models.User.objects.get_or_create(
        username=SAMPLE_USER_INSTALL,
        password='!',
        is_active=False,
        is_superuser=False,
        id=SAMPLE_USER_ID,
        pk=SAMPLE_USER_ID)

      if created:
        LOG.info('Installed a user called "%s"' % SAMPLE_USER_INSTALL)

    if user.username != SAMPLE_USER_INSTALL:
      LOG.warn('Sample user does not have username "%s", will attempt to modify the username.' % SAMPLE_USER_INSTALL)
      with transaction.atomic():
        user = auth_models.User.objects.get(id=SAMPLE_USER_ID)
        user.username = SAMPLE_USER_INSTALL
        user.save()
  except Exception, ex:
    LOG.exception('Failed to get or create sample user')

  # If sample user doesn't belong to default group, add to default group
  default_group = get_default_user_group()
  if user is not None and default_group is not None and default_group not in user.groups.all():
    user.groups.add(default_group)
    user.save()

  fs = cluster.get_hdfs()
  # If home directory doesn't exist for sample user, create it
  try:
    if not fs.do_as_user(SAMPLE_USER_INSTALL, fs.get_home_dir):
      fs.do_as_user(SAMPLE_USER_INSTALL, fs.create_home_dir)
      LOG.info('Created home directory for user: %s' % SAMPLE_USER_INSTALL)
    else:
      LOG.info('Home directory already exists for user: %s' % SAMPLE_USER_INSTALL)
  except Exception, ex:
    LOG.exception('Failed to create home directory for user %s: %s' % (SAMPLE_USER_INSTALL, str(ex)))

  return user
