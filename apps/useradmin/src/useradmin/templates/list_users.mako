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

<%namespace name="layout" file="layout.mako" />
${commonheader(_('Hue Users'), "useradmin", user, "100px")}
${layout.menubar(section='users', _=_)}

<div class="container-fluid">
    <h1>${_('Hue Users')}</h1>
    <div class="subnavContainer">
        <div class="subnav sticky">
            <p class="pull-right">
                <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for username, name, e-mail, etc...')}">
            </p>
            <p style="padding: 4px">
                %if user.is_superuser:
                    <button id="deleteUserBtn" class="btn confirmationModal" title="${_('Delete')}" disabled="disabled"><i class="icon-trash"></i> ${_('Delete')}</button>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                    <a href="${ url('useradmin.views.edit_user') }" class="btn"><i class="icon-user"></i> ${_('Add user')}</a>
                    <a href="${ url('useradmin.views.add_ldap_user') }" class="btn"><i class="icon-briefcase"></i> ${_('Add/Sync LDAP user')}</a>
                    <a href="javascript:void(0)" class="btn confirmationModal" data-confirmation-url="${ url('useradmin.views.sync_ldap_users_groups') }"><i class="icon-refresh"></i> ${_('Sync LDAP users/groups')}</a>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                %endif
            </p>
        </div>
    </div>
    <br/>

    <table class="table table-striped table-condensed datatables">
        <thead>
            <tr>
                %if user.is_superuser:
                    <th width="1%"><input id="selectAll" type="checkbox"/></th>
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
                    <td class="center" data-row-selector-exclude="true">
                        <input type="checkbox" class="userCheck" data-username="${listed_user.username}" data-confirmation-url="${ url('useradmin.views.delete_user', username=urllib.quote(listed_user.username))}" data-row-selector-exclude="true"/>
                    </td>
                %endif
                <td>
                    %if user.is_superuser or user.username == listed_user.username:
                        <h5><a title="${_('Edit %(username)s') % dict(username=listed_user.username)}" href="${ url('useradmin.views.edit_user', username=urllib.quote(listed_user.username)) }" data-row-selector="true">${listed_user.username}</a></h5>
                    %else:
                        <h5>${listed_user.username}</h5>
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

    <div id="deleteUser" class="modal hide fade"></div>

</div>

    <script type="text/javascript" charset="utf-8">
        $(document).ready(function(){
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
                ]
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

            $("#selectAll").change(function(){
                if ($(this).is(":checked")){
                    $(".userCheck").attr("checked", "checked");
                }
                else {
                    $(".userCheck").removeAttr("checked");
                }
                $(".userCheck").change();
            });

            $(".userCheck").change(function(){
                if ($(".userCheck:checked").length == 1){
                    $("#deleteUserBtn").removeAttr("disabled").data("confirmation-url", $(".userCheck:checked").data("confirmation-url"));
                }
                else {
                    $("#deleteUserBtn").attr("disabled", "disabled");
                }
            });

            $("a[data-row-selector='true']").jHueRowSelector();
        });
    </script>

${layout.commons()}

${commonfooter(messages)}
