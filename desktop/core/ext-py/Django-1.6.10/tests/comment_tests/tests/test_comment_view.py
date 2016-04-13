from __future__ import absolute_import, unicode_literals

import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments import signals
from django.contrib.comments.models import Comment

from . import CommentTestCase
from ..models import Article, Book


post_redirect_re = re.compile(r'^http://testserver/posted/\?c=(?P<pk>\d+$)')

class CommentViewTests(CommentTestCase):

    def testPostCommentHTTPMethods(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.get("/post/", data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "POST")

    def testPostCommentMissingCtype(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        del data["content_type"]
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostCommentBadCtype(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["content_type"] = "Nobody expects the Spanish Inquisition!"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostCommentMissingObjectPK(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        del data["object_pk"]
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostCommentBadObjectPK(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["object_pk"] = "14"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostInvalidIntegerPK(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["comment"] = "This is another comment"
        data["object_pk"] = '\ufffd'
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testPostInvalidDecimalPK(self):
        b = Book.objects.get(pk='12.34')
        data = self.getValidData(b)
        data["comment"] = "This is another comment"
        data["object_pk"] = 'cookies'
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testCommentPreview(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["preview"] = "Preview"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "comments/preview.html")

    def testHashTampering(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["security_hash"] = "Nobody expects the Spanish Inquisition!"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)

    def testDebugCommentErrors(self):
        """The debug error template should be shown only if DEBUG is True"""
        olddebug = settings.DEBUG

        settings.DEBUG = True
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["security_hash"] = "Nobody expects the Spanish Inquisition!"
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "comments/400-debug.html")

        settings.DEBUG = False
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateNotUsed(response, "comments/400-debug.html")

        settings.DEBUG = olddebug

    def testCreateValidComment(self):
        address = "1.2.3.4"
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        self.response = self.client.post("/post/", data, REMOTE_ADDR=address)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.all()[0]
        self.assertEqual(c.ip_address, address)
        self.assertEqual(c.comment, "This is my comment")

    def testCreateValidCommentIPv6(self):
        """
        Test creating a valid comment with a long IPv6 address.
        Note that this test should fail when Comment.ip_address is an IPAddress instead of a GenericIPAddress,
        but does not do so on SQLite or PostgreSQL, because they use the TEXT and INET types, which already
        allow storing an IPv6 address internally.
        """
        address = "2a02::223:6cff:fe8a:2e8a"
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        self.response = self.client.post("/post/", data, REMOTE_ADDR=address)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.all()[0]
        self.assertEqual(c.ip_address, address)
        self.assertEqual(c.comment, "This is my comment")

    def testCreateValidCommentIPv6Unpack(self):
        address = "::ffff:18.52.18.52"
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        self.response = self.client.post("/post/", data, REMOTE_ADDR=address)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.all()[0]
        # We trim the '::ffff:' bit off because it is an IPv4 addr
        self.assertEqual(c.ip_address, address[7:])
        self.assertEqual(c.comment, "This is my comment")

    def testPostAsAuthenticatedUser(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data['name'] = data['email'] = ''
        self.client.login(username="normaluser", password="normaluser")
        self.response = self.client.post("/post/", data, REMOTE_ADDR="1.2.3.4")
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.all()[0]
        self.assertEqual(c.ip_address, "1.2.3.4")
        u = User.objects.get(username='normaluser')
        self.assertEqual(c.user, u)
        self.assertEqual(c.user_name, u.get_full_name())
        self.assertEqual(c.user_email, u.email)

    def testPostAsAuthenticatedUserWithoutFullname(self):
        """
        Check that the user's name in the comment is populated for
        authenticated users without first_name and last_name.
        """
        user = User.objects.create_user(username='jane_other',
                email='jane@example.com', password='jane_other')
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data['name'] = data['email'] = ''
        self.client.login(username="jane_other", password="jane_other")
        self.response = self.client.post("/post/", data, REMOTE_ADDR="1.2.3.4")
        c = Comment.objects.get(user=user)
        self.assertEqual(c.ip_address, "1.2.3.4")
        self.assertEqual(c.user_name, 'jane_other')
        user.delete()

    def testPreventDuplicateComments(self):
        """Prevent posting the exact same comment twice"""
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        self.client.post("/post/", data)
        self.client.post("/post/", data)
        self.assertEqual(Comment.objects.count(), 1)

        # This should not trigger the duplicate prevention
        self.client.post("/post/", dict(data, comment="My second comment."))
        self.assertEqual(Comment.objects.count(), 2)

    def testCommentSignals(self):
        """Test signals emitted by the comment posting view"""

        # callback
        def receive(sender, **kwargs):
            self.assertEqual(kwargs['comment'].comment, "This is my comment")
            self.assertTrue('request' in kwargs)
            received_signals.append(kwargs.get('signal'))

        # Connect signals and keep track of handled ones
        received_signals = []
        expected_signals = [
            signals.comment_will_be_posted, signals.comment_was_posted
        ]
        for signal in expected_signals:
            signal.connect(receive)

        # Post a comment and check the signals
        self.testCreateValidComment()
        self.assertEqual(received_signals, expected_signals)

        for signal in expected_signals:
            signal.disconnect(receive)

    def testWillBePostedSignal(self):
        """
        Test that the comment_will_be_posted signal can prevent the comment from
        actually getting saved
        """
        def receive(sender, **kwargs): return False
        signals.comment_will_be_posted.connect(receive, dispatch_uid="comment-test")
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.post("/post/", data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)
        signals.comment_will_be_posted.disconnect(dispatch_uid="comment-test")

    def testWillBePostedSignalModifyComment(self):
        """
        Test that the comment_will_be_posted signal can modify a comment before
        it gets posted
        """
        def receive(sender, **kwargs):
             # a bad but effective spam filter :)...
            kwargs['comment'].is_public = False

        signals.comment_will_be_posted.connect(receive)
        self.testCreateValidComment()
        c = Comment.objects.all()[0]
        self.assertFalse(c.is_public)

    def testCommentNext(self):
        """Test the different "next" actions the comment view can take"""
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = post_redirect_re.match(location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

        data["next"] = "/somewhere/else/"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^http://testserver/somewhere/else/\?c=\d+$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

        data["next"] = "http://badserver/somewhere/else/"
        data["comment"] = "This is another comment with an unsafe next url"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = post_redirect_re.match(location)
        self.assertTrue(match != None, "Unsafe redirection to: %s" % location)

    def testCommentDoneView(self):
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = post_redirect_re.match(location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)
        pk = int(match.group('pk'))
        response = self.client.get(location)
        self.assertTemplateUsed(response, "comments/posted.html")
        self.assertEqual(response.context[0]["comment"], Comment.objects.get(pk=pk))

    def testCommentNextWithQueryString(self):
        """
        The `next` key needs to handle already having a query string (#10585)
        """
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["next"] = "/somewhere/else/?foo=bar"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^http://testserver/somewhere/else/\?foo=bar&c=\d+$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

    def testCommentPostRedirectWithInvalidIntegerPK(self):
        """
        Tests that attempting to retrieve the location specified in the
        post redirect, after adding some invalid data to the expected
        querystring it ends with, doesn't cause a server error.
        """
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        broken_location = location + "\ufffd"
        response = self.client.get(broken_location)
        self.assertEqual(response.status_code, 200)

    def testCommentNextWithQueryStringAndAnchor(self):
        """
        The `next` key needs to handle already having an anchor. Refs #13411.
        """
        # With a query string also.
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["next"] = "/somewhere/else/?foo=bar#baz"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^http://testserver/somewhere/else/\?foo=bar&c=\d+#baz$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)

        # Without a query string
        a = Article.objects.get(pk=1)
        data = self.getValidData(a)
        data["next"] = "/somewhere/else/#baz"
        data["comment"] = "This is another comment"
        response = self.client.post("/post/", data)
        location = response["Location"]
        match = re.search(r"^http://testserver/somewhere/else/\?c=\d+#baz$", location)
        self.assertTrue(match != None, "Unexpected redirect location: %s" % location)
