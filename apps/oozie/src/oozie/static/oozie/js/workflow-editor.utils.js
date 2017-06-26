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

function toggleProperties(widget) {
  if (widget.oozieMovable()) {
    var _el = $("#wdg_" + widget.id());
    if (!widget.ooziePropertiesExpanded()) {
      setLastExpandedWidget(widget);
      _el.find(".prop-editor").show();
      widget.ooziePropertiesExpanded(true);
    } else {
      if (widget.oozieExpanded()) {
        exposeOverlayClickHandler();
      } else {
        _el.find(".prop-editor").hide();
        widget.ooziePropertiesExpanded(false);
      }
    }
    $(document).trigger("drawArrows");
  }
}

var _linkMappingTimeout = -1;
$(document).on("drawArrows", function () {
  window.clearTimeout(_linkMappingTimeout);
  if (typeof renderChangeables != 'undefined') {
    _linkMappingTimeout = window.setTimeout(renderChangeables, 25);
  }
});

$(document).on("removeArrows", function () {
  $("canvas").remove();
});
