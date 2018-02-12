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
    <!-- ko hueSpinner: { spin: loading, inline: true, size: 'small' } --><!-- /ko -->
    <!-- ko if: !loading() && columnSamples().length -->
    <table class="table table-condensed table-nowrap">
      <thead>
        <tr>
          <th>${ _("Sample") }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: columnSamples">
        <tr>
          <td data-bind="html: $data"></td>
        </tr>
      </tbody>
    </table>
    <!-- /ko -->

    <!-- ko if: !loading() && entries().length -->
    <div class="context-popover-inline-autocomplete" style="width: 250px">
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
    <!-- ko if: catalogEntry.isDatabase() -->
    <table class="table table-condensed table-nowrap">
      <thead>
      <tr>
        <th>${ _("Table") }</th><th>${ _("Description") }</th>
      </tr>
      </thead>
      <!-- ko if: filteredEntries().length -->
      <tbody data-bind="foreach: filteredEntries">
        <tr>
          <td><a href="javascript: void(0);" data-bind="text: catalogEntry.name, click: onClick"></a></td>
          <td data-bind="text: catalogEntry.getResolvedComment()"></td>
        </tr>
      </tbody>
      <!-- /ko -->
      <!-- ko if: filteredEntries().length === 0 -->
      <tbody>
        <tr>
          <td colspan="2" style="font-style: italic;">${ _("No result found") }</td>
        </tr>
      </tbody>
      <!-- /ko -->
    </table>
    <!-- /ko -->
    <!-- ko if: catalogEntry.isTableOrView() || catalogEntry.isComplex() -->
    <table class="table table-condensed table-nowrap">
      <thead>
        <tr>
          <th>${ _("Column") }</th><th>${ _("Type") }</th><th colspan="2">${ _("Sample") } <!-- ko if: loadingSamples --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
        </tr>
      </thead>
      <!-- ko if: filteredEntries().length -->
      <tbody data-bind="foreach: filteredEntries">
        <tr>
          <td><a href="javascript: void(0);" data-bind="text: catalogEntry.name, click: onClick"></a></td>
          <td data-bind="text: catalogEntry.getType()"></td>
          <td data-bind="html: firstSample"></td>
          <td data-bind="html: secondSample"></td>
        </tr>
      </tbody>
      <!-- /ko -->
      <!-- ko if: filteredEntries().length === 0 -->
      <tbody>
        <tr>
          <td colspan="4" style="font-style: italic;">${ _("No result found") }</td>
        </tr>
      </tbody>
      <!-- /ko -->
    </table>
    <!-- /ko -->
    <!-- /ko -->
  </script>

  <script type="text/javascript">
    (function () {

      function SampleEnrichedEntry(catalogEntry, onClick) {
        var self = this;
        self.catalogEntry = catalogEntry;
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
        self.errorloading = ko.observable(false);
        self.loadingSamples = ko.observable(false);

        // TODO: Can be computed based on contents (instead of always suggesting all col types etc.)
        self.knownFacetValues = {};
        if (self.catalogEntry.isDatabase()) {
          self.knownFacetValues = { 'type': { 'table': -1, 'view': -1 } };
        } else if (self.catalogEntry.isTableOrView()) {
          self.knownFacetValues = SQL_COLUMNS_KNOWN_FACET_VALUES;
        }
        self.facets = Object.keys(self.knownFacetValues);

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
                match = !!facets['type'][entry.catalogEntry.getType()];
              } else if (entry.catalogEntry.isTableOrView()) {
                match = (facets['type']['table'] && entry.catalogEntry.isTable()) || (facets['type']['view'] && entry.catalogEntry.isView()) ;
              }
            }

            if (match && !isTextMatch) {
              match = self.querySpec().text.every(function (text) {
                return entry.catalogEntry.name.toLowerCase().indexOf(text.toLowerCase()) !== -1 ||
                        entry.catalogEntry.getResolvedComment().toLowerCase().indexOf(text.toLowerCase()) !== -1;
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

        if (self.catalogEntry.isColumn() && !self.catalogEntry.isComplex()) {
          self.loading(true);
          self.catalogEntry.getSample({ silenceErrors: true }).done(function (samples) {
            if (samples.data && samples.data.length) {
              self.columnSamples(samples.data);
            }
          }).always(function () {
            self.loading(false);
          })
        } else if (self.catalogEntry.hasPossibleChildren()) {
          self.loading(true);
          var onClick = function (sampleEnrichedEntry) {
            params.onClick(sampleEnrichedEntry.catalogEntry);
          };
          var childPromise = self.catalogEntry.getChildren({ silenceErrors: true }).done(function (childEntries) {
            self.entries($.map(childEntries, function (entry) { return new SampleEnrichedEntry(entry, onClick) }));
          }).fail(function () {
            self.errorloading(true);
          }).always(function () {
            self.loading(false);
          });
          self.cancellablePromises.push(childPromise);

          if (self.catalogEntry.isTableOrView() || self.catalogEntry.isField()) {
            self.loadingSamples(true);
            self.cancellablePromises.push(self.catalogEntry.getSample({ silenceErrors: true }).done(function (sample) {
              childPromise.done(function () {
                if (sample.meta && sample.meta.length && sample.data && sample.data.length) {
                  var entryIndex = {};
                  self.entries().forEach(function (entry) {
                    entryIndex[entry.catalogEntry.name] = entry;
                  });
                  for (var i = 0; i < sample.meta.length; i++) {
                    var sampleEntry = entryIndex[sample.meta[i].name];
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
