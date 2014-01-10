# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2007 Simon Willison
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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.html import escape


def index(request):
    s = ['<p>']
    if request.user.is_authenticated():
        s.append('You are signed in as <strong>%s</strong> (%s)' % (
                escape(request.user.username),
                escape(request.user.get_full_name())))
        s.append(' | <a href="/logout">Sign out</a>')
    else:
        s.append('<a href="/openid/login">Sign in with OpenID</a>')

    s.append('</p>')

    s.append('<p><a href="/private">This requires authentication</a></p>')
    return HttpResponse('\n'.join(s))


def next_works(request):
    return HttpResponse('?next= bit works. <a href="/">Home</a>')


@login_required
def require_authentication(request):
    return HttpResponse('This page requires authentication')
