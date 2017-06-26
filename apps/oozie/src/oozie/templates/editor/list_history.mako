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
  from django.utils.translation import ugettext as _
  import time as py_time
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("History"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='history') }


<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Submission History') }</h1>
    <div class="card-body">
      <p>
        <form class="form-search">
          <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search for username, name, etc...') }">
        </form>

        <table class="table table-condensed datatables" id="jobTable">
    <thead>
      <tr>
        <th width="10%">${ _('Submission Date') }</th>
        <th width="50%">${ _('Name') }</th>
        <th width="15%">${ _('Submitter') }</th>
        <th width="10%">${ _('Type') }</th>
        <th width="15%">${ _('Submission Id') }</th>
      </tr>
    </thead>
    <tbody>
    % for record in history:
      <tr>
        <td data-sort-value="${py_time.mktime(record.submission_date.timetuple())}">
          <a href="${ url('oozie:list_history_record', record_id=record.id) }" data-row-selector="true"></a>
          ${ utils.format_date(record.submission_date) }
        </td>
        <td><a href="${ record.job.get_absolute_url() }">${ record.job.name }</a></td>
        <td>${ record.submitter.username }</td>
        <td>${ record.job.get_type().title() }</td>
        <td><a href="${ record.get_absolute_oozie_url() }">${ record.oozie_job_id }</a></td>
      </tr>
    % endfor
    </tbody>
  </table>
      </p>
    </div>
</div>
</div>


<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function() {
    var oTable = $('#jobTable').dataTable( {
      "bLengthChange": false,
      "sPaginationType": "bootstrap",
      "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
      "aoColumns": [
        { "sSortDataType": "dom-sort-value", "sType": "numeric" },
        null,
        null,
        null,
        null
      ],
      "aaSorting": [[ 0, "desc" ]],
      "oLanguage": {
            "sEmptyTable":     "${_('No data available')}",
            "sInfo":           "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
            "sInfoEmpty":      "${_('Showing 0 to 0 of 0 entries')}",
            "sInfoFiltered":   "${_('(filtered from _MAX_ total entries)')}",
            "sZeroRecords":    "${_('No matching records')}",
            "oPaginate": {
                "sFirst":    "${_('First')}",
                "sLast":     "${_('Last')}",
                "sNext":     "${_('Next')}",
                "sPrevious": "${_('Previous')}"
            }
      },
      "fnDrawCallback":function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    $("#filterInput").keyup(function() {
       oTable.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });

</script>

${ commonfooter(request, messages) | n,unicode }
