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
from desktop import conf
from desktop.lib.i18n import smart_unicode

from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="inlineAutocomplete()">

  <script type="text/html" id="inline-autocomplete-template">
    <div class="inline-autocomplete-container">
      <div>
        <!-- ko if: showMagnify -->
          <!-- ko ifnot: spin -->
          <i style="top: 6px;" class="inline-autocomplete-magnify-icon fa fa-fw fa-search"></i>
          <!-- /ko -->
          <!-- ko if: spin -->
          <i class="inline-autocomplete-magnify-icon fa fa-fw fa-spinner fa-spin"></i>
          <!-- /ko -->
        <!-- /ko-->
        <input class="inline-autocomplete-input" autocorrect="off" autocapitalize="off" spellcheck="false" type="text" data-bind="
          attr: { 'placeHolder' : hasFocus() ? '' : placeHolder },
          textInput: searchInput,
          hasFocus: hasFocus,
          clearable: { value: searchInput, onClear: onClear },
          css: { 'inline-autocomplete-magnify-input': showMagnify }">
        <input class="inline-autocomplete-autocomplete" disabled type="text" data-bind="
          value: inlineAutocomplete,
          css: { 'inline-autocomplete-magnify-input': showMagnify }">
      </div>
    </div>

    <div class="hue-drop-down-container hue-drop-down-fixed" data-bind="event: { 'mousedown': facetDropDownMouseDown }, css: { 'open' : facetDropDownVisible() }, dropDownKeyUp: { onEsc: facetDropDownOnEsc, onEnter: facetDropDownOnEnter, onSelected: facetDropDownOnSelected, dropDownVisible: facetDropDownVisible }">
      <div class="dropdown-menu" style="overflow-y: auto;" data-bind="visible: facetSuggestions().length > 0">
        <ul class="hue-inner-drop-down" data-bind="foreach: facetSuggestions">
          <li><a href="javascript:void(0)" data-bind="html: label, click: function () { $parent.facetClicked($data); }, clickBubble: false"></a></li>
        </ul>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var getSortedFacets = function (facetIndex) {
        var result = Object.keys(facetIndex);
        result.sort(function (a, b) {
          return a.localeCompare(b);
        });
        return result;
      };

      var InlineAutocomplete = function (params) {
        var self = this;
        self.disposals = [];

        self.showMagnify = !!params.showMagnify;
        self.spin = params.spin;
        self.placeHolder = params.placeHolder || '${ _('Filter...') }';
        self.hasFocus = params.hasFocus || ko.observable();
        self.querySpec = params.querySpec;
        self.querySpec({
          query: '',
          facets: {},
          text: []
        });
        self.autocompleteFromEntries = params.autocompleteFromEntries || function () { return []; };
        self.facets = params.facets || [];
        self.knownFacetValues = params.knownFacetValues || {};
        self.uniqueFacets = !!params.uniqueFacets;
        self.disableNavigation = !!params.disableNavigation;
        self.changedAfterFocus = false;

        self.searchInput = ko.observable('');
        self.suggestions = ko.observableArray();
        self.selectedSuggestionIndex = ko.observable(0);

        self.suggestions.subscribe(function () {
          self.selectedSuggestionIndex(0);
        });

        self.facetSuggestions = ko.observableArray();
        self.facetDropDownVisible = params.facetDropDownVisible || ko.observable(false);

        self.facetClicked = function (facet) {
          self.searchInput(facet.value);
          self.facetDropDownVisible(false);
        };

        self.facetDropDownOnEnter = function (facet) {
          if (facet) {
            self.searchInput(facet.value);
          }
          self.facetDropDownVisible(false);
        };

        self.facetDropDownOnEsc = function () {
          self.facetDropDownVisible(false);
        };

        self.facetDropDownOnSelected = function (facet) {
          if (facet) {
            var suggestions = self.suggestions();
            for (var i = 0; i < suggestions.length; i++) {
              if (facet.value === suggestions[i]) {
                self.selectedSuggestionIndex(i);
                break;
              }
            }
          }
        };

        self.facetDropDownMouseDown = function (data, evt) {
          evt.preventDefault(); // Prevent focus loss on the input when an entry is clicked
          return false;
        };

        self.inlineAutocomplete = ko.pureComputed(function () {
          if (!self.hasFocus() || self.suggestions().length === 0) {
            return '';
          }
          return self.suggestions()[self.selectedSuggestionIndex()];
        });

        self.lastParseResult = {};

        var querySpecSub = self.querySpec.subscribe(function (newVal) {
          if (!newVal || !newVal.query) {
            self.lastParseResult = {};
            self.searchInput('');
            self.clearSuggestions();
          }
        });

        self.disposals.push(function () {
          querySpecSub.dispose();
        });

        self.onClear = function () {
          if (params.onClear) {
            params.onClear();
          }
          self.clearSuggestions();
        };

        if (params.triggerObservable) {
          var triggerSub = params.triggerObservable.subscribe(function () {
            self.autocomplete();
          });
          self.disposals.push(function () {
            triggerSub.dispose();
          })
        }

        var inputSub = self.searchInput.subscribe(function (newValue) {
          if (self.querySpec() && self.querySpec().query === newValue) {
            return;
          }

          if (newValue === '') {
            self.changedAfterFocus = false;
            self.clearSuggestions();
            if (self.querySpec() && self.querySpec().query !== '') {
              self.querySpec({
                query: '',
                facets: {},
                text: []
              });
            }
            return;
          }

          self.changedAfterFocus = true;

          self.updateQuerySpec();
          self.autocomplete();
        });

        self.disposals.push(function () {
          inputSub.dispose();
        });

        var onKeyDown = function (event) {
          if (!self.hasFocus()) {
            return;
          }
          if (!self.disableNavigation && event.keyCode === 38 && self.suggestions().length && !self.facetDropDownVisible()) { // Up
            if (self.selectedSuggestionIndex() === 0) {
              self.selectedSuggestionIndex(self.suggestions().length - 1);
            } else {
              self.selectedSuggestionIndex(self.selectedSuggestionIndex() - 1);
            }
            event.preventDefault();
            return;
          }

          if (!self.disableNavigation && event.keyCode === 40 && self.suggestions().length && !self.facetDropDownVisible()) { // Down
            if (self.selectedSuggestionIndex() === self.suggestions().length - 1) {
              self.selectedSuggestionIndex(0);
            } else {
              self.selectedSuggestionIndex(self.selectedSuggestionIndex() + 1);
            }
            event.preventDefault();
            return;
          }
          if (event.keyCode === 32 && event.ctrlKey) { // Ctrl-Space
            if (!self.lastParseResult) {
              self.updateQuerySpec();
            }
            self.changedAfterFocus = true;
            self.autocomplete();
            return;
          }
          if (event.keyCode === 39 && self.inlineAutocomplete() !== '' && self.inlineAutocomplete() !== self.searchInput()) { // Right arrow
            // TODO: Check that cursor is last
            self.searchInput(self.inlineAutocomplete());
            return;
          }
          if (event.keyCode === 9 && self.inlineAutocomplete() !== self.searchInput()) { // Tab
            self.searchInput(self.inlineAutocomplete());
            event.preventDefault();
          }
        };

        self.disposals.push(function () {
          $(document).off('keydown.inlineAutocomplete', onKeyDown);
        });

        var focusSub = self.hasFocus.subscribe(function (newVal) {
          if (!newVal) {
            self.clearSuggestions();
            self.changedAfterFocus = false;
            $(document).off('keydown.inlineAutocomplete', onKeyDown);
          } else if (self.searchInput() !== '') {
            self.autocomplete();
            $(document).on('keydown.inlineAutocomplete', onKeyDown);
          } else {
            $(document).on('keydown.inlineAutocomplete', onKeyDown);
          }
          if (!newVal && self.facetDropDownVisible()) {
            self.facetDropDownVisible(false);
          }
        });

        self.disposals.push(function () {
          focusSub.dispose();
        });
      };

      InlineAutocomplete.prototype.updateQuerySpec = function () {
        var self = this;
        // TODO: Get cursor position and split to before and after
        self.lastParseResult = globalSearchParser.parseGlobalSearch(self.searchInput(), '');
        if (hueDebug && hueDebug.showGlobalSearchParseResults) {
          console.log(self.lastParseResult);
        }
        var querySpec = { query: self.searchInput() };

        if (self.lastParseResult.facets) {
          var knownFacetValues = typeof self.knownFacetValues === 'function' ? self.knownFacetValues() : self.knownFacetValues;
          var cleanFacets = {};
          Object.keys(self.lastParseResult.facets).forEach(function (facet) {
            if (!knownFacetValues[facet]) {
              cleanFacets[facet] = self.lastParseResult.facets[facet];
            } else {
              cleanFacets[facet] = {};
              Object.keys(self.lastParseResult.facets[facet]).forEach(function (value) {
                if (knownFacetValues[facet][value]) {
                  cleanFacets[facet][value] = self.lastParseResult.facets[facet][value];
                } else {
                  var found = false;
                  // Find the closest match, i.e. type:s -> type: [string, smallint, ...]
                  getSortedFacets(knownFacetValues[facet]).forEach(function (knownValue) {
                    if (knownValue.toLowerCase().indexOf(value.toLowerCase()) === 0) {
                      if (!cleanFacets[facet][knownValue]) {
                        cleanFacets[facet][knownValue] = [];
                      }
                      cleanFacets[facet][knownValue] = true;
                      found = true
                    }
                  });
                  if (!found) {
                    cleanFacets[facet][value] = self.lastParseResult.facets[facet][value];
                  }
                }
              })
            }
          });
          querySpec.facets = cleanFacets;
        }
        if (self.lastParseResult.text) {
          querySpec.text = self.lastParseResult.text;
        }

        self.querySpec(querySpec);
      };

      InlineAutocomplete.prototype.clearSuggestions = function () {
        var self = this;
        if (self.suggestions().length) {
          self.suggestions([]);
        }
        if (self.facetSuggestions().length) {
          self.facetSuggestions([]);
        }
      };

      InlineAutocomplete.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      InlineAutocomplete.prototype.autocomplete = function () {
        var self = this;
        if (!self.lastParseResult) {
          self.clearSuggestions();
          return;
        }

        var text = self.searchInput();
        var partial, nonPartial;
        var partialMatch = text.match(/([^:\s]+)$/i);
        if (partialMatch) {
          partial = partialMatch[0];
          nonPartial = text.substring(0, text.length - partial.length);
        } else {
          partial = '';
          nonPartial = text;
        }

        var newSuggestions = [];
        var facetSuggestions = [];
        var partialLower = partial.toLowerCase();
        if (self.lastParseResult.suggestFacets) {
          var existingFacetIndex = {};
          if (self.uniqueFacets && self.lastParseResult.facets) {
            Object.keys(self.lastParseResult.facets).forEach(function (facet) {
              existingFacetIndex[facet.toLowerCase()] = true;
            })
          }

          var suggestion = nonPartial + partial;
          var isLowerCase = suggestion.length > 0 && suggestion.toLowerCase() === suggestion;
          self.facets.forEach(function (facet) {
            if (self.uniqueFacets && existingFacetIndex[facet]) {
              return;
            }
            if (partial.length === 0 || facet.indexOf(partialLower) === 0) {
              var remainder = facet.substring(partial.length);
              suggestion += isLowerCase ? remainder : remainder.toUpperCase();
              suggestion += ':';
              newSuggestions.push(suggestion);
            }
          });
        }

        if (self.lastParseResult.suggestFacetValues) {
          var facetValues = typeof self.knownFacetValues === 'function' ? self.knownFacetValues() : self.knownFacetValues;
          if (facetValues && facetValues[self.lastParseResult.suggestFacetValues.toLowerCase()]) {
            var matchedFacets = facetValues[self.lastParseResult.suggestFacetValues.toLowerCase()];
            getSortedFacets(matchedFacets).forEach(function (value) {
              if (value.toLowerCase().indexOf(partialLower) === 0) {
                var fullValue = nonPartial + partial + value.substring(partial.length, value.length);

                var label = partial.length ? '<b>' + partial + '</b>' + value.substring(partial.length) : value;

                if (matchedFacets[value] !== -1) {
                  label += ' (' + matchedFacets[value] + ')';
                }
                if (matchedFacets[value] !== 0) {
                  facetSuggestions.push({ label: label, value: fullValue });
                  newSuggestions.push(fullValue);
                }
              }
            });
          }
        }

        if (partial !== '' && self.lastParseResult.suggestResults) {
          newSuggestions = newSuggestions.concat(self.autocompleteFromEntries(nonPartial, partial));
        }
        self.facetSuggestions(facetSuggestions);
        if (self.changedAfterFocus && (facetSuggestions.length > 1 || (facetSuggestions.length === 1 && facetSuggestions[0].value !== self.searchInput()))) {
          self.facetDropDownVisible(true);
        } else if (self.facetDropDownVisible()) {
          self.facetDropDownVisible(false);
        }
        self.suggestions(newSuggestions);
      };

      ko.components.register('inline-autocomplete', {
        viewModel: InlineAutocomplete,
        template: {element: 'inline-autocomplete-template'}
      });
    })();
  </script>
</%def>