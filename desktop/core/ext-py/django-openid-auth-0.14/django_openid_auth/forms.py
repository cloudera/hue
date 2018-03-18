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

from __future__ import unicode_literals

from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _
from django.conf import settings

from openid.yadis import xri

from django_openid_auth import PY3


def teams_new_unicode(self):
    """
    Replacement for Group.__unicode__()
    Calls original method to chain results
    """
    name = self.unicode_before_teams()
    teams_mapping = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
    group_teams = [t for t in teams_mapping if teams_mapping[t] == self.name]
    if len(group_teams) > 0:
        return "%s -> %s" % (name, ", ".join(group_teams))
    else:
        return name


if PY3:
    Group.unicode_before_teams = Group.__str__
    Group.__str__ = teams_new_unicode
else:
    Group.unicode_before_teams = Group.__unicode__
    Group.__unicode__ = teams_new_unicode


class UserChangeFormWithTeamRestriction(UserChangeForm):
    """
    Extends UserChangeForm to add teams awareness to the user admin form
    """
    def clean_groups(self):
        data = self.cleaned_data['groups']
        teams_mapping = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
        known_teams = teams_mapping.values()
        user_groups = self.instance.groups.all()
        for group in data:
            if group.name in known_teams and group not in user_groups:
                raise forms.ValidationError(
                    "The group %s is mapped to an external team.  "
                    "You cannot assign it manually." % group.name)
        return data


UserAdmin.form = UserChangeFormWithTeamRestriction


class OpenIDLoginForm(forms.Form):
    openid_identifier = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'required openid'}))

    def clean_openid_identifier(self):
        if 'openid_identifier' in self.cleaned_data:
            openid_identifier = self.cleaned_data['openid_identifier']
            if (xri.identifierScheme(openid_identifier) == 'XRI' and
                    getattr(settings, 'OPENID_DISALLOW_INAMES', False)):
                raise forms.ValidationError(_('i-names are not supported'))
            return self.cleaned_data['openid_identifier']
