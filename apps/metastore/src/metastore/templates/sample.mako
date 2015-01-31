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
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

% if sample is not None:
  % if error_message:
    <div class="alert alert-error">
      <h3>${ _('Error!') }</h3>
      <pre>${ error_message | h }</pre>
    </div>
  % else:
  <table class="table table-striped table-condensed sampleTable">
    <thead>
      <tr>
        <th style="width: 10px"></th>
        % for col in table.cols:
          <th>${ col.name }</th>
        % endfor
      </tr>
    </thead>
    <tbody>
      % for i, row in enumerate(sample):
      <tr>
        <td>${ i }</td>
        % for item in row:
        <td>
          % if item is None:
            NULL
          % else:
            ${ escape(smart_unicode(item, errors='ignore')).replace(' ', '&nbsp;') | n,unicode }
          % endif
        </td>
        % endfor
      </tr>
      % endfor
    </tbody>
  </table>
  % endif
% endif

<style type="text/css">
  .sampleTable td, .sampleTable th {
    white-space: nowrap;
  }
</style>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $(".sampleTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });
  });
</script>
