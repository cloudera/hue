#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
Tests for "user admin"
"""

from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import make_logged_in_client
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

def reset_all_users():
  """Reset to a clean state by deleting all users"""
  for user in User.objects.all():
    user.delete()

def test_user_admin():
  reset_all_users()
  c = make_logged_in_client(username="test", is_superuser=True)

  # Test basic output.
  response = c.get('/useradmin/')
  assert_true(len(response.context["users"]) > 0)
  assert_true("Hue Users" in response.content)

  # Test editing a superuser
  # Just check that this comes back
  response = c.get('/useradmin/edit/test')
  # Edit it, to add a first and last name
  response = c.post('/useradmin/edit/test',
                    dict(username="test",
                         first_name=u"Inglés",
                         last_name=u"Español",
                         is_superuser="True",
                         is_active="True"))
  # Now make sure that those were materialized
  response = c.get('/useradmin/edit/test')
  assert_equal(smart_unicode("Inglés"), response.context["form"].instance.first_name)
  assert_true("Español" in response.content)
  # Shouldn't be able to demote to non-superuser
  response = c.post('/useradmin/edit/test', dict(username="test",
                        first_name=u"Inglés", last_name=u"Español",
                        is_superuser=False, is_active=True))
  assert_true("You cannot remove" in response.content,
              "Shouldn't be able to remove the last superuser")
  # Shouldn't be able to delete the last superuser
  response = c.post('/useradmin/delete/test', {})
  assert_true("You cannot remove" in response.content,
              "Shouldn't be able to delete the last superuser")

  # Let's try changing the password
  response = c.post('/useradmin/edit/test', dict(username="test", first_name="Tom", last_name="Tester", is_superuser=True, password1="foo", password2="foobar"))
  assert_equal(["Passwords do not match."], response.context["form"]["password2"].errors, "Should have complained about mismatched password")
  response = c.post('/useradmin/edit/test', dict(username="test", first_name="Tom", last_name="Tester", password1="foo", password2="foo", is_active=True, is_superuser=True))
  assert_true(User.objects.get(username="test").is_superuser)
  assert_true(User.objects.get(username="test").check_password("foo"))
  # Change it back!
  response = c.post('/useradmin/edit/test', dict(username="test", first_name="Tom", last_name="Tester", password1="test", password2="test", is_active="True", is_superuser="True"))
  assert_true(User.objects.get(username="test").check_password("test"))
  assert_true(make_logged_in_client(username = "test", password = "test"),
              "Check that we can still login.")

  # Create a new regular user (duplicate name)
  assert_true(c.get('/useradmin/new'))
  response = c.post('/useradmin/new', dict(username="test", password1="test", password2="test"))
  assert_equal({ 'username': ["User with this Username already exists."]}, response.context["form"].errors)

  # Create a new regular user (for real)
  response = c.post('/useradmin/new', dict(username="test_user_creation", password1="test", password2="test", is_active="True"))
  response = c.get('/useradmin/')
  assert_true("test_user_creation" in response.content)
  assert_true(len(response.context["users"]) > 1)
  assert_true("Hue Users" in response.content)

  # Check permissions by logging in as the new user
  c_reg = make_logged_in_client(username="test_user_creation", password="test")
  # Regular user should be able to modify oneself
  response = c_reg.post('/useradmin/edit/test_user_creation',
                        dict(username = "test_user_creation",
                        first_name = "Hello",
                        is_active = True))
  response = c_reg.get('/useradmin/edit/test_user_creation')
  assert_equal("Hello", response.context["form"].instance.first_name)
  # Can't edit other people.
  response = c_reg.post("/useradmin/delete/test")
  assert_true("You must be a superuser" in response.content,
              "Regular user can't edit other people")
  # Regular user should not be able to self-promote to superuser
  response = c_reg.post('/useradmin/edit/test_user_creation',
                        dict(username = "test_user_creation",
                        first_name = "OLÁ",
                        is_superuser = True,
                        is_active = True))
  assert_true("You cannot" in response.content,
              "Regular users can't self-promote to superuser")

  # Revert to regular "test" user, that has superuser powers.
  c_su = make_logged_in_client()
  # Inactivate "test_user_creation"
  c_su.post('/useradmin/edit/test_user_creation',
                        dict(username = "test_user_creation",
                        first_name = "Hello",
                        is_active = False))
  # Now make sure "test_user_creation" can't log back in
  response = c_reg.get('/useradmin/edit/test_user_creation')
  assert_true(response.status_code == 302 and "login" in response["location"],
              "Inactivated user gets redirected to login page")

  # Delete that regular user
  response = c_su.post('/useradmin/delete/test_user_creation')
  assert_true("Hue Users" in response.content)
  # You shouldn't be able to create a user without a password
  response = c_su.post('/useradmin/new', dict(username="test"))
  assert_true("You must specify a password when creating a new user." in response.content)
