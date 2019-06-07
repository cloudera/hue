// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <script type="text/html" id="entries-table-td-description">
    <td data-bind="attr: { 'title': comment }">
    <!-- ko if: $parent.editableDescriptions && !window.HAS_READ_ONLY_CATALOG -->
      <div class="hue-catalog-entries-table-desc" data-bind="visibleOnHover: { selector: '.editable-inline-action' }">
        <div data-bind="editable: comment, editableOptions: {
          mode: 'inline',
          enabled: true,
          type: 'textarea',
          showbuttons: 'bottom',
          inputclass: 'hue-table-browser-desc-input',
          toggle: 'manual',
          toggleElement: '.toggle-editable',
          placeholder: '${I18n('Add a description...')}',
          emptytext: '${I18n('Add a description...')}',
          inputclass: 'hue-catalog-entries-table-desc-input',
          rows: 6,
          save: saveComment,
          inlineEditAction: { editClass: 'toggle-editable editable-inline-action' },
          multiLineEllipsis: { overflowHeight: '40px', expandable: true, expandActionClass: 'editable-inline-action' }
        }">${I18n('Add a description...')}</div>
      </div>
    <!-- /ko -->
    <!-- ko if: !$parent.editableDescriptions || window.HAS_READ_ONLY_CATALOG -->
      <div class="entries-table-description" data-bind="text: comment, multiLineEllipsis"></div>
    <!-- /ko -->
    </td>
  </script>

  <script type="text/html" id="entries-table-tbody-no-entries">
    <tbody>
      <tr>
        <td style="font-style: italic;" data-bind="attr: { 'colspan': colCount + (typeof $component.selectedEntries !== 'undefined' ? 1 : 0) + ($component.contextPopoverEnabled ? 1 : 0) }">
          <!-- ko ifnot: hasErrors -->
          ${I18n('No entries found')}
          <!-- /ko -->
          <!-- ko if: hasErrors -->
          ${I18n('Error loading entries')}
          <!-- /ko -->
        </td>
      </tr>
    </tbody>
  </script>

  <script type="text/html" id="entries-table-shared-headers">
    <!-- ko if: typeof selectedEntries !== 'undefined' -->
    <th width="1%" class="select-column"><div class="hue-checkbox fa" data-bind="hueCheckAll: { allValues: filteredEntries, selectedValues: selectedEntries }"></div></th>
    <!-- /ko -->
    <!-- ko if: contextPopoverEnabled -->
    <th width="1%">&nbsp;</th>
    <!-- /ko -->
  </script>

  <script type="text/html" id="entries-table-shared-columns">
    <!-- ko if: typeof $parent.selectedEntries !== 'undefined' -->
    <td width="1%" class="select-column"><div class="hue-checkbox fa" data-bind="multiCheck: '#entryTable', value: $data, hueChecked: $parent.selectedEntries"></div></td>
    <!-- /ko -->
    <!-- ko if: $parent.contextPopoverEnabled -->
    <td width="1%"><a href="javascript: void(0);" data-bind="click: showContextPopover"><i class="fa fa-info"></i></a></td>
    <!-- /ko -->
  </script>

  <!-- ko if: !loading() && (!catalogEntry().isField() || catalogEntry().isComplex())-->
  <div class="context-popover-inline-autocomplete">
    <div class="context-popover-sample-filter">
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
  </div>
  <!-- /ko -->

  <div class="catalog-entries-list-container">
    <!-- ko hueSpinner: { spin: loading, center: true, size: 'xlarge' } --><!-- /ko -->
    <!-- ko if: !loading() && catalogEntry().isSource() -->
    <table id="entryTable" class="table table-condensed table-nowrap">
      <thead>
        <tr>
          <!-- ko template: 'entries-table-shared-headers' --><!-- /ko -->
          <th>${I18n('Database')}</th>
          <th>${I18n(
            'Description'
          )} <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
        </tr>
      </thead>
      <!-- ko if: filteredEntries().length -->
      <tbody data-bind="foreach: filteredEntries">
        <tr data-bind="click: onRowClick">
          <!-- ko template: 'entries-table-shared-columns' --><!-- /ko -->
          <td><a href="javascript: void(0);" data-bind="text: catalogEntry().name, click: onClick, attr: { 'title': catalogEntry().getTitle() }"></a></td>
          <!-- ko template: 'entries-table-td-description' --><!-- /ko -->
        </tr>
      </tbody>
      <!-- /ko -->
      <!-- ko if: filteredEntries().length === 0 -->
      <!-- ko template: { name: 'entries-table-tbody-no-entries', data: { colCount: 2, hasErrors: hasErrors } } --><!-- /ko -->
      <!-- /ko -->
    </table>
    <!-- /ko -->

    <!-- ko if: !loading() && catalogEntry().isDatabase() -->
    <table id="entryTable" class="table table-condensed table-nowrap">
      <thead>
      <tr>
        <!-- ko template: 'entries-table-shared-headers' --><!-- /ko -->
        <th data-bind="text: catalogEntry().getSourceType() !== 'solr' ? '${I18n(
          'Table'
        )}' : '${I18n('Collection')}'"></th>
        <th>${I18n(
          'Description'
        )} <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
      </tr>
      </thead>
      <!-- ko if: filteredEntries().length -->
      <tbody data-bind="foreach: filteredEntries">
      <tr data-bind="click: onRowClick">
        <!-- ko template: 'entries-table-shared-columns' --><!-- /ko -->
        <td><a href="javascript: void(0);" data-bind="text: catalogEntry().name, click: onClick, attr: { 'title': catalogEntry().getTitle() }"></a></td>
        <!-- ko template: 'entries-table-td-description' --><!-- /ko -->
      </tr>
      </tbody>
      <!-- /ko -->
      <!-- ko if: filteredEntries().length === 0 -->
      <!-- ko template: { name: 'entries-table-tbody-no-entries', data: { colCount: 2, hasErrors: hasErrors } } --><!-- /ko -->
      <!-- /ko -->
    </table>
    <!-- /ko -->

    <!-- ko if: !loading() && (catalogEntry().isTableOrView() || catalogEntry().isComplex()) -->
    <table class="table table-condensed table-nowrap">
      <thead>
      <tr>
        <!-- ko template: 'entries-table-shared-headers' --><!-- /ko -->
        <th><span data-bind="text: catalogEntry().getSourceType() !== 'solr' ? '${I18n(
          'Column'
        )}' : '${I18n(
  'Field'
)}'"></span> (<span data-bind="text: filteredEntries().length"></span>)</th>
        <th>${I18n('Type')}</th>
        <th>${I18n(
          'Description'
        )} <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
        <th colspan="2">${I18n(
          'Sample'
        )} <!-- ko if: loadingSamples() || sampleRefreshEnabled() --><i class="fa fa-spinner fa-spin"></i><!-- /ko --> <!-- ko if: sampleRefreshEnabled --><a class="inactive-action" href="javascript: void(0);" data-bind="toggle: sampleRefreshEnabled"><i class="fa fa-stop"></i></a><!-- /ko --></th>
      </tr>
      </thead>
      <!-- ko if: filteredEntries().length -->
      <tbody data-bind="foreach: filteredEntries">
      <tr data-bind="click: onRowClick">
        <!-- ko template: 'entries-table-shared-columns' --><!-- /ko -->
        <td class="name-column" data-bind="attr: { 'title': catalogEntry().name + ' - ${I18n(
          'Click for more details'
        )}' }">
          <a href="javascript: void(0);" data-bind="click: onClick">
            <span data-bind="text: catalogEntry().name"></span>
            <!-- ko if: isKey -->
            &nbsp;<i class="fa fa-key" data-bind="tooltip: { title: keyText, html: true }"></i>
            <!-- /ko -->
            <!-- ko if: popularity && popularity() >= 5 -->
            &nbsp;<i data-bind="tooltip: { title: '${I18n(
              'Popularity'
            )}: ' + popularity() + '%' }" class="fa fa-star-o"></i>
            <!-- /ko -->
          </a>
        </td>
        <td class="type-column" data-bind="text: catalogEntry().getType(), attr: { 'title': catalogEntry().getRawType() }"></td>
        <!-- ko template: 'entries-table-td-description' --><!-- /ko -->
        <td class="sample-column" data-bind="html: firstSample, attr: { 'title': hueUtils.html2text(firstSample()) }"></td>
        <td class="sample-column" data-bind="html: secondSample, attr: { 'title': hueUtils.html2text(secondSample()) }"></td>
      </tr>
      </tbody>
      <!-- /ko -->
      <!-- ko if: filteredEntries().length === 0 -->
      <!-- ko template: { name: 'entries-table-tbody-no-entries', data: { colCount: 5, hasErrors: hasErrors } } --><!-- /ko -->
      <!-- /ko -->
    </table>
    <!-- /ko -->

    <!-- ko if: !loading() && catalogEntry().isField() && !catalogEntry().isComplex() -->
    <!-- ko component: { name: 'field-samples', params: {
        catalogEntry: catalogEntry,
        onSampleClick: onSampleClick,
        refreshSampleInterval: refreshSampleInterval
      }} --><!-- /ko -->
    <!-- /ko -->
  </div>
`;

class SampleEnrichedEntry {
  constructor(index, catalogEntry, onClick, onRowClick) {
    const self = this;
    self.index = index;
    self.catalogEntry = ko.isObservable(catalogEntry) ? catalogEntry : ko.observable(catalogEntry);
    self.popularity = ko.observable(0);
    self.firstSample = ko.observable();
    self.secondSample = ko.observable();
    self.onClick = onClick;
    self.onRowClick = onRowClick;
    self.comment = self.catalogEntry().getCommentObservable();
    self.joinColumns = ko.observableArray();

    self.isKey = ko.pureComputed(() => {
      return (
        self.catalogEntry().isPrimaryKey() ||
        self.catalogEntry().isPartitionKey() ||
        self.joinColumns().length
      );
    });

    self.keyText = ko.pureComputed(() => {
      const keys = [];
      if (self.catalogEntry().isPrimaryKey()) {
        keys.push(I18n('Primary key'));
      }
      if (self.catalogEntry().isPartitionKey()) {
        keys.push(I18n('Partition key'));
      }
      if (self.joinColumns().length) {
        let key = I18n(self.joinColumns().length > 1 ? 'Foreign keys' : 'Foreign key') + ':';
        self.joinColumns().forEach(joinCol => {
          key += '<br/>' + joinCol;
        });
        keys.push(key);
      }
      return keys.join('<br/>');
    });
  }

  showContextPopover(entry, event) {
    const $source = $(event.currentTarget || event.target);
    const offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: entry.catalogEntry()
      },
      orientation: 'right',
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 2
      }
    });
  }

  saveComment() {
    const self = this;
    if (self.comment() !== self.catalogEntry().getResolvedComment()) {
      self
        .catalogEntry()
        .setComment(self.comment())
        .done(self.comment)
        .fail(() => {
          self.comment(self.catalogEntry().getResolvedComment());
        });
    }
  }
}

class CatalogEntriesList {
  constructor(params) {
    const self = this;
    self.catalogEntry = ko.isObservable(params.catalogEntry)
      ? params.catalogEntry
      : ko.observable(params.catalogEntry);
    self.selectedEntries = params.selectedEntries;
    self.entries = ko.observableArray();
    self.editableDescriptions = !!params.editableDescriptions;
    self.contextPopoverEnabled = !!params.contextPopoverEnabled;
    self.onSampleClick = params.onSampleClick;
    self.querySpec = ko.observable();
    self.cancellablePromises = [];
    self.lastSamplePromise = undefined;
    self.fetchSampleTimeout = -1;
    self.loading = ko.observable(false);
    self.loadingNav = ko.observable(false);
    self.loadingSamples = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.refreshSampleInterval = params.refreshSampleInterval;
    self.sampleRefreshEnabled = ko.observable(!!params.refreshSampleInterval);

    self.sampleRefreshEnabled.subscribe(newVal => {
      if (!newVal) {
        window.clearTimeout(self.fetchSampleTimeout);
        if (self.lastSamplePromise && self.lastSamplePromise.cancel) {
          self.lastSamplePromise.cancel();
        }
      }
    });

    // TODO: Can be computed based on contents (instead of always suggesting all col types etc.)
    self.knownFacetValues = ko.pureComputed(() => {
      if (self.catalogEntry().isDatabase()) {
        return { type: { table: -1, view: -1 } };
      } else if (self.catalogEntry().isTableOrView()) {
        const typeIndex = { type: {} };

        // Issue with filteredEntries is that it's not updated in time when typing,
        // i.e. type:| doesn't automatically open the suggestion list.
        self.entries().forEach(entry => {
          const type = entry
            .catalogEntry()
            .getType()
            .toLowerCase();
          if (!typeIndex['type'][type]) {
            typeIndex['type'][type] = 1;
          } else {
            typeIndex['type'][type]++;
          }
        });
        return typeIndex;
      }
    });

    self.facets = self.catalogEntry().isField() && !self.catalogEntry().isComplex() ? [] : ['type'];

    self.filteredEntries = ko.pureComputed(() => {
      if (!self.querySpec() || self.querySpec().query === '') {
        return self.entries();
      }

      const facets = self.querySpec().facets;
      const isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
      const isTextMatch = !self.querySpec().text || self.querySpec().text.length === 0;

      return self.entries().filter(entry => {
        let match = true;

        if (!isFacetMatch) {
          if (entry.catalogEntry().isField()) {
            match = !!facets['type'][
              entry
                .catalogEntry()
                .getType()
                .toLowerCase()
            ];
          } else if (entry.catalogEntry().isTableOrView()) {
            match =
              (facets['type']['table'] && entry.catalogEntry().isTable()) ||
              (facets['type']['view'] && entry.catalogEntry().isView());
          }
        }

        if (match && !isTextMatch) {
          match = self.querySpec().text.every(text => {
            const textLower = text.toLowerCase();
            return (
              entry
                .catalogEntry()
                .name.toLowerCase()
                .indexOf(textLower) !== -1 ||
              entry
                .catalogEntry()
                .getResolvedComment()
                .toLowerCase()
                .indexOf(textLower) !== -1
            );
          });
        }

        return match;
      });
    });

    self.autocompleteFromEntries = function(nonPartial, partial) {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.entries().forEach(entry => {
        if (
          entry
            .catalogEntry()
            .name.toLowerCase()
            .indexOf(partialLower) === 0
        ) {
          result.push(nonPartial + partial + entry.catalogEntry().name.substring(partial.length));
        }
      });
      return result;
    };

    const entrySort = function(a, b) {
      const aIsKey = a.catalogEntry().isPrimaryKey() || a.catalogEntry().isPartitionKey();
      const bIsKey = b.catalogEntry().isPrimaryKey() || b.catalogEntry().isPartitionKey();
      if (aIsKey && !bIsKey) {
        return -1;
      }
      if (bIsKey && !aIsKey) {
        return 1;
      }

      return b.popularity() - a.popularity() || a.index - b.index;
    };

    const onClick = function(sampleEnrichedEntry, event) {
      if (params.onClick) {
        params.onClick(sampleEnrichedEntry.catalogEntry(), event);
      } else if (self.contextPopoverEnabled) {
        sampleEnrichedEntry.showContextPopover(sampleEnrichedEntry, event);
      } else {
        self.catalogEntry(sampleEnrichedEntry.catalogEntry());
      }
    };

    const onRowClick = function(sampleEnrichedEntry, event) {
      if (self.selectedEntries && $(event.target).is('td')) {
        $(event.currentTarget)
          .find('.hue-checkbox')
          .trigger('click');
      }
      return true;
    };

    const loadEntries = function() {
      self.loading(true);

      const entriesAddedDeferred = $.Deferred();

      const childPromise = self
        .catalogEntry()
        .getChildren({ silenceErrors: true, cancellable: true })
        .done(childEntries => {
          const entries = $.map(childEntries, (entry, index) => {
            return new SampleEnrichedEntry(index, entry, onClick, onRowClick);
          });
          entries.sort(entrySort);
          self.entries(entries);
          entriesAddedDeferred.resolve(entries);
        })
        .fail(() => {
          self.hasErrors(true);
          entriesAddedDeferred.reject();
        })
        .always(() => {
          self.loading(false);
        });

      if (self.catalogEntry().isTableOrView()) {
        const joinsPromise = self
          .catalogEntry()
          .getTopJoins({ silenceErrors: true, cancellable: true })
          .done(topJoins => {
            if (topJoins && topJoins.values && topJoins.values.length) {
              entriesAddedDeferred.done(entries => {
                const entriesIndex = {};
                entries.forEach(entry => {
                  entriesIndex[
                    entry
                      .catalogEntry()
                      .path.join('.')
                      .toLowerCase()
                  ] = { joinColumnIndex: {}, entry: entry };
                });
                topJoins.values.forEach(topJoin => {
                  topJoin.joinCols.forEach(topJoinCols => {
                    if (topJoinCols.columns.length === 2) {
                      if (entriesIndex[topJoinCols.columns[0].toLowerCase()]) {
                        entriesIndex[topJoinCols.columns[0].toLowerCase()].joinColumnIndex[
                          topJoinCols.columns[1].toLowerCase()
                        ] = topJoinCols.columns[1];
                      } else if (entriesIndex[topJoinCols.columns[1].toLowerCase()]) {
                        entriesIndex[topJoinCols.columns[1].toLowerCase()].joinColumnIndex[
                          topJoinCols.columns[0].toLowerCase()
                        ] = topJoinCols.columns[0];
                      }
                    }
                  });
                });
                Object.keys(entriesIndex).forEach(key => {
                  if (Object.keys(entriesIndex[key].joinColumnIndex).length) {
                    entriesIndex[key].entry.joinColumns(
                      Object.keys(entriesIndex[key].joinColumnIndex)
                    );
                  }
                });
              });
            }
          });
        self.cancellablePromises.push(joinsPromise);
      }

      const navMetaPromise = self
        .catalogEntry()
        .loadNavigatorMetaForChildren({ silenceErrors: true, cancellable: true })
        .always(() => {
          self.loadingNav(false);
        });

      self.cancellablePromises.push(navMetaPromise);
      self.cancellablePromises.push(childPromise);

      self.cancellablePromises.push(
        self
          .catalogEntry()
          .loadNavOptPopularityForChildren({ silenceErrors: true, cancellable: true })
          .done(popularEntries => {
            if (popularEntries.length) {
              childPromise.done(() => {
                const entryIndex = {};
                self.entries().forEach(entry => {
                  entryIndex[entry.catalogEntry().name] = entry;
                });

                let totalCount = 0;
                const popularityToApply = [];
                popularEntries.forEach(popularEntry => {
                  if (
                    entryIndex[popularEntry.name] &&
                    popularEntry.navOptPopularity &&
                    popularEntry.navOptPopularity.selectColumn &&
                    popularEntry.navOptPopularity.selectColumn.columnCount > 0
                  ) {
                    totalCount += popularEntry.navOptPopularity.selectColumn.columnCount;
                    popularityToApply.push(() => {
                      entryIndex[popularEntry.name].popularity(
                        Math.round(
                          (100 * popularEntry.navOptPopularity.selectColumn.columnCount) /
                            totalCount
                        )
                      );
                    });
                  }
                });
                const foundPopularEntries = popularityToApply.length !== 0;
                while (popularityToApply.length) {
                  popularityToApply.pop()();
                }
                if (foundPopularEntries) {
                  self.entries().sort(entrySort);
                }
              });
            }
          })
      );

      if (self.catalogEntry().isTableOrView() || self.catalogEntry().isComplex()) {
        self.loadingSamples(true);

        let firstSampleFetch = true;

        const fetchSamples = function() {
          window.clearInterval(self.fetchSampleTimeout);
          self.lastSamplePromise = self
            .catalogEntry()
            .getSample({
              silenceErrors: true,
              cancellable: true,
              refreshCache: !firstSampleFetch
            })
            .done(sample => {
              childPromise
                .done(() => {
                  if (sample.meta && sample.meta.length && sample.data && sample.data.length) {
                    const entryIndex = {};
                    self.entries().forEach(entry => {
                      entryIndex[entry.catalogEntry().name] = entry;
                    });
                    for (let i = 0; i < sample.meta.length; i++) {
                      let name = sample.meta[i].name;
                      if (
                        name.toLowerCase().indexOf(self.catalogEntry().name.toLowerCase() + '.') ===
                        0
                      ) {
                        name = name.substring(self.catalogEntry().name.length + 1);
                      }
                      const sampleEntry = entryIndex[name];
                      if (sampleEntry) {
                        sampleEntry.firstSample(sample.data[0][i]);
                        if (sample.data.length > 1) {
                          sampleEntry.secondSample(sample.data[1][i]);
                        }
                      }
                    }
                  }
                })
                .always(() => {
                  self.loadingSamples(false);
                  firstSampleFetch = false;
                  if (self.refreshSampleInterval && self.sampleRefreshEnabled()) {
                    self.fetchSampleTimeout = window.setTimeout(
                      fetchSamples,
                      self.refreshSampleInterval
                    );
                  }
                });
            })
            .fail(() => {
              self.loadingSamples(false);
            });
        };

        fetchSamples();
      }
    };

    window.setTimeout(loadEntries, 100);
  }

  dispose() {
    const self = this;
    window.clearTimeout(self.fetchSampleTimeout);
    if (self.lastSamplePromise && self.lastSamplePromise.cancel) {
      self.lastSamplePromise.cancel();
    }
    while (self.cancellablePromises.length) {
      const promise = self.cancellablePromises.pop();
      if (promise.cancel) {
        promise.cancel();
      }
    }
  }
}

componentUtils.registerComponent('catalog-entries-list', CatalogEntriesList, TEMPLATE);
