// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

function showStats(options) {
  if (options.isTable) {
    $("#columnAnalysis").hide();
    $("#tableAnalysis .stats-refresh").data("startUrl", options.statsUrl);
    $("#tableAnalysis .stats-refresh").data("tableName", options.tableName);
    $("#tableAnalysis .popover-content").css("opacity", ".5");
  }
  else {
    $("#tableAnalysis").hide();
    $("#columnAnalysis .stats-refresh").data("startUrl", options.statsUrl);
    $("#columnAnalysis .stats-refresh").data("columnName", options.columnName);
    $("#columnAnalysis .popover-content").css("opacity", ".5");
  }
  $.ajax({
    url: options.statsUrl,
    data: {},
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-Requested-With", "Hue");
    },
    dataType: "json",
    success: function (data) {
      if (data && data.status == 0) {
        var _stats = "<table class='table table-striped'>";
        if (options.isTable) {
          data.stats.forEach(function (item) {
            _stats += "<tr><th>" + item.data_type + "</th><td>" + item.comment + "</td></tr>";
            if (item.data_type == "COLUMN_STATS_ACCURATE") {
              if (item.comment == "false") {
                $("#tableAnalysis .stats-warning").show();
              }
              else {
                $("#tableAnalysis .stats-warning").hide();
              }
            }
          });
          _stats += "</table>"
          $("#tableAnalysis .table-name").text(options.tableName);
          $("#tableAnalysis .popover-content").html(_stats);
          $("#tableAnalysis .popover-content").css("opacity", "1");
        }
        else {
          data.stats.forEach(function (item) {
            _stats += "<tr><th>" + Object.keys(item)[0] + "</th><td>" + item[Object.keys(item)[0]] + "</td></tr>";
          });
          _stats += "</table>"
          $("#columnAnalysis .column-name").text(options.columnName);
          $("#columnAnalysis .popover-content").html(_stats);
          $("#columnAnalysis .popover-content").css("opacity", "1");
        }
        if (options.callback) {
          options.callback();
        }
      }
      else {
        $(document).trigger("error", "${ _('There was a problem loading the table stats.') }");
        $("#tableAnalysis").hide();
        $("#columnAnalysis").hide();
      }
    },
    error: function (e) {
      if (e.status == 500) {
        $(document).trigger("error", "${ _('There was a problem loading the table stats.') }");
        $("#tableAnalysis").hide();
        $("#columnAnalysis").hide();
      }
    }
  });
}

function showTableStats(statsUrl, tableName, callback) {
  showStats({
    isTable: true,
    statsUrl: statsUrl,
    tableName: tableName,
    callback: callback
  });
}

function showColumnStats(statsUrl, columnName, callback) {
  showStats({
    isTable: false,
    statsUrl: statsUrl,
    columnName: columnName,
    callback: callback
  });
}

$(document).ready(function () {
  $("#tableAnalysis .stats-refresh").on("click", function () {
    showTableStats($("#tableAnalysis .stats-refresh").data("startUrl"), $("#tableAnalysis .stats-refresh").data("tableName"));
  });

  $("#columnAnalysis .stats-refresh").on("click", function () {
    showColumnStats($("#columnAnalysis .stats-refresh").data("startUrl"), $("#columnAnalysis .stats-refresh").data("columnName"));
  });
});