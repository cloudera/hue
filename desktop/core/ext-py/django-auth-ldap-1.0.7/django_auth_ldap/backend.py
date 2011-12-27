# Copyright (c) 2009, Peter Sagerson
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# - Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# - Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
LDAP authentication backend

Complete documentation can be found in docs/howto/auth-ldap.txt (or the thing it
compiles to).

Use of this backend requires the python-ldap module. To support unit tests, we
import ldap in a single centralized place (config._LDAPConfig) so that the test
harness can insert a mock object.

A few notes on naming conventions. If an identifier ends in _dn, it is a string
representation of a distinguished name. If it ends in _info, it is a 2-tuple
containing a DN and a dictionary of lists of attributes. ldap.search_s returns a
list of such structures. An identifier that ends in _attrs is the dictionary of
attributes from the _info structure.

A connection is an LDAPObject that has been successfully bound with a DN and
password. The identifier 'user' always refers to a User model object; LDAP user
information will be user_dn or user_info.

Additional classes can be found in the config module next to this one.
"""

try:
    set
except NameError:
    from sets import Set as set     # Python 2.3 fallback

import sys
import traceback
import pprint
import copy

import django.db
from django.contrib.auth.models import User, Group, SiteProfileNotAvailable
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from django_auth_ldap.config import _LDAPConfig, LDAPSearch, LDAPGroupType


logger = _LDAPConfig.get_logger()


class LDAPBackend(object):
    """
    The main backend class. This implements the auth backend API, although it
    actually delegates most of its work to _LDAPUser, which is defined next.
    """
    ldap = None # The cached ldap module (or mock object)
    
    def __init__(self):
        self.ldap = self.ldap_module()
    
    def ldap_module(cls):
        """
        Requests the ldap module from _LDAPConfig. Under a test harness, this
        will be a mock object. We only do this once because this is where we
        apply AUTH_LDAP_GLOBAL_OPTIONS.
        """
        if cls.ldap is None:
            cls.ldap = _LDAPConfig.get_ldap()
            
            for opt, value in ldap_settings.AUTH_LDAP_GLOBAL_OPTIONS.iteritems():
                cls.ldap.set_option(opt, value)
        
        return cls.ldap
    ldap_module = classmethod(ldap_module)


    #
    # The Django auth backend API
    #

    def authenticate(self, username, password):
        ldap_user = _LDAPUser(self, username=username)
        user = ldap_user.authenticate(password)
        
        return user
    
    def get_user(self, user_id):
        user = None
        
        try:
            user = User.objects.get(pk=user_id)
            _LDAPUser(self, user=user) # This sets user.ldap_user
        except User.DoesNotExist:
            pass
        
        return user
    
    def has_perm(self, user, perm):
        return perm in self.get_all_permissions(user)

    def has_module_perms(self, user, app_label):
        for perm in self.get_all_permissions(user):
            if perm[:perm.index('.')] == app_label:
                return True

        return False

    def get_all_permissions(self, user):
        return self.get_group_permissions(user)

    def get_group_permissions(self, user):
        if not hasattr(user, 'ldap_user') and ldap_settings.AUTH_LDAP_AUTHORIZE_ALL_USERS:
            _LDAPUser(self, user=user) # This sets user.ldap_user
        
        if hasattr(user, 'ldap_user'):
            return user.ldap_user.get_group_permissions()
        else:
            return set()

    #
    # Bonus API: populate the Django user from LDAP without authenticating.
    #

    def populate_user(self, username):
        ldap_user = _LDAPUser(self, username=username)
        user = ldap_user.populate_user()
        
        return user
    
    #
    # Hooks for subclasses
    #

    def get_or_create_user(self, username, ldap_user):
        """
        This must return a (User, created) 2-tuple for the given LDAP user.
        username is the Django-friendly username of the user. ldap_user.dn is
        the user's DN and ldap_user.attrs contains all of their LDAP attributes.
        """
        return User.objects.get_or_create(username=username)

    def ldap_to_django_username(self, username):
        return username

    def django_to_ldap_username(self, username):
        return username


class _LDAPUser(object):
    """
    Represents an LDAP user and ultimately fields all requests that the
    backend receives. This class exists for two reasons. First, it's
    convenient to have a separate object for each request so that we can use
    object attributes without running into threading problems. Second, these
    objects get attached to the User objects, which allows us to cache
    expensive LDAP information, especially around groups and permissions.
    
    self.backend is a reference back to the LDAPBackend instance, which we need
    to access the ldap module and any hooks that a subclass has overridden.
    """
    class AuthenticationFailed(Exception):
        pass
    
    #
    # Initialization
    #
    
    def __init__(self, backend, username=None, user=None):
        """
        A new LDAPUser must be initialized with either a username or an
        authenticated User object. If a user is given, the username will be
        ignored.
        """
        self.backend = backend
        self.ldap = backend.ldap_module()
        self._username = username
        self._user_dn = None
        self._user_attrs = None
        self._user = None
        self._groups = None
        self._group_permissions = None
        self._connection = None
        self._connection_bound = False  # True if we're bound as AUTH_LDAP_BIND_*
        
        if user is not None:
            self._set_authenticated_user(user)
        
        if username is None and user is None:
            raise Exception("Internal error: _LDAPUser improperly initialized.")

    def __deepcopy__(self, memo):
        obj = object.__new__(self.__class__)
        obj.backend = self.backend
        obj.ldap = self.ldap
        obj._user = copy.deepcopy(self._user, memo)

        # This is all just cached immutable data. There's no point copying it.
        obj._username = self._username
        obj._user_dn = self._user_dn
        obj._user_attrs = self._user_attrs
        obj._groups = self._groups
        obj._group_permissions = self._group_permissions
        
        # The connection couldn't be copied even if we wanted to
        obj._connection = self._connection
        obj._connection_bound = self._connection_bound

        return obj

    def _set_authenticated_user(self, user):
        self._user = user
        self._username = self.backend.django_to_ldap_username(user.username)

        user.ldap_user = self
        user.ldap_username = self._username
    
    #
    # Entry points
    #
    
    def authenticate(self, password):
        """
        Authenticates against the LDAP directory and returns the corresponding
        User object if successful. Returns None on failure.
        """
        user = None
        
        try:
            self._authenticate_user_dn(password)
            self._check_requirements()
            self._get_or_create_user()

            user = self._user
        except self.AuthenticationFailed, e:
            logger.debug(u"Authentication failed for %s" % self._username)
        except self.ldap.LDAPError, e:
            logger.warning(u"Caught LDAPError while authenticating %s: %s",
                self._username, pprint.pformat(e))
        except Exception, e:
            logger.error(u"Caught Exception while authenticating %s: %s",
                self._username, pprint.pformat(e))
            logger.error(''.join(traceback.format_tb(sys.exc_info()[2])))
            raise

        return user

    def get_group_permissions(self):
        """
        If allowed by the configuration, this returns the set of permissions
        defined by the user's LDAP group memberships.
        """
        if self._group_permissions is None:
            self._group_permissions = set()

            if ldap_settings.AUTH_LDAP_FIND_GROUP_PERMS:
                try:
                    self._load_group_permissions()
                except self.ldap.LDAPError, e:
                    logger.warning("Caught LDAPError loading group permissions: %s",
                        pprint.pformat(e))
        
        return self._group_permissions

    def populate_user(self):
        """
        Populates the Django user object using the default bind credentials.
        """
        user = None
        
        try:
            self._get_or_create_user(force_populate=True)
            
            user = self._user
        except self.ldap.LDAPError, e:
            logger.warning(u"Caught LDAPError while authenticating %s: %s",
                self._username, pprint.pformat(e))
        except Exception, e:
            logger.error(u"Caught Exception while authenticating %s: %s",
                self._username, pprint.pformat(e))
            logger.error(''.join(traceback.format_tb(sys.exc_info()[2])))
            raise
        
        return user

    #
    # Public properties (callbacks). These are all lazy for performance reasons.
    #

    def _get_user_dn(self):
        if self._user_dn is None:
            self._load_user_dn()

        return self._user_dn
    dn = property(_get_user_dn)

    def _get_user_attrs(self):
        if self._user_attrs is None:
            self._load_user_attrs()
        
        return self._user_attrs
    attrs = property(_get_user_attrs)

    def _get_bound_connection(self):
        if not self._connection_bound:
            self._bind()
        
        return self._get_connection()
    connection = property(_get_bound_connection)

    #
    # Authentication
    #

    def _authenticate_user_dn(self, password):
        """
        Binds to the LDAP server with the user's DN and password. Raises
        AuthenticationFailed on failure.
        """
        if self.dn is None:
            raise self.AuthenticationFailed("Failed to map the username to a DN.")

        try:
            self._bind_as(self.dn, password)
        except self.ldap.INVALID_CREDENTIALS:
            raise self.AuthenticationFailed("User DN/password rejected by LDAP server.")
    
    def _load_user_attrs(self):
        if self.dn is not None:
            search = LDAPSearch(self.dn, self.ldap.SCOPE_BASE)
            results = search.execute(self.connection)

            if results is not None and len(results) > 0:
                self._user_attrs = results[0][1]
    
    def _load_user_dn(self):
        """
        Populates self._user_dn with the distinguished name of our user. This
        will either construct the DN from a template in
        AUTH_LDAP_USER_DN_TEMPLATE or connect to the server and search for it.
        """
        if self._using_simple_bind_mode():
            self._construct_simple_user_dn()
        else:
            self._search_for_user_dn()

    def _using_simple_bind_mode(self):
        return (ldap_settings.AUTH_LDAP_USER_DN_TEMPLATE is not None)

    def _construct_simple_user_dn(self):
        template = ldap_settings.AUTH_LDAP_USER_DN_TEMPLATE
        username = self.ldap.dn.escape_dn_chars(self._username)
        
        self._user_dn = template % {'user': username}

    def _search_for_user_dn(self):
        """
        Searches the directory for a user matching AUTH_LDAP_USER_SEARCH.
        Populates self._user_dn and self._user_attrs.
        """
        search = ldap_settings.AUTH_LDAP_USER_SEARCH
        if search is None:
            raise ImproperlyConfigured('AUTH_LDAP_USER_SEARCH must be an LDAPSearch instance.')
        
        results = search.execute(self.connection, {'user': self._username})
        if results is not None and len(results) == 1:
            (self._user_dn, self._user_attrs) = results[0]

    def _check_requirements(self):
        """
        Checks all authentication requirements beyond credentials. Raises
        AuthenticationFailed on failure.
        """
        self._check_required_group()
    
    def _check_required_group(self):
        """
        Returns True if the group requirement (AUTH_LDAP_REQUIRE_GROUP) is
        met. Always returns True if AUTH_LDAP_REQUIRE_GROUP is None.
        """
        required_group_dn = ldap_settings.AUTH_LDAP_REQUIRE_GROUP
        
        if required_group_dn is not None:
            is_member = self._get_groups().is_member_of(required_group_dn)
            if not is_member:
                raise self.AuthenticationFailed("User is not a member of AUTH_LDAP_REQUIRE_GROUP")

    #
    # User management
    #

    def _get_or_create_user(self, force_populate=False):
        """
        Loads the User model object from the database or creates it if it
        doesn't exist. Also populates the fields, subject to
        AUTH_LDAP_ALWAYS_UPDATE_USER.
        """
        save_user = False
        
        username = self.backend.ldap_to_django_username(self._username)

        (self._user, created) = self.backend.get_or_create_user(username, self)

        if created:
            logger.debug("Created Django user %s", username)
            self._user.set_unusable_password()
            save_user = True

        if(force_populate or ldap_settings.AUTH_LDAP_ALWAYS_UPDATE_USER or created):
            logger.debug("Populating Django user %s", username)
            self._populate_user()
            self._populate_and_save_user_profile()
            save_user = True

        if ldap_settings.AUTH_LDAP_MIRROR_GROUPS:
            self._mirror_groups()

        if save_user:
            self._user.save()

        self._user.ldap_user = self
        self._user.ldap_username = self._username

    def _populate_user(self):
        """
        Populates our User object with information from the LDAP directory.
        """
        self._populate_user_from_attributes()
        self._populate_user_from_group_memberships()
    
    def _populate_user_from_attributes(self):
        for field, attr in ldap_settings.AUTH_LDAP_USER_ATTR_MAP.iteritems():
            try:
                setattr(self._user, field, self.attrs[attr][0])
            except (KeyError, IndexError):
                pass
    
    def _populate_user_from_group_memberships(self):
        for field, group_dn in ldap_settings.AUTH_LDAP_USER_FLAGS_BY_GROUP.iteritems():
            value = self._get_groups().is_member_of(group_dn)
            setattr(self._user, field, value)

    def _populate_and_save_user_profile(self):
        """
        Populates a User profile object with fields from the LDAP directory.
        """
        try:
            profile = self._user.get_profile()

            for field, attr in ldap_settings.AUTH_LDAP_PROFILE_ATTR_MAP.iteritems():
                try:
                    # user_attrs is a hash of lists of attribute values
                    setattr(profile, field, self.attrs[attr][0])
                except (KeyError, IndexError):
                    pass

            if len(ldap_settings.AUTH_LDAP_PROFILE_ATTR_MAP) > 0:
                profile.save()
        except (SiteProfileNotAvailable, ObjectDoesNotExist):
            pass
    
    def _mirror_groups(self):
        """
        Mirrors the user's LDAP groups in the Django database and updates the
        user's membership.
        """
        group_names = self._get_groups().get_group_names()
        groups = [Group.objects.get_or_create(name=group_name)[0] for group_name
            in group_names]
        
        self._user.groups = groups
    
    #
    # Group information
    #
    
    def _load_group_permissions(self):
        """
        Populates self._group_permissions based on LDAP group membership and
        Django group permissions.
        
        The SQL is lifted from ModelBackend, with modifications.
        """
        group_names = self._get_groups().get_group_names()
        placeholders = ', '.join(['%s'] * len(group_names))
        
        cursor = django.db.connection.cursor()
        # The SQL below works out to the following, after DB quoting:
        # cursor.execute("""
        #     SELECT ct."app_label", p."codename"
        #     FROM "auth_permission" p, "auth_group_permissions" gp, "auth_group" g, "django_content_type" ct
        #     WHERE p."id" = gp."permission_id"
        #         AND gp."group_id" = g."id"
        #         AND ct."id" = p."content_type_id"
        #         AND g."name" IN (%s, %s, ...)""", ['group1', 'group2', ...])
        qn = django.db.connection.ops.quote_name
        sql = u"""
            SELECT ct.%s, p.%s
            FROM %s p, %s gp, %s g, %s ct
            WHERE p.%s = gp.%s
                AND gp.%s = g.%s
                AND ct.%s = p.%s
                AND g.%s IN (%s)""" % (
            qn('app_label'), qn('codename'),
            qn('auth_permission'), qn('auth_group_permissions'),
            qn('auth_group'), qn('django_content_type'),
            qn('id'), qn('permission_id'),
            qn('group_id'), qn('id'),
            qn('id'), qn('content_type_id'),
            qn('name'), placeholders)
        
        cursor.execute(sql, group_names)
        self._group_permissions = \
            set([u"%s.%s" % (row[0], row[1]) for row in cursor.fetchall()])

    def _get_groups(self):
        """
        Returns an _LDAPUserGroups object, which can determine group
        membership.
        """
        if self._groups is None:
            self._groups = _LDAPUserGroups(self)
        
        return self._groups

    #
    # LDAP connection
    #

    def _bind(self):
        """
        Binds to the LDAP server with AUTH_LDAP_BIND_DN and
        AUTH_LDAP_BIND_PASSWORD.
        """
        self._bind_as(ldap_settings.AUTH_LDAP_BIND_DN,
            ldap_settings.AUTH_LDAP_BIND_PASSWORD)

        self._connection_bound = True

    def _bind_as(self, bind_dn, bind_password):
        """
        Binds to the LDAP server with the given credentials. This does not trap
        exceptions.

        If successful, we set self._connection_bound to False under the
        assumption that we're not binding as the default user. Callers can set
        it to True as appropriate.
        """
        self._get_connection().simple_bind_s(bind_dn.encode('utf-8'),
            bind_password.encode('utf-8'))

        self._connection_bound = False

    def _get_connection(self):
        """
        Returns our cached LDAPObject, which may or may not be bound.
        """
        if self._connection is None:
            self._connection = self.ldap.initialize(ldap_settings.AUTH_LDAP_SERVER_URI)
            
            for opt, value in ldap_settings.AUTH_LDAP_CONNECTION_OPTIONS.iteritems():
                self._connection.set_option(opt, value)

            if ldap_settings.AUTH_LDAP_START_TLS:
                logger.debug("Initiating TLS")
                self._connection.start_tls_s()

        return self._connection



class _LDAPUserGroups(object):
    """
    Represents the set of groups that a user belongs to.
    """
    def __init__(self, ldap_user):
        self._ldap_user = ldap_user
        self._group_type = None
        self._group_search = None
        self._group_infos = None
        self._group_dns = None
        self._group_names = None
        
        self._init_group_settings()
    
    def _init_group_settings(self):
        """
        Loads the settings we need to deal with groups. Raises
        ImproperlyConfigured if anything's not right.
        """
        self._group_type = ldap_settings.AUTH_LDAP_GROUP_TYPE
        if self._group_type is None:
            raise ImproperlyConfigured("AUTH_LDAP_GROUP_TYPE must be an LDAPGroupType instance.")
        
        self._group_search = ldap_settings.AUTH_LDAP_GROUP_SEARCH
        if self._group_search is None:
            raise ImproperlyConfigured("AUTH_LDAP_GROUP_SEARCH must be an LDAPSearch instance.")
    
    def get_group_names(self):
        """
        Returns the list of Django group names that this user belongs to by
        virtue of LDAP group memberships.
        """
        if self._group_names is None:
            self._load_cached_attr("_group_names")
        
        if self._group_names is None:
            group_infos = self._get_group_infos()
            self._group_names = [self._group_type.group_name_from_info(group_info)
                for group_info in group_infos]
            self._cache_attr("_group_names")
        
        return self._group_names
    
    def is_member_of(self, group_dn):
        """
        Returns true if our user is a member of the given group.
        """
        is_member = None
        
        # If we have self._group_dns, we'll use it. Otherwise, we'll try to
        # avoid the cost of loading it.
        if self._group_dns is None:
            is_member = self._group_type.is_member(self._ldap_user, group_dn)
        
        if is_member is None:
            is_member = (group_dn in self._get_group_dns())
        
        logger.debug("%s is%sa member of %s", self._ldap_user.dn,
                     is_member and " " or " not ", group_dn)

        return is_member
    
    def _get_group_dns(self):
        """
        Returns a (cached) set of the distinguished names in self._group_infos.
        """
        if self._group_dns is None:
            group_infos = self._get_group_infos()
            self._group_dns = set([group_info[0] for group_info in group_infos])
        
        return self._group_dns
    
    def _get_group_infos(self):
        """
        Returns a (cached) list of group_info structures for the groups that our
        user is a member of.
        """
        if self._group_infos is None:
            self._group_infos = self._group_type.user_groups(self._ldap_user,
                self._group_search)
        
        return self._group_infos

    def _load_cached_attr(self, attr_name):
        if ldap_settings.AUTH_LDAP_CACHE_GROUPS:
            key = self._cache_key(attr_name)
            value = cache.get(key)
            setattr(self, attr_name, value)
    
    def _cache_attr(self, attr_name):
        if ldap_settings.AUTH_LDAP_CACHE_GROUPS:
            key = self._cache_key(attr_name)
            value = getattr(self, attr_name, None)
            cache.set(key, value, ldap_settings.AUTH_LDAP_GROUP_CACHE_TIMEOUT)
    
    def _cache_key(self, attr_name):
        return u'auth_ldap.%s.%s.%s' % (self.__class__.__name__, attr_name, self._ldap_user.dn)


class LDAPSettings(object):
    """
    This is a simple class to take the place of the global settings object. An
    instance will contain all of our settings as attributes, with default values
    if they are not specified by the configuration.
    """
    defaults = {
        'AUTH_LDAP_ALWAYS_UPDATE_USER': True,
        'AUTH_LDAP_AUTHORIZE_ALL_USERS': False,
        'AUTH_LDAP_BIND_DN': '',
        'AUTH_LDAP_BIND_PASSWORD': '',
        'AUTH_LDAP_CACHE_GROUPS': False,
        'AUTH_LDAP_CONNECTION_OPTIONS': {},
        'AUTH_LDAP_FIND_GROUP_PERMS': False,
        'AUTH_LDAP_GLOBAL_OPTIONS': {},
        'AUTH_LDAP_GROUP_CACHE_TIMEOUT': None,
        'AUTH_LDAP_GROUP_SEARCH': None,
        'AUTH_LDAP_GROUP_TYPE': None,
        'AUTH_LDAP_MIRROR_GROUPS': False,
        'AUTH_LDAP_PROFILE_ATTR_MAP': {},
        'AUTH_LDAP_REQUIRE_GROUP': None,
        'AUTH_LDAP_SERVER_URI': 'ldap://localhost',
        'AUTH_LDAP_START_TLS': False,
        'AUTH_LDAP_USER_ATTR_MAP': {},
        'AUTH_LDAP_USER_DN_TEMPLATE': None,
        'AUTH_LDAP_USER_FLAGS_BY_GROUP': {},
        'AUTH_LDAP_USER_SEARCH': None,
    }
    
    def __init__(self):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        from django.conf import settings
        
        for name, default in self.defaults.iteritems():
            value = getattr(settings, name, default)
            setattr(self, name, value)


# Our global settings object
ldap_settings = LDAPSettings()
