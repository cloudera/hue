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

import django
import threading
from django import forms
from django.contrib.auth.models import User
from desktop.lib.django_util import render, PopupException
from django.core import urlresolvers

__users_lock = threading.Lock()


def list_users(request):
  return render("list_users.mako", request, dict(users=User.objects.all()))

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

class UserChangeForm(django.contrib.auth.forms.UserChangeForm):
  """
  This is similar, but not quite the same as djagno.contrib.auth.forms.UserChangeForm
  and UserCreationForm.
  """
  username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w]+$',
          help_text = "Required. 30 characters or fewer. Letters and digits only.",
          error_messages = {'invalid': "This value may contain only letters and numbers."})
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
