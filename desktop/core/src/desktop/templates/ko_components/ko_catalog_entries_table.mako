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

  <script type="text/html" id="entries-table-td-description">
    <td data-bind="attr: { 'title': comment }">
    <!-- ko if: $parent.editableDescriptions -->
      <div class="hue-catalog-entries-table-desc" data-bind="visibleOnHover: { selector: '.editable-inline-action' }">
        <div data-bind="editable: comment, editableOptions: {
          mode: 'inline',
          enabled: true,
          type: 'textarea',
          showbuttons: 'bottom',
          inputclass: 'hue-table-browser-desc-input',
          toggle: 'manual',
          toggleElement: '.toggle-editable',
          placeholder: '${ _ko('Add a description...') }',
          emptytext: '${ _ko('Add a description...') }',
          inputclass: 'hue-catalog-entries-table-desc-input',
          rows: 6,
          save: saveComment,
          inlineEditAction: { editClass: 'toggle-editable editable-inline-action' },
          multiLineEllipsis: { overflowHeight: '40px', expandable: true, expandActionClass: 'editable-inline-action' }
        }">${ _('Add a description...') }</div>
      </div>
    <!-- /ko -->
    <!-- ko ifnot: $parent.editableDescriptions -->
      <div class="entries-table-description" data-bind="text: comment, multiLineEllipsis"></div>
    <!-- /ko -->
    </td>
  </script>

  <script type="text/html" id="entries-table-tbody-no-entries">
    <tbody>
      <tr>
        <td style="font-style: italic;" data-bind="attr: { 'colspan': colCount + (typeof $component.selectedEntries !== 'undefined' ? 1 : 0) + ($component.contextPopoverEnabled ? 1 : 0) }">
          <!-- ko ifnot: hasErrors -->
          ${ _("No entries found") }
          <!-- /ko -->
          <!-- ko if: hasErrors -->
          ${ _("Error loading entries") }
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

  <script type="text/html" id="catalog-entries-list-template">
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
            <th>${ _("Database") }</th>
            <th>${ _("Description") } <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
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
          <th data-bind="text: catalogEntry().getSourceType() !== 'solr' ? '${ _ko("Table") }' : '${ _ko("Collection") }'"></th>
          <th>${ _("Description") } <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
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
          <th><span data-bind="text: catalogEntry().getSourceType() !== 'solr' ? '${ _ko("Column") }' : '${ _ko("Field") }'"></span> (<span data-bind="text: filteredEntries().length"></span>)</th>
          <th>${ _("Type") }</th>
          <th>${ _("Description") } <!-- ko if: loadingNav --><i class="fa fa-spinner fa-spin"></i><!-- /ko --></th>
          <th colspan="2">${ _("Sample") } <!-- ko if: loadingSamples() || sampleRefreshEnabled() --><i class="fa fa-spinner fa-spin"></i><!-- /ko --> <!-- ko if: sampleRefreshEnabled --><a class="inactive-action" href="javascript: void(0);" data-bind="toggle: sampleRefreshEnabled"><i class="fa fa-stop"></i></a><!-- /ko --></th>
        </tr>
        </thead>
        <!-- ko if: filteredEntries().length -->
        <tbody data-bind="foreach: filteredEntries">
        <tr data-bind="click: onRowClick">
          <!-- ko template: 'entries-table-shared-columns' --><!-- /ko -->
          <td class="name-column" data-bind="attr: { 'title': catalogEntry().name + ' - ${ _ko("Click for more details") }' }">
            <a href="javascript: void(0);" data-bind="click: onClick">
              <span data-bind="text: catalogEntry().name"></span>
              <!-- ko if: isKey -->
              &nbsp;<i class="fa fa-key" data-bind="tooltip: { title: keyText, html: true }"></i>
              <!-- /ko -->
              <!-- ko if: popularity && popularity() >= 5 -->
              &nbsp;<i data-bind="tooltip: { title: '${ _ko("Popularity") }: ' + popularity() + '%' }" class="fa fa-star-o"></i>
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
  </script>

  <script type="text/javascript">
    (function () {

      function SampleEnrichedEntry(index, catalogEntry, onClick, onRowClick) {
        var self = this;
        self.index = index;
        self.catalogEntry = ko.isObservable(catalogEntry) ? catalogEntry : ko.observable(catalogEntry);
        self.popularity = ko.observable(0);
        self.firstSample = ko.observable();
        self.secondSample = ko.observable();
        self.onClick = onClick;
        self.onRowClick = onRowClick;
        self.comment = self.catalogEntry().getCommentObservable();
        self.joinColumns = ko.observableArray();

        self.isKey = ko.pureComputed(function () {
          return self.catalogEntry().isPrimaryKey() || self.catalogEntry().isPartitionKey() || self.joinColumns().length;
        });

        self.keyText = ko.pureComputed(function () {
          var keys = [];
          if (self.catalogEntry().isPrimaryKey()) {
            keys.push('${ _("Primary key") }')
          }
          if (self.catalogEntry().isPartitionKey()) {
            keys.push('${ _("Partition key") }')
          }
          if (self.joinColumns().length) {
            var key = self.joinColumns().length > 1 ? '${ _("Foreign keys") }:' : '${ _("Foreign key") }:';
            self.joinColumns().forEach(function (joinCol) {
              key += '<br/>' + joinCol;
            });
            keys.push(key);
          }
          return keys.join('<br/>');
        })
      }

      SampleEnrichedEntry.prototype.showContextPopover = function (entry, event) {
        var $source = $(event.currentTarget || event.target);
        var offset = $source.offset();
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
      };

      SampleEnrichedEntry.prototype.saveComment = function () {
        var self = this;
        if (self.comment() !== self.catalogEntry().getResolvedComment()) {
          self.catalogEntry().setComment(self.comment()).done(self.comment).fail(function () {
            self.comment(self.catalogEntry().getResolvedComment());
          })
        }
      };

      function CatalogEntriesList(params) {
        var self = this;
        self.catalogEntry = ko.isObservable(params.catalogEntry) ? params.catalogEntry : ko.observable(params.catalogEntry);
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

        self.sampleRefreshEnabled.subscribe(function (newVal) {
          if (!newVal) {
            window.clearTimeout(self.fetchSampleTimeout);
            if (self.lastSamplePromise && self.lastSamplePromise.cancel) {
              self.lastSamplePromise.cancel();
            }
          }
        });

        // TODO: Can be computed based on contents (instead of always suggesting all col types etc.)
        self.knownFacetValues = ko.pureComputed(function () {
          if (self.catalogEntry().isDatabase()) {
            return { 'type': { 'table': -1, 'view': -1 } };
          } else if (self.catalogEntry().isTableOrView()) {
            var typeIndex = { 'type': {} };

            // Issue with filteredEntries is that it's not updated in time when typing,
            // i.e. type:| doesn't automatically open the suggestion list.
            self.entries().forEach(function (entry) {
              var type = entry.catalogEntry().getType().toLowerCase();
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
              if (entry.catalogEntry().isField()) {
                match = !!facets['type'][entry.catalogEntry().getType().toLowerCase()];
              } else if (entry.catalogEntry().isTableOrView()) {
                match = (facets['type']['table'] && entry.catalogEntry().isTable()) || (facets['type']['view'] && entry.catalogEntry().isView()) ;
              }
            }

            if (match && !isTextMatch) {
              match = self.querySpec().text.every(function (text) {
                var textLower = text.toLowerCase();
                return entry.catalogEntry().name.toLowerCase().indexOf(textLower) !== -1
                  || entry.catalogEntry().getResolvedComment().toLowerCase().indexOf(textLower) !== -1;
              });
            }

            return match;
          });
        });

        self.autocompleteFromEntries = function (nonPartial, partial) {
          var result = [];
          var partialLower = partial.toLowerCase();
          self.entries().forEach(function (entry) {
            if (entry.catalogEntry().name.toLowerCase().indexOf(partialLower) === 0) {
              result.push(nonPartial + partial + entry.catalogEntry().name.substring(partial.length))
            }
          });
          return result;
        };

        var entrySort = function (a, b) {
          var aIsKey = a.catalogEntry().isPrimaryKey() || a.catalogEntry().isPartitionKey();
          var bIsKey = b.catalogEntry().isPrimaryKey() || b.catalogEntry().isPartitionKey();
          if (aIsKey && !bIsKey) {
            return -1;
          }
          if (bIsKey && !aIsKey) {
            return 1;
          }

          return (b.popularity() - a.popularity()) || (a.index - b.index);
        };

        var onClick = function (sampleEnrichedEntry, event) {
          if (params.onClick) {
            params.onClick(sampleEnrichedEntry.catalogEntry(), event);
          } else if (self.contextPopoverEnabled) {
            sampleEnrichedEntry.showContextPopover(sampleEnrichedEntry, event);
          } else {
            self.catalogEntry(sampleEnrichedEntry.catalogEntry());
          }
        };

        var onRowClick = function (sampleEnrichedEntry, event) {
          if (self.selectedEntries && $(event.target).is('td')) {
           $(event.currentTarget).find('.hue-checkbox').trigger('click');
          }
          return true;
        };

        var loadEntries = function () {
          self.loading(true);

          var entriesAddedDeferred = $.Deferred();

          var childPromise = self.catalogEntry().getChildren({ silenceErrors: true, cancellable: true }).done(function (childEntries) {
            var entries = $.map(childEntries, function (entry, index) { return new SampleEnrichedEntry(index, entry, onClick, onRowClick) });
            entries.sort(entrySort);
            self.entries(entries);
            entriesAddedDeferred.resolve(entries);
          }).fail(function () {
            self.hasErrors(true);
            entriesAddedDeferred.reject();
          }).always(function () {
            self.loading(false);
          });

          if (self.catalogEntry().isTableOrView()) {
            var joinsPromise = self.catalogEntry().getTopJoins({ silenceErrors: true, cancellable: true }).done(function (topJoins) {
              if (topJoins && topJoins.values && topJoins.values.length) {
                entriesAddedDeferred.done(function (entries) {
                  var entriesIndex = {};
                  entries.forEach(function (entry) {
                    entriesIndex[entry.catalogEntry().path.join('.').toLowerCase()] = { joinColumnIndex: {}, entry: entry };
                  });
                  topJoins.values.forEach(function (topJoin) {
                    topJoin.joinCols.forEach(function (topJoinCols) {
                      if (topJoinCols.columns.length === 2) {
                        if (entriesIndex[topJoinCols.columns[0].toLowerCase()]) {
                          entriesIndex[topJoinCols.columns[0].toLowerCase()].joinColumnIndex[topJoinCols.columns[1].toLowerCase()] = topJoinCols.columns[1]
                        } else if (entriesIndex[topJoinCols.columns[1].toLowerCase()]) {
                          entriesIndex[topJoinCols.columns[1].toLowerCase()].joinColumnIndex[topJoinCols.columns[0].toLowerCase()] = topJoinCols.columns[0]
                        }
                      }
                    })
                  });
                  Object.keys(entriesIndex).forEach(function (key) {
                    if (Object.keys(entriesIndex[key].joinColumnIndex).length) {
                      entriesIndex[key].entry.joinColumns(Object.keys(entriesIndex[key].joinColumnIndex));
                    }
                  })
                })
              }
            });
            self.cancellablePromises.push(joinsPromise);
          }

          var navMetaPromise = self.catalogEntry().loadNavigatorMetaForChildren({ silenceErrors: true, cancellable: true }).always(function () {
            self.loadingNav(false);
          });

          self.cancellablePromises.push(navMetaPromise);
          self.cancellablePromises.push(childPromise);

          self.cancellablePromises.push(self.catalogEntry().loadNavOptPopularityForChildren({ silenceErrors: true, cancellable: true }).done(function (popularEntries) {
            if (popularEntries.length) {
              childPromise.done(function () {
                var entryIndex = {};
                self.entries().forEach(function (entry) {
                  entryIndex[entry.catalogEntry().name] = entry;
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
                var foundPopularEntries = popularityToApply.length !== 0;
                while (popularityToApply.length) {
                  popularityToApply.pop()();
                }
                if (foundPopularEntries) {
                  self.entries().sort(entrySort);
                }
              });
            }
          }));

          if (self.catalogEntry().isTableOrView() || self.catalogEntry().isComplex()) {
            self.loadingSamples(true);

            var firstSampleFetch = true;

            var fetchSamples = function () {
              window.clearInterval(self.fetchSampleTimeout);
              self.lastSamplePromise = self.catalogEntry().getSample({
                silenceErrors: true,
                cancellable: true,
                refreshCache: !firstSampleFetch
              }).done(function (sample) {
                childPromise.done(function () {
                  if (sample.meta && sample.meta.length && sample.data && sample.data.length) {
                    var entryIndex = {};
                    self.entries().forEach(function (entry) {
                      entryIndex[entry.catalogEntry().name] = entry;
                    });
                    for (var i = 0; i < sample.meta.length; i++) {
                      var name = sample.meta[i].name;
                      if (name.toLowerCase().indexOf(self.catalogEntry().name.toLowerCase() + '.') === 0) {
                        name = name.substring(self.catalogEntry().name.length + 1);
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
                  firstSampleFetch = false;
                  if (self.refreshSampleInterval && self.sampleRefreshEnabled()) {
                    self.fetchSampleTimeout = window.setTimeout(fetchSamples, self.refreshSampleInterval);
                  }
                })
              }).fail(function () {
                self.loadingSamples(false);
              });
            };

            fetchSamples();
          }
        };

        window.setTimeout(loadEntries, 100)
      }

      CatalogEntriesList.prototype.dispose = function () {
        var self = this;
        window.clearTimeout(self.fetchSampleTimeout);
        if (self.lastSamplePromise && self.lastSamplePromise.cancel) {
          self.lastSamplePromise.cancel();
        }
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

  <script type="text/html" id="polling-catalog-entries-list-template">
    <div>
    <!-- ko hueSpinner: { spin: !catalogEntryExists(), inline: true } --><!-- /ko -->
    <!-- ko if: catalogEntryExists -->
      <!-- ko component: { name: 'catalog-entries-list', params: {
        catalogEntry: catalogEntry,
        selectedEntries: selectedEntries,
        editableDescriptions: editableDescriptions,
        contextPopoverEnabled: contextPopoverEnabled,
        onSampleClick: onSampleClick,
        refreshSampleInterval: refreshSampleInterval
      }} --><!-- /ko -->
    <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      /**
       * This is the same as the 'catalog-entries-list' component with the difference that this
       * one waits until a catalog entry exists.
       *
       * Example usage:
       *
       * <div data-bind="component: { name: 'polling-catalog-entries-list', params: {
       *   sourceType: sourceType,
       *   namespace: ko.observable({ id: 'default' }),
       *   compute: ko.observable({ id: 'default' }),
       *   path: ko.observable('default.foo'),
       *   refreshSampleInterval: 3000
       * }}" />
       *
       * @param params
       * @constructor
       */

      function PollingCatalogEntriesList(params) {
        var self = this;
        self.selectedEntries = params.selectedEntries;
        self.editableDescriptions = params.editableDescriptions;
        self.contextPopoverEnabled = params.contextPopoverEnabled;
        self.onSampleClick = params.onSampleClick;
        self.sourceType = params.sourceType;
        self.namespace = params.namespace;
        self.compute = params.compute;
        self.path = params.path;
        self.refreshSampleInterval = params.refreshSampleInterval;

        self.pollTimeout = -1;
        self.pollCount = 0;

        self.disposals = [];

        self.lastPollSourceMetaPromise = undefined;

        self.catalogEntryExists = ko.observable(false);
        self.catalogEntry = ko.observable();

        self.intialize();

        if (ko.isObservable(self.path)) {
          var pathSub = self.path.subscribe(function (newValue) {
            if (newValue) {
              self.intialize();
            }
          });
          self.disposals.push(function () {
            pathSub.dispose();
          });
        }
      }

      PollingCatalogEntriesList.prototype.pollForSourceMeta = function () {
        var self = this;
        window.clearTimeout(self.pollTimeout);

        var pollInternal = function () {
          self.pollCount++;
          if (self.catalogEntry()) {
            self.lastPollSourceMetaPromise = self.catalogEntry().getSourceMeta({
              silenceErrors: true,
              refreshCache: self.pollCount > 0,
              cancellable: true
            }).done(function (sourceMeta) {
              if (sourceMeta.notFound) {
                self.pollForSourceMeta();
              } else {
                self.catalogEntryExists(true);
              }
            }).fail(function () {
              self.pollForSourceMeta();
            })
          }
        };

        if (self.pollCount === 0) {
          pollInternal();
        } else {
          self.pollTimeout = window.setTimeout(pollInternal, Math.min(1000 * self.pollCount, 3000));
        }

      };

      PollingCatalogEntriesList.prototype.intialize = function () {
        var self = this;
        self.pollCount = 0;
        window.clearTimeout(self.pollTimeout);
        self.catalogEntryExists(false);

        if (self.lastPollSourceMetaPromise && self.lastPollSourceMetaPromise.cancel) {
          self.lastPollSourceMetaPromise.cancel();
        }

        DataCatalog.getEntry({
          sourceType: ko.unwrap(self.sourceType),
          namespace: ko.unwrap(self.namespace),
          compute: ko.unwrap(self.compute),
          path: ko.unwrap(self.path)
        }).done(function (catalogEntry) {
          self.catalogEntry(catalogEntry);
          self.pollForSourceMeta();
        })
      };

      PollingCatalogEntriesList.prototype.dispose = function () {
        var self = this;
        window.clearTimeout(self.pollTimeout);
        if (self.lastPollSourceMetaPromise && self.lastPollSourceMetaPromise.cancel) {
          self.lastPollSourceMetaPromise.cancel();
        }
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      ko.components.register('polling-catalog-entries-list', {
        viewModel: PollingCatalogEntriesList,
        template: { element: 'polling-catalog-entries-list-template' }
      });
    })();
  </script>

  <script type="text/html" id="field-samples-template">
    <div class="context-popover-inline-autocomplete" style="display: flex">
      <div class="context-popover-sample-filter">
        <!-- ko component: {
          name: 'inline-autocomplete',
          params: {
            querySpec: querySpec,
            autocompleteFromEntries: autocompleteFromEntries
          }
        } --><!-- /ko -->
      </div>
      <!-- ko if: showOperations -->
      <div class="context-popover-sample-controls">
        <div class="margin-left-10 inline-block" data-bind="component: { name: 'hue-drop-down', params: { value: operation, entries: operations } }"></div>
        <div class="margin-left-10 inactive-action inline-block">
          <!-- ko if: loadingSamples() || refreshSampleEnabled() -->
          <a href="javascript:void(0);" data-bind="click: function () { refreshSampleEnabled(false); cancelRunningQueries() }"><i class="fa fa-stop"></i></a>
          <!-- /ko -->
          <!-- ko if: !loadingSamples() && !refreshSampleEnabled() -->
          <a href="javascript:void(0);" data-bind="click: function () { loadSamples(true) }"><i class="fa fa-play"></i></a>
          <!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
    </div>

    <table class="table table-condensed table-nowrap">
      <thead>
      <tr>
        <th>${ _("Sample") }</th>
      </tr>
      </thead>
      <!-- ko if: loadingSamples() && (!refreshSampleEnabled() || (refreshSampleEnabled() && columnSamples().length === 0))  -->
      <tbody>
      <tr>
        <td><!-- ko hueSpinner: { spin: true, inline: true } --><!-- /ko --></td>
      </tr>
      </tbody>
      <!-- /ko -->

      <!-- ko if: !loadingSamples() || (refreshSampleEnabled() && columnSamples().length > 0)  -->
      <tbody data-bind="foreach: filteredColumnSamples">
      <tr>
        <!-- ko if: typeof $parent.onSampleClick === 'function' -->
        <td class="sample-column pointer" data-bind="html: $data, attr: { 'title': hueUtils.html2text($data) }, click: $parent.sampleClick"></td>
        <!-- /ko -->
        <!-- ko ifnot: typeof $parent.onSampleClick === 'function' -->
        <td class="sample-column" data-bind="html: $data, attr: { 'title': hueUtils.html2text($data) }"></td>
        <!-- /ko -->
      </tr>
      </tbody>
      <!-- ko if: filteredColumnSamples().length === 0 -->
      <tbody>
      <tr>
        <!-- ko ifnot: hasErrors -->
        <td style="font-style: italic;">${ _("No entries found") }</td>
        <!-- /ko -->
        <!-- ko if: hasErrors -->
        <td style="font-style: italic;">${ _("Error loading samples") }</td>
        <!-- /ko -->
      </tr>
      </tbody>
      <!-- /ko -->
      <!-- /ko -->
    </table>
  </script>

  <script type="text/javascript">
    (function () {
      function FieldSamples (params) {
        var self = this;
        self.catalogEntry = ko.isObservable(params.catalogEntry) ? params.catalogEntry : ko.observable(params.catalogEntry);
        self.onSampleClick = params.onSampleClick;
        self.refreshSampleInterval = params.refreshSampleInterval;
        self.refreshSampleTimeout = -1;
        self.refreshSampleEnabled = ko.observable(!!self.refreshSampleInterval);

        self.cancellablePromises = [];
        self.querySpec = ko.observable();

        self.hasErrors = ko.observable();
        self.loadingSamples = ko.observable();

        self.showOperations = self.catalogEntry().getSourceType() === 'impala' || self.catalogEntry().getSourceType() === 'hive';

        self.sampleClick = function (html) {
          self.onSampleClick(hueUtils.html2text(html));
          huePubSub.publish('context.popover.hide');
        };

        self.operations = [
          {
            label: '${ _("default") }',
            type: 'default'
          },{
            label: '${ _("distinct") }',
            type: 'distinct'
          },{
            label: '${ _("max") }',
            type: 'max'
          },{
            label: '${ _("min") }',
            type: 'min'
          }
        ];

        self.operation = ko.observable(self.operations[0]);

        self.operation.subscribe(function () {
          self.loadSamples();
        });

        self.columnSamples = ko.observableArray();

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

        self.autocompleteFromEntries = function (nonPartial, partial) {
          var result = [];
          var partialLower = partial.toLowerCase();
          self.columnSamples().forEach(function (sample) {
            if (sample[0].toString().toLowerCase().indexOf(partialLower) === 0) {
              result.push(nonPartial + partial + sample[0].toString().substring(partial.length))
            }
          });
          return result;
        };

        self.loadSamples();
      }

      FieldSamples.prototype.loadSamples = function (refreshCache) {
        var self = this;
        window.clearTimeout(self.refreshSampleTimeout);
        self.cancelRunningQueries();
        self.loadingSamples(true);
        self.cancellablePromises.push(self.catalogEntry().getSample({ silenceErrors: true, cancellable: true, refreshCache: refreshCache, operation: self.operation().type }).done(function (samples) {
          if (samples.data && samples.data.length) {
            self.columnSamples(samples.data);
          }
        }).fail(function () {
          self.hasErrors(true);
        }).always(function () {
          self.loadingSamples(false);
          if (self.refreshSampleTimeout && self.refreshSampleEnabled()) {
            self.refreshSampleTimeout = window.setTimeout(function () {
              self.loadSamples(true);
            }, self.refreshSampleInterval);
          }
        }));
      };

      FieldSamples.prototype.cancelRunningQueries = function () {
        var self = this;
        window.clearTimeout(self.refreshSampleTimeout);
        while (self.cancellablePromises.length) {
          var promise = self.cancellablePromises.pop();
          if (promise.cancel) {
            promise.cancel();
          }
        }
      };

      FieldSamples.prototype.dispose = function () {
        var self = this;
        self.cancelRunningQueries();
      };

      ko.components.register('field-samples', {
        viewModel: FieldSamples,
        template: { element: 'field-samples-template' }
      })
    })();
  </script>
</%def>
