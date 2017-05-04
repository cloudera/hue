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
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
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

            <div data-bind="template: { name: 'breadcrumbs' }"></div>
            <!-- ko if: interface() !== 'slas' && interface() !== 'oozie-info' -->
            <!-- ko if: !$root.job() -->
            <form class="form-inline">
              ${_('Filter')} <input type="text" class="input-xlarge search-query" data-bind="textInput: jobs.textFilter" placeholder="${_('Filter by id, name, user...')}" />
              <span data-bind="foreach: jobs.statesValuesFilter">
                <label class="checkbox">
                  <div class="pull-left margin-left-5 status-border status-content" data-bind="css: value, hueCheckbox: checked"></div>
                  <div class="inline-block" data-bind="text: name, toggle: checked"></div>
                </label>
              </span>

              ${_('in the last')} <input class="input-mini no-margin" type="number" min="1" max="3650" data-bind="value: jobs.timeValueFilter">
              <select class="input-small no-margin" data-bind="value: jobs.timeUnitFilter, options: jobs.timeUnitFilterUnits, optionsText: 'name', optionsValue: 'value'">
                <option value="days">${_('days')}</option>
                <option value="hours">${_('hours')}</option>
                <option value="minutes">${_('minutes')}</option>
              </select>

              <a class="btn" title="${ _('Refresh') }" data-bind="click: jobs.updateJobs">
                <i class="fa fa-refresh"></i>
              </a>

              <!-- ko ifnot: $root.isMini -->
              <div data-bind="template: { name: 'job-actions', 'data': jobs }" class="pull-right"></div>
              <!-- /ko -->
            </form>


            <div class="card card-small">
              <!-- ko hueSpinner: { spin: jobs.loadingJobs(), center: true, size: 'xlarge' } --><!-- /ko -->
              <!-- ko ifnot: jobs.loadingJobs() -->
                <!-- ko if: $root.isMini -->
                <ul class="unstyled" id="jobsTable" data-bind="foreach: jobs.apps">
                  <li class="status-border pointer" data-bind="css: {'completed': apiStatus() == 'SUCCEEDED', 'running': isRunning(), 'failed': apiStatus() == 'FAILED'}, click: fetchJob">
                    <span class="muted pull-left" data-bind="momentFromNow: {data: submitted, interval: 10000, titleFormat: 'LLL'}"></span><span data-bind="text: status"></span></td>
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
                <table id="jobsTable" class="datatables table table-condensed">
                  <thead>
                  <tr>
                    <th width="1%"><div class="select-all hueCheckbox fa" data-bind="hueCheckAll: { allValues: jobs.apps, selectedValues: jobs.selectedJobs }"></div></th>
                    <th width="15%">${_('Id')}</th>
                    <th width="20%">${_('Name')}</th>
                    <th width="3%">${_('Duration')}</th>
                    <th width="10%">${_('Started')}</th>
                    <th width="7%">${_('Type')}</th>
                    <th width="5%">${_('Status')}</th>
                    <th width="5%">${_('Progress')}</th>
                    <th width="10%">${_('User')}</th>
                  </tr>
                  </thead>
                  <tbody data-bind="foreach: jobs.apps">
                    <tr class="status-border pointer" data-bind="css: {'completed': apiStatus() == 'SUCCEEDED', 'running': isRunning(), 'failed': apiStatus() == 'FAILED'}, click: fetchJob">
                      <td>
                        <div class="hueCheckbox fa" data-bind="click: function() {}, clickBubble: false, multiCheck: '#jobsTable', value: $data, hueChecked: $parent.jobs.selectedJobs"></div>
                      </td>
                      <td data-bind="text: id"></td>
                      <td data-bind="text: name"></td>
                      <td data-bind="text: duration().toHHMMSS()"></td>
                      <td data-bind="moment: {data: submitted, format: 'LLL'}"></td>
                      <td data-bind="text: type"></td>
                      <td data-bind="text: status"></td>
                      <td data-bind="text: progress"></td>
                      <td data-bind="text: user"></td>
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

          <div data-bind="template: { name: 'pagination', data: $root.jobs }, visible: ! $root.job()"></div>
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
  <div id="rerun-modal" class="modal hide" data-bind="html: $root.job().rerunModalContent"></div>
<!-- /ko -->

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
    <ul class="inline hue-breadcrumbs-bar" data-bind="foreach: breadcrumbs">
      <li>
      <!-- ko if: $index() > 1 -->
        <span class="divider">&gt;</span>
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
    <!-- ko if: ! $root.isMini() -->
      <!-- ko if: ['workflows', 'schedules', 'bundles', 'slas'].indexOf(interface()) > -1 -->
      <span class="pull-right">
        <a href="javascript:void(0)" data-bind="click: function() { $root.selectInterface('oozie-info') }">${ _('Configuration') }</a>
      </span>
      <!-- /ko -->
    <!-- /ko -->
  </h3>
</script>


<script type="text/html" id="pagination">
  <!-- ko ifnot: hasPagination -->
  <div class="inline">
    <span data-bind="text: paginationResultCounts()"></span>
    ${ _('jobs') }
  </div>
  <!-- /ko -->

  <!-- ko if: hasPagination -->
  <div class="inline">
    <div class="inline">
      ${ _('Showing') }
      <span data-bind="text: Math.min((paginationPage() - 1) * paginationResultPage() + 1, paginationResultCounts())"></span>
      ${ _('to')}
      <span data-bind="text: Math.min(paginationPage() * paginationResultPage(), paginationResultCounts())"></span>
      ${ _('of') }
      <span data-bind="text: paginationResultCounts"></span>

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
  <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
    </div>
  </div>
</script>


<script type="text/html" id="job-mapreduce-page">


  <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko with: properties -->
          <li class="nav-header">${ _('Map') }</li>
          <li><span data-bind="text: maps_percent_complete"></span> <span data-bind="text: finishedMaps"></span> /<span data-bind="text: desiredMaps"></span></li>
          <li class="nav-header">${ _('Reduce') }</li>
          <li><span data-bind="text: reduces_percent_complete"></span> <span data-bind="text: finishedReduces"></span> / <span data-bind="text: desiredReduces"></span></li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: $parent.duration"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
      <div class="clearfix"></div>

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
          ${_('Filter')}
          <input data-bind="textFilter: textFilter, clearable: {value: textFilter}" type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">

          <span data-bind="foreach: statesValuesFilter">
            <label class="checkbox">
              <input type="checkbox" data-bind="checked: checked, attr: {id: name}">
              <span data-bind="text: name, attr: {for: name}"></span>
            </label>
          </span>

          <span data-bind="foreach: typesValuesFilter">
            <label class="checkbox">
              <input type="checkbox" data-bind="checked: checked, attr: {id: name}">
              <span data-bind="text: name, attr: {for: name}"></span>
            </label>
          </span>

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

    </div>
  </div>

</script>


<script type="text/html" id="job-mapreduce-task-page">

  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko with: properties -->
          <li class="nav-header">${ _('State') }</li>
          <li><span data-bind="text: state"></span></li>
          <li class="nav-header">${ _('Start time') }</li>
          <li><span data-bind="text: startTime"></span></li>
          <li class="nav-header">${ _('Successful attempt') }</li>
          <li><span data-bind="text: successfulAttempt"></span></li>
          <li class="nav-header">${ _('Finish time') }</li>
          <li><span data-bind="text: finishTime"></span></li>
          <li class="nav-header">${ _('Elapsed time') }</li>
          <li><span data-bind="text: elapsedTime"></span></li>
          <!-- /ko -->

        </ul>
      </div>
    </div>
    <div class="span10">
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
    </div>
  </div>

</script>


<script type="text/html" id="job-mapreduce-task-attempt-page">

  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
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
          <li><span data-bind="text: startTime"></span></li>
          <li class="nav-header">${ _('Finish time') }</li>
          <li><span data-bind="text: finishTime"></span></li>
          <li class="nav-header">${ _('Elapsed time') }</li>
          <li><span data-bind="text: elapsedTime"></span></li>
          <!-- /ko -->

        </ul>
      </div>
    </div>
    <div class="span10">

      <ul class="nav nav-tabs margin-top-20">
        <li class="active"><a href="#job-mapreduce-task-attempt-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#job-mapreduce-task-attempt-page-counters" data-bind="click: function(){ fetchProfile('counters'); $('a[href=\'#job-mapreduce-task-attempt-page-counters\']').tab('show'); }">${ _('Counters') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="job-mapreduce-task-attempt-page-logs">
          % for name in ['stdout', 'stderr', 'syslog']:
            <a href="javascript:void(0)" data-bind="click: function() { fetchLogs('${ name }'); }, text: '${ name }'"></a>
          % endfor
          <br>
          <pre data-bind="html: logs"></pre>
        </div>

        <div class="tab-pane" id="job-mapreduce-task-attempt-page-counters">
          <pre data-bind="text: ko.toJSON(properties['counters'], null, 2)"></pre>
        </div>
      </div>

    </div>
  </div>

</script>


<script type="text/html" id="job-impala-page">
   <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
    </div>
  </div>
</script>


<script type="text/html" id="job-spark-page">
   <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
    </div>
  </div>
</script>


<script type="text/html" id="job-actions">
  <div class="btn-group">
    <!-- ko if: hasResume -->
    <button class="btn" title="${ _('Resume selected') }" data-bind="click: function() { control('resume'); }, enable: resumeEnabled">
      <i class="fa fa-play"></i> ${ _('Resume') }
    </button>
    <!-- /ko -->

    <!-- ko if: hasPause -->
    <button class="btn" title="${ _('Suspend selected') }" data-bind="click: function() { control('suspend'); }, enable: pauseEnabled">
      <i class="fa fa-pause"></i> ${ _('Suspend') }
    </button>
    <!-- /ko -->

    <!-- ko if: hasRerun -->
    <button class="btn" title="${ _('Rerun selected') }" data-bind="click: function() { control('rerun'); }, enable: rerunEnabled">
      <i class="fa fa-repeat"></i> ${ _('Rerun') }
    </button>
    <!-- /ko -->

    <!-- ko if: hasKill -->
    <button class="btn btn-danger" title="${_('Stop selected')}" data-bind="click: function() { control('kill'); }, enable: killEnabled">
      ## TODO confirmation
      <i class="fa fa-times"></i> ${_('Kill')}
    </button>
    <!-- /ko -->

    <!-- ko if: hasIgnore -->
    <button class="btn btn-danger" title="${_('Ignore selected')}" data-bind="click: function() { control('ignore'); }, enable: ignoreEnabled">
      ## TODO confirmation
      <i class="fa fa-eraser"></i> ${_('Ignore')}
    </button>
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="workflow-page">

  <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': isRunning(), 'progress-success': apiStatus() === 'SUCCEEDED', 'progress-danger': apiStatus() === 'FAILED'}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
      <div class="clearfix"></div>

      <ul class="nav nav-tabs margin-top-20">
        <li class="active"><a href="#workflow-page-graph" data-toggle="tab">${ _('Graph') }</a></li>
        <li><a href="#workflow-page-metadata" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#workflow-page-metadata\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a href="#workflow-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#workflow-page-tasks" data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a href="#workflow-page-xml" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#workflow-page-xml\']').tab('show'); }">${ _('XML') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="workflow-page-graph">
        </div>

        <div class="tab-pane" id="workflow-page-logs">
          <pre data-bind="html: logs"></pre>
        </div>

        <div class="tab-pane" id="workflow-page-tasks">
          <table id="actionsTable" class="datatables table table-condensed">
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
    </div>
  </div>
</script>


<script type="text/html" id="workflow-action-page">

  <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      Log (if external id) | Child jobs
    </div>
  </div>

</script>


<script type="text/html" id="schedule-page">

  <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
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
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
      <div class="clearfix"></div>

      <ul class="nav nav-tabs">
        <li class="active"><a href="#schedule-page-task" data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a href="#schedule-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#schedule-page-metadata" data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#schedule-page-metadata\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a href="#schedule-page-xml" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#schedule-page-xml\']').tab('show'); }">${ _('XML') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="schedule-page-calendar">
          <!-- ko with: coordinatorActions() -->
          <div data-bind="template: { name: 'job-actions' }"></div>

          ${_('Filter')}
          <input data-bind="value: textFilter" type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">

          <span data-bind="foreach: statesValuesFilter">
            <label class="checkbox">
              <input type="checkbox" data-bind="checked: checked, attr: {id: name}">
              <span data-bind="text: name, attr: {for: name}"></span>
            </label>
          </span>

          <table id="schedulesTable" class="datatables table table-condensed">
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
              <tr data-bind="click: function() {  if (properties.externalId()) { $root.job().id(properties.externalId()); $root.job().fetchJob();} }">
                <td>
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

        <div class="tab-pane" id="schedule-page-logs">
          <pre data-bind="html: logs"></pre>
        </div>

        <div class="tab-pane" id="schedule-page-metadata">
          <pre data-bind="text: ko.toJSON(properties['properties'], null, 2)"></pre>
        </div>

        <div class="tab-pane" id="schedule-page-xml">
          <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="bundle-page">

  <div class="row-fluid">
    <div class="span2">
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
          <li><span data-bind="text: progress"></span></li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': progress() < 100, 'progress-success': progress() === 100}">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration"></span></li>
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
    <div class="span10">
      <div class="pull-right" data-bind="template: { name: 'job-actions' }"></div>
      <div class="clearfix"></div>

      <ul class="nav nav-tabs">
        <li class="active"><a href="#bundle-page-coordinators" data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a href="#bundle-page-logs" data-toggle="tab">${ _('Logs') }</a></li>
        <li><a href="#bundle-page-metadata"  data-bind="click: function(){ fetchProfile('properties'); $('a[href=\'#bundle-page-metadata\']').tab('show'); }">${ _('Properties') }</a></li>
        <li><a href="#bundle-page-xml" data-bind="click: function(){ fetchProfile('xml'); $('a[href=\'#bundle-page-xml\']').tab('show'); }">${ _('XML') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="bundle-page-coordinators">
          <div data-bind="template: { name: 'job-actions' }"></div>

          ${_('Filter')} <input type="text" class="input-xlarge search-query"  placeholder="${_('Filter by id, name, user...')}" />
          <div class="btn-group">
            <select size="3" multiple="true"></select>
            <a class="btn btn-status btn-success" data-value="completed">${ _('Succeeded') }</a>
            <a class="btn btn-status btn-warning" data-value="running">${ _('Running') }</a>
            <a class="btn btn-status btn-danger disable-feedback" data-value="failed">${ _('Failed') }</a>
          </div>

          <table id="coordsTable" class="datatables table table-condensed">
            <thead>
            <tr>
              <th width="1%"><div class="select-all hueCheckbox fa"></div></th>
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
              <tr data-bind="click: function() {  if (id()) { $root.job().id(id()); $root.job().fetchJob();} }">
                <td><div class="hueCheckbox fa"></div></td>
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
          </table>    </div>

        <div class="tab-pane" id="bundle-page-logs">
          <pre data-bind="html: logs"></pre>
        </div>

        <div class="tab-pane" id="bundle-page-metadata">
          <pre data-bind="text: ko.toJSON(properties['properties'], null, 2)"></pre>
        </div>

        <div class="tab-pane" id="bundle-page-xml">
          <div data-bind="readonlyXML: properties['xml'], path: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>

</script>


<script type="text/javascript">

  (function () {

    var Job = function (vm, job) {
      var self = this;

      self.id = ko.observableDefault(job.id);
      self.name = ko.observableDefault(job.name);
      self.type = ko.observableDefault(job.type);

      self.status = ko.observableDefault(job.status);
      self.apiStatus = ko.observableDefault(job.apiStatus);
      self.progress = ko.observableDefault(job.progress);
      self.isRunning = ko.computed(function() {
        return self.apiStatus() == 'RUNNING' || self.apiStatus() == 'PAUSED';
      });

      self.user = ko.observableDefault(job.user);
      self.cluster = ko.observableDefault(job.cluster);
      self.duration = ko.observableDefault(job.duration);
      self.submitted = ko.observableDefault(job.submitted);

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

      self.rerunModalContent = ko.observable('');

      self.hasKill = ko.pureComputed(function() {
        return ['MAPREDUCE', 'SPARK', 'workflow', 'schedule', 'bundle'].indexOf(self.type()) != -1;
      });
      self.killEnabled = ko.pureComputed(function() {
        return self.hasKill() && self.apiStatus() == 'RUNNING';
      });

      self.hasResume = ko.pureComputed(function() {
        return ['workflow', 'schedule', 'bundle'].indexOf(self.type()) != -1;
      });
      self.resumeEnabled = ko.pureComputed(function() {
        return self.hasResume() && self.apiStatus() == 'PAUSED';
      });

      self.hasRerun = ko.pureComputed(function() {
        return ['workflow', 'schedule-task'].indexOf(self.type()) != -1;
      });
      self.rerunEnabled = ko.pureComputed(function() {
        return self.hasRerun() && ! self.isRunning();
      });

      self.hasPause = ko.pureComputed(function() {
        return ['workflow', 'schedule', 'bundle'].indexOf(self.type()) != -1;
      });
      self.pauseEnabled = ko.pureComputed(function() {
        return self.hasPause() && self.apiStatus() == 'RUNNING';
      });

      self.hasIgnore = ko.pureComputed(function() {
        return ['schedule-task'].indexOf(self.type()) != -1;
      });
      self.ignoreEnabled = ko.pureComputed(function() {
        return self.hasIgnore() && ! self.isRunning();
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

      self.conditionalFetchJob = function () {
        if (vm.isMini()) {
          huePubSub.publish('hide.jobs.panel');
          if (window.location.pathname.indexOf('jobbrowser') > -1) {
            window.location.hash = '#!id=' + self.id();
          }
          else {
            huePubSub.publish('open.link', '/jobbrowser/#!id=' + self.id())
          }
        }
        else {
          self.fetchJob();
        }
      };

      self.fetchJob = function () {
        vm.apiHelper.cancelActiveRequest(lastFetchJobRequest);
        vm.apiHelper.cancelActiveRequest(lastUpdateJobRequest);

        self.loadingJob(true);

        var interface = vm.interface();
        if (/oozie-oozi-W/.test(self.id())) {
          interface = 'workflows';
        }
        else if (/oozie-oozi-C/.test(self.id())) {
          interface = 'schedules';
        }
        else if (/oozie-oozi-B/.test(self.id())) {
          interface = 'bundles';
        }

        interface = vm.isValidInterface(interface);
        vm.interface(interface);

        lastFetchJobRequest = self._fetchJob(function (data) {
          if (data.status == 0) {
            vm.interface(interface);
            vm.job(new Job(vm, data.app));

            hueUtils.changeURL('#!id=' + vm.job().id());
            var crumbs = [];

            if (/^attempt_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
              crumbs.push({'id': vm.job().properties['task_id'], 'name': vm.job().properties['task_id'], 'type': 'task'});
            }
            if (/^task_/.test(vm.job().id())) {
              crumbs.push({'id': vm.job().properties['app_id'], 'name': vm.job().properties['app_id'], 'type': 'app'});
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

            if (vm.job().type() === 'workflow' && !vm.job().workflowGraphLoaded) {
              vm.job().updateWorkflowGraph();
            }

            vm.job().fetchLogs();

          } else {
            $(document).trigger("error", data.message);
          }
        }).always(function () {
          self.loadingJob(false);
        });
      };

      self.updateJob = function () {console.log('update job');
        vm.apiHelper.cancelActiveRequest(lastUpdateJobRequest);

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
            $('#rerun-modal').modal('show');
            self.rerunModalContent(response);
          });
        } else {
          vm.jobs._control([self.id()], action, function(data) {
              $(document).trigger("info", data.message);
              self.fetchStatus();
          });
        }
      }

      self.workflowGraphLoaded = false;
      self.updateWorkflowGraph = function() {
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
              self.workflowGraphLoaded = true;
              $('#workflow-page-graph').html(response);
              updateArrowPosition();
              arrowsPolling();
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
        return ['jobs', 'workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1 && ! self.isCoordinator();
      });
      self.killEnabled = ko.pureComputed(function() {
        return self.hasKill() && self.selectedJobs().length > 0 && $.grep(self.selectedJobs(), function(job) {
          return job.killEnabled();
        }).length == self.selectedJobs().length;
      });

      self.hasResume = ko.pureComputed(function() {
        return ['workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1 && ! self.isCoordinator();
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
        return ['workflows', 'schedules', 'bundles'].indexOf(vm.interface()) != -1 && ! self.isCoordinator();
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
      self.paginationOffset = ko.observable(1);
      self.paginationResultPage = ko.observable(100);
      self.paginationResultCounts = ko.computed(function() {
        return self.apps().length;
      });
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

      self.filters = ko.pureComputed(function() {
        return [
          {'text': self.textFilter()},
          {'time': {'time_value': self.timeValueFilter(), 'time_unit': self.timeUnitFilter()}},
          {'states': ko.mapping.toJS(self.statesFilter())},
          {'pagination': self.pagination()},
        ];
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

      self.updateJobs = function () {console.log('update jobs');
        vm.apiHelper.cancelActiveRequest(lastUpdateJobsRequest);

        lastFetchJobsRequest = self._fetchJobs(function(data) {
          var apps = [];
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
              self.apps().splice(i, self.apps().length - i);
            }

            newJobs.forEach(function (job) {
              self.apps.push(job);
            });

            self.totalApps(data.total);
          }
        });
      };

      self.control = function (action) {
        if (action == 'rerun') {
          $.get('/oozie/rerun_oozie_coord/' + vm.job().id() + '/?format=json', function(response) {
            $('#rerun-modal').modal('show');
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
        var schedulerInterfaceCondition = function () {
          return self.appConfig() && self.appConfig()['scheduler'] && self.appConfig()['scheduler']['interpreters'].length > 0;
        }

        var interfaces = [
          {'interface': 'jobs', 'label': '${ _ko('Jobs') }', 'condition': jobsInterfaceCondition},
          {'interface': 'workflows', 'label': '${ _ko('Workflows') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'schedules', 'label': '${ _ko('Schedules') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'bundles', 'label': '${ _ko('Bundles') }', 'condition': schedulerInterfaceCondition},
          {'interface': 'slas', 'label': '${ _ko('SLAs') }', 'condition': schedulerInterfaceCondition},
        ];

        return interfaces.filter(function (i) {
          return i.condition()
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
        if (flatAvailableInterfaces.indexOf(name) != -1) {
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
        hueUtils.changeURL('#!' + interface);
        % endif
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
      var clock;
      self.job.subscribe(function(val) {
        clearInterval(clock);
        if (self.interface() && self.interface() !== 'slas' && self.interface() !== 'oozie-info'){
          if (val) {
            clock = setInterval(val.updateJob, 5000, 'jobbrowser');
          } else {
            clock = setInterval(self.jobs.updateJobs, 20000, 'jobbrowser');
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

      self.load = function() {
        var h = window.location.hash;

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
            self.selectInterface(h);
            break;
          default:
            if (h.indexOf('id=') === 0 && ! self.isMini()){
              new Job(viewModel, {id: h.substr(3)}).fetchJob();
            }
            else {
              self.selectInterface('reset');
            }
        }
      }
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
      viewModel = new JobBrowserViewModel();
      % if not is_mini:
      ko.applyBindings(viewModel, $('#jobbrowserComponents')[0]);
      % else:
      ko.applyBindings(viewModel, $('#jobbrowserMiniComponents')[0]);
      viewModel.isMini(true);
      % endif

      var loadHash = function () {
        if (window.location.pathname.indexOf('jobbrowser') > -1) {
          viewModel.load();
        }
      };

      window.onhashchange = function () {
        loadHash();
      }

      huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
        viewModel.appConfig(clusterConfig && clusterConfig['app_config']);
        loadHash();
      });

      huePubSub.publish('cluster.config.get.config');

      % if not is_mini:
      huePubSub.subscribe('submit.rerun.popup.return', function (data) {
        $.jHueNotify.info('${_('Rerun submitted.')}');
        $('#rerun-modal').modal('hide');
        viewModel.job().apiStatus('RUNNING');
        viewModel.job().updateJob();
      }, 'jobbrowser');
      % else:
      viewModel.selectInterface('jobs');
      huePubSub.subscribe('mini.jb.navigate', function(interface){
        viewModel.selectInterface(interface);
      });
      % endif
    });
  })();
</script>
</span>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
