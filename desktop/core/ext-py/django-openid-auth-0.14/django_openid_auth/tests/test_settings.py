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

from unittest import skipIf

from django import VERSION
from django.conf import settings
from django.test import TestCase


class SessionSerializerTest(TestCase):
    """Django 1.6 changed the default session serializer to use JSON
    instead of pickle for security reasons[0]. Unfortunately the
    openid module on which we rely stores objects which are not JSON
    serializable[1], so until this is fixed upstream (or we decide to
    create a wrapper serializer) we are recommending Django 1.6 users
    to fallback to the PickleSerializer.

    [0] https://bit.ly/1myzetd
    [1] https://github.com/openid/python-openid/issues/17
    """

    @skipIf(VERSION < (1, 5), "Django 1.4 does not provide SESSION_SERIALIZER")
    def test_using_pickle_session_serializer(self):
        serializer = getattr(settings, 'SESSION_SERIALIZER', '')
        self.assertEqual(
            serializer, 'django.contrib.sessions.serializers.PickleSerializer')
