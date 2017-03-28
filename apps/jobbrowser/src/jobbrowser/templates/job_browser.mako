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
  from desktop import conf
  from desktop.views import commonheader, commonfooter, _ko
  from django.utils.translation import ugettext as _
%>

% if not is_embeddable:
${ commonheader("Job Browser", "jobbrowser", user, request) | n,unicode }
<%namespace name="assist" file="/assist.mako" />
% endif

<span class="notebook">

<link rel="stylesheet" href="${ static('desktop/ext/css/basictable.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
% if not is_embeddable:
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
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
<script src="${ static('oozie/js/list-oozie-coordinator.ko.js') }"></script>
<script src="${ static('desktop/js/ace/ace.js') }"></script>

% if not is_mini:
<div id="jobbrowserComponents" class="jobbrowser-components">
% else:
<div id="jobbrowserMiniComponents" class="jobbrowserComponents">
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
            <li data-bind="css: {'active': interface() === 'jobs'}"><a class="pointer" data-bind="click: function(){ selectInterface('jobs'); }">${ _('Jobs') }</a></li>
            <li data-bind="css: {'active': interface() === 'workflows'}"><a class="pointer" data-bind="click: function(){ selectInterface('workflows'); }">${ _('Workflows') }</a></li>
            <li data-bind="css: {'active': interface() === 'schedules'}"><a class="pointer" data-bind="click: function(){ selectInterface('schedules'); }">${ _('Schedules') }</a></li>
            <li data-bind="css: {'active': interface() === 'bundles'}"><a class="pointer" data-bind="click: function(){ selectInterface('bundles'); }">${ _('Bundles') }</a></li>
            <li data-bind="css: {'active': interface() === 'slas'}"><a class="pointer" data-bind="click: function(){ selectInterface('slas'); }">${ _('SLAs') }</a></li>
            </ul>
          % if not hiveserver2_impersonation_enabled:
            <div class="pull-right alert alert-warning" style="margin-top: 4px">${ _("Hive jobs are running as the 'hive' user") }</div>
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

            <div data-bind="template: { name: 'breadcrumbs' }"></div>

            <!-- ko if: ! $root.job() -->
            ${_('Filter')} <input type="text" class="input-xlarge search-query" data-bind="textInput: jobs.textFilter" placeholder="${_('Filter by id, name, user...')}" />
            <div class="btn-group">
              <a class="btn btn-status btn-success" data-value="completed">${ _('Succeeded') }</a>
              <a class="btn btn-status btn-warning" data-value="running">${ _('Running') }</a>
              <a class="btn btn-status btn-danger disable-feedback" data-value="failed">${ _('Failed') }</a>
            </div>

            ${_('in the last')} <input id="timeValue" class="input-mini no-margin" type="number" value="7" min="1" max="3650">
            <select id="timeUnit" class="input-small no-margin">
              <option value="days">${_('days')}</option>
              <option value="hours">${_('hours')}</option>
              <option value="minutes">${_('minutes')}</option>
            </select>

            <div class="btn-toolbar pull-right" style="display: inline; vertical-align: middle; margin-left: 10px; font-size: 12px">
              <span class="loader hide"><i class="fa fa-2x fa-spinner fa-spin muted"></i></span>
              <button class="btn bulkToolbarBtn bulk-resume" data-operation="resume" title="${ _('Resume selected') }" disabled="disabled" type="button">
                <i class="fa fa-play"></i><span class="hide-small"> ${ _('Resume') }</span>
              </button>
              <button class="btn bulkToolbarBtn bulk-suspend" data-operation="suspend" title="${ _('Suspend selected') }" disabled="disabled" type="button">
                <i class="fa fa-pause"></i><span class="hide-small"> ${ _('Suspend') }</span>
              </button>
              <button class="btn bulkToolbarBtn btn-danger bulk-kill disable-feedback" data-operation="kill" title="${ _('Kill selected') }" disabled="disabled" type="button">
                <i class="fa fa-times"></i><span class="hide-small"> ${ _('Kill') }</span>
              </button>
            </div>


            <div class="card card-small">
              <table id="jobsTable" class="datatables table table-condensed">
                <thead>
                <tr>
                  <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
                  <th>${_('Duration')}</th>
                  <th>${_('Type')}</th>
                  <th>${_('Status')}</th>
                  <th>${_('Progress')}</th>
                  <th>${_('Name')}</th>
                  <th>${_('User')}</th>
                  <th>${_('Id')}</th>
                </tr>
                </thead>
                <tbody data-bind="foreach: jobs.apps">
                  <tr data-bind="click: fetchJob">
                    <td><div class="hueCheckbox fa"></div></td>
                    <td data-bind="text: duration"></td>
                    <td data-bind="text: type"></td>
                    <td data-bind="text: status"></td>
                    <td data-bind="text: progress"></td>
                    <td data-bind="text: name"></td>
                    <td data-bind="text: user"></td>
                    <td data-bind="text: id"></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- /ko -->

          <!-- ko if: $root.job() -->
          <!-- ko with: $root.job() -->
            <!-- ko if: mainType() == 'jobs' -->
              <div data-bind="template: { name: 'job-page' }"></div>
            <!-- /ko -->

            <!-- ko if: mainType() == 'workflows' -->
              <!-- ko if: type() == 'workflow' -->
                <div data-bind="template: { name: 'workflow-page' }"></div>
              <!-- /ko -->

              <!-- ko if: type() == 'workflow-action' -->
                <div data-bind="template: { name: 'workflow-action-page' }"></div>
              <!-- /ko -->
            <!-- /ko -->

            <!-- ko if: mainType() == 'schedules' -->
              <div data-bind="template: { name: 'schedule-page' }"></div>
            <!-- /ko -->

            <!-- ko if: mainType() == 'bundles' -->
              <div data-bind="template: { name: 'bundle-page' }"></div>
            <!-- /ko -->

            <!-- ko if: mainType() == 'sla' -->
              <div data-bind="template: { name: 'sla-page' }"></div>
            <!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->

          <div data-bind="template: { name: 'pagination' }, visible: ! $root.job()"></div>
        </div>
      </div>

    </div>
  </div>
</div>
</div>
</div>


<script type="text/html" id="breadcrumbs-icons">
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


<script type="text/html" id="breadcrumbs">
  <h3>
    <ul class="inline hueBreadcrumbBar" data-bind="foreach: breadcrumbs">
      <li>
      <!-- ko if: $index() > 0 -->
        <span class="divider">&gt;</span>
      <!-- /ko -->

      <!-- ko if: $index() == 0 -->
        <a href="javascript:void(0)" data-bind="text: name, click: function() { $root.selectInterface(name); }" style="text-transform: capitalize"></a>
      <!-- /ko -->
      <!-- ko if: $index() != 0 -->
        <!-- ko if: $index() != $parent.breadcrumbs().length - 1 -->
          <a href="javascript:void(0)" data-bind="click: function() { $parent.breadcrumbs.splice($index()); $root.job().id(id); $root.job().fetchJob(); }">
          <span data-bind="template: 'breadcrumbs-icons'"></span>
          <span data-bind="text: id"></span></a>
        <!-- /ko -->
        <!-- ko if: $index() == $parent.breadcrumbs().length - 1 -->
          <span data-bind="template: 'breadcrumbs-icons'"></span>
          <span data-bind="text: id, attr: {title: id}"></span>
        <!-- /ko -->
      <!-- /ko -->
      </li>
    </ul>
  </h3>
</script>


<script type="text/html" id="pagination">
  Showing
  <span data-bind="text: paginationPage"></span>
  to
  <span data-bind="text: paginationOffset() * paginationResultPage()"></span>
  of
  <span data-bind="text: paginationResultCounts"></span>

  Show
  <span data-bind="text: paginationOffset"></span>
  results by page.
</script>


<script type="text/html" id="job-page">
  <!-- ko if: type() == 'MAPREDUCE' -->
    <div data-bind="template: { name: 'job-mapreduce-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'MAP' || type() == 'REDUCE' -->
    <div data-bind="template: { name: 'job-mapreduce-task-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'MAP_ATTEMPT' || type() == 'REDUCE_ATTEMPT' -->
    <div data-bind="template: { name: 'job-mapreduce-task-attempt-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YARN' -->
    <div data-bind="template: { name: 'job-yarn-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'IMPALA' -->
    <div data-bind="template: { name: 'job-impala-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'SPARK' -->
    <div data-bind="template: { name: 'job-spark-page', data: $root.job() }"></div>
  <!-- /ko -->
</script>

<script type="text/html" id="job-yarn-page">
  <h2>YARN</h2>
  <br>

  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>
</script>


<script type="text/html" id="job-mapreduce-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>

  <br><br>

  <!-- ko with: properties -->
  Map <span data-bind="text: maps_percent_complete"></span> <span data-bind="text: finishedMaps"></span> /<span data-bind="text: desiredMaps"></span>
  Reduce <span data-bind="text: reduces_percent_complete"></span> <span data-bind="text: finishedReduces"></span> / <span data-bind="text: desiredReduces"></span><br>
  Duration <span data-bind="text: $parent.duration"></span><br>
  <!-- /ko -->
  <br><br>

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <a href="javascript:void(0)" data-bind="click: function() { control('kill'); }">Stop</a>

  <ul class="nav nav-tabs margin-top-20">
    <li class="active"><a href="#job-mapreduce-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#job-mapreduce-page-tasks" data-bind="click: function(){ fetchProfile('tasks'); $('a[href=\'#job-mapreduce-page-tasks\']').tab('show'); }">${ _('Tasks') }</a></li>
    <li><a href="#job-mapreduce-page-metadata" data-bind="click: function(){ fetchProfile('metadata'); $('a[href=\'#job-mapreduce-page-metadata\']').tab('show'); }">${ _('Metadata') }</a></li>
    <li><a href="#job-mapreduce-page-counters" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-page-counters\']').tab('show'); }">${ _('Counters') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="job-mapreduce-page-logs">
      % for name in ['stdout', 'stderr', 'syslog']:
        <a href="javascript:void(0)" data-bind="click: function() { fetchLogs('${ name }'); }, text: '${ name }'"></a>
      % endfor
      <br>

      <pre data-bind="html: logs"></pre>
    </div>

    <div class="tab-pane" id="job-mapreduce-page-tasks">
      ${_('Filter')} <input type="text" class="input-xlarge search-query" placeholder="${_('Filter by id, name, user...')}" value="user:${ user.username }">
      <span class="btn-group">
        <class="btn-group">
          <a class="btn btn-status btn-success" data-value="completed">${ _('MAP') }</a>
          <a class="btn btn-status btn-warning" data-value="running">${ _('REDUCE') }</a>
        </span>
      </span>

      <div class="btn-toolbar pull-right" style="display: inline; vertical-align: middle; margin-left: 10px; font-size: 12px">
        <span class="loader hide"><i class="fa fa-2x fa-spinner fa-spin muted"></i></span>
        <button class="btn bulkToolbarBtn bulk-resume" data-operation="resume" title="${ _('Resume selected') }" disabled="disabled" type="button"><i class="fa fa-play"></i><span class="hide-small"> ${ _('View') }</span></button>
      </div>

      <table class="table table-condensed">
        <thead>
        <tr>
          <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
          <th>${_('Type')}</th>
          <th>${_('Id')}</th>
          <th>${_('elapsedTime')}</th>
          <th>${_('progress')}</th>
          <th>${_('state')}</th>
          <th>${_('startTime')}</th>
          <th>${_('successfulAttempt')}</th>
          <th>${_('finishTime')}</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: properties['tasks']()['task_list']">
          <tr data-bind="click: function() { $root.job().id(id); $root.job().fetchJob(); }">
            <td><div class="hueCheckbox fa"></div></td>
            <td data-bind="text: type"></td>
            <td data-bind="text: id"></td>
            <td data-bind="text: elapsedTime"></td>
            <td data-bind="text: progress"></td>
            <td data-bind="text: state"></td>
            <td data-bind="text: startTime"></td>
            <td data-bind="text: successfulAttempt"></td>
            <td data-bind="text: finishTime"></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="tab-pane" id="job-mapreduce-page-metadata">
      <pre data-bind="text: ko.toJSON(properties['metadata'], null, 2)"></pre>
    </div>

    <div class="tab-pane" id="job-mapreduce-page-counters">
      <pre data-bind="text: ko.toJSON(properties['counters'], null, 2)"></pre>
    </div>
  </div>

</script>


<script type="text/html" id="job-mapreduce-task-page">

  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('progress') } <span data-bind="text: progress"></span>

  <br><br>

  <!-- ko with: properties -->
  ${ _('state') } <span data-bind="text: state"></span>
  ${ _('startTime') } <span data-bind="text: startTime"></span>
  ${ _('successfulAttempt') } <span data-bind="text: successfulAttempt"></span>
  ${ _('finishTime') } <span data-bind="text: finishTime"></span>
  ${ _('elapsedTime') } <span data-bind="text: elapsedTime"></span>
  <!-- /ko -->

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <ul class="nav nav-tabs margin-top-20">
    <li class="active"><a href="#job-mapreduce-task-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#job-mapreduce-task-page-attempts" data-bind="click: function(){ fetchProfile('attempts'); $('a[href=\'#job-mapreduce-task-page-attempts\']').tab('show'); }">${ _('Attempts') }</a></li>
    <li><a href="#job-mapreduce-task-page-counters" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-task-page-counters\']').tab('show'); }">${ _('Counters') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="job-mapreduce-task-page-logs">
      % for name in ['stdout', 'stderr', 'syslog']:
        <a href="javascript:void(0)" data-bind="click: function() { fetchLogs('${ name }'); }, text: '${ name }'"></a>
      % endfor
      <br>

      <pre data-bind="html: logs"></pre>
    </div>

    <div class="tab-pane" id="job-mapreduce-task-page-attempts">
      ${_('Filter')} <input type="text" class="input-xlarge search-query" placeholder="${_('Filter by id, name, user...')}" value="user:${ user.username }">
      <span class="btn-group">
        <class="btn-group">
          <a class="btn btn-status btn-success" data-value="completed">${ _('Succeeded') }</a>
          <a class="btn btn-status btn-warning" data-value="running">${ _('Running') }</a>
          <a class="btn btn-status btn-danger disable-feedback" data-value="failed">${ _('Failed') }</a>
        </span>
      </span>

      <div class="btn-toolbar pull-right" style="display: inline; vertical-align: middle; margin-left: 10px; font-size: 12px">
        <span class="loader hide"><i class="fa fa-2x fa-spinner fa-spin muted"></i></span>
        <button class="btn bulkToolbarBtn bulk-resume" data-operation="resume" title="${ _('Resume selected') }" disabled="disabled" type="button"><i class="fa fa-play"></i><span class="hide-small"> ${ _('View') }</span></button>
      </div>

      <table class="table table-condensed">
        <thead>
        <tr>
          <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
          <th>${_('assignedContainerId')}</th>
          <th>${_('progress')}</th>
          <th>${_('elapsedTime')}</th>
          <th>${_('state')}</th>
          <th>${_('rack')}</th>
          <th>${_('nodeHttpAddress')}</th>
          <th>${_('type')}</th>
          <th>${_('startTime')}</th>
          <th>${_('id')}</th>
          <th>${_('finishTime')}</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: properties['attempts']()['task_list']">
          <tr data-bind="click: function() { $root.job().id(id); $root.job().fetchJob(); }">
            <td><div class="hueCheckbox fa"></div></td>
            <td data-bind="text: assignedContainerId"></td>
            <td data-bind="text: progress"></td>
            <td data-bind="text: elapsedTime"></td>
            <td data-bind="text: state"></td>
            <td data-bind="text: rack"></td>
            <td data-bind="text: nodeHttpAddress"></td>
            <td data-bind="text: type"></td>
            <td data-bind="text: startTime"></td>
            <td data-bind="text: id"></td>
            <td data-bind="text: finishTime"></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="tab-pane" id="job-mapreduce-task-page-counters">
      <pre data-bind="text: ko.toJSON(properties['counters'], null, 2)"></pre>
    </div>
  </div>

</script>


<script type="text/html" id="job-mapreduce-task-attempt-page">

  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('progress') } <span data-bind="text: progress"></span>
  ${ _('type') } <span data-bind="text: type"></span>

  <br><br>

  <!-- ko with: properties -->
  ${ _('assignedContainerId') } <span data-bind="text: assignedContainerId"></span>
  ${ _('elapsedTime') } <span data-bind="text: elapsedTime"></span>
  ${ _('rack') } <span data-bind="text: rack"></span>
  ${ _('nodeHttpAddress') } <span data-bind="text: nodeHttpAddress"></span>
  ${ _('state') } <span data-bind="text: state"></span>
  ${ _('startTime') } <span data-bind="text: startTime"></span>
  ${ _('finishTime') } <span data-bind="text: finishTime"></span>
  <!-- /ko -->

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <ul class="nav nav-tabs margin-top-20">
    <li class="active"><a href="#job-mapreduce-task-attempt-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#job-mapreduce-task-attempt-page-counters" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-task-attempt-page-counters\']').tab('show'); }">${ _('Counters') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="job-mapreduce-task-attempt-page-logs">
      <ul class="nav nav-tabs">
        <li class="active"><a href="#job-mapreduce-task-attempt-page-logs-attempts" data-toggle="tab">${ _('Attempts') }</a></li>
        <li><a href="#job-mapreduce-task-attempt-page-logs-container" data-toggle="tab">${ _('Container') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="job-mapreduce-task-attempt-page-logs-attempts">
          % for name in ['stdout', 'stderr', 'syslog']:
            <a href="javascript:void(0)" data-bind="click: function() { fetchLogs('${ name }'); }, text: '${ name }'"></a>
          % endfor
          <br>
          <pre data-bind="html: logs"></pre>
        </div>

        <div class="tab-pane" id="job-mapreduce-task-attempt-page-logs-container">
          % for name in ['container-stdout', 'container-stderr', 'container-syslog']:
            <a href="javascript:void(0)" data-bind="click: function() { fetchLogs('${ name }'); }, text: '${ name }'"></a>
          % endfor
          <br>
          <pre data-bind="html: logs"></pre>
        </div>
      </div>
    </div>

    <div class="tab-pane" id="job-mapreduce-task-attempt-page-counters">
      <pre data-bind="text: ko.toJSON(properties['counters'], null, 2)"></pre>
    </div>
  </div>

</script>


<script type="text/html" id="job-impala-page">
  <h2>Impala</h2>
  <br>

  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>
</script>

<script type="text/html" id="job-spark-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>
</script>


<script type="text/html" id="workflow-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>

  <br><br>
  Variables, Workspace<br>
  Duration 8s<br>
  <br><br>

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <a href="javascript:void(0)" data-bind="click: function() { control('kill'); }">${ _('Stop') }</a> |
  <a href="javascript:void(0)" data-bind="click: function() { control('resume'); }">${ _('Resume')}</a> |
  <a href="javascript:void(0)" data-bind="click: function() { control('rerun'); }">${ _('Rerun') }</a>

  <ul class="nav nav-tabs margin-top-20">
    <li class="active"><a href="#workflow-page-graph" data-toggle="tab">${ _('Graph') }</a></li>
    <li><a href="#workflow-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#workflow-page-tasks" data-toggle="tab">${ _('Tasks') }</a></li>
    <li><a href="#workflow-page-metadata" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#workflow-page-metadata\']').tab('show'); }">${ _('Properties') }</a></li>
    <li><a href="#workflow-page-xml" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#workflow-page-xml\']').tab('show'); }">${ _('XML') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="workflow-page-graph">
    </div>

    <div class="tab-pane" id="workflow-page-logs">
      <pre data-bind="html: logs"></pre>
    </div>

    <div class="tab-pane" id="workflow-page-tasks">
      <table id="jobsTable" class="datatables table table-condensed">
        <thead>
        <tr>
          <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
          <th>${_('log')}</th>
          <th>${_('status')}</th>
          <th>${_('errorMessage')}</th>
          <th>${_('errorCode')}</th>
          <th>${_('externalId')}</th>
          <th>${_('id')}</th>
          <th>${_('startTime')}</th>
          <th>${_('endTime')}</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: properties['actions']">
          <tr data-bind="click: function() {  $root.job().id(id); $root.job().fetchJob(); }">
            <td><div class="hueCheckbox fa"></div></td>
            <td data-bind="text: 'logs'"></td>
            <td data-bind="text: status"></td>
            <td data-bind="text: errorMessage"></td>
            <td data-bind="text: errorCode"></td>
            <td data-bind="text: externalId"></td>
            <td data-bind="text: id"></td>
            <td data-bind="text: startTime"></td>
            <td data-bind="text: endTime"></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="tab-pane" id="workflow-page-metadata">
      <pre data-bind="text: ko.toJSON(properties['properties'], null, 2)"></pre>
    </div>

    <div class="tab-pane" id="workflow-page-xml">
      <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
    </div>
  </div>

</script>


<script type="text/html" id="workflow-action-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>

  <br><br>
  Job ID ....<br>
  Duration 8s<br>
  <br><br>

  Log (if external id) | Child jobs

</script>


<script type="text/html" id="schedule-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>


  <br><br>
  Variables, Workspace<br>
  Duration 8s<br>
  nextTime<span data-bind="text: properties['nextTime']"></span><br>
  total_actions<span data-bind="text: properties['total_actions']"></span><br>
  endTime<span data-bind="text: properties['endTime']"></span><br>
  <br><br>

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <a href="javascript:void(0)" data-bind="click: function() { control('kill'); }">${ _('Stop') }</a> |
  <a href="javascript:void(0)" data-bind="click: function() { control('resume'); }">${ _('Resume')}</a> |
  <a href="javascript:void(0)" data-bind="click: function() { control('rerun'); }">${ _('Rerun') }</a>

  <br>

  <ul class="nav nav-tabs">
    <li class="active"><a href="#schedule-page-calendar" data-toggle="tab">${ _('Calendar') }</a></li>
    <li><a href="#schedule-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#schedule-page-tasks" data-toggle="tab">${ _('Tasks') }</a></li>
    <li><a href="#schedule-page-metadata"  data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#schedule-page-metadata\']').tab('show'); }">${ _('Properties') }</a></li>
    <li><a href="#schedule-page-xml" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#schedule-page-xml\']').tab('show'); }">${ _('XML') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="schedule-page-calendar">
      <pre data-bind="text: ko.toJSON(properties['actions'], null, 2)"></pre>
    </div>

    <div class="tab-pane" id="schedule-page-logs">
      <pre data-bind="html: logs"></pre>
    </div>

    <div class="tab-pane" id="schedule-page-tasks">
      <table id="jobsTable" class="datatables table table-condensed">
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
        <tbody data-bind="foreach: properties['actions']">
          <tr data-bind="click: function() {  if (externalId()) { $root.job().id(externalId()); $root.job().fetchJob();} }">
            <td><div class="hueCheckbox fa"></div></td>
            <td data-bind="text: status"></td>
            <td data-bind="text: title"></td>
            <td data-bind="text: type"></td>
            <td data-bind="text: errorMessage"></td>
            <td data-bind="text: missingDependencies"></td>
            <td data-bind="text: number"></td>
            <td data-bind="text: errorCode"></td>
            <td data-bind="text: externalId"></td>
            <td data-bind="text: id"></td>
            <td data-bind="text: lastModifiedTime"></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="tab-pane" id="schedule-page-metadata">
      <pre data-bind="text: ko.toJSON(properties['properties'], null, 2)"></pre>
    </div>

    <div class="tab-pane" id="schedule-page-xml">
      <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
    </div>
  </div>
</script>


<script type="text/html" id="bundle-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>
</script>


<script type="text/html" id="slas-page">
<div class="container-fluid">
  <div class="card card-small">

      <div class="card-body">
        <p>
          <div class="search-something center empty-wrapper">
            <a href="http://gethue.com/hadoop-tutorial-monitor-and-get-alerts-for-your-workflows-with-the-oozie-slas/" target="_blank" title="${ _('Click to learn more') }">
              <i class="fa fa-exclamation"></i>
            </a>
            <h1>${_('Oozie is not setup to create SLAs')}</h1>
            <br/>
          </div>
        </p>
      </div>

      <h1 class="card-heading simple">
      <div class="pull-left" style="margin-right: 20px;margin-top: 2px">${_('Search')}</div>
      <form class="form-inline" id="searchForm" method="GET" action="." style="margin-bottom: 4px">
        <label>
          ${_('Name or Id')}
          <input type="text" name="job_name" class="searchFilter input-xlarge search-query" placeholder="${_('Job Name or Id (required)')}">
        </label>
        <span style="padding-left:25px">
          <label class="label-with-margin">
            ${ _('Start') }
            <input type="text" name="start_0" class="input-small date" value="" placeholder="${_('Date in GMT')}"  data-bind="enable: useDates">
            <input type="text" name="start_1" class="input-small time" value="" data-bind="enable: useDates">
          </label>
          <label>
            ${ _('End') }
            <input type="text" name="end_0" class="input-small date" value="" placeholder="${_('Date in GMT')}" data-bind="enable: useDates">
            <input type="text" name="end_1" class="input-small time" value="" data-bind="enable: useDates">
          </label>
        </span>
        <label class="checkbox label-with-margin">
          <input type="checkbox" name="useDates" class="searchFilter" data-bind="checked: useDates, click: performSearch()">
          ${ _('Date filter') }
        </label>
      </form>
      </h1>
      <div class="card-body">
        <p>
          <div class="loader hide" style="text-align: center;margin-top: 20px">
            <!--[if lte IE 9]>
              <img src="${ static('desktop/art/spinner-big.gif') }" />
            <![endif]-->
            <!--[if !IE]> -->
              <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
            <!-- <![endif]-->
          </div>

          <div class="search-something center empty-wrapper">
            <i class="fa fa-search"></i>
            <h1>${_('Use the form above to search for SLAs.')}</h1>
            <br/>
          </div>

          <div class="no-results center empty-wrapper hide">
            <h1>${_('The server returned no results.')}</h1>
            <br/>
          </div>

         <div class="results hide">
           <ul class="nav nav-tabs">
             <li class="active"><a href="#slaListTab" data-toggle="tab">${ _('List') }</a></li>
             <li><a href="#chartTab" data-toggle="tab">${ _('Chart') }</a></li>
           </ul>

           <div class="tab-content" style="padding-bottom:200px">
             <div class="tab-pane active" id="slaListTab">
               <div class="tabbable">
                 <div class="tab-content">
                   <table id="slaTable" class="table table-striped table-condensed">
                     <thead>
                       <th>${_('Status')}</th>
                       <th>${_('Name')}</th>
                       <th>${_('Type')}</th>
                       <th>${_('ID')}</th>
                       <th>${_('Nominal Time')}</th>
                       <th>${_('Expected Start')}</th>
                       <th>${_('Actual Start')}</th>
                       <th>${_('Expected End')}</th>
                       <th>${_('Actual End')}</th>
                       <th>${_('Expected Duration')}</th>
                       <th>${_('Actual Duration')}</th>
                       <th>${_('Job Status')}</th>
                       <th>${_('User')}</th>
                       <th>${_('Last Modified')}</th>
                     </thead>
                     <tbody>
                     </tbody>
                   </table>
                 </div>
               </div>
             </div>

             <div class="tab-pane" id="chartTab" style="padding-left: 20px">
               <div id="yAxisLabel" class="hide">${_('Time since Nominal Time in min')}</div>
               <div id="slaChart"></div>
             </div>
            </div>
          </div>
        </p>
      </div>

  </div>
</div>
</script>


<script type="text/javascript">

  (function () {

/**
    var Workflow = function(vm, job) {

            var lastPosition = {
              top: 0,
              left: 0
            }

            var updateArrowPosition = function () {
              huePubSub.publish('draw.graph.arrows');
              if ($('canvas').position().top !== lastPosition.top && $('canvas').position().left !== lastPosition.left) {
                lastPosition = $('canvas').position();
                window.setTimeout(updateArrowPosition, 100);
              }
            }

            var arrowsPolling = function () {
              if ($('#workflow-page-graph').is(':visible')){
                window.setTimeout(arrowsPolling, 100);
              }
              else {
                $('canvas').remove();
              }
            }

            $('canvas').remove();

            if (vm.job().type() === 'workflow') {
              $('#workflow-page-graph').empty();
              $.ajax({
                url: "/oozie/list_oozie_workflow/" + vm.job().id(),
                data: {
                  'graph': true,
                  'element': 'workflow-page-graph'
                },
                beforeSend: function (xhr) {
                  xhr.setRequestHeader("X-Requested-With", "Hue");
                },
                dataType: "html",
                success: function (response) {
                  $('#workflow-page-graph').html(response);
                  updateArrowPosition();
                  arrowsPolling();
                }
              });
            }
    }
*/
    var Job = function (vm, job) {
      var self = this;

      self.id = ko.observableDefault(job.id);
      self.name = ko.observableDefault(job.name);
      self.type = ko.observableDefault(job.type);

      self.status = ko.observableDefault(job.status);
      self.apiStatus = ko.observableDefault(job.apiStatus);
      self.progress = ko.observableDefault(job.progress);
      self.checkStatusTimeout = null;

      self.user = ko.observableDefault(job.user);
      self.cluster = ko.observableDefault(job.cluster);
      self.duration = ko.observableDefault(job.duration);
      self.submitted = ko.observableDefault(job.submitted);

      self.logs = ko.observable('');

      //self.coordVM = new RunningCoordinatorModel([]);

      self.properties = ko.mapping.fromJS(job.properties || {});
      self.mainType = ko.observable(vm.interface());

      self.loadingJob = ko.observable(false);


      self.fetchJob = function () {
        self.loadingJob(true);

        if (self.checkStatusTimeout != null) {
          clearTimeout(self.checkStatusTimeout);
          self.checkStatusTimeout = null;
        }

        var interface = vm.interface();
        if (/oozie-oozi-W/.test(self.id())) { interface = 'workflows'; };

        $.post("/jobbrowser/api/job", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(interface)
        }, function (data) {
          if (data.status == 0) {
            vm.interface(interface);
            vm.job(new Job(vm, data.app));

            hueUtils.changeURL('#!' + vm.job().id());
            vm.breadcrumbs.push({'id': vm.job().id(), 'name': vm.job().name(), 'type': vm.job().type()});

            vm.job().fetchLogs();
            vm.job().fetchStatus();

            //if (self.mainType() == 'schedules') {
              //vm.job().coordVM.setActions(data.app.actions);
            //}
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
          self.loadingJob(false);
        });
      };

      self.fetchLogs = function (name) {
        $.post("/jobbrowser/api/job/logs", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          type: ko.mapping.toJSON(self.type),
          name: ko.mapping.toJSON(name ? name : 'default')
        }, function (data) {
          if (data.status == 0) {
            self.logs(data.logs.logs)
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
        });
      };

      self.fetchProfile = function (name) {
        $.post("/jobbrowser/api/job/profile", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          app_type: ko.mapping.toJSON(self.type),
          app_property: ko.mapping.toJSON(name)
        }, function (data) {
          if (data.status == 0) {
            self.properties[name](data[name]);
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
        });
      };

      self.fetchStatus = function () {
        if (self.apiStatus() != 'RUNNING') {
          return;
        }

        $.post("/jobbrowser/api/job", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(self.mainType)
        }, function (data) {
          if (data.status == 0) {
            self.status(data.app.status);
            self.apiStatus(data.app.apiStatus);
            self.progress(data.app.progress);

            if (self.apiStatus() == 'RUNNING') {
              self.checkStatusTimeout = setTimeout(self.fetchStatus, 2000);
            }
          } else {
            $(document).trigger("error", data.message);
          }
        });
      };

      self.control = function (action) {
        $.post("/jobbrowser/api/job/action", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface),
          app_type: ko.mapping.toJSON(self.type),
          operation: ko.mapping.toJSON({action: action})
        }, function (data) {
          if (data.status == 0) {
             $(document).trigger("info", data.message);
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
        });
      };
    };

    var Jobs = function (vm) {
      var self = this;

      self.apps = ko.observableArray();
      self.loadingJobs = ko.observable(false);
      self.textFilter = ko.observable('user:${ user.username } ').extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 500 } });
      self.textFilter.subscribe(function(value) {
        self.fetchJobs();
        // TBD: refreshPagination()
      });

      self.filters = ko.computed(function() {
        return [{'text': self.textFilter()}];
      });


      self.fetchJobs = function () {
        self.loadingJobs(true);
        vm.job(null);

        $.post("/jobbrowser/api/jobs", {
          interface: ko.mapping.toJSON(vm.interface),
          filters: ko.mapping.toJSON(self.filters),
        }, function (data) {
          if (data.status == 0) {
            var apps = [];
            if (data && data.apps) {
              data.apps.forEach(function (job) { // TODO: update and merge with status and progress
                apps.push(new Job(vm, job));
              });
            }
            self.apps(apps);
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
          self.loadingJobs(false);
        });
      };

      self.control = function (action) {
        $.post("/jobbrowser/api/job/action", {
          app_id: ko.mapping.toJSON(self.id), // CSV list
          interface: ko.mapping.toJSON(vm.interface),
          operation: ko.mapping.toJSON({action: action})
        }, function (data) {
          if (data.status == 0) {
            $(document).trigger("info", data.message);
          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
        });
      };
    };

    var JobBrowserViewModel = function (RunningCoordinatorModel) {
      var self = this;

      self.apiHelper = ApiHelper.getInstance();
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

      self.jobs = new Jobs(self);
      self.job = ko.observable();

      self.interface = ko.observable('jobs');
      self.interface.subscribe(function (val) {
        hueUtils.changeURL('#!' + val);
        self.jobs.fetchJobs();
      });
      self.selectInterface = function(interface) {
        self.interface(interface);
        self.resetBreadcrumbs();
        self.job(null);
      };
      self.breadcrumbs = ko.observableArray([]);
      self.resetBreadcrumbs = function() {
        self.breadcrumbs([{'id': '', 'name': self.interface(), 'type': self.interface()}]);
      }
      self.resetBreadcrumbs();

      self.paginationOffset = ko.observable(0);
      self.paginationResultPage = ko.observable(100);
      self.paginationPage = ko.observable(1);
      self.paginationResultCounts = ko.observable();
    };

    var viewModel;

    huePubSub.subscribe('oozie.action.logs.click', function (widget) {
      viewModel.job().id(widget.externalId());
      viewModel.job().fetchJob();
    });

    huePubSub.subscribe('oozie.action.click', function (widget) {
      viewModel.job().id(widget.externalId());
      viewModel.job().fetchJob();
    });

    $(document).ready(function () {
      viewModel = new JobBrowserViewModel(RunningCoordinatorModel);
      % if not is_mini:
      ko.applyBindings(viewModel, $('#jobbrowserComponents')[0]);
      % else:
      ko.applyBindings(viewModel, $('#jobbrowserMiniComponents')[0]);
      % endif

      var loadHash = function () {
        var h = window.location.hash;
        if (h.indexOf('#!') === 0) {
          h = h.substr(2);
        }
        switch (h) {
          case '':
           break;
          case 'apps':
          case 'workflows':
          case 'schedules':
          case 'bundles':
            viewModel.interface(h);
            break;
          default:
            var isJob = true;
            if (/oozie-oozi-W/.test(h)) { viewModel.interface('workflows'); }
            else if (/oozie-oozi-C/.test(h)) { viewModel.interface('schedules'); }
            else if (/oozie-oozi-B/.test(h)) { viewModel.interface('bundles'); }
            else { isJob = false; }
            if (isJob) {
              new Job(viewModel, {id: h}).fetchJob();
            }
        }
      }

      window.onhashchange = function () {
        loadHash();
      }
      loadHash();

      viewModel.jobs.fetchJobs();
    });
  })();
</script>
</span>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
