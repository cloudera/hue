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

${ commonheader(_("SLA"), "sla", user) | n,unicode }
${ layout.menubar(section='sla', dashboard=True) }


<div class="container-fluid">

  <div class="card card-small">
  <div class="card-body">
  <p>

  <h1 class="card-heading card-heading-noborder simple pull-right" style="margin-top: -4px;">
    Import / Export
  </h1>

  <ul class="nav nav-tabs">
      <form class="form-search" id="searchForm" method="GET" action=".">
        <input type="text" name="job_name" class="searchFilter input-xlarge search-query" placeholder="${_('Job Name or Id (required)')}">
        <input type="checkbox" name="isParent" class="searchFilter" placeholder="${_('Text Filter')}">
        ${ _('Parent ID') }
        Start
        <input type="text" name="start" class="searchFilter input-xlarge search-query" placeholder="${_('Start in GMT')}">
        End
        <input type="text" name="end" class="searchFilter input-xlarge search-query" placeholder="${_('End')}">
      </form>
    <li class="active"><a href="#slaListTab" data-toggle="tab">${ _('List') }</a></li>
    <li><a href="#graphTab" data-toggle="tab">${ _('Graph') }</a></li>
  </ul>

  <div class="tab-content" style="padding-bottom:200px">
    <div class="tab-pane active" id="slaListTab">
      <form class="form-search">
        <input type="text" class="searchFilter input-xlarge search-query" placeholder="${_('Text Filter')}">
      </form>
      <div class="tabbable">

        <div class="tab-content">

            <table id="slaTable" class="table table-striped table-condensed">
              <thead>
                % for col in columns:
                  <th>${ col }</th>
                % endfor
              </thead>
              <tbody>
                % for sla in oozie_slas:
                <tr>
                  % for col in columns:
                    <td>${ sla.get(col, '') }</td>
                  % endfor
                </tr>
                % endfor
              </tbody>
              </table>

        </div>
      </div>

    </div>

    <div class="tab-pane" id="graphTab">
      MY GRAPH      
    </div>

    </p>
    </div>
    </div>
  </div>


<script>
  $(document).ready(function(){
    $("a[data-row-selector='true']").jHueRowSelector();

    $("*[rel=tooltip]").tooltip();

    var slaTable = $("#slaTable").dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bAutoWidth": false,
        "oLanguage": {
            "sEmptyTable": "${_('No data available')}",
            "sZeroRecords": "${_('No matching records')}"
        }
    });

    var _filterTimeout = -1;
    $(".searchFilter").keyup(function() {
      window.clearTimeout(_filterTimeout);
      _filterTimeout = window.setTimeout(function () {
        $.post("${ url('oozie:list_oozie_sla') }?format=json", $("#searchForm").serialize(), function(data) {
          slaTable.fnClearTable();
          if (data['oozie_slas']) {
            slaTable.fnAddData(data['oozie_slas']);
          } 
        });
      }, 300);
    });

    $(".dataTables_wrapper").css("min-height","0");
    $(".dataTables_filter").hide();
  });
</script>

${ commonfooter(messages) | n,unicode }
