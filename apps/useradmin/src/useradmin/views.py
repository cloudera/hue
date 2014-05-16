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

import pwd
import grp
import logging
import threading
import subprocess
import json

import ldap
import ldap_access

from django.contrib.auth.models import User, Group
from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.forms.util import ErrorList
from django.shortcuts import redirect
from django.http import HttpResponse

import desktop.conf
from desktop.conf import LDAP
from hadoop.fs.exceptions import WebHdfsException
from useradmin.models import HuePermission, UserProfile, LdapGroup
from useradmin.models import get_profile, get_default_user_group
from useradmin.forms import SyncLdapUsersGroupsForm, AddLdapGroupsForm, AddLdapUsersForm,\
  PermissionsEditForm, GroupEditForm, SuperUserChangeForm, UserChangeForm



LOG = logging.getLogger(__name__)

__users_lock = threading.Lock()
__groups_lock = threading.Lock()


def list_users(request):
  is_ldap_setup = bool(LDAP.LDAP_SERVERS.get()) or LDAP.LDAP_URL.get() is not None
  return render("list_users.mako", request, {
      'users': User.objects.all(),
      'users_json': json.dumps(list(User.objects.values_list('id', flat=True))),
      'request': request,
      'is_ldap_setup': is_ldap_setup
  })


def list_groups(request):
  is_ldap_setup = bool(LDAP.LDAP_SERVERS.get()) or LDAP.LDAP_URL.get() is not None
  return render("list_groups.mako", request, {
      'groups': Group.objects.all(),
      'is_ldap_setup': is_ldap_setup
  })


def list_permissions(request):
  return render("list_permissions.mako", request, dict(permissions=HuePermission.objects.all()))


def list_for_autocomplete(request):
  # Restrict to what the current user can interact withreverse('desktop.views.home')
  if request.ajax:
    user_groups = request.user.groups.all()
    response = {
      'users': massage_users_for_json(User.objects.filter(groups__in=user_groups).exclude(pk=request.user.pk)),
      'groups': massage_groups_for_json(Group.objects.all())
    }
    return HttpResponse(json.dumps(response), mimetype="application/json")

  return HttpResponse("")


def massage_users_for_json(users):
  simple_users = []
  for user in users:
    simple_users.append({
      'id': user.id,
      'username': user.username,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email
    })
  return simple_users


def massage_groups_for_json(groups):
  simple_groups = []
  for group in groups:
    simple_groups.append({
      'id': group.id,
      'name': group.name
    })
  return simple_groups


def delete_user(request):
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to delete users."), error_code=401)

  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  ids = request.POST.getlist('user_ids')
  global __users_lock
  __users_lock.acquire()
  try:
    if str(request.user.id) in ids:
      raise PopupException(_("You cannot remove yourself."), error_code=401)

    UserProfile.objects.filter(user__id__in=ids).delete()
    User.objects.filter(id__in=ids).delete()
  finally:
    __users_lock.release()

  request.info(_('The users were deleted.'))
  return redirect(reverse(list_users))


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
        get_profile(instance)
      else:
        if username != form.instance.username:
          raise PopupException(_("You cannot change a username."), error_code=401)
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


def add_ldap_users(request):
  """
  add_ldap_users(request) -> reply

  Handler for importing LDAP users into the Hue database.

  If a user has been previously imported, this will sync their user information.
  If the LDAP request failed, the error message is generic right now.
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add another user."), error_code=401)

  if request.method == 'POST':
    form = AddLdapUsersForm(request.POST)
    if form.is_valid():
      username_pattern = form.cleaned_data['username_pattern']
      import_by_dn = form.cleaned_data['dn']
      server = form.cleaned_data.get('server')
      try:
        connection = ldap_access.get_connection_from_server(server)
        users = import_ldap_users(connection, username_pattern, False, import_by_dn)
      except ldap.LDAPError, e:
        LOG.error("LDAP Exception: %s" % e)
        raise PopupException(_('There was an error when communicating with LDAP'), detail=str(e))

      if users and form.cleaned_data['ensure_home_directory']:
        for user in users:
          try:
            ensure_home_directory(request.fs, user.username)
          except (IOError, WebHdfsException), e:
            request.error(_("Cannot make home directory for user %s." % user.username))

      if not users:
        errors = form._errors.setdefault('username_pattern', ErrorList())
        errors.append(_('Could not get LDAP details for users in pattern %s.') % username_pattern)
      else:
        return redirect(reverse(list_users))
  else:
    form = AddLdapUsersForm()

  return render('add_ldap_users.mako', request, dict(form=form))


def add_ldap_groups(request):
  """
  add_ldap_groups(request) -> reply

  Handler for importing LDAP groups into the Hue database.

  If a group has been previously imported, this will sync membership within the
  group with the LDAP server. If --import-members is specified, it will import
  all unimported users.
  """
  if not request.user.is_superuser:
    raise PopupException(_("You must be a superuser to add another group."), error_code=401)

  if request.method == 'POST':
    form = AddLdapGroupsForm(request.POST)
    if form.is_valid():
      groupname_pattern = form.cleaned_data['groupname_pattern']
      import_by_dn = form.cleaned_data['dn']
      import_members = form.cleaned_data['import_members']
      import_members_recursive = form.cleaned_data['import_members_recursive']
      server = form.cleaned_data.get('server')
      try:
        connection = ldap_access.get_connection_from_server(server)
        groups = import_ldap_groups(connection, groupname_pattern, import_members=import_members, import_members_recursive=import_members_recursive, sync_users=True, import_by_dn=import_by_dn)
      except ldap.LDAPError, e:
        LOG.error(_("LDAP Exception: %s") % e)
        raise PopupException(_('There was an error when communicating with LDAP'), detail=str(e))

      if groups:
        return redirect(reverse(list_groups))
      else:
        errors = form._errors.setdefault('groupname_pattern', ErrorList())
        errors.append(_('Could not get LDAP details for groups in pattern %s') % groupname_pattern)

  else:
    form = AddLdapGroupsForm()

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
      is_ensuring_home_directory = form.cleaned_data['ensure_home_directory']
      server = form.cleaned_data.get('server')
      connection = ldap_access.get_connection_from_server(server)
      sync_ldap_users_and_groups(connection, is_ensuring_home_directory, request.fs)
      return redirect(reverse(list_users))
  else:
    form = SyncLdapUsersGroupsForm()

  return render("sync_ldap_users_groups.mako", request, dict(path=request.path, form=form))

def sync_ldap_users_and_groups(connection, is_ensuring_home_directory=False, fs=None):
  try:
    users = sync_ldap_users(connection)
    groups = sync_ldap_groups(connection)
  except ldap.LDAPError, e:
    LOG.error("LDAP Exception: %s" % e)
    raise PopupException(_('There was an error when communicating with LDAP'), detail=str(e))

  # Create home dirs for every user sync'd
  if is_ensuring_home_directory:
    for user in users:
      try:
        ensure_home_directory(fs, user.username)
      except (IOError, WebHdfsException), e:
        raise PopupException(_("The import may not be complete, sync again."), detail=e)

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
    LOG.info(_("Synced user %s from Unix") % hue_user.username)

  __users_lock.release()
  __groups_lock.release()


def _import_ldap_users(connection, username_pattern, sync_groups=False, import_by_dn=False):
  """
  Import a user from LDAP. If import_by_dn is true, this will import the user by
  the distinguished name, rather than the configured username attribute.
  """
  user_info = connection.find_users(username_pattern, find_by_dn=import_by_dn)
  if not user_info:
    LOG.warn("Could not get LDAP details for users with pattern %s" % username_pattern)
    return None

  return _import_ldap_users_info(connection, user_info, sync_groups, import_by_dn)


def _import_ldap_users_info(connection, user_info, sync_groups=False, import_by_dn=False):
  """
  Import user_info found through ldap_access.find_users.
  """
  imported_users = []
  for ldap_info in user_info:
    user, created = ldap_access.get_or_create_ldap_user(username=ldap_info['username'])
    profile = get_profile(user)
    if not created and profile.creation_method == str(UserProfile.CreationMethod.HUE):
      # This is a Hue user, and shouldn't be overwritten
      LOG.warn(_('There was a naming conflict while importing user %(username)s') % {
        'username': ldap_info['username']
      })
      return None

    default_group = get_default_user_group()
    if created and default_group is not None:
      user.groups.add(default_group)

    if 'first' in ldap_info:
      user.first_name = ldap_info['first']
    if 'last' in ldap_info:
      user.last_name = ldap_info['last']
    if 'email' in ldap_info:
      user.email = ldap_info['email']

    profile.creation_method = UserProfile.CreationMethod.EXTERNAL
    profile.save()
    user.save()
    imported_users.append(user)

    # sync groups
    if sync_groups and 'groups' in ldap_info:
      old_groups = set(user.groups.all())
      new_groups = set()
      # Skip if 'memberOf' or 'isMemberOf' are not set
      for group_dn in ldap_info['groups']:
        group_ldap_info = connection.find_groups(group_dn, find_by_dn=True, scope=ldap.SCOPE_BASE)
        for group_info in group_ldap_info:
          # Add only if user isn't part of group.
          if not user.groups.filter(name=group_info['name']).exists():
            groups = import_ldap_groups(connection, group_info['dn'], import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=True)
            if groups:
              new_groups.update(groups)

      # Remove out of date groups
      remove_groups = old_groups - new_groups
      remove_ldap_groups = LdapGroup.objects.filter(group__in=remove_groups)
      remove_groups_filtered = [ldapgroup.group for ldapgroup in remove_ldap_groups]
      user.groups.filter(group__in=remove_groups_filtered).delete()
      user.groups.add(*new_groups)
      Group.objects.filter(group__in=remove_groups_filtered).delete()
      remove_ldap_groups.delete()

  return imported_users


def _import_ldap_members(connection, group, ldap_info, count=0, max_count=1):
  if count >= max_count:
    return None

  # Find all users and groups of group.
  users_info = connection.find_users_of_group(ldap_info['dn'])
  groups_info = connection.find_groups_of_group(ldap_info['dn'])
  posix_members = ldap_info['posix_members']

  for user_info in users_info:
    LOG.debug("Importing user %s into group %s" % (smart_str(user_info['dn']), smart_str(group.name)))
    users = _import_ldap_users(connection, smart_str(user_info['dn']), import_by_dn=True)
    group.user_set.add(*users)

  for group_info in groups_info:
    LOG.debug("Importing group %s" % smart_str(group_info['dn']))
    groups = _import_ldap_groups(connection, smart_str(group_info['dn']), import_by_dn=True)

    # Must find all members of subgroups
    if len(groups) > 1:
      LOG.warn('Found multiple groups for member %s.' % smart_str(group_info['dn']))
    else:
      for group in groups:
        _import_ldap_members(connection, group, group_info, count+1, max_count)

  for posix_member in posix_members:
    LOG.debug("Importing posix user %s into group %s" % (smart_str(posix_member), smart_str(group.name)))
    user_info = connection.find_users(posix_member, search_attr='uid', user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(), find_by_dn=False)
    users = _import_ldap_users_info(connection, user_info)

    if users:
      LOG.debug("Adding member %s represented as users (should be a single user) %s to group %s" % (str(posix_member), str(users), str(group.name)))
      group.user_set.add(*users)


def _sync_ldap_members(connection, group, ldap_info, count=0, max_count=1):
  if count >= max_count:
    return None

  # Find all users and groups of group.
  users_info = connection.find_users_of_group(ldap_info['dn'])
  groups_info = connection.find_groups_of_group(ldap_info['dn'])
  posix_members = ldap_info['posix_members']

  for user_info in users_info:
    LOG.debug("Synchronizing user %s with group %s" % (smart_str(user_info['dn']), smart_str(group.name)))
    try:
      user = ldap_access.get_ldap_user(username=user_info['username'])
      group.user_set.add(user)
    except User.DoesNotExist:
      LOG.debug("Synchronizing user %s with group %s failed. User does not exist." % (smart_str(user_info['dn']), smart_str(group.name)))

  for group_info in groups_info:
    LOG.debug("Synchronizing group %s" % smart_str(group_info['dn']))

    try:
      group = Group.objects.get(name=group_info['name'])
      _sync_ldap_members(connection, group, group_info, count+1, max_count)
    except Group.DoesNotExist:
      LOG.debug("Synchronizing group %s failed. Group does not exist." % smart_str(group.name))

  for posix_member in posix_members:
    LOG.debug("Synchronizing posix user %s with group %s" % (smart_str(posix_member), smart_str(group.name)))
    users_info = connection.find_users(posix_member, search_attr='uid', user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(), find_by_dn=False)
    for user_info in users_info:
      try:
        user = ldap_access.get_ldap_user(username=user_info['username'])
        group.user_set.add(user)
      except User.DoesNotExist:
        LOG.debug("Synchronizing posix user %s with group %s failed. User does not exist." % (smart_str(posix_member), smart_str(group.name)))


def _import_ldap_nested_groups(connection, groupname_pattern, import_members=False, recursive_import_members=False, sync_users=True, import_by_dn=False):
  """
  Import a group from LDAP. If import_members is true, this will also import any
  LDAP users that exist within the group. This will use nested groups logic.
  A nested group is a group that is a member of another group.
  e.g. CN=subtest,OU=groups,DC=exampe,DC=COM is a member of CN=test,OU=groups,DC=exampe,DC=COM
  and they both of the object class "groupOfNames" (or some other object class for groups).
  """
  if import_by_dn:
    scope = ldap.SCOPE_BASE
  else:
    scope = ldap.SCOPE_SUBTREE
  group_info = connection.find_groups(groupname_pattern, find_by_dn=import_by_dn, scope=scope)

  if not group_info:
    LOG.warn("Could not get LDAP details for group pattern %s" % groupname_pattern)
    return None

  groups = []
  for ldap_info in group_info:
    group, created = Group.objects.get_or_create(name=ldap_info['name'])
    if not created and not LdapGroup.objects.filter(group=group).exists():
      # This is a Hue group, and shouldn't be overwritten
      LOG.warn(_('There was a naming conflict while importing group %(groupname)s in pattern %(groupname_pattern)s') % {
        'groupname': ldap_info['name'],
        'groupname_pattern': groupname_pattern
      })
      return None

    LdapGroup.objects.get_or_create(group=group)
    group.user_set.clear()

    # Find members and posix members for group and subgoups
    # Import users and groups
    max_count = recursive_import_members and desktop.conf.LDAP.NESTED_MEMBERS_SEARCH_DEPTH.get() or 1

    if import_members:
      _import_ldap_members(connection, group, ldap_info, max_count=max_count)

    # Sync users
    if sync_users:
      _sync_ldap_members(connection, group, ldap_info, max_count=max_count)

    group.save()
    groups.append(group)

  return groups


def _import_ldap_suboordinate_groups(connection, groupname_pattern, import_members=False, recursive_import_members=False, sync_users=True, import_by_dn=False):
  """
  Import a group from LDAP. If import_members is true, this will also import any
  LDAP users that exist within the group. This will use suboordinate group logic.
  A suboordinate group is a group that is a subentry of another group.
  e.g. CN=subtest,CN=test,OU=groups,DC=exampe,DC=COM is a suboordinate group of
  CN=test,OU=groups,DC=exampe,DC=COM
  """
  if import_by_dn:
    scope = ldap.SCOPE_BASE
  else:
    scope = ldap.SCOPE_SUBTREE
  group_info = connection.find_groups(groupname_pattern, find_by_dn=import_by_dn, scope=scope)

  if not group_info:
    LOG.warn("Could not get LDAP details for group pattern %s" % groupname_pattern)
    return None

  groups = []
  for ldap_info in group_info:
    group, created = Group.objects.get_or_create(name=ldap_info['name'])
    if not created and not LdapGroup.objects.filter(group=group).exists():
      # This is a Hue group, and shouldn't be overwritten
      LOG.warn(_('There was a naming conflict while importing group %(groupname)s in pattern %(groupname_pattern)s') % {
        'groupname': ldap_info['name'],
        'groupname_pattern': groupname_pattern
      })
      return None

    LdapGroup.objects.get_or_create(group=group)
    group.user_set.clear()

    # Find members and posix members for group and subgoups
    members = ldap_info['members']
    posix_members = ldap_info['posix_members']

    # @TODO: Deprecate recursive_import_members as it may not be useful.
    if import_members:
      if recursive_import_members:
        for sub_ldap_info in connection.find_groups(ldap_info['dn'], find_by_dn=True):
          members += sub_ldap_info['members']
          posix_members += sub_ldap_info['posix_members']

      for member in members:
        LOG.debug("Importing user %s" % smart_str(member))
        group.user_set.add( *( _import_ldap_users(connection, member, import_by_dn=True) or [] ) )

    # Sync users
    if sync_users:
      for member in members:
        user_info = connection.find_users(member, find_by_dn=True)
        if len(user_info) > 1:
          LOG.warn('Found multiple users for member %s.' % member)
        else:
          for ldap_info in user_info:
            try:
              user = ldap_access.get_ldap_user(username=ldap_info['username'])
              group.user_set.add(user)
            except User.DoesNotExist:
              pass

    # Import/fetch posix users and groups
    # Posix members
    if posix_members:
      if import_members:
        for posix_member in posix_members:
          LOG.debug("Importing user %s" % str(posix_member))
          # posixGroup class defines 'memberUid' to be login names,
          # which are defined by 'uid'.
          user_info = connection.find_users(posix_member, search_attr='uid', user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(), find_by_dn=False)
          users = _import_ldap_users_info(connection, user_info, import_by_dn=False)

          if users:
            LOG.debug("Adding member %s represented as users (should be a single user) %s to group %s" % (str(posix_member), str(users), str(group.name)))
            group.user_set.add(*users)

      if sync_users:
        for posix_member in posix_members:
          user_info = connection.find_users(posix_member, search_attr='uid', user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(), find_by_dn=False)
          if len(user_info) > 1:
            LOG.warn('Found multiple users for member %s.' % posix_member)
          else:
            for ldap_info in user_info:
              try:
                user = ldap_access.get_ldap_user(username=ldap_info['username'])
                group.user_set.add(user)
              except User.DoesNotExist:
                pass

    group.save()
    groups.append(group)

  return groups


def _import_ldap_groups(connection, groupname_pattern, import_members=False, recursive_import_members=False, sync_users=True, import_by_dn=False):
  """
  Import a group from LDAP. If import_members is true, this will also import any
  LDAP users that exist within the group.
  """
  if desktop.conf.LDAP.SUBGROUPS.get().lower() == 'suboordinate':
    return _import_ldap_suboordinate_groups(connection=connection,
                                            groupname_pattern=groupname_pattern,
                                            import_members=import_members,
                                            recursive_import_members=recursive_import_members,
                                            sync_users=sync_users,
                                            import_by_dn=import_by_dn)
  else:
    return _import_ldap_nested_groups(connection=connection,
                                      groupname_pattern=groupname_pattern,
                                      import_members=import_members,
                                      recursive_import_members=recursive_import_members,
                                      sync_users=sync_users,
                                      import_by_dn=import_by_dn)


def import_ldap_users(connection, user_pattern, sync_groups, import_by_dn):
  return _import_ldap_users(connection, user_pattern, sync_groups=sync_groups, import_by_dn=import_by_dn)


def import_ldap_groups(connection, group_pattern, import_members, import_members_recursive, sync_users, import_by_dn):
  return _import_ldap_groups(connection, group_pattern, import_members, import_members_recursive, sync_users, import_by_dn)


def sync_ldap_users(connection):
  """
  Syncs LDAP user information. This will not import new
  users from LDAP. It is also not possible to import both a user and a
  group at the same time. Each must be a separate operation. If neither a user,
  nor a group is provided, all users and groups will be synced.
  """
  users = User.objects.filter(userprofile__creation_method=str(UserProfile.CreationMethod.EXTERNAL)).all()
  for user in users:
    _import_ldap_users(connection, user.username)
  return users


def sync_ldap_groups(connection):
  """
  Syncs LDAP group memberships. This will not import new
  groups from LDAP. It is also not possible to import both a user and a
  group at the same time. Each must be a separate operation. If neither a user,
  nor a group is provided, all users and groups will be synced.
  """
  groups = Group.objects.filter(group__in=LdapGroup.objects.all())
  for group in groups:
    _import_ldap_groups(connection, group.name)
  return groups
