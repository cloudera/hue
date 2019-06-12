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

import datetime
from nose.tools import assert_true, assert_false, assert_equal

from django_auth_ldap import backend as django_auth_ldap_backend
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test.client import Client

from hadoop.test_base import PseudoHdfsTestBase
from hadoop import pseudo_hdfs4
from useradmin import ldap_access
from useradmin.models import get_default_user_group
from useradmin.tests import LdapTestConnection
from useradmin.views import import_ldap_groups

from desktop import conf, middleware
from desktop.auth import backend
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group


def get_mocked_config():
  return {'mocked_ldap': {
    'users': {},
    'groups': {}
  }}

class TestLoginWithHadoop(PseudoHdfsTestBase):
  integration = True
  reset = []
  test_username = 'test_login_with_hadoop'

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()
    PseudoHdfsTestBase.setup_class()

    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.AllowFirstUserDjangoBackend',)

  @classmethod
  def teardown_class(cls):
    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

  def setUp(self):
    self.c = Client()

    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.AllowFirstUserDjangoBackend']) )
    self.reset.append(conf.LDAP.SYNC_GROUPS_ON_LOGIN.set_for_testing(False))

  def tearDown(self):
    User.objects.all().delete()

    for finish in self.reset:
      finish()

    if self.cluster.fs.do_as_user(self.test_username, self.cluster.fs.exists, "/user/%s" % self.test_username):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/%s" % self.test_username)

  def test_login(self):
    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context[0]['first_login_ever'])

    response = self.c.post('/hue/accounts/login/', dict(username=self.test_username, password="foo"))
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(response.url, "/")
    assert_true(self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username))

  def test_login_old(self):
    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context[0]['first_login_ever'])

    response = self.c.post('/accounts/login/', dict(username=self.test_username, password="foo"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username))

    response = self.c.get('/accounts/login/')
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(response.url, "/")

  def test_login_home_creation_failure(self):
    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context[0]['first_login_ever'])

    # Create home directory as a file in order to fail in the home creation later
    cluster = pseudo_hdfs4.shared_cluster()
    fs = cluster.fs
    assert_false(cluster.fs.exists("/user/%s" % self.test_username))
    fs.do_as_superuser(fs.create, "/user/%s" % self.test_username)

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "test-hue-foo2",
      }, follow=True)

    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('/about' in response.content, response.content)
    # Custom login process should not do 'http-equiv="refresh"' but call the correct view
    # 'Could not create home directory.' won't show up because the messages are consumed before

  def test_login_expiration(self):
    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "test-hue-foo2",
      }, follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")

    self.reset.append(conf.AUTH.EXPIRES_AFTER.set_for_testing(10000))
    user = User.objects.get(username=self.test_username)
    user.last_login = datetime.datetime.now() + datetime.timedelta(days=-365)
    user.save()

    # Deactivate user
    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "test-hue-foo2",
      }, follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true("Account deactivated. Please contact an administrator." in response.content, response.content)

    # Activate user
    user = User.objects.get(username=self.test_username)
    user.is_active = True
    user.save()
    response = self.c.post('/hue/accounts/login/', dict(username=self.test_username, password="foo"))
    assert_equal(200, response.status_code, "Expected ok status.")


class TestLdapLogin(PseudoHdfsTestBase):

  reset = []
  test_username = 'test_ldap_login'

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()

    PseudoHdfsTestBase.setup_class()

    cls.ldap_backend = django_auth_ldap_backend.LDAPBackend
    django_auth_ldap_backend.LDAPBackend = MockLdapBackend

    # Override auth backend, settings are only loaded from conf at initialization so we can't use set_for_testing
    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.LdapBackend',)

    # Need to recreate LdapBackend class with new monkey patched base class
    reload(backend)

  @classmethod
  def teardown_class(cls):
    django_auth_ldap_backend.LDAPBackend = cls.ldap_backend

    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

    reload(backend)

  def setUp(self):
    self.c = Client()
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.LdapBackend']) )
    self.reset.append(conf.LDAP.LDAP_URL.set_for_testing('does not matter'))
    self.reset.append(conf.LDAP.SYNC_GROUPS_ON_LOGIN.set_for_testing(False))

  def tearDown(self):
    User.objects.all().delete()

    for finish in self.reset:
      finish()

    if self.cluster.fs.do_as_user(self.test_username, self.cluster.fs.exists, "/user/%s" % self.test_username):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/%s" % self.test_username)

    if self.cluster.fs.do_as_user("curly", self.cluster.fs.exists, "/user/curly"):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/curly")

  def test_login(self):
    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context[0]['first_login_ever'])

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "ldap1",
        'server': "LDAP"
    })

    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(response.url, "/")
    assert_true(self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username))

  def test_login_failure_for_bad_username(self):
    self.reset.append(conf.LDAP.LDAP_SERVERS.set_for_testing(get_mocked_config()))

    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")

    response = self.c.post('/hue/accounts/login/', dict(username="test1*)(&(objectClass=*)", password="foo"))
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('Invalid username or password' in response.content, response)

  def test_login_does_not_reset_groups(self):
    client = make_logged_in_client(username=self.test_username, password="test")

    user = User.objects.get(username=self.test_username)
    test_group, created = Group.objects.get_or_create(name=self.test_username)
    default_group = get_default_user_group()

    user.groups.all().delete()
    assert_false(user.groups.exists())

    # No groups
    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal([default_group.name], [i for i in user.groups.values_list('name', flat=True)])

    add_to_group(self.test_username, self.test_username)

    # Two groups
    client.get('/accounts/logout')
    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(set([default_group.name, test_group.name]), set(user.groups.values_list('name', flat=True)))

    user.groups.filter(name=default_group.name).delete()
    assert_equal(set([test_group.name]), set(user.groups.values_list('name', flat=True)))

    # Keep manual group only, don't re-add default group
    client.get('/accounts/logout')
    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal([test_group.name], list(user.groups.values_list('name', flat=True)))

    user.groups.remove(test_group)
    assert_false(user.groups.exists())

    # Re-add default group
    client.get('/accounts/logout')
    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal([default_group.name], list(user.groups.values_list('name', flat=True)))

  def test_login_home_creation_failure(self):
    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context[0]['first_login_ever'])

    # Create home directory as a file in order to fail in the home creation later
    cluster = pseudo_hdfs4.shared_cluster()
    fs = cluster.fs
    assert_false(self.cluster.fs.do_as_user(self.test_username, cluster.fs.exists, "/user/%s" % self.test_username))
    fs.do_as_superuser(fs.create, "/user/%s" % self.test_username)

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "test-hue-ldap2",
        'server': "LDAP"
    }, follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('/about' in response.content, response.content)
    # Custom login process should not do 'http-equiv="refresh"' but call the correct view
    # 'Could not create home directory.' won't show up because the messages are consumed before

  def test_login_ignore_case(self):
    self.reset.append(conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username.upper(),
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

    self.c.logout()

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

  def test_login_force_lower_case(self):
    self.reset.append(conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username.upper(),
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))

    self.c.logout()

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

  def test_login_force_lower_case_and_ignore_case(self):
    self.reset.append(conf.LDAP.IGNORE_USERNAME_CASE.set_for_testing(True))
    self.reset.append(conf.LDAP.FORCE_USERNAME_LOWERCASE.set_for_testing(True))

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username.upper(),
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

    self.c.logout()

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

  def test_import_groups_on_login(self):
    self.reset.append(conf.LDAP.SYNC_GROUPS_ON_LOGIN.set_for_testing(True))
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()
    # Make sure LDAP groups exist or they won't sync
    import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'TestUsers', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)
    import_ldap_groups(ldap_access.CACHED_LDAP_CONN, 'Test Administrators', import_members=False, import_members_recursive=False, sync_users=False, import_by_dn=False)

    response = self.c.post('/hue/accounts/login/', {
      'username': "curly",
      'password': "ldap1",
      'server': "TestUsers"
    })
    assert_equal(302, response.status_code, response.status_code)
    assert_equal(1, len(User.objects.all()))
    # The two curly are a part of in LDAP and the default group.
    assert_equal(3, User.objects.all()[0].groups.all().count(), User.objects.all()[0].groups.all())


class TestRemoteUserLogin(PseudoHdfsTestBase):

  reset = []
  test_username = "test_remote_user_login"

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()

    PseudoHdfsTestBase.setup_class()

    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.RemoteUserDjangoBackend',)
    cls.remote_user_middleware_header = middleware.HueRemoteUserMiddleware.header
    middleware.HueRemoteUserMiddleware.header = conf.AUTH.REMOTE_USER_HEADER.get()

  @classmethod
  def teardown_class(cls):
    middleware.HueRemoteUserMiddleware.header = cls.remote_user_middleware_header
    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

  def setUp(self):
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.RemoteUserDjangoBackend']) )
    self.reset.append( conf.AUTH.REMOTE_USER_HEADER.set_for_testing('REMOTE_USER') )  # Set for middleware

    self.c = Client()

  def tearDown(self):
    for finish in self.reset:
      finish()

    User.objects.all().delete()

    if self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/%s" % self.test_username)

    if self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s_%s" % (self.test_username, '2')):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/%s_%s" % (self.test_username, '2'))

  def test_normal(self):
    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context[0]['first_login_ever'])

    assert_equal(0, len(User.objects.all()))
    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

  def test_ignore_case(self):
    self.reset.append( conf.AUTH.IGNORE_USERNAME_CASE.set_for_testing(True) )

    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context[0]['first_login_ever'])

    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username.upper()})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": "%s_%s" % (self.test_username.upper(), '2')})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all().order_by('username')))
    assert_equal("%s_%s" % (self.test_username, '2'), User.objects.all().order_by('username')[1].username)

    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": "%s_%s" % (self.test_username, '2')})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all()))
    assert_equal("%s_%s" % (self.test_username, '2'), User.objects.all().order_by('username')[1].username)

  def test_force_lower_case(self):
    self.reset.append( conf.AUTH.FORCE_USERNAME_LOWERCASE.set_for_testing(True) )

    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_false(response.context[0]['first_login_ever'])

    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)

    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username.upper()})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username, User.objects.all()[0].username)


  def test_ignore_case_and_force_lower_case(self):
    reset = conf.AUTH.FORCE_USERNAME_LOWERCASE.set_for_testing(False)
    try:
      response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username.upper()})
      assert_equal(200, response.status_code, "Expected ok status.")
      assert_equal(1, len(User.objects.all()))
      assert_equal(self.test_username.upper(), User.objects.all()[0].username)
    finally:
      reset()

    self.reset.append( conf.AUTH.FORCE_USERNAME_LOWERCASE.set_for_testing(True) )
    self.reset.append( conf.AUTH.IGNORE_USERNAME_CASE.set_for_testing(True) )

    # Previously existing users should not be forced to lower case.
    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": self.test_username.upper()})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal(self.test_username.upper(), User.objects.all()[0].username)

    # New users should be forced to lowercase.
    response = self.c.post('/hue/accounts/login/', {}, **{"REMOTE_USER": "%s_%s" % (self.test_username.upper(), '2')})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all()))
    assert_equal("%s_%s" % (self.test_username, '2'), User.objects.all().order_by('username')[1].username)


class TestMultipleBackendLogin(PseudoHdfsTestBase):
  integration = True
  reset = []
  test_username = "test_multiple_login"

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()

    PseudoHdfsTestBase.setup_class()

    cls.ldap_backend = django_auth_ldap_backend.LDAPBackend
    django_auth_ldap_backend.LDAPBackend = MockLdapBackend

    # Override auth backend, settings are only loaded from conf at initialization so we can't use set_for_testing
    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.LdapBackend','desktop.auth.backend.AllowFirstUserDjangoBackend')

    # Need to recreate LdapBackend class with new monkey patched base class
    reload(backend)

  @classmethod
  def teardown_class(cls):
    django_auth_ldap_backend.LDAPBackend = cls.ldap_backend

    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

    reload(backend)

  def setUp(self):
    self.c = Client()
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.LdapBackend','desktop.auth.backend.AllowFirstUserDjangoBackend']))
    self.reset.append(conf.LDAP.LDAP_URL.set_for_testing('does not matter'))

  def tearDown(self):
    User.objects.all().delete()

    for finish in self.reset:
      finish()

    if self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/%s" % self.test_username)

  def test_login_with_ldap(self):
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    response = self.c.post('/hue/accounts/login/', {
      'username': "curly",
      'password': "ldap1",
      'server': "LDAP"
    })
    assert_equal(302, response.status_code, response.status_code)
    assert_equal(1, len(User.objects.all()))

  def test_fallback_to_db(self):
    ldap_access.CACHED_LDAP_CONN = LdapTestConnection()

    client = make_logged_in_client(username=self.test_username, password="test")
    client.get('/accounts/logout')
    user = User.objects.get(username=self.test_username)

    response = self.c.post('/hue/accounts/login/', dict(username=self.test_username, password="foo", server="LDAP"))
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_true(self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username))


class TestMultipleBackendLoginNoHadoop(object):
  integration = True
  reset = []
  test_username = "test_mlogin_no_hadoop"

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()

    cls.ldap_backend = django_auth_ldap_backend.LDAPBackend
    django_auth_ldap_backend.LDAPBackend = MockLdapBackend

    # Override auth backend, settings are only loaded from conf at initialization so we can't use set_for_testing
    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = (['desktop.auth.backend.LdapBackend', 'desktop.auth.backend.AllowFirstUserDjangoBackend'])

    # Need to recreate LdapBackend class with new monkey patched base class
    reload(backend)

  @classmethod
  def teardown_class(cls):
    django_auth_ldap_backend.LDAPBackend = cls.ldap_backend

    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

    reload(backend)

  def setUp(self):
    self.c = Client()
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['AllowFirstUserDjangoBackend', 'LdapBackend']) )
    self.reset.append(conf.LDAP.LDAP_URL.set_for_testing('does not matter'))

  def tearDown(self):
    User.objects.all().delete()

    for finish in self.reset:
      finish()

  def test_login(self):
    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context[0]['first_login_ever'])

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "ldap1",
        'password1': "ldap1",
        'password2': "ldap1",
        'server': "Local"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(response.url, "/")

    self.c.get('/accounts/logout')

    response = self.c.post('/hue/accounts/login/', {
        'username': self.test_username,
        'password': "ldap1",
        'server': "LDAP"
    })
    assert_equal(302, response.status_code, "Expected ok redirect status.")
    assert_equal(response.url, "/")


class TestLogin(PseudoHdfsTestBase):

  reset = []
  test_username = "test_login"

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()

    PseudoHdfsTestBase.setup_class()

    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.AllowFirstUserDjangoBackend',)

  @classmethod
  def teardown_class(cls):
    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

  def setUp(self):
    self.c = Client()

    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.AllowFirstUserDjangoBackend']) )

  def tearDown(self):
    for finish in self.reset:
      finish()

    User.objects.all().delete()

    if self.cluster.fs.do_as_user(self.test_username, self.fs.exists, "/user/%s" % self.test_username):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, "/user/%s" % self.test_username)

  def test_bad_first_user(self):
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(["desktop.auth.backend.AllowFirstUserDjangoBackend"]) )

    response = self.c.get('/hue/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context[0]['first_login_ever'])

    response = self.c.post('/hue/accounts/login/', dict(username="foo 1", password="foo"))
    assert_equal(200, response.status_code, "Expected ok status.")
    #assert_true('This value may contain only letters, numbers and @/./+/-/_ characters.' in response.content, response)
    assert_true('This value may contain only ' in response.content, response)

  def test_non_jframe_login(self):
    client = make_logged_in_client(username=self.test_username, password="test")
    # Logout first
    client.get('/accounts/logout')
    # Login
    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    template = 'hue.mako'
    assert_true(any([template in _template.filename for _template in response.templates]), response.content) # Go to superuser wizard

  def test_login_expiration(self):
    """ Expiration test without superusers """
    old_settings = settings.ADMINS
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(["desktop.auth.backend.AllowFirstUserDjangoBackend"]) )
    self.reset.append( conf.AUTH.EXPIRES_AFTER.set_for_testing(0) )
    self.reset.append( conf.AUTH.EXPIRE_SUPERUSERS.set_for_testing(False) )

    client = make_logged_in_client(username=self.test_username, password="test")
    client.get('/accounts/logout')
    user = User.objects.get(username=self.test_username)

    # Login successfully
    try:
      user.is_superuser = True
      user.save()
      response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
      assert_equal(200, response.status_code, "Expected ok status.")

      client.get('/accounts/logout')

      # Login fail
      settings.ADMINS = [(self.test_username, 'test@test.com')]
      user.is_superuser = False
      user.save()
      response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
      assert_equal(200, response.status_code, "Expected ok status.")
      assert_true('Account deactivated. Please contact an <a href="mailto:test@test.com">administrator</a>' in response.content, response.content)

      # Failure should report an inactive user without admin link
      settings.ADMINS = []
      response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
      assert_equal(200, response.status_code, "Expected ok status.")
      assert_true("Account deactivated. Please contact an administrator." in response.content, response.content)
    finally:
      settings.ADMINS = old_settings

  def test_login_expiration_with_superusers(self):
    """ Expiration test with superusers """
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(["desktop.auth.backend.AllowFirstUserDjangoBackend"]) )
    self.reset.append( conf.AUTH.EXPIRES_AFTER.set_for_testing(0) )
    self.reset.append( conf.AUTH.EXPIRE_SUPERUSERS.set_for_testing(True) )

    client = make_logged_in_client(username=self.test_username, password="test")
    client.get('/accounts/logout')
    user = User.objects.get(username=self.test_username)

    # Login fail
    user.is_superuser = True
    user.save()
    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected unauthorized status.")


class TestLoginNoHadoop(object):

  reset = []
  test_username = "test_login_no_hadoop"

  @classmethod
  def setup_class(cls):
    # Simulate first login ever
    User.objects.all().delete()

    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.AllowFirstUserDjangoBackend',)

  @classmethod
  def teardown_class(cls):
    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

  def setUp(self):
    self.c = Client()

    self.reset.append( conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.AllowFirstUserDjangoBackend']) )

  def tearDown(self):
    for finish in self.reset:
      finish()

    User.objects.all().delete()
    if Group.objects.filter(name=self.test_username).exists():
      Group.objects.filter(name=self.test_username).delete()

  def test_login_does_not_reset_groups(self):
    self.reset.append( conf.AUTH.BACKEND.set_for_testing(["desktop.auth.backend.AllowFirstUserDjangoBackend"]) )

    client = make_logged_in_client(username=self.test_username, password="test")
    client.get('/accounts/logout')
    user = User.objects.get(username=self.test_username)
    group, created = Group.objects.get_or_create(name=self.test_username)

    user.groups.all().delete()
    assert_false(user.groups.exists())

    response = client.post('/hue/accounts/login/', dict(username=self.test_username, password="test"), follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")


class TestImpersonationBackend(object):
  test_username = "test_login_impersonation"
  test_login_as_username = "test_login_as_impersonation"

  @classmethod
  def setup_class(cls):
    cls.client = make_logged_in_client(username=cls.test_username, password="test")
    cls.auth_backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.ImpersonationBackend',)

  @classmethod
  def teardown_class(cls):
    settings.AUTHENTICATION_BACKENDS = cls.auth_backends

  def setUp(self):
    self.reset = [conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.ImpersonationBackend'])]

  def tearDown(self):
    for finish in self.reset:
      finish()

  def test_login_does_not_reset_groups(self):
    self.client.get('/accounts/logout')

    user = User.objects.get(username=self.test_username)
    group, created = Group.objects.get_or_create(name=self.test_username)

    response = self.client.post('/hue/accounts/login/', dict(username=self.test_username, password="test", login_as=self.test_login_as_username), follow=True)
    assert_equal(200, response.status_code)
    assert_equal(self.test_login_as_username, response.context[0]['user'].username)


class MockLdapBackend(object):
  settings = django_auth_ldap_backend.LDAPSettings()

  def get_or_create_user(self, username, ldap_user):
    return User.objects.get_or_create(username)

  def authenticate(self, username=None, password=None, server=None):
    user, created = self.get_or_create_user(username, None)
    return user

  def get_user(self, user_id):
    return User.objects.get(id=user_id)
