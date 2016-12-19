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
from django.utils.html import escape
from django.utils.translation import ugettext as _

from desktop import conf
from desktop.conf import USE_NEW_EDITOR
from beeswax.conf import LIST_PARTITIONS_LIMIT
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter, _ko
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="components" file="components.mako" />
% if not is_embeddable:
${ commonheader(_("Metastore"), app_name, user, request) | n,unicode }

<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>
<script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('beeswax/js/stats.utils.js') }"></script>
<script src="${ static('desktop/js/jquery.huedatatable.js') }"></script>

${ assist.assistJSModels() }

<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">
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

${ assist.assistPanel() }
% endif

<span class="notebook">

${ components.menubar() }

<script src="${ static('metastore/js/metastore.ko.js') }"></script>
<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">

<script type="text/html" id="metastore-breadcrumbs">
  <ul class="nav nav-pills hueBreadcrumbBar" id="breadcrumbs">
    <li>
      <a href="javascript:void(0);" data-bind="click: databasesBreadcrumb">${_('Databases')}</a>
      <!-- ko if: database -->
      <span class="divider">&gt;</span>
      <!-- /ko -->
    </li>
    <!-- ko with: database -->
    <li>
      <a href="javascript:void(0);" data-bind="text: name, click: $root.tablesBreadcrumb"></a>
      <!-- ko if: table -->
      <span class="divider">&gt;</span>
      <!-- /ko -->
    </li>
    <!-- ko with: table -->
    <li class="editable-breadcrumbs" title="${_('Edit path')}" data-bind="click: function(){ $parent.editingTable(true); }, visible: !$parent.editingTable()">
      <span data-bind="text: name"></span>
    </li>
    <!-- /ko -->
    <!-- ko if: editingTable -->
      <!-- ko with: table -->
      <li class="editable-breadcrumb-input">
        <input type="text" data-bind="hivechooser: {data: name, database: $parent.name, skipColumns: true, searchEverywhere: true, onChange: function(val){ $parent.setTableByName(val); $parent.editingTable(false); }}" autocomplete="off" />
      </li>
      <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
  </ul>
</script>

<script type="text/html" id="metastore-columns-table">
  <div style="overflow-x: auto; overflow-y: hidden">
    <table class="table table-striped table-condensed table-nowrap">
      <br/>
      <thead>
      <tr>
        <th width="2%">&nbsp;</th>
        <th width="2%" class="no-sort">&nbsp;</th>
        <th width="17%">${_('Name')}</th>
        <th width="15%">${_('Type')}</th>
        <!-- ko if: $root.optimizerEnabled  -->
          <th width="15%">${_('Popularity')}</th>
        <!-- /ko -->
        <th width="50%">${_('Comment')}</th>
      </tr>
      </thead>
      <tbody data-bind="hueach: {data: $data, itemHeight: 29, scrollable: '.content-panel', scrollableOffset: 200, disableHueEachRowCount: 5, scrollUp: true}">
        <tr>
          <td data-bind="text: $index() + $indexOffset() + 1"></td>
          <td><a class="blue" href="javascript:void(0)" data-bind="click: showContextPopover"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a></td>
          <td title="${ _("Scroll to the column") }">
            <!-- ko if: $root.database().table().samples.loading() -->
            <span data-bind="text: name"></span>
            <!-- /ko -->
            <!-- ko ifnot: $root.database().table().samples.loading() -->
            <a href="javascript:void(0)" class="column-selector" data-bind="text: name, click: scrollToColumn"></a>
            <!-- /ko -->
          </td>
          <td data-bind="text: type"></td>
          <!-- ko if: $root.optimizerEnabled  -->
          <td>
            <div class="progress" style="height: 10px; width: 70px; margin-top:5px;" data-bind="attr: { 'title': popularity() }">
              <div class="bar" style="background-color: #338bb8" data-bind="style: { 'width' : popularity() + '%' }"></div>
            </div>
          </td>
          <!-- /ko -->
          <td>
            % if has_write_access:
              <span data-bind="editable: comment, editableOptions: {enabled: true, placement: 'left', emptytext: '${ _ko('Add a comment...') }', inputclass: 'input-xlarge'}" class="editable editable-click editable-empty">
                ${ _('Add a comment...') }</span>
            % else:
              <span data-bind="text: comment"></span>
            % endif
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</script>

<script type="text/html" id="metastore-partition-columns-table">
  <div style="overflow-x: auto; overflow-y: hidden">
    <table class="table table-striped table-condensed table-nowrap">
      <thead>
        <tr>
          <th style="width: 1%">&nbsp;</th>
          <th>${_('Name')}</th>
          <th>${_('Type')}</th>
        </tr>
      </thead>
      <tbody>
      <!-- ko foreach: detailedKeys -->
      <tr>
        <td data-bind="text: $index() + 1"></td>
        <td data-bind="text: $data.name"></td>
        <td data-bind="text: $data.type"></td>
      </tr>
      <!-- /ko -->
      </tbody>
    </table>
  </div>
</script>

<script type="text/html" id="metastore-partition-values-table">
  <div style="overflow-x: auto; overflow-y: hidden">
    <table class="table table-striped table-condensed table-nowrap">
      <thead>
        <tr>
          <th style="width: 1%">&nbsp;</th>
          <th>${_('Values')}</th>
          <th>${_('Spec')}</th>
          <th>${_('Browse')}</th>
        </tr>
      </thead>
      <tbody>
      <!-- ko foreach: values -->
      <tr>
        <td data-bind="text: $index()+1"></td>
        <td><a data-bind="attr: {'href': readUrl }, text: '[\'' + columns.join('\',\'') + '\']'"></a></td>
        <td data-bind="text: partitionSpec"></td>
        <td>
          <a data-bind="attr: {'href': readUrl }"><i class="fa fa-th"></i> ${_('Data')}</a>
          <a data-bind="attr: {'href': browseUrl }"><i class="fa fa-file-o"></i> ${_('Files')}</a>
        </td>
      </tr>
      <!-- /ko -->
      </tbody>
    </table>
  </div>
</script>

<script type="text/html" id="metastore-samples-table">
  <table class="table table-striped table-condensed table-nowrap sample-table">
    <thead>
      <tr>
        <th style="width: 1%">&nbsp;</th>
        <!-- ko foreach: headers -->
        <th data-bind="text: $data"></th>
        <!-- /ko -->
      </tr>
    </thead>
    <tbody>
      <!-- ko foreach: rows -->
        <tr>
          <td data-bind="text: $index()+1"></td>
          <!-- ko foreach: $data -->
            <td data-bind="text: $data"></td>
          <!-- /ko -->
        </tr>
      <!-- /ko -->
    </tbody>
  </table>

  <div id="jumpToColumnAlert" class="alert hide" style="margin-top: 12px;">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>${_('Did you know?')}</strong>
    <ul>
      <li>${ _('If the sample contains a large number of columns, click a row to select a column to jump to') }</li>
    </ul>
  </div>
</script>

<script type="text/html" id="metastore-table-properties">
  <i data-bind="visible: loadingDetails" class="fa fa-spinner fa-spin fa-2x muted" style="display: none;"></i>
  <!-- ko with: tableDetails -->
  <h4>${ _('Properties') }</h4>
  <div class="row-fluid">
    <div title="${ _('Type') }">
      <!-- ko if: is_view -->
        <i class="fa fa-fw fa-eye muted"></i> ${ _('View') }
      <!-- /ko -->
      <!-- ko ifnot: is_view -->
        <i class="fa fa-fw fa-table muted"></i> ${ _('Table') }
      <!-- /ko -->
    </div>
    <div title="${ _('Owner') }">
      <i class="fa fa-fw fa-user muted"></i> <span data-bind="text: details.properties.owner"></span>
    </div>
    <div title="${ _('Created') }"><i class="fa fa-fw fa-clock-o muted"></i> <span data-bind="text: localeFormat(details.properties.create_time)"></span></div>
    <div title="${ _('Format') }">
      <i class="fa fa-fw fa-file-o muted"></i> <span data-bind="text: details.properties.format"></span>
      <i class="fa fa-fw fa-archive muted"></i> <span data-bind="visible: details.properties.compressed" style="display:none;">${_('Compressed')}</span>
      <span data-bind="visible: !details.stats.compressed" style="display:none;">${_('Not compressed')}</span>
    </div>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-table-stats">
  <!-- ko if: tableDetails() && ! tableDetails().is_view -->
    <!-- ko with: tableDetails -->
    <h4>${ _('Stats') }
      <!-- ko ifnot: partition_keys.length -->
        % if has_write_access:
        <!-- ko if: $parent.refreshingTableStats -->
        <i class="fa fa-refresh fa-spin"></i>
        <!-- /ko -->
        <!-- ko ifnot: $parent.refreshingTableStats() || is_view  -->
        <a class="pointer" href="javascript: void(0);" data-bind="click: $parent.refreshTableStats"><i class="fa fa-refresh"></i></a>
        <!-- /ko -->
        % endif
        <span data-bind="visible: details.stats.COLUMN_STATS_ACCURATE == 'false' && ! is_view" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }"><i class="fa fa-exclamation-triangle"></i></span>
      <!-- /ko -->
    </h4>
    <div class="row-fluid">
      <div>
        <i class="fa fa-fw fa-hdd-o muted"></i>
        <!-- ko if: details.properties.format == 'kudu' -->
          ${_('Stored in')} Kudu
        <!-- /ko -->
        <!-- ko if: details.properties.format != 'kudu' -->
          <a data-bind="attr: {'href': hdfs_link, 'rel': path_location}">${_('Location')}</a>
        <!-- /ko -->
      </div>
      <!-- ko with: $parent.tableStats -->
        <!-- ko if: typeof last_modified_by !== 'undefined' -->
          <div title="${ _('Last modified by') }"><i class="fa fa-fw fa-user muted"></i> <span data-bind="text: last_modified_by"></span> </div>
        <!-- /ko -->
        <!-- ko if: typeof last_modified_time !== 'undefined' -->
          <div title="${ _('Last modified time') }"><i class="fa fa-fw fa-clock-o muted"></i> <span data-bind="text: localeFormat(last_modified_time*1000)"></span></div>
        <!-- /ko -->
        <!-- ko if: typeof numFiles !== 'undefined' && typeof last_modified_by === 'undefined' -->
          <div title="${ _('Number of files') }"><i class="fa fa-fw fa-files-o muted"></i> <span data-bind="text: numFiles"></span> ${ _('files') }</div>
        <!-- /ko -->
        <!-- ko if: typeof numRows !== 'undefined' -->
          <div title="${ _('Number of rows') }"><i class="fa fa-fw fa-list muted"></i> <span data-bind="text: numRows"></span> ${ _('rows') }</div>
        <!-- /ko -->
        <!-- ko if: typeof totalSize !== 'undefined' && typeof last_modified_by === 'undefined' -->
          <div title="${ _('Total size') }"><i class="fa fa-fw fa-tasks muted"></i> <span data-bind="text: filesize(totalSize)"></span></div>
        <!-- /ko -->
      <!-- /ko -->
    </div>
    <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-databases">
  <div class="actionbar-actions" data-bind="dockable: { scrollable: '.content-panel', nicescroll: true, jumpCorrection: 5 }">
    <input class="input-xlarge search-query margin-left-10" type="text" placeholder="${ _('Search for a database...') }" data-bind="clearable: databaseQuery, value: databaseQuery, valueUpdate: 'afterkeydown'"/>
    % if has_write_access:
      <button class="btn toolbarBtn margin-left-20" title="${_('Drop the selected databases')}" data-bind="click: function () { $('#dropDatabase').modal('show'); }, disable: selectedDatabases().length === 0"><i class="fa fa-times"></i>  ${_('Drop')}</button>
      <div id="dropDatabase" class="modal hide fade">
        <form id="dropDatabaseForm" action="/metastore/databases/drop" method="POST">
          ${ csrf_token(request) | n,unicode }
          <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times</a>
            <div class="alert-message block-message warning">${ _('Warning: This will drop all tables and objects within the database.') }</div>
            </br>
            <h3 id="dropDatabaseMessage">${ _('Do you really want to delete the following database(s)?') }</h3>
            <ul data-bind="foreach: selectedDatabases">
              <li>
                <span data-bind="text: name"></span>
                <!-- ko if: $data.tables().length > 0 -->
                    (<span data-bind="text: $data.tables().length"></span> tables)
                <!-- /ko -->
              </li>
            </ul>
          </div>
          <div class="modal-footer">
            <input type="button" class="btn" data-dismiss="modal" value="${_('No')}">
            <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
          </div>
          <!-- ko foreach: selectedDatabases -->
          <input type="hidden" name="database_selection" data-bind="value: name" />
          <!-- /ko -->
        </form>
      </div>
    % endif
  </div>
  <table id="databasesTable" class="table table-condensed datatables" style="margin-bottom: 10px" data-bind="visible: filteredDatabases().length > 0">
    <thead>
    <tr>
      <th width="1%" style="text-align: center"><div class="hueCheckbox fa" data-bind="hueCheckAll: { allValues: filteredDatabases, selectedValues: selectedDatabases }"></div></th>
      <th>${ _('Database Name') }</th>
    </tr>
    </thead>
    <tbody data-bind="hueach: {data: filteredDatabases, itemHeight: 29, scrollable: '.content-panel', scrollableOffset: 145, scrollUp: true}">
    <tr>
      <td width="1%" style="text-align: center">
        <div class="hueCheckbox fa" data-bind="multiCheck: '#databasesTable', value: $data, hueChecked: $parent.selectedDatabases"></div>
      </td>
      <td>
        <a href="javascript: void(0);" data-bind="text: name, click: function () { $parent.setDatabase($data, function(){ huePubSub.publish('metastore.url.change'); }) }"></a>
      </td>
    </tr>
    </tbody>
  </table>
  <span class="margin-left-10" data-bind="visible: filteredDatabases().length === 0" style="font-style: italic; display: none;">${_('No databases found')}</span>
</script>

<script type="text/html" id="metastore-tables">
    <div class="row-fluid">
      <!-- ko with: stats  -->
      <div class="
      %if is_optimizer_enabled:
        span8
      %else:
        span12
      %endif
       tile">

          <div class="span6 tile">
            <h4>${ _('Properties') }</h4>
            <div title="${ _('Comment') }"><i class="fa fa-fw fa-comment muted"></i>
              <!-- ko if: comment -->
              <span data-bind="text: comment"></span>
              <!-- /ko -->
              <!-- ko ifnot: comment -->
              <i>${_('No comment.')}</i>
              <!-- /ko -->
              <div title="${ _('Owner') }">
                <i class="fa fa-fw fa-user muted"></i>
                <span data-bind="text: owner_name"></span> (<span data-bind="text: owner_type"></span>)
                </br>
                <i class="fa fa-fw fa-hdd-o muted"></i> <a data-bind="attr: {'href': hdfs_link, 'rel': location }"> ${_('Location')}</a>
              </div>
            </div>
          </div>
          <div class="span6 tile">
            <!-- ko if: $root.navigatorEnabled()  -->
            <h4>${ _('Tagging') }</h4>
            <div style="margin-top: 5px" data-bind="component: { name: 'nav-tags', params: {
              sourceType: 'hive',
              database: db_name
              } }"></div>
            <!-- /ko -->
        </div>
        <!-- ko with: parameters -->
        <div class="row-fluid">
          <div class="span12">
            <div title="${ _('Parameters') }">
              <!-- ko template: { name: 'metastore-databases-parameters', data: hueUtils.parseHivePseudoJson($data) }--><!-- /ko -->
            </div>
          </div>
        </div>
        <!-- /ko -->
      </div>
      <!-- /ko -->

      <!-- ko if: $root.optimizerEnabled() && $root.database().optimizerStats() && $root.database().optimizerStats().length > 0 -->
      <div class="span4 tile chart-container">
        <h4>${ _('Popularity') }</h4>

        <ul>
          <li>
            <span>Diagram?</span>
          </li>
          <li>
            <span>DB specific stats</span>
          </li>
        </ul>

      </div>
      <!-- /ko -->

    </div>


    <div class="row-fluid">
      <div class="span12 tile">
        <h4>${ _('Tables') }</h4>
        <div class="actionbar-actions" data-bind="visible: tables().length > 0, dockable: { scrollable: '.content-panel', nicescroll: true, jumpCorrection: 5 }">
          <input class="input-xlarge search-query margin-left-10" type="text" placeholder="${ _('Search for a table...') }" data-bind="clearable: tableQuery, value: tableQuery, valueUpdate: 'afterkeydown'"/>
          <button class="btn toolbarBtn margin-left-20" title="${_('Browse the selected table')}" data-bind="click: function () { setTable(selectedTables()[0]); selectedTables([]); }, disable: selectedTables().length !== 1"><i class="fa fa-eye"></i> ${_('View')}</button>
          <button class="btn toolbarBtn" title="${_('Query the selected table')}" data-bind="click: function () { location.href = '/notebook/browse/' + name + '/' + selectedTables()[0].name; }, disable: selectedTables().length !== 1">
            <i class="fa fa-pencil-square-o"></i> ${_('Query')}
          </button>
          % if has_write_access:
            <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete the selected tables')}" data-bind="click: function () { $('#dropTable').modal('show'); }, disable: selectedTables().length === 0"><i class="fa fa-times"></i>  ${_('Drop')}</button>
          % endif
          <!-- ko if: $root.optimizerEnabled  -->
          &nbsp;
          &nbsp;
          <button class="btn toolbarBtn" title="${_('View the selected table')}" data-bind="click: function () { window.open($root.optimizerUrl() + '#/table/' + selectedTables()[0].optimizerStats().eid, '_blank'); }, disable: selectedTables().length !== 1">
            <i class="fa fa-skyatlas"></i> ${_('View in Optimizer')}
          </button>
          <!-- /ko -->
        </div>

        <table id="tablesTable" class="table table-striped table-condensed table-nowrap" style="margin-bottom: 10px; width: 100%" data-bind="visible: filteredTables().length > 0">
          <thead>
          <tr>
            <th width="1%" style="text-align: center"><div class="hueCheckbox fa" data-bind="hueCheckAll: { allValues: filteredTables, selectedValues: selectedTables }"></div></th>
            <th>&nbsp;</th>
            <th width="30%">${ _('Table Name') }</th>
            <th width="48%">${ _('Comment') }</th>
            <!-- ko if: $root.optimizerEnabled  -->
            <th width="10%">${ _('Popularity') }</th>
            <th width="10%">${ _('Columns') }</th>
            <!-- /ko -->
            <th width="1%">${ _('Type') }</th>
          </tr>
          </thead>
          <tbody data-bind="hueach: {data: filteredTables, itemHeight: 29, scrollable: '.content-panel', scrollableOffset: 277, scrollUp: true}">
            <tr>
              <td width="1%" style="text-align: center">
                <div class="hueCheckbox fa" data-bind="multiCheck: '#tablesTable', value: $data, hueChecked: $parent.selectedTables"></div>
              </td>
              <td width="1%"><a class="blue" href="javascript:void(0)" data-bind="click: showContextPopover"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a></td>
              <td>
                <a class="tableLink" href="javascript:void(0);" data-bind="text: name, click: function() { $parent.setTable($data, function(){ huePubSub.publish('metastore.url.change'); }) }"></a>
              </td>
              <td style="text-overflow: ellipsis; overflow: hidden; max-width: 0" data-bind="text: comment, attr: {title: comment}"></td>
              <!-- ko if: $root.optimizerEnabled -->
                <!-- ko if: optimizerStats() -->
                <td>
                  <div class="progress" style="height: 10px; width: 70px; margin-top:5px;" data-bind="attr: {'title': optimizerStats().popularity}">
                    <div class="bar" style="background-color: #338bb8" data-bind="style: { 'width' : optimizerStats().popularity + '%' }"></div>
                  </div>
                </td>
                <td data-bind="text: optimizerStats().column_count"></td>
              <!-- /ko -->
              <!-- ko ifnot: optimizerStats() -->
                <td></td>
                <td></td>
              <!-- /ko -->
              <!-- /ko -->

              <td class="center">
                <!-- ko ifnot: $root.optimizerEnabled && optimizerStats() -->
                  <!-- ko if: type == 'Table' -->
                    <i class="fa fa-fw fa-table muted" title="${ _('Table') }"></i>
                  <!-- /ko -->
                  <!-- ko if: type == 'View' -->
                    <i class="fa fa-fw fa-eye muted" title="${ _('View') }"></i>
                  <!-- /ko -->
                <!-- /ko -->
                <!-- ko if: $root.optimizerEnabled && optimizerStats() -->
                  <!-- ko if: optimizerStats().is_fact -->
                    <i class="fa fa-fw muted fa-database" title="${ _('Fact table') }"></i>
                  <!-- /ko -->
                  <!-- ko ifnot: optimizerStats().is_fact -->
                    <i class="fa fa-fw muted fa-calendar" title="${ _('Dimension table') }"></i>
                  <!-- /ko -->
                <!-- /ko -->
              </td>
            </tr>
          </tbody>
        </table>
        <span data-bind="visible: filteredTables().length === 0, css: {'margin-left-10': tables().length > 0}" style="font-style: italic; display: none;">${_('No tables found.')}</span>
      </div>
    </div>

  % if has_write_access:
    <div id="dropTable" class="modal hide fade">
      <form data-bind="attr: { 'action': '/metastore/tables/drop/' + name }" method="POST">
        ${ csrf_token(request) | n,unicode }
        <div class="modal-header">
          <a href="#" class="close" data-dismiss="modal">&times;</a>
          <h3 id="dropTableMessage">${_('Do you really want to drop the selected table(s)?')}</h3>
        </div>
        <div class="modal-body">
          <label class="checkbox" style="display: inline-block; margin-top: 5px">
            <input type="checkbox" name="skip_trash" /> ${ _('Skip the trash') }
          </label>
        </div>
        <div class="modal-footer">
          <input type="button" class="btn" data-dismiss="modal" value="${_('No')}" />
          <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
        </div>
        <!-- ko foreach: selectedTables -->
        <input type="hidden" name="table_selection" data-bind="value: name" />
        <!-- /ko -->
      </form>
    </div>
  % endif
</script>

<script type="text/html" id="metastore-databases-parameters">
  <div data-bind="toggleOverflow: {height: 24}">
    <div class="inline margin-right-20"><i class="fa fa-fw fa-cog muted"></i></div>
    <!-- ko foreach: Object.keys($data) -->
      <div class="inline margin-right-20"><strong data-bind="text: $data"></strong>: <span data-bind="text: $parent[$data]"></span></div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="metastore-databases-actions">
  <div class="inline-block pull-right">
    <a class="inactive-action" href="javascript:void(0)" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function () { huePubSub.publish('assist.db.refresh', { sourceType: 'hive' }); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : $root.reloading }" title="${_('Refresh')}"></i></a>
    % if has_write_access:
    <a class="inactive-action margin-left-10" data-bind="tooltip: { placement: 'bottom', delay: 750 }" href="${ url('beeswax:create_database') }" title="${_('Create a new database')}"><i class="fa fa-plus"></i></a>
    % endif
  </div>
</script>

<script type="text/html" id="metastore-tables-actions">
  <div class="inline-block pull-right">
    <a class="inactive-action" href="javascript:void(0)" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function () { huePubSub.publish('assist.db.refresh', { sourceType: 'hive' }); }" title="${_('Refresh')}"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : $root.reloading }"></i></a>
    % if has_write_access:
    <a class="inactive-action margin-left-10" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'href': '/beeswax/create/import_wizard/' + database().name }" title="${_('Create a new table from a file')}"><span class="fa-stack fa-fw" style="width: 1.28571429em"><i class="fa fa-file-o fa-stack-1x"></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 5px; margin-top: 6px;"></i></span></a>
    <a class="inactive-action margin-left-10" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'href': '/beeswax/create/create_table/' + database().name }" title="${_('Create a new table manually')}"><i class="fa fa-plus"></i></a>
    % endif
  </div>
</script>

<script type="text/html" id="metastore-describe-table-actions">
  <div class="inline-block pull-right">
    <!-- ko with: database -->
    <!-- ko with: table -->
    % if USE_NEW_EDITOR.get():
      <a class="inactive-action" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'href': '/notebook/browse/' + database.name + '/' + name }" title="${_('Query the table')}"><i class="fa fa-pencil-square-o"></i></a>
    % else:
      <a class="inactive-action" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'href': '/metastore/table/'+ database.name + '/' + name + '/read' }" title="${_('Browse Data')}"><i class="fa fa-list"></i></a>
    % endif
    <a class="inactive-action margin-left-10" href="javascript:void(0)" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function () { huePubSub.publish('assist.db.refresh', { sourceType: 'hive' }); }" title="${_('Refresh')}"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : $root.reloading }"></i></a>
    <!-- ko if: $root.optimizerEnabled() && $root.database().table().optimizerStats() -->
      <a class="inactive-action margin-left-10" title="${_('View in Optimizer')}" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'href': $root.optimizerUrl() + '#/table/' + $root.database().table().optimizerStats().eid }" target="_blank"><i class="fa fa-skyatlas"></i></a>
    <!-- /ko -->
##     <a class="inactive-action margin-left-10" href="javascript: void(0);"><i class="fa fa-star"></i></a>
    % if has_write_access:
      <a class="inactive-action margin-left-10" href="#" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: showImportData, visible: tableDetails() && ! tableDetails().is_view" title="${_('Import Data')}"><i class="fa fa-upload"></i></a>
    % endif
    % if has_write_access:
      <a class="inactive-action margin-left-10" href="#dropSingleTable" data-toggle="modal" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'title' : tableDetails() && tableDetails().is_view ? '${_('Drop View')}' : '${_('Drop Table')}' }"><i class="fa fa-times"></i></a>
    % endif
    <!-- ko if: tableDetails() -->
      <a class="inactive-action margin-left-10" data-bind="tooltip: { placement: 'bottom', delay: 750 }, visible: tableDetails().hdfs_link, attr: {'href': tableDetails().hdfs_link, 'rel': tableDetails().path_location}" title="${_('View File Location')}"><i class="fa fa-fw fa-hdd-o"></i></a>
      <!-- ko if: tableDetails().partition_keys.length -->
      <a class="inactive-action margin-left-10" data-bind="tooltip: { placement: 'bottom', delay: 750 }, attr: { 'href': '/metastore/table/' + database.name + '/' + name + '/partitions' }" title="${_('Show Partitions')}"><i class="fa fa-sitemap"></i></a>
      <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="metastore-overview-tab">
  <div class="row-fluid margin-top-10">
    <div class="span3 tile">
      <!-- ko template: 'metastore-table-properties' --><!-- /ko -->
    </div>
    <div class="span3 tile">
      <!-- ko template: 'metastore-table-stats' --><!-- /ko -->
    </div>
    <!-- ko if: $root.navigatorEnabled() && navigatorStats() -->
    <div class="span6 tile">
      <h4>${ _('Tagging') }</h4>
      <div style="margin-top: 5px" data-bind="component: { name: 'nav-tags', params: {
        sourceType: 'hive',
        database: database.name,
        table: name
      } }"></div>
    </div>
    <!-- /ko -->
  </div>

  <div class="tile">
    <h4>${ _('Columns') } (<span data-bind="text: columns().length"></span>) <i data-bind="visible: loadingColumns" class="fa fa-spinner fa-spin" style="display: none;"></i></h4>
    <!-- ko with: favouriteColumns -->
    <!-- ko template: "metastore-columns-table" --><!-- /ko -->
    <!-- /ko -->

    <a class="pointer" data-bind="visible: columns().length >= 3, click: function() { $('li a[href=\'#columns\']').click(); }">
      ${_('View more...')}
    </a>
  </div>

  <div class="tile">
    <h4>${ _('Sample') } <i data-bind="visible: samples.loading" class='fa fa-spinner fa-spin' style="display: none;"></i></h4>
    <!-- ko with: samples -->
      <!-- ko if: loaded -->
        <!-- ko with: preview -->
        <!-- ko template: { if: rows().length, name: 'metastore-samples-table' } --><!-- /ko -->
        <a class="pointer" data-bind="visible: rows().length >= 3, click: function() { $('li a[href=\'#sample\']').click(); }"  style="display: none;">
          ${_('View more...')}
        </a>
        <!-- /ko -->
        <div data-bind="visible: !rows().length && metastoreTable.tableDetails().is_view" style="display: none;">${ _('The view does not contain any data.') }</div>
        <div data-bind="visible: !rows().length && !metastoreTable.tableDetails().is_view" style="display: none;">${ _('The table does not contain any data.') }</div>
      <!-- /ko -->
    <!-- /ko -->
  </div>

  <div class="tile" data-bind="visible: tableDetails() && tableDetails().partition_keys.length" style="display: none;">
    <!-- ko with: partitions -->
    <h4>${ _('Partitions') } <i data-bind="visible: loading" class='fa fa-spinner fa-spin' style="display: none;"></i></h4>
    <!-- ko if: loaded -->
    <!-- ko with: preview -->
    <!-- ko template: { if: values().length, name: 'metastore-partition-values-table' } --><!-- /ko -->
    <a class="pointer" data-bind="visible: values().length >= 3, click: function() { $('li a[href=\'#partitions\']').click(); }"  style="display: none;">
      ${_('View more...')}
    </a>
    <!-- /ko -->
    <span data-bind="visible: !values().length" style="display: none;">${ _('The partition does not contain any values') }</span>
    <!-- /ko -->
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="metastore-columns-tab">
  <!-- ko with: filteredColumns -->
  <!-- ko template: "metastore-columns-table" --><!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-partitions-tab">
  <!-- ko with: partitions -->
  <div class="tile" data-bind="visible: true" style="display: none;">
    <h4>${ _('Columns') }</h4>
    <!-- ko template: 'metastore-partition-columns-table' --><!-- /ko -->
  </div>
  <div class="tile" data-bind="visible: true" style="display: none;">
    <h4>${ _('Partitions') } <i data-bind="visible: loading" class='fa fa-spinner fa-spin' style="display: none;"></i></h4>
    <!-- ko if: loaded -->
    <!-- ko template: { if: values().length, name: 'metastore-partition-values-table' } --><!-- /ko -->
    <span data-bind="visible: !values().length" style="display: none;">${ _('The partition does not contain any values') }</span>
    <!-- /ko -->
  </div>
  <!-- /ko -->
  <a data-bind="attr: { 'href': '/metastore/table/' + database.name + '/' + name + '/partitions' }">${ _('View all') }</a>
</script>

<script type="text/html" id="metastore-sample-tab">
  <!-- ko with: samples -->
  <!-- ko if: loading -->
  <div class="empty-message">
    <i data-bind="visible: loading" class='fa fa-spinner fa-spin' style="display: none;"></i>
  </div>
  <!-- /ko -->
  <!-- ko if: loaded -->
  <!-- ko template: { if: rows().length, name: 'metastore-samples-table' } --><!-- /ko -->
  <div data-bind="visible: !rows().length && metastoreTable.tableDetails().is_view" style="display: none;" class="empty-message">${ _('The view does not contain any data.') }</div>
  <div data-bind="visible: !rows().length && !metastoreTable.tableDetails().is_view" style="display: none;" class="empty-message">${ _('The table does not contain any data.') }</div>
  <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-queries-tab">
  <br/>
  <i class="fa fa-spinner fa-spin" data-bind="visible: $root.loadingQueries"></i>
  <table data-bind="visible: ! loadingQueries() && $data.optimizerDetails().queryList().length > 0" class="table table-condensed">
    <thead>
    <tr>
      <th width="10%">${ _('Id') }</th>
      <th width="10%">${ _('Popularity') }</th>
      <th>${ _('Character') }</th>
      <th>${ _('Query') }</th>
      <th width="20%">${ _('Complexity') }</th>
      <th width="10%">${ _('Hive Compatible') }</th>
      <th width="10%">${ _('Impala Compatible') }</th>
    </tr>
    </thead>
    <tbody data-bind="hueach: {data: $data.optimizerDetails().queryList(), itemHeight: 29, scrollable: '.content-panel', scrollableOffset: 200}">
    <tr class="pointer" data-bind="click: function(){ window.open($root.optimizerUrl() + '#/query/' + qid(), '_blank'); }">
      <td data-bind="text: qid"></td>
      <td style="height: 10px; width: 70px; margin-top:5px;" data-bind="attr: {'title': queryCount()}">
        <div class="progress bar" style="background-color: #338bb8" data-bind="style: { 'width' : Math.round(queryCount() / $parent.optimizerDetails().queryCount() * 100) + '%' }"></div>
      </td>
      <td><code data-bind="text: queryChar"></code></td>
      <td><code data-bind="text: query().substring(0, 100) + '...'"></code></td>
      <td data-bind="text: complexity, css: {'alert-success': complexity() == 'Low', 'alert-warning': complexity() == 'Medium', 'alert-danger': complexity() == 'High'}" class="alert"></td>
      <td data-bind="text: hiveCompatible"></td>
      <td data-bind="text: impalaCompatible"></td>
    </tr>
    </tbody>
  </table>
  <div data-bind="visible: ! loadingQueries() && $data.optimizerDetails().queryList().length == 0" class="empty-message">
    ${ _('No queries found for the current table.') }
  </div>
</script>

<script type="text/html" id="metastore-details-tab">
  <!-- ko with: tableDetails -->
  <table class="properties-table">
    <tbody data-bind="foreach: properties">
      <!-- ko if: col_name.indexOf('#') === 0 -->
      <tr>
        <td colspan="3"><h4 data-bind="text: col_name.substring(1)"></h4></td>
      </tr>
      <!-- /ko -->
      <!-- ko ifnot: col_name.indexOf('#') === 0 -->
      <tr>
        <td class="property-name" data-bind="text: col_name || '&nbsp;'"></td>
        <td data-bind="text: data_type || '&nbsp;'"></td>
        <td data-bind="text: comment || '&nbsp;'"></td>
      </tr>
      <!-- /ko -->
    </tbody>
  </table>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-describe-table">
  <div class="clearfix"></div>

  % if has_write_access:
  <span data-bind="editable: comment, editableOptions: {enabled: true, placement: 'bottom', emptytext: '${ _ko('Add a description...') }', inputclass:'input-xlarge', rows: 10 }" class="editable editable-click editable-empty" data-type="textarea">
    ${ _('Add a description...') }
  </span>
  % else:
    <span data-bind="text: comment"></span>
  %endif


  <ul class="nav nav-pills margin-top-30">
    <li><a href="#overview" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-overview'); }">${_('Overview')}</a></li>
    <li><a href="#columns" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-columns'); }">${_('Columns')} (<span data-bind="text: columns().length"></span>)</a></li>
    <!-- ko if: tableDetails() && tableDetails().partition_keys.length -->
      <li><a href="#partitions" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-partitions'); }">${_('Partitions')} (<span data-bind="text: partitionsCountLabel"></span>)</a></li>
    <!-- /ko -->
    <li><a href="#sample" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-sample'); }">${_('Sample')}</a></li>
    <!-- ko if: $root.optimizerEnabled() -->
      <!-- ko if: $root.database().table().optimizerDetails() -->
      <li><a href="#permissions" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-permissions'); }">${_('Permissions')}</a></li>
      <li><a href="#queries" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-queries'); }">${_('Queries')} (<span data-bind="text: $root.database().table().optimizerDetails().queryCount"></span>)</a></li>
      <li><a href="#joins" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-joins'); }">${_('Joins')} (<span data-bind="text: $root.database().table().optimizerDetails().joinCount"></span>)</a></li>
      <!-- /ko -->
      <!-- ko if: $root.database().table().relationshipsDetails() -->
      <li><a href="#relationships" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-relationships'); }">${_('Relationships')} (<span data-bind="text: $root.database().table().relationshipsDetails().inputs().length + $root.database().table().relationshipsDetails().targets().length"></span>)</a></li>
      <!-- /ko -->
    <!-- /ko -->
    <li><a href="#details" data-toggle="tab" data-bind="click: function(){ $root.currentTab('table-details'); }">${ _('Details') }</a></li>
  </ul>

  <div class="tab-content margin-top-10" style="border: none; overflow: hidden">
    <div class="tab-pane" id="overview">
      <!-- ko if: $root.currentTab() == 'table-overview' -->
      <!-- ko template: 'metastore-overview-tab' --><!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="columns">
      <!-- ko if: $root.currentTab() == 'table-columns' -->
        <input class="input-xlarge search-query margin-left-10" type="text" placeholder="${ _('Search for a column...') }" data-bind="clearable: columnQuery, value: columnQuery, valueUpdate: 'afterkeydown'"/>
        <!-- ko template: 'metastore-columns-tab' --><!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="partitions">
      <!-- ko if: $root.currentTab() == 'table-partitions' -->
      <!-- ko template: 'metastore-partitions-tab' --><!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="sample">
      <!-- ko if: $root.currentTab() == 'table-sample' -->
      <!-- ko template: 'metastore-sample-tab' --><!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="permissions">
      <div class="acl-panel-content" style="height: 988px;">
        <div class="pull-right">
          <input class="input-medium no-margin" type="text" placeholder="Search privileges..."> &nbsp;
          <a class="btn pointer">
            <i class="fa fa-plus-circle"></i> Add role
          </a>
        </div>
        <h4 style="margin-top: 4px;">Privileges &nbsp;</h4>

      <div class="acl-block-title">
        <i class="fa fa-cube muted"></i> <a class="pointer"><span>customerFraud</span></a>
      </div>
      <div>
      <div class="acl-block acl-block-airy">
          <span class="muted" title="3 months ago">TABLE</span>
          <span>
            <a class="muted" target="_blank" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
          </span>
          <br>
          server=<span>server1</span>
            <span>
              <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" title="Browse db privileges"><span data-bind="text: $root.database().name"></span></a>
            </span>
            <span>
              <i class="fa fa-long-arrow-right"></i> table=<a class="pointer" title="Browse table privileges"><span data-bind="text: name"></span></a>
            </span>
            <span style="display: none;">
              <i class="fa fa-long-arrow-right"></i> column=<a class="pointer" title="Browse column privileges"><span></span></a>
            </span>

          <i class="fa fa-long-arrow-right"></i> action=INSERT
      </div>

      <div class="acl-block acl-block-airy">
        <span class="muted" title="3 months ago">TABLE</span>

        <span>
          <a class="muted" target="_blank" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
        </span>
        <br>

        server=server1

          <span>
            <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" title="Browse db privileges"><span data-bind="text: $root.database().name"></span></a>
          </span>
          <span>
            <i class="fa fa-long-arrow-right"></i> table=<a class="pointer" title="Browse table privileges"><span data-bind="text: name"></span></a>
          </span>
          <span style="display: none;">
            <i class="fa fa-long-arrow-right"></i> column=<a class="pointer" title="Browse column privileges"><span></span></a>
          </span>

          <i class="fa fa-long-arrow-right"></i> action=<span>SELECT</span>
      </div>
    </div>
    <div class="acl-block acl-actions">
      <span class="pointer" title="Show 50 more..." style="display: none;"><i class="fa fa-ellipsis-h"></i></span>
      <span class="pointer" title="Add privilege"><i class="fa fa-plus"></i></span>
      <span class="pointer" title="Undo" style="display: none;"> &nbsp; <i class="fa fa-undo"></i></span>
      <span class="pointer" title="Save" style="display: none;"> &nbsp; <i class="fa fa-save"></i></span>
    </div>

    <div class="acl-block-title">
      <i class="fa fa-cube muted"></i> <a class="pointer"><span>customerAccess</span></a>
    </div>
    <div>
      <div class="acl-block acl-block-airy">
        <span class="muted" title="3 months ago">TABLE</span>

        <span>
          <a class="muted" target="_blank" style="margin-left: 4px" title="Open in Sentry" href="/security/hive"><i class="fa fa-external-link"></i></a>
        </span>
        <br>

        server=server1

          <span>
            <i class="fa fa-long-arrow-right"></i> db=<a class="pointer" title="Browse db privileges"><span data-bind="text: $root.database().name"></span></a>
          </span>
          <span>
            <i class="fa fa-long-arrow-right"></i> table=<a class="pointer" title="Browse table privileges"><span data-bind="text: name"></span></a>
          </span>
          <span style="display: none;">
            <i class="fa fa-long-arrow-right"></i> column=<a class="pointer" title="Browse column privileges"><span></span></a>
          </span>

        <i class="fa fa-long-arrow-right"></i> action=<span>ALL</span>
      </div>
      <div class="acl-block acl-actions">
        <span class="pointer" title="Show 50 more..." style="display: none;"><i class="fa fa-ellipsis-h"></i></span>
        <span class="pointer" title="Add privilege"><i class="fa fa-plus"></i></span>
        <span class="pointer" title="Undo" style="display: none;"> &nbsp; <i class="fa fa-undo"></i></span>
        <span class="pointer" title="Save" style="display: none;"> &nbsp; <i class="fa fa-save"></i></span>
      </div>
    </div>
  </div>

    <style>
    .acl-panel {
      border-left: 1px solid #e5e5e5;
      padding-top: 6px;
      padding-left: 12px;
    }

    .acl-panel .nav-tabs {
      margin-bottom: 0;
    }

    .acl-panel h4:not(:first-child) {
      margin-top: 20px;
    }

    .acl-panel-content {
      padding: 6px;
      overflow-y: scroll;
    }

    .acl-block-title {
      background-color: #eeeeee;
      font-weight: bold;
      padding: 3px;
      margin-top: 14px;
      margin-bottom: 4px;
    }

    .acl-block {
      background-color: #f6f6f6;
      padding: 3px;
      margin-bottom: 4px;
    }

    .acl-block .checkbox, .acl-block .radio {
      margin-left: 6px;
    }

    .acl-block-airy {
      padding: 6px;
    }

    .acl-block-airy input {
      margin-bottom: 0;
    }

    .acl-block-section {
      margin-top: 10px;
    }

    .acl-block-section input {
      margin-left: 14px;
    }

    .span6 .acl-block input[type='text'] {
      width: 25%;
    }

    .span6 .acl-block input[type='text'] {
      width: 21%;
    }

    .acl-actions {
      padding: 5px;
      text-align: center;
      color: #CCC;
      font-size: 20px;
    }

    .acl-actions span:hover {
      color: #999;
    }
    </style>
    </div>

    <div class="tab-pane" id="queries">
      <!-- ko if: $root.optimizerEnabled() && $root.currentTab() == 'table-queries' -->
        <!-- ko template: {name: 'metastore-queries-tab', data: $root.database().table()} --><!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="joins">
      <!-- ko if: $root.optimizerEnabled() && $root.database().table().optimizerDetails() -->
      <!-- ko with: $root.database().table().optimizerDetails().joinTables -->
        <table data-bind="visible: $data.length > 0" class="table table-condensed">
          <thead>
          <tr>
            <th width="10%">${ _('Id') }</th>
            <th width="10%">${ _('Popularity') }</th>
            <th width="30%">${ _('Table Name') }</th>
            <th>${ _('Join Column') }</th>
            <th width="10%">${ _('Join counts') }</th>
          </tr>
          </thead>
          <tbody data-bind="hueach: {data: $data, itemHeight: 29, scrollable: '.content-panel', scrollableOffset: 200}">
          <tr>
            <td class="pointer" data-bind="text: tableEid, click: function(){ window.open($root.optimizerUrl() + '#/table/' + tableEid(), '_blank'); }"></td>
            <td style="height: 10px; width: 70px; margin-top:5px;" data-bind="attr: {'title': joinpercent()}">
              <div class="progress bar" style="background-color: #338bb8" data-bind="style: { 'width' : joinpercent() + '%' }"></div>
            </td>
            <td><a data-bind="text: tableName, attr: { href: '/metastore/table/' + $root.database().name + '/' + tableName() }"</a></td>
            <td class="pointer"><code data-bind="text: joinColumns, click: scrollToColumn"></code></td>
            <td data-bind="text: numJoins"></td>
          </tr>
          </tbody>
        </table>
        <!-- /ko -->
        <!-- /ko -->
    </div>

    <div class="tab-pane" id="relationships">
      <!-- ko if: $root.currentTab() == 'table-relationships' && $root.database().table().relationshipsDetails() -->
      <!-- ko with: $root.database().table().relationshipsDetails() -->
        <h4>${ _('Inputs') }</h4>
        <div class="row-fluid">
           <!-- ko foreach: inputs -->
             <div data-bind="text: $data"></div>
           <!-- /ko -->
         <!-- ko if: inputs().length == 0 -->
           ${ _('Not inputs') }
         <!-- /ko -->
        </div>

        </br>

        <h4>${ _('Targets') }</h4>
        <div class="row-fluid">
         <!-- ko foreach: targets -->
           <div data-bind="text: $data"></div>
         <!-- /ko -->
         <!-- ko if: targets().length == 0 -->
           ${ _('Not targets') }
         <!-- /ko -->
        </div>

        </br>

       <h4>${ _('Source query') }</h4>
       <div class="row-fluid">
          <!-- ko if: source_query().length > 0 -->
            <code data-bind="text: source_query"></code>
          <!-- /ko -->
          <!-- ko if: source_query().length == 0 -->
            ${ _('No source query') }
          <!-- /ko -->
        </div>

        </br>

        <h4>${ _('Target queries') }</h4>
        <div class="row-fluid">
          <!-- ko foreach: target_queries -->
            <div>
              <code data-bind="text: $data"></code>
            </div>
          <!-- /ko -->
          <!-- ko if: target_queries().length == 0 -->
          ${ _('Not target queries') }
         <!-- /ko -->
        </div>

        </br>

        <h4>${ _('Lineage') }</h4>
        <div class="row-fluid">
          <button class="btn toolbarBtn" title="${_('Open in Navigator ')}" data-bind="click: function () { window.open($root.navigatorUrl() + '?view=detailsView&id=' + id() + '&b=rFlCX&tab=lineage', '_blank'); }">
            <i class="fa fa-skyatlas"></i> ${_('View in Navigator')}
          </button>
        </div>
      <!-- /ko -->
      <!-- /ko -->
    </div>

    <div class="tab-pane" id="details">
      <!-- ko if: $root.currentTab() == 'table-details' -->
      <!-- ko template: 'metastore-details-tab' --><!-- /ko -->
      <!-- /ko -->
    </div>
  </div>
</script>

<span id="metastoreComponents">
  % if not is_embeddable:
  <a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function () { $root.isLeftPanelVisible(true); }">
    <i class="fa fa-chevron-right"></i>
  </a>
  % endif

  <div class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
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
                  openItem: true,
                  showStats: true
                }
              },
              visibleAssistPanels: ['sql']
            }
          }"></div>
      </div>
      <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>
      % endif
      <div class="content-panel" data-bind="niceScroll">
        <div class="metastore-main">
          <h3>
            <!-- ko template: { if: database() !== null && database().table() !== null, name: 'metastore-describe-table-actions' }--><!-- /ko -->
            <!-- ko template: { if: database() !== null && database().table() === null, name: 'metastore-tables-actions' }--><!-- /ko -->
            <!-- ko template: { if: database() === null, name: 'metastore-databases-actions' }--><!-- /ko -->
            <!-- ko template: 'metastore-breadcrumbs' --><!-- /ko -->
          </h3>
          <i data-bind="visible: loading" class="fa fa-spinner fa-spin fa-2x margin-left-10" style="color: #999; display: none;"></i>
          <!-- ko template: { if: !loading() && database() === null, name: 'metastore-databases' } --><!-- /ko -->
          <!-- ko with: database -->
          <i data-bind="visible: loading" class="fa fa-spinner fa-spin fa-2x margin-left-10" style="color: #999; display: none;"></i>
          <!-- ko template: { if: !loading() && table() === null, name: 'metastore-tables' } --><!-- /ko -->
          <!-- ko with: table -->
            <!-- ko template: 'metastore-describe-table' --><!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
    </div>
  </div>

  <div id="dropSingleTable" class="modal hide fade">
    <form method="POST">
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Drop Table')}</h3>
      </div>
      <div class="modal-body">
        <div>${_('Do you really want to drop the table')} <span style="font-weight: bold;" data-bind="text: database() && database().table() ? database().table().name : ''"></span>?</div>
      </div>
      <div class="modal-footer">
        <input type="hidden" name="table_selection" data-bind="value: database() && database().table() ? database().table().name : ''" />
        <input type="button" class="btn" data-dismiss="modal" value="${_('No')}"/>
        <input type="submit" data-bind="click: function (vm, e) { var $form = $(e.target).parents('form'); $form.attr('action', '/metastore/tables/drop/' + vm.database().name); return true; }" class="btn btn-danger" value="${_('Yes, drop this table')}"/>
      </div>
    </form>
  </div>

  <div id="import-data-modal" class="modal hide fade" style="display: block;width: 640px;margin-left: -320px!important;"></div>
</div>
</span>
<script type="text/javascript" charset="utf-8">

  function pieChartDataTransformer(rawDatum) {
    var _data = [];
    $(rawDatum.counts).each(function (cnt, item) {
      _data.push({
        label: item.name,
        value: item.popularity,
        obj: item
      });
    });
    _data.sort(function (a, b) {
      return a.value - b.value
    });

    return _data;
  }

  (function () {

    ko.options.deferUpdates = true;

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        % if is_embeddable:
        responsive: true,
        % endif
        i18n: {
          errorFetchingTableDetails: '${_('An error occurred fetching the table details. Please try again.')}',
          errorFetchingTableFields: '${_('An error occurred fetching the table fields. Please try again.')}',
          errorFetchingTableSample: '${_('An error occurred fetching the table sample. Please try again.')}',
          errorRefreshingTableStats: '${_('An error occurred refreshing the table stats. Please try again.')}',
          errorLoadingDatabases: '${ _('There was a problem loading the databases. Please try again.') }',
          errorLoadingTablePreview: '${ _('There was a problem loading the table preview. Please try again.') }'
        },
        optimizerEnabled: '${ is_optimizer_enabled }' === 'True',
        navigatorEnabled: '${ is_navigator_enabled }' === 'True',
        optimizerUrl: '${ optimizer_url }',
        navigatorUrl: '${ navigator_url }',
        partitionsLimit: ${ LIST_PARTITIONS_LIMIT.get() }
      };

      var viewModel = new MetastoreViewModel(options);

      huePubSub.subscribe('metastore.scroll.to.top', function () {
        $(".content-panel").scrollTop(0);
        $('.content-panel').getNiceScroll().resize();
      });

      viewModel.currentTab.subscribe(function(tab){
        if (tab == 'table-relationships') {
          // viewModel.database().table().getRelationships();
        } else if (tab == 'table-sample') {
          var selector = '#sample .sample-table';
          if ($(selector).parents('.dataTables_wrapper').length == 0){
            hueUtils.waitForRendered(selector, function(el){ return el.find('td').length > 0 }, function(){
              $(selector).dataTable({
                "bPaginate": false,
                "bLengthChange": false,
                "bInfo": false,
                "bDestroy": true,
                "bFilter": false,
                "bAutoWidth": false,
                "oLanguage": {
                  "sEmptyTable": "${_('No data available')}",
                  "sZeroRecords": "${_('No matching records')}"
                },
                "fnDrawCallback": function (oSettings) {
                  $(selector).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
                  $(selector).jHueTableExtender({
                    fixedHeader: true,
                    fixedFirstColumn: true,
                    includeNavigator: false,
                    parentId: 'sample',
                    classToRemove: 'sample-table',
                    mainScrollable: '.content-panel',
                    stickToTopPosition: 73,
                    clonedContainerPosition: "fixed"
                  });
                  $(selector).jHueHorizontalScrollbar();
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
            });
          }
        }
        $('.content-panel').getNiceScroll().resize();
      });

      ko.applyBindings(viewModel, $('#metastoreComponents')[0]);

      if (location.getParameter('refresh') === 'true') {
        huePubSub.publish('assist.db.refresh', { sourceType: 'hive' });
        hueUtils.replaceURL('?');
      }

      window.scrollToColumn = function (col) {
        if (!col.table.samples.loading()) {
          $('a[href="#sample"]').click();
          window.setTimeout(function () {
            var sampleTable = $('#sample').find('table');
            var sampleCol = sampleTable.find('th').filter(function () {
              return $.trim($(this).text()).indexOf(col.name()) > -1;
            });
            sampleTable.find('.columnSelected').removeClass('columnSelected');
            sampleTable.find('tr td:nth-child(' + (sampleCol.index() + 1) + ')').addClass('columnSelected');
            var scrollLeft = 0;
            sampleTable.find('th:lt(' + sampleCol.index() + ')').each(function () {
              scrollLeft += $(this).outerWidth();
            });
            sampleTable.parent().scrollLeft(scrollLeft);
          }, 200);
        }
      }

    });
  })();
</script>
</span>
% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
