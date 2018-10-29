# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2008-2013 Canonical Ltd.
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

"""Exception classes thrown by OpenID Authentication and Validation."""

from __future__ import unicode_literals


class DjangoOpenIDException(Exception):
    pass


class RequiredAttributeNotReturned(DjangoOpenIDException):
    pass


class IdentityAlreadyClaimed(DjangoOpenIDException):

    def __init__(self, message=None):
        if message is None:
            self.message = (
                "Another user already exists for your selected OpenID")
        else:
            self.message = message


class DuplicateUsernameViolation(DjangoOpenIDException):

    def __init__(self, message=None):
        if message is None:
            self.message = "Your desired username is already being used."
        else:
            self.message = message


class MissingUsernameViolation(DjangoOpenIDException):

    def __init__(self, message=None):
        if message is None:
            self.message = "No nickname given for your account."
        else:
            self.message = message


class MissingPhysicalMultiFactor(DjangoOpenIDException):

    def __init__(self, message=None):
        if message is None:
            self.message = (
                "Login requires physical multi-factor authentication.")
        else:
            self.message = message
