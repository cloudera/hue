from __future__ import absolute_import

import time

from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment

from . import CommentTestCase
from ..models import Article


class CommentFormTests(CommentTestCase):
    def testInit(self):
        f = CommentForm(Article.objects.get(pk=1))
        self.assertEqual(f.initial['content_type'], str(Article._meta))
        self.assertEqual(f.initial['object_pk'], "1")
        self.assertNotEqual(f.initial['security_hash'], None)
        self.assertNotEqual(f.initial['timestamp'], None)

    def testValidPost(self):
        a = Article.objects.get(pk=1)
        f = CommentForm(a, data=self.getValidData(a))
        self.assertTrue(f.is_valid(), f.errors)
        return f

    def tamperWithForm(self, **kwargs):
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)
        d.update(kwargs)
        f = CommentForm(Article.objects.get(pk=1), data=d)
        self.assertFalse(f.is_valid())
        return f

    def testHoneypotTampering(self):
        self.tamperWithForm(honeypot="I am a robot")

    def testTimestampTampering(self):
        self.tamperWithForm(timestamp=str(time.time() - 28800))

    def testSecurityHashTampering(self):
        self.tamperWithForm(security_hash="Nobody expects the Spanish Inquisition!")

    def testContentTypeTampering(self):
        self.tamperWithForm(content_type="auth.user")

    def testObjectPKTampering(self):
        self.tamperWithForm(object_pk="3")

    def testSecurityErrors(self):
        f = self.tamperWithForm(honeypot="I am a robot")
        self.assertTrue("honeypot" in f.security_errors())

    def testGetCommentObject(self):
        f = self.testValidPost()
        c = f.get_comment_object()
        self.assertIsInstance(c, Comment)
        self.assertEqual(c.content_object, Article.objects.get(pk=1))
        self.assertEqual(c.comment, "This is my comment")
        c.save()
        self.assertEqual(Comment.objects.count(), 1)

    def testProfanities(self):
        """Test COMMENTS_ALLOW_PROFANITIES and PROFANITIES_LIST settings"""
        a = Article.objects.get(pk=1)
        d = self.getValidData(a)

        # Save settings in case other tests need 'em
        saved = settings.PROFANITIES_LIST, settings.COMMENTS_ALLOW_PROFANITIES

        # Don't wanna swear in the unit tests if we don't have to...
        settings.PROFANITIES_LIST = ["rooster"]

        # Try with COMMENTS_ALLOW_PROFANITIES off
        settings.COMMENTS_ALLOW_PROFANITIES = False
        f = CommentForm(a, data=dict(d, comment="What a rooster!"))
        self.assertFalse(f.is_valid())

        # Now with COMMENTS_ALLOW_PROFANITIES on
        settings.COMMENTS_ALLOW_PROFANITIES = True
        f = CommentForm(a, data=dict(d, comment="What a rooster!"))
        self.assertTrue(f.is_valid())

        # Restore settings
        settings.PROFANITIES_LIST, settings.COMMENTS_ALLOW_PROFANITIES = saved
