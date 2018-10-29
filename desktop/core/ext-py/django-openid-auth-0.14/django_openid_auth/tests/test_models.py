# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2013 Canonical Ltd.
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
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
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

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase

from django_openid_auth.models import (
    Permission,
    UserOpenID,
)


class UserOpenIDModelTestCase(TestCase):

    def test_create_useropenid(self):
        user = User.objects.create_user('someuser', 'someuser@example.com',
                                        password=None)
        user_openid, created = UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/existing_identity',
            display_id='http://example.com/existing_identity')

        self.assertEqual('someuser', user_openid.user.username)
        self.assertEqual(
            user_openid.claimed_id, 'http://example.com/existing_identity')
        self.assertEqual(
            user_openid.display_id, 'http://example.com/existing_identity')
        self.assertFalse(
            User.objects.get(username='someuser').has_perm(
                'django_openid_auth.account_verified'))

    def test_delete_verified_useropenid(self):
        user = User.objects.create_user('someuser', 'someuser@example.com',
                                        password=None)
        user_openid, created = UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/existing_identity',
            display_id='http://example.com/existing_identity')
        permission = Permission.objects.get(codename='account_verified')
        user.user_permissions.add(permission)
        self.assertTrue(
            User.objects.get(username='someuser').has_perm(
                'django_openid_auth.account_verified'))
        user_openid.delete()
        self.assertFalse(
            User.objects.get(username='someuser').has_perm(
                'django_openid_auth.account_verified'))
