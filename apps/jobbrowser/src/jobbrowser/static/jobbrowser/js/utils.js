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

var Utils = {
  SUCCEEDED_ARRAY: ['SUCCEEDED', 'OK', 'DONE'],
  RUNNING_ARRAY: ['RUNNING', 'ACCEPTED', 'READY',
    'PREP', 'WAITING', 'SUSPENDED',
    'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED',
    'SUBMITTED', 'SUSPENDEDWITHERROR', 'PAUSEDWITHERROR', 'FINISHING', 'STARTED']
};

function initLogsElement(element) {
  element.data("logsAtEnd", true);
  element.scroll(function () {
    element.data("logsAtEnd", ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight));
  });
  element.css("overflow", "auto").height($(window).height() - element.offset().top - 80);
}

function appendAndScroll(element, logs) {
  var newLines = logs.split("\n").slice(element.text().split("\n").length);
  if (newLines.length > 0) {
    element.html(element.text() + newLines.join("\n") + "\n");
  }
  if (element.data("logsAtEnd")) {
    element.scrollTop(element[0].scrollHeight - element.height());
  }
}

function resizeLogs(element) {
  element.css("overflow", "auto").height($(window).height() - element.offset().top - 80);
}

var _resizeTimeout = -1;

function enableResizeLogs() {
  $(window).on("resize", function () {
    $(document).trigger("resized");
  });
}

function getQueryStringParameter(name) {
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(location.search);
  return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function getStatusClass(status, prefix) {
  if (prefix == null) {
    prefix = "label-";
  }
  var klass = "";
  if (Utils.SUCCEEDED_ARRAY.indexOf(status) > -1) {
    klass = prefix + "success";
  }
  else if (Utils.RUNNING_ARRAY.indexOf(status) > -1) {
    klass = prefix + "warning";
  }
  else {
    klass = prefix + "important";
    if (prefix == "bar-") {
      klass = prefix + "danger";
    }
  }
  return klass;
}

function emptyStringIfNull(obj) {
  if (obj != null && obj != undefined) {
    return obj;
  }
  return "";
}

jQuery.fn.dataTableExt.oSort['title-numeric-asc'] = function (a, b) {
  var x = a.match(/title="*(-?[0-9\.]+)/)[1];
  var y = b.match(/title="*(-?[0-9\.]+)/)[1];
  x = parseFloat(x);
  y = parseFloat(y);
  return ((x < y) ? -1 : ((x > y) ? 1 : 0));
};

jQuery.fn.dataTableExt.oSort['title-numeric-desc'] = function (a, b) {
  var x = a.match(/title="*(-?[0-9\.]+)/)[1];
  var y = b.match(/title="*(-?[0-9\.]+)/)[1];
  x = parseFloat(x);
  y = parseFloat(y);
  return ((x < y) ? 1 : ((x > y) ? -1 : 0));
};
