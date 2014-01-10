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

<style type="text/css">
  .label-with-margin {
    margin-right: 20px;
  }

  .checkbox {
    margin-bottom: 2px !important;
  }

  input[type='checkbox'] {
    margin-right: 5px !important;
    margin-top: 3px;
  }

  th {
    vertical-align: middle !important;
  }

  #yAxisLabel {
    -webkit-transform: rotate(270deg);
    -moz-transform: rotate(270deg);
    -o-transform: rotate(270deg);
    writing-mode: lr-tb;
    margin-left: -82px;
    margin-top: 120px;
    position: absolute;
  }

</style>

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">
    <div class="pull-left" style="margin-right: 20px;margin-top: 2px">${_('Search SLA')}</div>
    <form class="form-inline" id="searchForm" method="GET" action="." style="margin-bottom: 4px">
      <label>
        ${_('Name or Id')}
        <input type="text" name="job_name" class="searchFilter input-xlarge search-query" placeholder="${_('Job Name or Id (required)')}">
      </label>
      <label class="checkbox label-with-margin">
        <input type="checkbox" name="isParent" class="searchFilter">
        ${ _('This is the parent ID') }
      </label>
      <label class="label-with-margin">
        ${ _('Start') }
        <input type="text" name="start_0" class="input-small date" value="" placeholder="${_('Date in GMT')}"><input type="text" name="start_1" class="input-small time" value="">
      </label>
      <label>
        ${ _('End') }
        <input type="text" name="end_0" class="input-small date" value="" placeholder="${_('Date in GMT')}"><input type="text" name="end_1" class="input-small time" value="">
      </label>
    </form>
    </h1>
    <div class="card-body">
      <p>
        <div class="loader hide" style="text-align: center;margin-top: 20px">
          <!--[if lte IE 9]>
              <img src="/static/art/spinner-big.gif" />
          <![endif]-->
          <!--[if !IE]> -->
            <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
          <!-- <![endif]-->
        </div>

        <div class="search-something center empty-wrapper">
          <i class="fa fa-search"></i>
          <h1>${_('Use the form above to search for SLAs.')}</h1>
          <br/>
        </div>

        <div class="no-results center empty-wrapper hide">
          <i class="fa fa-frown-o"></i>
          <h1>${_('The server returned no results.')}</h1>
          <br/>
        </div>

        <div class="results hide">
          <ul class="nav nav-tabs">
            <li class="active"><a href="#slaListTab" data-toggle="tab">${ _('List') }</a></li>
            <li><a href="#chartTab" data-toggle="tab">${ _('Chart') }</a></li>
          </ul>

          <div class="tab-content" style="padding-bottom:200px">
            <div class="tab-pane active" id="slaListTab">
              <div class="tabbable">
                <div class="tab-content">
                  <table id="slaTable" class="table table-striped table-condensed">
                    <thead>
                      <th>${_('Status')}</th>
                      <th>${_('Name')}</th>
                      <th>${_('Type')}</th>
                      <th>${_('ID')}</th>
                      <th>${_('Nominal Time')}</th>
                      <th>${_('Expected Start')}</th>
                      <th>${_('Actual Start')}</th>
                      <th>${_('Expected End')}</th>
                      <th>${_('Actual End')}</th>
                      <th>${_('Expected Duration')}</th>
                      <th>${_('Actual Duration')}</th>
                      <th>${_('Job Status')}</th>
                      <th>${_('User')}</th>
                      <th>${_('Last Modified')}</th>
                    </thead>
                    <tbody>
                    </tbody>
                  </table>
                </div>
              </div>

            </div>

            <div class="tab-pane" id="chartTab">
              <div id="yAxisLabel" class="hide">${_('Time since Nominal Time')}</div>
              <div id="slaChart"></div>
            </div>
          </div>
        </div>
      </p>
    </div>
  </div>
</div>

<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.selection.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.time.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js"></script>

<script type="text/javascript" charset="utf-8">
  var slaTable;
  function performSearch(id) {
    if ((id != null || $("input[name='job_name']").val().trim()) != "" && slaTable) {
      $(".results").addClass("hide");
      $(".loader").removeClass("hide");
      $(".search-something").addClass("hide");
      var IN_DATETIME_FORMAT = "MM/DD/YYYY hh:mm A";
      var OUT_DATETIME_FORMAT = "YYYY-MM-DD[T]HH:mm[Z]";
      var _postObj = {
        "job_name": id != null ? id : $("input[name='job_name']").val()
      };

      if ($("input[name='isParent']").is("checked")) {
        _postObj.isParent = true;
      }
      if ($("input[name='start_0']").val() != "" && $("input[name='start_1']").val() != "") {
        _postObj.start = moment($("input[name='start_0']").val() + " " + $("input[name='start_1']").val(), IN_DATETIME_FORMAT).format(OUT_DATETIME_FORMAT);
      }
      if ($("input[name='end_0']").val() != "" && $("input[name='end_1']").val() != "") {
        _postObj.end = moment($("input[name='end_0']").val() + " " + $("input[name='end_1']").val(), IN_DATETIME_FORMAT).format(OUT_DATETIME_FORMAT)
      }

      $.post("${ url('oozie:list_oozie_sla') }?format=json", _postObj, function (data) {
        $(".loader").addClass("hide");
        slaTable.fnClearTable();
        if (data['oozie_slas'] && data['oozie_slas'].length > 0) {
          $(".no-results").addClass("hide");
          $(".results").removeClass("hide");
          for (var i = 0; i < data['oozie_slas'].length; i++) {
            slaTable.fnAddData(getSLArow(data['oozie_slas'][i]));
          }
        }
        else {
          $(".results").addClass("hide");
          $(".no-results").removeClass("hide");
        }
      });
    }
  }

  function getSLArow(row) {
    return [
      getStatusClass(row.slaStatus),
      emptyStringIfNull(row.appName),
      emptyStringIfNull(row.appType),
      '<a href="' + row.appUrl + '" data-row-selector="true">' + row.id + '</a>',
      emptyStringIfNull(row.nominalTime),
      emptyStringIfNull(row.expectedStart),
      emptyStringIfNull(row.actualStart),
      emptyStringIfNull(row.expectedEnd),
      emptyStringIfNull(row.actualEnd),
      emptyStringIfNull(row.expectedDuration),
      emptyStringIfNull(row.actualDuration),
      emptyStringIfNull(row.jobStatus),
      emptyStringIfNull(row.user),
      emptyStringIfNull(row.lastModified)
    ];
  }

  function getStatusClass(status) {
    var klass = "";
    if (['MET'].indexOf(status.toUpperCase()) > -1) {
      klass = "label-success";
    }
    else if (['NOT_STARTED', 'IN_PROCESS'].indexOf(status.toUpperCase()) > -1) {
      klass = "label-warning";
    }
    else {
      klass = "label-important";
    }
    return '<span class="label ' + klass + '">' + status + '</span>'
  }

  function emptyStringIfNull(obj) {
    if (obj != null && obj != undefined) {
      return obj;
    }
    return "";
  }

  $(document).ready(function () {
    $("a[data-row-selector='true']").jHueRowSelector();

    $("*[rel=tooltip]").tooltip();

    $("input[name='start_0']").val(moment().subtract('days', 7).format("MM/DD/YYYY"));
    $("input[name='start_1']").val(moment().subtract('days', 7).format("hh:mm A"));
    $("input[name='end_0']").val(moment().format("MM/DD/YYYY"));
    $("input[name='end_1']").val(moment().format("hh:mm A"));


    $.getJSON("${url('oozie:list_oozie_workflows')}?format=json&justsla=true", function (data) {
      var _autocomplete = [];
      $(data).each(function (iWf, item) {
        _autocomplete.push(item.id);
      });
      $("input[name='job_name']").typeahead({
        source: _autocomplete,
        updater: function (item) {
          performSearch(item);
          return item;
        }
      });
    });

    $("input[name='job_name']").on("keydown", function (e) {
      if (e.keyCode == 13) {
        performSearch();
      }
    });

    slaTable = $("#slaTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bAutoWidth": false,
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}"
      },
      "fnDrawCallback": function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    $(".dataTables_wrapper").css("min-height", "0");
    $(".dataTables_filter").hide();

    function msToTime(millis) {
      var s = Math.abs(millis);
      var ms = s % 1000;
      s = (s - ms) / 1000;
      var secs = s % 60;
      s = (s - secs) / 60;
      var mins = s % 60;
      var hrs = (s - mins) / 60;
      return (millis < 0 ? "-" : "") + (hrs < 10 ? "0" : "") + hrs + ":" + (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
    }

    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#chartTab") {
        window.setTimeout(function () {
          $("#slaChart").jHueBlueprint("reset");
          var rows = slaTable.fnGetNodes();
          for (var i = 0; i < rows.length; i++) {
            function getOptions(differenceCellValue, label, color) {
              return {
                data: [
                  [moment($(rows[i]).find("td:eq(4)").html()).valueOf(), (moment(differenceCellValue).valueOf() - moment($(rows[i]).find("td:eq(4)").html()).valueOf())]
                ],
                label: label,
                yAxisFormatter: function (val, axis) {
                  return msToTime(val);
                },
                type: $.jHueBlueprint.TYPES.POINTCHART,
                color: color,
                isDateTime: true,
                timeFormat: "<span style='color:" + ($(rows[i]).find("td:eq(4)").text().toUpperCase() == "MET" ? $.jHueBlueprint.COLORS.GREEN : $.jHueBlueprint.COLORS.RED) + "'>%Y-%m-%d %H:%M:%S</span>",
                fill: false,
                height: 300,
                yTooltipFormatter: function (val) {
                  return msToTime(val);
                },
                onItemClick: function (pos, item) {
                  if (item) {
                    location.href = $(slaTable.fnGetNodes()[item.dataIndex]).find("a").attr("href");
                  }
                }
              }
            }

            if ($("#slaChart").data('plugin_jHueBlueprint') == null) {
              $("#slaChart").jHueBlueprint(getOptions($(rows[i]).find("td:eq(4)").html(), (i == 0 ? "${_('Nominal Time')}" : null), $.jHueBlueprint.COLORS.ORANGE));
            }
            else {
              $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("td:eq(4)").html(), (i == 0 ? "${_('Nominal Time')}" : null), $.jHueBlueprint.COLORS.ORANGE));
            }
            if ($(rows[i]).find("td:eq(5)").html().trim() != "") {
              $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("td:eq(5)").html(), (i == 0 ? "${_('Expected Start')}" : null), $.jHueBlueprint.COLORS.BLUE));
            }
            if ($(rows[i]).find("td:eq(6)").html().trim() != "") {
              $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("td:eq(6)").html(), (i == 0 ? "${_('Actual Start')}" : null), $.jHueBlueprint.COLORS.GREEN));
            }
            if ($(rows[i]).find("td:eq(7)").html().trim() != "") {
              $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("td:eq(7)").html(), (i == 0 ? "${_('Expected End')}" : null), $.jHueBlueprint.COLORS.FALAFEL));
            }
            if ($(rows[i]).find("td:eq(8)").html().trim() != "") {
              $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("td:eq(8)").html(), (i == 0 ? "${_('Actual End')}" : null), $.jHueBlueprint.COLORS.TURQUOISE));
            }
            $("#yAxisLabel").removeClass("hide");
          }
        }, 300)
      }
    });
  });
</script>

${ utils.decorate_datetime_fields() }

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $("input[name='start_0']").parent().datepicker().on("changeDate", function () {
      performSearch();
    });

    $("input[name='end_0']").parent().datepicker().on("changeDate", function () {
      performSearch();
    });
    $("input[name='start_1']").on("change", function (e) {
      // the timepicker plugin doesn't have a change event handler
      // so we need to wait a bit to handle in with the default field event
      window.setTimeout(function () {
        performSearch();
      }, 200);
    });

    $("input[name='end_1']").on("change", function () {
      window.setTimeout(function () {
        performSearch();
      }, 200);
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
