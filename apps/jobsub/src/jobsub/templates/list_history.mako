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
import time as py_time
from django.template.defaultfilters import date, time
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${commonheader(_('Job Designer'), "jobsub", user, "100px")}
${layout.menubar(section='history')}

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
    <h1>${_('Job Submission History')}</h1>

    <%actionbar:render />

    <table class="table table-condensed datatables" id="jobTable">
        <thead>
        <tr>
            <th>${_('Oozie Job ID')}</th>
            <th>${_('Owner')}</th>
            <th>${_('Name')}</th>
            <th>${_('Type')}</th>
            <th>${_('Description')}</th>
            <th>${_('Submission Date')}</th>
        </tr>
        </thead>
        <tbody>
                %for record in history:
                <% design = record.design %>
                <tr>
                    <td><a href="${url('jobsub.views.oozie_job', jobid=record.job_id)}">${record.job_id}</a></td>
                    <td>${record.owner.username}</td>
                    <td>${design.name}</td>
                    <td>${design.root_action.action_type}</td>
                    <td>${design.description}</td>
                    <td data-sort-value="${py_time.mktime(record.submission_date.timetuple())}">${date(record.submission_date)} ${time(record.submission_date).replace("p.m.","PM").replace("a.m.","AM")}</td>
                </tr>
                %endfor
        </tbody>
    </table>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function() {
        var oTable = $('#jobTable').dataTable( {
            'sPaginationType': 'bootstrap',
            "bLengthChange": false,
            "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
            "aoColumns": [
                null,
                null,
                null,
                null,
                null,
                { "sSortDataType": "dom-sort-value", "sType": "numeric" }
            ],
            "aaSorting": [[ 5, "desc" ]],
            "oLanguage": {
                "sEmptyTable":     "${_('No data available in table')}",
                "sInfo":           "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
                "sInfoEmpty":      "${_('Showing 0 to 0 of 0 entries')}",
                "sInfoFiltered":   "${_('(filtered from _MAX_ total entries)')}",
                "sZeroRecords":    "${_('No matching records found')}",
                "oPaginate": {
                    "sFirst":    "${_('First')}",
                    "sLast":     "${_('Last')}",
                    "sNext":     "${_('Next')}",
                    "sPrevious": "${_('Previous')}"
                }
            }
        });

        $("#filterInput").keyup(function() {
            oTable.fnFilter($(this).val());
        });

    });
</script>

${commonfooter(messages)}
