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

function linkWidgets(fromId, toId) {
  var _from = $("#wdg_" + (typeof fromId == "function" ? fromId() : fromId));
  var _to = $("#wdg_" + (typeof toId == "function" ? toId() : toId));
  if (_from.length > 0 && _to.length > 0) {
    var $painter = $(document.body);

    if ($('.oozie_workflowComponents').length > 0){
      $painter = $('.oozie_workflowComponents');
    }

    var _fromCenter = {
      x: _from.position().left + _from.outerWidth() / 2,
      y: _from.position().top + _from.outerHeight() + 3
    }

    var _toCenter = {
      x: _to.position().left + _to.outerWidth() / 2,
      y: _to.position().top - 5
    }

    var _curveCoords = {};

    if (_fromCenter.x == _toCenter.x) {
      _curveCoords.x = _fromCenter.x;
      _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
    } else {
      if (_fromCenter.x > _toCenter.x) {
        _fromCenter.x = _fromCenter.x - 5;
        _toCenter.x = _toCenter.x + 5;
      } else {
        _fromCenter.x = _fromCenter.x + 5;
        _toCenter.x = _toCenter.x - 5;
      }
      _curveCoords.x = _fromCenter.x - (_fromCenter.x - _toCenter.x) / 4;
      _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
    }

    $painter.curvedArrow({
      p0x: _fromCenter.x,
      p0y: _fromCenter.y,
      p1x: _curveCoords.x,
      p1y: _curveCoords.y,
      p2x: _toCenter.x,
      p2y: _toCenter.y,
      lineWidth: 2,
      size: 10,
      strokeStyle: viewModel.isEditing() ? '#e5e5e5' : '#dddddd'
    });
  }
}

function drawArrows() {
  $("canvas").remove();
  if (viewModel.oozieColumns()[0].rows().length > 3) {
    var _links = viewModel.workflow.linkMapping();
    Object.keys(_links).forEach(function (id) {
      if (_links[id].length > 0) {
        _links[id].forEach(function (nextId) {
          linkWidgets(id, nextId);
        });
      }
    });
  }
}

huePubSub.subscribe('draw.graph.arrows', drawArrows);

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
