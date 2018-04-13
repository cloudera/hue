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

<%def name="historyPanel()">

  <script type="text/html" id="hue-history-panel-template">
    <button class="btn btn-flat pull-right btn-toggle-jobs-panel" title="${_('Task history')}" data-bind="click: toggleVisibility">
      <i class="fa fa-history"></i>
      <div class="jobs-badge" data-bind="text: historyRunningJobs().length, visible: historyRunningJobs().length > 0"></div>
      ## <div class="jobs-badge" data-bind="text: historyFinishedJobs().length, visible: historyFinishedJobs().length > 0"></div>
    </button>

    <div class="jobs-panel history-panel" data-bind="visible: historyPanelVisible, style: { 'top' : top, 'left': left }" style="display: none;">
      <a class="pointer inactive-action pull-right" data-bind="click: function(){ historyPanelVisible(false); }"><i class="fa fa-fw fa-times"></i></a>
      <!-- ko ifnot: editorViewModel.selectedNotebook() && editorViewModel.selectedNotebook().history().length > 0 -->
        <span style="font-style: italic">${ _('No task history.') }</span>
      <!-- /ko -->
      <!-- ko if: editorViewModel.selectedNotebook() && editorViewModel.selectedNotebook().history().length > 0 -->
      <!-- ko with: editorViewModel.selectedNotebook() -->
      <div class="notification-history margin-bottom-10">
        <!-- ko if: onSuccessUrl() -->
        <div class="notification-history-title">
          <strong class="margin-left-5" data-bind="text: name"></strong>
          <!-- ko if: onSuccessUrl() !== 'assist.db.refresh' -->
          <a class="pull-right margin-right-10" href="javascript:void(0)" data-bind="hueLink: onSuccessUrl()">
            ${ _('Output') }
          </a>
          <!-- /ko -->
          <div class="clearfix"></div>
        </div>
        <!-- /ko -->
        <!-- ko if: snippets()[0] -->
        <!-- ko with: snippets()[0] -->
        <!-- ko if: progress -->
        <div class="snippet-progress-container">
          <div class="progress-snippet progress" data-bind="css: {
                    'progress-starting': progress() == 0 && status() == 'running',
                    'progress-warning': progress() > 0 && progress() < 100,
                    'progress-success': progress() == 100,
                    'progress-danger': progress() == 0 && errors().length > 0}" style="background-color: #FFF; width: 100%">
            <div class="bar" data-bind="style: {'width': (errors().length > 0 ? 100 : Math.max(2, progress())) + '%'}"></div>
          </div>
        </div>
        <!-- /ko -->
        <!-- ko if: result -->
        <pre data-bind="visible: result.logs() && result.logs().length == 0" class="logs logs-bigger">${ _('No logs available at this moment.') }</pre>
        <pre data-bind="visible: result.logs() && result.logs().length > 0, text: result.logs, logScroller: result.logs, logScrollerVisibilityEvent: showLogs" class="logs logs-bigger logs-populated" style="height: 120px"></pre>
        <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
      </div>
      <!-- ko if: history -->
      <hr>
      <div class="notification-history margin-bottom-10">
        <!-- ko if: history().length == 0 -->
        <span style="font-style: italic">${ _('No task history.') }</span>
        <!-- /ko -->
        <!-- ko if: history().length > 0 -->
        <div class="notification-history-title">
          <strong class="margin-left-5">${ _('Task History') }</strong>
          <div class="inactive-action pointer pull-right" title="${_('Clear the query history')}" data-target="#clearNotificationHistoryModal" data-toggle="modal" rel="tooltip">
            <i class="fa fa-calendar-times-o"></i>
          </div>
          <div class="clearfix"></div>
        </div>
        <ul class="unstyled notification-history-list">
          <!-- ko foreach: history -->
          <li data-bind="click: function() { $parents[1].editorViewModel.openNotebook(uuid()); }, css: {'active': $parents[1].editorViewModel.selectedNotebook() !== null && $parents[1].editorViewModel.selectedNotebook().uuid() === uuid() }">
            <div class="muted pull-left" data-bind="momentFromNow: {data: lastExecuted, interval: 10000, titleFormat: 'LLL'}"></div>
            <div class="pull-right muted">
              <!-- ko switch: status -->
              <!-- ko case: 'running' -->
              <div class="history-status" data-bind="tooltip: { title: '${ _ko("Query running") }', placement: 'bottom' }"><i class="fa fa-fighter-jet fa-fw"></i></div>
              <!-- /ko -->
              <!-- ko case: 'failed' -->
              <div class="history-status" data-bind="tooltip: { title: '${ _ko("Query failed") }', placement: 'bottom' }"><i class="fa fa-exclamation fa-fw"></i></div>
              <!-- /ko -->
              <!-- ko case: 'available' -->
              <div class="history-status" data-bind="tooltip: { title: '${ _ko("Result available") }', placement: 'bottom' }"><i class="fa fa-check fa-fw"></i></div>
              <!-- /ko -->
              <!-- ko case: 'expired' -->
              <div class="history-status" data-bind="tooltip: { title: '${ _ko("Result expired") }', placement: 'bottom' }"><i class="fa fa-unlink fa-fw"></i></div>
              <!-- /ko -->
              <!-- /ko -->
            </div>
            <div class="clearfix"></div>
            <strong data-bind="text: name, attr: { title: uuid }"></strong>
            <div data-bind="highlight: { value: query }"></div>
          </li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    </div>

    <div id="clearNotificationHistoryModal" class="modal hide fade" data-backdrop="false">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Confirm History Clearing')}</h2>
      </div>
      <div class="modal-body">
        <p>${_('Are you sure you want to clear the task history?')}</p>
      </div>
      <div class="modal-footer">
        <a class="btn" data-dismiss="modal">${_('No')}</a>
        <a class="btn btn-danger disable-feedback" data-bind="click: function() { editorViewModel.selectedNotebook().clearHistory(); editorViewModel.selectedNotebook(null); }">${_('Yes')}</a>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var HistoryPanel = function (params) {
        var self = this;

        self.top = ko.observable();
        self.left = ko.observable();
        self.historyPanelVisible = ko.observable(false);

        self.historyPanelVisible.subscribe(function (newVal) {
          if (newVal) {
            huePubSub.publish('hide.jobs.panel');
          }
        });

        huePubSub.subscribe('hide.history.panel', function () {
          self.historyPanelVisible(false);
        });

        self.editorViewModel = new EditorViewModel(null, '', {
          user: '${ user.username }',
          userId: ${ user.id },
          languages: [{name: "Java", type: "java"}, {name: "Hive SQL", type: "hive"}], // TODO reuse
          snippetViewSettings: {
            hive: {
              placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
              aceMode: 'ace/mode/hive',
              snippetImage: '${ static("beeswax/art/icon_beeswax_48.png") }',
              sqlDialect: true
            },
            impala: {
              placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
              aceMode: 'ace/mode/impala',
              snippetImage: '${ static("impala/art/icon_impala_48.png") }',
              sqlDialect: true
            },
            java : {
              snippetIcon: 'fa-file-code-o'
            },
            shell: {
              snippetIcon: 'fa-terminal'
            },
            sqoop1: {
              sqlDialect: false
            },
            spark: {
              sqlDialect: false
            },
          }
        });
        self.editorViewModel.editorMode(true);
        self.editorViewModel.isNotificationManager(true);
        self.editorViewModel.newNotebook();

        self.$toggleElement;
        var $container = $(HUE_CONTAINER);

        self.reposition = function () {
          self.top((self.$toggleElement.offset().top + self.$toggleElement.height() + 15) + 'px');
          self.left(($container.offset().left + $container.width() - 630) + 'px');
        };

        self.historyRunningJobs = ko.computed(function() {
          if (self.editorViewModel.selectedNotebook()) {
            return $.grep(self.editorViewModel.selectedNotebook().history(), function(task) { return task.status() == 'running'; });
          } else {
            return [];
          }
        });
        self.historyFinishedJobs = ko.computed(function() {
          if (self.editorViewModel.selectedNotebook()) {
            return $.grep(self.editorViewModel.selectedNotebook().history(), function(task) { return task.status() == 'available' || task.status() == 'failed'; });
          } else {
            return [];
          }
        });


        huePubSub.subscribe("notebook.task.submitted", function (history_id) {
          self.editorViewModel.openNotebook(history_id, null, true, function(){
            var notebook = self.editorViewModel.selectedNotebook();
            notebook.snippets()[0].progress.subscribe(function(val){
              if (val == 100){
                //self.indexingStarted(false);
                //self.isIndexing(false);
                //self.indexingSuccess(true);
              }
            });

            notebook.snippets()[0].status.subscribe(function(val){
              if (val == 'failed'){
                //self.isIndexing(false);
                //self.indexingStarted(false);
                //self.indexingError(true);
              } else if (val == 'available') {
                var snippet = notebook.snippets()[0];
                if (! snippet.result.handle().has_more_statements) {
                  // TODO: Show finish notification and clicking on it does onSuccessUrl
                  // or if still on initial spinner we redirect automatically to onSuccessUrl
                  if (notebook.onSuccessUrl() && notebook.onSuccessUrl() !== 'assist.db.refresh') { // TODO: Similar if in in FB directory, also refresh FB dir
                    huePubSub.publish('open.link', notebook.onSuccessUrl());
                  }

                  if (notebook.onSuccessUrl() === 'assist.db.refresh') {
                    DataCatalog.getEntry({ sourceType: snippet.type(), path: [] }).done(function (entry) {
                      entry.clear('cache', true);
                    });
                  } else if (notebook.onSuccessUrl()) {
                    huePubSub.publish(notebook.pubSubUrl());
                  }
                } else { // Perform last DROP statement execute
                  snippet.execute();
                }
              }
            });
            notebook.snippets()[0].checkStatus();

            // Add to history
            notebook.history.unshift(
                notebook._makeHistoryRecord(
                    notebook.onSuccessUrl(),
                    notebook.description(),
                    (new Date()).getTime(),
                    notebook.snippets()[0].status(),
                    notebook.name(),
                    notebook.uuid()
                )
            );

            self.historyPanelVisible(true);
          });
        });
      };

      HistoryPanel.prototype.toggleVisibility = function (historyPanel, event) {
        var self = this;
        if (!self.historyPanelVisible()) {
          self.$toggleElement = $(event.target);
          self.reposition();
          $(window).on('resize', self.reposition);
          var positionSub = self.historyPanelVisible.subscribe(function (newValue) {
            if (!newValue) {
              $(window).off('resize', self.reposition);
              positionSub.dispose();
            }
          })
        }
        self.historyPanelVisible(!self.historyPanelVisible());
      };

      HistoryPanel.prototype.dispose = function () {
        $(window).off('resize', self.reposition);
      };

      ko.components.register('hue-history-panel', {
        viewModel: HistoryPanel,
        template: { element: 'hue-history-panel-template' }
      });
    })();
  </script>
</%def>