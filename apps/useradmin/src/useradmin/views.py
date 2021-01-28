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

from __future__ import absolute_import
from builtins import map
import pwd
import grp
import logging
import subprocess
import sys
import json

LOG = logging.getLogger(__name__)

from axes.conf import settings
from axes.models import AccessAttempt
from axes.utils import reset
try:
  import ldap
except ImportError:
  LOG.warn('ldap module not found')

from django.urls import reverse
from django.forms import ValidationError
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.encoding import smart_str
from django.utils.translation import get_language, ugettext as _

import desktop.conf
from desktop.auth.backend import is_admin
from desktop.conf import LDAP, ENABLE_ORGANIZATIONS, ENABLE_CONNECTORS, ENABLE_SHARING
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import _get_apps
from desktop.views import antixss, serve_403_error
from hadoop.fs.exceptions import WebHdfsException

from useradmin import ldap_access
from useradmin.forms import SyncLdapUsersGroupsForm, AddLdapGroupsForm, AddLdapUsersForm, \
  PermissionsEditForm, GroupEditForm, SuperUserChangeForm, validate_username, validate_first_name, \
  validate_last_name, PasswordChangeForm
from useradmin.ldap_access import LdapBindException, LdapSearchException
from useradmin.models import HuePermission, UserProfile, LdapGroup, get_profile, get_default_user_group, User, Group, Organization

if sys.version_info[0] > 2:
  unicode = str

if ENABLE_ORGANIZATIONS.get():
  from useradmin.forms import OrganizationUserChangeForm as UserChangeForm, OrganizationSuperUserChangeForm as SuperUserChangeForm
else:
  from useradmin.forms import UserChangeForm, SuperUserChangeForm


def is_ldap_setup():
  return bool(LDAP.LDAP_SERVERS.get()) or LDAP.LDAP_URL.get() is not None


def list_users(request):
  return render("list_users.mako", request, {
      'users': User.objects.all(),
      'users_json': json.dumps(list(User.objects.values_list('id', flat=True))),
      'request': request,
      'is_embeddable': request.GET.get('is_embeddable', False),
      'is_ldap_setup': is_ldap_setup()
  })


def list_groups(request):
  return render("list_groups.mako", request, {
      'groups': Group.objects.all(),
      'groups_json': json.dumps(list(Group.objects.values_list('name', flat=True))),
      'is_embeddable': request.GET.get('is_embeddable', False),
      'is_ldap_setup': is_ldap_setup()
  })


def list_permissions(request):
  if ENABLE_CONNECTORS.get():
    permissions = HuePermission.objects.all()
  else:
    current_app, other_apps, apps_list = _get_apps(request.user)
    permissions = HuePermission.objects.filter(app__in=apps_list)

  return render("list_permissions.mako", request, {
    'permissions': permissions,
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def list_configurations(request):
  return render("list_configurations.mako", request, {
    'is_embeddable': request.GET.get('is_embeddable', False)
  })


def list_organizations(request):
  return render("list_organizations.mako", request, {
      'groups': Organization.objects.all(),
      'groups_json': json.dumps(list(Organization.objects.values_list('name', flat=True))),
      'is_embeddable': request.GET.get('is_embeddable', False),
  })


def list_for_autocomplete(request):
  extended_user_object = request.GET.get('extend_user') == 'true'
  autocomplete_filter = request.GET.get('filter', "")
  count = int(request.GET.get("count", 100))

  if is_admin(request.user):
    if ENABLE_ORGANIZATIONS.get():
      users = User.objects.filter(email__icontains=autocomplete_filter).order_by('email')
    else:
      users = User.objects.filter(username__icontains=autocomplete_filter).order_by('username')
    groups = Group.objects.filter(name__icontains=autocomplete_filter).order_by('name')
    if request.GET.get('only_mygroups'):
      groups = request.user.groups.filter(name__icontains=autocomplete_filter).order_by('name')
  elif not ENABLE_SHARING.get():
    return serve_403_error(request)
  else:
    usergroups = request.user.groups.all()
    # Get all users in the usergroups he belongs to and then filter by username
    if ENABLE_ORGANIZATIONS.get():
      users = User.objects.filter(groups__in=usergroups, email__icontains=autocomplete_filter).order_by('email').distinct()
    else:
      users = User.objects.filter(groups__in=usergroups, username__icontains=autocomplete_filter).order_by('username').distinct()
    groups = usergroups.filter(name__icontains=autocomplete_filter).order_by('name')

  # Don't include myself by default
  if not request.GET.get('include_myself'):
    users = users.exclude(pk=request.user.pk)

  users = users[:count]
  groups = groups[:count]

  response = {
    'users': massage_users_for_json(users, extended_user_object),
    'groups': massage_groups_for_json(groups)
  }
  return JsonResponse(response)


def get_users_by_id(request):
  if not is_admin(request.user) and not ENABLE_SHARING.get():
    return serve_403_error(request)

  userids = json.loads(request.GET.get('userids', "[]"))
  userids = userids[:100]
  users = User.objects.filter(id__in=userids).order_by('email' if ENABLE_ORGANIZATIONS.get() else 'username')
  response = {
    'users': massage_users_for_json(users)
  }
  return JsonResponse(response)


def massage_users_for_json(users, extended=False):
  simple_users = []
  for user in users:
    appendable = {
      'id': user.id,
      'username': user.username,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'last_login': user.last_login,
      'editURL': reverse('useradmin:useradmin.views.edit_user', kwargs={'username': user.username})
    }
    if extended:
      appendable['groups'] = massage_groups_for_json(user.groups.all())
    simple_users.append(appendable)
  return simple_users


def massage_groups_for_json(groups):
  simple_groups = []
  for group in groups:
    simple_groups.append({
      'id': group.id,
      'name': group.name
    })
  return simple_groups


def is_user_locked_out(username):
  attempts = AccessAttempt.objects.filter(username=username)
  return any(attempt.failures_since_start >= settings.AXES_FAILURE_LIMIT and settings.AXES_LOCK_OUT_AT_FAILURE for attempt in attempts)


def delete_user(request):
  if not is_admin(request.user):
    request.audit = {
      'operation': 'DELETE_USER',
      'operationText': _get_failed_operation_text(request.user.username, 'DELETE_USER'),
      'allowed': False
    }
    raise PopupException(_("You must be a superuser to delete users."), error_code=401)

  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  ids = request.POST.getlist('user_ids')
  is_delete = request.POST.get('is_delete')
  action_text = _('deleted') if is_delete else _('deactivated')

  if str(request.user.id) in ids:
    raise PopupException(_("You cannot remove yourself."), error_code=401)

  users = User.objects.filter(id__in=ids)
  usernames = list(users.values_list('username', flat=True))

  if is_delete:
    UserProfile.objects.filter(user__id__in=ids).delete()
    users.delete()
  else:
    users.update(is_active=False)

  request.audit = {
    'operation': 'DELETE_USER',
    'operationText': '%s User(s): %s' % (action_text.title(), ', '.join(usernames))
  }

  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if is_embeddable:
    return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_users')})
  else:
    request.info(_('The users were %s.') % action_text)
    return redirect(reverse('useradmin:useradmin.views.list_users'))


def delete_group(request):
  if not is_admin(request.user):
    request.audit = {
      'operation': 'DELETE_GROUP',
       'operationText': _get_failed_operation_text(request.user.username, 'DELETE_GROUP'),
      'allowed': False
    }
    raise PopupException(_("You must be a superuser to delete groups."), error_code=401)

  if request.method == 'POST':
    try:
      group_names = request.POST.getlist('group_names')
      # Get the default group before getting the group, because we may be
      # trying to delete the default group, and it may not have been created yet.
      default_group = get_default_user_group()
      if default_group is not None and default_group.name in group_names:
        raise PopupException(_("The default user group may not be deleted."), error_code=401)
      Group.objects.filter(name__in=group_names).delete()

      request.audit = {
        'operation': 'DELETE_GROUP',
        'operationText': 'Deleted Group(s): %s' % ', '.join(group_names)
      }
      is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

      if is_embeddable:
        return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_groups')})
      else:
        request.info(_('The groups were deleted.'))
        return redirect(reverse('useradmin:useradmin.views.list_groups'))
    except Group.DoesNotExist:
      raise PopupException(_("Group not found."), error_code=404)
  else:
    return render("delete_group.mako", request, {'path': request.path})


def require_change_password(self):
  """ Return true if user has never logged in before. """
  if 'desktop.auth.backend.AllowFirstUserDjangoBackend' in desktop.conf.AUTH.BACKEND.get() and \
     self.first_login and desktop.conf.AUTH.CHANGE_DEFAULT_PASSWORD.get():
    return True


def edit_user(request, username=None):
  """
  edit_user(request, username = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type username:       string
  @param username:      Default to None, when creating a new user
  """
  if request.user.username != username and not is_admin(request.user):
    request.audit = {'allowed': False}
    if username is not None:
      request.audit['operation'] = 'EDIT_USER'
      request.audit['operationText'] = _get_failed_operation_text(request.user.username, 'EDIT_USER')
    else:
      request.audit['operation'] = 'CREATE_USER'
      request.audit['operationText'] = _get_failed_operation_text(request.user.username, 'CREATE_USER')
    raise PopupException(_("You must be a superuser to add or edit another user."), error_code=401)

  userprofile = get_profile(request.user)
  updated = False
  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if username is not None:
    instance = User.objects.get(username=username)
  else:
    instance = None

  if require_change_password(userprofile):
    form_class = PasswordChangeForm
  elif is_admin(request.user):
    form_class = SuperUserChangeForm
  else:
    form_class = UserChangeForm

  if request.method == 'POST':
    form = form_class(request.POST, instance=instance)
    if is_admin(request.user) and request.user.username != username:
      form.fields.pop("password_old")

    if form.is_valid():
      if instance is None:
        instance = form.save()
        get_profile(instance)
      else:
        if username != form.instance.username:
          raise PopupException(_("You cannot change a username."), error_code=401)
        if request.user.username == username and not form.instance.is_active:
          raise PopupException(_("You cannot make yourself inactive."), error_code=401)

        # User changing his own information, form.changed_data=['ensure_home_directory', 'language']
        # or changing information about another user, form.changed_data=['ensure_home_directory']
        updated = (
          request.user.username == username and len(form.changed_data) > 2) or (
          request.user.username != username and len(form.changed_data) > 1
        )

        # form.instance (and instance) now carry the new data
        orig = User.objects.get(username=username)
        if orig.is_superuser:
          if not form.instance.is_superuser or not form.instance.is_active:
            _check_remove_last_super(orig)
        else:
          if form.instance.is_superuser and not is_admin(request.user):
            raise PopupException(_("You cannot make yourself a superuser."), error_code=401)

        form.save()

        if form.cleaned_data.get('unlock_account'):
          if not is_admin(request.user):
            raise PopupException(_('You must be a superuser to reset users.'), error_code=401)

          try:
            reset(username=username)
            request.info(_('Successfully unlocked account for user: %s') % username)
          except Exception as e:
            raise PopupException(_('Failed to reset login attempts for %s: %s') % (username, str(e)))

      # Ensure home directory is created, if necessary.
      if form.cleaned_data.get('ensure_home_directory'):
        try:
          ensure_home_directory(request.fs, instance)
        except (IOError, WebHdfsException) as e:
          request.error(_('Cannot make home directory for user %s.') % instance.username)
        else:
          updated = True

      # Change language preference, if necessary
      if form.cleaned_data.get('language') and form.cleaned_data.get('language') != get_language():
        request.session['django_language'] = form.cleaned_data.get('language')
        updated = True

      if updated and not is_embeddable:
        request.info(_('User information updated'))

      # Audit log
      if username is not None:
        request.audit = {
          'operation': 'EDIT_USER',
          'operationText': 'Edited User with username: %s' % username
        }
      else:
        request.audit = {
          'operation': 'CREATE_USER',
          'operationText': 'Created User with username: %s' % instance.username
        }

      if require_change_password(userprofile):
        userprofile.first_login = False
        userprofile.save()

        if is_admin(request.user):
          return redirect(reverse('about:index'))
        else:
          return JsonResponse({'url': '/hue'})
      elif is_admin(request.user):
        if is_embeddable:
          return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_users')})
        else:
          return redirect(reverse('useradmin:useradmin.views.list_users'))
      else:
        if is_embeddable:
          return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.edit_user', kwargs={'username': username})})
        else:
          return redirect(reverse('useradmin:useradmin.views.edit_user', kwargs={'username': username}))
  else:
    # Initialize form values
    default_user_group = get_default_user_group()
    initial = {
      'language': request.session.get('django_language', get_language()),
      'ensure_home_directory': instance is None,
      'groups': default_user_group and [default_user_group] or []
    }
    form = form_class(instance=instance, initial=initial)

    if is_admin(request.user) and request.user.username != username:
      form.fields.pop("password_old")

  if require_change_password(userprofile):
    return render('change_password.mako', request, {
      'form': form,
      'username': username,
      'is_embeddable': is_embeddable
    })
  else:
    if request.method == 'POST' and is_embeddable:
      return JsonResponse({'status': -1,
                           'errors': [{'id': f.id_for_label, 'message': list(map(antixss, f.errors))} for f in form if
                                      f.errors]})
    else:
      return render('edit_user.mako', request, {
        'form': form,
        'username': username,
        'is_embeddable': is_embeddable
      })


def edit_group(request, name=None):
  """
  edit_group(request, name = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type name:       string
  @param name:      Default to None, when creating a new group

  Only superusers may create a group
  """
  if not is_admin(request.user):
    request.audit = {'allowed': False}
    if name is not None:
      request.audit['operation'] = 'EDIT_GROUP'
      request.audit['operationText'] = _get_failed_operation_text(request.user.username, 'EDIT_GROUP')
    else:
      request.audit['operation'] = 'CREATE_GROUP'
      request.audit['operationText'] = _get_failed_operation_text(request.user.username, 'CREATE_GROUP')

    raise PopupException(_("You must be a superuser to add or edit a group."), error_code=401)

  if name is not None:
    instance = Group.objects.get(name=name)
  else:
    instance = None

  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if request.method == 'POST':
    form = GroupEditForm(request.POST, instance=instance)

    if form.is_valid():
      form.save()

      if name is not None:
        usernames = instance.user_set.all().values_list('username', flat=True)
        request.audit = {
          'operation': 'EDIT_GROUP',
          'operationText': 'Edited Group: %s, with member(s): %s' % (
            name, ', '.join([user.username for diffs in form._compute_diff("members") for user in diffs])
          )
        }
      else:
        user_ids = request.POST.getlist('members', [])
        usernames = User.objects.filter(pk__in=user_ids).values_list('username', flat=True)
        request.audit = {
          'operation': 'CREATE_GROUP',
          'operationText': 'Created Group: %s, with member(s): %s' % (request.POST.get('name', ''), ', '.join(usernames))
        }

      if is_embeddable:
        return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_groups')})
      else:
        request.info(_('Group information updated'))
        return redirect('/useradmin/groups')
  else:
    form = GroupEditForm(instance=instance)

  if request.method == 'POST' and is_embeddable:
    return JsonResponse({
      'status': -1,
      'errors': [{'id': f.id_for_label, 'message': f.errors} for f in form if f.errors]
    })
  else:
    return render('edit_group.mako', request, {
      'form': form,
      'action': request.path,
      'name': name,
      'is_embeddable': is_embeddable,
    })


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
  if not is_admin(request.user):
    request.audit = {
      'operation': 'EDIT_PERMISSION',
      'operationText': _get_failed_operation_text(request.user.username, 'EDIT_PERMISSION'),
      'allowed': False
    }
    raise PopupException(_("You must be a superuser to change permissions."), error_code=401)

  instance = HuePermission.objects.get(app=app, action=priv)
  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if request.method == 'POST':
    form = PermissionsEditForm(request.POST, instance=instance)
    if form.is_valid():
      form.save()
      request.audit = {
        'operation': 'EDIT_PERMISSION',
        'operationText': 'Successfully edited permissions: %(app)s/%(priv)s' % {'app': app, 'priv': priv}
      }

      if is_embeddable:
        return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_permissions')})
      else:
        request.info(_('Permission information updated'))
        return redirect(reverse('useradmin:useradmin.views.list_permissions'))
  else:
    form = PermissionsEditForm(instance=instance)
  if request.method == 'POST' and is_embeddable:
    return JsonResponse(
        {'status': -1, 'errors': [{'id': f.id_for_label, 'message': f.errors} for f in form if f.errors]}
    )
  else:
    return render('edit_permissions.mako', request, {
      'form': form,
      'action': request.path,
      'app': app,
      'priv': priv,
      'is_embeddable': is_embeddable,
    })


def add_ldap_users(request):
  """
  add_ldap_users(request) -> reply

  Handler for importing LDAP users into the Hue database.

  If a user has been previously imported, this will sync their user information.
  If the LDAP request failed, the error message is generic right now.
  """
  if not is_admin(request.user):
    request.audit = {
      'operation': 'ADD_LDAP_USERS',
      'operationText': _get_failed_operation_text(request.user.username, 'ADD_LDAP_USERS'),
      'allowed': False,
    }
    raise PopupException(_("You must be a superuser to add another user."), error_code=401)

  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if request.method == 'POST':
    form = AddLdapUsersForm(request.POST)
    if form.is_valid():
      username_pattern = smart_str(form.cleaned_data['username_pattern'])
      import_by_dn = form.cleaned_data['dn']
      server = form.cleaned_data.get('server')
      try:
        failed_ldap_users = []
        connection = ldap_access.get_connection_from_server(server)
        users = import_ldap_users(connection, username_pattern, False, import_by_dn, failed_users=failed_ldap_users)
      except (ldap.LDAPError, LdapBindException) as e:
        LOG.error("LDAP Exception: %s" % smart_str(e))
        raise PopupException(smart_str(_('There was an error when communicating with LDAP: %s')) % str(e))
      except ValidationError as e:
        LOG.error("LDAP Exception: %s" % smart_str(e))
        raise PopupException(smart_str(_('There was a problem with some of the LDAP information: %s')) % str(e))

      if users and form.cleaned_data['ensure_home_directory']:
        for user in users:
          try:
            ensure_home_directory(request.fs, user)
          except (IOError, WebHdfsException) as e:
            request.error(_("Cannot make home directory for user %s.") % user.username)

      if not users:
        errors = form._errors.setdefault('username_pattern', ErrorList())
        errors.append(_('Could not get LDAP details for users in pattern %s.') % username_pattern)
      else:
        request.audit = {
          'operation': 'ADD_LDAP_USERS',
          'operationText': 'Added/Synced LDAP username(s): %s' % username_pattern
        }

        if failed_ldap_users:
          unique_users = set(failed_ldap_users)
          request.warn(_('Failed to import following users: %s') % ', '.join(unique_users))

        if is_embeddable:
          return JsonResponse({'status': 0})
        else:
          return redirect(reverse('useradmin:useradmin.views.list_users'))
  else:
    form = AddLdapUsersForm()

  if request.method == 'POST' and is_embeddable:
    return JsonResponse(
      {'status': -1, 'errors': [{'id': f.id_for_label, 'message': f.errors} for f in form if f.errors]})
  else:
    return render('add_ldap_users.mako', request, dict(form=form, is_embeddable=is_embeddable))


def add_ldap_groups(request):
  """
  add_ldap_groups(request) -> reply

  Handler for importing LDAP groups into the Hue database.

  If a group has been previously imported, this will sync membership within the
  group with the LDAP server. If --import-members is specified, it will import
  all unimported users.
  """
  if not is_admin(request.user):
    request.audit = {
      'operation': 'ADD_LDAP_GROUPS',
      'operationText': _get_failed_operation_text(request.user.username, 'ADD_LDAP_GROUPS'),
      'allowed': False,
    }
    raise PopupException(_("You must be a superuser to add another group."), error_code=401)

  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if request.method == 'POST':
    form = AddLdapGroupsForm(request.POST)
    if form.is_valid():
      groupname_pattern = form.cleaned_data['groupname_pattern']
      import_by_dn = form.cleaned_data['dn']
      import_members = form.cleaned_data['import_members']
      import_members_recursive = form.cleaned_data['import_members_recursive']
      is_ensuring_home_directories = form.cleaned_data['ensure_home_directories']
      server = form.cleaned_data.get('server')

      try:
        failed_ldap_users = []
        connection = ldap_access.get_connection_from_server(server)
        groups = import_ldap_groups(connection, groupname_pattern, import_members=import_members,
                                    import_members_recursive=import_members_recursive, sync_users=True,
                                    import_by_dn=import_by_dn, failed_users=failed_ldap_users)
      except (ldap.LDAPError, LdapBindException) as e:
        LOG.error("LDAP Exception: %s" % smart_str(e))
        raise PopupException(smart_str(_('There was an error when communicating with LDAP: %s')) % str(e))
      except ValidationError as e:
        LOG.error("LDAP Exception: %s" % smart_str(e))
        raise PopupException(smart_str(_('There was a problem with some of the LDAP information: %s')) % str(e))

      unique_users = set()
      if is_ensuring_home_directories and groups:
        for group in groups:
          for user in group.user_set.all():
            unique_users.add(user)
        for user in unique_users:
          try:
            ensure_home_directory(request.fs, user)
          except (IOError, WebHdfsException) as e:
            raise PopupException(_("Exception creating home directory for LDAP user %s in group %s.") % (user, group), detail=e)

      if groups:
        request.audit = {
          'operation': 'ADD_LDAP_GROUPS',
          'operationText': 'Added LDAP Group(s): %s' % groupname_pattern
        }

        if failed_ldap_users:
          unique_users = set(failed_ldap_users)
          request.warn(_('Failed to import following users: %s') % ', '.join(unique_users))

        if is_embeddable:
          return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_groups')})
        else:
          return redirect(reverse('useradmin:useradmin.views.list_groups'))

      else:
        errors = form._errors.setdefault('groupname_pattern', ErrorList())
        errors.append(_('Could not get LDAP details for groups in pattern %s') % groupname_pattern)

  else:
    form = AddLdapGroupsForm()

  if request.method == 'POST' and is_embeddable:
    return JsonResponse(
        {'status': -1, 'errors': [{'id': f.id_for_label, 'message': f.errors} for f in form if f.errors]}
    )
  else:
    return render('edit_group.mako', request, dict(form=form, action=request.path, ldap=True, is_embeddable=is_embeddable))


def sync_ldap_users_groups(request):
  """
  Handler for syncing the Hue database with LDAP users and groups.

  This will not import any users or groups that don't already exist in Hue. All
  user information and group memberships will be updated based on the LDAP
  server's current state.
  """
  if not is_admin(request.user):
    request.audit = {
      'operation': 'SYNC_LDAP_USERS_GROUPS',
      'operationText': _get_failed_operation_text(request.user.username, 'SYNC_LDAP_USERS_GROUPS'),
      'allowed': False
    }
    raise PopupException(_("You must be a superuser to sync the LDAP users/groups."), error_code=401)

  is_embeddable = request.GET.get('is_embeddable', request.POST.get('is_embeddable', False))

  if request.method == 'POST':
    form = SyncLdapUsersGroupsForm(request.POST)
    if form.is_valid():
      is_ensuring_home_directory = form.cleaned_data['ensure_home_directory']
      server = form.cleaned_data.get('server')
      try:
        connection = ldap_access.get_connection_from_server(server)
      except (ldap.LDAPError, LdapBindException) as e:
        LOG.error("LDAP Exception: %s" % smart_str(e))
        raise PopupException(smart_str(_('There was an error when communicating with LDAP: %s')) % str(e))

      failed_ldap_users = []

      sync_ldap_users_and_groups(connection, is_ensuring_home_directory, request.fs, failed_users=failed_ldap_users)

      request.audit = {
        'operation': 'SYNC_LDAP_USERS_GROUPS',
        'operationText': 'Successfully synced LDAP users/groups'
      }

      if failed_ldap_users:
        unique_users = set(failed_ldap_users)
        request.warn(_('Failed to import following users: %s') % ', '.join(unique_users))

      if is_embeddable:
        return JsonResponse({'url': '/hue' + reverse('useradmin:useradmin.views.list_users')})
      else:
        return redirect(reverse('useradmin:useradmin.views.list_users'))
  else:
    form = SyncLdapUsersGroupsForm()

  if request.method == 'POST' and is_embeddable:
    return JsonResponse(
        {'status': -1, 'errors': [{'id': f.id_for_label, 'message': f.errors} for f in form if f.errors]}
    )
  else:
    return render("sync_ldap_users_groups.mako", request, dict(path=request.path, form=form, is_embeddable=is_embeddable))


def sync_ldap_users_and_groups(connection, is_ensuring_home_directory=False, fs=None, failed_users=None):
  try:
    users = sync_ldap_users(connection, failed_users=failed_users)
    groups = sync_ldap_groups(connection, failed_users=failed_users)
  except (ldap.LDAPError, LdapBindException) as e:
    LOG.error("LDAP Exception: %s" % smart_str(e))
    raise PopupException(smart_str(_('There was an error when communicating with LDAP: %s')) % str(e))

  # Create home dirs for every user sync'd
  if is_ensuring_home_directory:
    for user in users:
      try:
        ensure_home_directory(fs, user)
      except (IOError, WebHdfsException) as e:
        raise PopupException(_("The import may not be complete, sync again."), detail=e)


def import_ldap_users(connection, user_pattern, sync_groups, import_by_dn, server=None, failed_users=None):
  return _import_ldap_users(
      connection, user_pattern, sync_groups=sync_groups, import_by_dn=import_by_dn, server=server, failed_users=failed_users
  )


def import_ldap_groups(connection, group_pattern, import_members, import_members_recursive, sync_users, import_by_dn, failed_users=None):
  return _import_ldap_groups(
      connection, group_pattern, import_members, import_members_recursive, sync_users, import_by_dn, failed_users=failed_users
  )


def get_find_groups_filter(ldap_info, server=None):
  return _get_find_groups_filter(ldap_info, server=server)


def sync_ldap_users(connection, failed_users=None):
  """
  Syncs LDAP user information. This will not import new
  users from LDAP. It is also not possible to import both a user and a
  group at the same time. Each must be a separate operation. If neither a user,
  nor a group is provided, all users and groups will be synced.
  """
  users = User.objects.filter(userprofile__creation_method=UserProfile.CreationMethod.EXTERNAL.name).all()
  for user in users:
    _import_ldap_users(connection, smart_str(user.username), failed_users=failed_users)
  return users


def sync_ldap_groups(connection, failed_users=None):
  """
  Syncs LDAP group memberships. This will not import new
  groups from LDAP. It is also not possible to import both a user and a
  group at the same time. Each must be a separate operation. If neither a user,
  nor a group is provided, all users and groups will be synced.
  """
  groups = Group.objects.filter(group__in=LdapGroup.objects.all())
  for group in groups:
    _import_ldap_groups(connection, group.name, failed_users=failed_users)
  return groups


def ensure_home_directory(fs, user):
  """
  Adds a users home directory if it doesn't already exist.

  Throws IOError, WebHdfsException.
  """
  if fs is None:
    LOG.warn("Not creating home directory of %s as no file system connector is configured" % user)
    return

  userprofile = get_profile(user)
  username = user.username
  home_directory = userprofile.home_directory

  if is_ldap_setup():
    username = user.username.split('@')[0]
    home_directory = userprofile.home_directory.split('@')[0]

  if userprofile is not None and userprofile.home_directory:
    if not isinstance(home_directory, unicode):
      home_directory = home_directory.decode("utf-8")
    fs.do_as_user(username, fs.create_home_dir, home_directory)
  else:
    LOG.warn("Not creating home directory of %s as his profile is empty" % user)

def sync_unix_users_and_groups(min_uid, max_uid, min_gid, max_gid, check_shell):
  """
  Syncs the Hue database with the underlying Unix system, by importing users and
  groups from 'getent passwd' and 'getent groups'. This should also pull in
  users who are accessible via NSS.
  """
  hadoop_groups = dict((group.gr_name, group) for group in grp.getgrall() \
      if (group.gr_gid >= min_gid and group.gr_gid < max_gid) or group.gr_name == 'hadoop')
  user_groups = dict()

  # Import groups
  for name, group in hadoop_groups.items():
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
        user_groups[member] = [hue_group]
      else:
        user_groups[member].append(hue_group)

  # Now let's import the users
  hadoop_users = dict((user.pw_name, user) for user in pwd.getpwall() \
      if (user.pw_uid >= min_uid and user.pw_uid < max_uid) or user.pw_name in grp.getgrnam('hadoop').gr_mem)
  for username, user in hadoop_users.items():
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


def _check_remove_last_super(user_obj):
  """Raise an error if we're removing the last superuser"""
  """We could actually check the entire super group as well"""
  if not user_obj.is_superuser:
    return

  # Is there any other active superuser left?
  all_active_su = User.objects.filter(is_superuser__exact=True, is_active__exact=True)
  num_active_su = all_active_su.count()

  if num_active_su < 1:
    raise PopupException(_("No active superuser configured."))
  if num_active_su == 1:
    raise PopupException(_("You cannot remove the last active superuser from the configuration."), error_code=401)


def _import_ldap_users(connection, username_pattern, sync_groups=False, import_by_dn=False, server=None, failed_users=None):
  """
  Import a user from LDAP. If import_by_dn is true, this will import the user by
  the distinguished name, rather than the configured username attribute.
  """
  user_info = None
  try:
    user_info = connection.find_users(username_pattern, find_by_dn=import_by_dn)
  except LdapSearchException as e:
    LOG.warn("Failed to find LDAP user: %s" % e)

  if not user_info:
    LOG.warn("Could not get LDAP details for users with pattern %s" % username_pattern)
    return None

  return _import_ldap_users_info(connection, user_info, sync_groups, import_by_dn, server, failed_users=failed_users)


def _get_find_groups_filter(ldap_info, server=None):
  if desktop.conf.LDAP.LDAP_SERVERS.get():
    # Choose from multiple server configs
    ldap_config = desktop.conf.LDAP.LDAP_SERVERS.get()[server]
  else:
    ldap_config = desktop.conf.LDAP

  group_member_attr = ldap_config.GROUPS.GROUP_MEMBER_ATTR.get()
  group_filter = ldap_config.GROUPS.GROUP_FILTER.get()
  # Search for groups based on group_member_attr=username and group_member_attr=dn
  # covers AD, Standard Ldap and posixAcount/posixGroup
  if not group_filter.startswith('('):
    group_filter = '(' + group_filter + ')'

  # Sanitizing the DN before using in a Search filter
  sanitized_dn = ldap.filter.escape_filter_chars(ldap_info['dn']).replace(r'\2a', r'*')
  sanitized_dn = sanitized_dn.replace(r'\5c,', r'\5c\2c')

  find_groups_filter = "(&" + group_filter + "(|(" + group_member_attr + "=" + ldap_info['username'] + ")(" + \
                       group_member_attr + "=" + sanitized_dn + ")))"

  return find_groups_filter


def _import_ldap_users_info(connection, user_info, sync_groups=False, import_by_dn=False, server=None, failed_users=None):
  """
  Import user_info found through ldap_access.find_users.
  """
  imported_users = []

  for ldap_info in user_info:
    # Extra validation in case import by DN and username has spaces or colons
    try:
      validate_username(ldap_info['username'])

      user, created = ldap_access.get_or_create_ldap_user(username=ldap_info['username'])
      profile = get_profile(user)
      if not created and profile.creation_method == UserProfile.CreationMethod.HUE.name:
        # This is a Hue user, and shouldn't be overwritten
        LOG.warn(_('There was a naming conflict while importing user %(username)s') % {
          'username': ldap_info['username']
        })
        return None

      default_group = get_default_user_group()
      if created and default_group is not None:
        user.groups.add(default_group)

      if 'first' in ldap_info:
        validate_first_name(ldap_info['first'])
        user.first_name = ldap_info['first']
      if 'last' in ldap_info:
        validate_last_name(ldap_info['last'])
        user.last_name = ldap_info['last']
      if 'email' in ldap_info:
        user.email = ldap_info['email']

      profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
      profile.save()
      user.save()
      imported_users.append(user)

      # sync groups
      if sync_groups:
        old_groups = set(user.groups.all())
        new_groups = set()
        current_ldap_groups = set()

        find_groups_filter = _get_find_groups_filter(ldap_info, server=server)

        group_ldap_info = connection.find_groups("*", group_filter=find_groups_filter)
        for group_info in group_ldap_info:
          if Group.objects.filter(name=group_info['name']).exists():
          # Add only if user isn't part of group.
            current_ldap_groups.add(Group.objects.get(name=group_info['name']))
            if not user.groups.filter(name=group_info['name']).exists():
              groups = import_ldap_groups(
                  connection, group_info['dn'], import_members=False, import_members_recursive=False,
                  sync_users=True, import_by_dn=True, failed_users=failed_users
              )
              if groups:
                new_groups.update(groups)
        # Remove out of date groups
        remove_groups = old_groups - current_ldap_groups
        remove_ldap_groups = LdapGroup.objects.filter(group__in=remove_groups)
        remove_groups_filtered = [ldapgroup.group for ldapgroup in remove_ldap_groups]
        for group in remove_groups_filtered:
          user.groups.remove(group)
        user.groups.add(*new_groups)
        Group.objects.filter(group__in=remove_groups_filtered).delete()
    except (ValidationError, LdapSearchException) as e:
      if failed_users is None:
        failed_users = []
      failed_users.append(ldap_info['username'])
      LOG.warn('Could not import %s: %s' % (ldap_info['username'], e.message))

  return imported_users


def _import_ldap_members(connection, group, ldap_info, count=0, max_count=1, failed_users=None):
  if count >= max_count:
    return None

  # Find all users and groups of group.
  users_info, groups_info = [], []

  try:
    users_info = connection.find_users_of_group(ldap_info['dn'])
  except LdapSearchException as e:
    LOG.warn("Failed to find LDAP users of group: %s" % e)

  try:
    groups_info = connection.find_groups_of_group(ldap_info['dn'])
  except LdapSearchException as e:
    LOG.warn("Failed to find LDAP groups of group: %s" % e)

  posix_members = ldap_info['posix_members']

  for user_info in users_info:
    LOG.debug("Importing user %s into group %s" % (smart_str(user_info['dn']), smart_str(group.name)))
    users = _import_ldap_users(connection, smart_str(user_info['dn']), import_by_dn=True, failed_users=None)
    group.user_set.add(*users)

  for group_info in groups_info:
    LOG.debug("Importing group %s" % smart_str(group_info['dn']))
    groups = _import_ldap_groups(connection, smart_str(group_info['dn']), import_by_dn=True, failed_users=None)

    # Must find all members of subgroups
    if len(groups) > 1:
      LOG.warn('Found multiple groups for member %s.' % smart_str(group_info['dn']))
    else:
      for group in groups:
        _import_ldap_members(connection, group, group_info, count+1, max_count, failed_users=failed_users)

  for posix_member in posix_members:
    LOG.debug("Importing posix user %s into group %s" % (smart_str(posix_member), smart_str(group.name)))
    user_info = None
    try:
      user_info = connection.find_users(posix_member, search_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(),
                                        user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(), find_by_dn=False)
    except LdapSearchException as e:
      LOG.warn("Failed to find LDAP users: %s" % e)

    if user_info:
      users = _import_ldap_users_info(connection, user_info, failed_users=failed_users)
      if users:
        LOG.debug("Adding member %s represented as users (should be a single user) %s to group %s" % (
        smart_str(posix_member), smart_str(users), smart_str(group.name)))
        group.user_set.add(*users)


def _sync_ldap_members(connection, group, ldap_info, count=0, max_count=1, failed_users=None):
  if count >= max_count:
    return None

  # Find all users and groups of group.
  users_info, groups_info = [], []

  try:
    users_info = connection.find_users_of_group(ldap_info['dn'])
  except LdapSearchException as e:
    LOG.warn("Failed to find LDAP users of group: %s" % e)

  try:
    groups_info = connection.find_groups_of_group(ldap_info['dn'])
  except LdapSearchException as e:
    LOG.warn("Failed to find LDAP groups of group: %s" % e)

  posix_members = ldap_info['posix_members']

  for user_info in users_info:
    LOG.debug("Synchronizing user %s with group %s" % (smart_str(user_info['dn']), smart_str(group.name)))
    try:
      user = ldap_access.get_ldap_user(username=user_info['username'])
      group.user_set.add(user)
    except User.DoesNotExist:
      LOG.warn("Synchronizing user %s with group %s failed. User does not exist." % (
      smart_str(user_info['dn']), smart_str(group.name)))

  for group_info in groups_info:
    LOG.debug("Synchronizing group %s" % smart_str(group_info['dn']))

    try:
      group = Group.objects.get(name=group_info['name'])
      _sync_ldap_members(connection, group, group_info, count+1, max_count, failed_users=failed_users)
    except Group.DoesNotExist:
      LOG.warn("Synchronizing group %s failed. Group does not exist." % smart_str(group.name))

  for posix_member in posix_members:
    LOG.debug("Synchronizing posix user %s with group %s" % (smart_str(posix_member), smart_str(group.name)))
    users_info = []
    try:
      users_info = connection.find_users(posix_member, search_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(),
                                         user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(), find_by_dn=False)
    except LdapSearchException as e:
      LOG.warn("Failed to find LDAP users: %s" % e)

    for user_info in users_info:
      try:
        user = ldap_access.get_ldap_user(username=user_info['username'])
        group.user_set.add(user)
      except User.DoesNotExist:
        LOG.warn("Synchronizing posix user %s with group %s failed. User does not exist." % (
        smart_str(posix_member), smart_str(group.name)))


def _import_ldap_nested_groups(connection, groupname_pattern, import_members=False, recursive_import_members=False,
                               sync_users=True, import_by_dn=False, failed_users=None):
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

  group_info = None
  try:
    group_info = connection.find_groups(groupname_pattern, find_by_dn=import_by_dn, scope=scope)
  except LdapSearchException as e:
    LOG.warn("Failed to find LDAP group: %s" % e)

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
      _import_ldap_members(connection, group, ldap_info, max_count=max_count, failed_users=failed_users)

    # Sync users
    if sync_users:
      _sync_ldap_members(connection, group, ldap_info, max_count=max_count, failed_users=failed_users)

    group.save()
    groups.append(group)

  return groups


def _import_ldap_suboordinate_groups(connection, groupname_pattern, import_members=False, recursive_import_members=False,
                                     sync_users=True, import_by_dn=False, failed_users=None):
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

  group_info = None
  try:
    group_info = connection.find_groups(groupname_pattern, find_by_dn=import_by_dn, scope=scope)
  except LdapSearchException as e:
    LOG.warn("Could not find LDAP group: %s" % e)

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
        group_info = []
        try:
          group_info = connection.find_groups(ldap_info['dn'], find_by_dn=True)
        except LdapSearchException as e:
          LOG.warn("Failed to find LDAP group: %s" % e)

        for sub_ldap_info in group_info:
          members += sub_ldap_info['members']
          posix_members += sub_ldap_info['posix_members']

      for member in members:
        LOG.debug("Importing user %s" % smart_str(member))
        group.user_set.add(
          *(_import_ldap_users(connection, member, import_by_dn=True, failed_users=failed_users) or []))

    # Sync users
    if sync_users:
      for member in members:
        user_info = []
        try:
          user_info = connection.find_users(member, find_by_dn=True)
        except LdapSearchException as e:
          LOG.warn("Failed to find LDAP user: %s" % e)

        if user_info is None:
          continue

        if len(user_info) > 1:
          LOG.warn('Found multiple users for member %s.' % member)
        else:
          for ldap_info in user_info:
            try:
              validate_username(ldap_info['username'])
              user = ldap_access.get_ldap_user(username=ldap_info['username'])
              group.user_set.add(user)
            except ValidationError as e:
              if failed_users is None:
                failed_users = []
              failed_users.append(ldap_info['username'])
              LOG.warn('Could not sync %s: %s' % (ldap_info['username'], e.message))
            except User.DoesNotExist:
              pass

    # Import/fetch posix users and groups
    # Posix members
    if posix_members:
      if import_members:
        for posix_member in posix_members:
          LOG.debug("Importing user %s" % smart_str(posix_member))
          # posixGroup class defines 'memberUid' to be login names,
          # which are defined by 'uid'.
          user_info = None
          try:
            user_info = connection.find_users(posix_member, search_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(),
                                              user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(),
                                              find_by_dn=False)
          except LdapSearchException as e:
            LOG.warn("Failed to find LDAP user: %s" % e)

          if user_info:
            users = _import_ldap_users_info(connection, user_info, import_by_dn=False, failed_users=failed_users)
            if users:
              LOG.debug("Adding member %s represented as users (should be a single user) %s to group %s" % (
              smart_str(posix_member), smart_str(users), smart_str(group.name)))
              group.user_set.add(*users)

      if sync_users:
        for posix_member in posix_members:
          user_info = []
          try:
            user_info = connection.find_users(posix_member, search_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(),
                                              user_name_attr=desktop.conf.LDAP.USERS.USER_NAME_ATTR.get(),
                                              find_by_dn=False)
          except LdapSearchException as e:
            LOG.warn("Failed to find LDAP user: %s" % e)

          if len(user_info) > 1:
            LOG.warn('Found multiple users for member %s.' % posix_member)
          else:
            for ldap_info in user_info:
              try:
                validate_username(ldap_info['username'])
                user = ldap_access.get_ldap_user(username=ldap_info['username'])
                group.user_set.add(user)
              except ValidationError as e:
                if failed_users is None:
                  failed_users = []
                failed_users.append(ldap_info['username'])
                LOG.warn('Could not sync %s: %s' % (ldap_info['username'], e.message))
              except User.DoesNotExist:
                pass

    group.save()
    groups.append(group)

  return groups


def _import_ldap_groups(connection, groupname_pattern, import_members=False, recursive_import_members=False,
                        sync_users=True, import_by_dn=False, failed_users=None):
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
                                            import_by_dn=import_by_dn,
                                            failed_users=failed_users)
  else:
    return _import_ldap_nested_groups(connection=connection,
                                      groupname_pattern=groupname_pattern,
                                      import_members=import_members,
                                      recursive_import_members=recursive_import_members,
                                      sync_users=sync_users,
                                      import_by_dn=import_by_dn,
                                      failed_users=failed_users)


def _get_failed_operation_text(username, operation):
  return '%(username)s is not allowed to perform %(operation)s' % {'username': username, 'operation': operation}
