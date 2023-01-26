// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import * as ko from 'knockout';
import { CancellablePromise } from '../../../api/cancellablePromise';

import AsteriskContextTabs from './asteriskContextTabs';
import CollectionContextTabs from './collectionContextTabs';
import DataCatalogContext from './dataCatalogContext';
import DocumentContext, { DOCUMENT_CONTEXT_TEMPLATE } from './documentContext';
import FunctionContextTabs, { FUNCTION_CONTEXT_TEMPLATE } from './functionContext';
import { DOCUMENT_CONTEXT_FOOTER } from './ko.documentContextFooter';
import LangRefContext from './langRefContext';
import PartitionContext, { PARTITION_CONTEXT_TEMPLATE } from './partitionContext';
import ResizeHelper from './resizeHelper';
import StorageContext from './storageContext';
import { getNamespaces } from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import { GET_KNOWN_CONFIG_TOPIC } from 'config/events';
import { findEditorConnector } from 'config/hueConfig';
import { ASSIST_KEY_COMPONENT } from 'ko/components/assist/ko.assistKey';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { getFromLocalStorage } from 'utils/storageUtils';

export const CONTEXT_POPOVER_CLASS = 'hue-popover';
export const HIDE_CONTEXT_POPOVER_EVENT = 'context.popover.hide';
export const CONTEXT_POPOVER_HIDDEN_EVENT = 'context.popover.hidden';
export const SHOW_CONTEXT_POPOVER_EVENT = 'context.popover.show';
export const NAME = 'context-popover';

// prettier-ignore
const SUPPORT_TEMPLATES = `
  <script type="text/html" id="context-popover-footer">
    <div class="context-popover-flex-bottom-links">
      <div class="context-popover-link-row">
        <a href="javascript: void(0);" class="inactive-action" data-bind="visible: showInAssistEnabled, publish: 'context.popover.show.in.assist'">
          <i style="font-size: 11px;" title="${I18n(
            'Show in Assist...'
          )}" class="fa fa-search"></i> ${I18n('Assist')}
        </a>
        <!-- ko if: isDocument -->
        <!-- ko with: contents -->
        <!-- ko if: documentId -->
        <a href="javascript: void(0);" class="inactive-action" data-bind="click: download">
          <i style="font-size: 11px;" title="${I18n('Download')}" class="fa fa-download"></i> ${I18n('Download')}
        </a>
        <!-- /ko -->
        <a href="javascript: void(0);" class="inactive-action" data-bind="click: open">
          <i style="font-size: 11px;" title="${I18n('Open')}" class="fa fa-file-o"></i> ${I18n('Open')}
        </a>
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: expandColumnsEnabled -->
        <!-- ko with: contents.data -->
        <!-- ko if: selectedColumns().length > 0 -->
        <a class="inactive-action pointer" data-bind="click: expand">${I18n(
          'Expand to selected columns'
        )}</a>
        <!-- /ko -->
        <!-- ko if: selectedColumns().length === 0 -->
        <a class="inactive-action pointer" data-bind="click: expand">${I18n(
          'Expand to all columns'
        )}</a>
        <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
      </div>
      <!-- ko if: isDocument -->
        <div class="context-popover-bottom-attributes">
        <!-- ko with: contents -->
          <!-- ko component: { name: '${ DOCUMENT_CONTEXT_FOOTER }', params: { popoverData: $data } } --><!-- /ko -->
        <!-- /ko -->
        </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="context-popover-collection-stats-details">
    <div class="context-popover-flex-fill">
      <div style="padding: 8px">
        <div data-bind="with: stats">
        <!-- ko hueSpinner: { spin:  $parent.loadingStats, center: true, size: 'large' } --><!-- /ko -->
        <div class="alert" data-bind="visible: !$parent.loadingStats() && !$parent.statsSupported()">${I18n(
          'This field does not support stats'
        )}</div>
        <div class="alert" data-bind="visible: !$parent.loadingStats() && $parent.statsSupported() && $data.data().length == 0">${I18n(
          'There are no stats to be shown'
        )}</div>
        <table style="width: 100%" data-bind="visible: !$parent.loadingStats() && $data.data().length > 0" class="table table-condensed">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td style="vertical-align: top"><strong data-bind="text: key"></strong></td>
            <!-- ko if: key == 'facets' -->
            <td>
              <!-- ko if: val[Object.keys(val)[0]] != null -->
              <table>
                <tbody data-bind="foreach: Object.keys(val[Object.keys(val)[0]])">
                  <tr>
                    <td style="vertical-align: top; padding-left: 4px; padding-right: 4px"><strong data-bind="text: $data"></strong></td>
                    <td data-bind="template: 'context-popover-collection-stats-facets'"></td>
                  </tr>
                </tbody>
              </table>
              <!-- /ko -->
              <!-- ko ifnot: val[Object.keys(val)[0]] != null -->
              ${I18n('Not available')}
              <!-- /ko -->
            </td>
            <!-- /ko -->
            <!-- ko ifnot: key == 'facets' -->
            <td data-bind="text: val"></td>
            <!-- /ko -->
          </tr>
          </tbody>
        </table>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-collection-stats-facets">
    <table style="width: 100%">
      <tbody data-bind="foreach: Object.keys($parent.val[Object.keys($parent.val)[0]][$data])">
        <tr>
          <td style="vertical-align: top; padding-left: 4px; padding-right: 4px"><strong data-bind="text: $data"></strong></td>
          <!-- ko ifnot: $data == 'facets' -->
          <td style="vertical-align: top" data-bind="text: $parents[1].val[Object.keys($parents[1].val)[0]][$parent][$data]"></td>
          <!-- /ko -->
        </tr>
      </tbody>
    </table>
  </script>

  <script type="text/html" id="context-popover-collection-terms-details">
    <div class="context-popover-flex-fill">
      <input type="text" data-bind="value: terms.prefix, clearable: terms.prefix, valueUpdate:'afterkeydown'" placeholder="${I18n(
        'Filter...'
      )}" class="pull-right">
      <div data-bind="with: terms">
        <!-- ko hueSpinner: { spin:  $parent.loadingTerms, center: true, size: 'large' } --><!-- /ko -->
        <div class="clearfix"></div>
        <div class="alert" data-bind="visible: !$parent.loadingTerms() && $data.data().length == 0">${I18n(
          'There are no terms to be shown'
        )}</div>
        <table style="width: 100%" data-bind="visible: !$parent.loadingTerms() && $data.data().length > 0" class="table table-condensed">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td data-bind="text: val.value"></td>
            <td style="width: 40px">
              <div class="progress">
                <div class="bar-label" data-bind="text:val.count"></div>
                <div class="bar bar-info" style="margin-top:-20px;" data-bind="style: {'width': ((val.count / $parent.data()[0].val.count) * 100) + '%'}"></div>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-asterisk-details">
    <div class="context-popover-flex-fill">
      <!-- ko component: { name: 'sql-columns-table', params: { columns: columns, scrollToColumns: false } } --><!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="context-hue-app-details">
    <div class="context-popover-flex-fill" style="overflow: auto;" data-bind="with: data">
      <div style="padding: 8px">
        <div style="width:100%; text-align: center; margin-top: 30px; font-size: 100px; color: #787878;" data-bind="template: { name: 'app-icon-template', data: { icon: interpreter.type } }"></div>
          <div style="width: 100%; margin-top: 20px; text-align:center">
            <a style="font-size: 20px;" href="javascript:void(0)" data-bind="text: interpreter.displayName, hueLink: interpreter.page, click: function () { $parents[1].close(); }, attr: { 'title': interpreter.tooltip }"></a>
          </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-contents">
    <div class="context-popover-content">
      <!-- ko with: contents -->
      <!-- ko if: typeof tabs !== 'undefined' -->
      <ul class="nav nav-tabs context-popover-tabs" data-bind="foreach: tabs">
        <li data-bind="click: function () { $parent.activeTab(id); }, css: { 'active' : $parent.activeTab() === id }">
          <a class="context-popover-tab" data-toggle="tab" data-bind="text: label, attr: { href: '#' + id }"></a>
        </li>
      </ul>
      <div class="context-popover-tab-container" data-bind="foreach: tabs">
        <div class="context-popover-tab-pane tab-pane" data-bind="visible : $parent.activeTab() === id, attr: { id: id }, css: { 'active' : $parent.activeTab() === id }">
          <div class="context-popover-flex">
            <!-- ko with: templateData -->
            <div class="context-popover-flex-fill" data-bind="visible: loading"><!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko --></div>
            <!-- ko if: ! loading() && hasErrors() -->
            <div class="context-popover-flex-fill">
                <div class="alert">
                <span data-bind="text: $parent.errorText"></span>
                <!-- ko if: $parent.enableSampleError && $parents[1].activeTab() === 'sample' -->
                <a href="javascript:void(0);" data-bind="click: function(){ huePubSub.publish('sample.error.insert.click', $data); huePubSub.publish('context.popover.hide');}">${I18n(
                  'Insert '
                )}<span data-bind="text:$parent.title"></span> ${I18n('sample query')}</a> ${I18n(
  'at cursor'
)}
                <!-- /ko -->
                </div>
            </div>
            <!-- /ko -->
            <!-- ko if: ! loading() && ! hasErrors() -->
            <!-- ko template: { name: $parent.template } --><!-- /ko -->
            <!-- /ko -->
            <!-- /ko -->
            <!-- ko template: { name: 'context-popover-footer', data: $parents[1] } --><!-- /ko -->
          </div>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: typeof tabs === 'undefined' -->
      <div class="context-popover-flex-fill" data-bind="visible: loading"><!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko --></div>
      <!-- ko if: !loading() && hasErrors() -->
      <div class="context-popover-flex-fill">
        <div class="alert" data-bind="text: errorText"></div>
      </div>
      <!-- /ko -->
      <!-- ko if: !loading() && !hasErrors() -->
      <!-- ko template: { name: template } --><!-- /ko -->
      <!-- /ko -->
      <!-- ko template: { name: 'context-popover-footer', data: $parent } --><!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="context-catalog-doc-title">
  </script>

  <script type="text/html" id="context-lang-ref-title">
    <div class="hue-popover-title" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 20px;">
      <i class="fa fa-book muted" style="margin-top: 3px"></i> <span class="blue" style="padding-left: 4px;" data-bind="text: title"></span>
      <div class="hue-popover-title-actions">
        <a class="pointer inactive-action" title="${I18n(
          'Pin'
        )}" data-bind="visible: popover.pinEnabled, click: popover.pin"><i class="fa fa-fw fa-thumb-tack"></i></a>
        <a class="pointer inactive-action" title="${I18n(
          'Close'
        )}" data-bind="visible: !popover.closeDisabled, click: popover.close"><i class="fa fa-fw fa-times"></i></a>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-lang-ref-contents">
    <div class="context-popover-content">
      <div class="context-popover-flex-fill context-popover-docs-details" data-bind="htmlUnsecure: body"></div>
      <div class="context-popover-flex-bottom-links">
        <div class="context-popover-link-row">
          <a class="inactive-action pointer" data-bind="click: openInRightAssist">
            <i style="font-size: 11px;" title="${I18n(
              'Show in Assist...'
            )}" class="fa fa-search"></i> ${I18n('Assist')}
          </a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-catalog-entry-title">
    <div class="hue-popover-title">
      <!-- ko if: catalogEntry().isTable() -->
        <span class="hue-popover-title-secondary-icon-container">
          <!-- ko hueSpinner: { spin: loading, inline: true } --><!-- /ko -->
          <!-- ko ifnot: loading -->  
            <!-- ko if:catalogEntry().isIcebergTable() -->  
              <i class="hue-popover-title-icon fa muted fa-snowflake-o"  title="${I18n(
                'Iceberg table'
              )}"></i>
            <!-- /ko -->
            <!-- ko ifnot:catalogEntry().isIcebergTable() -->  
              <i class="hue-popover-title-icon fa muted fa-table"></i>
            <!-- /ko -->            
          <!-- /ko -->
        </span>
      <!-- /ko -->
      <!-- ko ifnot: catalogEntry().isTable() -->
        <i class="hue-popover-title-icon fa muted" data-bind="css: 
        catalogEntry() && (catalogEntry().isView() || parentIsView()) 
        ? 'fa-eye' 
        : (catalogEntry().isDatabase() 
        ? 'fa-database' 
        : (catalogEntry().isModel() 
        ? 'fa-puzzle-piece' 
        : 'fa-table'))"></i>      
      <!-- /ko -->
      <span class="hue-popover-title-text" data-bind="foreach: breadCrumbs">
        <!-- ko ifnot: isActive --><div><a href="javascript: void(0);" data-bind="click: makeActive, text: name"></a>.</div><!-- /ko -->
        <!-- ko if: isActive -->
        <div>
          <span data-bind="text: name"></span>
          <!-- ko with: catalogEntry -->
          <!-- ko if: isField() -->
          (<span data-bind="text: getType()"></span>)
          <!-- ko if: isKey() -->
            <!-- ko component: { name: '${ ASSIST_KEY_COMPONENT }', params: { entry: $data, onForeignKeyClick: $parents[1].setEntry.bind($parents[1]) } } --><!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </span>
      <div class="hue-popover-title-actions">
        <!-- ko hueSpinner: { spin: loading, inline: true } --><!-- /ko -->
        <a class="pointer inactive-action" title="${I18n(
          'Refresh'
        )}" data-bind="visible: !loading() && catalogEntry() && !catalogEntry().isTemporary, click: refresh"><i class="fa fa-fw fa-refresh"></i></a>
        <a class="pointer inactive-action" title="${I18n(
          'Pin'
        )}" data-bind="visible: popover.pinEnabled && catalogEntry() && !catalogEntry().isTemporary, click: popover.pin"><i class="fa fa-fw fa-thumb-tack"></i></a>
        <a class="pointer inactive-action" title="${I18n(
          'Close'
        )}" data-bind="visible: !popover.closeDisabled, click: popover.close"><i class="fa fa-fw fa-times"></i></a>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-catalog-entry-contents">
    <div class="context-popover-content">
      <div class="context-popover-flex-fill" data-bind="visible: loading"><!-- ko hueSpinner: { spin: loading, center: true, size: 'xlarge' } --><!-- /ko --></div>
      <!-- ko if: !loading() && hasErrors() -->
      <div class="context-popover-flex-fill">
        <div class="alert" data-bind="text: errorText"></div>
      </div>
      <!-- /ko -->
      <!-- ko if: !loading() && !hasErrors() && typeof catalogEntry() !== 'undefined'-->
      <div class="context-popover-flex-fill" data-bind="with: catalogEntry">
        <div class="context-popover-inner-content">
          <!-- ko if: $parent.comment() && !isTemporary  -->
          <div class="context-popover-comment" data-bind="attr: { 'title': $parent.comment }, multiLineEllipsis: { expanded: $parent.commentExpanded, expandable: true, expandClass: 'context-popover-comment-expanded' }, text: $parent.comment"></div>
          <!-- /ko -->

          <!-- ko ifnot: $parent.commentExpanded -->
              <!-- ko if: window.HAS_CATALOG && !isTemporary && (getDialect() === 'hive' || getDialect() === 'impala') -->
              <div data-bind="component: { name: 'nav-tags', params: { catalogEntry: $data, overflowEllipsis: true } }"></div>
              <!-- /ko -->

            <!-- ko if: isView() && $parent.viewSql() -->
            <a href="javascript:void(0);" style="text-align: right; margin-bottom: 5px;" data-bind="toggle: $parent.viewSqlVisible, text: $parent.viewSqlVisible() ? '${I18n(
              'Show columns'
            )}' : '${I18n('Show view SQL')}'"></a>
            <!-- /ko -->

            <!-- ko if: $parent.viewSqlVisible -->
            <div class="context-popover-sql" data-bind="highlight: { value: $parent.viewSql, enableOverflow: true, formatted: true, dialect: getDialect() }"></div>
            <!-- /ko -->
            <!-- ko ifnot: $parent.viewSqlVisible -->
            <!-- ko component: { name: 'catalog-entries-list', params: { catalogEntry: $data, onClick: $parent.catalogEntry, onSampleClick: $parent.onSampleClick } } --><!-- /ko -->
            <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>

      <div class="context-popover-flex-bottom-links">
        <div class="context-popover-link-row">
          <!-- ko if: catalogEntry -->
          <a class="inactive-action pointer" data-bind="visible: popover.showInAssistEnabled || catalogEntry() !== originalCatalogEntry, click: showInAssist">
            <i style="font-size: 11px;" title="${I18n(
              'Show in Assist...'
            )}" class="fa fa-search"></i> ${I18n('Assist')}
          </a>
          <!-- ko if: window.HAS_SQL_DASHBOARD -->
            <a class="inactive-action pointer" data-bind="visible: openActionsEnabled, click: openInDashboard">
              <i style="font-size: 11px;" title="${I18n(
                'Open in Dashboard...'
              )}" class="fa fa-external-link"></i> ${I18n('Dashboard')}
            </a>
          <!-- /ko -->
          <!-- ko if: catalogEntry().getDialect() !== 'solr' && openActionsEnabled() -->
          <a class="inactive-action pointer" data-bind="click: openInTableBrowser">
            <i style="font-size: 11px;" title="${I18n(
              'Open in Table Browser...'
            )}" class="fa fa-external-link"></i> ${I18n('Table Browser')}
          </a>
          <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="context-storage-entry-title">
    <div class="hue-popover-title">
      <i class="hue-popover-title-icon fa muted" data-bind="css: storageEntry() && storageEntry().definition.type === 'dir' ? 'fa-folder-o' : 'fa-file-o'"></i>
      <span class="hue-popover-title-text" data-bind="foreach: breadCrumbs">
        <!-- ko ifnot: isActive --><div><a href="javascript: void(0);" data-bind="click: makeActive, text: name"></a><!-- ko if: $index() > 0 -->/<!-- /ko --></div><!-- /ko -->
        <!-- ko if: isActive -->
        <div>
          <span data-bind="text: name"></span>
        </div>
        <!-- /ko -->
      </span>
      <div class="hue-popover-title-actions">
        <!-- ko hueSpinner: { spin: loading, inline: true } --><!-- /ko -->
        <a class="pointer inactive-action" title="${I18n(
          'Go Home'
        )}" data-bind="visible: !loading(), click: goHome"><i class="fa fa-fw fa-home"></i></a>
        <a class="pointer inactive-action" title="${I18n(
          'Close'
        )}" data-bind="visible: !popover.closeDisabled, click: popover.close"><i class="fa fa-fw fa-times"></i></a>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-storage-entry-contents">
    <div class="context-popover-content" data-bind="with: storageEntry">
      <!-- ko if: !loading() && hasErrors() -->
      <div class="context-popover-flex-fill">
        <div class="alert" data-bind="text: errorText"></div>
      </div>
      <!-- /ko -->

      <div class="context-popover-flex-fill" data-bind="visible: loading"><!-- ko hueSpinner: { spin: loading, center: true, size: 'xlarge' } --><!-- /ko --></div>

      <!-- ko if: !loading() && !hasErrors() -->
      <!-- ko with: definition -->
      <div class="context-popover-flex-attributes">
          <!-- ko if: typeof humansize !== 'undefined' -->
          <div class="context-popover-attribute"><div>${I18n(
            'Size'
          )}</div><div data-bind="text: humansize"></div></div>
          <!-- /ko -->
          <!-- ko if: typeof stats !== 'undefined' -->
          <!-- ko with: stats -->
          <!-- ko if: user -->
          <div class="context-popover-attribute"><div>${I18n(
            'Owner'
          )}</div><div data-bind="text: user"></div></div>
          <!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
          <!-- ko if: typeof rwx !== 'undefined' -->
          <div class="context-popover-attribute"><div>${I18n(
            'Permissions'
          )}</div><div data-bind="text: rwx"></div></div>
          <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- ko if: definition.type === 'dir' -->
      <div class="context-popover-flex-fill storage-entry-container" data-bind="fetchMore: { fetchMore: fetchMore.bind($data), hasMore: hasMorePages, loadingMore: loadingMore.bind($data) }">
        <table class="table table-condensed table-nowrap">
          <thead>
            <tr>
              <th width="1%"></th>
              <th>${I18n('Name')}</th>
              <th>${I18n('Size')}</th>
              <th>${I18n('Permissions')}</th>
            </tr>
          </thead>
          <tbody>
            <!-- ko if: $parent.storageEntry().parent -->
            <tr>
              <td><i class="fa fa-folder-o"></i></td>
              <td><a href="javascript: void(0);" data-bind="click: function () { $parent.storageEntry($parent.storageEntry().parent) }">..</a></td>
              <td data-bind="text: $parent.storageEntry().definition.humansize"></td>
              <td data-bind="text: $parent.storageEntry().definition.rwx"></td>
            </tr>
            <!-- /ko -->
            <!-- ko foreach: entries -->
            <tr>
              <td><i class="fa" data-bind="css: definition.type === 'dir' ? 'fa-folder-o' : 'fa-file-o'"></i></td>
              <td><a href="javascript: void(0);" data-bind="click: function () { $parents[1].storageEntry($data) }, text: definition.name"></a></td>
              <td data-bind="text: definition.humansize"></td>
              <td data-bind="text: definition.rwx"></td>
            </tr>
            <!-- /ko -->
          </tbody>
        </table>
      </div>
      <!-- /ko -->
      <!-- ko if: definition.type !== 'dir' -->
      <div class="context-popover-flex-header"><div class="context-popover-header">${I18n(
        'Preview'
      )}</div></div>
      <div class="context-popover-flex-fill storage-entry-container">
        <div data-bind="with: preview">
          <!-- ko if: view && view.contents -->
          <pre data-bind="text: view.contents"></pre>
          <!-- /ko -->
          <!-- ko if: view && !view.contents -->
          <div class="empty-file-contents">${I18n('Empty file...')}</div>
          <!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- /ko -->

      <div class="context-popover-flex-bottom-links">
        <div class="context-popover-link-row">
          <!-- ko ifnot: loading -->
          <a class="inactive-action pointer" data-bind="click: $parent.openInFileBrowser">
            <i style="font-size: 11px;" title="${I18n(
              'Open in File Browser...'
            )}" class="fa fa-external-link"></i> ${I18n('File Browser')}
          </a>
          <!-- ko if: typeof $parent.editorLocation !== 'undefined' -->
          <a class="inactive-action pointer" data-bind="click: function () { $parent.replaceInEditor($data, $parent) }">
            <i style="font-size: 11px;" title="${I18n(
              'Replace the editor content...'
            )}" class="fa fa-pencil"></i> ${I18n('Insert in the editor')}
          </a>
          <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
    </div>
  </script>
`;

// prettier-ignore
const CONTEXT_POPOVER_TEMPLATE = `
  <div class="${ CONTEXT_POPOVER_CLASS }" data-bind="css: orientationClass, style: { 'left': left() + 'px', 'top': top() + 'px', 'width': width() + 'px', height: height() + 'px' }, resizable: { containment: 'document', handles: resizeHelper.resizableHandles, start: resizeHelper.resizeStart, stop: resizeHelper.resizeStop, resize: resizeHelper.resize }">
    <div class="hue-popover-arrow" data-bind="style: { 'margin-left': leftAdjust() + 'px',  'margin-top': topAdjust() + 'px' }"></div>
    <!-- ko if: typeof titleTemplate !== 'undefined' -->
    <!-- ko template: { name: titleTemplate, data: contents } --><!-- /ko -->
    <!-- /ko -->
    <!-- ko if: typeof titleTemplate === 'undefined' -->
    <div class="hue-popover-title" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 30px;">
      <i class="fa muted" data-bind="css: iconClass" style="margin-top: 3px"></i> <span style="padding-left: 4px;" data-bind="text: title"></span>
      <!-- ko if: typeof subtitle !== 'undefined' && subtitle -->
      <span class="muted" style="padding-left: 4px;" data-bind="html: subtitle"></span>
      <!-- /ko -->
      <div style="position: absolute; right: 6px; top: 8px;">
        <a class="pointer inactive-action" data-bind="visible: pinEnabled, click: pin"><i class="fa fa-fw fa-thumb-tack"></i></a>
        <a class="pointer inactive-action" data-bind="click: close"><i class="fa fa-fw fa-times"></i></a>
      </div>
    </div>
    <!-- /ko -->
    <!-- ko if: typeof contentsComponent !== 'undefined' -->
    <!-- ko component: { name: contentsComponent, params: data } --><!-- /ko -->
    <!-- /ko -->
    <!-- ko if: typeof contentsTemplate !== 'undefined' -->
    <!-- ko template: { name: contentsTemplate, data: contents } --><!-- /ko -->
    <!-- /ko -->
    <!-- ko if: typeof contentsTemplate === 'undefined' && typeof contentsComponent === 'undefined' -->
    <!-- ko template: 'context-popover-contents' --><!-- /ko -->
    <!-- /ko -->
  </div>
`;

// prettier-ignore
const GLOBAL_SEARCH_TEMPLATE = `
  <!-- ko if: isCatalogEntry -->
  <!-- ko with: contents -->
  <div class="global-search-catalog-entry">
    <!-- ko template: 'context-catalog-entry-title' --><!-- /ko -->
    <!-- ko template: 'context-catalog-entry-contents' --><!-- /ko -->
  </div>
  <!-- /ko -->
  <!-- /ko -->
  <!-- ko ifnot: isCatalogEntry -->
  <!-- ko template: 'context-popover-contents' --><!-- /ko -->
  <!-- /ko -->
`;

const HALF_ARROW = 6;

let preventHide = false;

const hidePopover = function () {
  if (!preventHide) {
    const $contextPopover = $('#contextPopover');
    if ($contextPopover.length > 0) {
      ko.cleanNode($contextPopover[0]);
      $contextPopover.remove();
      $(document).off('click.context');
      huePubSub.publish(CONTEXT_POPOVER_HIDDEN_EVENT);
    }
  }
};

class ContextPopoverViewModel {
  constructor(params) {
    const self = this;
    self.disposals = [];

    self.left = ko.observable(0);
    self.top = ko.observable(0);

    const popoverSize = getFromLocalStorage('assist.popover.size', {
      width: 450,
      height: 400
    });

    self.width = ko.observable(popoverSize.width);
    self.height = ko.observable(popoverSize.height);

    self.leftAdjust = ko.observable(0);
    self.topAdjust = ko.observable(0);

    self.data = params.data;
    self.connector = params.connector;
    self.sourceType = params.sourceType;
    self.namespace = params.namespace;
    self.compute = params.compute;
    self.defaultDatabase = params.defaultDatabase;
    self.close = hidePopover;
    self.onSampleClick = params.onSampleClick;
    const orientation = params.orientation || 'bottom';
    self.contents = null;
    self.resizeHelper = new ResizeHelper(orientation, self.leftAdjust, self.topAdjust, noHide => {
      preventHide = noHide;
    });

    if (typeof params.source.element !== 'undefined') {
      // Track the source element and close the popover if moved
      const $source = $(params.source.element);
      const originalSourceOffset = $source.offset();
      let currentSourceOffset;

      const detectMoveInterval = window.setInterval(() => {
        currentSourceOffset = $source.offset();
        if (currentSourceOffset.top !== originalSourceOffset.top) {
          hidePopover();
        }
      }, 200);

      self.disposals.push(() => {
        window.clearInterval(detectMoveInterval);
      });
    }

    const windowWidth = $(window).width();
    const fitHorizontally = function () {
      let left =
        params.source.left +
        Math.round((params.source.right - params.source.left) / 2) -
        self.width() / 2;
      if (left + self.width() > windowWidth - 10) {
        self.leftAdjust(left + self.width() - windowWidth + 5);
        left = windowWidth - self.width() - 10;
      } else if (left < 10) {
        self.leftAdjust(left - 10 - HALF_ARROW);
        left = 10;
      } else {
        self.leftAdjust(-HALF_ARROW);
      }
      self.left(left);
    };

    const windowHeight = $(window).height();
    const fitVertically = function () {
      let top =
        params.source.top +
        Math.round((params.source.bottom - params.source.top) / 2) -
        self.height() / 2;
      if (top + self.height() > windowHeight - 10) {
        self.topAdjust(top + self.height() - windowHeight + 5);
        top = windowHeight - self.height() - 10;
      } else if (top < 10) {
        self.topAdjust(top - 10 - HALF_ARROW);
        top = 10;
      } else {
        self.topAdjust(-HALF_ARROW);
      }
      self.top(top);
    };

    switch (orientation) {
      case 'top':
        fitHorizontally();
        self.top(params.source.top - self.height());
        break;
      case 'right':
        fitVertically();
        self.left(params.source.right);
        break;
      case 'bottom':
        fitHorizontally();
        self.top(params.source.bottom);
        break;
      case 'left':
        fitVertically();
        self.left(params.source.left - self.width());
    }

    self.isSolr = params.sourceType === 'solr';

    self.isComplex = params.data.type === 'complex';
    self.isFunction = params.data.type === 'function';
    self.isStorageEntry = params.data.type === 'storageEntry';
    self.isAsterisk = params.data.type === 'asterisk';
    self.isDocument = params.data.type.toLowerCase() === 'hue';
    self.isCollection = params.data.type === 'collection';
    self.isCatalogEntry = !!params.data.catalogEntry;
    self.isLangRef = params.data.type === 'statementType';

    if (
      self.isCatalogEntry &&
      params.data.catalogEntry.getDialect() === 'solr' &&
      params.data.catalogEntry.isField()
    ) {
      self.isCollection = true;
      self.isCatalogEntry = false;
      self.namespace = params.data.catalogEntry.namespace;
      self.compute = params.data.catalogEntry.compute;
    }

    self.showInAssistEnabled =
      (typeof params.showInAssistEnabled !== 'undefined' ? params.showInAssistEnabled : true) &&
      (self.isDocument || self.isCollection || self.isCatalogEntry);
    self.openInDashboardEnabled = self.isCatalogEntry && params.data.catalogEntry.path.length <= 2;
    self.openInTableBrowserEnabled =
      self.isCatalogEntry && params.data.catalogEntry.path.length <= 2;
    self.expandColumnsEnabled = self.isAsterisk;

    self.pinEnabled =
      params.pinEnabled &&
      !self.isFunction &&
      !self.isAsterisk &&
      !self.isStorageEntry &&
      !self.isCatalogEntry;

    if (params.data.type === 'quickQuery') {
      self.contentsComponent = 'quick-query-context';
      self.title = I18n('Quick Query');
      self.iconClass = 'fa-play';
      self.pinEnabled = false;
    } else if (self.isCatalogEntry) {
      self.contents = new DataCatalogContext({
        popover: self,
        catalogEntry: params.data.catalogEntry
      });
      self.titleTemplate = 'context-catalog-entry-title';
      self.contentsTemplate = 'context-catalog-entry-contents';
    } else if (self.isFunction) {
      self.contents = new FunctionContextTabs(self.data, self.connector);
      self.title = self.data.function;
      self.iconClass = 'fa-superscript';
    } else if (self.isStorageEntry) {
      self.contents = new StorageContext({
        popover: self,
        storageEntry: params.data.storageEntry,
        editorLocation: params.data.editorLocation
      });
      self.titleTemplate = 'context-storage-entry-title';
      self.contentsTemplate = 'context-storage-entry-contents';
    } else if (self.isAsterisk) {
      self.contents = new AsteriskContextTabs(
        self.data,
        self.connector,
        self.namespace,
        self.compute,
        self.defaultDatabase
      );
      self.title = '*';
      self.iconClass = 'fa-table';
    } else if (self.isDocument) {
      self.contents = new DocumentContext(self.data.definition);
      self.titleTemplate = 'context-catalog-doc-title';
    } else if (self.isCollection) {
      self.contents = new CollectionContextTabs(self.data);
      self.title = self.data.catalogEntry.path.slice(1).join('.');
      self.iconClass = 'fa-search';
    } else if (self.isLangRef) {
      self.contents = new LangRefContext({ popover: self, data: params.data });
      self.titleTemplate = 'context-lang-ref-title';
      self.contentsTemplate = 'context-lang-ref-contents';
    } else {
      self.title = '';
      self.iconClass = 'fa-info';
    }
    self.orientationClass = 'hue-popover-' + orientation;

    if (params.delayedHide) {
      let hideTimeout = -1;
      const onLeave = function () {
        hideTimeout = window.setTimeout(() => {
          $('.hue-popover').fadeOut(200, () => {
            hidePopover();
          });
        }, 1000);
      };

      const onEnter = function () {
        window.clearTimeout(hideTimeout);
      };

      $(params.delayedHide)
        .add($('.hue-popover'))
        .on('mouseleave', onLeave)
        .on('mouseenter', onEnter);

      const keepPopoverOpenOnClick = function () {
        window.clearTimeout(hideTimeout);
        $(params.delayedHide)
          .add($('.hue-popover'))
          .off('mouseleave', onLeave)
          .off('mouseenter', onEnter);
      };

      $('.hue-popover').on('click', keepPopoverOpenOnClick);

      self.disposals.push(() => {
        $(params.delayedHide)
          .add($('.hue-popover'))
          .off('mouseleave', onLeave)
          .off('mouseenter', onEnter);
        $('.hue-popover').off('click', keepPopoverOpenOnClick);
      });
    }

    const closeOnEsc = function (e) {
      if (e.keyCode === 27) {
        hidePopover();
      }
    };

    $(document).on('keyup', closeOnEsc);

    self.disposals.push(() => {
      $(document).off('keyup', closeOnEsc);
    });

    window.setTimeout(() => {
      $(document).off('click.context');
      $(document).on('click.context', event => {
        if (
          $.contains(document, event.target) &&
          !$.contains($('#contextPopover')[0], event.target) &&
          ($('.modal')[0].length === 0 || !$.contains($('.modal')[0], event.target))
        ) {
          hidePopover();
        }
      });
    }, 0);

    self.disposals.push(() => {
      $(document).off('click.context');
    });
  }

  dispose() {
    const self = this;
    while (self.disposals.length) {
      self.disposals.pop()();
    }

    if (self.contents && self.contents.dispose) {
      self.contents.dispose();
    }
    huePubSub.publish('context.popover.dispose');
  }

  pin() {
    const self = this;
    hidePopover();
    if (self.contents && typeof self.contents.sample !== 'undefined') {
      self.contents.sample.fetchedData(undefined);
    }
    huePubSub.publish('sql.context.pin', self);
    if (self.contents && self.contents.activeTab() === 'sample') {
      self.contents.refetchSamples();
    }
  }
}

componentUtils
  .registerComponent(
    NAME,
    ContextPopoverViewModel,
    SUPPORT_TEMPLATES +
      DOCUMENT_CONTEXT_TEMPLATE +
      FUNCTION_CONTEXT_TEMPLATE +
      PARTITION_CONTEXT_TEMPLATE +
      CONTEXT_POPOVER_TEMPLATE
  )
  .then(() => {
    huePubSub.subscribe(HIDE_CONTEXT_POPOVER_EVENT, hidePopover);

    huePubSub.subscribe(SHOW_CONTEXT_POPOVER_EVENT, details => {
      hidePopover();
      const $contextPopover = $(
        '<div id="contextPopover" data-bind="component: { name: \'context-popover\', params: $data }" ></div>'
      );
      $('body').append($contextPopover);
      ko.applyBindings(details, $contextPopover[0]);
      huePubSub.publish('context.popover.shown');
    });
  });

class SqlContextContentsGlobalSearch {
  constructor(params) {
    const self = this;
    self.contents = ko.observable();

    self.disposals = [];

    self.isCatalogEntry =
      params.data.type === 'catalogEntry' ||
      params.data.type.toLowerCase() === 'database' ||
      params.data.type.toLowerCase() === 'table' ||
      params.data.type.toLowerCase() === 'field' ||
      params.data.type.toLowerCase() === 'view';

    self.isDocument = params.data.type.toLowerCase() === 'hue';
    self.isPartition = params.data.type.toLowerCase() === 'partition';

    self.close = params.globalSearch.close.bind(params.globalSearch);

    // These are currently not in the global search results
    self.isStorageEntry = false;
    self.isAsterisk = false;
    self.isComplex = false;
    self.isFunction = false;

    self.showInAssistEnabled = !self.isHueApp;
    self.openInDashboardEnabled = false;
    self.openInTableBrowserEnabled = false;
    self.expandColumnsEnabled = self.isAsterisk;
    self.closeDisabled = true; // Global search has it's own close

    const adaptedData = { identifierChain: [] };

    const path = params.data.originalName.split('.');
    path.forEach(part => {
      adaptedData.identifierChain.push({ name: part });
    });

    let connectorId = params.data.sourceType && params.data.sourceType.toLowerCase();

    if (!connectorId || connectorId === 'hive') {
      huePubSub.publish(GET_KNOWN_CONFIG_TOPIC, clusterConfig => {
        if (clusterConfig) {
          const defaultEditor = clusterConfig['default_sql_interpreter'];
          if (!connectorId || (connectorId === 'hive' && defaultEditor === 'impala')) {
            connectorId = defaultEditor;
          }
        }
      });
    }

    if (self.isCatalogEntry) {
      // TODO: Connector, Namespace and compute selection for global search results?
      let connector = findEditorConnector(connector => connector.id === connectorId);

      if (!connector) {
        // TODO: Global search results are referring to dialect and not type
        connector = findEditorConnector(connector => connector.dialect === connectorId);
      }
      getNamespaces({ connector })
        .then(context => {
          dataCatalog
            .getEntry({
              namespace: context.namespaces[0],
              compute: context.namespaces[0].computes[0],
              connector: connector,
              path: path,
              definition: { type: params.data.type.toLowerCase() }
            })
            .then(catalogEntry => {
              catalogEntry.navigatorMeta = params.data;
              catalogEntry.navigatorMetaPromise = CancellablePromise.resolve(
                catalogEntry.navigatorMeta
              );
              catalogEntry.saveLater();
              self.contents(new DataCatalogContext({ popover: self, catalogEntry: catalogEntry }));
            });
        })
        .catch();
    } else if (self.isDocument) {
      self.contents(new DocumentContext(params.data));
    } else if (self.isPartition) {
      self.contents(new PartitionContext(params.data));
    }
  }

  dispose() {
    const self = this;
    while (self.disposals.length) {
      self.disposals.pop()();
    }
    if (self.contents && self.contents.dispose) {
      self.contents.dispose();
    }

    huePubSub.publish('context.popover.dispose');
  }
}

componentUtils.registerComponent(
  'context-popover-contents-global-search',
  SqlContextContentsGlobalSearch,
  SUPPORT_TEMPLATES +
    DOCUMENT_CONTEXT_TEMPLATE +
    FUNCTION_CONTEXT_TEMPLATE +
    PARTITION_CONTEXT_TEMPLATE +
    GLOBAL_SEARCH_TEMPLATE
);
