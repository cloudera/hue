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

from desktop.auth.backend import is_admin
from desktop.conf import ENABLE_ORGANIZATIONS
from desktop.views import commonheader, commonfooter

from useradmin.models import group_permissions, Group

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />

% if not is_embeddable:
  ${ commonheader(_('Permissions'), "useradmin", user, request) | n,unicode }
% endif
  ${ layout.menubar(section='permissions') }

<div id="permissionsComponents" class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">
      ${_('Permissions')}
      % if ENABLE_ORGANIZATIONS.get():
        @ ${ user.organization }
      % endif
    </h1>

    <%actionbar:render>
      <%def name="search()">
          <input type="text" class="input-xlarge search-query filter-input" placeholder="${_('Search for application, group, etc...')}">
      </%def>
    </%actionbar:render>

    <table class="table table-condensed datatables">
      <thead>
      <tr>
        <th>${_('Application')}</th>
        <th>${_('Permission')}</th>
        <th>${_('Groups')}</th>
      </tr>
      </thead>
      <tbody>
          % for perm in permissions:
          <tr class="tableRow"
              data-search="${perm.app}${perm.description}${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}">
            <td>
              % if is_admin(user):
                <strong>
                  <a title="${ _('Edit permission') }"
                      href="${ url('useradmin:useradmin.views.edit_permission', app=perm.app, priv=perm.action) }"
                      data-name="${ perm.app }" data-row-selector="true">${ perm.app }
                  </a>
                </strong>
              % else:
                <strong>${ perm.app }</strong>
              % endif
            </td>
            <td>${ perm.description }</td>
            <td>${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')]) }</td>
          </tr>
          % endfor
      </tbody>
      <tfoot class="hide">
      <tr>
        <td colspan="3">
          <div class="alert">
            ${_('There are no permissions matching the search criteria.')}
          </div>
        </td>
      </tr>
      </tfoot>
    </table>
  </div>
</div>

<script src="${ static('desktop/js/permissions-inline.js') }" type="text/javascript"></script>

${layout.commons()}

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
