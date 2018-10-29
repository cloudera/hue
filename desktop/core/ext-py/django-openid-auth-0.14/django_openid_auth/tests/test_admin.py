# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2009-2013 Canonical Ltd.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Tests for the django_openid_auth Admin login form replacement."""

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User

from django.test import TestCase
from django.test.utils import override_settings


@override_settings(OPENID_USE_AS_ADMIN_LOGIN=True)
class SiteAdminTests(TestCase):
    """
    TestCase for accessing /admin/ when the django_openid_auth form replacement
    is in use.
    """

    def test_admin_site_with_openid_login_authenticated_non_staff(self):
        """
        If the request has an authenticated user, who is not flagged as a
        staff member, then they get a failure response.
        """
        User.objects.create_user(
            username='testing', email='testing@example.com', password='test')
        assert self.client.login(username='testing', password='test')
        response = self.client.get('/admin/', follow=True)
        self.assertContains(
            response,
            'User testing does not have admin/staff access.', status_code=403)

    def test_admin_site_with_openid_login_non_authenticated_user(self):
        """
        Unauthenticated users accessing the admin page should be directed to
        the OpenID login url.
        """
        response = self.client.get('/admin/', follow=True)
        self.assertRedirects(
            response,
            getattr(settings, 'LOGIN_URL', '/openid/login') +
            '?next=%2Fadmin%2F')
