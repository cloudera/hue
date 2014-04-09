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
    element.text(element.text() + newLines.join("\n") + "\n");
  }
  if (element.data("logsAtEnd")) {
    element.scrollTop(element[0].scrollHeight - element.height());
  }
}

function resizeLogs(element) {
  element.css("overflow", "auto").height($(window).height() - element.offset().top - 80);
}

var _resizeTimeout = -1;
var _winWidth = $(window).width();
var _winHeight = $(window).height();

function enableResizeLogs() {
  $(window).on("resize", function () {
    window.clearTimeout(_resizeTimeout);
    _resizeTimeout = window.setTimeout(function () {
      // prevents endless loop in IE8
      if (_winWidth != $(window).width() || _winHeight != $(window).height()) {
        $(document).trigger("resized");
        _winWidth = $(window).width();
        _winHeight = $(window).height();
      }
    }, 200);
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

function hellipsify() {
  var MAX_LENGTH = 20;
  $(".hellipsify").each(function () {
    var _this = $(this);
    if (_this.text().length > MAX_LENGTH) {
      var _oText = _this.text();
      var _clone = $("<div>");
      _clone.html(_this.html());
      _clone.css("position", "absolute").css("background-color", "#F5F5F5");
      _clone.css("top", (_this.is("a") ? _this.position().top + 3 : _this.position().top)).css("left", _this.position().left)
      _clone.css("z-index", "9999").css("display", "none");
      _clone.appendTo($("body"));
      _clone.mouseout(function () {
        $(this).hide();
      })
      $(this).html(_oText.substr(0, MAX_LENGTH - 1) + "&hellip;&nbsp;");
      var _eye = $("<button class='nochrome btn-small'></button>");
      _eye.html("<i class='fa fa-eye'></i>");
      _eye.css("cursor", "pointer");
      _eye.on("click", function (e) {
        e.stopImmediatePropagation();
        e.preventDefault();
        _clone.show();
        _this.tooltip("hide");
      });
      _eye.appendTo(_this);
      _this.data("original-text", _oText);
      _this.tooltip({
        title: _oText,
        placement: "right"
      });
    }
  });
}