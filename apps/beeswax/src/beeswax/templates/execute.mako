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
  from desktop.views import commonheader, commonfooter, commonshare, _ko
  from beeswax import conf as beeswax_conf
  from desktop import conf
  from desktop.conf import USE_NEW_EDITOR
  from django.utils.translation import ugettext as _
  from notebook.conf import ENABLE_QUERY_BUILDER
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Query'), app_name, user, request) | n,unicode }
${ layout.menubar(section='query') }

<div id="temporaryPlaceholder"></div>
<div id="beeswax-execute">
  <div id="query-editor" class="container-fluid hide section">
  <div class="panel-container">
  <div class="left-panel" id="navigator">
    <ul class="nav nav-tabs" style="margin-bottom: 0">
      <li class="active"><a href="#navigatorTab" data-toggle="tab" class="sidetab">${_('Assist')}</a></li>
      <li><a href="#settingsTab" data-toggle="tab" class="sidetab">${_('Settings')} <span data-bind="visible:design.settings.values().length + design.fileResources.values().length + design.functions.values().length > 0, text: design.settings.values().length + design.fileResources.values().length + design.functions.values().length" class="badge badge-info">12</span></a></li>
      % if app_name == 'impala':
      <li><a href="#sessionTab" data-toggle="tab" class="sidetab">${_('Session')}</a></li>
      % endif
    </ul>
    <div class="tab-content" style=" overflow: hidden;">
      <div class="tab-pane active" id="navigatorTab">
        <div class="card card-small card-tab" style="margin-bottom: 0;">
          <div class="card-body" style="margin-top: 0; height: 100%;">
            <div class="assist" data-bind="component: {
              name: 'assist-panel',
              params: {
                user: HIVE_AUTOCOMPLETE_USER,
                onlySql: true,
                sql: {
                  sourceTypes: editorViewModel.sqlSourceTypes,
                  activeSourceType: snippetType,
                  navigationSettings: {
                    openItem: false,
                    showPreview: true,
                    showStats: true
                  }
                },
                visibleAssistPanels: ['sql']
              }
            }"></div>
          </div>
        </div>
      </div>
      <div class="tab-pane" id="settingsTab">
        <div class="card card-small card-tab">
          <div class="card-body" style="overflow-y: auto; height: 100%;">
            <div id="advanced-settings">
            <form id="advancedSettingsForm" action="" method="POST" class="form form-horizontal">
                ${ csrf_token(request) | n,unicode }
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
                        <input data-bind="value: key" type="text" class="settingsField" autocomplete="off" placeholder="${ 'impala.resultset.cache.size' if app_name == 'impala' else 'mapred.reduce.tasks' }"/>
                      </div>

                      <div data-bind="css: {'error': $root.getSettingValueErrors($index()).length > 0}" class="control-group">
                        <label>${_('Value')}</label>
                        <input data-bind="value: value" type="text" class="settingValuesField" placeholder="${ '5000' if app_name == 'impala' else '1' }"/>
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
                        <input data-bind="value: path" type="text" class="filesField fileChooser" placeholder="/user/foo/udf.jar"/>
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
                        <input data-bind="value: name" type="text" class="functionsField" autocomplete="off" placeholder="myFunction"/>
                      </div>

                      <div data-bind="css: {'error': $root.getFunctionClassNameErrors($index()).length > 0}" class="control-group">
                        <label>${_('Class name')}</label>
                        <input data-bind="value: class_name" type="text" class="classNamesField" placeholder="com.acme.example"/>
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
      % if app_name == 'impala':
      <div class="tab-pane" id="sessionTab">
        <div class="card card-small card-tab">
          <div class="card-body">
            <!-- ko if: $root.fetchingImpalaSession() -->
            <div style="margin: 5px">
              <i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i>
            </div>
            <!-- /ko -->

            <!-- ko ifnot: $root.fetchingImpalaSession() -->
              <!-- ko if: $root.impalaSessionLink() != '' -->
              <ul class="nav nav-list" style="border: none; padding: 0;">
                <li class="nav-header">${ _('address')}</li>
              </ul>
              <div style="margin: 2px">
              <a data-bind="attr: {'href': $root.impalaSessionLink()}" target="_blank"><span data-bind="text: $root.impalaSessionLink().replace(/^(https?):\/\//, '')"></span> <i class="fa fa-external-link"></i></a>
              </div>
              <!-- /ko -->
              <!-- ko if: $root.impalaSessionLink() == '' -->
              <div style="margin: 5px">
                ${ _("There's currently no valid session") }
              </div>
              <!-- /ko -->
            <!-- /ko -->
          </div>
        </div>
      </div>
      % endif
    </div>
  </div>
  <div class="resizer" data-bind="splitDraggable : { appName: '${app_name}', onPosition: onPanelPosition, leftPanelVisible: isEditor }"><div class="resize-bar"><i class="fa fa-ellipsis-v"></i></div></div>
  <div class="content-panel" id="querySide">
    % if USE_NEW_EDITOR.get() and action != 'watch-redirect' and action != 'watch-results':
    <div class="alert">
      ${ _('This is the old SQL Editor, it is recommended to instead use: ') }
      % if app_name == 'impala':
        <a href="/hue/editor?type=impala" target="_blank">${_('Impala')}</a>
      % else:
        <a href="/hue/editor?type=hive" target="_blank">${_('Hive')}</a>
      % endif
    </div>
    % endif
    <div class="alert" data-bind="visible: design.isRedacted">
      ${ _('This query had some sensitive information removed when saved.') }
    </div>
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
            <a class="share-link" rel="tooltip" data-placement="bottom" style="padding-left:10px; padding-right: 10px" data-bind="click: openShareModal,
              attr: {'data-original-title': '${ _ko("Share") } '+name},
              css: {'baseShared': true, 'isShared': isShared()}">
              <i class="fa fa-users"></i>
            </a>
            <a href="javascript:void(0);"
               id="query-name"
               data-type="text"
               data-name="name"
               data-value="${design.name}"
               data-original-title="${ _('Query name') }"
               data-placement="right">
            </a>
            <br />
            <div style="display: inline-block; margin: 0 10px 0 46px; line-height: 20px; ">
              <a href="javascript:void(0);"
                 id="query-description"
                 data-type="textarea"
                 data-name="description"
                 data-value="${design.desc}"
                 data-original-title="${ _('Query description') }"
                 data-placement="bottom"
                 style="font-size: 14px; line-height: 20px; white-space: normal; " >
              </a>
            </div>
          </h1>
          %endif
      </div>
      <div class="card-body">
        <div class="tab-content">
          <div id="queryPane">

            <div data-bind="css: {'hide': design.errors().length == 0 || design.inlineErrors().length > 0}" class="alert alert-error">
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

            <div data-bind="css: {'hide': design.watch.errors().length == 0 || design.watch.inlineErrors().length > 0}" class="alert alert-error">
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
              <button data-bind="click: formatQuery" type="button" class="btn">${_('Format')}</button>
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
      <div class="query-right-actions" data-bind="visible: !design.explain()">
        <!-- ko if: $root.hasResults() -->
        <a id="expandResults" href="javascript:void(0)" title="${_('See results in full screen')}" rel="tooltip"
          class="view-query-results hide pull-right"><h4><i class="fa fa-expand"></i></h4></a>

        <a id="save-results" data-bind="click: saveResultsModal" href="javascript:void(0)" title="${_('Save the results to HDFS or a new Hive table')}" rel="tooltip"
          class="view-query-results hide pull-right"><h4><i class="fa fa-save"></i></h4>
        </a>

        ## Tricks for not triggering the closing of the query on download
        <a id="download-csv" data-bind="attr: {'href': '/${ app_name }/download/' + $root.design.history.id() + '/csv'}, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }" href="javascript:void(0)" title="${_('Download the results in CSV format')}" rel="tooltip"
          class="view-query-results download hide pull-right"><h4><i class="hfo hfo-file-csv"></i></h4>
        </a>

        <a id="download-excel" data-bind="attr: {'href': '/${ app_name }/download/' + $root.design.history.id() + '/xls'}, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }" href="javascript:void(0)" title="${_('Download the results in XLS format')}" rel="tooltip"
          class="view-query-results download hide pull-right"><h4><i class="hfo hfo-file-xls"></i></h4></a>
        <!-- /ko -->
        <a href="#clearHistoryModal" title="${_('Clear the query history')}" rel="tooltip" class="clear-queries pull-right" data-toggle="modal"><h4><i class="fa fa-calendar-times-o"></i></h4></a>
      </div>

      <div class="card-body">
        <ul class="nav nav-tabs">
          <li class="active recentLi"><a href="#recentTab" data-toggle="tab">${_('Recent queries')}</a></li>
          <li><a href="#query" data-toggle="tab">${_('Query')}</a></li>
          %if ENABLE_QUERY_BUILDER.get():
          <li><a href="#queryBuilderTab" data-toggle="tab">${_('Query builder')}</a></li>
          %endif
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
              <i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #DDD"></i>
            </div>
            <table id="recentQueries" class="table table-condensed datatables" cellpadding="0" cellspacing="0" data-tablescroller-enforce-height="true">
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
          %if ENABLE_QUERY_BUILDER.get():
          <div class="tab-pane" id="queryBuilderTab">
            <div id="queryBuilderAlert" style="display: none" class="alert">${ _('There are currently no rules defined. To get started, right click on any table column in the SQL Assist panel.') }</div>
            <table id="queryBuilder" class="table table-condensed">
              <thead>
                <tr>
                  <th width="10%">${ _('Table') }</th>
                  <th>${ _('Column') }</th>
                  <th width="10%">${ _('Operation') }</th>
                  <th width="5%">&nbsp;</th>
                  <th width="1%">&nbsp;</th>
                </tr>
              </thead>
            </table>
            <div class="button-panel">
              <button class="btn btn-primary disable-feedback" onclick="generateQuery()">${_('Build query')}</button>
            </div>
          </div>
          %endif

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
              <pre data-bind="visible: $root.design.watch.logs().length == 0">${_('There are currently no logs to visualize.')} <img src="${ static('desktop/art/spinner.gif') }" alt="${ _('Spinner') }" data-bind="visible: $root.design.isRunning()"/></pre>
              <pre data-bind="visible: $root.design.watch.logs().length > 0, text: $root.design.watch.logs().join('\n')"></pre>
            </div>
          </div>

          <div class="tab-pane" id="columns">
            <pre data-bind="visible: $root.design.results.columns().length == 0">${_('There are currently no columns to visualize.')}</pre>
            <div data-bind="visible: $root.design.results.columns().length > 10">
              <input id="columnFilter" class="input-xlarge" type="text" placeholder="${_('Filter for column name or type...')}" />
            </div>
            <table class="table table-condensed" cellpadding="0" cellspacing="0">
              <tbody data-bind="foreach: $root.design.results.columns">
                <tr class="columnRow" data-bind="visible: $index() > 0">
                  <td rel="columntooltip" data-placement="left" data-bind="attr: {title: '${ _ko("Scroll to the column") }">
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
              <table id="resultTable" class="table table-condensed" cellpadding="0" cellspacing="0" data-tablescroller-enforce-height="true">
                <thead>
                <tr data-bind="foreach: $root.design.results.columns">
                  <th data-bind="html: ($index() == 0 ? '&nbsp;' : $data.name), css: { 'sort-numeric': isNumericColumn($data.type), 'sort-date': isDateTimeColumn($data.type), 'sort-string': isStringColumn($data.type), 'datatables-counter-col': $index() == 0}"></th>
                </tr>
                </thead>
              </table>
              % if app_name == 'impala':
              <a class="pointer" data-bind="visible: $root.scrollNotWorking() && $root.hasMoreResults(), click: manualFetch" style="padding: 10px">${ _('Show more results...') }</a>
              % endif
            </div>

            <div data-bind="css: {'hide': !$root.design.results.empty() || $root.design.results.expired()}" id="resultEmpty">
              <pre>${_('The operation has no results.')}</pre>
            </div>

            <div data-bind="css: {'hide': !$root.design.results.expired()}" id="resultExpired">
              <pre>${_('The results have expired, rerun the query if needed.')}</pre>
            </div>
          </div>

          <div class="tab-pane" id="chart">
            <pre data-bind="visible: $root.design.results.empty() || $root.design.results.expired()">${_('There is currently no data to build a chart on.')}</pre>
            <div class="alert hide">
              <strong>${_('Warning:')}</strong> ${_('the results on the chart have been limited to 1000 rows.')}
            </div>

            <div data-bind="visible: ! $root.design.results.empty() && ! $root.design.results.expired()" style="text-align: center">
            <form class="form-inline">
              ${_('Chart type')}&nbsp;
              <div class="btn-group" data-toggle="buttons-radio">
                <a rel="tooltip" data-placement="top" title="${_('Bars')}" id="blueprintBars" href="javascript:void(0)" class="btn"><i class="hcha hcha-bar-chart"></i></a>
                <a rel="tooltip" data-placement="top" title="${_('Lines')}" id="blueprintLines" href="javascript:void(0)" class="btn"><i class="hcha hcha-line-chart"></i></a>
                <a rel="tooltip" data-placement="top" title="${_('Pie')}" id="blueprintPie" href="javascript:void(0)" class="btn"><i class="hcha hcha-pie-chart"></i></a>
                <a rel="tooltip" data-placement="top" title="${_('Map')}" id="blueprintMap" href="javascript:void(0)" class="btn"><i class="hcha hcha-map-chart"></i></a>
              </div>&nbsp;&nbsp;
              <span id="blueprintAxis" class="hide">
                <label>${_('X-Axis')}
                  <select id="blueprintX" class="blueprintSelect"></select>
                </label>&nbsp;&nbsp;
                <label>${_('Y-Axis')}
                <select id="blueprintY" class="blueprintSelect"></select>
                </label>&nbsp;
                <div class="btn-group" data-toggle="buttons-radio">
                  <a rel="tooltip" data-placement="top" title="${_('No sorting')}" id="blueprintNoSort" href="javascript:void(0)" class="btn active"><i class="fa fa-align-left fa-rotate-270"></i></a>
                  <a rel="tooltip" data-placement="top" title="${_('Sort ascending')}" id="blueprintSortAsc" href="javascript:void(0)" class="btn"><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
                  <a rel="tooltip" data-placement="top" title="${_('Sort descending')}" id="blueprintSortDesc" href="javascript:void(0)" class="btn"><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
                </div>&nbsp;&nbsp;
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
            <div data-bind="visible: ! $root.design.results.empty() && ! $root.design.results.expired()" id="blueprint" class="empty center">${_("Please select a chart type.")}</div>
            <div style="margin: 10px" data-bind="visible: ! $root.design.results.empty() && ! $root.design.results.expired()">
              <div id="pieChart" data-bind="pieChart: {data: {counts: $root.chartData}, fqs: ko.observableArray([]),
                transformer: pieChartDataTransformer,
                maxWidth: 350 }, visible: $root.chartType() == 'pie'"></div>

              <div id="barChart" data-bind="barChart: {datum: {counts: $root.chartData}, fqs: ko.observableArray([]), hideSelection: true,
                    transformer: barChartDataTransformer}, visible: $root.chartType() == 'bars'"></div>

              <div id="lineChart" data-bind="lineChart: {datum: {counts: $root.chartData},
                    transformer: lineChartDataTransformer,
                    showControls: false }, visible: $root.chartType() == 'lines'"></div>

              <div id="leafletMapChart" data-bind="leafletMapChart: {datum: {counts: $root.chartData},
                    transformer: leafletMapChartDataTransformer,
                    showControls: false }, visible: $root.chartType() == 'map'"></div>
            </div>
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
            ${ csrf_token(request) | n,unicode }
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
            ${ csrf_token(request) | n,unicode }
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


  <div id="chooseFolder" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Select a directory') }</h2>
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
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Select a file or directory') }</h2>
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
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Choose a name') }</h2>
    </div>
    <form class="form-horizontal">
      <div class="control-group" id="saveas-query-name">
        <label class="control-label">${_('Name')}</label>
        <div class="controls">
          <input data-bind="value: $root.design.name, html" type="text" class="input-xlarge">
          <span class="help-inline"></span>
        </div>
      </div>
      <div class="control-group" id="saveas-query-description">
        <label class="control-label">${_('Description')}</label>
        <div class="controls">
          <input data-bind="value: $root.design.description, html" type="text" class="input-xlarge">
          <span class="help-inline"></span>
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
      <i class="fa fa-spinner fa-spin"></i>
    </div>

    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Save Query Results') }</h2>
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
        ${ csrf_token(request) | n,unicode }
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
      % if app_name != 'impala':
      <a id="save-results-advanced" href="javascript:void(0)" class="pull-left">${ _('Show advanced fields') }</a>
      % endif
      <a id="save-results-simple" href="javascript:void(0)" class="pull-left hide">${ _('Hide advanced fields') }</a>
      <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
      <button data-bind="click: trySaveResults" class="btn btn-primary disable-feedback">${_('Save')}</button>
    </div>
  </div>
</div>


<div id="clearHistoryModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Confirm History Clear') }</h2>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to clear the query history?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger disable-feedback" onclick="viewModel.clearQueryHistory()">${_('Yes')}</a>
  </div>
</div>

%if ENABLE_QUERY_BUILDER.get():
<div id="invalidQueryBuilder" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ _('Invalid Query') }</h2>
  </div>
  <div class="modal-body">
    <p>${_('Query requires a select or an aggregate.')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>
%endif

${ commonshare() | n,unicode }

<script>
  var SqlAutocompleter2 = {};
</script>

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>

${ assist.assistJSModels() }

<script src="${ static('beeswax/js/beeswax.vm.js') }"></script>
<script src="${ static('desktop/js/share.vm.js') }"></script>
%if ENABLE_QUERY_BUILDER.get():
<!-- For query builder -->
<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.contextMenu.min.css') }">
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.contextMenu.min.js') }"></script>
<script src="${ static('desktop/js/queryBuilder.js') }"></script>
<script>
  // query-builder-menu is the class to use
  // Callback will run after each rule add, just focus to the queryBuilder tab
  QueryBuilder.bindMenu('.query-builder-menu', function () {
    $("a[href='#queryBuilderTab']").click();
  });
  function generateQuery() {
    var result = QueryBuilder.buildHiveQuery();
    if (result.status == "fail") {
      $("#invalidQueryBuilder").modal("show");
    } else {
      codeMirror.setValue(result.query);
      codeMirror.focus();
    }
  }

  window.setInterval(function(){
    if ($('#queryBuilder tbody').length > 0 && $('#queryBuilder tbody').find('tr').length > 0){
      $('.button-panel').show();
      $('#queryBuilder').show();
      $('#queryBuilderAlert').hide();
    }
    else {
      $('.button-panel').hide();
      $('#queryBuilder').hide();
      $('#queryBuilderAlert').show();
    }
  }, 500);

</script>

<!-- End query builder imports -->
%endif

<script src="${ static('desktop/ext/js/codemirror-3.11.js') }"></script>
<link rel="stylesheet" href="${ static('desktop/ext/css/codemirror.css') }">
<script src="${ static('desktop/js/codemirror-hql.js') }"></script>
% if app_name == 'impala':
  <script src="${ static('desktop/js/codemirror-isql-hint.js') }"></script>
% else:
  <script src="${ static('desktop/js/codemirror-hql-hint.js') }"></script>
% endif
<script src="${ static('desktop/js/codemirror-show-hint.js') }"></script>

<link href="${ static('desktop/ext/css/bootstrap-editable.css') }" rel="stylesheet">

<script src="${ static('beeswax/js/stats.utils.js') }"></script>

${ assist.assistPanel() }

<style type="text/css">
  h1 {
    margin-bottom: 5px;
  }

  .panel-container {
    width: 100%;
    position: relative;
  }

  .left-panel {
    position: fixed !important;
    z-index: 1030;
    outline: none !important;
  }

  .mega-popover .popover-content {
    min-height: 190px !important;
  }

  .mega-popover .content {
    height: auto !important;
    max-height: 280px;
  }

  .resizer {
    position: fixed !important;
    margin-left: 15px;
    width: 20px;
    text-align: center;
    z-index: 1000;
  }

  .resize-bar {
    top: 50%;
    position: relative;
    cursor: ew-resize;
  }

  .content-panel {
    position: absolute;
    outline: none !important;
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

  .table-actions {
    position: absolute;
    right: 0;
    padding-left: 3px;
    background-color: #FFF;
  }

  .preview-data {
    margin-right: 5px;
  }

  .remove {
    float: right;
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

  .tooltip.left {
    margin-left: -13px;
  }

  .fullscreen {
    position: fixed;
    top: -16px;
    left: 0;
    width: 100%;
    background-color: #FFFFFF;
    z-index: 2000;
  }

  body.fullscreen {
    overflow: hidden;
  }

  .map {
    height: 200px;
  }

  #resultTable td, #resultTable th {
    white-space: nowrap;
    border-right: 1px solid #e5e5e5;
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

  .table-container {
    margin-right:10px;
  }

  #navigator .card-body {
    margin-top: 1px !important;
    padding: 7px !important;
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

  .tooltip {
    z-index: 10001;
  }

  .filesField, .functionsField, .classNamesField, .settingsField, .settingValuesField {
    width: 60%;
  }

  .fileChooser, .folderChooser {
    border-radius: 3px 0 0 3px !important;
    border-right: 0 !important;
  }

  .pull-right.hover-actions, .pull-right.blue {
    margin-top: -4px;
  }

  .query-right-actions {
    margin-right: 10px;
  }

  .query-right-actions h4 {
    padding: 0 10px;
  }
</style>

<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">

<script src="${ static('desktop/ext/js/jquery/plugins/jquery-fieldselection.js') }" type="text/javascript"></script>

<script type="text/javascript">

// avoid blinking of the panels
var leftPanelWidth = $.totalStorage("${app_name}_left_panel_width") != null ? $.totalStorage("${app_name}_left_panel_width") : 250;
$(".left-panel").css("width", leftPanelWidth + "px");
$(".content-panel").css("left", leftPanelWidth + 20 + "px");

var codeMirror, dataTable, renderRecent, syncWithHive;

var HIVE_AUTOCOMPLETE_BASE_URL = "${ autocomplete_base_url | n,unicode }";
var HIVE_AUTOCOMPLETE_FAILS_QUIETLY_ON = [500]; // error codes from beeswax/views.py - autocomplete
var HIVE_AUTOCOMPLETE_USER = "${ user }";
var HIVE_AUTOCOMPLETE_APP = "${app_name}";

var STATS_PROBLEMS = "${ _('There was a problem loading the stats.') }";

var snippetType = HIVE_AUTOCOMPLETE_APP == "impala" ? "impala" : "hive";

var editorViewModelOptions = {
  snippetViewSettings: {},
  languages: [],
  user: HIVE_AUTOCOMPLETE_USER
};

editorViewModelOptions.snippetViewSettings[snippetType] = {
  sqlDialect: true
};

editorViewModelOptions.languages.push({
  type: snippetType,
  name: HIVE_AUTOCOMPLETE_APP == "impala" ? "Impala" : "Hive"
});

var apiHelper = window.apiHelper;

var editorViewModel = {
  sqlSourceTypes: [{
    type: snippetType,
    name: HIVE_AUTOCOMPLETE_APP == "impala" ? "Impala" : "Hive"
  }]
};

var snippet = {
  type: ko.observable(snippetType),
  isSqlDialect: ko.observable(true),
  database: ko.observable()
};

var autocompleter = new AceAutocompleteWrapper({
  snippet: snippet,
  user: HIVE_AUTOCOMPLETE_USER,
  oldEditor: true,
  optEnabled: false,
  timeout: AUTOCOMPLETE_TIMEOUT
});

var totalStorageUserPrefix = apiHelper.getTotalStorageUserPrefix(snippetType);

var truncateOutput = function (obj) {
  //default to 20 characters (column output displays first 21 chars so we need to consider the length of both column name and type
  var chars = obj.chars || 20,
    name = obj.name || '',
    type = obj.type || '',
    output = name.length + type.length,
    suffix = '',
    trim;
  if (output > chars) {
    trim = Math.abs((output + 4) - chars); // 4 accounts for ellipsis, spaces, parenthesis
    type = type.slice(0, Math.abs(type.length - trim));
    suffix = '&hellip;';
  }
  return hueUtils.escapeOutput(type) + suffix;
};

var reinitTimeout = -1;

function onPanelPosition() {
  placeResizePanelHandle();
  window.clearTimeout(reinitTimeout);
  reinitTimeout = window.setTimeout(function () {
    reinitializeTableExtenders();
  }, 50);
}

function placeResizePanelHandle() {
  // dynamically positioning the resize panel handle since IE doesn't play well with styles.
  $("#resizePanel a").css("left", $("#resizePanel").position().left + $("#resizePanel").width()/2 - 8);
}

function reinitializeTableExtenders() {
  if (viewModel.design.results.columns().length > 0 && viewModel.design.results.columns().length < 500) {
    $("#resultTable").jHueTableExtender({
      fixedHeader: true,
      fixedFirstColumn: true,
      includeNavigator: false,
      clonedContainerPosition: "absolute"
    });
  }
  $("#recentQueries").jHueTableExtender({
    fixedHeader: true,
    includeNavigator: false,
    clonedContainerPosition: "absolute"
  });
}
var CURRENT_CODEMIRROR_SIZE = 100;
var INITIAL_CODEMIRROR_SIZE = CURRENT_CODEMIRROR_SIZE;
var CODEMIRROR_MANUALLY_RESIZED = false;
var INITIAL_HORIZONTAL_RESIZE_POSITION = -1;

// Navigator, recent queries
$(document).ready(function () {
  $(document).on('click', '.assist-table .fa-list', function(){ $('.modal-backdrop').before($('#assistQuickLook')) });
  $("#resizePanel a").draggable({
    axis: "y",
    start: function (e, ui) {
      CODEMIRROR_MANUALLY_RESIZED = true;
      draggableHelper($(this), e, ui);
    },
    drag: function (e, ui) {
      draggableHelper($(this), e, ui);
      $(".jHueTableExtenderClonedContainer").hide();
      $(".jHueTableExtenderClonedContainerColumn").hide();
      $(".jHueTableExtenderClonedContainerCell").hide();
    },
    stop: function (e, ui) {
      draggableHelper($(this), e, ui);
      $(".jHueTableExtenderClonedContainer").show();
      $(".jHueTableExtenderClonedContainerColumn").show();
      $(".jHueTableExtenderClonedContainerCell").show();
      reinitializeTableExtenders();
    }
  });

  function checkForInitialSplitterPosition() {
    INITIAL_HORIZONTAL_RESIZE_POSITION = $("#resizePanel a").position().top;
    if (INITIAL_HORIZONTAL_RESIZE_POSITION <= 0) {
      window.setTimeout(checkForInitialSplitterPosition, 200);
    }
  }

  checkForInitialSplitterPosition();

  function resizeCodeMirror(el) {
    CURRENT_CODEMIRROR_SIZE = INITIAL_CODEMIRROR_SIZE + (el.position().top - INITIAL_HORIZONTAL_RESIZE_POSITION);
    if (CURRENT_CODEMIRROR_SIZE < 100) {
      CURRENT_CODEMIRROR_SIZE = 100;
    }
    codeMirror.setSize("99%", CURRENT_CODEMIRROR_SIZE);
  }

  function draggableHelper(el, e, ui) {
    resizeCodeMirror(el);
    var minHandlePosition = $('.card-heading.simple').is(':visible') ? $('.card-heading.simple').outerHeight() + 205 : 205;
    if (ui.position.top < minHandlePosition) {
      ui.position.top = minHandlePosition;
    }
  }

  var recentQueries = $("#recentQueries").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "aoColumns": [
        { "sWidth" : "100px", "sSortDataType":"dom-sort-value", "sType":"numeric" },
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
    $("#recentQueries").hide();
    recentQueries.fnClearTable();
    $.getJSON("${ url(app_name + ':list_query_history') }?format=json&recent=true", function(data) {
      if (data && data.queries) {
        var _rows = [];
        $(data.queries).each(function(cnt, item){
          _rows.push([
            '<span data-sort-value="' + item.timeInMs + '">' + moment(item.timeInMs*1000).format("L LTS") + '</span>',
            '<code style="cursor:pointer">' + item.query + '</code>',
            (item.resultsUrl != "" ? '<a href="' + item.resultsUrl + '" data-row-selector-exclude="true">${_('See results...')}</a>': ''),
            (item.designUrl != "" ? '<a href="' + item.designUrl + '" data-row-selector="true">&nbsp;</a>': '')
          ]);
        });
        recentQueries.fnAddData(_rows);
        if (_rows.length > 0){
          $(".clear-queries").show();
        }
        else {
          $(".clear-queries").hide();
        }
      }
      $("a[data-row-selector='true']").jHueRowSelector();
      $("#recentLoader").hide();
      $("#recentQueries").show().css("width", "100%");
      reinitializeTableExtenders();
    });
  };

  renderRecent();

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

  var lastWindowHeight = -1;
  var resizeNavigator = function () {
    var newHeight = $(window).height();
    if (lastWindowHeight !== newHeight) {
      $(".resizer").css("height", (newHeight - 90) + "px");
      $("#navigator .card").css("height", (newHeight - 130) + "px").css("overflow-y", "hidden");
      lastWindowHeight = newHeight;
    }
  };

  resizeNavigator();
  $(window).on("scroll", resizeNavigator);
  $(window).on("resize", resizeNavigator);
  window.setInterval(resizeNavigator, 500);

  $(document).on("click", "#expandResults", function(){
    $("#resultTablejHueTableExtenderClonedContainer").remove();
    $("#resultTablejHueTableExtenderClonedContainerColumn").remove();
    $("#resultTablejHueTableExtenderClonedContainerCell").remove();
    if ($(this).find("i").hasClass("fa-expand")){
      $(this).find("i").removeClass("fa-expand").addClass("fa-compress");
      $(this).parents('.resultsContainer').addClass("fullscreen");
      $('body').addClass("fullscreen");
    }
    else {
      $(this).find("i").addClass("fa-expand").removeClass("fa-compress");
      $(this).parents('.resultsContainer').removeClass("fullscreen");
      $('body').removeClass("fullscreen");
    }
    window.setTimeout(reinitializeTable, 200);
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

  $(document).on("clear.history", function() {
    renderRecent();
    $("#clearHistoryModal").modal("hide");
  });

  $(document).on("shown", "a[data-toggle='tab']:not(.sidetab)", function (e) {
    if ($(e.target).attr("href") == "#log" || $(e.target).attr("href") == "#query" ) {
      logsAtEnd = true;
      window.setTimeout(resizeLogs, 100);
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
    if ($(e.target).attr("href") != "#results" && $(e.target).attr("href") != "#columns"){
      $($(e.target).attr("href")).css('height', 'auto');
      if ($(e.target).attr("href") == "#chart") {
        hueAnalytics.log('beeswax', 'results/chart');
        predictGraph();
      }
    } else {
      reinitializeTable();
    }
    return e;
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
  var _heightCorrection = $('body').hasClass('fullscreen') ? 85 : 150;

  function fn(){
    var container = $($("a[data-toggle='tab']:not(.sidetab)").parent(".active").find("a").attr("href"));
    if ($("#results .dataTables_wrapper").height() > 0) {

      $("#results .dataTables_wrapper").jHueTableScroller({
        minHeight: $(window).height() - _heightCorrection,
        heightAfterCorrection: 0
      });
      $("#recentTab .dataTables_wrapper").jHueTableScroller({
        minHeight: $(window).height() - _heightCorrection,
        heightAfterCorrection: 0
      });
      reinitializeTableExtenders();
      container.height($(window).height() - _heightCorrection);
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

    var _statementAtCursor = getStatementAtCursor();
    var _before = codeMirror.getValue().substr(0, codeMirror.indexFromPos(codeMirror.getCursor()));
    var _after = _statementAtCursor.statement.substr(_statementAtCursor.relativeIndex).replace(/;+$/, "");

    autocompleter.autocomplete(_before, _after, function(suggestions) {
      var isFromDot = _before.match(/.*\.[^ ]*$/) != null;
      var isTable = false;
      var tableFieldMagic = false;
      var hasFromPrefix = false;

      var values = suggestions.map(function(suggestion) {
        if (suggestion.meta === "table") {
          isTable = true; // They're all tables.
          var match = suggestion.value.match(/(\? )?from ([^ ]+)$/i);
          if (match != null) {
            if (typeof match[1] != "undefined") {
              tableFieldMagic = true;
              return match[2];
            } else {
              hasFromPrefix = true;
            }
          }
          return suggestion.value;
        } else {
          return isFromDot ? "." + suggestion.value : suggestion.value;
        }
      }).join(" ");

      if (values.length > 0 && !hasFromPrefix) {
        CodeMirror.fromDot = isFromDot;
        CodeMirror.possibleSoloField = true;
        CodeMirror.tableFieldMagic = tableFieldMagic;
        CodeMirror.possibleTable = isTable && !tableFieldMagic;
        CodeMirror.catalogTables = isTable ? values : "";
        CodeMirror.catalogFields = isTable ? "" : values;
      } else {
        CodeMirror.fromDot = false;
        CodeMirror.possibleSoloField = false;
        CodeMirror.tableFieldMagic = false;
        CodeMirror.possibleTable = false;
        CodeMirror.catalogTables = "";
        CodeMirror.catalogFields = "";
      }

      CodeMirror.showHint(cm, AUTOCOMPLETE_SET);
    });
  };

  codeMirror = CodeMirror(function (elt) {
    queryEditor.parentNode.replaceChild(elt, queryEditor);
  }, {
    value: queryEditor.value,
    readOnly: false,
    lineNumbers: true,
    viewportMargin: Infinity,
    % if app_name == 'impala':
    mode: "text/x-impalaql",
    % else:
    mode: "text/x-hiveql",
    % endif
    extraKeys: {
      "Ctrl-Space": function () {
        codeMirror.execCommand("autocomplete");
      },
      Tab: function (cm) {
        $("#executeQuery").focus();
      }
    },
    onKeyEvent: function (e, s) {
      if (s.type == "keydown" && s.keyCode == 73 && (s.altKey || s.ctrlKey || s.metaKey)) {
        formatQuery();
      }
      if (s.type == "keyup") {
        if (s.keyCode == 190) {
          var _statement = getStatementAtCursor().statement;
          if (_statement.toUpperCase().indexOf("FROM") > -1) {
            window.setTimeout(function () {
              codeMirror.execCommand("autocomplete");
            }, 100);  // timeout for IE8
          }
        }
      }
    }
  });

  huePubSub.subscribe('assist.dblClickDbItem', function(assistDbEntry) {
    var text = assistDbEntry.editorText();
    if (codeMirror.getValue() == queryPlaceholder) {
      codeMirror.setValue("");
      if (assistDbEntry.definition.isTable) {
        text = "SELECT * FROM " + assistDbEntry.editorText() + " LIMIT 100";
      }
      else if (assistDbEntry.definition.isColumn) {
        text = "SELECT " + assistDbEntry.editorText().split(",")[0] + " FROM " + assistDbEntry.parent.editorText() + " LIMIT 100";
      }
    }
    codeMirror.replaceSelection(text);
    codeMirror.setSelection(codeMirror.getCursor());
    codeMirror.focus();
  });

  $(".CodeMirror").droppable({
    accept: ".draggableText",
    drop: function (e, ui) {
      var position = codeMirror.coordsChar({"left": e.clientX, "top": e.clientY});
      var text = ui.helper.text();
      codeMirror.setCursor(position);
      var value = codeMirror.getValue();
      var index = codeMirror.indexFromPos(codeMirror.getCursor());
      if (index > 0 && value.charAt(index - 1) !== ' ' && value.charAt(index - 1) !== '.') {
        text = " " + text;
      }
      if ((index + 1) < value.length - 1  && value.charAt(index + 1) !== ' ' && text.charAt(text.length - 1) !== ' ') {
        text += " ";
      }
      codeMirror.replaceSelection(text);
      codeMirror.setSelection(codeMirror.getCursor());
      codeMirror.focus();
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
    if ($.totalStorage(totalStorageUserPrefix + "${app_name}_temp_query") != null && $.totalStorage(totalStorageUserPrefix + "${app_name}_temp_query") != "") {
      viewModel.queryEditorBlank(true);
      codeMirror.setValue($.totalStorage(totalStorageUserPrefix + "${app_name}_temp_query"));
    }
  % endif

  codeMirror.on("blur", function () {
    $(document.body).off("contextmenu");
  });

  codeMirror.on("change", function () {
    window.setTimeout(function () {
      if (!CODEMIRROR_MANUALLY_RESIZED && $('.CodeMirror').height() < 270 && codeMirror.lineCount() > 7) {
        CURRENT_CODEMIRROR_SIZE = 270;
        if ($('.card-heading.simple').is(':visible')) {
          INITIAL_CODEMIRROR_SIZE = 270;
          INITIAL_HORIZONTAL_RESIZE_POSITION = $('.card-heading.simple').outerHeight() + 374;
        }
        codeMirror.setSize("99%", CURRENT_CODEMIRROR_SIZE);
        reinitializeTableExtenders();
      }
    }, 200);
  });

  $("#download-excel").click(function () {
    if (viewModel.design.results.columns().length > 255) {
      $.jHueNotify.warn("${ _('Results exceeds maximum number of columns permitted by Excel, will truncate results to 255 columns.') }")
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

  $(".fileChooser:not(:has(~ button))").after(hueUtils.getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
};

$(document).one('fetched.design', editables);

$(document).one('fetched.query', editables);

function isNumericColumn(type) {
  return $.inArray(type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE', 'TIMESTAMP_TYPE', 'DATE_TYPE', 'DATETIME_TYPE']) > -1;
}

function isDateTimeColumn(type) {
  return $.inArray(type, ['TIMESTAMP_TYPE', 'DATE_TYPE', 'DATETIME_TYPE']) > -1;
}

function isStringColumn(type) {
  return !isNumericColumn(type) && !isDateTimeColumn(type);
}

var map;
var graphHasBeenPredicted = false;
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
    $("#blueprint").attr("class", "").attr("style", "").empty();
    if (graphType == window.HUE_CHARTS.TYPES.MAP) {
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

        var _koData = [];

        try {
          $("#resultTable>tbody>tr>td:nth-child(" + _latCol + ")").each(function (cnt) {
            if (cnt < 1000) {
              if (_descCol != "-1") {
                _koData.push({ lat: $.trim($(this).text()) * 1, lng: $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1, label: $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _descCol + ")").text())});
              }
              else {
                _koData.push({ lat: $.trim($(this).text()) * 1, lng: $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _lngCol + ")").text()) * 1});
              }
            }
          });
          viewModel.chartData(_koData);
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
        var _koData = [];
        $("#resultTable>tbody>tr>td:nth-child(" + _x + ")").each(function (cnt) {
          if (cnt < 1000) {
            _koData.push({ value: $.trim($(this).text()), count: $.trim($("#resultTable>tbody>tr:nth-child(" + (cnt + 1) + ")>td:nth-child(" + _y + ")").text()) * 1});
          }
        });

        viewModel.chartData(_koData);

        if ($("#resultTable>tbody>tr>td:nth-child(" + _x + ")").length > 1000){
          $("#chart .alert").removeClass("hide");
        }
      }
      else {
        $("#blueprint").addClass("empty").css("text-align", "center").text("${_("Please select the columns you would like to see in this chart.")}");
      }
    }
  }
}

function getGraphType() {
  var _type = "";
  if ($("#blueprintBars").hasClass("active")) {
    _type = window.HUE_CHARTS.TYPES.BARCHART;
  }
  if ($("#blueprintLines").hasClass("active")) {
    _type = window.HUE_CHARTS.TYPES.LINECHART;
  }
  if ($("#blueprintMap").hasClass("active")) {
    _type = window.HUE_CHARTS.TYPES.MAP;
  }
  if ($("#blueprintPie").hasClass("active")) {
    _type = window.HUE_CHARTS.TYPES.PIECHART;
  }
  viewModel.chartType(_type);
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
      $("#blueprintLines").removeClass("active");
      $("#blueprintPie").removeClass("active");
      $("#blueprintMap").removeClass("active");
      $("#blueprintAxis").removeClass("hide");
      $("#blueprintLatLng").addClass("hide");
      $("#blueprintX").val(_firstAllString);
      $("#blueprintY").val(_firstAllNumeric);
    }
  }
  generateGraph(getGraphType());
}

// Logs
var logsAtEnd = true;
$(document).ready(function () {
  var labels = {
    MRJOB: "${_('MR Job')}",
    MRJOBS: "${_('MR Jobs')}"
  };

  $('.assist').css('top', '36px');

  $(window).resize(function () {
    resizeLogs();
  });

  $("a[href='#log']").on("shown", function () {
    resizeLogs();
  });
  $("a[href='#query']").on("shown", function () {
    resizeLogs();
  });

  % if app_name == 'impala':
  $("a[href='#sessionTab']").on("shown", function () {
    // get the impala session info
    viewModel.fetchImpalaSession();
  });
  % endif

  $(".blueprintSelect").on("change", function () {
    generateGraph(getGraphType())
  });

  $("#blueprintBars").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    viewModel.chartType(window.HUE_CHARTS.TYPES.BARCHART);
    generateGraph(window.HUE_CHARTS.TYPES.BARCHART)
  });
  $("#blueprintLines").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    viewModel.chartType(window.HUE_CHARTS.TYPES.LINECHART);
    generateGraph(window.HUE_CHARTS.TYPES.LINECHART)
  });
  $("#blueprintPie").on("click", function () {
    $("#blueprintAxis").removeClass("hide");
    $("#blueprintLatLng").addClass("hide");
    viewModel.chartType(window.HUE_CHARTS.TYPES.PIECHART);
    generateGraph(window.HUE_CHARTS.TYPES.PIECHART)
  });
  $("#blueprintMap").on("click", function () {
    $("#blueprintAxis").addClass("hide");
    $("#blueprintLatLng").removeClass("hide");
    viewModel.chartType(window.HUE_CHARTS.TYPES.MAP);
    generateGraph(window.HUE_CHARTS.TYPES.MAP)
  });

  $("#blueprintNoSort").on("click", function () {
    viewModel.chartSorting("none");
    redrawChart();
  });

  $("#blueprintSortAsc").on("click", function () {
    viewModel.chartSorting("asc");
    redrawChart();
  });

  $("#blueprintSortDesc").on("click", function () {
    viewModel.chartSorting("desc");
    redrawChart();
  });

  function redrawChart() {
    generateGraph(viewModel.chartType());
  }

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
  if ($("#query pre:eq(1)").length > 0) {
    var _height = Math.max($(window).height() - $("#query pre:eq(1)").offset().top, 250);
    $("#query").height(_height - 10);
    $("#query pre:eq(1)").css("overflow", "auto").height(_height - 50);
  }
}

// Result Datatable
function cleanResultsTable() {
  if (dataTable) {
    viewModel.design.results.rows([]);
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
    item.unshift(cnt + startIndex + 1);
    _tmpdata.push(item);
  });
  return _tmpdata;
}

var _scrollTimeout = -1;
function datatableScroll() {
 viewModel.scrollNotWorking(false);

  // Automatic results grower
  var dataTableEl = $("#results .dataTables_wrapper");
  var _lastScrollPosition = dataTableEl.data("scrollPosition") != null ? dataTableEl.data("scrollPosition") : 0;
  window.clearTimeout(_scrollTimeout);
  _scrollTimeout = window.setTimeout(function(){
    dataTableEl.data("scrollPosition", dataTableEl.scrollTop());
    if (_lastScrollPosition !=  dataTableEl.scrollTop() && dataTableEl.scrollTop() + dataTableEl.outerHeight() + 20 > dataTableEl[0].scrollHeight && dataTable && viewModel.hasMoreResults()) {
      dataTableEl.animate({opacity: '0.55'}, 200);
      viewModel.fetchResults();
    }
  }, 100);
}

var firstFnDrawcallback = false;

var manualFetchResultCounter = 0;

function addResults(viewModel, dataTable, startRow, nextRow) {
  if (startRow == 0) {
    firstFnDrawcallback = true;
  }
  dataTable.fnAddData(addRowNumberToResults(viewModel.design.results.rows.slice(startRow, nextRow), startRow));

  % if app_name == 'impala':
  manualFetchResultCounter += (nextRow - startRow);
  if (manualFetchResultCounter < 100 && viewModel.scrollNotWorking() && viewModel.hasMoreResults()){
    manualFetch();
  }
  else {
    manualFetchResultCounter = 0;
  }
  %endif
}

function resultsTable(e, data) {
  $("#results .dataTables_wrapper").animate({opacity: '1'}, 50);
  $.totalStorage(totalStorageUserPrefix + "${app_name}_temp_query", null);
  if (viewModel.design.results.columns().length > 0) {
    if (!dataTable) {
      if (viewModel.design.results.columns().length < 500) {
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
            if (firstFnDrawcallback) {
              firstFnDrawcallback = false;
              window.setTimeout(reinitializeTable, 100);
            }
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
      }
      else {
        dataTable = $("#resultTable").hueDataTable({
          "oLanguage": {
            "sEmptyTable": "${_('No data available')}",
            "sZeroRecords": "${_('No matching records')}"
          },
          "fnDrawCallback": function (oSettings) {
            reinitializeTableExtenders();
            if (firstFnDrawcallback) {
              firstFnDrawcallback = false;
              window.setTimeout(reinitializeTable, 100);
            }
          }
        });
      }
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
      dataTableEl.on("scroll", datatableScroll);
    }

    addResults(viewModel, dataTable, data.start_row, data.next_row);
  }
}

function manualFetch() {
  $("#results .dataTables_wrapper").css("opacity", "0.55");
  viewModel.fetchResults();
}

$(document).on('execute.query', cleanResultsTable);
$(document).on('explain.query', cleanResultsTable);
$(document).on('fetched.results', resultsTable);

var selectedLine = -1;
var errorWidgets = [];

function clearErrorWidgets() {
  $(".jHueTableExtenderClonedContainer").hide();
  $(".jHueTableExtenderClonedContainerColumn").hide();
  $(".jHueTableExtenderClonedContainerCell").hide();
  $.each(errorWidgets, function(index, errorWidget) {
    errorWidget.clear();
  });
  errorWidgets = [];
}

$(document).on('execute.query', clearErrorWidgets);
$(document).on('explain.query', clearErrorWidgets);

$(document).on('error.query', function () {
  $.each(errorWidgets, function(index, el) {
    $(el).remove();
    errorWidgets = [];
  });

  // Move error to codeMirror if we know the line number
  $.each($(".queryErrorMessage"), function(index, el) {
    var err = $(el).text();
    var firstPos = err.toLowerCase().indexOf("line");
    if (firstPos > -1) {
      selectedLine = $.trim(err.substring(err.indexOf(" ", firstPos), err.indexOf(":", firstPos))) * 1;
      if (codeMirror.getSelection()) {
        selectedLine += codeMirror.getCursor(true).line;
      }
      errorWidgets.push(
        codeMirror.addLineWidget(
          selectedLine > 0 ? selectedLine - 1 : selectedLine,
          $("<div>").addClass("editorError").text(err)[0], {
            coverGutter: true,
            noHScroll: true
          }
        )
      );
      codeMirror.scrollTo(null, codeMirror.charCoords({
            line: selectedLine > 0 ? selectedLine - 1 : selectedLine,
            ch: 0
          }, "local").top - codeMirror.getScrollerElement().offsetHeight / 2 - 5);
      $(el).hide();
    }
  });

  reinitializeTableExtenders();
});


// Save
function trySaveDesign() {
  var query = codeMirror.getValue();
  viewModel.design.query.value(query);
  if (viewModel.design.id() && viewModel.design.id() != -1) {
    viewModel.saveDesign();
    hueAnalytics.log('beeswax', 'design/save');
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
    $('#saveAs').find('.help-inline').text('');
    $('#saveAs').find('.control-group').removeClass('error');
    hueAnalytics.log('beeswax', 'design/save-as');
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
  hueAnalytics.log('beeswax', 'results/save');
}

$(document).on('saved.results', function() {
  $('#saveResultsModal').modal('hide');
});

// Querying and click events.
function tryExecuteQuery() {
  viewModel.scrollNotWorking(true);
  $("#results .dataTables_wrapper").off("scroll", datatableScroll);
  $(".jHueTableExtenderClonedContainer").hide();
  $(".jHueTableExtenderClonedContainerColumn").hide();
  $(".jHueTableExtenderClonedContainerCell").hide();
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

  hueAnalytics.log('beeswax', 'query/execute');
}

function tryExecuteNextStatement() {
  viewModel.scrollNotWorking(true);
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

  hueAnalytics.log('beeswax', 'query/execute_next');
}

function tryExecuteParameterizedQuery() {
  viewModel.scrollNotWorking(true);
  $(".tooltip").remove();
  viewModel.executeQuery();
  routie('query');
}

function tryExplainQuery() {
  $(".tooltip").remove();
  var query = getHighlightedQuery() || codeMirror.getValue();
  viewModel.design.query.value(query);
  viewModel.explainQuery();

  hueAnalytics.log('beeswax', 'query/explain');
}


function formatQuery() {
  $.post("/notebook/api/format", {
    statements: codeMirror.getSelection() != '' ? codeMirror.getSelection() : codeMirror.getValue()
  }, function (data) {
    if (data.status == 0) {
      if (codeMirror.getSelection() != '') {
        codeMirror.replaceSelection(data.formatted_statements);
      }
      else {
        codeMirror.setValue(data.formatted_statements);
      }
      viewModel.design.query.value(codeMirror.getValue());
    } else {
      $.jHueNotify.error(data);
    }
  });
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
  $.totalStorage(totalStorageUserPrefix + "${app_name}_temp_query", null);
  location.href="${ url(app_name + ':execute_query') }";
}

// Server error handling.
$(document).on('server.error', function (e, data) {
  $(document).trigger('error', "${_('Server error occurred: ')}" + data.message ? data.message : data.error);
});
$(document).on('server.unmanageable_error', function (e, responseText) {
  var message = responseText;
  if (! message) {
    message = '${ _("Hue server is probably down.") }';
  }
  $(document).trigger('error', "${_('Unmanageable server error occurred: ')}" + message);
});

// Other
$(document).on('saved.design', function (e, id) {
  $('#saveAs').modal('hide');
  $(document).trigger('info', "${_('Query saved.')}");
  huePubSub.publish('open.link', "/${ app_name }/execute/design/" + id);
});
$(document).on('error_save.design', function (e, message) {
  var _message = "${_('Could not save design')}";
  if (typeof message == "object"){
    $('#saveAs').find('.help-inline').text('');
    $('#saveAs').find('.control-group').removeClass('error');
    if (message.saveform){
      if ($('#saveAs').is(":visible")){
        if (message.saveform.name){
          $('#saveas-query-name').addClass('error');
          $('#saveas-query-name').find('.help-inline').text(message.saveform.name.join(' '));
        }
        if (message.saveform.description) {
          $('#saveas-query-description').addClass('error');
          $('#saveas-query-name').find('.help-inline').text(message.saveform.description.join(' '));
        }
      }
      else {
        if (message.saveform.name) {
          _message += " - ${_('Name')}: " + message.saveform.name.join(' ');
        }
        if (message.saveform.description) {
          _message += " - ${_('Description')}: " + message.saveform.description.join(' ');
        }
        $(document).trigger('error', _message);
      }
    }
  }
  else {
    if (message) {
      _message += ": " + message;
    }
    $(document).trigger('error', _message);
  }
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
    }).attr('data-original-title', hueUtils.escapeOutput($(this).val())).tooltip('fixTitle');
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
      source: $.map(data.configuration, function (value, key) {
        return value.key;
      })
    });
  });

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

<%
  if app_name == 'impala':
    from impala import conf as impala_conf
%>
% if ( app_name == 'beeswax' and beeswax_conf.CLOSE_QUERIES.get() ) or ( app_name == 'impala' and impala_conf.CLOSE_QUERIES.get() ):
$(document).ready(function () {
  $(document).on('explain.query', function() {
    viewModel.closeQuery();
  });

  $(document).on('execute.query', function() {
    viewModel.closeQuery();
  });
});

// Close the query when leaving the page, backup for later when disabling the close before downloading results.
window.onbeforeunload = function(e) {
  viewModel.closeQuery();
};
% endif

$(window).data('beforeunload', window.onbeforeunload);

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
    $('.hue-title-bar').show();
    $('.resultsContainer').css('marginTop', '20px');
  }

  function watchPageComponents() {
    $('#advanced-settings').hide();
    viewModel.isEditor(false);
    $('#navigator').hide();
    $('#queryContainer').hide();
    $('#resizePanel').hide();
    $('a[href="#query"]').parent().hide();
    $('a[href="#recentTab"]').parent().hide();
    $('a[href="#queryBuilderTab"]').parent().hide();
    $('.hue-title-bar').hide();
    $('.resultsContainer').css('marginTop', '-50px');
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
    $(".view-query-results[rel=tooltip]").tooltip({
      placement: 'bottom'
    });
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

      hueAnalytics.log('beeswax', 'query/results');
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

      hueAnalytics.log('beeswax', 'watch/logs');
    },
    'watch/results': function() {
      showSection('query-editor');
      watchResultsPage();

      clickHard('.resultsContainer .nav-tabs a[href="#results"]');

      hueAnalytics.log('beeswax', 'watch/results');
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
  var _waitForCodemirrorInit = -1;
  _waitForCodemirrorInit = window.setInterval(function () {
    if (typeof codeMirror != "undefined") {
      codeMirror.on("change", function () {
        $(".query").val(codeMirror.getValue());
        $.totalStorage(totalStorageUserPrefix + "${app_name}_temp_query", codeMirror.getValue());
      });
      window.clearInterval(_waitForCodemirrorInit);
    }
  }, 100);
}

function loadDesign(design_id) {
  viewModel.design.id(design_id);
  viewModel.fetchDesign();

  setupCodeMirrorSubscription();
}

function loadQueryHistory(query_history_id) {
  viewModel.design.history.id(query_history_id);
  viewModel.fetchQueryHistory();

  setupCodeMirrorSubscription();
}

function setupCodeMirrorSubscription() {
  var codeMirrorSubscription = viewModel.design.query.value.subscribe(function (value) {
    viewModel.queryEditorBlank(true);
    var _waitForCodemirrorInit = -1;
    _waitForCodemirrorInit = window.setInterval(function () {
      if (typeof codeMirror != "undefined") {
        codeMirror.setValue(value);
        codeMirrorSubscription.dispose();
        window.clearInterval(_waitForCodemirrorInit);
      }
    }, 100);
  });
}

// Knockout
viewModel = new BeeswaxViewModel("${app_name}", apiHelper);
ko.applyBindings(viewModel, $("#beeswax-execute")[0]);

var handleAssistSelection = function (databaseDef) {
  if (databaseDef.sourceType === snippetType && snippet.database() !== databaseDef.name) {
    snippet.database(databaseDef.name);
  }
};

huePubSub.subscribe("assist.database.set", handleAssistSelection);
huePubSub.subscribe("assist.database.selected", handleAssistSelection);

if (! snippet.database()) {
  huePubSub.publish("assist.get.database", snippetType);
}

shareViewModel = initSharing("#documentShareModal");
shareViewModel.setDocId(${doc_id});

$('.left-panel').on('mousewheel', function(e){
  e.preventDefault();
  e.stopPropagation();
  return false;
});

% if not beeswax_conf.USE_GET_LOG_API.get() and app_name != 'impala':
  viewModel.shouldAppendLogs = true;
% endif

% if query_history:
  loadQueryHistory(${query_history.id});
% elif design.id:
  loadDesign(${design.id});
% else:
  $(document).ready(cacheQueryTextEvents);
% endif
viewModel.design.fileResources.values.subscribe(function() {
  // File chooser button for file resources.
  $(".fileChooser:not(:has(~ button))").after(hueUtils.getFileBrowseButton($(".fileChooser:not(:has(~ button))")));
});

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
    var successUrl = "${request.GET['on_success_url']}";
    if (viewModel.design.watch.errors().length != 0) {
      window.setTimeout(function(){
        huePubSub.publish('open.link', successUrl + (successUrl.indexOf("?") > -1 ? "&" : "?") + "error=" + encodeURIComponent(viewModel.design.watch.errors().join("\n")));
      }, 200);
    }
    else if (viewModel.design.results.errors().length == 0) {
      window.setTimeout(function(){
        huePubSub.publish('open.link', successUrl + (successUrl.indexOf("?") > -1 ? "&" : "?") + "refresh=true");
      }, 1000);
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


// chart related stuff


function pieChartDataTransformer(data) {
  var _data = [];
  $(data.counts()).each(function (cnt, item) {
    _data.push({
      label: item.value,
      value: item.count,
      obj: item
    });
  });

  if (viewModel.chartSorting() == "asc"){
    _data.sort(function(a, b){
      return a.value - b.value
    });
  }
  if (viewModel.chartSorting() == "desc"){
    _data.sort(function(a, b){
      return b.value - a.value
    });
  }

  return _data;
}

function leafletMapChartDataTransformer(data) {
  if (data != null && data.counts != null) return data.counts();
}

function barChartDataTransformer(rawDatum) {
  var _datum = [];
  var _data = [];

  $(rawDatum.counts()).each(function (cnt, item) {
    if (typeof item.from != "undefined") {
      _data.push({
        series: 0,
        x: item.from,
        x_end: item.to,
        y: item.value,
        obj: item
      });
    }
    else {
      _data.push({
        series: 0,
        x: item.value,
        y: item.count,
        obj: item
      });
    }
  });

  if (viewModel.chartSorting() == "asc"){
    _data.sort(function(a, b){
      return a.y - b.y
    });
  }
  if (viewModel.chartSorting() == "desc"){
    _data.sort(function(a, b){
      return b.y - a.y
    });
  }

  _datum.push({
    key: $("#blueprintY option:selected").text(),
    values: _data
  });
  return _datum;
}

function lineChartDataTransformer(rawDatum) {
  var _datum = [];
  var _data = [];
    $(rawDatum.counts()).each(function (cnt, item) {
      if (typeof item.from != "undefined") {
        _data.push({
          series: 0,
          x: item.from,
          x_end: item.to,
          y: item.value,
          obj: item
        });
      }
      else {
        _data.push({
          series: 0,
          x: item.value,
          y: item.count,
          obj: item
        });
      }
    });

    if (viewModel.chartSorting() == "asc"){
      _data.sort(function(a, b){
        return a.y - b.y
      });
    }
    if (viewModel.chartSorting() == "desc"){
      _data.sort(function(a, b){
        return b.y - a.y
      });
    }

    _datum.push({
      key: $("#blueprintY option:selected").text(),
      values: _data
    });
  return _datum;
}


</script>

${ commonfooter(request, messages) | n,unicode }

