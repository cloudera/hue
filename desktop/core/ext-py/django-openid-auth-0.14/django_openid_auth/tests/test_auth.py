# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2010-2013 Canonical Ltd.
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

import re
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from openid.consumer.consumer import (
    CancelResponse,
    FailureResponse,
    SetupNeededResponse,
    SuccessResponse,
)
from openid.consumer.discover import OpenIDServiceEndpoint
from openid.extensions import pape
from openid.message import Message, OPENID2_NS

from django_openid_auth.auth import OpenIDBackend, get_user_group_model
from django_openid_auth.exceptions import (
    DuplicateUsernameViolation,
    MissingPhysicalMultiFactor,
    MissingUsernameViolation,
    RequiredAttributeNotReturned,
)
from django_openid_auth.models import UserOpenID
from django_openid_auth.signals import openid_duplicate_username
from django_openid_auth.teams import ns_uri as TEAMS_NS
from django_openid_auth.tests.helpers import override_session_serializer


SREG_NS = "http://openid.net/sreg/1.0"
AX_NS = "http://openid.net/srv/ax/1.0"
SERVER_URL = 'http://example.com'


def make_claimed_id(id_):
    return urljoin(SERVER_URL, id_)


class TestMessage(Message):
    """Convenience class to construct test OpenID messages and responses."""

    def __init__(self, openid_namespace=OPENID2_NS):
        super(TestMessage, self).__init__(openid_namespace=openid_namespace)
        endpoint = OpenIDServiceEndpoint()
        endpoint.claimed_id = make_claimed_id('some-id')
        endpoint.server_url = SERVER_URL
        self.endpoint = endpoint

    def set_ax_args(
            self,
            email="foo@example.com",
            first=None,
            fullname="Some User",
            last=None,
            nickname="someuser",
            schema="http://axschema.org/",
            verified=False):

        attributes = [
            ("nickname", schema + "namePerson/friendly", nickname),
            ("fullname", schema + "namePerson", fullname),
            ("email", schema + "contact/email", email),
            ("account_verified",
             "http://ns.login.ubuntu.com/2013/validation/account",
             "token_via_email" if verified else "no")
            ]
        if first:
            attributes.append(
                ("first", "http://axschema.org/namePerson/first", first))
        if last:
            attributes.append(
                ("last", "http://axschema.org/namePerson/last", last))

        self.setArg(AX_NS, "mode", "fetch_response")
        for (alias, uri, value) in attributes:
            self.setArg(AX_NS, "type.%s" % alias, uri)
            self.setArg(AX_NS, "value.%s" % alias, value)

    def set_pape_args(self, *auth_policies):
        self.setArg(pape.ns_uri, 'auth_policies', ' '.join(auth_policies))

    def _set_args(self, ns, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                self.setArg(ns, key, value)
            elif self.hasKey(ns, key):
                self.delArg(ns, key)

    def set_sreg_args(self, **kwargs):
        self._set_args(SREG_NS, **kwargs)

    def set_team_args(self, **kwargs):
        self._set_args(TEAMS_NS, **kwargs)

    def to_response(self):
        return SuccessResponse(
            self.endpoint, self, signed_fields=self.toPostArgs().keys())


@override_session_serializer
@override_settings(
    OPENID_USE_EMAIL_FOR_USERNAME=False,
    OPENID_LAUNCHPAD_TEAMS_REQUIRED=[],
    OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=False,
    OPENID_EMAIL_WHITELIST_REGEXP_LIST=[])
class OpenIDBackendTests(TestCase):

    def setUp(self):
        super(OpenIDBackendTests, self).setUp()
        self.backend = OpenIDBackend()
        self.message = TestMessage()

    def make_user_openid(
            self, user=None, claimed_id=make_claimed_id('existing_identity')):
        if user is None:
            user = User.objects.create_user(
                username='someuser', email='someuser@example.com',
                password='12345678')

        user_openid, created = UserOpenID.objects.get_or_create(
            user=user, claimed_id=claimed_id, display_id=claimed_id)
        return user_openid

    def _assert_account_verified(self, user, expected):
        permission = Permission.objects.get(codename='account_verified')
        perm_label = '%s.%s' % (permission.content_type.app_label,
                                permission.codename)
        # Always invalidate the per-request perm cache
        attrs = list(user.__dict__.keys())
        for attr in attrs:
            if attr.endswith('_perm_cache'):
                delattr(user, attr)

        self.assertEqual(user.has_perm(perm_label), expected)

    def assert_account_not_verified(self, user):
        self._assert_account_verified(user, False)

    def assert_account_verified(self, user):
        self._assert_account_verified(user, True)

    def assert_no_users_created(self, expected_count=0):
        current_count = User.objects.count()
        msg = 'New users found (expected: %i, current: %i)' % (
            expected_count, current_count)
        self.assertEqual(current_count, expected_count, msg)

    def test_extract_user_details_sreg(self):
        expected = {
            'nickname': 'someuser',
            'first_name': 'Some',
            'last_name': 'User',
            'email': 'foo@example.com',
            'account_verified': False,
        }
        data = {
            'nickname': expected['nickname'],
            'fullname': "%s %s" % (expected['first_name'],
                                   expected['last_name']),
            'email': expected['email'],
        }
        self.message.set_sreg_args(**data)

        details = self.backend._extract_user_details(
            self.message.to_response())
        self.assertEqual(details, expected)

    def test_extract_user_details_ax(self):
        self.message.set_ax_args(
            email="foo@example.com",
            fullname="Some User",
            nickname="someuser",
        )
        data = self.backend._extract_user_details(self.message.to_response())

        self.assertEqual(data, {"nickname": "someuser",
                                "first_name": "Some",
                                "last_name": "User",
                                "email": "foo@example.com",
                                "account_verified": False})

    def test_extract_user_details_ax_split_name(self):
        # Include fullname too to show that the split data takes
        # precedence.
        self.message.set_ax_args(
            fullname="Bad Data", first="Some", last="User")
        data = self.backend._extract_user_details(self.message.to_response())

        self.assertEqual(data, {"nickname": "someuser",
                                "first_name": "Some",
                                "last_name": "User",
                                "email": "foo@example.com",
                                "account_verified": False})

    def test_extract_user_details_ax_broken_myopenid(self):
        self.message.set_ax_args(
            schema="http://schema.openid.net/", fullname="Some User",
            nickname="someuser", email="foo@example.com")
        data = self.backend._extract_user_details(self.message.to_response())

        self.assertEqual(data, {"nickname": "someuser",
                                "first_name": "Some",
                                "last_name": "User",
                                "email": "foo@example.com",
                                "account_verified": False})

    def test_update_user_details_long_names(self):
        self.message.set_ax_args()
        user = User.objects.create_user(
            'someuser', 'someuser@example.com', password=None)
        user_openid, created = UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/existing_identity',
            display_id='http://example.com/existing_identity')
        data = dict(
            first_name=u"Some56789012345678901234567890123",
            last_name=u"User56789012345678901234567890123",
            email=u"someotheruser@example.com", account_verified=False)

        self.backend.update_user_details(
            user, data, self.message.to_response())

        self.assertEqual("Some56789012345678901234567890",  user.first_name)
        self.assertEqual("User56789012345678901234567890",  user.last_name)

    def _test_update_user_perms_account_verified(
            self, user, initially_verified, verified):
        # set user's verification status
        permission = Permission.objects.get(codename='account_verified')
        if initially_verified:
            user.user_permissions.add(permission)
        else:
            user.user_permissions.remove(permission)

        if initially_verified:
            self.assert_account_verified(user)
        else:
            self.assert_account_not_verified(user)

        # get a response including verification status
        self.message.set_ax_args()
        data = dict(first_name=u"Some56789012345678901234567890123",
                    last_name=u"User56789012345678901234567890123",
                    email=u"someotheruser@example.com",
                    account_verified=verified)
        self.backend.update_user_details(
            user, data, self.message.to_response())

        # refresh object from the database
        user = User.objects.get(pk=user.pk)

        if verified:
            self.assert_account_verified(user)
        else:
            self.assert_account_not_verified(user)

    def test_update_user_perms_initially_verified_then_verified(self):
        self._test_update_user_perms_account_verified(
            self.make_user_openid().user,
            initially_verified=True, verified=True)

    def test_update_user_perms_initially_verified_then_unverified(self):
        self._test_update_user_perms_account_verified(
            self.make_user_openid().user,
            initially_verified=True, verified=False)

    def test_update_user_perms_initially_not_verified_then_verified(self):
        self._test_update_user_perms_account_verified(
            self.make_user_openid().user,
            initially_verified=False, verified=True)

    def test_update_user_perms_initially_not_verified_then_unverified(self):
        self._test_update_user_perms_account_verified(
            self.make_user_openid().user,
            initially_verified=False, verified=False)

    def test_extract_user_details_name_with_trailing_space(self):
        self.message.set_ax_args(fullname="SomeUser ")

        data = self.backend._extract_user_details(self.message.to_response())

        self.assertEqual("", data['first_name'])
        self.assertEqual("SomeUser", data['last_name'])

    def test_extract_user_details_name_with_thin_space(self):
        self.message.set_ax_args(fullname=u"Some\u2009User")

        data = self.backend._extract_user_details(self.message.to_response())

        self.assertEqual("Some", data['first_name'])
        self.assertEqual("User", data['last_name'])

    @override_settings(OPENID_CREATE_USERS=True)
    def test_auth_username_when_no_nickname(self):
        self.message.set_sreg_args(nickname='')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)
        self.assertEqual(
            user.username, 'openiduser',
            "username must default to 'openiduser'")

    @override_settings(OPENID_USE_EMAIL_FOR_USERNAME=True)
    def test_auth_username_email_munging(self):
        for nick, email, expected in [
                ('nickcomesfirst', 'foo@example.com', 'nickcomesfirst'),
                ('', 'foo@example.com', 'fooexamplecom'),
                ('noemail', '', 'noemail'),
                ('', '@%.-', 'openiduser'),
                ('', '', 'openiduser'),
                (None, None, 'openiduser')]:
            self.message.set_sreg_args(nickname=nick, email=email)
            user = self.backend.authenticate(
                openid_response=self.message.to_response())
            # Cleanup user for further tests
            user.delete()

            self.assertIsNotNone(user)
            self.assertEqual(user.username, expected)

    @override_settings(OPENID_USE_EMAIL_FOR_USERNAME=False)
    def test_auth_username_no_email_munging(self):
        for nick, email, expected in [
                ('nickcomesfirst', 'foo@example.com', 'nickcomesfirst'),
                ('', 'foo@example.com', 'openiduser'),
                ('noemail', '', 'noemail'),
                ('', '@%.-', 'openiduser'),
                ('', '', 'openiduser'),
                (None, None, 'openiduser')]:
            self.message.set_sreg_args(nickname=nick, email=email)
            user = self.backend.authenticate(
                openid_response=self.message.to_response())
            # Cleanup user for further tests
            user.delete()

            self.assertIsNotNone(user)
            self.assertEqual(user.username, expected)

    @override_settings(
        OPENID_CREATE_USERS=True,
        OPENID_FOLLOW_RENAMES=False,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_username_duplicate_numbering(self):
        # Setup existing user to conflict with
        User.objects.create_user('testuser')

        self.message.set_sreg_args(nickname='testuser')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)
        self.assertEqual(
            user.username, 'testuser2',
            'Username must contain numeric suffix to avoid collisions.')

    def test_auth_username_duplicate_numbering_with_conflicts(self):
        # Setup existing users to conflict with
        User.objects.create_user('testuser')
        User.objects.create_user('testuser3')

        self.message.set_sreg_args(nickname='testuser')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it starting with the count of users with
        # username starting with 'testuser', of which there are 2.  i should
        # start at 3, which already exists, so it should skip to 4.
        self.assertIsNotNone(user)
        self.assertEqual(
            user.username, 'testuser4',
            'Username must contain numeric suffix to avoid collisions.')

    def test_auth_username_duplicate_numbering_with_holes(self):
        # Setup existing users to conflict with
        User.objects.create_user('testuser')
        User.objects.create_user('testuser1')
        User.objects.create_user('testuser6')
        User.objects.create_user('testuser7')
        User.objects.create_user('testuser8')

        self.message.set_sreg_args(nickname='testuser')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it starting with the count of users with
        # username starting with 'testuser', of which there are 5.  i should
        # start at 6, and increment until it reaches 9.
        self.assertIsNotNone(user)
        self.assertEqual(
            user.username, 'testuser9',
            'Username must contain numeric suffix to avoid collisions.')

    def test_auth_username_duplicate_numbering_with_nonsequential_matches(
            self):
        # Setup existing users to conflict with
        User.objects.create_user('testuser')
        User.objects.create_user('testuserfoo')

        self.message.set_sreg_args(nickname='testuser')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it starting with the count of users with
        # username starting with 'testuser', of which there are 2.  i should
        # start at 3, which will be available.
        self.assertIsNotNone(user)
        self.assertEqual(
            user.username, 'testuser3',
            'Username must contain numeric suffix to avoid collisions.')

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team'])
    def test_authenticate_when_not_member_of_teams_required(self):
        Group.objects.create(name='team')

        self.message.set_sreg_args(nickname='someuser')
        self.message.set_team_args(is_member='foo')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNone(user)

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team'])
    def test_authenticate_when_no_group_mapping_to_required_team(self):
        assert Group.objects.filter(name='team').count() == 0

        self.message.set_sreg_args(nickname='someuser')
        self.message.set_team_args(is_member='foo')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNone(user)

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team'])
    def test_authenticate_when_member_of_teams_required(self):
        Group.objects.create(name='team')

        self.message.set_sreg_args(nickname='someuser')
        self.message.set_team_args(is_member='foo,team')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

    @override_settings(OPENID_LAUNCHPAD_TEAMS_REQUIRED=[])
    def test_authenticate_when_no_teams_required(self):
        self.message.set_sreg_args(nickname='someuser')
        self.message.set_team_args(is_member='team')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team1', 'team2'])
    def test_authenticate_when_member_of_at_least_one_team(self):
        Group.objects.create(name='team1')

        self.message.set_sreg_args(nickname='someuser')
        self.message.set_team_args(is_member='foo,team1')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team'],
        OPENID_EMAIL_WHITELIST_REGEXP_LIST=['foo(\+[^@]*)?@foo.com'])
    def test_authenticate_when_not_in_required_team_but_email_whitelisted(
            self):
        assert Group.objects.filter(name='team').count() == 0

        self.message.set_sreg_args(
            nickname='someuser', email='foo@foo.com')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

        self.message.set_sreg_args(
            nickname='someuser', email='foo+bar@foo.com')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team'],
        OPENID_EMAIL_WHITELIST_REGEXP_LIST=['foo@foo.com', 'bar@foo.com'])
    def test_authenticate_whitelisted_email_multiple_patterns(self):
        assert Group.objects.filter(name='team').count() == 0

        self.message.set_sreg_args(nickname='someuser', email='bar@foo.com')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

    @override_settings(
        OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO=True,
        OPENID_LAUNCHPAD_TEAMS_REQUIRED=['team'],
        OPENID_EMAIL_WHITELIST_REGEXP_LIST=['foo@foo.com'])
    def test_authenticate_whitelisted_email_not_match(self):
        assert Group.objects.filter(name='team').count() == 0

        self.message.set_sreg_args(nickname='someuser', email='bar@foo.com')
        self.message.set_team_args(is_member='foo')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNone(user)

    def test_auth_no_response(self):
        self.assertIsNone(self.backend.authenticate())
        self.assert_no_users_created()

    def test_auth_cancel_response(self):
        response = CancelResponse(OpenIDServiceEndpoint())

        self.assertIsNone(self.backend.authenticate(openid_response=response))
        self.assert_no_users_created()

    def test_auth_failure_response(self):
        response = FailureResponse(OpenIDServiceEndpoint())

        self.assertIsNone(self.backend.authenticate(openid_response=response))
        self.assert_no_users_created()

    def test_auth_setup_needed_response(self):
        response = SetupNeededResponse(OpenIDServiceEndpoint())

        self.assertIsNone(self.backend.authenticate(openid_response=response))
        self.assert_no_users_created()

    @override_settings(OPENID_CREATE_USERS=False)
    def test_auth_no_create_users(self):
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNone(user)
        self.assert_no_users_created()

    @override_settings(OPENID_CREATE_USERS=False)
    def test_auth_no_create_users_existing_user(self):
        existing_openid = self.make_user_openid(
            claimed_id=self.message.endpoint.claimed_id)
        expected_user_count = User.objects.count()
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)
        self.assertEqual(user, existing_openid.user)
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_UPDATE_DETAILS_FROM_SREG=True,
        OPENID_VALID_VERIFICATION_SCHEMES={
            SERVER_URL: {'token_via_email'}})
    def test_auth_update_details_from_sreg(self):
        first_name = 'a' * 31
        last_name = 'b' * 31
        email = 'new@email.com'
        self.message.set_ax_args(
            fullname=first_name + ' ' + last_name,
            nickname='newnickname',
            email=email,
            first=first_name,
            last=last_name,
            verified=True,
        )
        existing_openid = self.make_user_openid(
            claimed_id=self.message.endpoint.claimed_id)
        original_username = existing_openid.user.username
        expected_user_count = User.objects.count()

        self.assert_account_not_verified(existing_openid.user)

        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(user, existing_openid.user)
        self.assertEqual(
            user.username, original_username,
            'Username must not be updated unless OPENID_FOLLOW_RENAMES=True.')
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name[:30])
        self.assertEqual(user.last_name, last_name[:30])
        self.assert_account_verified(user)
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_UPDATE_DETAILS_FROM_SREG=True,
        OPENID_VALID_VERIFICATION_SCHEMES={
            SERVER_URL: {'token_via_email'}})
    def test_auth_update_details_from_sreg_unverifies_account(self):
        first_name = 'a' * 31
        last_name = 'b' * 31
        email = 'new@email.com'
        kwargs = dict(
            fullname=first_name + ' ' + last_name,
            nickname='newnickname',
            email=email,
            first=first_name,
            last=last_name,
            verified=True,
        )
        self.message.set_ax_args(**kwargs)
        verified_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assert_account_verified(verified_user)
        expected_user_count = User.objects.count()

        kwargs['verified'] = False
        self.message.set_ax_args(**kwargs)
        unverified_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(verified_user, unverified_user)
        self.assert_account_not_verified(unverified_user)
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(OPENID_PHYSICAL_MULTIFACTOR_REQUIRED=True)
    def test_physical_multifactor_required_not_given(self):
        response = self.message.to_response()

        with self.assertRaises(MissingPhysicalMultiFactor):
            self.backend.authenticate(openid_response=response)

        self.assertTrue(
            UserOpenID.objects.filter(
                claimed_id=self.message.endpoint.claimed_id).exists(),
            'User must be created anyways.')

    @override_settings(OPENID_PHYSICAL_MULTIFACTOR_REQUIRED=True)
    def test_physical_multifactor_required_invalid_auth_policy(self):
        self.message.set_pape_args(
            pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT)

        with self.assertRaises(MissingPhysicalMultiFactor):
            self.backend.authenticate(
                openid_response=self.message.to_response())

        self.assertTrue(
            UserOpenID.objects.filter(
                claimed_id=self.message.endpoint.claimed_id).exists(),
            'User must be created anyways.')

    @override_settings(OPENID_PHYSICAL_MULTIFACTOR_REQUIRED=True)
    def test_physical_multifactor_required_valid_auth_policy(self):
        self.message.set_pape_args(
            pape.AUTH_MULTI_FACTOR, pape.AUTH_MULTI_FACTOR_PHYSICAL,
            pape.AUTH_PHISHING_RESISTANT)
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)

    @override_settings(OPENID_STRICT_USERNAMES=True)
    def test_auth_strict_usernames(self):
        username = 'nickname'
        self.message.set_sreg_args(nickname=username)
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user, 'User must be created')
        self.assertEqual(user.username, username)

    @override_settings(OPENID_STRICT_USERNAMES=True)
    def test_auth_strict_usernames_no_nickname(self):
        self.message.set_sreg_args(nickname='')

        msg = re.escape(
            "An attribute required for logging in was not returned (nickname)")

        with self.assertRaisesRegexp(RequiredAttributeNotReturned, msg):
            self.backend.authenticate(
                openid_response=self.message.to_response())

        self.assert_no_users_created()

    @override_settings(
        OPENID_STRICT_USERNAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_strict_usernames_conflict(self):
        existing_openid = self.make_user_openid()
        expected_user_count = User.objects.count()
        self.message.set_sreg_args(
            nickname=existing_openid.user.username)

        with self.assertRaises(DuplicateUsernameViolation):
            self.backend.authenticate(
                openid_response=self.message.to_response())

        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames(self):
        new_username = 'new'
        self.message.set_sreg_args(nickname='username')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())
        expected_user_count = User.objects.count()

        self.assertIsNotNone(user, 'User must be created')

        self.message.set_sreg_args(nickname=new_username)
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(user.pk, renamed_user.pk)
        self.assertEqual(renamed_user.username, new_username)
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_STRICT_USERNAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_strict_usernames_no_nickname(self):
        self.message.set_sreg_args(nickname='nickame')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())
        expected_user_count = User.objects.count()

        self.assertIsNotNone(user, 'User must be created')

        self.message.set_sreg_args(nickname='')

        # XXX: Check possibilities to normalize this error into a
        # `RequiredAttributeNotReturned`.
        with self.assertRaises(MissingUsernameViolation):
            self.backend.authenticate(
                openid_response=self.message.to_response())

        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_STRICT_USERNAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_strict_usernames_rename_conflict(self):
        # Setup existing user to conflict with
        User.objects.create_user('testuser')

        self.message.set_sreg_args(nickname='nickname')
        user = self.backend.authenticate(
            openid_response=self.message.to_response())
        expected_user_count = User.objects.count()

        self.assertIsNotNone(user, 'First request should succeed')

        self.message.set_sreg_args(nickname='testuser')

        with self.assertRaises(DuplicateUsernameViolation):
            self.backend.authenticate(
                openid_response=self.message.to_response())

        db_user = User.objects.get(pk=user.pk)
        self.assertEqual(db_user.username, 'nickname')
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_STRICT_USERNAMES=False,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_to_conflict(self):
        # Setup existing user to conflict with
        User.objects.create_user('testuser')
        # Setup user to rename
        user = User.objects.create_user('nickname')
        self.make_user_openid(
            user=user, claimed_id=self.message.endpoint.claimed_id)
        # Trigger rename
        self.message.set_sreg_args(nickname='testuser')
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(renamed_user.pk, user.pk)
        self.assertEqual(
            renamed_user.username, 'testuser2',
            'Username must have a numbered suffix to avoid conflict.')

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_no_change(self):
        # Setup user to rename
        user = User.objects.create_user('username')
        self.make_user_openid(
            user=user, claimed_id=self.message.endpoint.claimed_id)
        expected_user_count = User.objects.count()
        # Trigger rename
        self.message.set_sreg_args(nickname=user.username)
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(renamed_user.pk, user.pk)
        self.assertEqual(
            renamed_user.username, user.username,
            'No numeric suffix should be appended for username owner.')
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_to_numbered_suffix(self):
        # Setup user to rename to numbered suffix pattern
        user = User.objects.create_user('testuser2000eight')
        self.make_user_openid(
            user=user, claimed_id=self.message.endpoint.claimed_id)
        # Trigger rename
        self.message.set_sreg_args(nickname='testuser2')
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(renamed_user.pk, user.pk)
        self.assertEqual(
            renamed_user.username, 'testuser2',
            'The numbered suffix must be kept.')

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_to_numbered_suffix_with_existing(self):
        # Setup existing user to conflict with
        User.objects.create_user('testuser')
        # Setup user to rename to numbered suffix pattern
        user = User.objects.create_user('testuser2000eight')
        self.make_user_openid(
            user=user, claimed_id=self.message.endpoint.claimed_id)
        # Trigger rename
        self.message.set_sreg_args(nickname='testuser3')
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(renamed_user.pk, user.pk)
        self.assertEqual(
            renamed_user.username, 'testuser3',
            'Username must be kept as there are no conflicts.')

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_from_numbered_suffix_to_conflict(self):
        # Setup existing user to conflict with
        User.objects.create_user('testuser')
        # Setup user with numbered suffix pattern
        user = User.objects.create_user('testuser2000')
        self.make_user_openid(
            user=user, claimed_id=self.message.endpoint.claimed_id)
        # Trigger rename
        self.message.set_sreg_args(nickname='testuser')
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(renamed_user.pk, user.pk)
        self.assertEqual(
            user.username, 'testuser2000',
            'Since testuser conflicts, username must remain unchanged as it '
            'maches the number suffix pattern.')

    @override_settings(
        OPENID_FOLLOW_RENAMES=True,
        OPENID_UPDATE_DETAILS_FROM_SREG=True)
    def test_auth_follow_renames_from_numbered_suffix_no_conflict(self):
        # Setup user with numbered suffix pattern
        user = User.objects.create_user('testuser2')
        self.make_user_openid(
            user=user, claimed_id=self.message.endpoint.claimed_id)
        # Trigger rename
        self.message.set_sreg_args(nickname='testuser')
        renamed_user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertEqual(renamed_user.pk, user.pk)
        self.assertEqual(
            renamed_user.username, 'testuser',
            'Username must be updated as there are no conflicts.')

    @override_settings(OPENID_STRICT_USERNAMES=True)
    def test_auth_duplicate_username_signal_is_sent(self):
        existing_openid = self.make_user_openid()
        expected_user_count = User.objects.count()
        signal_kwargs = {}

        def duplicate_username_handler(sender, **kwargs):
            signal_kwargs.update(kwargs)
        self.addCleanup(
            openid_duplicate_username.disconnect,
            duplicate_username_handler, sender=User, dispatch_uid='testing')
        openid_duplicate_username.connect(
            duplicate_username_handler, sender=User, weak=False,
            dispatch_uid='testing')

        self.message.set_sreg_args(
                nickname=existing_openid.user.username)

        with self.assertRaises(DuplicateUsernameViolation):
            self.backend.authenticate(
                openid_response=self.message.to_response())

        self.assertIn('username', signal_kwargs)
        self.assertEqual(
            signal_kwargs['username'], existing_openid.user.username)
        self.assert_no_users_created(expected_count=expected_user_count)

    @override_settings(OPENID_STRICT_USERNAMES=True)
    def test_auth_duplicate_username_signal_can_prevent_duplicate_error(self):
        existing_openid = self.make_user_openid()

        def duplicate_username_handler(sender, **kwargs):
            existing_user = existing_openid.user
            existing_user.username += '_other'
            existing_user.save()
        self.addCleanup(
            openid_duplicate_username.disconnect,
            duplicate_username_handler, sender=User, dispatch_uid='testing')
        openid_duplicate_username.connect(
            duplicate_username_handler, sender=User, weak=False,
            dispatch_uid='testing')

        self.message.set_sreg_args(
                nickname=existing_openid.user.username)
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)
        self.assertNotEqual(user, existing_openid.user)

    @override_settings(OPENID_STRICT_USERNAMES=True)
    def test_auth_duplicate_username_is_not_called_if_no_conflict(self):
        def duplicate_username_handler(sender, **kwargs):
            assert False, 'This should never have been called.'
        self.addCleanup(
            openid_duplicate_username.disconnect,
            duplicate_username_handler, sender=User, dispatch_uid='testing')
        openid_duplicate_username.connect(
            duplicate_username_handler, sender=User, weak=False,
            dispatch_uid='testing')

        self.message.set_sreg_args(nickname='nickname')
        self.backend.authenticate(openid_response=self.message.to_response())

    @override_settings(OPENID_STRICT_USERNAMES=False)
    def test_auth_duplicate_username_is_not_called_if_not_strict(self):
        existing_openid = self.make_user_openid()

        def duplicate_username_handler(sender, **kwargs):
            assert False, 'This should never have been called.'
        self.addCleanup(
            openid_duplicate_username.disconnect,
            duplicate_username_handler, sender=User, dispatch_uid='testing')
        openid_duplicate_username.connect(
            duplicate_username_handler, sender=User, weak=False,
            dispatch_uid='testing')

        self.message.set_sreg_args(nickname=existing_openid.user.username)
        self.backend.authenticate(openid_response=self.message.to_response())

    @override_settings(OPENID_STRICT_USERNAMES=True)
    def test_auth_duplicate_username_handling_bypass_numbered_suffix(self):
        nickname = 'nickname87'
        existing_openid = self.make_user_openid(
            user=User.objects.create_user(nickname))

        def duplicate_username_handler(sender, **kwargs):
            existing_user = existing_openid.user
            existing_user.username += '00'
            existing_user.save()
        self.addCleanup(
            openid_duplicate_username.disconnect,
            duplicate_username_handler, sender=User, dispatch_uid='testing')
        openid_duplicate_username.connect(
            duplicate_username_handler, sender=User, weak=False,
            dispatch_uid='testing')

        self.message.set_sreg_args(nickname=existing_openid.user.username)
        user = self.backend.authenticate(
            openid_response=self.message.to_response())

        self.assertIsNotNone(user)
        self.assertNotEqual(user, existing_openid.user)
        self.assertEqual(
            user.username, nickname,
            'In strict mode, when conflicts are handled, the username must '
            'be kept unmodified without numbered suffixes.')


class GetGroupModelTestCase(TestCase):

    def setUp(self):
        super(GetGroupModelTestCase, self).setUp()
        self.inject_test_models()

    def inject_test_models(self):
        installed_apps = settings.INSTALLED_APPS + (
            'django_openid_auth.tests',
        )
        p = self.settings(INSTALLED_APPS=installed_apps)
        p.enable()
        self.addCleanup(p.disable)
        self.clear_app_cache()

    def clear_app_cache(self):
        try:
            from django.apps import apps
            apps.clear_cache()
        except ImportError:
            from django.db.models.loading import cache
            cache.loaded = False

    def test_default_group_model(self):
        model = get_user_group_model()
        self.assertEqual(model, User.groups.through)

    @override_settings(AUTH_USER_GROUP_MODEL='tests.UserGroup')
    def test_custom_group_model(self):
        from django_openid_auth.tests.models import UserGroup
        model = get_user_group_model()
        self.assertEqual(model, UserGroup)

    @override_settings(
        AUTH_USER_GROUP_MODEL='django_openid_auth.models.UserGroup')
    def test_improperly_configured_invalid_name(self):
        self.assertRaises(ImproperlyConfigured, get_user_group_model)

    @override_settings(
        AUTH_USER_GROUP_MODEL='invalid.UserGroup')
    def test_improperly_configured_invalid_app(self):
        self.assertRaises(ImproperlyConfigured, get_user_group_model)
