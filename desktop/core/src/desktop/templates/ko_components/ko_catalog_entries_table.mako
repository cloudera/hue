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
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%def name="catalogEntriesTable()">

  <script type="text/html" id="catalog-entries-list-template">
    <!-- ko if: !loading() -->
    <div class="catalog-entries-list-filter context-popover-inline-autocomplete">
      <!-- ko component: {
        name: 'inline-autocomplete',
        params: {
          querySpec: querySpec,
          facets: facets,
          knownFacetValues: knownFacetValues,
          autocompleteFromEntries: autocompleteFromEntries
        }
      } --><!-- /ko -->
    </div>
    <!-- /ko -->

    <div class="catalog-entries-list-container">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'xlarge' } --><!-- /ko -->

      <!-- ko if: !loading() && catalogEntry.isDatabase() -->
      <table class="table table-condensed table-nowrap">
        <thead>
        <tr>
          <th data-bind="text: catalogEntry.getSourceType() !== 'solr' ? '${ _ko("Table") }' : '${ _ko("Collection") }'"></th>
          <th>${ _("Description") } <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
        </tr>
        </thead>
        <!-- ko if: filteredEntries().length -->
        <tbody data-bind="foreach: filteredEntries">
        <tr>
          <td><a href="javascript: void(0);" data-bind="text: catalogEntry.name, click: onClick, attr: { 'title': catalogEntry.getTitle() }"></a></td>
          <td data-bind="text: catalogEntry.getCommentObservable(), attr: { 'title': catalogEntry.getCommentObservable() }"></td>
        </tr>
        </tbody>
        <!-- /ko -->
        <!-- ko if: filteredEntries().length === 0 -->
        <tbody>
        <tr>
          <!-- ko ifnot: hasErrors -->
          <td colspan="2" style="font-style: italic;">${ _("No entries found") }</td>
          <!-- /ko -->
          <!-- ko if: hasErrors -->
          <td colspan="2" style="font-style: italic;">${ _("Error loading entries") }</td>
          <!-- /ko -->
        </tr>
        </tbody>
        <!-- /ko -->
      </table>
      <!-- /ko -->

      <!-- ko if: !loading() && (catalogEntry.isTableOrView() || catalogEntry.isComplex()) -->
      <table class="table table-condensed table-nowrap">
        <thead>
        <tr>
          <th><span data-bind="text: catalogEntry.getSourceType() !== 'solr' ? '${ _ko("Column") }' : '${ _ko("Field") }'"></span> (<span data-bind="text: filteredEntries().length"></span>)</th>
          <th>${ _("Type") }</th>
          <th>${ _("Description") } <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
          <th colspan="2">${ _("Sample") } <!-- ko if: loadingSamples --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
        </tr>
        </thead>
        <!-- ko if: filteredEntries().length -->
        <tbody data-bind="foreach: filteredEntries">
        <tr>
          <td class="name-column" data-bind="attr: { 'title': catalogEntry.name + ' - ${ _ko("Click for more details") }' }">
            <a href="javascript: void(0);" data-bind="click: onClick">
              <span data-bind="text: catalogEntry.name"></span>
              <!-- ko if: catalogEntry.isPrimaryKey() -->
              &nbsp;<i title="${ _("Primary Key") }"class="fa fa-key"></i>
              <!-- /ko -->
              <!-- ko if: catalogEntry.isPartitionKey() -->
              &nbsp;<i title="${ _("Partition Key") }"class="fa fa-key"></i>
              <!-- /ko -->
              <!-- ko if: popularity -->
              &nbsp;<i data-bind="attr: { 'title': '${ _ko("Popularity") }: ' + popularity() + '%' }" class="fa fa-star-o"></i>
              <!-- /ko -->
            </a>
          </td>
          <td class="type-column" data-bind="text: catalogEntry.getType(), attr: { 'title': catalogEntry.getRawType() }"></td>
          <td class="comment-column" data-bind="text: catalogEntry.getCommentObservable(), attr: { 'title': catalogEntry.getCommentObservable() }"></td>
          <td class="sample-column" data-bind="html: firstSample, attr: { 'title': hueUtils.html2text(firstSample()) }"></td>
          <td class="sample-column" data-bind="html: secondSample, attr: { 'title': hueUtils.html2text(secondSample()) }"></td>
        </tr>
        </tbody>
        <!-- /ko -->
        <!-- ko if: filteredEntries().length === 0 -->
        <tbody>
        <tr>
          <!-- ko ifnot: hasErrors -->
          <td colspan="5" style="font-style: italic;">${ _("No entries found") }</td>
          <!-- /ko -->
          <!-- ko if: hasErrors -->
          <td colspan="5" style="font-style: italic;">${ _("Error loading entries") }</td>
          <!-- /ko -->
        </tr>
        </tbody>
        <!-- /ko -->
      </table>
      <!-- /ko -->

      <!-- ko if: !loading() && catalogEntry.isField() && !catalogEntry.isComplex() -->
      <table class="table table-condensed table-nowrap">
        <thead>
          <tr>
            <th>${ _("Sample") }</th>
          </tr>
        </thead>
        <tbody data-bind="foreach: filteredColumnSamples">
          <tr>
            <td class="sample-column" data-bind="html: $data, attr: { 'title': hueUtils.html2text($data) }"></td>
          </tr>
        </tbody>
        <!-- ko if: filteredColumnSamples().length === 0 -->
        <tbody>
        <tr>
          <!-- ko ifnot: hasErrors -->
          <td style="font-style: italic;">${ _("No entries found") }</td>
          <!-- /ko -->
          <!-- ko if: hasErrors -->
          <td style="font-style: italic;">${ _("Error loading entries") }</td>
          <!-- /ko -->
        </tr>
        </tbody>
        <!-- /ko -->
      </table>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      function SampleEnrichedEntry(catalogEntry, onClick) {
        var self = this;
        self.catalogEntry = catalogEntry;
        self.popularity = ko.observable();
        self.firstSample = ko.observable();
        self.secondSample = ko.observable();
        self.onClick = onClick;
      }

      function CatalogEntriesList(params) {
        var self = this;
        self.catalogEntry = params.catalogEntry;
        self.entries = ko.observableArray();

        // If the entry is a column without children
        self.columnSamples = ko.observableArray();
        self.querySpec = ko.observable();
        self.cancellablePromises = [];
        self.loading = ko.observable(false);
        self.loadingNav = ko.observable(false);
        self.loadingSamples = ko.observable(false);
        self.hasErrors = ko.observable(false);

        // TODO: Can be computed based on contents (instead of always suggesting all col types etc.)
        self.knownFacetValues = ko.pureComputed(function () {
          if (self.catalogEntry.isDatabase()) {
            return { 'type': { 'table': -1, 'view': -1 } };
          } else if (self.catalogEntry.isTableOrView()) {
            var typeIndex = { 'type': {} };

            // Issue with filteredEntries is that it's not updated in time when typing,
            // i.e. type:| doesn't automatically open the suggestion list.
            self.entries().forEach(function (entry) {
              var type = entry.catalogEntry.getType().toLowerCase();
              if (!typeIndex['type'][type]) {
                typeIndex['type'][type] = 1;
              } else {
                typeIndex['type'][type]++;
              }
            });
            return typeIndex;
          }
        });

        self.facets = self.catalogEntry.isField() && !self.catalogEntry.isComplex() ? [] : ['type'];

        self.filteredColumnSamples = ko.pureComputed(function () {
          if (!self.querySpec() || self.querySpec().query === '') {
            return self.columnSamples();
          }

          return self.columnSamples().filter(function (sampleValue) {
            if (typeof sampleValue === 'undefined' || sampleValue === null) {
              return false;
            }
            return self.querySpec().text.every(function (text) {
              var textLower = text.toLowerCase();
              return sampleValue.toString().toLowerCase().indexOf(textLower) !== -1;
            });
          });
        });

        self.filteredEntries = ko.pureComputed(function () {
          if (!self.querySpec() || self.querySpec().query === '') {
            return self.entries();
          }

          var facets = self.querySpec().facets;
          var isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
          var isTextMatch = !self.querySpec().text || self.querySpec().text.length === 0;

          return self.entries().filter(function (entry) {
            var match = true;

            if (!isFacetMatch) {
              if (entry.catalogEntry.isField()) {
                match = !!facets['type'][entry.catalogEntry.getType().toLowerCase()];
              } else if (entry.catalogEntry.isTableOrView()) {
                match = (facets['type']['table'] && entry.catalogEntry.isTable()) || (facets['type']['view'] && entry.catalogEntry.isView()) ;
              }
            }

            if (match && !isTextMatch) {
              match = self.querySpec().text.every(function (text) {
                var textLower = text.toLowerCase();
                return entry.catalogEntry.name.toLowerCase().indexOf(textLower) !== -1
                  || entry.catalogEntry.getResolvedComment().toLowerCase().indexOf(textLower) !== -1;
              });
            }

            return match;
          });
        });

        self.autocompleteFromEntries = function (nonPartial, partial) {
          var result = [];
          var partialLower = partial.toLowerCase();
          self.entries().forEach(function (entry) {
            if (entry.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
              result.push(nonPartial + partial + entry.catalogEntry.name.substring(partial.length))
            }
          });
          return result;
        };

        self.loading(true);

        window.setTimeout(function () {
          if (self.catalogEntry.isField() && !self.catalogEntry.isComplex()) {
            self.cancellablePromises.push(self.catalogEntry.getSample({ silenceErrors: true, cancellable: true }).done(function (samples) {
              if (samples.data && samples.data.length) {
                self.columnSamples(samples.data);
              }
            }).fail(function () {
              self.hasErrors(true);
            }).always(function () {
              self.loading(false);
            }));
          } else {
            var onClick = function (sampleEnrichedEntry) {
              params.onClick(sampleEnrichedEntry.catalogEntry);
            };
            var childPromise = self.catalogEntry.getChildren({ silenceErrors: true, cancellable: true }).done(function (childEntries) {
              self.entries($.map(childEntries, function (entry) { return new SampleEnrichedEntry(entry, onClick) }));
            }).fail(function () {
              self.hasErrors(true);
            }).always(function () {
              self.loading(false);
            });

            var navMetaPromise = self.catalogEntry.loadNavigatorMetaForChildren({ silenceErrors: true, cancellable: true }).always(function () {
              self.loadingNav(false);
            });

            self.cancellablePromises.push(navMetaPromise);
            self.cancellablePromises.push(childPromise);

            self.cancellablePromises.push(self.catalogEntry.loadNavOptPopularityForChildren({ silenceErrors: true, cancellable: true }).done(function (popularEntries) {
              if (popularEntries.length) {
                childPromise.done(function () {
                  var entryIndex = {};
                  self.entries().forEach(function (entry) {
                    entryIndex[entry.catalogEntry.name] = entry;
                  });

                  var totalCount = 0;
                  var popularityToApply = [];
                  popularEntries.forEach(function (popularEntry) {
                    if (entryIndex[popularEntry.name] && popularEntry.navOptPopularity && popularEntry.navOptPopularity.selectColumn && popularEntry.navOptPopularity.selectColumn.columnCount > 0) {
                      totalCount += popularEntry.navOptPopularity.selectColumn.columnCount;
                      popularityToApply.push(function () {
                        entryIndex[popularEntry.name].popularity(Math.round(100 * popularEntry.navOptPopularity.selectColumn.columnCount / totalCount))
                      });
                    }
                  });
                  while (popularityToApply.length) {
                    popularityToApply.pop()();
                  }
                });
              }
            }));

            if (self.catalogEntry.isTableOrView() || self.catalogEntry.isField()) {
              self.loadingSamples(true);
              self.cancellablePromises.push(self.catalogEntry.getSample({ silenceErrors: true, cancellable: true }).done(function (sample) {
                childPromise.done(function () {
                  if (sample.meta && sample.meta.length && sample.data && sample.data.length) {
                    var entryIndex = {};
                    self.entries().forEach(function (entry) {
                      entryIndex[entry.catalogEntry.name] = entry;
                    });
                    for (var i = 0; i < sample.meta.length; i++) {
                      var name = sample.meta[i].name;
                      if (name.toLowerCase().indexOf(self.catalogEntry.name.toLowerCase() + '.') === 0) {
                        name = name.substring(self.catalogEntry.name.length + 1);
                      }
                      var sampleEntry = entryIndex[name];
                      if (sampleEntry) {
                        sampleEntry.firstSample(sample.data[0][i]);
                        if (sample.data.length > 1) {
                          sampleEntry.secondSample(sample.data[1][i])
                        }
                      }
                    }
                  }
                }).always(function () {
                  self.loadingSamples(false);
                })
              }).fail(function () {
                self.loadingSamples(false);
              }));
            }
          }
        }, 100)
      }

      CatalogEntriesList.prototype.dispose = function () {
        var self = this;
        while (self.cancellablePromises.length) {
          var promise = self.cancellablePromises.pop();
          if (promise.cancel) {
            promise.cancel();
          }
        }
      };

      ko.components.register('catalog-entries-list', {
        viewModel: CatalogEntriesList,
        template: { element: 'catalog-entries-list-template' }
      });
    })();
  </script>
</%def>
