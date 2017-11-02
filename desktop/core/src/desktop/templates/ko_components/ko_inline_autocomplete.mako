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

        self.searchInput = ko.observable('');
        self.inlineAutocomplete = ko.observable('');
        self.lastResult = {};

        self.querySpec({
          query: '',
          facets: {},
          text: []
        });

        var querySpecSub = self.querySpec.subscribe(function (newVal) {
          if (!newVal || !newVal.query) {
              self.searchInput('');
              self.inlineAutocomplete('');
          }
        });

        self.disposals.push(function () {
          querySpecSub.dispose();
        });

        self.onClear = function () {
          if (params.onClear) {
            params.onClear();
          }
          self.inlineAutocomplete('');
        };

        if (params.triggerObservable) {
          var triggerSub = params.triggerObservable.subscribe(function () {
            self.autocomplete(self.searchInput(), self.inlineAutocomplete);
          });
          self.disposals.push(function () {
            triggerSub.dispose();
          })
        }

        var inputSub = self.searchInput.subscribe(function (newValue) {
          if (newValue === '' && self.querySpec() && self.querySpec().query === '') {
            self.inlineAutocomplete('');
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
            self.inlineAutocomplete('');
          } else if (self.inlineAutocomplete() === newValue || self.inlineAutocomplete().indexOf(newValue) !== 0) {
            self.autocomplete(newValue, self.inlineAutocomplete);
          } else if (self.inlineAutocomplete().indexOf(newValue) === 0) {
            var newAutocomp = self.inlineAutocomplete();
            while (newAutocomp.lastIndexOf(' ') >= newValue.length) {
              newAutocomp = newAutocomp.substring(0, newAutocomp.lastIndexOf(' '));
            }
            if (newAutocomp !== self.inlineAutocomplete()) {
              self.inlineAutocomplete(newAutocomp);
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
          if (event.keyCode === 32 && event.ctrlKey) { // Ctrl-Space
            self.autocomplete(self.searchInput(), self.inlineAutocomplete);
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
            self.inlineAutocomplete('');
            $(document).off('keydown', onKeyDown);
          } else if (self.searchInput() !== '') {
            self.autocomplete(self.searchInput(), self.inlineAutocomplete);
            $(document).on('keydown', onKeyDown);
          } else {
            $(document).on('keydown', onKeyDown);
          }
        });

        self.disposals.push(function () {
          focusSub.dispose();
        });
      };

      InlineAutocomplete.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      InlineAutocomplete.prototype.autocomplete = function (text, callback) {
        var self = this;
        if (!self.lastResult) {
          callback('');
          return;
        }

        var partial, nonPartial;
        var partialMatch = text.match(/([^:\s]+)$/i);
        if (partialMatch) {
          partial = partialMatch[0];
          nonPartial = text.substring(0, text.length - partial.length);
        } else {
          partial = '';
          nonPartial = text;
        }

        var newAutocomplete = '';
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
          self.facets.every(function (facet) {
            if (self.uniqueFacets && existingFacetIndex[facet]) {
              return true;
            }
            if (partial.length === 0 || facet.indexOf(partialLower) === 0) {
              var remainder = facet.substring(partial.length);
              suggestion += isLowerCase ? remainder : remainder.toUpperCase();
              suggestion += ':';
              newAutocomplete = suggestion;
              return false;
            }
            return true;
          });
        }

        if (self.lastResult.suggestFacetValues && !newAutocomplete) {
          var facetValues = ko.unwrap(self.knownFacetValues);
          if (facetValues[self.lastResult.suggestFacetValues.toLowerCase()]) {
            getSortedFacets(facetValues[self.lastResult.suggestFacetValues.toLowerCase()]).every(function (value) {
              if (value.toLowerCase().indexOf(partialLower) === 0) {
                newAutocomplete = nonPartial + partial + value.substring(partial.length, value.length);
                return false;
              }
              return true;
            });
          }
        }

        if (partial !== '' && self.lastResult.suggestResults && !newAutocomplete) {
          newAutocomplete = self.autocompleteFromEntries(nonPartial, partial);
        }

        if (!newAutocomplete) {
          callback('');
        } else if (newAutocomplete !== self.inlineAutocomplete()) {
          callback(newAutocomplete);
        }
      };

      ko.components.register('inline-autocomplete', {
        viewModel: InlineAutocomplete,
        template: {element: 'inline-autocomplete-template'}
      });
    })();
  </script>
</%def>