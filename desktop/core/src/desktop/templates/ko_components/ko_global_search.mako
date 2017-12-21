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

from metadata.conf import has_navigator

from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%def name="globalSearch()">

  <script type="text/html" id="hue-global-search-template">
    <!-- ko component: {
      name: 'inline-autocomplete',
      params: {
        hasFocus: searchHasFocus,
        disableNavigation: true,
        placeHolder: '${ _ko('Search data and saved documents...') if has_navigator(user) else _ko('Search saved documents...') }',
        querySpec: querySpec,
        onClear: function () { selectedIndex(null); searchResultVisible(false); },
        facets: ['type', 'tags'],
        knownFacetValues: knownFacetValues,
        autocompleteFromEntries: autocompleteFromEntries,
        triggerObservable: searchResultCategories
      }
    } --><!-- /ko -->
    <!-- ko if: searchResultVisible-->
    <div class="global-search-results" data-bind="onClickOutside: onResultClickOutside, css: { 'global-search-empty' : searchResultCategories().length === 0 }, style: { 'height' : heightWhenDragging }">
      <!-- ko hueSpinner: { spin: loading() && searchResultCategories().length === 0 , center: true, size: 'large' } --><!-- /ko -->
      <!-- ko if: !loading() && searchResultCategories().length === 0 -->
        <div>${ _('No results found.') }</div>
      <!-- /ko -->
      <!-- ko if: searchResultCategories().length > 0 -->
      <div class="global-search-alternatives" data-bind="niceScroll" style="position:relative;">
        <!-- ko foreach: searchResultCategories -->
        <div class="global-search-category">
          <div class="global-search-category-header" data-bind="text: label"></div>
          <ul data-bind="foreach: result">
            <!-- ko if: typeof draggable !== 'undefined' -->
            <li data-bind="multiClick: {
                click: function () { $parents[1].resultSelected($parentContext.$index(), $index()) },
                dblClick: function () { $parents[1].resultSelected($parentContext.$index(), $index()); $parents[1].openResult(); }
              }, html: label, css: { 'selected': $parents[1].selectedResult() === $data }, draggableText: { text: draggable, meta: draggableMeta }"></li>
            <!-- /ko -->
            <!-- ko if: typeof draggable === 'undefined' -->
            <li data-bind="multiClick: {
                click: function () { $parents[1].resultSelected($parentContext.$index(), $index()) },
                dblClick: function () { $parents[1].resultSelected($parentContext.$index(), $index()); $parents[1].openResult(); }
              }, html: label, css: { 'selected': $parents[1].selectedResult() === $data }"></li>
            <!-- /ko -->
          </ul>
        </div>
        <!-- /ko -->
        <!-- ko hueSpinner: { spin: loading() && searchResultCategories().length > 0, center: true, inline: true } --><!-- /ko -->
      </div>
      <div class="global-search-preview" style="overflow: auto;">
        <!-- ko with: selectedResult -->
          <!-- ko switch: type -->
            <!-- ko case: ['database', 'document', 'field', 'table', 'view', 'hueApp']  -->
              <!-- ko component: { name: 'context-popover-contents-global-search', params: { data: data, globalSearch: $parent } } --><!-- /ko -->
            <!-- /ko -->
            <!-- ko case: $default -->
              <pre data-bind="text: ko.mapping.toJSON($data)"></pre>
            <!-- /ko -->
          <!-- /ko -->
        <!--/ko -->
      </div>
      <!-- /ko -->
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="top-search-autocomp-item">
    <a href="javascript:void(0);">
      <div>
        <div><i class="fa fa-fw" data-bind="css: icon"></i></div>
        <div>
          <div data-bind="html: label, style: { 'padding-top': description ? 0 : '9px' }"></div>
          <!-- ko if: description -->
          <div data-bind="html: description"></div>
          <!-- /ko -->
        </div>
      </div>
    </a>
  </script>

  <script type="text/html" id="top-search-autocomp-no-match">
    <div style="height: 30px;">
      <div>${ _('No match found') }</div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var GlobalSearch = function (params) {
        var self = this;
        self.apiHelper = ApiHelper.getInstance();
        self.knownFacetValues = ko.observable({});

        self.autocompleteThrottle = -1;
        self.fetchThrottle = -1;

        self.searchHasFocus = ko.observable(false);
        self.querySpec = ko.observable();
        self.searchActive = ko.observable(false);
        self.searchResultVisible = ko.observable(false);
        self.heightWhenDragging = ko.observable(null);
        self.searchResultCategories = ko.observableArray([]);
        self.selectedIndex = ko.observable();
        self.loading = ko.observable(false);

        self.selectedResult = ko.pureComputed(function () {
          if (self.selectedIndex()) {
            return self.searchResultCategories()[self.selectedIndex().categoryIndex].result[self.selectedIndex().resultIndex]
          } else if (self.searchResultCategories().length > 0 && self.searchResultCategories()[0].result.length > 0) {
            return self.searchResultCategories()[0].result[0];
          }
        }).extend({ deferred: true });;

        var deferredCloseIfVisible = function () {
          window.setTimeout(function () {
            if (self.searchResultVisible()) {
              self.close();
            }
          }, 0);
        };

        huePubSub.subscribe('context.popover.open.in.metastore', deferredCloseIfVisible);
        huePubSub.subscribe('context.popover.show.in.assist', deferredCloseIfVisible);
        huePubSub.subscribe('sample.error.insert.click', deferredCloseIfVisible);

        huePubSub.subscribe('draggable.text.started', function (meta) {
          // We have to set the height to 0 when dragging a text, just closing the results will break the
          // jQuery draggable plugin
          if (meta.source === 'globalSearch') {
            huePubSub.subscribeOnce('draggable.text.stopped', function () {
              self.heightWhenDragging(null);
              self.close();
            });
            self.heightWhenDragging(0);
          }
        });

        self.querySpec.subscribe(function (newValue) {
          if (newValue && newValue.query !== '') {
            window.clearTimeout(self.fetchThrottle);
            self.fetchThrottle = window.setTimeout(function () {
              self.fetchResults(newValue.query);
            }, 500);
          } else {
            self.selectedIndex(undefined);
            self.searchResultCategories([]);
          }
        });

        self.autocompleteFromEntries = function (lastNonPartial, partial) {
          var result;
          var partialLower = partial.toLowerCase();
          self.searchResultCategories().every(function (category) {
            return category.result.every(function (entry) {
              if (category.type === 'documents' && entry.data.originalName.toLowerCase().indexOf(partialLower) === 0) {
                result = lastNonPartial + partial + entry.data.originalName.substring(partial.length, entry.data.originalName.length);
                return false;
              } else if (entry.data.selectionName && entry.data.selectionName.toLowerCase().indexOf(partialLower) === 0) {
                result = lastNonPartial + partial + entry.data.selectionName.substring(partial.length, entry.data.selectionName.length);
                return false;
              }
              return true;
            });
          });
          return result;
        };

        self.searchHasFocus.subscribe(function (newVal) {
          if (newVal && self.querySpec() && self.querySpec().query !== '') {
            if (!self.searchResultVisible()) {
              self.searchResultVisible(true);
            }
          }
        });

        self.searchResultVisible.subscribe(function (newVal) {
          if (newVal) {
            self.heightWhenDragging(null);
          } else {
            self.selectedIndex(undefined);
          }
        });

        // TODO: Consider attach/detach on focus
        $(document).keydown(function (event) {
          if (!self.searchHasFocus() && !self.searchResultVisible()) {
            return;
          }

          if (event.keyCode === 13 && self.searchHasFocus() && self.querySpec() && self.querySpec().query !== '') {
            window.clearTimeout(self.fetchThrottle);
            self.fetchResults(self.querySpec().query);
            return;
          }

          if (self.searchResultVisible() && self.searchResultCategories().length > 0) {
            var currentIndex = self.selectedIndex();
            if (event.keyCode === 40) { // Down
              self.searchHasFocus(false);
              if (currentIndex && !(self.searchResultCategories()[currentIndex.categoryIndex].result.length <= currentIndex.resultIndex + 1 && self.searchResultCategories().length <= currentIndex.categoryIndex + 1)) {
                if (self.searchResultCategories()[currentIndex.categoryIndex].result.length <= currentIndex.resultIndex + 1) {
                  self.selectedIndex({ categoryIndex: currentIndex.categoryIndex + 1, resultIndex: 0 });
                } else {
                  self.selectedIndex({ categoryIndex: currentIndex.categoryIndex, resultIndex: currentIndex.resultIndex + 1})
                }
              } else {
                self.selectedIndex({ categoryIndex: 0, resultIndex: 0 });
              }
              event.preventDefault();
            } else if (event.keyCode === 38) { // Up
              self.searchHasFocus(false);
              if (currentIndex && !(currentIndex.categoryIndex === 0 && currentIndex.resultIndex === 0)) {
                if (currentIndex.resultIndex === 0) {
                  self.selectedIndex({ categoryIndex: currentIndex.categoryIndex - 1, resultIndex: self.searchResultCategories()[currentIndex.categoryIndex - 1].result.length - 1 });
                } else {
                  self.selectedIndex({ categoryIndex: currentIndex.categoryIndex, resultIndex: currentIndex.resultIndex - 1 });
                }
              } else {
                self.selectedIndex({ categoryIndex: self.searchResultCategories().length - 1, resultIndex: self.searchResultCategories()[self.searchResultCategories().length - 1].result.length - 1 });
              }
              event.preventDefault();
            } else if (event.keyCode === 13 && !self.searchHasFocus() && self.selectedIndex()) { // Enter
              self.openResult();
            }
          }
        });
      };

      GlobalSearch.prototype.close = function () {
        var self = this;
        self.searchResultVisible(false);
        self.querySpec({
          query: '',
          facets: {},
          text: []
        });
      };

      GlobalSearch.prototype.openResult = function () {
        var self = this;
        var selectedResult = self.selectedResult();
        if (['database', 'table', 'field', 'view'].indexOf(selectedResult.type) !== -1) {
          huePubSub.publish('context.popover.show.in.assist');
        } else if (selectedResult.type === 'document') {
          huePubSub.publish('open.link', '/hue' + selectedResult.data.link);
        } else if (selectedResult.type === 'hueApp' && selectedResult.data.interpreter && selectedResult.data.interpreter.page) {
          huePubSub.publish('open.link', selectedResult.data.interpreter.page);
        } else if (selectedResult.type === 'hueApp' && selectedResult.data.app && selectedResult.data.app.page) {
          huePubSub.publish('open.link', selectedResult.data.app.page);
        }
        self.close();
      };

      GlobalSearch.prototype.resultSelected = function (categoryIndex, resultIndex) {
        var self = this;
        if (!self.selectedIndex() || !(self.selectedIndex().categoryIndex === categoryIndex && self.selectedIndex().resultIndex === resultIndex)) {
          self.selectedIndex({ categoryIndex: categoryIndex, resultIndex: resultIndex });
        }
      };

      GlobalSearch.prototype.onResultClickOutside = function () {
        var self = this;
        if (!self.searchResultVisible() || self.searchHasFocus()) {
          return false;
        }
        self.searchResultVisible(false);
        window.clearTimeout(self.fetchThrottle);
        window.clearTimeout(self.autocompleteThrottle);
      };

      GlobalSearch.prototype.mainSearchSelect = function (entry) {
        if (entry.data && entry.data.link) {
          huePubSub.publish('open.link', entry.data.link);
        } else if (!/:\s*$/.test(entry.value)) {
          huePubSub.publish('assist.show.sql');
          huePubSub.publish('assist.db.search', entry.value);
        }
      };

      var HUE_APP_CATEGORY = 'hueApp';
      var HUE_DOC_CATEGORY = 'documents';
      var NAV_CATEGORY = 'nav';

      var CATEGORIES = {
        'table': '${ _('Tables') }',
        'database': '${ _('Databases') }',
        'field': '${ _('Columns') }',
        'partition': '${ _('Partitions') }',
        'view': '${ _('Views') }',
        'hueDoc': '${ _('Documents') }',
        'hueApp': '${ _('Applications') }'
      };


      GlobalSearch.prototype.fetchHueConfig = function () {
        var promise = $.Deferred();
        huePubSub.publish('cluster.config.get.config', promise.resolve);
        return promise;
      };

      GlobalSearch.prototype.updateCategories = function (type, categoriesToAdd) {
        var self = this;
        var newCategories = self.searchResultCategories().filter(function (category) {
          return category.type !== type;
        });

        var change = newCategories.length !== self.searchResultCategories().length;

        if (categoriesToAdd.length > 0) {
          newCategories = newCategories.concat(categoriesToAdd);
          newCategories.sort(function (a, b) {
            if (a.weight === b.weight) {
              return a.label.localeCompare(b.label);
            }
            return b.weight - a.weight;
          });
          change = true;
        }

        if (change) {
          var selected = self.selectedResult();
          var newIndex = undefined;
          if (selected) {
            for (var i = 0; i < newCategories.length; i++) {
              for (var j = 0; j < newCategories[i].result.length; j++) {
                if (newCategories[i].result[j].type === selected.type && newCategories[i].result[j].label === selected.label) {
                  newIndex = { categoryIndex: i, resultIndex: j };
                  break;
                }
              }
              if (newIndex) {
                break;
              }
            }
          }
          self.selectedIndex(newIndex);
          self.searchResultCategories(newCategories);
        }
      };

      GlobalSearch.prototype.fetchResults = function (query) {
        var self = this;
        self.loading(true);
        self.searchResultVisible(true);
        var hueDocsPromise = self.apiHelper.fetchHueDocsInteractive(query);
        var navPromise = self.apiHelper.fetchNavEntitiesInteractive(query);
        var hueAppsPromise = self.fetchHueConfig();

        hueAppsPromise.done(function (apps) {
          var categories = [];

          if (apps && apps.app_config) {
            var hueApps = {
              type: HUE_APP_CATEGORY,
              label: CATEGORIES[HUE_APP_CATEGORY],
              result: [],
              weight: 1
            };
            Object.keys(apps.app_config).forEach(function (appConfigKey) {
              var appCatecory = apps.app_config[appConfigKey];
              var addAll = appCatecory.name.toLowerCase().indexOf(query) === 0 || appCatecory.displayName.toLowerCase().indexOf(query) === 0;
              if (appCatecory.interpreters) {
                appCatecory.interpreters.forEach(function (interpreter) {
                  // Special case for metastore that is now called table browser and hdfs
                  var specialMatch = appCatecory.name === 'browser' && (
                    (interpreter.type === 'tables' && 'metastore'.indexOf(query.toLowerCase()) === 0) ||
                    (interpreter.type === 'hdfs' && 'hdfs'.indexOf(query.toLowerCase()) === 0));
                  if (addAll || specialMatch || interpreter.displayName.toLowerCase().indexOf(query.toLowerCase()) === 0) {
                    var label;
                    if (appCatecory.name === 'browser') {
                      label = '${ _('Browse') } ' + interpreter.displayName;
                    } else {
                      label = interpreter.displayName + ' ' + appCatecory.displayName;
                    }
                    hueApps.result.push({
                      label: label,
                      type: HUE_APP_CATEGORY,
                      data: {
                        interpreter: interpreter,
                        app: appCatecory,
                        type: HUE_APP_CATEGORY,
                        originalName: interpreter.displayName
                      }
                    })
                  }
                })
              }
            })
          }
          if (hueApps.result.length > 0) {
            hueApps.result.sort(function (a, b) {
              return a.label.localeCompare(b.label);
            });
            categories.push(hueApps);
          }

          self.updateCategories(HUE_APP_CATEGORY, categories);
        });

        hueDocsPromise.done(function (data) {
          var categories = [];

          var docCategory = {
            label: CATEGORIES.hueDoc,
            result: [],
            type: HUE_DOC_CATEGORY,
            weight: 3
          };

          data.results.forEach(function (doc) {
            docCategory.result.push({
              label: doc.hue_name,
              draggable: doc.originalName,
              draggableMeta: {
                source: 'globalSearch'
              },
              type: 'document',
              data: doc
            })
          });

          if (docCategory.result.length) {
            categories.push(docCategory);
          }

          self.updateCategories(HUE_DOC_CATEGORY, categories);
        });

        navPromise.done(function (data) {
          if (data.facets) {
            var facetValues = ko.unwrap(self.knownFacetValues);
            Object.keys(data.facets).forEach(function (facet) {
              if (!facetValues[facet] && Object.keys(data.facets[facet]).length > 0) {
                facetValues[facet] = {};
              }
              Object.keys(data.facets[facet]).forEach(function (facetKey) {
                facetValues[facet][facetKey] = data.facets[facet][facetKey];
              });
            })
          }
          var categories = [];
          var newCategories = {};
          data.results.forEach(function (result) {
            var typeLower = result.type.toLowerCase();
            if (CATEGORIES[typeLower]) {
              var category = newCategories[typeLower];
              if (!category) {
                category = {
                  label: CATEGORIES[typeLower],
                  result: [],
                  type: NAV_CATEGORY,
                  weight: 2
                };
                newCategories[typeLower] = category;
              }
              var meta = {
                source: 'globalSearch'
              };
              if (result.type.toLowerCase() === 'database') {
                meta.type = 'sql';
                meta.database = result.originalName
              } else if (result.type.toLowerCase() === 'table') {
                meta.type = 'sql';
                var split = result.originalName.split('.');
                if (split.length == 2) {
                  meta.database = split[0];
                  meta.table = split[1];
                }
              } else if (result.type.toLowerCase() === 'field') {
                meta.type = 'sql';
                var split = result.originalName.split('.');
                if (split.length >= 3) {
                  meta.database = split[0];
                  meta.table = split[1];
                  meta.column = split[2];
                }
              }
              category.result.push({
                label: result.hue_name || result.originalName,
                draggable: result.originalName,
                draggableMeta: meta,
                type: typeLower,
                data: result
              })
            }
          });

          Object.keys(newCategories).forEach(function (key) {
            categories.push(newCategories[key]);
          });

          self.updateCategories(NAV_CATEGORY, categories);
        });

        $.when.apply($, [hueAppsPromise, navPromise, hueDocsPromise]).always(function () {
          self.loading(false);
        })
      };

      ko.components.register('hue-global-search', {
        viewModel: GlobalSearch,
        template: {element: 'hue-global-search-template'}
      });
    })();
  </script>
</%def>