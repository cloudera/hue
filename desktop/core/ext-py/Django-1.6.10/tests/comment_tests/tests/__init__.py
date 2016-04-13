from __future__ import absolute_import

from django.contrib.auth.models import User
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings

from ..models import Article, Author

# Shortcut
CT = ContentType.objects.get_for_model

# Helper base class for comment tests that need data.
@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',))
class CommentTestCase(TestCase):
    fixtures = ["comment_tests"]
    urls = 'comment_tests.urls_default'

    def createSomeComments(self):
        # Two anonymous comments on two different objects
        c1 = Comment.objects.create(
            content_type = CT(Article),
            object_pk = "1",
            user_name = "Joe Somebody",
            user_email = "jsomebody@example.com",
            user_url = "http://example.com/~joe/",
            comment = "First!",
            site = Site.objects.get_current(),
        )
        c2 = Comment.objects.create(
            content_type = CT(Author),
            object_pk = "1",
            user_name = "Joe Somebody",
            user_email = "jsomebody@example.com",
            user_url = "http://example.com/~joe/",
            comment = "First here, too!",
            site = Site.objects.get_current(),
        )

        # Two authenticated comments: one on the same Article, and
        # one on a different Author
        user = User.objects.create(
            username = "frank_nobody",
            first_name = "Frank",
            last_name = "Nobody",
            email = "fnobody@example.com",
            password = "",
            is_staff = False,
            is_active = True,
            is_superuser = False,
        )
        c3 = Comment.objects.create(
            content_type = CT(Article),
            object_pk = "1",
            user = user,
            user_url = "http://example.com/~frank/",
            comment = "Damn, I wanted to be first.",
            site = Site.objects.get_current(),
        )
        c4 = Comment.objects.create(
            content_type = CT(Author),
            object_pk = "2",
            user = user,
            user_url = "http://example.com/~frank/",
            comment = "You get here first, too?",
            site = Site.objects.get_current(),
        )

        return c1, c2, c3, c4

    def getData(self):
        return {
            'name'      : 'Jim Bob',
            'email'     : 'jim.bob@example.com',
            'url'       : '',
            'comment'   : 'This is my comment',
        }

    def getValidData(self, obj):
        f = CommentForm(obj)
        d = self.getData()
        d.update(f.initial)
        return d

from comment_tests.tests.test_app_api import *
from comment_tests.tests.test_feeds import *
from comment_tests.tests.test_models import *
from comment_tests.tests.test_comment_form import *
from comment_tests.tests.test_templatetags import *
from comment_tests.tests.test_comment_view import *
from comment_tests.tests.test_comment_utils_moderators import *
from comment_tests.tests.test_moderation_views import *
