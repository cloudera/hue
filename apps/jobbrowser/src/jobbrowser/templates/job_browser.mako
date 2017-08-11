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

  from desktop import conf
  from desktop.views import commonheader, commonfooter, _ko
  from jobbrowser.conf import DISABLE_KILLING_JOBS, MAX_JOB_FETCH
%>

<%
SUFFIX = is_mini and "-mini" or ""
%>

% if not is_embeddable:
${ commonheader("Job Browser", "jobbrowser", user, request) | n,unicode }
<%namespace name="assist" file="/assist.mako" />
% endif

<span class="notebook">

<link rel="stylesheet" href="${ static('desktop/ext/css/basictable.css') }">

% if not is_embeddable:
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
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
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.basictable.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>

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


% if not is_mini:
<div class="navbar hue-title-bar">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              <a href="/${app_name}">
                <img src="${ static('jobbrowser/art/icon_jobbrowser_48.png') }" class="app-icon" alt="${ _('Job browser icon') }"/>
                ${ _('Job Browser') }
              </a>
            </li>
            <!-- ko foreach: availableInterfaces -->
              <li data-bind="css: {'active': $parent.interface() === interface}, visible: condition()">
                <a class="pointer" data-bind="click: function(){ $parent.selectInterface(interface); }, text: label"></a>
              </li>
            <!-- /ko -->
          </ul>
          % if not hiveserver2_impersonation_enabled:
            <div class="pull-right label label-warning" style="margin-top: 16px">${ _("Hive jobs are running as the 'hive' user") }</div>
          % endif
        </div>
      </div>
    </div>
</div>
% endif

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
              <input type="text" class="input-large" data-bind="clearable: jobs.textFilter, valueUpdate: 'afterkeydown'" placeholder="${_('Filter by id, name, user...')}" />
              <!-- ko if: jobs.statesValuesFilter -->
              <span data-bind="foreach: jobs.statesValuesFilter">
                <label class="checkbox">
                  <div class="pull-left margin-left-5 status-border status-content" data-bind="css: value, hueCheckbox: checked"></div>
                  <div class="inline-block" data-bind="text: name, toggle: checked"></div>
                </label>
              </span>
              <!-- /ko -->

              <!-- ko ifnot: $root.isMini -->
              ${_('in the last')} <input class="input-mini no-margin" type="number" min="1" max="3650" data-bind="value: jobs.timeValueFilter">
              <select class="input-small no-margin" data-bind="value: jobs.timeUnitFilter, options: jobs.timeUnitFilterUnits, optionsText: 'name', optionsValue: 'value'">
                <option value="days">${_('days')}</option>
                <option value="hours">${_('hours')}</option>
                <option value="minutes">${_('minutes')}</option>
              </select>

              <a class="btn" title="${ _('Refresh') }" data-bind="click: jobs.updateJobs">
                <i class="fa fa-refresh"></i>
              </a>

              <div data-bind="template: { name: 'job-actions${ SUFFIX }', 'data': jobs }" class="pull-right"></div>
              <!-- /ko -->
            </form>

            <div data-bind="visible: jobs.showJobCountBanner" class="pull-center alert alert-warning">${ _("Showing oldest %s jobs. Use days filter to get the recent ones.") % MAX_JOB_FETCH.get() }</div>

            <div class="card card-small">
              <!-- ko hueSpinner: { spin: jobs.loadingJobs(), center: true, size: 'xlarge' } --><!-- /ko -->
              <!-- ko ifnot: jobs.loadingJobs() -->
                <!-- ko if: $root.isMini -->
                <ul class="unstyled status-border-container" id="jobsTable" data-bind="foreach: jobs.apps">
                  <li class="status-border pointer" data-bind="css: {'completed': apiStatus() == 'SUCCEEDED', 'running': isRunning(), 'failed': apiStatus() == 'FAILED'}, click: fetchJob">
                    <span class="muted pull-left" data-bind="momentFromNow: {data: submitted, interval: 10000, titleFormat: 'LLL'}"></span><span class="muted">&nbsp;-&nbsp;</span><span class="muted" data-bind="text: status"></span></td>
                    <span class="muted pull-right" data-bind="text: duration().toHHMMSS()"></span>
                    <div class="clearfix"></div>
                    <strong class="pull-left" data-bind="text: type"></strong>
                    <div class="inline-block pull-right"><i class="fa fa-user muted"></i> <span data-bind="text: user"></span></div>
                    <div class="clearfix"></div>
                    <div class="pull-left" data-bind="ellipsis: {data: name(), length: 40 }"></div>
                    <div class="pull-right muted" data-bind="text: id"></div>
                    <div class="clearfix"></div>
                  </li>
                  <div class="status-bar status-background" data-bind="css: {'running': isRunning()}, style: {'width': progress() + '%'}"></div>
                </ul>
                <!-- /ko -->
                <!-- ko ifnot: $root.isMini -->
                <table id="jobsTable" class="datatables table table-condensed status-border-container">
                  <thead>
                  <tr>
                    <th width="1%" class="vertical-align-middle"><div class="select-all hueCheckbox fa" data-bind="hueCheckAll: { allValues: jobs.apps, selectedValues: jobs.selectedJobs }"></div></th>
                    <th width="15%">${_('Id')}</th>
                    <th width="20%">${_('Name')}</th>
                    <th width="6%">${_('User')}</th>
                    <th width="6%">${_('Type')}</th>
                    <th width="5%">${_('Status')}</th>
                    <th width="3%">${_('Progress')}</th>
                    <th width="5%">${_('Group')}</th>
                    <th width="10%" data-bind="text: interface() != 'schedules' ? '${_('Started')}' : '${_('Modified')}'"></th>
                    <th width="6%">${_('Duration')}</th>
                  </tr>
                  </thead>
                  <tbody data-bind="foreach: jobs.apps">
                    <tr class="status-border pointer" data-bind="css: {'completed': apiStatus() == 'SUCCEEDED', 'running': isRunning(), 'failed': apiStatus() == 'FAILED'}, click: fetchJob">
                      <td data-bind="click: function() {}, clickBubble: false">
                        <div class="hueCheckbox fa" data-bind="click: function() {}, clickBubble: false, multiCheck: '#jobsTable', value: $data, hueChecked: $parent.jobs.selectedJobs"></div>
                      </td>
                      <td data-bind="text: id"></td>
                      <td data-bind="text: name"></td>
                      <td data-bind="text: user"></td>
                      <td data-bind="text: type"></td>
                      <td data-bind="text: status"></td>
                      <td data-bind="text: $root.formatProgress(progress)"></td>
                      <td data-bind="text: queue"></td>
                      <td data-bind="moment: {data: submitted, format: 'LLL'}"></td>
                      <td data-bind="text: duration().toHHMMSS()"></td>
                    </tr>
                  </tbody>
                </table>
                <!-- /ko -->
              <!-- /ko -->
            </div>
            <!-- /ko -->

          <!-- ko if: $root.job() -->
          <!-- ko with: $root.job() -->
            <!-- ko if: mainType() == 'jobs' -->
              <div class="jb-panel" data-bind="template: { name: 'job-page${ SUFFIX }' }"></div>
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
  <div id="rerun-modal${ SUFFIX }" class="modal hide" data-bind="html: $root.job().rerunModalContent"></div>
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
    ${ _('jobs') }
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

  <!-- ko if: type() == 'IMPALA' -->
    <div data-bind="template: { name: 'job-impala-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'SPARK' -->
    <div data-bind="template: { name: 'job-spark-page${ SUFFIX }', data: $root.job() }"></div>
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
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <li data-bind="visible: id() != name()" class="nav-header">${ _('Name') }</li>
          <li data-bind="visible: id() != name(), attr: { title: name }"><span data-bind="text: name"></span></li>
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
            <li class="${ name == 'default' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); }, text: '${ name }'"></a></li>
          % endfor
          </ul>

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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() !== 'FAILED' && progress() < 100, 'progress-success': apiStatus() !== 'FAILED' && progress() === 100, 'progress-danger': apiStatus() === 'FAILED'}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko with: properties -->
          <li class="nav-header">${ _('State') }</li>
          <li><span data-bind="text: state"></span></li>
          <li class="nav-header">${ _('Start time') }</li>
          <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
          <li class="nav-header">${ _('Successful attempt') }</li>
          <li><span data-bind="text: successfulAttempt"></span></li>
          <li class="nav-header">${ _('Finish time') }</li>
          <li><span data-bind="moment: {data: finishTime, format: 'LLL'}"></span></li>
          <li class="nav-header">${ _('Elapsed time') }</li>
          <li><span data-bind="text: elapsedTime().toHHMMSS()"></span></li>
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
            <li class="${ name == 'stdout' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); }, text: '${ name }'"></a></li>
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': apiStatus() == 'RUNNING', 'progress-success': apiStatus() == 'SUCCEEDED', 'progress-danger': apiStatus() == 'FAILED'}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
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
            <li class="${ name == 'stdout' and 'active' or '' }"><a href="javascript:void(0)" data-bind="click: function(data, e) { $(e.currentTarget).parent().siblings().removeClass('active'); $(e.currentTarget).parent().addClass('active'); fetchLogs('${ name }'); }, text: '${ name }'"></a></li>
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


<script type="text/html" id="job-impala-page${ SUFFIX }">
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
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration().toHHMMSS()"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a href="#job-spark-page-properties${ SUFFIX }" data-toggle="tab">${ _('Properties') }</a></li>

        <li class="pull-right" data-bind="template: { name: 'job-actions${ SUFFIX }' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" id="job-spark-page-properties${ SUFFIX }">
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


<script type="text/html" id="dataeng-job-page${ SUFFIX }">
  <button class="btn" title="${ _('Troubleshoot') }" data-bind="click: troubleshoot">
    <i class="fa fa-tachometer"></i> ${ _('Troubleshoot') }
  </button>

  <!-- ko if: type() == 'dataeng-job-HIVE' -->
    <div data-bind="template: { name: 'dataeng-job-hive-page${ SUFFIX }', data: $root.job() }"></div>
  <!-- /ko -->
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': isRunning(), 'progress-success': apiStatus() === 'SUCCEEDED' }">
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
    <button class="btn btn-danger disable-feedback" title="${_('Stop selected')}" data-bind="click: function() { control('kill'); }, enable: killEnabled">
      ## TODO confirmation
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-danger': apiStatus() === 'FAILED', 'progress-warning': isRunning(), 'progress-success': apiStatus() === 'SUCCEEDED' }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration().toHHMMSS()"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
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
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        %if not is_mini:
        <li class="active"><a href="#workflow-page-graph${ SUFFIX }" data-toggle="tab">${ _('Graph') }</a></li>
        %endif
        <li><a href="#workflow-page-metadata${ SUFFIX }" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#workflow-page-metadata${ SUFFIX }\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a class="jb-logs-link" href="#workflow-page-logs${ SUFFIX }" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#workflow-page-tasks${ SUFFIX }" data-toggle="tab">${ _('Tasks') }</a></li>
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

        <div class="tab-pane" id="workflow-page-tasks${ SUFFIX }">
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
          <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
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
          <div data-bind="readonlyXML: properties['conf']"></div>
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
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
          <li class="nav-header">${ _('Next Run') }</li>
          <li><span data-bind="text: properties['nextTime']"></span></li>
          <li class="nav-header">${ _('Total Actions') }</li>
          <li><span data-bind="text: properties['total_actions']"></span></li>
          <li class="nav-header">${ _('End time') }</li>
          <li><span data-bind="text: properties['endTime']"></span></li>
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
              <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
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
                  <div class="hueCheckbox fa" data-bind="click: function() {}, clickBubble: false, multiCheck: '#schedulesTable', value: $data, hueChecked: $parent.selectedJobs"></div>
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
          <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
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
            <a data-bind="hueLink: doc_url" href="javascript: void(0);" title="${ _('Open in editor') }">
              <span data-bind="text: name"></span>
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
          <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>

</script>

<script type="text/html" id="render-properties${ SUFFIX }">
  <!-- ko hueSpinner: { spin: !$data.properties, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko if: $data.properties -->
  <form class="form-search">
    <input type="text" data-bind="clearable: $parent.propertiesFilter, valueUpdate: 'afterkeydown'" class="input-xlarge search-query" placeholder="${_('Text Filter')}">
  </form>
  <br>
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
  <table id="jobbrowserJobMetadataTable" class="table table-condensed">
    <thead>
    <tr>
      <th>${ _('Name') }</th>
      <th width="50%">${ _('Value') }</th>
    </tr>
    </thead>
    <tbody data-bind="foreach: property">
      <tr>
        <td data-bind="text: name"></td>
        <td>
          <!-- ko template: { name: 'link-or-text${ SUFFIX }', data: { name: name, value: value } } --><!-- /ko -->
        </td>
      </tr>
    </tbody>
  </table>
  <!-- /ko -->
</script>


<script type="text/html" id="link-or-text${ SUFFIX }">
  <!-- ko if: typeof $data.value === 'string' -->
    <!-- ko if: $data.name.indexOf('dir') > -1 || $data.name.indexOf('path') > -1 || $data.name.indexOf('output') > -1 || $data.name.indexOf('input') > -1 || $data.value.startsWith('/') ||  $data.value.startsWith('hdfs://') -->
      <a href="javascript:void(0)" data-bind="hueLink: '/filebrowser/view=' + $root.getHDFSPath($data.value) , text: $data.value"></a>
    <!-- /ko -->
    <!-- ko ifnot: $data.name.indexOf('dir') > -1 || $data.name.indexOf('path') > -1 || $data.name.indexOf('output') > -1 || $data.name.indexOf('input') > -1 || $data.value.startsWith('/') ||  $data.value.startsWith('hdfs://') -->
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
      self.name = ko.observableDefault(job.name || job.id);
      self.type = ko.observableDefault(job.type);

      self.status = ko.observableDefault(job.status);
      self.apiStatus = ko.observableDefault(job.apiStatus);
      self.progress = ko.observableDefault(job.progress);
      self.isRunning = ko.computed(function() {
        return self.apiStatus() == 'RUNNING' || self.apiStatus() == 'PAUSED';
      });

      self.user = ko.observableDefault(job.user);
      self.queue = ko.observableDefault(job.queue);
      self.cluster = ko.observableDefault(job.cluster);
      self.duration = ko.observableDefault(job.duration);
      self.submitted = ko.observableDefault(job.submitted);
      self.canWrite = ko.observableDefault(job.canWrite == true);

      self.logs = ko.observable('');

      self.properties = ko.mapping.fromJS(job.properties || {});
      self.mainType = ko.observable(vm.interface());

      self.coordinatorActions = ko.pureComputed(function() {
        if (self.mainType() == 'schedules' && self.properties['tasks']) {
          var apps = [];
          self.properties['tasks']().forEach(function (instance) {
            var job = new Job(vm, ko.mapping.toJS(instance));
            job.resumeEnabled = function() { return false };
            job.properties = instance;
            apps.push(job);
          });
          var instances = new Jobs(vm);
          instances.apps(apps)
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
        return ['MAPREDUCE', 'SPARK', 'workflow', 'schedule', 'bundle'].indexOf(self.type()) != -1;
      });
      self.killEnabled = ko.pureComputed(function() {
        return self.hasKill() && self.canWrite() && (self.apiStatus() == 'RUNNING' || self.apiStatus() == 'PAUSED');
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

      self._fetchJob = function (callback) {
        return $.post("/jobbrowser/api/job", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface)
        }, function (data) {
          if (data.status == 0) {
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
        if (/oozie-oozi-W/.test(self.id())) {
          interface = 'workflows';
        }
        else if (/oozie-oozi-C/.test(self.id())) {
          interface = 'schedules';
        }
        else if (/oozie-oozi-B/.test(self.id())) {
          interface = 'bundles';
        }
        else if (/[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}/.test(self.id())) {
          interface = 'dataeng-jobs';
        }
        else if (/livy-[0-9]+/.test(self.id())) {
          interface = 'livy-sessions';
        }

        interface = vm.isValidInterface(interface);
        vm.interface(interface);

        lastFetchJobRequest = self._fetchJob(function (data) {
          if (data.status == 0) {
            vm.interface(interface);
            vm.job(new Job(vm, data.app));
            if (window.location.hash !== '#!id=' + vm.job().id()) {
              hueUtils.changeURL('#!id=' + vm.job().id());
            }
            var crumbs = [];

            if (/^attempt_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
              crumbs.push({'id': vm.job().properties['task_id'], 'name': vm.job().properties['task_id'], 'type': 'task'});
            }
            if (/^task_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
            }
            var oozieWorkflow = vm.job().name().match(/oozie:launcher:T=.+?:W=.+?:A=.+?:ID=(.+?-oozie-oozi-W)$/i);
            if (oozieWorkflow) {
              crumbs.push({'id': oozieWorkflow[1], 'name': oozieWorkflow[1], 'type': 'workflow'});
            }

            if (/-oozie-oozi-W@/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['workflow_id'], 'name': vm.job().properties['workflow_id'], 'type': 'workflow'});
            }
            else if (/-oozie-oozi-W/.test(vm.job().id())) {
              if (vm.job().properties['bundle_id']()) {
                crumbs.push({'id': vm.job().properties['bundle_id'](), 'name': vm.job().properties['bundle_id'](), 'type': 'bundle'});
              }
              if (vm.job().properties['coordinator_id']()) {
                crumbs.push({'id': vm.job().properties['coordinator_id'](), 'name': vm.job().properties['coordinator_id'](), 'type': 'schedule'});
              }
            }
            else if (/-oozie-oozi-C/.test(vm.job().id())) {
              if (vm.job().properties['bundle_id']()) {
                crumbs.push({'id': vm.job().properties['bundle_id'](), 'name': vm.job().properties['bundle_id'](), 'type': 'bundle'});
              }
            }

            crumbs.push({'id': vm.job().id(), 'name': vm.job().name(), 'type': vm.job().type()});
            vm.resetBreadcrumbs(crumbs);

            %if not is_mini:
            if (vm.job().type() === 'workflow' && !vm.job().workflowGraphLoaded) {
              vm.job().updateWorkflowGraph();
            }
            %else:
            if (vm.job().type() === 'workflow') {
              vm.job().fetchProfile('properties');
              $('a[href="#workflow-page-metadata${ SUFFIX }"]').tab('show');
            }
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
        vm.apiHelper.cancelActiveRequest(lastUpdateJobRequest);
        huePubSub.publish('graph.refresh.view');

        if (vm.job() == self && self.apiStatus() == 'RUNNING') {
          lastFetchJobRequest = self._fetchJob(function (data) {
            if (vm.job().type() == 'schedule') {
              vm.job(new Job(vm, data.app)); // Updates everything but redraw the page
            } else {
              vm.job().fetchStatus();
              vm.job().fetchLogs();
            }
            // vm.job().fetchProfile(); // Get name of active tab?
          });
        }
      };

      self.fetchLogs = function (name) {
        self.logs('');
        $.post("/jobbrowser/api/job/logs", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          type: ko.mapping.toJSON(self.type),
          name: ko.mapping.toJSON(name ? name : 'default')
        }, function (data) {
          if (data.status == 0) {
            self.logs(data.logs.logs);
            if ($('.jb-panel pre:visible').length > 0){
              $('.jb-panel pre:visible').css('overflow-y', 'auto').height(Math.max(200, $(window).height() - $('.jb-panel pre:visible').offset().top - $('.page-content').scrollTop() - 30));
            }
          } else {
            $(document).trigger("error", data.message);
          }
        });
      };

      self.fetchProfile = function (name) {
        $.post("/jobbrowser/api/job/profile", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          app_type: ko.mapping.toJSON(self.type),
          app_property: ko.mapping.toJSON(name),
          app_filters: ko.mapping.toJSON(self.filters),
        }, function (data) {
          if (data.status == 0) {
            self.properties[name](data[name]);
          } else {
            $(document).trigger("error", data.message);
          }
        });
      };

      self.fetchStatus = function () {
        $.post("/jobbrowser/api/job", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(self.mainType)
        }, function (data) {
          if (data.status == 0) {
            self.status(data.app.status);
            self.apiStatus(data.app.apiStatus);
            self.progress(data.app.progress);
          } else {
            $(document).trigger("error", data.message);
          }
        });
      };

      self.control = function (action) {
        if (action == 'rerun') {
          $.get('/oozie/rerun_oozie_job/' + self.id() + '/?format=json', function(response) {
            $('#rerun-modal${ SUFFIX }').modal('show');
            self.rerunModalContent(response);
          });
        } else {
          vm.jobs._control([self.id()], action, function(data) {
            $(document).trigger("info", data.message);
            self.fetchStatus();
          });
        }
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

        if (!IS_HUE_4) {
          huePubSub.subscribe('hue4.process.headers', function (opts) {
            opts.callback(opts.response);
          });
        }
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

    var Jobs = function (vm) {
      var self = this;

      self.apps = ko.observableArray().extend({ rateLimit: 50 });
      self.totalApps = ko.observable(null);
      self.isCoordinator = ko.observable(false);

      self.loadingJobs = ko.observable(false);
      self.selectedJobs = ko.observableArray();

      self.hasKill = ko.pureComputed(function() {
        return ['jobs', 'workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1 && !self.isCoordinator();
      });
      self.killEnabled = ko.pureComputed(function() {
        return self.hasKill() && self.selectedJobs().length > 0 && $.grep(self.selectedJobs(), function(job) {
          return job.killEnabled();
        }).length == self.selectedJobs().length;
      });

      self.hasResume = ko.pureComputed(function() {
        return ['workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1 && !self.isCoordinator();
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
        return ['workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1 && !self.isCoordinator();
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
        return $.post("/jobbrowser/api/jobs", {
          interface: ko.mapping.toJSON(vm.interface),
          filters: ko.mapping.toJSON(self.filters),
        }, function (data) {
          if (data.status == 0) {
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

            while (i < self.apps().length && j < data.apps.length) {
              if (self.apps()[i].id() != data.apps[j].id) {
                // New Job
                newJobs.push(new Job(vm, data.apps[j]));
                j++;
              } else {
                // Updated jobs
                if (self.apps()[i].status() != data.apps[j].status) {
                  self.apps()[i].status(data.apps[j].status);
                  self.apps()[i].apiStatus(data.apps[j].apiStatus);
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
      };

      self.control = function (action) {
        if (action == 'rerun') {
          $.get('/oozie/rerun_oozie_coord/' + vm.job().id() + '/?format=json', function(response) {
            $('#rerun-modal${ SUFFIX }').modal('show');
            vm.job().rerunModalContent(response);

            var frag = document.createDocumentFragment();
            vm.job().coordinatorActions().selectedJobs().forEach(function (item) {
              var option = $('<option>', {
                value: item.properties.number(),
                selected: true
              });
              option.appendTo($(frag));
            });
            $('#id_actions').find('option').remove();
            $(frag).appendTo('#id_actions');
          });
        } else if (action == 'ignore') {
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
        $.post("/jobbrowser/api/job/action", {
          app_ids: ko.mapping.toJSON(app_ids),
          interface: ko.mapping.toJSON(vm.interface),
          operation: ko.mapping.toJSON({action: action})
        }, function (data) {
          if (data.status == 0) {
            if (callback) {
              callback(data);
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

      self.apiHelper = ApiHelper.getInstance();
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
      self.appConfig = ko.observable();
      self.isMini = ko.observable(false);

      self.availableInterfaces = ko.pureComputed(function () {
        var jobsInterfaceCondition = function () {
          return self.appConfig() && self.appConfig()['browser'] && self.appConfig()['browser']['interpreter_names'].indexOf('yarn') != -1;
        }
        var dataEngInterfaceCondition = function () {
          return self.appConfig() && self.appConfig()['browser'] && self.appConfig()['browser']['interpreter_names'].indexOf('dataeng') != -1;
        }
        var schedulerInterfaceCondition = function () {
          return self.appConfig() && self.appConfig()['scheduler'] && self.appConfig()['scheduler']['interpreters'].length > 0;
        }
        var livyInterfaceCondition = function () {
          return self.appConfig() && self.appConfig()['editor'] && self.appConfig()['editor']['interpreter_names'].indexOf('pyspark') != -1;
        }

        var interfaces = [
          {'interface': 'jobs', 'label': '${ _ko('Jobs') }', 'condition': jobsInterfaceCondition},
          {'interface': 'dataeng-jobs', 'label': '${ _ko('Jobs') }', 'condition': dataEngInterfaceCondition},
          {'interface': 'workflows', 'label': '${ _ko('Workflows') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'schedules', 'label': '${ _ko('Schedules') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'bundles', 'label': '${ _ko('Bundles') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'slas', 'label': '${ _ko('SLAs') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'dataeng-clusters', 'label': '${ _ko('Clusters') }', 'condition': dataEngInterfaceCondition},
          {'interface': 'livy-sessions', 'label': '${ _ko('Livy') }', 'condition': livyInterfaceCondition},
        ];

        return interfaces.filter(function (i) {
          return i.condition();
        });
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
      }

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
      }

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

      self.jobs = new Jobs(self);
      self.job = ko.observable();

      var updateJobInterval = -1;
      var updateJobsInterval = -1;
      self.job.subscribe(function(val) {
        window.clearInterval(updateJobInterval);
        window.clearInterval(updateJobsInterval);
        if (self.interface() && self.interface() !== 'slas' && self.interface() !== 'oozie-info'){
          if (val) {
            if (val.apiStatus() == 'RUNNING') {
              updateJobInterval = setInterval(val.updateJob, 5000, 'jobbrowser');
            }
          }
          else {
            updateJobsInterval = setInterval(self.jobs.updateJobs, 20000, 'jobbrowser');
          }
        }
      });


      self.breadcrumbs = ko.observableArray([]);
      self.resetBreadcrumbs = function(extraCrumbs) {
        var crumbs = [{'id': '', 'name': self.interface(), 'type': self.interface()}]
        if (extraCrumbs) {
          crumbs = crumbs.concat(extraCrumbs);
        }
        self.breadcrumbs(crumbs);
      }

      self.resetBreadcrumbs();

      self.getHDFSPath = function (path) {
        if (path.startsWith('hdfs://')) {
          var bits = path.substr(7).split('/');
          bits.shift();
          return '/' + bits.join('/');
        }
        return path;
      }

      self.formatProgress = function (progress) {
        if (typeof progress === 'function') {
          progress = progress();
        }
        if (!isNaN(progress)) {
          return Math.round(progress*100)/100 + '%';
        }
        return progress;
      }

      self.load = function() {
        var h = window.location.hash;
        %if not is_mini:
        huePubSub.publish('graph.stop.refresh.view');
        %endif

        h = h.indexOf('#!') === 0 ? h.substr(2) : '';
        switch (h) {
          case '':
            h = 'jobs';
          case 'slas':
          case 'oozie-info':
          case 'jobs':
          case 'workflows':
          case 'schedules':
          case 'bundles':
          case 'dataeng-clusters':
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
      }
    };


    $(document).ready(function () {
      var jobBrowserViewModel = new JobBrowserViewModel();
      function openJob(id) {
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
              if (data.attemptid) {
                openJob(data.attemptid);
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
      }

      huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
        jobBrowserViewModel.appConfig(clusterConfig && clusterConfig['app_config']);
        loadHash();
      });

      huePubSub.publish('cluster.config.get.config');

      huePubSub.subscribe('submit.rerun.popup.return', function (data) {
        $.jHueNotify.info('${_('Rerun submitted.')}');
        $('#rerun-modal${ SUFFIX }').modal('hide');
        jobBrowserViewModel.job().apiStatus('RUNNING');
        jobBrowserViewModel.job().updateJob();
      }, 'jobbrowser');
      % if is_mini:
        huePubSub.subscribe('mini.jb.navigate', function (interface) {
          $('#jobsPanel .nav-pills li').removeClass('active');
          interface = jobBrowserViewModel.isValidInterface(interface);
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
          $(dest).find('pre').css('overflow-y', 'auto').height(Math.max(200, $(window).height() - $(dest).find('pre').offset().top - $('.page-content').scrollTop() - 30));
        }
      });
    });
  })();
</script>
</span>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
