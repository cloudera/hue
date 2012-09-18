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
from django.contrib.auth.models import Group
%>

<%namespace name="layout" file="layout.mako" />
${commonheader(_('Hue Permissions'), "useradmin", user, "100px")}
${layout.menubar(section='permissions', _=_)}

<div class="container-fluid">
    <h1>${_('Hue Permissions')}</h1>
    <div class="well hueWell">
        <form class="form-search">
                ${_('Filter: ')}<input id="filterInput" class="input-xxlarge search-query" placeholder="${_('Search for application name, description, etc...')}">
        </form>
    </div>
    <table class="table table-striped datatables">
        <thead>
        <tr>
            <th>${_('Application')}</th>
            <th>${_('Permission')}</th>
            <th>${_('Groups')}</th>
            %if user.is_superuser:
                <th>&nbsp;</th>
            %endif
        </tr>
        </thead>
        <tbody>
            % for perm in permissions:
            <tr class="permissionRow" data-search="${perm.app}${perm.description}${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}">
                <td>${perm.app}</td>
                <td>${perm.description}</td>
                <td>${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}</td>
            %if user.is_superuser:
                <td class="right">
                    <a title="${_('Edit permission')}" class="btn small editPermissionBtn" href="${ url('useradmin.views.edit_permission', app=urllib.quote(perm.app), priv=urllib.quote(perm.action)) }" data-name="${perm.app}" data-row-selector="true">${_('Edit')}</a>
                </td>
            %endif
            </tr>
            % endfor
        </tbody>
    </table>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $(".datatables").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bFilter": false,
            "aoColumns": [
                null,
                null,
                %if user.is_superuser:
                    null,
                    { "bSortable": false }
                %else:
                    null
                %endif
            ]
        });
        $(".dataTables_wrapper").css("min-height","0");
        $(".dataTables_filter").hide();

        $("#filterInput").keyup(function(){
            $.each($(".permissionRow"), function(index, value) {
                if($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
                    $(value).hide(250);
                }else{
                    $(value).show(250);
                }
            });
        });

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>

${commonfooter(messages)}
