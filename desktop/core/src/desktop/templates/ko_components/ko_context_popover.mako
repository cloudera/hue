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
from django.utils.translation import ugettext as _

from dashboard.conf import HAS_SQL_ENABLED
from desktop import conf
from desktop.conf import IS_EMBEDDED
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko

from metadata.conf import has_navigator
%>

<%namespace name="impalaDocIndex" file="/impala_doc_index.mako" />

<%def name="contextPopover()">
  <script type="text/html" id="context-popover-footer">
    <div class="context-popover-flex-bottom-links">
      <div class="context-popover-link-row">
        <a href="javascript: void(0);" class="inactive-action" data-bind="visible: showInAssistEnabled, publish: 'context.popover.show.in.assist'">
          <i style="font-size: 11px;" title="${ _("Show in Assist...") }" class="fa fa-search"></i> ${ _("Assist") }
        </a>
        <!-- ko if: isDocument -->
        <!-- ko with: contents -->
        <a href="javascript: void(0);" class="inactive-action" data-bind="click: open">
          <i style="font-size: 11px;" title="${ _("Open...") }" class="fa fa-file-o"></i> ${ _("Open") }
        </a>
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: expandColumnsEnabled -->
        <!-- ko with: contents.data -->
        <!-- ko if: selectedColumns().length > 0 -->
        <a class="inactive-action pointer" data-bind="click: expand">${ _("Expand to selected columns") }</a>
        <!-- /ko -->
        <!-- ko if: selectedColumns().length === 0 -->
        <a class="inactive-action pointer" data-bind="click: expand">${ _("Expand to all columns") }</a>
        <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-collection-stats-details">
    <div class="context-popover-flex-fill">
      <div style="padding: 8px">
        <div data-bind="with: stats">
        <!-- ko hueSpinner: { spin:  $parent.loadingStats, center: true, size: 'large' } --><!-- /ko -->
        <div class="alert" data-bind="visible: !$parent.loadingStats() && !$parent.statsSupported()">${ _('This field does not support stats') }</div>
        <div class="alert" data-bind="visible: !$parent.loadingStats() && $parent.statsSupported() && $data.data().length == 0">${ _('There are no stats to be shown') }</div>
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
              ${ _('Not available') }
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
      <input type="text" data-bind="value: terms.prefix, clearable: terms.prefix, valueUpdate:'afterkeydown'" placeholder="${ _('Filter...') }" class="pull-right">
      <div data-bind="with: terms">
        <!-- ko hueSpinner: { spin:  $parent.loadingTerms, center: true, size: 'large' } --><!-- /ko -->
        <div class="clearfix"></div>
        <div class="alert" data-bind="visible: !$parent.loadingTerms() && $data.data().length == 0">${ _('There are no terms to be shown') }</div>
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

  <script type="text/html" id="context-popover-function-details">
    <!-- ko if: typeof details === 'undefined' -->
    <div class="context-popover-flex-fill">
      <div class="alert">${_('Could not find details for the function')} <span data-bind="text: $parents[2].title"></span>()</div>
    </div>
    <!-- /ko -->
    <!-- ko if: typeof details !== 'undefined' -->
    <div class="context-popover-flex-fill" data-bind="with: details">
      <div style="padding: 8px">
        <p style="margin: 10px 10px 18px 10px;"><span style="white-space: pre;" class="monospace" data-bind="text: signature"></span></p>
        <p><span data-bind="text: description"></span></p>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="generic-document-context-template">
    <div style="width:100%; text-align: center; margin-top: 40px; font-size: 100px; color: #787878;" data-bind="template: { name: 'document-icon-template', data: { document: { isDirectory: type === 'directory', definition: function() { return $data } } } }"></div>
    <div style="width: 100%; margin-top: 20px; text-align:center">
      <!-- ko if: type === 'directory' -->
      <a style="font-size: 20px;" href="javascript:void(0)" data-bind="text: name, publish: 'context.popover.show.in.assist'"></a>
      <!-- /ko -->
      <!-- ko if: type !== 'directory' -->
      <a style="font-size: 20px;" href="javascript:void(0)" data-bind="text: name, hueLink: link, click: function () { $parents[1].close(); }"></a>
      <!-- /ko -->
      <br/>
      <span data-bind="text: HUE_I18n.documentType[type] || type"></span>
      <!-- ko if: description -->
      <div class="context-popover-doc-description" data-bind="html: description"></div>
      <!-- /ko -->
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

  <script type="text/html" id="context-document-details">
    <div class="context-popover-flex-fill" style="overflow: auto;">
      <div class="context-popover-inner-content">
        <div style="position: absolute; right: 6px; top: 8px;">
          <a class="pointer inactive-action" data-bind="visible: !$parent.closeDisabled, click: function () { $parent.close() }"><i class="fa fa-fw fa-times"></i></a>
        </div>
        <!-- ko if: typeof documentContents() !== 'undefined' && typeof documentContents().snippets !== 'undefined' -->
        <!-- ko with: details -->
        <div class="context-popover-doc-header-link" ><a href="javascript:void(0)" data-bind="hueLink: link, click: function () { $parents[1].close(); }"><!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: false } } --><!-- /ko --> <span data-bind="text:name"></span></a></div>
        <!-- ko if: description -->
        <div class="context-popover-doc-description" data-bind="html: description"></div>
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko with: documentContents -->
        <!-- ko foreach: snippets -->
        <div class="context-popover-doc-contents" data-bind="highlight: { value: statement_raw, formatted: true, dialect: type }"></div>
        <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: typeof documentContents() === 'undefined' || typeof documentContents().snippets === 'undefined' -->
        <div style="width: 100%;" data-bind="template: { name: 'generic-document-context-template', data: details }"></div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="context-partition-details">
    <div class="context-popover-flex-fill" style="overflow: auto;">
      <div class="context-popover-inner-content">
        <div style="position: absolute; right: 6px; top: 8px;">
          <a class="pointer inactive-action" data-bind="visible: !$parent.closeDisabled, click: function () { $parent.close() }"><i class="fa fa-fw fa-times"></i></a>
        </div>
        <!-- ko with: data -->
        <div class="context-popover-flex-header blue"><span data-bind="text: originalName"></span></div>
        <div class="context-popover-flex-attributes">
          <div class="context-popover-attribute"><div>${ _('Created') }</div><div data-bind="text: created"></div></div>
        </div>
        <!-- ko if: description -->
        <div class="context-popover-doc-description" data-bind="html: description"></div>
        <!-- /ko -->
        <div class="context-popover-flex-fill">
          <table id="partitionsTable" class="table table-condensed table-nowrap">
            <thead>
            <tr>
              <th>${ _('Values') }</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: colValues">
              <tr>
                <td data-bind="text: $data"></td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-template">
    <div class="hue-popover" data-bind="css: orientationClass, style: { 'left': left() + 'px', 'top': top() + 'px', 'width': width() + 'px', height: height() + 'px' }, resizable: { containment: 'document', handles: resizeHelper.resizableHandles, start: resizeHelper.resizeStart, stop: resizeHelper.resizeStop, resize: resizeHelper.resize }">
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
      <!-- ko if: typeof contentsTemplate !== 'undefined' -->
      <!-- ko template: { name: contentsTemplate, data: contents } --><!-- /ko -->
      <!-- /ko -->
      <!-- ko if: typeof contentsTemplate === 'undefined' -->
      <!-- ko template: 'context-popover-contents' --><!-- /ko -->
      <!-- /ko -->
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
                <a href="javascript:void(0);" data-bind="click: function(){ huePubSub.publish('sample.error.insert.click', $data); huePubSub.publish('context.popover.hide');}">${_('Insert ')}<span data-bind="text:$parent.title"></span> ${_(' sample query')}</a> ${_('at cursor')}
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
        <a class="pointer inactive-action" title="${ _('Pin') }" data-bind="visible: popover.pinEnabled, click: popover.pin"><i class="fa fa-fw fa-thumb-tack"></i></a>
        <a class="pointer inactive-action" title="${ _('Close') }" data-bind="visible: !popover.closeDisabled, click: popover.close"><i class="fa fa-fw fa-times"></i></a>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-lang-ref-contents">
    <div class="context-popover-content">
      <div class="context-popover-flex-fill context-popover-docs-details" data-bind="html: body"></div>
      <div class="context-popover-flex-bottom-links">
        <div class="context-popover-link-row">
          <a class="inactive-action pointer" data-bind="click: openInRightAssist">
            <i style="font-size: 11px;" title="${ _("Show in Assist...") }" class="fa fa-search"></i> ${ _("Assist") }
          </a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-catalog-entry-title">
    <div class="hue-popover-title">
      <i class="hue-popover-title-icon fa muted" data-bind="css: catalogEntry() && catalogEntry().isView() ? 'fa-eye' : 'fa-table'"></i>
      <span class="hue-popover-title-text" data-bind="foreach: breadCrumbs">
        <!-- ko ifnot: isActive --><div><a href="javascript: void(0);" data-bind="click: makeActive, text: name"></a>.</div><!-- /ko -->
        <!-- ko if: isActive -->
        <div>
          <span data-bind="text: name"></span>
          <!-- ko with: catalogEntry -->
          <!-- ko if: isField() -->
          (<span data-bind="text: getType()"></span>)
          <i class="fa fa-key" title="${ _('Primary Key') }" data-bind="visible: isPrimaryKey()"></i>
          <i class="fa fa-key" title="${ _('Partition Key') }" data-bind="visible: isPartitionKey()"></i>
          <!-- /ko -->
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </span>
      <div class="hue-popover-title-actions">
        <!-- ko hueSpinner: { spin: loading, inline: true } --><!-- /ko -->
        <a class="pointer inactive-action" title="${ _('Refresh') }" data-bind="visible: !loading(), click: refresh"><i class="fa fa-fw fa-refresh"></i></a>
        <a class="pointer inactive-action" title="${ _('Pin') }" data-bind="visible: popover.pinEnabled, click: popover.pin"><i class="fa fa-fw fa-thumb-tack"></i></a>
        <a class="pointer inactive-action" title="${ _('Close') }" data-bind="visible: !popover.closeDisabled, click: popover.close"><i class="fa fa-fw fa-times"></i></a>
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
      <!-- ko if: !loading() && !hasErrors() && typeof catalogEntry() !== 'undefined' -->
      <div class="context-popover-flex-fill" data-bind="with: catalogEntry">
        <div class="context-popover-inner-content">
          <!-- ko if: $parent.comment() -->
          <div class="context-popover-comment" data-bind="attr: { 'title': $parent.comment }, multiLineEllipsis: { expanded: $parent.commentExpanded, expandable: true, expandClass: 'context-popover-comment-expanded' }, text: $parent.comment"></div>
          <!-- /ko -->

          <!-- ko ifnot: $parent.commentExpanded -->
            %if has_navigator(user):
              <!-- ko if: getSourceType() === 'hive' || getSourceType() === 'impala' -->
              <div data-bind="component: { name: 'nav-tags', params: { catalogEntry: $data, overflowEllipsis: true } }"></div>
              <!-- /ko -->
            %endif

            <!-- ko if: isView() && $parent.viewSql() -->
            <a href="javascript:void(0);" style="text-align: right; margin-bottom: 5px;" data-bind="toggle: $parent.viewSqlVisible, text: $parent.viewSqlVisible() ? '${ _ko('Show columns')}' : '${ _ko('Show view SQL')}'"></a>
            <!-- /ko -->

            <!-- ko if: $parent.viewSqlVisible -->
            <div class="context-popover-sql" data-bind="highlight: { value: $parent.viewSql, formatted: true, dialect: getSourceType() }"></div>
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
            <i style="font-size: 11px;" title="${ _("Show in Assist...") }" class="fa fa-search"></i> ${ _("Assist") }
          </a>
          % if HAS_SQL_ENABLED.get():
            <a class="inactive-action pointer" data-bind="visible: openActionsEnabled, click: openInDashboard">
              <i style="font-size: 11px;" title="${ _("Open in Dashboard...") }" class="fa fa-external-link"></i> ${ _("Dashboard") }
            </a>
          % endif
          % if not IS_EMBEDDED.get():
            <!-- ko if: catalogEntry().getSourceType() !== 'solr' && openActionsEnabled() -->
            <a class="inactive-action pointer" data-bind="click: openInTableBrowser">
              <i style="font-size: 11px;" title="${ _("Open in Table Browser...") }" class="fa fa-external-link"></i> ${ _("Table Browser") }
            </a>
            <!-- /ko -->
          % endif
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
        <a class="pointer inactive-action" title="${ _('Go Home') }" data-bind="visible: !loading(), click: goHome"><i class="fa fa-fw fa-home"></i></a>
        <a class="pointer inactive-action" title="${ _('Close') }" data-bind="visible: !popover.closeDisabled, click: popover.close"><i class="fa fa-fw fa-times"></i></a>
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
          <div class="context-popover-attribute"><div>${ _('Size') }</div><div data-bind="text: humansize"></div></div>
          <!-- /ko -->
          <!-- ko if: typeof stats !== 'undefined' -->
          <!-- ko with: stats -->
          <!-- ko if: user -->
          <div class="context-popover-attribute"><div>${ _('Owner') }</div><div data-bind="text: user"></div></div>
          <!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
          <!-- ko if: typeof rwx !== 'undefined' -->
          <div class="context-popover-attribute"><div>${ _('Permissions') }</div><div data-bind="text: rwx"></div></div>
          <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- ko if: definition.type === 'dir' -->
      <div class="context-popover-flex-fill storage-entry-container" data-bind="fetchMore: { fetchMore: fetchMore.bind($data), hasMore: hasMorePages, loadingMore: loadingMore.bind($data) }">
        <table class="table table-condensed table-nowrap">
          <thead>
            <tr>
              <th width="1%"></th>
              <th>${ _('Name') }</th>
              <th>${ _('Size') }</th>
              <th>${ _('Permissions') }</th>
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
      <div class="context-popover-flex-header"><div class="context-popover-header">${ _('Preview') }</div></div>
      <div class="context-popover-flex-fill storage-entry-container">
        <div data-bind="with: preview">
          <!-- ko if: view && view.contents -->
          <pre data-bind="text: view.contents"></pre>
          <!-- /ko -->
          <!-- ko if: view && !view.contents -->
          <div class="empty-file-contents">${ _('Empty file...') }</div>
          <!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- /ko -->

      <div class="context-popover-flex-bottom-links">
        <div class="context-popover-link-row">
          <!-- ko ifnot: loading -->
          <a class="inactive-action pointer" data-bind="click: $parent.openInFileBrowser">
            <i style="font-size: 11px;" title="${ _("Open in File Browser...") }" class="fa fa-external-link"></i> ${ _("File Browser") }
          </a>
          <!-- ko if: typeof $parent.editorLocation !== 'undefined' -->
          <a class="inactive-action pointer" data-bind="click: function () { $parent.replaceInEditor($data, $parent) }">
            <i style="font-size: 11px;" title="${ _("Replace the editor content...") }" class="fa fa-pencil"></i> ${ _("Insert in the editor") }
          </a>
          <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="global-search-context">
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
  </script>

  <script type="text/javascript">
    (function () {

      var DataCatalogContext = function (options) {
        var self = this;
        self.popover = options.popover;
        self.catalogEntry = ko.observable(options.catalogEntry);

        self.loading = ko.observable(false);
        self.hasErrors = ko.observable(false);
        self.activePromises = [];
        self.errorText = ko.observable();

        self.onSampleClick = options.popover.onSampleClick;

        self.analysis = ko.observable();
        self.comment = ko.observable();
        self.commentExpanded = ko.observable(false);
        self.viewSql = ko.observable();
        self.viewSqlVisible = ko.observable(false);

        self.openActionsEnabled = ko.pureComputed(function () {
          return self.catalogEntry() && self.catalogEntry().path.length <= 2;
        });

        self.catalogEntry.subscribe(self.load.bind(self));

        self.breadCrumbs = ko.pureComputed(function () {
          var result = [];
          var catalogEntry = self.catalogEntry();
          if (catalogEntry) {
            for (var i = 0; i < catalogEntry.path.length; i++) {
              result.push({
                name: catalogEntry.path[i],
                isActive: i === catalogEntry.path.length - 1,
                path: catalogEntry.path.slice(0, i + 1),
                catalogEntry: self.catalogEntry,
                makeActive: function () {
                  self.catalogEntry().dataCatalog.getEntry({ namespace: self.catalogEntry().namespace, compute: self.catalogEntry().compute, path: this.path }).done(self.catalogEntry);
                }
              })
            }
          }
          return result;
        });
        self.originalCatalogEntry = options.catalogEntry;
        self.load();
      };

      DataCatalogContext.prototype.refresh = function () {
        var self = this;
        self.catalogEntry().clearCache({ invalidate: 'invalidate', cascade: true }).always(self.load.bind(self));
      };

      DataCatalogContext.prototype.load = function () {
        var self = this;
        self.loading(true);
        self.hasErrors(false);
        self.cancelActivePromises();

        var viewSqlDeferred = $.Deferred().done(self.viewSql);
        self.activePromises.push(viewSqlDeferred.promise());

        self.activePromises.push(self.catalogEntry().getSourceMeta({ cancellable: true }).fail(function () {
          self.hasErrors(true);
        }).always(function () {
          self.loading(false);
        }));

        if (self.catalogEntry().getSourceType() === 'impala' || self.catalogEntry().getSourceType() === 'hive') {
          self.activePromises.push(self.catalogEntry().getAnalysis({
            silenceErrors: true,
            cancellable: true
          }).done(function (analysis) {
            var found = analysis.properties && analysis.properties.some(function (property) {
              if (property.col_name.toLowerCase() === 'view original text:') {
                ApiHelper.getInstance().formatSql({statements: property.data_type}).done(function (formatResponse) {
                  if (formatResponse.status === 0) {
                    viewSqlDeferred.resolve(formatResponse.formatted_statements);
                  } else {
                    viewSqlDeferred.resolve(property.data_type)
                  }
                }).fail(function () {
                  viewSqlDeferred.resolve(property.data_type)
                });
                return true;
              }
            });
            if (!found) {
              viewSqlDeferred.resolve();
            }
            self.analysis(analysis);
          }).fail(viewSqlDeferred.reject));
        } else {
          viewSqlDeferred.reject();
        }

        self.activePromises.push(self.catalogEntry().getComment({ silenceErrors: true, cancellable: true }).done(self.comment));

        $.when.apply($, self.activePromises).always(function () {
          self.activePromises.length = 0;
        })
      };

      DataCatalogContext.prototype.cancelActivePromises = function () {
        var self = this;
        while (self.activePromises.length) {
          var promise = self.activePromises.pop();
          if (promise.cancel) {
            promise.cancel();
          }
        }
      };

      DataCatalogContext.prototype.dispose = function () {
        var self = this;
        self.cancelActivePromises();
      };

      DataCatalogContext.prototype.showInAssist = function () {
        var self = this;
        huePubSub.publish('assist.db.highlight', self.catalogEntry());
        huePubSub.publish('global.search.close');
      };

      DataCatalogContext.prototype.openInDashboard = function() {
        var self = this;
        huePubSub.publish('open.link', '/hue/dashboard/browse/' + self.catalogEntry().path.join('.') + '?engine=' + self.catalogEntry().getSourceType());
        huePubSub.publish('context.popover.hide');
        huePubSub.publish('global.search.close');
      };

      DataCatalogContext.prototype.openInTableBrowser = function () {
        var self = this;
        huePubSub.publish('open.link', '/metastore/table' + (self.catalogEntry().isTableOrView() ? '/' : 's/') + self.catalogEntry().path.join('/')
                + '?source=' + self.catalogEntry().getSourceType() + '&namespace=' + self.catalogEntry().namespace.id);
        huePubSub.publish('context.popover.hide');
        huePubSub.publish('global.search.close');
      };

      function AsteriskData(data, sourceType, namespace, compute, defaultDatabase) {
        var self = this;
        self.loading = ko.observable(true);
        self.hasErrors = ko.observable(false);
        self.columns = [];

        self.selectedColumns = ko.pureComputed(function () {
          return self.columns.filter(function (column) {
            return column.selected();
          });
        });

        self.expand = function () {
          var colsToExpand = self.selectedColumns().length === 0 ? self.columns : self.selectedColumns();
          var colIndex = {};
          var colsTableMap = {};
          self.columns.forEach(function (col) {
            if (colsTableMap[col.name]) {
              colsTableMap[col.name].push(col.table);
            }
            else {
              colsTableMap[col.name] = [col.table];
            }
          });
          colsToExpand.forEach(function (col) {
            if (colIndex[col.name]) {
              colIndex[col.name]++;
            } else {
              colIndex[col.name] = 1;
            }
          });
          Object.keys(colIndex).forEach(function (name) {
            if (colIndex[name] === 1 && colsTableMap[name].length === 1) {
              delete colIndex[name];
            }
          });
          huePubSub.publish('ace.replace', {
            location: data.location,
            text: $.map(colsToExpand, function (column) {
              if (column.tableAlias) {
                return SqlUtils.backTickIfNeeded(sourceType, column.tableAlias) + '.' + SqlUtils.backTickIfNeeded(sourceType, column.name);
              }
              if (colIndex[column.name]) {
                return SqlUtils.backTickIfNeeded(sourceType, column.table) + '.' + SqlUtils.backTickIfNeeded(sourceType, column.name);
              }
              return SqlUtils.backTickIfNeeded(sourceType, column.name)
            }).join(', ')
          });
          huePubSub.publish('context.popover.hide');
        };

        var deferrals = [];
        data.tables.forEach(function (table) {
          if (table.identifierChain) {
            var fetchDeferred = $.Deferred();
            deferrals.push(fetchDeferred);
            var path = $.map(table.identifierChain, function (identifier) { return identifier.name });
            if (path.length === 1) {
              path.unshift(defaultDatabase);
            }
            DataCatalog.getEntry({
              sourceType: sourceType,
              namespace: namespace,
              compute: compute,
              path: path
            }).done(function (entry) {
              entry.getSourceMeta({ silenceErrors: true }).done(function (sourceMeta) {
                if (typeof sourceMeta.extended_columns !== 'undefined') {
                  var newColumns = [];
                  sourceMeta.extended_columns.forEach(function (column) {
                    var clonedColumn = $.extend({}, column);
                    clonedColumn.extendedType = clonedColumn.type.replace(/</g, '&lt;').replace(/>/g, '&lt;');
                    if (clonedColumn.type.indexOf('<') !== -1) {
                      clonedColumn.type = clonedColumn.type.substring(0, clonedColumn.type.indexOf('<'));
                    }
                    clonedColumn.selected = ko.observable(false);
                    clonedColumn.table = table.identifierChain[table.identifierChain.length - 1].name;
                    if (table.alias) {
                      clonedColumn.tableAlias = table.alias
                    }
                    newColumns.push(clonedColumn);
                  });
                  self.columns = self.columns.concat(newColumns);
                }
                fetchDeferred.resolve();
              }).fail(fetchDeferred.reject);
            }).fail(fetchDeferred.reject);
          }
        });

        if (deferrals.length === 0) {
          self.loading(false);
        }
        $.when.apply($, deferrals).done(function () {
          self.loading(false);
        }, function () {
          if (self.columns.length === 0) {
            self.hasErrors(true);
          }
        });
      }

      function AsteriskContextTabs(data, sourceType, namespace, compute, defaultDatabase) {
        var self = this;
        self.data = new AsteriskData(data, sourceType, namespace, compute, defaultDatabase);

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'context-popover-asterisk-details', templateData: self.data }
        ];
        self.activeTab = ko.observable('details');
      }

      var StorageContext = function (options) {
        var self = this;

        self.popover = options.popover;
        self.storageEntry = ko.observable();
        self.editorLocation = options.editorLocation;

        self.loading = ko.pureComputed(function () {
          return self.storageEntry() && self.storageEntry().loading();
        });

        self.storageEntry.subscribe(function (newVal) {
          if (!newVal.loaded && !newVal.loading()) {
            if (newVal.definition.type === 'dir') {
              newVal.open(true);
            } else {
              newVal.loadPreview();
            }
          }
        });

        self.storageEntry(options.storageEntry);

        self.breadCrumbs = ko.pureComputed(function () {
          var result = [];
          var currentEntry = self.storageEntry();
          do {
            result.unshift({
              name: currentEntry.definition.name,
              isActive: currentEntry === self.storageEntry(),
              storageEntry: currentEntry,
              makeActive: function () {
                self.storageEntry(this.storageEntry);
              }
            });

            currentEntry = currentEntry.parent;
          } while (currentEntry);
          return result;
        });
      };

      StorageContext.prototype.openInFileBrowser = function (entry) {
        huePubSub.publish('open.link', entry.definition.url);
        huePubSub.publish('context.popover.hide');
        huePubSub.publish('global.search.close');
      };

      StorageContext.prototype.replaceInEditor = function (entry, storageContext) {
        var text = entry.originalType ? entry.originalType + ':/' + entry.path : entry.path;
        huePubSub.publish('ace.replace', {
          location: storageContext.editorLocation,
          text: text
        });
        huePubSub.publish('context.popover.hide');
      };

      StorageContext.prototype.goHome = function () {
        var self = this;
        AssistStorageEntry.getEntry(USER_HOME_DIR, self.storageEntry().type).done(self.storageEntry)
      };

      function FunctionContextTabs(data, sourceType) {
        var self = this;
        self.func = ko.observable({
          details: SqlFunctions.findFunction(sourceType, data.function),
          loading: ko.observable(false),
          hasErrors: ko.observable(false)
        });

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'context-popover-function-details', templateData: self.func }
        ];
        self.activeTab = ko.observable('details');
      }

      ${ impalaDocIndex.impalaDocIndex() }

      function LangRefContext(options) {
        var self = this;
        self.popover = options.popover;
        self.title = ko.observable();
        self.body = ko.observable();

        self.topicId = 'topics/impala_' + options.data.identifier.toLowerCase().replace(/ /g, '_') + '.xml';

        $.get(IMPALA_DOC_INDEX[self.topicId]).done(function (topic) {
          self.title(topic.title);
          self.body(topic.body);
        });

        $('.hue-popover').on('click.contextLangRef', function (event) {
          if (event.target.className === 'hue-doc-internal-link') {
            huePubSub.publish('assist.lang.ref.show.topic', {
              ref: $(event.target).data('doc-ref'),
              anchorId: $(event.target).data('doc-anchor-id')
            });
          }
        });
      }

      LangRefContext.prototype.dispose = function () {
        $('.hue-popover').off('click.contextLangRef');
      };

      LangRefContext.prototype.openInRightAssist = function () {
        var self = this;
        huePubSub.publish('assist.lang.ref.show.topic', self.topicId);
        huePubSub.publish('context.popover.hide');
      };

      function PartitionContext(data) {
        var self = this;
        self.disposals = [];

        self.data = data;
        self.loading = ko.observable(false);
        self.hasErrors = ko.observable(false);
        self.errorText = ko.observable();
        self.template = 'context-partition-details';
      }

      PartitionContext.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      function DocumentContext(data) {
        var self = this;
        self.disposals = [];

        // Adapt some details to a common format, the global search endpoint has different structure than the docs one
        self.details = {
          type: data.doc_type || data.type,
          name: data.originalName || data.name || data.hue_name,
          link: data.absoluteUrl || data.link,
          description: data.description || data.hue_description,
          isDirectory: data.doc_type === 'directory' || data.type === 'directory',
          definition: ko.observable({
            type: data.doc_type || data.type
          })
        };
        self.data = data;
        self.loading = ko.observable(true);
        self.hasErrors = ko.observable(false);
        self.errorText = ko.observable();
        self.template = 'context-document-details';

        self.documentContents = ko.observable();
        self.loadDocument();

        var showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', function () {
          huePubSub.publish('assist.doc.highlight', {
            parentUuid: self.data.parentUuid,
            docUuid: self.data.uuid
          });
        });

        self.disposals.push(function () {
          showInAssistPubSub.remove();
        })
      }

      DocumentContext.prototype.open = function (entry) {
        huePubSub.publish('open.link', entry.details.link);
        huePubSub.publish('context.popover.hide');
        huePubSub.publish('global.search.close');
      };

      DocumentContext.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      DocumentContext.prototype.loadDocument = function () {
        var self = this;
        self.hasErrors(false);
        self.loading(true);
        ApiHelper.getInstance().fetchDocument({
          uuid: self.data.uuid,
          fetchContents: true,
          silenceErrors: true
        }).done(function (response) {
          self.documentContents(response.data);
          self.loading(false);
        }).fail(function (errorMessage) {
          self.loading(false);
          self.hasErrors(false); // Allows us to revert to a generic document panel in case it can't fetch it.
        })
      };

      function CollectionContextTabs(data) {
        var self = this;

        self.apiHelper = ApiHelper.getInstance();

        self.disposals = [];

        self.catalogEntry = data.catalogEntry;

        self.data = ko.observable({
          details: data,
          loading: ko.observable(false),
          hasErrors: ko.observable(false),
          selectedPath: ko.observable(data.path),
          loadingTerms: ko.observable(false),
          loadingStats: ko.observable(false),
          statsSupported: ko.observable(true),
          terms: ko.mapping.fromJS({'prefix': '', 'data': []}),
          stats: ko.mapping.fromJS({'facet': '', 'data': []})
        });

        self.data().terms.prefix.subscribe(function () {
          self.loadTerms();
        });
        self.data().terms.prefix.extend({rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});

        self.loadTerms();
        self.loadStats();

        self.tabs = [
          {
            id: 'terms',
            label: '${ _("Terms") }',
            template: 'context-popover-collection-terms-details',
            templateData: self.data
          }, {
            id: 'stats',
            label: '${ _("Stats") }',
            template: 'context-popover-collection-stats-details',
            templateData: self.data
          }
        ];
        self.activeTab = ko.observable('terms');

        var showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', function () {
          huePubSub.publish('assist.db.highlight', self.catalogEntry);
        });
        self.disposals.push(function () {
          showInAssistPubSub.remove();
        })
      }

      CollectionContextTabs.prototype.loadTerms = function () {
        var self = this;
        self.data().terms.data.removeAll();
        self.data().loadingTerms(true);
        self.apiHelper.fetchDashboardTerms({
          collectionName: self.catalogEntry.path[1],
          fieldName: self.catalogEntry.path[2],
          prefix: self.data().terms.prefix(),
          engine: 'solr',
          successCallback: function (data) {
            if (data.terms != null) {
              $.each(data.terms, function (key, val) {
                self.data().terms.data.push({'key': key, 'val': val});
              });
            }
          },
          alwaysCallback: function () {
            self.data().loadingTerms(false);
          }
        });
      };

      CollectionContextTabs.prototype.loadStats = function () {
        var self = this;
        self.data().terms.data.removeAll();
        self.data().loadingStats(true);
        self.data().statsSupported(true);
        var fieldName = self.catalogEntry.path[2];
        self.apiHelper.fetchDashboardStats({
          collectionName: self.catalogEntry.path[1],
          fieldName: fieldName,
          engine: 'solr',
          successCallback: function (data) {
            if (data.stats.stats.stats_fields[fieldName] != null) {
              $.each(data.stats.stats.stats_fields[fieldName], function (key, val) {
                self.data().stats.data.push({ 'key': key, 'val': val });
              });
            }
          },
          notSupportedCallback: function () {
            self.data().statsSupported(false);
          },
          alwaysCallback: function () {
            self.data().loadingStats(false);
          }
        });
      };

      CollectionContextTabs.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      var HALF_SIZE_LIMIT_X = 130;
      var HALF_SIZE_LIMIT_Y = 100;
      var HALF_ARROW = 6;

      var preventHide = false;

      var hidePopover = function () {
        if (! preventHide) {
          if ($('#contextPopover').length > 0) {
            ko.cleanNode($('#contextPopover')[0]);
            $('#contextPopover').remove();
            $(document).off('click.context');
            huePubSub.publish('context.popover.hidden');
          }
        }
      };

      function ResizeHelper (orientation, leftAdjust, topAdjust) {
        var self = this;

        var apiHelper = ApiHelper.getInstance();

        var originalMidX, originalWidth, originalRightX, originalLeftX, originalMidY, originalHeight, originalTopY, originalBottomY;
        var rightX, leftX, leftDiff, rightDiff, topY, bottomY, topDiff, bottomDiff;
        var redrawHeaders = false;

        var initOriginalValues = function (attempt) {
          if (attempt > 20) {
            return;
          }
          window.setTimeout(function () {
            var offset = $('.hue-popover').offset();
            if (!offset) {
              // Popover isn't visible yet, wait a bit and try again
              attempt++;
              initOriginalValues(attempt);
              return;
            }
            if (orientation === 'right') {
              offset.left -= 5;
            } else if (orientation === 'bottom') {
              offset.top -= 5;
            }
            originalHeight = $('.hue-popover').height();
            originalWidth = $('.hue-popover').width();
            originalMidX = offset.left + originalWidth / 2;
            originalMidY = offset.top + originalHeight / 2;
            originalLeftX = offset.left;
            originalRightX = offset.left + originalWidth;
            originalTopY = offset.top;
            originalBottomY = offset.top + originalHeight;
          }, attempt * 20);
        };

        initOriginalValues(0);

        self.saveSize = function () {
          apiHelper.setInTotalStorage('assist', 'popover.size', {
            width: $('.hue-popover').width(),
            height: $('.hue-popover').height()
          });
        };

        self.resizeStart = function (event, ui) {
          preventHide = true;
        };

        self.resizeStop = function (event, ui) {
          if (redrawHeaders) {
            huePubSub.publish('table.extender.redraw', 'sampleTab');
            redrawHeaders = false;
          }

          huePubSub.publish('context.popover.resized');

          // Delay or it will close the popover when releasing at the window borders
          window.setTimeout(function () {
            preventHide = false;
          }, 300);

          self.saveSize();
        };

        var resizeTopBottomHorizontal = function (event, ui) {
          leftX = ui.position.left;
          rightX = ui.position.left + ui.size.width;

          if (rightX < originalMidX + HALF_SIZE_LIMIT_X) {
            ui.size.width = originalMidX + HALF_SIZE_LIMIT_X - ui.position.left;
            rightX = ui.position.left + ui.size.width;
            $('.hue-popover').css('width', ui.size.width + 'px');
          }

          if (leftX > originalMidX - HALF_SIZE_LIMIT_X) {
            ui.position.left = originalMidX - HALF_SIZE_LIMIT_X;
            ui.size.width = ui.originalSize.width - (ui.position.left - ui.originalPosition.left);
            leftX = ui.position.left;
            rightX = ui.position.left + ui.size.width;
            $('.hue-popover').css('left', ui.position.left + 'px');
            $('.hue-popover').css('width', ui.size.width + 'px');
          }

          leftDiff = originalLeftX - leftX;
          rightDiff = originalRightX - rightX;
          $('.hue-popover-arrow').css('margin-left', (leftDiff + rightDiff) / 2 + leftAdjust() + 'px');
        };

        var resizeLeftRightVertical = function (event, ui) {
          if (!redrawHeaders && ui.originalPosition.top !== ui.position.top) {
            redrawHeaders = true;
            huePubSub.publish('table.extender.hide', 'sampleTab');
          }
          topY = ui.position.top;
          bottomY = ui.position.top + ui.size.height;

          if (bottomY < originalMidY + HALF_SIZE_LIMIT_Y) {
            ui.size.height = originalMidY + HALF_SIZE_LIMIT_Y - ui.position.top;
            bottomY = ui.position.top + ui.size.height;
            $('.hue-popover').css('height', ui.size.height + 'px');
          }

          if (topY > originalMidY - HALF_SIZE_LIMIT_Y) {
            ui.position.top = originalMidY - HALF_SIZE_LIMIT_Y;
            ui.size.height = ui.originalSize.height - (ui.position.top - ui.originalPosition.top);
            topY = ui.position.top;
            bottomY = ui.position.top + ui.size.height;
            $('.hue-popover').css('top', ui.position.top + 'px');
            $('.hue-popover').css('height', ui.size.height + 'px');
          }

          topDiff = originalTopY - topY;
          bottomDiff = originalBottomY - bottomY;
          $('.hue-popover-arrow').css('margin-top', (topDiff + bottomDiff) / 2 + topAdjust() + 'px');
        };

        switch(orientation) {
          case 'top':
            self.resizableHandles = "w, nw, n, ne, e";
            self.resize = function (event, ui) {
              resizeTopBottomHorizontal(event, ui);
              // TODO: Implement resize height limits when popover is above
            };
            break;
          case 'right':
            self.resizableHandles = "n, ne, e, se, s";
            self.resize = function (event, ui) {
              resizeLeftRightVertical(event, ui);
              if (ui.size.width < 350) {
                ui.size.width = 350;
                $('.hue-popover').css('width', 350 + 'px');
              }
            };
            break;
          case 'bottom':
            self.resizableHandles = "e, se, s, sw, w";
            self.resize = function (event, ui) {
              resizeTopBottomHorizontal(event, ui);
              if (ui.size.height < 200) {
                ui.size.height = 200;
                $('.hue-popover').css('height', 200 + 'px');
              }
            };
            break;
          case 'left':
            self.resizableHandles = "s, sw, w, nw, n";
            self.resize = function (event, ui) {
              resizeLeftRightVertical(event, ui);
              // TODO: Implement resize width limits when popover is on the left
            };
            break;
        }
      }

      function ContextPopoverViewModel(params) {
        var self = this;
        self.disposals = [];

        var apiHelper = ApiHelper.getInstance();

        self.left = ko.observable(0);
        self.top = ko.observable(0);

        var popoverSize = apiHelper.getFromTotalStorage('assist', 'popover.size', {
          width: 450,
          height: 400
        });

        self.width = ko.observable(popoverSize.width);
        self.height = ko.observable(popoverSize.height);

        self.leftAdjust = ko.observable(0);
        self.topAdjust = ko.observable(0);
        self.data = params.data;
        self.sourceType = params.sourceType;
        self.namespace = params.namespace;
        self.compute = params.compute;
        self.defaultDatabase = params.defaultDatabase;
        self.close = hidePopover;
        self.onSampleClick = params.onSampleClick;
        var orientation = params.orientation || 'bottom';
        self.contents = null;
        self.resizeHelper = new ResizeHelper(orientation, self.leftAdjust, self.topAdjust);

        if (typeof params.source.element !== 'undefined') {
          // Track the source element and close the popover if moved
          var $source = $(params.source.element);
          var originalSourceOffset = $source.offset();
          var currentSourceOffset;

          var detectMoveInterval = window.setInterval(function () {
            currentSourceOffset = $source.offset();
            if (currentSourceOffset.top !== originalSourceOffset.top) {
              hidePopover();
            }
          }, 200);

          self.disposals.push(function () {
            window.clearInterval(detectMoveInterval);
          });
        }

        var windowWidth = $(window).width();
        var fitHorizontally = function () {
          var left = params.source.left + Math.round((params.source.right - params.source.left) / 2) - (self.width() / 2);
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

        var windowHeight = $(window).height();
        var fitVertically = function () {
          var top = params.source.top + Math.round((params.source.bottom - params.source.top) / 2) - (self.height() / 2);
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

        if (self.isCatalogEntry && params.data.catalogEntry.getSourceType() === 'solr' && params.data.catalogEntry.isField()) {
          self.isCollection = true;
          self.isCatalogEntry = false;
          self.namespace = params.data.catalogEntry.namespace;
          self.compute = params.data.catalogEntry.compute;
        }

        self.showInAssistEnabled = (typeof params.showInAssistEnabled !== 'undefined' ? params.showInAssistEnabled : true)
                && (self.isDocument || self.isCollection || self.isCatalogEntry);
        self.openInDashboardEnabled = self.isCatalogEntry && params.data.catalogEntry.path.length <= 2;
        self.openInTableBrowserEnabled = self.isCatalogEntry && params.data.catalogEntry.path.length <= 2;
        self.expandColumnsEnabled = self.isAsterisk;

        self.pinEnabled = params.pinEnabled && !self.isFunction && !self.isAsterisk && !self.isStorageEntry && !self.isCatalogEntry;

        if (self.isCatalogEntry) {
          self.contents = new DataCatalogContext({ popover: self, catalogEntry: params.data.catalogEntry });
          self.titleTemplate = 'context-catalog-entry-title';
          self.contentsTemplate = 'context-catalog-entry-contents';
        } else if (self.isFunction) {
          self.contents = new FunctionContextTabs(self.data, self.sourceType);
          self.title = self.data.function;
          self.iconClass = 'fa-superscript';
        } else if (self.isStorageEntry) {
          self.contents = new StorageContext({ popover: self, storageEntry: params.data.storageEntry, editorLocation: params.data.editorLocation });
          self.titleTemplate = 'context-storage-entry-title';
          self.contentsTemplate = 'context-storage-entry-contents';
        } else if (self.isAsterisk) {
          self.contents = new AsteriskContextTabs(self.data, self.sourceType, self.namespace, self.compute, self.defaultDatabase);
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
          var hideTimeout = -1;
          var onLeave = function () {
            hideTimeout = window.setTimeout(function () {
              $('.hue-popover').fadeOut(200, function () {
                hidePopover();
              })
            }, 1000);
          };

          var onEnter = function () {
            window.clearTimeout(hideTimeout);
          };

          $(params.delayedHide).add($('.hue-popover')).on('mouseleave', onLeave).on('mouseenter', onEnter);

          var keepPopoverOpenOnClick = function () {
            window.clearTimeout(hideTimeout);
            $(params.delayedHide).add($('.hue-popover')).off('mouseleave', onLeave).off('mouseenter', onEnter);
          };

          $('.hue-popover').on('click', keepPopoverOpenOnClick);

          self.disposals.push(function () {
            $(params.delayedHide).add($('.hue-popover')).off('mouseleave', onLeave).off('mouseenter', onEnter);
            $('.hue-popover').off('click', keepPopoverOpenOnClick);
          });
        }

        var closeOnEsc = function (e) {
          if (e.keyCode === 27) {
            hidePopover();
          }
        };

        $(document).on('keyup', closeOnEsc);

        self.disposals.push(function () {
          $(document).off('keyup', closeOnEsc);
        });

        window.setTimeout(function() {
          $(document).off('click.context');
          $(document).on('click.context', function (event) {
            if (jQuery.contains(document, event.target) && !$.contains($('#contextPopover')[0], event.target) && ($('.modal')[0].length === 0 || !$.contains($('.modal')[0], event.target))) {
              hidePopover();
            }
          });
        }, 0);

        self.disposals.push(function () {
          $(document).off('click.context');
        })
      }

      ContextPopoverViewModel.prototype.dispose = function() {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }

        if(self.contents && self.contents.dispose) {
          self.contents.dispose();
        }
        huePubSub.publish('context.popover.dispose');
      };

      ContextPopoverViewModel.prototype.pin = function () {
        var self = this;
        hidePopover();
        if (self.contents && typeof self.contents.sample !== 'undefined') {
          self.contents.sample.fetchedData(undefined);
        }
        huePubSub.publish('sql.context.pin', self);
        if (self.contents && self.contents.activeTab() === 'sample') {
          self.contents.refetchSamples();
        }
      };

      ko.components.register('context-popover', {
        viewModel: ContextPopoverViewModel,
        template: { element: 'context-popover-template' }
      });

      huePubSub.subscribe('context.popover.hide', hidePopover);

      huePubSub.subscribe('context.popover.show', function (details) {
        hidePopover();
        var $contextPopover = $('<div id="contextPopover" data-bind="component: { name: \'context-popover\', params: $data }" />');
        $(HUE_CONTAINER).append($contextPopover);
        ko.applyBindings(details, $contextPopover[0]);
        huePubSub.publish('context.popover.shown');
      });

      var SqlContextContentsGlobalSearch = function (params) {
        var self = this;
        self.contents = ko.observable();

        self.disposals = [];

        self.isCatalogEntry = params.data.type === 'catalogEntry'
                || params.data.type.toLowerCase() === 'database'
                || params.data.type.toLowerCase() === 'table'
                || params.data.type.toLowerCase() === 'field'
                || params.data.type.toLowerCase() === 'view';

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

        var adaptedData = { identifierChain: [] };

        var path = params.data.originalName.split('.');
        path.forEach(function (part) {
          adaptedData.identifierChain.push({ name: part });
        });

        var sourceType = params.data.sourceType && params.data.sourceType.toLowerCase();

        if (!sourceType || sourceType === 'hive') {
          huePubSub.publish('cluster.config.get.config', function (clusterConfig) {
            if (clusterConfig) {
              var defaultEditor = clusterConfig['default_sql_interpreter'];
              if (!sourceType || (sourceType === 'hive' && defaultEditor === 'impala')) {
                sourceType = defaultEditor;
              }
            }
          });
        }

        if (self.isCatalogEntry) {
          ContextCatalog.getNamespaces({ sourceType: sourceType }).done(function (context) {
            // TODO: Namespace and compute selection for global search results?
            DataCatalog.getEntry({ sourceType: sourceType, namespace: context.namespaces[0], compute: context.namespaces[0].computes[0], path: path, definition: { type: params.data.type.toLowerCase() }}).done(function (catalogEntry) {
              catalogEntry.navigatorMeta = params.data;
              catalogEntry.navigatorMetaPromise = $.Deferred().resolve(catalogEntry.navigatorMeta);
              catalogEntry.saveLater();
              self.contents(new DataCatalogContext({ popover: self, catalogEntry: catalogEntry }));
            });
          });
        } else if (self.isDocument) {
          self.contents(new DocumentContext(params.data));
        } else if (self.isPartition) {
          self.contents(new PartitionContext(params.data));
        }
      };

      SqlContextContentsGlobalSearch.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
        if (self.contents && self.contents.dispose) {
          self.contents.dispose();
        }

        huePubSub.publish('context.popover.dispose');
      };

      ko.components.register('context-popover-contents-global-search', {
        viewModel: SqlContextContentsGlobalSearch,
        template: { element: 'global-search-context' }
      })
    })();
  </script>
</%def>