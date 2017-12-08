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

    editor.enableAutocomplete = function () {
      editor.setOptions({enableBasicAutocompletion: true, enableLiveAutocompletion: true});
    }

    editor.disableAutocomplete = function () {
      editor.setOptions({enableBasicAutocompletion: false, enableLiveAutocompletion: false});
    }

    editor.removeTextBeforeCursor = function (length) {
      var _r = new AceRange(this.getCursorPosition().row, this.getCursorPosition().column - length, this.getCursorPosition().row, this.getCursorPosition().column);
      editor.getSession().getDocument().remove(_r);
    }

    editor.getTextBeforeCursor = function (separator) {
      var _r = new AceRange(0, 0, this.getCursorPosition().row, this.getCursorPosition().column);
      return separator ? this.session.getTextRange(_r).split(separator).pop() : this.session.getTextRange(_r);
    }

    editor.removeTextAfterCursor = function (length) {
      var _r = new AceRange(this.getCursorPosition().row, this.getCursorPosition().column, this.getCursorPosition().row, this.getCursorPosition().column + length);
      editor.getSession().getDocument().remove(_r);
    }

    editor.getTextAfterCursor = function (separator) {
      var _r = new AceRange(this.getCursorPosition().row, this.getCursorPosition().column, this.session.getLength(), this.session.getRowLength(this.session.getLength()));
      return separator ? this.session.getTextRange(_r).split(separator).shift() : this.session.getTextRange(_r);
    }

    editor.getCursorScreenPosition = function () {
      return this.renderer.textToScreenCoordinates(this.getCursorPosition());
    }

    editor.showSpinner = function () {
      var _position = this.getCursorScreenPosition();
      if ($(".ace-spinner").length == 0) {
        $("<i class='fa fa-spinner fa-spin ace-spinner'></i>").appendTo(HUE_CONTAINER);
      }
      $(".ace-spinner").css("top", _position.pageY + "px").css("left", (_position.pageX - 4) + "px").show();
    }

    editor.hideSpinner = function () {
      $(".ace-spinner").hide();
    }

    editor.showFileButton = function () {
      var _position = this.getCursorScreenPosition();
      if ($(".ace-inline-button").length == 0) {
        $("<a class='btn btn-mini ace-inline-button'><i class='fa fa-ellipsis-h'></i></a>").appendTo(HUE_CONTAINER);
      }
      $(".ace-inline-button").css("top", _position.pageY + "px").css("left", (_position.pageX + 4) + "px").show();
      $(".ace-inline-button").off("click");
      return $(".ace-inline-button");
    }

    editor.hideFileButton = function () {
      $(".ace-inline-button").hide();
    }

    editor.clearAnnotations = function (type) {
      if (type === 'error') {
        this.session.setAnnotations(this.session.getAnnotations().filter(function (item) {
          return item.type === 'warning'
        }));
      }
      else if (type === 'warning') {
        this.session.setAnnotations(this.session.getAnnotations().filter(function (item) {
          return item.type === 'error'
        }));
      }
      else {
        this.session.clearAnnotations();
      }
    }

    editor.clearErrorsAndWarnings = function (type) {
      for (var id in this.session.getMarkers()) {
        var _marker = this.session.getMarkers()[id];
        var _condition = _marker.clazz == "ace_error-line" || _marker.clazz == "ace_warning-line";
        if (type === 'error') {
          _condition = _marker.clazz == "ace_error-line";
        }
        if (type === 'warning') {
          _condition = _marker.clazz == "ace_warning-line";
        }
        if (_condition) {
          this.session.removeMarker(_marker.id);
        }
      }
      editor.clearAnnotations(type);
    }

    editor.clearErrors = function () {
      editor.clearErrorsAndWarnings('error');
    }

    editor.clearWarnings = function () {
      editor.clearErrorsAndWarnings('warning');
    }

    editor.addError = function (message, line) {
      var _range = new AceRange(line, 0, line, this.session.getLine(line).length);
      this.session.addMarker(_range, "ace_error-line");
      var errors = this.session.getAnnotations();
      errors.push({
        row: _range.start.row,
        column: _range.start.column,
        raw: message,
        text: message,
        type: "error"
      });
      this.session.setAnnotations(errors);
    }

    editor.addWarning = function (message, line) {
      var _range = new AceRange(line, 0, line, this.session.getLine(line).length);
      this.session.addMarker(_range, "ace_warning-line");
      var warnings = this.session.getAnnotations();
      warnings.push({
        row: _range.start.row,
        column: _range.start.column,
        raw: message,
        text: message,
        type: "warning"
      });
      this.session.setAnnotations(warnings);
    }

    return editor;
  }
}
catch (e) {
  console.error("You need to include ace.js before including this snippet.")
}
