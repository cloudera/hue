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
<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="common" file="common.mako" />

${ commonheader(_('Applications'), app_name, user) | n,unicode }

${ common.navbar('applications') }

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Applications')}</h1>

    <%actionbar:render>
      <%def name="search()">
          <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name')}">
      </%def>
      <%def name="creation()">
         <button type="button" class="btn uploadAppModalBtn"><i class="fa fa-plus-circle"></i> ${ _('Upload app') }</button>
      </%def>
    </%actionbar:render>



    <table class="table table-condensed datatables">
    <thead>
      <tr>
        <th>${_('Name')}</th>
        <th>${_('Upload time')}</th>
      </tr>
    </thead>
    <tbody>
    % for name, ts in applications.iteritems():
      <tr>
        <td>
          <a href="${ url('spark:editor') }#applicationId=${ name }" data-row-selector="true" title="${ _('Click to open and execute') }">
            ${ name }
          </a>
        </td>
        <td>${ ts }</td>
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


${ common.uploadAppModal() }


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {

    var apps = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "aaSorting":[
        [1, 'desc']
      ],
      "aoColumns":[
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
      apps.fnFilter($(this).val());
    });

    $(".uploadAppModalBtn").on("click", function(){
      $("#uploadAppModal").modal("show");
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }
