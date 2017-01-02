## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="hueAceAutocompleter()">
  <style>
    .hue-ace-autocompleter {
      position: absolute;
      z-index: 100000;
      width: 500px;
      height: 250px;
      border: 1px solid #DDD;
      border-radius: 3px;
      display: flex;
      flex-direction: column;
      background-color: #FFF;
    }

    .autocompleter-header {
      flex: 1 1 30px;
      padding: 5px;
    }

    .autocompleter-list {
      flex: 1 1 100%;
      overflow-y: auto;
      padding: 0 5px;
    }

    .autocompleter-list > div {
      height: 19px;
      clear: both;
    }

    .autocompleter-list > div.selected {
      background-color: #F00;
    }

  </style>
  <script type="text/html" id="hue-ace-autocompleter">
    <div class="autocompleter-header"><div class="pull-right">header</div></div>
    <div class="autocompleter-list" data-bind="foreach: activeSuggestions">
      <div data-bind="css: { 'selected': $index() === $parent.selectedIndex() }"><div class="pull-left" data-bind="text: value"></div><div class="pull-right" data-bind="text: meta"></div></div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/javascript" charset="utf-8">
    (function () {
      var aceUtil = ace.require("ace/autocomplete/util");
      var HashHandler = ace.require("ace/keyboard/hash_handler").HashHandler;

      function HueAceAutocompleter (params, element) {
        var self = this;
        var snippet = params.snippet;
        var editor = params.editor;

        var autocompleter = new SqlAutocompleter3({ snippet: snippet, timeout: AUTOCOMPLETE_TIMEOUT });
        self.suggestions = autocompleter.autocomplete(editor.getTextBeforeCursor(), editor.getTextAfterCursor());
        self.activeSuggestions = ko.pureComputed(function () {
          if (self.suggestions.keywords) {
            return self.suggestions.keywords.suggestions();
          }
          return [];
        });

        self.selectedIndex = ko.observable(0);

        var session = editor.getSession();
        var pos = editor.getCursorPosition();

        var line = session.getLine(pos.row);
        var prefix = aceUtil.retrievePrecedingIdentifier(line, pos.column);

        self.base = session.doc.createAnchor(pos.row, pos.column - prefix.length);
        self.base.$insertRight = true;

        self.keyboardHandler = new HashHandler();
        self.keyboardHandler.bindKeys({
          "Up": function(editor) {
            if (self.selectedIndex() !== 0) {
              self.selectedIndex(self.selectedIndex() - 1);
            }
          },
          "Down": function(editor) {
            if (self.selectedIndex() !== self.activeSuggestions().length) {
              self.selectedIndex(self.selectedIndex() + 1);
            }
          },
          "Ctrl-Up|Ctrl-Home": function(editor) {
            console.log('start');
          },
          "Ctrl-Down|Ctrl-End": function(editor) {
            console.log('end');
          },
          "Esc": function(editor) {
            self.destroy();
          },
          "Return": function(editor) {
            editor.execCommand("insertstring", self.activeSuggestions()[self.selectedIndex()].value);
            editor.renderer.scrollCursorIntoView();
            self.destroy();
          },
          "Shift-Return": function(editor) {
            console.log('insert deleteSuffix');
          },
          "Tab": function(editor) {
            console.log('insert or down if nothing selected');
          },
          "PageUp": function(editor) {
            console.log('page up');
          },
          "PageDown": function(editor) {
            console.log('page down');
          }
        });

        var changeTimeout = -1;

        self.changeListener = function () {
          window.clearTimeout(changeTimeout);
          var cursor = editor.selection.lead;
          if (cursor.row != self.base.row || cursor.column < self.base.column) {
            self.destroy();
          } else {
            changeTimeout = window.setTimeout(self.updateCompletions, 200)
          }
        };

        self.blurListener = function () {
          console.log('blur');
          //self.destroy();
        };

        self.mousedownListener = function () {
          console.log('mousedown');
        };

        self.mousewheelListener = function () {
          console.log('mousewheel');
        };

        this.destroy = function () {
          self.base.detach();
          window.clearTimeout(changeTimeout);
          editor.keyBinding.removeKeyboardHandler(self.keyboardHandler);
          editor.off("changeSelection", self.changeListener);
          editor.off("blur", self.blurListener);
          editor.off("mousedown", self.mousedownListener);
          editor.off("mousewheel", self.mousewheelListener);
          $(element).remove();
        };

        editor.keyBinding.addKeyboardHandler(self.keyboardHandler);
        editor.on("changeSelection", self.changeListener);
        editor.on("blur", self.blurListener);
        editor.on("mousedown", self.mousedownListener);
        editor.on("mousewheel", self.mousewheelListener);
      }

      ko.components.register('hueAceAutocompleter', {
        viewModel: { createViewModel: function (params, componentInfo) {
          return new HueAceAutocompleter(params, componentInfo.element);
        }},
        template: { element: 'hue-ace-autocompleter' }
      });
    })();
  </script>
</%def>
