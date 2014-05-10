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
  from beeswax import conf as beeswax_conf
  from impala import conf as impala_conf
  from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Query'), app_name, user) | n,unicode }
${layout.menubar(section='query')}

<div id="temporaryPlaceholder"></div>

<div id="query-editor" class="container-fluid hide section">
<div class="row-fluid">

<div class="span2" id="navigator">
  <ul class="nav nav-tabs" style="margin-bottom: 0">
    <li class="active"><a href="#navigatorTab" data-toggle="tab" class="sidetab">${_('Assist')}</a></li>
    <li><a href="#settingsTab" data-toggle="tab" class="sidetab">${_('Settings')} <span data-bind="visible:design.settings.values().length + design.fileResources.values().length + design.functions.values().length > 0, text: design.settings.values().length + design.fileResources.values().length + design.functions.values().length" class="badge badge-info">12</span></a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="navigatorTab">
      <div class="card card-small card-tab">
        <div class="card-body" style="margin-top: 0">
          <a href="#" title="${_('Double click on a table name or field to insert it in the editor')}" rel="tooltip" data-placement="top" class="pull-right" style="margin:3px; margin-top:7px"><i class="fa fa-question-circle"></i></a>
          <a id="refreshNavigator" href="#" title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="top" class="pull-right" style="margin:3px; margin-top:7px"><i class="fa fa-refresh"></i></a>
          <ul class="nav nav-list" style="border: none; padding: 0; background-color: #FFF">
            <li class="nav-header">${_('database')}</li>
          </ul>
          <select data-bind="options: databases, value: database" class="input-medium chosen-select" name="query-database" data-placeholder="${_('Choose a database...')}"></select>
          <input id="navigatorSearch" type="text" placeholder="${ _('Table name...') }" style="width:90%; margin-top: 20px"/>
          <div id="navigatorNoTables">${_('The selected database has no tables.')}</div>
          <ul id="navigatorTables" class="unstyled"></ul>
          <div id="navigatorLoader">
            <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #DDD"></i><!--<![endif]-->
            <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
          </div>
        </div>
      </div>
    </div>
    <div class="tab-pane" id="settingsTab">
      <div class="card card-small card-tab">
        <div class="card-body">
          <div id="advanced-settings">
          <form id="advancedSettingsForm" action="" method="POST" class="form form-horizontal">
              <ul class="nav nav-list" style="border: none; padding: 0;">
                <li class="nav-header">${_('settings')}</li>
                <li class="white paramContainer">
                  <!-- ko foreach: design.settings.values -->
                  <div class="param">
                    <div class="remove">
                      <button data-bind="click: $root.removeSetting.bind(this, $index())" type="button" class="btn btn-mini settingsDelete" title="${_('Delete this setting')}">x
                      </button>
                    </div>
                    <div data-bind="css: {'error': $root.getSettingKeyErrors($index()).length > 0}" class="control-group">
                      <label>${_('Key')}</label>
                      <input data-bind="value: key" type="text" class="settingsField span8" autocomplete="off" placeholder="${ 'impala.resultset.cache.size' if app_name == 'impala' else 'mapred.reduce.tasks' }"/>
                    </div>

                    <div data-bind="css: {'error': $root.getSettingValueErrors($index()).length > 0}" class="control-group">
                      <label>${_('Value')}</label>
                      <input data-bind="value: value" type="text" class="settingValuesField span8" placeholder="${ '5000' if app_name == 'impala' else '1' }"/>
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
                  <!-- ko foreach: design.fileResources.values -->
                  <div class="param">
                    <div class="remove">
                      <button data-bind="click: $root.removeFileResource.bind(this, $index())" type="button" class="btn btn-mini" title="${_('Delete this setting')}">&times;</button>
                    </div>
                    <div data-bind="css: {'error': $root.getFileResourceTypeErrors($index()).length > 0}" class="control-group">
                      <label>${_('Type')}</label>
                      <select data-bind="value: type" class="input-small">
                        <option value="JAR">${_('jar')}</option>
                        <option value="ARCHIVE">${_('archive')}</option>
                        <option value="FILE">${_('file')}</option>
                      </select>
                    </div>

                    <div data-bind="css: {'error': $root.getFileResourcePathErrors($index()).length > 0}" class="control-group">
                      <label>${_('Path')}</label>
                      <input data-bind="value: path" type="text" class="filesField span7 fileChooser" placeholder="/user/foo/udf.jar"/>
                    </div>
                  </div>
                  <!-- /ko -->

                  <div class="control-group">
                    <a data-bind="click: function() { $root.addFileResource('','') }" class="btn btn-mini paramAdd">${_('Add')}</a>
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
                  <!-- ko foreach: design.functions.values -->
                  <div class="param">
                    <div class="remove">
                      <button data-bind="click: $root.removeFunction.bind(this, $index())" type="button" class="btn btn-mini settingsDelete" title="${_('Delete this setting')}">&times;</button>
                    </div>
                    <div data-bind="css: {'error': $root.getFunctionNameErrors($index()).length > 0}" class="control-group">
                      <label>${_('Name')}</label>
                      <input data-bind="value: name" type="text" class="functionsField span8" autocomplete="off" placeholder="myFunction"/>
                    </div>

                    <div data-bind="css: {'error': $root.getFunctionClassNameErrors($index()).length > 0}" class="control-group">
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
                <li class="white" style="padding-top:0; padding-left:0">
                  <label class="checkbox" rel="tooltip" data-original-title="${_("If checked (the default), you can include parameters like $parameter_name in your query, and users will be prompted for a value when the query is run.")}">
                    <input data-bind="checked: design.isParameterized" type="checkbox"/>
                    ${_("Enable parameterization")}
                  </label>
                  <label class="checkbox
                  % if app_name == 'impala':
                    hide
                  % endif
                  " rel="tooltip" data-original-title="${_("If checked, you will receive an email notification when the query completes.")}">
                    <input data-bind="checked: design.email" type="checkbox"/>
                    ${_("Email me on completion")}
                  </label>
                </li>
                % if app_name == 'impala':
                  <li class="nav-header">
                    ${_('Metastore Catalog')}
                  </li>
                  <li class="white" style="padding-top:0; padding-left:0">
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
              </ul>
          </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="querySide" class="span10">
  <div id="queryContainer" class="card card-small">
    <div class="pull-right" style="margin: 10px">
      <i class="fa fa-question-circle" id="help"></i>
      <div id="help-content" class="hide">
        <ul style="text-align: left;">
          <li>${ _('Press CTRL + Space to autocomplete') }</li>
          <li>${ _("You can execute queries with multiple SQL statements delimited by a semicolon ';'") }</li>
          <li>${ _('You can highlight and run a fragment of a query') }</li>
        </ul>
      </div>
    </div>
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

          <div data-bind="css: {'hide': design.errors().length == 0}" class="alert alert-error">
            <!-- ko if: $root.getQueryErrors().length > 0 -->
            <p><strong>${_('Please provide a query')}</strong></p>
            <!-- /ko -->
            <!-- ko if: $root.getQueryErrors().length == 0 -->
            <p><strong>${_('Your query has the following error(s):')}</strong></p>

            <div data-bind="foreach: design.errors">
              <p data-bind="text: $data" class="queryErrorMessage"></p>
            </div>
            <!-- /ko -->
          </div>

          <div data-bind="css: {'hide': design.watch.errors().length == 0}" class="alert alert-error">
            <p><strong>${_('Your query has the following error(s):')}</strong></p>

            <div data-bind="foreach: design.watch.errors">
              <p data-bind="text: $data" class="queryErrorMessage"></p>
            </div>
          </div>

          <textarea class="hide" tabindex="1" name="query" id="queryField"></textarea>

          <div class="actions">
            <button data-bind="click: tryExecuteQuery, visible: $root.canExecute, enable: $root.queryEditorBlank" type="button" id="executeQuery" class="btn btn-primary disable-feedback" tabindex="2">${_('Execute')}</button>
            <button data-bind="click: tryCancelQuery, visible: $root.design.isRunning()" class="btn btn-danger" data-loading-text="${ _('Canceling...') }" rel="tooltip" data-original-title="${ _('Cancel the query') }">${ _('Cancel') }</button>

            <button data-bind="click: tryExecuteNextStatement, visible: !$root.design.isFinished()" type="button" class="btn btn-primary disable-feedback" tabindex="2">${_('Next')}</button>
            <button data-bind="click: tryExecuteQuery, visible: !$root.design.isFinished()" type="button" id="executeQuery" class="btn btn-primary disable-feedback" tabindex="2">${_('Restart')}</button>

            % if can_edit:
            <button data-bind="click: trySaveDesign, css: {'hide': !$root.design.id() || $root.design.id() == -1}" type="button" class="btn hide">${_('Save')}</button>
            % endif
            <button data-bind="click: saveAsModal" type="button" class="btn">${_('Save as...')}</button>
            <button data-bind="click: tryExplainQuery, visible: $root.canExecute" type="button" id="explainQuery" class="btn">${_('Explain')}</button>
            &nbsp; ${_('or create a')} &nbsp;
            <button data-bind="click: createNewQuery" type="button" class="btn">${_('New query')}</button>
            <br/><br/>
          </div>

        </div>
      </div>
    </div>
  </div>

  <div id="resizePanel"><a href="javascript:void(0)"><i class="fa fa-ellipsis-h"></i></a></div>

  <div class="card card-small scrollable resultsContainer">
    <div data-bind="visible: !design.explain() && $root.hasResults()">
      <a id="expandResults" href="javascript:void(0)" title="${_('See results in full screen')}" rel="tooltip"
        class="view-query-results hide pull-right"><h4 style="margin-right: 20px"><i class="fa fa-expand"></i></h4></a>

      <a id="save-results" data-bind="click: saveResultsModal" href="javascript:void(0)" title="${_('Save the results to HDFS or a new Hive table')}" rel="tooltip"
        class="view-query-results hide pull-right"><h4 style="margin-right: 20px"><i class="fa fa-save"></i></h4>
      </a>

      <a id="download-csv" data-bind="attr: {'href': '/${ app_name }/download/' + $root.design.history.id() + '/csv'}" href="javascript:void(0)" title="${_('Download the results in CSV format')}" rel="tooltip"
        class="view-query-results download hide pull-right"><h4 style="margin-right: 20px"><i class="hfo hfo-file-csv"></i></h4>
      </a>

      <a id="download-excel" data-bind="attr: {'href': '/${ app_name }/download/' + $root.design.history.id() + '/xls'}" href="javascript:void(0)" title="${_('Download the results in XLS format')}" rel="tooltip"
        class="view-query-results download hide pull-right"><h4 style="margin-right: 20px"><i class="hfo hfo-file-xls"></i></h4></a>
    </div>

    <div class="card-body">
      <ul class="nav nav-tabs">
        <li class="active recentLi"><a href="#recentTab" data-toggle="tab">${_('Recent queries')}</a></li>
        <li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
        <!-- ko if: !design.explain() -->
        <li><a href="#log" data-toggle="tab">${_('Log')}</a></li>
        <!-- /ko -->
        <!-- ko if: !design.explain() -->
        <li><a href="#columns" data-toggle="tab">${_('Columns')}</a></li>
        <li><a href="#results" data-toggle="tab">${_('Results')}</a></li>
        <li><a href="#chart" data-toggle="tab">${_('Chart')}</a></li>
        <!-- /ko -->
        <!-- ko if: design.explain() && !design.isRunning() -->
        <li><a href="#explanation" data-toggle="tab">${_('Explanation')}</a></li>
        <!-- /ko -->
      </ul>

      <div class="tab-content">
        <div class="active tab-pane" id="recentTab">
          <div id="recentLoader">
            <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #DDD"></i><!--<![endif]-->
            <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
          </div>
          <table id="recentQueries" class="table table-striped table-condensed datatables" cellpadding="0" cellspacing="0" data-tablescroller-enforce-height="true">
            <thead>
              <tr>
                <th>${_('Time')}</th>
                <th>${_('Query')}</th>
                <th>${_('Result')}</th>
                <th>&nbsp;</th>
              </tr>
            </thead>
            <tbody>
            </tbody>
          </table>
        </div>
        <div class="tab-pane" id="query">
          <pre data-bind="visible: viewModel.design.statement() == ''">${_('There is currently no query to visualize.')}</pre>
          <pre data-bind="visible: viewModel.design.statement() != '', text: viewModel.design.statement()"></pre>
        </div>

        <!-- ko if: design.explain() -->
        <div class="tab-pane" id="explanation">
          <pre data-bind="text: $root.design.results.explanation()"></pre>
        </div>
        <!-- /ko -->

        <!-- ko if: !design.explain() -->
        <div class="tab-pane" id="log">
          <div style="position:relative">
            <ul data-bind="foreach: $root.design.watch.jobUrls" class="unstyled jobs-overlay">
              <li><a data-bind="text: $.trim($data.name), attr: { href: $data.url }" target="_blank"></a></li>
            </ul>
            <pre data-bind="visible: $root.design.watch.logs().length == 0">${_('There are currently no logs to visualize.')} <img src="/static/art/spinner.gif" data-bind="visible: $root.design.isRunning()"/></pre>
            <pre data-bind="visible: $root.design.watch.logs().length > 0, text: $root.design.watch.logs().join('\n')"></pre>
          </div>
        </div>

        <div class="tab-pane" id="columns">
          <pre data-bind="visible: $root.design.results.columns().length == 0">${_('There are currently no columns to visualize.')}</pre>
          <div data-bind="visible: $root.design.results.columns().length > 10">
            <input id="columnFilter" class="input-xlarge" type="text" placeholder="${_('Filter for column name or type...')}" />
          </div>
          <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
            <tbody data-bind="foreach: $root.design.results.columns">
              <tr class="columnRow" data-bind="visible: $index() > 0">
                <td rel="columntooltip" data-placement="left" data-bind="attr: {title: '${ _("Scroll to the column") }">
                  <a href="javascript:void(0)" data-row-selector="true" class="column-selector" data-bind="text: $data.name"></a>
                </td>
                <td class="columnType" data-bind="text: $.trim($data.type)"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="results">
          <div data-bind="css: {'hide': design.results.errors().length == 0}" class="alert alert-error">
            <p><strong>${_('Fetching results ran into the following error(s):')}</strong></p>

            <div data-bind="foreach: design.results.errors">
              <p data-bind="text: $data" class="queryErrorMessage"></p>
            </div>
          </div>

          <div data-bind="css: {'hide': !$root.hasResults()}">
            <table id="resultTable" class="table table-striped table-condensed" cellpadding="0" cellspacing="0" data-tablescroller-enforce-height="true">
              <thead>
              <tr data-bind="foreach: $root.design.results.columns">
                <th data-bind="html: ($index() == 0 ? '&nbsp;' : $data.name), css: { 'sort-numeric': isNumericColumn($data.type), 'sort-date': isDateTimeColumn($data.type), 'sort-string': isStringColumn($data.type)}"></th>
              </tr>
              </thead>
            </table>
          </div>

          <div data-bind="css: {'hide': !$root.design.results.empty() || $root.design.results.expired()}" id="resultEmpty">
            <pre>${_('The operation has no results.')}</pre>
          </div>

          <div data-bind="css: {'hide': !$root.design.results.expired()}" id="resultExpired">
            <pre>${_('The results have expired, rerun the query if needed.')}</pre>
          </div>
        </div>

        <div class="tab-pane" id="chart">
          <pre data-bind="visible: $root.design.results.columns().length == 0">${_('There is currently no data to build a chart on.')}</pre>
          <div class="alert hide">
            <strong>${_('Warning:')}</strong> ${_('the results on the chart have been limited to 1000 rows.')}
          </div>
          <div data-bind="visible: $root.design.results.columns().length > 0" style="text-align: center">
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
              </label>
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
          <div  data-bind="visible: $root.design.results.columns().length > 0" id="blueprint" class="empty">${_("Please select a chart type.")}</div>
        </div>
        <!-- /ko -->
      </div>
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
            <!-- ko foreach: $root.design.parameters -->
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
            <!-- ko foreach: $root.design.parameters -->
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

<div id="chooseFolder" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Select a directory')}</h3>
  </div>
  <div class="modal-body">
    <div id="folderchooser">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>

<div id="choosePath" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Select a file or directory')}</h3>
  </div>
  <div class="modal-body">
    <div id="pathchooser">
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
        <input data-bind="value: $root.design.name" type="text" class="input-xlarge">
      </div>
    </div>
    <div class="control-group">
      <label class="control-label">${_('Description')}</label>

      <div class="controls">
        <input data-bind="value: $root.design.description" type="text" class="input-xlarge">
      </div>
    </div>
  </form>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <button data-bind="click: trySaveAsDesign" class="btn btn-primary">${_('Save')}</button>
  </div>
</div>


<div id="saveResultsModal" class="modal hide fade">
  <div class="loader">
    <div class="overlay"></div>
    <!--[if !IE]><!--><i class="fa fa-spinner fa-spin"></i><!--<![endif]-->
    <!--[if IE]><img class="spinner" src="/static/art/spinner-big-inverted.gif"/><![endif]-->
  </div>

  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Save Query Results')}</h3>
  </div>
  <div class="modal-body" style="padding: 4px">
    <!-- ko if: $root.design.results.save.saveTargetError() -->
      <h4 data-bind="text: $root.design.results.save.saveTargetError()"></h4>
    <!-- /ko -->
    <!-- ko if: $root.design.results.save.targetTableError() -->
      <h4 data-bind="text: $root.design.results.save.targetTableError()"></h4>
    <!-- /ko -->
    <!-- ko if: $root.design.results.save.targetDirectoryError() -->
      <h4 data-bind="text: $root.design.results.save.targetDirectoryError()"></h4>
    <!-- /ko -->
    <form id="saveResultsForm" method="POST" class="form form-inline">
      <fieldset>
        <div data-bind="css: {'error': $root.design.results.save.targetFileError()}" class="control-group">
          <div class="controls">
            <label class="radio">
              <input data-bind="checked: $root.design.results.save.type" type="radio" name="save-results-type" value="hdfs-file">
              &nbsp;${ _('In an HDFS file') }
            </label>
            <span data-bind="visible: $root.design.results.save.type() == 'hdfs-file'">
              <input data-bind="value: $root.design.results.save.path" type="text" name="target_file" placeholder="${_('Path to CSV file')}" class="pathChooser">
            </span>
            <label class="radio" data-bind="visible: $root.design.results.save.type() == 'hdfs-file'">
              <input data-bind="checked: $root.design.results.save.overwrite" type="checkbox" name="overwrite">
              ${ _('Overwrite') }
            </label>
          </div>
        </div>
        <div data-bind="css: {'error': $root.design.results.save.targetTableError()}" class="control-group">
          <div class="controls">
            <label class="radio">
              <input data-bind="checked: $root.design.results.save.type" type="radio" name="save-results-type" value="hive-table">
              &nbsp;${ _('In a new table') }
            </label>
            <span data-bind="visible: $root.design.results.save.type() == 'hive-table'">
              <input data-bind="value: $root.design.results.save.path" type="text" name="target_table" class="span4" placeholder="${_('Table name or <database name>.<table name>')}">
            </span>
          </div>
        </div>
        <div data-bind="css: {'error': $root.design.results.save.targetDirectoryError()}" class="control-group hide advanced">
          <div class="controls">
            <label class="radio">
              <input data-bind="checked: $root.design.results.save.type" type="radio" name="save-results-type" value="hdfs-directory">
              &nbsp;${ _('Big Query in HDFS') }
            </label>
            <span data-bind="visible: $root.design.results.save.type() == 'hdfs-directory'">
              <input data-bind="value: $root.design.results.save.path" type="text" name="target_dir" placeholder="${_('Path to directory')}" class="folderChooser">
              <i class="fa fa-question-circle" id="hdfs-directory-help"></i>
            </span>
          </div>
        </div>
      </fieldset>
    </form>
    <div id="hdfs-directory-help-content" class="hide">
      <p>${ _("Use this option if you have a large result. It will rerun the entire query and save the results to the chosen HDFS directory.") }</p>
    </div>
  </div>
  <div class="modal-footer">
    <a id="save-results-advanced" href="javascript:void(0)" class="pull-left">${ _('Show advanced fields') }</a>
    <a id="save-results-simple" href="javascript:void(0)" class="pull-left hide">${ _('Hide advanced fields') }</a>
    <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
    <button data-bind="click: trySaveResults" class="btn btn-primary disable-feedback">${_('Save')}</button>
  </div>
</div>

<div id="navigatorQuicklook" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    % if has_metastore:
    <a class="tableLink pull-right" href="#" target="_blank" style="margin-right: 20px;margin-top:6px">
      <iclass="fa fa-external-link"></i> ${ _('View in Metastore Browser') }
    </a>
    % endif

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

<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
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

  #chooseFile, #chooseFolder, #choosePath {
    z-index: 1100;
  }

  #filechooser, #folderchooser, #pathchooser {
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

  .editable-empty, .editable-empty:hover {
    color: #666;
    font-style: normal;
  }

  #navigatorTables {
    margin: 4px;
  }

  #navigatorTables li div {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #navigatorSearch, #navigatorNoTables {
    display: none;
  }

  #navigatorNoTables {
    padding: 6px;
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
    z-index: 100;
  }

  .map {
    height: 200px;
  }

  #resultTable td, #resultTable th {
    white-space: nowrap;
  }

  .tab-content {
    min-height: 100px;
  }

  .columnType {
    text-align: right!important;
    color: #999;
  }

  #queryContainer {
    margin-bottom: 0;
  }

  #resizePanel a {
    position: absolute;
    cursor: ns-resize;
    color: #666;
    margin-left: auto;
    margin-right: auto;
  }

  .resultsContainer {
    margin-top: 20px;
  }

  #recentQueries {
    width: 100%;
  }

  #recentQueries code {
    cursor: pointer;
    white-space: normal;
  }

  #recentQueries tr td:first-child {
    white-space: nowrap;
  }

  #navigator .card-body {
    margin-top: 1px !important;
    padding: 6px !important;
  }

  #navigator .nav-header {
    padding-left: 0;
  }

  #navigator .control-group {
    padding-left: 0;
  }

  #navigator .nav-list > li.white, #navigator .nav-list .nav-header {
    margin: 0;
  }

  .jobs-overlay {
    background-color: #FFF;
    opacity: 0.8;
    position: absolute;
    top: 10px;
    right: 15px;
  }

  .jobs-overlay li {
    padding: 5px;
  }

  .jobs-overlay:hover {
    opacity: 1;
  }

  #saveResultsModal .overlay {
    background: black; opacity: 0.5;
    position: absolute;
    top: 0px;
    right:0px;
    left: 0px;
    bottom: 0px;
    z-index: 100;
  }

  #saveResultsModal .loader {
    text-align: center;
    position: absolute;
    top: 0px;
    right:0px;
    left: 0px;
    bottom: 0px;
  }

  #saveResultsModal i.fa-spinner, #saveResultsModal img.spinner {
    margin-top: -30px;
    margin-left: -30px;
    position: absolute;
    top: 50%;
    left: 50%;
    z-index: 101;
  }

  #saveResultsModal i.fa-spinner {
    font-size: 60px;
    color: #DDD;
  }

</style>

<link href="/static/ext/css/leaflet.css" rel="stylesheet">
<link href="/static/ext/css/hue-filetypes.css" rel="stylesheet">

<script src="/static/ext/js/jquery/plugins/jquery-fieldselection.js" type="text/javascript"></script>
<script src="/beeswax/static/js/autocomplete.utils.js" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
var codeMirror, renderNavigator, resetNavigator, resizeNavigator, dataTable, renderRecent;

var HIVE_AUTOCOMPLETE_BASE_URL = "${ autocomplete_base_url | n,unicode }";
var HIVE_AUTOCOMPLETE_FAILS_QUIETLY_ON = [500]; // error codes from beeswax/views.py - autocomplete
var HIVE_AUTOCOMPLETE_USER = "${ user }";

var HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK = function (data) {
  if (data != null && data.error) {
    resetNavigator();
  }
};

function placeResizePanelHandle() {
  // dynamically positioning the resize panel handle since IE doesn't play well with styles.
  $("#resizePanel a").css("left", $("#resizePanel").position().left + $("#resizePanel").width()/2 - 8);
}

function reinitializeTableExtenders() {
  $("#resultTable").jHueTableExtender({
     fixedHeader: true,
     includeNavigator: false
  });
  $("#recentQueries").jHueTableExtender({
     fixedHeader: true,
     includeNavigator: false
  });
}

var CURRENT_CODEMIRROR_SIZE = 100;

// Navigator, recent queries
$(document).ready(function () {

  var INITIAL_RESIZE_POSITION = 299;
  $("#resizePanel a").draggable({
    axis: "y",
    drag: function(e, ui) {
      draggableHelper($(this), e, ui);
      $(".jHueTableExtenderClonedContainer").hide();
    },
    stop: function(e, ui) {
      $(".jHueTableExtenderClonedContainer").show();
      draggableHelper($(this), e, ui);
      reinitializeTableExtenders();
    }
  });

  function draggableHelper(el, e, ui) {
    if (el.offset().top > INITIAL_RESIZE_POSITION){
      CURRENT_CODEMIRROR_SIZE = 100 + (el.offset().top - INITIAL_RESIZE_POSITION);
      codeMirror.setSize("99%", CURRENT_CODEMIRROR_SIZE);
    }
    if (ui.position.top < INITIAL_RESIZE_POSITION) {
      ui.position.top = INITIAL_RESIZE_POSITION;
    }
  }


  var recentQueries = $("#recentQueries").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "aoColumns": [
        { "sWidth" : "100px"},
        null,
        { "sWidth" : "80px", "bSortable": false },
        { "bSortable": false, "sWidth" : "4px" }
      ],
      "aaSorting": [
        [0, 'desc']
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sInfo": "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty": "${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered": "${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords": "${_('No matching records')}",
        "oPaginate": {
          "sFirst": "${_('First')}",
          "sLast": "${_('Last')}",
          "sNext": "${_('Next')}",
          "sPrevious": "${_('Previous')}"
        }
      }
    });

  renderRecent = function() {
    $("#recentLoader").show();
    recentQueries.fnClearTable();
    $.getJSON("${ url(app_name + ':list_query_history') }?format=json", function(data) {
      if (data && data.queries) {
        var _rows = [];
        $(data.queries).each(function(cnt, item){
          _rows.push([
            '<span data-time="' + item.timeInMs + '">' + item.timeFormatted + '</span>',
            '<code style="cursor:pointer">' + item.query + '</code>',
            (item.resultsUrl != "" ? '<a href="' + item.resultsUrl + '" data-row-selector-exclude="true">${_('See results...')}</a>': ''),
            (item.designUrl != "" ? '<a href="' + item.designUrl + '" data-row-selector="true">&nbsp;</a>': '')
          ]);
        });
        recentQueries.fnAddData(_rows);
      }
      $("a[data-row-selector='true']").jHueRowSelector();
      $("#recentLoader").hide();
      $("#recentQueries").css("width", "100%");
      reinitializeTableExtenders();
    });
  }

  $(document).on("click", "#recentQueries code", function(){
    codeMirror.setValue($(this).text());
  });

  renderRecent();

  $("#navigatorQuicklook").modal({
    show: false
  });

  $("#navigatorSearch").jHueDelayedInput(function(){
    $("#navigatorTables li").removeClass("hide");
    $("#navigatorTables li").each(function () {
      if ($(this).text().toLowerCase().indexOf($("#navigatorSearch").val().toLowerCase()) == -1) {
        $(this).addClass("hide");
      }
    });
  });

  $("#columnFilter").jHueDelayedInput(function(){
    $(".columnRow").removeClass("hide");
    $(".columnRow").each(function () {
      if ($(this).text().toLowerCase().indexOf($("#columnFilter").val().toLowerCase()) == -1) {
        $(this).addClass("hide");
      }
    });
  });

  resizeNavigator = function () {
    $("#navigator .card").css("min-height", ($(window).height() - 150) + "px");
    $("#navigatorTables").css("max-height", ($(window).height() - 280) + "px").css("overflow-y", "auto");
  }

  resetNavigator = function () {
    var _db = viewModel.database();
    if (_db != null) {
      $.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + _db, null);
      $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_tables_' + _db, null);
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
          var _metastoreLink = "";
          % if has_metastore:
            _metastoreLink = "<i class='fa fa-eye' title='" + "${ _('View in Metastore Browser') }" + "'></i>";
          % endif
          _table.html("<a href='javascript:void(0)' class='pull-right' style='padding-right:5px'><i class='fa fa-list' title='" + "${ _('Preview Sample data') }" + "' style='margin-left:5px'></i></a><a href='/metastore/table/" + viewModel.database() + "/" + table + "' target='_blank' class='pull-right hide'>" + _metastoreLink + "</a><div><a href='javascript:void(0)' title='" + table + "'><i class='fa fa-table'></i> " + table + "</a><ul class='unstyled'></ul></div>");

          _table.data("table", table).attr("id", "navigatorTables_" + table);
          _table.find("a:eq(2)").on("click", function () {
            _table.find(".fa-table").removeClass("fa-table").addClass("fa-spin").addClass("fa-spinner");
            hac_getTableColumns(viewModel.database(), table, "", function (plain_columns, extended_columns) {
              _table.find("a:eq(1)").removeClass("hide");
              _table.find("ul").empty();
              _table.find(".fa-spinner").removeClass("fa-spinner").removeClass("fa-spin").addClass("fa-table");
              $(extended_columns).each(function (iCnt, col) {
                var _column = $("<li>");
                _column.html("<a href='javascript:void(0)' style='padding-left:10px'" + (col.comment != null && col.comment != "" ? " title='" + col.comment + "'" : "") + "><i class='fa fa-columns'></i> " + col.name + ($.trim(col.type) != "" ? " (" + $.trim(col.type) + ")" : "") + "</a>");
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
            var tableUrl = "/${ app_name }/api/table/" + viewModel.database() + "/" + _table.data("table");
            $("#navigatorQuicklook").find(".tableName").text(table);
            $("#navigatorQuicklook").find(".tableLink").attr("href", "/metastore/table/" + viewModel.database() + "/" + table);
            $("#navigatorQuicklook").find(".sample").empty("");
            $("#navigatorQuicklook").attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");
            $.ajax({
              url: tableUrl,
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
      $(this).parent().parent().addClass("fullscreen");
    }
    else {
      $(this).find("i").addClass("fa-expand").removeClass("fa-compress");
      $(this).parent().parent().removeClass("fullscreen");
    }
    reinitializeTable();
  });

  renderNavigator();

  $("#refreshNavigator").on("click", function () {
    resetNavigator();
  });

  resizeNavigator();

  viewModel.databases.subscribe(function () {
    if ($.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_last_database") != null && $.inArray($.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_last_database"), viewModel.databases())) {
      viewModel.database($.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_last_database"));
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

  $(document).on("click", ".column-selector", function () {
    var _t = $("#resultTable");
    var _text = $.trim($(this).text().split("(")[0]);
    var _col = _t.find("th").filter(function() {
      return $.trim($(this).text()) == _text;
    });
    _t.find(".columnSelected").removeClass("columnSelected");
    _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
    $("a[href='#results']").click();
  });

  $(document).on("shown", "a[data-toggle='tab']:not(.sidetab)", function (e) {
    if ($(e.target).attr("href") == "#log") {
      logsAtEnd = true;
      window.setTimeout(resizeLogs, 150);
    }
    if ($(e.target).attr("href") == "#results" && $(e.relatedTarget).attr("href") == "#columns") {
      if ($("#resultTable .columnSelected").length > 0) {
        var _t = $("#resultTable");
        var _col = _t.find("th:nth-child(" + ($("#resultTable .columnSelected").index() + 1) + ")");
        _t.parent().animate({
          scrollLeft: _col.position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
        }, 300);
      }
    }
    if ($(e.target).attr("href") == "#results" || $(e.target).attr("href") == "#recentTab") {
      reinitializeTableExtenders();
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

function reinitializeTable(max) {
  var _max = max || 10;

  function fn(){
    var container = $($("a[data-toggle='tab']:not(.sidetab)").parent(".active").find("a").attr("href"));
    if ($("#results .dataTables_wrapper").height() > 0) {
      $("#results .dataTables_wrapper").jHueTableScroller({
        minHeight: $(window).height() - 150,
        heightAfterCorrection: 0
      });
      $("#recentTab .dataTables_wrapper").jHueTableScroller({
        minHeight: $(window).height() - 150,
        heightAfterCorrection: 0
      });
      reinitializeTableExtenders();
      container.height($("#results .dataTables_wrapper").height());
      $("#results .dataTables_wrapper").jHueScrollUp();
    } else if ($('#resultEmpty').height() > 0) {
      container.height($('#resultEmpty').height());
    } else if ($('#resultExpired').height() > 0) {
      container.height($('#resultExpired').height());
    }

    if ($("#results .dataTables_wrapper").data('original-height') == 0 && --_max != 0) {
      $("#results .dataTables_wrapper").data('original-height', $("#results .dataTables_wrapper").height());
      window.setTimeout(fn, 100);
    }

    if ($("#recentTab .dataTables_wrapper").data('original-height') == 0 && --_max != 0) {
      $("#recentTab .dataTables_wrapper").data('original-height', $("#recentTab .dataTables_wrapper").height());
      window.setTimeout(fn, 100);
    }
  }
  window.setTimeout(fn, 100);
}

$(document).ready(function () {
  $.jHueScrollUp();

  var queryPlaceholder = $("<span>").html($("<span>").html("${_('Example: SELECT * FROM tablename, or press CTRL + space')}").text()).text();

  $("#executeQuery").tooltip({
    title: '${_("Press \"tab\", then \"enter\".")}'
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
        resizeNavigator();
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
    if (data.indexOf("(") > -1){
      codeMirror.setCursor({line: from.line, ch: from.ch + data.length - 1});
      codeMirror.execCommand("autocomplete");
    }
    if (CodeMirror.tableFieldMagic) {
      codeMirror.replaceRange(" ", from, from);
      codeMirror.setCursor(from);
      codeMirror.execCommand("autocomplete");
    }
  };

  $(document).on("error.autocomplete", function(){
    $(".CodeMirror-spinner").remove();
  });

  function splitStatements(hql) {
    var statements = [];
    var current = "";
    var betweenQuotes = null;
    for (var i = 0, len = hql.length; i < len; i++) {
      var c = hql[i];
      current += c;
      if ($.inArray(c, ['"', "'"]) > -1) {
        if (betweenQuotes == c) {
          betweenQuotes = null;
        }
        else if (betweenQuotes == null) {
          betweenQuotes = c;
        }
      }
      else if (c == ";") {
        if (betweenQuotes == null) {
          statements.push(current);
          current = "";
        }
      }
    }

    if (current != "" && current != ";") {
      statements.push(current);
    }
    return statements;
  }

  function getStatementAtCursor() {
    var _pos = codeMirror.indexFromPos(codeMirror.getCursor());
    var _statements = splitStatements(codeMirror.getValue());
    var _cumulativePos = 0;
    var _statementAtCursor = "";
    var _relativePos = 0;
    for (var i = 0; i < _statements.length; i++) {
      if (_cumulativePos + _statements[i].length >= _pos && _statementAtCursor == "") {
        _statementAtCursor = _statements[i].split("\n").join(" ");
        _relativePos = _pos - _cumulativePos;
      }
      _cumulativePos += _statements[i].length;
    }
    return {
      statement: _statementAtCursor,
      relativeIndex: _relativePos
    };
  }

  CodeMirror.commands.autocomplete = function (cm) {
    $(document.body).on("contextmenu", function (e) {
      e.preventDefault(); // prevents native menu on FF for Mac from being shown
    });

    var pos = cm.cursorCoords();
    if ($(".CodeMirror-spinner").length == 0) {
      $("<i class='fa fa-spinner fa-spin CodeMirror-spinner'></i>").appendTo($("body"));
    }
    $(".CodeMirror-spinner").css("top", pos.top + "px").css("left", (pos.left - 4) + "px").show();

    if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + viewModel.database()) == null) {
      CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
      hac_getTables(viewModel.database(), function () {
      }); // if preload didn't work, tries again
    }
    else {
      hac_getTables(viewModel.database(), function (tables) {
        CodeMirror.catalogTables = tables;
        var _statementAtCursor = getStatementAtCursor();
        var _before = _statementAtCursor.statement.substr(0, _statementAtCursor.relativeIndex).replace(/;+$/, "");
        var _after = _statementAtCursor.statement.substr(_statementAtCursor.relativeIndex).replace(/;+$/, "");
        if ($.trim(_before).substr(-1) == ".") {
          var _statement = _statementAtCursor.statement;
          var _line = codeMirror.getLine(codeMirror.getCursor().line);
          var _partial = _line.substring(0, codeMirror.getCursor().ch);
          var _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length - 1);
          if (_statement.indexOf("FROM") > -1) {
            hac_getTableColumns(viewModel.database(), _table, _statement, function (columns) {
              var _cols = columns.split(" ");
              for (var col in _cols) {
                _cols[col] = "." + _cols[col];
              }
              CodeMirror.catalogFields = _cols.join(" ");
              CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
            });
          }
        }
        else {
          CodeMirror.possibleTable = false;
          CodeMirror.tableFieldMagic = false;
          if ((_before.toUpperCase().indexOf(" FROM ") > -1 || _before.toUpperCase().indexOf(" TABLE ") > -1 || _before.toUpperCase().indexOf(" STATS ") > -1) && _before.toUpperCase().indexOf(" ON ") == -1 && _before.toUpperCase().indexOf(" ORDER BY ") == -1 && _before.toUpperCase().indexOf(" WHERE ") == -1 ||
              _before.toUpperCase().indexOf("REFRESH") > -1 || _before.toUpperCase().indexOf("METADATA") > -1 || _before.toUpperCase().indexOf("DESCRIBE") > -1) {
            CodeMirror.possibleTable = true;
          }
          CodeMirror.possibleSoloField = false;
          if (_before.toUpperCase().indexOf("SELECT ") > -1 && _before.toUpperCase().indexOf(" FROM ") == -1 && !CodeMirror.fromDot) {
            if (_after.toUpperCase().indexOf("FROM ") > -1 || $.trim(_before).substr(-1) == "(") {
              fieldsAutocomplete(cm);
            }
            else {
              CodeMirror.tableFieldMagic = true;
              CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
            }
          }
          else {
            if ((_before.toUpperCase().indexOf("WHERE ") > -1 || _before.toUpperCase().indexOf("ORDER BY ") > -1) && !CodeMirror.fromDot && _before.toUpperCase().match(/ ON| LIMIT| GROUP| SORT/) == null) {
              fieldsAutocomplete(cm);
            }
            else {
              CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
            }
          }
        }
      });
    }
  }

  function fieldsAutocomplete(cm) {
    CodeMirror.possibleSoloField = true;
    try {
      var _value = getStatementAtCursor().statement;
      var _from = _value.toUpperCase().indexOf("FROM");
      if (_from > -1) {
        var _match = _value.toUpperCase().substring(_from).match(/ ON| LIMIT| WHERE| GROUP| SORT| ORDER BY|;/);
        var _to = _value.length;
        if (_match) {
          _to = _match.index;
        }
        var _found = _value.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
      }

      var _foundTable = "";
      for (var i = 0; i < _found.length; i++) {
        if ($.trim(_found[i]) != "" && _foundTable == "") {
          _foundTable = $.trim(_found[i]).split(" ")[0];
        }
      }
      if (_foundTable != "") {
        if (hac_tableHasAlias(_foundTable, _value)) {
          CodeMirror.possibleSoloField = false;
          CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
        }
        else {
          hac_getTableColumns(viewModel.database(), _foundTable, _value,
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
    % if app_name == 'impala':
    mode: "text/x-impalaql",
    % else:
    mode: "text/x-hiveql",
    % endif
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
          var _statement = getStatementAtCursor().statement;
          var _line = codeMirror.getLine(codeMirror.getCursor().line);
          var _partial = _line.substring(0, codeMirror.getCursor().ch);
          var _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length - 1);
          if (_statement.indexOf("FROM") > -1) {
            hac_getTableColumns(viewModel.database(), _table, _statement, function (columns) {
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
    viewModel.queryEditorBlank(true);
    clearErrorWidgets();
    $("#validationResults").empty();
  });

  % if not (design and design.id) and not ( query_history and query_history.id ):
    if ($.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_temp_query") != null && $.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_temp_query") != "") {
      viewModel.queryEditorBlank(true);
      codeMirror.setValue($.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_temp_query"));
    }
  % endif

  codeMirror.on("blur", function () {
    $(document.body).off("contextmenu");
  });

  codeMirror.on("update", function () {
    if (CURRENT_CODEMIRROR_SIZE == 100 && codeMirror.lineCount() > 7){
      CURRENT_CODEMIRROR_SIZE = 270;
      codeMirror.setSize("99%", CURRENT_CODEMIRROR_SIZE);
      reinitializeTableExtenders();
    }
  });

});

var editables = function() {
  // Edit query name and description.
  $("#query-name").editable({
    validate: function (value) {
      if ($.trim(value) == '') {
        return "${ _('This field is required.') }";
      }
    },
    success: function (response, newValue) {
      viewModel.design.name(newValue);
    },
    emptytext: "${ _('Query name') }"
  });

  $("#query-description").editable({
    success: function (response, newValue) {
      viewModel.design.description(newValue);
    },
    emptytext: "${ _('Empty description') }"
  });

  $(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
};

$(document).one('fetched.design', editables);

$(document).one('fetched.query', editables);

function isNumericColumn(type) {
  return $.inArray(type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE', 'TIMESTAMP_TYPE', 'DATE_TYPE']) > -1;
}

function isDateTimeColumn(type) {
  return $.inArray(type, ['TIMESTAMP_TYPE', 'DATE_TYPE']) > -1;
}

function isStringColumn(type) {
  return !isNumericColumn(type) && !isDateTimeColumn(type);
}

var map;
var graphHasBeenPredicted = false;
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

  $(document).on("shown", "a[data-toggle='tab']:not(.sidetab)", function (e) {
    if ($(e.target).attr("href") != "#results"){
      $($(e.target).attr("href")).css('height', 'auto');
      if ($(e.target).attr("href") == "#chart") {
        logGA('results/chart');
        predictGraph();
      }
      if ($(e.target).attr("href") == "#resultTab") {
        reinitializeTable();
      }
    } else {
      reinitializeTable();
    }
    return e;
  });


  function getMapBounds(lats, lngs) {
    lats = lats.sort();
    lngs = lngs.sort();
    return [
      [lats[lats.length - 1], lngs[lngs.length - 1]], // north-east
      [lats[0], lngs[0]] // south-west
    ]
  }

  function generateGraph(graphType) {
    $("#chart").height(Math.max($(window).height() - $("#blueprint").offset().top + 30, 500));
    $("#chart .alert").addClass("hide");
    if (graphType != "") {
      if (map != null){
        try {
          map.remove();
        }
        catch (err) {
          if (typeof console != "undefined") {
            console.error(err);
          }
        }
      }
      $("#blueprint").attr("class", "").attr("style", "").empty();
      $("#blueprint").data("plugin_jHueBlueprint", null);
      if (graphType == $.jHueBlueprint.TYPES.MAP) {
        L.DomUtil.get("blueprint")._leaflet = false;
        if ($("#blueprintLat").val() != "-1" && $("#blueprintLng").val() != "-1") {
          var _latCol = $("#blueprintLat").val() * 1;
          var _lngCol = $("#blueprintLng").val() * 1;
          var _descCol = $("#blueprintDesc").val() * 1;
          var _lats = [];
          var _lngs = [];
          $("#resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
            _lats.push($.trim($(this).text()) * 1);
          });
          $("#resultTable>tbody>tr>td:nth-child(" + _lngCol + ")").each(function (cnt) {
            _lngs.push($.trim($(this).text()) * 1);
          });
          $("#blueprint").height($("#blueprint").parent().height() - 100);
          try {
            map = L.map("blueprint").fitBounds(getMapBounds(_lats, _lngs));

            L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
              attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);

            $("#resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
              if (cnt < 1000) {
                if (_descCol != "-1") {
                  L.marker([$.trim($(this).text()) * 1, $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1]).addTo(map).bindPopup($.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _descCol + ")").text()));
                }
                else {
                  L.marker([$.trim($(this).text()) * 1, $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1]).addTo(map);
                }
              }
            });
          }
          catch (err) {
            if (typeof console != "undefined") {
              console.error(err);
            }
          }
          if ($("#resultTable>tbody>tr>td:nth-child(" + _latCol + ")").length > 1000){
            $("#chart .alert").removeClass("hide");
          }
        }
        else {
          $("#blueprint").addClass("empty").css("text-align", "center").text("${_("Please select the latitude and longitude columns.")}");
        }
      }
      else {
        if ($("#blueprintX").val() != "-1" && $("#blueprintY").val() != "-1") {
          var _x = $("#blueprintX").val() * 1;
          var _y = $("#blueprintY").val() * 1;
          var _data = [];
          $("#resultTable>tbody>tr>td:nth-child(" + _x + ")").each(function (cnt) {
            if (cnt < 1000) {
              _data.push([$.trim($(this).text()), $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _y + ")").text()) * 1]);
            }
          });
          if ($("#resultTable>tbody>tr>td:nth-child(" + _x + ")").length > 1000){
            $("#chart .alert").removeClass("hide");
          }
          $("#blueprint").jHueBlueprint({
            data: _data,
            label: $("#resultTable>thead>tr>th:nth-child(" + _y + ")").text(),
            type: graphType,
            color: $.jHueBlueprint.COLORS.BLUE,
            isCategories: true,
            fill: true,
            enableSelection: false,
            height: $("#blueprint").parent().height() - 100
          });
          if (_data.length > 30){
            $(".flot-x-axis .flot-tick-label").hide();
          }
        }
        else {
          $("#blueprint").addClass("empty").text("${_("Please select the columns you would like to see in this chart.")}");
        }
      }
    }
  }

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


  function predictGraph() {
    if (!graphHasBeenPredicted) {
      graphHasBeenPredicted = true;
      var _firstAllString, _firstAllNumeric;
      var _cols = viewModel.design.results.columns();
      $(_cols).each(function (cnt, col) {
        if (cnt > 0){
          if (_firstAllString == null && !isNumericColumn(col.type)) {
            _firstAllString = cnt + 1;
          }
          if (_firstAllNumeric == null && isNumericColumn(col.type)) {
            _firstAllNumeric = cnt + 1;
          }
        }
      });

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

  $("#log pre:eq(1)").scroll(function () {
    if ($(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight) {
      logsAtEnd = true;
    }
    else {
      logsAtEnd = false;
    }
  });

  viewModel.design.watch.logs.subscribe(function(val){
    var _logsEl = $("#log pre:eq(1)");

    if (logsAtEnd && _logsEl[0]) {
      _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
    }
    window.setTimeout(resizeLogs, 10);
  });

  viewModel.design.results.columns.subscribe(function(val){
    $("*[rel=columntooltip]").tooltip({
      delay: {show: 500}
    });
    $("a[data-row-selector='true']").jHueRowSelector();
  });
});

function resizeLogs() {
  // Use fixed subtraction since logs aren't always visible.
  if ($("#log pre:eq(1)").length > 0) {
    var _height = Math.max($(window).height() - $("#log pre:eq(1)").offset().top, 250);
    $("#log").height(_height - 10);
    $("#log pre:eq(1)").css("overflow", "auto").height(_height - 50);
  }
}

// Result Datatable
function cleanResultsTable() {
  if (dataTable) {
    dataTable.fnClearTable();
    dataTable.fnDestroy();
    viewModel.design.results.columns.valueHasMutated();
    viewModel.design.results.rows.valueHasMutated();
    dataTable = null;
  }
}

function addRowNumberToResults(data, startIndex) {
  var _tmpdata = [];
  $(data).each(function(cnt, item){
    item.unshift(cnt + startIndex);
    _tmpdata.push(item);
  });
  return _tmpdata;
}

function addResults(viewModel, dataTable, index, pageSize) {
  if (viewModel.hasMoreResults() && index + pageSize > viewModel.design.results.rows().length) {
    $(document).one('fetched.results', function () {
      $.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_temp_query", null);
      dataTable.fnAddData(addRowNumberToResults(viewModel.design.results.rows.slice(index, index + pageSize), index));
    });
    viewModel.fetchResults();
  } else {
    dataTable.fnAddData(addRowNumberToResults(viewModel.design.results.rows.slice(index, index + pageSize), index));
  }
}

function resultsTable(e, data) {
  if (!dataTable && viewModel.design.results.columns().length > 0) {
    dataTable = $("#resultTable").dataTable({
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
        reinitializeTableExtenders();
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
    $(viewModel.design.results.columns()).each(function(cnt, item){
      if (cnt > 0){
        _options += '<option value="'+(cnt + 1)+'">'+ item.name +'</option>';
      }
    });
    $(".blueprintSelect").html(_options);

    // Automatic results grower
    var dataTableEl = $("#results .dataTables_wrapper");
    var index = 0;
    var pageSize = 100;
    var _scrollTimeout = -1;
    dataTableEl.on("scroll", function (e) {
      var _lastScrollPosition = dataTableEl.data("scrollPosition") != null ? dataTableEl.data("scrollPosition") : 0;
      window.clearTimeout(_scrollTimeout);
      _scrollTimeout = window.setTimeout(function(){
        dataTableEl.data("scrollPosition", dataTableEl.scrollTop());
        if (_lastScrollPosition !=  dataTableEl.scrollTop() && dataTableEl.scrollTop() + dataTableEl.outerHeight() + 20 > dataTableEl[0].scrollHeight && dataTable) {
          dataTableEl.animate({opacity: '0.55'}, 200);
          addResults(viewModel, dataTable, index, pageSize);
          index += pageSize;
          dataTableEl.animate({opacity: '1'}, 50);
        }
      }, 100);
    });
    addResults(viewModel, dataTable, index, pageSize);
    index += pageSize;
    dataTableEl.jHueScrollUp();
  }
}

$(document).on('execute.query', cleanResultsTable);
$(document).on('explain.query', cleanResultsTable);
$(document).on('fetched.results', resultsTable);

var selectedLine = -1;
var errorWidgets = [];

function clearErrorWidgets() {
  $(".jHueTableExtenderClonedContainer").hide();
  $.each(errorWidgets, function(index, errorWidget) {
    errorWidget.clear();
  });
  errorWidgets = [];
}

$(document).on('execute.query', clearErrorWidgets);

$(document).on('error.query', function () {
  $.each(errorWidgets, function(index, el) {
    $(el).remove();
    errorWidgets = [];
  });

  // Move error to codeMirror if we know the line number
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

  reinitializeTableExtenders();
});


// Save
function trySaveDesign() {
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.design.query.value(query);
  if (viewModel.design.id() && viewModel.design.id() != -1) {
    viewModel.saveDesign();
    logGA('design/save');
  }
}

function saveAsModal() {
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.design.query.value(query);
  $('#saveAs').modal('show');
}

function trySaveAsDesign() {
  if (viewModel.design.query.value() && viewModel.design.name()) {
    viewModel.design.id(-1);
    viewModel.saveDesign();
    $('#saveas-query-name').removeClass('error');
    $('#saveAs').modal('hide');
    logGA('design/save-as');
  } else if (viewModel.design.name()) {
    $.jHueNotify.error("${_('No query provided to save.')}");
    $('#saveAs').modal('hide');
  } else {
    $('#saveas-query-name').addClass('error');
  }
}

function saveResultsModal() {
  $("#saveResultsModal .loader").hide();
  $('#saveResultsModal').modal('show');
}

function trySaveResults() {
  var deferred = viewModel.saveResults();
  if (deferred) {
    $("#saveResultsModal button.btn-primary").button('loading');
    $("#saveResultsModal .loader").show();
    deferred.done(function() {
      $("#saveResultsModal button.btn-primary").button('reset');
      $("#saveResultsModal .loader").hide();
    });
  }
  logGA('results/save');
}

$(document).on('saved.results', function() {
  $('#saveResultsModal').modal('hide');
});


// Querying and click events.
function tryExecuteQuery() {
  $(".jHueTableExtenderClonedContainer").hide();
  $(".tooltip").remove();
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.design.query.value(query);
  if ($("#results .dataTables_wrapper").length > 0) { // forces results to be up
    $("#results .dataTables_wrapper").scrollTop(0);
  }
  if ($("#recentQueries .dataTables_wrapper").length > 0) { // forces results to be up
    $("#recentQueries .dataTables_wrapper").scrollTop(0);
  }
  renderRecent();
  clickHard('.resultsContainer .nav-tabs a[href="#log"]');
  graphHasBeenPredicted = false;
  if (viewModel.design.isParameterized()) {
    viewModel.fetchParameters();
  } else {
    viewModel.executeQuery();
  }

  logGA('query/execute');
}

function tryExecuteNextStatement() {
  var query = getHighlightedQuery() || codeMirror.getValue();

  // If we highlight a part of query, we update the query and restart the query history
  // In the other case we update the query but continue at the same statement we were
  if (viewModel.design.query.value() != query) {
    viewModel.design.query.value(query);
    if (getHighlightedQuery()) {
      viewModel.executeQuery();
    } else {
      viewModel.executeNextStatement();
    }
  } else {
    viewModel.executeNextStatement();
  }

  logGA('query/execute_next');
}

function tryExecuteParameterizedQuery() {
  $(".tooltip").remove();
  viewModel.executeQuery();
  routie('query');
}

function tryExplainQuery() {
  $(".tooltip").remove();
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.design.query.value(query);
  viewModel.explainQuery();

  logGA('query/explain');
}

function tryExplainParameterizedQuery() {
  $(".tooltip").remove();
  viewModel.explainQuery();
  routie('query');
}

function tryCancelQuery() {
  $(".tooltip").remove();
  viewModel.cancelQuery();
}

function createNewQuery() {
  $.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_temp_query", null);
  location.href="${ url(app_name + ':execute_query') }";
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


// Server error handling.
$(document).on('server.error', function (e, data) {
  $(document).trigger('error', "${_('Server error occurred: ')}" + data.message ? data.message : data.error);
});
$(document).on('server.unmanageable_error', function (e, responseText) {
  $(document).trigger('error', "${_('Unmanageable server error occurred: ')}" + responseText);
});

// Other
$(document).on('saved.design', function (e, id) {
  $(document).trigger('info', "${_('Query saved.')}");
  window.location.href = "/${ app_name }/execute/design/" + id;
});
$(document).on('error_save.design', function (e, message) {
  var _message = "${_('Could not save design')}";
  if (message) {
    _message += ": " + message;
  }
  $(document).trigger('error', _message);
});
$(document).on('error_save.results', function (e, message) {
  var _message = "${_('Could not save results')}";
  if (message) {
    _message += ": " + message;
  }
  $(document).trigger('error', _message);
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
    'placement': 'left',
    'html': true
  });

  $("#hdfs-directory-help").popover({
    'title': "${_('Did you know?')}",
    'content': $("#hdfs-directory-help-content").html(),
    'trigger': 'hover',
    'placement': 'right',
    'html': true
  });

  $(document).on('click', '#save-results-simple', function() {
    $('#save-results-advanced').removeClass('hide');
    $('#save-results-simple').addClass('hide');
    $('#saveResultsForm .advanced').addClass('hide');
  });
  $(document).on('click', '#save-results-advanced', function() {
    $('#save-results-advanced').addClass('hide');
    $('#save-results-simple').removeClass('hide');
    $('#saveResultsForm .advanced').removeClass('hide');
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
});

% if app_name == 'impala':
$(document).ready(function () {
  $("#downloadQuery").click(function () {
    $("<input>").attr("type", "hidden").attr("name", "button-submit").attr("value", "Execute").appendTo($("#advancedSettingsForm"));
    $("<input>").attr("type", "hidden").attr("name", "download").attr("value", "true").appendTo($("#advancedSettingsForm"));
    tryExecuteQuery();
  });

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
});
% endif

% if ( app_name == 'beeswax' and beeswax_conf.CLOSE_QUERIES.get() ) or ( app_name == 'impala' and impala_conf.CLOSE_QUERIES.get() ):
$(document).ready(function () {
  $(document).on('explain.query', function() {
    viewModel.closeQuery();
  });

  $(document).on('execute.query', function() {
    viewModel.closeQuery();
  });

  // Tricks for not triggering the closing of the query on download
  $("a.download").hover(function(){
      window.onbeforeunload = null;
    },function() {
      window.onbeforeunload = $(window).data('beforeunload');
    }
  );
});

// Close the query when leaving the page, backup for later when disabling the close before downloading results.
window.onbeforeunload = function(e) {
  viewModel.closeQuery();
};
$(window).data('beforeunload', window.onbeforeunload);

% endif

$(".folderChooser:not(:has(~ button))").after(getFolderBrowseButton($(".folderChooser:not(:has(~ button))"), true));
$(".pathChooser:not(:has(~ button))").after(getPathBrowseButton($(".pathChooser:not(:has(~ button))"), true));


// Routie
$(document).ready(function () {
  function queryPageComponents() {
    $('#advanced-settings').show();
    $('#navigator').show();
    $('#queryContainer').show();
    $('#resizePanel').show();
    $('a[href="#query"]').parent().show();
    if (!$('#querySide').hasClass('span10')) {
      $('#querySide').addClass('span10');
    }
  }

  function watchPageComponents() {
    $('#advanced-settings').hide();
    $('#navigator').hide();
    $('#queryContainer').hide();
    $('#resizePanel').hide();
    $('a[href="#query"]').parent().hide();
    $('a[href="#recentTab"]').parent().hide();
    if ($('#querySide').hasClass('span10')) {
      $('#querySide').removeClass('span10');
    }
  }

  function queryPage() {
    queryPageComponents();
    $('.resultsContainer .watch-query').hide();
    $('.resultsContainer .view-query-results').hide();
  }

  function queryLogPage() {
    queryPageComponents();
    $('.resultsContainer .watch-query').show();
    $('.resultsContainer .view-query-results').hide();
  }

  function queryResultsPage() {
    queryPageComponents();
    $('.resultsContainer .watch-query').hide();
    $('.resultsContainer .view-query-results').show();
  }

  function parametersPage() {
    queryPageComponents();
    $('.resultsContainer .watch-query').hide();
    $('.resultsContainer .view-query-results').hide();
  }

  function watchLogsPage() {
    watchPageComponents();
    $('.resultsContainer .watch-query').show();
    $('.resultsContainer .view-query-results').hide();
  }

  function watchResultsPage() {
    watchPageComponents();
    $('.resultsContainer .watch-query').hide();
    $('.resultsContainer .view-query-results').show();
  }

  routie({
    'query': function () {
      showSection('query-editor');
      queryPage();
      codeMirror.setSize("99%", CURRENT_CODEMIRROR_SIZE);
      placeResizePanelHandle();
    },
    'query/execute/params': function () {
      if (viewModel.design.parameters().length == 0) {
        routie('query');
      }

      showSection('execute-parameter-selection');
      parametersPage();
    },
    'query/explain/params': function () {
      if (viewModel.design.parameters().length == 0) {
        routie('query');
      }

      showSection('explain-parameter-selection');
      parametersPage();
    },
    'query/logs': function () {
      if (viewModel.design.watch.logs().length == 0 && viewModel.design.watch.errors().length == 0) {
        routie('query');
      }

      showSection('query-editor');
      queryLogPage();

      clickHard('.resultsContainer .nav-tabs a[href="#log"]');
    },
    'query/results': function () {
      showSection('query-editor');
      queryResultsPage();

      clickHard('.resultsContainer .nav-tabs a[href="#results"]');

      renderRecent();
      placeResizePanelHandle();

      logGA('query/results');
    },
    'query/explanation': function () {
      if (! viewModel.design.results.explanation()) {
        routie('query');
      }

      showSection('query-editor');
      queryResultsPage();

      clickHard('.resultsContainer .nav-tabs a[href="#explanation"]');
    },
    'watch/logs': function() {
      showSection('query-editor');
      watchLogsPage();

      clickHard('.resultsContainer .nav-tabs a[href="#log"]');

      logGA('watch/logs');
    },
    'watch/results': function() {
      showSection('query-editor');
      watchResultsPage();

      clickHard('.resultsContainer .nav-tabs a[href="#results"]');

      logGA('watch/results');
    },
    '*': function () {
      routie('query');
    }
  });
});


// Event setup
function queryEvents() {
  $(document).on('fetched.parameters', function () {
    if (viewModel.design.parameters().length > 0) {
      routie('query/execute/params');
    } else {
      viewModel.executeQuery();
    }
  });
  $(document).on('explained.query', function () {
    routie('query/explanation');
  });
  $(document).on('watched.query', function (e, data) {
    if (data.status != 2) {
      if (data.status && data.status && data.status != 0) {
        viewModel.design.watch.errors.push(data.error || data.message);
      }
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
  $(document).ready(function() {
    routie('query');
  });
}

function watchEvents() {
  $(document).ready(function() {
    routie('watch/logs');
  });
  $(document).on('error_watch.query', function () {
    routie('watch/logs');
  });
  $(document).on('fetched.results', function () {
    routie('watch/results');
  });
}

function cacheQueryTextEvents() {
  codeMirror.on("change", function () {
    $(".query").val(codeMirror.getValue());
    $.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_temp_query", codeMirror.getValue());
  });
}

function databaseCacheWriter() {
  $(".chosen-select").chosen().change(function () {
    $.totalStorage(hac_getTotalStorageUserPrefix() + "${app_name}_last_database", viewModel.database());
  });
}

function loadEditor() {
  $(document).one('fetched.databases', databaseCacheWriter);
  viewModel.fetchDatabases();
}

function loadDesign(design_id) {
  $(document).one('fetched.databases', function() {
    viewModel.design.id(design_id);
    viewModel.fetchDesign();
  });

  $(document).one('fetched.design', databaseCacheWriter);

  var codeMirrorSubscription = viewModel.design.query.value.subscribe(function(value) {
    viewModel.queryEditorBlank(true);
    codeMirror.setValue(value);
    codeMirrorSubscription.dispose();
  });

  loadEditor();
}

function loadQueryHistory(query_history_id) {
  $(document).one('fetched.databases', function() {
    viewModel.design.history.id(query_history_id);
    viewModel.fetchQueryHistory();
  });

  $(document).one('fetched.query', databaseCacheWriter);

  var codeMirrorSubscription = viewModel.design.query.value.subscribe(function(value) {
    viewModel.queryEditorBlank(true);
    codeMirror.setValue(value);
    codeMirrorSubscription.dispose();
  });

  loadEditor();
}

// Knockout
viewModel = new BeeswaxViewModel("${app_name}");
% if query_history:
  loadQueryHistory(${query_history.id});
% elif design.id:
  loadDesign(${design.id});
% else:
  $(document).ready(cacheQueryTextEvents);
  loadEditor();
% endif
viewModel.design.fileResources.values.subscribe(function() {
  // File chooser button for file resources.
  $(".fileChooser:not(:has(~ button))").after(getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
});
ko.applyBindings(viewModel);


% if action == 'watch-results':
  $(document).ready(watchEvents);
  $(document).one('fetched.query', function(e) {
    viewModel.watchQueryLoop();
    cacheQueryTextEvents();
  });
% elif action == 'watch-redirect':
  $(document).ready(watchEvents);
  $(document).one('fetched.query', function(e) {
    viewModel.watchQueryLoop();
    cacheQueryTextEvents();
  });
  $(document).on('stop_watch.query', function(e) {
    if (viewModel.design.results.errors().length == 0) {
      window.location.href = "${request.GET['on_success_url']}";
    }
  });
% elif action == 'editor-results':
  $(document).ready(queryEvents);
  $(document).one('fetched.query', function(e) {
    viewModel.watchQueryLoop();
    cacheQueryTextEvents();
  });
% elif action == 'editor-expired-results':
  $(document).ready(queryEvents);
  $(document).one('fetched.query', function(e) {
    viewModel.design.results.expired(true);
    $(document).trigger('fetched.results', [ [] ]);
    cacheQueryTextEvents();
  });
% else:
  $(document).ready(queryEvents);
% endif

</script>

${ commonfooter(messages) | n,unicode }

