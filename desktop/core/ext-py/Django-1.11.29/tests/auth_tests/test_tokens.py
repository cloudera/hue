import unittest
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.utils.six import PY3


class TokenGeneratorTest(TestCase):

    def test_make_token(self):
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        self.assertTrue(p0.check_token(user, tk1))

    def test_10265(self):
        """
        The token generated for a user created in the same request
        will work correctly.
        """
        # See ticket #10265
        user = User.objects.create_user('comebackkid', 'test3@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        reload = User.objects.get(username='comebackkid')
        tk2 = p0.make_token(reload)
        self.assertEqual(tk1, tk2)

    def test_timeout(self):
        """
        The token is valid after n days, but no greater.
        """
        # Uses a mocked version of PasswordResetTokenGenerator so we can change
        # the value of 'today'
        class Mocked(PasswordResetTokenGenerator):
            def __init__(self, today):
                self._today_val = today

            def _today(self):
                return self._today_val

        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        p1 = Mocked(date.today() + timedelta(settings.PASSWORD_RESET_TIMEOUT_DAYS))
        self.assertTrue(p1.check_token(user, tk1))

        p2 = Mocked(date.today() + timedelta(settings.PASSWORD_RESET_TIMEOUT_DAYS + 1))
        self.assertFalse(p2.check_token(user, tk1))

    @unittest.skipIf(PY3, "Unnecessary test with Python 3")
    def test_date_length(self):
        """
        Overly long dates, which are a potential DoS vector, aren't allowed.
        """
        user = User.objects.create_user('ima1337h4x0r', 'test4@example.com', 'p4ssw0rd')
        p0 = PasswordResetTokenGenerator()

        # This will put a 14-digit base36 timestamp into the token, which is too large.
        with self.assertRaises(ValueError):
            p0._make_token_with_timestamp(user, 175455491841851871349)

    def test_check_token_with_nonexistent_token_and_user(self):
        user = User.objects.create_user('tokentestuser', 'test2@example.com', 'testpw')
        p0 = PasswordResetTokenGenerator()
        tk1 = p0.make_token(user)
        self.assertIs(p0.check_token(None, tk1), False)
        self.assertIs(p0.check_token(user, None), False)
