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

function initLogsElement(element) {
  element.data("logsAtEnd", true);
  element.scroll(function () {
    element("logsAtEnd", ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight));
  });
  element.css("overflow", "auto").height($(window).height() - element.offset().top - 50);
}

function appendAndScroll(element, logs) {
  var newLines = logs.split("\n").slice(element.text().split("\n").length);
  element.text(element.text() + newLines.join("\n"));
  if (element.data("logsAtEnd")) {
    element.scrollTop(element[0].scrollHeight - element.height());
  }
}

function resizeLogs(element) {
  element.css("overflow", "auto").height($(window).height() - element.offset().top - 50);
}

var resizeTimeout = -1;
var winWidth = $(window).width();
var winHeight = $(window).height();

$(window).on("resize", function () {
  window.clearTimeout(resizeTimeout);
  resizeTimeout = window.setTimeout(function () {
    // prevents endless loop in IE8
    if (winWidth != $(window).width() || winHeight != $(window).height()) {
      $(document).trigger("resized");
      winWidth = $(window).width();
      winHeight = $(window).height();
    }
  }, 200);
});
