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
import re
import pwd
import grp
import logging
import threading
import subprocess

import django
import django.contrib.auth.forms
from django import forms
from django.contrib.auth.models import User, Group
from desktop.lib.django_util import get_username_re_rule, get_groupname_re_rule, render, PopupException, format_preserving_redirect
from django.core import urlresolvers

LOG = logging.getLogger(__name__)

__users_lock = threading.Lock()
__groups_lock = threading.Lock()

def list_users(request):
  return render("list_users.mako", request, dict(users=User.objects.all()))

def list_groups(request):
  return render("list_groups.mako", request, dict(groups=Group.objects.all()))

def delete_user(request, username):
  if not request.user.is_superuser:
    raise PopupException("You must be a superuser to delete users.")
  if request.method == 'POST':
    try:
      global __users_lock
      __users_lock.acquire()
      try:
        user = User.objects.get(username=username)
        _check_remove_last_super(user)
        user.delete()
      finally:
        __users_lock.release()

      # Send a flash message saying "deleted"?
      return list_users(request)
    except User.DoesNotExist:
      raise PopupException("User not found.")
  else:
    return render("confirm.mako",
      request,
      dict(path=request.path, title="Delete user?"))

def delete_group(request, name):
  if not request.user.is_superuser:
    raise PopupException("You must be a superuser to delete groups.")
  if request.method == 'POST':
    try:
      global groups_lock
      __groups_lock.acquire()
      try:
        group = Group.objects.get(name=name)
        group.delete()
      finally:
        __groups_lock.release()

      # Send a flash message saying "deleted"?
      return list_groups(request)
    except Group.DoesNotExist:
      raise PopupException("Group not found.")
  else:
    return render("confirm.mako",
      request,
      dict(path=request.path, title="Delete group?"))

class UserChangeForm(django.contrib.auth.forms.UserChangeForm):
  """
  This is similar, but not quite the same as djagno.contrib.auth.forms.UserChangeForm
  and UserCreationForm.
  """
  username = forms.RegexField(
      label="Username",
      max_length=30,
      regex='^%s$' % (get_username_re_rule(),),
      help_text = "Required. 30 characters or fewer. No whitespaces or colons.",
      error_messages = {'invalid': "Whitespaces and ':' not allowed" })
  password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
  password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput, required=False)

  class Meta(django.contrib.auth.forms.UserChangeForm.Meta):
    fields = ["username", "first_name", "last_name", "email", "is_active", "is_superuser"]

  def clean_password2(self):
    password1 = self.cleaned_data.get("password1", "")
    password2 = self.cleaned_data["password2"]
    if password1 != password2:
      raise forms.ValidationError("Passwords do not match.")
    return password2

  def clean_password1(self):
    password = self.cleaned_data.get("password1", "")
    if self.instance.id is None and password == "":
      raise forms.ValidationError("You must specify a password when creating a new user.")
    return self.cleaned_data.get("password1", "")

  def save(self, commit=True):
    """
    Update password if it's set.
    """
    user = super(UserChangeForm, self).save(commit=False)
    if self.cleaned_data["password1"]:
      user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
    return user

def edit_user(request, username=None):
  """
  edit_user(request, username = None) -> reply

  @type request:        HttpRequest
  @param request:       The request object
  @type username:       string
  @param username:      Default to None, when creating a new user
  """
  if request.user.username != username and not request.user.is_superuser:
    raise PopupException("You must be a superuser to add or edit another user.")
  if username is not None:
    instance = User.objects.get(username=username)
  else:
    instance = None

  if request.method == 'POST':
    form = UserChangeForm(request.POST, instance=instance)
    if form.is_valid(): # All validation rules pass
      if instance is None:
        form.save()
      else:
        #
        # Check for 3 more conditions:
        # (1) A user cannot inactivate oneself;
        # (2) Non-superuser cannot promote himself; and
        # (3) The last active superuser cannot demote/inactivate himself.
        #
        if request.user.username == username and not form.instance.is_active:
          raise PopupException("You cannot make yourself inactive.")

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
              raise PopupException("You cannot make yourself a superuser.")

          # All ok
          form.save()
        finally:
          __users_lock.release()

      request.path = urlresolvers.reverse(list_users)
      return list_users(request)
  else:
    form = UserChangeForm(instance=instance)
  return render('edit_user.mako', request,
    dict(form=form, action=request.path, username=username))

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
    raise PopupException("You must be a superuser to add or edit a group.")

  if name is not None:
    instance = Group.objects.get(name=name)
  else:
    instance = None

  if request.method == 'POST':
    form = GroupEditForm(request.POST, instance=instance)
    if form.is_valid():
      form.save()
      request.flash.put('Group information updated')
      url = urlresolvers.reverse(list_groups)
      return format_preserving_redirect(request, url)

  else:
    form = GroupEditForm(instance=instance)
  return render('edit_group.mako', request,
    dict(form=form, action=request.path, name=name))


def _check_remove_last_super(user_obj):
  """Raise an error if we're removing the last superuser"""
  if not user_obj.is_superuser:
    return

  # Is there any other active superuser left?
  all_active_su = User.objects.filter(is_superuser__exact = True,
                                      is_active__exact = True)
  num_active_su = all_active_su.count()
  assert num_active_su >= 1, "No active superuser configured"
  if num_active_su == 1:
    raise PopupException("You cannot remove the last active "
                         "superuser from the configuration.")

def sync_unix_users_and_groups(min_uid, max_uid, check_shell):
  """
  Syncs the Hue database with the underlying Unix system, by importing users and
  groups from 'getent passwd' and 'getent groups'. This should also pull in
  users who are accessible via NSS.
  """
  global __users_lock, __groups_lock

  hadoop_groups = dict((group.gr_name, group) for group in grp.getgrall() \
      if (group.gr_gid >= min_uid and group.gr_gid < max_uid) or group.gr_name == 'hadoop')
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

class GroupEditForm(forms.ModelForm):
  """
  Form to manipulate a group.  This manages the group name and its membership.
  """
  class Meta:
    model = Group
    fields = ("name",)

  def clean_name(self):
    # Note that the superclass doesn't have a clean_name method.
    data = self.cleaned_data["name"]
    if not re.match(get_groupname_re_rule(), data):
      raise forms.ValidationError("Group name may only contain letters, " +
                                  "numbers, hypens or underscores.")
    return data

  def __init__(self, *args, **kwargs):
    super(GroupEditForm, self).__init__(*args, **kwargs)

    if self.instance.id:
      initial_members = User.objects.filter(groups=self.instance).order_by('username')
    else:
      initial_members = []

    self.fields["members"] = _make_model_field(initial_members, User.objects.order_by('username'))

  def _compute_diff(self, field_name):
    """Used for members, but not permissions."""
    current = set(self.fields[field_name].initial_objs)
    updated = set(self.cleaned_data[field_name])
    delete = current.difference(updated)
    add = updated.difference(current)
    return delete, add

  def save(self):
    super(GroupEditForm, self).save()
    self._save_members()

  def _save_members(self):
    delete_membership, add_membership = self._compute_diff("members")
    for user in delete_membership:
      user.groups.remove(self.instance)
      user.save()
    for user in add_membership:
      user.groups.add(self.instance)
      user.save()

def _make_model_field(initial, choices, multi=True):
  """ Creates multiple choice field with given query object as choices. """
  if multi:
    field = forms.models.ModelMultipleChoiceField(choices, required=False)
    field.initial_objs = initial
    field.initial = [ obj.pk for obj in initial ]
  else:
    field = forms.models.ModelChoiceField(choices, required=False)
    field.initial_obj = initial
    if initial:
      field.initial = initial.pk
  return field


