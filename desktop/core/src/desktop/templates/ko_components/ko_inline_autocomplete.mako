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
        <input class="inline-autocomplete-input" autocorrect="off" autocapitalize="off" spellcheck="false" type="text" data-bind="attr: { 'placeHolder' : hasFocus() ? '' : placeHolder }, textInput: searchInput, hasFocus: hasFocus, clearable: { value: searchInput, onClear: onClear }">
        <input class="inline-autocomplete-autocomplete" disabled type="text" data-bind="value: inlineAutocomplete">
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var getSortedFacets = function (facetIndex) {
        var result = Object.keys(facetIndex);
        result.sort(function (a, b) {
          if (facetIndex[a] > facetIndex[b]) {
            return -1;
          }
          if (facetIndex[b] > facetIndex[a]) {
            return 1;
          }
          return a.localeCompare(b);
        });
        return result;
      };

      var InlineAutocomplete = function (params) {
        var self = this;
        self.disposals = [];

        self.placeHolder = params.placeHolder || '${ _('Filter...') }';
        self.hasFocus = params.hasFocus || ko.observable();
        self.querySpec = params.querySpec;
        self.autocompleteFromEntries = params.autocompleteFromEntries || function () {};
        self.facets = params.facets || [];
        self.knownFacetValues = params.knownFacetValues || {};
        self.uniqueFacets = !!params.uniqueFacets;
        self.disableNavigation = !!params.disableNavigation;

        self.searchInput = ko.observable('');
        self.suggestions = ko.observableArray();
        self.selectedSuggestionIndex = ko.observable(0);

        self.suggestions.subscribe(function () {
          self.selectedSuggestionIndex(0);
        });

        self.inlineAutocomplete = ko.pureComputed(function () {
          if (self.suggestions().length === 0) {
            return '';
          }
          return self.suggestions()[self.selectedSuggestionIndex()];
        });

        self.lastResult = {};

        self.querySpec({
          query: '',
          facets: {},
          text: []
        });

        var querySpecSub = self.querySpec.subscribe(function (newVal) {
          if (!newVal || !newVal.query) {
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
          if (newValue === '' && self.querySpec() && self.querySpec().query === '') {
            self.clearSuggestions();
            return;
          }
          if (newValue === '' && self.querySpec() && self.querySpec().query !== '') {
            self.querySpec({
              query: '',
              facets: {},
              text: []
            });
          } else {
            // TODO: Get cursor position and split to before and after
            self.lastResult = globalSearchParser.parseGlobalSearch(newValue, '');
            if (hueDebug && hueDebug.showGlobalSearchParseResults) {
              console.log(self.lastResult);
            }
            var querySpec = { query: newValue };
            if (self.lastResult.facets) {

              var knownFacetValues = ko.unwrap(self.knownFacetValues);
              var cleanFacets = {};
              Object.keys(self.lastResult.facets).forEach(function (facet) {
                if (!knownFacetValues[facet]) {
                  cleanFacets[facet] = self.lastResult.facets[facet];
                } else {
                  cleanFacets[facet] = {};
                  Object.keys(self.lastResult.facets[facet]).forEach(function (value) {
                    if (knownFacetValues[facet][value]) {
                      cleanFacets[facet][value] = self.lastResult.facets[facet][value];
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
                        cleanFacets[facet][value] = self.lastResult.facets[facet][value];
                      }
                    }
                  })
                }
              });
              querySpec.facets = cleanFacets;
            }
            if (self.lastResult.text) {
              querySpec.text = self.lastResult.text;
            }
            self.querySpec(querySpec);
          }

          if (newValue === '') {
            self.clearSuggestions();
          } else if (self.inlineAutocomplete() === newValue || self.inlineAutocomplete().indexOf(newValue) !== 0) {
            self.autocomplete();
          } else if (self.inlineAutocomplete().indexOf(newValue) === 0) {
            var newAutocomp = self.inlineAutocomplete();
            while (newAutocomp.lastIndexOf(' ') >= newValue.length) {
              newAutocomp = newAutocomp.substring(0, newAutocomp.lastIndexOf(' '));
            }
            if (newAutocomp !== self.inlineAutocomplete()) {
              self.suggestions([newAutocomp]);
            }
          }
        });

        self.disposals.push(function () {
          inputSub.dispose();
        });

        var onKeyDown = function (event) {
          if (!self.hasFocus()) {
            return;
          }
          if (!self.disableNavigation && event.keyCode === 38 && self.suggestions().length) { // Up
            if (self.selectedSuggestionIndex() === 0) {
              self.selectedSuggestionIndex(self.suggestions().length - 1);
            } else {
              self.selectedSuggestionIndex(self.selectedSuggestionIndex() - 1);
            }
            event.preventDefault();
            return;
          }

          if (!self.disableNavigation && event.keyCode === 40 && self.suggestions().length) { // Down
            if (self.selectedSuggestionIndex() === self.suggestions().length - 1) {
              self.selectedSuggestionIndex(0);
            } else {
              self.selectedSuggestionIndex(self.selectedSuggestionIndex() + 1);
            }
            event.preventDefault();
            return;
          }
          if (event.keyCode === 32 && event.ctrlKey) { // Ctrl-Space
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
          $(document).off('keydown', onKeyDown);
        });

        var focusSub = self.hasFocus.subscribe(function (newVal) {
          if (!newVal) {
            self.clearSuggestions();
            $(document).off('keydown', onKeyDown);
          } else if (self.searchInput() !== '') {
            self.autocomplete();
            $(document).on('keydown', onKeyDown);
          } else {
            $(document).on('keydown', onKeyDown);
          }
        });

        self.disposals.push(function () {
          focusSub.dispose();
        });
      };

      InlineAutocomplete.prototype.clearSuggestions = function () {
        var self = this;
        if (self.suggestions().length > 0) {
          self.suggestions([]);
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
        if (!self.lastResult) {
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
        var partialLower = partial.toLowerCase();
        if (self.lastResult.suggestFacets) {
          var existingFacetIndex = {};
          if (self.uniqueFacets && self.lastResult.facets) {
            Object.keys(self.lastResult.facets).forEach(function (facet) {
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

        if (self.lastResult.suggestFacetValues) {
          var facetValues = ko.unwrap(self.knownFacetValues);
          if (facetValues[self.lastResult.suggestFacetValues.toLowerCase()]) {
            getSortedFacets(facetValues[self.lastResult.suggestFacetValues.toLowerCase()]).forEach(function (value) {
              if (value.toLowerCase().indexOf(partialLower) === 0) {
                newSuggestions.push(nonPartial + partial + value.substring(partial.length, value.length));
              }
            });
          }
        }

        if (partial !== '' && self.lastResult.suggestResults) {
          newSuggestions = newSuggestions.concat(self.autocompleteFromEntries(nonPartial, partial));
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