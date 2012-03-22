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
This module provides access to LDAP servers, along with some basic functionality required for Hue and
User Admin to work seamlessly with LDAP.
"""
import desktop.conf
import ldap
import ldap.filter

import logging
LOG = logging.getLogger(__name__)

CACHED_LDAP_CONN = None

def get_connection():
  global CACHED_LDAP_CONN
  if CACHED_LDAP_CONN is not None:
    return CACHED_LDAP_CONN

  ldap_url = desktop.conf.LDAP.LDAP_URL.get()
  nt_domain = desktop.conf.LDAP.NT_DOMAIN.get()
  username = desktop.conf.LDAP.BIND_DN.get()
  password = desktop.conf.LDAP.BIND_PASSWORD.get()
  ldap_cert = desktop.conf.LDAP.LDAP_CERT.get()

  return LdapConnection(ldap_url, get_ldap_username(username, nt_domain),
                        password, ldap_cert)

def get_ldap_username(username, nt_domain):
  if nt_domain:
    return '%s@%s' % (username, nt_domain)
  else:
    return username

class LdapConnection(object):
  """
  Constructor creates LDAP connection. Contains methods
  to easily query an LDAP server.
  """

  def __init__(self, ldap_url, bind_user=None, bind_password=None, cert_file=None):
    """
    Constructor initializes the LDAP connection
    """
    if cert_file is not None:
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
      ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, cert_file)

    ldap.set_option(ldap.OPT_REFERRALS, 0)

    self.ldap_handle = ldap.initialize(ldap_url)

    if bind_user is not None:
      try:
        self.ldap_handle.simple_bind_s(bind_user, bind_password)
      except:
        raise RuntimeError("Failed to bind to LDAP server as user %s" %
            (bind_user,))
    else:
      try:
        # Do anonymous bind
        self.ldap_handle.simple_bind_s('','')
      except:
        raise RuntimeError("Failed to bind to LDAP server anonymously")

  def find_user(self, username, find_by_dn=False):
    """
    LDAP search helper method finding users. This supports searching for users
    by distinguished name, or the configured username attribute.
    """
    base_dn = self._get_root_dn()
    scope = ldap.SCOPE_SUBTREE

    user_filter = desktop.conf.LDAP.USERS.USER_FILTER.get()
    if not user_filter.startswith('('):
      user_filter = '(' + user_filter + ')'
    user_name_attr = desktop.conf.LDAP.USERS.USER_NAME_ATTR.get()

    if find_by_dn:
      sanitized_name = ldap.filter.escape_filter_chars(username)
      user_name_filter = '(distinguishedName=' + sanitized_name + ')'
    else:
      sanitized_name = ldap.filter.escape_filter_chars(username)
      user_name_filter = '(' + user_name_attr + '=' + sanitized_name + ')'
    ldap_filter = '(&' + user_filter + user_name_filter + ')'

    ldap_result_id = self.ldap_handle.search(base_dn, scope, ldap_filter)
    result_type, result_data = self.ldap_handle.result(ldap_result_id)
    if result_type == ldap.RES_SEARCH_RESULT and result_data[0][0] is not None:
      data = result_data[0][1]
      user_info = { 'username': data[user_name_attr][0] }

      if 'givenName' in data:
        user_info['first'] = data['givenName'][0]
      if 'sn' in data:
        user_info['last'] = data['sn'][0]
      if 'mail' in data:
        user_info['email'] = data['mail'][0]

      return user_info

    return None

  def find_group(self, groupname, find_by_dn=False):
    """
    LDAP search helper method for finding groups
    """
    base_dn = self._get_root_dn()
    scope = ldap.SCOPE_SUBTREE

    group_filter = desktop.conf.LDAP.GROUPS.GROUP_FILTER.get()
    if not group_filter.startswith('('):
      group_filter = '(' + group_filter + ')'
    group_name_attr = desktop.conf.LDAP.GROUPS.GROUP_NAME_ATTR.get()

    if find_by_dn:
      sanitized_name = ldap.filter.escape_filter_chars(groupname)
      group_name_filter = '(distinguishedName=' + sanitized_name + ')'
    else:
      sanitized_name = ldap.filter.escape_filter_chars(groupname)
      group_name_filter = '(' + group_name_attr + '=' + sanitized_name + ')'
    ldap_filter = '(&' + group_filter + group_name_filter + ')'

    ldap_result_id = self.ldap_handle.search(base_dn, scope, ldap_filter)
    result_type, result_data = self.ldap_handle.result(ldap_result_id)
    if result_type == ldap.RES_SEARCH_RESULT and result_data[0][0] is not None:
      data = result_data[0][1]
      group_info = { 'name': data[group_name_attr][0] }

      member_attr = desktop.conf.LDAP.GROUPS.GROUP_MEMBER_ATTR.get()
      if member_attr in data:
        group_info['members'] = data[member_attr]
      else:
        group_info['members'] = []

      return group_info

    return None

  def _get_root_dn(self):
    """
    Returns the configured base DN (DC=desktop,DC=local).
    """
    return desktop.conf.LDAP.BASE_DN.get()
