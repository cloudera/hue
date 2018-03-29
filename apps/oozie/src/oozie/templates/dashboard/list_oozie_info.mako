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

%if not is_embeddable:
${ commonheader(_("Oozie Information"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='oozie', dashboard=True) }
%endif

<style type="text/css">
  .oozie-info .form-search {
    margin: 0 0 20px !important;
  }
  .oozie-info .tab-content {
    padding: 0 !important;
  }
  .oozie-info .dataTables_wrapper table tbody tr, .oozie-info table th {
    background-color: #FFFFFF;
  }
</style>


<div class="oozie-info container-fluid">

  <div class="card card-small">
  <div class="card-body">

  <h1 class="card-heading card-heading-noborder simple pull-right" style="margin-top: -4px;">
  ${ _('Oozie status') }
  <div class="label ${ utils.get_status(oozie_status['systemMode']) }" style="line-height: 20px; vertical-align: middle">
    ${ oozie_status['systemMode'] }
  </div>
  </h1>

  <ul class="nav nav-pills">
    % if instrumentation:
    <li class="active"><a href="#instrumentation" data-toggle="tab">${ _('Instrumentation') }</a></li>
    % else:
    <li class="active"><a href="#metrics" data-toggle="tab">${ _('Metrics') }</a></li>
    % endif
    <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
  </ul>

  <div class="tab-content" style="padding-bottom:200px">

    % if instrumentation:
    <div class="tab-pane active" id="instrumentation">
      <form class="form-search">
        <input type="text" class="searchFilter input-xlarge search-query" placeholder="${_('Text Filter')}">
      </form>
      <div class="tabbable">
        <ul class="nav nav-tabs nav-tabs-border">
            % for category in instrumentation.iterkeys():
            <li
            % if loop.first:
              class="active"
            % endif
            >
              <a href="#${ category }" data-toggle="tab">${ category }</a>
            </li>
            % endfor
        </ul>

        <div class="tab-content">
            % for category in instrumentation.iterkeys():
            <div class="tab-pane
              % if loop.first:
              active
              % endif
            " id="${ category }">

              % for index, group in enumerate(instrumentation[category]):
              <div class="nav-header">${ group['group'] }</div>
              <table id="intrumentationTable-${ category }-${ index }" class="table table-condensed">
              <tbody>
                % for item in group['data']:
                <tr>
                <% name = item.pop('name') %>
                  <td>${ name }</td>
                % if category == 'timers':
                  <td>
                    % for label, timer in zip(['ownMinTime', 'ownTimeStdVar', 'totalTimeStdVar', 'ownTimeAvg', 'ticks', 'name', 'ownMaxTime', 'totalMinTime', 'totalMaxTime', 'totalTimeAvg'], item.values()):
                    ${ label } :
                    % if label == 'name':
                      ${ name } -
                    % endif
                    ${ timer }
                    % if not loop.last:
                        <br/>
                    % endif
                    % endfor
                  </td>
                % else:
                    <td>${ ', '.join(map(str, item.values())) }</td>
                % endif
                </tr>
                % endfor
              </tbody>
              </table>
              % endfor
            </div>
            % endfor
        </div>
      </div>
    </div>
    % endif

    % if metrics:
    <div class="tab-pane active" id="metrics">
        <form class="form-search">
          <input type="text" class="searchFilter input-xlarge search-query" placeholder="${_('Text Filter')}">
        </form>
        <ul class="nav nav-tabs nav-tabs-border">
        % for obj in metrics:
          % if obj != 'version':
          <li
            % if loop.first:
                class="active"
            % endif
          >
          <a href="#metrics${ obj }" data-toggle="tab">${ obj }</a>
          </li>
          % endif
        % endfor
        </ul>
        <div class="tab-content">
        % for obj in metrics:
          % if obj != 'version':
            <div class="tab-pane
            % if loop.first:
              active
            % endif
            " id="metrics${obj}">
                ${recurse(metrics[obj])}
            </div>
          % endif
        % endfor
        </div>

    </div>

    <%def name="recurse(metric)">
        % if metric:
          % if isinstance(metric, basestring):
            <table class="table table-condensed">
              <tr>
                <th>${metric}</th>
              </tr>
            </table>
          % else:
            <table class="table table-condensed metricsTable">
            <thead>
            <tr>
              <th>${_('Name')}</th>
              <th>${_('Value')}</th>
            </tr>
            </thead>
           <tbody>
            % for val in metric:
            <tr>
              <td width="30%">
                <table class="table" style="margin-bottom: 0">
                  <tr>
                    <th style="border: none">${val}</th>
                  </tr>
                </table>
              </td>
              <td width="70%">
                <table class="table" style="margin-bottom: 0">
                % for prop in metric[val]:
                  <tr>
                    <th width="20%" style="border: none">${prop}</th>
                    <td width="80%" style="border: none">${metric[val][prop]}</td>
                  </tr>
                % endfor
                </table>
              </td>
            </tr>
            % endfor
              </tbody>
            </table>
          % endif
        % else:
          <table class="table table-condensed">
          <tr>
            <td>${ _('No metrics available for this section.') }</td>
          </tr>
          </table>
        % endif
      </%def>

    % endif

    <div class="tab-pane" id="configuration">
      <form class="form-search">
        <input type="text" class="searchFilter input-xlarge search-query" placeholder="${_('Text Filter')}">
      </form>
      ${ utils.display_conf(configuration, "configurationTable") }
    </div>

    %if not is_embeddable:
    <div style="margin-bottom: 16px; margin-top: 10px">
      <a href="${ url('oozie:list_oozie_bundles') }" class="btn">${ _('Back') }</a>
    </div>
    %endif

    </div>
    </div>
  </div>
</div>

<script>
  $(document).ready(function(){
    $("a[data-row-selector='true']").jHueRowSelector();

    $("*[rel=tooltip]").tooltip();

    var _metadataTable = $("#configurationTable").dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bAutoWidth": false,
        "aoColumns": [
            { "sWidth": "30%" },
            { "sWidth": "70%" }
        ],
        "oLanguage": {
           "sEmptyTable": "${_('No data available')}",
           "sZeroRecords": "${_('No matching records')}",
        },
        "asStripeClasses": []
   });
  var metricsTables = [];
% if metrics:
   $(".metricsTable").each(function(){
     var _table = $(this).dataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bAutoWidth": false,
        "aoColumns": [
            { "sWidth": "30%" },
            { "sWidth": "70%", "bSortable": false }
        ],
        "oLanguage": {
           "sEmptyTable": "${_('No data available')}",
           "sZeroRecords": "${_('No matching records')}",
        },
        "asStripeClasses": []
      });
     metricsTables.push(_table);
   });
% endif

   var instrumentationTables = [];

   % for category in instrumentation.iterkeys():
      % for index in range(len(instrumentation[category])):
        var table = $("#intrumentationTable-${ category }-${ index }").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bAutoWidth": false,
            "aoColumns": [
                { "sWidth": "30%" },
                { "sWidth": "70%" }
            ],
            "oLanguage": {
                "sEmptyTable": "${_('No data available')}",
                "sZeroRecords": "${_('No matching records')}"
            },
            "asStripeClasses": []
        });
        $("#intrumentationTable-${ category }-${ index } th").removeClass();
        instrumentationTables.push(table);
      % endfor
    % endfor

    function filterTables(search) {
      _metadataTable.fnFilter(search);
      $.each(instrumentationTables, function(index, item){
        item.fnFilter(search);
      });
      $.each(metricsTables, function(index, item){
        item.fnFilter(search);
      });
    }

    $(".searchFilter").on("keyup", function(){
      filterTables($(this).val());
    });

    $(".dataTables_wrapper").css("min-height","0");
    $(".dataTables_filter").hide();

    $(".nav-tabs a[data-toggle='tab']").on("show", function (e) {
      $(".searchFilter").val("");
      filterTables("");
    });
  });
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
