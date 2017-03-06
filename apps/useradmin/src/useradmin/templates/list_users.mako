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
from desktop.views import commonheader, commonfooter, antixss, _ko
from django.template.defaultfilters import date, time
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
${ commonheader(_('Hue Users'), "useradmin", user, request) | n,unicode }
${layout.menubar(section='users')}

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Hue Users')}</h1>

    <%actionbar:render>
      <%def name="search()">
        <input type="text" class="input-xlarge search-query" placeholder="${_('Search for name, group, etc...')}" data-bind="textInput: filter">
      </%def>
      <%def name="actions()">
        <!-- ko if: isSuperUser -->
        <button id="deleteUserBtn" class="btn" title="${_('Delete')}" data-bind="enable: chosenUsers().length > 0"><i class="fa fa-trash-o"></i> ${_('Delete')}</button>
        <!-- /ko -->
      </%def>
      <%def name="creation()">
        <!-- ko if: isSuperUser -->
        % if not is_ldap_setup:
            <a href="${ url('useradmin.views.edit_user') }" class="btn"><i class="fa fa-user"></i> ${_('Add user')}</a>
        %endif

        % if is_ldap_setup:
        <a href="${ url('useradmin.views.add_ldap_users') }" class="btn"><i class="fa fa-briefcase"></i> ${_('Add/Sync LDAP user')}</a>
        <a href="javascript:void(0)" class="btn confirmationModal" data-confirmation-url="${ url('useradmin.views.sync_ldap_users_groups') }"><i class="fa fa-refresh"></i> ${_('Sync LDAP users/groups')}</a>
        % endif

        <a href="http://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/" class="btn" title="${ ('Learn how to integrate Hue with your company') }" target="_blank">
          <i class="fa fa-question-circle"></i> LDAP
        </a>
        <!-- /ko -->
      </%def>
    </%actionbar:render>

    <table class="table table-condensed">
      <thead>
      <tr>
        <!-- ko if: isSuperUser -->
        <th width="1%">
          <div class="hueCheckbox fa fa-fw" data-bind="css: {'fa-check': allSelected, 'fa-minus': someSelected}, click: toggleAll"></div>
        </th>
        <!-- /ko -->
        <th>${_('Username')}</th>
        <th>${_('First Name')}</th>
        <th>${_('Last Name')}</th>
        <th>${_('E-mail')}</th>
        <th>${_('Groups')}</th>
        <th>${_('Last Login')}</th>
      </tr>
      </thead>
      <tbody data-bind="foreach: filteredUsers">
        <tr>
          <!-- ko if: $parent.isSuperUser -->
            <!-- ko if: username() !== '${ user.username }' -->
            <td class="center" data-bind="click: function(){ selected(!selected()) }" style="cursor: default" data-row-selector-exclude="true">
              <div class="hueCheckbox fa" data-bind="css: { 'fa-check': selected }"></div>
            </td>
            <!-- /ko -->
            <!-- ko if: username() === '${ user.username }' -->
            <td class="center" style="cursor: default" data-row-selector-exclude="true">
              <div class="hueCheckbox disabled"></div>
            </td>
            <!-- /ko -->
          <!-- /ko -->
          <td>
            <!-- ko if: $parent.isSuperUser() || username() == '${user.username}' -->
            <strong><a data-bind="text: username, attr: {'title': '${ _ko('Edit user') } ' + username(), 'href': editURL}" data-row-selector="true"></a></strong>
            <!-- /ko -->
            <!-- ko if: !$parent.isSuperUser() && username() != '${user.username}' -->
            <strong data-bind="text: username"></strong>
            <!-- /ko -->
          </td>
          <td data-bind="text: first_name"></td>
          <td data-bind="text: last_name"></td>
          <td data-bind="text: email"></td>
          <td data-bind="text: readableGroups"></td>
          <td data-bind="text: localeFormat(last_login)"></td>
        </tr>
      </tbody>
      <!-- ko if: filteredUsers().length === 0 -->
      <tfoot>
      <tr>
        <td colspan="8">
          <div class="alert">
            ${_('There are no users matching the search criteria.')}
          </div>
        </td>
      </tr>
      </tfoot>
      <!-- /ko -->
    </table>
  </div>

  <div id="syncLdap" class="modal hide fade"></div>

  <div id="deleteUser" class="modal hide fade">
    <form id="dropTableForm" action="${ url('useradmin.views.delete_user') }" method="POST">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>

        <h3 id="deleteUserMessage">${ _("Are you sure you want to delete the selected user(s)?") }</h3>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
        <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <div class="hide">
        <select name="user_ids" data-bind="options: availableUsers().map(function(item){ return item.id() }), selectedOptions: chosenUsers().map(function(item){ return item.id() })" multiple="true"></select>
      </div>
    </form>
  </div>

</div>

<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {

    var ListUsersViewModel = function () {
      var self = this;

      self.filter = ko.observable('').extend({throttle: 500});

      self.isSuperUser = ko.observable(${ user.is_superuser and 'true' or 'false' })
      self.availableUsers = ko.observableArray([]);

      self.filteredUsers = ko.pureComputed(function () {
        return self.availableUsers().filter(function (item) {
          return item.username().toLowerCase().indexOf(self.filter()) > -1 ||
              item.first_name().toLowerCase().indexOf(self.filter()) > -1 ||
              item.last_name().toLowerCase().indexOf(self.filter()) > -1 ||
              item.email().toLowerCase().indexOf(self.filter()) > -1 ||
              item.readableGroups().toLowerCase().indexOf(self.filter()) > -1
        });
      });

      self.chosenUsers = ko.pureComputed(function () {
        return self.filteredUsers().filter(function (item) {
          return item.selected()
        });
      });

      self.toggleAll = function () {
        var selected = self.allSelected();
        ko.utils.arrayForEach(self.filteredUsers(), function (user) {
          if (user.username() !== '${ user.username }') {
            user.selected(!selected);
          }
          else {
            user.selected(false);
          }
        });
      };

      self.allSelected = ko.pureComputed(function () {
        var filtered = self.filteredUsers().filter(function (item) {
          return item.selected()
        });
        return filtered.length > 0 && filtered.length === self.filteredUsers().length - 1
      });

      self.someSelected = ko.pureComputed(function () {
        var filtered = self.filteredUsers().filter(function (item) {
          return item.selected()
        });
        return filtered.length > 0 && filtered.length < self.filteredUsers().length - 1
      });

      self.init = function () {
        $.getJSON('/useradmin/users', function (data) {
          if (data && data.users) {
            var users = [];
            data.users.forEach(function (u) {
              var user = ko.mapping.fromJS(u);
              user.selected = ko.observable(false);
              user.readableGroups = ko.pureComputed(function () {
                return u.groups ? user.groups().map(function (item) {
                      return item.name()
                    }).join(', ') : ''
              });
              users.push(user);
            })
            self.availableUsers(users);
          }
        });
      }
    };

    var viewModel = new ListUsersViewModel();

    viewModel.init();

    ko.applyBindings(viewModel);

    $(".confirmationModal").click(function () {
      var _this = $(this);
      $.ajax({
        url: _this.data("confirmation-url"),
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-Requested-With", "Hue");
        },
        dataType: "html",
        success: function (data) {
          $("#deleteUser").html(data);
          $("#deleteUser").modal("show");
        }
      });
    });

    $("#deleteUserBtn").click(function () {
      $("#deleteUser").modal("show");
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${layout.commons()}

${ commonfooter(request, messages) | n,unicode }
