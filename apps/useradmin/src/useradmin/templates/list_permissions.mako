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

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
${ commonheader(_('Hue Permissions'), "useradmin", user, "100px") | n,unicode }
${layout.menubar(section='permissions', _=_)}

<div class="container-fluid">
    <h1>${_('Hue Permissions')}</h1>
    <%actionbar:render>
      <%def name="search()">
        <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for application, group, etc...')}">
      </%def>
    </%actionbar:render>

    <table class="table table-striped table-condensed datatables">
        <thead>
        <tr>
            <th>${_('Application')}</th>
            <th>${_('Permission')}</th>
            <th>${_('Groups')}</th>
        </tr>
        </thead>
        <tbody>
            % for perm in permissions:
            <tr class="tableRow" data-search="${perm.app}${perm.description}${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}">
                <td>
                %if user.is_superuser:
                    <strong><a title="${_('Edit permission')}" href="${ url('useradmin.views.edit_permission', app=urllib.quote(perm.app), priv=urllib.quote(perm.action)) }" data-name="${perm.app}" data-row-selector="true">${perm.app}</a></strong>
                %else:
                    <strong>${perm.app}</strong>
                %endif
                </td>
                <td>${perm.description}</td>
                <td>${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}</td>
            </tr>
            % endfor
        </tbody>
        <tfoot class="hide">
        <tr>
            <td colspan="3">
                <div class="alert">
                    ${_('There are no permissions matching the search criteria.')}
                </div>
            </td>
        </tr>
        </tfoot>
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
                null
            ],
            "oLanguage": {
                "sEmptyTable": "${_('No data available')}",
                "sZeroRecords": "${_('No matching records')}",
            }
        });

        $(".dataTables_wrapper").css("min-height","0");
        $(".dataTables_filter").hide();

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>

${layout.commons()}

${ commonfooter(messages) | n,unicode }
