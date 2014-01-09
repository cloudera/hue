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
  from desktop.lib.django_util import extract_field_data
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Query'), app_name, user) | n,unicode }
${layout.menubar(section='query')}

<div id="query-editor" class="container-fluid hide section">
<div class="row-fluid">
<div class="span2">
  <form id="advancedSettingsForm" action="${action}" method="POST" class="form form-horizontal">
    <div class="sidebar-nav">
      <ul class="nav nav-list">
        <li class="nav-header">${_('database')}</li>
        <li class="white" style="padding-top:0px">
          <select data-bind="options: databases, value: database" class="input-medium chosen-select" name="query-database" data-placeholder="${_('Choose a database...')}"></select>
        </li>
        <li class="nav-header">${_('settings')}</li>
        <li class="white paramContainer">
          <!-- ko foreach: query.settings -->
          <div class="param">
            <div class="remove">
              <button data-bind="click: $root.removeSetting.bind(this, $index())" type="button" class="btn btn-mini settingsDelete" title="${_('Delete this setting')}">x
              </button>
            </div>
            <div class="control-group">
              <label>${_('Key')}</label>
              <input data-bind="value: key" type="text" class="settingsField span8" autocomplete="off" placeholder="mapred.reduce.tasks"/>
            </div>

            <div class="control-group">
              <label>${_('Value')}</label>
              <input data-bind="value: value" type="text" class="settingValuesField span8" placeholder="1"/>
            </div>
          </div>
          <!-- /ko -->

          <div class="control-group">
            <a data-bind="click: function() { $root.addSetting('','') }" class="btn btn-mini paramAdd">${_('Add')}</a>
          </div>
        </li>
        <li class="nav-header
          % if app_name == 'impala':
             hide
          % endif
          ">
          ${_('File Resources')}
        </li>
        <li class="white paramContainer
          % if app_name == 'impala':
             hide
          % endif
          ">
          <!-- ko foreach: query.fileResources -->
          <div class="param">
            <div class="remove">
              <button data-bind="click: $root.removeFileResources.bind(this, $index())" type="button" class="btn btn-mini" title="${_('Delete this setting')}">&times;</button>
            </div>
            <div class="control-group">
              <label>${_('Type')}</label>
              <select data-bind="value: type" class="input-small">
                <option value="JAR">${_('jar')}</option>
                <option value="ARCHIVE">${_('archive')}</option>
                <option value="FILE">${_('file')}</option>
              </select>
            </div>

            <div class="control-group">
              <label>${_('Path')}</label>
              <input data-bind="value: path" type="text" class="filesField span7 pathChooser" placeholder="/user/foo/udf.jar"/>
            </div>
          </div>
          <!-- /ko -->

          <div class="control-group">
            <a data-bind="click: function() { $root.addFileResources('','') }" class="btn btn-mini paramAdd">${_('Add')}</a>
          </div>
        </li>
        <li title="${ _('User-Defined Functions') }" class="nav-header
          % if app_name == 'impala':
            hide
          % endif
          ">
          ${_('UDFs')}
        </li>
        <li class="white paramContainer
          % if app_name == 'impala':
            hide
          % endif
          ">
          <!-- ko foreach: query.functions -->
          <div class="param">
            <div class="remove">
              <button data-bind="click: $root.removeFunction.bind(this, $index())" type="button" class="btn btn-mini settingsDelete" title="${_('Delete this setting')}">&times;</button>
            </div>
            <div class="control-group">
              <label>${_('Name')}</label>
              <input data-bind="value: name" type="text" class="functionsField span8" autocomplete="off" placeholder="myFunction"/>
            </div>

            <div class="control-group">
              <label>${_('Class name')}</label>
              <input data-bind="value: class_name" type="text" class="classNamesField span8" placeholder="com.acme.example"/>
            </div>
          </div>
          <!-- /ko -->

          <div class="control-group">
            <a data-bind="click: function() { $root.addFunction('','') }" class="btn btn-mini paramAdd">${_('Add')}</a>
          </div>
        </li>
        <li class="nav-header">${_('Options')}</li>
        <li class="white" style="padding-top:0px">
          <label class="checkbox" rel="tooltip" data-original-title="${_("If checked (the default), you can include parameters like $parameter_name in your query, and users will be prompted for a value when the query is run.")}">
            <input data-bind="checked: query.isParameterized" type="checkbox"/>
            ${_("Enable parameterization")}
          </label>
          <label class="checkbox
          % if app_name == 'impala':
            hide
          % endif
          " rel="tooltip" data-original-title="${_("If checked, you will receive an email notification when the query completes.")}">
            <input data-bind="checked: query.email" type="checkbox"/>
            ${_("Email me on completion")}
          </label>
        </li>
        % if app_name == 'impala':
          <li class="nav-header">
            ${_('Metastore Catalog')}
          </li>
          <li class="white">
            <div class="control-group">
              <span id="refresh-dyk">
                <i class="fa fa-refresh"></i>
                ${ _('Sync tables tips') }
              </span>

              <div id="refresh-content" class="hide">
                <ul style="text-align: left;">
                  <li>"invalidate
                    metadata" ${ _("invalidates the entire catalog metadata. All table metadata will be reloaded on the next access.") }</li>
                  <li>"invalidate metadata
                    &lt;table&gt;" ${ _("invalidates the metadata, load on the next access") }</li>
                  <li>"refresh
                    &lt;table&gt;" ${ _("refreshes the metadata immediately. It is a faster, incremental refresh.") }</li>
                </ul>
              </div>
            </div>
          </li>
        % endif
        <li class="nav-header"></li>
        <li class="white">
          <div class="control-group">
            <i class="fa fa-question-circle" id="help"></i>

            <div id="help-content" class="hide">
              <ul style="text-align: left;">
                <li>${ _('Press CTRL + Space to autocomplete') }</li>
                <li>${ _("You can execute queries with multiple SQL statements delimited by a semicolon ';'") }</li>
                <li>${ _('You can highlight and run a fragment of a query') }</li>
              </ul>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </form>
</div>

<div id="querySide" class="span8">
  <div class="card card-small">
    <div style="margin-bottom: 30px">
        % if can_edit_name:
        <h1 class="card-heading simple">
          <a href="javascript:void(0);"
             id="query-name"
             data-type="text"
             data-name="name"
             data-value="${design.name}"
             data-original-title="${ _('Query name') }"
             data-placement="right">
          </a>
          <a href="javascript:void(0);"
             id="query-description"
             data-type="textarea"
             data-name="description"
             data-value="${design.desc}"
             data-original-title="${ _('Query description') }"
             data-placement="right" style="font-size: 14px; margin-left: 10px">
          </a>
        </h1>
        %endif
    </div>
    <div class="card-body">
      <div class="tab-content">
        <div id="queryPane">

          <div data-bind="css: {'hide': query.errors().length == 0}" class="hide alert alert-error">
            <p><strong>${_('Your query has the following error(s):')}</strong></p>

            <div data-bind="foreach: query.errors">
              <p data-bind="text: $data" class="queryErrorMessage"></p>
            </div>
          </div>

          <div data-bind="css: {'hide': query.watch.errors().length == 0}" class="alert alert-error">
            <p><strong>${_('Your query has the following error(s):')}</strong></p>

            <div data-bind="foreach: query.watch.errors">
              <p data-bind="text: $data" class="queryErrorMessage"></p>
            </div>
          </div>

          <textarea class="hide" tabindex="1" name="query" id="queryField"></textarea>

          <div class="actions">
            % if app_name == 'impala':
            <button data-bind="click: tryExecuteQuery, visible: !$root.query.isRunning() && $root.query.isFinished()" type="button" id="executeQuery" class="btn btn-primary disable-feedback" tabindex="2">${_('Execute')}</button>
            <button data-bind="click: tryCancelQuery, visible: $root.query.isRunning()" class="btn btn-danger" data-loading-text="${ _('Canceling...') }" rel="tooltip" data-original-title="${ _('Cancel the query') }">${ _('Cancel') }</button>
            % else:
            <button data-bind="click: tryExecuteQuery, enable: !$root.query.isRunning(), visible: $root.query.isFinished()" type="button" id="executeQuery" class="btn btn-primary disable-feedback" tabindex="2">${_('Execute')}</button>
            % endif
            <button data-bind="click: executeNextStatement, visible: !$root.query.isFinished()" type="button" class="btn btn-primary disable-feedback" tabindex="2">${_('Next')}</button>

            <button data-bind="click: trySaveQuery, css: {'hide': !$root.query.id() || $root.query.id() == -1}" type="button" class="btn hide">${_('Save')}</button>
            <button data-bind="click: saveAsModal" type="button" class="btn">${_('Save as...')}</button>
            <button data-bind="click: tryExplainQuery" type="button" id="explainQuery" class="btn">${_('Explain')}</button>
            &nbsp; ${_('or create a')} &nbsp;
            <button data-bind="click: createNewQuery" type="button" class="btn">${_('New query')}</button>
            <br/><br/>
          </div>

        </div>
      </div>
    </div>
  </div>

  <div class="card card-small scrollable resultsContainer">
    <a id="expandResults" href="javascript:void(0)" title="${_('See results in full screen')}" rel="tooltip"
      class="view-query-results hide pull-right"><h4 style="margin-right: 20px"><i class="fa fa-expand"></i></h4></a>

    <a id="save-results" data-bind="click: saveResultsModal" href="javascript:void(0)" title="${_('Save the results to HDFS or a new Hive table')}" rel="tooltip"
      class="view-query-results hide pull-right"><h4 style="margin-right: 20px"><i class="fa fa-save"></i></h4></a>

    <a id="download-csv" data-bind="attr: {'href': '/beeswax/download/' + $root.query.id() + '/csv'}" href="javascript:void(0)" title="${_('Download the results in CSV format')}" rel="tooltip"
      class="view-query-results hide pull-right"><h4 style="margin-right: 20px"><i class="fa fa-arrow-circle-o-down"></i></h4></a>

    <a id="download-excel" data-bind="attr: {'href': '/beeswax/download/' + $root.query.id() + '/xls'}" href="javascript:void(0)" title="${_('Download the results for excel')}" rel="tooltip"
      class="view-query-results hide pull-right"><h4 style="margin-right: 20px"><i class="fa fa-arrow-circle-o-down"></i></h4></a>

    <div class="card-body">
      <ul class="nav nav-tabs">
        <li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
        <!-- ko if: !query.explain() -->
        <li><a href="#log" data-toggle="tab">${_('Log')}</a></li>
        <!-- /ko -->
        <!-- ko if: !query.explain() && !query.isRunning() -->
        <li><a href="#columns" data-toggle="tab">${_('Columns')}</a></li>
        <li><a href="#results" data-toggle="tab">${_('Results')}</a></li>
        <li><a href="#chart" data-toggle="tab">${_('Chart')}</a></li>
        <!-- /ko -->
        <!-- ko if: query.explain() && !query.isRunning() -->
        <li><a href="#explanation" data-toggle="tab">${_('Explanation')}</a></li>
        <!-- /ko -->
      </ul>

      <div class="tab-content">
        <div class="tab-pane" id="query">
          <pre data-bind="text: viewModel.query.statement()"></pre>
        </div>
        <!-- ko if: query.explain() -->
        <div class="tab-pane" id="explanation">
          <pre data-bind="text: $root.query.results.explanation()"></pre>
        </div>
        <!-- /ko -->
        <!-- ko if: !query.explain() -->
        <div class="active tab-pane" id="log">
          <pre data-bind="text: $root.query.watch.logs().join('\n')"></pre>
        </div>
        <div class="tab-pane" id="columns">
          <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
            <thead>
              <tr><th>${_('Name')}</th></tr>
            </thead>
            <tbody data-bind="foreach: $root.query.results.columns">
              <tr>
                <td><a href="javascript:void(0)" class="column-selector" data-bind="text: $data.name"></a></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="tab-pane" id="results">

          <div data-bind="css: {'hide': $root.query.results.rows().length == 0}" class="hide">
            <table class="table table-striped table-condensed resultTable" cellpadding="0" cellspacing="0" data-tablescroller-enforce-height="true">
              <thead>
              <tr data-bind="foreach: $root.query.results.columns">
                <th data-bind="text: $data.name, css: { 'sort-numeric': $.inArray($data.type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE']) > -1, 'sort-date': $.inArray($data.type, ['TIMESTAMP_TYPE', 'DATE_TYPE']) > -1, 'sort-string': $.inArray($data.type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE', 'TIMESTAMP_TYPE', 'DATE_TYPE']) == -1 }"></th>
              </tr>
              </thead>
            </table>
          </div>

          <div data-bind="css: {'hide': !$root.query.results.empty()}" class="hide">
            <div class="card card-small scrollable">
              <div class="row-fluid">
                <div class="span10 offset1 center empty-wrapper">
                  <i class="fa fa-frown-o"></i>
                  <h1>${_('The server returned no results.')}</h1>
                  <br/>
                </div>
              </div>
            </div>
          </div>
        </div>

         <div class="tab-pane" id="chart">
          <div style="text-align: center">
          <form class="form-inline">
            ${_('Chart type')}&nbsp;
            <div class="btn-group" data-toggle="buttons-radio">
              <a rel="tooltip" data-placement="top" title="${_('Bars')}" id="blueprintBars" href="javascript:void(0)" class="btn"><i class="fa fa-bar-chart-o"></i></a>
              <a rel="tooltip" data-placement="top" title="${_('Lines')}" id="blueprintLines" href="javascript:void(0)" class="btn"><i class="fa fa-signal"></i></a>
              <a rel="tooltip" data-placement="top" title="${_('Map')}" id="blueprintMap" href="javascript:void(0)" class="btn"><i class="fa fa-map-marker"></i></a>
            </div>&nbsp;&nbsp;
            <span id="blueprintAxis" class="hide">
              <label>${_('X-Axis')}
                <select id="blueprintX" class="blueprintSelect"></select>
              </label>&nbsp;&nbsp;
              <label>${_('Y-Axis')}
              <select id="blueprintY" class="blueprintSelect"></select>
              </label>&nbsp;&nbsp;
              <a rel="tooltip" data-placement="top" title="${_('Download image')}" id="blueprintDownload" href="javascript:void(0)" class="btn hide"><i class="fa fa-download"></i></a>
            </span>
            <span id="blueprintLatLng" class="hide">
              <label>${_('Latitude')}
                <select id="blueprintLat" class="blueprintSelect"></select>
              </label>&nbsp;&nbsp;
              <label>${_('Longitude')}
              <select id="blueprintLng" class="blueprintSelect"></select>
              </label>&nbsp;&nbsp;
              <label>${_('Label')}
              <select id="blueprintDesc" class="blueprintSelect"></select>
              </label>
            </span>
          </form>
          </div>
          <div id="blueprint" class="empty">${_("Please select a chart type.")}</div>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </div>
</div>

<div class="span2" id="navigator">
  <div class="card card-small">
    <a href="#" title="${_('Double click on a table name or field to insert it in the editor')}" rel="tooltip" data-placement="left" class="pull-right" style="margin:10px;margin-left: 0"><i class="fa fa-question-circle"></i></a>
    <a id="refreshNavigator" href="#" title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="left" class="pull-right" style="margin:10px"><i class="fa fa-refresh"></i></a>

    <h1 class="card-heading simple"><i class="fa fa-compass"></i> ${_('Navigator')}</h1>

    <div class="card-body">
      <p>
        <input id="navigatorSearch" type="text" placeholder="${ _('Table name...') }" style="width:90%"/>
        <span id="navigatorNoTables">${_('The selected database has no tables.')}</span>
        <ul id="navigatorTables" class="unstyled"></ul>
        <div id="navigatorLoader">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #DDD"></i><!--<![endif]-->
          <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
        </div>
      </p>
    </div>
  </div>
</div>
</div>
</div>


<div id="execute-parameter-selection" class="container-fluid hide section">
  <div class="row-fluid">
    <div class="card card-small">
      <h1 class="card-heading simple">${_('Please specify parameters for this query')}</h1>
      <div class="card-body">
        <p>
        <form method="POST" action="" class="form-horizontal">
          <fieldset>
            <!-- ko foreach: $root.query.parameters -->
            <div class="control-group">
              <label data-bind="text: name" class="control-label"></label>
              <div class="controls">
                <input data-bind="value: value, valueUpdate:'afterkeydown'" type="text"/>
              </div>
            </div>
            <!-- /ko -->
            <div class="form-actions" style="padding-left: 10px">
              <a class="btn" href="javascript:history.go(-1);">${_('Cancel')}</a>
              <button data-bind="enable: $root.hasParametersFilled, click: tryExecuteParameterizedQuery" type="button" class="btn btn-primary">${_('Execute query')}</button>
            </div>
          </fieldset>
        </form>
        </p>
      </div>
    </div>
  </div>
</div>


<div id="explain-parameter-selection" class="container-fluid hide section">
  <div class="row-fluid">
    <div class="card card-small">
      <h1 class="card-heading simple">${_('Please specify parameters for this query')}</h1>

      <div class="card-body">
        <p>

        <form method="POST" action="" class="form-horizontal">
          <fieldset>
            <!-- ko foreach: $root.query.parameters -->
            <div class="control-group">
              <label data-bind="text: name" class="control-label"></label>

              <div class="controls">
                <input data-bind="value: value, valueUpdate:'afterkeydown'" type="text"/>
              </div>
            </div>
            <!-- /ko -->
            <div class="form-actions" style="padding-left: 10px">
              <a class="btn" href="javascript:history.go(-1);">${_('Cancel')}</a>
              <button data-bind="enable: $root.hasParametersFilled, click: tryExplainParameterizedQuery" type="button" class="btn btn-primary">${_('Explain query')}</button>
            </div>
          </fieldset>
        </form>
        </p>
      </div>
    </div>
  </div>
</div>


<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>

    <h3>${_('Choose a file')}</h3>
  </div>
  <div class="modal-body">
    <div id="filechooser">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>


<div id="saveAs" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>

    <h3>${_('Choose a name')}</h3>
  </div>
  <form class="form-horizontal">
    <div class="control-group" id="saveas-query-name">
      <label class="control-label">${_('Name')}</label>

      <div class="controls">
        <input data-bind="value: $root.query.name" type="text" class="input-xlarge">
      </div>
    </div>
    <div class="control-group">
      <label class="control-label">${_('Description')}</label>

      <div class="controls">
        <input data-bind="value: $root.query.description" type="text" class="input-xlarge">
      </div>
    </div>
  </form>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <button data-bind="click: trySaveAsQuery" class="btn btn-primary">${_('Save')}</button>
  </div>
</div>


<div id="saveResultsModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Save Query Results')}</h3>
  </div>
  <div class="modal-body">
    <!-- ko if: $root.query.results.save.saveTargetError() -->
      <h4 data-bind="text: $root.query.results.save.saveTargetError()"></h4>
    <!-- /ko -->
    <!-- ko if: $root.query.results.save.targetTableError() -->
      <h4 data-bind="text: $root.query.results.save.targetTableError()"></h4>
    <!-- /ko -->
    <!-- ko if: $root.query.results.save.targetDirectoryError() -->
      <h4 data-bind="text: $root.query.results.save.targetDirectoryError()"></h4>
    <!-- /ko -->
    <form id="saveResultsForm" method="POST" class="form form-inline">
      <fieldset>
        <div data-bind="css: {'error': $root.query.results.save.targetTableError()}" class="control-group">
          <div class="controls">
            <label class="radio">
              <input data-bind="checked: $root.query.results.save.type" type="radio" name="save-results-type" value="hive-table">
              &nbsp;${ _('In a new table') }
            </label>
            <span data-bind="visible: $root.query.results.save.type() == 'hive-table'">
              <input data-bind="value: $root.query.results.save.path" type="text" name="target_table" placeholder="${_('Table name')}">
            </span>
          </div>
        </div>
        <div data-bind="css: {'error': $root.query.results.save.targetDirectoryError()}" class="control-group">
          <div class="controls">
            <label class="radio">
              <input data-bind="checked: $root.query.results.save.type" type="radio" name="save-results-type" value="hdfs">
              &nbsp;${ _('In an HDFS directory') }
            </label>
            <span data-bind="visible: $root.query.results.save.type() == 'hdfs'">
              <input data-bind="value: $root.query.results.save.path" type="text" name="target_dir" placeholder="${_('Results location')}" class="pathChooser">
            </span>
          </div>
        </div>
      </fieldset>
    </form>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <button data-bind="click: trySaveResults" class="btn btn-primary">${_('Save')}</button>
  </div>
</div>

<div id="navigatorQuicklook" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <a class="tableLink pull-right" href="#" target="_blank" style="margin-right: 20px;margin-top:6px"><i
        class="fa fa-external-link"></i> ${ _('View in Metastore Browser') }</a>

    <h3>${_('Data sample for')} <span class="tableName"></span></h3>
  </div>
  <div class="modal-body" style="min-height: 100px">
    <div class="loader">
      <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
      <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
    </div>
    <div class="sample"></div>
  </div>
  <div class="modal-footer">
    <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Ok')}</button>
  </div>
</div>

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/beeswax/static/js/beeswax.vm.js"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/js/codemirror-hql.js"></script>
% if app_name == 'impala':
  <script src="/static/js/codemirror-isql-hint.js"></script>
% else:
  <script src="/static/js/codemirror-hql-hint.js"></script>
% endif
<script src="/static/js/codemirror-show-hint.js"></script>

<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
<script src="/static/ext/js/bootstrap-editable.min.js"></script>

<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.categories.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js" type="text/javascript" charset="utf-8"></script>


<style type="text/css">
  h1 {
    margin-bottom: 5px;
  }

  #filechooser {
    min-height: 100px;
    overflow-y: auto;
  }

  .control-group {
    margin-bottom: 3px !important;
  }

  .control-group label {
    float: left;
    padding-top: 5px;
    text-align: left;
    width: 40px;
  }

  .control-group label.radio {
    float: none;
    width: auto;
  }

  .sidebar-nav {
    margin-bottom: 90px !important;
  }

  .paramContainer {
    padding-top: 3px!important;
    padding-left: 0px!important;
    padding-right: 0px!important;
  }

  .param {
    margin-bottom: 5px;
    padding:4px;
    padding-left:8px;
    border-bottom: 1px solid #F6F6F6;
  }

  .param:nth-child(even) {
    background-color: #F0F0F0;
  }

  .paramAdd {
    margin-left: 18px;
  }

  .remove {
    float: right;
  }

  .fileChooserBtn {
    border-radius: 0 3px 3px 0;
  }

  .CodeMirror {
    border: 1px solid #eee;
    margin-bottom: 20px;
  }

  .editorError {
    color: #B94A48;
    background-color: #F2DEDE;
    padding: 4px;
    font-size: 11px;
  }

  .editorError {
    color: #B94A48;
    background-color: #F2DEDE;
    padding: 4px;
    font-size: 11px;
  }

  .editable-empty, .editable-empty:hover {
    color: #666;
    font-style: normal;
  }

  #navigatorTables li {
    width: 95%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #navigatorSearch, #navigatorNoTables {
    display: none;
  }

  .tooltip.left {
    margin-left: -13px;
  }

  .fullscreen {
    position: absolute;
    top: 70px;
    left: 0;
    width: 100%;
    background-color: #FFFFFF;
    z-index: 32000;
  }

  .map {
    height: 200px;
  }

  .resultTable td, .resultTable th {
    white-space: nowrap;
  }

  .tab-content {
    min-height: 100px;
  }

</style>

<link href="/static/ext/css/leaflet.css" rel="stylesheet">

<script src="/static/ext/js/jquery/plugins/jquery-fieldselection.js" type="text/javascript"></script>
<script src="/beeswax/static/js/autocomplete.utils.js" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
var codeMirror, renderNavigator, resetNavigator, dataTable;

var HIVE_AUTOCOMPLETE_BASE_URL = "${ autocomplete_base_url | n,unicode }";
var HIVE_AUTOCOMPLETE_FAILS_SILENTLY_ON = [500]; // error codes from beeswax/views.py - autocomplete

var HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK = function (data) {
  if (data != null && data.error) {
    resetNavigator();
  }
};


// Navigator.
$(document).ready(function () {

  $("#navigatorQuicklook").modal({
    show: false
  });

  var navigatorSearchTimeout = -1;
  $("#navigatorSearch").on("keyup", function () {
    window.clearTimeout(navigatorSearchTimeout);
    navigatorSearchTimeout = window.setTimeout(function () {
      $("#navigatorTables li").removeClass("hide");
      $("#navigatorTables li").each(function () {
        if ($(this).text().toLowerCase().indexOf($("#navigatorSearch").val().toLowerCase()) == -1) {
          $(this).addClass("hide");
        }
      });
    }, 300);
  });

  resetNavigator = function () {
    var _db = viewModel.database();
    if (_db != null) {
      $.totalStorage('tables_' + _db, null);
      $.totalStorage('timestamp_tables_' + _db, null);
      renderNavigator();
    }
  }

  renderNavigator = function () {
    $("#navigatorTables").empty();
    $("#navigatorLoader").show();
    hac_getTables(viewModel.database(), function (data) {  //preload tables for the default db
      $(data.split(" ")).each(function (cnt, table) {
        if ($.trim(table) != "") {
          var _table = $("<li>");
          _table.html("<a href='#' class='pull-right'><i class='fa fa-list' title='" + "${ _('Preview Sample data') }" + "' style='margin-left:5px'></i></a><a href='/metastore/table/" + viewModel.database() + "/" + table + "' target='_blank' class='pull-right hide'><i class='fa fa-eye' title='" + "${ _('View in Metastore Browser') }" + "'></i></a><a href='#' title='" + table + "'><i class='fa fa-table'></i> " + table + "</a><ul class='unstyled'></ul>");
          _table.data("table", table).attr("id", "navigatorTables_" + table);
          _table.find("a:eq(2)").on("click", function () {
            _table.find(".fa-table").removeClass("fa-table").addClass("fa-spin").addClass("fa-spinner");
            hac_getTableColumns(viewModel.database(), table, "", function (plain_columns, extended_columns) {
              _table.find("a:eq(1)").removeClass("hide");
              _table.find("ul").empty();
              _table.find(".fa-spinner").removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-table");
              $(extended_columns).each(function (iCnt, col) {
                var _column = $("<li>");
                _column.html("<a href='#' style='padding-left:10px'" + (col.comment != null && col.comment != "" ? " title='" + col.comment + "'" : "") + "><i class='fa fa-columns'></i> " + col.name + " (" + col.type + ")</a>");
                _column.appendTo(_table.find("ul"));
                _column.on("dblclick", function () {
                  codeMirror.replaceSelection($.trim(col.name) + ', ');
                  codeMirror.setSelection(codeMirror.getCursor());
                  codeMirror.focus();
                });
              });
            });
          });
          _table.find("a:eq(2)").on("dblclick", function () {
            codeMirror.replaceSelection($.trim(table) + ' ');
            codeMirror.setSelection(codeMirror.getCursor());
            codeMirror.focus();
          });
          _table.find("a:eq(0)").on("click", function () {
            $("#navigatorQuicklook").find(".tableName").text(table);
            $("#navigatorQuicklook").find(".tableLink").attr("href", "/metastore/table/" + viewModel.database() + "/" + _table.data("table"));
            $("#navigatorQuicklook").find(".sample").empty("");
            $("#navigatorQuicklook").attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");
            $.ajax({
              url: "/metastore/table/" + viewModel.database() + "/" + _table.data("table"),
              data: {"sample": true},
              beforeSend: function (xhr) {
                xhr.setRequestHeader("X-Requested-With", "Hue");
              },
              dataType: "html",
              success: function (data) {
                $("#navigatorQuicklook").find(".loader").hide();
                $("#navigatorQuicklook").find(".sample").html(data);
              },
              error: function (e) {
                if (e.status == 500) {
                  resetNavigator();
                  $(document).trigger("error", "${ _('There was a problem loading the table preview.') }");
                  $("#navigatorQuicklook").modal("hide");
                }
              }
            });
            $("#navigatorQuicklook").modal("show");
          });
          _table.appendTo($("#navigatorTables"));
        }
      });
      $("#navigatorLoader").hide();
      if ($("#navigatorTables li").length > 0) {
        $("#navigatorSearch").show();
        $("#navigatorNoTables").hide();
      }
      else {
        $("#navigatorSearch").hide();
        $("#navigatorNoTables").show();
      }
    });
  }

  $("#expandResults").on("click", function(){
    if ($(this).find("i").hasClass("fa-expand")){
      $(this).find("i").removeClass("fa-expand").addClass("fa-compress");
      $(this).parent().addClass("fullscreen");
    }
    else {
      $(this).find("i").addClass("fa-expand").removeClass("fa-compress");
      $(this).parent().removeClass("fullscreen");
    }
    reinitializeTable();
  });

  renderNavigator();

  $("#refreshNavigator").on("click", function () {
    resetNavigator();
  });

  $("#navigator .card").css("min-height", ($(window).height() - 130) + "px");
  $("#navigatorTables").css("max-height", ($(window).height() - 260) + "px").css("overflow-y", "auto");

  viewModel.databases.subscribe(function () {
    if ($.totalStorage("${app_name}_last_database") != null && $.inArray($.totalStorage("${app_name}_last_database"), viewModel.databases())) {
      viewModel.database($.totalStorage("${app_name}_last_database"));
    }
  });

  viewModel.database.subscribe(function (value) {
    $(".chosen-select").trigger("chosen:updated");
    renderNavigator();
  });

  $(".chosen-select").chosen({
    disable_search_threshold: 5,
    width: "100%",
    no_results_text: "${_('Oops, no database found!')}"
  });

  $(".chosen-select").chosen().change(function () {
    $.totalStorage("${app_name}_last_database", viewModel.database());
  });

  $(document).on("click", ".column-selector", function () {
    var _t = $(".resultTable");
    var _col = _t.find("th:econtains(" + $(this).text() + ")");
    _t.find(".columnSelected").removeClass("columnSelected");
    _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
    $("a[href='#results']").click();
  });

  $("a[data-toggle='tab']").on("shown", function (e) {
    if ($(e.target).attr("href") == "#log") {
      logsAtEnd = true;
      window.setTimeout(resizeLogs, 150);
    }
    if ($(e.target).attr("href") == "#results" && $(e.relatedTarget).attr("href") == "#columns") {
      if ($(".resultTable .columnSelected").length > 0) {
        var _t = $(".resultTable");
        var _col = _t.find("th:nth-child(" + ($(".resultTable .columnSelected").index() + 1) + ")");
        _t.parent().animate({
          scrollLeft: _col.position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
        }, 300);
      }
    }
  });


});


// Codemirror query field
function getHighlightedQuery() {
  var selection = codeMirror.getSelection();
  if (selection != "") {
    return selection;
  }
  return null;
}

function reinitializeTable () {
  window.setTimeout(function(){
    $(".dataTables_wrapper").jHueTableScroller({
      minHeight: $(window).height() - 190,
      heightAfterCorrection: 0
    });
    $(".resultTable").jHueTableExtender({
      hintElement: "#jumpToColumnAlert",
      fixedHeader: true,
      firstColumnTooltip: true
    });
    $($("a[data-toggle='tab']").parent(".active").find("a").attr("href")).height($(".dataTables_wrapper").height());
    $(".dataTables_wrapper").jHueScrollUp({
      secondClickScrollToTop: true
    });
  }, 400)
}

$(document).ready(function () {
  var queryPlaceholder = "${_('Example: SELECT * FROM tablename, or press CTRL + space')}";

  $("#executeQuery").tooltip({
    title: '${_("Press \"tab\", then \"enter\".")}'
  });

  $("#executeQuery").keyup(function (event) {
    if (event.keyCode == 13) {
      tryExecuteQuery();
    }
  });

  initQueryField();

  var resizeTimeout = -1;
  var winWidth = $(window).width();
  var winHeight = $(window).height();

  $(window).on("resize", function () {
    window.clearTimeout(resizeTimeout);
    resizeTimeout = window.setTimeout(function () {
      // prevents endless loop in IE8
      if (winWidth != $(window).width() || winHeight != $(window).height()) {
        $("#navigator .card").css("min-height", ($(window).height() - 130) + "px");
        $("#navigatorTables").css("max-height", ($(window).height() - 260) + "px").css("overflow-y", "auto");
        winWidth = $(window).width();
        winHeight = $(window).height();
      }
    }, 200);
  });

  function initQueryField() {
    if ($("#queryField").val() == "") {
      $("#queryField").val(queryPlaceholder);
    }
  }

  var queryEditor = $("#queryField")[0];

  % if app_name == 'impala':
    var AUTOCOMPLETE_SET = CodeMirror.impalaSQLHint;
  % else:
    var AUTOCOMPLETE_SET = CodeMirror.hiveQLHint;
  % endif

  CodeMirror.onAutocomplete = function (data, from, to) {
    if (CodeMirror.tableFieldMagic) {
      codeMirror.replaceRange(" ", from, from);
      codeMirror.setCursor(from);
      codeMirror.execCommand("autocomplete");
    }
  };

  CodeMirror.commands.autocomplete = function (cm) {
    $(document.body).on("contextmenu", function (e) {
      e.preventDefault(); // prevents native menu on FF for Mac from being shown
    });

    var pos = cm.cursorCoords();
    $("<i class='fa fa-spinner fa-spin CodeMirror-spinner'></i>").css("top", pos.top + "px").css("left", (pos.left - 4) + "px").appendTo($("body"));

    if ($.totalStorage('tables_' + viewModel.database()) == null) {
      CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
      hac_getTables(viewModel.database(), function () {
      }); // if preload didn't work, tries again
    }
    else {
      hac_getTables(viewModel.database(), function (tables) {
        CodeMirror.catalogTables = tables;
        var _before = codeMirror.getRange({line: 0, ch: 0}, {line: codeMirror.getCursor().line, ch: codeMirror.getCursor().ch}).replace(/(\r\n|\n|\r)/gm, " ");
        CodeMirror.possibleTable = false;
        CodeMirror.tableFieldMagic = false;
        if (_before.toUpperCase().indexOf(" FROM ") > -1 && _before.toUpperCase().indexOf(" ON ") == -1 && _before.toUpperCase().indexOf(" WHERE ") == -1 ||
            _before.toUpperCase().indexOf("REFRESH") > -1 || _before.toUpperCase().indexOf("METADATA") > -1) {
          CodeMirror.possibleTable = true;
        }
        CodeMirror.possibleSoloField = false;
        if (_before.toUpperCase().indexOf("SELECT ") > -1 && _before.toUpperCase().indexOf(" FROM ") == -1 && !CodeMirror.fromDot) {
          if (codeMirror.getValue().toUpperCase().indexOf("FROM ") > -1) {
            fieldsAutocomplete(cm);
          }
          else {
            CodeMirror.tableFieldMagic = true;
            CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
          }
        }
        else {
          if (_before.toUpperCase().indexOf("WHERE ") > -1 && !CodeMirror.fromDot && _before.match(/ON|GROUP|SORT/) == null) {
            fieldsAutocomplete(cm);
          }
          else {
            CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
          }
        }
      });
    }
  }

  function fieldsAutocomplete(cm) {
    CodeMirror.possibleSoloField = true;
    try {
      var _possibleTables = $.trim(codeMirror.getValue(" ").substr(codeMirror.getValue().toUpperCase().indexOf("FROM ") + 4)).split(" ");
      var _foundTable = "";
      for (var i = 0; i < _possibleTables.length; i++) {
        if ($.trim(_possibleTables[i]) != "" && _foundTable == "") {
          _foundTable = _possibleTables[i];
        }
      }
      if (_foundTable != "") {
        if (hac_tableHasAlias(_foundTable, codeMirror.getValue())) {
          CodeMirror.possibleSoloField = false;
          CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
        }
        else {
          hac_getTableColumns(viewModel.database(), _foundTable, codeMirror.getValue(),
              function (columns) {
                CodeMirror.catalogFields = columns;
                CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
              });
        }
      }
    }
    catch (e) {
    }
  }

  CodeMirror.fromDot = false;

  codeMirror = CodeMirror(function (elt) {
    queryEditor.parentNode.replaceChild(elt, queryEditor);
  }, {
    value: queryEditor.value,
    readOnly: false,
    lineNumbers: true,
    mode: "text/x-hiveql",
    extraKeys: {
      "Ctrl-Space": function () {
        CodeMirror.fromDot = false;
        codeMirror.execCommand("autocomplete");
      },
      Tab: function (cm) {
        $("#executeQuery").focus();
      }
    },
    onKeyEvent: function (e, s) {
      if (s.type == "keyup") {
        if (s.keyCode == 190) {
          var _line = codeMirror.getLine(codeMirror.getCursor().line);
          var _partial = _line.substring(0, codeMirror.getCursor().ch);
          var _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length - 1);
          if (codeMirror.getValue().toUpperCase().indexOf("FROM") > -1) {
            hac_getTableColumns(viewModel.database(), _table, codeMirror.getValue(), function (columns) {
              var _cols = columns.split(" ");
              for (var col in _cols) {
                _cols[col] = "." + _cols[col];
              }
              CodeMirror.catalogFields = _cols.join(" ");
              CodeMirror.fromDot = true;
              window.setTimeout(function () {
                codeMirror.execCommand("autocomplete");
              }, 100);  // timeout for IE8
            });
          }
        }
      }
    }
  });

  codeMirror.on("focus", function () {
    if (codeMirror.getValue() == queryPlaceholder) {
      codeMirror.setValue("");
    }
    if (errorWidgets) {
      $.each(errorWidgets, function(index, errorWidget) {
        errorWidget.clear();
      });
      errorWidgets = [];
    }
    $("#validationResults").empty();
  });

  % if design and not design.id:
    if ($.totalStorage("${app_name}_temp_query") != null && $.totalStorage("${app_name}_temp_query") != "") {
      codeMirror.setValue($.totalStorage("${app_name}_temp_query"));
    }
  % endif

  codeMirror.on("blur", function () {
    $(document.body).off("contextmenu");
  });

  codeMirror.on("change", function () {
    $(".query").val(codeMirror.getValue());
    $.totalStorage("${app_name}_temp_query", codeMirror.getValue());
  });
});


$(document).one('fetched.query', function () {
  // Edit query name and description.
  $("#query-name").editable({
    validate: function (value) {
      if ($.trim(value) == '') {
        return "${ _('This field is required.') }";
      }
    },
    success: function (response, newValue) {
      viewModel.query.name(newValue);
    },
    emptytext: "${ _('Query name') }"
  });

  $("#query-description").editable({
    success: function (response, newValue) {
      viewModel.query.description(newValue);
    },
    emptytext: "${ _('Empty description') }"
  });
});


// Logs
var logsAtEnd = true;
$(document).ready(function () {
  var labels = {
    MRJOB: "${_('MR Job')}",
    MRJOBS: "${_('MR Jobs')}"
  };

  $(window).resize(function () {
    resizeLogs();
  });

  $("a[href='#log']").on("shown", function () {
    resizeLogs();
  });

  $("a[data-toggle='tab']").on("shown", function (e) {
    if ($(e.target).attr("href") != "#results"){
      $($(e.target).attr("href")).height($(".dataTables_wrapper").height());
      if ($(e.target).attr("href") == "#chart") {
        predictGraph();
      }
    }
    else {
      reinitializeTable();
    }
  });


  function getMapBounds(lats, lngs) {
    lats = lats.sort();
    lngs = lngs.sort();
    return [
      [lats[lats.length - 1], lngs[lngs.length - 1]], // north-east
      [lats[0], lngs[0]] // south-west
    ]
  }
  var map;
  function generateGraph(graphType) {
    if (graphType != "") {
      if (map != null) {
        try {
          map.remove();
        }
        catch (err) { // do nothing
        }
      }
      $("#blueprintDownload").addClass("hide");
      $("#blueprint").attr("class", "").attr("style", "").empty();
      $("#blueprint").data("plugin_jHueBlueprint", null);
      if (graphType == $.jHueBlueprint.TYPES.MAP) {
        if ($("#blueprintLat").val() != "-1" && $("#blueprintLng").val() != "-1") {
          var _latCol = $("#blueprintLat").val() * 1;
          var _lngCol = $("#blueprintLng").val() * 1;
          var _descCol = $("#blueprintDesc").val() * 1;
          var _lats = [];
          var _lngs = [];
          $(".resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
            _lats.push($.trim($(this).text()) * 1);
          });
          $(".resultTable>tbody>tr>td:nth-child(" + _lngCol + ")").each(function (cnt) {
            _lngs.push($.trim($(this).text()) * 1);
          });
          //$("#blueprint").addClass("map");
          $("#blueprint").height($("#blueprint").parent().height() - 100);
          map = L.map("blueprint").fitBounds(getMapBounds(_lats, _lngs));

          L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          }).addTo(map);

          $(".resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
            if (cnt < 1000) {
              if (_descCol != "-1") {
                L.marker([$.trim($(this).text()) * 1, $.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1]).addTo(map).bindPopup($.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _descCol + ")").text()));
              }
              else {
                L.marker([$.trim($(this).text()) * 1, $.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1]).addTo(map);
              }
            }
          });

        }
        else {
          $("#blueprint").addClass("empty").text("${_("Please select the latitude and longitude columns.")}");
        }
      }
      else {
        if ($("#blueprintX").val() != "-1" && $("#blueprintY").val() != "-1") {
          var _x = $("#blueprintX").val() * 1;
          var _y = $("#blueprintY").val() * 1;
          var _data = [];
          $(".resultTable>tbody>tr>td:nth-child(" + _x + ")").each(function (cnt) {
            if (cnt < 1000) {
              _data.push([$.trim($(this).text()), $.trim($(".resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _y + ")").text()) * 1]);
            }
          });

          $("#blueprint").jHueBlueprint({
            data: _data,
            label: $(".resultTable>thead>tr>th:nth-child(" + _y + ")").text(),
            type: graphType,
            color: $.jHueBlueprint.COLORS.BLUE,
            isCategories: true,
            fill: true,
            enableSelection: false,
            height: 250
          });
          if (_data.length > 30){
            $(".flot-x-axis .flot-tick-label").hide();
          }
          $("#blueprintDownload").removeClass("hide");
        }
        else {
          $("#blueprint").addClass("empty").text("${_("Please select the columns you would like to see in this chart.")}");
        }
      }
    }
  }

  $("#blueprintDownload").on("click", function(){
    window.open($(".flot-base")[0].toDataURL());
  });

  function getGraphType() {
    var _type = "";
    if ($("#blueprintBars").hasClass("active")) {
      _type = $.jHueBlueprint.TYPES.BARCHART;
    }
    if ($("#blueprintLines").hasClass("active")) {
      _type = $.jHueBlueprint.TYPES.LINECHART;
    }
    if ($("#blueprintMap").hasClass("active")) {
      _type = $.jHueBlueprint.TYPES.MAP;
    }
    return _type;
  }

  var hasBeenPredicted = false;
  function predictGraph() {
    if (!hasBeenPredicted) {
      hasBeenPredicted = true;
      var _firstAllString, _firstAllNumeric;
      for (var i = 1; i < $(".resultTable>thead>tr>th").length; i++) {
        var _isNumeric = true;
        $(".resultTable>tbody>tr>td:nth-child(" + (i + 1) + ")").each(function (cnt) {
          if (!$.isNumeric($.trim($(this).text()))) {
            _isNumeric = false;
          }
        });
        if (_firstAllString == null && !_isNumeric) {
          _firstAllString = i + 1;
        }
        if (_firstAllNumeric == null && _isNumeric) {
          _firstAllNumeric = i + 1;
        }
      }
      if (_firstAllString != null && _firstAllNumeric != null) {
        $("#blueprintBars").addClass("active");
        $("#blueprintAxis").removeClass("hide");
        $("#blueprintLatLng").addClass("hide");
        $("#blueprintX").val(_firstAllString);
        $("#blueprintY").val(_firstAllNumeric);
      }
    }
    generateGraph(getGraphType());
  }

  $(".blueprintSelect").on("change", function () {
    generateGraph(getGraphType())
  });

  $("#blueprintBars").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    generateGraph($.jHueBlueprint.TYPES.BARCHART)
  });
  $("#blueprintLines").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    generateGraph($.jHueBlueprint.TYPES.LINECHART)
  });
  $("#blueprintMap").on("click", function () {
    $("#blueprintAxis").addClass("hide");
    $("#blueprintLatLng").removeClass("hide");
    generateGraph($.jHueBlueprint.TYPES.MAP)
  });

  $("#log pre").scroll(function () {
    if ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight) {
      logsAtEnd = true;
    }
    else {
      logsAtEnd = false;
    }
  });

  viewModel.query.watch.logs.subscribe(function(val){
    if (logsAtEnd) {
      var _logsEl = $("#log pre");
      _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
    }
  });
});

function resizeLogs() {
  // Use fixed subtraction since logs aren't always visible.
  $("#log").height($(window).height() - $("#log pre").offset().top - 10);
  $("#log pre").css("overflow", "auto").height($(window).height() - $("#log pre").offset().top - 50);
}

// Result Datatable
function cleanResultsTable() {
  if (dataTable) {
    dataTable.fnClearTable();
    dataTable.fnDestroy();
    viewModel.query.results.columns.valueHasMutated();
    viewModel.query.results.rows.valueHasMutated();
    dataTable = null;
  }
}

function addResults(viewModel, dataTable, index, pageSize) {
  if (viewModel.hasMoreResults() && index + pageSize > viewModel.query.results.rows().length) {
    $(document).one('fetched.results', function () {
      $.totalStorage("${app_name}_temp_query", null);
      dataTable.fnAddData(viewModel.query.results.rows.slice(index, index + pageSize));
    });
    viewModel.fetchResults();
  } else {
    dataTable.fnAddData(viewModel.query.results.rows.slice(index, index + pageSize));
  }
}

function resultsTable(e, data) {
  if (!dataTable && viewModel.query.results.columns().length > 0) {
    dataTable = $(".resultTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bDestroy": true,
      "bAutoWidth": false,
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}"
      },
      "fnDrawCallback": function (oSettings) {
        reinitializeTable();
      },
      "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        // Make sure null values are seen as NULL.
        for (var j = 0; j < aData.length; ++j) {
          if (aData[j] == null) {
            $(nRow).find('td:eq(' + j + ')').html("NULL");
          }
        }
        return nRow;
      },
      "aoColumnDefs": [
        {
          "sType": "numeric",
          "aTargets": [ "sort-numeric" ]
        },
        {
          "sType": "string",
          "aTargets": [ "sort-string" ]
        },
        {
          "sType": "date",
          "aTargets": [ "sort-date" ]
        }
      ]
    });
    $(".dataTables_filter").hide();
    reinitializeTable();
    var _options = '<option value="-1">${ _("Please select a column")}</option>';
    $(viewModel.query.results.columns()).each(function(cnt, item){
      _options += '<option value="'+(cnt + 1)+'">'+ item.name +'</option>';
    });
    $(".blueprintSelect").html(_options);

    // Automatic results grower
    var dataTableEl = $(".dataTables_wrapper");
    var index = 0;
    var pageSize = 100;
    dataTableEl.on("scroll", function (e) {
      if (dataTableEl.scrollTop() + dataTableEl.outerHeight() + 20 > dataTableEl[0].scrollHeight && dataTable) {
        dataTableEl.animate({opacity: '0.55'}, 200);
        $(".spinner").show();
        addResults(viewModel, dataTable, index, pageSize);
        index += pageSize;
        $(".spinner").hide();
        dataTableEl.animate({opacity: '1'}, 50);
      }
    });
    addResults(viewModel, dataTable, index, pageSize);
    index += pageSize;
    dataTableEl.jHueScrollUp({
      secondClickScrollToTop: true
    });
  }
}

$(document).on('execute.query', cleanResultsTable);
$(document).on('explain.query', cleanResultsTable);
$(document).on('fetched.results', resultsTable);

var selectedLine = -1;
var errorWidgets = [];

$(document).on('error.query', function () {
  $.each(errorWidgets, function(index, el) {
    $(el).remove();
    errorWidgets = [];
  });

  // Move error to codeMirror if we konw the line number
  $.each($(".queryErrorMessage"), function(index, el) {
    var err = $(el).text().toLowerCase();
    var firstPos = err.indexOf("line");
    if (firstPos > -1) {
      selectedLine = $.trim(err.substring(err.indexOf(" ", firstPos), err.indexOf(":", firstPos))) * 1;
      errorWidgets.push(
         codeMirror.addLineWidget(
             selectedLine - 1,
             $("<div>").addClass("editorError").html("<i class='fa fa-exclamation-circle'></i> " + err)[0], {
                 coverGutter: true,
                 noHScroll: true
             }
         )
      );
      $(el).hide();
    }
  });

  if ($(".queryErrorMessage:hidden").length == $(".queryErrorMessage").length) {
    $(".queryErrorMessage").parent().parent().hide();
  }
});


// Save
function trySaveQuery() {
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.query.query(query);
  if (viewModel.query.id() && viewModel.query.id() != -1) {
    viewModel.saveQuery();
  }
}

function saveAsModal() {
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.query.query(query);
  $('#saveAs').modal('show');
}

function trySaveAsQuery() {
  if (viewModel.query.query() && viewModel.query.name()) {
    viewModel.query.id(-1);
    viewModel.saveQuery();
    $('#saveas-query-name').removeClass('error');
    $('#saveAs').modal('hide');
  } else if (viewModel.query.name()) {
    $.jHueNotify.error("${_('No query provided to save.')}");
    $('#saveAs').modal('hide');
  } else {
    $('#saveas-query-name').addClass('error');
  }
}

function saveResultsModal() {
  $('#saveResultsModal').modal('show');
}

function trySaveResults() {
  viewModel.saveResults();
}

$(document).on('saved.results', function() {
  $('#saveResultsModal').modal('hide');
});


// Querying and click events.
function tryExecuteQuery() {
  $(".tooltip").remove();
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.query.query(query);
  if ($(".dataTables_wrapper").length > 0) { // forces results to be up
    $(".dataTables_wrapper").scrollTop(0);
  }
  if (viewModel.query.isParameterized()) {
    viewModel.fetchParameters();
  } else {
    viewModel.executeQuery();
  }
}

function tryExecuteParameterizedQuery() {
  $(".tooltip").remove();
  viewModel.executeQuery();
  routie('query');
}
;

function tryExplainQuery() {
  $(".tooltip").remove();
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.query.query(query);
  viewModel.explainQuery();
}

function tryExplainParameterizedQuery() {
  $(".tooltip").remove();
  viewModel.explainQuery();
  routie('query');
}
;

function tryCancelQuery() {
  $(".tooltip").remove();
  viewModel.cancelQuery();
}

function createNewQuery() {
  $.totalStorage("${app_name}_temp_query", null);
  location.href="${ url('beeswax:execute_query') }";
}

function checkLastDatabase(server, database) {
  var key = "hueBeeswaxLastDatabase-" + server;
  if (database != $.totalStorage(key)) {
    $.totalStorage(key, database);
  }
}

function getLastDatabase(server) {
  var key = "hueBeeswaxLastDatabase-" + server;
  return $.totalStorage(key);
}


// Knockout
function clickHard(el) {
  var timer = setInterval(function () {
    if ($(el).length > 0) {
      $(el).click();
      clearInterval(timer);
    }
  }, 100);
}

viewModel = new BeeswaxViewModel("${app_name}", ${design.id and design.id or -1});
viewModel.fetchDatabases();
var subscription = viewModel.databases.subscribe(function() {
  if (viewModel.query.id() > 0) {
    viewModel.fetchQuery();
  }
  subscription.dispose();
});
if (viewModel.query.id() > 0) {
  // Code mirror and ko.
  viewModel.query.query.subscribe((function () {
    // First call skipped to avoid reset of hueBeeswaxLastDatabase
    var counter = 0;
    return function (value) {
      if (counter++ == 0) {
        codeMirror.setValue(value);
      }
    }
  })());
  viewModel.fetchQuery();
}
viewModel.query.fileResources.subscribe(function() {
  // File chooser button for file resources.
  $(".pathChooser:not(:has(~ button))").after(getFileBrowseButton($(".pathChooser:not(:has(~ button))")));
});
ko.applyBindings(viewModel);

// Server error handling.
$(document).on('server.error', function (e, data) {
  $(document).trigger('error', "${_('Server error occured: ')}" + data.message ? data.message : data.error);
});
$(document).on('server.unmanageable_error', function (e, responseText) {
  $(document).trigger('error', "${_('Unmanageable server error occured: ')}" + responseText);
});

// Other
$(document).on('saved.query', function (e, id) {
  $(document).trigger('info', "${'Query saved.'}");
  window.location.href = "/beeswax/execute/" + id;
});
$(document).on('error_cancel.query', function (e, message) {
  $(document).trigger("error", "${ _('Problem: ') }" + message);
});
$(document).on('cancelled.query', function (e) {
  $(document).trigger("info", "${ _('Query canceled!') }")
});

function updateSidebarTooltips(selector) {
  $(selector).each(function(){
    $(this).tooltip({
      placement: "right",
      title: $(this).val()
    }).attr('data-original-title', $(this).val()).tooltip('fixTitle');
  });
}

$(document).ready(function () {
  $(".pathChooser:not(:has(~ button))").after(getFileBrowseButton($(".pathChooser:not(:has(~ button))")));

  $("*[rel=tooltip]").tooltip({
    placement: 'bottom'
  });

  // hack for select default rendered fields
  $("select").addClass("input-medium");

  // Type ahead for settings.
  $.getJSON("${ url(app_name + ':configuration') }", function (data) {
    $(".settingsField").typeahead({
      source: $.map(data.config_values, function (value, key) {
        return value.key;
      })
    });
  });

  // Help.
  $("#help").popover({
    'title': "${_('Did you know?')}",
    'content': $("#help-content").html(),
    'trigger': 'hover',
    'html': true
  });

  $(document).on("change", ".settingsField", function(){
    updateSidebarTooltips(".settingsField");
  });

  $(document).on("change", ".settingValuesField", function(){
    updateSidebarTooltips(".settingValuesField");
  });

  $(document).on("change", ".filesField", function(){
    updateSidebarTooltips(".filesField");
  });

  $(document).on("change", ".functionsField", function(){
    updateSidebarTooltips(".functionsField");
  });

  $(document).on("change", ".classNamesField", function(){
    updateSidebarTooltips(".classNamesField");
  });

  // loads default
  updateSidebarTooltips(".settingsField");
  updateSidebarTooltips(".settingValuesField");
  updateSidebarTooltips(".filesField");
  updateSidebarTooltips(".functionsField");
  updateSidebarTooltips(".classNamesField");

  % if app_name == 'impala':
    $("#downloadQuery").click(function () {
      $("<input>").attr("type", "hidden").attr("name", "button-submit").attr("value", "Execute").appendTo($("#advancedSettingsForm"));
      $("<input>").attr("type", "hidden").attr("name", "download").attr("value", "true").appendTo($("#advancedSettingsForm"));
      tryExecuteQuery();
    });
  % endif

  % if app_name == 'impala':
    $("#refresh-dyk").popover({
      'title': "${_('Missing some tables? In order to update the list of tables/metadata seen by Impala, execute one of these queries:')}",
      'content': $("#refresh-content").html(),
      'trigger': 'hover',
      'html': true
    });

    $("#refresh-tip").popover({
      'title': "${_('Missing some tables? In order to update the list of tables/metadata seen by Impala, execute one of these queries:')}",
      'content': $("#refresh-content").html(),
      'trigger': 'hover',
      'html': true
    });

    window.onbeforeunload = function(e) {
      viewModel.closeQuery();
    };

    $(document).on('explain.query', function() {
      viewModel.closeQuery();
    });

    $(document).on('execute.query', function() {
      viewModel.closeQuery();
    });
  % endif
});


// Routie
$(document).ready(function () {
  routie({
    'query': function () {
      showSection('query-editor');
      $('.resultsContainer').hide();
      codeMirror.setSize("99%", $(window).height() - 270 - $("#queryPane .alert-error").outerHeight() - $(".nav-tabs").outerHeight());
    },
    'query/execute/params': function () {
      if (viewModel.query.parameters().length == 0) {
        routie('query');
      }
      showSection('execute-parameter-selection');
    },
    'query/explain/params': function () {
      if (viewModel.query.parameters().length == 0) {
        routie('query');
      }
      showSection('explain-parameter-selection');
    },
    'query/logs': function () {
      if (viewModel.query.watch.logs().length == 0 && viewModel.query.watch.errors().length == 0) {
        routie('query');
      }
      codeMirror.setSize("99%", 100);
      $('.resultsContainer').show();
      $('.resultsContainer .watch-query').show();
      $('.resultsContainer .view-query-results').hide();
      clickHard('.resultsContainer .nav-tabs a[href="#log"]');
    },
    'query/results': function () {
      if (viewModel.query.id() == -1 && viewModel.query.results.empty()) {
        routie('query');
      } else {
        codeMirror.setSize("99%", 100);
        $('.resultsContainer').show();
        $('.resultsContainer .watch-query').hide();
        $('.resultsContainer .view-query-results').show();
        clickHard('.resultsContainer .nav-tabs a[href="#results"]');
        $("html, body").animate({ scrollTop: ($(".resultsContainer").position().top - 80) + "px" });
      }
    },
    'query/explanation': function () {
      if (!viewModel.query.results.explanation()) {
        routie('query');
      }
      codeMirror.setSize("99%", 100);
      $('.resultsContainer').show();
      $('.resultsContainer .watch-query').hide();
      $('.resultsContainer .view-query-results').show();
      clickHard('.resultsContainer .nav-tabs a[href="#explanation"]');
    },
    '': function () {
      routie('query');
    }
  });
  $(document).on('fetched.parameters', function () {
    if (viewModel.query.parameters().length > 0) {
      routie('query/execute/params');
    } else {
      viewModel.executeQuery();
    }
  });
  $(document).on('explained.query', function () {
    routie('query/explanation');
  });
  $(document).on('watched.query', function (e, data) {
    if (data.status && data.status && data.status != 0) {
      viewModel.query.watch.errors.push(data.error || data.message);
    }
    routie('query/logs');
  });
  $(document).on('error_watch.query', function () {
    routie('query/logs');
  });
  $(document).on('fetched.results', function () {
    routie('query/results');
  });
  $(document).on('execute.query', function() {
    routie('query');
  });
});

// @TODO: Improve resize logs to be more relative. See FF versus Chrome.
// @TODO: Stop operation
// @TODO: Re-add download query for impala
// @TODO: Re-enable type ahead for settings
</script>

${ commonfooter(messages) | n,unicode }
