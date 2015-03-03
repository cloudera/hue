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

from nose.tools import assert_true, assert_false, assert_equal

from django.contrib.auth.models import User
from django.test.client import Client
from django.conf import settings

from desktop import conf, middleware
from desktop.auth import backend
from django_auth_ldap import backend as django_auth_ldap_backend
from desktop.lib.django_test_util import make_logged_in_client
from hadoop.test_base import PseudoHdfsTestBase
from hadoop import pseudo_hdfs4

from useradmin import ldap_access
from useradmin.tests import LdapTestConnection


class TestLoginWithHadoop(PseudoHdfsTestBase):

  def setUp(self):
    # Simulate first login ever
    User.objects.all().delete()
    self.c = Client()

  def test_login(self):
    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context['first_login_ever'])

    response = self.c.post('/accounts/login/', dict(username="foo", password="foo"))
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_true(self.fs.exists("/user/foo"))

    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

  def test_login_home_creation_failure(self):
    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context['first_login_ever'])

    # Create home directory as a file in order to fail in the home creation later
    cluster = pseudo_hdfs4.shared_cluster()
    fs = cluster.fs
    assert_false(cluster.fs.exists("/user/foo2"))
    fs.do_as_superuser(fs.create, "/user/foo2")

    response = self.c.post('/accounts/login/', dict(username="foo2", password="foo2"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('/beeswax' in response.content, response.content)
    # Custom login process should not do 'http-equiv="refresh"' but call the correct view
    # 'Could not create home directory.' won't show up because the messages are consumed before


class TestLdapLogin(PseudoHdfsTestBase):
  reset = []

  @classmethod
  def setup_class(cls):
    PseudoHdfsTestBase.setup_class()

    cls.backend = django_auth_ldap_backend.LDAPBackend
    django_auth_ldap_backend.LDAPBackend = MockLdapBackend

    # Need to recreate LdapBackend class with new monkey patched base class
    reload(backend)

    cls.old_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ("desktop.auth.backend.LdapBackend",)

  @classmethod
  def teardown_class(cls):
    django_auth_ldap_backend.LDAPBackend = cls.backend

    # Need to recreate LdapBackend class with old base class
    reload(backend)

    settings.AUTHENTICATION_BACKENDS = cls.old_backends

  def tearDown(self):
    for finish in self.reset:
      finish()

  def setUp(self):
    # Simulate first login ever
    User.objects.all().delete()
    self.c = Client()

    self.reset.append(conf.LDAP.LDAP_URL.set_for_testing('does not matter'))

  def test_login(self):
    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

    response = self.c.post('/accounts/login/', {
        'username': "ldap1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_true(self.fs.exists("/user/ldap1"))

    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

  def test_login_home_creation_failure(self):
    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

    # Create home directory as a file in order to fail in the home creation later
    cluster = pseudo_hdfs4.shared_cluster()
    fs = cluster.fs
    assert_false(cluster.fs.exists("/user/ldap2"))
    fs.do_as_superuser(fs.create, "/user/ldap2")

    response = self.c.post('/accounts/login/', {
        'username': "ldap2",
        'password': "ldap2"
    }, follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('/beeswax' in response.content, response.content)
    # Custom login process should not do 'http-equiv="refresh"' but call the correct view
    # 'Could not create home directory.' won't show up because the messages are consumed before

  def test_login_ignore_case(self):
    self.reset.append(conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))

    response = self.c.post('/accounts/login/', {
        'username': "LDAP1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('LDAP1', User.objects.all()[0].username)

    self.c.logout()

    response = self.c.post('/accounts/login/', {
        'username': "ldap1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('LDAP1', User.objects.all()[0].username)

  def test_login_force_lower_case(self):
    self.reset.append(conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))

    response = self.c.post('/accounts/login/', {
        'username': "LDAP1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))

    self.c.logout()

    response = self.c.post('/accounts/login/', {
        'username': "ldap1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('ldap1', User.objects.all()[0].username)

  def test_login_force_lower_case_and_ignore_case(self):
    self.reset.append(conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))
    self.reset.append(conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))

    response = self.c.post('/accounts/login/', {
        'username': "LDAP1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('ldap1', User.objects.all()[0].username)

    self.c.logout()

    response = self.c.post('/accounts/login/', {
        'username': "ldap1",
        'password': "ldap1"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('ldap1', User.objects.all()[0].username)

  def test_import_groups_on_login(self):
    self.reset.append(conf.LDAP.SYNC_GROUPS_ON_LOGIN.set_for_testing(True))
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    response = self.c.post('/accounts/login/', {
      'username': "curly",
      'password': "ldap1"
    })
    assert_equal(302, response.status_code, response.status_code)
    assert_equal(1, len(User.objects.all()))
    # The two curly are a part of in LDAP and the default group.
    assert_equal(3, User.objects.all()[0].groups.all().count(), User.objects.all()[0].groups.all())


class TestRemoteUserLogin(object):
  reset = []

  def setUp(self):
    User.objects.all().delete()
    self.reset.append( conf.AUTH.BACKEND.set_for_testing('desktop.auth.backend.RemoteUserDjangoBackend') )
    self.reset.append( conf.AUTH.REMOTE_USER_HEADER.set_for_testing('REMOTE_USER') ) # Set for middlware
    self.backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.RemoteUserDjangoBackend',)
    self.remote_user_middleware_header = middleware.HueRemoteUserMiddleware.header
    middleware.HueRemoteUserMiddleware.header = conf.AUTH.REMOTE_USER_HEADER.get() # Set for middlware
    self.c = Client()

  def tearDown(self):
    middleware.HueRemoteUserMiddleware.header = self.remote_user_middleware_header
    settings.AUTHENTICATION_BACKENDS = self.backends
    for finish in self.reset:
      finish()

  def test_normal(self):
    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

    assert_equal(0, len(User.objects.all()))
    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "foo3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('foo3', User.objects.all()[0].username)

  def test_ignore_case(self):
    self.reset.append( conf.AUTH.IGNORE_USERNAME_CASE.set_for_testing(True) )

    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "foo3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('foo3', User.objects.all()[0].username)

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('foo3', User.objects.all()[0].username)

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO4"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all()))
    assert_equal('foo4', User.objects.all()[1].username)

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "foo4"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all()))
    assert_equal('foo4', User.objects.all()[1].username)

  def test_force_lower_case(self):
    self.reset.append( conf.AUTH.FORCE_USERNAME_LOWERCASE.set_for_testing(True) )

    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context['first_login_ever'])

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "foo3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('foo3', User.objects.all()[0].username)

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('foo3', User.objects.all()[0].username)

  def test_ignore_case_and_force_lower_case(self):
    reset = conf.AUTH.FORCE_USERNAME_LOWERCASE.set_for_testing(False)
    try:
      response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO3"})
      assert_equal(200, response.status_code, "Expected ok status.")
      assert_equal(1, len(User.objects.all()))
      assert_equal('FOO3', User.objects.all()[0].username)
    finally:
      reset()

    self.reset.append( conf.AUTH.FORCE_USERNAME_LOWERCASE.set_for_testing(True) )
    self.reset.append( conf.AUTH.IGNORE_USERNAME_CASE.set_for_testing(True) )

    # Previously existing users should not be forced to lower case.
    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('FOO3', User.objects.all()[0].username)

    # New users should be forced to lowercase.
    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO4"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all()))
    assert_equal('foo4', User.objects.all()[1].username)


class TestLogin(object):
  reset = []

  def setUp(self):
    # Simulate first login ever
    User.objects.all().delete()
    self.c = Client()

  def tearDown(self):
    for finish in self.reset:
      finish()

  def test_bad_first_user(self):
    self.reset.append( conf.AUTH.BACKEND.set_for_testing("desktop.auth.backend.AllowFirstUserDjangoBackend") )

    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context['first_login_ever'])

    response = self.c.post('/accounts/login/', dict(username="foo 1", password="foo"))
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('This value may contain only letters, numbers and @/./+/-/_ characters.' in response.content, response)

  def test_non_jframe_login(self):
    client = make_logged_in_client(username="test", password="test")
    # Logout first
    client.get('/accounts/logout')
    # Login
    response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
    assert_true(any(["admin_wizard.mako" in _template.filename for _template in response.templates]), response.content) # Go to superuser wizard

  def test_login_expiration(self):
    """ Expiration test without superusers """
    old_settings = settings.ADMINS
    self.reset.append( conf.AUTH.BACKEND.set_for_testing("desktop.auth.backend.AllowFirstUserDjangoBackend") )
    self.reset.append( conf.AUTH.EXPIRES_AFTER.set_for_testing(0) )
    self.reset.append( conf.AUTH.EXPIRE_SUPERUSERS.set_for_testing(False) )

    client = make_logged_in_client(username="test", password="test")
    client.get('/accounts/logout')
    user = User.objects.get(username="test")

    # Login successfully
    try:
      user.is_superuser = True
      user.save()
      response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
      assert_equal(200, response.status_code, "Expected ok status.")

      client.get('/accounts/logout')

      # Login fail
      settings.ADMINS = [('test', 'test@test.com')]
      user.is_superuser = False
      user.save()
      response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
      assert_equal(200, response.status_code, "Expected ok status.")
      assert_true('Account deactivated. Please contact an <a href="mailto:test@test.com">administrator</a>' in response.content, response.content)

      # Failure should report an inactive user without admin link
      settings.ADMINS = []
      response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
      assert_equal(200, response.status_code, "Expected ok status.")
      assert_true("Account deactivated. Please contact an administrator." in response.content, response.content)
    finally:
      settings.ADMINS = old_settings

  def test_login_expiration_with_superusers(self):
    """ Expiration test with superusers """
    self.reset.append( conf.AUTH.BACKEND.set_for_testing("desktop.auth.backend.AllowFirstUserDjangoBackend") )
    self.reset.append( conf.AUTH.EXPIRES_AFTER.set_for_testing(0) )
    self.reset.append( conf.AUTH.EXPIRE_SUPERUSERS.set_for_testing(True) )

    client = make_logged_in_client(username="test", password="test")
    client.get('/accounts/logout')
    user = User.objects.get(username="test")

    # Login fail
    user.is_superuser = True
    user.save()
    response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected unauthorized status.")


class MockLdapBackend(object):
  settings = django_auth_ldap_backend.LDAPSettings()

  def get_or_create_user(self, username, ldap_user):
    return User.objects.get_or_create(username)

  def authenticate(self, username=None, password=None, server=None):
    user, created = self.get_or_create_user(username, None)
    return user

  def get_user(self, user_id):
    return User.objects.get(id=user_id)
