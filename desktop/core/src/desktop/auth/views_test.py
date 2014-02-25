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

from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import Client
from desktop import conf
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


class TestRemoteUserLogin(object):
  reset = []

  def setUp(self):
    self.backends = settings.AUTHENTICATION_BACKENDS
    settings.AUTHENTICATION_BACKENDS = ('desktop.auth.backend.RemoteUserDjangoBackend',)
    self.reset.append( conf.AUTH.BACKEND.set_for_testing('desktop.auth.backend.RemoteUserDjangoBackend') )
    self.reset.append( conf.AUTH.REMOTE_USER_HEADER.set_for_testing('REMOTE_USER') )
    self.c = Client()

  def tearDown(self):
    User.objects.all().delete()
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
    assert_equal('FOO4', User.objects.all()[1].username)

    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "foo4"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(2, len(User.objects.all()))
    assert_equal('FOO4', User.objects.all()[1].username)

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
    response = self.c.post('/accounts/login/', {}, **{"REMOTE_USER": "FOO3"})
    assert_equal(200, response.status_code, "Expected ok status.")
    assert_equal(1, len(User.objects.all()))
    assert_equal('FOO3', User.objects.all()[0].username)

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
    assert_true('admin_wizard.mako' in response.template, response.template) # Go to superuser wizard
