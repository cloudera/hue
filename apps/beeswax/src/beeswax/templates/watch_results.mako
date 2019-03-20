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
from desktop.views import commonheader, commonfooter
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />
<%namespace name="comps" file="beeswax_components.mako" />

${ commonheader(_('Query Results'), app_name, user, request) | n,unicode }
${layout.menubar(section='query')}

<style type="text/css">
  #collapse {
    padding: 4px 0 0;
  }

  #expand {
    display: none;
    cursor: pointer;
    position: absolute;
    background-color: #01639C;
    padding: 3px;
    -webkit-border-top-right-radius: 5px;
    -webkit-border-bottom-right-radius: 5px;
    -moz-border-radius-topright: 5px;
    -moz-border-radius-bottomright: 5px;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    opacity: 0.5;
    left: -4px;
  }

  #expand:hover {
    opacity: 1;
    left: 0;
  }

  .resultTable td, .resultTable th {
    white-space: nowrap;
  }

  .noLeftMargin {
    margin-left: 0!important;
  }

  .empty {
    text-align: center;
    color: #CCCCCC;
    font-size: 24px;
    padding: 40px;
  }
  .map {
    height: 400px;
  }
</style>

<div class="container-fluid">
  <div id="expand"><i class="fa fa-chevron-right" style="color: #FFFFFF"></i></div>
    <div class="row-fluid">
        <div class="span3">
            <div class="sidebar-nav">
                <ul class="nav nav-list">
                    <li><a id="collapse" class="btn btn-small"><i class="fa fa-chevron-left" rel="tooltip" title="${_('Collapse this panel')}"></i></a></li>
                    % if download_urls and download:
                      <li class="nav-header">${_('Results')}</li>
                      <li><a target="_blank" href="${download_urls["csv"]}"><i class="fa fa-arrow-circle-o-down"></i> ${_('Download as CSV')}</a></li>
                      <li><a target="_blank" href="${download_urls["xls"]}"><i class="fa fa-arrow-circle-o-down"></i> ${_('Download as XLS')}</a></li>
                    % endif
                    % if can_save and download:
                      <li><a data-toggle="modal" href="#saveAs"><i class="fa fa-floppy-o"></i> ${_('Save')}</a></li>
                    % endif
                    % if app_name != 'impala':
                      <%
                        n_jobs = hadoop_jobs and len(hadoop_jobs) or 0
                        mr_jobs = (n_jobs == 1) and _('MapReduce Job') or _('MapReduce Jobs')
                      %>
                      % if n_jobs > 0:
                        <li class="nav-header">${mr_jobs} (${n_jobs})</li>
                        % for jobid in hadoop_jobs:
                          <li><a href="${url("jobbrowser.views.single_job", job=jobid.replace('application', 'job'))}">${ jobid.replace("application_", "") }</a></li>
                        % endfor
                      % else:
                        <li class="nav-header">${mr_jobs}</li>
                        <li class="white">${_('No Hadoop jobs were launched in running this query.')}</li>
                      % endif
                    % endif
                </ul>
            </div>

          % if not query.is_finished():
            <div id="multiStatementsQuery" class="alert">
              <button type="button" class="close" data-dismiss="alert">&times;</button>
              <strong>${_('Multi-statement query')}</strong><br/>
              ${_('Hue stopped as one of your query contains some results.') }
              ${_('Click on') }
              <form action="${ url(app_name + ':watch_query_history', query.id) }?context=${ query.design.get_query_context() }" method="POST">
                ${ csrf_token(request) | n,unicode }
                <input type="submit" value="${ _("next") }"/ class="btn btn-primary">
              </form>
              ${_('to continue execution of the remaining statements.') }
            </div>
          % endif

          <div id="jumpToColumnAlert" class="alert hide" style="margin-top: 12px;">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <strong>${_('Did you know?')}</strong>
            <ul>
              <li>${ _('If the result contains a large number of columns, click a row to select a column to jump to') }</li>
              <li>${ _('Save huge results on HDFS and download them with FileBrowser') }</li>
            </ul>
          </div>
        </div>

        <div class="span9">
          <div class="card card-small">
            <h1 class="card-heading simple">${_('Query Results:')} ${ util.render_query_context(query_context) }</h1>
            <div class="card-body">
            <p>
            <ul class="nav nav-tabs">
              <li class="active"><a href="#results" data-toggle="tab">
                  % if error:
                        ${_('Error')}
                  % else:
                        ${_('Results')}
                  % endif
              </a></li>
              <li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
              <li><a href="#log" data-toggle="tab">${_('Log')}</a></li>
              % if not error:
              <li><a href="#columns" data-toggle="tab">${_('Columns')}</a></li>
              <li><a href="#chart" data-toggle="tab">${_('Chart')}</a></li>
              % endif
            </ul>

            <div class="tab-content">
        <div class="active tab-pane" id="results">
            % if error:
              <div class="alert alert-error">
                <h3>${_('Error')}</h3>
                <pre>${ error_message }</pre>
                % if expired and query_context:
                    <div class="well">
                        ${ _('The query result has expired.') }
                        ${ _('You can rerun it from ') } ${ util.render_query_context(query_context) }
                    </div>
                % endif
              </div>
            % else:
            % if expected_first_row != start_row:
                <div class="alert"><strong>${_('Warning:')}</strong> ${_('Page offset may have incremented since last view.')}</div>
            % endif
            <table id="resultTable" class="table table-condensed resultTable" cellpadding="0" cellspacing="0" data-tablescroller-min-height-disable="true" data-tablescroller-enforce-height="true">
            <thead>
            <tr>
              <th>&nbsp;</th>
              % for col in columns:
                <th>${ col.name }</th>
              % endfor
            </tr>
            </thead>
            <tbody>
              % for i, row in enumerate(results):
              <tr>
                <td>${ start_row + i }</td>
                % for item in row:
                  <td>
                    % if item is None:
                      NULL
                    % else:
                      ${ smart_unicode(item, errors='ignore') | u }
                    % endif
                  </td>
                % endfor
              </tr>
              % endfor
            </tbody>
            </table>

             <div style="text-align: center; padding: 5px; height: 30px">
               <span class="noMore hide"
                     style="color:#999999">${ _('You have reached the last record for this query.') }</span><img
                     src="${ static('desktop/art/spinner.gif') }" alt="${ _('Spinner') }"
                     class="spinner"
                     style="display: none;"/>
             </div>
            % endif
        </div>

        <div class="tab-pane" id="query">
          <pre>${ query.get_current_statement() }</pre>
        </div>

        <div class="tab-pane" id="log">
          <pre>${ force_unicode(log) }</pre>
        </div>

        % if not error:
        <div class="tab-pane" id="columns">
          <table class="table table-condensed" cellpadding="0" cellspacing="0">
            <thead>
              <tr><th>${_('Name')}</th></tr>
            </thead>
            <tbody>
              % for col in columns:
                <tr><td><a href="javascript:void(0)" class="column-selector" data-column="${ col.name }">${ col.name }</a></td></tr>
              % endfor
            </tbody>
          </table>
        </div>
        <div class="tab-pane" id="chart">
          <div style="text-align: center">
          <form class="form-inline">
            ${_('Chart type')}&nbsp;
            <div class="btn-group" data-toggle="buttons-radio">
              <a rel="tooltip" data-placement="top" title="${_('Bars')}" id="blueprintBars" href="javascript:void(0)" class="btn"><i class="fa fa-bar-chart-o"></i></a>
              <a rel="tooltip" data-placement="top" title="${_('Lines')}" id="blueprintLines" href="javascript:void(0)" class="btn"><i class="fa fa-signal"></i></a>
              <a rel="tooltip" data-placement="top" title="${_('Map')}" id="blueprintMap" href="javascript:void(0)" class="btn"><i class="fa fa-map-marker"></i></a>
            </div>&nbsp;&nbsp;
            <span id="blueprintAxis" class="hide">
              <label>${_('X-Axis')}
                <select id="blueprintX" class="blueprintSelect">
                  <option value="-1">${ _("Please select a column")}</option>
                  % for col in columns:
                    <option value="${loop.index+2}">${ col.name }</option>
                  % endfor
                </select>
              </label>&nbsp;&nbsp;
              <label>${_('Y-Axis')}
              <select id="blueprintY" class="blueprintSelect">
                  <option value="-1">${ _("Please select a column")}</option>
                  % for col in columns:
                    <option value="${loop.index+2}">${ col.name }</option>
                  % endfor
                </select>
              </label>
            </span>
            <span id="blueprintLatLng" class="hide">
              <label>${_('Latitude')}
                <select id="blueprintLat" class="blueprintSelect">
                  <option value="-1">${ _("Please select a column")}</option>
                  % for col in columns:
                    <option value="${loop.index+2}">${ col.name }</option>
                  % endfor
                </select>
              </label>&nbsp;&nbsp;
              <label>${_('Longitude')}
              <select id="blueprintLng" class="blueprintSelect">
                  <option value="-1">${ _("Please select a column")}</option>
                  % for col in columns:
                    <option value="${loop.index+2}">${ col.name }</option>
                  % endfor
                </select>
              </label>&nbsp;&nbsp;
              <label>${_('Label')}
              <select id="blueprintDesc" class="blueprintSelect">
                  <option value="-1">${ _("Please select a column")}</option>
                  % for col in columns:
                    <option value="${loop.index+2}">${ col.name }</option>
                  % endfor
                </select>
              </label>
            </span>
          </form>
          </div>
          <div id="blueprint" class="empty">${_("Please select a chart type.")}</div>
        </div>
        % endif
      </div>
            </p>
            </div>
          </div>
        </div>
    </div>
</div>

% if can_save:
## duplication from save_results.mako
<div id="saveAs" class="modal hide fade">
  <form id="saveForm" action="${url(app_name + ':save_results', query.id) }" method="POST"
        class="form form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Save Query Results') }</h2>
    </div>
    <div class="modal-body">
      <label class="radio">
        <input id="id_save_target_0" type="radio" name="save_target" value="to a new table" checked="checked"/>
        &nbsp;${_('In a new table')}
      </label>
      ${comps.field(save_form['target_table'], notitle=True, placeholder=_('Table Name'))}
      <br/>

      <label class="radio">
        <input id="id_save_target_1" type="radio" name="save_target" value="to HDFS directory">
        &nbsp;${_('In an HDFS directory')}
      </label>
      <span id="hdfs" class="hide">
        ${comps.field(save_form['target_dir'], notitle=True, hidden=False, placeholder=_('Results location'), klass="pathChooser input-xlarge")}
        <br/>
        <br/>
        <div class="alert alert-warn">
          ${ _('In text with columns separated by ^A and rows separated by newlines. JSON for non-primitive type columns.') }
        </div>
      </span>
      <div id="fileChooserModal" class="smallModal well hide">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
      </div>
    </div>
    <div class="modal-footer">
      <div id="fieldRequired" class="hide" style="position: absolute; left: 10;">
        <span class="label label-important">${_('Name or directory required.')}</span>
      </div>
      <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
      <a id="saveBtn" class="btn btn-primary">${_('Save')}</a>
      <input type="hidden" name="save" value="save"/>
    </div>
  </form>
</div>
% endif.resultTable

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.flot.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.flot.categories.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/leaflet/leaflet.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/leaflet/leaflet.markercluster.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/jquery.blueprint.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
$(document).ready(function () {

  var dataTable = $(".resultTable").dataTable({
    "bPaginate": false,
    "bLengthChange": false,
    "bInfo": false,
    "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
    },
    "aoColumns":[
        {"sSortDataType":"dom-text", "sType":"numeric", "sWidth":"1%" },
        % for col in columns:
          <%
          sType = "string"
          if col.type in ["TINYINT_TYPE", "SMALLINT_TYPE", "INT_TYPE", "BIGINT_TYPE", "FLOAT_TYPE", "DOUBLE_TYPE", "DECIMAL_TYPE"]:
            sType = "numeric"
          elif col.type in ["TIMESTAMP_TYPE", "DATE_TYPE", "DATETIME_TYPE"]:
            sType = "date"
          %>
        { "sSortDataType":"dom-text", "sType":"${ sType }"},
        % endfor
    ],
    "fnDrawCallback": function( oSettings ) {
      $(".resultTable").jHueTableExtender({
        hintElement: "#jumpToColumnAlert",
        fixedHeader: true,
        firstColumnTooltip: true
      });
    },
    "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
      // Make sure null values are seen as NULL.
      for(var j = 0; j < aData.length; ++j) {
        if (aData[j] == null) {
          $(nRow).find('td:eq('+j+')').html("NULL");
        }
      }
      return nRow;
    }
  });

  $(".dataTables_wrapper").css("min-height", "0");
  $(".dataTables_filter").hide();

  $("input[name='save_target']").change(function () {
    $("#fieldRequired").addClass("hide");
    $("input[name='target_dir']").removeClass("fieldError");
    $("input[name='target_table']").removeClass("fieldError");
    if ($(this).val().indexOf("HDFS") > -1) {
      $("input[name='target_table']").addClass("hide");
      $("#hdfs").removeClass("hide");
      $(".fileChooserBtn").removeClass("hide");
    }
    else {
      $("input[name='target_table']").removeClass("hide");
      $("#hdfs").addClass("hide");
      $(".fileChooserBtn").addClass("hide");
    }
  });

  $("#saveBtn").click(function () {
    if ($("input[name='save_target']:checked").val().indexOf("HDFS") > -1) {
      if ($.trim($("input[name='target_dir']").val()) == "") {
        $("#fieldRequired").removeClass("hide");
        $("input[name='target_dir']").addClass("fieldError");
        return false;
      }
    }
    else {
      if ($.trim($("input[name='target_table']").val()) == "") {
        $("#fieldRequired").removeClass("hide");
        $("input[name='target_table']").addClass("fieldError");
        return false;
      }
    }
    $("#saveForm").submit();
  });


  $("input[name='target_dir']").after(hueUtils.getFileBrowseButton($("input[name='target_dir']")));

  $("#collapse").click(function () {
    $(".sidebar-nav").parent().css("margin-left", "-31%");
    $("#expand").show().css("top", $(".sidebar-nav i").position().top + "px");
    $(".sidebar-nav").parent().next().removeClass("span9").addClass("span12").addClass("noLeftMargin");
    generateGraph(getGraphType());
  });
  $("#expand").click(function () {
    $(this).hide();
    $(".sidebar-nav").parent().next().removeClass("span12").addClass("span9").removeClass("noLeftMargin");
    $(".sidebar-nav").parent().css("margin-left", "0");
    generateGraph(getGraphType());
  });

  $(document).on("click", ".column-selector", function () {
    var _t = $(".resultTable");
    var _col = _t.find("th:econtains(" + $(this).data("column") + ")");
    _t.find(".columnSelected").removeClass("columnSelected");
    _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
    $("a[href='#results']").click();
  });

  $("a[data-toggle='tab']").on("shown", function (e) {
    if ($(e.target).attr("href") == "#results" && $(e.relatedTarget).attr("href") == "#columns") {
      if ($(".resultTable .columnSelected").length > 0) {
        var _t = $(".resultTable");
        var _col = _t.find("th:nth-child(" + ($(".resultTable .columnSelected").index() + 1) + ")");
        _t.parent().animate({
          scrollLeft: _col.position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
        }, 300);
      }
    }
  });

  resizeLogs();

  $(window).resize(function () {
    resizeLogs();
  });

  $("a[href='#log']").on("shown", function () {
    resizeLogs();
  });

  function resizeLogs() {
    $("#log pre").css("overflow", "auto").height($(window).height() - $("#log pre").position().top - 40);
  }

  % if app_name == 'impala' and query.is_finished():
    % if not download:
      $("#collapse").click();
      $(".sidebar-nav, #expand").hide();
    % elif not error:
      $("table").replaceWith("${ _('Download results from the left.') }");
    % endif
  % endif

  // enable infinite scroll instead of pagination
  var _nextJsonSet = "${ next_json_set }";
  var _hasMore = ${ has_more and 'true' or 'false' };
  var _dt = $("div.dataTables_wrapper");
  _dt.on("scroll", function (e) {
    if (_dt.scrollTop() + _dt.outerHeight() + 20 > _dt[0].scrollHeight && !_dt.data("isLoading") && _hasMore) {
      _dt.data("isLoading", true);
      _dt.animate({opacity: '0.55'}, 200);
      $(".spinner").show();
      $.getJSON(_nextJsonSet, function (data) {
        _hasMore = data.has_more;
        if (!_hasMore) {
          $(".noMore").removeClass("hide");
        }
        _nextJsonSet = data.next_json_set;
        var _cnt = 0;
        for (var i = 0; i < data.results.length; i++) {
          var row = data.results[i];
          row.unshift(data.start_row + _cnt);
          dataTable.fnAddData(row);
          _cnt++;
        }
        _dt.data("isLoading", false);
        _dt.animate({opacity: '1'}, 50);
        $(".spinner").hide();
      });
    }
  });

  _dt.jHueScrollUp();

  function getMapBounds(lats, lngs) {
    lats = lats.sort();
    lngs = lngs.sort();
    return [
      [lats[lats.length - 1], lngs[lngs.length - 1]], // north-east
      [lats[0], lngs[0]] // south-west
    ]
  }
  var map;
  function generateGraph(graphType) {
    if (graphType != "") {
      if (map != null) {
        try {
          map.remove();
        }
        catch (err) { // do nothing
        }
      }
      $("#blueprint").attr("class", "").attr("style", "").empty();
      $("#blueprint").data("plugin_jHueBlueprint", null);
      if (graphType == $.jHueBlueprint.TYPES.MAP) {
        if ($("#blueprintLat").val() != "-1" && $("#blueprintLng").val() != "-1") {
          var _latCol = $("#blueprintLat").val() * 1;
          var _lngCol = $("#blueprintLng").val() * 1;
          var _descCol = $("#blueprintDesc").val() * 1;
          var _lats = [];
          var _lngs = [];
          $(".resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
            _lats.push($.trim($(this).text()) * 1);
          });
          $(".resultTable>tbody>tr>td:nth-child(" + _lngCol + ")").each(function (cnt) {
            _lngs.push($.trim($(this).text()) * 1);
          });
          $("#blueprint").addClass("map");
          map = L.map("blueprint").fitBounds(getMapBounds(_lats, _lngs));

          L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          }).addTo(map);

          $(".resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
            if (_descCol != "-1") {
              L.marker([$.trim($(this).text()) * 1, $.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1]).addTo(map).bindPopup($.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _descCol + ")").text()));
            }
            else {
              L.marker([$.trim($(this).text()) * 1, $.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1]).addTo(map);
            }
          });

        }
        else {
          $("#blueprint").addClass("empty").text("${_("Please select the latitude and longitude columns.")}");
        }
      }
      else {
        if ($("#blueprintX").val() != "-1" && $("#blueprintY").val() != "-1") {
          var _x = $("#blueprintX").val() * 1;
          var _y = $("#blueprintY").val() * 1;
          var _data = [];
          $(".resultTable>tbody>tr>td:nth-child(" + _x + ")").each(function (cnt) {
            _data.push([$.trim($(this).text()), $.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _y + ")").text()) * 1]);
          });

          $("#blueprint").jHueBlueprint({
            data: _data,
            label: $(".resultTable>thead>tr>th:nth-child(" + _y + ")").text(),
            type: graphType,
            color: $.jHueBlueprint.COLORS.BLUE,
            isCategories: true,
            fill: true,
            enableSelection: false,
            height: 250
          });
          if (_data.length > 30){
            $(".flot-x-axis .flot-tick-label").hide();
          }
        }
        else {
          $("#blueprint").addClass("empty").text("${_("Please select the columns you would like to see in this chart.")}");
        }
      }
    }
  }

  function getGraphType() {
    var _type = "";
    if ($("#blueprintBars").hasClass("active")) {
      _type = $.jHueBlueprint.TYPES.BARCHART;
    }
    if ($("#blueprintLines").hasClass("active")) {
      _type = $.jHueBlueprint.TYPES.LINECHART;
    }
    if ($("#blueprintMap").hasClass("active")) {
      _type = $.jHueBlueprint.TYPES.MAP;
    }
    return _type;
  }

  var hasBeenPredicted = false;
  function predictGraph() {
    if (!hasBeenPredicted) {
      hasBeenPredicted = true;
      var _firstAllString, _firstAllNumeric;
      for (var i = 1; i < $(".resultTable>thead>tr>th").length; i++) {
        var _isNumeric = true;
        $(".resultTable>tbody>tr>td:nth-child(" + (i + 1) + ")").each(function (cnt) {
          if (!$.isNumeric($.trim($(this).text()))) {
            _isNumeric = false;
          }
        });
        if (_firstAllString == null && !_isNumeric) {
          _firstAllString = i + 1;
        }
        if (_firstAllNumeric == null && _isNumeric) {
          _firstAllNumeric = i + 1;
        }
      }
      if (_firstAllString != null && _firstAllNumeric != null) {
        $("#blueprintBars").addClass("active");
        $("#blueprintAxis").removeClass("hide");
        $("#blueprintLatLng").addClass("hide");
        $("#blueprintX").val(_firstAllString);
        $("#blueprintY").val(_firstAllNumeric);
      }
    }
    generateGraph(getGraphType());
  }


  $("a[data-toggle='tab']").on("shown", function (e) {
    if ($(e.target).attr("href") == "#chart") {
      predictGraph();
    }
  });

  $(".blueprintSelect").on("change", function () {
    generateGraph(getGraphType())
  });

  $("#blueprintBars").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    generateGraph($.jHueBlueprint.TYPES.BARCHART)
  });
  $("#blueprintLines").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    generateGraph($.jHueBlueprint.TYPES.LINECHART)
  });
  $("#blueprintMap").on("click", function () {
    $("#blueprintAxis").addClass("hide");
    $("#blueprintLatLng").removeClass("hide");
    generateGraph($.jHueBlueprint.TYPES.MAP)
  });

  % if app_name == 'impala':
    window.onbeforeunload = function(e) {
      $.ajax({url: "${ url(app_name + ':close_operation', query.id) }", type: 'post', async: false});
    }
  % endif
});
</script>

${ commonfooter(request, messages) | n,unicode }
