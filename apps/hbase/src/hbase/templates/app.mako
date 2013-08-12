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

<%def name="datatable(datasource,rowTemplate = 'itemTemplate')">
  <table data-datasource="${datasource}" class="table table-striped table-condensed datatables tablescroller-disable">
      <thead>
        <tr>
          <th width="1%"><div data-bind="click: ${datasource}.toggleSelectAll, css: {hueCheckbox: true,'icon-ok':${datasource}.selected().length == ${datasource}.items().length && ${datasource}.items().length>0}"></div></th>
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
  <div class="smartview" data-bind="foreach: ${datasource}.items()">
    <div class="smartview-row" data-bind="css:{selected:$data.isSelected()}, visible: $data.items().length > 0 || $data.isLoading()">
      <h5 data-bind="click: lockClickOrigin($data.select, $element)"><code class="row_key" data-bind="text: $data.row.slice(0, 100) + ($data.row.length > 100 ? '...' : '')"></code> <i class="icon-check-sign" data-bind="visible:$data.isSelected()"></i> <img data-bind="visible: $data.isLoading()" src="/static/art/spinner.gif" />
        <span class="smartview-row-controls controls-hover-bottom">
          <button class="btn" data-bind="click: $data.reload, clickBubble: false" data-toggle="tooltip" title="${_('Refresh Row')}"><i class="icon-refresh"></i></button>
          % if user.is_superuser:
            <button class="btn" data-bind="click: $data.drop, clickBubble: false" data-toggle="tooltip" title="${_('Delete Row')}"><i class="icon-trash"></i></button>
          % endif
        </span>
        <span class="smartview-row-controls pull-right">
          <button class="btn" data-bind="click: $data.toggleSelectedCollapse, enable: $data.selected().length > 0, clickBubble: false" data-toggle="tooltip" title="${_('Toggle Collapse Selected')}"><i class="icon-resize-small"></i></button>
          <button class="btn" data-bind="click: $data.toggleSelectAllVisible, enable: $data.displayedItems().length > 0, clickBubble: false" data-toggle="tooltip" title="${_('Select All Visible')}"><i class="icon-check"></i></button>
          <input type="text" placeholder="${('Filter Column Names/Family')}" data-bind="value: $data.searchQuery, valueUpdate: $data.items().length < 100 ? 'afterkeydown' : 'change', clickBubble: false"/>
          ${sortBtn('$data.sortDropDown')}
          % if user.is_superuser:
            <button class="btn" data-bind="enable: $data.selected().length > 0, click: $data.dropSelected, clickBubble: false"><i class="icon-trash"></i> Drop Columns</button>
          % endif
          <a href="#new_column_modal" data-bind="click:function(){$('#new_column_row_key').val($data.row);app.focusModel($data);logGA('new_column_modal');}" class="btn" data-toggle="modal" title="${_('Add New Column/Cell')}"><i class="icon-plus"></i></a>
        </span>
      </h5>
      <ul class="smartview-cells" data-bind="event: {scroll: onScroll}">
        <!-- ko foreach: $data.displayedItems() -->
        <li data-bind="css: {'active': $data.isSelected()}, click: $data.select">
          <div>
            <h6><span class="label" data-bind="text: $data.name.split(':')[0]+':', style: {'backgroundColor': stringHashColor($data.name.split(':')[0])}"></span> <span data-bind="text: $data.name.split(':')[1]"></span></h6>
            <span class="timestamp label"><i class='icon-time'></i> <span data-bind="text: convertTimestamp($data.timestamp)"></span></span>
            % if user.is_superuser:
              <a class="corner-btn btn" data-bind="click: $data.drop, clickBubble: false"><i class="icon-trash"></i></a>
            % endif
            <a class="corner-btn btn" data-bind="visible: $data.editing(), event: { mousedown: function(){launchModal('cell_edit_modal',{content:$data, mime: detectMimeType($data.value())})} }"><i class="icon-pencil"></i> ${_('Full Editor')}</a>
            <pre data-bind="text: $data.value().length > 146 ? $data.value().substring(0, 144)+'...' : $data.value(), click: $data.value().length > 146 ? function(){launchModal('cell_edit_modal',{content:$data, mime: detectMimeType($data.value())})} : function(){$data.editing(true)}, clickBubble: false, visible: !$data.isLoading() && !$data.editing()"></pre>
            <textarea data-bind="visible: !$data.isLoading() && $data.editing(), hasfocus: $data.editing, value: $data.value, click:function(){}, clickBubble: false"></textarea>
            <img src="/static/art/spinner.gif" data-bind="visible: $data.isLoading() " />
          </div>
        </li>
        <!-- /ko -->
      </ul>
    </div>
  </div>
  <br/>
  <div class="alert alert-error" data-bind="visible: !${datasource}.isLoading()">
    <b>${_('Notice:')}</b> ${_(' entries may be truncated with limit set at')} <i data-bind="text: ${datasource}.truncateLimit"></i> ${_('items per set.')}
  </div>
  <div class="alert alert-warning" data-bind="visible: !${datasource}.isLoading()">
      ${_('Query executed in')} <i data-bind="text:${datasource}.lastReloadTime() + 's'"></i> ${_('fetching')} <i data-bind="text: ${datasource}.items().length"></i> ${_('rows')}.
  </div>
  <center data-bind="visible: ${datasource}.isLoading()">
  <!--[if !IE]><!--><i class="icon-spinner icon-spin loader-main"></i><!--<![endif]-->
  <!--[if IE]><img src="/hbase/static/art/loader.gif" /><![endif]-->
  </center>
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
  <!-- Page Header -->
  <h1>
    <a href="/hbase/">HBase Browser</a> - <a data-bind="text: app.cluster(), attr: { href: '#' + app.cluster() }"></a>
    <span data-bind="visible: app.station() == 'table'">/ <a data-bind="text: app.views.tabledata.name(), attr: { href: '#' + app.cluster() + '/' + app.views.tabledata.name()}"></a></span>
    <span class="pull-right">
      <span class="dropdown">
        <a class="dropdown-toggle btn" id="dLabel" data-toggle="dropdown">
          Switch Cluster
          <b class="caret"></b>
        </a>
        <ul id="cluster-menu" class="dropdown-menu" role="menu" aria-labelledby="dLabel" data-bind="foreach: app.clusters()">
          <li><a data-bind="text: $data.name, click: function(){ routie($data.name); }"></a></li>
        </ul>
      </span>
    </span>
  </h1>

  <!-- Application Pages -->
  <div id="main"></div>

  <div id="hbase-page-clusterview" class="hbase-page"> <!-- maybe turn these into script tags, then populate them into #main and then rerender + apply bindings to old viemodels to have modular viewmodels? -->
    <div class="actionbar">
      <div class="well well-small">
        <input type="text" class="input-large search-query" placeholder="${_('Search for Table Name')}" data-bind="value: views.tables.searchQuery, valueUpdate: 'afterkeydown'">
        % if user.is_superuser:
          <span class="btn-group">
            <button class="btn" data-bind="enable: views.tables.canEnable, click: views.tables.enableSelected"><i class="icon-check-sign"></i> ${_('Enable')}</button>
            <button class="btn" data-bind="enable: views.tables.canDisable, click: views.tables.disableSelected">
              <i class="icon-check-empty"></i> ${_('Disable')}
            </button>
          </span>
          <button class="btn" data-bind="enable: views.tables.selected().length > 0, click: views.tables.dropSelected"><i class="icon-trash"></i> ${_('Drop')}</button>
        % endif
        <span class="pull-right">
          <a href="#new_table_modal" role="button" data-bind="click: function(){app.focusModel(app.views.tables);}" class="btn" data-toggle="modal"><i class='icon-plus-sign'></i> ${_('New Table')}</a>
        </span>
      </div>
    </div>

    ${datatable('views.tables')}

    <script id="itemTemplate" type="text/html">
      <tr>
        <td><div data-bind="click: $data.select, css: {hueCheckbox: true,'icon-ok':$data.isSelected}" data-row-selector-exclude="true"></div></td>
        <td width="90%"><a data-bind="text:$data.name,attr: {href: '#'+app.cluster()+'/'+$data.name}" data-row-selector="true"></a></td>
        <td width="5%"><i data-bind="click: $data.toggle, css: {'icon-check-sign':$data.enabled, 'icon-check-empty':$data.enabled != true}" data-row-selector-exclude="true"></i></td>
      </tr>
    </script>

    <!-- New Table Modal -->
    <form id="new_table_modal" action="createTable" method="POST" class="modal hide fade ajaxSubmit" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>${_('Create New Table')}</h3>
      </div>
      <div class="modal-body controls">
        <input type="hidden" name="cluster" data-bind="value:app.cluster"/>
        <label>${_('Table Name')}:</label> <input name="tableName" placeholder="MyTable" type="text"/>
        <label>${_('Column Families')}:</label>
        <ul>
          <li><input type="text" name="table_columns" placeholder="family_name"></li>
        </ul>
        <a class="btn action_addColumn"><i class="icon-plus-sign"></i> ${_('Additional Column Family')}</a>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
        <input type="submit" class="btn btn-primary" value="${_('Submit')}"/>
      </div>
    </form>
  </div>

  <!-- Table View Page -->
  <div id="hbase-page-dataview" class="hbase-page">
    <div class="subnav sticky">
      <div class="container-fluid">
        <div class="row-fluid">
          <div id="searchbar-main" class="span5" data-bind="click: search.clickTagBar">
            <div id="search-tags" contenteditable="true" data-bind="editableText: search.cur_input, hasfocus: search.focused, css: { 'active': search.cur_input() != '' }, event: { 'keydown': search.onKeyDown, click: search.updateMenu.bind(null) }" data-placeholder="${_('row_key, row_key_prefix* + scan_length, row_key [family:col1, family2:col2, family3:]')}">
            </div>
          </div>
          <ul id="search-typeahead" data-bind="visible: search.focused() && !search.submitted()">
            <!-- ko if: search.mode() != 'idle' -->
            <li><a><b data-bind="text: search.modes[search.mode()].hint"></b>: <span data-bind="html: search.hintText()"></span> <code class="pull-right" data-bind="text: search.modes[search.mode()].type"></code></a></li>
            <!-- /ko -->
            <!-- ko foreach: search.activeHints() -->
            <li data-bind="event: { mousedown: function(){app.search.cur_input(app.search.cur_input() + $data.shortcut);} }, css: {active: self.activeHint}"><a><span data-bind="text: $data.hint"></span> <code class="pull-right" data-bind="text: $data.shortcut"></code></a></li>
            <!-- /ko -->
            <li class="search-suggestion-header" data-bind="visible: search.activeSuggestions().length > 0"><a>${_('Autocomplete Suggestions:')}</a></li>
            <!-- ko foreach: search.activeSuggestions() -->
            <li class="search-suggestion" data-bind="event: { mousedown: app.search.replaceFocusNode.bind(null, $data) }, css: {active: app.search.activeSuggestion() == $index()}"><a><span data-bind="text: $data"></span></a></li>
            <!-- /ko -->
          </ul>
          <a class="search-remove" data-bind="visible: search.cur_input() != '', click: function(){ app.search.cur_input(''); }"><i class="icon-remove-sign"></i></a>
          <button class="btn btn-primary add-on" data-bind="enabled: !search.submitted(), click: search.evaluate.bind(null)"><i class="icon-search"></i></button>
          <span id="column-family-selectors">
            <!-- ko foreach: views.tabledata.columnFamilies() -->
              <span class="label" data-bind="text: $data.name, style: {'backgroundColor': ($data.enabled()) ? stringHashColor($data.name.split(':')[0]) : '#ccc' ,'cursor':'pointer'}, click: $data.toggle"></span>
            <!-- /ko -->
           </span>
            <span class="pull-right">
              <input type="text" placeholder="Filter Columns/Families" style="margin-left: 5px;" data-bind="value: app.views.tabledata.columnQuery, clickBubble: false"/>
              <button class="btn" data-bind="click: views.tabledata.toggleSelectAll" style="margin-left: 5px;" data-toggle="tooltip" title="${_('Toggle Select All Rows')}"><i class="icon-check-sign"></i> ${_('All')}</button>
              ${sortBtn('views.tabledata.sortDropDown')}
            </span>
            <span class="smartview-row-controls pull-right" data-bind="if: views.tabledata.items().length > 0 && views.tabledata.selected().length > 0">
              <button class="btn" data-bind="click: views.tabledata.batchSelectedAlias.bind(null, 'toggleSelectedCollapse'), clickBubble: false" data-toggle="tooltip" title="${_('Toggle Collapse Selected')}"><i class="icon-resize-small"></i></button>
              <button class="btn" data-bind="click: views.tabledata.batchSelectedAlias.bind(null, 'toggleSelectAllVisible'), clickBubble: false" data-toggle="tooltip" title="${_('Select All Visible')}"><i class="icon-check"></i></button>
              % if user.is_superuser:
                <button class="btn" data-bind="enable: views.tabledata.items()[0].selected().length > 0, click: views.tabledata.items()[0].dropSelected, clickBubble: false"><i class="icon-trash"></i> ${_('Drop Columns')}</button>
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
            <b>${_('Displaying')}</b>
            <!-- ko foreach: app.views.tabledata.querySet -->
            <span data-bind="visible: $data.scan_length() > 1 || $data.editing()"><b data-bind="text: $data.scan_length, visible: !$data.editing(), click: $data.editing.bind(true)"></b>
            <input type="number" style="width:30px" data-bind="value: $data.scan_length, visible: $data.editing()"/>
            entr<span data-bind="text: $data.scan_length() > 1 ? 'ies' : 'y'"></span> ${_('starting from')}</span>
            <code data-bind="text: $data.row_key, visible: !$data.editing(), click: $data.editing.bind(true)"></code><input type="text" class="input-small" placeholder="row_key" data-bind="value: $data.row_key, visible: $data.editing()"/>
            <span data-bind="visible: $data != app.views.tabledata.querySet()[app.views.tabledata.querySet().length - 1],
                             text: $data == app.views.tabledata.querySet()[app.views.tabledata.querySet().length - 2] ? 'and' : ','"></span>
            <!-- /ko -->
            <a class="btn" data-bind="click: app.views.tabledata.addQuery"><i class="icon-plus-sign"></i> ${_('Add Query Field')}</a>
            <a class="btn btn-primary" data-bind="click: app.views.tabledata.evaluateQuery">${_('Go')}</a>
          </div>
          <span class="pull-right">
            % if user.is_superuser:
              <button class="btn" data-bind="enable: views.tabledata.selected().length > 0, click: views.tabledata.dropSelected"><i class="icon-trash"></i> ${_('Drop Rows')}</button>
            % endif
            <a href="#new_row_modal" data-bind="click:function(){app.focusModel(app.views.tabledata);logGA('new_row_modal');}" role="button" class="btn btn-primary" data-callback="" data-toggle="modal"><i class='icon-plus-sign'></i> ${_('New Row')}</a>
          </span>
        </div>
    </div>

    <!-- New Row Modal -->
    <form id="new_row_modal" action="putRow" method="POST" class="modal hide fade ajaxSubmit" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>${_('Insert New Row')} - <span data-bind="text: pageTitle"></span></h3>
      </div>
      <div class="modal-body controls">
        <input type="hidden" name="cluster" data-bind="value:app.cluster"/>
        <input type="hidden" name="tableName" data-bind="value:views.tabledata.name"/>
        <label class="control-label">${_('Row Key')}</label>
        <input type="text" name="row_key" placeholder="row_key">
        <input type="hidden" name="column_data" data-subscribe="#new_row_field_list"/>
        <ul id="new_row_field_list"></ul>
        <a class="btn action_addColumnValue"><i class="icon-plus-sign"></i> ${_('Add Field')}</a>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
        <input type="submit" class="btn btn-primary" value="Submit" />
      </div>
    </form>

    <!-- New Column Modal -->
    <form id="new_column_modal" action="putColumn" method="POST" class="modal hide fade ajaxSubmit" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>${_('Create New Column')} - <span data-bind="text: pageTitle"></span></h3>
      </div>
      <div class="modal-body controls">
        <input type="hidden" data-bind="value: app.cluster"/>
        <input type="hidden" data-bind="value: app.views.tabledata.name"/>
        <input id="new_column_row_key" type="hidden"/>
        <label class="control-label">${_('Column Name')}</label>
        <input type="text" placeholder = "family:column_name">
        <label class="control-label">${_('Cell Value')}</label>
        <input type="text" placeholder = "${_('Cell Value')}">
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
        <input type="submit" class="btn btn-primary" value="Submit">
      </div>
    </form>

    <!-- Cell Edit Modal -->
    <form id="cell_edit_modal" action="putColumn" method="POST" class="modal hide fade ajaxSubmit">
    </form>

    <script id="cell_edit_modal_template" type="text/html">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>Edit Cell - <span data-bind="text: content.name"></span> <code data-bind="text: mime"></code></h3>
      </div>
      <div class="modal-body container-fluid">
          <div class="row-fluid">
            <div class="span10 controls">
              <input type="hidden" data-bind="value: app.cluster"/>
              <input type="hidden" data-bind="value: app.views.tabledata.name"/>
              <input type="hidden" data-bind="value: $data.content.parent.row"/>
              <input type="hidden" data-bind="value: $data.content.name"/>
              <!-- ko template: {name: 'cell_'+mime.split('/')[0].toLowerCase()+'_template'} -->
              <!-- /ko -->
            </div>
            <div class="span2">
              <ul class="nav nav-list well well-small">
                <li class="nav-header">Cell History:</li>
                <!-- ko foreach: $data.content.history.items() -->
                  <li><a data-bind="click: function(){$parent.content.value($data.value);}, text: convertTimestamp($data.timestamp)"></a></li>
                <!-- /ko -->
                <li data-bind="visible: $data.content.history.loading()"><img src="/static/art/spinner.gif" /></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        % if user.is_superuser:
          <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
          <button id="file-upload-btn" class="btn fileChooserBtn" aria-hidden="true"><i class="icon-upload"></i> ${_('Upload')}</button>
          <input type="submit" class="btn btn-primary" value="${_('Save')}">
        % else:
          <button class="btn" data-dismiss="modal" aria-hidden="true">${_('OK')}</button>
        % endif
      </div>
    </script>
    <script id="cell_image_template" type="text/html">
      <img data-bind="attr:{src: 'data:image/' + $data.mime + ';base64,' + $data.content.value()}"/>
    </script>
    <script id="cell_text_template" type="text/html">
      <textarea id="codemirror_target" data-bind="text: $data.content.value()" data-use-post="true"></textarea>
    </script>
    <script id="cell_application_template" type="text/html">
      <iframe width="100%" height="100%" data-bind="attr:{src: 'data:' + $data.mime + ';base64,' + $data.content.value()}"></iframe>
    </script>
    <script id="cell_type_template" type="text/html">
      <textarea style="width:100%" data-bind="text: $data.content.value()" data-use-post="true"></textarea>
    </script>
  </div>

  <!-- Confirm Modal -->
  <div id="confirm-modal" action="createTable" method="POST" class="modal hide fade"></div>
  <script id="confirm_template" type="text/html">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
      <h3 data-bind="text: title"></h3>
    </div>
    <div class="modal-body" data-bind="text: text">
    </div>
    <div class="modal-footer">
      <button class="btn" data-dismiss="modal" aria-hidden="true">${_('Cancel')}</button>
      <button class="confirm-submit btn btn-danger" data-dismiss="modal">${_('Confirm')}</button>
    </div>
  </script>
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
  'Mark Row/Column Prefix': "${_('Mark Row/Column Prefix')}",
  'Start Row/Column Scan': "${_('Start Row/Column Scan')}",
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
  'Integer': "${_('Integer')}"
};

function i18n(text) {
  if(text in i18n_cache)
    return i18n_cache[text];
  return text;
};
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