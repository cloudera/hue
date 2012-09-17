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
import urllib
from django.utils.translation import ugettext as _
from useradmin.models import group_permissions
%>

<%namespace name="layout" file="layout.mako" />
${commonheader(_('Hue Groups'), "useradmin", user, "100px")}
${layout.menubar(section='groups', _=_)}

<div class="container-fluid">
    <h1>${_('Hue Groups')}</h1>
    <div class="subnavContainer">
        <div class="subnav sticky">
            <p class="pull-right">
                <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for group name, members, etc...')}">
            </p>
            <p style="padding: 4px">
                %if user.is_superuser:
                    <button id="deleteGroupBtn" class="btn confirmationModal" title="${_('Delete')}" disabled="disabled"><i class="icon-trash"></i> ${_('Delete')}</button>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                    <a id="addGroupBtn" href="${url('useradmin.views.edit_group')}" class="btn"><i class="icon-plus-sign"></i> ${_('Add group')}</a>
                    <a id="addLdapGroupBtn" href="${url('useradmin.views.add_ldap_group')}" class="btn"><i class="icon-refresh"></i> ${_('Add/Sync LDAP group')}</a>
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
        <th>${_('Group Name')}</th>
        <th>${_('Members')}</th>
        <th>${_('Permissions')}</th>
      </tr>
    </thead>
    <tbody>
    % for group in groups:
      <tr class="tableRow" data-search="${group.name}${', '.join([group_user.username for group_user in group.user_set.all()])}">
        %if user.is_superuser:
          <td class="center" data-row-selector-exclude="true">
            <input type="checkbox" class="groupCheck" data-group="${group.name}" data-confirmation-url="${ url('useradmin.views.delete_group', name=urllib.quote_plus(group.name)) }" data-row-selector-exclude="true"/>
          </td>
        %endif
        <td>
            %if user.is_superuser:
            <h5><a title="${_('Edit %(groupname)s') % dict(groupname=group.name)}" href="${ url('useradmin.views.edit_group', name=urllib.quote(group.name)) }" data-row-selector="true">${group.name}</a></h5>
            %else:
            <h5>${group.name}</h5>
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


<div id="deleteGroup" class="modal hide fade groupModal"></div>



    <script type="text/javascript" charset="utf-8">
        $(document).ready(function(){
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
                        $("#deleteGroup").html(data);
                        $("#deleteGroup").modal("show");
                    }
                });
            });

            $("#selectAll").change(function(){
                if ($(this).is(":checked")){
                    $(".groupCheck").attr("checked", "checked");
                }
                else {
                    $(".groupCheck").removeAttr("checked");
                }
                $(".groupCheck").change();
            });

            $(".groupCheck").change(function(){
                if ($(".groupCheck:checked").length == 1){
                    $("#deleteGroupBtn").removeAttr("disabled").data("confirmation-url", $(".groupCheck:checked").data("confirmation-url"));
                }
                else {
                    $("#deleteGroupBtn").attr("disabled", "disabled");
                }
            });

            $("a[data-row-selector='true']").jHueRowSelector();
        });
    </script>

${layout.commons()}

${commonfooter(messages)}
