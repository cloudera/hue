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

<script src="${ static('oozie/js/dashboard-utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.basictable.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
<script src="${ static('oozie/js/list-oozie-coordinator.ko.js') }"></script>

% if not is_embeddable:
  ${ assist.assistJSModels() }
  ${ assist.assistPanel() }

  <a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
    <i class="fa fa-chevron-right"></i>
  </a>
% endif

<div id="jobbrowserComponents">
<div class="navbar navbar-inverse navbar-fixed-top nokids">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="currentApp">
              <a href="/${app_name}">
                <img src="${ static('jobbrowser/art/icon_jobbrowser_48.png') }" class="app-icon"/>
                ${ _('Job Browser') }
              </a>
            </li>
          </ul>
            <span class="form-inline">
              <input class="btn btn-status" type="radio" name="interface" value="apps" data-bind="checked: interface" id="apps"><label for="apps">${ _('Apps') }</label>
              <input class="btn btn-status" type="radio" name="interface" value="workflows" data-bind="checked: interface" id="workflows"><label for="workflows">${ _('Workflows') }</label>
              <input class="btn btn-status" type="radio" name="interface" value="schedules" data-bind="checked: interface" id="schedules"><label for="schedules">${ _('Schedules') }</label>
              <input class="btn btn-status" type="radio" name="interface" value="bundles" data-bind="checked: interface" id="bundles"><label for="bundles">${ _('Bundles') }</label>
            </span>
          % if not hiveserver2_impersonation_enabled:
            <div class="pull-right alert alert-warning" style="margin-top: 4px">${ _("Hive jobs are running as the 'hive' user") }</div>
          % endif
        </div>
      </div>
    </div>
</div>

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
                  sourceTypes: [{
                    name: 'hive',
                    type: 'hive'
                  }],
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

          <div class="container-fluid">
            <div data-bind="template: { name: 'breadcrumbs' }"></div>

            <!-- ko if: ! $root.job() -->
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
          </div>

          <!-- ko if: $root.job() -->
          <!-- ko with: $root.job() -->
            <!-- ko if: mainType() == 'apps' -->
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
          <!-- /ko -->
          <!-- /ko -->

          <div data-bind="template: { name: 'pagination' }, visible: ! $root.job()"></div>
      </div>
    </div>
  </div>
</div>
</div>


<script type="text/html" id="breadcrumbs">
  <h2 data-bind="foreach: breadcrumbs">
    <!-- ko if: $index() > 0 -->
      &gt;
    <!-- /ko -->

    <!-- ko if: $index() == 0 -->
      <a href="javascript:void(0)" data-bind="text: name, click: function() { $root.interface(name); $parent.breadcrumbs([{'id': '', 'name': name, 'type': type}]); $root.job(null); }" style="text-transform: capitalize"></a>
    <!-- /ko -->
    <!-- ko if: $index() != 0 -->
      <!-- ko if: $index() != $parent.breadcrumbs().length - 1 -->
        <a href="javascript:void(0)" data-bind="text: type, click: function() { $parent.breadcrumbs.splice($index()); $root.job().id(id); $root.job().fetchJob(); }"></a>
        :
        <a href="javascript:void(0)" data-bind="text: id, click: function() { $parent.breadcrumbs.splice($index()); $root.job().id(id); $root.job().fetchJob(); }"></a>
      <!-- /ko -->
      <!-- ko if: $index() == $parent.breadcrumbs().length - 1 -->
        <span data-bind="text: type"></span>
        :
        <span data-bind="text: id"></span>
      <!-- /ko -->
    <!-- /ko -->
  </h2>
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
  <br/>

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

  </br></br>

  <!-- ko with: properties -->
  Map <span data-bind="text: maps_percent_complete"></span> <span data-bind="text: finishedMaps"></span> /<span data-bind="text: desiredMaps"></span>
  Reduce <span data-bind="text: reduces_percent_complete"></span> <span data-bind="text: finishedReduces"></span> / <span data-bind="text: desiredReduces"></span><br/>
  Duration <span data-bind="text: $parent.duration"></span><br/>
  <!-- /ko -->
  </br></br>

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <a href="javascript:void(0)" data-bind="click: function() { control('kill'); }">Stop</a>

  </br>

  <ul class="nav nav-tabs">
    <li class="active"><a href="#job-mapreduce-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#job-mapreduce-page-tasks" data-toggle="tab">${ _('Tasks') }</a></li>
    <li><a href="#job-mapreduce-page-metadata" data-toggle="tab">${ _('Metadata') }</a></li>
    <li><a href="#job-mapreduce-page-counters" data-toggle="tab">${ _('Counters') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="job-mapreduce-page-logs">
      % for name in ['stdout', 'stderr', 'syslog']:
        <a href="javascript:void(0)" data-bind="click: fetchLogs, text: '${ name }'"></a>
      % endfor
      </br>

      <pre data-bind="html: logs['default']"></pre>
    </div>

    <div class="tab-pane" id="job-mapreduce-page-tasks">
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('tasks'); }">Load</a>
      </br>

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
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('metadata'); }">Load</a>

      <span data-bind="text: ko.mapping.toJSON(properties['metadata'])"></span>
    </div>

    <div class="tab-pane" id="job-mapreduce-page-counters">
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('counters'); }">Load</a>

      <span data-bind="text: ko.mapping.toJSON(properties['counters'])"></span>
    </div>
  </div>

</script>


<script type="text/html" id="job-mapreduce-task-page">

  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('progress') } <span data-bind="text: progress"></span>

  <br/><br/>

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

  <ul class="nav nav-tabs">
    <li class="active"><a href="#job-mapreduce-task-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#job-mapreduce-task-page-attempts" data-toggle="tab">${ _('Attempts') }</a></li>
    <li><a href="#job-mapreduce-task-page-counters" data-toggle="tab">${ _('Counters') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="job-mapreduce-task-page-logs">
      % for name in ['stdout', 'stderr', 'syslog']:
        <a href="javascript:void(0)" data-bind="click: fetchLogs, text: '${ name }'"></a>
      % endfor
      </br>

      <pre data-bind="html: logs['default']"></pre>
    </div>

    <div class="tab-pane" id="job-mapreduce-task-page-attempts">
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('attempts'); }">Load</a>
      </br>

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
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('counters'); }">Load</a>

      <span data-bind="text: ko.mapping.toJSON(properties['counters'])"></span>
    </div>
  </div>

</script>


<script type="text/html" id="job-mapreduce-task-attempt-page">

  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('progress') } <span data-bind="text: progress"></span>
  ${ _('type') } <span data-bind="text: type"></span>

  <br/><br/>

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

  <ul class="nav nav-tabs">
    <li class="active"><a href="#job-mapreduce-task-attempt-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#job-mapreduce-task-attempt-page-counters" data-toggle="tab">${ _('Counters') }</a></li>
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
            <a href="javascript:void(0)" data-bind="click: fetchLogs, text: '${ name }'"></a>
          % endfor
          </br>
          <pre data-bind="html: logs['default']"></pre>
        </div>

        <div class="tab-pane" id="job-mapreduce-task-attempt-page-logs-container">
          % for name in ['container-stdout', 'container-stderr', 'container-syslog']:
            <a href="javascript:void(0)" data-bind="click: fetchLogs, text: '${ name }'"></a>
          % endfor
          </br>
          <pre data-bind="html: logs['default']"></pre>
        </div>
      </div>
    </div>

    <div class="tab-pane" id="job-mapreduce-task-attempt-page-counters">
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('counters'); }">Load</a>

      <span data-bind="text: ko.mapping.toJSON(properties['counters'])"></span>
    </div>
  </div>

</script>


<script type="text/html" id="job-impala-page">
  <h2>Impala</h2>
  <br/>

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

  </br></br>
  Variables, Workspace</br>
  Duration 8s</br>
  </br></br>

  <div class="progress-job progress active pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
    <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
  </div>

  <a href="javascript:void(0)" data-bind="click: function() { control('kill'); }">Stop</a> |
  <a href="javascript:void(0)" data-bind="click: function() { control('resume'); }">Resume</a> |
  <a href="javascript:void(0)" data-bind="click: function() { control('rerun'); }">Rerun</a>

  <br/>

  <ul class="nav nav-tabs">
    <li class="active"><a href="#workflow-page-graph" data-toggle="tab">${ _('Graph') }</a></li>
    <li><a href="#workflow-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
    <li><a href="#workflow-page-tasks" data-toggle="tab">${ _('Tasks') }</a></li>
    <li><a href="#workflow-page-metadata" data-toggle="tab">${ _('Properties') }</a></li>
    <li><a href="#workflow-page-xml" data-toggle="tab">${ _('XML') }</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane active" id="workflow-page-graph">
      <span data-bind="html: properties['graph']"></span>
    </div>

    <div class="tab-pane" id="workflow-page-logs">
      <pre data-bind="html: logs['default']"></pre>
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
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('properties'); }">Load</a>
      <br/>

      <span data-bind="text: ko.mapping.toJSON(properties['properties'])"></span>
    </div>

    <div class="tab-pane" id="workflow-page-xml">
      <a href="javascript:void(0)" data-bind="click: function() { return fetchProfile('xml'); }">Load</a>
      <br/>

      <span data-bind="text: ko.mapping.toJSON(properties['xml'])"></span>
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

  </br></br>
  Job ID ....</br>
  Duration 8s</br>
  </br></br>

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

  <!-- ko with: coordVM -->
  <div>
    <table class="table table-striped table-condensed margin-top-10">
    <tbody data-bind="foreach: filteredActions">
      <tr data-bind="css: { disabled: url == '' }">
        <td data-bind="css: { disabled: url == '' }">
          <a data-bind="attr: {href: url != '' ? url : 'javascript:void(0)', title: url ? '' : '${ _ko('Workflow not available or instantiated yet') }' }, css: { disabled: url == '' }" target="_blank">
            <span data-bind="text: title, attr: {'class': statusClass, 'id': 'date-' + $index()}"></span>
          </a>
          <span class="pull-right">
          <i class="fa fa-exclamation-triangle" data-bind="visible: (errorMessage == null || errorMessage == '') && (missingDependencies == null || missingDependencies == '') && url == '', attr: {title: '${ _ko('Workflow not available or instantiated yet') }'}"></i><i class="fa fa-exclamation-triangle" data-bind="visible: errorMessage != null && errorMessage != '', attr: {title: errorMessage}"></i> <i class="fa fa-exclamation-triangle" data-bind="visible:missingDependencies !='' && missingDependencies != null, attr: { title: '${ _ko('Missing')} ' + missingDependencies }"></i>
          </span>
        </td>
      </tr>
    </tbody>
    <tfoot>
      <tr data-bind="visible: filteredActions().length == 0">
        <td>
          <div class="alert">
            ${ _('There are no actions to be shown.') }
          </div>
        </td>
      </tr>
    </tfoot>
  </table>
  </div>
  <!-- /ko -->
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


<script type="text/javascript" charset="utf-8">

  (function () {

    var Job = function (vm, job) {
      var self = this;

      self.id = ko.observableDefault(job.id);
      self.name = ko.observableDefault(job.name);
      self.type = ko.observableDefault(job.type);
      self.status = ko.observableDefault(job.status);
      self.user = ko.observableDefault(job.user);
      self.cluster = ko.observableDefault(job.cluster);
      self.progress = ko.observableDefault(job.progress);
      self.duration = ko.observableDefault(job.duration);
      self.submitted = ko.observableDefault(job.submitted);

      self.logs = ko.mapping.fromJS({'default': ''});

      self.coordVM = new RunningCoordinatorModel([]);

      self.properties = ko.mapping.fromJS(job.properties || {});
      self.mainType = ko.observable(vm.interface());

      self.loadingJob = ko.observable(false);

      self.fetchJob = function () {
        self.loadingJob(true);

        $.post("/jobbrowser/api/job", {
          app_id: ko.mapping.toJSON(self.id),
          interface: ko.mapping.toJSON(vm.interface)
        }, function (data) {
          if (data.status == 0) {
            vm.job(new Job(vm, data.app));
            hueUtils.changeURL('#!' + vm.job().id());
            vm.breadcrumbs.push({'id': vm.job().id(), 'name': vm.job().name(), 'type': vm.job().type()});

            vm.job().fetchLogs();
            if (self.mainType() == 'schedules') {
              vm.job().coordVM.setActions(data.app.actions);
            }
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
          name: name ? name : 'default'
        }, function (data) {
          if (data.status == 0) {
            self.logs['default'](data.logs.logs['default'])
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

    var Jobs = function (vm, options) {
      var self = this;

      self.apps = ko.observableArray();
      self.loadingJobs = ko.observable(false);

      self.username = ko.observable('${ user.username }');

      self.fetchJobs = function () {
        self.loadingJobs(true);
        vm.job(null);
        $.post("/jobbrowser/api/jobs", {
          username: ko.mapping.toJSON(self.username),
          interface: ko.mapping.toJSON(vm.interface)
        }, function (data) {
          if (data.status == 0) {
            var apps = [];
            if (data && data.apps) {
              data.apps.forEach(function (job) { // TODO: update and merge
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

    var JobBrowserViewModel = function (options, RunningCoordinatorModel) {
      var self = this;

      self.apiHelper = ApiHelper.getInstance(options);
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

      self.jobs = new Jobs(self, options);
      self.job = ko.observable();

      self.interface = ko.observable('apps');
      self.interface.subscribe(function (val) {
        hueUtils.changeURL('#!' + val);
        self.breadcrumbs([{'id': '', 'name': val, 'type': val}]);
        self.jobs.fetchJobs();
      });
      self.breadcrumbs = ko.observableArray([]);
      self.breadcrumbs.push({'id': '', 'name': 'apps', 'type': 'apps'});

      self.paginationOffset = ko.observable(0);
      self.paginationResultPage = ko.observable(100);
      self.paginationPage = ko.observable(1);
      self.paginationResultCounts = ko.observable();
    };

    var viewModel;

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
        }
      };

      viewModel = new JobBrowserViewModel(options, RunningCoordinatorModel);
      ko.applyBindings(viewModel, $('#jobbrowserComponents')[0]);

      var loadHash = function () {
        var h = window.location.hash;
        if (h.indexOf('#!') === 0) {
          h = h.substr(2);
        }
        switch (h) {
          case 'apps':
          case 'workflows':
          case 'schedules':
          case 'bundles':
            viewModel.interface(h);
            break;
          default:
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
