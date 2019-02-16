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
from useradmin.models import group_permissions
from desktop.auth.backend import is_admin

from desktop.views import commonheader, commonfooter, antixss
%>


<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />

%if not is_embeddable:
${ commonheader(_('Hue Groups'), "useradmin", user, request) | n,unicode }
%endif

${layout.menubar(section='groups')}

<div id="groupsComponents" class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Groups')}</h1>

    <%actionbar:render>
      <%def name="search()">
          <input type="text" class="input-xlarge search-query filter-input" placeholder="${_('Search for name, members, etc...')}">
      </%def>
      <%def name="actions()">
        %if is_admin(user):
            <button class="btn delete-group-btn confirmationModal" title="${_('Delete')}" disabled="disabled"><i class="fa fa-trash-o"></i> ${_('Delete')}</button>
        %endif
      </%def>
      <%def name="creation()">
        %if is_admin(user):
          <a id="addGroupBtn" href="${url('useradmin.views.edit_group')}" class="btn"><i
              class="fa fa-plus-circle"></i> ${_('Add group')}</a>
          % if is_ldap_setup:
            <a id="addLdapGroupBtn" href="${url('useradmin.views.add_ldap_groups')}" class="btn"><i
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
        <th>${_('Group Name')}</th>
        <th>${_('Members')}</th>
        <th>${_('Permissions')}</th>
      </tr>
      </thead>
      <tbody>
          % for group in groups:
          <tr class="tableRow"
              data-search="${group.name}${', '.join([group_user.username for group_user in group.user_set.all()])}">
          %if is_admin(user):
            <td data-row-selector-exclude="true">
              <div class="hue-checkbox groupCheck fa" data-name="${group.name}" data-row-selector-exclude="true"></div>
            </td>
          %endif
          <td>
            %if is_admin(user):
              <strong><a title="${ _('Edit %(groupname)s') % dict(groupname=group.name) }"
                         href="${ url('useradmin.views.edit_group', name=group.name) }"
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
  <div class="modal hide fade delete-group">
    <form action="${ url('useradmin.views.delete_group') }" method="POST">
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
    var $groupsComponents = $('#groupsComponents');
    $(document).off('click', '#groupsComponents .groupCheck');

    var viewModel = {
      availableGroups: ko.observableArray(${ groups_json | n,antixss }),
      chosenGroups: ko.observableArray([])
    };

    ko.applyBindings(viewModel, $groupsComponents[0]);

    var dt = $groupsComponents.find('.datatables').dataTable({
      "sPaginationType":"bootstrap",
      "iDisplayLength":100,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "bInfo": false,
      "bFilter": true,
      "bAutoWidth": false,
      "aoColumns": [
        %if is_admin(user):
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

    % if is_embeddable:
    $groupsComponents.find('.delete-group form').ajaxForm({
      dataType:  'json',
      success: function(data) {
        $groupsComponents.find(".delete-group").modal("hide");
        $.jHueNotify.info("${ _('The groups were deleted.') }");
        if (data && data.url){
          huePubSub.publish('open.link', data.url);
        }
      }
    });
    % endif

    $groupsComponents.find(".filter-input").jHueDelayedInput(function () {
      if (dt) {
        dt.fnFilter($groupsComponents.find(".filter-input").val().toLowerCase());
      }
    });

    $groupsComponents.find('[data-rel="tooltip"]').tooltip({
      placement: 'right'
    });

    $groupsComponents.find(".dataTables_wrapper").css("min-height", "0");
    $groupsComponents.find(".dataTables_filter").hide();

    $groupsComponents.find(".select-all").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("fa-check");
        $groupsComponents.find(".groupCheck").removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("fa-check");
        $groupsComponents.find(".groupCheck").addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    $(document).on('click', '#groupsComponents .groupCheck', function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    function toggleActions() {
      if ($groupsComponents.find(".groupCheck[checked='checked']").length > 0) {
        $groupsComponents.find(".delete-group-btn").removeAttr("disabled");
      }
      else {
        $groupsComponents.find(".delete-group-btn").attr("disabled", "disabled");
      }
    }

    $groupsComponents.find(".delete-group-btn").click(function () {
      viewModel.chosenGroups.removeAll();

      $groupsComponents.find(".hue-checkbox[checked='checked']").each(function (index) {
        viewModel.chosenGroups.push($(this).data("name").toString()); // needed for numeric group names
      });

      $groupsComponents.find(".delete-group").modal("show");
    });

    $groupsComponents.find("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${layout.commons()}

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
