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
from desktop import conf
from desktop.conf import USE_NEW_SIDE_PANELS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
from django.utils.translation import ugettext as _
from metadata.conf import has_navigator
%>

<%def name="sqlContextPopover()">
  <script type="text/html" id="sql-context-footer">
    <div class="sql-context-flex-bottom-links">
      <div class="sql-context-link-row">
        <a class="inactive-action pointer" data-bind="visible: showInAssistEnabled && (isTable || isColumn), click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="${ _("Show in Assist...") }" class="fa fa-search"></i> ${ _("Assist") }</a>
        <a class="inactive-action pointer" data-bind="visible: isTable || isDatabase, click: function() { huePubSub.publish('sql.context.popover.open.in.metastore', isTable ? 'table' : 'db') }"><i style="font-size: 11px;" title="${ _("Open in Metastore...") }" class="fa fa-external-link"></i> ${ _("Metastore") }</a>
        <a class="inactive-action pointer" data-bind="visible: isHdfs, click: function() { huePubSub.publish('sql.context.popover.replace.in.editor') }"><i style="font-size: 11px;" title="${ _("Replace the editor content...") }" class="fa fa-pencil"></i> ${ _("Insert in the editor") }</a>
        <a class="inactive-action pointer" data-bind="visible: isHdfs, click: function() { huePubSub.publish('sql.context.popover.open.in.file.browser') }"><i style="font-size: 11px;" title="${ _("Open in File Browser...") }" class="fa fa-external-link"></i> ${ _("File Browser") }</a>
        <!-- ko if: isAsterisk -->
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

  <script type="text/html" id="sql-context-columns">
    <div class="sql-context-flex-fill" data-bind="with: fetchedData">
      <!-- ko component: { name: 'sql-columns-table', params: { columns: extended_columns } } --><!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="sql-context-table-details">
    <!-- ko with: fetchedData -->
    <div style="flex: 1; padding: 10px 10px 0 10px;">
      <!-- ko if: details && details.properties -->
      <div style="margin: 10px; font-size: 15px; font-weight: 300;">${ _("Properties") }</div>
      <div style="margin-left: 15px;">
        <span style="margin-right: 5px;" title="${ _('Owner') }">
          <i class="fa fa-fw fa-user muted"></i> <span data-bind="text: details.properties.owner"></span>
        </span>
        <span style="margin-right: 5px;" title="${ _('Created') }">
          <i class="fa fa-fw fa-clock-o muted"></i> <span data-bind="text: localeFormat(details.properties.create_time)"></span>
        </span>
        <span style="margin-right: 5px;" title="${ _('Format') }">
          <i class="fa fa-fw fa-file-o muted"></i> <span data-bind="text: details.properties.format"></span>
        </span>
        <span style="margin-right: 5px;" title="${ _('Format') }">
          <i class="fa fa-fw fa-archive muted"></i> <span data-bind="visible: details.properties.compressed" style="display:none;">${_('Compressed')}</span> <span data-bind="visible: !details.stats.compressed" style="display:none;">${_('Not compressed')}</span>
        </span>
      </div>
      <!-- /ko -->
      <!-- ko if: typeof comment !== 'undefined' && comment !== '' && comment !== null -->
      <div style="margin: 10px; font-size: 15px; font-weight: 300;">${ _("Comment") }</div>
      <div style="margin-left: 15px; font-style: italic;" data-bind="text: comment"></div>
      <!-- /ko -->
      %if has_navigator(user):
        <!-- ko if: $parent.sourceType === 'hive' || $parent.sourceType === 'impala' -->
        <div style="margin: 10px; font-size: 15px; font-weight: 300;">${ _("Tags") }</div>
        <div style="margin-left: 15px;" data-bind="component: { name: 'nav-tags', params: $parent } "></div>
        <!-- /ko -->
      %endif
      <!-- ko if: typeof viewSql !== 'undefined' -->
      <div style="margin: 10px; font-size: 15px; font-weight: 300;">${ _("View SQL") }</div>
      <!-- ko hueSpinner: { spin: loadingViewSql, center: true, size: 'large' } --><!-- /ko -->
      <!-- ko ifnot: loadingViewSql -->
      <div style="margin: 0 10px;" class="pointer" title="${ _("Click to copy") }" data-bind="tooltip: { placement: 'bottom' }, clickToCopy: viewSql, click: function () { huePubSub.publish('sql.context.popover.hide'); }, highlight: { value: viewSql, formatted: true, dialect: $parent.sourceType }"></div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-column-details">
    <div class="sql-context-flex-fill" data-bind="with: fetchedData, nicescroll">
      <div style="margin: 15px;">
        <a class="pointer" data-bind="text: name, attr: { title: name }, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name); }"></a> <!-- ko if: typeof type !== 'undefined' -->(<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)<!-- /ko -->
        <!-- ko if: typeof comment !== 'undefined' && comment !== '' && comment !== null -->
        <div style="margin-top: 10px; font-size: 15px; font-weight: 300;">${ _("Comment") }</div>
        <div data-bind="text: comment"></div>
        <!-- /ko -->
        %if has_navigator(user):
          <!-- ko if: $parent.sourceType === 'hive' || $parent.sourceType === 'impala' -->
          <div style="margin-top: 10px; font-size: 15px; font-weight: 300;">${ _("Tags") }</div>
          <div style="margin: 10px" data-bind="component: { name: 'nav-tags', params: $parent } "></div>
          <!-- /ko -->
        %endif
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-complex-details">
    <div class="sql-context-flex-fill" data-bind="with: fetchedData, nicescroll">
      <div style="margin: 15px;">
        <a class="pointer" data-bind="visible: typeof sample !== 'undefined', text: name || $parents[2].title, attr: { title: name || $parents[2].title }, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name || $parents[2].title); }"></a>
        <span data-bind="visible: typeof sample === 'undefined', text: name || $parents[2].title, attr: { title: name || $parents[2].title }"></span> <!-- ko if: typeof type !== 'undefined' -->(<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)<!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-table-and-column-sample">
    <div class="sql-context-flex-fill context-sample-container" data-bind="with: fetchedData">
      <div class="context-sample sample-scroll">
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

  <script type="text/html" id="sql-context-table-analysis">
    <div class="sql-context-flex-fill" data-bind="with: fetchedData, niceScroll">
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

  <script type="text/html" id="sql-context-column-analysis">
    <div class="sql-context-flex-fill" data-bind="with: fetchedData, niceScroll">
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

  <script type="text/html" id="sql-context-database-details">
    <div class="sql-context-flex-fill">
      <div class="sql-context-flex">
        <div data-bind="if: $parent.comment">
          <div style="margin: 10px; font-size: 15px; font-weight: 300;">${ _("Comment") }</div>
          <div style="margin-left: 15px; font-style: italic;" data-bind="text: $parent.comment"></div>
        </div>
        <div style="margin: 10px 5px 0 10px;">
          <span style="font-size: 15px; font-weight: 300;">${_('Tags')}</span>
        </div>
        <div class="sql-context-flex-fill sql-columns-table" style="position:relative; height: 100%; overflow-y: auto;">
          <div style="margin: 10px" data-bind="component: { name: 'nav-tags', params: $data } "></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-hdfs-details">
    <div class="sql-context-flex-fill" data-bind="with: details, niceScroll">
      <div style="padding: 8px">
        <div style="margin: 10px 10px 18px 10px;">
          <div data-bind="hdfsTree: { path: $data.path, selectedPath: $parent.selectedPath }"></div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-asterisk-details">
    <div class="sql-context-flex-fill">
      <!-- ko component: { name: 'sql-columns-table', params: { columns: columns, scrollToColumns: false } } --><!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="sql-context-function-details">
    <!-- ko if: typeof details === 'undefined' -->
    <div class="sql-context-flex-fill">
      <div class="alert">${_('Could not find details for the function')} <span data-bind="text: $parents[2].title"></span>()</div>
    </div>
    <!-- /ko -->
    <!-- ko if: typeof details !== 'undefined' -->
    <div class="sql-context-flex-fill" data-bind="with: details, niceScroll">
      <div style="padding: 8px">
        <p style="margin: 10px 10px 18px 10px;"><span style="white-space: pre; font-family: monospace;" data-bind="text: signature"></span></p>
        <p><span data-bind="text: description"></span></p>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-table-partitions">
    <div class="sql-context-flex-fill" data-bind="with: fetchedData, niceScroll">
      <div style="margin: 10px 5px 0 10px;">
        <span style="font-size: 15px; font-weight: 300;">${_('Columns')}</span>
      </div>
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
            <td data-bind="text: $index()+1"></td>
            <td><a href="#" data-bind="text: $data, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', $data); }"></a></td>
          </tr>
          </tbody>
        </table>
      </div>
      <div style="margin: 10px 5px 0 10px;">
        <span style="font-size: 15px; font-weight: 300;">${_('Partitions')}</span>
      </div>
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
            <td data-bind="text: $index()+1"></td>
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

  <script type="text/html" id="sql-context-popover-template">
    <div class="hue-popover" data-bind="css: orientationClass, style: { 'left': left() + 'px', 'top': top() + 'px', 'width': width() + 'px', height: height() + 'px' }, resizable: { containment: 'document', handles: resizeHelper.resizableHandles, start: resizeHelper.resizeStart, stop: resizeHelper.resizeStop, resize: resizeHelper.resize }">
      <div class="hue-popover-arrow" data-bind="style: { 'margin-left': leftAdjust() + 'px',  'margin-top': topAdjust() + 'px' }"></div>
      <div class="hue-popover-title" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 30px;">
        <i class="fa muted" data-bind="css: iconClass" style="margin-top: 3px"></i> <span data-bind="text: title"></span>
        <div style="position: absolute; right: 6px; top: 8px;">
          <a class="pointer inactive-action" data-bind="visible: pinEnabled, click: pin"><i class="fa fa-fw fa-thumb-tack"></i></a>
          <a class="pointer inactive-action" data-bind="click: close"><i class="fa fa-fw fa-times"></i></a>
        </div>
      </div>
      <!-- ko template: 'sql-context-contents' --><!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="sql-context-contents">
    <div class="sql-context-popover-content">
      <!-- ko with: contents -->
      <ul class="nav nav-tabs sql-context-tabs" data-bind="foreach: tabs">
        <li data-bind="click: function () { $parent.activeTab(id); }, css: { 'active' : $parent.activeTab() === id }">
          <a class="sql-context-tab" data-toggle="tab" data-bind="text: label, attr: { href: '#' + id }"></a>
        </li>
      </ul>
      <div class="sql-context-tab-container" data-bind="foreach: tabs">
        <div class="sql-context-tab-pane tab-pane" id="sampleTab" data-bind="visible : $parent.activeTab() === id, attr: { id: id }, css: { 'active' : $parent.activeTab() === id }">
          <div class="sql-context-flex">
            <!-- ko with: templateData -->
            <div class="sql-context-flex-fill" data-bind="visible: loading"><!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko --></div>
            <!-- ko if: ! loading() && hasErrors() -->
            <div class="sql-context-flex-fill">
                <div class="alert">
                <span data-bind="text: $parent.errorText"></span>
                <!-- ko if: $parent.enableSampleError -->
                <a href="javascript:void(0);" data-bind="click: function(){ huePubSub.publish('sample.error.insert.click', $data); huePubSub.publish('sql.context.popover.hide');}">${_('Insert ')}<span data-bind="text:$parent.title"></span> ${_(' sample query')}</a> ${_('at cursor')}
                <!-- /ko -->
                </div>
            </div>
            <!-- /ko -->
            <!-- ko if: ! loading() && ! hasErrors() -->
            <!-- ko template: { name: $parent.template } --><!-- /ko -->
            <!-- /ko -->
            <!-- /ko -->
            <!-- ko template: { name: 'sql-context-footer', data: $parents[1] } --><!-- /ko -->
          </div>
        </div>
      </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var HALF_SIZE_LIMIT_X = 130;
      var HALF_SIZE_LIMIT_Y = 100;
      var HALF_ARROW = 6;

      var preventHide = false;
      var intervals = [];
      var pubSubs = [];

      var hidePopover = function () {
        if (! preventHide) {
          if ($('#sqlContextPopover').length > 0) {
            ko.cleanNode($('#sqlContextPopover')[0]);
            huePubSub.publish('sql.context.popover.dispose');
            $('#sqlContextPopover').remove();
            $(document).off('click', hideOnClickOutside);
            while (intervals.length > 0) {
              window.clearInterval(intervals.pop());
            }
            while (pubSubs.length > 0) {
              pubSubs.pop().remove();
            }
            huePubSub.publish('sql.context.popover.hidden');
          }
        }
      };

      var hideOnClickOutside = function (event) {
        if (jQuery.contains(document, event.target) && !$.contains($('#sqlContextPopover')[0], event.target)) {
          hidePopover();
        }
      };

      function GenericTabContents(identifierChain, sourceType, defaultDatabase, apiFunction) {
        var self = this;
        self.identifierChain = identifierChain;
        self.sourceType = sourceType;
        self.defaultDatabase = defaultDatabase;
        self.apiHelper = ApiHelper.getInstance();
        self.apiFunction = apiFunction;

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

        var apiHelper = ApiHelper.getInstance();

        self.columns = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAutocomplete);
        self.columnDetails = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAutocomplete);
        self.tableDetails = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAnalysis);
        self.sample = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchSamples);
        self.analysis = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchAnalysis);
        self.partitions = new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, apiHelper.fetchPartitions);

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
                    template: 'sql-context-table-and-column-sample',
                    templateData: self.sample,
                    errorText: '${ _("There was a problem loading the samples.") }'
                  });
                }
              })
            }
          } else if (typeof self[newValue].fetchedData() === 'undefined') {
            self[newValue].fetch();
          }
        });

        if (isColumn) {
          self.tabs.push({
            id: 'columnDetails',
            label: '${ _("Details") }',
            template: 'sql-context-column-details',
            templateData: self.columnDetails,
            errorText: '${ _("There was a problem loading the column details.") }',
            isColumn: true
          });
          self.activeTab('columnDetails');
        } else if (isComplex) {
          self.tabs.push({
            id: 'complexDetails',
            label: '${ _("Details") }',
            template: 'sql-context-complex-details',
            templateData: self.columnDetails,
            errorText: '${ _("There was a problem loading the details.") }',
            isColumn: false
          });
          self.activeTab('complexDetails');
        } else {
          self.tabs.push({
            id: 'columns',
            label: '${ _("Columns") }',
            template: 'sql-context-columns',
            templateData: self.columns,
            errorText: '${ _("There was a problem loading the columns.") }',
            isColumn: false
          });
          self.tabs.push({
            id: 'tableDetails',
            label: '${ _("Details") }',
            template: 'sql-context-table-details',
            templateData: self.tableDetails,
            errorText: '${ _("There was a problem loading the table details.") }',
            isColumn: false
          });
          self.activeTab('columns');
        }

        if (!isComplex) {
          self.tabs.push({
            id: 'sample',
            label: '${ _("Sample") }',
            template: 'sql-context-table-and-column-sample',
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
              template: 'sql-context-column-analysis',
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
                template: 'sql-context-table-analysis',
                templateData: self.analysis,
                errorText: '${ _("There was a problem loading the table analysis.") }',
                isColumn: false
              });
            } else if (data.partition_keys.length > 0) {
              self.tabs.push({
                id: 'partitions',
                label: '${ _("Partitions") }',
                template: 'sql-context-table-partitions',
                templateData: self.partitions,
                errorText: '${ _("There was a problem loading the table partitions.") }',
                isColumn: false
              });
            }
          });
        }

        intervals.push(window.setInterval(function () {
          if (self.activeTab() !== 'sample') {
            return;
          }
          var $t = $('.samples-table');
          if ($t.length === 0) {
            return;
          }

          $t.parents('.dataTables_wrapper').getNiceScroll().resize();
        }, 300));

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

        pubSubs.push(huePubSub.subscribe('sql.context.popover.scroll.to.column', function (colName) {
          if (typeof self.sample.fetchedData() === 'undefined') {
            self.sample.fetch(function (data) {
              self.initializeSamplesTable(data);
              window.setTimeout(function () {
                performScrollToColumn(colName);
              }, 0);
            });
          } else {
            performScrollToColumn(colName);
          }
        }));

        apiHelper.identifierChainToPath({
          sourceType: sourceType,
          defaultDatabase: defaultDatabase,
          identifierChain: data.identifierChain
        }, function (path) {
          pubSubs.push(huePubSub.subscribe('sql.context.popover.show.in.assist', function () {
            huePubSub.publish('assist.db.highlight', {
              sourceType: sourceType,
              path: path
            });
          }));
        });
      }

      TableAndColumnContextTabs.prototype.refetchSamples = function () {
        var self = this;
        self.sample.fetch(self.initializeSamplesTable);
      };

      TableAndColumnContextTabs.prototype.initializeSamplesTable = function (data) {
        window.setTimeout(function () {
          var $t = $('.samples-table');

          if ($t.parent().hasClass('dataTables_wrapper')) {
            if ($t.parent().data('scrollFnDt')) {
              $t.parent().off('scroll', $t.parent().data('scrollFnDt'));
            }
            $t.unwrap();
            if ($t.children('tbody').length > 0) {
              $t.children('tbody').empty();
            }
            else {
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

          $t.parents('.dataTables_wrapper').css('height', '100%');

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

          huePubSub.subscribeOnce('sql.context.popover.dispose', function () {
            if ($t.data('plugin_jHueTableExtender2')) {
              $t.data('plugin_jHueTableExtender2').destroy();
            }
          });

          hueUtils.initNiceScroll($t.parents('.dataTables_wrapper'));

          $t.parents('.dataTables_wrapper').niceScroll({
            cursorcolor: "#C1C1C1",
            cursorborder: "1px solid #C1C1C1",
            cursoropacitymin: 0,
            cursoropacitymax: 1,
            scrollspeed: 100,
            mousescrollstep: 60,
            cursorminheight: 20,
            horizrailenabled: true,
            autohidemode: "leave"
          });

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

      function DatabaseContextTabs(data, sourceType, defaultDatabase) {
        var self = this;
        self.dbComment = ko.observable('');
        var dbName = data.identifierChain[data.identifierChain.length - 1].name;
        $.getJSON('/metastore/databases/' + dbName + '/metadata', function (data) {
          if (data && data.status == 0 && data.data.comment) {
              self.dbComment(data.data.comment);
          }
        });
        self.tabs = [
          { id: 'details', label: '${ _("Details") }', comment : self.dbComment, template: 'sql-context-database-details', templateData: new GenericTabContents(data.identifierChain, sourceType, defaultDatabase, ApiHelper.getInstance().fetchAutocomplete) }
        ];
        self.activeTab = ko.observable('details');
      }


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
          huePubSub.publish('sql.context.popover.hide');
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
          { id: 'details', label: '${ _("Details") }', template: 'sql-context-asterisk-details', templateData: self.data }
        ];
        self.activeTab = ko.observable('details');
      }

      function HdfsContextTabs(data) {
        var self = this;

        // TODO: Update Ace token with selected path
        self.data = ko.observable({
          details: data,
          loading: ko.observable(false),
          hasErrors: ko.observable(false),
          selectedPath: ko.observable(data.path)
        });

        pubSubs.push(huePubSub.subscribe('sql.context.popover.open.in.file.browser', function () {
          window.open((data.path.indexOf('/') === 0 ? '/filebrowser/#' : '/filebrowser/#/') + data.path, '_blank');
        }));

        pubSubs.push(huePubSub.subscribe('sql.context.popover.replace.in.editor', function () {
          huePubSub.publish('ace.replace', {
            location: data.location,
            text: self.data().selectedPath()
          });
        }));

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'sql-context-hdfs-details', templateData: self.data }
        ];
        self.activeTab = ko.observable('details');
      }

      function FunctionContextTabs(data, sourceType) {
        var self = this;
        self.func = ko.observable({
          details: SqlFunctions.findFunction(sourceType, data.function),
          loading: ko.observable(false),
          hasErrors: ko.observable(false)
        });

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'sql-context-function-details', templateData: self.func }
        ];
        self.activeTab = ko.observable('details');
      }

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
              if (ui.size.width < 310) {
                ui.size.width = 310;
                $('.hue-popover').css('width', 310 + 'px');
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

      function SqlContextPopoverViewModel(params) {
        var self = this;
        self.disposalFunctions = [];

        var apiHelper = ApiHelper.getInstance();

        self.left = ko.observable(0);
        self.top = ko.observable(0);

        self.showInAssistEnabled = typeof params.showInAssistEnabled !== 'undefined' ? params.showInAssistEnabled : true;

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
        self.pinEnabled = false;
        % if USE_NEW_SIDE_PANELS.get():
          self.pinEnabled = params.pinEnabled || false;
        % endif
        var orientation = params.orientation || 'bottom';
        self.contents = null;
        self.resizeHelper = new ResizeHelper(orientation, self.leftAdjust, self.topAdjust);

        if (typeof params.source.element !== 'undefined') {
          // Track the source element and close the popover if moved
          var $source = $(params.source.element);
          var originalSourceOffset = $source.offset();
          var currentSourceOffset;
          intervals.push(window.setInterval(function () {
            currentSourceOffset = $source.offset();
            if (currentSourceOffset.left !== originalSourceOffset.left || currentSourceOffset.top !== originalSourceOffset.top) {
              hidePopover();
            }
          }, 200));
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


        self.isDatabase = params.data.type === 'database';
        self.isTable = params.data.type === 'table';
        self.isColumn = params.data.type === 'column';
        self.isComplex = params.data.type === 'complex';
        self.isFunction = params.data.type === 'function';
        self.isHdfs = params.data.type === 'hdfs';
        self.isAsterisk = params.data.type === 'asterisk';
        self.isView = params.data.type === 'view';

        if (self.isDatabase) {
          self.contents = new DatabaseContextTabs(self.data, self.sourceType, self.defaultDatabase);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-database';
        } else if (self.isTable) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, false, false);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-table'
        } else if (self.isView) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, false, false);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-eye'
        } else if (self.isComplex) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, false, true);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-columns'
        } else if (self.isColumn) {
          self.contents = new TableAndColumnContextTabs(self.data, self.sourceType, self.defaultDatabase, true, false);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-columns'
        } else if (self.isFunction) {
          self.contents = new FunctionContextTabs(self.data, self.sourceType);
          self.title = self.data.function;
          self.iconClass = 'fa-superscript'
        } else if (self.isHdfs) {
          self.contents = new HdfsContextTabs(self.data);
          self.title = self.data.path;
          self.iconClass = 'fa-folder-o'
        } else if (self.isAsterisk) {
          self.contents = new AsteriskContextTabs(self.data, self.sourceType, self.defaultDatabase);
          self.title = '*';
          self.iconClass = 'fa-table';
        } else {
          self.title = '';
          self.iconClass = 'fa-info'
        }
        self.orientationClass = 'hue-popover-' + orientation;

        if ((self.isDatabase || self.isTable || self.isView) && self.data.identifierChain) {
          apiHelper.identifierChainToPath({
            sourceType: self.sourceType,
            identifierChain: self.data.identifierChain
          }, function (path) {
            pubSubs.push(huePubSub.subscribe('sql.context.popover.open.in.metastore', function (type) {
              if (IS_HUE_4) {
                huePubSub.publish('open.link', '/metastore/table' + (type === 'table' ? '/' : 's/') + path.join('/'));
                huePubSub.publish('sql.context.popover.hide');
              } else {
                window.open('/metastore/table' + (type === 'table' ? '/' : 's/') + path.join('/'), '_blank');
              }
            }));
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

          self.disposalFunctions.push(function () {
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

        self.disposalFunctions.push(function () {
          $(document).off('keyup', closeOnEsc);
        });

        window.setTimeout(function() {
          $(document).on('click', hideOnClickOutside);
        }, 0);

        self.disposalFunctions.push(function () {
          $(document).off('click', hideOnClickOutside);
        })
      }

      SqlContextPopoverViewModel.prototype.dispose = function() {
        var self = this;
        self.disposalFunctions.forEach(function (fn) {
          fn();
        })
      };

      SqlContextPopoverViewModel.prototype.pin = function () {
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

      ko.components.register('sql-context-popover', {
        viewModel: SqlContextPopoverViewModel,
        template: { element: 'sql-context-popover-template' }
      });

      huePubSub.subscribe('sql.context.popover.hide', hidePopover);

      huePubSub.subscribe('sql.context.popover.show', function (details) {
        hidePopover();
        var $sqlContextPopover = $('<div id="sqlContextPopover" data-bind="component: { name: \'sql-context-popover\', params: $data }" />');
        $('body').append($sqlContextPopover);
        ko.applyBindings(details, $sqlContextPopover[0]);
        huePubSub.publish('sql.context.popover.shown');
      });
    })();
  </script>

  <script type="text/html" id="sql-columns-table-template">
    <div class="sql-context-flex">
      <div class="sql-context-flex-header">
        <div style="margin: 10px 5px 0 10px;">
          <span style="font-size: 15px; font-weight: 300;">${_('Columns')} (<span data-bind="text: filteredColumns().length"></span>)</span>
          <a href="#" data-bind="toggle: searchVisible"><i class="snippet-icon fa fa-search inactive-action margin-left-10" data-bind="css: { 'blue': searchVisible }"></i></a>
          <input class="input-large sql-context-inline-search" type="text" data-bind="visible: searchVisible, hasFocus: searchFocus, clearable: searchInput, valueUpdate:'afterkeydown'" placeholder="${ _('Filter columns...') }">
        </div>
      </div>
      <div class="sql-context-flex-fill sql-columns-table" style="position:relative; height: 100%; overflow-y: auto;">
        <table id="sqlColumnsTable" style="width: 100%" class="table table-condensed table-nowrap">
          <!-- ko if: filteredColumns().length !== 0 -->
          <thead>
          <tr>
            <th width="6%">&nbsp;</th>
            <!-- ko if: typeof filteredColumns()[0].table === 'undefined' -->
            <th width="60%">${_('Name')}</th>
            <!-- /ko -->
            <!-- ko if: typeof filteredColumns()[0].table !== 'undefined' -->
            <th width="40%">${_('Name')}</th>
            <th width="20%">${_('Table')}</th>
            <!-- /ko -->
            <th width="34%">${_('Type')}</th>
            <th width="6%">&nbsp;</th>
          </tr>
          </thead>
          <!-- /ko -->
          <tbody data-bind="foreachVisible: { data: filteredColumns, minHeight: 29, container: '.sql-columns-table', pubSubDispose: 'sql.context.popover.dispose' }">
          <tr>
            <!-- ko if: typeof selected === 'undefined' -->
            <td data-bind="text: $index()+$indexOffset()+1"></td>
            <!-- /ko -->
            <!-- ko if: typeof selected !== 'undefined' -->
            <td data-bind="toggle: selected" class="center" style="cursor: default;">
              <div class="hueCheckbox fa" data-bind="multiCheck: '#sqlColumnsTable', css: {'fa-check': selected }"></div>
            </td>

            <!-- /ko -->
            <td style="overflow: hidden;">
              <!-- ko if: $parent.scrollToColumns -->
              <a href="javascript:void(0)" class="column-selector" data-bind="text: name, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name); }" title="${ _("Show sample") }"></a>
              <!-- /ko -->
              <!-- ko ifnot: $parent.scrollToColumns -->
              <span data-bind="text: name"></span>
              <!-- /ko -->
            </td>
            <!-- ko if: typeof table !== 'undefined' -->
            <td><span data-bind="text: table"></span></td>
            <!-- /ko -->
            <td><span data-bind="text: type, attr: { 'title': extendedType }, tooltip: { placement: 'bottom' }"></span></td>
            <td><i class="snippet-icon fa fa-question-circle" data-bind="visible: comment, attr: { 'title': comment }, tooltip: { placement: 'bottom' }"></i></td>
          </tr>
          </tbody>
        </table>
        <div class="sql-context-empty-columns" data-bind="visible: filteredColumns().length === 0">${_('No columns found')}</div>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      function SqlColumnsTable(params) {
        var self = this;
        var columns = params.columns;
        self.scrollToColumns = typeof params.scrollToColumns !== 'undefined' ?  params.scrollToColumns : true;
        self.searchInput = ko.observable('');
        self.searchVisible = ko.observable(false);
        self.searchFocus = ko.observable(false);

        self.searchVisible.subscribe(function (newValue) {
          if (newValue) {
            self.searchFocus(true);
          }
        });

        self.filteredColumns = ko.pureComputed(function () {
          if (self.searchInput() === '') {
            return columns;
          }
          var query = self.searchInput().toLowerCase();
          return columns.filter(function (column) {
            return column.name.toLowerCase().indexOf(query) != -1
                || column.type.toLowerCase().indexOf(query) != -1
                || column.comment.toLowerCase().indexOf(query) != -1
                || (typeof column.table !== 'undefined' && column.table.toLowerCase().indexOf(query) !== -1);
          })
        });
      }

      ko.components.register('sql-columns-table', {
        viewModel: SqlColumnsTable,
        template: { element: 'sql-columns-table-template' }
      });
    })();
  </script>
</%def>
