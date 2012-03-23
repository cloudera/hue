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

import urllib

from nose.tools import assert_true, assert_equal, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from django.contrib.auth.models import User, Group
from django.utils.encoding import smart_unicode

from useradmin.models import HuePermission, GroupPermission, LdapGroup, UserProfile
from useradmin.models import get_profile

import useradmin.conf
from views import sync_ldap_users_and_groups, import_ldap_user, import_ldap_group
import ldap_access

def reset_all_users():
  """Reset to a clean state by deleting all users"""
  for user in User.objects.all():
    user.delete()

def reset_all_groups():
  """Reset to a clean state by deleting all users"""

  useradmin.conf.DEFAULT_USER_GROUP.set_for_testing(None)
  for grp in Group.objects.all():
    grp.delete()

class LdapTestConnection(object):
  """
  Test class which mimics the behaviour of LdapConnection (from ldap_access.py).
  It also includes functionality to fake modifications to an LDAP server.  It is designed
  as a singleton, to allow for changes to persist across discrete connections.
  """

  _instance = None
  def __init__(self):
    if LdapTestConnection._instance is None:
      LdapTestConnection._instance = LdapTestConnection._Singleton()

  def add_user_group_for_test(self, user, group):
    LdapTestConnection._instance.groups[group]['members'].append(user)

  def remove_user_group_for_test(self, user, group):
    LdapTestConnection._instance.groups[group]['members'].remove(user)

  def find_user(self, user, find_by_dn=False):
    """ Returns info for a particular user """
    return LdapTestConnection._instance.users[user]

  def find_group(self, groupname, find_by_dn=False):
    """ Return all groups in the system with parents and children """
    return LdapTestConnection._instance.groups[groupname]

  class _Singleton:
    def __init__(self):
      self.users = {'moe': {'username':'moe', 'first':'Moe', 'email':'moe@stooges.com'},
                    'larry': {'username':'larry', 'first':'Larry', 'last':'Stooge', 'email':'larry@stooges.com'},
                    'curly': {'username':'curly', 'first':'Curly', 'last':'Stooge', 'email':'curly@stooges.com'},
                    'otherguy': {'username':'otherguy', 'first':'Other', 'last':'Guy', 'email':'other@guy.com'}}

      self.groups = {'TestUsers': {'name':'TestUsers', 'members':['moe','larry','curly']},
                     'Test Administrators': {'name':'Test Administrators', 'members':['curly','larry']},
                     'OtherGroup': {'name':'OtherGroup', 'members':[]}}



def test_invalid_username():
  BAD_NAMES = ('-foo', 'foo:o', 'foo o', ' foo')

  c = make_logged_in_client(username="test", is_superuser=True)

  for bad_name in BAD_NAMES:
    assert_true(c.get('/useradmin/users/new'))
    response = c.post('/useradmin/users/new', dict(username=bad_name, password1="test", password2="test"))
    assert_true('not allowed' in response.context["form"].errors['username'][0])

def test_group_permissions():
  reset_all_users()
  reset_all_groups()

  # Get ourselves set up with a user and a group
  c = make_logged_in_client(username="test", is_superuser=True)
  Group.objects.create(name="test-group")
  test_user = User.objects.get(username="test")
  test_user.groups.add(Group.objects.get(name="test-group"))
  test_user.save()

  # Make sure that a superuser can always access applications
  response = c.get('/useradmin/users')
  assert_true('Hue Users' in response.content)

  assert_true(len(GroupPermission.objects.all()) == 0)
  c.post('/useradmin/groups/edit/test-group',
         dict(name="test-group",
         members=[User.objects.get(username="test").pk],
         permissions=[HuePermission.objects.get(app='useradmin',action='access').pk],
         save="Save"), follow=True)
  assert_true(len(GroupPermission.objects.all()) == 1)

  # Now test that we have limited access
  c1 = make_logged_in_client(username="nonadmin", is_superuser=False)
  response = c1.get('/useradmin/users')
  assert_true('You do not have permission to access the Useradmin application.' in response.content)

  # Add the non-admin to a group that should grant permissions to the app
  test_user = User.objects.get(username="nonadmin")
  test_user.groups.add(Group.objects.get(name='test-group'))
  test_user.save()

  # Check that we have access now
  response = c1.get('/useradmin/users')
  assert_true(get_profile(test_user).has_hue_permission('access','useradmin'))
  assert_true('Hue Users' in response.content)

  # And revoke access from the group
  c.post('/useradmin/permissions/edit/useradmin/access',
         dict(app='useradmin',
         priv='access',
         groups=[],
         save="Save"), follow=True)
  assert_true(len(GroupPermission.objects.all()) == 0)
  assert_false(get_profile(test_user).has_hue_permission('access','useradmin'))

  # We should no longer have access to the app
  response = c1.get('/useradmin/users')
  assert_true('You do not have permission to access the Useradmin application.' in response.content)

def test_group_admin():
  reset_all_users()
  reset_all_groups()

  c = make_logged_in_client(username="test", is_superuser=True)
  response = c.get('/useradmin/groups')
  # No groups just yet
  assert_true(len(response.context["groups"]) == 0)
  assert_true("Hue Groups" in response.content)

  # Create a group
  response = c.get('/useradmin/groups/new')
  assert_equal('/useradmin/groups/new', response.context['action'])
  c.post('/useradmin/groups/new', dict(name="testgroup"))

  # We should have an empty group in the DB now
  assert_true(len(Group.objects.all()) == 1)
  assert_true(Group.objects.filter(name="testgroup").exists())
  assert_true(len(Group.objects.get(name="testgroup").user_set.all()) == 0)

  # And now, just for kicks, let's try adding a user
  response = c.post('/useradmin/groups/edit/testgroup',
                    dict(name="testgroup",
                    members=[User.objects.get(username="test").pk],
                    save="Save"), follow=True)
  assert_true(len(Group.objects.get(name="testgroup").user_set.all()) == 1)
  assert_true(Group.objects.get(name="testgroup").user_set.filter(username="test").exists())

  # Test some permissions
  c2 = make_logged_in_client(username="nonadmin", is_superuser=False)

  # Need to give access to the user for the rest of the test
  group = Group.objects.create(name="access-group")
  perm = HuePermission.objects.get(app='useradmin', action='access')
  GroupPermission.objects.create(group=group, hue_permission=perm)
  test_user = User.objects.get(username="nonadmin")
  test_user.groups.add(Group.objects.get(name="access-group"))
  test_user.save()

  response = c2.get('/useradmin/groups/new')
  assert_true("You must be a superuser" in response.content)
  response = c2.get('/useradmin/groups/edit/testgroup')
  assert_true("You must be a superuser" in response.content)

  # Should be one group left, because we created the other group
  response = c.post('/useradmin/groups/delete/testgroup')
  assert_true(len(Group.objects.all()) == 1)


def test_user_admin():
  FUNNY_NAME = '~`!@#$%^&*()_-+={}[]|\;"<>?/,.'
  FUNNY_NAME_QUOTED = urllib.quote(FUNNY_NAME)

  reset_all_users()
  reset_all_groups()
  c = make_logged_in_client(username="test", is_superuser=True)

  # Test basic output.
  response = c.get('/useradmin/')
  assert_true(len(response.context["users"]) > 0)
  assert_true("Hue Users" in response.content)

  # Test editing a superuser
  # Just check that this comes back
  response = c.get('/useradmin/users/edit/test')
  # Edit it, to add a first and last name
  response = c.post('/useradmin/users/edit/test',
                    dict(username="test",
                         first_name=u"Inglés",
                         last_name=u"Español",
                         is_superuser="True",
                         is_active="True"))
  # Now make sure that those were materialized
  response = c.get('/useradmin/users/edit/test')
  assert_equal(smart_unicode("Inglés"), response.context["form"].instance.first_name)
  assert_true("Español" in response.content)
  # Shouldn't be able to demote to non-superuser
  response = c.post('/useradmin/users/edit/test', dict(username="test",
                        first_name=u"Inglés", last_name=u"Español",
                        is_superuser=False, is_active=True))
  assert_true("You cannot remove" in response.content,
              "Shouldn't be able to remove the last superuser")
  # Shouldn't be able to delete the last superuser
  response = c.post('/useradmin/users/delete/test', {})
  assert_true("You cannot remove" in response.content,
              "Shouldn't be able to delete the last superuser")

  # Let's try changing the password
  response = c.post('/useradmin/users/edit/test', dict(username="test", first_name="Tom", last_name="Tester", is_superuser=True, password1="foo", password2="foobar"))
  assert_equal(["Passwords do not match."], response.context["form"]["password2"].errors, "Should have complained about mismatched password")
  response = c.post('/useradmin/users/edit/test', dict(username="test", first_name="Tom", last_name="Tester", password1="foo", password2="foo", is_active=True, is_superuser=True))
  assert_true(User.objects.get(username="test").is_superuser)
  assert_true(User.objects.get(username="test").check_password("foo"))
  # Change it back!
  response = c.post('/useradmin/users/edit/test', dict(username="test", first_name="Tom", last_name="Tester", password1="test", password2="test", is_active="True", is_superuser="True"))
  assert_true(User.objects.get(username="test").check_password("test"))
  assert_true(make_logged_in_client(username = "test", password = "test"),
              "Check that we can still login.")

  # Create a new regular user (duplicate name)
  assert_true(c.get('/useradmin/users/new'))
  response = c.post('/useradmin/users/new', dict(username="test", password1="test", password2="test"))
  assert_equal({ 'username': ["User with this Username already exists."]}, response.context["form"].errors)

  # Create a new regular user (for real)
  response = c.post('/useradmin/users/new', dict(username=FUNNY_NAME,
                                           password1="test",
                                           password2="test",
                                           is_active="True"))
  response = c.get('/useradmin/')
  assert_true(FUNNY_NAME_QUOTED in response.content)
  assert_true(len(response.context["users"]) > 1)
  assert_true("Hue Users" in response.content)

  # Need to give access to the user for the rest of the test
  group = Group.objects.create(name="test-group")
  perm = HuePermission.objects.get(app='useradmin', action='access')
  GroupPermission.objects.create(group=group, hue_permission=perm)

  # Verify that we can modify user groups through the user admin pages
  response = c.post('/useradmin/users/new', dict(username="group_member", password1="test", password2="test", groups=[group.pk]))
  User.objects.get(username='group_member')
  assert_true(User.objects.get(username='group_member').groups.filter(name='test-group').exists())
  response = c.post('/useradmin/users/edit/group_member', dict(username="group_member", password1="test", password2="test", groups=[]))
  assert_false(User.objects.get(username='group_member').groups.filter(name='test-group').exists())

  # Check permissions by logging in as the new user
  c_reg = make_logged_in_client(username=FUNNY_NAME, password="test")
  test_user = User.objects.get(username=FUNNY_NAME)
  test_user.groups.add(Group.objects.get(name="test-group"))
  test_user.save()

  # Regular user should be able to modify oneself
  response = c_reg.post('/useradmin/users/edit/%s' % (FUNNY_NAME_QUOTED,),
                        dict(username = FUNNY_NAME,
                             first_name = "Hello",
                             is_active = True))
  response = c_reg.get('/useradmin/users/edit/%s' % (FUNNY_NAME_QUOTED,))
  assert_equal("Hello", response.context["form"].instance.first_name)
  # Can't edit other people.
  response = c_reg.post("/useradmin/users/delete/test")
  assert_true("You must be a superuser" in response.content,
              "Regular user can't edit other people")

  # Revert to regular "test" user, that has superuser powers.
  c_su = make_logged_in_client()
  # Inactivate FUNNY_NAME
  c_su.post('/useradmin/users/edit/%s' % (FUNNY_NAME_QUOTED,),
                        dict(username = FUNNY_NAME,
                             first_name = "Hello",
                             is_active = False))
  # Now make sure FUNNY_NAME can't log back in
  response = c_reg.get('/useradmin/users/edit/%s' % (FUNNY_NAME_QUOTED,))
  assert_true(response.status_code == 302 and "login" in response["location"],
              "Inactivated user gets redirected to login page")

  # Delete that regular user
  response = c_su.post('/useradmin/users/delete/%s' % (FUNNY_NAME_QUOTED,))
  assert_true("Hue Users" in response.content)
  # You shouldn't be able to create a user without a password
  response = c_su.post('/useradmin/users/new', dict(username="test"))
  assert_true("You must specify a password when creating a new user." in response.content)

def test_useradmin_ldap_integration():
  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  # Try importing a user
  import_ldap_user('larry', import_by_dn=False)
  larry = User.objects.get(username='larry')
  assert_true(larry.first_name == 'Larry')
  assert_true(larry.last_name == 'Stooge')
  assert_true(larry.email == 'larry@stooges.com')
  assert_true(get_profile(larry).creation_method == str(UserProfile.CreationMethod.EXTERNAL))

  # Should be a noop
  sync_ldap_users_and_groups()
  assert_equal(len(User.objects.all()), 1)
  assert_equal(len(Group.objects.all()), 0)

  # Should import a group, but will only sync already-imported members
  import_ldap_group('Test Administrators', import_members=False, import_by_dn=False)
  assert_equal(len(User.objects.all()), 1)
  assert_equal(len(Group.objects.all()), 1)
  test_admins = Group.objects.get(name='Test Administrators')
  assert_equal(len(test_admins.user_set.all()), 1)
  assert_equal(test_admins.user_set.all()[0].username, larry.username)

  # Import all members of TestUsers
  import_ldap_group('TestUsers', import_members=True, import_by_dn=False)
  test_users = Group.objects.get(name='TestUsers')
  assert_true(LdapGroup.objects.filter(group=test_users).exists())
  assert_equal(len(test_users.user_set.all()), 3)

  ldap_access.CACHED_LDAP_CONN.remove_user_group_for_test('moe', 'TestUsers')
  import_ldap_group('TestUsers', import_members=False, import_by_dn=False)
  assert_equal(len(test_users.user_set.all()), 2)
  assert_equal(len(User.objects.get(username='moe').groups.all()), 0)

  ldap_access.CACHED_LDAP_CONN.add_user_group_for_test('moe', 'TestUsers')
  import_ldap_group('TestUsers', import_members=False, import_by_dn=False)
  assert_equal(len(test_users.user_set.all()), 3)
  assert_equal(len(User.objects.get(username='moe').groups.all()), 1)

  # Make sure that if a Hue user already exists with a naming collision, we
  # won't overwrite any of that user's information.
  hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
  import_ldap_user('otherguy', import_by_dn=False)
  hue_user = User.objects.get(username='otherguy')
  assert_equal(get_profile(hue_user).creation_method, str(UserProfile.CreationMethod.HUE))
  assert_equal(hue_user.first_name, 'Different')

  # Make sure Hue groups with naming collisions don't get marked as LDAP groups
  hue_group = Group.objects.create(name='OtherGroup')
  hue_group.user_set.add(hue_user)
  hue_group.save()
  import_ldap_group('OtherGroup', import_members=False, import_by_dn=False)
  assert_false(LdapGroup.objects.filter(group=hue_group).exists())
  assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
