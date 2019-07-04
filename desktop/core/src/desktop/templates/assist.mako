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
  
  <script type="text/javascript">


    (function () {

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
      <div data-bind="component: { name: 'assist-editor-context-panel', params: { activeTab: activeTab, sourceType: sourceType } }, visible: activeTab() === 'editorAssistant'"></div>
      <!-- /ko -->

      <!-- ko if: functionsTabAvailable -->
      <div data-bind="component: { name: 'assist-functions-panel' }, visible: activeTab() === 'functions'"></div>
      <!-- /ko -->

      <!-- ko if: langRefTabAvailable -->
      <div data-bind="component: { name: 'assist-language-reference-panel' }, visible: activeTab() === 'langRef'"></div>
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
