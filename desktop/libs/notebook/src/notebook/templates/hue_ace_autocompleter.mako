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
      flex: 1 1 22px;
      padding: 5px;
      background-color: #F9F9F9;
    }

    .autocompleter-list {
      display: inline-block;
      position: relative;
      overflow-y: auto;
      width: 300px;
      height: 100%;
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

    .autocompleter-spinner {
      position: relative;
      float: right;
      width: 15px;
      margin-top: 1px;
    }

    .autocompleter-entries {
      position: relative;
      flex: 1 1 100%;
      overflow: hidden;
    }

    .autocompleter-details {
      vertical-align: top;
      display: inline-block;
      width: 300px;
      overflow-y: auto;
    }

    .autocompleter-categories {
      display: inline-block;
    }

    .autocompleter-categories > div {
      display: inline-block;
      line-height: 14px;
      border-bottom: 2px solid transparent;
      cursor: pointer;
      padding: 0 3px;
    }

    .autocompleter-categories > div.active {
      display: inline-block;
      border-bottom: 2px solid #338BB8;
      cursor: default;
    }

    .autocompleter-suggestion {
      font: 12px/normal 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;direction: ltr;
      line-height: 18px;
    }

    .autocompleter-dot {
      margin-top: 5px;
      margin-right: 5px;
      width: 8px;
      height: 8px;
      border-radius: 4px;
    }
  </style>

  <script type="text/html" id="hue-ace-autocompleter">
    <!-- ko if: active -->
    <div class="hue-ace-autocompleter" data-bind="style: { top: top() + 'px', left: left() + 'px' }">
      <!-- ko if: suggestions.availableCategories().length > 1 || suggestions.loading() -->
      <div class="autocompleter-header">
        <!-- ko if: suggestions.availableCategories().length > 1 -->
        <div class="autocompleter-categories" data-bind="foreach: suggestions.availableCategories()">
          <div data-bind="text: label, css: { 'active': $parent.suggestions.activeCategory() === $data }, style: { 'border-color': $parent.suggestions.activeCategory() === $data ? color : 'transparent' }, click: function (data, event) { $parent.suggestions.activeCategory($data); event.stopPropagation(); }"></div>
        </div>
        <!-- /ko -->
        <div class="autocompleter-spinner"><!-- ko hueSpinner: { spin: suggestions.loading, size: 'small' } --><!-- /ko --></div>
      </div>
      <!-- /ko -->
      <div class="autocompleter-entries">
        <div class="autocompleter-list" data-bind="foreach: suggestions.filtered">
          <div data-bind="click: function () { $parent.selectedIndex($index()); $parent.insertSuggestion(); $parent.editor().focus(); }, css: { 'selected': $index() === $parent.selectedIndex() }">
            <div class="pull-left autocompleter-dot" data-bind="style: { 'background-color': category.color }"></div>
            <div class="autocompleter-suggestion pull-left" data-bind="matchedText: { suggestion: $data, filter: $parent.suggestions.filter }"></div>
            <div class="autocompleter-suggestion pull-right" data-bind="text: meta"></div>
          </div>
        </div>
        <!-- ko if: selectedEntry() && selectedEntry().details -->
        <div class="autocompleter-details" data-bind="template: { name: 'autocomplete-details-' + selectedEntry().detailsTemplate, data: selectedEntry }"></div>
        <!-- /ko -->
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="autocomplete-details-keyword">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-column-alias">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-udf">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-table">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-column">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-hdfs">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-join">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-join-condition">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-aggregate-function">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-group-by">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-order-by">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
  </script>

  <script type="text/html" id="autocomplete-details-filter">
    <pre data-bind="text: ko.mapping.toJSON(details)"></pre>
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

        self.active = ko.observable(false).extend({ rateLimit: 10 }); // to prevent flickering on empty result
        self.top = ko.observable(1);
        self.left = ko.observable(1);

        self.selectedIndex = ko.observable(0);

        self.selectedEntry = ko.pureComputed(function () {
          if (self.suggestions.filtered().length > 0) {
            return self.suggestions.filtered()[self.selectedIndex()];
          }
          return null;
        });

        self.suggestions.filtered.subscribe(function (newValue) {
          if (self.selectedIndex() > newValue.length - 1) {
            self.selectedIndex(Math.max(0, newValue.length -1));
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
              if (self.suggestions.filtered().length === 0) {
                self.detach();
              }
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
          if (!self.active()) {
            return;
          }
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

        huePubSub.subscribe('hue.ace.autocompleter.done', function () {
          window.setTimeout(function () {
            if (self.active() && self.suggestions.filtered().length === 0) {
              self.detach();
            }
          }, 0);
        });

        huePubSub.subscribe('hue.ace.autocompleter.show', function (data) {
          var session = self.editor().getSession();
          var pos = self.editor().getCursorPosition();
          var line = session.getLine(pos.row);
          var prefix = aceUtil.retrievePrecedingIdentifier(line, pos.column);
          var newBase = session.doc.createAnchor(pos.row, pos.column - prefix.length);
          self.top(data.position.top + data.lineHeight + 3);
          self.left(data.position.left);
          if (!self.active() || (!self.base || newBase.column !== self.base.column || newBase.row !== self.base.row)) {
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
