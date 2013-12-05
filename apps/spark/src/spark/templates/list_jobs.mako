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

${ commonheader(_('Query'), app_name, user) | n,unicode }

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
        <td>${ job.get('jobId') }</td>
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

<div id="deleteQuery" class="modal hide fade">
  <form id="deleteQueryForm" action="${ url(app_name + ':delete_design') }" method="POST">
    <input type="hidden" name="skipTrash" id="skipTrash" value="false"/>
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteQueryMessage">${_('Confirm action')}</h3>
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
    </div>
    <div class="hide">
      <select name="designs_selection" data-bind="options: availableSavedQueries, selectedOptions: chosenSavedQueries" multiple="true"></select>
    </div>
  </form>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
        availableSavedQueries : ko.observableArray(${ jobs_json | n,unicode }),
        chosenSavedQueries : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    var savedQueries = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false,
      "aaSorting":[
        [4, 'desc']
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
      savedQueries.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }
