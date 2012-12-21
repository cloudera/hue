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
User management application.
"""

import pwd
import grp
import logging
import threading
import subprocess

import ldap_access
from ldap import LDAPError

from django.contrib.auth.models import User, Group
from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.forms.util import ErrorList
from django.shortcuts import redirect

from hadoop.fs.exceptions import WebHdfsException
from useradmin.models import HuePermission, UserProfile, LdapGroup
from useradmin.models import get_profile, get_default_user_group
from useradmin.forms import SyncLdapUsersGroupsForm, AddLdapGroupForm,\
  AddLdapUserForm, PermissionsEditForm, GroupEditForm, SuperUserChangeForm,\
  UserChangeForm


LOG = logging.getLogger(__name__)

__users_lock = threading.Lock()
__groups_lock = threading.Lock()



def list_users(request):
  return render("list_users.mako", request, dict(users=User.objects.all(), request=request))


def list_groups(request):
  return render("list_groups.mako", request, dict(groups=Group.objects.all()))


def list_permissions(request):
  return render("list_permissions.mako", request, dict(permissions=HuePermission.objects.all()))


def delete_user(request, username):
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to delete users."), error_code=401)

  if request.method == 'POST':
    try:
      global __users_lock
      __users_lock.acquire()
      try:
        if username == request.user.username:
          raise PopupException(_("You cannot remove yourself."), error_code=401)
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.delete()
        user.delete()
      finally:
        __users_lock.release()

      request.info(_('The user was deleted.'))
      return redirect(reverse(list_users))
    except User.DoesNotExist:
      raise PopupException(_("User not found."), error_code=404)
  else:
    return render("delete_user.mako", request, dict(path=request.path, username=username))


def delete_group(request, name):
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to delete groups."), error_code=401)

  if request.method == 'POST':
    try:
      global groups_lock
      __groups_lock.acquire()
      try:
        # Get the default group before getting the group, because we may be
        # trying to delete the default group, and it may not have been created
        # yet
        default_group = get_default_user_group()
        group = Group.objects.get(name=name)
        if default_group is not None and default_group.name == name:
          raise PopupException(_("The default user group may not be deleted."), error_code=401)
        group.delete()
      finally:
        __groups_lock.release()

      request.info(_('The group was deleted.'))
      return redirect(reverse(list_groups))
    except Group.DoesNotExist:
      raise PopupException(_("Group not found."), error_code=404)
  else:
    return render("delete_group.mako", request, dict(path=request.path, groupname=name))


def edit_user(request, username=None):
  """
  edit_user(request, username = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type username:       string
  @param username:      Default to None, when creating a new user
  """
  if request.user.username != username and not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add or edit another user."), error_code=401)

  if username is not None:
    instance = User.objects.get(username=username)
  else:
    instance = None

  if request.user.is_superuser:
    form_class = SuperUserChangeForm
  else:
    form_class = UserChangeForm

  if request.method == 'POST':
    form = form_class(request.POST, instance=instance)
    if form.is_valid(): # All validation rules pass
      if instance is None:
        instance = form.save()
      else:
        #
        # Check for 3 more conditions:
        # (1) A user cannot inactivate oneself;
        # (2) Non-superuser cannot promote himself; and
        # (3) The last active superuser cannot demote/inactivate himself.
        #
        if request.user.username == username and not form.instance.is_active:
          raise PopupException(_("You cannot make yourself inactive."), error_code=401)

        global __users_lock
        __users_lock.acquire()
        try:
          # form.instance (and instance) now carry the new data
          orig = User.objects.get(username=username)
          if orig.is_superuser:
            if not form.instance.is_superuser or not form.instance.is_active:
              _check_remove_last_super(orig)
          else:
            if form.instance.is_superuser and not request.user.is_superuser:
              raise PopupException(_("You cannot make yourself a superuser."), error_code=401)

          # All ok
          form.save()
          request.info(_('User information updated'))
        finally:
          __users_lock.release()

      # Ensure home directory is created, if necessary.
      if form.cleaned_data['ensure_home_directory']:
        try:
          ensure_home_directory(request.fs, instance.username)
        except (IOError, WebHdfsException), e:
          request.error(_('Cannot make home directory for user %s.' % instance.username))
      if request.user.is_superuser:
        return redirect(reverse(list_users))
      else:
        return redirect(reverse(edit_user, kwargs={'username': username}))
  else:
    default_user_group = get_default_user_group()
    initial = {
      'ensure_home_directory': instance is None,
      'groups': default_user_group and [default_user_group] or []
    }
    form = form_class(instance=instance, initial=initial)

  return render('edit_user.mako', request, dict(form=form, username=username))


def edit_group(request, name=None):
  """
  edit_group(request, name = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type name:       string
  @param name:      Default to None, when creating a new group

  Only superusers may create a group
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add or edit a group."), error_code=401)

  if name is not None:
    instance = Group.objects.get(name=name)
  else:
    instance = None

  if request.method == 'POST':
    form = GroupEditForm(request.POST, instance=instance)
    if form.is_valid():
      form.save()
      request.info(_('Group information updated'))
      return list_groups(request)

  else:
    form = GroupEditForm(instance=instance)

  return render('edit_group.mako', request, dict(form=form, action=request.path, name=name))


def edit_permission(request, app=None, priv=None):
  """
  edit_permission(request, app = None, priv = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type app:       string
  @param app:      Default to None, specifies the app of the privilege
  @type priv:      string
  @param priv      Default to None, the action of the privilege

  Only superusers may modify permissions
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to change permissions."), error_code=401)

  instance = HuePermission.objects.get(app=app, action=priv)

  if request.method == 'POST':
    form = PermissionsEditForm(request.POST, instance=instance)
    if form.is_valid():
      form.save()
      request.info(_('Permission information updated'))
      return render("list_permissions.mako", request, dict(permissions=HuePermission.objects.all()))

  else:
    form = PermissionsEditForm(instance=instance)

  return render('edit_permissions.mako', request, dict(form=form, action=request.path, app=app, priv=priv))


def add_ldap_user(request):
  """
  add_ldap_user(request) -> reply

  Handler for importing LDAP users into the Hue database.

  If a user has been previously imported, this will sync their user information.
  If the LDAP request failed, the error message is generic right now.
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add another user."), error_code=401)

  if request.method == 'POST':
    form = AddLdapUserForm(request.POST)
    if form.is_valid():
      username = form.cleaned_data['username']
      import_by_dn = form.cleaned_data['dn']
      try:
        user = import_ldap_user(username, import_by_dn)
      except LDAPError, e:
        LOG.error("LDAP Exception: %s" % e)
        raise PopupException(_('There was an error when communicating with LDAP: %s') % str(e))

      if user and form.cleaned_data['ensure_home_directory']:
        try:
          ensure_home_directory(request.fs, user.username)
        except (IOError, WebHdfsException), e:
          request.error(_("Cannot make home directory for user %s." % user.username))

      if user is None:
        errors = form._errors.setdefault('username', ErrorList())
        errors.append(_('Could not get LDAP details for user %(username)s.') % dict(username=(username,)))
      else:
        return redirect(reverse(list_users))
  else:
    form = AddLdapUserForm()

  return render('add_ldap_user.mako', request, dict(form=form))


def add_ldap_group(request):
  """
  add_ldap_group(request) -> reply

  Handler for importing LDAP groups into the Hue database.

  If a group has been previously imported, this will sync membership within the
  group with the LDAP server. If --import-members is specified, it will import
  all unimported users.
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add another group."), error_code=401)

  if request.method == 'POST':
    form = AddLdapGroupForm(request.POST)
    if form.is_valid():
      groupname = form.cleaned_data['name']
      import_by_dn = form.cleaned_data['dn']
      import_members = form.cleaned_data['import_members']
      try:
        group = import_ldap_group(groupname, import_members, import_by_dn)
      except LDAPError, e:
        LOG.error("LDAP Exception: %s" % e)
        raise PopupException(_('There was an error when communicating with LDAP: %s') % str(e))

      if group is None:
        errors = form._errors.setdefault('name', ErrorList())
        errors.append(_('Could not get LDAP details for group %(groupname)s') % dict(groupname=(groupname,)))
      else:
        return redirect(reverse(list_groups))
  else:
    form = AddLdapGroupForm()

  return render('edit_group.mako', request, dict(form=form, action=request.path, ldap=True))


def sync_ldap_users_groups(request):
  """
  Handler for syncing the Hue database with LDAP users and groups.

  This will not import any users or groups that don't already exist in Hue. All
  user information and group memberships will be updated based on the LDAP
  server's current state.
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to sync the LDAP users/groups."), error_code=401)

  if request.method == 'POST':
    form = SyncLdapUsersGroupsForm(request.POST)
    if form.is_valid():
      try:
        users = sync_ldap_users()
        groups = sync_ldap_groups()
      except LDAPError:
        LOG.error("LDAP Exception: %s" % e)
        raise PopupException(_('There was an error when communicating with LDAP: %s') % str(e))

      # Create home dirs for every user sync'd
      if form.cleaned_data['ensure_home_directory']:
        for user in users:
          try:
            ensure_home_directory(request.fs, user.username)
          except (IOError, WebHdfsException), e:
            raise PopupException(_("The import may not be complete, sync again."), detail=e)
      return redirect(reverse(list_users))
  else:
    form = SyncLdapUsersGroupsForm()

  return render("sync_ldap_users_groups.mako", request, dict(path=request.path, form=form))


def ensure_home_directory(fs, username):
  """
  Adds a users home directory if it doesn't already exist.

  Throws IOError, WebHdfsException.
  """
  home_dir = '/user/%s' % username
  fs.do_as_user(username, fs.create_home_dir, home_dir)


def _check_remove_last_super(user_obj):
  """Raise an error if we're removing the last superuser"""
  if not user_obj.is_superuser:
    return

  # Is there any other active superuser left?
  all_active_su = User.objects.filter(is_superuser__exact = True,
                                      is_active__exact = True)
  num_active_su = all_active_su.count()
  assert num_active_su >= 1, _("No active superuser configured.")
  if num_active_su == 1:
    raise PopupException(_("You cannot remove the last active superuser from the configuration."), error_code=401)


def sync_unix_users_and_groups(min_uid, max_uid, min_gid, max_gid, check_shell):
  """
  Syncs the Hue database with the underlying Unix system, by importing users and
  groups from 'getent passwd' and 'getent groups'. This should also pull in
  users who are accessible via NSS.
  """
  global __users_lock, __groups_lock

  hadoop_groups = dict((group.gr_name, group) for group in grp.getgrall() \
      if (group.gr_gid >= min_gid and group.gr_gid < max_gid) or group.gr_name == 'hadoop')
  user_groups = dict()

  __users_lock.acquire()
  __groups_lock.acquire()
  # Import groups
  for name, group in hadoop_groups.iteritems():
    try:
      if len(group.gr_mem) != 0:
        hue_group = Group.objects.get(name=name)
    except Group.DoesNotExist:
      hue_group = Group(name=name)
      hue_group.save()
      LOG.info("Created group %s" % (hue_group.name,))

    # Build a map of user to groups that the user is a member of
    members = group.gr_mem
    for member in members:
      if member not in user_groups:
        user_groups[member] = [ hue_group ]
      else:
        user_groups[member].append(hue_group)

  # Now let's import the users
  hadoop_users = dict((user.pw_name, user) for user in pwd.getpwall() \
      if (user.pw_uid >= min_uid and user.pw_uid < max_uid) or user.pw_name in grp.getgrnam('hadoop').gr_mem)
  for username, user in hadoop_users.iteritems():
    try:
      if check_shell:
        pw_shell = user.pw_shell
        if subprocess.call([pw_shell, "-c", "echo"], stdout=subprocess.PIPE) != 0:
          continue
      hue_user = User.objects.get(username=username)
    except User.DoesNotExist:
      hue_user = User(username=username, password='!', is_active=True, is_superuser=False)
      hue_user.set_unusable_password()

    # We have to do a save here, because the user needs to exist before we can
    # access the associated list of groups
    hue_user.save()
    if username not in user_groups:
      hue_user.groups = []
    else:
      # Here's where that user to group map we built comes in handy
      hue_user.groups = user_groups[username]
    hue_user.save()
    LOG.info("Synced user %s from Unix" % (hue_user.username,))

  __users_lock.release()
  __groups_lock.release()


def _import_ldap_user(username, import_by_dn=False):
  """
  Import a user from LDAP. If import_by_dn is true, this will import the user by
  the distinguished name, rather than the configured username attribute.
  """
  conn = ldap_access.get_connection()
  user_info = conn.find_user(username, import_by_dn)
  if user_info is None:
    LOG.warn("Could not get LDAP details for user %s" % (username,))
    return None

  user, created = User.objects.get_or_create(username=user_info['username'])
  profile = get_profile(user)
  if not created and profile.creation_method == str(UserProfile.CreationMethod.HUE):
    # This is a Hue user, and shouldn't be overwritten
    LOG.warn('There was a naming conflict while importing user %s' % (username,))
    return None

  default_group = get_default_user_group()
  if created and default_group is not None:
    user.groups.add(default_group)

  if 'first' in user_info:
    user.first_name = user_info['first']
  if 'last' in user_info:
    user.last_name = user_info['last']
  if 'email' in user_info:
    user.email = user_info['email']

  profile.creation_method = UserProfile.CreationMethod.EXTERNAL
  profile.save()
  user.save()

  return user


def _import_ldap_group(groupname, import_members=False, import_by_dn=False):
  """
  Import a group from LDAP. If import_members is true, this will also import any
  LDAP users that exist within the group.
  """
  conn = ldap_access.get_connection()
  group_info = conn.find_group(groupname, import_by_dn)
  if group_info is None:
    LOG.warn("Could not get LDAP details for group %s" % (groupname,))
    return None

  group, created = Group.objects.get_or_create(name=group_info['name'])
  if not created and not LdapGroup.objects.filter(group=group).exists():
    # This is a Hue group, and shouldn't be overwritten
    LOG.warn('There was a naming conflict while importing group %s' % (groupname,))
    return None

  LdapGroup.objects.get_or_create(group=group)

  group.user_set.clear()
  for member in group_info['members']:
    if import_members:
      LOG.debug("Importing user %s" % (member,))
      user = _import_ldap_user(member, import_by_dn=True)
    else:
      user_info = conn.find_user(member, find_by_dn=True)
      try:
        user = User.objects.get(username=user_info['username'])
      except User.DoesNotExist:
        continue

    if user is None:
      # There was a naming conflict, or for some other reason, we couldn't get
      # at the user
      continue
    LOG.debug("Adding user %s to group %s" % (member, group.name))
    group.user_set.add(user)

  group.save()
  return group


def import_ldap_user(user, import_by_dn):
  return _import_ldap_user(user, import_by_dn)


def import_ldap_group(group, import_members, import_by_dn):
  return _import_ldap_group(group, import_members, import_by_dn)


def sync_ldap_users():
  """
  Syncs LDAP user information. This will not import new
  users from LDAP. It is also not possible to import both a user and a
  group at the same time. Each must be a separate operation. If neither a user,
  nor a group is provided, all users and groups will be synced.
  """
  users = User.objects.filter(userprofile__creation_method=str(UserProfile.CreationMethod.EXTERNAL)).all()
  for user in users:
    _import_ldap_user(user.username)
  return users


def sync_ldap_groups():
  """
  Syncs LDAP group memberships. This will not import new
  groups from LDAP. It is also not possible to import both a user and a
  group at the same time. Each must be a separate operation. If neither a user,
  nor a group is provided, all users and groups will be synced.
  """
  groups = Group.objects.filter(group__in=LdapGroup.objects.all())
  for group in groups:
    _import_ldap_group(group.name)
  return groups
