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

import ldap

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_equal, assert_false

import desktop.conf
from desktop.lib.test_utils import grant_access
from desktop.lib.django_test_util import make_logged_in_client
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.urls import reverse

from useradmin.models import LdapGroup, UserProfile, get_profile

from hadoop import pseudo_hdfs4
from hadoop.pseudo_hdfs4 import is_live_cluster
from views import sync_ldap_users, sync_ldap_groups, import_ldap_users, import_ldap_groups, \
                  add_ldap_users, add_ldap_groups, sync_ldap_users_groups

import ldap_access
from tests import BaseUserAdminTests, LdapTestConnection, reset_all_groups, reset_all_users

class TestUserAdminLdapDeprecated(BaseUserAdminTests):
  def test_useradmin_ldap_user_group_membership_sync(self):
    settings.MIDDLEWARE_CLASSES.append('useradmin.middleware.LdapSynchronizationMiddleware')

    try:
      # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
      ldap_access.CACHED_LDAP_CONN = LdapTestConnection()
      # Make sure LDAP groups exist or they won't sync
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)

      # Import curly who is part of TestUsers and Test Administrators
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'curly', sync_groups=False, import_by_dn=False)

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
      settings.MIDDLEWARE_CLASSES.remove('useradmin.middleware.LdapSynchronizationMiddleware')


  def test_useradmin_ldap_suboordinate_group_integration(self):
    reset = []

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    # Test old subgroups
    reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("suboordinate"))

    try:
      # Import groups only
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      test_users = Group.objects.get(name='TestUsers')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 0)

      # Import all members of TestUsers
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='TestUsers')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 3)

      # Should import a group, but will only sync already-imported members
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(User.objects.all().count(), 3)
      assert_equal(Group.objects.all().count(), 2)
      test_admins = Group.objects.get(name='Test Administrators')
      assert_equal(test_admins.user_set.all().count(), 2)
      larry = User.objects.get(username='lårry')
      assert_equal(test_admins.user_set.all().order_by('username')[1].username, larry.username)

      # Only sync already imported
      ldap_access.CACHED_LDAP_CONN.remove_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 2)
      assert_equal(User.objects.get(username='moe').groups.all().count(), 0)

      # Import missing user
      ldap_access.CACHED_LDAP_CONN.add_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 3)
      assert_equal(User.objects.get(username='moe').groups.all().count(), 1)

      # Import all members of TestUsers and members of subgroups
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='TestUsers')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 4)

      # Make sure Hue groups with naming collisions don't get marked as LDAP groups
      hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
      hue_group = Group.objects.create(name='OtherGroup')
      hue_group.user_set.add(hue_user)
      hue_group.save()
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_false(LdapGroup.objects.filter(group=hue_group).exists())
      assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
    finally:
      for finish in reset:
        finish()


  def test_useradmin_ldap_nested_group_integration(self):
    reset = []

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    # Test old subgroups
    reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("nested"))

    try:
      # Import groups only
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      test_users = Group.objects.get(name='TestUsers')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 0)

      # Import all members of TestUsers
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='TestUsers')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 3)

      # Should import a group, but will only sync already-imported members
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(User.objects.all().count(), 3)
      assert_equal(Group.objects.all().count(), 2)
      test_admins = Group.objects.get(name='Test Administrators')
      assert_equal(test_admins.user_set.all().count(), 2)
      larry = User.objects.get(username='lårry')
      assert_equal(test_admins.user_set.all().order_by('username')[1].username, larry.username)

      # Only sync already imported
      assert_equal(test_users.user_set.all().count(), 3)
      ldap_access.CACHED_LDAP_CONN.remove_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 2)
      assert_equal(User.objects.get(username='moe').groups.all().count(), 0)

      # Import missing user
      ldap_access.CACHED_LDAP_CONN.add_user_group_for_test('uid=moe,ou=People,dc=example,dc=com', 'TestUsers')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 3)
      assert_equal(User.objects.get(username='moe').groups.all().count(), 1)

      # Import all members of TestUsers and not members of suboordinate groups (even though specified)
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='TestUsers')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 3)

      # Nested group import
      # First without recursive import, then with.
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'NestedGroups', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      nested_groups = Group.objects.get(name='NestedGroups')
      nested_group = Group.objects.get(name='NestedGroup')
      assert_true(LdapGroup.objects.filter(group=nested_groups).exists())
      assert_true(LdapGroup.objects.filter(group=nested_group).exists())
      assert_equal(nested_groups.user_set.all().count(), 0, nested_groups.user_set.all())
      assert_equal(nested_group.user_set.all().count(), 0, nested_group.user_set.all())

      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'NestedGroups', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
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
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_false(LdapGroup.objects.filter(group=hue_group).exists())
      assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
    finally:
      for finish in reset:
        finish()


  def test_useradmin_ldap_suboordinate_posix_group_integration(self):
    reset = []

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    # Test old subgroups
    reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("suboordinate"))

    try:
      # Import groups only
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      test_users = Group.objects.get(name='PosixGroup')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 0)

      # Import all members of TestUsers
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='PosixGroup')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 2)

      # Should import a group, but will only sync already-imported members
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(User.objects.all().count(), 2, User.objects.all())
      assert_equal(Group.objects.all().count(), 2, Group.objects.all())
      test_admins = Group.objects.get(name='Test Administrators')
      assert_equal(test_admins.user_set.all().count(), 1)
      larry = User.objects.get(username='lårry')
      assert_equal(test_admins.user_set.all().order_by('username')[0].username, larry.username)

      # Only sync already imported
      ldap_access.CACHED_LDAP_CONN.remove_posix_user_group_for_test('posix_person', 'PosixGroup')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 1)
      assert_equal(User.objects.get(username='posix_person').groups.all().count(), 0)

      # Import missing user
      ldap_access.CACHED_LDAP_CONN.add_posix_user_group_for_test('posix_person', 'PosixGroup')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 2)
      assert_equal(User.objects.get(username='posix_person').groups.all().count(), 1)

      # Import all members of PosixGroup and members of subgroups
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='PosixGroup')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 3)

      # Make sure Hue groups with naming collisions don't get marked as LDAP groups
      hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
      hue_group = Group.objects.create(name='OtherGroup')
      hue_group.user_set.add(hue_user)
      hue_group.save()
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_false(LdapGroup.objects.filter(group=hue_group).exists())
      assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
    finally:
      for finish in reset:
        finish()


  def test_useradmin_ldap_nested_posix_group_integration(self):
    reset = []

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    # Test nested groups
    reset.append(desktop.conf.LDAP.SUBGROUPS.set_for_testing("nested"))

    try:
      # Import groups only
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      test_users = Group.objects.get(name='PosixGroup')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 0)

      # Import all members of TestUsers
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='PosixGroup')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 2)

      # Should import a group, but will only sync already-imported members
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(User.objects.all().count(), 2, User.objects.all())
      assert_equal(Group.objects.all().count(), 2, Group.objects.all())
      test_admins = Group.objects.get(name='Test Administrators')
      assert_equal(test_admins.user_set.all().count(), 1)
      larry = User.objects.get(username='lårry')
      assert_equal(test_admins.user_set.all().order_by('username')[0].username, larry.username)

      # Only sync already imported
      ldap_access.CACHED_LDAP_CONN.remove_posix_user_group_for_test('posix_person', 'PosixGroup')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 1)
      assert_equal(User.objects.get(username='posix_person').groups.all().count(), 0)

      # Import missing user
      ldap_access.CACHED_LDAP_CONN.add_posix_user_group_for_test('posix_person', 'PosixGroup')
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=True, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_equal(test_users.user_set.all().count(), 2)
      assert_equal(User.objects.get(username='posix_person').groups.all().count(), 1)

      # Import all members of PosixGroup and members of subgroups (there should be no subgroups)
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'PosixGroup', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
      test_users = Group.objects.get(name='PosixGroup')
      assert_true(LdapGroup.objects.filter(group=test_users).exists())
      assert_equal(test_users.user_set.all().count(), 2)

      # Import all members of NestedPosixGroups and members of subgroups
      reset_all_users()
      reset_all_groups()
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'NestedPosixGroups', import_members=True, import_members_recursive=True, sync_users=True, import_by_dn=False)
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
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'OtherGroup', import_members=False, import_members_recursive=False, sync_users=True, import_by_dn=False)
      assert_false(LdapGroup.objects.filter(group=hue_group).exists())
      assert_true(hue_group.user_set.filter(username=hue_user.username).exists())
    finally:
      for finish in reset:
        finish()


  def test_useradmin_ldap_user_integration(self):
    done = []
    try:
      # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
      ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

      # Try importing a user
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'lårry', sync_groups=False, import_by_dn=False)
      larry = User.objects.get(username='lårry')
      assert_true(larry.first_name == 'Larry')
      assert_true(larry.last_name == 'Stooge')
      assert_true(larry.email == 'larry@stooges.com')
      assert_true(get_profile(larry).creation_method == UserProfile.CreationMethod.EXTERNAL.name)

      # Should be a noop
      sync_ldap_users(ldap_access.CACHED_LDAP_CONN)
      sync_ldap_groups(ldap_access.CACHED_LDAP_CONN)
      assert_equal(User.objects.all().count(), 1)
      assert_equal(Group.objects.all().count(), 0)

      # Make sure that if a Hue user already exists with a naming collision, we
      # won't overwrite any of that user's information.
      hue_user = User.objects.create(username='otherguy', first_name='Different', last_name='Guy')
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'otherguy', sync_groups=False, import_by_dn=False)
      hue_user = User.objects.get(username='otherguy')
      assert_equal(get_profile(hue_user).creation_method, UserProfile.CreationMethod.HUE.name)
      assert_equal(hue_user.first_name, 'Different')

      # Make sure LDAP groups exist or they won't sync
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
      # Try importing a user and sync groups
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'curly', sync_groups=True, import_by_dn=False)
      curly = User.objects.get(username='curly')
      assert_equal(curly.first_name, 'Curly')
      assert_equal(curly.last_name, 'Stooge')
      assert_equal(curly.email, 'curly@stooges.com')
      assert_equal(get_profile(curly).creation_method, UserProfile.CreationMethod.EXTERNAL.name)
      assert_equal(2, curly.groups.all().count(), curly.groups.all())

      reset_all_users()
      reset_all_groups()
    finally:
      for finish in done:
        finish()


  @attr('integration')
  def test_useradmin_ldap_case_sensitivity(self):
    if is_live_cluster():
      raise SkipTest('HUE-2897: Cannot yet guarantee database is case sensitive')

    done = []
    try:
      # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
      ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

      # Test import case sensitivity
      done.append(desktop.conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'Lårry', sync_groups=False, import_by_dn=False)
      assert_false(User.objects.filter(username='Lårry').exists())
      assert_true(User.objects.filter(username='lårry').exists())

      # Test lower case
      User.objects.filter(username__iexact='Rock').delete()
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'Rock', sync_groups=False, import_by_dn=False)
      assert_false(User.objects.filter(username='Rock').exists())
      assert_true(User.objects.filter(username='rock').exists())

      done.append(desktop.conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))

      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'Rock', sync_groups=False, import_by_dn=False)
      assert_false(User.objects.filter(username='Rock').exists())
      assert_true(User.objects.filter(username='rock').exists())

      User.objects.filter(username='Rock').delete()
      import_ldap_users(ldap_access.CACHED_LDAP_CONN, 'Rock', sync_groups=False, import_by_dn=False)
      assert_false(User.objects.filter(username='Rock').exists())
      assert_true(User.objects.filter(username='rock').exists())
    finally:
      for finish in done:
        finish()


  def test_add_ldap_users(self):
    done = []
    try:
      URL = reverse(add_ldap_users)

      # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
      ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

      c = make_logged_in_client('test', is_superuser=True)

      assert_true(c.get(URL))

      response = c.post(URL, dict(username_pattern='moe', password1='test', password2='test'))
      assert_true('Location' in response, response)
      assert_true('/useradmin/users' in response['Location'], response)

      response = c.post(URL, dict(username_pattern='bad_name', password1='test', password2='test'))
      assert_true('Could not' in response.context[0]['form'].errors['username_pattern'][0], response)

      # Test wild card
      response = c.post(URL, dict(username_pattern='*rr*', password1='test', password2='test'))
      assert_true('/useradmin/users' in response['Location'], response)

      # Test regular with spaces (should fail)
      response = c.post(URL, dict(username_pattern='user with space', password1='test', password2='test'))
      assert_true("Username must not contain whitespaces and ':'" in response.context[0]['form'].errors['username_pattern'][0], response)

      # Test dn with spaces in username and dn (should fail)
      response = c.post(URL, dict(username_pattern='uid=user with space,ou=People,dc=example,dc=com', password1='test', password2='test', dn=True))
      assert_true("Could not get LDAP details for users in pattern" in response.content, response)
      response = c.get(reverse(desktop.views.log_view))
      assert_true("{username}: Username must not contain whitespaces".format(username='user with space') in response.content, response.content)

      # Test dn with spaces in dn, but not username (should succeed)
      response = c.post(URL, dict(username_pattern='uid=user without space,ou=People,dc=example,dc=com', password1='test', password2='test', dn=True))
      assert_true(User.objects.filter(username='spaceless').exists())

    finally:
      for finish in done:
        finish()


  @attr('integration')
  def test_add_ldap_users_case_sensitivity(self):
    if is_live_cluster():
      raise SkipTest('HUE-2897: Cannot yet guarantee database is case sensitive')

    done = []
    try:
      URL = reverse(add_ldap_users)

      reset_all_users()
      reset_all_groups()

      # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
      ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

      c = make_logged_in_client('test', is_superuser=True)

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


  def test_add_ldap_groups(self):
    URL = reverse(add_ldap_groups)

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

    response = c.post(URL, dict(groupname_pattern='toolongnametoolongnametoolongnametoolongnametoolongnametoolongname'
                                                  'toolongnametoolongnametoolongnametoolongnametoolongnametoolongname'
                                                  'toolongnametoolongnametoolongnametoolongnametoolongnametoolongname'
                                                  'toolongnametoolongnametoolongnametoolongnametoolongnametoolongname'))
    assert_true('Ensure this value has at most 256 characters' in response.context[0]['form'].errors['groupname_pattern'][0], response)

    # Test wild card
    response = c.post(URL, dict(groupname_pattern='*r*'))
    assert_true('/useradmin/groups' in response['Location'], response)

  def test_sync_ldap_users_groups(self):
    URL = reverse(sync_ldap_users_groups)

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    c = make_logged_in_client('test', is_superuser=True)

    assert_true(c.get(URL))
    assert_true(c.post(URL))

  def test_ldap_exception_handling(self):
    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    class LdapTestConnectionError(LdapTestConnection):
      def find_users(self, user, find_by_dn=False):
        raise ldap.LDAPError('No such object')
    ldap_access.CACHED_LDAP_CONN = LdapTestConnectionError()

    c = make_logged_in_client('test', is_superuser=True)

    response = c.post(reverse(add_ldap_users), dict(username_pattern='moe', password1='test', password2='test'), follow=True)
    assert_true('There was an error when communicating with LDAP' in response.content, response)

class TestUserAdminLdapDeprecatedWithHadoop(BaseUserAdminTests):
  requires_hadoop = True
  integration = True

  def test_ensure_home_directory_add_ldap_users(self):
    try:
      URL = reverse(add_ldap_users)

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
      assert_true('Could not' in response.context[0]['form'].errors['username_pattern'][0])
      assert_false(cluster.fs.exists('/user/bad_name'))

      # See if moe, who did not ask for his home directory, has a home directory.
      assert_false(cluster.fs.exists('/user/moe'))

      # Try wild card now
      response = c.post(URL, dict(username_pattern='*rr*', password1='test', password2='test', ensure_home_directory=True))
      assert_true('/useradmin/users' in response['Location'])
      assert_true(cluster.fs.exists('/user/curly'))
      assert_true(cluster.fs.exists(u'/user/lårry'))
      assert_false(cluster.fs.exists('/user/otherguy'))
    finally:
      # Clean up
      if cluster.fs.exists('/user/curly'):
        cluster.fs.rmtree('/user/curly')
      if cluster.fs.exists(u'/user/lårry'):
        cluster.fs.rmtree(u'/user/lårry')
      if cluster.fs.exists('/user/otherguy'):
        cluster.fs.rmtree('/user/otherguy')

  def test_ensure_home_directory_sync_ldap_users_groups(self):
    URL = reverse(sync_ldap_users_groups)

    # Set up LDAP tests to use a LdapTestConnection instead of an actual LDAP connection
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    cluster = pseudo_hdfs4.shared_cluster()
    c = make_logged_in_client(cluster.superuser, is_superuser=True)
    cluster.fs.setuser(cluster.superuser)

    c.post(reverse(add_ldap_users), dict(username_pattern='curly', password1='test', password2='test'))
    assert_false(cluster.fs.exists('/user/curly'))
    assert_true(c.post(URL, dict(ensure_home_directory=True)))
    assert_true(cluster.fs.exists('/user/curly'))
