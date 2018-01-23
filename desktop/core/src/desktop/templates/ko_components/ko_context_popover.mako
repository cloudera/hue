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

<%def name="contextPopover()">
  <script type="text/html" id="context-popover-footer">
    <div class="context-popover-flex-bottom-links">
      <div class="context-popover-link-row">
        <a class="inactive-action pointer" data-bind="visible: showInAssistEnabled, click: function() { huePubSub.publish('context.popover.show.in.assist') }">
          <i style="font-size: 11px;" title="${ _("Show in Assist...") }" class="fa fa-search"></i> ${ _("Assist") }
        </a>
        % if HAS_SQL_ENABLED.get():
        <a class="inactive-action pointer" data-bind="visible: openInDashboardEnabled, click: function() { huePubSub.publish('context.popover.open.in.dashboard') }">
          <i style="font-size: 11px;" title="${ _("Open in Dashboard...") }" class="fa fa-external-link"></i> ${ _("Dashboard") }
        </a>
        % endif
        % if not IS_EMBEDDED.get():
        <!-- ko if: typeof sourceType === 'undefined' || sourceType !== 'solr' -->
        <a class="inactive-action pointer" data-bind="visible: openInTableBrowserEnabled, click: function() { huePubSub.publish('context.popover.open.in.metastore', isTable || isView ? 'table' : 'db') }">
          <i style="font-size: 11px;" title="${ _("Open in Table Browser...") }" class="fa fa-external-link"></i> ${ _("Table Browser") }
        </a>
        <!-- /ko -->
        % endif
        <a class="inactive-action pointer" data-bind="visible: replaceEditorContentEnabled, click: function() { huePubSub.publish('context.popover.replace.in.editor') }">
          <i style="font-size: 11px;" title="${ _("Replace the editor content...") }" class="fa fa-pencil"></i> ${ _("Insert in the editor") }
        </a>
        <a class="inactive-action pointer" data-bind="visible: openInFileBrowserEnabled, click: function() { huePubSub.publish('context.popover.open.in.file.browser') }">
          <i style="font-size: 11px;" title="${ _("Open in File Browser...") }" class="fa fa-external-link"></i> ${ _("File Browser") }
        </a>
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

  <script type="text/html" id="context-popover-columns">
    <div class="context-popover-flex-fill" data-bind="with: fetchedData">
      <!-- ko component: { name: 'sql-columns-table', params: { columns: extended_columns } } --><!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="context-popover-table-details">
    <!-- ko with: fetchedData -->
    <div class="context-popover-table-details">
      <!-- ko if: details && details.properties -->
      <div class="context-popover-header">${ _("Properties") }</div>
      <div class="context-popover-section">
        <span style="margin-right: 5px;" title="${ _('Owner') }">
          <i class="fa fa-fw fa-user muted"></i> <span data-bind="text: details.properties.owner"></span>
        </span>
        <span style="margin-right: 5px;" title="${ _('Created') }">
          <i class="fa fa-fw fa-clock-o muted"></i> <span data-bind="text: localeFormat(details.properties.create_time)"></span>
        </span>
        <span style="margin-right: 5px;" title="${ _('Format') }">
          <i class="fa fa-fw fa-file-o muted"></i> <span data-bind="text: details.properties.format"></span>
        </span>
        <span style="margin-right: 5px; white-space: nowrap" title="${ _('Type') }">
          <i class="fa fa-fw fa-archive muted"></i> <span data-bind="visible: details.properties.table_type === 'MANAGED_TABLE'" style="display:none;">${_('Managed')}</span><span data-bind="visible: !details.stats.table_type === 'EXTERNAL_TABLE'" style="display:none;">${_('External')}</span>
        </span>
      </div>
      <!-- /ko -->
      <!-- ko if: typeof comment !== 'undefined' && comment !== '' && comment !== null -->
      <div class="context-popover-header">${ _("Comment") }</div>
      <div class="context-popover-section" style="font-style: italic;" data-bind="text: comment"></div>
      <!-- /ko -->
      %if has_navigator(user):
        <!-- ko if: $parent.sourceType === 'hive' || $parent.sourceType === 'impala' -->
        <div class="context-popover-header">${ _("Tags") }</div>
        <div class="context-popover-section" data-bind="component: { name: 'nav-tags', params: $parent } "></div>
        <!-- /ko -->
      %endif
      <!-- ko if: typeof viewSql !== 'undefined' -->
      <div class="context-popover-header">${ _("View SQL") }</div>
      <!-- ko hueSpinner: { spin: loadingViewSql, center: true, size: 'large' } --><!-- /ko -->
      <!-- ko ifnot: loadingViewSql -->
      <div class="context-popover-section" class="pointer" title="${ _("Click to copy") }" data-bind="tooltip: { placement: 'bottom' }, clickToCopy: viewSql, click: function () { huePubSub.publish('context.popover.hide'); }, highlight: { value: viewSql, formatted: true, dialect: $parent.sourceType }"></div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="context-popover-column-details">
    <div class="context-popover-flex-fill" data-bind="with: fetchedData, nicescroll">
      <div>
        <div style="margin: 0 0 5px 10px;"><a class="pointer" data-bind="text: name, attr: { title: name }, click: function() { huePubSub.publish('context.popover.scroll.to.column', name); }"></a> <!-- ko if: typeof type !== 'undefined' -->(<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)<!-- /ko --></div>
        <!-- ko if: typeof comment !== 'undefined' && comment !== '' && comment !== null -->
        <div class="context-popover-header">${ _("Comment") }</div>
        <div class="context-popover-section" data-bind="text: comment"></div>
        <!-- /ko -->
        %if has_navigator(user):
          <!-- ko if: $parent.sourceType === 'hive' || $parent.sourceType === 'impala' -->
          <div class="context-popover-header">${ _("Tags") }</div>
          <div class="context-popover-section" data-bind="component: { name: 'nav-tags', params: $parent } "></div>
          <!-- /ko -->
        %endif
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-complex-details">
    <div class="context-popover-flex-fill" data-bind="with: fetchedData, nicescroll">
      <div style="margin: 15px;">
        <a class="pointer" data-bind="visible: typeof sample !== 'undefined', text: name || $parents[2].title, attr: { title: name || $parents[2].title }, click: function() { huePubSub.publish('context.popover.scroll.to.column', name || $parents[2].title); }"></a>
        <span data-bind="visible: typeof sample === 'undefined', text: name || $parents[2].title, attr: { title: name || $parents[2].title }"></span> <!-- ko if: typeof type !== 'undefined' -->(<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)<!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-table-and-column-unknown">
    <div class="context-popover-flex-fill">
      <div style="margin: 15px;">
        <div class="alert" data-bind="text: message"></div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-table-and-column-sample">
    <div class="context-popover-flex-fill context-popover-sample-container" data-bind="with: fetchedData">
      <div class="context-popover-sample sample-scroll">
        <!-- ko if: rows.length == 0 -->
        <div class="alert">${ _('The selected table has no data.') }</div>
        <!-- /ko -->
        <!-- ko if: rows.length > 0 -->
        <table id="samples-table" class="samples-table table table-condensed">
          <thead>
          <tr>
            <th style="width: 10px">&nbsp;</th>
            <!-- ko foreach: headers -->
            <th data-bind="text: $data"></th>
            <!-- /ko -->
          </tr>
          </thead>
          <tbody>
          </tbody>
        </table>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-table-analysis">
    <div class="context-popover-flex-fill" data-bind="with: fetchedData, niceScroll">
      <!-- ko if: stats.length > 0 -->
        <table class="table table-condensed">
          <tbody data-bind="foreach: stats">
            <tr>
              <td><strong data-bind="text: data_type"></strong></td>
              <td data-bind="text: $parents[1].formatAnalysisValue(data_type, comment)"></td>
            </tr>
          </tbody>
        </table>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="context-popover-column-analysis">
    <div class="context-popover-flex-fill" data-bind="with: fetchedData, niceScroll">
      <table class="table table-condensed">
        <tbody data-bind="foreach: stats">
          <tr>
            <td><strong data-bind="text: Object.keys($data)[0]"></strong></td>
            <td data-bind="text: $data[Object.keys($data)[0]]"></td>
          </tr>
        </tbody>
      </table>
    </div>
  </script>

  <script type="text/html" id="context-popover-database-details">
    <div class="context-popover-flex-fill">
      <div class="context-popover-flex">
        <div data-bind="if: $parent.comment">
          <div class="context-popover-header">${ _("Comment") }</div>
          <div class="context-popover-section" style="font-style: italic;" data-bind="text: $parent.comment"></div>
        </div>
        <div class="context-popover-header">${_('Tags')}</div>
        <div class="context-popover-flex-fill sql-columns-table" style="position:relative; height: 100%; overflow-y: auto;">
          <div data-bind="component: { name: 'nav-tags', params: $data } "></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-hdfs-details">
    <div class="context-popover-flex-fill" data-bind="with: details, niceScroll">
      <div style="padding: 8px">
        <div style="margin: 10px 10px 18px 10px;">
          <div data-bind="hdfsTree: { isS3: $data.path.indexOf('s3a://') === 0, path: $data.path, selectedPath: $parent.selectedPath }"></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-collection-stats-details">
    <div class="context-popover-flex-fill" data-bind="niceScroll">
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
    <div class="context-popover-flex-fill" data-bind="niceScroll">
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
    <div class="context-popover-flex-fill" data-bind="with: details, niceScroll">
      <div style="padding: 8px">
        <p style="margin: 10px 10px 18px 10px;"><span style="white-space: pre;" class="monospace" data-bind="text: signature"></span></p>
        <p><span data-bind="text: description"></span></p>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="context-popover-table-partitions">
    <div class="context-popover-flex-fill" data-bind="with: fetchedData, niceScroll">
      <div class="context-popover-header">${_('Columns')}</div>
      <div>
        <table class="table table-condensed table-nowrap">
          <thead>
          <tr>
            <th style="width: 1%">&nbsp;</th>
            <th>${_('Name')}</th>
          </tr>
          </thead>
          <tbody data-bind="foreach: partition_keys_json">
          <tr>
            <td data-bind="text: $index() + 1"></td>
            <td><a href="#" data-bind="text: $data, click: function() { huePubSub.publish('context.popover.scroll.to.column', $data); }"></a></td>
          </tr>
          </tbody>
        </table>
      </div>
      <div class="context-popover-header">${_('Partitions')}</div>
      <table class="table table-condensed table-nowrap">
        <thead>
          <tr>
            <th style="width: 1%">&nbsp;</th>
            <th>${_('Values')}</th>
            <th>${_('Spec')}</th>
            <th>${_('Browse')}</th>
          </tr>
        </thead>
        <tbody data-bind="foreach: partition_values_json">
          <tr>
            <td data-bind="text: $index() + 1"></td>
            <td><a href="#" data-bind="click: function () { window.open(readUrl, '_blank'); return false; }, text: '[\'' + columns.join('\',\'') + '\']'"></a></td>
            <td data-bind="text: partitionSpec"></td>
            <td>
              <a href="#" data-bind="click: function () { window.open(readUrl, '_blank'); return false; }" title="${_('Data')}"><i class="fa fa-th"></i></a> <a href="#" data-bind="click: function () { window.open(browseUrl, '_blank'); return false; }" title="${_('Files')}"><i class="fa fa-file-o"></i></a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </script>

  <script type="text/html" id="generic-document-context-template">
    <div style="width:100%; text-align: center; margin-top: 30px; font-size: 100px; color: #787878;" data-bind="template: { name: 'document-icon-template', data: { document: { isDirectory: type === 'directory', definition: function() { return $data } } } }"></div>
    <div style="width: 100%; margin-top: 20px; text-align:center">
      <!-- ko if: type === 'directory' -->
      <a style="font-size: 20px;" href="javscript:void(0)" data-bind="text: name, publish: 'context.popover.show.in.assist'"></a>
      <!-- /ko -->
      <!-- ko if: type !== 'directory' -->
      <a style="font-size: 20px;" href="javscript:void(0)" data-bind="text: name, hueLink: link, click: function () { $parents[1].close(); }"></a>
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
           <a style="font-size: 20px;" href="javscript:void(0)" data-bind="text: interpreter.displayName, hueLink: interpreter.page, click: function () { $parents[1].close(); }, attr: { 'title': interpreter.tooltip }"></a>
         </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="context-document-details">
    <div class="context-popover-flex-fill" style="overflow: auto;" data-bind="niceScroll">
      <div style="padding: 8px">
        <!-- ko if: typeof documentContents() !== 'undefined' && typeof documentContents().snippets !== 'undefined' -->

        <!-- ko with: details -->
        <div class="context-popover-doc-header-link" ><a href="javscript:void(0)" data-bind="hueLink: link, click: function () { $parents[1].close(); }"><!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: false } } --><!-- /ko --> <span data-bind="text:name"></span></a></div>
        <!-- ko if: description -->
        <div class="context-popover-doc-description" data-bind="html: description"></div>
        <!-- /ko -->
        <!-- /ko -->

        <div class="context-popover-header" style="margin: 10px 0 5px 0">${_('Contents')}</div>
        <!-- ko with: documentContents -->
        <!-- ko foreach: snippets -->
        <div data-bind="highlight: { value: statement_raw, formatted: true, dialect: type }"></div>
        <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: typeof documentContents() === 'undefined' || typeof documentContents().snippets === 'undefined' -->
        <div style="width: 100%;" data-bind="template: { name: 'generic-document-context-template', data: details }"></div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="context-popover-template">
    <div class="hue-popover" data-bind="css: orientationClass, style: { 'left': left() + 'px', 'top': top() + 'px', 'width': width() + 'px', height: height() + 'px' }, resizable: { containment: 'document', handles: resizeHelper.resizableHandles, start: resizeHelper.resizeStart, stop: resizeHelper.resizeStop, resize: resizeHelper.resize }">
      <div class="hue-popover-arrow" data-bind="style: { 'margin-left': leftAdjust() + 'px',  'margin-top': topAdjust() + 'px' }"></div>
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
      <!-- ko template: 'context-popover-contents' --><!-- /ko -->
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

  <script type="text/javascript">
    (function () {

      var HALF_SIZE_LIMIT_X = 130;
      var HALF_SIZE_LIMIT_Y = 100;
      var HALF_ARROW = 6;

      var preventHide = false;

      var hidePopover = function () {
        if (! preventHide) {
          if ($('#contextPopover').length > 0) {
            ko.cleanNode($('#contextPopover')[0]);
            $('#contextPopover').remove();
            $(document).off('click', hideOnClickOutside);
            huePubSub.publish('context.popover.hidden');
          }
        }
      };

      var hideOnClickOutside = function (event) {
        if (jQuery.contains(document, event.target) && !$.contains($('#contextPopover')[0], event.target) && ($('.modal')[0].length === 0 || !$.contains($('.modal')[0], event.target))) {
          hidePopover();
        }
      };

      function GenericTabContents(identifierChain, sourceType, defaultDatabase, apiFunction, parent) {
        var self = this;
        self.identifierChain = identifierChain;
        self.sourceType = sourceType;
        self.defaultDatabase = defaultDatabase;
        self.apiHelper = ApiHelper.getInstance();
        self.apiFunction = apiFunction;
        self.parent = parent;

        self.fetchedData = ko.observable();
        self.loading = ko.observable(false);
        self.hasErrors = ko.observable(false);
      }

      GenericTabContents.prototype.formatAnalysisValue = function (type, val) {
        if (type === 'last_modified_time' || type === 'transient_lastDdlTime') {
          return localeFormat(val * 1000);
        }
        if (type.toLowerCase().indexOf('size') > -1) {
          return filesize(val);
        }
        return val;
      };

      GenericTabContents.prototype.fetch = function (callback) {
        var self = this;
        if (self.loading()) {
          return;
        }
        self.loading(true);
        self.hasErrors(false);

        self.apiFunction.bind(self.apiHelper)({
          sourceType: self.sourceType,
          identifierChain: self.identifierChain,
          defaultDatabase: self.defaultDatabase,
          silenceErrors: true,
          successCallback: function (data) {
            if (data.code === 500) {
              self.loading(false);
              self.hasErrors(true);
              if (data.notFound) {
                self.parent.notFound(data);
              }
              return;
            }
            if (typeof data.extended_columns !== 'undefined') {
              data.extended_columns.forEach(function (column) {
                column.extendedType = column.type.replace(/</g, '&lt;').replace(/>/g, '&lt;');
                if (column.type.indexOf('<') !== -1) {
                  column.type = column.type.substring(0, column.type.indexOf('<'));
                }
              });
            }
            if (typeof data.properties !== 'undefined') {
              data.properties.forEach(function (property) {
                if (property.col_name.toLowerCase() === 'view original text:') {
                  data.viewSql = ko.observable();
                  data.loadingViewSql = ko.observable(true);
                  ApiHelper.getInstance().formatSql(property.data_type).done(function (formatResponse) {
                    if (formatResponse.status == 0) {
                      data.viewSql(formatResponse.formatted_statements);
                    } else {
                      data.viewSql(property.data_type);
                    }
                  }).fail(function () {
                    data.viewSql(property.data_type);
                  }).always(function () {
                    data.loadingViewSql(false);
                  })
                }
              })
            }
            self.fetchedData(data);
            self.loading(false);
            if (typeof callback === 'function') {
              callback(data);
            }
          },
          errorCallback: function () {
            self.loading(false);
            self.hasErrors(true);
          }
        });
      };

      function TableAndColumnContextTabs(data, sourceType, defaultDatabase, isColumn, isComplex) {
        var self = this;
        self.tabs = ko.observableArray();
        self.disposals = [];

        var apiHelper = ApiHelper.getInstance();

        self.columns = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAutocomplete, self);
        self.columnDetails = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAutocomplete, self);
        self.tableDetails = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, sourceType === 'solr' ? $.noop : apiHelper.fetchAnalysis_OLD, self);
        self.sample = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchSamples, self);
        self.analysis = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAnalysis_OLD, self);
        self.partitions = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchPartitions, self);

        self.hasErrors = false;
        self.isTable = !isColumn && !isComplex;

        self.title = data.identifierChain[data.identifierChain.length - 1].name;

        self.activeTab = ko.observable();

        self.activeTab.subscribe(function (newValue) {
          if (newValue === 'sample') {
            if (typeof self.sample.fetchedData() === 'undefined') {
              if (!isComplex) {
                self.sample.fetch(self.initializeSamplesTable);
              } else {
                var data = self.columnDetails.fetchedData();
                var rows = [];
                data.sample.forEach(function (sample) {
                  rows.push([sample]);
                });
                self.sample.fetchedData({
                  headers: [ data.name || self.title ],
                  rows: rows
                });
                self.initializeSamplesTable(self.sample.fetchedData());
              }
            }
          } else if (newValue === 'complexDetails') {
            if (typeof self.columnDetails.fetchedData() === 'undefined') {
              self.columnDetails.fetch(function (data) {
                if (data.sample) {
                  self.tabs.push({
                    id: 'sample',
                    label: '${ _("Sample") }',
                    template: 'context-popover-table-and-column-sample',
                    templateData: self.sample,
                    errorText: '${ _("There was a problem loading the samples.") }'
                  });
                }
              })
            }
          } else if (!self.hasErrors && typeof self[newValue].fetchedData() === 'undefined') {
            self[newValue].fetch();
          }
        });

        if (isColumn) {
          self.tabs.push({
            id: 'columnDetails',
            label: '${ _("Details") }',
            template: 'context-popover-column-details',
            templateData: self.columnDetails,
            errorText: '${ _("There was a problem loading the column details.") }',
            isColumn: true
          });
          self.activeTab('columnDetails');
        } else if (isComplex) {
          self.tabs.push({
            id: 'complexDetails',
            label: '${ _("Details") }',
            template: 'context-popover-complex-details',
            templateData: self.columnDetails,
            errorText: '${ _("There was a problem loading the details.") }',
            isColumn: false
          });
          self.activeTab('complexDetails');
        } else {
          self.tabs.push({
            id: 'columns',
            label: '${ _("Columns") }',
            template: 'context-popover-columns',
            templateData: self.columns,
            errorText: '${ _("There was a problem loading the columns.") }',
            isColumn: false
          });
          if (sourceType !== 'solr') {
            self.tabs.push({
              id: 'tableDetails',
              label: '${ _("Details") }',
              template: 'context-popover-table-details',
              templateData: self.tableDetails,
              errorText: '${ _("There was a problem loading the table details.") }',
              isColumn: false
            });
          }
          self.activeTab('columns');
        }

        if (!isComplex) {
          self.tabs.push({
            id: 'sample',
            label: '${ _("Sample") }',
            template: 'context-popover-table-and-column-sample',
            templateData: self.sample,
            errorText: '${ _("There was a problem loading the samples.") }',
            isColumn: isColumn,
            title: self.title,
            enableSampleError: true
          });
        }

        if (isColumn) {
          self.columnDetails.fetch(function (data) {
            self.tabs.push({
              id: 'analysis',
              label: '${ _("Analysis") }',
              template: 'context-popover-column-analysis',
              templateData: self.analysis,
              errorText: '${ _("There was a problem loading the column analysis.") }',
              isColumn: true
            });
          });
        } else if (!isComplex) {
          self.tableDetails.fetch(function (data) {
            if (data.partition_keys.length === 0) {
              self.tabs.push({
                id: 'analysis',
                label: '${ _("Analysis") }',
                template: 'context-popover-table-analysis',
                templateData: self.analysis,
                errorText: '${ _("There was a problem loading the table analysis.") }',
                isColumn: false
              });
            } else if (data.partition_keys.length > 0) {
              self.tabs.push({
                id: 'partitions',
                label: '${ _("Partitions") }',
                template: 'context-popover-table-partitions',
                templateData: self.partitions,
                errorText: '${ _("There was a problem loading the table partitions.") }',
                isColumn: false
              });
            }
          });
        }

        var sampleInterval = window.setInterval(function () {
          if (self.activeTab() !== 'sample') {
            return;
          }
          var $t = $('.samples-table');
          if ($t.length === 0) {
            return;
          }

          $t.parents('.dataTables_wrapper').getNiceScroll().resize();
        }, 300);

        self.disposals.push(function () {
          window.clearInterval(sampleInterval);
        });

        var performScrollToColumn = function (colName) {
          self.activeTab('sample');
          window.setTimeout(function () {
            var _t = $('.samples-table');
            var _col = _t.find("th").filter(function () {
              return $.trim($(this).text()).endsWith(colName);
            });
            _t.find(".columnSelected").removeClass("columnSelected");
            var _colSel = _t.find("tr th:nth-child(" + (_col.index() + 1) + ")");
            if (_colSel.length > 0) {
              _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
              _t.parent().animate({
                scrollLeft: _colSel.position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
              }, 300, function(){
                _t.data('scrollToCol', _col.index());
                _t.data('scrollToRow', null);
                _t.data('scrollAnimate', true);
                _t.data('scrollInPopover', true);
                _t.parent().trigger('scroll');
              });
            }
          }, 0);
        };

        var scrollPubSub = huePubSub.subscribe('context.popover.scroll.to.column', function (colName) {
          if (typeof self.sample.fetchedData() === 'undefined') {
            self.activeTab('sample');
            self.sample.fetch(function (data) {
              self.initializeSamplesTable(data);
              window.setTimeout(function () {
                performScrollToColumn(colName);
              }, 0);
            });
          } else {
            performScrollToColumn(colName);
          }
        });
        self.disposals.push(function () {
          scrollPubSub.remove();
        });

        apiHelper.identifierChainToPath({
          sourceType: sourceType,
          defaultDatabase: defaultDatabase,
          identifierChain: data.identifierChain
        }).done(function (path) {
          var showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', function () {
            huePubSub.publish('assist.db.highlight', {
              sourceType: sourceType,
              path: path
            });
          });
          self.disposals.push(function () {
            showInAssistPubSub.remove();
          })
        });

        self.initializeSamplesTable = function (data) {
          window.setTimeout(function () {
            var $t = $('.samples-table');

            if ($t.parent().hasClass('dataTables_wrapper')) {
              if ($t.parent().data('scrollFnDt')) {
                $t.parent().off('scroll', $t.parent().data('scrollFnDt'));
              }
              $t.unwrap();
              if ($t.children('tbody').length > 0) {
                $t.children('tbody').empty();
              } else {
                $t.children('tr').remove();
              }
              $t.data('isScrollAttached', null);
              $t.data('data', []);
            }
            var dt = $t.hueDataTable({
              i18n: {
                NO_RESULTS: "${_('No results found.')}",
                OF: "${_('of')}"
              },
              fnDrawCallback: function (oSettings) {
              },
              scrollable: '.dataTables_wrapper',
              forceInvisible: 10
            });

            $t.parents('.dataTables_wrapper').height($t.parents('.sample-scroll').parent().height());

            $t.jHueTableExtender2({
              fixedHeader: true,
              fixedFirstColumn: true,
              fixedFirstColumnTopMargin: -2,
              headerSorting: false,
              includeNavigator: false,
              parentId: 'sampleTab',
              noSort: true,
              mainScrollable: '.sample-scroll > .dataTables_wrapper'
            });

            huePubSub.subscribe('context.popover.resized', function () {
              $t.parent().height($t.parents('.context-popover-sample-container').height());
            });

            self.disposals.push(function () {
              if ($t.data('plugin_jHueTableExtender2')) {
                $t.data('plugin_jHueTableExtender2').destroy();
              }
              huePubSub.removeAll('context.popover.resized');
            });

            hueUtils.initNiceScroll($t.parents('.dataTables_wrapper'));

            if (data && data.rows) {
              var _tempData = [];
              $.each(data.rows, function (index, row) {
                var _row = row.slice(0); // need to clone the array otherwise it messes with the caches
                _row.unshift(index + 1);
                _tempData.push(_row);
              });
              if (_tempData.length > 0) {
                dt.fnAddData(_tempData);
              }
            }
          }, 0);
        };
      }

      TableAndColumnContextTabs.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      TableAndColumnContextTabs.prototype.notFound = function (data) {
        var self = this;
        self.hasErrors = true;
        var message;
        if (data.error && data.error.indexOf('10001]:') !== -1) {
          message = data.error.substring(data.error.indexOf('10001]:') + 8);
        } else {
          message = '${ _("Could not load") }' + ': ' + self.title
        }
        self.tabs([{
          id: 'notFound',
          label: '${ _("Details") }',
          templateData: {
            loading: ko.observable(false),
            hasErrors: ko.observable(false),
            message: message
          },
          template: 'context-popover-table-and-column-unknown',
          title: self.title
        }]);
        self.activeTab('notFound');
      };

      TableAndColumnContextTabs.prototype.refetchSamples = function () {
        var self = this;
        self.sample.fetch(self.initializeSamplesTable);
      };

      function DatabaseContextTabs(data, sourceType, defaultDatabase) {
        var self = this;
        self.disposals = [];
        self.dbComment = ko.observable('');
        var dbName = data.identifierChain[data.identifierChain.length - 1].name;
        var catalogEntry = DataCatalog.getEntry({ sourceType: sourceType, path: [dbName], definition: { type: 'database' }})

        catalogEntry.getComment().done(self.dbComment);
        self.tabs = [
          { id: 'details', label: '${ _("Details") }', comment : self.dbComment, template: 'context-popover-database-details', templateData: new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, ApiHelper.getInstance().fetchAutocomplete) }
        ];
        self.activeTab = ko.observable('details');

        var showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', function () {
          huePubSub.publish('assist.db.highlight', {
            sourceType: sourceType,
            path: catalogEntry.path
          });
        });

        self.disposals.push(function () {
          showInAssistPubSub.remove();
        })
      }

      DatabaseContextTabs.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      function AsteriskData(data, sourceType, defaultDatabase) {
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
          var sqlAutocompleter = new SqlAutocompleter2({
            snippet: {
              type: function () {
                return sourceType;
              }
            }
          });
          huePubSub.publish('ace.replace', {
            location: data.location,
            text: $.map(colsToExpand, function (column) {
              if (column.tableAlias) {
                return sqlAutocompleter.backTickIfNeeded(column.tableAlias) + '.' + sqlAutocompleter.backTickIfNeeded(column.name);
              }
              if (colIndex[column.name]) {
                return sqlAutocompleter.backTickIfNeeded(column.table) + '.' + sqlAutocompleter.backTickIfNeeded(column.name);
              }
              return sqlAutocompleter.backTickIfNeeded(column.name)
            }).join(', ')
          });
          huePubSub.publish('context.popover.hide');
        };

        var apiHelper = ApiHelper.getInstance();
        var deferrals = [];
        data.tables.forEach(function (table) {
          if (table.identifierChain) {
            var fetchDeferred = $.Deferred();
            deferrals.push(fetchDeferred);
            apiHelper.fetchAutocomplete({
              sourceType: sourceType,
              defaultDatabase: defaultDatabase,
              identifierChain: table.identifierChain,
              successCallback: function (data) {
                if (typeof data.extended_columns !== 'undefined') {
                  data.extended_columns.forEach(function (column) {
                    column.extendedType = column.type.replace(/</g, '&lt;').replace(/>/g, '&lt;');
                    if (column.type.indexOf('<') !== -1) {
                      column.type = column.type.substring(0, column.type.indexOf('<'));
                    }
                    column.selected = ko.observable(false);
                    column.table = table.identifierChain[table.identifierChain.length - 1].name;
                    if (table.alias) {
                      column.tableAlias = table.alias
                    }
                  });
                }
                self.columns = self.columns.concat(data.extended_columns);
                fetchDeferred.resolve();
              },
              silenceErrors: true,
              errorCallback: fetchDeferred.reject
            })
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

      function AsteriskContextTabs(data, sourceType, defaultDatabase) {
        var self = this;
        self.data = new AsteriskData(data, sourceType, defaultDatabase);

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'context-popover-asterisk-details', templateData: self.data }
        ];
        self.activeTab = ko.observable('details');
      }

      function HdfsContextTabs(data) {
        var self = this;

        self.disposals = [];

        // TODO: Update Ace token with selected path
        self.data = ko.observable({
          details: data,
          loading: ko.observable(false),
          hasErrors: ko.observable(false),
          selectedPath: ko.observable(data.path)
        });

        var showInFileBrowserPubSub = huePubSub.subscribe('context.popover.open.in.file.browser', function () {
          window.open((data.path.indexOf('/') === 0 ? '/filebrowser/#' : '/filebrowser/#/') + data.path, '_blank');
        });

        self.disposals.push(function () {
          showInFileBrowserPubSub.remove();
        });

        var replaceInEditorPubSub = huePubSub.subscribe('context.popover.replace.in.editor', function () {
          huePubSub.publish('ace.replace', {
            location: data.location,
            text: self.data().selectedPath()
          });
        });
        self.disposals.push(function () {
          replaceInEditorPubSub.remove();
        });

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'context-popover-hdfs-details', templateData: self.data }
        ];
        self.activeTab = ko.observable('details');
      }

      HdfsContextTabs.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
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

      function HueAppContext(data) {
        var self = this;
        self.data = data;
        self.hasErrors = ko.observable(false);
        self.loading = ko.observable(false);
        self.template = 'context-hue-app-details';
      }

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
          },
          {
            id: 'stats',
            label: '${ _("Stats") }',
            template: 'context-popover-collection-stats-details',
            templateData: self.data
          }
        ];
        self.activeTab = ko.observable('terms');

        self.apiHelper.identifierChainToPath({
          sourceType: 'solr',
          identifierChain: data.identifierChain,
          defaultDatabase: 'default'
        }).done(function (path) {
          var showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', function () {
            huePubSub.publish('assist.db.highlight', {
              sourceType: 'solr',
              path: path
            });
          });
          self.disposals.push(function () {
            showInAssistPubSub.remove();
          })
        });

      }

      CollectionContextTabs.prototype.loadTerms = function () {
        var self = this;
        self.data().terms.data.removeAll();
        self.data().loadingTerms(true);
        self.apiHelper.fetchDashboardTerms({
          collectionName: self.data().details.identifierChain[1].name,
          fieldName: self.data().details.identifierChain[2].name,
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
        var fieldName = self.data().details.identifierChain[2].name;
        self.apiHelper.fetchDashboardStats({
          collectionName: self.data().details.identifierChain[1].name,
          fieldName: fieldName,
          engine: 'solr',
          successCallback: function (data) {
            if (data.stats.stats.stats_fields[fieldName] != null) {
              $.each(data.stats.stats.stats_fields[fieldName], function (key, val) {
                self.data().stats.data.push({'key': key, 'val': val});
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

      function ResizeHelper (orientation, leftAdjust, topAdjust) {
        var self = this;

        var apiHelper = ApiHelper.getInstance();

        var originalMidX, originalWidth, originalRightX, originalLeftX, originalMidY, originalHeight, originalTopY, originalBottomY;
        var rightX, leftX, leftDiff, rightDiff, topY, bottomY, topDiff, bottomDiff;
        var redrawHeaders = false;

        window.setTimeout(function () {
          var offset = $('.hue-popover').offset();
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
        }, 0);

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
        self.defaultDatabase = params.defaultDatabase;
        self.close = hidePopover;
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
            if (currentSourceOffset.left !== originalSourceOffset.left || currentSourceOffset.top !== originalSourceOffset.top) {
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

        self.isDatabase = params.data.type === 'database';
        self.isTable = params.data.type === 'table';
        self.isColumn = params.data.type === 'column';
        self.isComplex = params.data.type === 'complex';
        self.isFunction = params.data.type === 'function';
        self.isHdfs = params.data.type === 'hdfs';
        self.isAsterisk = params.data.type === 'asterisk';
        self.isView = params.data.type === 'view';
        self.isDocument = params.data.type.toLowerCase() === 'hue';
        self.isCollection = params.data.type === 'collection';

        self.showInAssistEnabled = (typeof params.showInAssistEnabled !== 'undefined' ? params.showInAssistEnabled : true) && (self.isDocument || self.isDatabase || self.isTable || self.isColumn || self.isCollection);
        self.openInDashboardEnabled = self.isTable || self.isView || self.isDatabase;
        self.openInTableBrowserEnabled = self.isTable || self.isView || self.isDatabase;
        self.replaceEditorContentEnabled = self.isHdfs;
        self.openInFileBrowserEnabled = self.isHdfs;
        self.expandColumnsEnabled = self.isAsterisk;

        if ((self.isColumn || self.isComplex) && self.data.tables && self.data.tables.length > 0) {
          var identifierChain = self.data.identifierChain;
          var foundTable = $.grep(self.data.tables, function (table) {
            return hueUtils.equalIgnoreCase(table.alias, identifierChain[0].name) ||
                    (table.identifierChain && hueUtils.equalIgnoreCase(table.identifierChain[table.identifierChain.length - 1].name, identifierChain[0].name));
          });
          if (foundTable.length === 1 && foundTable.identifierChain) {
            identifierChain.shift();
            identifierChain = foundTable.identifierChain.concat(identifierChain);
            delete self.data.tables;
          } else if (self.data.tables.length === 1 && self.data.tables[0].identifierChain) {
            identifierChain = self.data.tables[0].identifierChain.concat(identifierChain);
            delete self.data.tables;
          }
          self.data.identifierChain = identifierChain
        }

        self.pinEnabled = params.pinEnabled && !self.isFunction && !self.isAsterisk && !self.isHdfs;

        if (self.isTable || self.isView) {
          if (self.isSolr) {
            self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          }
          else {
            self.title = $.map(self.data.identifierChain, function (identifier) { return identifier.name; }).join('.');
            if (self.title.indexOf('.') === -1) {
              self.title = self.defaultDatabase + '.' + self.title;
            }
          }
        }

        if (self.isDatabase) {
          self.contents = new DatabaseContextTabs(self.data, self.sourceType, self.defaultDatabase);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-database';
        } else if (self.isTable) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, false, false);
          self.iconClass = self.isSolr ? 'fa-search' : 'fa-table';
        } else if (self.isView) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, false, false);
          self.iconClass = self.isSolr ? 'fa-search' : 'fa-eye';
        } else if (self.isComplex) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, false, true);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-columns';
        } else if (self.isColumn) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, true, false);
          if (self.data.identifierChain.length > 1) {
            self.title = self.data.identifierChain[self.data.identifierChain.length - 2].name + '.' + self.data.identifierChain[self.data.identifierChain.length - 1].name;
          } else {
            self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          }
          self.iconClass = 'fa-columns';
        } else if (self.isFunction) {
          self.contents = new FunctionContextTabs(self.data, self.sourceType);
          self.title = self.data.function;
          self.iconClass = 'fa-superscript';
        } else if (self.isHdfs) {
          self.contents = new HdfsContextTabs(self.data);
          self.title = self.data.path;
          self.iconClass = 'fa-folder-o';
        } else if (self.isAsterisk) {
          self.contents = new AsteriskContextTabs(self.data, self.sourceType, self.defaultDatabase);
          self.title = '*';
          self.iconClass = 'fa-table';
        } else if (self.isDocument) {
          self.contents = new DocumentContext(self.data.definition);
          self.title = self.data.definition.name;
          self.iconClass = 'fa-file-o';
        } else if (self.isCollection) {
          self.contents = new CollectionContextTabs(self.data);
          self.title = self.data.identifierChain[1].name + '.' + self.data.identifierChain[2].name;
          self.iconClass = 'fa-search';
        } else {
          self.title = '';
          self.iconClass = 'fa-info';
        }
        self.orientationClass = 'hue-popover-' + orientation;

        if ((self.isDatabase || self.isTable || self.isView) && self.data.identifierChain) {
          apiHelper.identifierChainToPath({
            sourceType: self.sourceType,
            identifierChain: self.data.identifierChain,
            defaultDatabase: self.defaultDatabase
          }).done(function (path) {

            var showInMetastorePubSub = huePubSub.subscribe('context.popover.open.in.metastore', function (type) {
              if (IS_HUE_4) {
                huePubSub.publish('open.link', '/metastore/table' + (type === 'table' || type === 'view' ? '/' : 's/') + path.join('/'));
                huePubSub.publish('context.popover.hide');
              } else {
                window.open('/metastore/table' + (type === 'table' || type === 'view' ? '/' : 's/') + path.join('/'), '_blank');
              }
            });
            self.disposals.push(function () {
              showInMetastorePubSub.remove();
            });
            % if HAS_SQL_ENABLED.get():
            var openInDashboardPubSub = huePubSub.subscribe('context.popover.open.in.dashboard', function () {
              if (IS_HUE_4) {
                huePubSub.publish('open.link', '/hue/dashboard/browse/' + path.join('.') + '?engine=' + self.sourceType);
                huePubSub.publish('context.popover.hide');
              } else {
                window.open('/hue/dashboard/browse/' + path.join('.') + '?engine=' + self.sourceType, '_blank');
              }
            });
            self.disposals.push(function () {
              openInDashboardPubSub.remove();
            });
            % endif
          });
        }

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
          $(document).on('click', hideOnClickOutside);
        }, 0);

        self.disposals.push(function () {
          $(document).off('click', hideOnClickOutside);
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
        if (typeof self.contents.sample !== 'undefined') {
          self.contents.sample.fetchedData(undefined);
        }
        huePubSub.publish('sql.context.pin', self);
        if (self.contents.activeTab() === 'sample') {
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
        self.contents = undefined;

        self.disposals = [];

        self.isDatabase = params.data.type.toLowerCase() === 'database';
        self.isTable = params.data.type.toLowerCase() === 'table';
        self.isColumn = params.data.type.toLowerCase() === 'field';
        self.isView = params.data.type.toLowerCase() === 'view';
        self.isDocument = params.data.type.toLowerCase() === 'hue';
        self.isHueApp = params.data.type.toLowerCase() === 'hueapp';

        self.close = params.globalSearch.close.bind(params.globalSearch);

        // These are currently not in the global search results
        self.isHdfs = false;
        self.isAsterisk = false;
        self.isComplex = false;
        self.isFunction = false;

        self.showInAssistEnabled = !self.isHueApp;
        self.openInDashboardEnabled = self.isTable || self.isView || self.isDatabase;
        self.openInTableBrowserEnabled = self.isTable || self.isView || self.isDatabase;
        self.replaceEditorContentEnabled = self.isHdfs;
        self.openInFileBrowserEnabled = self.isHdfs;
        self.expandColumnsEnabled = self.isAsterisk;

        var adaptedData = { identifierChain: [] };

        var path = params.data.originalName.split('.');
        path.forEach(function (part) {
          adaptedData.identifierChain.push({ name: part });
        });

        var metastorePubSub = huePubSub.subscribe('context.popover.open.in.metastore', function () {
          huePubSub.publish('open.link', '/metastore/table' + (self.isTable || self.isView ? '/' : 's/') + path.join('/'));
          self.close();
        });

        self.disposals.push(function () {
          metastorePubSub.remove();
        });

        var sqlSourceType;
        if (self.isDatabase || self.isTable || self.isView || self.isColumn || self.isComplex) {
          huePubSub.publish('cluster.config.get.config', function (clusterConfig) {
            if (clusterConfig && clusterConfig['app_config'] && clusterConfig['app_config']['editor']) {
              sqlSourceType = clusterConfig['app_config']['editor']['default_sql_interpreter'];
            }
          });
          if (!sqlSourceType) {
            sqlSourceType = params.data.sourceType.toLowerCase();
          }
        }

        if (self.isDatabase) {
          self.contents = new DatabaseContextTabs(adaptedData, sqlSourceType, 'default');
        } else if (self.isTable) {
          self.contents = new TableAndColumnContextTabs(adaptedData, sqlSourceType, 'default', false, false);
        } else if (self.isView) {
          self.contents = new TableAndColumnContextTabs(adaptedData, sqlSourceType, 'default', false, false);
        } else if (self.isColumn) {
          self.contents = new TableAndColumnContextTabs(adaptedData, sqlSourceType, 'default', true, false);
        } else if (self.isDocument) {
          self.contents = new DocumentContext(params.data);
        } else if (self.isHueApp) {
          self.contents = new HueAppContext(params.data);
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
        template: { element: 'context-popover-contents' }
      })
    })();
  </script>
</%def>
