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
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter, _ko
from beeswax.conf import LIST_PARTITIONS_LIMIT
from webpack_loader.templatetags.webpack_loader import render_bundle

from metastore.conf import ENABLE_NEW_CREATE_TABLE
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="components" file="components.mako" />

<%
MAIN_SCROLLABLE = is_embeddable and ".page-content" or ".content-panel"
if conf.CUSTOM.BANNER_TOP_HTML.get():
  TOP_SNAP = is_embeddable and "82px" or "108px"
else:
  TOP_SNAP = is_embeddable and "52px" or "78px"
%>

% if not is_embeddable:
${ commonheader(_("Metastore"), app_name, user, request) | n,unicode }

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>

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

<script src="${ static('beeswax/js/stats.utils.js') }"></script>

<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">

${ render_bundle('tableBrowser') | n,unicode }

<span class="notebook">

${ components.menubar(is_embeddable) }

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">

<script type="text/html" id="metastore-breadcrumbs">
  <div style="font-size: 14px; margin: 0 12px; line-height: 27px;">
    <!-- ko if: sources().length >= 2 -->
    <div data-bind="component: { name: 'hue-drop-down', params: { value: source, entries: sources, onSelect: sourceChanged, labelAttribute: 'name', searchable: true, linkTitle: '${ _ko('Source') }' } }"
      style="display: inline-block">
    </div>
    <!-- /ko -->
    <!-- ko with: source -->
    <!-- ko if: window.HAS_MULTI_CLUSTER -->
    <!-- ko if: namespaces().length === 0 -->
    <i class="margin-left-10 fa fa-warning"></i> ${ _('No namespaces found') }
    <!-- /ko -->
    <!-- ko if: namespaces().length > 0 -->
    <div class="margin-left-10" data-bind="component: { name: 'hue-drop-down', params: { value: namespace, entries: namespaces, onSelect: namespaceChanged, labelAttribute: 'name', searchable: true, linkTitle: '${ _ko('Namespace') }' } }"
      style="display: inline-block">
    </div>
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
  </div>
  <ul style="padding-top: 0" class="nav nav-pills hue-breadcrumbs-bar" id="breadcrumbs">
    <!-- ko with: source -->
    <!-- ko with: namespace -->
    <li>
      <a href="javascript:void(0);" data-bind="click: $root.databasesBreadcrumb">${_('Databases')}
        <!-- ko if: database -->
        <span class="divider">&gt;</span>
        <!-- /ko -->
      </a>
    </li>
    <!-- ko with: database -->
    <li>
      <a href="javascript:void(0);" data-bind="click: $root.tablesBreadcrumb">
        <span data-bind="text: catalogEntry.name"></span>
        <!-- ko with: table -->
        <span class="divider">&gt;</span>
        <!-- /ko -->
      </a>
    </li>
    <!-- ko with: table -->
    <li class="editable-breadcrumbs" title="${_('Edit path')}" data-bind="click: function(){ $parent.editingTable(true); }, visible: !$parent.editingTable()">
      <a href="javascript:void(0)" data-bind="text: catalogEntry.name"></a>
    </li>
    <!-- /ko -->
    <!-- ko if: editingTable -->
      <!-- ko with: table -->
      <li class="editable-breadcrumb-input">
        <input type="text" data-bind="hiveChooser: { data: catalogEntry.name, database: $parent.catalogEntry.name, namespace: $parent.catalogEntry.namespace, compute: $parent.catalogEntry.compute, skipColumns: true, searchEverywhere: true, onChange: function(val) { $parent.setTableByName(val); $parent.editingTable(false); }, apiHelperUser: '${ user }', apiHelperType: $root.source().type }" autocomplete="off" />
      </li>
      <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
  </ul>
</script>

<script type="text/html" id="metastore-partition-columns-table">
  <div style="overflow-x: auto; overflow-y: hidden">
    <table class="table table-condensed table-nowrap metastore-table">
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
    <table id="partitionsTable" class="table table-condensed table-nowrap metastore-table">
      <thead>
        <tr>
          <th style="width: 1%" class="vertical-align-middle">
            <!-- ko ifnot: $data.withDrop -->
            &nbsp;
            <!-- /ko -->
            <!-- ko if: $data.withDrop -->
            <div class="hue-checkbox fa" data-bind="hueCheckAll: { allValues: $data.values, selectedValues: $data.selectedValues }"></div>
            <!-- /ko -->
          </th>
          <th>${_('Values')}</th>
          <th>${_('Spec')}</th>
          <th data-bind="visible: $root.source().type !== 'impala'">${_('Browse')}</th>
        </tr>
      </thead>
      <tbody>
      <!-- ko foreach: $data.values -->
      <tr>
        <td>
          <!-- ko ifnot: $parent.withDrop -->
            <span data-bind="text: $index() + 1"></span>
          <!-- /ko -->
          <!-- ko if: $parent.withDrop -->
          <div class="hue-checkbox fa" data-bind="multiCheck: '#partitionsTable', value: $data, hueChecked: $parent.selectedValues"></div>
          <!-- /ko -->
        </td>
        <td title="${_('Query partition data')}">
          <a data-bind="click: function() { queryAndWatchUrl(notebookUrl, $root.source().type); }, text: '[\'' + columns.join('\',\'') + '\']'" href="javascript:void(0)"></a>
        </td>
        <td data-bind="text: partitionSpec"></td>
        <td data-bind="visible: $root.source().type != 'impala'">
          <a data-bind="click: function () { browsePartitionFolder(browseUrl); }" href="javascript:void(0)" title="${_('Browse partition files')}">
            ${_('Files')}
          </a>
        </td>
      </tr>
      <!-- /ko -->
      </tbody>
    </table>
  </div>
</script>

<script type="text/html" id="metastore-samples-table">
  <div data-bind="delayedOverflow">
    <table id="sampleTable" class="table table-condensed table-nowrap sample-table old-datatable metastore-table">
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
            <td data-bind="text: $index() + 1"></td>
            <!-- ko foreach: $data -->
              <td data-bind="html: $data"></td>
            <!-- /ko -->
          </tr>
        <!-- /ko -->
      </tbody>
    </table>
  </div>

  <div id="jumpToColumnAlert" class="alert hide" style="margin-top: 12px;">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>${_('Did you know?')}</strong>
    <ul>
      <li>${ _('If the sample contains a large number of columns, click a row to select a column to jump to') }</li>
    </ul>
  </div>
</script>

<script type="text/html" id="metastore-table-properties">
  <!-- ko with: tableDetails -->
  <h4>${ _('Properties') } <i data-bind="visible: $parent.loadingDetails()" class="fa fa-spinner fa-spin" style="display: none;"></i></h4>
  <div class="row-fluid">
    <div class="metastore-property">
      <!-- ko if: $parent.catalogEntry.isView() -->
        ${ _('View') }
      <!-- /ko -->
      <!-- ko ifnot: $parent.catalogEntry.isView() -->
        <span data-bind="visible: partition_keys.length" style="display: none;">
          <a class="pointer" data-bind="click: function() { $root.currentTab('partitions'); $('.page-content').scrollTop(0); }">
            ${ _("Partitioned") }
          </a>
        </span>
        ${ _('Table') }
      <!-- /ko -->
    </div>
    <!-- ko ifnot: $parent.catalogEntry.isView() -->
    <div class="metastore-property">
      <!-- ko if: details.properties.table_type == 'MANAGED_TABLE' -->
        ${_('Managed')}
      <!-- /ko -->
      <!-- ko if: details.properties.table_type == 'EXTERNAL_TABLE' -->
        ${_('External')}
      <!-- /ko -->
      ${_('and stored in')}
      <!-- ko if: details.properties.format === 'kudu' -->
        <div>${_('Kudu')}</div>
        <!-- /ko -->
        <!-- ko if: details.properties.format !== 'kudu' -->
        <div>
          <a href="javascript: void(0);" data-bind="storageContextPopover: { path: hdfs_link.replace('/filebrowser/view=', ''), offset: { left: 5 } }"> ${_('location')}</a>
        </div>
      <!-- /ko -->
    </div>
    <!-- /ko -->
    <div class="metastore-property">
      ${ _('Created by') }
      <span data-bind="text: details.properties.owner"></span>
      ${ _('on') }
      <span data-bind="text: localeFormat(details.properties.create_time) != 'Invalid Date' ? localeFormat(details.properties.create_time) : details.properties.create_time"></span>
    </div>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-table-stats">
  <!-- ko if: catalogEntry.isTable() -->
    <!-- ko with: tableDetails -->
    <h4>${ _('Stats') }
      <!-- ko ifnot: partition_keys.length -->
        % if has_write_access:
        <!-- ko if: $parent.refreshingTableStats -->
        <i class="fa fa-refresh fa-spin"></i>
        <!-- /ko -->
        <!-- ko ifnot: $parent.refreshingTableStats() -->
        <a class="pointer" href="javascript: void(0);" data-bind="click: $parent.refreshTableStats"><i class="fa fa-refresh"></i></a>
        <!-- /ko -->
        % endif
        <span data-bind="visible: details.stats.COLUMN_STATS_ACCURATE == 'false'" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }"><i class="fa fa-exclamation-triangle"></i></span>
      <!-- /ko -->
    </h4>
    <div class="row-fluid">
      <!-- ko with: $parent.tableStats -->
        <!-- ko if: typeof numFiles !== 'undefined' && typeof last_modified_by === 'undefined' -->
          <span class="metastore-property">
            <div>${ _('Files') }</div>
            <div data-bind="text: numFiles"></div>
          </span>
        <!-- /ko -->
        <!-- ko if: typeof numRows !== 'undefined' -->
          <span class="metastore-property">
            <div>${ _('Rows') }</div>
            <div data-bind="text: numRows"></div>
          </span>
        <!-- /ko -->
        <!-- ko if: typeof totalSize !== 'undefined' && typeof last_modified_by === 'undefined' -->
          <span class="metastore-property">
            <div>${ _('Total size') }</div>
            <div data-bind="text: filesize(totalSize)"></div>
          </span>
        <!-- /ko -->
        <!-- ko if: typeof transient_lastDdlTime !== 'undefined' -->
          <div class="metastore-property">
            ${ _('Data last updated on') }
            <span data-bind="text: localeFormat(transient_lastDdlTime * 1000)"></span>
          </div>
        <!-- /ko -->
        <!-- ko if: typeof last_modified_time !== 'undefined' -->
          <div class="metastore-property">
            ${ _('Schema last modified on') }
            <span data-bind="text: localeFormat(last_modified_time*1000)"></span>
            ${ _('by') }
            <span data-bind="text: last_modified_by"></span>
          </div>
        <!-- /ko -->
      <!-- /ko -->
    </div>
    <!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-databases">
  <div class="entries-table-container">
    <div class="actionbar-actions">
      % if has_write_access:
        <button class="btn toolbarBtn margin-left-20" title="${_('Drop the selected databases')}" data-bind="click: function () { $('#dropDatabase').modal('show'); }, disable: selectedDatabases().length === 0"><i class="fa fa-times"></i>  ${_('Drop')}</button>
        <div id="dropDatabase" class="modal hide fade">

        % if is_embeddable:
          <form action="/metastore/databases/drop" data-bind="submit: dropAndWatch" method="POST">
            <input type="hidden" name="is_embeddable" value="true"/>
            <input type="hidden" name="start_time" value=""/>
            <input type="hidden" name="source_type" data-bind="value: $root.source().type"/>
            <!-- ko with: catalogEntry -->
            <input type="hidden" name="namespace" data-bind="value: JSON.stringify(namespace)"/>
            <input type="hidden" name="cluster" data-bind="value: JSON.stringify(compute)"/>
            <!-- /ko -->
        % else:
          <form id="dropDatabaseForm" action="/metastore/databases/drop" method="POST">
        % endif
            ${ csrf_token(request) | n,unicode }
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
              <h2 id="dropDatabaseMessage" class="modal-title">${ _('Do you really want to delete the following database(s)?') }</h2>
            </div>
            <div class="modal-body">
              <ul data-bind="foreach: selectedDatabases">
                <li>
                  <span data-bind="text: catalogEntry().name"></span>
                </li>
              </ul>
            </div>
            <div class="modal-footer">
              <div class="label label-important margin-top-5 pull-left">${ _('Warning: This will drop all tables and objects within the database.') }</div>
              <input type="button" class="btn" data-dismiss="modal" value="${_('No')}">
              <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
            </div>
            <!-- ko foreach: selectedDatabases -->
            <input type="hidden" name="database_selection" data-bind="value: catalogEntry().name" />
            <!-- /ko -->
          </form>
        </div>

        % if is_embeddable:
          <button href="javascript: void(0);" class="btn btn-default" data-bind="publish: { 'open.link': '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }' + '/?sourceType=' + catalogEntry().getSourceType() + '&namespace=' + catalogEntry().namespace.id + '&compute=' + catalogEntry().compute.id  }" title="${_('Create a new database')}"><i class="fa fa-plus"></i> ${_('New')}</button>
        % elif ENABLE_NEW_CREATE_TABLE.get():
          <button class="btn btn-default" data-bind="attr: { 'href': '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }' + '/?sourceType=' + catalogEntry().getSourceType() + '&namespace=' + catalogEntry().namespace.id + '&compute=' + catalogEntry().compute.id }" title="${_('Create a new database')}"><i class="fa fa-plus"></i> ${_('New')}</button>
        % else:
          <button href="${ url('beeswax:create_database') }" class="btn btn-default" title="${_('Create a new database')}"><i class="fa fa-plus"></i> ${_('New')}</button>
        % endif
      % endif
    </div>

    <div class="entries-table-no-header">
      <!-- ko if: catalogEntry() -->
      <!-- ko component: { name: 'catalog-entries-list', params: { catalogEntry: catalogEntry(), contextPopoverEnabled: true, onClick: onDatabaseClick.bind($data), selectedEntries: selectedDatabases, editableDescriptions: /true/i.test('${ has_write_access }') } } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </div>
</script>

<script type="text/html" id="metastore-td-description">
  <!-- ko ifnot: window.HAS_READ_ONLY_CATALOG -->
  <div data-bind="visibleOnHover: { selector: '.editable-inline-action' }">
    <div data-bind="editable: comment, editableOptions: {
        mode: 'inline',
        enabled: true,
        type: 'textarea',
        showbuttons: 'bottom',
        inputclass: 'hue-table-browser-desc-input',
        toggle: 'manual',
        toggleElement: '.toggle-editable',
        placeholder: '${ _ko('Add a description...') }',
        emptytext: '${ _ko('Add a description...') }',
        inputclass: 'hue-table-browser-desc-input',
        rows: 6,
        inlineEditAction: { editClass: 'toggle-editable editable-inline-action' },
        multiLineEllipsis: { overflowHeight: '40px', expandable: true, expandActionClass: 'editable-inline-action' }
      }">
      ${ _('Add a description...') }</div>
  </div>
  <!-- /ko -->
  <!-- ko if: window.HAS_READ_ONLY_CATALOG -->
  <span style="white-space: pre;" data-bind="text: comment"></span>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-main-description">
  <!-- ko if: $root.navigatorEnabled() && !window.HAS_READ_ONLY_CATALOG -->
  <div class="hue-table-browser-desc-container" data-bind="visibleOnHover: { selector: '.editable-inline-action' }">
    <div class="hue-table-browser-desc">
      <div data-bind="editable: comment, editableOptions: {
        mode: 'inline',
        enabled: true,
        type: 'textarea',
        showbuttons: 'bottom',
        inputclass: 'hue-table-browser-desc-input',
        toggle: 'manual',
        toggleElement: '.toggle-editable',
        placeholder: '${ _ko('Add a description...') }',
        emptytext: '${ _ko('No description available') }',
        rows: 8,
        inlineEditAction: { editClass: 'toggle-editable editable-inline-action' },
        multiLineEllipsis: { overflowHeight: '120px', expandable: true, expandActionClass: 'editable-inline-action', inlineEditAction: true },
      }" class="inline-block">
        ${ _('Add a description...') }
      </div>
    </div>
  </div>
  <!-- /ko -->
  <!-- ko if: !$root.navigatorEnabled() || window.HAS_READ_ONLY_CATALOG -->
  <div data-bind="text: comment, attr: { title: comment }" class="table-description"></div>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-nav-tags">
  <!-- ko if: $root.navigatorEnabled()  -->
  <div class="metastore-nav-tags" data-bind="component: { name: 'nav-tags', params: { catalogEntry: catalogEntry }}"></div>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-nav-properties">
  <!-- ko if: $root.navigatorEnabled()  -->
  <div data-bind="component: { name: 'nav-properties', params: { catalogEntry: catalogEntry }}"></div>
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-tables">
  <div class="row-fluid">
    <!-- ko if: $root.navigatorEnabled() -->
    <!-- ko template: 'metastore-main-description' --><!-- /ko -->
    <!-- ko template: 'metastore-nav-tags' --><!-- /ko -->
    <!-- ko template: 'metastore-nav-properties' --><!-- /ko -->
    <!-- /ko -->

    <!-- ko with: stats  -->
    <div class="span12 tile" style="margin: 5px 10px;">
      <div class="span6 tile">
        <h4>${ _('Properties') }</h4>
        <div>
          <div class="metastore-property">
            <div>${ _('Owner') }</div>
            <div><span data-bind="text: owner_name ? owner_name : '${ _ko('None') }'"></span> <span data-bind="visible: owner_type">(<span data-bind="text: owner_type"></span>)</span></div>
          </div>
          <div class="metastore-property">
            <div>${ _('Location') }</div>
            <div>
              <a href="javascript: void(0);" data-bind="storageContextPopover: { path: hdfs_link.replace('/filebrowser/view=', ''), offset: { left: 5 } }"> ${_('Location')}</a>
            </div>
          </div>
        </div>
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
  </div>

  <div class="row-fluid">
    <div class="span12 tile entries-table-container">
      <h4 class="entries-table-header">${ _('Tables') }</h4>
      <div class="actionbar-actions">
        <button class="btn toolbarBtn margin-left-20" title="${_('Browse the selected table')}" data-bind="click: function () { onTableClick(selectedTables()[0].catalogEntry()); selectedTables([]); }, disable: selectedTables().length !== 1"><i class="fa fa-eye"></i> ${_('View')}</button>
        <button class="btn toolbarBtn" title="${_('Query the selected table')}" data-bind="click: function () { queryAndWatch(selectedTables()[0].catalogEntry()) }, disable: selectedTables().length !== 1">
          <i class="fa fa-play fa-fw"></i> ${_('Query')}
        </button>
        % if has_write_access:
          <button id="dropBtn" class="btn toolbarBtn" title="${_('Drop the selected tables')}" data-bind="click: function () { $('#dropTable').modal('show'); }, disable: selectedTables().length === 0"><i class="fa fa-times"></i>  ${_('Drop')}</button>
          % if is_embeddable:
            <button href="javascript: void(0);" class="btn btn-default" data-bind="publish: { 'open.link': '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + catalogEntry.name + '/?sourceType=' + catalogEntry.getSourceType() + '&namespace=' + catalogEntry.namespace.id + '&compute=' + catalogEntry.compute.id }" title="${_('Create a new table')}"><i class="fa fa-plus"></i> ${_('New')}</button>
          % elif ENABLE_NEW_CREATE_TABLE.get():
            <button class="btn btn-default" data-bind="attr: { 'href': '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + catalogEntry.name + '/?sourceType=' + catalogEntry.getSourceType() + '&namespace=' + catalogEntry.namespace.id + '&compute=' + catalogEntry.compute.id }" title="${_('Create a new table')}"><i class="fa fa-plus"></i> ${_('New')}</button>
          % else:
            <button class="btn btn-default" data-bind="attr: { 'href': '/beeswax/create/import_wizard/' + catalogEntry.name }" title="${_('Create a new table from a file')}"><i class="fa fa-stack"></i> ${_('New from file')}</button>
            <button class="btn btn-default" data-bind="attr: { 'href': '/beeswax/create/create_table/' + catalogEntry.name }" title="${_('Create a new table manually')}"><i class="fa fa-plus"></i> ${_('New manually')}</button>
          % endif
        % endif
      </div>

      <!-- ko component: { name: 'catalog-entries-list', params: { catalogEntry: catalogEntry, contextPopoverEnabled: true, onClick: onTableClick.bind($data), selectedEntries: selectedTables, editableDescriptions: /true/i.test('${ has_write_access }') } } --><!-- /ko -->
    </div>
  </div>

% if has_write_access:
  <div id="dropTable" class="modal hide fade">
    % if is_embeddable:
      <form data-bind="attr: { 'action': '/metastore/tables/drop/' + catalogEntry.name }, submit: dropAndWatch" method="POST">
        <input type="hidden" name="is_embeddable" value="true"/>
        <input type="hidden" name="start_time" value=""/>
        <input type="hidden" name="source_type" data-bind="value: $root.source().type"/>
        <input type="hidden" name="namespace" data-bind="value: JSON.stringify(catalogEntry.namespace)"/>
        <input type="hidden" name="cluster" data-bind="value: JSON.stringify(catalogEntry.compute)"/>
    % else:
      <form data-bind="attr: { 'action': '/metastore/tables/drop/' + catalogEntry.name }" method="POST">
    % endif
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 id="dropTableMessage" class="modal-title">${_('Do you really want to drop the selected table(s)?')}</h2>
      </div>
      <div class="modal-body">
        <ul data-bind="foreach: selectedTables">
          <!-- ko if: $index() <= 9 -->
          <li>
            <span data-bind="text: catalogEntry().name"></span>
          </li>
          <!-- /ko -->
        </ul>
        <!-- ko if: selectedTables().length > 10 -->
          ${_('and')} <span data-bind="text: selectedTables().length - 10"></span> ${_('others')}.<br>
        <!-- /ko -->
        <label class="checkbox" style="display: inline-block; margin-top: 5px">
          <input type="checkbox" name="skip_trash" /> ${ _('Skip the trash') }
        </label>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${_('No')}" />
        <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <!-- ko foreach: selectedTables -->
      <input type="hidden" name="table_selection" data-bind="value: catalogEntry().name" />
      <!-- /ko -->
    </form>
  </div>
% endif
</script>

<script type="text/html" id="metastore-databases-parameters">
  <div data-bind="toggleOverflow: {height: 24}" style="word-break: break-all">
    <div class="inline margin-right-20"><i class="fa fa-fw fa-cog muted"></i></div>
    <!-- ko foreach: Object.keys($data) -->
      <div class="inline margin-right-20"><strong data-bind="text: $data"></strong>: <span data-bind="text: $parent[$data]"></span></div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="metastore-overview-tab">
  <div class="row-fluid margin-top-10">
    <div class="span4 tile">
      <!-- ko template: 'metastore-table-properties' --><!-- /ko -->
    </div>
    <div class="span4 tile">
      <!-- ko template: 'metastore-table-stats' --><!-- /ko -->
    </div>
  </div>

  <div class="tile">
    <h4 style="margin-bottom: 5px;">${ _('Schema') } <i data-bind="visible: loadingColumns" class="fa fa-spinner fa-spin" style="display: none;"></i></h4>
    <!-- ko component: { name: 'catalog-entries-list', params: { catalogEntry: catalogEntry, contextPopoverEnabled: true, editableDescriptions: /true/i.test('${ has_write_access }') } } --><!-- /ko -->
  </div>
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
    <div class="row-fluid">
      <div class="span10">
        <div data-bind="visible: filters().length > 0">
          <div data-bind="foreach: filters">
              <div class="filter-box">
                <a href="javascript:void(0)" class="pull-right" data-bind="click: $parent.removeFilter">
                  <i class="fa fa-times"></i>
                </a>
                <select class="input-small" data-bind="options: $parent.keys, value: column"></select>
                &nbsp;
                <input class="input-small" type="text" data-bind="value: value, typeahead: { target: value, source: $parent.typeaheadValues(column), triggerOnFocus: true, forceUpdateSource: true}" placeholder="${ _('Value to filter...') }" />
            </div>
          </div>
          <div class="pull-left" style="margin-top: 4px; margin-bottom: 10px">
            <a class="add-filter" href="javascript: void(0)" data-bind="click: addFilter">
              <i class="fa fa-plus"></i> ${ _('Add') }
            </a>
            <label class="checkbox inline pulled">${ _('Sort Desc') } <input type="checkbox" data-bind="checked: sortDesc" /></label>
            <button class="btn" data-bind="click: filter"><i class="fa fa-filter"></i> ${ _('Filter') }</button>
          </div>
        </div>
        <a class="add-filter" href="javascript: void(0)" data-bind="click: addFilter, visible: values().length > 0 && filters().length == 0" style="margin-bottom: 20px; margin-left: 14px">
          <i class="fa fa-plus"></i> ${ _('Add a filter') }
        </a>
        <div class="clearfix"></div>
      </div>
      <div class="span2">
      % if has_write_access:
        <div class="pull-right">
          <button class="btn" title="${_('Delete the selected partitions')}" data-bind="click: function () { $('#dropPartition').modal('show'); }, disable: selectedValues().length === 0"><i class="fa fa-trash-o"></i>  ${_('Drop partition(s)')}</button>
        </div>
      % endif
      </div>
    </div>
    <!-- ko template: { if: values().length, name: 'metastore-partition-values-table', data: { values: values, selectedValues: selectedValues, withDrop: true } } --><!-- /ko -->
    <span data-bind="visible: !values().length" style="display: none;">${ _('The partition does not contain any values') }</span>
    <!-- /ko -->
  </div>

  % if has_write_access:
  <div id="dropPartition" class="modal hide fade">
    % if is_embeddable:
      <form data-bind="attr: { 'action': '/metastore/table/' + $parent.catalogEntry.path.join('/') + '/partitions/drop' }, submit: dropAndWatch" method="POST">
        <input type="hidden" name="is_embeddable" value="true"/>
        <input type="hidden" name="format" value="json"/>
        <input type="hidden" name="start_time" value=""/>
        <input type="hidden" name="source_type" data-bind="value: $root.source().type"/>
    % else:
      <form data-bind="attr: { 'action': '/metastore/table/' + $parent.catalogEntry.path.join('/')+ '/partitions/drop' }" method="POST">
    % endif
      ${ csrf_token(request) | n,unicode }
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 id="dropPartitionMessage" class="modal-title">${_('Confirm action')}</h2>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
        <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <select class="hide" name="partition_selection" data-bind="options: valuesFlat, selectedOptions: selectedValuesFlat" size="5" multiple="true"></select>
    </form>
  </div>
    % endif
  <!-- /ko -->
</script>

<script type="text/html" id="metastore-sample-tab">
  <!-- ko with: samples -->
  <!-- ko if: loading -->
  <div class="empty-message">
    <i data-bind="visible: loading" class='fa fa-spinner fa-spin' style="display: none;"></i>
  </div>
  <!-- /ko -->
  <!-- ko if: loaded() && !hasErrors() -->
  <!-- ko template: { if: rows().length, name: 'metastore-samples-table' } --><!-- /ko -->
  <div data-bind="visible: !rows().length && metastoreTable.catalogEntry.isView()" style="display: none;" class="empty-message">${ _('The view does not contain any data.') }</div>
  <div data-bind="visible: !rows().length && !metastoreTable.catalogEntry.isView()" style="display: none;" class="empty-message">${ _('The table does not contain any data.') }</div>
  <!-- /ko -->
  <!-- ko if: hasErrors() -->
  <div class="empty-message alert" data-bind="text: errorMessage() || '${ _ko('Could not load the sample, see the server log for details.') }'"></div>
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
    <tbody data-bind="hueach: { data: $data.optimizerDetails().queryList(), itemHeight: 32, scrollable: '${ MAIN_SCROLLABLE }', scrollableOffset: 200 }">
    <tr>
      <td data-bind="text: qid"></td>
      <td style="height: 10px; width: 70px; margin-top:5px;" data-bind="attr: {'title': queryCount()}">
        <div class="progress bar" style="background-color: #0B7FAD" data-bind="style: { 'width' : Math.round(queryCount() / $parent.optimizerDetails().queryCount() * 100) + '%' }"></div>
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


<script type="text/html" id="metastore-view-sql-tab">
  <div style="padding: 5px 15px">
    <!-- ko hueSpinner: { spin: loadingViewSql, inline: true } --><!-- /ko -->
    <!-- ko ifnot: loadingViewSql -->
    <div data-bind="highlight: { value: viewSql, formatted: true, dialect: catalogEntry.getSourceType() }"></div>
    <!-- /ko -->
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

<script type="text/html" id="metastore-relationships-tab">
  <!-- ko hueSpinner: { spin: loadingTopJoins, inline: true } --><!-- /ko -->
  <table data-bind="visible: !loadingTopJoins()" class="table table-condensed">
    <thead>
    <tr>
      <th>${ _('Table') }</th>
      <th>${ _('Foreign keys') }</th>
    </tr>
    </thead>
    <tbody>
    <!-- ko if: topJoins().length === 0 -->
    <tr>
      <td colspan="2" style="font-style: italic;">${ _('No related tables found.') }</td>
    </tr>
    <!-- /ko -->
    <!-- ko foreach: topJoins -->
    <tr>
      <td><a href="javascript:void(0);" data-bind="text: tableName, sqlContextPopover: { sourceType: $parents[1].catalogEntry.getSourceType(), namespace: parents[1].catalogEntry.namespace, compute: parents[1].catalogEntry.compute, path: tablePath, offset: { top: -3, left: 3 }}"></a></td>
      <td>
        <table class="metastore-join-column-table">
          <tbody data-bind="foreach: joinCols">
          <tr>
            <td><a href="javascript:void(0);" data-bind="text: target, sqlContextPopover: { sourceType: $parents[2].catalogEntry.getSourceType(), namespace: $parents[2].catalogEntry.namespace, compute: parents[2].catalogEntry.compute, path: targetPath, offset: { top: -3, left: 3 }}"></a></td>
            <td class="metastore-join-arrow"><i class="fa fa-arrows-h"></i></td>
            <td><a href="javascript:void(0);" data-bind="text: source, sqlContextPopover: { sourceType: $parents[2].catalogEntry.getSourceType(), namespace: $parents[2].catalogEntry.namespace, compute: parents[2].catalogEntry.compute, path: sourcePath, offset: { top: -3, left: 3 }}"></a></td>
          </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <!-- /ko -->
    </tbody>
  </table>
</script>

<script type="text/html" id="metastore-describe-table">
  <div class="clearfix"></div>
  <!-- ko template: 'metastore-main-description' --><!-- /ko -->
  <!-- ko if: $root.navigatorEnabled() -->
  <!-- ko template: 'metastore-nav-tags' --><!-- /ko -->
  <!-- ko template: 'metastore-nav-properties' --><!-- /ko -->
  <!-- /ko -->

  <ul class="nav nav-tabs nav-tabs-border margin-top-10">
    <li data-bind="css: { 'active': $root.currentTab() === 'overview' }"><a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('overview'); }">${_('Overview')}</a></li>
    <!-- ko if: $root.optimizerEnabled() -->
      <li data-bind="css: { 'active': $root.currentTab() === 'relationships' }"><a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('relationships'); }">${_('Relationships')} (<span data-bind="text: topJoins().length"></span>)</a></li>
##       <!-- ko if: $root.database().table().optimizerDetails() -->
##       <li data-bind="css: { 'active': $root.currentTab() === 'queries' }"><a href="javascript: void(0);" data-bind="click: function(){ $root.currentTab('queries'); }">${_('Queries')} (<span data-bind="text: $root.database().table().optimizerDetails().queryCount"></span>)</a></li>
##       <li data-bind="css: { 'active': $root.currentTab() === 'joins' }"><a href="javascript: void(0);" data-bind="click: function(){ $root.currentTab('joins'); }">${_('Joins')} (<span data-bind="text: $root.database().table().optimizerDetails().joinCount"></span>)</a></li>
##       <!-- /ko -->
##       <!-- ko if: $root.database().table().relationshipsDetails() -->
##       <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: tableDetails() && tableDetails().partition_keys.length -->
    <li data-bind="css: { 'active': $root.currentTab() === 'partitions' }">
      <a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('partitions'); }">${_('Partitions')} (<span data-bind="text: partitionsCountLabel"></span>)</a>
    </li>
    <!-- /ko -->
    <li data-bind="css: { 'active': $root.currentTab() === 'sample' }">
      <a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('sample'); }">${_('Sample')} (<span data-bind="text: samples.rows().length"></span>)</a>
    </li>
    <!-- ko if: catalogEntry.isView() -->
    <li data-bind="css: { 'active' : $root.currentTab() === 'viewSql' }">
      <a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('viewSql'); }">${ _('View SQL') }</a>
    </li>
    <!-- /ko -->
    <li data-bind="css: { 'active' : $root.currentTab() === 'details' }">
      <a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('details'); }">${ _('Details') }</a>
    </li>
    <!-- ko if: $root.appConfig() && $root.appConfig()['browser'] && $root.appConfig()['browser']['interpreter_names'].indexOf('security') !== -1 -->
    <li data-bind="css: { 'active' : $root.currentTab() === 'privileges' }">
      <a href="javascript: void(0);" data-bind="click: function() { $root.currentTab('privileges'); }">${ _('Privileges') }</a>
    </li>
    <!-- /ko -->
  </ul>

  <div class="tab-content margin-top-10" style="border: none; overflow: hidden">
    <div>
      <!-- ko if: $root.currentTab() === 'overview' -->
        <!-- ko template: 'metastore-overview-tab' --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.currentTab() === 'relationships' -->
      <!-- ko template: { name: 'metastore-relationships-tab' } --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.currentTab() === 'partitions' -->
        <!-- ko template: 'metastore-partitions-tab' --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.currentTab() === 'sample' -->
        <!-- ko template: 'metastore-sample-tab' --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.optimizerEnabled() && $root.currentTab() === 'queries' -->
        <!-- ko template: { name: 'metastore-queries-tab', data: $root.database().table() } --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.currentTab() === 'viewSql' -->
        <!-- ko template: 'metastore-view-sql-tab' --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.currentTab() === 'details' -->
        <!-- ko template: 'metastore-details-tab' --><!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $root.currentTab() === 'privileges' -->
        <div data-bind="component: { name: 'hue-sentry-privileges', params: { isSentryAdmin: false, readOnly: true, server: 'server1', path: catalogEntry.path.join('.')}}"></div>
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
      <div class="content-panel">
        <div class="metastore-main">
          <!-- ko hueSpinner: { spin: loading, center: true, size: 'xlarge' } --><!-- /ko -->
          <!-- ko ifnot: loading -->
            <h1>
              <div class="inline-block pull-right">
                <!-- ko with: source -->
                  <!-- ko with: namespace -->
                    <!-- ko with: database -->
                      <!-- ko with: table -->
                      % if USE_NEW_EDITOR.get():
                        <a href="javascript: void(0);" class="btn btn-default" data-bind="click: function() { queryAndWatch(catalogEntry); }" title="${_('Query')}"><i class="fa fa-play fa-fw"></i> ${_('Query')}</a>
                      % else:
                        <a class="btn btn-default" data-bind="attr: { 'href': '/metastore/table/'+ catalogEntry.path.join('/') + '/read' }" title="${_('Browse Data')}"><i class="fa fa-play fa-fw"></i> ${_('Browse Data')}</a>
                      % endif
                      % if has_write_access:
                        <a href="javascript: void(0);" class="btn btn-default" data-bind="click: showImportData, visible: tableDetails() && !catalogEntry.isView()" title="${_('Import Data')}"><i class="fa fa-upload fa-fw"></i> ${_('Import')}</a>
                      % endif
                      % if has_write_access:
                        <a href="#dropSingleTable" data-toggle="modal" class="btn btn-default" data-bind="attr: { 'title' : tableDetails() && catalogEntry.isView() ? '${_('Drop View')}' : '${_('Drop Table')}' }"><i class="fa fa-times fa-fw"></i> ${_('Drop')}</a>
                      % endif
                      <a href="javascript: void(0);" class="btn btn-default" data-bind="click: reload" title="${_('Refresh the table')}"><i class="fa fa-refresh" data-bind="css: { 'fa-spin blue' : refreshing }"></i> ${_('Refresh')}</a>
                      <!-- /ko -->
                      <!-- ko if: !table() -->
                      <a href="javascript: void(0);" class="btn btn-default" data-bind="click: reload" title="${_('Refresh the database')}"><i class="fa fa-refresh" data-bind="css: { 'fa-spin blue' : refreshing }"></i> ${_('Refresh')}</a>
                      <!-- /ko -->
                    <!-- /ko -->
                    <!-- ko if: !database() -->
                      <a href="javascript: void(0);" class="btn btn-default" data-bind="click: reload" title="${_('Refresh')}"><i class="fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }"></i> ${_('Refresh')}</a>
                    <!-- /ko -->
                  <!-- /ko -->
                <!-- /ko -->
              </div>

              <!-- ko template: 'metastore-breadcrumbs' --><!-- /ko -->
            </h1>

            <!-- ko with: source -->
              <!-- ko with: namespace -->
                <!-- ko template: { if: !loading() && !database(), name: 'metastore-databases' } --><!-- /ko -->
                <!-- ko with: database -->
                  <i data-bind="visible: loading" class="fa fa-spinner fa-spin fa-2x margin-left-10" style="color: #999; display: none;"></i>
                  <!-- ko template: { if: !loading() && !table(), name: 'metastore-tables' } --><!-- /ko -->
                  <!-- ko with: table -->
                    <!-- ko template: 'metastore-describe-table' --><!-- /ko -->
                  <!-- /ko -->
                <!-- /ko -->
              <!-- /ko -->
            <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
    </div>
  </div>
  <!-- ko with: source -->
    <!-- ko with: namespace -->
      <div id="dropSingleTable" class="modal hide fade">
        % if is_embeddable:
        <form data-bind="submit: dropAndWatch" method="POST">
          <input type="hidden" name="is_embeddable" value="true"/>
          <input type="hidden" name="start_time" value=""/>
          <input type="hidden" name="source_type" data-bind="value: $root.source().type"/>
        % else:
        <form method="POST">
        % endif
          ${ csrf_token(request) | n,unicode }
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
            <h2 class="modal-title">${_('Drop Table')}</h2>
          </div>
          <div class="modal-body">
            <div>${_('Do you really want to drop the table')} <span style="font-weight: bold;" data-bind="text: database() && database().table() ? database().table().catalogEntry.name : ''"></span>?</div>
          </div>
          <div class="modal-footer">
            <input type="hidden" name="table_selection" data-bind="value: database() && database().table() ? database().table().catalogEntry.name : ''" />
            <input type="button" class="btn" data-dismiss="modal" value="${_('No')}"/>
            <input type="submit" data-bind="click: function (vm, e) { var $form = $(e.target).parents('form'); $form.attr('action', '/metastore/tables/drop/' + vm.database().catalogEntry.name); return true; }" class="btn btn-danger" value="${_('Yes, drop this table')}"/>
          </div>
        </form>
      </div>
    <!-- /ko -->
  <!-- /ko -->
  <div id="import-data-modal" class="modal hide fade" style="display: block;width: 680px;margin-left: -340px!important;"></div>
</div>
</span>

<script type="text/javascript">

  function dropAndWatch(formElement) {
    $(formElement).find('input[name=start_time]').val(ko.mapping.toJSON(new Date().getTime()));
    $(formElement).ajaxSubmit({
      dataType: 'json',
      success: function(resp) {
        if (resp.history_uuid) {
          huePubSub.publish('notebook.task.submitted', resp);
          huePubSub.publish('metastore.clear.selection');
        } else if (resp && resp.message) {
          $(document).trigger("error", resp.message);
        }
        $("#dropTable").modal('hide');
        $("#dropSingleTable").modal('hide');
        $("#dropDatabase").modal('hide');
        $("#dropPartition").modal('hide');
      },
      error: function (xhr) {
        $(document).trigger("error", xhr.responseText);
      }
    });
  }

  function browsePartitionFolder(url) {
    $.get(url, {
      format: "json"
    },function(resp) {
      if (resp.uri_path) {
        huePubSub.publish('open.link', resp.uri_path);
      } else if (resp.message) {
        $(document).trigger("error", resp.message);
      }
    }).fail(function (xhr) {
      $(document).trigger("error", xhr.responseText);
    });
  }

  function queryAndWatchUrl(url, sourceType, namespaceId, compute) {
    $.post(url, {
      format: "json",
      sourceType: sourceType,
      namespace: namespaceId,
      cluster: compute
    },function(resp) {
      if (resp.history_uuid) {
        huePubSub.publish('open.editor.query', resp);
      } else if (resp.message) {
        $(document).trigger("error", resp.message);
      }
    }).fail(function (xhr) {
      $(document).trigger("error", xhr.responseText);
    });
  }

  function queryAndWatch(catalogEntry) {
    queryAndWatchUrl('/notebook/browse/' + catalogEntry.path.join('/') + '/', catalogEntry.getSourceType(),
            catalogEntry.namespace && catalogEntry.namespace.id, catalogEntry.compute)
  }
</script>
</span>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
