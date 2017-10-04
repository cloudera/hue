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

  <script type="text/html" id="breadcrumbs-template">
    <div class="hue-breadcrumb-container">
      <!-- ko if: hiddenBreadcrumbs().length > 0 -->
      ...
      <!-- ko component: { name: 'hue-drop-down', params: { entries: hiddenBreadcrumbs, noLabel: true, searchable: false, value: hiddenValue } } --><!-- /ko -->
      <div class="hue-breadcrumb-divider" data-bind="text: divider"></div>
      <!-- /ko -->
      <!-- ko foreach: lastTwoBreadcrumbs -->
      <!-- ko if: $index() < $parent.lastTwoBreadcrumbs().length - 1 -->
      <div class="hue-breadcrumb pointer" data-bind="text: $data.label || $data, click: $parent.onSelect"></div>
      <div class="hue-breadcrumb-divider" data-bind="text: $parent.divider"></div>
      <!-- /ko -->
      <!-- ko if: $index() === $parent.lastTwoBreadcrumbs().length - 1 -->
      <div class="hue-breadcrumb pointer" data-bind="text: $data.label || $data"></div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      function BreadcrumbViewModel(params) {
        var self = this;
        self.hiddenValue = ko.observable();
        self.onSelect = params.onSelect || function () {};
        self.hiddenValue.subscribe(function (newValue) {
          if (newValue) {
            self.onSelect(newValue);
          }
        });
        self.hiddenBreadcrumbs = ko.pureComputed(function () {
          if (params.breadcrumbs().length > 2) {
            return params.breadcrumbs().slice(0, params.breadcrumbs().length - 2);
          }
          return [];
        });
        self.lastTwoBreadcrumbs = ko.pureComputed(function () {
          return params.breadcrumbs().slice(params.breadcrumbs().length - 2, params.breadcrumbs().length);
        });
        self.divider  = params.divider || '>';
      }

      ko.components.register('hue-breadcrumbs', {
        viewModel: BreadcrumbViewModel,
        template: { element: 'breadcrumbs-template' }
      });
    })();
  </script>

  <script type="text/html" id="hue-drop-down-template">
    <!-- ko if: !menuOnly && (!dropDownVisible() || !searchable) -->
    <a class="inactive-action hue-drop-down-active" href="javascript:void(0)" data-bind="toggle: dropDownVisible, css: { 'blue': dropDownVisible }">
      <!-- ko if: icon --><i class="fa" data-bind="css: icon"></i><!-- /ko -->
      <!-- ko if: !noLabel && value -->
      <span data-bind="text: typeof value().label !== 'undefined' ? value().label : value(), visible: ! dropDownVisible() || !searchable, attr: { 'title': linkTitle }" ></span>
      <!-- /ko -->
      <i class="fa fa-caret-down"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: !menuOnly && (dropDownVisible() && searchable) -->
    <input class="hue-drop-down-input" type="text" data-bind="textInput: filter, attr: { 'placeHolder': value }, visible: dropDownVisible, style: { color: filterEdited() ? '#000' : '#AAA', 'min-height': '22px', 'margin-left': '10px' }"/>
    <i class="fa fa-caret-down"></i>
    <!-- /ko -->
    <div class="hue-drop-down-container" data-bind="css: { 'open' : dropDownVisible, 'hue-drop-down-fixed': fixedPosition }">
      <div class="dropdown-menu" data-bind="visible: filteredEntries().length > 0" style="min-width: 190px; max-width: 250px; min-height: 34px; max-height: 200px;">
        <!-- ko if: foreachVisible -->
        <ul class="hue-inner-drop-down" style="overflow-x: hidden;" data-bind="foreachVisible: { data: filteredEntries, minHeight: 34, container: '.dropdown-menu' }">
          <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
          <li class="divider"></li>
          <!-- /ko -->
          <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
          <li><a href="javascript:void(0)" data-bind="text: typeof $data.label !== 'undefined' ? $data.label : $data, click: function () { $parent.value($data); }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
        <!-- ko ifnot: foreachVisible -->
        <ul class="hue-inner-drop-down" style="overflow-x: hidden;" data-bind="foreach: filteredEntries">
          <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
          <li class="divider"></li>
          <!-- /ko -->
          <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
          <li><a href="javascript:void(0)" data-bind="text: typeof $data.label !== 'undefined' ? $data.label : $data, click: function () { $parent.value($data); }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var HueDropDown = function (params, element) {
        var self = this;
        self.dropDownVisible = ko.observable(!!params.showOnInit);
        self.menuOnly = !!params.menuOnly;
        self.noLabel = !!params.noLabel;
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
      <a class="btn btn-flat" style="padding-right: 4px" title="${_('Job browser')}" data-bind="hueLink: '/jobbrowser#!jobs', click: function(){ huePubSub.publish('hide.jobs.panel'); }">
        <span>${ _('Jobs') }</span>
      </a>
      <button class="btn btn-flat btn-toggle-jobs-panel" title="${_('Jobs preview')}" data-bind="click: function() { huePubSub.publish('toggle.jobs.panel'); }, style: {'paddingLeft': jobCount() > 0 ? '0': '4px'}">
        <span class="jobs-badge" data-bind="visible: jobCount() > 0, text: jobCount"></span>
        <i class="fa fa-tasks"></i>
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

        huePubSub.subscribe('show.jobs.panel', function (section) {
          huePubSub.publish('hide.history.panel');
          $('#jobsPanel').show();
          huePubSub.publish('mini.jb.navigate', section && section.interface ? section.interface : 'jobs');
          if (section && section.id) {
            huePubSub.publish('mini.jb.open.job', section.id);
          }
        });

        huePubSub.subscribe('toggle.jobs.panel', function () {
          if ($('#jobsPanel').is(':visible')){
            huePubSub.publish('hide.jobs.panel');
          }
          else {
            huePubSub.publish('show.jobs.panel');
          }
        });

        self.jobCounts = ko.observable({'yarn': 0, 'schedules': 0});
        self.jobCount = ko.pureComputed(function() {
          var total = 0;
          Object.keys(self.jobCounts()).forEach(function (value) {
            total += self.jobCounts()[value];
          });
          return total;
        });
        self.onePageViewModel = params.onePageViewModel;

        var lastYarnBrowserRequest = null;
        var checkYarnBrowserStatus = function() {
          return $.post("/jobbrowser/jobs/", {
              "format": "json",
              "state": "running",
              "user": "${user.username}"
            },
            function(data) {
              if (data != null && data.jobs != null) {
                huePubSub.publish('jobbrowser.data', data.jobs);
                self.jobCounts()['yarn'] = data.jobs.length;
                self.jobCounts.valueHasMutated();
              }
          })
        };
        var lastScheduleBrowserRequest = null;
        var checkScheduleBrowserStatus = function() {
          return $.post("/jobbrowser/api/jobs", {
              interface: ko.mapping.toJSON("schedules"),
              filters: ko.mapping.toJSON([
                  {"text": "user:${user.username}"},
                  {"time": {"time_value": 7, "time_unit": "days"}},
                  {"states": ["running"]},
                  {"pagination": {"page": 1, "offset": 1, "limit": 1}}
              ])
            },
            function(data) {
              if (data != null && data.total != null) {
                huePubSub.publish('jobbrowser.schedule.data', data.apps);
                self.jobCounts()['schedules'] = data.total;
                self.jobCounts.valueHasMutated();
              }
          })
        };

        var checkJobBrowserStatus = function() {
          lastYarnBrowserRequest = checkYarnBrowserStatus();
          lastScheduleBrowserRequest = checkScheduleBrowserStatus();

          $.when.apply($, [lastYarnBrowserRequest, lastScheduleBrowserRequest])
          .done(function () {
            checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
           })
          .fail(function () {
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

        huePubSub.subscribe('check.job.browser', checkYarnBrowserStatus);
        huePubSub.subscribe('check.schedules.browser', checkScheduleBrowserStatus);
      };

      ko.components.register('hue-job-browser-links', {
        viewModel: JobBrowserPanel,
        template: { element: 'hue-job-browser-links-template' }
      });
    })();
  </script>

  <script type="text/html" id="hue-favorite-app-template">
    <!-- ko if: isHue4 -->
    <div class="inline pointer favorite-app" data-bind="click: setAsFavoriteApp, tooltip: { placement: 'bottom', title: isFavorite() ? '${ _ko("Unset from default application") }' : '${ _ko("Set as default application") }' }">
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

  <script type="text/html" id="inline-autocomplete-template">
    <div class="inline-autocomplete-container">
      <div>
        <input class="inline-autocomplete-input" type="text" data-bind="attr: { 'placeHolder' : hasFocus() ? '' : placeHolder }, textInput: searchInput, hasFocus: hasFocus, clearable: { value: searchInput, onClear: onClear }">
        <input class="inline-autocomplete-autocomplete" disabled type="text" data-bind="value: inlineAutocomplete">
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var InlineAutocomplete = function (params) {
        var self = this;
        self.placeHolder = params.placeHolder;
        self.hasFocus = params.hasFocus || ko.observable();
        self.searchInput = ko.observable('');
        self.querySpec = params.querySpec;
        self.inlineAutocomplete = ko.observable('');
        self.lastNonPartial = null;
        self.lastResult = {};
        self.autocompleteFromEntries = params.autocompleteFromEntries;
        self.disposals = [];

        self.facets = params.facets;
        self.knownFacetValues = params.knownFacetValues;

        self.onClear = function () {
          if (params.onClear) {
            params.onClear();
          }
          self.inlineAutocomplete('');
        };

        if (params.triggerObservable) {
          var triggerSub = params.triggerObservable.subscribe(function () {
            self.triggerAutocomplete(self.searchInput(), true);
          });
          self.disposals.push(function () {
            triggerSub.remove();
          })
        }

        var inputSub = self.searchInput.subscribe(function (newValue) {
          if (self.inlineAutocomplete().indexOf(newValue) !== 0 || newValue === '') {
            self.inlineAutocomplete(newValue);
          }
          if (newValue !== '') {
            self.triggerAutocomplete(newValue);
          }
        });

        self.disposals.push(function () {
          inputSub.remove();
        });

        var onKeyDown = function (event) {
          if (!self.hasFocus()) {
            return;
          }
          if (event.keyCode === 32 && event.ctrlKey) { // Ctrl-Space
            self.triggerAutocomplete(self.searchInput(), true);
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
            self.triggerAutocomplete(self.searchInput());
            $(document).on('keydown', onKeyDown);
          } else {
            $(document).on('keydown', onKeyDown);
          }
        });

        self.disposals.push(function () {
          focusSub.remove();
        });
      };

      InlineAutocomplete.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      InlineAutocomplete.prototype.updateInlineAutocomplete = function (partial) {
        var self = this;
        var newAutocomplete = '';
        var partialLower = partial.toLowerCase();
        if (self.lastResult.suggestFacets) {
          var existingFacetIndex = {};
          if (self.lastResult.facets) {
            Object.keys(self.lastResult.facets).forEach(function (facet) {
              existingFacetIndex[facet.toLowerCase()] = true;
            })
          }

          if (partial !== '') {
            var lowerCase = partial.length !== '' && partialLower[partialLower.length - 1] === partial[partial.length - 1];
            var suggestion = self.lastNonPartial + partial;
            self.facets.every(function (facet) {
              if (existingFacetIndex[facet]) {
                return true;
              }
              if (facet.indexOf(partialLower) === 0) {
                var remainder = facet.substring(partial.length);
                suggestion += lowerCase ? remainder : remainder.toUpperCase();
                suggestion += ':';
                newAutocomplete = suggestion;
                return false;
              }
              return true;
            });
          }
        }

        if (self.lastResult.suggestFacetValues && !newAutocomplete) {
          if (self.knownFacetValues()[self.lastResult.suggestFacetValues.toLowerCase()]) {
            Object.keys(self.knownFacetValues()[self.lastResult.suggestFacetValues.toLowerCase()]).every(function (value) {
              if (value.toLowerCase().indexOf(partialLower) === 0) {
                newAutocomplete = self.lastNonPartial + partial + value.substring(partial.length, value.length);
                return false;
              }
              return true;
            });
          }
        }

        if (partial !== '' && self.lastResult.suggestResults && !newAutocomplete) {
          newAutocomplete = self.autocompleteFromEntries(self.lastNonPartial, partial);
        }

        if (!newAutocomplete) {
          if (self.inlineAutocomplete() !== '') {
            self.inlineAutocomplete('');
          }
        } else if (newAutocomplete !== self.inlineAutocomplete()) {
          self.inlineAutocomplete(newAutocomplete);
        }
      };

      InlineAutocomplete.prototype.triggerAutocomplete = function (newValue, direct) {
        var self = this;
        var partial, nonPartial;
        var partialMatch = newValue.match(/([^:\s]+)$/i);
        if (partialMatch) {
          partial = partialMatch[0];
          nonPartial = newValue.substring(0, newValue.length - partial.length);
        } else {
          partial = '';
          nonPartial = newValue;
        }

        if (self.lastNonPartial && self.lastNonPartial === nonPartial) {
          self.updateInlineAutocomplete(partial);
          return;
        }

        window.clearTimeout(self.autocompleteThrottle);
        self.autocompleteThrottle = window.setTimeout(function () {
          self.lastNonPartial = nonPartial;

          // TODO: Get cursor position and split to before and after
          self.lastResult = globalSearchParser.parseGlobalSearch(newValue, '');
          if (hueDebug && hueDebug.showGlobalSearchParseResults) {
            console.log(self.lastResult);
          }
          if (self.lastResult) {
            var querySpec = { query: newValue };
            if (self.lastResult.facets) {
              querySpec.facets = self.lastResult.facets
            }
            if (self.lastResult.text) {
              querySpec.text = self.lastResult.text;
            }
            self.querySpec(querySpec);
            self.updateInlineAutocomplete(partial);
          } else {
            self.lastNonPartial = null;
          }
        }, direct ? 0 : 200);
      };

      ko.components.register('inline-autocomplete', {
        viewModel: InlineAutocomplete,
        template: {element: 'inline-autocomplete-template'}
      });
    })();
  </script>

  <script type="text/html" id="hue-global-search-template">
    <!-- ko component: {
      name: 'inline-autocomplete',
      params: {
        hasFocus: searchHasFocus,
        placeHolder: '${ _ko('Search data and saved documents...') }',
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
      <div class="global-search-alternatives" data-bind="foreach: searchResultCategories">
        <div class="global-search-category">
          <div class="global-search-category-header" data-bind="text: label"></div>
          <ul data-bind="foreach: result">
            <li data-bind="multiClick: {
                click: function () { $parents[1].resultSelected($parentContext.$index(), $index()) },
                dblClick: function () { $parents[1].resultSelected($parentContext.$index(), $index()); $parents[1].openResult(); }
              }, html: label, css: { 'selected': $parents[1].selectedResult() === $data }, draggableText: { text: draggable, meta: draggableMeta }"></li>
          </ul>
        </div>
      </div>
      <div class="global-search-preview" style="overflow: auto;">
        <!-- ko with: selectedResult -->
          <!-- ko switch: type -->
            <!-- ko case: ['database', 'document', 'field', 'table', 'view']  -->
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
          }
        });

        huePubSub.subscribe('context.popover.show.in.assist', function () {
          window.setTimeout(function () {
            if (self.searchResultVisible()) {
              self.close();
            }
          }, 0);
        });

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
        self.querySpec({});
      };

      GlobalSearch.prototype.openResult = function () {
        var self = this;
        var selectedResult = self.selectedResult();
        if (['database', 'table', 'field', 'view'].indexOf(selectedResult.type) !== -1) {
          huePubSub.publish('context.popover.show.in.assist');
        } else if (selectedResult.type === 'document') {
          huePubSub.publish('open.link', '/hue' + selectedResult.data.link);
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

      var CATEGORIES = {
        'table': '${ _('Tables') }',
        'database': '${ _('Databases') }',
        'field': '${ _('Columns') }',
        'partition': '${ _('Partitions') }',
        'view': '${ _('Views') }'
      };

      GlobalSearch.prototype.fetchResults = function (query) {
        var self = this;
        self.loading(true);
        self.searchResultVisible(true);
        var hueDocsPromise = self.apiHelper.fetchHueDocsInteractive(query);
        var navPromise = self.apiHelper.fetchNavEntitiesInteractive(query);
        hueDocsPromise.done(function (data) {
          var categories = self.searchResultCategories().filter(function (category) {
            return category.type !== 'documents';
          });
          var docCategory = {
            label: '${ _('Documents') }',
            result: [],
            type: 'documents'
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
            categories.unshift(docCategory);
          }
          self.selectedIndex(undefined);
          self.searchResultCategories(categories);
        });

        navPromise.done(function (data) {
          if (data.facets) {
            Object.keys(data.facets).forEach(function (facet) {
              if (!self.knownFacetValues()[facet] && Object.keys(data.facets[facet]).length > 0) {
                self.knownFacetValues()[facet] = {};
              }
              Object.keys(data.facets[facet]).forEach(function (facetKey) {
                self.knownFacetValues()[facet][facetKey] = data.facets[facet][facetKey];
              });
            })
          }
          var categories = self.searchResultCategories().length > 0 && self.searchResultCategories()[0].type === 'documents' ? [self.searchResultCategories()[0]] : [];
          var newCategories = {};
          data.results.forEach(function (result) {
            var typeLower = result.type.toLowerCase();
            if (CATEGORIES[typeLower]) {
              var category = newCategories[typeLower];
              if (!category) {
                category = {
                  label: CATEGORIES[typeLower],
                  result: []
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
          self.selectedIndex(undefined);
          self.searchResultCategories(categories);
        });

        $.when.apply($, [navPromise, hueDocsPromise]).always(function () {
          self.loading(false);
        })
      };

      ko.components.register('hue-global-search', {
        viewModel: GlobalSearch,
        template: {element: 'hue-global-search-template'}
      });
    })();
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
</%def>