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
  import sys

  from impala.conf import COORDINATOR_URL as IMPALA_COORDINATOR_URL
  from jobbrowser.conf import DISABLE_KILLING_JOBS

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%def name="include()">
<script type="text/html" id="jb-apps-list">
  <table data-bind="attr: {id: tableId}"
         class="datatables table table-condensed status-border-container hue-jobs-table">
    <thead>
    <tr>
      <th width="1%" class="vertical-align-middle">
        <div class="select-all hue-checkbox fa"
             data-bind="hueCheckAll: { allValues: apps, selectedValues: selectedJobs }"></div>
      </th>
      <th width="20%">${_('Name')}</th>
      <th width="6%">${_('User')}</th>
      <th width="6%">${_('Type')}</th>
      <th width="5%">${_('Status')}</th>
      <th width="3%">${_('Progress')}</th>
      <th width="5%">${_('Group')}</th>
      <th width="10%" data-bind="text: $root.interface() != 'schedules' ? '${_('Started')}' : '${_('Next Materialized')}'"></th>
      <th width="6%">${_('Duration')}</th>
      <th width="15%">${_('Id')}</th>
    </tr>
    </thead>
    <tbody data-bind="foreach: apps">
    <tr class="status-border pointer" data-bind="
      css: {
        'completed': apiStatus() == 'SUCCEEDED',
        'info': apiStatus() == 'PAUSED',
        'running': apiStatus() == 'RUNNING',
        'failed': apiStatus() == 'FAILED'
      },
      click: function (data, event) {
        onTableRowClick(event, id());
      }
    ">
      <td data-bind="click: function() {}, clickBubble: false">
        <div class="hue-checkbox fa" data-bind="
          click: function() {},
          clickBubble: false,
          multiCheck: '#' + $parent.tableId,
          value: $data,
          hueChecked: $parent.selectedJobs
        "></div>
      </td>
      <td data-bind="text: name"></td>
      <td data-bind="text: user"></td>
      <td data-bind="text: type"></td>
      <td><span class="label job-status-label" data-bind="text: status"></span></td>
      <!-- ko if: progress() !== '' -->
      <td data-bind="text: $root.formatProgress(progress)"></td>
      <!-- /ko -->
      <!-- ko if: progress() === '' -->
      <td data-bind="text: ''"></td>
      <!-- /ko -->
      <td data-bind="text: queue"></td>
      <td data-bind="moment: {data: submitted, format: 'LLL'}"></td>
      <td data-bind="text: duration() ? duration().toHHMMSS() : ''"></td>
      <td data-bind="text: id"></td>
    </tr>
    </tbody>
  </table>
</script>

<script type="text/html" id="jb-create-cluster-content">
  <form>
    <fieldset>
      <label for="clusterCreateName">${ _('Name') }</label>
      <input id="clusterCreateName" type="text" placeholder="${ _('Name') }"
             data-bind="clearable: jobs.createClusterName, valueUpdate: 'afterkeydown'">

      <!-- ko if: $root.interface() == 'dataware2-clusters' -->
      <label for="clusterCreateWorkers">${ _('Workers') }</label>
      <input id="clusterCreateWorkers" type="number" min="1"
             data-bind="value: jobs.createClusterWorkers, valueUpdate: 'afterkeydown'" class="input-mini"
             placeholder="${_('Size')}">
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
    <button class="btn btn-primary close-template-popover" data-bind="
      click: jobs.createCluster,
      enable: jobs.createClusterName().length > 0 && jobs.createClusterWorkers() > 0
    " title="${ _('Start creation') }">
      ${ _('Create') }
    </button>
  </div>
</script>

<script type="text/html" id="jb-configure-cluster-content">
  <form>
    <fieldset>
      <label for="clusterConfigureWorkers">${ _('Workers') }</label>
      <span data-bind="visible: !updateClusterAutoResize()">
        <input id="clusterConfigureWorkers" type="number" min="1"
               data-bind="value: updateClusterWorkers, valueUpdate: 'afterkeydown'" class="input-mini"
               placeholder="${_('Size')}">
      </span>
      <span data-bind="visible: updateClusterAutoResize()">
        <input type="number" min="0" data-bind="value: updateClusterAutoResizeMin, valueUpdate: 'afterkeydown'"
               class="input-mini" placeholder="${_('Min')}">
        <input type="number" min="0" data-bind="value: updateClusterAutoResizeMax, valueUpdate: 'afterkeydown'"
               class="input-mini" placeholder="${_('Max')}">
        <input type="number" min="0" data-bind="value: updateClusterAutoResizeCpu, valueUpdate: 'afterkeydown'"
               class="input-mini" placeholder="${_('CPU')}">
      </span>

      <label class="checkbox" style="margin-right: 10px; float: right;">
        <input type="checkbox" data-bind="checked: updateClusterAutoResize"> ${ _('Auto resize') }
      </label>
    </fieldset>
  </form>
  <div style="width: 100%; text-align: right;">
    <button class="btn close-template-popover" title="${ _('Cancel') }">${ _('Cancel') }</button>
    <button class="btn btn-primary close-template-popover"
            data-bind="click: updateCluster, enable: clusterConfigModified" title="${ _('Update') }">
      ${ _('Update') }
    </button>
  </div>
</script>

<script type="text/html" id="jb-hive-queries-template">
  <queries-list></queries-list>
</script>

<script type="text/html" id="jb-impala-queries-template">
  <impala-queries></impala-queries>
</script>

<script type="text/html" id="jb-breadcrumbs-icons">
  <!-- ko switch: type -->
  <!-- ko case: 'workflow' -->
  <img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }" />
  <!-- /ko -->
  <!-- ko case: 'workflow-action' -->
  <i class="fa fa-fw fa-code-fork"></i>
  <!-- /ko -->
  <!-- ko case: 'schedule' -->
  <img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon"
       alt="${ _('Oozie coordinator icon') }" />
  <!-- /ko -->
  <!-- ko case: 'bundle' -->
  <img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }" />
  <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="jb-breadcrumbs">
  <h3 class="jb-breadcrumbs">
    <ul class="inline hue-breadcrumbs-bar">
      <!-- ko foreach: breadcrumbs -->
      <li>
        <!-- ko if: $index() > 1 -->
        <span class="divider">&gt;</span>
        <!-- /ko -->

        <!-- ko if: $index() != 0 -->
        <!-- ko if: $index() != $parent.breadcrumbs().length - 1 -->
        <a href="javascript:void(0)" data-bind="
          click: function() {
            $parent.breadcrumbs.splice($index());
            $root.job().id(id);
            $root.job().fetchJob();
          }
        ">
          <span data-bind="template: 'jb-breadcrumbs-icons'"></span>
          <span data-bind="text: name"></span></a>
        <!-- /ko -->
        <!-- ko if: $index() == $parent.breadcrumbs().length - 1 -->
        <span data-bind="template: 'jb-breadcrumbs-icons'"></span>
        <span data-bind="text: name, attr: { title: id }"></span>
        <!-- /ko -->
        <!-- /ko -->
      </li>
      <!-- /ko -->

      <!-- ko ifnot: $root.isMini() -->
      <!-- ko if: ['workflows', 'schedules', 'bundles', 'slas'].indexOf(interface()) > -1 -->
      <li class="pull-right">
        <a href="javascript:void(0)" data-bind="
          click: function() {
            $root.selectInterface('oozie-info')
          }
        ">${ _('Configuration') }</a>
      </li>
      <!-- /ko -->
      <!-- /ko -->
    </ul>
  </h3>
</script>

<script type="text/html" id="jb-pagination">
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
    </div>

    <ul class="inline">
      <li class="previous-page" data-bind="visible: showPreviousPage">
        <a href="javascript:void(0);" data-bind="click: previousPage" title="${_('Previous page')}"><i
          class="fa fa-backward"></i></a>
      </li>
      <li class="next-page" data-bind="visible: showNextPage">
        <a href="javascript:void(0);" data-bind="click: nextPage" title="${_('Next page')}"><i
          class="fa fa-forward"></i></a>
      </li>
    </ul>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="jb-job-page">
  <!-- ko if: type() == 'MAPREDUCE' -->
  <div data-bind="template: { name: 'jb-job-mapreduce-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'MAP' || type() == 'REDUCE' -->
  <div data-bind="template: { name: 'jb-job-mapreduce-task-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'MAP_ATTEMPT' || type() == 'REDUCE_ATTEMPT' -->
  <div data-bind="template: { name: 'jb-job-mapreduce-task-attempt-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YARN' -->
  <div data-bind="template: { name: 'jb-job-yarn-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YarnV2' -->
  <div data-bind="template: { name: 'jb-job-yarnv2-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'YarnV2_ATTEMPT' -->
  <div data-bind="template: { name: 'jb-job-yarnv2-attempt-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'SPARK' -->
  <div data-bind="template: { name: 'jb-job-spark-page', data: $root.job() }"></div>
  <!-- /ko -->

  <!-- ko if: type() == 'SPARK_EXECUTOR' -->
  <div data-bind="template: { name: 'jb-job-spark-executor-page', data: $root.job() }"></div>
  <!-- /ko -->
</script>

<script type="text/html" id="jb-history-page">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="hueLink: doc_url" title="${ _('Open in editor') }">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-danger': apiStatus() === 'FAILED',
                'progress-warning': apiStatus() === 'RUNNING',
                'progress-success': apiStatus() === 'SUCCEEDED'
              }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css: {'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">

      <ul class="nav nav-pills margin-top-20">
        <li>
          <a data-bind="
            attr: {
              href: $root.contextId('#history-page-statements')
            },
            click: function() {
              fetchProfile('properties');
              $root.showTab('#history-page-statements');
            }
          ">${ _('Properties') }</a>
        </li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="
          attr: {
            id: $root.contextId('history-page-statements')
          }
        ">
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

<script type="text/html" id="jb-job-yarn-page">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                'progress-success': apiStatus() !== 'FAILED' && progress() === 100,
                'progress-danger': apiStatus() === 'FAILED'
              }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <div class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-mapreduce-page">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini()}">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li><span data-bind="text: id"></span></li>
          <!-- ko ifnot: $root.isMini() -->
          <li data-bind="visible: id() != name()" class="nav-header">${ _('Name') }</li>
          <li data-bind="visible: id() != name(), attr: {title: name}"><span
            data-bind="text: name"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                'progress-success': apiStatus() !== 'FAILED' && progress() === 100,
                'progress-danger': apiStatus() === 'FAILED'
              },
              attr: { title: status }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
          <!-- ko with: properties -->
          <li class="nav-header">${ _('Map') }</li>
          <li><span data-bind="text: maps_percent_complete"></span>% <span data-bind="text: finishedMaps"></span> /<span
            data-bind="text: desiredMaps"></span></li>
          <li class="nav-header">${ _('Reduce') }</li>
          <li><span data-bind="text: reduces_percent_complete"></span>% <span data-bind="text: finishedReduces"></span>
            / <span data-bind="text: desiredReduces"></span></li>
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
        <li class="active"><a class="jb-logs-link" data-toggle="tab" data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-page-logs')
          }
        ">${ _('Logs') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-page-tasks')
          },
          click: function() {
            fetchProfile('tasks');
            $root.showTab('#job-mapreduce-page-tasks');
          }
        ">${ _('Tasks') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-page-metadata')
          },
          click: function() {
            fetchProfile('metadata');
            $root.showTab('#job-mapreduce-page-metadata');
          }
        ">${ _('Metadata') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-page-counters')
          },
          click: function() {
            fetchProfile('counters');
            $root.showTab('#job-mapreduce-page-counters');
          }
        ">${ _('Counters') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-page-logs')
          }
        ">
          <ul class="nav nav-tabs">
            <li class="active"><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('default');
                logActive('default');
              }
            ">default</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stdout');
                logActive('stdout');
              }
            ">stdout</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stderr');
                logActive('stderr');
              }
            ">stderr</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('syslog');
                logActive('syslog');
              }
            ">syslog</a></li>
          </ul>
          <!-- ko if: properties.diagnostics() -->
          <pre data-bind="text: properties.diagnostics"></pre>
          <!-- /ko -->
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-page-tasks')
          }
        ">
          <form class="form-inline">
            <input data-bind="textFilter: textFilter, clearable: {value: textFilter}, valueUpdate: 'afterkeydown'"
                   type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">

            <span data-bind="foreach: statesValuesFilter">
              <label class="checkbox">
                <div class="pull-left margin-left-5 status-border status-content"
                     data-bind="css: value, hueCheckbox: checked"></div>
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
            <tr data-bind="
              click: function() {
                $root.job().id(id);
                $root.job().fetchJob();
              },
              css: {
                'completed': apiStatus == 'SUCCEEDED',
                'running': apiStatus == 'RUNNING',
                'failed': apiStatus == 'FAILED'
              }
            " class="status-border pointer">
              <td data-bind="text: type"></td>
              <td data-bind="text: id"></td>
              <td data-bind="text: elapsedTime ? elapsedTime.toHHMMSS() : ''"></td>
              <td data-bind="text: progress"></td>
              <td><span class="label job-status-label" data-bind="text: state"></span></td>
              <td data-bind="moment: {data: startTime, format: 'LLL'}"></td>
              <td data-bind="text: successfulAttempt"></td>
              <td data-bind="moment: {data: finishTime, format: 'LLL'}"></td>
            </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-page-metadata')
          }
        ">
          <div data-bind="template: { name: 'jb-render-metadata', data: properties['metadata'] }"></div>
        </div>

        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-page-counters')
          }
        ">
          <div data-bind="template: { name: 'jb-render-page-counters', data: properties['counters'] }"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-mapreduce-task-page">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                'progress-success': apiStatus() !== 'FAILED' && progress() === 100,
                'progress-danger': apiStatus() === 'FAILED'
              },
              attr: { title: status }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
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
          <li><span data-bind="text: elapsedTime() ? elapsedTime().toHHMMSS() : ''"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-task-page-logs')
          }
        " data-toggle="tab">${ _('Logs') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-task-page-attempts')
          },
          click: function() {
            fetchProfile('attempts');
            $root.showTab('#job-mapreduce-task-page-attempts');
          }
        ">${ _('Attempts') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-task-page-counters')
          },
          click: function() {
            fetchProfile('counters');
            $root.showTab('#job-mapreduce-task-page-counters');
          }
        ">${ _('Counters') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-task-page-logs')
          }
        ">
          <ul class="nav nav-tabs">
            <li class="active"><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stdout');
                logActive('stdout');
              }
            ">stdout</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stderr');
                logActive('stderr');
              }
            ">stderr</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('syslog');
                logActive('syslog');
              }
            ">syslog</a></li>
          </ul>

          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-task-page-attempts')
          }
        ">
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
              <td data-bind="text: elapsedTime ? elapsedTime.toHHMMSS() : ''"></td>
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

        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-task-page-counters')
          }
        ">
          <div data-bind="template: { name: 'jb-render-task-counters', data: properties['counters'] }"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-yarnv2-page">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() == 'RUNNING',
                'progress-success': apiStatus() == 'SUCCEEDED',
                'progress-danger': apiStatus() == 'FAILED'
              },
              attr: { title: status }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('State') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- ko with: properties -->
          <li class="nav-header">${ _('Start time') }</li>
          <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
          <li class="nav-header">${ _('Finish time') }</li>
          <li><span data-bind="moment: {data: finishTime, format: 'LLL'}"></span></li>
          <li class="nav-header">${ _('Elapsed time') }</li>
          <li><span data-bind="text: elapsedTime() ? elapsedTime().toHHMMSS() : ''"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" data-bind="
          attr: {
            href: $root.contextId('#job-yarnv2-page-logs')
          }
        " data-toggle="tab">${ _('Logs') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-yarnv2-page-attempts')
          },
          click: function() {
            fetchProfile('attempts');
            $root.showTab('#job-yarnv2-page-attempts');
          }
        ">${ _('Attempts') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="
          attr: {
            id: $root.contextId('job-yarnv2-page-logs')
          }
        ">
          <ul class="nav nav-tabs scrollable" data-bind="foreach: logsList">
            <li data-bind="
              css: {
                'active': $data == $parent.logActive()
              }
            "><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $parent.fetchLogs($data);
                $parent.logActive($data);
              },
              text: $data
            "></a></li>
          </ul>
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('job-yarnv2-page-attempts') }">
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

<script type="text/html" id="jb-job-yarnv2-attempt-page">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko with: properties -->
          <li class="nav-header">${ _('Attempt Id') }</li>
          <li class="break-word"><span data-bind="text: appAttemptId"></span></li>
          <li class="nav-header">${ _('State') }</li>
          <li><span data-bind="text: state"></span></li>
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Start time') }</li>
          <li><span data-bind="moment: {data: startTime, format: 'LLL'}"></span></li>
          <li class="nav-header">${ _('Node Http Address') }</li>
          <li><span data-bind="text: nodeHttpAddress"></span></li>
          <li class="nav-header">${ _('Elapsed time') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>
    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-mapreduce-task-attempt-page">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() == 'RUNNING',
                'progress-success': apiStatus() == 'SUCCEEDED',
                'progress-danger': apiStatus() == 'FAILED'
              },
              attr: { title: status }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
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
          <li><span data-bind="text: elapsedTime() ? elapsedTime().toHHMMSS() : ''"></span></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: {'span10': !$root.isMini(), 'span12': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="jb-logs-link" data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-task-attempt-page-logs')
          }
        " data-toggle="tab">${ _('Logs') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-mapreduce-task-attempt-page-counters')
          },
          click: function() {
            fetchProfile('counters');
            $root.showTab('#job-mapreduce-task-attempt-page-counters');
          }
        ">${ _('Counters') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active"
             data-bind="attr: { id: $root.contextId('job-mapreduce-task-attempt-page-logs') }">
          <ul class="nav nav-tabs">
            <li class="active"><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stdout');
                logActive('stdout');
              }
            ">stdout</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stderr');
                logActive('stderr');
              }">stderr</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('syslog');
                logActive('syslog');
              }">syslog</a></li>
          </ul>
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>
        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-mapreduce-task-attempt-page-counters')
          }
        ">
          <div data-bind="
            template: {
              name: 'jb-render-attempt-counters',
              data: properties['counters']
            }
          "></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-spark-page">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                'progress-success': apiStatus() !== 'FAILED' && progress() === 100,
                'progress-danger': apiStatus() === 'FAILED'
              }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css: {'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a class="job-spark-logs-link" data-bind="
          attr: {
            href: $root.contextId('#job-spark-page-logs')
          }
        " data-toggle="tab">${ _('Logs') }</a></li>
        <li><a data-bind="
          attr: {
            href: $root.contextId('#job-spark-page-executors')
          },
          click: function() {
            fetchProfile('executors');
            $root.showTab('#job-spark-page-executors');
          }
        ">${ _('Executors') }</a></li>
        <li><a data-bind="attr: { href: $root.contextId('#job-spark-page-properties') }"
               data-toggle="tab">${ _('Properties') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="
          attr: {
            id: $root.contextId('job-spark-page-logs')
          }
        ">
          <ul class="nav nav-tabs">
            <li class="active"><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stdout');
                logActive('stdout');
              }
            ">stdout</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stderr');
                logActive('stderr');
              }
            ">stderr</a></li>
          </ul>

          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>
        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-spark-page-executors')
          }
        ">
          <form class="form-inline">
            <input data-bind="
              textFilter: textFilter,
              clearable: { value: textFilter },
              valueUpdate: 'afterkeydown'
            " type="text" class="input-xlarge search-query" placeholder="${_('Filter by name')}">
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
            <tr data-bind="click: function() { $root.job().id(id); $root.job().fetchJob(); }"
                class="status-border pointer">
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
        <div class="tab-pane" data-bind="
          attr: {
            id: $root.contextId('job-spark-page-properties')
          }
        ">
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
              <td><!-- ko template: { name: 'jb-link-or-text', data: { name: name, value: value } } --><!-- /ko --></td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-spark-executor-page">
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
          <!-- ko ifnot: $root.isMini() -->
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
        <li class="active"><a class="jb-logs-link" data-bind="
          attr: {
            href: $root.contextId('#job-spark-executor-page-logs')
          }
        " data-toggle="tab">${ _('Logs') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="
          attr: {
            id: $root.contextId('job-spark-executor-page-logs')
          }
        ">
          <ul class="nav nav-tabs">
            <li class="active"><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stdout');
                logActive('stdout');
              }
            ">stdout</a></li>
            <li><a href="javascript:void(0)" data-bind="
              click: function(data, e) {
                $(e.currentTarget).parent().siblings().removeClass('active');
                $(e.currentTarget).parent().addClass('active');
                fetchLogs('stderr');
                logActive('stderr');
              }
            ">stderr</a></li>
          </ul>
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-dataeng-job-page">
  <button class="btn" title="${ _('Troubleshoot') }" data-bind="click: troubleshoot">
    <i class="fa fa-tachometer"></i> ${ _('Troubleshoot') }
  </button>

  <!-- ko if: type() == 'dataeng-job-HIVE' -->
  <div data-bind="template: { name: 'jb-dataeng-job-hive-page', data: $root.job() }"></div>
  <!-- /ko -->
</script>

<script type="text/html" id="jb-dataware-clusters-page">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                'progress-success': apiStatus() !== 'FAILED' && progress() === 100,
                'progress-danger': apiStatus() === 'FAILED'
              }
            ">
              <div class="bar" data-bind="style: {'width': '100%'}"></div>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <div class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></div>
    </div>
  </div>

  <br>

  <button class="btn" title="${ _('Troubleshoot') }" data-bind="click: troubleshoot">
    <i class="fa fa-tachometer"></i> ${ _('Troubleshoot') }
  </button>
</script>

<script type="text/html" id="jb-dataware2-clusters-page">
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
            - ${ _('CPU') } <span
            data-bind="text: properties['properties']['workercurrentCPUUtilizationPercentage']"></span>%
            <!-- /ko -->
            <!-- ko if: status() == 'SCALING_UP' || status() == 'SCALING_DOWN' -->
            <i class="fa fa-spinner fa-spin fa-fw"></i>
            <!-- /ko -->
          </li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-warning': status() == 'SCALING_UP' || status() == 'SCALING_DOWN',
                'progress-success': status() == 'ONLINE',
                'progress-danger': apiStatus() === 'FAILED'
              }
            ">
              <div class="bar" data-bind="
                style: {
                  'width': Math.min(
                    properties['properties']['workerReplicas'](),
                    properties['properties']['workerReplicasOnline']()
                  ) / Math.max(
                    properties['properties']['workerReplicasOnline'](),
                    properties['properties']['workerReplicas']()
                  ) * 100 + '%'
                }
              "></div>
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
            <a href="#"
               data-bind="attr: { 'href': properties['properties']['coordinatorEndpoint']['publicHost']() + ':25000' }">
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
        <button class="btn" title="Create cluster" data-bind="
          enable: isRunning(),
          visible: $root.interface() == 'dataware2-clusters',
          templatePopover: {
            placement: 'bottom',
            contentTemplate: 'jb-configure-cluster-content',
            minWidth: '320px',
            trigger: 'click'
          },
          click: updateClusterShow
        ">${ _('Configure') } <i class="fa fa-chevron-down"></i></button>

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
                ${ _("Metrics are not setup") }
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
                  <a class="muted" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i
                    class="fa fa-external-link"></i></a>
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
                  <a class="muted" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i
                    class="fa fa-external-link"></i></a>
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
              <span class="pointer" title="Show 50 more..." style="display: none;"><i
                class="fa fa-ellipsis-h"></i></span>
              <span class="pointer" title="Add privilege"><i class="fa fa-plus"></i></span>
              <span class="pointer" title="Undo" style="display: none;"> &nbsp; <i class="fa fa-undo"></i></span>
              <span class="pointer" title="Save" style="display: none;"> &nbsp; <i class="fa fa-save"></i></span>
            </div>
          </div>
          <div class="tab-pane" id="servicesTroubleshooting">
            <div class="wxm-poc" style="clear: both;">
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Outliers</h4>
                <img src="${ static('desktop/art/wxm_fake/outliers.svg') }" style="height: 440px" />
              </div>
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Statement Types</h4>
                <img src="${ static('desktop/art/wxm_fake/statement_types.svg') }" style="height: 440px" />
              </div>
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Duration</h4>
                <img src="${ static('desktop/art/wxm_fake/duration.svg') }" style="height: 440px" />
              </div>
              <div style="float:left; margin-right: 10px; margin-bottom: 10px;">
                <h4>Memory Utilization</h4>
                <img src="${ static('desktop/art/wxm_fake/memory.svg') }" style="height: 440px" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-dataeng-job-hive-page">
  ${ _('Id') } <span data-bind="text: id"></span>
  ${ _('Name') } <span data-bind="text: name"></span>
  ${ _('Type') } <span data-bind="text: type"></span>
  ${ _('Status') } <span data-bind="text: status"></span>
  ${ _('User') } <span data-bind="text: user"></span>
  ${ _('Progress') } <span data-bind="text: progress"></span>
  ${ _('Duration') } <span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span>
  ${ _('Submitted') } <span data-bind="text: submitted"></span>
  <br>
  <span data-bind="text: ko.mapping.toJSON(properties['properties'])"></span>
</script>

<script type="text/html" id="jb-queries-page">
  <div class="row-fluid" data-jobType="queries">
    <!-- ko if: id() -->
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Id') }</li>
          <li>
            % if hasattr(IMPALA_COORDINATOR_URL, 'get') and not IMPALA_COORDINATOR_URL.get():
            <a data-bind="attr: { href: doc_url_modified }" target="_blank" title="${ _('Open in Impalad') }">
              <span data-bind="text: id"></span>
            </a>
            % else:
            <span data-bind="text: id"></span>
            % endif
            <!-- ko if: $root.isMini() -->
            <div class="progress-job progress" style="background-color: #FFF; width: 100%; height: 4px" data-bind="
              css: {
                'progress-danger': apiStatus() === 'FAILED',
                'progress-warning': apiStatus() === 'RUNNING',
                'progress-success': apiStatus() === 'SUCCEEDED'
              },
              attr: { 'title': progress() + '%' }
            ">
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
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li>
            <span data-bind="text: progress"></span>%
          </li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
              css: {
                'progress-danger': apiStatus() === 'FAILED',
                'progress-warning': apiStatus() === 'RUNNING',
                'progress-success': apiStatus() === 'SUCCEEDED'
              }
            ">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- ko if: properties.plan && properties.plan().status && properties.plan().status.length > 2 -->
          <li class="nav-header">${ _('Status Text') }</li>
          <li><span data-bind="text: properties.plan().status"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('Open Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
          <!-- /ko -->
        </ul>
      </div>
    </div>

    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <!-- ko if: $root.job().mainType() == 'queries-impala' -->
        <li>
          <a data-bind="
            attr: {
              href: $root.contextId('#queries-page-plan')
            },
            click: function() {
              $root.showTab('#queries-page-plan');
            },
            event: {
              'shown': function () {
                if (!properties.plan || !properties.plan()) {
                  fetchProfile('plan');
                }
              }
            }
          ">${ _('Plan') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-stmt')
              },
              click: function() {
                $root.showTab('#queries-page-stmt');
              }">${ _('Query') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-plan-text')
              },
              click: function() {
                $root.showTab('#queries-page-plan-text');
              }">${ _('Text Plan') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-summary')
              },
              click: function() {
                $root.showTab('#queries-page-summary');
              }">${ _('Summary') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-profile')
              },
              click: function() {
                $root.showTab('#queries-page-profile');
              },
              event: {
                'shown': function () {
                  if (!properties.profile || !properties.profile().profile) {
                    fetchProfile('profile');
                  }
                }
              }">${ _('Profile') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-memory')
              },
              click: function() {
                $root.showTab('#queries-page-memory');
              },
              event: {
                'shown': function () {
                  if (!properties.memory || !properties.memory().mem_usage) {
                    fetchProfile('memory');
                  }
                }
              }">${ _('Memory') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-backends')
              },
              click: function() {
                $root.showTab('#queries-page-backends');
              },
              event: {
                'shown': function () {
                  if (!properties.backends || !properties.backends().backend_states) {
                    fetchProfile('backends');
                  }
                }
              }">${ _('Backends') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-finstances')
              },
              click: function() {
                $root.showTab('#queries-page-finstances');
              },
              event: {
                'shown': function () {
                  if (!properties.finstances || !properties.finstances().backend_instances) {
                    fetchProfile('finstances');
                  }
                }
              }">${ _('Instances') }</a>
        </li>
        <!-- /ko -->
        <!-- ko if: $root.job().mainType() == 'queries-hive' -->
        <li class="active">
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-hive-plan-text')
              },
              click: function() {
                $root.showTab('#queries-page-hive-plan-text');
              }">${ _('Plan') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-hive-stmt')
              },
              click: function() {
                $root.showTab('#queries-page-hive-stmt');
              }">${ _('Query') }</a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#queries-page-hive-perf')
              },
              click: function() {
                $root.showTab('#queries-page-hive-perf');
              }">${ _('Perf') }</a>
        </li>
        <!-- /ko -->
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <!-- ko if: $root.job().mainType() == 'queries-impala' -->
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-plan') }"
             data-profile="plan">
          <div
            data-bind="visible:properties.plan && properties.plan().plan_json && properties.plan().plan_json.plan_nodes.length">
            <div class="query-plan" data-bind="
               attr: { id: $root.contextId('queries-page-plan-graph') },
               impalaDagre: { value: properties.plan && properties.plan(), height: $root.isMini() ? 535 : 600 }
            ">
              <svg style="width:100%;height:100%;position:relative;"
                   data-bind="attr: { id: $root.contextId('queries-page-plan-svg') }">
                <g></g>
              </svg>
            </div>
          </div>
          <pre data-bind="
              visible:!properties.plan || !properties.plan().plan_json || !properties.plan().plan_json.plan_nodes.length
            ">${ _('The selected tab has no data') }</pre>
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-stmt') }"
             data-profile="plan">
          <!-- ko if: properties.plan && properties.plan().stmt -->
          <pre data-bind="
              highlight: {
                value: properties.plan().stmt.trim(),
                enableOverflow: true,
                formatted: true,
                dialect: 'impala'
              }"></pre>
          <!-- /ko -->
          <!-- ko ifnot: properties.plan && properties.plan().stmt -->
          <pre>
                ${ _('The selected tab has no data') }
              </pre>
          <!-- /ko -->
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-plan-text') }"
             data-profile="plan">
          <pre data-bind="text: (properties.plan && properties.plan().plan) || _('The selected tab has no data')"></pre>
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-summary') }"
             data-profile="plan">
            <pre
              data-bind="text: (properties.plan && properties.plan().summary) || _('The selected tab has no data')"></pre>
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-profile') }"
             data-profile="profile">
          <button class="btn" type="button" data-clipboard-target="#query-impala-profile" style="float: right;" data-bind="
            visible: properties.profile && properties.profile().profile,
            clipboard: {
              onSuccess: function() {
                huePubSub.publish('hue.global.info', {
                  message: '${ _("Profile copied to clipboard!") }'
                })
              }
            }">
          <i class="fa fa-fw fa-clipboard"></i> ${ _('Clipboard') }
          </button>
          <button class="btn" type="button" style="float: right;" data-bind="
                click: function(){ submitQueryProfileDownloadForm('download-profile'); },
                visible: properties.profile && properties.profile().profile">
            <i class="fa fa-fw fa-download"></i> ${ _('Download') }
          </button>
          <div id="downloadProgressModal"></div>
          <pre id="query-impala-profile" style="float: left; margin-top: 8px" data-bind="
                text: (properties.profile && properties.profile().profile) || _('The selected tab has no data')"></pre>
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-memory') }"
             data-profile="mem_usage">
            <pre
              data-bind="text: (properties.memory && properties.memory().mem_usage) || _('The selected tab has no data')"></pre>
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-backends') }"
             data-profile="backends">
          <!-- ko if: properties.backends && properties.backends().backend_states -->
          <div data-bind="attr: { id: $root.contextId('queries-page-memory-backends-template') }"
               style="overflow-x: scroll;">
            <table class="table table-condensed">
              <thead>
              <tr>
                <!-- ko foreach: Object.keys(properties.backends().backend_states[0]).sort() -->
                <th data-bind="text: $data"></th>
                <!-- /ko -->
              </tr>
              </thead>
              <tbody data-bind="
                  foreach: {
                    data: $data.properties.backends().backend_states,
                    minHeight: 20,
                    container: $root.contextId('#queries-page-memory-backends-template')
                  }">
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
          <pre data-bind="text: _('The selected tab has no data')"></pre>
          <!-- /ko -->
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-finstances') }"
             data-profile="finstances">
          <!-- ko if: properties.finstances && properties.finstances().backend_instances -->
          <div data-bind="attr: { id: $root.contextId('queries-page-memory-finstances-template') }"
               style="overflow-x: scroll;">
            <table class="table table-condensed">
              <thead>
              <tr>
                <!-- ko foreach: [_('host')].concat(Object.keys($data.properties.finstances().backend_instances[0].instance_stats[0])).sort() -->
                <th data-bind="text: $data"></th>
                <!-- /ko -->
              </tr>
              </thead>
              <tbody data-bind="
                  foreach: {
                    data: $data.properties.finstances().backend_instances.reduce(function(arr, instance) {
                      instance.instance_stats.forEach(function(stats) { stats.host = instance.host; });
                      return arr.concat(instance.instance_stats);
                    }, []),
                    minHeight: 20,
                    container: $root.contextId('#queries-page-memory-finstances-template')
                  }">
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
          <pre data-bind="text: _('The selected tab has no data')"></pre>
          <!-- /ko -->
        </div>
        <!-- /ko -->

        <!-- ko if: $root.job().mainType() == 'queries-hive' -->
        <div class="tab-pane active"
             data-bind="attr: { id: $root.contextId('queries-page-hive-plan-text') }"
             data-profile="plan">
          <!-- ko if: properties.plan && properties.plan().plan -->
          <pre data-bind="text: properties.plan().plan || _('The selected tab has no data')"></pre>
          <!-- /ko -->
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-hive-stmt') }"
             data-profile="stmt">
          <pre data-bind="text: (properties.plan && properties.plan().stmt) || _('The selected tab has no data')"></pre>
        </div>
        <div class="tab-pane" data-bind="attr: { id: $root.contextId('queries-page-hive-perf') }"
             data-profile="perf">
          <hive-query-plan></hive-query-plan>
        </div>
        <!-- /ko -->
      </div>
    </div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="jb-livy-session-page">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="hueLink: doc_url" title="${ _('Open in editor') }">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
                css: {
                  'progress-danger': apiStatus() === 'FAILED',
                  'progress-warning': apiStatus() === 'RUNNING',
                  'progress-success': apiStatus() === 'SUCCEEDED'
                }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{ 'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#livy-session-page-statements')
              },
              click: function() {
                fetchProfile('properties');
                $root.showTab('#livy-session-page-statements');
              }">${ _('Properties') }</a>
        </li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active"
             data-bind="attr: { id: $root.contextId('livy-session-page-statements') }">
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

<script type="text/html" id="jb-celery-beat-page">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="hueLink: doc_url" title="${ _('Open in editor') }">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
                css: {
                  'progress-danger': apiStatus() === 'FAILED',
                  'progress-warning': apiStatus() === 'RUNNING',
                  'progress-success': apiStatus() === 'SUCCEEDED'
                }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css: {'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#celery-beat-page-statements')
              },
              click: function() {
                fetchProfile('properties');
                $root.showTab('#celery-beat-page-statements');
              }">${ _('Properties') }</a>
        </li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: $root.contextId('celery-beat-page-statements') }">
          <table class="datatables table table-condensed">
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

<script type="text/html" id="jb-schedule-hive-page">
  <div class="row-fluid">
    <div data-bind="css: {'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <a data-bind="hueLink: doc_url" title="${ _('Open in editor') }">
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
                css: {
                  'progress-danger': apiStatus() === 'FAILED',
                  'progress-warning': apiStatus() === 'RUNNING',
                  'progress-success': apiStatus() === 'SUCCEEDED'
                }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css: {'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active">
          <a data-bind="attr: { href: $root.contextId('#schedule-hive-page-properties') }"
             data-toggle="tab">
            ${ _('Properties') }
          </a>
        </li>
        <li>
          <a data-bind="
              attr: {
                href: $root.contextId('#schedule-hive-page-queries')
              },
              click: function() {
                fetchProfile('tasks');
                $root.showTab('#schedule-hive-queries');
              }"
             data-toggle="tab">${ _('Queries') }</a>
        </li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active"
             data-bind="attr: { id: $root.contextId('schedule-hive-page-properties') }">
          <pre data-bind="highlight: { value: properties['query'], formatted: true, dialect: 'hive' }"></pre>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('schedule-hive-page-queries') }">
          <!-- ko with: coordinatorActions() -->
          <form class="form-inline">
            <div data-bind="template: { name: 'jb-job-actions' }" class="pull-right"></div>
          </form>

          <table data-bind="attr: { id: $root.contextId('schedulesHiveTable') }" class="datatables table table-condensed status-border-container">
            <thead>
            <tr>
              <th width="1%">
                <div class="select-all hue-checkbox fa"
                     data-bind="hueCheckAll: { allValues: apps, selectedValues: selectedJobs }"></div>
              </th>
              <th>${_('Status')}</th>
              <th>${_('Title')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: apps">
            <tr class="status-border pointer" data-bind="
                  css: {
                    'completed': properties.status() == 'SUCCEEDED',
                    'running': ['RUNNING', 'FAILED', 'KILLED'].indexOf(properties.status()) != -1,
                    'failed': properties.status() == 'FAILED' || properties.status() == 'KILLED'
                  },
                  click: function(data, event) {
                    $root.job().onTableRowClick(event, properties.externalId());
                  }">
              <td data-bind="click: function() {}, clickBubble: false">
                <div class="hue-checkbox fa" data-bind="
                    click: function() {},
                    clickBubble: false,
                    multiCheck: $root.contextId('#schedulesHiveTable'),
                    value: $data,
                    hueChecked: $parent.selectedJobs"></div>
              </td>
              <td><span class="label job-status-label" data-bind="text: properties.status"></span></td>
              <td data-bind="text: properties.title"></td>
            </tr>
            </tbody>
          </table>
          <!-- /ko -->
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-job-actions">
  <div class="btn-group">
    <!-- ko if: $root.job() && $root.job().type() === 'schedule' -->
    <button class="btn" title="${ _('Sync Coordinator') }"
            data-bind="click: function() { $root.job().showSyncCoorModal() }, enable: killEnabled">
      <i class="fa fa-refresh"></i> <!-- ko ifnot: $root.isMini -->${ _('Coordinator') }<!-- /ko -->
    </button>

    <button class="btn" title="${ _('Sync Workflow') }"
            data-bind="click: function(){ control('sync_workflow'); }, enable: killEnabled">
      <i class="fa fa-refresh"></i> <!-- ko ifnot: $root.isMini -->${ _('Workflow') }<!-- /ko -->
    </button>
    <!-- /ko -->
  </div>

  <div class="btn-group">
    <!-- ko if: hasResume -->
    <button class="btn" title="${ _('Resume selected') }"
            data-bind="click: function() { control('resume'); }, enable: resumeEnabled">
      <i class="fa fa-play"></i> <!-- ko ifnot: $root.isMini -->${ _('Resume') }<!-- /ko -->
    </button>
    <!-- /ko -->

    <!-- ko if: hasPause -->
    <button class="btn" title="${ _('Suspend selected') }"
            data-bind="click: function() { control('suspend'); }, enable: pauseEnabled">
      <i class="fa fa-pause"></i> <!-- ko ifnot: $root.isMini -->${ _('Suspend') }<!-- /ko -->
    </button>
    <!-- /ko -->

    <!-- ko if: hasRerun -->
    <button class="btn" title="${ _('Rerun selected') }"
            data-bind="click: function() { control('rerun'); }, enable: rerunEnabled">
      <i class="fa fa-repeat"></i> <!-- ko ifnot: $root.isMini -->${ _('Rerun') }<!-- /ko -->
    </button>
    <!-- /ko -->

    % if not DISABLE_KILLING_JOBS.get():
    <!-- ko if: hasKill -->
    <button class="btn btn-danger disable-feedback" title="${_('Stop selected')}" data-bind="
        click: function() { $($root.contextId('#killModal')).modal('show'); }, enable: killEnabled
      ">
      <i class="fa fa-times"></i> <!-- ko ifnot: $root.isMini -->${_('Kill')}<!-- /ko -->
    </button>
    <!-- /ko -->
    % endif

    <!-- ko if: hasIgnore -->
    <button class="btn btn-danger disable-feedback" title="${_('Ignore selected')}"
            data-bind="click: function() { control('ignore'); }, enable: ignoreEnabled">
      ## TODO confirmation
      <i class="fa fa-eraser"></i> <!-- ko ifnot: $root.isMini -->${_('Ignore')}<!-- /ko -->
    </button>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="jb-workflow-page">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- /ko -->
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <div>
              <a data-bind="hueLink: doc_url, text: name" title="${ _('Open') }"></a>
              <a data-bind="
                  documentContextPopover: { uuid: doc_url().split('=')[1], orientation: 'bottom', offset: { top: 5 } }"
                 href="javascript: void(0);" title="${ _('Preview document') }">
                <i class="fa fa-info"></i>
              </a>
            </div>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <!-- /ko -->
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
                css: {
                  'progress-danger': apiStatus() === 'FAILED',
                  'progress-warning': apiStatus() === 'RUNNING',
                  'progress-success': apiStatus() === 'SUCCEEDED'
                },
                attr: { title: status }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Duration') }</li>
          <li><span data-bind="text: duration() ? duration().toHHMMSS() : ''"></span></li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="moment: {data: submitted, format: 'LLL'}"></span></li>
          <!-- /ko -->
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
        <!-- ko ifnot: $root.isMini() -->
        <li class="active"><a href="#workflow-page-graph" data-toggle="tab">${ _('Graph') }</a></li>
        <!-- /ko -->
        <li><a data-bind="
            attr: {
              href: $root.contextId('#workflow-page-metadata')
            },
            click: function() {
              fetchProfile('properties');
              $root.showTab('#workflow-page-metadata');
            }">${_('Properties') }</a></li>
        <li><a class="jb-logs-link" data-bind="attr: { href: $root.contextId('#workflow-page-logs') }"
               data-toggle="tab">${ _('Logs') }</a></li>
        <li data-bind="css: { 'active': $root.isMini() }"><a
          data-bind="attr: { href: $root.contextId('#workflow-page-tasks') }" data-toggle="tab">${
          _('Tasks') }</a></li>
        <li><a data-bind="
            attr: {
              href: $root.contextId('#workflow-page-xml')
            },
            click: function() {
              fetchProfile('xml');
              $root.showTab('#workflow-page-xml');
            }">${ _('XML') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <!-- ko ifnot: $root.isMini() -->
        <div class="tab-pane active dashboard-container" id="workflow-page-graph"></div>
        <!-- /ko -->

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('workflow-page-logs') }">
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" data-bind="
            attr: { id: $root.contextId('workflow-page-tasks') }, css: { 'active': $root.isMini() }">
          <table class="datatables table table-condensed">
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
              <th>${_('Data')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: properties['actions']">
            <tr>
              <td>
                <a data-bind="hueLink: '/jobbrowser/jobs/#!id=' + ko.unwrap(externalId), clickBubble: false">
                  <i class="fa fa-tasks"></i>
                </a>
              </td>
              <td data-bind="text: status"></td>
              <td data-bind="text: errorMessage"></td>
              <td data-bind="text: errorCode"></td>
              <td data-bind="
                  text: externalId,
                  click: function() {
                    $root.job().id(ko.unwrap(externalId));
                    $root.job().fetchJob();
                  },
                  style: { color: '#0B7FAD' }" class="pointer"></td>
              <td data-bind="
                  text: id,
                  click: function(data, event) {
                    $root.job().onTableRowClick(event, id);
                  },
                  style: { color: '#0B7FAD' }" class="pointer"></td>
              <td data-bind="moment: {data: startTime, format: 'LLL'}"></td>
              <td data-bind="moment: {data: endTime, format: 'LLL'}"></td>
              <td data-bind="text: data"></td>
            </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('workflow-page-metadata') }">
          <div data-bind="
              template: {
                name: 'jb-render-properties',
                data: properties['properties']
              }"></div>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('workflow-page-xml') }">
          <div data-bind="readOnlyAce: properties['xml'], path: 'xml', type: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-workflow-action-page">
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
        <li class="active"><a
          data-bind="attr: { href: $root.contextId('#workflow-action-page-metadata') }"
          data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: $root.contextId('#workflow-action-page-tasks') }"
               data-toggle="tab">${ _('Child jobs') }</a></li>
        <li><a data-bind="attr: { href: $root.contextId('#workflow-action-page-xml') }"
               data-toggle="tab">${ _('XML') }</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active"
             data-bind="attr: { id: $root.contextId('workflow-action-page-metadata') }">
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

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('workflow-action-page-tasks') }">
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

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('workflow-action-page-xml' }">
          <div data-bind="readOnlyAce: properties['conf'], type: 'xml'"></div>
        </div>

      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-schedule-page">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- /ko -->
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <div>
              <a data-bind="hueLink: doc_url, text: name" title="${ _('Open') }"></a>
              <a data-bind="
                  documentContextPopover: {
                    uuid: doc_url().split('=')[1],
                    orientation: 'bottom',
                    offset: { top: 5 }
                  }" href="javascript: void(0);" title="${ _('Preview document') }"><i class="fa fa-info"></i></a>
            </div>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: doc_url -->
          <li class="nav-header">${ _('Name') }</li>
          <li><span data-bind="text: name"></span></li>
          <!-- /ko -->
          <!-- ko ifnot: $root.isMini() -->
          <li class="nav-header">${ _('Type') }</li>
          <li><span data-bind="text: type"></span></li>
          <li class="nav-header">${ _('Status') }</li>
          <li><span data-bind="text: status"></span></li>
          <!-- /ko -->
          <li class="nav-header">${ _('User') }</li>
          <li><span data-bind="text: user"></span></li>
          <li class="nav-header">${ _('Progress') }</li>
          <li><span data-bind="text: progress"></span>%</li>
          <li>
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
                css: {
                  'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                  'progress-success': apiStatus() !== 'FAILED' && progress() === 100,
                  'progress-danger': apiStatus() === 'FAILED'
                },
                attr: { title: status }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <!-- ko ifnot: $root.isMini() -->
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
    <div data-bind="css: {'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a data-bind="attr: { href: $root.contextId('#schedule-page-calendar') }"
                              data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a class="jb-logs-link" data-bind="attr: { href: $root.contextId('#schedule-page-logs') }"
               data-toggle="tab">${ _('Logs') }</a></li>
        <li><a data-bind="
            attr: {
              href: $root.contextId('#schedule-page-metadata')
            },
            click: function() {
              fetchProfile('properties');
              $root.showTab('#schedule-page-metadata');
            }">${ _('Properties') }</a></li>
        <li><a data-bind="
            attr: {
              href: $root.contextId('#schedule-page-xml')
            },
            click: function() {
              fetchProfile('xml');
              $root.showTab('#schedule-page-xml');
            }">${ _('XML') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: $root.contextId('schedule-page-calendar') }">
          <!-- ko with: coordinatorActions() -->
          <form class="form-inline">
            <!-- ko with: $root.job() -->
            <!-- ko if: type() === 'schedule' -->
            <span data-bind="foreach: statesValuesFilter">
                <label class="checkbox">
                  <div class="pull-left margin-left-5 status-border status-content"
                       data-bind="css: value, hueCheckbox: checked"></div>
                  <div class="inline-block" data-bind="text: name, toggle: checked"></div>
                </label>
              </span>
            <!-- /ko -->
            <!-- /ko -->
            <div data-bind="template: { name: 'jb-job-actions' }" class="pull-right"></div>
          </form>

          <table id="schedulesTable" class="datatables table table-condensed status-border-container">
            <thead>
            <tr>
              <th width="1%">
                <div class="select-all hue-checkbox fa"
                     data-bind="hueCheckAll: { allValues: apps, selectedValues: selectedJobs }"></div>
              </th>
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
            <!-- ko if: !$root.job().forceUpdatingJob() -->
            <tbody data-bind="foreach: apps">
            <tr class="status-border pointer" data-bind="
                  css: {
                    'completed': properties.status() == 'SUCCEEDED',
                    'running': ['RUNNING', 'FAILED', 'KILLED'].indexOf(properties.status()) != -1,
                    'failed': properties.status() == 'FAILED' || properties.status() == 'KILLED'
                  },
                  click: function(data, event) {
                    $root.job().onTableRowClick(event, properties.externalId());
                  }">
              <td data-bind="click: function() {}, clickBubble: false">
                <div class="hue-checkbox fa" data-bind="
                    click: function() {},
                    clickBubble: false,
                    multiCheck: '#schedulesTable',
                    value: $data,
                    hueChecked: $parent.selectedJobs"></div>
              </td>
              <td><span class="label job-status-label" data-bind="text: properties.status"></span></td>
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
            <!-- /ko -->
            <!-- ko if: $root.job().forceUpdatingJob() -->
            <tbody>
            <tr>
              <td colspan="11"><!-- ko hueSpinner: { spin: true, inline: true, size: 'large' } --><!-- /ko --></td>
            </tr>
            </tbody>
            <!-- /ko -->
          </table>
          <!-- /ko -->
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('schedule-page-logs') }">
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('schedule-page-metadata') }">
          <div data-bind="
              template: {
                name: 'jb-render-properties',
                data: properties['properties']
              }"></div>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('schedule-page-xml') }">
          <div data-bind="readOnlyAce: properties['xml'], path: 'xml', type: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-bundle-page">
  <div class="row-fluid">
    <div data-bind="css:{'span2': !$root.isMini(), 'span12': $root.isMini() }">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Id') }</li>
          <li class="break-word"><span data-bind="text: id"></span></li>
          <!-- ko if: doc_url -->
          <li class="nav-header">${ _('Document') }</li>
          <li>
            <div>
              <a data-bind="hueLink: doc_url, text: name" title="${ _('Open') }"></a>
              <a data-bind="
                  documentContextPopover: {
                    uuid: doc_url().split('=')[1],
                    orientation: 'bottom',
                    offset: { top: 5 }
                  }" href="javascript: void(0);" title="${ _('Preview document') }"><i class="fa fa-info"></i></a>
            </div>
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
            <div class="progress-job progress" style="background-color: #FFF; width: 100%" data-bind="
                css: {
                  'progress-danger': apiStatus() === 'FAILED',
                  'progress-warning': apiStatus() !== 'FAILED' && progress() < 100,
                  'progress-success': apiStatus() !== 'FAILED' && progress() === 100
                }">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </li>
          <li class="nav-header">${ _('Submitted') }</li>
          <li><span data-bind="text: submitted"></span></li>
        </ul>
      </div>
    </div>
    <div data-bind="css:{'span10': !$root.isMini(), 'span12 no-margin': $root.isMini() }">
      <ul class="nav nav-pills margin-top-20">
        <li class="active"><a data-bind="attr: { href: $root.contextId('#bundle-page-coordinators') }"
                              data-toggle="tab">${ _('Tasks') }</a></li>
        <li><a class="jb-logs-link" data-bind="attr: { href: $root.contextId('#bundle-page-logs') }"
               data-toggle="tab">${ _('Logs') }</a></li>
        <li><a data-bind="
            attr: {
              href: $root.contextId('#bundle-page-metadata')
            },
            click: function() {
              fetchProfile('properties');
              $root.showTab('#bundle-page-metadata');
            }">${ _('Properties') }</a></li>
        <li><a data-bind="
            attr: {
              href:$root.contextId('#bundle-page-xml')
            },
            click: function() {
              fetchProfile('xml');
              $root.showTab('#bundle-page-xml');
            }">${ _('XML') }</a></li>
        <li class="pull-right" data-bind="template: { name: 'jb-job-actions' }"></li>
      </ul>

      <div class="clearfix"></div>

      <div class="tab-content">
        <div class="tab-pane active"
             data-bind="attr: { id: $root.contextId('bundle-page-coordinators') }">
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
            <tr class="status-border pointer" data-bind="
                css: {
                  'completed': ko.unwrap(status) == 'SUCCEEDED',
                  'running': ['SUCCEEDED', 'FAILED', 'KILLED'].indexOf(ko.unwrap(status)) != -1,
                  'failed': ko.unwrap(status) == 'FAILED' || ko.unwrap(status) == 'KILLED'
                },
                click: function() {
                  if (ko.unwrap(id)) {
                    $root.job().id(ko.unwrap(id));
                    $root.job().fetchJob();
                  }
                }">
              <td><span class="label job-status-label" data-bind="text: status"></span></td>
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

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('bundle-page-logs') }">
          <pre data-bind="html: logs, logScroller: logs"></pre>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('bundle-page-metadata') }">
          <div data-bind="
              template: {
                name: 'jb-render-properties',
                data: properties['properties']
              }"></div>
        </div>

        <div class="tab-pane" data-bind="attr: { id: $root.contextId('bundle-page-xml') }">
          <div data-bind="readOnlyAce: properties['xml'], path: 'xml', type: 'xml'"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="jb-render-properties">
  <!-- ko hueSpinner: { spin: !$data.properties, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko if: $data.properties -->
  <!-- ko ifnot: $root.isMini() -->
  <form class="form-search">
    <input type="text" data-bind="clearable: $parent.propertiesFilter, valueUpdate: 'afterkeydown'"
           class="input-xlarge search-query" placeholder="${_('Text Filter')}">
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
        <!-- ko template: { name: 'jb-link-or-text', data: { name: $data, value: $parent.properties[$data] } } -->
        <!-- /ko -->
      </td>
    </tr>
    </tbody>
  </table>
  <!-- /ko -->
</script>

<script type="text/html" id="jb-render-page-counters">
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

<script type="text/html" id="jb-render-task-counters">
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

<script type="text/html" id="jb-render-attempt-counters">
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

<script type="text/html" id="jb-render-metadata">
  <!-- ko hueSpinner: { spin: !$data.property, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko if: $data.property -->
  <form class="form-search">
    <input type="text" data-bind="clearable: $parent.metadataFilter, valueUpdate: 'afterkeydown'"
           class="input-xlarge search-query" placeholder="${_('Text Filter')}">
  </form>
  <div data-bind="
      attr: {
        id: $root.contextId('job-mapreduce-page-metadata-template')
      },
      style: {
        'height': !$root.isMini() ? 'calc(100vh - 350px)' : '400px'
      }" style="overflow-y: hidden;">
    <table id="jobbrowserJobMetadataTable" class="table table-condensed">
      <thead>
      <tr>
        <th>${ _('Name') }</th>
        <th width="50%">${ _('Value') }</th>
      </tr>
      </thead>
      <tbody data-bind="
          foreachVisible: {
            data: property,
            minHeight: 20,
            container: $root.contextId('#job-mapreduce-page-metadata-template')
          }">
      <tr>
        <td data-bind="text: name"></td>
        <td>
          <!-- ko template: { name: 'jb-link-or-text', data: { name: name, value: value } } --><!-- /ko -->
        </td>
      </tr>
      </tbody>
    </table>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="jb-link-or-text">
  <!-- ko if: typeof $data.value === 'string' -->
  <!-- ko if: $data.name.indexOf('logs') > -1 || $data.name.indexOf('trackingUrl') > -1 -->
  <a href="javascript:void(0);" data-bind="text: $data.value, attr: { href: $data.value }" target="_blank"></a>
  <!-- /ko -->
  <!-- ko if: ($data.name.indexOf('dir') > -1 || $data.name.indexOf('path') > -1 || $data.name.indexOf('output') > -1 || $data.name.indexOf('input') > -1) && ($data.value.startsWith('/') || $data.value.startsWith('hdfs://') || $data.value.startsWith('s3a://')) -->
  <a href="javascript:void(0);"
     data-bind="hueLink: '/filebrowser/view=' + $root.getHDFSPath($data.value), text: $data.value"></a>
  <a href="javascript: void(0);"
     data-bind="storageContextPopover: { path: $root.getHDFSPath($data.value), orientation: 'left', offset: { top: 5 } }"><i
    class="fa fa-info"></i></a>
  <!-- /ko -->
  <!-- ko ifnot: $data.name.indexOf('logs') > -1 || $data.name.indexOf('trackingUrl') > -1 || (($data.name.indexOf('dir') > -1 || $data.name.indexOf('path') > -1 || $data.name.indexOf('output') > -1 || $data.name.indexOf('input') > -1) && ($data.value.startsWith('/') || $data.value.startsWith('hdfs://') || $data.value.startsWith('s3a://'))) -->
  <span data-bind="text: $data.value"></span>
  <!-- /ko -->
  <!-- /ko -->
  <!-- ko ifnot: typeof $data.value === 'string' -->
  <span data-bind="text: $data.value"></span>
  <!-- /ko -->
</script>
</%def>
