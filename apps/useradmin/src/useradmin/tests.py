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

import re
import urllib
import ldap

from nose.plugins.attrib import attr
from nose.tools import assert_true, assert_equal, assert_false

import desktop.conf
from desktop.lib.test_utils import grant_access
from desktop.lib.django_test_util import make_logged_in_client
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse

from useradmin.models import HuePermission, GroupPermission, LdapGroup, UserProfile
from useradmin.models import get_profile, get_default_user_group

import useradmin.conf
from hadoop import pseudo_hdfs4
from views import sync_ldap_users, sync_ldap_groups, import_ldap_users, import_ldap_groups, \
                  add_ldap_users, add_ldap_groups, sync_ldap_users_groups
import ldap_access

def reset_all_users():
  """Reset to a clean state by deleting all users"""
  for user in User.objects.all():
    user.delete()

def reset_all_groups():
  """Reset to a clean state by deleting all groups"""

  useradmin.conf.DEFAULT_USER_GROUP.set_for_testing(None)
  for grp in Group.objects.all():
    grp.delete()

class LdapTestConnection(object):
  """
  Test class which mimics the behaviour of LdapConnection (from ldap_access.py).
  It also includes functionality to fake modifications to an LDAP server.  It is designed
  as a singleton, to allow for changes to persist across discrete connections.

  This class assumes uid is the user_name_attr.
  """
  def __init__(self):
    self._instance = LdapTestConnection.Data()

  def add_user_group_for_test(self, user, group):
    self._instance.groups[group]['members'].append(user)

  def remove_user_group_for_test(self, user, group):
    self._instance.groups[group]['members'].remove(user)

  def add_posix_user_group_for_test(self, user, group):
    self._instance.groups[group]['posix_members'].append(user)

  def remove_posix_user_group_for_test(self, user, group):
    self._instance.groups[group]['posix_members'].remove(user)

  def find_users(self, username_pattern, search_attr=None, user_name_attr=None, find_by_dn=False, scope=ldap.SCOPE_SUBTREE):
    """ Returns info for a particular user via a case insensitive search """
    if find_by_dn:
      data = filter(lambda attrs: attrs['dn'] == username_pattern, self._instance.users.values())
    else:
      username_pattern = "^%s$" % username_pattern.replace('.','\\.').replace('*', '.*')
      username_fsm = re.compile(username_pattern, flags=re.I)
      usernames = filter(lambda username: username_fsm.match(username), self._instance.users.keys())
      data = [self._instance.users.get(username) for username in usernames]
    return data

  def find_groups(self, groupname_pattern, search_attr=None, group_name_attr=None, find_by_dn=False, scope=ldap.SCOPE_SUBTREE):
    """ Return all groups in the system with parents and children """
    if find_by_dn:
      data = filter(lambda attrs: attrs['dn'] == groupname_pattern, self._instance.groups.values())
      # SCOPE_SUBTREE means we return all sub-entries of the desired entry along with the desired entry.
      if data and scope == ldap.SCOPE_SUBTREE:
        sub_data = filter(lambda attrs: attrs['dn'].endswith(data[0]['dn']), self._instance.groups.values())
        data.extend(sub_data)
    else:
      groupname_pattern = "^%s$" % groupname_pattern.replace('.','\\.').replace('*', '.*')
      groupnames = filter(lambda username: re.match(groupname_pattern, username), self._instance.groups.keys())
      data = [self._instance.groups.get(groupname) for groupname in groupnames]
    return data

  def find_members_of_group(self, dn, search_attr, ldap_filter, scope=ldap.SCOPE_SUBTREE):
    members = []
    for group_info in self._instance.groups:
      if group_info['dn'] == dn:
        members.extend(group_info['members'])

    members = set(members)
    users = []
    for user_info in self._instance.users:
      if user_info['dn'] in members:
        users.append(user_info)

    groups = []
    for group_info in self._instance.groups:
      if group_info['dn'] in members:
        groups.append(group_info)

    return users + groups

  def find_users_of_group(self, dn):
    members = []
    for group_info in self._instance.groups.values():
      if group_info['dn'] == dn:
        members.extend(group_info['members'])

    members = set(members)
    users = []
    for user_info in self._instance.users.values():
      if user_info['dn'] in members:
        users.append(user_info)

    return users

  def find_groups_of_group(self, dn):
    members = []
    for group_info in self._instance.groups.values():
      if group_info['dn'] == dn:
        members.extend(group_info['members'])

    groups = []
    for group_info in self._instance.groups.values():
      if group_info['dn'] in members:
        groups.append(group_info)

    return groups

  class Data:
    def __init__(self):
      self.users = {'moe': {'dn': 'uid=moe,ou=People,dc=example,dc=com', 'username':'moe', 'first':'Moe', 'email':'moe@stooges.com', 'groups': ['cn=TestUsers,ou=Groups,dc=example,dc=com']},
                    'lårry': {'dn': 'uid=lårry,ou=People,dc=example,dc=com', 'username':'lårry', 'first':'Larry', 'last':'Stooge', 'email':'larry@stooges.com', 'groups': ['cn=TestUsers,ou=Groups,dc=example,dc=com', 'cn=Test Administrators,cn=TestUsers,ou=Groups,dc=example,dc=com']},
                    'curly': {'dn': 'uid=curly,ou=People,dc=example,dc=com', 'username':'curly', 'first':'Curly', 'last':'Stooge', 'email':'curly@stooges.com', 'groups': ['cn=TestUsers,ou=Groups,dc=example,dc=com', 'cn=Test Administrators,cn=TestUsers,ou=Groups,dc=example,dc=com']},
                    'Rock': {'dn': 'uid=Rock,ou=People,dc=example,dc=com', 'username':'Rock', 'first':'rock', 'last':'man', 'email':'rockman@stooges.com', 'groups': ['cn=Test Administrators,cn=TestUsers,ou=Groups,dc=example,dc=com']},
                    'nestedguy': {'dn': 'uid=nestedguy,ou=People,dc=example,dc=com', 'username':'nestedguy', 'first':'nested', 'last':'guy', 'email':'nestedguy@stooges.com', 'groups': ['cn=NestedGroup,ou=Groups,dc=example,dc=com']},
                    'otherguy': {'dn': 'uid=otherguy,ou=People,dc=example,dc=com', 'username':'otherguy', 'first':'Other', 'last':'Guy', 'email':'other@guy.com'},
                    'posix_person': {'dn': 'uid=posix_person,ou=People,dc=example,dc=com', 'username': 'posix_person', 'first': 'pos', 'last': 'ix', 'email': 'pos@ix.com'},
                    'posix_person2': {'dn': 'uid=posix_person2,ou=People,dc=example,dc=com', 'username': 'posix_person2', 'first': 'pos', 'last': 'ix', 'email': 'pos@ix.com'}}

      self.groups = {'TestUsers': {
                        'dn': 'cn=TestUsers,ou=Groups,dc=example,dc=com',
                        'name':'TestUsers',
                        'members':['uid=moe,ou=People,dc=example,dc=com','uid=lårry,ou=People,dc=example,dc=com','uid=curly,ou=People,dc=example,dc=com'],
                        'posix_members':[]},
                      'Test Administrators': {
                        'dn': 'cn=Test Administrators,cn=TestUsers,ou=Groups,dc=example,dc=com',
                        'name':'Test Administrators',
                        'members':['uid=Rock,ou=People,dc=example,dc=com','uid=lårry,ou=People,dc=example,dc=com','uid=curly,ou=People,dc=example,dc=com'],
                        'posix_members':[]},
                      'OtherGroup': {
                        'dn': 'cn=OtherGroup,cn=TestUsers,ou=Groups,dc=example,dc=com',
                        'name':'OtherGroup',
                        'members':[],
                        'posix_members':[]},
                      'NestedGroups': {
                        'dn': 'cn=NestedGroups,ou=Groups,dc=example,dc=com',
                        'name':'NestedGroups',
                        'members':['cn=NestedGroup,ou=Groups,dc=example,dc=com'],
                        'posix_members':[]
                      },
                      'NestedGroup': {
                        'dn': 'cn=NestedGroup,ou=Groups,dc=example,dc=com',
                        'name':'NestedGroup',
                        'members':['uid=nestedguy,ou=People,dc=example,dc=com'],
                        'posix_members':[]
                      },
                      'NestedPosixGroups': {
                        'dn': 'cn=NestedPosixGroups,ou=Groups,dc=example,dc=com',
                        'name':'NestedPosixGroups',
                        'members':['cn=PosixGroup,ou=Groups,dc=example,dc=com'],
                        'posix_members':[]
                      },
                      'PosixGroup': {
                        'dn': 'cn=PosixGroup,ou=Groups,dc=example,dc=com',
                        'name':'PosixGroup',
                        'members':[],
                        'posix_members':['posix_person','lårry']},
                      'PosixGroup1': {
                        'dn': 'cn=PosixGroup1,cn=PosixGroup,ou=Groups,dc=example,dc=com',
                        'name':'PosixGroup1',
                        'members':[],
                        'posix_members':['posix_person2']},
                     }


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

  # Make sure we can't modify permissions
  response = c1.get('/useradmin/permissions/edit/useradmin/access')
  assert_true('must be a superuser to change permissions' in response.content)

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

def test_default_group():
  reset_all_users()
  reset_all_groups()
  useradmin.conf.DEFAULT_USER_GROUP.set_for_testing('test_default')
  get_default_user_group()

  c = make_logged_in_client(username='test', is_superuser=True)

  # Create default group if it doesn't already exist.
  assert_true(Group.objects.filter(name='test_default').exists())

  # Try deleting the default group
  assert_true(Group.objects.filter(name='test_default').exists())
  response = c.post('/useradmin/groups/delete/test_default')
  assert_true('default user group may not be deleted' in response.content)
  assert_true(Group.objects.filter(name='test_default').exists())

  # Change the name of the default group, and try deleting again
  useradmin.conf.DEFAULT_USER_GROUP.set_for_testing('new_default')
  response = c.post('/useradmin/groups/delete/test_default')
  assert_false(Group.objects.filter(name='test_default').exists())
  assert_true(Group.objects.filter(name='new_default').exists())

def test_get_profile():
  # Ensure profiles are created after get_profile is called.
  reset_all_users()
  reset_all_groups()
  c = make_logged_in_client(username='test', password='test', is_superuser=True)
  assert_equal(0, UserProfile.objects.count())
  p = get_profile(User.objects.get(username='test'))
  assert_equal(1, UserProfile.objects.count())

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

  # Make sure non-superusers can't do bad things
  response = c2.get('/useradmin/groups/new')
  assert_true("You must be a superuser" in response.content)
  response = c2.get('/useradmin/groups/edit/testgroup')
  assert_true("You must be a superuser" in response.content)

  response = c2.post('/useradmin/groups/new', dict(name="nonsuperuser"))
  assert_true("You must be a superuser" in response.content)
  response = c2.post('/useradmin/groups/edit/testgroup',
                    dict(name="nonsuperuser",
                    members=[User.objects.get(username="test").pk],
                    save="Save"), follow=True)
  assert_true("You must be a superuser" in response.content)

  # Should be one group left, because we created the other group
  response = c.post('/useradmin/groups/delete/testgroup')
  assert_true(len(Group.objects.all()) == 1)

  group_count = len(Group.objects.all())
  response = c.post('/useradmin/groups/new', dict(name="with space"))
  assert_equal(len(Group.objects.all()), group_count + 1)

def test_user_admin():
  FUNNY_NAME = '~`!@#$%^&*()_-+={}[]|\;"<>?/,.'
  FUNNY_NAME_QUOTED = urllib.quote(FUNNY_NAME)

  reset_all_users()
  reset_all_groups()
  useradmin.conf.DEFAULT_USER_GROUP.set_for_testing('test_default')

  c = make_logged_in_client('test', is_superuser=True)
  user = User.objects.get(username='test')

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
                         is_active="True"),
                    follow=True)
  assert_true("User information updated" in response.content,
              "Notification should be displayed in: %s" % response.content)
  # Edit it, can't change username
  response = c.post('/useradmin/users/edit/test',
                    dict(username="test2",
                         first_name=u"Inglés",
                         last_name=u"Español",
                         is_superuser="True",
                         is_active="True"),
                    follow=True)
  assert_true("You cannot change a username" in response.content)
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
  # Shouldn't be able to delete oneself
  response = c.post('/useradmin/users/delete', {u'user_ids': [user.id]})
  assert_true("You cannot remove yourself" in response.content,
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

  # Check new user form for default group
  group = get_default_user_group()
  response = c.get('/useradmin/users/new')
  assert_true(response)
  assert_true(('<option value="1" selected="selected">%s</option>' % group) in str(response))

  # Create a new regular user (duplicate name)
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
  # Validate profile is created.
  assert_true(UserProfile.objects.filter(user__username=FUNNY_NAME).exists())

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
  funny_user = User.objects.get(username=FUNNY_NAME)
  # Can't edit other people.
  response = c_reg.post("/useradmin/users/delete", {u'user_ids': [funny_user.id]})
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
  funny_profile = get_profile(test_user)
  response = c_su.post('/useradmin/users/delete', {u'user_ids': [funny_user.id]})
  assert_equal(302, response.status_code)
  assert_false(User.objects.filter(username=FUNNY_NAME).exists())
  assert_false(UserProfile.objects.filter(id=funny_profile.id).exists())

  # Bulk delete users
  u1 = User.objects.create(username='u1', password="u1")
  u2 = User.objects.create(username='u2', password="u2")
  assert_equal(User.objects.filter(username__in=['u1', 'u2']).count(), 2)
  response = c_su.post('/useradmin/users/delete', {u'user_ids': [u1.id, u2.id]})
  assert_equal(User.objects.filter(username__in=['u1', 'u2']).count(), 0)

  # Make sure that user deletion works if the user has never performed a request.
  funny_user = User.objects.create(username=FUNNY_NAME, password='test')
  assert_true(User.objects.filter(username=FUNNY_NAME).exists())
  assert_false(UserProfile.objects.filter(user__username=FUNNY_NAME).exists())
  response = c_su.post('/useradmin/users/delete', {u'user_ids': [funny_user.id]})
  assert_equal(302, response.status_code)
  assert_false(User.objects.filter(username=FUNNY_NAME).exists())
  assert_false(UserProfile.objects.filter(user__username=FUNNY_NAME).exists())

  # You shouldn't be able to create a user without a password
  response = c_su.post('/useradmin/users/new', dict(username="test"))
  assert_true("You must specify a password when creating a new user." in response.content)


def test_useradmin_ldap_user_group_membership_sync():
  reset = [desktop.conf.AUTH.USER_GROUP_MEMBERSHIP_SYNCHRONIZATION_BACKEND.set_for_testing('desktop.auth.backend.LdapSynchronizationBackend')]
  settings.MIDDLEWARE_CLASSES.append('desktop.middleware.UserGroupSynchronizationMiddleware')

  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  try:
    # Import curly who is part of TestUsers and Test Administrators
    import_ldap_users('curly', sync_groups=False, import_by_dn=False)

    # Set a password so that we can login
    user = User.objects.get(username='curly')
    user.set_password('test')
    user.save()

    # Should have 0 groups
    assert_equal(0, user.groups.all().count())

    # Make an authenticated request as curly so that we can see call middleware.
    c = make_logged_in_client('curly', 'test', is_superuser=False)
    grant_access("curly", "test", "useradmin")
    response = c.get('/useradmin/users')

    # Refresh user groups
    user = User.objects.get(username='curly')

    # Should have 3 groups now. 2 from LDAP and 1 from 'grant_access' call.
    assert_equal(3, user.groups.all().count(), user.groups.all())

    # Now remove a group and try again.
    old_group = ldap_access.CACHED_LDAP_CONN._instance.users['curly']['groups'].pop()

    # Make an authenticated request as curly so that we can see call middleware.
    response = c.get('/useradmin/users')

    # Refresh user groups
    user = User.objects.get(username='curly')

    # Should have 2 groups now. 1 from LDAP and 1 from 'grant_access' call.
    assert_equal(3, user.groups.all().count(), user.groups.all())
  finally:
    for finish in reset:
      finish()
    settings.MIDDLEWARE_CLASSES.remove('desktop.middleware.UserGroupSynchronizationMiddleware')


def test_useradmin_ldap_suboordinate_group_integration():
  reset_all_users()
  reset_all_groups()

  reset = []

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  # Test old subgroups
  reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("suboordinate"))

  try:
    # Import groups only
    import_ldap_groups('TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
    test_users = Group.objects.get(name='TestUsers')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 0)

    # Import all members of TestUsers
    import_ldap_groups('TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='TestUsers')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 3)

    # Should import a group, but will only sync already-imported members
    import_ldap_groups('Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(User.objects.all().count(), 3)
    assert_equal(Group.objects.all().count(), 2)
    test_admins = Group.objects.get(name='Test Administrators')
    assert_equal(test_admins.user_set.all().count(), 2)
    larry = User.objects.get(username='lårry')
    assert_equal(test_admins.user_set.all()[0].username, larry.username)

    # Only sync already imported
    ldap_access.CACHED_LDAP_CONN.remove_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
    import_ldap_groups('TestUsers', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 2)
    assert_equal(User.objects.get(username='moe').groups.all().count(), 0)

    # Import missing user
    ldap_access.CACHED_LDAP_CONN.add_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
    import_ldap_groups('TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 3)
    assert_equal(User.objects.get(username='moe').groups.all().count(), 1)

    # Import all members of TestUsers and members of subgroups
    import_ldap_groups('TestUsers', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='TestUsers')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 4)

    # Make sure Hue groups with naming collisions don't get marked as LDAP groups
    hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
    hue_group = Group.objects.create(name='OtherGroup')
    hue_group.user_set.add(hue_user)
    hue_group.save()
    import_ldap_groups('OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_false(LdapGroup.objects.filter(group=hue_group).exists())
    assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
  finally:
    for finish in reset:
      finish()


def test_useradmin_ldap_nested_group_integration():
  reset_all_users()
  reset_all_groups()

  reset = []

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  # Test old subgroups
  reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("nested"))

  try:
    # Import groups only
    import_ldap_groups('TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
    test_users = Group.objects.get(name='TestUsers')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 0)

    # Import all members of TestUsers
    import_ldap_groups('TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='TestUsers')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 3)

    # Should import a group, but will only sync already-imported members
    import_ldap_groups('Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(User.objects.all().count(), 3)
    assert_equal(Group.objects.all().count(), 2)
    test_admins = Group.objects.get(name='Test Administrators')
    assert_equal(test_admins.user_set.all().count(), 2)
    larry = User.objects.get(username='lårry')
    assert_equal(test_admins.user_set.all()[0].username, larry.username)

    # Only sync already imported
    assert_equal(test_users.user_set.all().count(), 3)
    ldap_access.CACHED_LDAP_CONN.remove_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
    import_ldap_groups('TestUsers', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 2)
    assert_equal(User.objects.get(username='moe').groups.all().count(), 0)

    # Import missing user
    ldap_access.CACHED_LDAP_CONN.add_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
    import_ldap_groups('TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 3)
    assert_equal(User.objects.get(username='moe').groups.all().count(), 1)

    # Import all members of TestUsers and not members of suboordinate groups (even though specified)
    import_ldap_groups('TestUsers', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='TestUsers')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 3)

    # Nested group import
    # First without recursive import, then with.
    import_ldap_groups('NestedGroups', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    nested_groups = Group.objects.get(name='NestedGroups')
    nested_group = Group.objects.get(name='NestedGroup')
    assert_true(LdapGroup.objects.filter(group=nested_groups).exists())
    assert_true(LdapGroup.objects.filter(group=nested_group).exists())
    assert_equal(nested_groups.user_set.all().count(), 0, nested_groups.user_set.all())
    assert_equal(nested_group.user_set.all().count(), 0, nested_group.user_set.all())

    import_ldap_groups('NestedGroups', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
    nested_groups = Group.objects.get(name='NestedGroups')
    nested_group = Group.objects.get(name='NestedGroup')
    assert_true(LdapGroup.objects.filter(group=nested_groups).exists())
    assert_true(LdapGroup.objects.filter(group=nested_group).exists())
    assert_equal(nested_groups.user_set.all().count(), 0, nested_groups.user_set.all())
    assert_equal(nested_group.user_set.all().count(), 1, nested_group.user_set.all())

    # Make sure Hue groups with naming collisions don't get marked as LDAP groups
    hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
    hue_group = Group.objects.create(name='OtherGroup')
    hue_group.user_set.add(hue_user)
    hue_group.save()
    import_ldap_groups('OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_false(LdapGroup.objects.filter(group=hue_group).exists())
    assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
  finally:
    for finish in reset:
      finish()


def test_useradmin_ldap_suboordinate_posix_group_integration():
  reset_all_users()
  reset_all_groups()

  reset = []

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  # Test old subgroups
  reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("suboordinate"))

  try:
    # Import groups only
    import_ldap_groups('PosixGroup', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 0)

    # Import all members of TestUsers
    import_ldap_groups('PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 2)

    # Should import a group, but will only sync already-imported members
    import_ldap_groups('Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(User.objects.all().count(), 2, User.objects.all())
    assert_equal(Group.objects.all().count(), 2, Group.objects.all())
    test_admins = Group.objects.get(name='Test Administrators')
    assert_equal(test_admins.user_set.all().count(), 1)
    larry = User.objects.get(username='lårry')
    assert_equal(test_admins.user_set.all()[0].username, larry.username)

    # Only sync already imported
    ldap_access.CACHED_LDAP_CONN.remove_posix_user_group_for_test('posix_person', 'PosixGroup')
    import_ldap_groups('PosixGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 1)
    assert_equal(User.objects.get(username='posix_person').groups.all().count(), 0)

    # Import missing user
    ldap_access.CACHED_LDAP_CONN.add_posix_user_group_for_test('posix_person', 'PosixGroup')
    import_ldap_groups('PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 2)
    assert_equal(User.objects.get(username='posix_person').groups.all().count(), 1)

    # Import all members of PosixGroup and members of subgroups
    import_ldap_groups('PosixGroup', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 3)

    # Make sure Hue groups with naming collisions don't get marked as LDAP groups
    hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
    hue_group = Group.objects.create(name='OtherGroup')
    hue_group.user_set.add(hue_user)
    hue_group.save()
    import_ldap_groups('OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_false(LdapGroup.objects.filter(group=hue_group).exists())
    assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
  finally:
    for finish in reset:
      finish()


def test_useradmin_ldap_nested_posix_group_integration():
  reset_all_users()
  reset_all_groups()

  reset = []

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  # Test nested groups
  reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("nested"))

  try:
    # Import groups only
    import_ldap_groups('PosixGroup', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 0)

    # Import all members of TestUsers
    import_ldap_groups('PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 2)

    # Should import a group, but will only sync already-imported members
    import_ldap_groups('Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(User.objects.all().count(), 2, User.objects.all())
    assert_equal(Group.objects.all().count(), 2, Group.objects.all())
    test_admins = Group.objects.get(name='Test Administrators')
    assert_equal(test_admins.user_set.all().count(), 1)
    larry = User.objects.get(username='lårry')
    assert_equal(test_admins.user_set.all()[0].username, larry.username)

    # Only sync already imported
    ldap_access.CACHED_LDAP_CONN.remove_posix_user_group_for_test('posix_person', 'PosixGroup')
    import_ldap_groups('PosixGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 1)
    assert_equal(User.objects.get(username='posix_person').groups.all().count(), 0)

    # Import missing user
    ldap_access.CACHED_LDAP_CONN.add_posix_user_group_for_test('posix_person', 'PosixGroup')
    import_ldap_groups('PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_equal(test_users.user_set.all().count(), 2)
    assert_equal(User.objects.get(username='posix_person').groups.all().count(), 1)

    # Import all members of PosixGroup and members of subgroups (there should be no subgroups)
    import_ldap_groups('PosixGroup', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 2)

    # Import all members of NestedPosixGroups and members of subgroups
    reset_all_users()
    reset_all_groups()
    import_ldap_groups('NestedPosixGroups', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
    test_users = Group.objects.get(name='NestedPosixGroups')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 0)
    test_users = Group.objects.get(name='PosixGroup')
    assert_true(LdapGroup.objects.filter(group=test_users).exists())
    assert_equal(test_users.user_set.all().count(), 2)

    # Make sure Hue groups with naming collisions don't get marked as LDAP groups
    hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
    hue_group = Group.objects.create(name='OtherGroup')
    hue_group.user_set.add(hue_user)
    hue_group.save()
    import_ldap_groups('OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
    assert_false(LdapGroup.objects.filter(group=hue_group).exists())
    assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
  finally:
    for finish in reset:
      finish()


def test_useradmin_ldap_user_integration():
  done = []
  try:
    reset_all_users()
    reset_all_groups()

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    # Try importing a user
    import_ldap_users('lårry', sync_groups=False, import_by_dn=False)
    larry = User.objects.get(username='lårry')
    assert_true(larry.first_name == 'Larry')
    assert_true(larry.last_name == 'Stooge')
    assert_true(larry.email == 'larry@stooges.com')
    assert_true(get_profile(larry).creation_method == str(UserProfile.CreationMethod.EXTERNAL))

    # Should be a noop
    sync_ldap_users()
    sync_ldap_groups()
    assert_equal(User.objects.all().count(), 1)
    assert_equal(Group.objects.all().count(), 0)

    # Make sure that if a Hue user already exists with a naming collision, we
    # won't overwrite any of that user's information.
    hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
    import_ldap_users('otherguy', sync_groups=False, import_by_dn=False)
    hue_user = User.objects.get(username='otherguy')
    assert_equal(get_profile(hue_user).creation_method, str(UserProfile.CreationMethod.HUE))
    assert_equal(hue_user.first_name, 'Different')

    # Try importing a user and sync groups
    import_ldap_users('curly', sync_groups=True, import_by_dn=False)
    curly = User.objects.get(username='curly')
    assert_equal(curly.first_name, 'Curly')
    assert_equal(curly.last_name, 'Stooge')
    assert_equal(curly.email, 'curly@stooges.com')
    assert_equal(get_profile(curly).creation_method, str(UserProfile.CreationMethod.EXTERNAL))
    assert_equal(2, curly.groups.all().count(), curly.groups.all())

    reset_all_users()
    reset_all_groups()

    # Test import case sensitivity
    done.append(desktop.conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))
    import_ldap_users('Lårry', sync_groups=False, import_by_dn=False)
    assert_false(User.objects.filter(username='Lårry').exists())
    assert_true(User.objects.filter(username='lårry').exists())

    # Test lower case
    User.objects.filter(username__iexact='Rock').delete()
    import_ldap_users('Rock', sync_groups=False, import_by_dn=False)
    assert_true(User.objects.filter(username='Rock').exists())
    assert_false(User.objects.filter(username='rock').exists())

    done.append(desktop.conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))

    import_ldap_users('Rock', sync_groups=False, import_by_dn=False)
    assert_true(User.objects.filter(username='Rock').exists())
    assert_false(User.objects.filter(username='rock').exists())

    User.objects.filter(username='Rock').delete()
    import_ldap_users('Rock', sync_groups=False, import_by_dn=False)
    assert_false(User.objects.filter(username='Rock').exists())
    assert_true(User.objects.filter(username='rock').exists())
  finally:
    for finish in done:
      finish()


def test_add_ldap_users():
  done = []
  try:
    URL = reverse(add_ldap_users)

    reset_all_users()
    reset_all_groups()

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    c = make_logged_in_client('test', is_superuser=True)

    assert_true(c.get(URL))

    response = c.post(URL, dict(username_pattern='moe', password1='test', password2='test'))
    assert_true('Location' in response, response)
    assert_true('/useradmin/users' in response['Location'], response)

    response = c.post(URL, dict(username_pattern='bad_name', password1='test', password2='test'))
    assert_true('Could not' in response.context['form'].errors['username_pattern'][0], response)

    # Test wild card
    response = c.post(URL, dict(username_pattern='*r*', password1='test', password2='test'))
    assert_true('/useradmin/users' in response['Location'], response)

    # Test ignore case
    done.append(desktop.conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))
    User.objects.filter(username='moe').delete()
    assert_false(User.objects.filter(username='Moe').exists())
    assert_false(User.objects.filter(username='moe').exists())
    response = c.post(URL, dict(username_pattern='Moe', password1='test', password2='test'))
    assert_true('Location' in response, response)
    assert_true('/useradmin/users' in response['Location'], response)
    assert_false(User.objects.filter(username='Moe').exists())
    assert_true(User.objects.filter(username='moe').exists())

    # Test lower case
    done.append(desktop.conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))
    User.objects.filter(username__iexact='Rock').delete()
    assert_false(User.objects.filter(username='Rock').exists())
    assert_false(User.objects.filter(username='rock').exists())
    response = c.post(URL, dict(username_pattern='rock', password1='test', password2='test'))
    assert_true('Location' in response, response)
    assert_true('/useradmin/users' in response['Location'], response)
    assert_false(User.objects.filter(username='Rock').exists())
    assert_true(User.objects.filter(username='rock').exists())

  finally:
    for finish in done:
      finish()


def test_add_ldap_groups():
  URL = reverse(add_ldap_groups)

  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()


  c = make_logged_in_client(username='test', is_superuser=True)

  assert_true(c.get(URL))

  response = c.post(URL, dict(groupname_pattern='TestUsers'))
  assert_true('Location' in response, response)
  assert_true('/useradmin/groups' in response['Location'])

  # Test with space
  response = c.post(URL, dict(groupname_pattern='Test Administrators'))
  assert_true('Location' in response, response)
  assert_true('/useradmin/groups' in response['Location'], response)

  response = c.post(URL, dict(groupname_pattern='toolongnametoolongnametoolongnametoolongnametoolongnametoolongnametoolongnametoolongname'))
  assert_true('Ensure this value has at most 80 characters' in response.context['form'].errors['groupname_pattern'][0], response)

  # Test wild card
  response = c.post(URL, dict(groupname_pattern='*r*'))
  assert_true('/useradmin/groups' in response['Location'], response)

def test_sync_ldap_users_groups():
  URL = reverse(sync_ldap_users_groups)

  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  c = make_logged_in_client('test', is_superuser=True)

  assert_true(c.get(URL))
  assert_true(c.post(URL))

def test_ldap_exception_handling():
  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  class LdapTestConnectionError(LdapTestConnection):
    def find_users(self, user, find_by_dn=False):
      raise ldap.LDAPError('No such object')
  ldap_access.CACHED_LDAP_CONN = LdapTestConnectionError()

  c = make_logged_in_client('test', is_superuser=True)

  response = c.post(reverse(add_ldap_users), dict(username_pattern='moe', password1='test', password2='test'), follow=True)
  assert_true('There was an error when communicating with LDAP' in response.content, response)

@attr('requires_hadoop')
def test_ensure_home_directory_add_ldap_users():
  URL = reverse(add_ldap_users)

  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  cluster = pseudo_hdfs4.shared_cluster()
  c = make_logged_in_client(cluster.superuser, is_superuser=True)
  cluster.fs.setuser(cluster.superuser)

  assert_true(c.get(URL))

  response = c.post(URL, dict(username_pattern='moe', password1='test', password2='test'))
  assert_true('/useradmin/users' in response['Location'])
  assert_false(cluster.fs.exists('/user/moe'))

  # Try same thing with home directory creation.
  response = c.post(URL, dict(username_pattern='curly', password1='test', password2='test', ensure_home_directory=True))
  assert_true('/useradmin/users' in response['Location'])
  assert_true(cluster.fs.exists('/user/curly'))

  response = c.post(URL, dict(username_pattern='bad_name', password1='test', password2='test'))
  assert_true('Could not' in response.context['form'].errors['username_pattern'][0])
  assert_false(cluster.fs.exists('/user/bad_name'))

  # See if moe, who did not ask for his home directory, has a home directory.
  assert_false(cluster.fs.exists('/user/moe'))

  # Try wild card now
  response = c.post(URL, dict(username_pattern='*r*', password1='test', password2='test', ensure_home_directory=True))
  assert_true('/useradmin/users' in response['Location'])
  assert_true(cluster.fs.exists('/user/curly'))
  assert_true(cluster.fs.exists(u'/user/lårry'))
  assert_true(cluster.fs.exists('/user/otherguy'))

  # Clean up
  cluster.fs.rmtree('/user/curly')
  cluster.fs.rmtree(u'/user/lårry')
  cluster.fs.rmtree('/user/otherguy')

@attr('requires_hadoop')
def test_ensure_home_directory_sync_ldap_users_groups():
  URL = reverse(sync_ldap_users_groups)

  reset_all_users()
  reset_all_groups()

  # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
  ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

  cluster = pseudo_hdfs4.shared_cluster()
  c = make_logged_in_client(cluster.superuser, is_superuser=True)
  cluster.fs.setuser(cluster.superuser)

  response = c.post(reverse(add_ldap_users), dict(username_pattern='curly', password1='test', password2='test'))
  assert_false(cluster.fs.exists('/user/curly'))
  assert_true(c.post(URL, dict(ensure_home_directory=True)))
  assert_true(cluster.fs.exists('/user/curly'))

@attr('requires_hadoop')
def test_ensure_home_directory():
  reset_all_users()
  reset_all_groups()

  # Cluster and client for home directory creation
  cluster = pseudo_hdfs4.shared_cluster()
  c = make_logged_in_client(cluster.superuser, is_superuser=True, groupname='test1')
  cluster.fs.setuser(cluster.superuser)

  # Create a user with a home directory
  assert_false(cluster.fs.exists('/user/test1'))
  response = c.post('/useradmin/users/new', dict(username="test1", password1='test', password2='test', ensure_home_directory=True))
  assert_true(cluster.fs.exists('/user/test1'))
  dir_stat = cluster.fs.stats('/user/test1')
  assert_equal('test1', dir_stat.user)
  assert_equal('test1', dir_stat.group)
  assert_equal('40755', '%o' % dir_stat.mode)

  # Create a user, then add their home directory
  assert_false(cluster.fs.exists('/user/test2'))
  response = c.post('/useradmin/users/new', dict(username="test2", password1='test', password2='test'))
  assert_false(cluster.fs.exists('/user/test2'))
  response = c.post('/useradmin/users/edit/%s' % "test2", dict(username="test2", password1='test', password2='test', ensure_home_directory=True))
  assert_true(cluster.fs.exists('/user/test2'))
  dir_stat = cluster.fs.stats('/user/test2')
  assert_equal('test2', dir_stat.user)
  assert_equal('test2', dir_stat.group)
  assert_equal('40755', '%o' % dir_stat.mode)
