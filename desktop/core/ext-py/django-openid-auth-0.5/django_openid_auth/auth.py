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

"""Glue between OpenID and django.contrib.auth."""

__metaclass__ = type

from django.conf import settings
from django.contrib.auth.models import User, Group
from openid.consumer.consumer import SUCCESS
from openid.extensions import ax, sreg, pape

from django_openid_auth import teams
from django_openid_auth.models import UserOpenID
from django_openid_auth.exceptions import (
    IdentityAlreadyClaimed,
    DuplicateUsernameViolation,
    MissingUsernameViolation,
    MissingPhysicalMultiFactor,
    RequiredAttributeNotReturned,
)

class OpenIDBackend:
    """A django.contrib.auth backend that authenticates the user based on
    an OpenID response."""

    supports_object_permissions = False
    supports_anonymous_user = True

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, **kwargs):
        """Authenticate the user based on an OpenID response."""
        # Require that the OpenID response be passed in as a keyword
        # argument, to make sure we don't match the username/password
        # calling conventions of authenticate.

        openid_response = kwargs.get('openid_response')
        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        user = None
        try:
            user_openid = UserOpenID.objects.get(
                claimed_id__exact=openid_response.identity_url)
        except UserOpenID.DoesNotExist:
            if getattr(settings, 'OPENID_CREATE_USERS', False):
                user = self.create_user_from_openid(openid_response)
        else:
            user = user_openid.user

        if user is None:
            return None

        if getattr(settings, 'OPENID_UPDATE_DETAILS_FROM_SREG', False):
            details = self._extract_user_details(openid_response)
            self.update_user_details(user, details, openid_response)

        if getattr(settings, 'OPENID_PHYSICAL_MULTIFACTOR_REQUIRED', False):
            pape_response = pape.Response.fromSuccessResponse(openid_response)
            if pape_response is None or \
               pape.AUTH_MULTI_FACTOR_PHYSICAL not in pape_response.auth_policies:
                raise MissingPhysicalMultiFactor()

        teams_response = teams.TeamsResponse.fromSuccessResponse(
            openid_response)
        if teams_response:
            self.update_groups_from_teams(user, teams_response)
            self.update_staff_status_from_teams(user, teams_response)

        return user

    def _extract_user_details(self, openid_response):
        email = fullname = first_name = last_name = nickname = None
        sreg_response = sreg.SRegResponse.fromSuccessResponse(openid_response)
        if sreg_response:
            email = sreg_response.get('email')
            fullname = sreg_response.get('fullname')
            nickname = sreg_response.get('nickname')
        # If any attributes are provided via Attribute Exchange, use
        # them in preference.
        fetch_response = ax.FetchResponse.fromSuccessResponse(openid_response)
        if fetch_response:
            # The myOpenID provider advertises AX support, but uses
            # attribute names from an obsolete draft of the
            # specification.  We check for them first so the common
            # names take precedence.
            email = fetch_response.getSingle(
                'http://schema.openid.net/contact/email', email)
            fullname = fetch_response.getSingle(
                'http://schema.openid.net/namePerson', fullname)
            nickname = fetch_response.getSingle(
                'http://schema.openid.net/namePerson/friendly', nickname)

            email = fetch_response.getSingle(
                'http://axschema.org/contact/email', email)
            fullname = fetch_response.getSingle(
                'http://axschema.org/namePerson', fullname)
            first_name = fetch_response.getSingle(
                'http://axschema.org/namePerson/first', first_name)
            last_name = fetch_response.getSingle(
                'http://axschema.org/namePerson/last', last_name)
            nickname = fetch_response.getSingle(
                'http://axschema.org/namePerson/friendly', nickname)

        if fullname and not (first_name or last_name):
            # Django wants to store first and last names separately,
            # so we do our best to split the full name.
            fullname = fullname.strip()
            split_names = fullname.rsplit(None, 1)
            if len(split_names) == 2:
                first_name, last_name = split_names
            else:
                first_name = u''
                last_name = fullname

        return dict(email=email, nickname=nickname,
                    first_name=first_name, last_name=last_name)

    def _get_preferred_username(self, nickname, email):
        if nickname:
            return nickname
        if email and getattr(settings, 'OPENID_USE_EMAIL_FOR_USERNAME',
            False):
            suggestion = ''.join([x for x in email if x.isalnum()])
            if suggestion:
                return suggestion
        return 'openiduser'

    def _get_available_username(self, nickname, identity_url):
        # If we're being strict about usernames, throw an error if we didn't
        # get one back from the provider
        if getattr(settings, 'OPENID_STRICT_USERNAMES', False):
            if nickname is None or nickname == '':
                raise MissingUsernameViolation()
                
        # If we don't have a nickname, and we're not being strict, use a default
        nickname = nickname or 'openiduser'

        # See if we already have this nickname assigned to a username
        try:
            user = User.objects.get(username__exact=nickname)
        except User.DoesNotExist:
            # No conflict, we can use this nickname
            return nickname

        # Check if we already have nickname+i for this identity_url
        try:
            user_openid = UserOpenID.objects.get(
                claimed_id__exact=identity_url,
                user__username__startswith=nickname)
            # No exception means we have an existing user for this identity
            # that starts with this nickname.
            
            # If they are an exact match, the user already exists and hasn't
            # changed their username, so continue to use it
            if nickname == user_openid.user.username:
                return nickname
            
            # It is possible we've had to assign them to nickname+i already.
            oid_username = user_openid.user.username
            if len(oid_username) > len(nickname):
                try:
                    # check that it ends with a number
                    int(oid_username[len(nickname):])
                    return oid_username
                except ValueError:
                    # username starts with nickname, but isn't nickname+#
                    pass
        except UserOpenID.DoesNotExist:
            # No user associated with this identity_url
            pass


        if getattr(settings, 'OPENID_STRICT_USERNAMES', False):
            if User.objects.filter(username__exact=nickname).count() > 0:
                raise DuplicateUsernameViolation(
                    "The username (%s) with which you tried to log in is "
                    "already in use for a different account." % nickname)

        # Pick a username for the user based on their nickname,
        # checking for conflicts.  Start with number of existing users who's
        # username starts with this nickname to avoid having to iterate over
        # all of the existing ones.
        i = User.objects.filter(username__startswith=nickname).count() + 1
        while True:
            username = nickname
            if i > 1:
                username += str(i)
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                break
            i += 1
        return username

    def create_user_from_openid(self, openid_response):
        details = self._extract_user_details(openid_response)
        required_attrs = getattr(settings, 'OPENID_SREG_REQUIRED_FIELDS', [])
        if getattr(settings, 'OPENID_STRICT_USERNAMES', False):
            required_attrs.append('nickname')

        for required_attr in required_attrs:
            if required_attr not in details or not details[required_attr]:
                raise RequiredAttributeNotReturned(
                    "An attribute required for logging in was not "
                    "returned ({0}).".format(required_attr))

        nickname = self._get_preferred_username(details['nickname'],
            details['email'])
        email = details['email'] or ''

        username = self._get_available_username(nickname,
            openid_response.identity_url)

        user = User.objects.create_user(username, email, password=None)
        self.associate_openid(user, openid_response)
        self.update_user_details(user, details, openid_response)

        return user

    def associate_openid(self, user, openid_response):
        """Associate an OpenID with a user account."""
        # Check to see if this OpenID has already been claimed.
        try:
            user_openid = UserOpenID.objects.get(
                claimed_id__exact=openid_response.identity_url)
        except UserOpenID.DoesNotExist:
            user_openid = UserOpenID(
                user=user,
                claimed_id=openid_response.identity_url,
                display_id=openid_response.endpoint.getDisplayIdentifier())
            user_openid.save()
        else:
            if user_openid.user != user:
                raise IdentityAlreadyClaimed(
                    "The identity %s has already been claimed"
                    % openid_response.identity_url)

        return user_openid

    def update_user_details(self, user, details, openid_response):
        updated = False
        if details['first_name']:
            user.first_name = details['first_name'][:30]
            updated = True
        if details['last_name']:
            user.last_name = details['last_name'][:30]
            updated = True
        if details['email']:
            user.email = details['email']
            updated = True
        if getattr(settings, 'OPENID_FOLLOW_RENAMES', False):
            user.username = self._get_available_username(details['nickname'], openid_response.identity_url)
            updated = True

        if updated:
            user.save()

    def update_groups_from_teams(self, user, teams_response):
        teams_mapping_auto = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO', False)
        teams_mapping_auto_blacklist = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST', [])
        teams_mapping = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
        if teams_mapping_auto:
            #ignore teams_mapping. use all django-groups
            teams_mapping = dict()
            all_groups = Group.objects.exclude(name__in=teams_mapping_auto_blacklist)
            for group in all_groups:
                teams_mapping[group.name] = group.name

        if len(teams_mapping) == 0:
            return

        current_groups = set(user.groups.filter(
                name__in=teams_mapping.values()))
        desired_groups = set(Group.objects.filter(
                name__in=[teams_mapping[lp_team]
                          for lp_team in teams_response.is_member
                          if lp_team in teams_mapping]))
        for group in current_groups - desired_groups:
            user.groups.remove(group)
        for group in desired_groups - current_groups:
            user.groups.add(group)

    def update_staff_status_from_teams(self, user, teams_response):
        if not hasattr(settings, 'OPENID_LAUNCHPAD_STAFF_TEAMS'):
            return

        staff_teams = getattr(settings, 'OPENID_LAUNCHPAD_STAFF_TEAMS', [])
        user.is_staff = False

        for lp_team in teams_response.is_member:
            if lp_team in staff_teams:
                user.is_staff = True
                break

        user.save()

