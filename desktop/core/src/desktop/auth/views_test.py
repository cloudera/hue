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

from desktop import conf
from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from hadoop.test_base import PseudoHdfsTestBase
from hadoop import pseudo_hdfs4


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
  @classmethod
  def setup_class(cls):
    PseudoHdfsTestBase.setup_class()

    from desktop.auth import backend
    cls.ldap_backend = backend.LdapBackend
    backend.LdapBackend = MockLdapBackend
    MockLdapBackend.__name__ = 'LdapBackend'

    cls.old_backend = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ("desktop.auth.backend.LdapBackend",)

  @classmethod
  def teardown_class(cls):
    from desktop.auth import backend
    backend.LdapBackend = cls.ldap_backend

    settings.AUTHENTICATION_BACKENDS = cls.old_backend
    MockLdapBackend.__name__ = 'MockLdapBackend'

  def setUp(self):
    # Simulate first login ever
    User.objects.all().delete()
    self.c = Client()

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
        'username':" ldap2",
        'password': "ldap2"
    }, follow=True)
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('/beeswax' in response.content, response.content)
    # Custom login process should not do 'http-equiv="refresh"' but call the correct view
    # 'Could not create home directory.' won't show up because the messages are consumed before


class TestLogin(object):
  def setUp(self):
    # Simulate first login ever
    User.objects.all().delete()
    self.c = Client()

  def test_bad_first_user(self):
    finish = conf.AUTH.BACKEND.set_for_testing("desktop.auth.backend.AllowFirstUserDjangoBackend")

    response = self.c.get('/accounts/login/')
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true(response.context['first_login_ever'])

    response = self.c.post('/accounts/login/', dict(username="foo 1", password="foo"))
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_true('This value may contain only letters, numbers and @/./+/-/_ characters.' in response.content, response)

    finish()

  def test_non_jframe_login(self):
    client = make_logged_in_client(username="test", password="test")
    # Logout first
    client.get('/accounts/logout')
    # Login
    response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
    assert_true(any(["admin_wizard.mako" in _template.filename for _template in response.template]), response.template) # Go to superuser wizard


class MockLdapBackend(object):
  def authenticate(self, username=None, password=None):
    user, created = User.objects.get_or_create(username=username)
    return user

  def get_user(self, user_id):
    return rewrite_user(User.objects.get(id=user_id))

  @classmethod
  def manages_passwords_externally(cls):
    return True
LdapBackend = MockLdapBackend
