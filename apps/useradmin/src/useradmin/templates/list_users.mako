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
from desktop.views import commonheader, commonfooter
from django.template.defaultfilters import date, time
import urllib
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
${ commonheader(_('Hue Users'), "useradmin", user, "100px") | n,unicode }
${layout.menubar(section='users', _=_)}

<div class="container-fluid">
    <h1>${_('Hue Users')}</h1>

    <%actionbar:render>
        <%def name="search()">
          <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, group, etc...')}">
        </%def>
        <%def name="actions()">
            %if user.is_superuser:
                <button id="deleteUserBtn" class="btn" title="${_('Delete')}" disabled="disabled"><i class="icon-trash"></i> ${_('Delete')}</button>
            %endif
        </%def>
        <%def name="creation()">
            %if user.is_superuser:
                <a href="${ url('useradmin.views.edit_user') }" class="btn"><i class="icon-user"></i> ${_('Add user')}</a>
                <a href="${ url('useradmin.views.add_ldap_users') }" class="btn"><i class="icon-briefcase"></i> ${_('Add/Sync LDAP user')}</a>
                <a href="javascript:void(0)" class="btn confirmationModal" data-confirmation-url="${ url('useradmin.views.sync_ldap_users_groups') }"><i class="icon-refresh"></i> ${_('Sync LDAP users/groups')}</a>
            %endif
        </%def>
    </%actionbar:render>

    <table class="table table-striped table-condensed datatables">
        <thead>
            <tr>
                %if user.is_superuser:
                    <th width="1%"><div id="selectAll" class="hueCheckbox"></div></th>
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
            <tr class="tableRow" data-search="${listed_user.username}${listed_user.first_name}${listed_user.last_name}${listed_user.email}${', '.join([group.name for group in listed_user.groups.all()])}">
                %if user.is_superuser:
                    <td data-row-selector-exclude="true">
                        <div class="hueCheckbox userCheck" data-row-selector-exclude="true" data-id="${ listed_user.id }"></div>
                    </td>
                %endif
                <td>
                    %if user.is_superuser or user.username == listed_user.username:
                        <strong><a title="${_('Edit %(username)s') % dict(username=listed_user.username)}" href="${ url('useradmin.views.edit_user', username=urllib.quote(listed_user.username)) }" data-row-selector="true">${listed_user.username}</a></strong>
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

    <div id="syncLdap" class="modal hide fade"></div>

    <div id="deleteUser" class="modal hide fade">
        <form id="dropTableForm" action="${ url('useradmin.views.delete_user') }" method="POST">
            <div class="modal-header">
                <a href="#" class="close" data-dismiss="modal">&times;</a>
                <h3 id="deleteUserMessage">${ _("Are you sure you want to delete the selected user(s)?") }</h3>
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

</div>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
        availableUsers : ko.observableArray(${ users_json | n }),
        chosenUsers : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    $(".datatables").dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bFilter": false,
        "aoColumns": [
            %if user.is_superuser:
            { "bSortable": false },
            %endif
            null,
            null,
            null,
            null,
            null,
            { "sType": "date" }
        ],
        "oLanguage": {
            "sEmptyTable": "${_('No data available')}",
            "sZeroRecords": "${_('No matching records')}",
        }
    });

    $(".dataTables_wrapper").css("min-height","0");
    $(".dataTables_filter").hide();

    $(".confirmationModal").click(function(){
        var _this = $(this);
        $.ajax({
            url: _this.data("confirmation-url"),
            beforeSend: function(xhr){
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function(data){
                $("#deleteUser").html(data);
                $("#deleteUser").modal("show");
            }
        });
    });

    $("#selectAll").click(function(){
        if ($(this).attr("checked")) {
            $(this).removeAttr("checked");
            $(".userCheck").removeClass("icon-ok").removeAttr("checked");
        }
        else {
            $(this).attr("checked", "checked");
            $(".userCheck").addClass("icon-ok").attr("checked", "checked");
        }
        toggleActions();
    });

    $(".userCheck").click(function(){
        if ($(this).attr("checked")) {
            $(this).removeClass("icon-ok").removeAttr("checked");
        }
        else {
            $(this).addClass("icon-ok").attr("checked", "checked");
        }
        toggleActions();
    });

    function toggleActions() {
        if ($(".userCheck[checked='checked']").length >= 1) {
            $("#deleteUserBtn").removeAttr("disabled");
        }
        else {
            $("#deleteUserBtn").attr("disabled", "disabled");
        }
    }

    $("#deleteUserBtn").click(function () {
        viewModel.chosenUsers.removeAll();

        $(".hueCheckbox[checked='checked']").each(function( index ) {
            viewModel.chosenUsers.push($(this).data("id"));
        });

        $("#deleteUser").modal("show");
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${layout.commons()}

${ commonfooter(messages) | n,unicode }
