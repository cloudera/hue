# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2008-2013 Canonical Ltd.
# Copyright (C) 2010 Dave Walker
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

try:
    from urllib.parse import parse_qsl, urlencode, urlparse
except ImportError:
    from urllib import urlencode
    from urlparse import parse_qsl, urlparse

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django_openid_auth import views
from django_openid_auth.models import Nonce, Association, UserOpenID
from django_openid_auth.store import DjangoOpenIDStore


class NonceAdmin(admin.ModelAdmin):
    list_display = ('server_url', 'timestamp')
    actions = ['cleanup_nonces']

    def cleanup_nonces(self, request, queryset):
        store = DjangoOpenIDStore()
        count = store.cleanupNonces()
        self.message_user(request, "%d expired nonces removed" % count)
    cleanup_nonces.short_description = "Clean up expired nonces"


admin.site.register(Nonce, NonceAdmin)


class AssociationAdmin(admin.ModelAdmin):
    list_display = ('server_url', 'assoc_type')
    list_filter = ('assoc_type',)
    search_fields = ('server_url',)
    actions = ['cleanup_associations']

    def cleanup_associations(self, request, queryset):
        store = DjangoOpenIDStore()
        count = store.cleanupAssociations()
        self.message_user(request, "%d expired associations removed" % count)
    cleanup_associations.short_description = "Clean up expired associations"


admin.site.register(Association, AssociationAdmin)


class UserOpenIDAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('user', 'claimed_id')
    search_fields = ('claimed_id',)


admin.site.register(UserOpenID, UserOpenIDAdmin)


# store a reference to the original admin login
original_admin_login = admin.sites.AdminSite.login


def _openid_login(instance, request, error_message='', extra_context=None):
    # Support for allowing openid authentication for /admin
    # (django.contrib.admin)
    if not getattr(settings, 'OPENID_USE_AS_ADMIN_LOGIN', False):
        return original_admin_login(
            instance, request, extra_context=extra_context)

    if not request.user.is_authenticated():
        # Redirect to openid login path,
        _, _, path, _, query, _ = urlparse(request.get_full_path())
        qs = dict(parse_qsl(query))
        qs.setdefault('next', path)
        return HttpResponseRedirect(
            settings.LOGIN_URL + "?" + urlencode(qs))

    if not request.user.is_staff:
        return views.default_render_failure(
            request, "%s %s does not have admin/staff access."
            % (settings.AUTH_USER_MODEL, request.user.username))

    # No error message was supplied
    assert error_message, "Unknown Error: %s" % error_message


# Overide the standard admin login form.
admin.sites.AdminSite.login = _openid_login
