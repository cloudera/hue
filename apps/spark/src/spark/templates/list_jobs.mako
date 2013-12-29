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

<%namespace name="common" file="common.mako" />

${ commonheader(_('Jobs'), app_name, user) | n,unicode }

${ common.navbar('jobs') }

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Jobs')}</h1>

    <table class="table table-condensed datatables">
     <thead>
        <tr>
          <th>${_('Status')}</th>
          <th>${_('Job id')}</th>
          <th>${_('Class path')}</th>
          <th>${_('Context')}</th>
          <th>${_('Start time')}</th>
          <th>${_('Duration')}</th>
        </tr>
      </thead>
      <tbody>
        % for job in jobs:
        <tr>
          <td>${ job.get('status') }</td>
          <td>
            <%
              can_view = job.get('status') == 'FINISHED'
            %>
            % if can_view:
              <a href="${ url('spark:view_job', job.get('jobId')) }" data-row-selector="true" title="${ _('Click to open') }">
            % endif
            ${ job.get('jobId') }
            % if can_view:
              </a>
            % endif
          </td>
          <td>${ job.get('classPath') }</td>
          <td>${ job.get('context') }</td>
          <td>${ job.get('startTime') }</td>
          <td>${ job.get('duration') }</td>
        </tr>
        % endfor
      </tbody>
    </table>
    <div class="card-body">
      <p>
        ## ${ comps.pagination(page) }
      </p>
    </div>
  </div>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {

    var jobs = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false,
      "aaSorting":[
        [4, "desc"]
      ],
      "aoColumns":[
        null,
        null,
        null,
        null,
        null,
        null
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sZeroRecords":"${_('No matching records')}",
      },
      "bStateSave": true
    });

    $("#filterInput").keyup(function () {
      jobs.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }
