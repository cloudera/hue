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

from __future__ import unicode_literals

import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ImproperlyConfigured
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
from django_openid_auth.signals import openid_duplicate_username


User = get_user_model()


def get_user_group_model():
    """Returns the model used for mapping users to groups."""
    user_group_model_name = getattr(settings, 'AUTH_USER_GROUP_MODEL', None)
    if user_group_model_name is None:
        return User.groups.through
    else:
        try:
            # django.apps available starting from django 1.7
            from django.apps import apps
            get_model = apps.get_model
            args = (user_group_model_name,)
        except ImportError:
            # if we can't import, then it must be django 1.6, still using
            # the old django.db.models.loading code
            from django.db.models.loading import get_model
            app_label, model_name = user_group_model_name.split('.', 1)
            args = (app_label, model_name)
        try:
            model = get_model(*args)
            if model is None:
                # in django 1.6 referring to a non-installed app will
                # return None for get_model, but in 1.7 onwards it will
                # raise a LookupError exception.
                raise LookupError()
            return model
        except ValueError:
            raise ImproperlyConfigured(
                "AUTH_USER_GROUP_MODEL must be of the form "
                "'app_label.model_name'")
        except LookupError:
            raise ImproperlyConfigured(
                "AUTH_USER_GROUP_MODEL refers to model '%s' that has not been "
                "installed" % user_group_model_name)


UserGroup = get_user_group_model()


class OpenIDBackend(object):
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
            key = pape.AUTH_MULTI_FACTOR_PHYSICAL
            if (pape_response is None or
                    key not in pape_response.auth_policies):
                raise MissingPhysicalMultiFactor()

        teams_response = teams.TeamsResponse.fromSuccessResponse(
            openid_response)
        if teams_response:
            self.update_groups_from_teams(user, teams_response)
            self.update_staff_status_from_teams(user, teams_response)

        teams_required = getattr(settings,
                                 'OPENID_LAUNCHPAD_TEAMS_REQUIRED', [])
        if teams_required:
            teams_mapping = self.get_teams_mapping()
            groups_required = [group for team, group in teams_mapping.items()
                               if team in teams_required]
            user_groups = UserGroup.objects.filter(user=user)
            matches = set(groups_required).intersection(
                user_groups.values_list('group__name', flat=True))
            if not matches:
                name = 'OPENID_EMAIL_WHITELIST_REGEXP_LIST'
                whitelist_regexp_list = getattr(settings, name, [])
                for pattern in whitelist_regexp_list:
                    if re.match(pattern, user.email):
                        return user
                return None

        return user

    def _extract_user_details(self, openid_response):
        email = fullname = first_name = last_name = nickname = None
        verified = 'no'
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
            verified = fetch_response.getSingle(
                'http://ns.login.ubuntu.com/2013/validation/account', verified)

        if fullname and not (first_name or last_name):
            # Django wants to store first and last names separately,
            # so we do our best to split the full name.
            fullname = fullname.strip()
            split_names = fullname.rsplit(None, 1)
            if len(split_names) == 2:
                first_name, last_name = split_names
            else:
                first_name = ''
                last_name = fullname

        verification_scheme_map = getattr(
            settings, 'OPENID_VALID_VERIFICATION_SCHEMES', {})
        valid_schemes = verification_scheme_map.get(
            openid_response.endpoint.server_url,
            verification_scheme_map.get(None, ()))
        verified = (verified in valid_schemes)

        return dict(email=email, nickname=nickname, account_verified=verified,
                    first_name=first_name, last_name=last_name)

    def _get_preferred_username(self, nickname, email):
        if nickname:
            return nickname
        if email and getattr(settings, 'OPENID_USE_EMAIL_FOR_USERNAME', False):
            suggestion = ''.join([x for x in email if x.isalnum()])
            if suggestion:
                return suggestion
        return 'openiduser'

    def _get_available_username_for_nickname(self, nickname, identity_url):
        # If we don't have a nickname, and we're not being strict, use a
        # default
        nickname = nickname or 'openiduser'

        # See if we already have this nickname assigned to a username
        if not User.objects.filter(username=nickname).exists():
            return nickname

        # Check if we already have nickname+i for this identity_url
        try:
            user_openid = UserOpenID.objects.get(
                claimed_id=identity_url,
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

        # Pick a username for the user based on their nickname,
        # checking for conflicts.  Start with number of existing users who's
        # username starts with this nickname to avoid having to iterate over
        # all of the existing ones.
        i = User.objects.filter(username__startswith=nickname).count() + 1
        username = nickname
        while User.objects.filter(username=username).exists():
            username = nickname + str(i)
            i += 1

        return username

    def _ensure_available_username(self, nickname, identity_url):
        if not nickname:
            raise MissingUsernameViolation()

        # As long as the `QuerySet` does not get evaluated, no
        # caching should be involved in our multiple `exists()`
        # calls. See docs for details: http://bit.ly/2aYCmkw
        user_with_same_username = User.objects.exclude(
            useropenid__claimed_id=identity_url
        ).filter(username=nickname)

        if user_with_same_username.exists():
            # Notify any listeners that a duplicated username was
            # found and give the opportunity to handle conflict.
            openid_duplicate_username.send(sender=User, username=nickname)

            # Check for conflicts again as the signal could have handled it.
            if user_with_same_username.exists():
                raise DuplicateUsernameViolation(
                    "The username (%s) with which you tried to log in is "
                    "already in use for a different account." % nickname)

    def _get_available_username(self, nickname, identity_url):
        if getattr(settings, 'OPENID_STRICT_USERNAMES', False):
            self._ensure_available_username(nickname, identity_url)
        else:
            nickname = self._get_available_username_for_nickname(
                nickname, identity_url)
        return nickname

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

        nickname = self._get_preferred_username(
            details['nickname'], details['email'])
        email = details['email'] or ''

        username = self._get_available_username(
            nickname, openid_response.identity_url)

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
            user.username = self._get_available_username(
                details['nickname'], openid_response.identity_url)
            updated = True
        account_verified = details.get('account_verified', None)
        if (account_verified is not None):
            permission = Permission.objects.get(codename='account_verified')
            perm_label = '%s.%s' % (permission.content_type.app_label,
                                    permission.codename)
            if account_verified and not user.has_perm(perm_label):
                user.user_permissions.add(permission)
            elif not account_verified and user.has_perm(perm_label):
                user.user_permissions.remove(permission)

        if updated:
            user.save()

    def get_teams_mapping(self):
        teams_mapping_auto = getattr(
            settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO', False)
        teams_mapping_auto_blacklist = getattr(
            settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST', [])
        teams_mapping = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
        if teams_mapping_auto:
            # ignore teams_mapping. use all django-groups
            teams_mapping = dict()
            all_groups = Group.objects.exclude(
                name__in=teams_mapping_auto_blacklist)
            for group in all_groups:
                teams_mapping[group.name] = group.name
        return teams_mapping

    def update_groups_from_teams(self, user, teams_response):
        teams_mapping = self.get_teams_mapping()
        if len(teams_mapping) == 0:
            return

        mapping = [
            teams_mapping[lp_team] for lp_team in teams_response.is_member
            if lp_team in teams_mapping]
        user_groups = UserGroup.objects.filter(user=user)
        matching_groups = user_groups.filter(
            group__name__in=teams_mapping.values())
        current_groups = set(
            user_group.group for user_group in matching_groups)
        desired_groups = set(Group.objects.filter(name__in=mapping))
        groups_to_remove = current_groups - desired_groups
        groups_to_add = desired_groups - current_groups
        user_groups.filter(group__in=groups_to_remove).delete()
        for group in groups_to_add:
            UserGroup.objects.create(user=user, group=group)

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
