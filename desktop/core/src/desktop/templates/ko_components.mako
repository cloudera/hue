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

<%def name="all()">
  <script type="text/html" id="hue-drop-down-template">
    <!-- ko if: !dropDownVisible() || !searchable -->
    <a class="inactive-action hue-drop-down-active" href="javascript:void(0)" data-bind="toggle: dropDownVisible, css: { 'blue': dropDownVisible }">
      <!-- ko if: icon --><i class="fa" data-bind="css: icon"></i><!-- /ko -->
      <!-- ko if: value -->
      <span data-bind="text: typeof value().label !== 'undefined' ? value().label : value(), visible: ! dropDownVisible() || !searchable, attr: { 'title': linkTitle }" ></span>
      <!-- /ko -->
      <i class="fa fa-caret-down"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: dropDownVisible() && searchable -->
    <input class="hue-drop-down-input" type="text" data-bind="textInput: filter, attr: { 'placeHolder': value }, visible: dropDownVisible, style: { color: filterEdited() ? '#000' : '#AAA', 'min-height': '22px', 'margin-left': '10px' }"/>
    <i class="fa fa-caret-down"></i>
    <!-- /ko -->
    <div class="hue-drop-down-container" data-bind="css: { 'open' : dropDownVisible, 'hue-drop-down-fixed': fixedPosition }">
      <div class="dropdown-menu" data-bind="visible: filteredEntries().length > 0" style="min-width: 190px; max-width: 250px; min-height: 34px; max-height: 200px;">
        <!-- ko if: foreachVisible -->
        <ul class="hue-inner-drop-down" style="overflow-x: hidden;" data-bind="foreachVisible: { data: filteredEntries, minHeight: 34, container: '.dropdown-menu' }">
          <li><a href="javascript:void(0)" data-bind="text: typeof $data.label !== 'undefined' ? $data.label : $data, click: function () { $parent.value($data); }"></a></li>
        </ul>
        <!-- /ko -->
        <!-- ko ifnot: foreachVisible -->
        <ul class="hue-inner-drop-down" style="overflow-x: hidden;" data-bind="foreach: filteredEntries">
          <li><a href="javascript:void(0)" data-bind="text: typeof $data.label !== 'undefined' ? $data.label : $data, click: function () { $parent.value($data); }"></a></li>
        </ul>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var HueDropDown = function (params, element) {
        var self = this;
        self.dropDownVisible = ko.observable(false);
        self.icon = params.icon;
        self.value = params.value;
        self.entries = params.entries;
        self.searchable = params.searchable || false;
        self.foreachVisible = params.foreachVisible || false;
        self.linkTitle = params.linkTitle || '${ _('Selected entry') }';
        self.fixedPosition = !!params.fixedPosition;

        var closeOnOutsideClick = function (e) {
          var $input = $(element).find('.hue-drop-down-input');
          if (!$input.is($(e.target))) {
            self.dropDownVisible(false);
          }
        };

        var inputKeyup = function (e) {
          var $currentActive = $(element).find('.hue-inner-drop-down > .active');
          var activeTop = $currentActive.length !== 0 ? $currentActive.position().top : 0;
          var activeHeight = $currentActive.length !== 0 ? $currentActive.outerHeight(true) : $(element).find('.hue-inner-drop-down li:first-child').outerHeight(true);
          var containerHeight = $(element).find('.dropdown-menu').innerHeight();
          var containerScrollTop = $(element).find('.dropdown-menu').scrollTop();

          $currentActive.removeClass('active');
          if (e.keyCode === 27) {
            // esc
            self.dropDownVisible(false);
          } else if (e.keyCode === 38) {
            // up
            if ($currentActive.length !== 0 && $currentActive.prev().length !== 0) {
              if (activeTop < containerScrollTop + activeHeight) {
                $(element).find('.dropdown-menu').scrollTop(activeTop - containerHeight/2);
              }
              $currentActive.prev().addClass('active');
            }
          } else if (e.keyCode === 40) {
            // down
            if ($currentActive.length === 0) {
              $(element).find('.hue-inner-drop-down li:first-child').addClass('active');
            } else if ($currentActive.next().length !== 0) {
              if ((activeTop + activeHeight *3) > containerHeight - containerScrollTop) {
                $(element).find('.dropdown-menu').scrollTop(activeTop - containerHeight/2);
              }
              $currentActive.next().addClass('active');
            } else {
              $currentActive.addClass('active');
            }
          } else if (e.keyCode === 13) {
            // enter
            if ($currentActive.length > 0) {
              self.value(ko.dataFor($currentActive[0]));
              self.dropDownVisible(false);
              $(element).find('.dropdown-menu').scrollTop(0)
            }
          } else {
            $(element).find('.dropdown-menu').scrollTop(0)
          }
        };
        self.filter = ko.observable('');

        self.value.subscribe(function () {
          self.dropDownVisible(false);
        });

        self.filterEdited = ko.observable(false);

        self.filter.subscribe(function () {
          self.filterEdited(true);
          $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
        });
        self.dropDownVisible.subscribe(function (newValue) {
          self.filterEdited(false);
          if (newValue) {
            window.setTimeout(function () {
              self.filter('');
              $(window).on('click', closeOnOutsideClick);
              $(element).find('.hue-drop-down-input').on('keyup', inputKeyup);
              $(element).find('.hue-drop-down-input').focus();
            }, 0);
          } else {
            $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
            $(window).off('click', closeOnOutsideClick);
            $(element).find('.hue-drop-down-input').off('keyup', inputKeyup);
          }
        });
        self.filteredEntries = ko.pureComputed(function () {
          if (self.filter() === '' || ! self.filterEdited()) {
            return self.entries();
          } else {
            var lowerFilter = self.filter().toLowerCase();
            return self.entries().filter(function (database) {
              return database.toLowerCase().indexOf(lowerFilter) !== -1;
            });
          }
        });
      };

      ko.components.register('hue-drop-down', {
        viewModel: {
          createViewModel: function(params, componentInfo) {
            return new HueDropDown(params, componentInfo.element);
          }
        },
        template: { element: 'hue-drop-down-template' }
      });
    })();
  </script>

  <script type="text/html" id="hue-history-panel-template">
    <button class="btn btn-flat pull-right btn-toggle-jobs-panel" title="${_('Task history')}" data-bind="toggle: historyPanelVisible">
      <i class="fa fa-history"></i>
      <div class="jobs-badge" data-bind="text: historyRunningJobs().length, visible: historyRunningJobs().length > 0"></div>
      ## <div class="jobs-badge" data-bind="text: historyFinishedJobs().length, visible: historyFinishedJobs().length > 0"></div>
    </button>

    <div class="jobs-panel history-panel" data-bind="visible: historyPanelVisible" style="display: none;">
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
          <a class="pull-right margin-right-10" href="javascript:void(0)" data-bind="hueLink: onSuccessUrl()">
            ${ _('Output') }
          </a>
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
        <pre data-bind="visible: result.logs() && result.logs().length > 0, text: result.logs, logScroller: result.logs, logScrollerVisibilityEvent: showLogs, niceScroll" class="logs logs-bigger logs-populated" style="height: 120px"></pre>
        <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
      </div>
      <!-- ko if: history -->
      <hr>
      <div class="notification-history margin-bottom-10" data-bind="niceScroll">
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
          }
        });
        self.editorViewModel.editorMode(true);
        self.editorViewModel.isNotificationManager(true);
        self.editorViewModel.newNotebook();

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

      ko.components.register('hue-history-panel', {
        viewModel: HistoryPanel,
        template: { element: 'hue-history-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="hue-job-browser-links-template">
    <div class="btn-group pull-right">
      <button class="btn btn-flat" style="padding-right: 2px" title="${_('Job browser')}" data-bind="hueLink: '/jobbrowser', click: function(){ huePubSub.publish('hide.jobs.panel'); }">
        <span>${ _('Jobs') }</span>
      </button>
      <button class="btn btn-flat btn-toggle-jobs-panel" title="${_('Mini job browser')}" data-bind="click: function() { huePubSub.publish('toggle.jobs.panel'); }, style: {'paddingLeft': jobCount() > 0 ? '0': '4px'}">
        <span class="jobs-badge" data-bind="visible: jobCount() > 0, text: jobCount"></span>
        <i class="fa fa-sliders"></i>
      </button>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var JB_CHECK_INTERVAL_IN_MILLIS = 30000;

      var JobBrowserPanel = function (params) {
        var self = this;

        huePubSub.subscribe('hide.jobs.panel', function () {
          $('#jobsPanel').hide();
        });

        huePubSub.subscribe('show.jobs.panel', function () {
          huePubSub.publish('hide.history.panel');
          $('#jobsPanel').show();
          huePubSub.publish('mini.jb.navigate');
        });

        huePubSub.subscribe('toggle.jobs.panel', function () {
          if ($('#jobsPanel').is(':visible')){
            huePubSub.publish('hide.jobs.panel');
          }
          else {
            huePubSub.publish('show.jobs.panel');
          }
        });

        self.jobCount = ko.observable(0);
        self.onePageViewModel = params.onePageViewModel;

        var lastJobBrowserRequest = null;

        var checkJobBrowserStatus = function() {
          if (lastJobBrowserRequest !== null && lastJobBrowserRequest.readyState < 4) {
            return;
          }
          window.clearTimeout(checkJobBrowserStatusIdx);
          lastJobBrowserRequest = $.post("/jobbrowser/jobs/", {
              "format": "json",
              "state": "running",
              "user": "${user.username}"
            },
            function(data) {
              if (data != null && data.jobs != null) {
                huePubSub.publish('jobbrowser.data', data.jobs);
                self.jobCount(data.jobs.length);
              }
              checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
            }).fail(function () {
            window.clearTimeout(checkJobBrowserStatusIdx);
          });
        };

        // Load the mini jobbrowser
        $.ajax({
          url: '/jobbrowser/apps?is_embeddable=true&is_mini=true',
          beforeSend: function (xhr) {
            xhr.setRequestHeader('X-Requested-With', 'Hue');
          },
          dataType: 'html',
          success: function (response) {
            var r = params.onePageViewModel.processHeaders(response);
            $('#mini_jobbrowser').html(r);
          }
        });

        var checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);

        huePubSub.subscribe('check.job.browser', checkJobBrowserStatus);
      };

      ko.components.register('hue-job-browser-links', {
        viewModel: JobBrowserPanel,
        template: { element: 'hue-job-browser-links-template' }
      });
    })();
  </script>

  <script type="text/html" id="hue-favorite-app-template">
    <!-- ko if: isHue4 -->
    <div class="inline pointer favorite-app" data-bind="click: setAsFavoriteApp, attr: { title: isFavorite() ? '${ _ko("Unset from default application") }' : '${ _ko("Set as default application") }' }">
      <i class="fa inactive-action" data-bind="css: { 'fa-star-o': !isFavorite(), 'fa-star': isFavorite }"></i>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/javascript">
    (function () {

      var FavoriteApp = function (params) {
        var self = this;
        self.isHue4 = ko.observable(params.hue4);
        self.isFavorite = ko.observable(false);
        self.app = params.app;
        self.interpreter = params.interpreter;

        self.parseCurrentFavorite = function (data, announce) {
          self.isFavorite(false);
          if (data.status === 0 && data.data && data.data.default_app) {
            try {
              var defaultApp = JSON.parse(data.data.default_app);
              self.isFavorite(defaultApp.app === self.app && ((self.app === 'editor' && defaultApp.interpreter === self.interpreter) || self.app !== 'editor'));
              if (announce) {
                huePubSub.publish('hue.new.default.app', defaultApp);
              }
            } catch (e) {
              console.error('${ _ko("There was a problem decoding the default app setting.") }');
            }
          }
        };

        self.setAsFavoriteApp = function (vm, e) {
          e.originalEvent.stopPropagation();
          e.originalEvent.stopImmediatePropagation();
          var postParams = {
            app: self.app
          };
          if (self.interpreter !== '') {
            postParams['interpreter'] = self.interpreter;
          }
          var post = {};
          if (self.isFavorite()) {
            post['delete'] = true;
          }
          else {
            post['set'] = ko.mapping.toJSON(postParams);
          }
          $.post('/desktop/api2/user_preferences/default_app', post, function (data) {
            self.parseCurrentFavorite(data, true);
          });
        };

        if (self.isHue4()) {
          // Load the fav app status
          $.get('/desktop/api2/user_preferences/default_app', function (data) {
            self.parseCurrentFavorite(data);
          });
        }
      };

      ko.components.register('hue-favorite-app', {
        viewModel: FavoriteApp,
        template: {element: 'hue-favorite-app-template'}
      });
    })();
  </script>
</%def>