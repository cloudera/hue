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
<%
import sys

from desktop.conf import CUSTOM, IS_K8S_ONLY
from desktop.views import commonheader, commonfooter
from desktop.webpack_utils import get_hue_bundles
from jobbrowser.conf import MAX_JOB_FETCH, ENABLE_QUERY_BROWSER

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

% if not is_embeddable:
${ commonheader("Job Browser", "jobbrowser", user, request) | n,unicode }
% endif

<span class="notebook">
  % if not is_embeddable:
  <link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
  <link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
  <style type="text/css">
  % if CUSTOM.BANNER_TOP_HTML.get():
    .show-assist {
      top: 110px!important;
    }
    .main-content {
      top: 112px!important;
    }
  % endif
  </style>
  % endif
  
  <link rel="stylesheet" href="${ static('jobbrowser/css/jobbrowser-embeddable.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-timepicker.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/bootstrap-spinedit.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/bootstrap-slider.css') }">
  
  <script src="${ static('desktop/ext/js/bootstrap-datepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/bootstrap-timepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/bootstrap-spinedit.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/bootstrap-slider.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('oozie/js/dashboard-utils.js') }" type="text/javascript" charset="utf-8"></script>
  
  % if ENABLE_QUERY_BROWSER.get():
  <script src="${ static('desktop/ext/js/dagre-d3-min.js') }"></script>
  <script src="${ static('jobbrowser/js/impala_dagre.js') }"></script>
  % endif
  
  <div id="jobbrowserMiniComponents" class="jobbrowser-components jobbrowser-mini jb-panel">
  
  % if not is_embeddable:
    <a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
      <i class="fa fa-chevron-right"></i>
    </a>
  % endif
  
    <div class="mini-jb-context-selector">
      <!-- ko component: {
        name: 'hue-context-selector',
        params: {
          connector: { id: 'impala' },
          compute: compute,
          ##namespace: namespace,
          ##availableDatabases: availableDatabases,
          ##database: database,
          hideDatabases: true
        }
      } --><!-- /ko -->
  
      % if not IS_K8S_ONLY.get():
      <!-- ko component: {
        name: 'hue-context-selector',
        params: {
          connector: { id: 'jobs' },
          cluster: cluster,
          onClusterSelect: onClusterSelect,
          hideLabels: true
        }
      } --><!-- /ko -->
      % endif
    </div>
    <ul class="nav nav-pills">
      <!-- ko foreach: availableInterfaces -->
        <li data-bind="css: {'active': $parent.interface() === interface}, visible: condition()">
          <a class="pointer" data-bind="click: function(){ $parent.selectInterface(interface); }, text: label"></a>
        </li>
      <!-- /ko -->
    </ul>

    <div class="main-content">
      <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
        <div class="vertical-full">
          <div class="vertical-full row-fluid panel-container">
            % if not is_embeddable:
            <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
              <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
                <i class="fa fa-chevron-left"></i>
              </a>
              <div class="assist" data-bind="component: {
                  name: 'assist-panel',
                  params: {
                    user: '${user.username}',
                    sql: {
                      navigationSettings: {
                        openItem: false,
                        showStats: true
                      }
                    },
                    visibleAssistPanels: ['sql']
                  }
                }"></div>
            </div>
            <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>
            % endif
  
            <div class="content-panel">
              <div class="content-panel-inner">
                <!-- ko if: $root.job() -->
                <div data-bind="template: { name: 'jb-breadcrumbs' }"></div>
                <!-- /ko -->
  
                <!-- ko if: interface() !== 'slas' && interface() !== 'oozie-info' && interface() !== 'hive-queries' && interface() !== 'impala-queries'-->
                <!-- ko if: !$root.job() -->
                <form class="form-inline">
                  <!-- ko if: interface() != 'dataware2-clusters' && interface() != 'engines' -->
                  <input type="text" class="input-large" data-bind="clearable: jobs.textFilter, valueUpdate: 'afterkeydown'" placeholder="${_('Filter by id, name, user...')}" />
                    <!-- ko if: jobs.statesValuesFilter -->
                    <span data-bind="foreach: jobs.statesValuesFilter">
                      <label class="checkbox">
                        <div class="pull-left margin-left-5 status-border status-content" data-bind="css: value, hueCheckbox: checked"></div>
                        <div class="inline-block" data-bind="text: name, toggle: checked"></div>
                      </label>
                    </span>
                    <!-- /ko -->
                  <!-- /ko -->
                </form>
  
                <div data-bind="visible: jobs.showJobCountBanner" class="pull-center alert alert-warning">
                  ${ _("Showing oldest %s jobs. Use days filter to get the recent ones.") % MAX_JOB_FETCH.get() }
                </div>
  
                <div class="card card-small">
                  <!-- ko hueSpinner: { spin: jobs.loadingJobs(), center: true, size: 'xlarge' } --><!-- /ko -->
                  <!-- ko ifnot: jobs.loadingJobs() -->
                    <ul class="unstyled status-border-container" id="jobsTable" data-bind="foreach: jobs.apps">
                      <li class="status-border pointer" data-bind="
                        css: {
                          'completed': apiStatus() == 'SUCCEEDED',
                          'info': apiStatus() === 'PAUSED',
                          'running': apiStatus() === 'RUNNING',
                          'failed': apiStatus() == 'FAILED'
                        },
                        click: function (data, event) {
                          onTableRowClick(event, id());
                        }">
                        <span class="muted pull-left" data-bind="momentFromNow: {data: submitted, interval: 10000, titleFormat: 'LLL'}"></span><span class="muted">&nbsp;-&nbsp;</span><span class="muted" data-bind="text: status"></span>
                        <span class="muted pull-right" data-bind="text: duration() ? duration().toHHMMSS() : ''"></span>
                        <div class="clearfix"></div>
                        <strong class="pull-left" data-bind="text: type"></strong>
                        <div class="inline-block pull-right"><i class="fa fa-user muted"></i> <span data-bind="text: user"></span></div>
                        <div class="clearfix"></div>
                        <div class="pull-left" data-bind="ellipsis: {data: name(), length: 40 }"></div>
                        <div class="pull-right muted" data-bind="ellipsis: {data: id(), length: 32 }"></div>
                        <div class="clearfix"></div>
                      </li>
                      <div class="status-bar status-background" data-bind="css: {'running': isRunning()}, style: {'width': progress() + '%'}"></div>
                    </ul>
                  <!-- /ko -->
                </div>
                <!-- /ko -->
  
                <!-- ko if: $root.job() -->
                <!-- ko with: $root.job() -->
                  <!-- ko if: mainType() == 'history' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-history-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'jobs' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-job-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'queries-impala' || mainType() == 'queries-hive' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-queries-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'celery-beat' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-celery-beat-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'schedule-hive' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-schedule-hive-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'workflows' -->
                    <!-- ko if: type() == 'workflow' -->
                      <div class="jb-panel" data-bind="template: { name: 'jb-workflow-page' }"></div>
                    <!-- /ko -->
  
                    <!-- ko if: type() == 'workflow-action' -->
                      <div class="jb-panel" data-bind="template: { name: 'jb-workflow-action-page' }"></div>
                    <!-- /ko -->
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'schedules' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-schedule-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'bundles' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-bundle-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType().startsWith('dataeng-job') -->
                    <div data-bind="template: { name: 'jb-dataeng-job-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'dataeng-clusters' || mainType() == 'dataware-clusters' -->
                    <div data-bind="template: { name: 'jb-dataware-clusters-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'dataware2-clusters' -->
                    <div data-bind="template: { name: 'jb-dataware2-clusters-page' }"></div>
                  <!-- /ko -->
  
                  <!-- ko if: mainType() == 'livy-sessions' -->
                    <div class="jb-panel" data-bind="template: { name: 'jb-livy-session-page' }"></div>
                  <!-- /ko -->
                <!-- /ko -->
                <!-- /ko -->
  
                <!-- ko if: $root.job() && !$root.job().forceUpdatingJob() && $root.job().hasPagination() && interface() === 'schedules' -->
                <div data-bind="template: { name: 'jb-pagination', data: $root.job() }, visible: !jobs.loadingJobs()"></div>
                <!-- /ko -->
                <div data-bind="template: { name: 'jb-pagination', data: $root.jobs }, visible: !$root.job() && !jobs.loadingJobs()"></div>
                <!-- /ko -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  
    <!-- ko if: $root.job() -->
      <div id="rerun-modal-mini" class="modal hide" data-bind="htmlUnsecure: $root.job().rerunModalContent"></div>
    <!-- /ko -->
  
    <!-- ko if: ($root.job() && $root.job().hasKill()) || (!$root.job() && $root.jobs.hasKill()) -->
      <div id="killModal-mini" class="modal hide">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
          <h2 class="modal-title">${_('Confirm Kill')}</h2>
        </div>
        <div class="modal-body">
          <p>${_('Are you sure you want to kill the selected job(s)?')}</p>
        </div>
        <div class="modal-footer">
          <a class="btn" data-dismiss="modal">${_('No')}</a>
          <a id="killJobBtn" class="btn btn-danger disable-feedback" data-dismiss="modal" data-bind="click: function(){ if (job()) { job().control('kill'); } else { jobs.control('kill'); } }">${_('Yes')}</a>
        </div>
      </div>
    <!-- /ko -->
  
    <!-- ko if: $root.job() && $root.job().type() === 'schedule' -->
      <div id="syncCoordinatorModal-mini" class="modal hide">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
          <h2 class="modal-title confirmation_header">${ _('Update Coordinator Job Properties') }</h2>
        </div>
        <div id="update-coord" class="span10">
          <div class="control-group">
            <label class="control-label">${ _('End Time') }</label>
            <div class="controls">
              <div class="input-prepend input-group">
                <span class="add-on input-group-addon">
                  <i class="fa fa-calendar"></i>
                </span>
                <input id="endTimeDateUI" type="text" class="input-small disable-autofocus" data-bind="value: $root.job().syncCoorEndTimeDateUI, datepicker: {}" />
              </div>
              <div class="input-prepend input-group">
                <span class="add-on input-group-addon">
                  <i class="fa fa-clock-o"></i>
                </span>
                <input id="endTimeTimeUI" type="text" class="input-mini disable-autofocus" data-bind="value: $root.job().syncCoorEndTimeTimeUI, timepicker: {}" />
              </div>
              <span class="help-inline"></span>
            </div>
          </div>
          <div class="control-group">
            <label class="control-label">${ _('Pause Time') }</label>
            <div class="controls">
              <div class="input-prepend input-group">
                <span class="add-on input-group-addon">
                  <i class="fa fa-calendar"></i>
                </span>
                <input id="pauseTimeDateUI" type="text" class="input-small disable-autofocus" data-bind="value: $root.job().syncCoorPauseTimeDateUI, datepicker: {}" />
              </div>
              <div class="input-prepend input-group">
                <span class="add-on input-group-addon">
                  <i class="fa fa-clock-o"></i>
                </span>
                <input id="pauseTimeTimeUI" type="text" class="input-mini disable-autofocus" data-bind="value: $root.job().syncCoorPauseTimeTimeUI, timepicker: {}" />
              </div>
              <span class="help-inline"></span>
            </div>
          </div>
          <div class="control-group ">
            <label class="control-label">Clear Pause Time</label>
            <div class="controls">
              <input id="id_clearPauseTime" class="disable-autofocus" name="clearPauseTime" type="checkbox">
            </div>
          </div>
          <div class="control-group ">
            <label class="control-label">Concurrency</label>
            <div class="controls">
              <input id="id_concurrency" class="disable-autofocus" name="concurrency" type="number" data-bind="value: $root.job().syncCoorConcurrency">
            </div>
          </div>
        </div>
        <div class="modal-body">
            <p class="confirmation_body"></p>
        </div>
        <div class="modal-footer update">
          <a href="#" class="btn" data-dismiss="modal">Cancel</a>
          <a id="syncCoorBtn" class="btn btn-danger disable-feedback" data-dismiss="modal" data-bind="click: function(){ job().control('sync_coordinator'); }">${_('Update')}</a>
        </div>
      </div>
  
      <div id="syncWorkflowModal-mini" class="modal hide"></div>
    <!-- /ko -->
  </div>
</span>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif