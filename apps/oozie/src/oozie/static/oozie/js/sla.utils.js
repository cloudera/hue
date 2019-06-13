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

function getSLAStatusLabel(status) {
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
  return '<span class="slaStatus label ' + klass + '">' + status + '</span>'
}

function getXAxisColor(status) {
  if (['MET'].indexOf(status.toUpperCase()) > -1) {
    return $.jHueBlueprint.COLORS.GREEN;
  }
  else if (['NOT_STARTED', 'IN_PROCESS'].indexOf(status.toUpperCase()) > -1) {
    return $.jHueBlueprint.COLORS.ORANGE;
  }
  else {
    return $.jHueBlueprint.COLORS.RED;
  }
}

function getSLArow(row) {
  return [
    getSLAStatusLabel(row.slaStatus),
    emptyStringIfNull(row.appName),
    emptyStringIfNull(row.appType),
    '<a href="/hue/jobbrowser/#!id=' + row.id + '">' + row.id + '</a>',
    '<span class="nominalTime">' + emptyStringIfNull(row.nominalTime) + '</span>',
    '<span class="expectedStart">' + emptyStringIfNull(row.expectedStart) + '</span>',
    '<span class="actualStart">' + emptyStringIfNull(row.actualStart) + '</span>',
    '<span class="expectedEnd">' + emptyStringIfNull(row.expectedEnd) + '</span>',
    '<span class="actualEnd">' + emptyStringIfNull(row.actualEnd) + '</span>',
    emptyStringIfNull(row.expectedDuration),
    emptyStringIfNull(row.actualDuration),
    emptyStringIfNull(row.jobStatus),
    emptyStringIfNull(row.user),
    emptyStringIfNull(row.lastModified)
  ];
}

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


function updateSLAChart(slaTable, labels, limit) {
  $("#slaChart").jHueBlueprint("reset");
  var rows = slaTable.fnGetNodes();
  var from = limit != null && limit < rows.length ? rows.length - limit : 0;
  var to = rows.length;
  for (var i = from; i < to; i++) {
    function getOptions(differenceCellValue, label, color) {
      return {
        data: [
          [moment($(rows[i]).find("span.nominalTime").html()).valueOf(), (moment(differenceCellValue).valueOf() - moment($(rows[i]).find("span.nominalTime").html()).valueOf())]
        ],
        label: label,
        yAxisFormatter: function (val, axis) {
          return msToTime(val);
        },
        type: $.jHueBlueprint.TYPES.POINTCHART,
        color: color,
        isDateTime: true,
        timeFormat: "<span data-link='"+ $(rows[i]).find("a").attr("href") +"' style='color:" + getXAxisColor($(rows[i]).find(".slaStatus").text()) + "'>%Y-%m-%d %H:%M:%S</span>",
        fill: false,
        height: 300,
        tooltipAddon: labels.TOOLTIP_ADDON,
        yTooltipFormatter: function (val) {
          return msToTime(val);
        },
        onItemClick: function (pos, item) {
          if (!item) { // detect if it's a label click
            $(".flot-x-axis .tickLabel").each(function(cnt, label){
              if (pos.pageX >= $(label).offset().left && pos.pageX <= $(label).offset().left + $(label).width() && pos.pageY >= $(label).offset().top && pos.pageY <= $(label).offset().top + $(label).height()){
                location.href = $(label).find("span").data("link");
              }
            });
          }
          if (item && $(slaTable.fnGetNodes()[item.dataIndex]).find("a").length > 0) {
            location.href = $(slaTable.fnGetNodes()[item.dataIndex]).find("a").attr("href");
          }
        }
      }
    }

    if ($("#slaChart").data('plugin_jHueBlueprint') == null) {
      $("#slaChart").jHueBlueprint(getOptions($(rows[i]).find("span.nominalTime").html(), (i == 0 ? labels.NOMINAL_TIME : null), $.jHueBlueprint.COLORS.ORANGE));
    }
    else {
      $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("span.nominalTime").html(), (i == 0 ? labels.NOMINAL_TIME : null), $.jHueBlueprint.COLORS.ORANGE));
    }
    if ($(rows[i]).find("span.expectedStart").html().trim() != "") {
      $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("span.expectedStart").html(), (i == 0 ? labels.EXPECTED_START : null), $.jHueBlueprint.COLORS.BLUE));
    }
    if ($(rows[i]).find("span.actualStart").html().trim() != "") {
      $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("span.actualStart").html(), (i == 0 ? labels.ACTUAL_START : null), $.jHueBlueprint.COLORS.GREEN));
    }
    if ($(rows[i]).find("span.expectedEnd").html().trim() != "") {
      $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("span.expectedEnd").html(), (i == 0 ? labels.EXPECTED_END : null), $.jHueBlueprint.COLORS.FALAFEL));
    }
    if ($(rows[i]).find("span.actualEnd").html().trim() != "") {
      $("#slaChart").jHueBlueprint("add", getOptions($(rows[i]).find("span.actualEnd").html(), (i == 0 ? labels.ACTUAL_END : null), $.jHueBlueprint.COLORS.TURQUOISE));
    }
    $("#yAxisLabel").removeClass("hide");

  }
}
