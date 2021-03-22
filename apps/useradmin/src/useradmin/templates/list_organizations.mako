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
from desktop.views import commonheader, commonfooter, antixss

from useradmin.models import group_permissions

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />

% if not is_embeddable:
  ${ commonheader(_('Organizations'), "useradmin", user, request) | n,unicode }
% endif

${ layout.menubar(section='organizations') }

<div id="organizationsComponents" class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">
      ${ _('Organizations') }
    </h1>

    <%actionbar:render>
      <%def name="search()">
          <input type="text" class="input-xlarge search-query filter-input" placeholder="${_('Search for name, members, etc...')}">
      </%def>
      <%def name="actions()">
        % if is_admin(user):
          <button class="btn delete-group-btn confirmationModal" title="${_('Delete')}" disabled="disabled">
            <i class="fa fa-trash-o"></i> ${_('Delete')}
          </button>
        % endif
      </%def>
      <%def name="creation()">
        %if is_admin(user):
          <a id="addGroupBtn" href="${url('useradmin:useradmin.views.edit_group')}" class="btn"><i
              class="fa fa-plus-circle"></i> ${_('Add organization')}</a>
          % if is_ldap_setup:
            <a id="addLdapGroupBtn" href="${url('useradmin:useradmin.views.add_ldap_groups')}" class="btn"><i
                class="fa fa-refresh"></i> ${_('Add/Sync LDAP group')}</a>
          % endif
          <a href="http://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/"
            title="${ _('Learn how to integrate Hue with your company LDAP') }" target="_blank">
            <i class="fa fa-question-circle"></i>
          </a>
        %endif
      </%def>
    </%actionbar:render>

    <table class="table table-condensed datatables">
      <thead>
      <tr>
        %if is_admin(user):
          <th width="1%">
            <div class="select-all hue-checkbox fa"></div>
          </th>
        %endif
        <th>${_('Name')}</th>
        <th>${_('Members')}</th>
        <th>${_('Groups')}</th>
        <th>${_('Permissions')}</th>
      </tr>
      </thead>
      <tbody>
        % for group in groups:
          <tr class="tableRow"
              data-search="${group.name}${ ', '.join([group_user.username for group_user in group.organizationuser_set.all()]) }">
          % if is_admin(user):
            <td data-row-selector-exclude="true">
              <div class="hue-checkbox groupCheck fa" data-name="${ group.name }" data-row-selector-exclude="true"></div>
            </td>
          % endif
          <td>
            <strong>${ group.name }</strong>
          </td>
          <td>${ ', '.join([group_user.username for group_user in group.organizationuser_set.all()]) }</td>
          <td>${ ', '.join([org.name for org in group.organizationgroup_set.all()]) }</td>
          <td>${ ', '.join([perm.connector.name for perm in group.huepermission_set.all()]) }</td>
        </tr>
        % endfor
      </tbody>
      <tfoot class="hide">
      <tr>
        <td colspan="8">
          <div class="alert">
            ${_('There are no groups matching the search criteria.')}
          </div>
        </td>
      </tr>
      </tfoot>
    </table>
  </div>

  <div class="modal hide fade delete-group">
    <form action="${ url('useradmin:useradmin.views.delete_group') }" method="POST">
      ${ csrf_token(request) | n,unicode }
      % if is_embeddable:
        <input type="hidden" value="true" name="is_embeddable" />
      % endif
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_("Are you sure you want to delete the selected group(s)?")}</h2>
      </div>
      <div class="modal-footer">
        <a href="javascript:void(0);" class="btn" data-dismiss="modal">${_('No')}</a>
        <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <div class="hide">
        <select name="group_names" data-bind="options: chosenGroups, selectedOptions: chosenGroups" multiple="true"></select>
      </div>
    </form>
  </div>
</div>


<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">

  $(document).ready(function () {
    var $organizationsComponents = $('#organizationsComponents');
    $(document).off('click', '#organizationsComponents .groupCheck');

    var viewModel = {
      availableGroups: ko.observableArray(${ groups_json | n,antixss }),
      chosenGroups: ko.observableArray([])
    };

    ko.applyBindings(viewModel, $organizationsComponents[0]);

    var dt = $organizationsComponents.find('.datatables').dataTable({
      "sPaginationType":"bootstrap",
      "iDisplayLength":100,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "bInfo": false,
      "bFilter": true,
      "bAutoWidth": false,
      "aoColumns": [
        % if is_admin(user):
            { "bSortable": false },
        % endif
        { "sWidth": "20%" },
        { "sWidth": "20%" },
        { "sWidth": "20%" },
        null
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    % if is_embeddable:
    $organizationsComponents.find('.delete-group form').ajaxForm({
      dataType:  'json',
      success: function(data) {
        $organizationsComponents.find(".delete-group").modal("hide");
        $.jHueNotify.info("${ _('The groups were deleted.') }");
        if (data && data.url){
          huePubSub.publish('open.link', data.url);
        }
      }
    });
    % endif

    $organizationsComponents.find(".filter-input").jHueDelayedInput(function () {
      if (dt) {
        dt.fnFilter($organizationsComponents.find(".filter-input").val().toLowerCase());
      }
    });

    $organizationsComponents.find('[data-rel="tooltip"]').tooltip({
      placement: 'right'
    });

    $organizationsComponents.find(".dataTables_wrapper").css("min-height", "0");
    $organizationsComponents.find(".dataTables_filter").hide();

    $organizationsComponents.find(".select-all").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("fa-check");
        $organizationsComponents.find(".groupCheck").removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("fa-check");
        $organizationsComponents.find(".groupCheck").addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    $(document).on('click', '#organizationsComponents .groupCheck', function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    function toggleActions() {
      if ($organizationsComponents.find(".groupCheck[checked='checked']").length > 0) {
        $organizationsComponents.find(".delete-group-btn").removeAttr("disabled");
      }
      else {
        $organizationsComponents.find(".delete-group-btn").attr("disabled", "disabled");
      }
    }

    $organizationsComponents.find(".delete-group-btn").click(function () {
      viewModel.chosenGroups.removeAll();

      $organizationsComponents.find(".hue-checkbox[checked='checked']").each(function (index) {
        viewModel.chosenGroups.push($(this).data("name").toString()); // needed for numeric group names
      });

      $organizationsComponents.find(".delete-group").modal("show");
    });

    $organizationsComponents.find("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ layout.commons() }

% if not is_embeddable:
  ${ commonfooter(request, messages) | n,unicode }
% endif
