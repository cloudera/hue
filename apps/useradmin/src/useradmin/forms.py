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
import re

import django.contrib.auth.forms
from django import forms
from django.contrib.auth.models import User, Group
from django.forms import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import get_language, ugettext as _, ugettext_lazy as _t

from desktop import conf as desktop_conf
from desktop.lib.django_util import get_username_re_rule, get_groupname_re_rule
from desktop.models import HueUser
from desktop.settings import LANGUAGES

from useradmin.models import GroupPermission, HuePermission
from useradmin.models import get_default_user_group
from useradmin.hue_password_policy import hue_get_password_validators



LOG = logging.getLogger(__name__)


def get_server_choices():
  if desktop_conf.LDAP.LDAP_SERVERS.get():
    return [(ldap_server_record_key, ldap_server_record_key) for ldap_server_record_key in desktop_conf.LDAP.LDAP_SERVERS.get()]
  else:
    return []

def validate_dn(dn):
  if not dn:
    raise ValidationError(_('Full Distinguished Name required.'))

def validate_username(username_pattern):
  validator = re.compile(r"^%s$" % get_username_re_rule())

  if not username_pattern:
    raise ValidationError(_('Username is required.'))
  if len(username_pattern) > 30:
    raise ValidationError(_('Username must be fewer than 30 characters.'))
  if not validator.match(username_pattern):
    raise ValidationError(_("Username must not contain whitespaces and ':'"))

def validate_groupname(groupname_pattern):
  validator = re.compile(r"^%s$" % get_groupname_re_rule())

  if not groupname_pattern:
    raise ValidationError(_('Group name required.'))
  if len(groupname_pattern) > 80:
    raise ValidationError(_('Group name must be 80 characters or fewer.'))
  if not validator.match(groupname_pattern):
    raise ValidationError(_("Group name can be any character as long as it's 80 characters or fewer."))

def validate_first_name(first_name):
  if first_name and len(first_name) > 30:
    raise ValidationError(_('first_name must be fewer than 30 characters.'))

def validate_last_name(last_name):
  if last_name and len(last_name) > 30:
    raise ValidationError(_('last_name must be fewer than 30 characters.'))


class UserChangeForm(django.contrib.auth.forms.UserChangeForm):
  """
  This is similar, but not quite the same as djagno.contrib.auth.forms.UserChangeForm
  and UserCreationForm.
  """

  GENERIC_VALIDATION_ERROR = _("Username or password is invalid.")

  username = forms.RegexField(
      label=_t("Username"),
      max_length=30,
      regex='^%s$' % (get_username_re_rule(),),
      help_text = _t("Required. 30 characters or fewer. No whitespaces or colons."),
      error_messages = {'invalid': _t("Whitespaces and ':' not allowed") })

  password1 = forms.CharField(label=_t("New Password"),
                              widget=forms.
                              PasswordInput,
                              required=False,
                              validators=hue_get_password_validators())
  password2 = forms.CharField(label=_t("Password confirmation"),
                              widget=forms.PasswordInput,
                              required=False,
                              validators=hue_get_password_validators())
  password_old = forms.CharField(label=_t("Current password"), widget=forms.PasswordInput, required=False)
  ensure_home_directory = forms.BooleanField(label=_t("Create home directory"),
                                            help_text=_t("Create home directory if one doesn't already exist."),
                                            initial=True,
                                            required=False)
  language = forms.ChoiceField(label=_t("Language Preference"),
                               choices=LANGUAGES,
                               required=False)
  unlock_account = forms.BooleanField(label=_t("Unlock Account"),
                                      help_text=_t("Unlock user's account for login."),
                                      initial=False,
                                      required=False)

  class Meta(django.contrib.auth.forms.UserChangeForm.Meta):
    model =  HueUser
    fields = ["username", "first_name", "last_name", "email", "ensure_home_directory"]

  def __init__(self, *args, **kwargs):


    super(UserChangeForm, self).__init__(*args, **kwargs)

    if self.instance.id:
      self.fields['username'].widget.attrs['readonly'] = True

    if 'desktop.auth.backend.LdapBackend' in desktop_conf.AUTH.BACKEND.get():
      self.fields['password1'].widget.attrs['readonly'] = True
      self.fields['password2'].widget.attrs['readonly'] = True
      self.fields['password_old'].widget.attrs['readonly'] = True
      self.fields['first_name'].widget.attrs['readonly'] = True
      self.fields['last_name'].widget.attrs['readonly'] = True
      self.fields['email'].widget.attrs['readonly'] = True
      if 'is_active' in self.fields:
        self.fields['is_active'].widget.attrs['readonly'] = True
      if 'is_superuser' in self.fields:
        self.fields['is_superuser'].widget.attrs['readonly'] = True
      if 'unlock_account' in self.fields:
        self.fields['unlock_account'].widget.attrs['readonly'] = True
      if 'groups' in self.fields:
        self.fields['groups'].widget.attrs['readonly'] = True

  def clean_username(self):
    username = self.cleaned_data["username"]
    if self.instance.username == username:
      return username

    try:
      User._default_manager.get(username=username)
    except User.DoesNotExist:
      return username
    raise forms.ValidationError(_("Username already exists."), code='duplicate_username')

  def clean_password(self):
    return self.cleaned_data["password"]

  def clean_password2(self):
    password1 = self.cleaned_data.get("password1", "")
    password2 = self.cleaned_data["password2"]
    if password1 != password2:
      raise forms.ValidationError(_t("Passwords do not match."))
    return password2

  def clean_password1(self):
    password = self.cleaned_data.get("password1", "")
    if self.instance.id is None and password == "":
      raise forms.ValidationError(_("You must specify a password when creating a new user."))
    return self.cleaned_data.get("password1", "")

  def clean_password_old(self):
    if self.instance.id is not None:
      password1 = self.cleaned_data.get("password1", "")
      password_old = self.cleaned_data.get("password_old", "")
      if password1 != '' and not self.instance.check_password(password_old):
        raise forms.ValidationError(self.GENERIC_VALIDATION_ERROR)
    return self.cleaned_data.get("password_old", "")

  def save(self, commit=True):
    """
    Update password if it's set.
    """
    user = super(UserChangeForm, self).save(commit=False)
    if self.cleaned_data["password1"]:
      user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
      # groups must be saved after the user
      self.save_m2m()
    return user


class PasswordChangeForm(UserChangeForm):
  """
  This inherits from UserChangeForm to allow for forced password change on first login
  """
  class Meta(UserChangeForm.Meta):
    exclude = ('first_name', 'last_name', 'email')

  def __init__(self, *args, **kwargs):
    super(PasswordChangeForm, self).__init__(*args, **kwargs)
    self.fields.pop('ensure_home_directory')


class SuperUserChangeForm(UserChangeForm):
  class Meta(UserChangeForm.Meta):
    fields = ["username", "is_active"] + UserChangeForm.Meta.fields + ["is_superuser", "unlock_account", "groups"]

  def __init__(self, *args, **kwargs):
    super(SuperUserChangeForm, self).__init__(*args, **kwargs)
    if self.instance.id:
      # If the user exists already, we'll use its current group memberships
      self.initial['groups'] = set(self.instance.groups.all())
    else:
      # If his is a new user, suggest the default group
      default_group = get_default_user_group()
      if default_group is not None:
        self.initial['groups'] = set([default_group])
      else:
        self.initial['groups'] = []


class AddLdapUsersForm(forms.Form):
  username_pattern = forms.CharField(
      label=_t("Username"),
      help_text=_t("Required. 30 characters or fewer with username. 64 characters or fewer with DN. No whitespaces or colons."),
      error_messages={'invalid': _t("Whitespaces and ':' not allowed")})
  dn = forms.BooleanField(label=_t("Distinguished name"),
                          help_text=_t("Whether or not the user should be imported by "
                                    "distinguished name."),
                          initial=False,
                          required=False)
  ensure_home_directory = forms.BooleanField(label=_t("Create home directory"),
                                            help_text=_t("Create home directory for user if one doesn't already exist."),
                                            initial=True,
                                            required=False)

  def __init__(self, *args, **kwargs):
    super(AddLdapUsersForm, self).__init__(*args, **kwargs)
    if get_server_choices():
      self.fields['server'] = forms.ChoiceField(choices=get_server_choices(), required=True)

  def clean(self):
    cleaned_data = super(AddLdapUsersForm, self).clean()
    username_pattern = cleaned_data.get("username_pattern")
    dn = cleaned_data.get("dn")

    try:
      if dn:
        validate_dn(username_pattern)
      else:
        validate_username(username_pattern)
    except ValidationError, e:
      errors = self._errors.setdefault('username_pattern', ErrorList())
      errors.append(e.message)
      raise forms.ValidationError(e.message)

    return cleaned_data


class AddLdapGroupsForm(forms.Form):
  groupname_pattern = forms.CharField(
      label=_t("Name"),
      max_length=256,
      help_text=_t("Required. 256 characters or fewer."),
      error_messages={'invalid': _t("256 characters or fewer.") })
  dn = forms.BooleanField(label=_t("Distinguished name"),
                          help_text=_t("Whether or not the group should be imported by "
                                    "distinguished name."),
                          initial=False,
                          required=False)
  import_members = forms.BooleanField(label=_t('Import new members'),
                                      help_text=_t('Import unimported or new users from the group.'),
                                      initial=False,
                                      required=False)
  ensure_home_directories = forms.BooleanField(label=_t('Create home directories'),
                                                help_text=_t('Create home directories for every member imported, if members are being imported.'),
                                                initial=True,
                                                required=False)
  import_members_recursive = forms.BooleanField(label=_t('Import new members from all subgroups'),
                                                help_text=_t('Import unimported or new users from the all subgroups.'),
                                                initial=False,
                                                required=False)

  def __init__(self, *args, **kwargs):
    super(AddLdapGroupsForm, self).__init__(*args, **kwargs)
    if get_server_choices():
      self.fields['server'] = forms.ChoiceField(choices=get_server_choices(), required=True)

  def clean(self):
    cleaned_data = super(AddLdapGroupsForm, self).clean()
    groupname_pattern = cleaned_data.get("groupname_pattern")
    dn = cleaned_data.get("dn")

    try:
      if dn:
        validate_dn(groupname_pattern)
      else:
        validate_groupname(groupname_pattern)
    except ValidationError, e:
      errors = self._errors.setdefault('groupname_pattern', ErrorList())
      errors.append(e.message)
      raise forms.ValidationError(e.message)

    return cleaned_data


class GroupEditForm(forms.ModelForm):
  """
  Form to manipulate a group.  This manages the group name and its membership.
  """
  GROUPNAME = re.compile('^%s$' % get_groupname_re_rule())

  class Meta:
    model = Group
    fields = ("name",)

  def clean_name(self):
    # Note that the superclass doesn't have a clean_name method.
    data = self.cleaned_data["name"]
    if not self.GROUPNAME.match(data):
      raise forms.ValidationError(_("Group name may only contain letters, " +
                                  "numbers, hyphens or underscores."))
    return data

  def __init__(self, *args, **kwargs):
    super(GroupEditForm, self).__init__(*args, **kwargs)

    if self.instance.id:
      self.fields['name'].widget.attrs['readonly'] = True
      initial_members = User.objects.filter(groups=self.instance).order_by('username')
      initial_perms = HuePermission.objects.filter(grouppermission__group=self.instance).order_by('app','description')
    else:
      initial_members = []
      initial_perms = []

    self.fields["members"] = _make_model_field(_("members"), initial_members, User.objects.order_by('username'))
    self.fields["permissions"] = _make_model_field(_("permissions"), initial_perms, HuePermission.objects.order_by('app','description'))

  def _compute_diff(self, field_name):
    current = set(self.fields[field_name].initial_objs)
    updated = set(self.cleaned_data[field_name])
    delete = current.difference(updated)
    add = updated.difference(current)
    return delete, add

  def save(self):
    super(GroupEditForm, self).save()
    self._save_members()
    self._save_permissions()

  def _save_members(self):
    delete_membership, add_membership = self._compute_diff("members")
    for user in delete_membership:
      user.groups.remove(self.instance)
      user.save()
    for user in add_membership:
      user.groups.add(self.instance)
      user.save()

  def _save_permissions(self):
    delete_permission, add_permission = self._compute_diff("permissions")
    for perm in delete_permission:
      GroupPermission.objects.get(group=self.instance, hue_permission=perm).delete()
    for perm in add_permission:
      GroupPermission.objects.create(group=self.instance, hue_permission=perm)


class PermissionsEditForm(forms.ModelForm):
  """
  Form to manage the set of groups that have a particular permission.
  """

  class Meta:
    model = Group
    fields = ()

  def __init__(self, *args, **kwargs):
    super(PermissionsEditForm, self).__init__(*args, **kwargs)

    if self.instance.id:
      initial_groups = Group.objects.filter(grouppermission__hue_permission=self.instance).order_by('name')
    else:
      initial_groups = []

    self.fields["groups"] = _make_model_field(_("groups"), initial_groups, Group.objects.order_by('name'))

  def _compute_diff(self, field_name):
    current = set(self.fields[field_name].initial_objs)
    updated = set(self.cleaned_data[field_name])
    delete = current.difference(updated)
    add = updated.difference(current)
    return delete, add

  def save(self):
    self._save_permissions()

  def _save_permissions(self):
    delete_group, add_group = self._compute_diff("groups")
    for group in delete_group:
      GroupPermission.objects.get(group=group, hue_permission=self.instance).delete()
    for group in add_group:
      GroupPermission.objects.create(group=group, hue_permission=self.instance)


def _make_model_field(label, initial, choices, multi=True):
  """ Creates multiple choice field with given query object as choices. """
  if multi:
    field = forms.models.ModelMultipleChoiceField(choices, required=False)
    field.initial_objs = initial
    field.initial = [ obj.pk for obj in initial ]
    field.label = label
  else:
    field = forms.models.ModelChoiceField(choices, required=False)
    field.initial_obj = initial
    if initial:
      field.initial = initial.pk
  return field

class SyncLdapUsersGroupsForm(forms.Form):
  ensure_home_directory = forms.BooleanField(label=_t("Create Home Directories"),
                                            help_text=_t("Create home directory for every user, if one doesn't already exist."),
                                            initial=True,
                                            required=False)
  def __init__(self, *args, **kwargs):
    super(SyncLdapUsersGroupsForm, self).__init__(*args, **kwargs)
    if get_server_choices():
      self.fields['server'] = forms.ChoiceField(choices=get_server_choices(), required=True)
