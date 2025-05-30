## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
import sys
from django.template.defaultfilters import date, time

from desktop.auth.backend import is_admin
from desktop.conf import ENABLE_ORGANIZATIONS
from desktop.lib.django_util import USERNAME_RE_RULE
from desktop.views import commonheader, commonfooter, antixss

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />

%if not is_embeddable:
${ commonheader(_('Users'), "useradmin", user, request) | n,unicode }
%endif

${layout.menubar(section='users')}

<div id="usersComponents" class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">
      ${_('Users')}
      % if ENABLE_ORGANIZATIONS.get():
        @ ${ user.organization }
      % endif
    </h1>

    <%actionbar:render>
      <%def name="search()">
        <input type="text" class="input-xlarge search-query filter-input" placeholder="${_('Search for name, group, etc...')}">
      </%def>
      <%def name="actions()">
        % if is_admin(user):
          <button class="btn delete-user-btn" title="${_('Delete')}" disabled="disabled">
            <i class="fa fa-times"></i> ${_('Delete')}
          </button>
        % endif
      </%def>
      <%def name="creation()">
        % if is_admin(user):
          % if is_ldap_setup:
            <a href="${ url('useradmin:useradmin.views.add_ldap_users') }" class="btn">
              <i class="fa fa-plus-circle"></i> ${_('Add/Sync LDAP user')}
            </a>
            <a href="javascript:void(0)" class="btn confirmationModal"
                data-confirmation-url="${ url('useradmin:useradmin_views_sync_ldap_users_groups') }${ is_embeddable and '?is_embeddable=true' or ''}">
                <i class="fa fa-refresh"></i> ${_('Sync LDAP users/groups')}
            </a>
          % else:
            <a href="${ url('useradmin:useradmin.views.edit_user') }" class="btn">
              <i class="fa fa-plus-circle"></i> ${_('Add user')}
            </a>
          % endif

          <a href="https://docs.gethue.com/administrator/administration/user-management/"
            title="${ _('Learn how to integrate Hue with your company LDAP') }" target="_blank">
            <i class="fa fa-question-circle"></i>
          </a>
        % endif
      </%def>
    </%actionbar:render>

    <table class="table table-condensed datatables">
      <thead>
      <tr>
        % if is_admin(user):
          <th width="1%">
            <div class="select-all hue-checkbox fa"></div>
          </th>
        % endif
        <th>${_('Username')}</th>
        <th>${_('First Name')}</th>
        <th>${_('Last Name')}</th>
        <th>${_('E-mail')}</th>
        <th width="5%">${_('Is admin')}</th>
        <th width="5%">${_('Is active')}</th>
        <th>${_('Groups')}</th>
        <th width="15%">${_('Last Login')}</th>
      </tr>
      </thead>
      <tbody>
        % for listed_user in users:
        <tr class="tableRow"
            data-search="${ listed_user.username }${ listed_user.first_name }${ listed_user.last_name }${ listed_user.email }${ ', '.join([group.name for group in listed_user.groups.all()]) }">
          % if is_admin(user):
            <td data-row-selector-exclude="true">
              <div class="hue-checkbox userCheck fa" data-row-selector-exclude="true" data-id="${ listed_user.id }"></div>
            </td>
          % endif
          <td>
            % if is_admin(user) or user.username == listed_user.username:
              <strong>
                <a title="${_('Edit %(username)s') % dict(username=listed_user.username)}"
                    href="${ url('useradmin:useradmin.views.edit_user', username=listed_user.username) }"
                    data-row-selector="true">
                  ${ listed_user.username }
                </a>
              </strong>
            % else:
              <strong>${ listed_user.username }</strong>
            % endif
          </td>
          <td>${ listed_user.first_name }</td>
          <td>${ listed_user.last_name }</td>
          <td>${ listed_user.email }</td>
          <td>
            % if is_admin(listed_user):
              <i class="fa fa-check"></i>
            % endif
          </td>
          <td>
            % if listed_user.is_active:
              <i class="fa fa-check"></i>
            % endif
          </td>
          <td>${ ', '.join([group.name for group in listed_user.groups.all()]) }</td>
          <td>${ date(listed_user.last_login) } ${ time(listed_user.last_login).replace("p.m.","PM").replace("a.m.","AM") }</td>
        </tr>
        % endfor
      </tbody>
      <tfoot class="hide">
      <tr>
        <td colspan="8">
          <div class="alert">
            ${_('There are no users matching the search criteria.')}
          </div>
        </td>
      </tr>
      </tfoot>
    </table>
  </div>

  <div id="syncLdap" class="modal hide fade"></div>

  <div class="modal hide fade delete-user">
    <form action="${ url('useradmin:useradmin.views.delete_user') }" method="POST">
      ${ csrf_token(request) | n,unicode }
      % if is_embeddable:
        <input type="hidden" value="true" name="is_embeddable" />
      % endif
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${ _("Are you sure you want to deactivate the user selection?") }</h2>
      </div>
      <div class="modal-body">
        <div class="controls">
          <input type="checkbox" name="is_delete">
          ${ _('Delete forever the user selection and their data') }
        </div>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
        <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <div class="hide">
        <select name="user_ids" data-bind="options: availableUsers, selectedOptions: chosenUsers" multiple="true"></select>
      </div>
    </form>
  </div>

  <div class="modal hide fade sync-ldap">
  </div>

</div>

<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script type="application/json" id="listUsersOptions">
  ${ options_json | n }
</script>
  
<script src="${ static('desktop/js/listusers-inline.js') }" type="text/javascript"></script>

${ layout.commons() }

% if not is_embeddable:
  ${ commonfooter(request, messages) | n,unicode }
% endif
