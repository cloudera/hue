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
from django.template.defaultfilters import date, time
from django.utils.translation import ugettext as _

from desktop.lib.django_util import USERNAME_RE_RULE
from desktop.views import commonheader, commonfooter, antixss
from desktop.auth.backend import is_admin
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />

%if not is_embeddable:
${ commonheader(_('Hue Users'), "useradmin", user, request) | n,unicode }
%endif

${layout.menubar(section='users')}

<div id="usersComponents" class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Users')}</h1>

    <%actionbar:render>
      <%def name="search()">
          <input type="text" class="input-xlarge search-query filter-input" placeholder="${_('Search for name, group, etc...')}">
      </%def>
      <%def name="actions()">
        %if is_admin(user):
            <button class="btn delete-user-btn" title="${_('Delete')}" disabled="disabled"><i class="fa fa-trash-o"></i> ${_('Delete')}</button>
        %endif
      </%def>
      <%def name="creation()">
        %if is_admin(user):
            % if not is_ldap_setup:
              <a href="${ url('useradmin.views.edit_user') }" class="btn"><i class="fa fa-user"></i> ${_('Add user')}</a>
            %endif

            % if is_ldap_setup:
              <a href="${ url('useradmin.views.add_ldap_users') }" class="btn"><i class="fa fa-briefcase"></i> ${_('Add/Sync LDAP user')}</a>
              <a href="javascript:void(0)" class="btn confirmationModal"
                 data-confirmation-url="${ url('useradmin_views_sync_ldap_users_groups') }${ is_embeddable and '?is_embeddable=true' or ''}">
                 <i class="fa fa-refresh"></i> ${_('Sync LDAP users/groups')}
              </a>
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
        <th>${_('Username')}</th>
        <th>${_('First Name')}</th>
        <th>${_('Last Name')}</th>
        <th>${_('E-mail')}</th>
        <th>${_('Groups')}</th>
        <th>${_('Last Login')}</th>
      </tr>
      </thead>
      <tbody>
          % for listed_user in users:
          <tr class="tableRow"
              data-search="${listed_user.username}${listed_user.first_name}${listed_user.last_name}${listed_user.email}${', '.join([group.name for group in listed_user.groups.all()])}">
          %if is_admin(user):
              <td data-row-selector-exclude="true">
                <div class="hue-checkbox userCheck fa" data-row-selector-exclude="true" data-id="${ listed_user.id }"></div>
              </td>
          %endif
          <td>
            %if is_admin(user) or user.username == listed_user.username:
              <strong><a title="${_('Edit %(username)s') % dict(username=listed_user.username)}"
                         href="${ url('useradmin.views.edit_user', username=listed_user.username) }"
                         data-row-selector="true">${listed_user.username}</a></strong>
            %else:
              <strong>${listed_user.username}</strong>
            %endif
          </td>
            <td>${listed_user.first_name}</td>
            <td>${listed_user.last_name}</td>
            <td>${listed_user.email}</td>
            <td>${', '.join([group.name for group in listed_user.groups.all()])}</td>
            <td>${date(listed_user.last_login)} ${time(listed_user.last_login).replace("p.m.","PM").replace("a.m.","AM")}</td>
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
    <form action="${ url('useradmin.views.delete_user') }" method="POST">
      ${ csrf_token(request) | n,unicode }
      % if is_embeddable:
        <input type="hidden" value="true" name="is_embeddable" />
      % endif
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${ _("Are you sure you want to delete the selected user(s)?") }</h2>
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

<script type="text/javascript">

  $(document).ready(function () {
    var $usersComponents = $('#usersComponents');
    $(document).off('click', '#usersComponents .userCheck');

    var viewModel = {
      availableUsers: ko.observableArray(${ users_json | n,antixss }),
      chosenUsers: ko.observableArray([])
    };

    ko.applyBindings(viewModel, $usersComponents[0]);

    var dt = $usersComponents.find('.datatables').dataTable({
      "sPaginationType":"bootstrap",
      "iDisplayLength":100,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "bInfo": false,
      "bFilter": true,
      "aoColumns": [
        %if is_admin(user):
            { "bSortable": false },
        %endif
        null,
        null,
        null,
        null,
        null,
        { "sType": "date" },
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    $usersComponents.find(".filter-input").jHueDelayedInput(function () {
      if (dt) {
        dt.fnFilter($usersComponents.find(".filter-input").val().toLowerCase());
      }
    });

    $usersComponents.find('[data-rel="tooltip"]').tooltip({
      placement: 'right'
    });

    % if is_embeddable:
    $usersComponents.find('.delete-user form').ajaxForm({
      dataType:  'json',
      success: function(data) {
        $usersComponents.find(".delete-user").modal("hide");
        $.jHueNotify.info("${ _('The users were deleted.') }")
        if (data && data.url){
          huePubSub.publish('open.link', data.url);
        }
      },
      error: function(response, status, err) {
        $usersComponents.find(".delete-user").modal("hide");
        if (response.responseJSON && response.responseJSON.message && response.status == 401) {
          $.jHueNotify.error(response.responseJSON.message);
        }
        else {
          $.jHueNotify.error("${ _('An unknown error has occurred while deleting the user. Please try again.') }");
        }
      }
    });
    % endif

    $usersComponents.find(".dataTables_wrapper").css("min-height", "0");
    $usersComponents.find(".dataTables_filter").hide();

    $usersComponents.find(".confirmationModal").click(function () {
      var _this = $(this);
      $.ajax({
        url: _this.data("confirmation-url"),
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-Requested-With", "Hue");
        },
        dataType: "html",
        success: function (data) {
          $usersComponents.find(".sync-ldap").html(data);
          % if is_embeddable:
          $usersComponents.find('.sync-ldap form').ajaxForm({
            dataType:  'json',
            beforeSend: function (xhr) {
              $usersComponents.find('input[type="submit"]').attr('disabled','disabled');
            },
            success: function(data) {
              $usersComponents.find('input[type="submit"]').removeAttr("disabled");
              if (data && data.status == -1) {
                renderUseradminErrors(data.errors);
              }
              else if (data && data.url) {
                $usersComponents.find(".sync-ldap").modal("hide");
                $.jHueNotify.info("${ _('The users and groups were updated correctly.') }");
                huePubSub.publish('open.link', data.url);
              }
            },
            error: function(data) {
              $usersComponents.find('input[type="submit"]').removeAttr("disabled");
              $usersComponents.find(".sync-ldap").modal("hide");
              $.jHueNotify.error(data.responseJSON['message']);
              huePubSub.publish('open.link', data.url);
            }
          });
          % endif
          $usersComponents.find(".sync-ldap").modal("show");
        }
      });
    });

    $usersComponents.find(".select-all").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("fa-check");;
        $usersComponents.find(".userCheck").removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("fa-check");
        $usersComponents.find(".userCheck").addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    $(document).on('click', '#usersComponents .userCheck', function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    function toggleActions() {
      if ($usersComponents.find(".userCheck[checked='checked']").length >= 1) {
        $usersComponents.find(".delete-user-btn").removeAttr("disabled");
      }
      else {
        $usersComponents.find(".delete-user-btn").attr("disabled", "disabled");
      }
    }

    $usersComponents.find(".delete-user-btn").click(function () {
      viewModel.chosenUsers.removeAll();

      $usersComponents.find(".hue-checkbox[checked='checked']").each(function (index) {
        viewModel.chosenUsers.push($(this).data("id"));
      });

      $usersComponents.find(".delete-user").modal("show");
    });

    $usersComponents.find("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${layout.commons()}

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
