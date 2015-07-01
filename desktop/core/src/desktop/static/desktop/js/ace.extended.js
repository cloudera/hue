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

try {
  ace.originalEdit = ace.edit;
  var AceRange = ace.require('ace/range').Range;
  ace.edit = function(el) {
    var editor = ace.originalEdit(el);

    editor.enableAutocomplete = function() {
      editor.setOptions({enableBasicAutocompletion: true, enableLiveAutocompletion: true});
    }

    editor.disableAutocomplete = function() {
      editor.setOptions({enableBasicAutocompletion: false, enableLiveAutocompletion: false});
    }

    editor.getTextBeforeCursor = function (separator) {
      var _r = new AceRange(0, 0, this.getCursorPosition().row, this.getCursorPosition().column);
      return this.session.getTextRange(_r);
    }

    editor.getCursorScreenPosition = function () {
      return this.renderer.textToScreenCoordinates(this.getCursorPosition());
    }

    editor.showSpinner = function () {
      var _position = this.getCursorScreenPosition();
      if ($(".ace-spinner").length == 0) {
        $("<i class='fa fa-spinner fa-spin ace-spinner'></i>").appendTo($("body"));
      }
      $(".ace-spinner").css("top", _position.pageY + "px").css("left", (_position.pageX - 4) + "px").show();
    }

    editor.hideSpinner = function () {
      $(".ace-spinner").hide();
    }

    editor.showFileButton = function () {
      var _position = this.getCursorScreenPosition();
      if ($(".ace-inline-button").length == 0) {
        $("<a class='btn btn-mini ace-inline-button'><i class='fa fa-ellipsis-h'></i></a>").appendTo($("body"));
      }
      $(".ace-inline-button").css("top", _position.pageY + "px").css("left", (_position.pageX + 4) + "px").show();
      $(".ace-inline-button").off("click");
      return $(".ace-inline-button");
    }

    editor.hideFileButton = function () {
      $(".ace-inline-button").hide();
    }

    editor.clearErrors = function() {
      for (var id in this.session.getMarkers()) {
        var _marker = this.session.getMarkers()[id];
        if (_marker.clazz == "ace_error-line"){
          this.session.removeMarker(_marker.id);
        }
      };
      this.session.clearAnnotations();
    }

    editor.addError = function (message, line) {
      var _range = new AceRange(line, 0, line, this.session.getLine(line).length);
      this.session.addMarker(_range, "ace_error-line");
      this.session.setAnnotations([{
        row: _range.start.row,
        column: _range.start.column,
        raw: message,
        text: message,
        type: "error"
      }]);
    }

    return editor;
  }
}
catch (e) {
  console.error("You need to include ace.js before including this snippet.")
}
