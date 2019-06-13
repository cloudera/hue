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
  <script type="text/html" id="hue-ace-autocompleter">
    <!-- ko if: active() && (suggestions.filtered().length !== 0 || suggestions.loading()) -->
    <div class="hue-ace-autocompleter" data-bind="style: { top: top() + 'px', left: left() + 'px' }">
      <div class="autocompleter-suggestions">
        <!-- ko if: suggestions.availableCategories().length > 1 || suggestions.loading() -->
        <div class="autocompleter-header">
          <!-- ko if: suggestions.availableCategories().length > 1 -->
          <div class="autocompleter-categories" data-bind="foreach: suggestions.availableCategories()">
            <div data-bind="text: label, css: { 'active': $parent.suggestions.activeCategory() === $data }, style: { 'border-color': $parent.suggestions.activeCategory() === $data ? color : 'transparent' }, click: function (data, event) { $parent.suggestions.activeCategory($data); event.stopPropagation(); $parent.editor().focus(); }"></div>
          </div>
          <!-- /ko -->
          <div class="autocompleter-spinner"><!-- ko hueSpinner: { spin: suggestions.loading, size: 'small' } --><!-- /ko --></div>
        </div>
        <!-- /ko -->
        <div class="autocompleter-entries">
          <div data-bind="foreachVisible: { data: suggestions.filtered, minHeight: 25, container: '.autocompleter-entries' }">
            <div class="autocompleter-suggestion" data-bind="click: function () { $parent.selectedIndex($index() + $indexOffset()); $parent.insertSuggestion(); $parent.editor().focus(); },
                css: { 'selected': $index() + $indexOffset() === $parent.selectedIndex() },
                event: { 'mouseover': function () { $parent.hoveredIndex($index() + $indexOffset()); }, 'mouseout': function () { $parent.hoveredIndex(null); } }">
              <div class="autocompleter-suggestion-value">
                <div class="autocompleter-dot" data-bind="style: { 'background-color': category.color }"></div> <span data-bind="matchedText: { suggestion: $data, filter: $parent.suggestions.filter }"></span> <!-- ko if: details && details.primary_key === 'true' --><i class="fa fa-key"></i><!-- /ko -->
              </div>
              <div class="autocompleter-suggestion-meta"><!-- ko if: popular --><i class="fa fa-star-o popular-color"></i> <!-- /ko --><span data-bind="text: meta"></span></div>
            </div>
          </div>
        </div>
      </div>
      <!-- ko if: focusedEntry() && focusedEntry().details -->
      <!-- ko template: { name: 'autocomplete-' + (focusedEntry().hasCatalogEntry ? 'catalog-details-' : 'details-') + focusedEntry().category.detailsTemplate, data: focusedEntry } --><!-- /ko -->
      <!-- /ko -->
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="autocomplete-details-keyword">
  </script>

  <script type="text/html" id="autocomplete-details-solr-field">
  </script>

  <script type="text/html" id="autocomplete-catalog-details-solr-field">
  </script>

  <script type="text/html" id="autocomplete-details-udf">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-superscript"></i> <span data-bind="text: details.signature.substring(0, details.signature.indexOf('('));"></span></div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: details.signature"></div>
          <div class="details-description" data-bind="text: details.description"></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-option">
    <div class="autocompleter-details">
      <div class="autocompleter-header" data-bind="text: value"></div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code">${ _ko('Type:') } <span data-bind="text: details.type"></span></div>
          <div class="details-code">${ _ko('Default:') } <span data-bind="text: details.default"></span></div>
          <div class="details-description" data-bind="text: details.description"></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-database">
  </script>

  <script type="text/html" id="autocomplete-catalog-details-database">
    <div class="autocompleter-details">
      <div class="autocompleter-header">
        <i class="fa fa-fw fa-database"></i> <span data-bind="text: details.getTitle()"></span>
      </div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner" data-bind="component: { name: 'dataCatalogMiniContext', params: { catalogEntry: details } }">
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-table">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw" data-bind="css: { 'fa-eye': details.type.toLowerCase() !== 'table', 'fa-table': details.type.toLowerCase() === 'table' }"></i> <span data-bind="text: details.name"></span></div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-attribute" ><i class="fa fa-database fa-fw"></i> <span data-bind="text: details.database"></span></div>
          <!-- ko if: typeof details.popularity !== 'undefined' -->
          <div class="details-popularity margin-left-5" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + details.popularity.relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.popularity.relativePopularity + '%' }"></div>
            </div>
          </div>
          <!-- /ko -->
          <!-- ko if: typeof details.comment !== 'undefined' && details.comment !== null -->
          <div class="details-comment" data-bind="matchedText: { suggestion: $data, filter: $parent.suggestions.filter, isComment: true }"></div>
          <!-- /ko -->
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-catalog-details-table">
    <div class="autocompleter-details">
      <div class="autocompleter-header">
        <i class="fa fa-fw" data-bind="css: { 'fa-eye': details.isView(), 'fa-table': details.isTable() }"></i> <span data-bind="text: details.getTitle()"></span>
        <!-- ko if: popular() && relativePopularity -->
        <div class="autocompleter-header-popularity" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i></div>
        <!-- /ko -->
      </div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner" data-bind="component: { name: 'dataCatalogMiniContext', params: { catalogEntry: details } }">
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-column">
    <!-- ko if: typeof details.name !== 'undefined' -->
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-columns"></i> <span data-bind="text: details.name"></span></div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <!-- ko if: typeof details.database !== 'undefined' && typeof details.table !== 'undefined' -->
          <div class="details-attribute" ><i class="fa fa-table fa-fw"></i> <span data-bind="text: details.database"></span>.<span data-bind="text: details.table"></span></div>
          <!-- /ko -->
          <!-- ko if: typeof partitionKey !== 'undefined' && partitionKey -->
          <div class="details-attribute" ><i class="fa fa-key fa-fw"></i> ${ _('Partition key') }</div>
          <!-- /ko -->
          <!-- ko if: typeof details.primary_key !== 'undefined' && details.primary_key === 'true' -->
          <div class="details-attribute" ><i class="fa fa-key fa-fw"></i> ${ _('Primary key') }</div>
          <!-- /ko -->
          <!-- ko if: typeof details.popularity !== 'undefined' -->
          <br/>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + details.popularity.relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.popularity.relativePopularity + '%' }"></div>
            </div>
          </div>
          <!-- /ko -->
          <!-- ko if: typeof details.comment !== 'undefined' && details.comment !== null -->
          <div class="details-comment" data-bind="matchedText: { suggestion: $data, filter: $parent.suggestions.filter, isComment: true }"></div>
          <!-- /ko -->
        </div>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="autocomplete-catalog-details-column">
    <div class="autocompleter-details">
      <div class="autocompleter-header">
        <i class="fa fa-fw fa-columns"></i> <span data-bind="text: details.name"></span>
        <!-- ko if: popular() && relativePopularity -->
        <div class="autocompleter-header-popularity" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i></div>
        <!-- /ko -->
      </div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner" data-bind="component: { name: 'dataCatalogMiniContext', params: { catalogEntry: details } }">
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-variable">
  </script>

  <script type="text/html" id="autocomplete-details-hdfs">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw" data-bind="css: { 'fa-folder-o': details.type === 'dir', 'fa-file-o': details.type !== 'dir' }"></i> <span data-bind="text: details.name"></span></div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <!-- ko with: details -->
          <div class="assist-details-wrap">
            <div><div class="assist-details-header">${ _('Size') }</div><div class="assist-details-value" data-bind="text: humansize"></div></div>
            <!-- ko with: stats -->
            <div><div class="assist-details-header">${ _('User') }</div><div class="assist-details-value" data-bind="text: user"></div></div>
            <div><div class="assist-details-header">${ _('Group') }</div><div class="assist-details-value" data-bind="text: group"></div></div>
            <!-- /ko -->
            <div><div class="assist-details-header">${ _('Permissions') }</div><div class="assist-details-value" data-bind="text: rwx"></div></div>
            <div><div class="assist-details-header">${ _('Date') }</div><div class="assist-details-value" data-bind="text: mtime"></div></div>
          </div>
          <!-- /ko -->
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-join">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular join')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: value"></div>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + details.relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.relativePopularity + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-join-condition">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular join condition')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: value"></div>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + details.relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.relativePopularity + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-agg-udf">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-superscript"></i> ${ _('Popular aggregate')} - <span data-bind="text: details.aggregateFunction"></span></div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: value"></div>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + details.relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.relativePopularity + '%' }"></div>
            </div>
          </div>
          <div class="details-comment" data-bind="text: details.function.description"></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-value">
    <!-- ko if: value.length > 31 -->
    <div class="autocompleter-details">
      <div class="autocompleter-header">${ _('Value')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner" style="word-wrap: break-word; white-space: normal" data-bind="text: value">
        </div>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="autocomplete-details-identifier">
  </script>

  <script type="text/html" id="autocomplete-details-cte">
  </script>

  <script type="text/html" id="autocomplete-details-group-by">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular group by')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: value"></div>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Workload percent') } ' + details.workloadPercent + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.workloadPercent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-catalog-details-group-by">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular group by')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner" data-bind="component: { name: 'dataCatalogMiniContext', params: { catalogEntry: details, showTitle: true } }"></div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-order-by">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular order by')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: value"></div>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Workload percent') } ' + details.workloadPercent + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.workloadPercent + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-catalog-details-order-by">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular order by')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner" data-bind="component: { name: 'dataCatalogMiniContext', params: { catalogEntry: details, showTitle: true } }"></div>
      </div>
    </div>
  </script>

  <script type="text/html" id="autocomplete-details-filter">
    <div class="autocompleter-details">
      <div class="autocompleter-header"><i class="fa fa-fw fa-star-o"></i> ${ _('Popular filter')}</div>
      <div class="autocompleter-details-contents">
        <div class="autocompleter-details-contents-inner">
          <div class="details-code" data-bind="text: value"></div>
          <div class="details-popularity margin-top-10" data-bind="tooltip: { title: '${ _ko('Popularity') } ' + details.relativePopularity + '%', placement: 'bottom' }"><i class="fa fa-fw fa-star-o popular-color"></i>
            <div class="progress">
              <div class="bar" data-bind="style: { 'width': details.relativePopularity + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </script>


  <script type="text/javascript">
    (function () {

      var aceUtil = ace.require('ace/autocomplete/util');
      var HashHandler = ace.require('ace/keyboard/hash_handler').HashHandler;

      ko.bindingHandlers.matchedText = {
        init: function (element, valueAccessor) {
          var options = valueAccessor();
          var $element = $(element);

          var refresh = function () {
            $element.empty();
            var suggestion = options.suggestion;
            var value = options.isComment ? suggestion.details.comment : suggestion.value;

            if (options.filter() && suggestion.matchIndex > -1 && ((!options.isComment && !suggestion.matchComment) || (options.isComment && suggestion.matchComment))) {
              var before = value.substring(0, suggestion.matchIndex);
              var match = value.substring(suggestion.matchIndex, suggestion.matchIndex + suggestion.matchLength);
              var after = value.substring(suggestion.matchIndex + suggestion.matchLength);
              $element.append(document.createTextNode(before));
              $('<b>').text(match).appendTo($element);
              $element.append(document.createTextNode(after));
            } else {
              $element.text(value);
            }
          };

          refresh();

          // matchIndex and matchLength are not observable, hence the pubsub to update
          var updatePubSub = huePubSub.subscribe('hue.ace.autocompleter.match.updated', refresh);
          ko.utils.domNodeDisposal.addDisposeCallback(element, updatePubSub.remove)
        }
      };

      function HueAceAutocompleter (params, element) {
        var self = this;
        self.disposeFunctions = [];
        self.editor = params.editor;
        self.snippet = params.snippet || {};
        self.foreachVisible = ko.observable();

        self.autocompleter = params.autocompleter || new SqlAutocompleter(params);
        self.suggestions = self.autocompleter.suggestions;

        self.active = ko.observable(false).extend({ rateLimit: 10 }); // to prevent flickering on empty result
        self.top = ko.observable(1);
        self.left = ko.observable(1);

        self.selectedIndex = ko.observable(0);
        self.hoveredIndex = ko.observable(null);

        self.focusedEntry = ko.pureComputed(function () {
          if (self.suggestions.filtered().length > 0) {
            return self.suggestions.filtered()[self.hoveredIndex() || self.selectedIndex()];
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
          'Up': function(editor, evt) {
            if (self.suggestions.filtered().length <= 1) {
              self.detach();
              self.editor().execCommand('golineup');
            } else if (self.selectedIndex() > 0) {
              self.selectedIndex(self.selectedIndex() - 1);
              self.hoveredIndex(null);
              self.scrollSelectionIntoView();
            } else {
              self.selectedIndex(self.suggestions.filtered().length - 1);
              self.hoveredIndex(null);
              self.scrollSelectionIntoView();
            }
          },
          'Down': function(editor) {
            if (self.suggestions.filtered().length <= 1) {
              self.detach();
              self.editor().execCommand('golinedown');
            } else if (self.selectedIndex() < self.suggestions.filtered().length - 1) {
              self.selectedIndex(self.selectedIndex() + 1);
              self.hoveredIndex(null);
              self.scrollSelectionIntoView();
            } else {
              self.selectedIndex(0);
              self.hoveredIndex(null);
              self.scrollSelectionIntoView();
            }
          },
          'Ctrl-Up|Ctrl-Home': function() {
            if (self.suggestions.filtered().length <= 1) {
              self.detach();
              self.editor().execCommand('gotostart');
            } else {
              self.selectedIndex(0);
              self.hoveredIndex(null);
              self.scrollSelectionIntoView();
            }
          },
          'Ctrl-Down|Ctrl-End': function() {
            if (self.suggestions.filtered().length <= 1) {
              self.detach();
              self.editor().execCommand('gotoend');
            } else if (self.suggestions.filtered().length > 0 ) {
              self.selectedIndex(self.suggestions.filtered().length - 1);
              self.hoveredIndex(null);
              self.scrollSelectionIntoView();
            }
          },
          'Esc': function() {
            self.detach();
          },
          'Return': function() {
            self.insertSuggestion(function () {
              self.editor().execCommand('insertstring', '\n');
            });
          },
          'Shift-Return': function() {
            // TODO: Delete suffix
            self.insertSuggestion();
          },
          'Tab': function() {
            self.insertSuggestion(function () {
              self.editor().execCommand('indent');
            });
          }
        });

        var changeTimeout = -1;

        self.changeListener = function () {
          window.clearTimeout(changeTimeout);
          var cursor = self.editor().selection.lead;
          if (cursor.row !== self.base.row || cursor.column < self.base.column) {
            self.detach();
          } else {
            changeTimeout = window.setTimeout(function () {
              var pos = self.editor().getCursorPosition();
              if (self.active() && self.autocompleter.onPartial) {
                self.autocompleter.onPartial(aceUtil.retrievePrecedingIdentifier(self.editor().session.getLine(pos.row), pos.column));
              }
              self.suggestions.filter(self.editor().session.getTextRange({ start: self.base, end: pos }));
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

        var positionInterval = -1;

        var disposeEventHanders = function () {
          window.clearTimeout(changeTimeout);
          window.clearInterval(positionInterval);
          $(document).off('click', closeOnClickOutside);
          self.editor().keyBinding.removeKeyboardHandler(self.keyboardHandler);
          self.editor().off('changeSelection', self.changeListener);
          self.editor().off('mousedown', self.mousedownListener);
          self.editor().off('mousewheel', self.mousewheelListener);
        };

        self.detach = function () {
          self.suggestions.cancelRequests();
          disposeEventHanders();
          if (!self.active()) {
            return;
          }
          self.active(false);
          self.base.detach();
          self.base = null;
        };

        self.attach = function () {
          disposeEventHanders();
          $(document).on('click', closeOnClickOutside);
          self.editor().keyBinding.addKeyboardHandler(self.keyboardHandler);
          self.editor().on('changeSelection', self.changeListener);
          self.editor().on('mousedown', self.mousedownListener);
          self.editor().on('mousewheel', self.mousewheelListener);
          var $container = $(self.editor().container);
          var initialOffset = $container.offset();
          var initialDevicePixelRation = window.devicePixelRatio; // Detect zoom changes
          positionInterval = window.setInterval(function () {
            var newOffset = $container.offset();
            if (initialDevicePixelRation !== window.devicePixelRatio) {
              initialOffset = newOffset;
              initialDevicePixelRation = window.devicePixelRatio;
            } else if (Math.abs(newOffset.top - initialOffset.top) > 20 || Math.abs(newOffset.left - initialOffset.left) > 20) {
              self.detach();
            }
          }, 300);
        };

        var autocompleterDoneSub = huePubSub.subscribe('hue.ace.autocompleter.done', function () {
          window.setTimeout(function () {
            if (self.active() && self.suggestions.filtered().length === 0 && !self.suggestions.loading()) {
              self.detach();
            }
          }, 0);
        });

        self.disposeFunctions.push(function () {
          autocompleterDoneSub.remove();
        });

        var autocompleterShowSub = huePubSub.subscribe('hue.ace.autocompleter.show', function (data) {
          if (data.editor !== self.editor()) {
            return;
          }
          var session = self.editor().getSession();
          var pos = self.editor().getCursorPosition();
          var line = session.getLine(pos.row);
          var prefix = aceUtil.retrievePrecedingIdentifier(line, pos.column);
          var newBase = session.doc.createAnchor(pos.row, pos.column - prefix.length);
          self.top(data.position.top + data.lineHeight + 3);
          self.left(data.position.left);
          var newAutocomp = false;
          if (!self.active() || (!self.base || newBase.column !== self.base.column || newBase.row !== self.base.row)) {
            self.autocompleter.autocomplete();
            newAutocomp = true;
          }
          newBase.$insertRight = true;
          self.base = newBase;
          self.suggestions.filter(prefix);
          self.active(true);
          self.selectedIndex(0);
          if (newAutocomp) {
            self.attach();
          }
        });

        self.disposeFunctions.push(function () {
          autocompleterShowSub.remove();
        });

        var autocompleterHideSub = huePubSub.subscribe('hue.ace.autocompleter.hide', function () {
          self.detach();
        });

        self.disposeFunctions.push(function () {
          autocompleterHideSub.remove();
        });
      }

      HueAceAutocompleter.prototype.dispose = function () {
        var self = this;
        self.disposeFunctions.forEach(function (disposeFunction) {
          disposeFunction();
        });
        self.detach();
      };

      HueAceAutocompleter.prototype.insertSuggestion = function (emptyCallback) {
        var self = this;
        if (self.suggestions.filtered().length === 0) {
          self.detach();
          if (emptyCallback) {
            emptyCallback();
          }
          return;
        }
        var selectedSuggestion = self.suggestions.filtered()[self.selectedIndex()];
        var valueToInsert = selectedSuggestion.value;
        if (selectedSuggestion.popular() && selectedSuggestion.category) {
          hueAnalytics.convert('editor', 'popularAutocomplete/' + self.suggestions.filtered()[self.selectedIndex()].category.id)
        }
        // Not always the case as we also match in comments
        if (valueToInsert.toLowerCase() === self.suggestions.filter().toLowerCase()) {
          // Close the autocompleter when the user has typed a complete suggestion
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
        // TODO: Only replace when editing identifiers (using parse locations)
##         var match = self.editor().getTextAfterCursor().match(/^[^\s.]+/);
##         if (match) {
##           self.editor().removeTextAfterCursor(match[0].length);
##         }
        // TODO: Move cursor handling for '? FROM tbl' here
        self.editor().execCommand('insertstring', valueToInsert);
        self.editor().renderer.scrollCursorIntoView();
        self.detach();
      };

      HueAceAutocompleter.prototype.scrollSelectionIntoView = function () {
        var self = this;
        if (self.foreachVisible()) {
          self.foreachVisible().scrollToIndex(self.selectedIndex());
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

  <script type="text/html" id="data-catalog-mini-context">
    <!-- ko if: catalogEntry.isColumn() -->
    <!-- ko ifnot: showTitle -->
    <div class="details-attribute" ><i class="fa fa-table fa-fw"></i> <span data-bind="text: catalogEntry.path[0]"></span>.<span data-bind="text: catalogEntry.path[1]"></span></div>
    <!-- /ko -->
    <!-- ko if: showTitle -->
    <div class="details-attribute" ><i class="fa fa-columns fa-fw"></i> <span data-bind="text: catalogEntry.getTitle()"></span></div>
    <!-- /ko -->
    <!-- ko if: catalogEntry.isPartitionKey() -->
    <div class="details-attribute" ><i class="fa fa-key fa-fw"></i> ${ _('Partition key') }</div>
    <!-- /ko -->
    <!-- ko if: catalogEntry.isPrimaryKey() -->
    <div class="details-attribute" ><i class="fa fa-key fa-fw"></i> ${ _('Primary key') }</div>
    <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: loading -->
    <div class="details-comment" ><!-- ko hueSpinner: { spin: loading, size: 'small', inline: true } --><!-- /ko --></div>
    <!-- /ko -->
    <!-- ko ifnot: loading -->
    <!-- ko if: comment() -->
    <div class="details-comment" data-bind="text: comment"></div>
    <!-- /ko -->
    <!-- ko ifnot: comment() -->
    <div class="details-no-comment">
      ${ _('No description') }
    </div>
    <!-- /ko -->
    <!-- /ko -->
  </script>

  <script type="text/javascript">
    (function () {

      var COMMENT_LOAD_DELAY = 1500;

      function DataCatalogMiniContext (params) {
        var self = this;
        self.catalogEntry = params.catalogEntry;
        self.filter = params.filter;
        self.comment = ko.observable();
        self.popularity = ko.observable();
        self.showTitle = !!params.showTitle;
        self.loading = ko.observable(false);

        self.loadTimeout = -1;
        self.activePromises = [];

        if (self.catalogEntry.hasResolvedComment()) {
          self.comment(self.catalogEntry.getResolvedComment());
        } else {
          self.loading(true);
          self.loadTimeout = window.setTimeout(function () {
            self.activePromises.push(self.catalogEntry.getComment({ silenceErrors: true, cancellable: true }).done(self.comment).always(function () {
              self.loading(false);
            }));
          }, COMMENT_LOAD_DELAY);
        }

        if (self.catalogEntry.navOptPopularity && self.catalogEntry.navOptPopularity.relativePopularity) {
          self.popularity(self.catalogEntry.navOptPopularity.relativePopularity);
        }
      }

      DataCatalogMiniContext.prototype.dispose = function () {
        var self = this;
        window.clearTimeout(self.loadTimeout);
        while (self.activePromises.length) {
          var promise = self.activePromises.pop();
          if (promise.cancel) {
            promise.cancel();
          }
        }
      };

      ko.components.register('dataCatalogMiniContext', {
        viewModel: DataCatalogMiniContext,
        template: { element: 'data-catalog-mini-context' }
      });
    })();
  </script>
</%def>
