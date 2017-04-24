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
    $("#tableAnalysis .stats-refresh").data("refreshUrl", options.refreshUrl);
    $("#tableAnalysis .stats-refresh").data("tableName", options.tableName);
    $("#tableAnalysis .stats-refresh").data("isTable", true);
    $("#tableAnalysisStats .content").css("opacity", ".5");
  }
  else {
    $("#tableAnalysis").hide();
    $("#columnAnalysis .stats-refresh").data("startUrl", options.statsUrl);
    $("#columnAnalysis .stats-refresh").data("refreshUrl", options.refreshUrl);
    $("#columnAnalysis .stats-refresh").data("termsUrl", options.termsUrl);
    $("#columnAnalysis .stats-refresh").data("columnName", options.columnName);
    $("#columnAnalysis .stats-refresh").data("errorLabel", options.errorLabel);
    $("#columnAnalysis .stats-refresh").data("isTable", false);
    $("#columnAnalysisStats .content").css("opacity", ".5");
    $("#columnAnalysisTerms .content").css("opacity", ".5");
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
        var _stats = "<table class='table table-condensed'>";
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
          $("#tableAnalysisStats .content").html(_stats);
          $("#tableAnalysisStats .content").css("opacity", "1");
        }
        else {
          data.stats.forEach(function (item) {
            _stats += "<tr><th>" + Object.keys(item)[0] + "</th><td>" + item[Object.keys(item)[0]] + "</td></tr>";
          });
          _stats += "</table>"
          $("#columnAnalysis .column-name").text(options.columnName);
          $("#columnAnalysisStats .content").html(_stats);
          $("#columnAnalysisStats .content").css("opacity", "1");
        }
        if (options.callback) {
          options.callback();
        }
      }
      else {
        $(document).trigger("error", options.errorLabel);
        $("#tableAnalysis").hide();
        $("#columnAnalysis").hide();
      }
    },
    error: function (e) {
      if (e.status == 500) {
        $(document).trigger("error", options.errorLabel);
        $("#tableAnalysis").hide();
        $("#columnAnalysis").hide();
      }
    }
  });
  loadTerms(options);
}

function loadTerms(options) {
  $.ajax({
    url: options.termsUrl,
    data: {},
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-Requested-With", "Hue");
    },
    dataType: "json",
    success: function (data) {
      if (data && data.status == 0) {
        if (data.terms.length > 0){
          $("#columnAnalysisTerms .alert").addClass("hide");
          var _terms = '<table class="table table-condensed">';
          data.terms.forEach(function(item){
            _terms += '<tr><td>' + item[0] + '</td>';
            _terms += '<td style="width: 40px">';
            _terms += '<div class="progress">';
            _terms += '<div class="bar-label" data-bind="text:val.count">' + item[1] + '</div>';
            _terms += '<div class="bar bar-info" style="margin-top: -20px; width: ' + ((parseFloat(item[1]) / parseFloat(data.terms[0][1])) * 100) + '%"></div>';
            _terms += '</div>';
            _terms += '</td></tr>';
          });
          _terms += '</table>';
          $("#columnAnalysisTerms .content").html(_terms);
          $("#columnAnalysisTerms .content").css("opacity", "1");
        }
        else {
          $("#columnAnalysisTerms .alert").removeClass("hide");
          $("#columnAnalysisTerms .content").html("");
        }
      }
      else {
        $(document).trigger("error", options.errorLabel);
        $("#tableAnalysis").hide();
        $("#columnAnalysis").hide();
      }
    },
    error: function (e) {
      if (e.status == 500) {
        $(document).trigger("error", options.errorLabel);
        $("#tableAnalysis").hide();
        $("#columnAnalysis").hide();
      }
    }
  });
}

function showTableStats(statsUrl, refreshUrl, tableName, errorLabel, callback) {
  showStats({
    isTable: true,
    statsUrl: statsUrl,
    refreshUrl: refreshUrl,
    tableName: tableName,
    errorLabel: errorLabel,
    callback: callback
  });
}

function showColumnStats(statsUrl, refreshUrl, termsUrl, columnName, errorLabel, callback) {
  showStats({
    isTable: false,
    statsUrl: statsUrl,
    refreshUrl: refreshUrl,
    termsUrl: termsUrl,
    columnName: columnName,
    errorLabel: errorLabel,
    callback: callback
  });
}

function refreshLoop(el){
  $.get($(el).data("watchUrl"), function (data){
    if (data && data.status != -1 && !data.isSuccess && !data.isFailure){
      $(el).data("refreshTimeout", window.setTimeout(function(){
        refreshLoop($(el));
      }, 2000))
    }
    else {
      $(el).removeClass("fa-spin");
      $(el).parents(".popover").find(".content").css("opacity", "1");
      if (data.isSuccess){
        if (el.data("isTable")){
          showTableStats($(el).data("startUrl"), $(el).data("refreshUrl"), $(el).data("tableName"), $(el).data("errorLabel"));
        }
        else {
          showColumnStats($(el).data("startUrl"), $(el).data("refreshUrl"), $(el).data("termsUrl"), $(el).data("columnName"), $(el).data("errorLabel"));
        }
      }
      else {
        $(document).trigger("error", data.message);
      }
    }
  });
}

$(document).ready(function () {
  $(".stats-refresh").on("click", function () {
    $("#columnAnalysis .filter input").val("");
    var _this = $(this);
    _this.parents(".popover").find(".content").css("opacity", ".5");
    if (_this.hasClass("fa-spin")){
      _this.removeClass("fa-spin");
      _this.parents(".popover").find(".content").css("opacity", "1");
      window.clearTimeout(_this.data("refreshTimeout"));
    }
    else {
      _this.addClass("fa-spin");
      $.post(_this.data("refreshUrl"), function(data){
        if (data && data.status == 0 && data.watch_url != ""){
          _this.data("watchUrl", data.watch_url);
          _this.data("refreshTimeout", window.setTimeout(function(){
            refreshLoop(_this);
          }, 2000))
        }
      });
    }
  });
  $("#columnAnalysis .filter input").jHueDelayedInput(function(){
    $("#columnAnalysisTerms .content").css("opacity", ".5");
    loadTerms({
      errorLabel: $("#columnAnalysis .stats-refresh").data("errorLabel"),
      termsUrl: $("#columnAnalysis .stats-refresh").data("termsUrl") + $("#columnAnalysis .filter input").val()
    });
  });
});