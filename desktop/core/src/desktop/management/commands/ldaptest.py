#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
When Hue is integrated with LDAP users can use their existing credentials
to authenticate and inherit their existing groups transparently. This script
is for testing LDAP setting in hue.ini. It uses [desktop] > [[ldap]] in hue.ini
You can run this script through Hue Service in CM(Cloudera Manager) which has
LDAP Test Command option for the test.

There are two ways to authenticate in Hue:
Search Bind: requires user_filter and user_name_attr properties.
Direct Bind: requires nt_domain and ldap_username_pattern

This script uses HUE libraries and works in HUE setup only.
"""
import ldap
import ldap.filter
import logging
import os
import socket
import sys

from desktop.conf import LDAP
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from useradmin import ldap_access

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOG.addHandler(ch)

ldap_url_msg = """
This is the URL to contact LDAP or AD.
Syntax: ldap://<server>:<port> or ldaps://<server>:<port>.
If port is not specified, 389 will be used for LDAP and 636 for LDAPS.
"""

nt_domain_msg = """
This is only necessary for connecting to AD without search bind authentication.
Enter the FQDN of the domain, for example qa.test.com.
Important:  Only one of Use search bind, NT Domain and LDAP Username Pattern
should ever be used at one time. They are incompatible with each other.
"""
ldap_username_pattern_msg = """
This is only necessary for connecting to LDAP without Search Bind Authentication.
It is used to find the user attempting to login in LDAP based on adding
the username to a predefined DN string. Use <username> to reference the user
that is logging in.  An example is uid=<username>,ou=people,dc=test,dc=com.
Important:  Only one of Use Search Bind, NT Domain and LDAP Username Pattern
should ever be used at one time.  They are incompatible with each other.
"""

ldap_cert_msg = """
This is the path to the certificate to use TLS with LDAP or for LDAPS.
TLS is still over port 389 whereas LDAPS is over port 636.
"""

base_dn_msg = """
This is the base DN to search for users.
Cloudera recommends that you use cn=Users,dc=test,dc=com instead of dc=test,dc=com.
"""

bind_dn_msg = """
This is only necessary if LDAP/AD does not support anonymous binds.
Typically LDAP supports anonymous binds by default and AD does not.
For AD, this should be a DN, cn=Administrator,cn=Users,dc=test,dc=com,
when using Search Bind Authentication and just the username, Administrator, when using NT Domain.
For LDAP, it needs to be a DN, cn=manager,dc=test,dc=com.
"""

bind_password_msg = """
This is the password for the bind user.
"""

user_filter_msg = """
This is the base filter for searching for users.
(Optional) - Leaving this blank will use the default (objectclass=*) that will
allow all LDAP users to log in to Hue. LDAP Sync and Search Bind Authentication
are the only situations where this is used. NT Domain config and LDAP
Username Pattern do not use this. Search Bind Authentication can use
the LDAP Filter to narrow which users are permitted to login based on the filter.
Typically this is set to objectclass=*, however, this may change based on
the environment. For example, some LDAP environments are configured to support
Posix objects for *nix authentication. So the user filter might need to be
objectclass=posixAccount.
"""

user_name_attr_msg = """
This is the attribute in LDAP that contains the username.
(Optional) - Leaving this blank will use the default (sAMAccountName/uid) that
will typically work with Active Directory/LDAP. Typically this is uid for
LDAP and sAMAccountName for Active Directory. When putting attributes in
this value for Active Directory, Cloudera recommends you maintain case sensitivity.
"""

group_filter_msg = """
This is the base filter for searching for groups.
(Optional) - Leaving this blank will use the default (objectclass=*) that
will allow for syncing all groups in LDAP. This is only necessary for LDAP Sync,
it is not used for authentication. Typically this is set to objectclass=*,
however, this may change based on the environment.  For example, some
LDAP environments are configured to support Posix objects
for *nix authentication.  So the group filter might need to be
objectclass=posixGroup.
"""

group_name_attr_msg = """
This is the attribute in ldap that contains the groupname.
(Optional) - Leaving this blank will use the default (Common Name) that will
typically work with Active Directory/LDAP. Typically this is CN for LDAP and AD.
When putting attributes in this value for AD, Cloudera recommends you
maintain case sensitivity.
"""

group_member_attr_msg = """
This is the attribute in the group that contains DNs of all the members.
(Optional) - Leaving this blank will use the default (memberOf/member) that
will typically work with Active Directory/LDAP. Typically this is member
for Active Directory and LDAP.
"""

class Command(BaseCommand):
  def print_ldap_global_settings(self, cfg, is_multi_ldap):
    LOG.info('[desktop]')
    LOG.info('[[ldap]]')
    LOG.info('create_users_on_login=%s' % cfg.CREATE_USERS_ON_LOGIN.get())
    LOG.info('sync_groups_on_login=%s' % cfg.SYNC_GROUPS_ON_LOGIN.get())
    LOG.info('ignore_username_case=%s' % cfg.IGNORE_USERNAME_CASE.get())
    LOG.info('force_username_lowercase=%s' % cfg.FORCE_USERNAME_LOWERCASE.get())
    LOG.info('force_username_uppercase=%s' % cfg.FORCE_USERNAME_UPPERCASE.get())
    LOG.info('subgroups=%s' % cfg.SUBGROUPS.get())
    LOG.info('nested_members_search_depth=%s' % cfg.NESTED_MEMBERS_SEARCH_DEPTH.get())
    if is_multi_ldap:
      LOG.info('[[[ldap_servers]]]')

  def print_ldap_setting(self, cfg, is_multi_ldap):
    if not is_multi_ldap:
      self.print_ldap_global_settings(cfg, is_multi_ldap)
    else:
      LOG.info('[[[[%s]]]]', cfg.prefix.split('.')[3])

    LOG.info('follow_referrals=%s' % cfg.FOLLOW_REFERRALS.get())
    LOG.info('debug=%s' % cfg.DEBUG.get())
    LOG.info('debug_level=%s' % cfg.DEBUG_LEVEL.get())
    LOG.info('trace_level=%s' % cfg.TRACE_LEVEL.get())
    LOG.info('base_dn="%s"' % cfg.BASE_DN.get())
    LOG.info('nt_domain="%s"' % cfg.NT_DOMAIN.get())
    LOG.info('ldap_url="%s"' % cfg.LDAP_URL.get())
    LOG.info('use_start_tls=%s' % cfg.USE_START_TLS.get())
    LOG.info('ldap_cert="%s"' % cfg.LDAP_CERT.get())
    LOG.info('ldap_username_pattern="%s"' % cfg.LDAP_USERNAME_PATTERN.get())
    LOG.info('bind_dn="%s"' % cfg.BIND_DN.get())
    LOG.info('bind_password=*******')
    LOG.info('search_bind_authentication=%s' % cfg.SEARCH_BIND_AUTHENTICATION.get())
    LOG.info('test_ldap_user="%s"' % cfg.TEST_LDAP_USER.get())
    LOG.info('test_ldap_group="%s"' % cfg.TEST_LDAP_GROUP.get())

    if not is_multi_ldap:
      LOG.info('[[[users]]]')
    else:
      LOG.info('[[[[[users]]]]]')

    LOG.info('user_filter="%s"' % cfg.USERS.USER_FILTER.get())
    LOG.info('user_name_attr="%s"' % cfg.USERS.USER_NAME_ATTR.get())

    if not is_multi_ldap:
      LOG.info('[[[groups]]]')
    else:
      LOG.info('[[[[[groups]]]]]')

    LOG.info('group_filter="%s"' % cfg.GROUPS.GROUP_FILTER.get())
    LOG.info('group_name_attr="%s"' % cfg.GROUPS.GROUP_NAME_ATTR.get())
    LOG.info('group_member_attr="%s"' % cfg.GROUPS.GROUP_MEMBER_ATTR.get())
    LOG.info('-----------------------')

  def check_ldap_params(self, ldap_config):
    err_code = 1
    ldap_url = ldap_config.LDAP_URL.get()
    if ldap_url is None:
      LOG.info(_(ldap_url_msg))
      LOG.warn('Could not find LDAP_URL server in hue.ini required for authentication')
      return err_code

    if not ((ldap_url.startswith("ldap") and
          "://" in ldap_url)):
      LOG.info(_(ldap_url_msg))
      LOG.warn("Check your ldap_url=%s" % ldap_url)
      return err_code

    ldap_cert = ldap_config.LDAP_CERT.get()
    if ldap_cert is not None and (not os.path.isfile(ldap_cert)):
      LOG.info(_(ldap_cert_msg))
      LOG.warn("Could not find certificate %s on %s" % (ldap_cert, socket.gethostname()))
      return err_code

    if ldap_cert is not None:
      LOG.info("Setting LDAP TLS option ldap.OPT_X_TLS_CACERTFILE=%s" % ldap_cert)
      LOG.info("Setting LDAP TLS option ldap.OPT_X_TLS_REQUIRE_CERT=ldap.OPT_X_TLS_ALLOW")

    bind_dn = ldap_config.BIND_DN.get()
    if bind_dn is None:
      LOG.info(_(bind_dn_msg))
      LOG.warn("Could not find bind_dn in hue.ini required for authentication")
      return err_code

    if ldap_config.SEARCH_BIND_AUTHENTICATION.get():
      # Search Bind Auth
      user_name_attr = ldap_config.USERS.USER_NAME_ATTR.get()
      user_filter = ldap_config.USERS.USER_FILTER.get()
      bind_password = ldap_config.BIND_PASSWORD.get()
      if user_name_attr=='' or ' ' in user_name_attr:
        LOG.info(_(user_name_attr_msg))
        LOG.warn("Could not find user_name_attr in hue.ini")
        return err_code

      if user_filter=='':
        LOG.info(_(user_filter_msg))
        LOG.warn("Could not find user_filter in hue.ini required for authentication")
        return err_code

      if (not bind_password and not ldap_config.BIND_PASSWORD_SCRIPT.get()):
        LOG.info(_(bind_password_msg))
        LOG.warn("Could not find bind_password in hue.ini, required for authentication")
        return err_code
    else:
      # Direct Bind Auth
      nt_domain = ldap_config.NT_DOMAIN.get()
      if nt_domain is None:
        pattern = ldap_config.LDAP_USERNAME_PATTERN.get()
        if pattern is None:
          LOG.info(_(nt_domain_msg))
          LOG.info(_(ldap_username_pattern_msg))
          LOG.warn('Could not find nt_domain in hue.ini')
          LOG.warn('Could not find ldap_username_pattern in hue.ini, required for authentication')
          return err_code
        else:
          pattern = pattern.replace('<username>', bind_dn)
          LOG.info('nt_domain is none, setting USER_DN_TEMPLATE with %s' % pattern)
      else:
        if ((',' in bind_dn) or ('@' in bind_dn) or ('=' in bind_dn) or (' ' in bind_dn)):
          LOG.info(_(nt_domain_msg))
          LOG.info(_(ldap_username_pattern_msg))
          LOG.warn('bind_dn value contains , or @ or = or " " character which is not allowed')
          return err_code
        # %(user)s is a special string that will get replaced during the authentication process
        LOG.info('Setting USER_DN_TEMPLATE as %s@%s' % (bind_dn, nt_domain))

    return 0

  def find_ldapusers(self, ldap_config, ldap_obj):
    err_code = 0
    test_ldap_user = ldap_config.TEST_LDAP_USER.get()
    if '*' in test_ldap_user:
      LOG.warn('Setting test_ldap_user as %s' % test_ldap_user)
      LOG.warn('This operation can overwhelm the server')
      LOG.warn('Chances are server may or may not respond')
      LOG.warn('If you want to test your LDAP Settings please use specific username')

    try:
      users = ldap_obj.find_users(test_ldap_user)
    except ldap.NO_SUCH_OBJECT as err:
      LOG.warn(str(err))
      LOG.info(_(base_dn_msg))
      LOG.warn('hints: check base_dn')
      err_code = 1
    except:
      typ, value, traceback = sys.exc_info()
      LOG.warn("%s %s" % (typ, value))
      LOG.info(_(base_dn_msg))
      LOG.warn('hints: check base_dn')
      err_code = 1

    # print ldapsearch command for debugging purpose
    if err_code:
      LOG.warn(ldap_obj.ldapsearch_cmd())
      return err_code
    else:
      LOG.info(ldap_obj.ldapsearch_cmd())

    if users:
      for user in users:
        LOG.info('%s' % user)
        if user.get('username', '')=='':
          LOG.info(_(user_name_attr_msg))
          LOG.warn('hints: check user_name_attr="%s"' % ldap_config.USERS.USER_NAME_ATTR.get())
          err_code = 1
    else:
      LOG.warn('test_ldap_user %s may not exist' % test_ldap_user)
      LOG.info(_(user_filter_msg))
      LOG.info(_(user_name_attr_msg))
      LOG.warn('hints: check user_filter="%s"' % ldap_config.USERS.USER_FILTER.get())
      LOG.warn('hints: check user_name_attr="%s"' % ldap_config.USERS.USER_NAME_ATTR.get())
      err_code = 1

    return err_code

  def find_ldapgroups(self, ldap_config, ldap_obj):
    err_code = 0
    test_ldap_group = ldap_config.TEST_LDAP_GROUP.get()
    if '*' in test_ldap_group:
      LOG.warn("Setting test_ldap_group as %s" % test_ldap_group)
      LOG.warn("This operation can overwhelm the server")
      LOG.warn("Chances are server may or may not respond")
      LOG.warn("If you want to test your LDAP Settings please use specific groupname")

    try:
      groups = ldap_obj.find_groups(test_ldap_group)
    except ldap.NO_SUCH_OBJECT as err:
      LOG.warn(str(err))
      LOG.info(_(base_dn_msg))
      LOG.warn("hints: check base_dn")
      err_code = 1
    except:
      typ, value, traceback = sys.exc_info()
      LOG.warn("%s %s" % (typ, value))
      LOG.info(_(base_dn_msg))
      LOG.warn("hints: check base_dn")
      err_code = 1

    if err_code:
      LOG.warn(ldap_obj.ldapsearch_cmd())
      return err_code
    else:
     LOG.info(ldap_obj.ldapsearch_cmd())

    if groups:
      for grp in groups:
        LOG.info("%s" % grp)
    else:
      LOG.warn("test_ldap_group %s may not exist" % test_ldap_group)
      LOG.info(_(group_filter_msg))
      LOG.info(_(group_name_attr_msg))
      LOG.warn("hints: check group_filter=\"%s\"" % ldap_config.GROUPS.GROUP_FILTER.get())
      LOG.warn("hints: check group_name_attr=\"%s\"" % ldap_config.GROUPS.GROUP_NAME_ATTR.get())
      err_code = 1

    return err_code

  def find_users_of_group(self, ldap_config, ldap_obj):
    err_code = 0
    test_ldap_group = ldap_config.TEST_LDAP_GROUP.get()

    try:
      groups = ldap_obj.find_users_of_group(test_ldap_group)
    except ldap.NO_SUCH_OBJECT as err:
      LOG.warn(str(err))
      LOG.info(_(base_dn_msg))
      LOG.warn('hints: check base_dn')
      err_code = 1
    except:
      typ, value, traceback = sys.exc_info()
      LOG.warn("%s %s" % (typ, value))
      LOG.info(_(base_dn_msg))
      LOG.warn('hints: check base_dn')
      err_code = 1

    # print ldapsearch command for debugging purpose
    if err_code:
      LOG.warn(ldap_obj.ldapsearch_cmd())
      return err_code
    else:
      LOG.info(ldap_obj.ldapsearch_cmd())

    if groups:
      for grp in groups:
        LOG.info('%s' % grp)
        if grp.get('members', [])==[]:
          LOG.info(_(group_member_attr_msg))
          LOG.warn('hints: check group_member_attr="%s"' % ldap_config.GROUPS.GROUP_MEMBER_ATTR.get())
          err_code = 1
    else:
      LOG.warn('find_users_of_group %s may not exist' % test_ldap_group)
      LOG.info(_(group_filter_msg))
      LOG.info(_(group_name_attr_msg))
      LOG.warn('hints: check group_filter="%s"' % ldap_config.GROUPS.GROUP_FILTER.get())
      LOG.warn('hints: check group_name_attr="%s"' % ldap_config.GROUPS.GROUP_NAME_ATTR.get())
      err_code = 1

    return err_code

  def find_groups_of_group(self, ldap_config, ldap_obj):
    err_code = 0
    test_ldap_group = ldap_config.TEST_LDAP_GROUP.get()

    try:
      groups = ldap_obj.find_groups_of_group(test_ldap_group)
    except ldap.NO_SUCH_OBJECT as err:
      LOG.warn(err.args)
      LOG.info(_(base_dn_msg))
      LOG.warn('hints: check base_dn')
      err_code = 1
    except:
      typ, value, traceback = sys.exc_info()
      LOG.warn("%s %s" % (typ, value))
      LOG.info(_(base_dn_msg))
      LOG.warn('hints: check base_dn')
      err_code = 1

    # print ldapsearch command for debugging purpose
    if err_code:
      LOG.warn(ldap_obj.ldapsearch_cmd())
      return err_code
    else:
      LOG.info(ldap_obj.ldapsearch_cmd())

    if groups:
      for grp in groups:
        LOG.info('%s' % grp)
        if grp.get('members',[])==[]:
          LOG.info(_(group_member_attr_msg))
          LOG.warn('hints: check group_member_attr="%s"' % ldap_config.GROUPS.GROUP_MEMBER_ATTR.get())
          err_code = 1
    else:
      LOG.info('find_groups_of_group %s may not exist' % test_ldap_group)

    return err_code

  def sys_exit(self, exit_code):
    if exit_code!=0:
      LOG.warn('LDAP Test Command failed')
    sys.exit(exit_code)

  def handle(self, *args, **options):
    """
      ldap_test management command enters here. Main logic as follows:
      * check ldap parameters from hue.ini file
      * check ldap connection if connection is not successful then provide hints and equivalent
      ldapsearch command for more hints.
      * using successful ldap connection check for the test_ldap_user. If test_ldap_user is not
      specified then assume filter string for all users
      * if test_ldap_group is presented in DN(distinguished name format) then execute
      find users of test_ldap_group and find groups of test_ldap_group
      * if test_ldap_group is not presented in DN format then execute ldap search function
      based on group_filter from hue.ini
    """
    err_code = 0
    connection = None
    ldap_config = None

    if LDAP.LDAP_SERVERS.get():
      self.print_ldap_global_settings(LDAP, True)
      for server in LDAP.LDAP_SERVERS.get():
        ldap_config = LDAP.LDAP_SERVERS.get()[server]
        err_code = self.check_single_ldap_setting(ldap_config, True)
    else:
      ldap_config = LDAP
      err_code = self.check_single_ldap_setting(ldap_config)

    self.sys_exit(err_code)


  def check_single_ldap_setting(self, ldap_config, is_multi_ldap=False):
    self.print_ldap_setting(ldap_config, is_multi_ldap)
    # Basic validation check for hue.ini's ldap parameters [desktop] > [[ldap]]
    err_code = self.check_ldap_params(ldap_config)

    if not err_code:
      # Connect to only one LDAP server given in the hue.ini config
      try:
        connection = ldap_access.get_connection(ldap_config)
      except ldap_access.LdapBindException as err:
        LOG.warn(str(err))
        LOG.info(_(ldap_url_msg))
        LOG.info(_(bind_dn_msg))
        LOG.warn('hints: check bind_dn, bind_password and ldap_url')
        LOG.warn('ldap_url="%s"' % ldap_config.LDAP_URL.get())
        LOG.warn('bind_dn="%s"' % ldap_config.BIND_DN.get())
        err_code = 1
      except:
        typ, value, traceback = sys.exc_info()
        LOG.warn("%s %s" % (typ, value))
        LOG.info(_(ldap_url_msg))
        LOG.info(_(bind_dn_msg))
        LOG.warn('hints: check bind_dn, bind_password and ldap_url')
        LOG.warn('ldap_url="%s"' % ldap_config.LDAP_URL.get())
        LOG.warn('bind_dn="%s"' % ldap_config.BIND_DN.get())
        err_code = 1

      if err_code:
        cfg = ldap_access.get_auth(ldap_config)
        ldapsearch = 'ldapsearch -x -LLL -H {ldap_url} -D "{binddn}" -w "********" -b "" ' \
                     ' -s base'.format(ldap_url=cfg[0], binddn=cfg[1])
        LOG.warn(ldapsearch)
        self.sys_exit(err_code)

      LOG.info('LDAP whoami_s() %s' % (connection.ldap_handle.whoami_s()))
      if ldap_config.TEST_LDAP_USER.get() is not None:
        err_code = self.find_ldapusers(ldap_config, connection)
        if err_code:
          self.sys_exit(err_code)

        if ldap_config.TEST_LDAP_GROUP.get() is not None:
          group_dn = None
          try:
            group_dn = ldap.explode_dn(ldap_config.TEST_LDAP_GROUP.get())
          except:
            group_dn = None

          if group_dn is not None:
            # group DN
            err_code = self.find_users_of_group(ldap_config, connection)
            if err_code:
              self.sys_exit(err_code)
            err_code = self.find_groups_of_group(ldap_config, connection)
            if err_code:
              self.sys_exit(err_code)
          else:
            # group name pattern goes as search attribute
            err_code = self.find_ldapgroups(ldap_config, connection)
            if err_code:
              self.sys_exit(err_code)
        else:
          LOG.info('Now test further by providing test ldap group in CM')
          LOG.info('test_ldap_group=somegroupname')
          LOG.info('test_ldap_group=cn=Administrators,dc=test,dc=com')
      else:
        LOG.info('Now test further by providing test ldap user in CM')
        LOG.info('test_ldap_user=someusername')

    return err_code
