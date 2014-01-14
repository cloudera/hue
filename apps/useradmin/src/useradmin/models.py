#!/usr/bin/env python2.5
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
from enum import Enum
import logging

from django.db import connection, models
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext_lazy as _t

from desktop import appmanager
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import SAMPLE_USERNAME
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
  CreationMethod = Enum('HUE', 'EXTERNAL')

  user = models.ForeignKey(auth_models.User, unique=True)
  home_directory = models.CharField(editable=True, max_length=1024, null=True)
  creation_method = models.CharField(editable=True, null=False, max_length=64, default=CreationMethod.HUE)

  def get_groups(self):
    return self.user.groups.all()

  def _lookup_permission(self, app, action):
    return HuePermission.objects.get(app=app, action=action)

  def has_hue_permission(self, action=None, app=None, perm=None):
    if perm is None:
      try:
        perm = self._lookup_permission(app, action)
      except HuePermission.DoesNotExist:
        LOG.exception("Permission object %s - %s not available. Was syncdb run after installation?" % (app, action))
        return self.user.is_superuser
    if self.user.is_superuser:
      return True

    for group in self.user.groups.all():
      if group_has_permission(group, perm):
        return True
    return False

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
  p.home_directory = "/user/%s" % p.user.username
  try:
    p.save()
    return p
  except:
    LOG.debug("Failed to automatically create user profile.", exc_info=True)
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
  if default_user_group is not None:
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
           not (new_dp.app == 'metastore' and new_dp.action == 'read_only_access'):
          GroupPermission.objects.create(group=default_group, hue_permission=new_dp)

    available = HuePermission.objects.count()

    LOG.info("HuePermissions: %d added, %d updated, %d up to date, %d stale" %
           (len(added),
            updated,
            uptodate,
            available - len(added) - updated - uptodate))

models.signals.post_syncdb.connect(update_app_permissions)
models.signals.post_syncdb.connect(get_default_user_group)


def install_sample_user():
  """
  Setup the de-activated sample user with a certain id. Do not create a user profile.
  """

  try:
    user = auth_models.User.objects.get(username=SAMPLE_USERNAME)
  except auth_models.User.DoesNotExist:
    try:
      user = auth_models.User.objects.create(username=SAMPLE_USERNAME, password='!', is_active=False, is_superuser=False, id=1100713, pk=1100713)
      LOG.info('Installed a user called "%s"' % (SAMPLE_USERNAME,))
    except Exception, e:
      LOG.info('Sample user race condition: %s' % e)
      user = auth_models.User.objects.get(username=SAMPLE_USERNAME)
      LOG.info('Sample user race condition, got: %s' % user)

  fs = cluster.get_hdfs()
  fs.do_as_user(SAMPLE_USERNAME, fs.create_home_dir)

  return user
