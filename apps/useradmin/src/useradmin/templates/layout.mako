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
from desktop import conf
from django.utils.translation import ugettext as _

def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="render_field(field, show_label=True, extra_attrs={})">
  % if not field.is_hidden:
    <% group_class = field.errors and "error" or "" %>
    <div class="control-group ${group_class}" data-original-title="${ field.label }" data-content="${ field.help_text }">
      % if show_label:
        <label class="control-label">${ field.label }
          % if field.help_text:
          <i title="${ field.help_text }" data-rel="tooltip" class="fa fa-question-circle muted"></i>
          % endif
        </label>
      % endif
      <div class="controls">
        <% field.field.widget.attrs.update(extra_attrs) %>
        ${ field | n,unicode }
        % if field.errors:
          <span class="help-inline">${ field.errors | n,unicode }</span>
        % endif
      </div>
    </div>
  %endif
</%def>


<%def name="menubar(section='')">
  <div class="page-header">
    <h1 class="currentApp">
      <a href="/${app_name}">
        <img src="${ static('useradmin/art/icon_useradmin_48.png') }" class="app-icon" />
        ${ _('User Admin') }
      </a>
    </h1>
    <ul class="nav nav-tabs">
      %if user.is_superuser:
        <li class="${is_selected(section, 'users')}"><a href="/useradmin/users">${_('Users')}</a></li>
        <li class="${is_selected(section, 'groups')}"><a href="/useradmin/groups">${_('Groups')}</a></li>
        <li class="${is_selected(section, 'permissions')}"><a href="/useradmin/permissions">${_('Permissions')}</a></li>
        %if conf.USE_DEFAULT_CONFIGURATION.get():
          <li class="${is_selected(section, 'configurations')}"><a href="/useradmin/configurations">${_('Configurations')}</a></li>
        %endif
      %endif
    </ul>
  </div>
</%def>


<%def name="commons()">
  <link href="${ static('useradmin/css/useradmin.css') }" rel="stylesheet">

  <script type="text/javascript">
    $(document).ready(function () {

      $("#filterInput").jHueDelayedInput(function () {
        if (mainDataTable) {
          mainDataTable.fnFilter($("#filterInput").val().toLowerCase());
        }
      });

      $('[data-rel="tooltip"]').tooltip({
        placement: 'right'
      });
    });
  </script>
</%def>
