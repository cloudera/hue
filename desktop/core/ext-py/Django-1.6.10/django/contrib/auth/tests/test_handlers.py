from __future__ import unicode_literals

from django.contrib.auth.handlers.modwsgi import check_password, groups_for_user
from django.contrib.auth.models import User, Group
from django.contrib.auth.tests.custom_user import CustomUser
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.test import TransactionTestCase
from django.test.utils import override_settings


# This must be a TransactionTestCase because the WSGI auth handler performs
# its own transaction management.
class ModWsgiHandlerTestCase(TransactionTestCase):
    """
    Tests for the mod_wsgi authentication handler
    """

    available_apps = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]

    @skipIfCustomUser
    def test_check_password(self):
        """
        Verify that check_password returns the correct values as per
        http://code.google.com/p/modwsgi/wiki/AccessControlMechanisms#Apache_Authentication_Provider
        """
        User.objects.create_user('test', 'test@example.com', 'test')

        # User not in database
        self.assertTrue(check_password({}, 'unknown', '') is None)

        # Valid user with correct password
        self.assertTrue(check_password({}, 'test', 'test'))

        # correct password, but user is inactive
        User.objects.filter(username='test').update(is_active=False)
        self.assertFalse(check_password({}, 'test', 'test'))

        # Valid user with incorrect password
        self.assertFalse(check_password({}, 'test', 'incorrect'))

    @override_settings(AUTH_USER_MODEL='auth.CustomUser')
    def test_check_password_custom_user(self):
        """
        Verify that check_password returns the correct values as per
        http://code.google.com/p/modwsgi/wiki/AccessControlMechanisms#Apache_Authentication_Provider

        with custom user installed
        """

        CustomUser._default_manager.create_user('test@example.com', '1990-01-01', 'test')

        # User not in database
        self.assertTrue(check_password({}, 'unknown', '') is None)

        # Valid user with correct password'
        self.assertTrue(check_password({}, 'test@example.com', 'test'))

        # Valid user with incorrect password
        self.assertFalse(check_password({}, 'test@example.com', 'incorrect'))

    @skipIfCustomUser
    def test_groups_for_user(self):
        """
        Check that groups_for_user returns correct values as per
        http://code.google.com/p/modwsgi/wiki/AccessControlMechanisms#Apache_Group_Authorisation
        """
        user1 = User.objects.create_user('test', 'test@example.com', 'test')
        User.objects.create_user('test1', 'test1@example.com', 'test1')
        group = Group.objects.create(name='test_group')
        user1.groups.add(group)

        # User not in database
        self.assertEqual(groups_for_user({}, 'unknown'), [])

        self.assertEqual(groups_for_user({}, 'test'), [b'test_group'])
        self.assertEqual(groups_for_user({}, 'test1'), [])
