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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(None, "hbase", user) | n,unicode } 

<link href="/hbase/static/css/hbase.css" rel="stylesheet" type="text/css" />

<div class="navbar navbar-inverse navbar-fixed-top nokids">
    <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="/${app_name}">
              <img src="/hbase/static/art/icon_hbase_48.png" class="app-icon" />
              ${ _('HBase Browser') }
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<%def name="datatable(datasource,rowTemplate = 'itemTemplate')">
  <table data-datasource="${datasource}" class="table table-striped table-condensed datatables tablescroller-disable" style="padding-left: 0;padding-right: 0">
      <thead>
        <tr>
          <th width="1%"><div data-bind="click: ${datasource}.toggleSelectAll, css: {hueCheckbox: true, 'fa': true, 'fa-check':${datasource}.selected().length == ${datasource}.items().length && ${datasource}.items().length>0}"></div></th>
          <!-- ko foreach: ${datasource}.columns() -->
            <th data-bind="text:$data"></th> <!-- need to i18n first -->
          <!-- /ko -->
        </tr>
      </thead>
      <tbody data-bind="template: {name: '${rowTemplate}', foreach: ${datasource}.items}">

      </tbody>
      <tfoot>
      <tr data-bind="visible: ${datasource}.isLoading()">
          <td colspan="8" class="left">
              <img src="/static/art/spinner.gif" />
          </td>
      </tr>
          <tr data-bind="visible: ${datasource}.items().length == 0 && !${datasource}.isLoading()">
              <td colspan="8">
                  <div class="alert">
                      ${_('There are no tables matching the search criteria.')}
                  </div>
            </td>
          </tr>
      </tfoot>
  </table>
</%def>

<%def name="smartview(datasource)">
  <div class="smartview" data-bind="foreach: ${datasource}.items(), css: { 'gridView': ${datasource}.showGrid() }">
    <div class="smartview-row" data-bind="css:{selected:$data.isSelected()}, visible: $data.items().length > 0 || $data.isLoading()">
      <h5 data-bind="click: lockClickOrigin($data.select, $element)"><code class="row_key" data-bind="text: $data.row.slice(0, 100) + ($data.row.length > 100 ? '...' : '')"></code> <i class="fa fa-check-square" data-bind="visible:$data.isSelected()"></i> <img data-bind="visible: $data.isLoading()" src="/static/art/spinner.gif" />
        <span class="smartview-row-controls controls-hover-bottom">
          <button class="btn" data-bind="click: $data.reload, clickBubble: false" data-toggle="tooltip" title="${_('Refresh Row')}"><i class="fa fa-refresh"></i></button>
          % if user.is_superuser:
            <button class="btn" data-bind="click: $data.drop, clickBubble: false" data-toggle="tooltip" title="${_('Delete Row')}"><i class="fa fa-trash-o"></i></button>
          % endif
        </span>
        <span class="smartview-row-controls pull-right">
          <button class="btn" data-bind="click: $data.toggleSelectedCollapse, enable: $data.selected().length > 0, clickBubble: false" data-toggle="tooltip" title="${_('Toggle Collapse Selected')}"><i data-bind="css: { 'fa': true, 'fa-compress': !$data.isCollapsed(), 'fa-expand': $data.isCollapsed() }"></i></button>
          <button class="btn" data-bind="click: $data.toggleSelectAllVisible, enable: $data.displayedItems().length > 0, clickBubble: false" data-toggle="tooltip" title="${_('Select All Visible')}"><i class="fa fa-check-square-o"></i></button>
          <input type="text" placeholder="${('Filter Column Names/Family')}" data-bind="value: $data.searchQuery, valueUpdate: $data.items().length < 100 ? 'afterkeydown' : 'change', clickBubble: false"/>
          ${sortBtn('$data.sortDropDown')}
          % if user.is_superuser:
            <button class="btn" data-bind="enable: $data.selected().length > 0, click: $data.dropSelected, clickBubble: false"><i class="fa fa-trash-o"></i> Drop Columns</button>
          % endif
          % if can_write:
          <a href="#new_column_modal" data-bind="click:function(){app.focusModel($data);launchModal('new_column_modal', $data);}" class="btn" title="${_('Add New Column/Cell')}"><i class="fa fa-plus"></i></a>
          % endif
        </span>
      </h5>
      <ul class="smartview-cells" data-bind="event: {scroll: onScroll}">
        <!-- ko foreach: $data.displayedItems() -->
        <li data-bind="css: {'active': $data.isSelected()}, click: $data.select">
          <div>
            <h6><span class="label" data-bind="text: $data.name.split(':')[0]+':', style: {'backgroundColor': stringHashColor($data.name.split(':')[0])}"></span> <span data-bind="text: $data.name.split(':')[1]"></span></h6>
            <span class="timestamp label"><i class='fa fa-clock-o'></i> <span data-bind="text: convertTimestamp($data.timestamp)"></span></span>
            % if user.is_superuser:
              <a class="corner-btn btn" data-bind="click: $data.drop, clickBubble: false"><i class="fa fa-trash-o"></i></a>
            % endif
            <a class="corner-btn btn" data-bind="visible: $data.editing(), event: { mousedown: function(){launchModal('cell_edit_modal',{content:$data, mime: detectMimeType($data.value())})} }"><i class="fa fa-pencil"></i> ${_('Full Editor')}</a>
            <pre data-bind="text: ($data.value().length > 146 ? $data.value().substring(0, 144)+'...' : $data.value()).replace(/(\r\n|\n|\r)/gm,''), click: editCell.bind(null, $data), clickBubble: false, visible: !$data.isLoading() && !$data.editing()"></pre>
            <textarea data-bind="visible: !$data.isLoading() && $data.editing(), hasfocus: $data.editing, value: $data.value, click:function(){}, clickBubble: false"></textarea>
            <img src="/static/art/spinner.gif" data-bind="visible: $data.isLoading() " />
          </div>
        </li>
        <!-- /ko -->
      </ul>
    </div>
  </div>
  <br/>
  <center data-bind="visible: ${datasource}.isLoading()">
  <!--[if !IE]><!--><i class="fa fa-spinner fa-spin loader-main"></i><!--<![endif]-->
  <!--[if IE]><img src="/hbase/static/art/loader.gif" /><![endif]-->
  </center>
  <div class="alert" data-bind="visible: ${datasource}.items().length == 0 && !${datasource}.isLoading()">
      ${_('No rows to display.')}
  </div>
</%def>

<%def name="sortBtn(datasource)">
  <div class="btn-group">
    <button class="btn" data-bind="click: ${datasource}.toggleSortMode">${_('Sort By')} <i data-bind="text: ${datasource}.sortField(), clickBubble: false"></i> <b data-bind="text: ${datasource}.sortAsc() ? 'ASC' : 'DESC'">ASC</b></button>
    <button class="btn dropdown-toggle" data-toggle="dropdown" data-bind="clickBubble: false">
      <span class="caret"></span>
    </button>
    <ul class="dropdown-menu" data-bind="foreach: ${datasource}.sortFields">
      <li><a data-bind="click: function(){('sortDropDown' in $parent ? $parent : $parent.views.tabledata).sortDropDown.sortField($data)}, text: $data, clickBubble: false"></a></li>
    </ul>
  </div>
</%def>

<div class="container-fluid">
  <div class="card card-small">
  <!-- Page Header -->
  <h1 class="card-heading simple">
    <a href="/hbase/">${_('Home')}</a> - <a data-bind="text: app.cluster(), attr: { href: '#' + app.cluster() }"></a>
    <span data-bind="visible: app.station() == 'table'">/ <a data-bind="text: app.views.tabledata.name(), attr: { href: '#' + app.cluster() + '/' + app.views.tabledata.name()}"></a></span>
    <span class="pull-right">
      <span class="dropdown">
        <a class="dropdown-toggle btn" id="dLabel" data-toggle="dropdown">
          ${_('Switch Cluster')}
          <b class="caret" style="margin-top: 0"></b>
        </a>
        <ul id="cluster-menu" class="dropdown-menu" role="menu" aria-labelledby="dLabel" data-bind="foreach: app.clusters()">
          <li><a data-bind="text: $data.name, click: function(){ routie($data.name); }"></a></li>
        </ul>
      </span>
    </span>
  </h1>

  <div class="card-body">
    <p>

  <!-- Application Pages -->
  <div id="main"></div>

  <div id="hbase-page-clusterview" class="hbase-page"> <!-- maybe turn these into script tags, then populate them into #main and then rerender + apply bindings to old viemodels to have modular viewmodels? -->
    <div class="actionbar">
      <div style="padding-bottom: 20px">
        <input type="text" class="input-large search-query" placeholder="${_('Search for Table Name')}" data-bind="value: views.tables.searchQuery, valueUpdate: 'afterkeydown'">
        % if user.is_superuser:
          <span class="btn-group">
            <button class="btn" data-bind="enable: views.tables.canEnable, click: views.tables.enableSelected"><i class="fa fa-check-square"></i> ${_('Enable')}</button>
            <button class="btn" data-bind="enable: views.tables.canDisable, click: views.tables.disableSelected">
              <i class="fa fa-square-o"></i> ${_('Disable')}
            </button>
          </span>
          <button class="btn" data-bind="enable: views.tables.selected().length > 0, click: views.tables.dropSelected"><i class="fa fa-trash-o"></i> ${_('Drop')}</button>
        % endif
        % if can_write:
        <span class="pull-right">
          <a href="#new_table_modal" role="button" data-bind="click: function(){prepareNewTableForm(); app.focusModel(app.views.tables);}" class="btn" data-toggle="modal"><i class='fa fa-plus-circle'></i> ${_('New Table')}</a>
        </span>
        % endif
      </div>
    </div>

    ${datatable('views.tables')}

    <script id="itemTemplate" type="text/html">
      <tr>
        <td><div data-bind="click: $data.select, css: {hueCheckbox: true,'fa': true, 'fa-check':$data.isSelected}" data-row-selector-exclude="true"></div></td>
        <td width="90%"><a data-bind="text:$data.name,attr: {href: '#'+app.cluster()+'/'+$data.name}" data-row-selector="true"></a></td>
        <td width="5%"><i data-bind="click: $data.toggle, css: {'fa': true, 'fa-check-square':$data.enabled, 'fa-square-o':$data.enabled != true}" data-row-selector-exclude="true"></i></td>
      </tr>
    </script>

    <!-- New Table Modal -->
    <form id="new_table_modal" action="createTable" method="POST" class="modal hide fade ajaxSubmit" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <a class="close pointer" data-dismiss="modal" aria-hidden="true">&times;</a>
        <h3>${_('Create New Table')}</h3>
      </div>
      <div class="modal-body controls">
        <input type="hidden" name="cluster" data-bind="value:app.cluster"/>
        <label>${_('Table Name')}:</label> <input name="tableName" placeholder="MyTable" type="text"/>
        <label>${_('Column Families')}:</label>
        <ul class="columns"></ul>
        <a class="pointer action_addColumn"><i class="fa fa-plus-circle"></i> ${_('Add an additional column family')}</a>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
        <input type="submit" class="btn btn-primary" value="${_('Submit')}"/>
      </div>
    </form>

    <script id="columnTemplate" type="text/html">
      <ul class="pull-right columnProperties"></ul>
      <div class="inline" style="width: 24px">
        <a class="pointer action_removeColumn" title="${_('Remove Column Family')}"><i class="fa fa-times"></i></a>
      </div>
      <input type="text" name="table_columns" placeholder="family_name" class="no-margin">
      <div class="clearfix"></div>
    </script>

    <script id="columnPropertyTemplate" type="text/html">
      <select name="table_columns_property" style="width:180px" class="no-margin">
        <option data-default="3" selected>maxVersions</option>
        <option data-default="NONE">compression</option>
        <option data-default="true">inMemory</option>
        <option data-default="NONE">bloomFilterType</option>
        <option data-default="0">bloomFilterVectorSize</option>
        <option data-default="0">bloomFilterNbHashes</option>
        <option data-default="true">blockCacheEnabled</option>
        <option data-default="-1">timeToLive</option>
      </select>
      <input type="text" name="table_columns_property_value" placeholder="3" style="width:80px" class="no-margin">
      <a class="pointer action_removeColumnProperty" title="${_('Remove column property')}"><i class="fa fa-minus-circle"></i></a>
      <a class="pointer action_addColumnProperty" title="${_('Additional column property')}"><i class="fa fa-plus-circle"></i></a>
    </script>
    <script id="columnPropertyEmptyTemplate" type="text/html">
      <li class="columnPropertyEmpty" style="width:310px; line-height: 29px">
        <a class="pointer action_addColumnProperty"><i class="fa fa-plus-circle"></i> ${_('Add a column property')}</a>
      </li>
    </script>
  </div>

  <!-- Table View Page -->
  <div id="hbase-page-dataview" class="hbase-page">
    <div class="subnav sticky">
      <div class="container-fluid">
        <div class="row-fluid">
          <div id="searchbar-main" class="span5" data-bind="click: search.clickTagBar">
            <a class="search-remove" data-bind="visible: search.cur_input() != '', click: function(){ app.search.cur_input(''); app.search.focused(true) }"><i class="fa fa-times-circle"></i></a>
            <div id="search-tags" contenteditable="true" data-bind="editableText: search.cur_input, hasfocus: search.focused, css: { 'active': search.cur_input() != '' }, event: { 'keydown': search.onKeyDown, click: search.updateMenu.bind(null) }" data-placeholder="${_('row_key, row_prefix* +scan_len [col1, family:col2, fam3:, col_prefix* +3, fam: col2 to col3] {Filter1() AND Filter2()}')}">
            </div>
          </div>
          <ul id="search-typeahead" data-bind="visible: search.focused() && !search.submitted()">
            <!-- ko if: search.mode() != 'idle' -->
            <li><a><b data-bind="text: search.modes[search.mode()].hint"></b> <code class="pull-right" data-bind="text: search.modes[search.mode()].type"></code></a></li>
            <!-- /ko -->
            <!-- ko foreach: search.activeHints() -->
            <li data-bind="event: { mousedown: function(){app.search.cur_input(app.search.cur_input() + $data.shortcut);} }, css: {active: self.activeHint}"><a><span data-bind="text: $data.hint"></span> <code class="pull-right" data-bind="text: $data.shortcut"></code></a></li>
            <!-- /ko -->
            <li class="search-suggestion-header" data-bind="visible: search.activeSuggestions().length > 0"><a>${_('Autocomplete Suggestions:')}</a></li>
            <!-- ko foreach: search.activeSuggestions() -->
            <li class="search-suggestion" data-bind="event: { mousedown: app.search.replaceFocusNode.bind(null, $data) }, css: {active: app.search.activeSuggestion() == $index()}"><a><span data-bind="text: $data"></span></a></li>
            <!-- /ko -->
          </ul>
          <button class="btn btn-primary add-on" data-bind="enabled: !search.submitted(), click: search.evaluate.bind(null)"><i class="fa fa-search"></i></button>
          <span id="column-family-selectors">
            <!-- ko foreach: views.tabledata.columnFamilies() -->
              <span class="label" data-bind="text: $data.name, style: {'backgroundColor': ($data.enabled()) ? stringHashColor($data.name.split(':')[0]) : '#ccc' ,'cursor':'pointer'}, click: $data.toggle"></span>
            <!-- /ko -->
           </span>
            <span class="pull-right">
              <button class="btn" data-bind="click: function(){views.tabledata.showGrid(!views.tabledata.showGrid());}, clickBubble: false" data-toggle="tooltip" title="${_('Toggle Grid')}"><i class="fa fa-table"></i></button>
              <input type="text" placeholder="Filter Columns/Families" style="margin-left: 5px;" data-bind="value: app.views.tabledata.columnQuery, clickBubble: false"/>
              <button class="btn" data-bind="click: views.tabledata.toggleSelectAll" style="margin-left: 5px;" data-toggle="tooltip" title="${_('Toggle Select All Rows')}"><i class="fa fa-check-square"></i> ${_('All')}</button>
              ${sortBtn('views.tabledata.sortDropDown')}
            </span>
            <span class="smartview-row-controls pull-right" data-bind="if: views.tabledata.items().length > 0 && views.tabledata.selected().length > 0">
              <button class="btn" data-bind="click: views.tabledata.batchSelectedAlias.bind(null, 'toggleSelectedCollapse'), clickBubble: false" data-toggle="tooltip" title="${_('Toggle Collapse Selected')}"><i class="fa fa-compress"></i></button>
              <button class="btn" data-bind="click: views.tabledata.batchSelectedAlias.bind(null, 'toggleSelectAllVisible'), clickBubble: false" data-toggle="tooltip" title="${_('Select All Visible')}"><i class="fa fa-check-square-o"></i></button>
              % if user.is_superuser:
                <button class="btn" data-bind="enable: views.tabledata.items()[0].selected().length > 0, click: views.tabledata.items()[0].dropSelected, clickBubble: false"><i class="fa fa-trash-o"></i> ${_('Drop Columns')}</button>
              % endif
            </span>
        </div>
      </div>
    </div>
    <br/>

    ${smartview('views.tabledata')}

    <br/><br/><br/><br/>
    <div class="subnav navbar-fixed-bottom well-small">
        <div class="container-fluid">
          <div class="footer-slider">
            <span data-bind="visible: !app.views.tabledata.isLoading()">
              ${_('Fetched')}
              <!-- ko foreach: app.views.tabledata.querySet -->
              <span data-bind="visible: $data.scan_length() > 1"><b data-bind="text: $data.scan_length"></b>
              entr<span data-bind="text: $data.scan_length() > 1 ? 'ies' : 'y'"></span> ${_('starting from')}</span>
              <code data-bind="text: $data.row_key"></code>
              <span data-bind="visible: $data != app.views.tabledata.querySet()[app.views.tabledata.querySet().length - 1],
                               text: $data == app.views.tabledata.querySet()[app.views.tabledata.querySet().length - 2] ? 'and' : ','"></span>
              <!-- /ko -->
              ${_('in')} <i data-bind="text: app.views.tabledata.lastReloadTime()"></i> ${_('seconds')}.
              <b data-bind="visible: app.views.tabledata.reachedLimit()">${_('Entries after')} <i data-bind="text: app.views.tabledata.truncateLimit"></i> ${_('were truncated.')}</b>
            </span>
          </div>
          <span class="pull-right">
            % if user.is_superuser:
              <a class="btn" data-bind="enable: views.tabledata.selected().length > 0, click: views.tabledata.dropSelected"><i class="fa fa-trash-o"></i> ${_('Drop Rows')}</a>
            % endif
            % if can_write:
            <a id="bulk-upload-btn" class="btn fileChooserBtn" data-toggle="tooltip" title="${_('.CSV, .TSV, etc...')}" aria-hidden="true"><i class="fa fa-upload"></i> ${_('Bulk Upload')}</a>
            <a href="#new_row_modal" data-bind="click:function(){app.focusModel(app.views.tabledata);launchModal('new_row_modal')}" role="button" class="btn btn-primary" data-callback=""><i class='fa fa-plus-circle'></i> ${_('New Row')}</a>
            % endif
          </span>
        </div>
    </div>

    <!-- New Row Modal -->
    <form id="new_row_modal" action="putRow" method="POST" class="modal hide fade ajaxSubmit" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    </form>
    <script id="new_row_modal_template" type="text/html">
      <div class="modal-header">
        <a class="close pointer" data-dismiss="modal" aria-hidden="true">&times;</a>
        <h3>${_('Insert New Row')}</h3>
      </div>
      <div class="modal-body controls">
        <input type="hidden" name="cluster" data-bind="value:app.cluster"/>
        <input type="hidden" name="tableName" data-bind="value:app.views.tabledata.name"/>
        <label class="control-label">${_('Row Key')}</label>
        <input type="text" name="row_key" placeholder="row_key">
        <input type="hidden" name="column_data" data-subscribe="#new_row_field_list"/>
        <ul id="new_row_field_list"></ul>
        <a class="btn action_addColumnValue"><i class="fa fa-plus-circle"></i> ${_('Add Field')}</a>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
        <input type="submit" class="btn btn-primary" value="Submit" />
      </div>
    </script>

    <!-- New Column Modal -->
    <form id="new_column_modal" action="putColumn" method="POST" class="modal hide fade ajaxSubmit" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    </form>
    <script id="new_column_modal_template" type="text/html">
      <div class="modal-header">
          <a class="close pointer" data-dismiss="modal" aria-hidden="true">&times;</a>
          <h3>${_('Create New Column')}</h3>
        </div>
        <div class="modal-body controls">
          <input type="hidden" data-bind="value: app.cluster"/>
          <input type="hidden" data-bind="value: app.views.tabledata.name"/>
          <input type="hidden" data-bind="value: $data.row"/>
          <label class="control-label">${_('Column Name')}</label>
          <input id="new_column_name" type="text" placeholder = "family:column_name">
          <label class="control-label">${_('Cell Value')}</label>
          <textarea placeholder = "${_('Cell Value')}"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
          <a id="column-upload-btn" class="btn fileChooserBtn" aria-hidden="true"><i class="fa fa-upload"></i> ${_('Upload')}</a>
          <input type="submit" class="btn btn-primary" value="Submit">
        </div>
    </script>

    <!-- Cell Edit Modal -->
    <form id="cell_edit_modal" action="putColumn" method="POST" class="modal hide fade ajaxSubmit">
    </form>

    <script id="cell_edit_modal_template" type="text/html">
      <div class="modal-header">
        <a class="close pointer" data-dismiss="modal" aria-hidden="true">&times;</a>
        <h3>${_('Edit Cell')} - <span data-bind="text: content.name || formatTimestamp(content.timestamp)"></span> <code data-bind="text: mime"></code> <small><i class="fa fa-clock-o"></i> <span data-bind="text: formatTimestamp($data.content.timestamp)"></span></small></h3>
      </div>
      <div class="modal-body container-fluid">
          <div class="row-fluid">
            <div class="span9 controls">
              <!-- ko if: !$data.readonly -->
              <input type="hidden" data-bind="value: app.cluster"/>
              <input type="hidden" data-bind="value: app.views.tabledata.name"/>
              <input type="hidden" data-bind="value: $data.content.parent.row"/>
              <input type="hidden" data-bind="value: $data.content.name"/>
              <!-- /ko -->
              <!-- ko template: {name: 'cell_'+mime.split('/')[0].toLowerCase()+'_template'} -->
              <!-- /ko -->
            </div>
            <div class="span3">
              <ul class="nav nav-list cell-history">
                <li class="nav-header">${_('Cell History:')}</li>
                <!-- ko foreach: $data.content.history.items() -->
                  <li data-bind="css: { 'active': $data.timestamp == $parent.content.timestamp }"><a data-bind="click: $parent.content.history.pickHistory.bind(null, $data), text: formatTimestamp($data.timestamp)" class="pointer"></a></li>
                <!-- /ko -->
                <li data-bind="visible: $data.content.history.loading()"><img src="/static/art/spinner.gif" /></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer" data-bind="if: !$data.readonly">
        % if user.is_superuser:
          <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
          <a id="file-upload-btn" class="btn fileChooserBtn" aria-hidden="true"><i class="fa fa-upload"></i> ${_('Upload')}</a>
          <input data-bind="visible: mime.split('/')[0].toLowerCase() != 'application' && mime.split('/')[0].toLowerCase() != 'image'" type="submit" class="btn btn-primary" value="${_('Save')}">
        % else:
          <button class="btn" data-dismiss="modal" aria-hidden="true">${_('OK')}</button>
        % endif
      </div>
    </script>
    <script id="cell_image_template" type="text/html">
      <img data-bind="attr:{src: 'data:image/' + $data.mime + ';base64,' + $data.content.value()}"/>
    </script>
    <script id="cell_text_template" type="text/html">
      <textarea id="codemirror_target" data-bind="text: $data.content.value" data-use-post="true"></textarea>
    </script>
    <script id="cell_application_template" type="text/html">
      <iframe width="100%" height="100%" data-bind="attr:{src: 'data:' + $data.mime + ';base64,' + $data.content.value()}"></iframe>
    </script>
    <script id="cell_type_template" type="text/html">
      <textarea style="width:100%; height: 450px;" data-bind="text: $data.content.value" data-use-post="true"></textarea>
    </script>
  </div>

  <!-- Confirm Modal -->
  <div id="confirm-modal" action="createTable" method="POST" class="modal hide fade"></div>
  <script id="confirm_template" type="text/html">
    <div class="modal-header">
      <a class="close pointer" data-dismiss="modal" aria-hidden="true">&times;</a>
      <h3 data-bind="text: title"></h3>
    </div>
    <div class="modal-body" data-bind="text: text">
    </div>
    <div class="modal-footer">
      <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
      <button class="confirm-submit btn btn-danger" data-dismiss="modal">${_('Confirm')}</button>
    </div>
  </script>
  </p>
  </div>

</div><!-- card -->

</div>

<script type="text/javascript">
var i18n_cache = {
  "Confirm Delete": "${_('Confirm Delete')}",
  "Delete row ": "${_('Delete row ')}",
  '? (This cannot be undone)': "${_('? (This cannot be undone)')}",
  "Are you sure you want to drop this column?": "${_('Are you sure you want to drop this column?')}",
  'enable': "${_('enable')}",
  'disable': "${_('disable')}",
  'Confirm': "${_('Confirm')}",
  "Are you sure you want to": "${_('Are you sure you want to')}",
  "this table?": "${_('this table?')}",
  'End Query': "${_('End Query')}",
  'Prefix Scan': "${_('Prefix Scan')}",
  'Start Scan': "${_('Start Scan')}",
  'Start Select Columns': "${_('Start Select Columns')}",
  'End Column/Family': "${_('End Column/Family')}",
  'End Select Columns': "${_('End Select Columns')}",
  'Start FilterString': "${_('Start FilterString')}",
  'End FilterString': "${_('End FilterString')}",
  'Row Key Value': "${_('Row Key Value')}",
  'Length of Scan or Row Key': "${_('Length of Scan or Row Key')}",
  'Column Family: Column Name': "${_('Column Family: Column Name')}",
  'Rows starting with': "${_('Rows starting with')}",
  'String': "${_('String')}",
  'Integer': "${_('Integer')}",
  'Column Range': "${_('Column Range')}"
};

function i18n(text) {
  if(text in i18n_cache)
    return i18n_cache[text];
  return text;
};

canWrite = ${ str(can_write).lower() };
</script>
<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/mustache.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<script src="/static/ext/js/codemirror-xml.js"></script>
<script src="/static/ext/js/codemirror-javascript.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">

<script src="/hbase/static/js/base.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/api.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/controls.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/nav.js" type="text/javascript" charset="utf-8"></script>
<script src="/hbase/static/js/app.js" type="text/javascript" charset="utf-8"></script>

${ commonfooter(messages) | n,unicode }