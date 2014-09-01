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
import urllib

from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
from useradmin.models import group_permissions
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
${ commonheader(_('Hue Groups'), "useradmin", user) | n,unicode }
${layout.menubar(section='groups')}

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Groups')}</h1>

    <%actionbar:render>
      <%def name="search()">
          <input id="filterInput" type="text" class="input-xlarge search-query"
                 placeholder="${_('Search for name, members, etc...')}">
      </%def>
      <%def name="actions()">
        %if user.is_superuser:
            <button id="deleteGroupBtn" class="btn confirmationModal" title="${_('Delete')}" disabled="disabled"><i
                class="fa fa-trash-o"></i> ${_('Delete')}</button>
        %endif
      </%def>
      <%def name="creation()">
        %if user.is_superuser:
          <a id="addGroupBtn" href="${url('useradmin.views.edit_group')}" class="btn"><i
              class="fa fa-plus-circle"></i> ${_('Add group')}</a>
          % if is_ldap_setup:
            <a id="addLdapGroupBtn" href="${url('useradmin.views.add_ldap_groups')}" class="btn"><i
                class="fa fa-refresh"></i> ${_('Add/Sync LDAP group')}</a>
          % endif
          <a href="http://gethue.tumblr.com/post/75499679342/making-hadoop-accessible-to-your-employees-with-ldap" class="btn"
            title="${ ('Learn how to integrate Hue with your company') }" target="_blank">
            <i class="fa fa-question-circle"> LDAP</i>
          </a>
        %endif
      </%def>
    </%actionbar:render>

    <table class="table table-striped table-condensed datatables">
      <thead>
      <tr>
        %if user.is_superuser:
            <th width="1%">
              <div id="selectAll" class="hueCheckbox fa"></div>
            </th>
        %endif
        <th>${_('Group Name')}</th>
        <th>${_('Members')}</th>
        <th>${_('Permissions')}</th>
      </tr>
      </thead>
      <tbody>
          % for group in groups:
          <tr class="tableRow"
              data-search="${group.name}${', '.join([group_user.username for group_user in group.user_set.all()])}">
          %if user.is_superuser:
            <td data-row-selector-exclude="true">
              <div class="hueCheckbox groupCheck fa" data-name="${group.name}" data-row-selector-exclude="true"></div>
            </td>
          %endif
          <td>
            %if user.is_superuser:
              <strong><a title="${ _('Edit %(groupname)s') % dict(groupname=group.name) }"
                         href="${ url('useradmin.views.edit_group', name=urllib.quote(group.name)) }"
                         data-row-selector="true">${group.name}</a></strong>
            %else:
              <strong>${group.name}</strong>
            %endif
          </td>
            <td>${', '.join([group_user.username for group_user in group.user_set.all()])}</td>
            <td>${', '.join([perm.app + "." + perm.action for perm in group_permissions(group)])}</td>
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
</div>

<div id="deleteGroup" class="modal hide fade groupModal">
  <form id="deleteGroupForm" action="${ url('useradmin.views.delete_group') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteGroupMessage">${_("Are you sure you want to delete the selected group(s)?")}</h3>
    </div>
    <div class="modal-footer">
      <a href="javascript:void(0);" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
    </div>
    <div class="hide">
      <select name="group_names" data-bind="options: availableUsers, selectedOptions: chosenUsers" multiple="true"></select>
    </div>
  </form>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  var viewModel;

  $(document).ready(function () {
    viewModel = {
      availableUsers: ko.observableArray(${ groups_json | n }),
      chosenUsers: ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    $(".datatables").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "bAutoWidth": false,
      "aoColumns": [
        %if user.is_superuser:
            { "bSortable": false },
        %endif
        { "sWidth": "20%" },
        { "sWidth": "20%" },
        null
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    $(".dataTables_wrapper").css("min-height", "0");
    $(".dataTables_filter").hide();

    $("#selectAll").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked");
        $(".groupCheck").removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked");
        $(".groupCheck").addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    $(".groupCheck").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    function toggleActions() {
      if ($(".groupCheck[checked='checked']").length > 0) {
        $("#deleteGroupBtn").removeAttr("disabled");
      }
      else {
        $("#deleteGroupBtn").attr("disabled", "disabled");
      }
    }

    $("#deleteGroupBtn").click(function () {
      viewModel.chosenUsers.removeAll();

      $(".hueCheckbox[checked='checked']").each(function (index) {
        viewModel.chosenUsers.push($(this).data("name"));
      });

      $("#deleteGroup").modal("show");
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${layout.commons()}

${ commonfooter(messages) | n,unicode }
