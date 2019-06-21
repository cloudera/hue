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
from django.utils.translation import ugettext as _

from desktop.conf import CUSTOM, IS_K8S_ONLY
from desktop.views import commonheader, commonfooter, _ko
from metadata.conf import PROMETHEUS

from jobbrowser.conf import DISABLE_KILLING_JOBS, MAX_JOB_FETCH, ENABLE_QUERY_BROWSER
%>

<%
SUFFIX = is_mini and "-mini" or ""
%>

% if not is_embeddable:
${ commonheader("Job Browser", "jobbrowser", user, request) | n,unicode }
<%namespace name="assist" file="/assist.mako" />
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

<script src="${ static('oozie/js/dashboard-utils.js') }" type="text/javascript" charset="utf-8"></script>

% if ENABLE_QUERY_BROWSER.get():
<script src="${ static('desktop/ext/js/dagre-d3-min.js') }"></script>
<script src="${ static('jobbrowser/js/impala_dagre.js') }"></script>
% endif

% if not is_mini:
<div id="jobbrowserComponents" class="jobbrowser-components jobbrowser-full jb-panel">
% else:
<div id="jobbrowserMiniComponents" class="jobbrowser-components jobbrowser-mini jb-panel">
% endif

% if not is_embeddable:
  ${ assist.assistJSModels() }
  ${ assist.assistPanel() }

  <a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
    <i class="fa fa-chevron-right"></i>
  </a>
% endif


% if is_mini:
  <div class="mini-jb-context-selector">
    <!-- ko component: {
      name: 'hue-context-selector',
      params: {
        sourceType: 'impala',
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
        sourceType: 'jobs',
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
% else:
  <div class="navbar hue-title-bar">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              % if IS_K8S_ONLY.get():
                <a data-bind="click: function() { selectInterface('dataware2-clusters'); }">
                  <i class="altus-icon altus-adb-cluster"></i>
                  ${ _('Warehouses') }
                </a>
              % else:
              <!-- ko ifnot: $root.cluster() && $root.cluster()['type'].indexOf("altus-dw") !== -1 -->
              <a href="/${app_name}">
                <img src="${ static('jobbrowser/art/icon_jobbrowser_48.png') }" class="app-icon" alt="${ _('Job browser icon') }"/>
                <!-- ko if: !$root.cluster() || $root.cluster()['type'].indexOf("altus") == -1 -->
                  ${ _('Job Browser') }
                <!-- /ko -->
                <!-- ko if: $root.cluster() && $root.cluster()['type'].indexOf("altus-engines") !== -1 -->
                  ${ _('Clusters') }
                <!-- /ko -->
                <!-- ko if: $root.cluster() && $root.cluster()['type'].indexOf("altus-de") !== -1 -->
                  ${ _('Data Engineering') }
                <!-- /ko -->
              </a>
              <!-- /ko -->
              <!-- ko if: $root.cluster() && $root.cluster()['type'].indexOf("altus-dw") !== -1 -->
                <span>
                  <a data-bind="click: function() { huePubSub.publish('context.selector.set.cluster', 'engines'); }">
                    <img src="${ static('jobbrowser/art/icon_jobbrowser_48.png') }" class="app-icon" alt="${ _('Job browser icon') }"/>
                    ${ _('Clusters') }
                  </a>
                  > gke_gcp-eng-dsdw_us-west2-b_impala-demo
                </span>
              <!-- /ko -->
              % endif
            </li>
            <!-- ko foreach: availableInterfaces -->
              <li data-bind="css: {'active': $parent.interface() === interface}, visible: condition()">
                <a class="pointer" data-bind="click: function(){ $parent.selectInterface(interface); }, text: label, visible: label"></a>
              </li>
            <!-- /ko -->
          </ul>
          <div class="pull-right" style="padding-top: 15px">
            <!-- ko component: {
              name: 'hue-context-selector',
              params: {
                sourceType: 'jobs',
                cluster: cluster,
                onClusterSelect: onClusterSelect
              }
            } --><!-- /ko -->
          </div>
          % if not hiveserver2_impersonation_enabled:
            <div class="pull-right label label-warning" style="margin-top: 16px">${ _("Hive jobs are running as the 'hive' user") }</div>
          % endif
        </div>
      </div>
    </div>
  </div>
% endif


  <script type="text/html" id="apps-list${ SUFFIX }">
    <table data-bind="attr: {id: tableId}" class="datatables table table-condensed status-border-container">
      <thead>
      <tr>
        <th width="1%" class="vertical-align-middle">
          <div class="select-all hue-checkbox fa" data-bind="hueCheckAll: { allValues: apps, selectedValues: selectedJobs }"></div>
        </th>
        <th width="20%">${_('Name')}</th>
        <th width="6%">${_('User')}</th>
        <th width="6%">${_('Type')}</th>
        <th width="5%">${_('Status')}</th>
        <th width="3%">${_('Progress')}</th>
        <th width="5%">${_('Group')}</th>
        <th width="10%" data-bind="text: $root.interface() != 'schedules' ? '${_('Started')}' : '${_('Modified')}'"></th>
        <th width="6%">${_('Duration')}</th>
        <th width="15%">${_('Id')}</th>
      </tr>
      </thead>
      <tbody data-bind="foreach: apps">
        <tr class="status-border pointer" data-bind="css: {'completed': apiStatus() == 'SUCCEEDED', 'info': apiStatus() == 'PAUSED', 'running': apiStatus() == 'RUNNING', 'failed': apiStatus() == 'FAILED'}, click: fetchJob">
          <td data-bind="click: function() {}, clickBubble: false">
            <div class="hue-checkbox fa" data-bind="click: function() {}, clickBubble: false, multiCheck: '#' + $parent.tableId, value: $data, hueChecked: $parent.selectedJobs"></div>
          </td>
          <td data-bind="text: name"></td>
          <td data-bind="text: user"></td>
          <td data-bind="text: type"></td>
          <td data-bind="text: status"></td>
          <td data-bind="text: $root.formatProgress(progress)"></td>
          <td data-bind="text: queue"></td>
          <td data-bind="moment: {data: submitted, format: 'LLL'}"></td>
          <td data-bind="text: duration().toHHMMSS()"></td>
          <td data-bind="text: id"></td>
        </tr>
      </tbody>
    </table>
  </script>

  <script type="text/html" id="create-cluster-content">
    <form>
      <fieldset>
        <label for="clusterCreateName">${ _('Name') }</label>
        <input id="clusterCreateName" type="text" placeholder="${ _('Name') }" data-bind="clearable: jobs.createClusterName, valueUpdate: 'afterkeydown'">

        <!-- ko if: $root.interface() == 'dataware2-clusters' -->
        <label for="clusterCreateWorkers">${ _('Workers') }</label>
        <input id="clusterCreateWorkers" type="number" min="1" data-bind="value: jobs.createClusterWorkers, valueUpdate: 'afterkeydown'" class="input-mini" placeholder="${_('Size')}">
        <label class="checkbox" style="float: right;">
          <input type="checkbox" data-bind="checked: jobs.createClusterAutoPause"> ${ _('Auto pause') }
        </label>
        <label class="checkbox" style="margin-right: 10px; float: right;">
          <input type="checkbox" data-bind="checked: jobs.createClusterAutoResize"> ${ _('Auto resize') }
        </label>
        <!-- /ko -->
        <!-- ko if: $root.cluster() && $root.cluster()['type'] == 'altus-engines' -->
        <label for="clusterCreateSize">${ _('Size') }</label>
        <select id="clusterCreateSize" class="input-small" data-bind="visible: !jobs.createClusterShowWorkers()">
          <option>${ _('X-Large') }</option>
          <option>${ _('Large') }</option>
          <option>${ _('Medium') }</option>
          <option>${ _('Small') }</option>
          <option>${ _('X-Small') }</option>
        </select>
        <label for="clusterCreateEnvironment">${ _('Environment') }</label>
        <select id="clusterCreateEnvironment">
          <option>AWS-finance-secure</option>
          <option>GCE-east</option>
          <option>OpenShift-prem</option>
        </select>
        <!-- /ko -->
      </fieldset>
    </form>
    <div style="width: 100%; text-align: right;">
      <button class="btn close-template-popover" title="${ _('Cancel') }">${ _('Cancel') }</button>
      <button class="btn btn-primary close-template-popover" data-bind="click: jobs.createCluster, enable: jobs.createClusterName().length > 0 && jobs.createClusterWorkers() > 0" title="${ _('Start creation') }">
        ${ _('Create') }
      </button>
    </div>
  </script>

  <script type="text/html" id="configure-cluster-content">
    <form>
      <fieldset>
        <label for="clusterConfigureWorkers">${ _('Workers') }</label>
        <span data-bind="visible: !updateClusterAutoResize()">
          <input id="clusterConfigureWorkers" type="number" min="1" data-bind="value: updateClusterWorkers, valueUpdate: 'afterkeydown'" class="input-mini" placeholder="${_('Size')}">
        </span>
        <span data-bind="visible: updateClusterAutoResize()">
          <input type="number" min="0" data-bind="value: updateClusterAutoResizeMin, valueUpdate: 'afterkeydown'" class="input-mini" placeholder="${_('Min')}">
          <input type="number" min="0" data-bind="value: updateClusterAutoResizeMax, valueUpdate: 'afterkeydown'" class="input-mini" placeholder="${_('Max')}">
          <input type="number" min="0" data-bind="value: updateClusterAutoResizeCpu, valueUpdate: 'afterkeydown'" class="input-mini" placeholder="${_('CPU')}">
        </span>

        <label class="checkbox" style="margin-right: 10px; float: right;">
          <input type="checkbox" data-bind="checked: updateClusterAutoResize"> ${ _('Auto resize') }
        </label>
      </fieldset>
    </form>
    <div style="width: 100%; text-align: right;">
      <button class="btn close-template-popover" title="${ _('Cancel') }">${ _('Cancel') }</button>
      <button class="btn btn-primary close-template-popover" data-bind="click: updateCluster, enable: clusterConfigModified" title="${ _('Update') }">
        ${ _('Update') }
      </button>
    </div>
  </script>

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
              <div data-bind="template: { name: 'breadcrumbs${ SUFFIX }' }"></div>
              <!-- /ko -->

              <!-- ko if: interface() !== 'slas' && interface() !== 'oozie-info' -->
              <!-- ko if: !$root.job() -->
              <form class="form-inline">
                <!-- ko if: !$root.isMini() && interface() == 'queries' -->
                  ${ _('Impala queries from') }
                <!-- /ko -->
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

                <!-- ko ifnot: $root.isMini -->
                <!-- ko if: $root.interface() !== 'schedules' && $root.interface() !== 'bundles' -->

                  <!-- ko if: $root.interface() && $root.interface().indexOf('engines') === -1 && $root.interface().indexOf('cluster') === -1 -->
                  ${_('in the last')} <input class="input-mini no-margin" type="number" min="1" max="3650" data-bind="value: jobs.timeValueFilter">
                  <select class="input-small no-margin" data-bind="value: jobs.timeUnitFilter, options: jobs.timeUnitFilterUnits, optionsText: 'name', optionsValue: 'value'">
                    <option value="days">${_('days')}</option>
                    <option value="hours">${_('hours')}</option>
                    <option value="minutes">${_('minutes')}</option>
                  </select>

                  <a class="btn" title="${ _('Refresh') }" data-bind="click: jobs.updateJobs">
                    <i class="fa fa-refresh"></i>
                  </a>
                  <!-- /ko -->

                  <a class="btn" title="${ _('Create cluster') }" data-bind="visible: $root.interface() == 'dataware2-clusters', templatePopover : { placement: 'bottom', contentTemplate: 'create-cluster-content', minWidth: '320px', trigger: 'click' }, click: jobs.createClusterFormReset">
                    <!-- ko if: $root.cluster() && $root.cluster()['type'] != 'altus-engines' -->
                      ${ _('Add Warehouse') }
                    <!-- /ko -->
                    <!-- ko if: $root.cluster() && $root.cluster()['type'] == 'altus-engines' -->
                      ${ _('Create / Register') }
                    <!-- /ko -->
                    <i class="fa fa-chevron-down"></i>
                  </a>
                <!-- /ko -->

                <div data-bind="template: { name: 'job-actions${ SUFFIX }', 'data': jobs }" class="pull-right"></div>
                <!-- /ko -->
              </form>

              <div data-bind="visible: jobs.showJobCountBanner" class="pull-center alert alert-warning">${ _("Showing oldest %s jobs. Use days filter to get the recent ones.") % MAX_JOB_FETCH.get() }</div>

              <div class="card card-small">
                <!-- ko hueSpinner: { spin: jobs.loadingJobs(), center: true, size: 'xlarge' } --><!-- /ko -->
                <!-- ko ifnot: jobs.loadingJobs() -->
                  <!-- ko if: $root.isMini -->
                  <ul class="unstyled status-border-container" id="jobsTable" data-bind="foreach: jobs.apps">
                    <li class="status-border pointer" data-bind="css: {'completed': apiStatus() == 'SUCCEEDED', 'info': apiStatus() === 'PAUSED', 'running': apiStatus() === 'RUNNING', 'failed': apiStatus() == 'FAILED'}, click: fetchJob">
                      <span class="muted pull-left" data-bind="momentFromNow: {data: submitted, interval: 10000, titleFormat: 'LLL'}"></span><span class="muted">&nbsp;-&nbsp;</span><span class="muted" data-bind="text: status"></span></td>
                      <span class="muted pull-right" data-bind="text: duration().toHHMMSS()"></span>
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
                  <!-- ko ifnot: $root.isMini -->
                  <h4>${ _('Running') }</h4>
                  <div data-bind="template: { name: 'apps-list${ SUFFIX }', data: { apps: jobs.runningApps, tableId: 'runningJobsTable', selectedJobs: jobs.selectedJobs} }"></div>
                  <h4>${ _('Completed') }</h4>
                  <div data-bind="template: { name: 'apps-list${ SUFFIX }', data: { apps: jobs.finishedApps, tableId: 'completedJobsTable', selectedJobs: jobs.selectedJobs } }"></div>
                  <!-- /ko -->
                <!-- /ko -->
              </div>
              <!-- /ko -->

              <!-- ko if: $root.job() -->
              <!-- ko with: $root.job() -->
                <!-- ko if: mainType() == 'jobs' -->
                  <div class="jb-panel" data-bind="template: { name: 'job-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType() == 'queries' -->
                  <div class="jb-panel" data-bind="template: { name: 'queries-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType() == 'workflows' -->
                  <!-- ko if: type() == 'workflow' -->
                    <div class="jb-panel" data-bind="template: { name: 'workflow-page${ SUFFIX }' }"></div>
                  <!-- /ko -->

                  <!-- ko if: type() == 'workflow-action' -->
                    <div class="jb-panel" data-bind="template: { name: 'workflow-action-page${ SUFFIX }' }"></div>
                  <!-- /ko -->
                <!-- /ko -->

                <!-- ko if: mainType() == 'schedules' -->
                  <div class="jb-panel" data-bind="template: { name: 'schedule-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType() == 'bundles' -->
                  <div class="jb-panel" data-bind="template: { name: 'bundle-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType().startsWith('dataeng-job') -->
                  <div data-bind="template: { name: 'dataeng-job-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType() == 'dataeng-clusters' || mainType() == 'dataware-clusters' -->
                  <div data-bind="template: { name: 'dataware-clusters-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType() == 'dataware2-clusters' -->
                  <div data-bind="template: { name: 'dataware2-clusters-page${ SUFFIX }' }"></div>
                <!-- /ko -->

                <!-- ko if: mainType() == 'livy-sessions' -->
                  <div class="jb-panel" data-bind="template: { name: 'livy-session-page${ SUFFIX }' }"></div>
                <!-- /ko -->
              <!-- /ko -->
              <!-- /ko -->

              <div data-bind="template: { name: 'pagination${ SUFFIX }', data: $root.jobs }, visible: !$root.job() && !jobs.loadingJobs()"></div>
              <!-- /ko -->

              % if not is_mini:
              <!-- ko if: interface() === 'slas' -->
                <!-- ko hueSpinner: { spin: slasLoading(), center: true, size: 'xlarge' } --><!-- /ko -->
              <!-- /ko -->
              <div id="slas" data-bind="visible: interface() === 'slas'"></div>

              <!-- ko if: interface() === 'oozie-info' -->
                <!-- ko hueSpinner: { spin: oozieInfoLoading(), center: true, size: 'xlarge' } --><!-- /ko -->
              <!-- /ko -->
              <div id="oozieInfo" data-bind="visible: interface() === 'oozie-info'"></div>
              %endif
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ko if: $root.job() -->
    <div id="rerun-modal${ SUFFIX }" class="modal hide" data-bind="htmlUnsecure: $root.job().rerunModalContent"></div>
  <!-- /ko -->

  <!-- ko if: ($root.job() && $root.job().hasKill()) || (!$root.job() && $root.jobs.hasKill()) -->
    <div id="killModal${ SUFFIX }" class="modal hide">
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
</div>


<script type="text/html" id="breadcrumbs-icons${ SUFFIX }">
<!-- ko switch: type -->
  <!-- ko case: 'workflow' -->
    <img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/>
  <!-- /ko -->
  <!-- ko case: 'workflow-action' -->
    <i class="fa fa-fw fa-code-fork"></i>
  <!-- /ko -->
  <!-- ko case: 'schedule' -->
    <img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }"/>
  <!-- /ko -->
  <!-- ko case: 'bundle' -->
    <img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }"/>
  <!-- /ko -->
<!-- /ko -->
</script>


<script type="text/html" id="breadcrumbs${ SUFFIX }">
  <h3 class="jb-breadcrumbs">
    <ul class="inline hue-breadcrumbs-bar">
      <!-- ko foreach: breadcrumbs -->
        <li>
        <!-- ko if: $index() > 1 -->
          <span class="divider">&gt;</span>
        <!-- /ko -->

        <!-- ko if: $index() != 0 -->
          <!-- ko if: $index() != $parent.breadcrumbs().length - 1 -->
            <a href="javascript:void(0)" data-bind="click: function() { $parent.breadcrumbs.splice($index()); $root.job().id(id); $root.job().fetchJob(); }">
            <span data-bind="template: 'breadcrumbs-icons${ SUFFIX }'"></span>
            <span data-bind="text: name"></span></a>
          <!-- /ko -->
          <!-- ko if: $index() == $parent.breadcrumbs().length - 1 -->
            <span data-bind="template: 'breadcrumbs-icons${ SUFFIX }'"></span>
            <span data-bind="text: name, attr: { title: id }"></span>
          <!-- /ko -->
        <!-- /ko -->
        </li>
      <!-- /ko -->

      <!-- ko if: !$root.isMini() -->
        <!-- ko if: ['workflows', 'schedules', 'bundles', 'slas'].indexOf(interface()) > -1 -->
        <li class="pull-right">
          <a href="javascript:void(0)" data-bind="click: function() { $root.selectInterface('oozie-info') }">${ _('Configuration') }</a>
        </li>
        <!-- /ko -->
      <!-- /ko -->
    </ul>
  </h3>
</script>


<script type="text/html" id="pagination${ SUFFIX }">
  <!-- ko ifnot: hasPagination -->
  <div class="inline">
    <span data-bind="text: totalApps()"></span>
    <!-- ko if: $root.interface() === 'dataware2-clusters' -->
    ${ _('warehouses') }
    <!-- /ko -->
    <!-- ko if: $root.interface() !== 'dataware2-clusters' -->
    ${ _('jobs') }
    <!-- /ko -->
  </div>
  <!-- /ko -->

  <!-- ko if: hasPagination -->
  <div class="inline">
    <div class="inline">
      ${ _('Showing') }
      <span data-bind="text: Math.min(paginationOffset(), totalApps())"></span>
      ${ _('to')}
      <span data-bind="text: Math.min(paginationOffset() - 1 + paginationResultPage(), totalApps())"></span>
      ${ _('of') }
      <span data-bind="text: totalApps"></span>

      ##${ _('Show')}
      ##<span data-bind="text: paginationResultPage"></span>
      ##${ _('results by page.') }
    </div>

    <ul class="inline">
      <li class="previous-page" data-bind="visible: showPreviousPage">
        <a href="javascript:void(0);" data-bind="click: previousPage" title="${_('Previous page')}"><i class="fa fa-backward"></i></a>
      </li>
      <li class="next-page" data-bind="visible: showNextPage">
        <a href="javascript:void(0);" data-bind="click: nextPage" title="${_('Next page')}"><i class="fa fa-forward"></i></a>
      </li>
    </ul>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="job-page${ SUFFIX }">
  <!-- ko if: type() == 'MAPREDUCE' -->
    <div data-bind="template: { name: 'job-mapreduce-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'MAP' || type() == 'REDUCE' -->
    <div data-bind="template: { name: 'job-mapreduce-task-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'MAP_ATTEMPT' || type() == 'REDUCE_ATTEMPT' -->
    <div data-bind="template: { name: 'job-mapreduce-task-attempt-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YARN' -->
    <div data-bind="template: { name: 'job-yarn-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YarnV2' -->
    <div data-bind="template: { name: 'job-yarnv2-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YarnV2_ATTEMPT' -->
    <div data-bind="template: { name: 'job-yarnv2-attempt-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'SPARK' -->
    <div data-bind="template: { name: 'job-spark-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'SPARK_EXECUTOR' -->
    <div data-bind="template: { name: 'job-spark-executor-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

</script>

<script type="text/html" id="job-yarn-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration().toHHMMSS()"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <div class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></div>
    </div>
  </div>
</script>


<script type="text/html" id="job-mapreduce-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini()}">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <li data-bind="visible: id() != name() && ! $root.isMini()" class="nav-header">${ _('Name') }</li>
          <li data-bind="visible: id() != name() && ! $root.isMini(), attr: {title: name}"><span data-bind="text: name"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li data-bind="visible: ! $root.isMini()" class="nav-header">${ _('Status') }</li>
          <li data-bind="visible: ! $root.isMini()"><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}, attr: {title: status}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko if: !$root.isMini() -->
          <!-- ko with: properties -->
            <li class="nav-header">${ _('Map') }</li>
            <li><span data-bind="text: maps_percent_complete"></span>% <span data-bind="text: finishedMaps"></span> /<span data-bind="text: desiredMaps"></span></li>
            <li class="nav-header">${ _('Reduce') }</li>
            <li><span data-bind="text: reduces_percent_complete"></span>% <span data-bind="text: finishedReduces"></span> / <span data-bind="text: desiredReduces"></span></li>
            <li class="nav-header">${ _('Duration') }</li>
            <li><span data-bind="text: durationFormatted"></span></li>
            <li class="nav-header">${ _('Submitted') }</li>
            <li><span data-bind="text: startTimeFormatted"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" href="#job-mapreduce-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#job-mapreduce-page-tasks${ SUFFIX }" data-bind="click: function(){ fetchProfile('tasks'); $('a[href=\'#job-mapreduce-page-tasks${ SUFFIX }\']').tab('show'); }">${ _('Tasks') }</a></li>
        <li><a href="#job-mapreduce-page-metadata${ SUFFIX }" data-bind="click: function(){ fetchProfile('metadata'); $('a[href=\'#job-mapreduce-page-metadata${ SUFFIX }\']').tab('show'); }">${ _('Metadata') }</a></li>
        <li><a href="#job-mapreduce-page-counters${ SUFFIX }" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-page-counters${ SUFFIX }\']').tab('show'); }">${ _('Counters') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" id="job-mapreduce-page-logs${ SUFFIX }">
          <ul class="nav nav-tabs">
          % for name in ['default', 'stdout', 'stderr', 'syslog']:
            <li class="${ name == 'default' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); logActive('${ name }'); }, text: '${ name }'"></a></li>
          % endfor
          </ul>
          <!-- ko if: properties.diagnostics() -->
            <pre data-bind="text: properties.diagnostics"></pre>
          <!-- /ko -->
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" id="job-mapreduce-page-tasks${ SUFFIX }">
          <form class="form-inline">
            <input data-bind="textFilter: textFilter, clearable: {value: textFilter}, valueUpdate: 'afterkeydown'" type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">

            <span data-bind="foreach: statesValuesFilter">
              <label class="checkbox">
                <div class="pull-left margin-left-5 status-border status-content" data-bind="css: value, hueCheckbox: checked"></div>
                <div class="inline-block" data-bind="text: name, toggle: checked"></div>
              </label>
            </span>

            <span data-bind="foreach: typesValuesFilter" class="margin-left-30">
              <label class="checkbox">
                <div class="pull-left margin-left-5" data-bind="css: value, hueCheckbox: checked"></div>
                <div class="inline-block" data-bind="text: name, toggle: checked"></div>
              </label>
            </span>
          </form>

          <table class="table table-condensed">
            <thead>
            <tr>
              <th>${_('Type')}</th>
              <th>${_('Id')}</th>
              <th>${_('Elapsed Time')}</th>
              <th>${_('Progress')}</th>
              <th>${_('State')}</th>
              <th>${_('Start Time')}</th>
              <th>${_('Successful Attempt')}</th>
              <th>${_('Finish Time')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['tasks']()['task_list']">
              <tr data-bind="click: function() { $root.job().id(id); $root.job().fetchJob(); }, css: {'completed': apiStatus == 'SUCCEEDED', 'running': apiStatus == 'RUNNING', 'failed': apiStatus == 'FAILED'}" class="status-border pointer">
                <td data-bind="text: type"></td>
                <td data-bind="text: id"></td>
                <td data-bind="text: elapsedTime.toHHMMSS()"></td>
                <td data-bind="text: progress"></td>
                <td data-bind="text: state"></td>
                <td data-bind="moment: {data: startTime, format: 'LLL'}"></td>
                <td data-bind="text: successfulAttempt"></td>
                <td data-bind="moment: {data: finishTime, format: 'LLL'}"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="job-mapreduce-page-metadata${ SUFFIX }">
          <div data-bind="template: { name: 'render-metadata${ SUFFIX }', data: properties['metadata'] }"></div>
        </div>

        <div class="tab-pane" id="job-mapreduce-page-counters${ SUFFIX }">
          <div data-bind="template: { name: 'render-page-counters${ SUFFIX }', data: properties['counters'] }"></div>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="job-mapreduce-task-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}, attr: {title: status}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko if: !$root.isMini() -->
          <!-- ko with: properties -->
            <li data-bind="visible: ! $root.isMini()" class="nav-header">${ _('State') }</li>
            <li data-bind="visible: ! $root.isMini()"><span data-bind="text: state"></span></li>
            <li class="nav-header">${ _('Start time') }</li>
            <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
            <li class="nav-header">${ _('Successful attempt') }</li>
            <li><span data-bind="text: successfulAttempt"></span></li>
            <li class="nav-header">${ _('Finish time') }</li>
            <li><span data-bind="moment: {data: finishTime, format: 'LLL'}"></span></li>
            <li class="nav-header">${ _('Elapsed time') }</li>
            <li><span data-bind="text: elapsedTime().toHHMMSS()"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" href="#job-mapreduce-task-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#job-mapreduce-task-page-attempts${ SUFFIX }" data-bind="click: function(){ fetchProfile('attempts'); $('a[href=\'#job-mapreduce-task-page-attempts${ SUFFIX }\']').tab('show'); }">${ _('Attempts') }</a></li>
        <li><a href="#job-mapreduce-task-page-counters${ SUFFIX }" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-task-page-counters${ SUFFIX }\']').tab('show'); }">${ _('Counters') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="job-mapreduce-task-page-logs${ SUFFIX }">
          <ul class="nav nav-tabs">
          % for name in ['stdout', 'stderr', 'syslog']:
            <li class="${ name == 'stdout' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); logActive('${ name }'); }, text: '${ name }'"></a></li>
          % endfor
          </ul>

          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" id="job-mapreduce-task-page-attempts${ SUFFIX }">

          <table class="table table-condensed">
            <thead>
            <tr>
              <th>${_('Assigned Container Id')}</th>
              <th>${_('Progress')}</th>
              <th>${_('Elapsed Time')}</th>
              <th>${_('State')}</th>
              <th>${_('Rack')}</th>
              <th>${_('Node Http Address')}</th>
              <th>${_('Type')}</th>
              <th>${_('Start Time')}</th>
              <th>${_('Id')}</th>
              <th>${_('Finish Time')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['attempts']()['task_list']">
              <tr class="pointer" data-bind="click: function() { $root.job().id(id); $root.job().fetchJob(); }">
                <td data-bind="text: assignedContainerId"></td>
                <td data-bind="text: progress"></td>
                <td data-bind="text: elapsedTime.toHHMMSS()"></td>
                <td data-bind="text: state"></td>
                <td data-bind="text: rack"></td>
                <td data-bind="text: nodeHttpAddress"></td>
                <td data-bind="text: type"></td>
                <td data-bind="moment: {data: startTime, format: 'LLL'}"></td>
                <td data-bind="text: id"></td>
                <td data-bind="moment: {data: finishTime, format: 'LLL'}"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="job-mapreduce-task-page-counters${ SUFFIX }">
          <div data-bind="template: { name: 'render-task-counters${ SUFFIX }', data: properties['counters'] }"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="job-yarnv2-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: applicationType"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() == 'RUNNING', 'progress-success': apiStatus() == 'SUCCEEDED', 'progress-danger': apiStatus() == 'FAILED'}, attr: {title: status}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko if: !$root.isMini() -->
          <li class="nav-header">${ _('State') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- ko with: properties -->
            <li class="nav-header">${ _('Start time') }</li>
            <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
            <li class="nav-header">${ _('Finish time') }</li>
            <li><span data-bind="moment: {data: finishTime, format: 'LLL'}"></span></li>
            <li class="nav-header">${ _('Elapsed time') }</li>
            <li><span data-bind="text: elapsedTime().toHHMMSS()"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" href="#job-yarnv2-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#job-yarnv2-page-attempts${ SUFFIX }" data-bind="click: function(){ fetchProfile('attempts'); $('a[href=\'#job-yarnv2-page-attempts${ SUFFIX }\']').tab('show'); }">${ _('Attempts') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="job-yarnv2-page-logs${ SUFFIX }">
          <ul class="nav nav-tabs scrollable" data-bind="foreach: logsList">
            <li data-bind="css: { 'active': $data == $parent.logActive() }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $parent.fetchLogs($data); $parent.logActive($data); }, text: $data"></a></li>
          </ul>
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" id="job-yarnv2-page-attempts${ SUFFIX }">
          <table class="table table-condensed">
            <thead>
            <tr>
              <th>${_('Assigned Container Id')}</th>
              <th>${_('Node Id')}</th>
              <th>${_('Application Attempt Id')}</th>
              <th>${_('Start Time')}</th>
              <th>${_('Finish Time')}</th>
              <th>${_('Node Http Address')}</th>
              <th>${_('Blacklisted Nodes')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['attempts']()['task_list']">
              <tr class="pointer" data-bind="click: function() { $root.job().id(appAttemptId); $root.job().fetchJob(); }">
                <td data-bind="text: containerId"></td>
                <td data-bind="text: nodeId"></td>
                <td data-bind="text: id"></td>
                <td data-bind="moment: {data: startTime, format: 'LLL'}"></td>
                <td data-bind="moment: {data: finishedTime, format: 'LLL'}"></td>
                <td data-bind="text: nodeHttpAddress"></td>
                <td data-bind="text: blacklistedNodes"></td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

    </div>
  </div>
</script>

<script type="text/html" id="job-yarnv2-attempt-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko with: properties -->
          <li class="nav-header">${ _('Attempt Id') }</li>
          <li class="break-word"><span data-bind="text: appAttemptId"></span></li>
          <li class="nav-header">${ _('State') }</li>
          <li><span data-bind="text: state"></span></li>
          <!-- ko if: !$root.isMini() -->
          <li class="nav-header">${ _('Start time') }</li>
          <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
          <li class="nav-header">${ _('Node Http Address') }</li>
          <li><span data-bind="text: nodeHttpAddress"></span></li>
          <li class="nav-header">${ _('Elapsed time') }</li>
          <li><span data-bind="text: duration().toHHMMSS()"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>
    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">
    </div>
  </div>
</script>

<script type="text/html" id="job-mapreduce-task-attempt-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() == 'RUNNING', 'progress-success': apiStatus() == 'SUCCEEDED', 'progress-danger': apiStatus() == 'FAILED'}, attr: {title: status}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko if: !$root.isMini() -->
          <!-- ko with: properties -->
            <li class="nav-header">${ _('State') }</li>
            <li><span data-bind="text: state"></span></li>
            <li class="nav-header">${ _('Assigned Container ID') }</li>
            <li><span data-bind="text: assignedContainerId"></span></li>
            <li class="nav-header">${ _('Rack') }</li>
            <li><span data-bind="text: rack"></span></li>
            <li class="nav-header">${ _('Node HTTP address') }</li>
            <li><span data-bind="text: nodeHttpAddress"></span></li>
            <li class="nav-header">${ _('Start time') }</li>
            <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
            <li class="nav-header">${ _('Finish time') }</li>
            <li><span data-bind="moment: {data: finishTime, format: 'LLL'}"></span></li>
            <li class="nav-header">${ _('Elapsed time') }</li>
            <li><span data-bind="text: elapsedTime().toHHMMSS()"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" href="#job-mapreduce-task-attempt-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#job-mapreduce-task-attempt-page-counters${ SUFFIX }" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-task-attempt-page-counters${ SUFFIX }\']').tab('show'); }">${ _('Counters') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="job-mapreduce-task-attempt-page-logs${ SUFFIX }">
          <ul class="nav nav-tabs">
          % for name in ['stdout', 'stderr', 'syslog']:
            <li class="${ name == 'stdout' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); logActive('${ name }'); }, text: '${ name }'"></a></li>
          % endfor
          </ul>
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" id="job-mapreduce-task-attempt-page-counters${ SUFFIX }">
          <div data-bind="template: { name: 'render-attempt-counters${ SUFFIX }', data: properties['counters'] }"></div>
        </div>
      </div>

    </div>
  </div>
</script>

<script type="text/html" id="job-spark-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko if: !$root.isMini() -->
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration().toHHMMSS()"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="job-spark-logs-link" href="#job-spark-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#job-spark-page-executors${ SUFFIX }" data-bind="click: function(){ fetchProfile('executors'); $('a[href=\'#job-spark-page-executors${ SUFFIX }\']').tab('show'); }">${ _('Executors') }</a></li>
        <li><a href="#job-spark-page-properties${ SUFFIX }" data-toggle="tab">${ _('Properties') }</a></li>

        <li class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" id="job-spark-page-logs${ SUFFIX }">
          <ul class="nav nav-tabs">
          % for name in ['stdout', 'stderr']:
            <li class="${ name == 'stdout' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); logActive('${ name }'); }, text: '${ name }'"></a></li>
          % endfor
          </ul>

          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>
        <div class="tab-pane" id="job-spark-page-executors${ SUFFIX }">
          <form class="form-inline">
            <input data-bind="textFilter: textFilter, clearable: {value: textFilter}, valueUpdate: 'afterkeydown'" type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">
          </form>

          <table class="table table-condensed">
            <thead>
            <tr>
              <th>${_('Executor Id')}</th>
              <th>${_('Address')}</th>
              <th>${_('RDD Blocks')}</th>
              <th>${_('Storage Memory')}</th>
              <th>${_('Disk Used')}</th>
              <th>${_('Active Tasks')}</th>
              <th>${_('Failed Tasks')}</th>
              <th>${_('Complete Tasks')}</th>
              <th>${_('Task Time')}</th>
              <th>${_('Input')}</th>
              <th>${_('Shuffle Read')}</th>
              <th>${_('Shuffle Write')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['executors']()['executor_list']">
              <tr data-bind="click: function() { $root.job().id(id); $root.job().fetchJob(); }" class="status-border pointer">
                <td data-bind="text: executor_id"></td>
                <td data-bind="text: address"></td>
                <td data-bind="text: rdd_blocks"></td>
                <td data-bind="text: storage_memory"></td>
                <td data-bind="text: disk_used"></td>
                <td data-bind="text: active_tasks"></td>
                <td data-bind="text: failed_tasks"></td>
                <td data-bind="text: complete_tasks"></td>
                <td data-bind="text: task_time"></td>
                <td data-bind="text: input"></td>
                <td data-bind="text: shuffle_read"></td>
                <td data-bind="text: shuffle_write"></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="tab-pane" id="job-spark-page-properties${ SUFFIX }">
          <table class="datatables table table-condensed">
            <thead>
            <tr>
              <th>${_('Name')}</th>
              <th>${_('Value')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['metadata']">
              <tr>
                <td data-bind="text: name"></td>
                <td><!-- ko template: { name: 'link-or-text', data: { name: name(), value: value() } } --><!-- /ko --></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="job-spark-executor-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko with: properties -->
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: executor_id"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <!-- ko if: !$root.isMini() -->
          <!-- ko with: properties -->
            <li class="nav-header">${ _('Address') }</li>
            <li><span data-bind="text: address"></span></li>
            <li class="nav-header">${ _('RDD Blocks') }</li>
            <li><span data-bind="text: rdd_blocks"></span></li>
            <li class="nav-header">${ _('Storage Memory') }</li>
            <li><span data-bind="text: storage_memory"></span></li>
            <li class="nav-header">${ _('Disk Used') }</li>
            <li><span data-bind="text: disk_used"></span></li>
            <li class="nav-header">${ _('Active Tasks') }</li>
            <li><span data-bind="text: active_tasks"></span></li>
            <li class="nav-header">${ _('Failed Tasks') }</li>
            <li><span data-bind="text: failed_tasks"></span></li>
            <li class="nav-header">${ _('Complet Tasks') }</li>
            <li><span data-bind="text: complete_tasks"></span></li>
            <li class="nav-header">${ _('Input') }</li>
            <li><span data-bind="text: input"></span></li>
            <li class="nav-header">${ _('Shuffle Read') }</li>
            <li><span data-bind="text: shuffle_read"></span></li>
            <li class="nav-header">${ _('Shuffle Write') }</li>
            <li><span data-bind="text: shuffle_write"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" href="#job-spark-executor-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="job-spark-executor-page-logs${ SUFFIX }">
          <ul class="nav nav-tabs">
          % for name in ['stdout', 'stderr']:
            <li class="${ name == 'stdout' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); logActive('${ name }'); }, text: '${ name }'"></a></li>
          % endfor
          </ul>
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="dataeng-job-page${ SUFFIX }">
  <button class="btn" title="${ _('Troubleshoot') }" data-bind="click: troubleshoot">
    <i class="fa fa-tachometer"></i> ${ _('Troubleshoot') }
  </button>

  <!-- ko if: type() == 'dataeng-job-HIVE' -->
    <div data-bind="template: { name: 'dataeng-job-hive-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->
</script>


<script type="text/html" id="dataware-clusters-page${ SUFFIX }">

  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: properties['properties']['cdhVersion']"></span></li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}">
              <div class="bar" data-bind="style: {'width': '100%'}"></div>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <div class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></div>
    </div>
  </div>

  <br>

  <button class="btn" title="${ _('Troubleshoot') }" data-bind="click: troubleshoot">
    <i class="fa fa-tachometer"></i> ${ _('Troubleshoot') }
  </button>

</script>


<script type="text/html" id="dataware2-clusters-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('Workers Online') }</li>
          <li>
            <span data-bind="text: properties['properties']['workerReplicasOnline']"></span>
            /
            <span data-bind="text: properties['properties']['workerReplicas']"></span>
            <!-- ko if: properties['properties']['workerAutoResize'] -->
              - ${ _('CPU') } <span data-bind="text: properties['properties']['workercurrentCPUUtilizationPercentage']"></span>%
            <!-- /ko -->
            <!-- ko if: status() == 'SCALING_UP' || status() == 'SCALING_DOWN' -->
              <i class="fa fa-spinner fa-spin fa-fw"></i>
            <!-- /ko -->
          </li>
          <li>
            ##<div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}">
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': status() == 'SCALING_UP' || status() == 'SCALING_DOWN', 'progress-success': status() == 'ONLINE', 'progress-danger': apiStatus() === 'FAILED'}">
              <div class="bar" data-bind="style: {'width': Math.min(properties['properties']['workerReplicas'](), properties['properties']['workerReplicasOnline']()) / Math.max(properties['properties']['workerReplicasOnline'](), properties['properties']['workerReplicas']()) * 100 + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Auto resize') }</li>
          <li>
            <i data-bind="visible: !properties['properties']['workerAutoResize']()" class="fa fa-square-o fa-fw"></i>
            <span data-bind="visible: properties['properties']['workerAutoResize']">
              <i class="fa fa-check-square-o fa-fw"></i>
              <span data-bind="text: properties['properties']['workerAutoResizeMin']"></span> -
              <span data-bind="text: properties['properties']['workerAutoResizeMax']"></span>
              ${ _('CPU:') } <span data-bind="text: properties['properties']['workerAutoResizeCpu']"></span>%
            </span>
          </li>
          <li class="nav-header">${ _('Auto pause') }</li>
          <li><i class="fa fa-square-o fa-fw"></i></li>
          <li class="nav-header">${ _('Impalad') }</li>
          <li>
            <a href="#" data-bind="attr: { 'href': properties['properties']['coordinatorEndpoint']['publicHost']() + ':25000' }">
              <span data-bind="text: properties['properties']['coordinatorEndpoint']['publicHost']"></span>
              <i class="fa fa-external-link fa-fw"></i>
            </a>
          </li>
          <li class="nav-header">${ _('Id') }</li>
          <li><span class="break-word" data-bind="text: id"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }" style="position: relative;">
      <div style="position: absolute; top: 0; right: 0">
        <button class="btn" title="Create cluster" data-bind="enable: isRunning(), visible: $root.interface() == 'dataware2-clusters', templatePopover : { placement: 'bottom', contentTemplate: 'configure-cluster-content', minWidth: '320px', trigger: 'click' }, click: updateClusterShow" style="">
            ${ _('Configure') }
          <i class="fa fa-chevron-down"></i>
        </button>

        <a class="btn" title="${ _('Pause') }">
          <i class="fa fa-pause"></i>
        </a>

        <a class="btn" title="${ _('Refresh') }" data-bind="click: function() { fetchJob(); }">
          <i class="fa fa-refresh"></i>
        </a>
      </div>

      <div class="acl-panel-content">
        <ul class="nav nav-tabs">
          <li class="active"><a href="#servicesLoad" data-toggle="tab">${ _("Load") }</a></li>
          <li><a href="#servicesPrivileges" data-toggle="tab">${ _("Privileges") }</a></li>
          <li><a href="#servicesTroubleshooting" data-toggle="tab">${ _("Troubleshooting") }</a></li>
        </ul>

        <div class="tab-content">
          <div class="tab-pane active" id="servicesLoad">
            <div class="wxm-poc" style="clear: both;">
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                % if PROMETHEUS.API_URL.get():
                <!-- ko component: { name: 'performance-graph', params: { clusterName: name(), type: 'cpu' } } --><!-- /ko -->
                % else:
                  ${ _("Metrics are not setup") }
                % endif
              </div>
            </div>
          </div>
          <div class="tab-pane" id="servicesPrivileges">
            <div class="acl-block-title">
              <i class="fa fa-cube muted"></i> <a class="pointer"><span>admin</span></a>
            </div>
            <div>
              <div class="acl-block acl-block-airy">
                <span class="muted" title="3 months ago">CLUSTER</span>
                <span>
                  <a class="muted" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
                </span>
                <br>
                server=<span>server1</span>
                <span>
                  <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" title="Browse db privileges">gke_gcp-eng-dsdw_us-west2-b_impala-demo</a>
                </span>
                <i class="fa fa-long-arrow-right"></i> action=ALL
              </div>
            </div>
            <div class="acl-block-title">
              <i class="fa fa-cube muted"></i> <a class="pointer"><span>eng</span></a>
            </div>
            <div>
              <div class="acl-block acl-block-airy">
                <span class="muted" title="3 months ago">CLUSTER</span>
                <span>
                  <a class="muted" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
                </span>
                <br>
                server=server1
                <span>
                  <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" title="Browse db privileges">gke_gcp-eng-dsdw_us-west2-b_impala-demo</a>
                </span>
                <i class="fa fa-long-arrow-right"></i> action=<span>ACCESS</span>
              </div>
            </div>
            <div class="acl-block acl-actions">
              <span class="pointer" title="Show 50 more..." style="display: none;"><i class="fa fa-ellipsis-h"></i></span>
              <span class="pointer" title="Add privilege"><i class="fa fa-plus"></i></span>
              <span class="pointer" title="Undo" style="display: none;"> &nbsp; <i class="fa fa-undo"></i></span>
              <span class="pointer" title="Save" style="display: none;"> &nbsp; <i class="fa fa-save"></i></span>
            </div>
          </div>
          <div class="tab-pane" id="servicesTroubleshooting">
            <div class="wxm-poc" style="clear: both;">
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Outliers</h4>
                <img src="${ static('desktop/art/wxm_fake/outliers.svg') }" style="height: 440px"/>
              </div>
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Statement Types</h4>
                <img src="${ static('desktop/art/wxm_fake/statement_types.svg') }" style="height: 440px"/>
              </div>
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Duration</h4>
                <img src="${ static('desktop/art/wxm_fake/duration.svg') }" style="height: 440px"/>
              </div>
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Memory Utilization</h4>
                <img src="${ static('desktop/art/wxm_fake/memory.svg') }" style="height: 440px"/>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="dataeng-job-hive-page${ SUFFIX }">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration().toHHMMSS()"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>

  <br>

  <span data-bind="text: ko.mapping.toJSON(properties['properties'])"></span>
  ##<div data-bind="template: { name: 'render-properties${ SUFFIX }', data: properties['properties'] }"></div>
</script>


<script type="text/html" id="queries-page${ SUFFIX }">
  <div class="row-fluid" data-jobType="queries">
    <!-- ko if: id() -->
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Id') }</li>
          <li>
            <a data-bind="attr: { href: doc_url_modified }" target="_blank" title="${ _('Open in impalad') }">
              <span data-bind="text: id"></span>
            </a>
            <!-- ko if: $root.isMini() -->
            <div class="progress-job progress" style="background-color: #FFF; width: 100%; height: 4px" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': apiStatus() === 'RUNNING', 'progress-success': apiStatus() === 'SUCCEEDED' }, attr: {'title': progress() + '%'}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
            <!-- /ko -->
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span>
          </li>
          <!-- /ko -->
          <!-- ko if: !$root.isMini() -->
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li>
            <span data-bind="text: progress"></span>%
          </li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': apiStatus() === 'RUNNING', 'progress-success': apiStatus() === 'SUCCEEDED' }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- /ko -->
          <!-- ko if: !$root.isMini() -->
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- ko if: properties.plan && properties.plan().status && properties.plan().status.length > 2 -->
          <li class="nav-header">${ _('Status Text') }</li>
          <li><span data-bind="text: properties.plan().status"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Open Duration') }</li>
          <li><span data-bind="text: duration() && duration().toHHMMSS()"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li>
          <a href="#queries-page-plan${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-plan${ SUFFIX }\']').tab('show'); }, event: {'shown': function () { if (!properties.plan || !properties.plan()) { fetchProfile('plan'); } } }">
            ${ _('Plan') }</a>
        </li>
        <li>
          <a href="#queries-page-stmt${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-stmt${ SUFFIX }\']').tab('show'); }">
            ${ _('Query') }</a>
        </li>
        <li>
          <a href="#queries-page-plan-text${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-plan-text${ SUFFIX }\']').tab('show'); }">
            ${ _('Text Plan') }</a>
        </li>
        <li>
          <a href="#queries-page-summary${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-summary${ SUFFIX }\']').tab('show'); }">
            ${ _('Summary') }</a>
        </li>
        <li>
          <a href="#queries-page-profile${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-profile${ SUFFIX }\']').tab('show'); }, event: {'shown': function () { if (!properties.profile || !properties.profile().profile) { fetchProfile('profile'); } } }">
            ${ _('Profile') }</a>
        </li>
        <li>
          <a href="#queries-page-memory${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-memory${ SUFFIX }\']').tab('show'); }, event: {'shown': function () { if (!properties.memory || !properties.memory().mem_usage) { fetchProfile('memory'); } } }">
            ${ _('Memory') }</a>
        </li>
        <li>
          <a href="#queries-page-backends${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-backends${ SUFFIX }\']').tab('show'); }, event: {'shown': function () { if (!properties.backends || !properties.backends().backend_states) { fetchProfile('backends'); } } }">
            ${ _('Backends') }</a>
        </li>
        <li>
          <a href="#queries-page-finstances${ SUFFIX }" data-bind="click: function(){ $('a[href=\'#queries-page-finstances${ SUFFIX }\']').tab('show'); }, event: {'shown': function () { if (!properties.finstances || !properties.finstances().backend_instances) { fetchProfile('finstances'); } } }">
            ${ _('Instances') }</a>
        </li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane" id="queries-page-plan${ SUFFIX }" data-profile="plan">
          <div data-bind="visible:properties.plan && properties.plan().plan_json && properties.plan().plan_json.plan_nodes.length">
            <div class="query-plan" id="queries-page-plan-graph${ SUFFIX }" data-bind="impalaDagre: { value: properties.plan && properties.plan(), height:$root.isMini() ? 535 : 600 }">
              <svg style="width:100%;height:100%;position:relative;" id="queries-page-plan-svg${ SUFFIX }">
                <g/>
              </svg>
            </div>
          </div>
          <pre data-bind="visible:!properties.plan || !properties.plan().plan_json || !properties.plan().plan_json.plan_nodes.length" >${ _('The selected tab has no data') }</pre>
        </div>
        <div class="tab-pane" id="queries-page-stmt${ SUFFIX }" data-profile="plan">
          <pre data-bind="text: (properties.plan && properties.plan().stmt) || _('The selected tab has no data')"/>
        </div>
        <div class="tab-pane" id="queries-page-plan-text${ SUFFIX }" data-profile="plan">
          <pre data-bind="text: (properties.plan && properties.plan().plan) || _('The selected tab has no data')"/>
        </div>
        <div class="tab-pane" id="queries-page-summary${ SUFFIX }" data-profile="plan">
          <pre data-bind="text: (properties.plan && properties.plan().summary) || _('The selected tab has no data')"/>
        </div>
        <div class="tab-pane" id="queries-page-profile${ SUFFIX }" data-profile="profile">
          <pre data-bind="text: (properties.profile && properties.profile().profile) || _('The selected tab has no data')"/>
        </div>
        <div class="tab-pane" id="queries-page-memory${ SUFFIX }" data-profile="mem_usage">
          <pre data-bind="text: (properties.memory && properties.memory().mem_usage) || _('The selected tab has no data')"/>
        </div>
        <div class="tab-pane" id="queries-page-backends${ SUFFIX }" data-profile="backends">
          <!-- ko if: properties.backends && properties.backends().backend_states -->
          <div id="queries-page-memory-backends-template${ SUFFIX }" style="overflow-x: scroll;">
            <table class="table table-condensed">
              <thead>
              <tr>
                <!-- ko foreach: Object.keys(properties.backends().backend_states[0]).sort() -->
                <th data-bind="text: $data"></th>
                <!-- /ko -->
              </tr>
              </thead>
              <tbody data-bind="foreach: { data: $data.properties.backends().backend_states, minHeight: 20, container: '#queries-page-memory-backends-template${ SUFFIX }'}">
                <tr>
                  <!-- ko foreach: Object.keys($data).sort() -->
                  <td data-bind="text: $parent[$data]"></td>
                  <!-- /ko -->
                </tr>
              </tbody>
            </table>
          </div>
          <!-- /ko -->
          <!-- ko if: !properties.backends || !properties.backends().backend_states -->
          <pre data-bind="text: _('The selected tab has no data')"/>
          <!-- /ko -->
        </div>
        <div class="tab-pane" id="queries-page-finstances${ SUFFIX }" data-profile="finstances">
          <!-- ko if: properties.finstances && properties.finstances().backend_instances -->
          <div id="queries-page-memory-finstances-template${ SUFFIX }" style="overflow-x: scroll;">
            <table class="table table-condensed">
              <thead>
              <tr>
                <!-- ko foreach: [_('host')].concat(Object.keys($data.properties.finstances().backend_instances[0].instance_stats[0])).sort() -->
                <th data-bind="text: $data"></th>
                <!-- /ko -->
              </tr>
              </thead>
              <tbody data-bind="foreach: { data: $data.properties.finstances().backend_instances.reduce( function(arr, instance) { instance.instance_stats.forEach(function(stats) { stats.host = instance.host; }); return arr.concat(instance.instance_stats); }, []), minHeight: 20, container: '#queries-page-memory-finstances-template${ SUFFIX }'}">
                <tr>
                  <!-- ko foreach: Object.keys($data).sort() -->
                  <td data-bind="text: $parent[$data]"></td>
                  <!-- /ko -->
                </tr>
              </tbody>
            </table>
          </div>
          <!-- /ko -->
          <!-- ko if: !properties.finstances || !properties.finstances().backend_instances -->
          <pre data-bind="text: _('The selected tab has no data')"/>
          <!-- /ko -->
        </div>
      </div>
    </div>
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="livy-session-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="hueLink: doc_url" href="javascript: void(0);" title="${ _('Open in editor') }">
              <span data-bind="text: name"></span>
            </a>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': apiStatus() === 'RUNNING', 'progress-success': apiStatus() === 'SUCCEEDED' }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration().toHHMMSS()"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        <li>
          <a href="#livy-session-page-statements${ SUFFIX }" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#livy-session-page-statements${ SUFFIX }\']').tab('show'); }">
            ${ _('Properties') }</a>
        </li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" id="livy-session-page-statements${ SUFFIX }">
          <table id="actionsTable" class="datatables table table-condensed">
            <thead>
            <tr>
              <th>${_('Id')}</th>
              <th>${_('State')}</th>
              <th>${_('Output')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['statements']">
              <tr data-bind="click: function() {  $root.job().id(id); $root.job().fetchJob(); }" class="pointer">
                <td>
                  <a data-bind="hueLink: '/jobbrowser/jobs/' + id(), clickBubble: false">
                    <i class="fa fa-tasks"></i>
                  </a>
                </td>
                <td data-bind="text: state"></td>
                <td data-bind="text: output"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="job-actions${ SUFFIX }">
  <div class="btn-group">
    <!-- ko if: hasResume -->
    <button class="btn" title="${ _('Resume selected') }" data-bind="click: function() { control('resume'); }, enable: resumeEnabled">
      <i class="fa fa-play"></i> <!-- ko ifnot: $root.isMini -->${ _('Resume') }<!-- /ko -->
    </button>
    <!-- /ko -->

    <!-- ko if: hasPause -->
    <button class="btn" title="${ _('Suspend selected') }" data-bind="click: function() { control('suspend'); }, enable: pauseEnabled">
      <i class="fa fa-pause"></i> <!-- ko ifnot: $root.isMini -->${ _('Suspend') }<!-- /ko -->
    </button>
    <!-- /ko -->

    <!-- ko if: hasRerun -->
    <button class="btn" title="${ _('Rerun selected') }" data-bind="click: function() { control('rerun'); }, enable: rerunEnabled">
      <i class="fa fa-repeat"></i> <!-- ko ifnot: $root.isMini -->${ _('Rerun') }<!-- /ko -->
    </button>
    <!-- /ko -->

    % if not DISABLE_KILLING_JOBS.get():
    <!-- ko if: hasKill -->
    <button class="btn btn-danger disable-feedback" title="${_('Stop selected')}" data-bind="click: function() { $('#killModal${ SUFFIX }').modal('show'); }, enable: killEnabled">
      <i class="fa fa-times"></i> <!-- ko ifnot: $root.isMini -->${_('Kill')}<!-- /ko -->
    </button>
    <!-- /ko -->
    % endif

    <!-- ko if: hasIgnore -->
    <button class="btn btn-danger disable-feedback" title="${_('Ignore selected')}" data-bind="click: function() { control('ignore'); }, enable: ignoreEnabled">
      ## TODO confirmation
      <i class="fa fa-eraser"></i> <!-- ko ifnot: $root.isMini -->${_('Ignore')}<!-- /ko -->
    </button>
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="workflow-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header" data-bind="visible: ! $root.isMini()">${ _('Id') }</li>
          <li class="break-word" data-bind="visible: ! $root.isMini()"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="documentContextPopover: { uuid: doc_url().split('=')[1], orientation: 'bottom', offset: { top: 5 } }" href="javascript: void(0);" title="${ _('Preview document') }">
              <span data-bind="text: name"></span> <i class="fa fa-info"></i>
            </a>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <!-- /ko -->
          <li class="nav-header" data-bind="visible: ! $root.isMini()">${ _('Status') }</li>
          <li><span data-bind="text: status, visible: ! $root.isMini()"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': apiStatus() === 'RUNNING', 'progress-success': apiStatus() === 'SUCCEEDED' }, attr: {title: status}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li data-bind="visible: ! $root.isMini()" class="nav-header">${ _('Duration') }</li>
          <li data-bind="visible: ! $root.isMini()"><span data-bind="text: duration().toHHMMSS()"></span></li>
          <li class="nav-header" data-bind="visible: ! $root.isMini()">${ _('Submitted') }</li>
          <li data-bind="visible: ! $root.isMini()"><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
          <!-- ko if: properties['parameters'].length > 0 -->
          <li class="nav-header">${ _('Variables') }</li>
          <li>
            <ul class="unstyled" data-bind="foreach: properties['parameters']">
              <li class="margin-top-5">
              <span data-bind="text: name, attr: { title: value }" class="muted"></span><br>
                &nbsp;
              <!-- ko if: link -->
              <a data-bind="hueLink: link, text: value, attr: { title: value }" href="javascript: void(0);">
              </a>
              <!-- /ko -->
              <!-- ko ifnot: link -->
                <span data-bind="text: value, attr: { title: value }"></span>
              <!-- /ko -->
              </li>
            </ul>
          </li>
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: { 'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        %if not is_mini:
        <li class="active"><a href="#workflow-page-graph${ SUFFIX }" data-toggle="tab">${ _('Graph') }</a></li>
        %endif
        <li><a href="#workflow-page-metadata${ SUFFIX }" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#workflow-page-metadata${ SUFFIX }\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a class="jb-logs-link" href="#workflow-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li class="${ 'active' if is_mini else ''}"><a href="#workflow-page-tasks${ SUFFIX }" data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a href="#workflow-page-xml${ SUFFIX }" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#workflow-page-xml${ SUFFIX }\']').tab('show'); }">${ _('XML') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        %if not is_mini:
        <div class="tab-pane active dashboard-container" id="workflow-page-graph${ SUFFIX }"></div>
        %endif

        <div class="tab-pane" id="workflow-page-logs${ SUFFIX }">
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane ${ 'active' if is_mini else ''}" id="workflow-page-tasks${ SUFFIX }">
          <table id="actionsTable" class="datatables table table-condensed">
            <thead>
            <tr>
              <th>${_('Log')}</th>
              <th>${_('Status')}</th>
              <th>${_('Error message')}</th>
              <th>${_('Error code')}</th>
              <th>${_('External id')}</th>
              <th>${_('Id')}</th>
              <th>${_('Start time')}</th>
              <th>${_('End time')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['actions']">
              <tr data-bind="click: function() {  $root.job().id(id); $root.job().fetchJob(); }" class="pointer">
                <td>
                  <a data-bind="hueLink: '/jobbrowser/jobs/' + externalId(), clickBubble: false">
                    <i class="fa fa-tasks"></i>
                  </a>
                </td>
                <td data-bind="text: status"></td>
                <td data-bind="text: errorMessage"></td>
                <td data-bind="text: errorCode"></td>
                <td data-bind="text: externalId"></td>
                <td data-bind="text: id"></td>
                <td data-bind="moment: {data: startTime, format: 'LLL'}"></td>
                <td data-bind="moment: {data: endTime, format: 'LLL'}"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="workflow-page-metadata${ SUFFIX }">
          <div data-bind="template: { name: 'render-properties${ SUFFIX }', data: properties['properties'] }"></div>
        </div>

        <div class="tab-pane" id="workflow-page-xml${ SUFFIX }">
          <div data-bind="readOnlyAce: properties['xml'], path: 'xml', type: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="workflow-action-page${ SUFFIX }">

  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Job') }</li>
          <li>
            <a data-bind="hueLink: '/jobbrowser/jobs/' + properties['externalId']()" href="javascript: void(0);">
              <span data-bind="text: properties['externalId']"></span>
            </a>
          </li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a href="#workflow-action-page-metadata${ SUFFIX }" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a href="#workflow-action-page-tasks${ SUFFIX }" data-toggle="tab">${ _('Child jobs') }</a></li>
        <li><a href="#workflow-action-page-xml${ SUFFIX }" data-toggle="tab">${ _('XML') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="workflow-action-page-metadata${ SUFFIX }">
          <table class="datatables table table-condensed">
            <thead>
            <tr>
              <th>${_('Name')}</th>
              <th>${_('Value')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['properties']">
              <tr>
                <td data-bind="text: name"></td>
                <td data-bind="text: value"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="workflow-action-page-tasks${ SUFFIX }">
          <!-- ko if: properties['externalChildIDs'].length > 0 -->
          <table class="table table-condensed datatables">
            <thead>
              <tr>
                <th>${ _('Ids') }</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: properties['externalChildIDs']">
              <tr>
                <td>
                  <a data-bind="hueLink: '/jobbrowser/jobs/' + $data, text: $data" href="javascript: void(0);">
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
          <!-- /ko -->

          <!-- ko if: properties['externalChildIDs'].length == 0 -->
            ${ _('No external jobs') }
          <!-- /ko -->
        </div>

        <div class="tab-pane" id="workflow-action-page-xml${ SUFFIX }">
          <div data-bind="readOnlyAce: properties['conf'], type: 'xml'"></div>
        </div>

      </div>
    </div>
  </div>
</script>


<script type="text/html" id="schedule-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header" data-bind="visible: ! $root.isMini()">${ _('Id') }</li>
          <li class="break-word" data-bind="visible: ! $root.isMini()"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="documentContextPopover: { uuid: doc_url().split('=')[1], orientation: 'bottom', offset: { top: 5 } }" href="javascript: void(0);" title="${ _('Preview document') }">
              <span data-bind="text: name"></span> <i class="fa fa-info"></i>
            </a>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <!-- /ko -->
          <li class="nav-header" data-bind="visible: ! $root.isMini()">${ _('Type') }</li>
          <li data-bind="visible: ! $root.isMini()"><span data-bind="text: type"></span></li>
          <li class="nav-header" data-bind="visible: ! $root.isMini()">${ _('Status') }</li>
          <li data-bind="visible: ! $root.isMini()"><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}, attr: {title: status}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko if: !$root.isMini() -->
            <li class="nav-header">${ _('Submitted') }</li>
            <li><span data-bind="text: submitted"></span></li>
            <li class="nav-header">${ _('Next Run') }</li>
            <li><span data-bind="text: properties['nextTime']"></span></li>
            <li class="nav-header">${ _('Total Actions') }</li>
            <li><span data-bind="text: properties['total_actions']"></span></li>
            <li class="nav-header">${ _('End time') }</li>
            <li><span data-bind="text: properties['endTime']"></span></li>
          <!-- /ko -->
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a href="#schedule-page-calendar${ SUFFIX }" data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a class="jb-logs-link" href="#schedule-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#schedule-page-metadata${ SUFFIX }" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#schedule-page-metadata${ SUFFIX }\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a href="#schedule-page-xml${ SUFFIX }" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#schedule-page-xml${ SUFFIX }\']').tab('show'); }">${ _('XML') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" id="schedule-page-calendar${ SUFFIX }">
          <!-- ko with: coordinatorActions() -->
          <form class="form-inline">
            ##<input data-bind="value: textFilter" type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">

            ##<span data-bind="foreach: statesValuesFilter">
            ##  <label class="checkbox">
            ##    <div class="pull-left margin-left-5 status-border status-content" data-bind="css: value, hueCheckbox: checked"></div>
            ##    <div class="inline-block" data-bind="text: name, toggle: checked"></div>
            ##  </label>
            ##</span>
            <div data-bind="template: { name: 'job-actions${ SUFFIX }' }" class="pull-right"></div>
          </form>

          <table id="schedulesTable" class="datatables table table-condensed status-border-container">
            <thead>
            <tr>
              <th width="1%"><div class="select-all hue-checkbox fa" data-bind="hueCheckAll: { allValues: apps, selectedValues: selectedJobs }"></div></th>
              <th>${_('Status')}</th>
              <th>${_('Title')}</th>
              <th>${_('type')}</th>
              <th>${_('errorMessage')}</th>
              <th>${_('missingDependencies')}</th>
              <th>${_('number')}</th>
              <th>${_('errorCode')}</th>
              <th>${_('externalId')}</th>
              <th>${_('id')}</th>
              <th>${_('lastModifiedTime')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: apps">
              <tr class="status-border pointer" data-bind="css: {'completed': properties.status() == 'SUCCEEDED', 'running': ['RUNNING', 'FAILED', 'KILLED'].indexOf(properties.status()) != -1, 'failed': properties.status() == 'FAILED' || properties.status() == 'KILLED'}, click: function() {  if (properties.externalId() && properties.externalId() != '-') { $root.job().id(properties.externalId()); $root.job().fetchJob(); } }">
                <td data-bind="click: function() {}, clickBubble: false">
                  <div class="hue-checkbox fa" data-bind="click: function() {}, clickBubble: false, multiCheck: '#schedulesTable', value: $data, hueChecked: $parent.selectedJobs"></div>
                </td>
                <td data-bind="text: properties.status"></td>
                <td data-bind="text: properties.title"></td>
                <td data-bind="text: properties.type"></td>
                <td data-bind="text: properties.errorMessage"></td>
                <td data-bind="text: properties.missingDependencies"></td>
                <td data-bind="text: properties.number"></td>
                <td data-bind="text: properties.errorCode"></td>
                <td data-bind="text: properties.externalId"></td>
                <td data-bind="text: properties.id"></td>
                <td data-bind="text: properties.lastModifiedTime"></td>
              </tr>
            </tbody>
          </table>
          <!-- /ko -->
        </div>

        <div class="tab-pane" id="schedule-page-logs${ SUFFIX }">
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" id="schedule-page-metadata${ SUFFIX }">
          <div data-bind="template: { name: 'render-properties${ SUFFIX }', data: properties['properties'] }"></div>
        </div>

        <div class="tab-pane" id="schedule-page-xml${ SUFFIX }">
          <div data-bind="readOnlyAce: properties['xml'], path: 'xml', type: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="bundle-page${ SUFFIX }">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="documentContextPopover: { uuid: doc_url().split('=')[1], orientation: 'bottom', offset: { top: 5 } }" href="javascript: void(0);" title="${ _('Preview document') }">
              <span data-bind="text: name"></span> <i class="fa fa-info"></i>
            </a>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          ##<li class="nav-header">${ _('Duration') }</li>
          ##<li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
          ##<li class="nav-header">${ _('Next Run') }</li>
          ##<li><span data-bind="text: properties['nextTime']"></span></li>
          ##<li class="nav-header">${ _('Total Actions') }</li>
          ##<li><span data-bind="text: properties['total_actions']"></span></li>
          ##<li class="nav-header">${ _('End time') }</li>
          ##<li><span data-bind="text: properties['endTime']"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a href="#bundle-page-coordinators${ SUFFIX }" data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a class="jb-logs-link" href="#bundle-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#bundle-page-metadata${ SUFFIX }"  data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#bundle-page-metadata${ SUFFIX }\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a href="#bundle-page-xml${ SUFFIX }" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#bundle-page-xml${ SUFFIX }\']').tab('show'); }">${ _('XML') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" id="bundle-page-coordinators${ SUFFIX }">
          <table id="coordsTable" class="datatables table table-condensed status-border-container">
            <thead>
            <tr>
              <th>${_('Status')}</th>
              <th>${_('Name')}</th>
              <th>${_('Type')}</th>
              <th>${_('nextMaterializedTime')}</th>
              <th>${_('lastAction')}</th>
              <th>${_('frequency')}</th>
              <th>${_('timeUnit')}</th>
              <th>${_('externalId')}</th>
              <th>${_('id')}</th>
              <th>${_('pauseTime')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['actions']">
              <tr class="status-border pointer" data-bind="css: {'completed': status() == 'SUCCEEDED', 'running': ['SUCCEEDED', 'FAILED', 'KILLED'].indexOf(status()) != -1, 'failed': status() == 'FAILED' || status() == 'KILLED'}, click: function() { if (id()) { $root.job().id(id()); $root.job().fetchJob();} }">
                <td data-bind="text: status"></td>
                <td data-bind="text: name"></td>
                <td data-bind="text: type"></td>
                <td data-bind="text: nextMaterializedTime"></td>
                <td data-bind="text: lastAction"></td>
                <td data-bind="text: frequency"></td>
                <td data-bind="text: timeUnit"></td>
                <td data-bind="text: externalId"></td>
                <td data-bind="text: id"></td>
                <td data-bind="text: pauseTime"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="bundle-page-logs${ SUFFIX }">
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" id="bundle-page-metadata${ SUFFIX }">
          <div data-bind="template: { name: 'render-properties${ SUFFIX }', data: properties['properties'] }"></div>
        </div>

        <div class="tab-pane" id="bundle-page-xml${ SUFFIX }">
          <div data-bind="readOnlyAce: properties['xml'], path: 'xml', type: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="render-properties${ SUFFIX }">
  <!-- ko hueSpinner: { spin: !$data.properties, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko if: $data.properties -->
  <!-- ko if: !$root.isMini() -->
  <form class="form-search">
    <input type="text" data-bind="clearable: $parent.propertiesFilter, valueUpdate: 'afterkeydown'" class="input-xlarge search-query" placeholder="${_('Text Filter')}">
  </form>
  <br>
  <!-- /ko -->
  <table id="jobbrowserJobPropertiesTable" class="table table-condensed">
    <thead>
    <tr>
      <th>${ _('Name') }</th>
      <th>${ _('Value') }</th>
    </tr>
    </thead>
    <tbody data-bind="foreach: Object.keys($data.properties)">
      <tr>
        <td data-bind="text: $data"></td>
        <td>
        <!-- ko template: { name: 'link-or-text${ SUFFIX }', data: { name: $data, value: $parent.properties[$data] } } --><!-- /ko -->
        </td>
      </tr>
    </tbody>
  </table>
  <!-- /ko -->
</script>


<script type="text/html" id="render-page-counters${ SUFFIX }">
  <!-- ko hueSpinner: { spin: !$data, center: true, size: 'xlarge' } --><!-- /ko -->

  <!-- ko if: $data -->
    <!-- ko ifnot: $data.counterGroup -->
      <span class="muted">${ _('There are currently no counters to be displayed.') }</span>
    <!-- /ko -->
    <!-- ko if: $data.counterGroup -->
    <!-- ko foreach: $data.counterGroup -->
      <h3 data-bind="text: counterGroupName"></h3>
      <table class="table table-condensed">
        <thead>
        <tr>
          <th>${ _('Name') }</th>
          <th width="15%">${ _('Maps total') }</th>
          <th width="15%">${ _('Reduces total') }</th>
          <th width="15%">${ _('Total') }</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: counter">
          <tr>
            <td data-bind="text: name"></td>
            <td data-bind="text: mapCounterValue"></td>
            <td data-bind="text: reduceCounterValue"></td>
            <td data-bind="text: totalCounterValue"></td>
          </tr>
        </tbody>
      </table>
    <!-- /ko -->
    <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="render-task-counters${ SUFFIX }">
  <!-- ko hueSpinner: { spin: !$data.id, center: true, size: 'xlarge' } --><!-- /ko -->

  <!-- ko if: $data.id -->
    <!-- ko ifnot: $data.taskCounterGroup -->
      <span class="muted">${ _('There are currently no counters to be displayed.') }</span>
    <!-- /ko -->
    <!-- ko if: $data.taskCounterGroup -->
    <!-- ko foreach: $data.taskCounterGroup -->
      <h3 data-bind="text: counterGroupName"></h3>
      <table class="table table-condensed">
        <thead>
        <tr>
          <th>${ _('Name') }</th>
          <th width="30%">${ _('Value') }</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: counter">
          <tr>
            <td data-bind="text: name"></td>
            <td data-bind="text: value"></td>
          </tr>
        </tbody>
      </table>
    <!-- /ko -->
    <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="render-attempt-counters${ SUFFIX }">
  <!-- ko hueSpinner: { spin: !$data.id, center: true, size: 'xlarge' } --><!-- /ko -->

  <!-- ko if: $data.id -->
    <!-- ko ifnot: $data.taskAttemptCounterGroup -->
      <span class="muted">${ _('There are currently no counters to be displayed.') }</span>
    <!-- /ko -->
    <!-- ko if: $data.taskAttemptCounterGroup -->
    <!-- ko foreach: $data.taskAttemptCounterGroup -->
      <h3 data-bind="text: counterGroupName"></h3>
      <table class="table table-condensed">
        <thead>
        <tr>
          <th>${ _('Name') }</th>
          <th width="30%">${ _('Value') }</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: counter">
          <tr>
            <td data-bind="text: name"></td>
            <td data-bind="text: value"></td>
          </tr>
        </tbody>
      </table>
    <!-- /ko -->
    <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="render-metadata${ SUFFIX }">
  <!-- ko hueSpinner: { spin: !$data.property, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko if: $data.property -->
  <form class="form-search">
    <input type="text" data-bind="clearable: $parent.metadataFilter, valueUpdate: 'afterkeydown'" class="input-xlarge search-query" placeholder="${_('Text Filter')}">
  </form>
  %if not is_mini:
  <div id="job-mapreduce-page-metadata-template${ SUFFIX }" style="overflow-y: hidden; height: calc(100vh - 350px);">
  % else:
  <div id="job-mapreduce-page-metadata-template${ SUFFIX }" style="overflow-y: hidden; height: 400px;">
  %endif
    <table id="jobbrowserJobMetadataTable" class="table table-condensed">
      <thead>
      <tr>
        <th>${ _('Name') }</th>
        <th width="50%">${ _('Value') }</th>
      </tr>
      </thead>
      <tbody data-bind="foreachVisible: { data: property, minHeight: 20, container: '#job-mapreduce-page-metadata-template${ SUFFIX }'}">
        <tr>
          <td data-bind="text: name"></td>
          <td>
            <!-- ko template: { name: 'link-or-text${ SUFFIX }', data: { name: name, value: value } } --><!-- /ko -->
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="link-or-text${ SUFFIX }">
  <!-- ko if: typeof $data.value === 'string' -->
    <!-- ko if: $data.name.indexOf('logs') > -1 || $data.name.indexOf('trackingUrl') > -1 -->
      <a href="javascript:void(0);" data-bind="text: $data.value, attr: { href: $data.value }" target="_blank"></a>
    <!-- /ko -->
    <!-- ko if: ($data.name.indexOf('dir') > -1 || $data.name.indexOf('path') > -1 || $data.name.indexOf('output') > -1 || $data.name.indexOf('input') > -1) && ($data.value.startsWith('/') || $data.value.startsWith('hdfs://') || $data.value.startsWith('s3a://')) -->
      <a href="javascript:void(0);" data-bind="hueLink: '/filebrowser/view=' + $root.getHDFSPath($data.value), text: $data.value"></a>
      <a href="javascript: void(0);" data-bind="storageContextPopover: { path: $root.getHDFSPath($data.value), orientation: 'left', offset: { top: 5 } }"><i class="fa fa-info"></i></a>
    <!-- /ko -->
    <!-- ko ifnot: $data.name.indexOf('logs') > -1 || $data.name.indexOf('trackingUrl') > -1 || (($data.name.indexOf('dir') > -1 || $data.name.indexOf('path') > -1 || $data.name.indexOf('output') > -1 || $data.name.indexOf('input') > -1) && ($data.value.startsWith('/') || $data.value.startsWith('hdfs://') || $data.value.startsWith('s3a://'))) -->
      <span data-bind="text: $data.value"></span>
    <!-- /ko -->
  <!-- /ko -->
  <!-- ko ifnot: typeof $data.value === 'string' -->
    <span data-bind="text: $data.value"></span>
  <!-- /ko -->
</script>


<script type="text/javascript">

  (function () {

    var Job = function (vm, job) {
      var self = this;

      self.id = ko.observableDefault(job.id);
      %if not is_mini:
      self.id.subscribe(function () {
        huePubSub.publish('graph.stop.refresh.view');
      });
      %endif
      self.doc_url = ko.observableDefault(job.doc_url);
      self.doc_url_modified = ko.computed(function () {
        var url = self.doc_url();
        if (window.KNOX_BASE_URL.length && window.URL && url) { // KNOX
          try {
            var parsedDocUrl = new URL(url);
            var parsedKnoxUrl = new URL(window.KNOX_BASE_URL);
            parsedDocUrl.hostname = parsedKnoxUrl.hostname;
            parsedDocUrl.protocol = parsedKnoxUrl.protocol;
            parsedDocUrl.port = parsedKnoxUrl.port;
            var service = url.indexOf('livy') >= 0 ? '/livy' : '/impala';
            parsedDocUrl.pathname = parsedKnoxUrl.pathname + service + parsedDocUrl.pathname;
            return parsedDocUrl.toString();
          } catch (e) {
            return url;
          }
        } else if (window.KNOX_BASE_PATH.length && window.URL) { // DWX
          var parsedDocUrl = new URL(url);
          var service = url.indexOf('livy') >= 0 ? '/livy' : '/impala';
          parsedDocUrl.pathname = parsedKnoxUrl.pathname + service + window.KNOX_BASE_PATH;
        } else {
          return url;
        }
      });
      self.name = ko.observableDefault(job.name || job.id);
      self.type = ko.observableDefault(job.type);
      self.applicationType = ko.observableDefault(job.applicationType || '');

      self.status = ko.observableDefault(job.status);
      self.apiStatus = ko.observableDefault(job.apiStatus);
      self.progress = ko.observableDefault(job.progress);
      self.isRunning = ko.computed(function() {
        return ['RUNNING', 'PAUSED'].indexOf(self.apiStatus()) != -1 || job.isRunning;
      });

      self.user = ko.observableDefault(job.user);
      self.queue = ko.observableDefault(job.queue);
      self.cluster = ko.observableDefault(job.cluster);
      self.duration = ko.observableDefault(job.duration);
      self.submitted = ko.observableDefault(job.submitted);
      self.canWrite = ko.observableDefault(job.canWrite == true);

      self.logActive = ko.observable('default');
      self.logsByName = ko.observable({});
      self.logsListDefaults = ko.observable(['default', 'stdout', 'stderr', 'syslog']);
      self.logsList = ko.observable(self.logsListDefaults());
      self.logs = ko.pureComputed(function() {
        return self.logsByName()[self.logActive()];
      });

      self.properties = ko.mapping.fromJS(job.properties || { properties: '' });
      self.mainType = ko.observable(vm.interface());
      self.lastEvent = ko.observable(job.lastEvent || '');

      self.coordinatorActions = ko.pureComputed(function() {
        if (self.mainType() == 'schedules' && self.properties['tasks']) {
          var apps = self.properties['tasks']().map(function (instance) {
            var job = new CoordinatorAction(vm, ko.mapping.toJS(instance), self);
            job.properties = instance;
            return job;
          });
          var instances = new Jobs(vm);
          instances.apps(apps);
          instances.isCoordinator(true);
          return instances;
        }
      });

      self.textFilter = ko.observable('').extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 1000 } });
      self.statesValuesFilter = ko.observableArray([
        ko.mapping.fromJS({'value': 'completed', 'name': '${_("Succeeded")}', 'checked': false, 'klass': 'green'}),
        ko.mapping.fromJS({'value': 'running', 'name': '${_("Running")}', 'checked': false, 'klass': 'orange'}),
        ko.mapping.fromJS({'value': 'failed', 'name': '${_("Failed")}', 'checked': false, 'klass': 'red'}),
      ]);
      self.statesFilter = ko.computed(function () {
        var checkedStates = ko.utils.arrayFilter(self.statesValuesFilter(), function (state) {
          return state.checked();
        });
        return ko.utils.arrayMap(checkedStates, function(state){
          return state.value()
        });
      });
      self.typesValuesFilter = ko.observableArray([
        ko.mapping.fromJS({'value': 'map', 'name': '${_("Map")}', 'checked': false, 'klass': 'green'}),
        ko.mapping.fromJS({'value': 'reduce', 'name': '${_("Reduce")}', 'checked': false, 'klass': 'orange'}),
      ]);
      self.typesFilter = ko.computed(function () {
        var checkedTypes = ko.utils.arrayFilter(self.typesValuesFilter(), function (type) {
          return type.checked();
        });
        return ko.utils.arrayMap(checkedTypes, function(type){
          return type.value()
        });
      });
      self.filters = ko.pureComputed(function() {
        return [
          {'text': self.textFilter()},
          {'states': ko.mapping.toJS(self.statesFilter())},
          {'types': ko.mapping.toJS(self.typesFilter())},
        ];
      });
      self.filters.subscribe(function(value) {
        self.fetchProfile('tasks');
      });
      self.metadataFilter = ko.observable('');
      self.metadataFilter.subscribe(function(newValue) {
        $("#jobbrowserJobMetadataTable tbody tr").removeClass("hide");
        $("#jobbrowserJobMetadataTable tbody tr").each(function () {
          if ($(this).text().toLowerCase().indexOf(newValue.toLowerCase()) == -1) {
            $(this).addClass("hide");
          }
        });
      });
      self.propertiesFilter = ko.observable('');
      self.propertiesFilter.subscribe(function(newValue) {
        $("#jobbrowserJobPropertiesTable tbody tr").removeClass("hide");
        $("#jobbrowserJobPropertiesTable tbody tr").each(function () {
          if ($(this).text().toLowerCase().indexOf(newValue.toLowerCase()) == -1) {
            $(this).addClass("hide");
          }
        });
      });

      self.rerunModalContent = ko.observable('');

      self.hasKill = ko.pureComputed(function() {
        return self.type() && (['MAPREDUCE', 'SPARK', 'workflow', 'schedule', 'bundle', 'QUERY', 'TEZ', 'YarnV2'].indexOf(self.type()) != -1 || self.type().indexOf('Data Warehouse') != -1 || self.type().indexOf('Altus') != -1);
      });
      self.killEnabled = ko.pureComputed(function() {
        // Impala can kill queries that are finished, but not yet terminated
        return self.hasKill() && self.canWrite() && self.isRunning();
      });

      self.hasResume = ko.pureComputed(function() {
        return ['workflow', 'schedule', 'bundle'].indexOf(self.type()) != -1;
      });
      self.resumeEnabled = ko.pureComputed(function() {
        return self.hasResume() && self.canWrite() && self.apiStatus() == 'PAUSED';
      });

      self.hasRerun = ko.pureComputed(function() {
        return ['workflow', 'schedule-task'].indexOf(self.type()) != -1;
      });
      self.rerunEnabled = ko.pureComputed(function() {
        return self.hasRerun() && self.canWrite() && ! self.isRunning();
      });

      self.hasPause = ko.pureComputed(function() {
        return ['workflow', 'schedule', 'bundle'].indexOf(self.type()) != -1;
      });
      self.pauseEnabled = ko.pureComputed(function() {
        return self.hasPause() && self.canWrite() && self.apiStatus() == 'RUNNING';
      });

      self.hasIgnore = ko.pureComputed(function() {
        return ['schedule-task'].indexOf(self.type()) != -1;
      });
      self.ignoreEnabled = ko.pureComputed(function() {
        return self.hasIgnore() && self.canWrite() && ! self.isRunning();
      });

      self.loadingJob = ko.observable(false);
      var lastFetchJobRequest = null;
      var lastUpdateJobRequest = null;
      var lastFetchLogsRequest = null;
      var lastFetchProfileRequest = null;
      var lastFetchStatusRequest = null;

      self._fetchJob = function (callback) {
        if (vm.interface() == 'engines') {
          huePubSub.publish('context.selector.set.cluster', 'AltusV2');
          return;
        }

        return $.post("/jobbrowser/api/job/" + vm.interface(), {
          cluster: ko.mapping.toJSON(vm.compute),
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface)
        }, function (data) {
          if (data.status == 0) {
            if (data.app) {
              huePubSub.publish('jobbrowser.data', [data.app]);
            }
            if (callback) {
              callback(data);
            };
          } else {
            $(document).trigger("error", data.message);
          }
        });
      };

      self.fetchJob = function () {
        vm.apiHelper.cancelActiveRequest(lastFetchJobRequest);
        vm.apiHelper.cancelActiveRequest(lastUpdateJobRequest);

        self.loadingJob(true);

        var interface = vm.interface();
        if (/application_/.test(self.id()) || /job_/.test(self.id()) || /attempt_/.test(self.id())) {
          interface = 'jobs';
        }
        if (/oozie-\w+-W/.test(self.id())) {
          interface = 'workflows';
        }
        else if (/oozie-\w+-C/.test(self.id())) {
          interface = 'schedules';
        }
        else if (/oozie-\w+-B/.test(self.id())) {
          interface = 'bundles';
        }
        else if (/altus:dataeng/.test(self.id()) && /:job:/.test(self.id())) {
          interface = 'dataeng-jobs';
        }
        else if (/altus:dataeng/.test(self.id()) && /:cluster:/.test(self.id())) {
          interface = 'dataeng-clusters';
        }
        else if (/altus:dataware:k8/.test(self.id()) && /:cluster:/.test(self.id())) {
          interface = 'dataware2-clusters';
        }
        else if (/altus:dataware/.test(self.id()) && /:cluster:/.test(self.id())) {
          interface = 'dataware-clusters';
        }
        else if (/[a-z0-9]{16}:[a-z0-9]{16}/.test(self.id())) {
          interface = 'queries';
        }
        else if (/livy-[0-9]+/.test(self.id())) {
          interface = 'livy-sessions';
        }

        interface = interface.indexOf('dataeng') || interface.indexOf('dataware') ? interface : vm.isValidInterface(interface); // TODO: support multi cluster selection in isValidInterface
        vm.interface(interface);

        lastFetchJobRequest = self._fetchJob(function (data) {
          if (data.status == 0) {
            vm.interface(interface);
            vm.job(new Job(vm, data.app));
            if (window.location.hash !== '#!id=' + vm.job().id()) {
              hueUtils.changeURL('#!id=' + vm.job().id());
            }
            var crumbs = [];
            if (/^appattempt_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
            }
            if (/^attempt_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
              crumbs.push({'id': vm.job().properties['task_id'], 'name': vm.job().properties['task_id'], 'type': 'task'});
            }
            if (/^task_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
            }
            if (/_executor_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
            }
            var oozieWorkflow = vm.job().name().match(/oozie:launcher:T=.+?:W=.+?:A=.+?:ID=(.+?-oozie-\w+-W)$/i);
            if (oozieWorkflow) {
              crumbs.push({'id': oozieWorkflow[1], 'name': oozieWorkflow[1], 'type': 'workflow'});
            }

            if (/-oozie-\w+-W@/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['workflow_id'], 'name': vm.job().properties['workflow_id'], 'type': 'workflow'});
            }
            else if (/-oozie-\w+-W/.test(vm.job().id())) {
              if (vm.job().properties['bundle_id']()) {
                crumbs.push({'id': vm.job().properties['bundle_id'](), 'name': vm.job().properties['bundle_id'](), 'type': 'bundle'});
              }
              if (vm.job().properties['coordinator_id']()) {
                crumbs.push({'id': vm.job().properties['coordinator_id'](), 'name': vm.job().properties['coordinator_id'](), 'type': 'schedule'});
              }
            }
            else if (/-oozie-\w+-C/.test(vm.job().id())) {
              if (vm.job().properties['bundle_id']()) {
                crumbs.push({'id': vm.job().properties['bundle_id'](), 'name': vm.job().properties['bundle_id'](), 'type': 'bundle'});
              }
            }

            if (vm.job().type() == 'SPARK_EXECUTOR') {
              crumbs.push({'id': vm.job().id(), 'name': vm.job().properties['executor_id'](), 'type': vm.job().type()});
            }
            else {
              crumbs.push({'id': vm.job().id(), 'name': vm.job().name(), 'type': vm.job().type()});
            }

            vm.resetBreadcrumbs(crumbs);
            // Show is still bound to old job, setTimeout allows knockout model change event done at begining of this method to sends it's notification
            setTimeout(function () {
              if (vm.job().type() === 'queries' && !$("#queries-page-plan${ SUFFIX }").parent().children().hasClass("active")) {
                $("a[href=\'#queries-page-plan${ SUFFIX }\']").tab("show");
              }
            }, 0);
            %if not is_mini:
            if (vm.job().type() === 'workflow' && !vm.job().workflowGraphLoaded) {
              vm.job().updateWorkflowGraph();
            }
            %else:
            if (vm.job().type() === 'workflow') {
              vm.job().fetchProfile('properties');
              $('a[href="#workflow-page-metadata${ SUFFIX }"]').tab('show');
            }
            $('#rerun-modal${ SUFFIX }').on('shown', function (e) {
                // Replaces dark modal backdrop from the end of the body tag to the closer scope
                // in order to activate z-index effect.
                var rerunModalData = $(this).data('modal');
                rerunModalData.$backdrop.appendTo("#jobbrowserMiniComponents");
            });
            $('#killModal${ SUFFIX }').on('shown', function (e) {
                 var killModalData = $(this).data('modal');
                 killModalData.$backdrop.appendTo("#jobbrowserMiniComponents");
            });
            %endif

            vm.job().fetchLogs();

          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
          self.loadingJob(false);
        });
      };

      self.updateJob = function () {
        huePubSub.publish('graph.refresh.view');
        var deferred = $.Deferred();
        if (vm.job() == self && self.apiStatus() == 'RUNNING') {
          vm.apiHelper.cancelActiveRequest(lastUpdateJobRequest);
          lastUpdateJobRequest = self._fetchJob(function (data) {
            var requests = [];
            if (['schedule', 'workflow'].indexOf(vm.job().type()) >= 0) {
              window.hueUtils.deleteAllEmptyStringKey(data.app); // It's preferable for our backend to return empty strings for various values in order to initialize them, but they shouldn't overwrite any values that are currently set.
              var selectedIDs = []
              if (vm.job().coordinatorActions()) {
                selectedIDs = vm.job().coordinatorActions().selectedJobs().map(
                  function(coordinatorAction) {
                      return coordinatorAction.id();
                  }
                );
              }
              vm.job = ko.mapping.fromJS(data.app, {}, vm.job);
              if (selectedIDs.length > 0) {
                vm.job().coordinatorActions().selectedJobs(
                  vm.job().coordinatorActions().apps().filter(function(coordinatorAction){
                      return selectedIDs.indexOf(coordinatorAction.id()) != -1
                  })
                )
              }
            } else {
              requests.push(vm.job().fetchStatus());
            }
            requests.push(vm.job().fetchLogs(vm.job().logActive()));
            var profile = $("div[data-jobType] .tab-content .active").data("profile");
            if (profile) {
              requests.push(vm.job().fetchProfile(profile));
            }
            $.when.apply(this, requests).done(function (){
              deferred.resolve();
            });
          });
        }
        return deferred;
      };

      self.fetchLogs = function (name) {
        name = name || 'default';
        vm.apiHelper.cancelActiveRequest(lastFetchLogsRequest);
        lastFetchLogsRequest = $.post("/jobbrowser/api/job/logs?is_embeddable=${ str(is_embeddable).lower() }", {
          cluster: ko.mapping.toJSON(vm.compute),
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          type: ko.mapping.toJSON(self.type),
          name: ko.mapping.toJSON(name)
        }, function (data) {
          if (data.status == 0) {
            var result = self.logsByName();
            result[name] = data.logs.logs;
            self.logsByName(result);
            if (data.logs.logsList && data.logs.logsList.length) {
              var logsListDefaults = self.logsListDefaults();
              self.logsList(logsListDefaults.concat(data.logs.logsList.filter(function(log) { return logsListDefaults.indexOf(log) < 0; })));
            }
            if ($('.jb-panel pre:visible').length > 0){
              $('.jb-panel pre:visible').css('overflow-y', 'auto').height(Math.max(200, $(window).height() - $('.jb-panel pre:visible').offset().top - $('.page-content').scrollTop() - 75));
            }
          } else {
            $(document).trigger("error", data.message);
          }
        });
        return lastFetchLogsRequest;
      };

      self.fetchProfile = function (name, callback) {
        vm.apiHelper.cancelActiveRequest(lastFetchProfileRequest);
        lastFetchProfileRequest = $.post("/jobbrowser/api/job/profile", {
          cluster: ko.mapping.toJSON(vm.compute),
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          app_type: ko.mapping.toJSON(self.type),
          app_property: ko.mapping.toJSON(name),
          app_filters: ko.mapping.toJSON(self.filters),
        }, function (data) {
          if (data.status == 0) {
            self.properties[name](data[name]);
            if (callback) {
              callback(data);
            }
          } else {
            $(document).trigger("error", data.message);
          }
        });
        return lastFetchProfileRequest;
      };

      self.fetchStatus = function () {
        vm.apiHelper.cancelActiveRequest(lastFetchStatusRequest);
        lastFetchStatusRequest = $.post("/jobbrowser/api/job", {
          cluster: ko.mapping.toJSON(vm.compute),
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(self.mainType)
        }, function (data) {
          if (data.status == 0) {
            self.status(data.app.status);
            self.apiStatus(data.app.apiStatus);
            self.progress(data.app.progress);
            self.canWrite(data.app.canWrite);
          } else {
            $(document).trigger("error", data.message);
          }
        });
        return lastFetchStatusRequest;
      };

      self.control = function (action) {
        if (action == 'rerun') {
          $.get('/oozie/rerun_oozie_job/' + self.id() + '/?format=json' + '${ "&is_mini=true" if is_mini else "" | n }', function(response) {
            $('#rerun-modal${ SUFFIX }').modal('show');
            self.rerunModalContent(response);
          });
        } else {
          vm.jobs._control([self.id()], action, function(data) {
            $(document).trigger("info", data.message);
            self.fetchStatus();
          });
        }
      };

      self.updateClusterWorkers = ko.observable(1);
      self.updateClusterAutoResize = ko.observable(false);
      self.updateClusterAutoResizeMin = ko.observable(1);
      self.updateClusterAutoResizeMax = ko.observable(3);
      self.updateClusterAutoResizeCpu = ko.observable(80);
      self.updateClusterAutoPause = ko.observable();

      self.updateClusterShow = function() {
        self.updateClusterWorkers(self.properties['properties']['workerReplicas']());
        self.updateClusterAutoResize(self.properties['properties']['workerAutoResize']());
        if (self.properties['properties']['workerAutoResize']()) {
          self.updateClusterAutoResizeMin(self.properties['properties']['workerAutoResizeMin']());
          self.updateClusterAutoResizeMax(self.properties['properties']['workerAutoResizeMax']());
          self.updateClusterAutoResizeCpu(self.properties['properties']['workerAutoResizeCpu']());
        }
      };

      self.clusterConfigModified = ko.pureComputed(function () {
        return (self.updateClusterWorkers() > 0 && self.updateClusterWorkers() !== self.properties['properties']['workerReplicas']()) ||
            (self.updateClusterAutoResize() !== self.properties['properties']['workerAutoResize']());
      });

      ## TODO Move to control
      self.updateCluster = function() {
        $.post("/metadata/api/analytic_db/update_cluster/", {
          "is_k8": vm.interface().indexOf('dataware2-clusters') != -1,
          "cluster_name": self.id(),
          "workers_group_size": self.updateClusterWorkers(),
          "auto_resize_changed": self.updateClusterAutoResize() !== self.properties['properties']['workerAutoResize'](),
          "auto_resize_enabled": self.updateClusterAutoResize(),
          "auto_resize_min": self.updateClusterAutoResizeMin(),
          "auto_resize_max": self.updateClusterAutoResizeMax(),
          "auto_resize_cpu": self.updateClusterAutoResizeCpu()
        }, function(data) {
          console.log(ko.mapping.toJSON(data));
          ## $(document).trigger("info", ko.mapping.toJSON(data));
          self.updateJob();
        });
      }

      self.troubleshoot = function (action) {
        $.post('/metadata/api/workload_analytics/get_operation_execution_details', {
          operation_id: ko.mapping.toJSON(self.id())
        }, function(data) {
          console.log(ko.mapping.toJSON(data));
        });
      }


      self.workflowGraphLoaded = false;

      self.lastArrowsPosition = {
        top: 0,
        left: 0
      }

      self.initialArrowsDrawingCount = 0;
      self.initialArrowsDrawing = function() {
        if (self.initialArrowsDrawingCount < 20) {
          self.initialArrowsDrawingCount++;
          huePubSub.publish('graph.draw.arrows');
          window.setTimeout(self.initialArrowsDrawing, 100);
        }
        else if (self.initialArrowsDrawingCount < 30){
          self.initialArrowsDrawingCount++;
          huePubSub.publish('graph.draw.arrows');
          window.setTimeout(self.initialArrowsDrawing, 500);
        }
        else {
          self.initialArrowsDrawingCount = 0;
        }
      }

      self.updateArrowsInterval = -1;
      self.updateArrows = function() {
        if ($('canvas').length > 0 && $('canvas').position().top !== self.lastArrowsPosition.top && $('canvas').position().left !== self.lastArrowsPosition.left) {
          self.lastArrowsPosition = $('canvas').position();
        }
        if ($('#workflow-page-graph${ SUFFIX }').is(':visible')){
          if ($('canvas').length === 0){
            huePubSub.publish('graph.draw.arrows');
          }
        }
        else {
          $('canvas').remove();
        }
      }

      self.updateWorkflowGraph = function() {
        huePubSub.publish('graph.stop.refresh.view');

        $('canvas').remove();

        if (vm.job().type() === 'workflow') {
          $('#workflow-page-graph${ SUFFIX }').html('<div class="hue-spinner"><i class="fa fa-spinner fa-spin hue-spinner-center hue-spinner-xlarge"></i></div>');
          $.ajax({
            url: "/oozie/list_oozie_workflow/" + vm.job().id(),
            data: {
              'graph': true,
              'element': 'workflow-page-graph${ SUFFIX }',
              'is_jb2': true
            },
            beforeSend: function (xhr) {
              xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function (response) {
              self.workflowGraphLoaded = true;

              huePubSub.publish('hue4.process.headers', {
                response: response,
                callback: function (r) {
                  $('#workflow-page-graph${ SUFFIX }').html(r);
                  window.clearInterval(self.updateArrowsInterval);
                  self.initialArrowsDrawing();
                  self.updateArrowsInterval = window.setInterval(self.updateArrows, 100, 'jobbrowser');
                }
              });
            }
          });
        }
      };
    };

    var CoordinatorAction = function (vm, job, coordinator) {
      var self = this;
      Job.apply(self, [vm, job]);
      self.coordinator = coordinator;

      self.canWrite = ko.computed(function () {
        return self.coordinator.canWrite();
      });

      self.resumeEnabled = function () {
        return false;
      };
    };

    var Jobs = function (vm) {
      var self = this;

      self.apps = ko.observableArray().extend({ rateLimit: 50 });
      self.runningApps = ko.pureComputed(function() {
        return $.grep(self.apps(), function(app) {
          return app.isRunning();
        });
      });
      self.finishedApps = ko.pureComputed(function() {
        return $.grep(self.apps(), function(app) {
          return !app.isRunning();
        });
      });
      self.totalApps = ko.observable(null);
      self.isCoordinator = ko.observable(false);

      self.loadingJobs = ko.observable(false);
      self.selectedJobs = ko.observableArray();

      self.hasKill = ko.pureComputed(function() {
        return ['jobs', 'workflows', 'schedules', 'bundles', 'queries', 'dataeng-jobs', 'dataeng-clusters', 'dataware-clusters', 'dataware2-clusters'].indexOf(vm.interface()) != -1 && !self.isCoordinator();
      });
      self.killEnabled = ko.pureComputed(function() {
        return self.hasKill() && self.selectedJobs().length > 0 && $.grep(self.selectedJobs(), function(job) {
          return job.killEnabled();
        }).length == self.selectedJobs().length;
      });

      self.hasResume = ko.pureComputed(function() {
        return ['workflows', 'schedules', 'bundles', 'dataware2-clusters'].indexOf(vm.interface()) != -1 && !self.isCoordinator();
      });
      self.resumeEnabled = ko.pureComputed(function() {
        return self.hasResume() && self.selectedJobs().length > 0 && $.grep(self.selectedJobs(), function(job) {
          return job.resumeEnabled();
        }).length == self.selectedJobs().length;
      });

      self.hasRerun = ko.pureComputed(function() {
        return self.isCoordinator();
      });
      self.rerunEnabled = ko.pureComputed(function() {
        return self.hasRerun() && self.selectedJobs().length == 1 && $.grep(self.selectedJobs(), function(job) {
          return job.rerunEnabled();
        }).length == self.selectedJobs().length;
      });

      self.hasPause = ko.pureComputed(function() {
        return ['workflows', 'schedules', 'bundles', 'dataware2-clusters'].indexOf(vm.interface()) != -1 && !self.isCoordinator();
      });
      self.pauseEnabled = ko.pureComputed(function() {
        return self.hasPause() && self.selectedJobs().length > 0 && $.grep(self.selectedJobs(), function(job) {
          return job.pauseEnabled();
        }).length == self.selectedJobs().length;
      });

      self.hasIgnore = ko.pureComputed(function() {
        return self.isCoordinator();
      });
      self.ignoreEnabled = ko.pureComputed(function() {
        return self.hasIgnore() && self.selectedJobs().length > 0 && $.grep(self.selectedJobs(), function(job) {
          return job.ignoreEnabled();
        }).length == self.selectedJobs().length;
      });

      self.textFilter = ko.observable('user:${ user.username } ').extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 1000 } });
      self.statesValuesFilter = ko.observableArray([
        ko.mapping.fromJS({'value': 'completed', 'name': '${_("Succeeded")}', 'checked': false, 'klass': 'green'}),
        ko.mapping.fromJS({'value': 'running', 'name': '${_("Running")}', 'checked': false, 'klass': 'orange'}),
        ko.mapping.fromJS({'value': 'failed', 'name': '${_("Failed")}', 'checked': false, 'klass': 'red'}),
      ]);
      self.statesFilter = ko.computed(function () {
        var checkedStates = ko.utils.arrayFilter(self.statesValuesFilter(), function (state) {
          return state.checked();
        });
        return ko.utils.arrayMap(checkedStates, function(state){
          return state.value()
        });
      });
      self.timeValueFilter = ko.observable(7).extend({ throttle: 500 });
      self.timeUnitFilter = ko.observable('days').extend({ throttle: 500 });
      self.timeUnitFilterUnits = ko.observable([
        {'value': 'days', 'name': '${_("days")}'},
        {'value': 'hours', 'name': '${_("hours")}'},
        {'value': 'minutes', 'name': '${_("minutes")}'},
      ]);

      self.hasPagination = ko.computed(function() {
        return ['workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1;
      });
      self.paginationPage = ko.observable(1);
      self.paginationOffset = ko.observable(1); // Starting index
      self.paginationResultPage = ko.observable(100);
      self.pagination = ko.computed(function() {
        return {
            'page': self.paginationPage(),
            'offset': self.paginationOffset(),
            'limit': self.paginationResultPage()
        };
      });

      self.showPreviousPage = ko.computed(function() {
        return self.paginationOffset() > 1;
      });
      self.showNextPage = ko.computed(function() {
        return self.totalApps() != null && (self.paginationOffset() + self.paginationResultPage()) < self.totalApps();
      });
      self.previousPage = function() {
        self.paginationOffset(self.paginationOffset() - self.paginationResultPage());
      };
      self.nextPage = function() {
        self.paginationOffset(self.paginationOffset() + self.paginationResultPage());
      };

      self.searchFilters = ko.pureComputed(function() {
        return [
          {'text': self.textFilter()},
          {'time': {'time_value': self.timeValueFilter(), 'time_unit': self.timeUnitFilter()}},
          {'states': ko.mapping.toJS(self.statesFilter())},
        ];
      });
      self.searchFilters.subscribe(function() {
        self.paginationOffset(1);
      });
      self.paginationFilters = ko.pureComputed(function() {
        return [
          {'pagination': self.pagination()},
        ];
      });
      self.filters = ko.pureComputed(function() {
        return self.searchFilters().concat(self.paginationFilters());
      });
      self.filters.subscribe(function(value) {
        self.fetchJobs();
      });


      self._fetchJobs = function (callback) {
        return $.post("/jobbrowser/api/jobs/" + vm.interface(), {
          cluster: ko.mapping.toJSON(vm.compute),
          interface: ko.mapping.toJSON(vm.interface),
          filters: ko.mapping.toJSON(self.filters),
        }, function (data) {
          if (data.status == 0) {
            if (data.apps && data.apps.length) {
              huePubSub.publish('jobbrowser.data', data.apps);
            }
            if (callback) {
              callback(data);
            };
          } else {
            $(document).trigger("error", data.message);
          }
        });
      };

      var lastFetchJobsRequest = null;
      var lastUpdateJobsRequest = null;
      self.showJobCountBanner = ko.pureComputed(function() {
        return self.apps().length == ${ MAX_JOB_FETCH.get() };
      });

      self.fetchJobs = function () {
        vm.apiHelper.cancelActiveRequest(lastUpdateJobsRequest);
        vm.apiHelper.cancelActiveRequest(lastFetchJobsRequest);

        self.loadingJobs(true);
        vm.job(null);
        lastFetchJobsRequest = self._fetchJobs(function(data) {
          var apps = [];
          if (data && data.apps) {
            data.apps.forEach(function (job) {
              apps.push(new Job(vm, job));
            });
          }
          self.apps(apps);
          self.totalApps(data.total);
        }).always(function () {
          self.loadingJobs(false);
        });
      }

      self.updateJobs = function () {
        vm.apiHelper.cancelActiveRequest(lastUpdateJobsRequest);

        lastFetchJobsRequest = self._fetchJobs(function(data) {
          if (data && data.apps) {
            var i = 0, j = 0;
            var newJobs = [];

            while ((self.apps().length == 0 || i < self.apps().length) && j < data.apps.length) { // Nothing displayed or compare existing
              if (self.apps().length == 0 || self.apps()[i].id() != data.apps[j].id) {
                // New Job
                newJobs.unshift(new Job(vm, data.apps[j]));
                j++;
              } else {
                // Updated jobs
                if (self.apps()[i].status() != data.apps[j].status) {
                  self.apps()[i].status(data.apps[j].status);
                  self.apps()[i].apiStatus(data.apps[j].apiStatus);
                  self.apps()[i].canWrite(data.apps[j].canWrite);
                }
                i++;
                j++;
              }
            }

            if (i < self.apps().length) {
              self.apps.splice(i, self.apps().length - i);
            }

            newJobs.forEach(function (job) {
              self.apps.unshift(job);
            });

            self.totalApps(data.total);
          }
        });
        return lastFetchJobsRequest;
      };

      self.createClusterShow = ko.observable(false);
      self.createClusterName = ko.observable('');
      self.createClusterWorkers = ko.observable(1);
      self.createClusterShowWorkers = ko.observable(false);
      self.createClusterAutoResize = ko.observable(false);
      self.createClusterAutoPause = ko.observable(false);

      self.createClusterFormReset = function() {
        self.createClusterName('');
        self.createClusterWorkers(1);
        self.createClusterAutoResize(false);
        self.createClusterAutoPause(false);
      }

      self.createCluster = function() {
        if (vm.interface().indexOf('dataeng') != -1) {
          $.post("/metadata/api/dataeng/create_cluster/", {
            "cluster_name": "cluster_name",
            "cdh_version": "CDH515",
            "public_key": "public_key",
            "instance_type": "m4.xlarge",
            "environment_name": "crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:analytics/236ebdda-18bd-428a-9d2b-cd6973d42946",
            "workers_group_size": "3",
            "namespace_name": "crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:analytics/7ea35fe5-dbc9-4b17-92b1-97a1ab32e410"
          }, function(data) {
            console.log(ko.mapping.toJSON(data));
            $(document).trigger("info", ko.mapping.toJSON(data));
            self.updateJobs();
            huePubSub.publish('context.catalog.refresh');
          });
        } else {
          $.post("/metadata/api/analytic_db/create_cluster/", {
            "is_k8": vm.interface().indexOf('dataware2-clusters') != -1,
            "cluster_name": self.createClusterName(),
            "cluster_hdfs_host": "hdfs-namenode",
            "cluster_hdfs_port": 9820,
            "cdh_version": "CDH515",
            "public_key": "public_key",
            "instance_type": "m4.xlarge",
            "environment_name": "crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:jheyming-secure/b4e6d99a-261f-4ada-9b4a-576aa0af8979",
            "workers_group_size": self.createClusterWorkers(),
            "namespace_name": "crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:analytics/7ea35fe5-dbc9-4b17-92b1-97a1ab32e410"
          }, function(data) {
            console.log(ko.mapping.toJSON(data));
            self.createClusterFormReset();
            ##$(document).trigger("info", ko.mapping.toJSON(data));
            self.updateJobs();
            huePubSub.publish('context.catalog.refresh');
          });
        }
        self.createClusterShow(false);
      };

      self.control = function (action) {
        if (action === 'rerun') {
          $.get('/oozie/rerun_oozie_coord/' + vm.job().id() + '/?format=json' + '${ "&is_mini=true" if is_mini else "" | n }', function(response) {
            $('#rerun-modal${ SUFFIX }').modal('show');
            vm.job().rerunModalContent(response);
            // Force Knockout to handle the update of rerunModalContent before trying to modify its DOM
            ko.tasks.runEarly();

            var frag = document.createDocumentFragment();
            vm.job().coordinatorActions().selectedJobs().forEach(function (item) {
              var option = $('<option>', {
                value: item.properties.number(),
                selected: true
              });
              option.appendTo($(frag));
            });
            $('#id_actions${ SUFFIX }').find('option').remove();
            $(frag).appendTo('#id_actions${ SUFFIX }');
          });
        } else if (action === 'ignore') {
          $.post('/oozie/manage_oozie_jobs/' + vm.job().id() + '/ignore', {
            actions: $.map(vm.job().coordinatorActions().selectedJobs(), function(wf) {
              return wf.properties.number();
            }).join(' ')
          }, function(response) {
            vm.job().apiStatus('RUNNING');
            vm.job().updateJob();
          });
        } else {
          self._control(
            $.map(self.selectedJobs(), function(job) {
              return job.id();
            }),
            action,
            function(data) {
              $(document).trigger("info", data.message);
              self.updateJobs();
            }
          )
        }
      }

      self._control = function (app_ids, action, callback) {
        $.post("/jobbrowser/api/job/action/" + vm.interface() + "/" + action, {
          app_ids: ko.mapping.toJSON(app_ids),
          interface: ko.mapping.toJSON(vm.interface),
          operation: ko.mapping.toJSON({action: action})
        }, function (data) {
          if (data.status === 0) {
            if (callback) {
              callback(data);
            }
            if (vm.interface().indexOf('clusters') !== -1 && action === 'kill') {
              huePubSub.publish('context.catalog.refresh');
              self.selectedJobs([]);
            }
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
        });
      };
    };

    var JobBrowserViewModel = function () {
      var self = this;

      self.apiHelper = window.apiHelper;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
      self.appConfig = ko.observable();
      self.clusterType = ko.observable();
      self.isMini = ko.observable(false);

      self.cluster = ko.observable();
      self.compute = ko.observable();
      self.compute.subscribe(function () {
        if (self.interface()) {
          self.jobs.fetchJobs();
        }
      });

      self.availableInterfaces = ko.pureComputed(function () {
        var jobsInterfaceCondition = function () {
          return self.appConfig() && self.appConfig()['browser'] && self.appConfig()['browser']['interpreter_names'].indexOf('yarn') != -1 && (!self.cluster() || self.cluster()['type'].indexOf('altus') == -1);
        };
        var dataEngInterfaceCondition = function () {
          return self.cluster() && self.cluster()['type'] == 'altus-de';
        };
        var enginesInterfaceCondition = function () {
          return self.cluster() && self.cluster()['type'] == 'altus-engines';
        };
        var dataWarehouseInterfaceCondition = function () {
          return self.cluster() && self.cluster()['type'] == 'altus-dw';
        };
        var dataWarehouse2InterfaceCondition = function () {
          return self.cluster() && self.cluster()['type'] == 'altus-dw2';
        };
        var schedulerInterfaceCondition = function () {
          return '${ user.has_hue_permission(action="access", app="oozie") }' == 'True' && (!self.cluster() || self.cluster()['type'].indexOf('altus') == -1) && self.appConfig() && self.appConfig()['scheduler'];
        };
        var schedulerExtraInterfaceCondition = function () {
          return '${ is_mini }' == 'False' && schedulerInterfaceCondition();
        };
        var livyInterfaceCondition = function () {
          return '${ is_mini }' == 'False' && self.appConfig() && self.appConfig()['editor'] && self.appConfig()['editor']['interpreter_names'].indexOf('pyspark') != -1 && (!self.cluster() || self.cluster()['type'].indexOf('altus') == -1);
        };
        var queryInterfaceCondition = function () {
          return '${ ENABLE_QUERY_BROWSER.get() }' == 'True' && self.appConfig() && self.appConfig()['editor'] && self.appConfig()['editor']['interpreter_names'].indexOf('impala') != -1 && (!self.cluster() || self.cluster()['type'].indexOf('altus') == -1);
        };

        var interfaces = [
          {'interface': 'jobs', 'label': '${ _ko('Jobs') }', 'condition': jobsInterfaceCondition},
          {'interface': 'dataeng-jobs', 'label': '${ _ko('Jobs') }', 'condition': dataEngInterfaceCondition},
          {'interface': 'dataeng-clusters', 'label': '${ _ko('Clusters') }', 'condition': dataEngInterfaceCondition},
          {'interface': 'dataware-clusters', 'label': '${ _ko('Clusters') }', 'condition': dataWarehouseInterfaceCondition},
          {'interface': 'dataware2-clusters', 'label': '${ _ko('Warehouses') }', 'condition': dataWarehouse2InterfaceCondition},
          {'interface': 'engines', 'label': '${ _ko('') }', 'condition': enginesInterfaceCondition},
          {'interface': 'queries', 'label': '${ _ko('Queries') }', 'condition': queryInterfaceCondition},
          {'interface': 'workflows', 'label': '${ _ko('Workflows') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'schedules', 'label': '${ _ko('Schedules') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'bundles', 'label': '${ _ko('Bundles') }', 'condition': schedulerExtraInterfaceCondition},
          {'interface': 'slas', 'label': '${ _ko('SLAs') }', 'condition': schedulerExtraInterfaceCondition},
          {'interface': 'livy-sessions', 'label': '${ _ko('Livy') }', 'condition': livyInterfaceCondition},
        ];

        return interfaces.filter(function (i) {
          return i.condition();
        });
      });

      self.availableInterfaces.subscribe(function (newInterfaces) {
        if (self.interface() && !newInterfaces.some(function (newInterface) {
          return newInterface.interface === self.interface();
        })) {
          self.selectInterface(newInterfaces[0]);
        }
      });

      self.slasLoadedOnce = false;
      self.slasLoading = ko.observable(true);
      self.loadSlaPage = function(){
        if (!self.slasLoadedOnce) {
          $.ajax({
            url: '/oozie/list_oozie_sla/?is_embeddable=true',
            beforeSend: function (xhr) {
              xhr.setRequestHeader('X-Requested-With', 'Hue');
            },
            dataType: 'html',
            success: function (response) {
              self.slasLoading(false);
              $('#slas').html(response);
            }
          });
        }
      };

      self.oozieInfoLoadedOnce = false;
      self.oozieInfoLoading = ko.observable(true);
      self.loadOozieInfoPage = function(){
        if (!self.oozieInfoLoadedOnce) {
          self.oozieInfoLoadedOnce = true;
          $.ajax({
            url: '/oozie/list_oozie_info/?is_embeddable=true',
            beforeSend: function (xhr) {
              xhr.setRequestHeader('X-Requested-With', 'Hue');
            },
            dataType: 'html',
            success: function (response) {
              self.oozieInfoLoading(false);
              $('#oozieInfo').html(response);
            }
          });
        }
      };

      self.interface = ko.observable();
      self.isValidInterface = function(name) {
        var flatAvailableInterfaces = self.availableInterfaces().map(function (i) {
          return i.interface;
        });
        if (flatAvailableInterfaces.indexOf(name) != -1 || name == 'oozie-info') {
          return name;
        } else {
          return flatAvailableInterfaces[0];
        }
      };
      self.selectInterface = function(interface) {
        interface = self.isValidInterface(interface);
        self.interface(interface);
        self.resetBreadcrumbs();

        % if not is_mini:
          huePubSub.publish('graph.stop.refresh.view');
          if (window.location.hash !== '#!' + interface) {
            hueUtils.changeURL('#!' + interface);
          }
        % endif
        self.jobs.selectedJobs([]);
        self.job(null);

        if (interface === 'slas'){
          % if not is_mini:
            self.loadSlaPage();
          % endif
        }
        else if (interface === 'oozie-info') {
          % if not is_mini:
            self.loadOozieInfoPage();
          % endif
        }
        else {
          self.jobs.fetchJobs();
        }
      };

      self.onClusterSelect = function () {
        var interfaceToSet = self.interface();
        if (!self.availableInterfaces().some(function (availableInterface) {
          return availableInterface.interface === interfaceToSet;
        })) {
          interfaceToSet = self.availableInterfaces()[0].interface;
        }
        self.selectInterface(interfaceToSet);
      };

      self.jobs = new Jobs(self);
      self.job = ko.observable();

      var updateJobTimeout = -1;
      var updateJobsTimeout = -1;
      self.job.subscribe(function(val) {
        self.monitorJob(val);
      });

      self.monitorJob = function(job) {
        window.clearTimeout(updateJobTimeout);
        window.clearTimeout(updateJobsTimeout);
        if (self.interface() && self.interface() !== 'slas' && self.interface() !== 'oozie-info'){
          if (job) {
            if (job.apiStatus() === 'RUNNING') {
              var _updateJob = function () {
                var def = job.updateJob();
                if (def) {
                  def.done(function () {
                    updateJobTimeout = setTimeout(_updateJob, window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS);
                  });
                }
              };
              updateJobTimeout = setTimeout(_updateJob, window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS);
            }
          }
          else {
            var _updateJobs = function () {
              self.jobs.updateJobs().done(function () {
                setTimeout(_updateJobs, window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS);
              });
            };
            updateJobsTimeout = setTimeout(_updateJobs, window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS);
          }
        }
      };

      self.breadcrumbs = ko.observableArray([]);
      self.resetBreadcrumbs = function(extraCrumbs) {
        var crumbs = [{'id': '', 'name': self.interface(), 'type': self.interface()}]
        if (extraCrumbs) {
          crumbs = crumbs.concat(extraCrumbs);
        }
        self.breadcrumbs(crumbs);
      };

      self.resetBreadcrumbs();

      self.getHDFSPath = function (path) {
        if (path.startsWith('hdfs://')) {
          var bits = path.substr(7).split('/');
          bits.shift();
          return '/' + bits.join('/');
        }
        return path;
      };

      self.formatProgress = function (progress) {
        if (typeof progress === 'function') {
          progress = progress();
        }
        if (!isNaN(progress)) {
          return Math.round(progress*100)/100 + '%';
        }
        return progress;
      };

      self.load = function() {
        var h = window.location.hash;
        % if not is_mini:
        huePubSub.publish('graph.stop.refresh.view');
        % endif

        h = h.indexOf('#!') === 0 ? h.substr(2) : '';
        switch (h) {
          case '':
            h = 'jobs';
          case 'slas':
          case 'oozie-info':
          case 'jobs':
          case 'queries':
          case 'workflows':
          case 'schedules':
          case 'bundles':
          case 'dataeng-clusters':
          case 'dataware-clusters':
          case 'dataware2-clusters':
          case 'engines':
          case 'dataeng-jobs':
          case 'livy-sessions':
            self.selectInterface(h);
            break;
          default:
            if (h.indexOf('id=') === 0 && !self.isMini()){
              new Job(self, {id: h.substr(3)}).fetchJob();
            }
            else {
              self.selectInterface('reset');
            }
        }
      };
    };


    $(document).ready(function () {
      var jobBrowserViewModel = new JobBrowserViewModel();
      var openJob = function(id) {
        if (jobBrowserViewModel.job() == null) {
          jobBrowserViewModel.job(new Job(jobBrowserViewModel, {}));
        }
        jobBrowserViewModel.job().id(id);
        jobBrowserViewModel.job().fetchJob();
      }
      % if not is_mini:
        ko.applyBindings(jobBrowserViewModel, $('#jobbrowserComponents')[0]);

        huePubSub.subscribe('oozie.action.logs.click', function (widget) {
          $.get(widget.logsURL(), {
              format: 'link'
            },
            function(data) {
              var id = data.job || data.attemptid;
              if (id) {
                openJob(id);
              } else {
                $(document).trigger("error", '${ _("No log available") }');
              }
            }
          );
        }, 'jobbrowser');

        huePubSub.subscribe('oozie.action.click', function (widget) {
          openJob(widget.externalId());
        }, 'jobbrowser');

        huePubSub.subscribe('browser.job.open.link', function (id) {
          openJob(id);
        }, 'jobbrowser');
      % else:
        ko.applyBindings(jobBrowserViewModel, $('#jobbrowserMiniComponents')[0]);
        jobBrowserViewModel.isMini(true);
      % endif

      huePubSub.subscribe('app.gained.focus', function (app) {
        if (app === 'jobbrowser') {
          huePubSub.publish('graph.draw.arrows');
          loadHash();
        }
      }, 'jobbrowser');

      var loadHash = function () {
        if (window.location.pathname.indexOf('jobbrowser') > -1) {
          jobBrowserViewModel.load();
        }
      };

      window.onhashchange = function () {
        loadHash();
      };

      huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
        jobBrowserViewModel.appConfig(clusterConfig && clusterConfig['app_config']);
        jobBrowserViewModel.clusterType(clusterConfig && clusterConfig['cluster_type']);
        loadHash();
      });

      huePubSub.publish('cluster.config.get.config');

      huePubSub.subscribe('submit.rerun.popup.return${ SUFFIX }', function (data) {
        $.jHueNotify.info('${_("Rerun submitted.")}');
        $('#rerun-modal${ SUFFIX }').modal('hide');

        jobBrowserViewModel.job().apiStatus('RUNNING');
        jobBrowserViewModel.monitorJob(jobBrowserViewModel.job());
      }, '${ "jobbrowser" if not is_mini else "" }');

      % if is_mini:
        huePubSub.subscribe('mini.jb.navigate', function (options) {
          if (options.compute) {
            jobBrowserViewModel.compute(options.compute);
          }
          $('#jobsPanel .nav-pills li').removeClass('active');
          interface = jobBrowserViewModel.isValidInterface(options.section);
          $('#jobsPanel .nav-pills li[data-interface="' + interface + '"]').addClass('active');
          jobBrowserViewModel.selectInterface(interface);
        });
        huePubSub.subscribe('mini.jb.open.job', openJob);
        huePubSub.subscribe('mini.jb.expand', function () {
          if (jobBrowserViewModel.job()) {
            huePubSub.publish('open.link', '/jobbrowser/#!id=' + jobBrowserViewModel.job().id());
          }
          else {
            huePubSub.publish('open.link', '/jobbrowser/#!' + jobBrowserViewModel.interface());
          }
        });
      % endif

      $(document).on('shown', '.jb-logs-link', function (e) {
        var dest = $(e.target).attr('href');
        if (dest.indexOf('logs') > -1 && $(dest).find('pre:visible').length > 0){
          $(dest).find('pre').css('overflow-y', 'auto').height(Math.max(200, $(window).height() - $(dest).find('pre').offset().top - $('.page-content').scrollTop() - 75));
        }
      });
    });
  })();
</script>
</span>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
