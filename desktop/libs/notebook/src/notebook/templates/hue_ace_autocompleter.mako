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
      position: fixed;
      z-index: 100000;
      width: 500px;
      height: 250px;
      border: 1px solid #DDD;
      display: flex;
      flex-direction: column;

      border-radius: 2px;
      background-color: #FFF;
      -webkit-box-shadow: 0 2px 8px rgba(0,0,0,.18);
      box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.18), 0 2px 8px 0 rgba(0, 0, 0, 0.13);
    }

    .autocompleter-header {
      flex: 1 1 30px;
      padding: 5px;
    }

    .autocompleter-list {
      position: relative;
      flex: 1 1 100%;
      overflow-y: auto;
    }

    .autocompleter-list > div {
      height: 19px;
      clear: both;
      background-color: #FFF;
      padding:3px;
      cursor: pointer;
    }

    .autocompleter-list > div:hover {
      background-color: #DBE8F1;
    }

    .autocompleter-list > div.selected {
      background-color: #DBE8F1;
    }

  </style>
  <script type="text/html" id="hue-ace-autocompleter">
    <!-- ko if: active -->
    <div class="hue-ace-autocompleter" data-bind="style: { top: top() + 'px', left: left() + 'px' }">
      <div class="autocompleter-header"><div class="pull-right">header</div></div>
      <div class="autocompleter-list" data-bind="foreach: suggestions.filtered">
        <div data-bind="click: function () { $parent.selectedIndex($index()); $parent.insertSuggestion(); $parent.editor().focus(); }, css: { 'selected': $index() === $parent.selectedIndex() }"><div class="pull-left" data-bind="matchedText: { suggestion: $data, filter: $parent.suggestions.filter }"></div><div class="pull-right" data-bind="text: meta"></div></div>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/javascript" charset="utf-8">
    (function () {

      var aceUtil = ace.require('ace/autocomplete/util');
      var HashHandler = ace.require('ace/keyboard/hash_handler').HashHandler;

      ko.bindingHandlers.matchedText = {
        update: function (element, valueAccessor) {
          var options = valueAccessor();
          var $element = $(element);
          $element.empty();
          var suggestion = options.suggestion;
          if (options.filter() && suggestion.matchIndex > -1) {
            var before = suggestion.value.substring(0, suggestion.matchIndex);
            var match = suggestion.value.substring(suggestion.matchIndex, suggestion.matchIndex + suggestion.matchLength);
            var after = suggestion.value.substring(suggestion.matchIndex + suggestion.matchLength);
            $element.append(document.createTextNode(before));
            $('<b>').text(match).appendTo($element);
            $element.append(document.createTextNode(after));
          } else {
            $element.text(suggestion.value);
          }
        }
      };

      function HueAceAutocompleter (params, element) {
        var self = this;
        self.editor = params.editor;
        self.snippet = params.snippet;

        self.autocompleter = new SqlAutocompleter3(params);
        self.suggestions = self.autocompleter.suggestions;

        self.active = ko.observable(false);
        self.top = ko.observable(1);
        self.left = ko.observable(1);

        self.selectedIndex = ko.observable(0);

        self.suggestions.filtered.subscribe(function (newValue) {
          if (self.selectedIndex() > newValue.length - 1) {
            self.selectedIndex(Math.max(0, newValue.length -1));
          }
          if (newValue.length === 0) {
            self.detach();
          }
        });

        self.keyboardHandler = new HashHandler();
        self.keyboardHandler.bindKeys({
          'Up': function() {
            if (self.selectedIndex() > 0) {
              self.selectedIndex(self.selectedIndex() - 1);
              self.scrollSelectionIntoView();
            }
          },
          'Down': function() {
            if (self.selectedIndex() < self.suggestions.filtered().length - 1) {
              self.selectedIndex(self.selectedIndex() + 1);
              self.scrollSelectionIntoView();
            }
          },
          'Ctrl-Up|Ctrl-Home': function() {
            self.selectedIndex(0);
            self.scrollSelectionIntoView();
          },
          'Ctrl-Down|Ctrl-End': function() {
            if (self.suggestions.filtered().length > 0 ) {
              self.selectedIndex(self.suggestions.filtered().length - 1);
              self.scrollSelectionIntoView();
            }
          },
          'Esc': function() {
            self.detach();
          },
          'Return': function() {
            self.insertSuggestion();
          },
          'Shift-Return': function() {
            // TODO: Delete suffix
            self.insertSuggestion();
          },
          'Tab': function() {
            self.insertSuggestion();
          }
        });

        var changeTimeout = -1;

        self.changeListener = function () {
          window.clearTimeout(changeTimeout);
          var cursor = self.editor().selection.lead;
          if (cursor.row != self.base.row || cursor.column < self.base.column) {
            self.detach();
          } else {
            changeTimeout = window.setTimeout(function () {
              self.suggestions.filter(self.editor().session.getTextRange({ start: self.base, end: self.editor().getCursorPosition() }));
            }, 200);
          }
        };

        self.mousedownListener = function () {
          self.detach();
        };

        self.mousewheelListener = function () {
          self.detach();
        };

        var closeOnClickOutside = function (event) {
          if ($.contains(document, event.target) && !$.contains(element, event.target)) {
            self.detach();
          }
        };

        self.detach = function () {
          self.active(false);
          self.base.detach();
          self.base = null;
          window.clearTimeout(changeTimeout);
          $(document).off('click', closeOnClickOutside);
          self.editor().keyBinding.removeKeyboardHandler(self.keyboardHandler);
          self.editor().off('changeSelection', self.changeListener);
          self.editor().off('mousedown', self.mousedownListener);
          self.editor().off('mousewheel', self.mousewheelListener);
        };

        self.attach = function () {
          $(document).on('click', closeOnClickOutside);
          self.editor().keyBinding.addKeyboardHandler(self.keyboardHandler);
          self.editor().on('changeSelection', self.changeListener);
          self.editor().on('mousedown', self.mousedownListener);
          self.editor().on('mousewheel', self.mousewheelListener);
        };

        huePubSub.subscribe('hue.ace.autocompleter.show', function (data) {
          var session = self.editor().getSession();
          var pos = self.editor().getCursorPosition();
          var line = session.getLine(pos.row);
          var prefix = aceUtil.retrievePrecedingIdentifier(line, pos.column);
          var newBase = session.doc.createAnchor(pos.row, pos.column - prefix.length);
          self.top(data.position.top + data.lineHeight + 3);
          self.left(data.position.left);
          if (self.active()) {
            if (!self.base || newBase.column !== self.base.column || newBase.row !== self.base.row) {
              self.autocompleter.autocomplete();
            }
            self.detach();
          } else {
            self.autocompleter.autocomplete();
          }
          newBase.$insertRight = true;
          self.base = newBase;
          self.suggestions.filter(prefix);
          self.active(true);
          self.attach();
          self.selectedIndex(0);
        });

        huePubSub.subscribe('hue.ace.autocompleter.hide', function () {
          self.detach();
        });

      }

      HueAceAutocompleter.prototype.insertSuggestion = function () {
        var self = this;
        if (self.suggestions.filtered().length === 0) {
          self.detach();
          return;
        }
        if (self.suggestions.filter()) {
          var ranges = self.editor().selection.getAllRanges();
          for (var i = 0, range; range = ranges[i]; i++) {
            range.start.column -= self.suggestions.filter().length;
            self.editor().session.remove(range);
          }
        }
        self.editor().execCommand('insertstring', self.suggestions.filtered()[self.selectedIndex()].value);
        self.editor().renderer.scrollCursorIntoView();
        self.detach();
      };

      HueAceAutocompleter.prototype.scrollSelectionIntoView = function () {
        var self = this;
        var $autocompleterList = $('.autocompleter-list');
        var selected = $autocompleterList.children().eq(self.selectedIndex());
        var selectedTop = selected.position().top;
        if (selectedTop < 0) {
          $autocompleterList.scrollTop($autocompleterList.scrollTop() + selectedTop);
          return;
        }
        var selectedHeight = selected.outerHeight(true);
        var listHeight = $autocompleterList.innerHeight();

        var diff = (selectedHeight + selectedTop) - listHeight;
        if (diff > 0) {
          $autocompleterList.scrollTop($autocompleterList.scrollTop() + diff);
        }
      };

      ko.components.register('hueAceAutocompleter', {
        viewModel: { createViewModel: function (params, componentInfo) {
          return new HueAceAutocompleter(params, componentInfo.element);
        }},
        template: { element: 'hue-ace-autocompleter' }
      });
    })();
  </script>
</%def>
