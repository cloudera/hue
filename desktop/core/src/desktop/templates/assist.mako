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

from dashboard.conf import HAS_SQL_ENABLED
from filebrowser.conf import SHOW_UPLOAD_BUTTON
from metadata.conf import OPTIMIZER
from metastore.conf import ENABLE_NEW_CREATE_TABLE
from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING

from desktop import appmanager
from desktop import conf
from desktop.conf import IS_EMBEDDED, USE_NEW_SIDE_PANELS, VCS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>



<%def name="assistPanel(is_s3_enabled=False)">


  <script type="text/html" id="editor-assistant-panel-template">
    <div class="assist-inner-panel assist-assistant-panel">
      <div class="assist-flex-panel">

        <div class="assist-flex-header">
          <div class="assist-inner-header">
            <!-- ko if: isSolr -->
            ${ _('Indexes') }
            <!-- /ko -->
            <!-- ko ifnot: isSolr -->
            ${ _('Tables') }
            <!-- ko if: statementCount() > 1 -->
            <div class="statement-count">${ _('Statement') } <span data-bind="text: activeStatementIndex() + '/' + statementCount()"></span></div>
            <!-- /ko -->
            <!-- /ko -->
          </div>
        </div>
        <div class="assist-flex-search" data-bind="visible: activeTables().length > 0">
          <div class="assist-filter">
            <!-- ko component: {
              name: 'inline-autocomplete',
              params: {
                querySpec: filter.querySpec,
                facets: ['type'],
                knownFacetValues: isSolr() ? SOLR_ASSIST_KNOWN_FACET_VALUES : SQL_ASSIST_KNOWN_FACET_VALUES,
                autocompleteFromEntries: $component.autocompleteFromEntries
              }
            } --><!-- /ko -->
          </div>
        </div>
        <div class="assist-flex-fill assist-db-scrollable" data-bind="delayedOverflow">
          <!-- ko if: filteredTables().length === 0 && (!filter.querySpec() || filter.querySpec().query === '') -->
          <div class="assist-no-entries">
            <!-- ko if: isSolr -->
            ${ _('No indexes selected.') }
            <!-- /ko -->
            <!-- ko ifnot: isSolr  -->
            ${ _('No tables identified.') }
            <!-- /ko -->
          </div>
          <!-- /ko -->
          <!-- ko if: filteredTables().length === 0 && filter.querySpec() && filter.querySpec().query !== '' && !someLoading() -->
          <div class="assist-no-entries">${ _('No entries found.') }</div>
          <!-- /ko -->
          <!-- ko if: filteredTables().length > 0 -->
          <ul class="database-tree assist-tables" data-bind="foreachVisible: { data: filteredTables, minHeight: 22, container: '.assist-db-scrollable', skipScrollEvent: true }">
            <!-- ko if: hasErrors -->
            <li class="assist-table hue-warning" data-bind="attr: { 'title': $parent.isSolr() ? '${ _ko('Error loading index details.') }' : '${ _ko('Error loading table details.') }'}">
              <span class="assist-entry">
                <i class="hue-warning fa fa-fw muted valign-middle fa-warning"></i>
                <!-- ko with: catalogEntry -->
                <!-- ko if: typeof reload !== 'undefined' -->
                <span data-bind="text: getDisplayName()"></span> <a class="inactive-action" href="javascript: void(0);" data-bind="click: reload"><i class="fa fa-refresh" data-bind="css: { 'fa-spin': reloading }"></i></a>
                <!-- /ko -->
                <!-- /ko -->
              </span>
            </li>
            <!-- /ko -->
            <!-- ko ifnot: hasErrors -->
            <!-- ko template: { if: catalogEntry.isTableOrView(), name: 'assist-table-entry' } --><!-- /ko -->
            <!-- ko template: { if: catalogEntry.isField(), name: 'assist-column-entry-assistant' } --><!-- /ko -->
            <!-- /ko -->
          </ul>
          <!-- /ko -->
          <!-- ko hueSpinner: { spin: filter.querySpec() && filter.querySpec().query !== '' && someLoading(), inline: true,  center: true} --><!-- /ko -->
        </div>

        <!-- ko if: showRisks -->
        <div class="assist-flex-header assist-divider"><div class="assist-inner-header">${ _('Query Analysis') }</div></div>
        <div class="assist-flex-third">
          <!-- ko if: ! activeRisks().hints -->
          <div class="assist-no-entries">${ _('Select a query or start typing to get optimization hints.') }</div>
          <!-- /ko -->
          <!-- ko if: activeRisks().hints && activeRisks().hints.length === 0 -->
          <div class="assist-no-entries">${ _('No optimizations identified.') }</div>
          <!-- /ko -->
          <!-- ko if: activeRisks().hints && activeRisks().hints.length > 0 -->
          <ul class="risk-list" data-bind="foreach: activeRisks().hints">
            <li>
              <div class="risk-list-title" data-bind="css: { 'risk-list-high' : risk === 'high', 'risk-list-normal':  risk !== 'high' }, tooltip: { title: risk + ' ' + riskTables }"><span data-bind="text: riskAnalysis"></span></div>
              <div class="risk-list-description" data-bind="text: riskRecommendation"></div>
              <div class="risk-quickfix" data-bind="visible: (riskId === 17 || riskId === 22) && $parent.activeEditor() && $parent.activeLocations()" style="display:none;">
                <a href="javascript:void(0);" data-bind="click: function () { $parent.addFilter(riskId); hueAnalytics.convert('optimizer', 'addFilter/' + riskId); }">${ _('Add filter') }</a>
              </div>
            </li>
          </ul>
          <!-- /ko -->
          <!-- ko if: hasMissingRisks() -->
          <div class="margin-top-20">
            <!-- ko hueSpinner: { spin: uploadingTableStats, inline: true} --><!-- /ko -->
            <!-- ko ifnot: uploadingTableStats -->
            <a href="javascript:void(0)" data-bind="visible: activeTables().length > 0, click: function() { uploadTableStats(true) }, attr: { 'title': ('${ _("Add table ") }'  + (isMissingDDL() ? 'DDL' : '') + (isMissingDDL() && isMissingStats() ? ' ${ _("and") } ' : '') + (isMissingStats() ? 'stats' : '')) }">
              <i class="fa fa-fw fa-plus-circle"></i> ${_('Improve Analysis')}
            </a>
            <!-- /ko -->
          </div>
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    var AssistantUtils = (function () {
      return {
        getFilteredTablesPureComputed: function (vm) {
          var openedByFilter = [];
          return ko.pureComputed(function () {
            if (vm.filter === null || !vm.filter.querySpec() || ((!vm.filter.querySpec().facets || Object.keys(vm.filter.querySpec().facets).length === 0) && (!vm.filter.querySpec().text || vm.filter.querySpec().text.length === 0))) {
              while (openedByFilter.length) {
                openedByFilter.pop().open(false);
              }
              return vm.activeTables();
            }

            var facets = vm.filter.querySpec().facets;

            var result = [];
            $.each(vm.activeTables(), function (index, entry) {
              var facetMatch = !facets || !facets['type'] || (!facets['type']['table'] && !facets['type']['view']);
              if (!facetMatch && facets['type']['table']) {
                facetMatch = entry.catalogEntry.isTable();
              }
              if (!facetMatch && facets['type']['view']) {
                facetMatch = entry.catalogEntry.isView();
              }

              var textMatch = !vm.filter.querySpec().text || vm.filter.querySpec().text.length === 0;
              if (!textMatch) {
                var nameLower = entry.catalogEntry.name.toLowerCase();
                textMatch = vm.filter.querySpec().text.every(function (text) {
                  return nameLower.indexOf(text.toLowerCase()) !== -1;
                });
              }
              entry.filterColumnNames(!textMatch);
              if ((facetMatch && textMatch) || entry.filteredEntries().length > 0) {
                if (!entry.open()) {
                  entry.open(true);
                  openedByFilter.push(entry);
                }
                result.push(entry);
              }
            });
            return result;
          });
        }
      }
    })();

    (function () {
      function EditorAssistantPanel(params) {
        var self = this;

        self.disposals = [];
        self.isSolr = ko.observable(false);
        self.activeTab = params.activeTab;

        self.sourceType = ko.observable(params.sourceType());

        self.showRisks = ko.pureComputed(function () {
          return window.HAS_OPTIMIZER && !self.isSolr() && (self.sourceType() === 'impala' || self.sourceType() === 'hive')
        });

        var typeSub = huePubSub.subscribe('active.snippet.type.changed', function (details) {
          self.sourceType(details.type);
        });

        self.disposals.push(function () {
          typeSub.remove();
        });

        self.uploadingTableStats = ko.observable(false);
        self.activeStatement = ko.observable();
        self.activeTables = ko.observableArray();
        self.activeRisks = ko.observable({});
        self.activeEditor = ko.observable();
        self.activeRisks.subscribe(function() {
          if (self.isMissingDDL()) {
            self.uploadTableStats(false);
          }
        });
        self.activeLocations = ko.observable();
        self.statementCount = ko.observable(0);
        self.activeStatementIndex = ko.observable(0);

        self.hasActiveRisks = ko.pureComputed(function () {
           return self.activeRisks().hints && self.activeRisks().hints.length > 0;
        });

        self.hasMissingRisks = ko.pureComputed(function () {
          return self.isMissingDDL() || self.isMissingStats();
        });

        self.isMissingDDL = ko.pureComputed(function () {
          return self.activeRisks().noDDL && self.activeRisks().noDDL.length > 0
        });

        self.isMissingStats = ko.pureComputed(function () {
          % if OPTIMIZER.AUTO_UPLOAD_STATS.get():
          return self.activeRisks().noStats && self.activeRisks().noStats.length > 0;
          % else:
          return false;
          % endif
        });

        self.someLoading = ko.pureComputed(function () {
          return self.activeTables().some(function (table) {
            return table.loading() || (!table.hasEntries() && !table.hasErrors());
          });
        });

        var createQualifiedIdentifier = function (identifierChain, defaultDatabase) {
          if (identifierChain.length === 1) {
            return defaultDatabase + '.' + identifierChain[0].name;
          }
          return $.map(identifierChain, function (identifier) {
            return identifier.name;
          }).join('.').toLowerCase();
        };

        self.filter = {
          querySpec: ko.observable({
            query: '',
            facets: {},
            text: []
          }).extend({ rateLimit: 300 })
        };

        self.filteredTables = AssistantUtils.getFilteredTablesPureComputed(self);

        var navigationSettings = {
          showStats: true,
          rightAssist: true
        };
        var i18n = {};

        var sources = {};

        var loadEntriesTimeout = -1;
        // This fetches the columns for each table synchronously with 2 second in between.
        var loadEntries = function (currentCount) {
          var count = currentCount || 0;
          count++;
          if (count > 10) {
            return;
          }
          window.clearTimeout(loadEntriesTimeout);
          if (self.activeTables().length === 1) {
            self.activeTables()[0].open(true);
          } else {
            loadEntriesTimeout = window.setTimeout(function () {
              self.activeTables().every(function (table) {
                if (!table.loaded && !table.hasErrors() && !table.loading()) {
                  table.loadEntries(function () {
                    loadEntries(count);
                  });
                  return false;
                }
                return !table.loading();
              })
            }, 2000);
          }
        };

        self.autocompleteFromEntries = function (nonPartial, partial) {
          var added = {};
          var result = [];
          var partialLower = partial.toLowerCase();
          self.filteredTables().forEach(function (table) {
            if (!added[table.catalogEntry.name] && table.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
              added[table.catalogEntry.name] = true;
              result.push(nonPartial + partial + table.catalogEntry.name.substring(partial.length))
            }
            table.entries().forEach(function (col) {
              if (!added[col.catalogEntry.name] && col.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
                added[col.catalogEntry.name] = true;
                result.push(nonPartial + partial + col.catalogEntry.name.substring(partial.length))
              }
            })
          });
          return result;
        };

        var activeTablesSub = self.activeTables.subscribe(loadEntries);
        self.disposals.push(function () {
          window.clearTimeout(loadEntriesTimeout);
          activeTablesSub.dispose();
        });

        var updateOnVisible = false;

        var runningPromises = [];

        var handleLocationUpdate = function (activeLocations) {
          while (runningPromises.length) {
            var promise = runningPromises.pop();
            if (promise.cancel) {
              promise.cancel();
            }
          }
          updateOnVisible = false;

          if (!sources[activeLocations.type]) {
            sources[activeLocations.type] = {
              assistDbSource: new AssistDbSource({
                i18n: i18n,
                initialNamespace: activeLocations.namespace,
                type: activeLocations.type,
                name: activeLocations.type,
                navigationSettings: navigationSettings
              }),
              databaseIndex: {},
              activeTableIndex: {}
            }
          }

          var assistDbSource = sources[activeLocations.type].assistDbSource;
          var databaseIndex = sources[activeLocations.type].databaseIndex;
          var activeTableIndex = sources[activeLocations.type].activeTableIndex;

          if (!activeLocations) {
            self.activeLocations(undefined);
            return;
          }
          self.activeLocations(activeLocations);
          self.statementCount(activeLocations.totalStatementCount);
          self.activeStatementIndex(activeLocations.activeStatementIndex);

          if (activeLocations.activeStatementLocations) {
            var updateTables = false;
            var tableQidIndex = {};
            var ctes = {};
            activeLocations.activeStatementLocations.forEach(function (location) {
              if (location.type === 'alias' && location.source === 'cte') {
                ctes[location.alias.toLowerCase()] = true;
              }
            });

            activeLocations.activeStatementLocations.forEach(function (location) {
              if (location.type === 'table' && (location.identifierChain.length !== 1 || !ctes[location.identifierChain[0].name.toLowerCase()])) {
                var tableDeferred = $.Deferred();
                var dbDeferred = $.Deferred();
                runningPromises.push(tableDeferred);
                runningPromises.push(dbDeferred);

                var qid = createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase);
                if (activeTableIndex[qid]) {
                  tableQidIndex[qid] = true;
                  tableDeferred.resolve(activeTableIndex[qid]);
                  dbDeferred.resolve(activeTableIndex[qid].parent);
                } else {
                  var database = location.identifierChain.length === 2 ? location.identifierChain[0].name : activeLocations.defaultDatabase;
                  database = database.toLowerCase();
                  if (databaseIndex[database]) {
                    dbDeferred.resolve(databaseIndex[database]);
                  } else {
                    dataCatalog.getEntry({
                      sourceType: activeLocations.type,
                      namespace: activeLocations.namespace,
                      compute: activeLocations.compute,
                      path: [ database ],
                      definition: { type: 'database' }
                    }).done(function (catalogEntry) {
                      databaseIndex[database] = new AssistDbEntry(catalogEntry, null, assistDbSource, self.filter, i18n,navigationSettings);
                      updateTables = true;
                      dbDeferred.resolve(databaseIndex[database])
                    }).fail(function () {
                      console.log('reject 1');
                      dbDeferred.reject();
                    });
                  }

                  dbDeferred.done(function (dbEntry) {
                    dbEntry.catalogEntry.getChildren({ silenceErrors: true }).done(function (tableEntries) {
                      var tableName = location.identifierChain[location.identifierChain.length - 1].name;
                      var found = tableEntries.some(function (tableEntry) {
                        if (tableEntry.name === tableName) {
                          var assistTableEntry = new AssistDbEntry(
                            tableEntry,
                            dbEntry,
                            assistDbSource,
                            self.filter,
                            i18n,
                            navigationSettings
                          );
                          activeTableIndex[createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase)] = assistTableEntry;
                          tableQidIndex[qid] = true;
                          updateTables = true;
                          tableDeferred.resolve(assistTableEntry);
                          return true;
                        }
                      });

                      if (!found) {
                        var missingEntry = new AssistDbEntry(
                          {
                            path: [dbEntry.catalogEntry.name, tableName],
                            name: tableName,
                            isTableOrView: function () { return true; },
                            getType: function () { return 'table' },
                            hasPossibleChildren: function () { return true; },
                            getSourceMeta: function () { return $.Deferred().resolve({ notFound: true }).promise() },
                            getDisplayName: function () { return dbEntry.catalogEntry.name + '.' + tableName },
                            reloading: ko.observable(false),
                            reload: function () {
                              var self = this;
                              if (self.reloading()) {
                                return;
                              }
                              self.reloading(true);
                              huePubSub.subscribeOnce('data.catalog.entry.refreshed', function (data) {
                                data.entry.getSourceMeta({ silenceErrors: true }).always(function () {
                                  self.reloading(false)
                                })
                              });
                              dataCatalog.getEntry({ sourceType: activeLocations.type, namespace: activeLocations.namespace, compute: activeLocations.compute, path: [] }).done(function (sourceEntry) {
                                sourceEntry.getChildren().done(function (dbEntries) {
                                  var clearPromise;
                                   // Clear the database first if it exists without cascade
                                  var hasDb = dbEntries.some(function (dbEntry) {
                                    if (dbEntry.name.toLowerCase() === self.path[0].toLowerCase()) {
                                      clearPromise = dbEntry.clearCache({ invalidate: 'invalidate', cascade: false });
                                      return true;
                                    }
                                  });
                                  if (!hasDb) {
                                    // If the database is missing clear the source without cascade
                                    clearPromise = sourceEntry.clearCache({ invalidate: 'invalidate', cascade: false });
                                  }
                                  clearPromise.fail(function () {
                                    self.reloading(false);
                                  });
                                }).fail(function () {
                                  self.reloading(false);
                                })
                              }).fail(function () {
                                self.reloading(false);
                              });
                            }
                          },
                          dbEntry,
                          assistDbSource,
                          self.filter,
                          i18n,
                          navigationSettings
                        );
                        activeTableIndex[createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase)] = missingEntry;
                        tableQidIndex[qid] = true;
                        updateTables = true;
                        missingEntry.hasErrors(true);
                        tableDeferred.resolve(missingEntry);
                      }
                    }).fail(tableDeferred.reject);
                  }).fail(tableDeferred.reject);
                }
              }
            });

            $.when.apply($, runningPromises).always(function () {
              runningPromises.length = 0;
              Object.keys(activeTableIndex).forEach(function (key) {
                if (!tableQidIndex[key]) {
                  delete activeTableIndex[key];
                  updateTables = true;
                }
              });

              if (updateTables) {
                var tables = [];
                Object.keys(activeTableIndex).forEach(function (key) {
                  tables.push(activeTableIndex[key]);
                });

                tables.sort(function (a, b) {
                  return a.catalogEntry.name.localeCompare(b.catalogEntry.name);
                });
                self.activeTables(tables);
              }
            });
          }
        };

        var entryRefreshedSub = huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
          var sourceType = details.entry.getSourceType();
          if (sources[sourceType]) {
            var completeRefresh = false;
            if (details.entry.isSource()) {
              sources[sourceType].databaseIndex = {};
              sources[sourceType].activeTableIndex = {};
              completeRefresh = true;
            } else if (details.entry.isDatabase() && sources[sourceType].databaseIndex[details.entry.name]) {
              var dbEntry = sources[sourceType].databaseIndex[details.entry.name];
              var activeTableIndex = sources[sourceType].activeTableIndex;
              Object.keys(activeTableIndex).forEach(function (tableKey) {
                var tableEntry = activeTableIndex[tableKey];
                if (tableEntry.parent === dbEntry) {
                  delete activeTableIndex[tableKey];
                  completeRefresh = true;
                }
              });
            } else if (details.entry.isTableOrView()) {
              var activeTableIndex = sources[sourceType].activeTableIndex;
              if (activeTableIndex[details.entry.getQualifiedPath()]) {
                delete activeTableIndex[details.entry.getQualifiedPath()];
                completeRefresh = true;
              }
            }
            if (completeRefresh) {
              handleLocationUpdate(self.activeLocations());
            }
          }
        });

        if (self.activeTab() === 'editorAssistant') {
          huePubSub.publish('get.active.editor.locations', handleLocationUpdate);
        } else {
          updateOnVisible = true;
        }

        var activeTabSub = self.activeTab.subscribe(function (activeTab) {
          if (activeTab === 'editorAssistant' && updateOnVisible) {
            huePubSub.publish('get.active.editor.locations', handleLocationUpdate);
          }
        });

        self.disposals.push(function () {
          entryRefreshedSub.remove();
          activeTabSub.dispose();
        });

        var activeLocationsSub = huePubSub.subscribe('editor.active.locations', function (activeLocations) {
          if (self.activeTab() === 'editorAssistant') {
            handleLocationUpdate(activeLocations);
          } else {
            updateOnVisible = true;
          }
        });

        var activeRisksSub = huePubSub.subscribe('editor.active.risks', function (details) {
          if (details.risks !== self.activeRisks()) {
            self.activeRisks(details.risks);
            self.activeEditor(details.editor);
          }
        });

        huePubSub.publish('editor.get.active.risks', function (details) {
          self.activeRisks(details.risks);
          self.activeEditor(details.editor);
        });

        self.disposals.push(function () {
          activeLocationsSub.remove();
          activeRisksSub.remove();
        });
      }

      EditorAssistantPanel.prototype.addFilter = function (riskId) {
        var self = this;
        if (self.activeLocations() && self.activeEditor()) {
          self.activeLocations().activeStatementLocations.every(function (location) {
            var isLowerCase = false;
            if (self.activeLocations().activeStatementLocations && self.activeLocations().activeStatementLocations.length > 0) {
              var firstToken = self.activeLocations().activeStatementLocations[0].firstToken;
              isLowerCase = firstToken === firstToken.toLowerCase();
            }

            if (location.type === 'whereClause' && !location.subquery && (location.missing || riskId === 22 )) {
              self.activeEditor().moveCursorToPosition({
                row: location.location.last_line - 1,
                column: location.location.last_column - 1
              });
              self.activeEditor().clearSelection();

              if (/\S$/.test(self.activeEditor().getTextBeforeCursor())) {
                self.activeEditor().session.insert(self.activeEditor().getCursorPosition(), ' ');
              }

              var operation = location.missing ? 'WHERE ' : 'AND ';
              self.activeEditor().session.insert(self.activeEditor().getCursorPosition(), isLowerCase ? operation.toLowerCase() : operation);
              self.activeEditor().focus();

              if (riskId === 22) {
                huePubSub.publish('editor.autocomplete.temporary.sort.override', { partitionColumnsFirst: true });
              }

              window.setTimeout(function () {
                self.activeEditor().execCommand("startAutocomplete");
              }, 1);

              return false;
            }
            return true;
          })
        }
      };

      EditorAssistantPanel.prototype.uploadTableStats = function (showProgress) {
        var self = this;
        if (self.uploadingTableStats()) {
          return;
        }
        self.uploadingTableStats(true);
        huePubSub.publish('editor.upload.table.stats', {
          activeTables: self.activeTables(),
          showProgress: showProgress,
          callback: function () {
            self.uploadingTableStats(false);
          }
        });
      };

      EditorAssistantPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('editor-assistant-panel', {
        viewModel: EditorAssistantPanel,
        template: { element: 'editor-assistant-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="schedule-panel-template">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko if: selectedNotebook() && selectedNotebook().isBatchable() -->
        <!-- ko with: selectedNotebook() -->
        <div class="tab-pane" id="scheduleTab">
          <!-- ko ifnot: isSaved() && ! isHistory() -->
          ${ _('Query needs to be saved.') }
          <!-- /ko -->
          <!-- ko if: isSaved() && ! isHistory() -->
            <!-- ko if: schedulerViewModelIsLoaded() && schedulerViewModel.coordinator.isDirty() -->
            <a data-bind="click: saveScheduler" href="javascript: void(0);">${ _('Save changes') }</a>
            <!-- /ko -->
            <!-- ko if: schedulerViewModelIsLoaded() && ! schedulerViewModel.coordinator.isDirty() && (! viewSchedulerId() || isSchedulerJobRunning() == false )-->
            <a data-bind="click: showSubmitPopup" href="javascript: void(0);">${ _('Start') }</a>
            <!-- /ko -->
            <!-- ko if: schedulerViewModelIsLoaded() && viewSchedulerId()-->
            <a data-bind="click: function() { huePubSub.publish('show.jobs.panel', {id: viewSchedulerId(), interface: 'schedules'}) }, clickBubble: false" href="javascript: void(0);">
              ${ _('View') }
            </a>
            <!-- ko if: isSchedulerJobRunning() -->
              ${ _("Running")}
            <!-- /ko -->
            <!-- ko if: isSchedulerJobRunning() == false -->
              ${ _("Stopped")}
            <!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
          <br>
          <br>
          <div id="schedulerEditor"></div>
        </div>
        <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      function SchedulePanel(params) {
        var self = this;
        self.disposals = [];
        self.selectedNotebook = ko.observable();

        // TODO: Move all the scheduler logic out of the notebook to here.

        var selectedNotebookSub = self.selectedNotebook.subscribe(function (notebook) { // Happening 4 times for each notebook loaded
          if (notebook && notebook.schedulerViewModel == null && notebook.isSaved() && ! notebook.isHistory()) {
            notebook.loadScheduler();
            if (notebook.viewSchedulerId()) {
              huePubSub.publish('check.schedules.browser');
            }
          }
        });
        self.disposals.push(selectedNotebookSub.dispose.bind(selectedNotebookSub));

        var setSelectedNotebookSub = huePubSub.subscribe('jobbrowser.schedule.data', function (jobs) {
          if (self.selectedNotebook() && self.selectedNotebook().viewSchedulerId()) {
            var _job = $.grep(jobs, function (job) {
              return self.selectedNotebook().viewSchedulerId() == job.id;
            });
            self.selectedNotebook().isSchedulerJobRunning(_job.length > 0 && _job[0].apiStatus == 'RUNNING');
          }
        });
        self.disposals.push(setSelectedNotebookSub.remove.bind(setSelectedNotebookSub));

        // Hue 3
        var setSelectedNotebookSub = huePubSub.subscribe('set.selected.notebook', self.selectedNotebook);
        self.disposals.push(setSelectedNotebookSub.remove.bind(setSelectedNotebookSub));
        var selectedNotebookChangedSub = huePubSub.subscribe('selected.notebook.changed', self.selectedNotebook);
        self.disposals.push(selectedNotebookChangedSub.remove.bind(selectedNotebookChangedSub));
        huePubSub.publish('get.selected.notebook');

        // Hue 4
        var currentAppSub = huePubSub.subscribe('set.current.app.view.model', function (viewModel) {
          if (viewModel.selectedNotebook) {
            if (viewModel.selectedNotebook()) {
              self.selectedNotebook(viewModel.selectedNotebook());
            } else {
              var subscription = viewModel.selectedNotebook.subscribe(function (notebook) {
                self.selectedNotebook(notebook);
                subscription.dispose();
              });
            }
          } else {
            self.selectedNotebook(null);
          }
        });
        self.disposals.push(currentAppSub.remove.bind(currentAppSub));
      }

      SchedulePanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('schedule-panel', {
        viewModel: SchedulePanel,
        template: { element: 'schedule-panel-template' }
      });
    })();
  </script>

  <script type="text/javascript">
    (function () {
      function DashboardAssistantPanel(params) {
        var self = this;

        self.disposals = [];
        self.isSolr = ko.observable(true);

        self.showRisks = ko.observable(false);

        self.filter = {
          querySpec: ko.observable({
            query: '',
            facets: {},
            text: []
          }).extend({ rateLimit: 300 })
        };

        self.sourceType = ko.observable('solr');

        self.activeTables = ko.observableArray();

        self.filteredTables = AssistantUtils.getFilteredTablesPureComputed(self);

        self.someLoading = ko.pureComputed(function () {
          return self.activeTables().some(function (table) {
            return table.loading() || (!table.hasEntries() && !table.hasErrors());
          });
        });

        var navigationSettings = {
          showStats: true,
          rightAssist: true
        };
        var i18n = {};

        var activeDashboardCollection = huePubSub.subscribe('set.active.dashboard.collection', function(collection) {
          var collectionName = collection.name();

          if (!collectionName) {
            return;
          }

          self.sourceType = ko.observable(collection.engine());

          var assistDbSource = new AssistDbSource({
            i18n : i18n,
            initialNamespace: collection.activeNamespace,
            initialCompute: collection.activeCompute,
            type: collection.engine(),
            name: collection.engine(),
            nonSqlType: true,
            navigationSettings: navigationSettings
          });

          var fakeParentName = collectionName.indexOf('.') > -1 ? collectionName.split('.')[0] : 'default';

          var sourceType = collection.source() === 'query' ? collection.engine() + '-query' : collection.engine();

          dataCatalog.getEntry({
            sourceType: sourceType,
            namespace: collection.activeNamespace,
            compute: collection.activeCompute,
            path: [ fakeParentName ],
            definition: { type: 'database' }
          }).done(function (fakeDbCatalogEntry) {
            var assistFakeDb = new AssistDbEntry(fakeDbCatalogEntry, null, assistDbSource, self.filter, i18n, navigationSettings);
            dataCatalog.getEntry({
              sourceType: sourceType,
              namespace: collection.activeNamespace,
              compute: collection.activeCompute,
              path: [fakeParentName, collectionName.indexOf('.') > -1 ? collectionName.split('.')[1] : collectionName],
              definition: { type: 'table' }
            }).done(function (collectionCatalogEntry) {
              var collectionEntry = new AssistDbEntry(collectionCatalogEntry, assistFakeDb, assistDbSource, self.filter, i18n, navigationSettings);
              self.activeTables([collectionEntry]);

              if (!collectionEntry.loaded && !collectionEntry.hasErrors() && !collectionEntry.loading()) {
                collectionEntry.loadEntries(function() { collectionEntry.toggleOpen(); });
              }
            });
          });

          self.autocompleteFromEntries = function (nonPartial, partial) {
            var added = {};
            var result = [];
            var partialLower = partial.toLowerCase();
            self.activeTables().forEach(function (table) {
              if (!added[table.catalogEntry.name] && table.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
                added[table.catalogEntry.name] = true;
                result.push(nonPartial + partial + table.catalogEntry.name.substring(partial.length))
              }
              table.entries().forEach(function (col) {
                if (!added[col.catalogEntry.name] && col.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
                  added[col.catalogEntry.name] = true;
                  result.push(nonPartial + partial + col.catalogEntry.name.substring(partial.length))
                }
              })
            });
            return result;
          };
        });

        self.disposals.push(function () {
          activeDashboardCollection.remove();
        });
      }

      DashboardAssistantPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('dashboard-assistant-panel', {
        viewModel: DashboardAssistantPanel,
        template: { element: 'editor-assistant-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="right-assist-panel-template">
    <div class="right-assist-tabs" data-bind="splitFlexDraggable : {
        containerSelector: '.content-wrapper',
        sidePanelSelector: '.right-panel',
        sidePanelVisible: visible,
        orientation: 'right',
        onPosition: function() { huePubSub.publish('split.draggable.position') }
      }">
      <div class="right-assist-tab" data-bind="visible: editorAssistantTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Assistant') }" data-bind="css: { 'blue' : activeTab() === 'editorAssistant' }, tooltip: { placement: 'left' }, click: editorAssistantTabClick"><i class="fa fa-fw fa-compass"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: dashboardAssistantTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Assistant') }" data-bind="css: { 'blue' : activeTab() === 'dashboardAssistant' }, tooltip: { placement: 'left' }, click: dashboardAssistantTabClick"><i class="fa fa-fw fa-compass"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: functionsTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Functions') }" data-bind="css: { 'blue' : activeTab() === 'functions' }, tooltip: { placement: 'left' }, click: functionsTabClick"><i class="fa fa-fw fa-superscript"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: langRefTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Language Reference') }" data-bind="css: { 'blue' : activeTab() === 'langRef' }, tooltip: { placement: 'left' }, click: langRefTabClick"><i class="fa fa-fw fa-book"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: schedulesTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Schedule') }" data-bind="css: { 'blue' : activeTab() === 'schedules' }, tooltip: { placement: 'left' }, click: schedulesTabClick"><i class="fa fa-fw fa-calendar"></i></a></div>
    </div>

    <!-- ko if: visible -->
    <div class="right-assist-contents">
      <!-- ko if: editorAssistantTabAvailable-->
      <div data-bind="component: { name: 'editor-assistant-panel', params: { activeTab: activeTab, sourceType: sourceType } }, visible: activeTab() === 'editorAssistant'"></div>
      <!-- /ko -->

      <!-- ko if: functionsTabAvailable -->
      <div data-bind="component: { name: 'functions-panel' }, visible: activeTab() === 'functions'"></div>
      <!-- /ko -->

      <!-- ko if: langRefTabAvailable -->
      <div data-bind="component: { name: 'language-reference-panel' }, visible: activeTab() === 'langRef'"></div>
      <!-- /ko -->

      <!-- ko if: dashboardAssistantTabAvailable -->
      <div data-bind="component: { name: 'dashboard-assistant-panel' }, visible: activeTab() === 'dashboardAssistant'"></div>
      <!-- /ko -->

      ## TODO: Switch to if: when loadSchedules from notebook.ko.js has been moved to the schedule-panel component
      <div data-bind="component: { name: 'schedule-panel' }, visible: activeTab() === 'schedules'" style="display:none;"></div>
    </div>
    <!-- /ko -->
  </script>


  <script type="text/javascript">
    (function () {

      var EDITOR_ASSISTANT_TAB = 'editorAssistant';
      var DASHBOARD_ASSISTANT_TAB = 'dashboardAssistant';
      var FUNCTIONS_TAB = 'functions';
      var SCHEDULES_TAB = 'schedules';
      var LANG_REF_TAB = 'langRef';

      function RightAssistPanel(params) {
        var self = this;
        self.disposals = [];

        self.activeTab = ko.observable();
        self.visible = params.visible;
        self.sourceType = ko.observable();

        self.editorAssistantTabAvailable = ko.observable(false);
        self.dashboardAssistantTabAvailable = ko.observable(false);
        self.functionsTabAvailable = ko.observable(false);
        self.langRefTabAvailable = ko.observable(false);
        self.schedulesTabAvailable = ko.observable(false);

        self.lastActiveTabEditor = window.apiHelper.withTotalStorage('assist', 'last.open.right.panel', ko.observable(), EDITOR_ASSISTANT_TAB);
        self.lastActiveTabDashboard = window.apiHelper.withTotalStorage('assist', 'last.open.right.panel.dashboard', ko.observable(), DASHBOARD_ASSISTANT_TAB);

        huePubSub.subscribe('assist.highlight.risk.suggestions', function () {
          if (self.editorAssistantTabAvailable() && self.activeTab() !== EDITOR_ASSISTANT_TAB) {
            self.activeTab(EDITOR_ASSISTANT_TAB);
          }
        });

        huePubSub.subscribe('assist.lang.ref.show.topic', function (targetTopic) {
          huePubSub.publish('right.assist.show');
          if (self.langRefTabAvailable() && self.activeTab() !== LANG_REF_TAB) {
            self.activeTab(LANG_REF_TAB);
          }
          huePubSub.publish('assist.lang.ref.panel.show.topic', targetTopic)
        });

        var updateTabs = function () {
          if (!self.visible()) {
            self.activeTab(undefined);
            return;
          }
          if (self.lastActiveTabEditor() === FUNCTIONS_TAB && self.functionsTabAvailable()) {
            self.activeTab(FUNCTIONS_TAB);
          } else if (self.lastActiveTabEditor() === SCHEDULES_TAB && self.schedulesTabAvailable()) {
            self.activeTab(SCHEDULES_TAB);
          } else if (self.lastActiveTabEditor() === LANG_REF_TAB && self.langRefTabAvailable()) {
            self.activeTab(LANG_REF_TAB);
          } else if (self.editorAssistantTabAvailable()) {
            self.activeTab(EDITOR_ASSISTANT_TAB);
          } else if (self.functionsTabAvailable()) {
            self.activeTab(FUNCTIONS_TAB);
          } else if (self.schedulesTabAvailable()) {
            self.activeTab(SCHEDULES_TAB);
          } else if (self.dashboardAssistantTabAvailable()) {
            self.activeTab(DASHBOARD_ASSISTANT_TAB);
          } else {
            self.activeTab(undefined);
          }
        };

        var updateContentsForType = function (type, isSqlDialect) {
          self.sourceType(type);

          // TODO: Get these dynamically from langref and functions modules when moved to webpack
          self.functionsTabAvailable(type === 'hive' || type === 'impala' || type === 'pig');
          self.langRefTabAvailable(type === 'hive' || type === 'impala');
          self.editorAssistantTabAvailable((!window.IS_EMBEDDED || window.EMBEDDED_ASSISTANT_ENABLED) && isSqlDialect);
          self.dashboardAssistantTabAvailable(type === 'dashboard');
          self.schedulesTabAvailable(false);
          if (type !== 'dashboard') {
            if ('${ ENABLE_QUERY_SCHEDULING.get() }' === 'True') {
              huePubSub.subscribeOnce('set.current.app.view.model', function (viewModel) {
                // Async
                self.schedulesTabAvailable(!!viewModel.selectedNotebook);
                updateTabs();
              });
              huePubSub.publish('get.current.app.view.model');
            } else {
              self.schedulesTabAvailable(false);
            }
          }
          updateTabs();
        };

        var snippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', function (details) { updateContentsForType(details.type, details.isSqlDialect) });
        self.disposals.push(snippetTypeSub.remove.bind(snippetTypeSub));

        huePubSub.subscribe('set.current.app.name', function (appName) {
          if (appName === 'dashboard') {
            updateContentsForType(appName, false);
          }
        });
        huePubSub.publish('get.current.app.name');
        updateTabs();
      }

      RightAssistPanel.prototype.switchTab = function (tabName) {
        var self = this;
        if (self.activeTab() === tabName) {
          self.visible(false);
          self.activeTab(undefined);
        } else {
          self.activeTab(tabName);
          if (!self.visible()) {
            self.visible(true);
          }
        }
      };

      RightAssistPanel.prototype.editorAssistantTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(EDITOR_ASSISTANT_TAB);
        self.switchTab(EDITOR_ASSISTANT_TAB);
      };

      RightAssistPanel.prototype.dashboardAssistantTabClick = function () {
        var self = this;
        self.lastActiveTabDashboard(DASHBOARD_ASSISTANT_TAB);
        self.switchTab(DASHBOARD_ASSISTANT_TAB);
      };

      RightAssistPanel.prototype.functionsTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(FUNCTIONS_TAB);
        self.switchTab(FUNCTIONS_TAB);
      };

      RightAssistPanel.prototype.langRefTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(LANG_REF_TAB);
        self.switchTab(LANG_REF_TAB);
      };

      RightAssistPanel.prototype.schedulesTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(SCHEDULES_TAB);
        self.switchTab(SCHEDULES_TAB);
      };

      RightAssistPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('right-assist-panel', {
        viewModel: RightAssistPanel,
        template: { element: 'right-assist-panel-template' }
      });
    })();
  </script>
</%def>
