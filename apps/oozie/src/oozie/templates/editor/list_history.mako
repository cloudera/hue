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
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='history') }


<div class="container-fluid">
  <h1>${ _('Submission History') }</h1>
  <div class="well hueWell">
    <form class="form-search">
      ${ _('Filter:') } <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search for username, name, etc...') }">
    </form>
  </div>

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
        <td>
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
</div>


<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function() {
    var oTable = $('#jobTable').dataTable( {
      "bLengthChange": false,
      "sPaginationType": "bootstrap",
      "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
      "aoColumns": [
        { "sType": "date" },
        null,
        null,
        null,
        null
      ],
      "aaSorting": [[ 0, "desc" ]],
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

  $("a[data-row-selector='true']").jHueRowSelector();
</script>

${commonfooter(messages)}
