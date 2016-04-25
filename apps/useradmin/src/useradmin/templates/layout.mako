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
    <div class="control-group ${group_class}"
      rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
      % if show_label:
        <label class="control-label">${ field.label }</label>
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
  <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                  <img src="${ static('useradmin/art/icon_useradmin_48.png') }" class="app-icon" />
                  ${ _('User Admin') }
                </a>
              </li>
              %if user.is_superuser:
              <li class="${is_selected(section, 'users')}"><a href="/useradmin/users">${_('Users')}</a></li>
				      <li class="${is_selected(section, 'groups')}"><a href="/useradmin/groups">${_('Groups')}</a></li>
				      <li class="${is_selected(section, 'permissions')}"><a href="/useradmin/permissions">${_('Permissions')}</a></li>
              <li class="${is_selected(section, 'configurations')}"><a href="/useradmin/configurations">${_('Configurations')}</a></li>
              %endif
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>


<%def name="commons()">
  <link href="${ static('useradmin/css/useradmin.css') }" rel="stylesheet">

  <script type="text/javascript">
    $(document).ready(function () {
      $("#filterInput").keyup(function () {
        var shown = 0;
        $(".datatables tfoot").hide();
        $.each($(".tableRow"), function (index, value) {
          if ($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != "") {
            $(value).hide();
          }
          else {
            $(value).show();
            shown++;
          }
        });
        if (shown == 0) {
          $(".datatables tfoot").show();
        }
      });
    });
  </script>
</%def>
