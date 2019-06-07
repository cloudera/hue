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
import logging
from django.utils.translation import ugettext as _

from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
from notebook.conf import ENABLE_SQL_INDEXER


LOG = logging.getLogger(__name__)

try:
  from beeswax.conf import DOWNLOAD_ROW_LIMIT, DOWNLOAD_BYTES_LIMIT
except ImportError, e:
  LOG.warn("Hive app is not enabled")
  DOWNLOAD_ROW_LIMIT = None
  DOWNLOAD_BYTES_LIMIT = None
%>

<%def name="addSnippetMenu()">
  <script type="text/html" id="add-snippet-menu-template">
    <div class="add-snippet-button" style="position:relative; width:65px; text-align: center;">
      <i class="pointer fa fa-plus-circle fa-5x" title="${ _('Add a new snippet') }" data-bind="click: addLastUsedSnippet, event: { 'mouseenter': showHistory, 'mouseleave': hideHistory }"></i>
      <div class="select-snippet-button" title="${ _('Select snippet') }" data-bind="fadeVisible: { value: hasAdditionalSnippets && showingSelectSnippet(), fadeOut: true }, click: showSnippetModal, event: { 'mouseenter': showHistory, 'mouseleave': hideHistory }">...</div>
      <div class="all-alternatives" data-bind="foreach: snippetHistory">
        <div class="add-snippet-alt pointer" style="display:none;" data-bind="
            event: { 'mouseenter': $parent.showHistory, 'mouseleave': $parent.hideHistory },
            fadeVisible: { value: $parent.showingHistory(), fadeOut: true, speed: 'slow' },
            style: { 'left': $parent.positions[$index()].left, 'top': $parent.positions[$index()].top },
            click: $parent.addNewSnippet">
          <div data-bind="text: name()"></div>
        </div>
      </div>
    </div>

    <div id="addSnippetModal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${ _('Add Snippet') }</h2>
      </div>
      <div class="modal-body" style="min-height: 100px">
        <ul class="snippet-list-alts" data-bind="foreach: availableSnippets">
          <li data-bind="click: function() { $parent.addNewSnippet($data) }">
            <div style="width: 30px; display:inline-block;">
            <!-- ko if: $root.getSnippetViewSettings(type()).snippetImage -->
            <img class="snippet-icon" data-bind="attr: { 'src': $root.getSnippetViewSettings(type()).snippetImage }"  alt="${ _('Snippet icon') }">
            <!-- /ko -->
            <!-- ko if: $root.getSnippetViewSettings(type()).snippetIcon -->
            <i style="margin-left: 2px; color: #0B7FAD;" class="fa snippet-icon" data-bind="css: $root.getSnippetViewSettings(type()).snippetIcon"></i>
            <!-- /ko -->
            </div>
            <span data-bind="text: name"></span>
          </li>
        </ul>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Close')}</button>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var WHEEL_RADIUS = 75;
      var PLUS_ICON_RADIUS = 27.859; // FA-5X

      var calculatePositions = function (alternativeCount) {
        var radius = WHEEL_RADIUS;
        var radIncrements = 2 * Math.PI / alternativeCount;
        var currentRad = -0.5 * Math.PI;

        var result = [];

        for (var i = 0; i < alternativeCount; i++) {
          result.push({
            left: radius * Math.cos(currentRad) + PLUS_ICON_RADIUS + 'px',
            top: radius * Math.sin(currentRad) + PLUS_ICON_RADIUS + 'px'
          });
          currentRad += radIncrements;
        }

        return result;
      };

      function AddSnippetMenuViewModel(params) {
        var self = this;
        self.notebook = params.notebook;
        self.availableSnippets = params.availableSnippets;
        self.snippetHistory = ko.observableArray([].concat(self.availableSnippets.slice(0, 5)));
        self.lastUsedSnippet = self.snippetHistory()[0];
        self.roundCount = 0;
        self.positions = calculatePositions(self.snippetHistory().length);
        self.showingHistory = ko.observable(false);
        self.hasAdditionalSnippets = params.availableSnippets().length > 5;
        self.showingSelectSnippet = ko.observable(false);

        self.addLastUsedSnippet = function () {
          self.addNewSnippet(self.lastUsedSnippet);
        };

        self.showSnippetModal = function () {
          $("#addSnippetModal").modal('show');
        };

        self.addNewSnippet = function (alternative) {
          clearTimeout(hideTimeout);
          self.showingHistory(false);
          self.showingSelectSnippet(false);
          $("#addSnippetModal").modal('hide');

          // When fewer than 5 it's always in history
          if (self.snippetHistory().indexOf(alternative) == -1) {
            self.snippetHistory.splice(4 - self.roundCount, 1, alternative);
            self.roundCount = (self.roundCount + 1) % 5;
          }

          self.lastUsedSnippet = alternative;
          self.notebook.newSnippet(alternative.type())
        };

        var hideTimeout = -1;

        self.showHistory = function () {
          clearTimeout(hideTimeout);
          self.showingHistory(true);
          self.showingSelectSnippet(true);
        };

        self.hideHistory = function () {
          clearTimeout(hideTimeout);
          hideTimeout = window.setTimeout(function () {
            self.showingHistory(false);
            self.showingSelectSnippet(false);
          }, 500);
        };
      }

      ko.components.register('add-snippet-menu', {
        viewModel: AddSnippetMenuViewModel,
        template: { element: 'add-snippet-menu-template' }
      });
    })();
  </script>
</%def>

<%def name="downloadSnippetResults()">
  <script type="text/html" id="download-results-template">
    <form method="POST" class="download-form" style="display: inline" data-bind="attr: { action: window.HUE_BASE_URL + '${ url('notebook:download') }' }">
      ${ csrf_token(request) | n,unicode }
      <input type="hidden" name="notebook"/>
      <input type="hidden" name="snippet"/>
      <input type="hidden" name="format"/>
    </form>

    <div class="hover-dropdown" data-bind="visible: snippet.result.hasSomeResults() && snippet.result.type() == 'table'" style="display:none;">
      <a class="inactive-action dropdown-toggle pointer" style="padding-right:0" data-toggle="dropdown" title="${ _('Export results') }" data-bind="css: {'grid-side-btn': gridSideBtn, 'snippet-side-btn': !gridSideBtn()}">
        <!-- ko ifnot: isDownloading -->
        <i class="fa fa-fw fa-download"></i>
        <!-- /ko -->

        <!-- ko if: isDownloading -->
        <i class="fa fa-fw fa-spinner fa-spin"></i>
        <!-- /ko -->
      </a>
      <ul class="dropdown-menu less-padding" style="z-index: 1040">
        <li>
          <a class="download" href="javascript:void(0)" data-bind="click: downloadCsv, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }"
          % if hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get() >= 0 and hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0:
          title="${ _('Download first %s rows or %s MB as CSV') % ( DOWNLOAD_ROW_LIMIT.get(), DOWNLOAD_BYTES_LIMIT.get() / 1024 / 1024 ) }"
          % elif hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0:
          title="${ _('Download first %s MB as CSV') % DOWNLOAD_BYTES_LIMIT.get() / 1024 / 1024 }"
          % else:
          title="${ _('Download first %s rows as CSV') % (hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get()) }"
          % endif
          >
            <i class="fa fa-fw fa-file-o"></i> ${ _('CSV') }
          </a>
        </li>
        <li>
          <a class="download" href="javascript:void(0)" data-bind="click: downloadXls, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }"
          % if hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get() >= 0 and hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0:
          title="${ _('Download first %s rows or %s MB as XLS') % ( DOWNLOAD_ROW_LIMIT.get(), DOWNLOAD_BYTES_LIMIT.get() / 1024 / 1024 ) }"
          % elif hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0:
          title="${ _('Download first %s MB as XLS') % DOWNLOAD_BYTES_LIMIT.get() / 1024 / 1024 }"
          % else:
          title="${ _('Download first %s rows as XLS') % (hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get()) }"
          % endif
          >
            <i class="fa fa-fw fa-file-excel-o"></i> ${ _('Excel') }
          </a>
        </li>
        <li>
          <a data-bind="css: clipboardClass" title="${ _('Copy the displayed results to your clipboard') }">
            <i class="fa fa-fw fa-clipboard"></i> ${ _('Clipboard') }
          </a>
        </li>
        % if ENABLE_SQL_INDEXER.get():
        <li>
          <a class="download" href="javascript:void(0)" data-bind="click: function() { saveTarget('dashboard'); if (notebook.canSave() ) { notebook.save() } else { $('#saveAsModaleditor').modal('show');} }" title="${ _('Visually explore the result') }">
            <!-- ko template: { name: 'app-icon-template', data: { icon: 'report' } } --><!-- /ko --> ${ _('Report') }
          </a>
        </li>
        <li>
          <a class="download" href="javascript:void(0)" data-bind="click: function() { saveTarget('dashboard'); trySaveResults(); }" title="${ _('Visually explore the result') }">
            <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Dashboard') }
          </a>
        </li>
        % endif
        <li>
          <a class="download" href="javascript:void(0)" data-bind="click: function() { savePath(''); $('#saveResultsModal' + snippet.id()).modal('show'); }" title="${ _('Export the result into a file, an index, a new table...') }">
            <i class="fa fa-fw fa-cloud-upload"></i> ${ _('Export') }
          </a>
        </li>
      </ul>
    </div>

    <div class="modal hide fade saveResultsModal" data-bind="attr: { 'id': 'saveResultsModal' + snippet.id() }">
      <div class="loader hide">
        <div class="overlay"></div>
        <i class="fa fa-spinner fa-spin"></i>
      </div>

      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Export the query result in a')} </h2>
      </div>
      <div class="modal-body" style="padding-left: 30px">
        <form method="POST" class="form form-inline">
          ${ csrf_token(request) | n,unicode }
          <fieldset>
            ${ _('File') }
            <br>
            <div class="control-group">
              <div class="controls">
                 <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="hdfs-file">
                  <span style="width: 190px; overflow: hidden; text-overflow: ellipsis; display: inline-block; white-space: nowrap;">
                  &nbsp;
                  % if hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get() >= 0 and hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0:
                    ${ _('First %s rows or %s MB') % ( DOWNLOAD_ROW_LIMIT.get(), DOWNLOAD_BYTES_LIMIT.get() / 1024 / 1024 ) }
                  % elif hasattr(DOWNLOAD_BYTES_LIMIT, 'get') and DOWNLOAD_BYTES_LIMIT.get() >= 0:
                    ${ _('First %s MB') % DOWNLOAD_BYTES_LIMIT.get() / 1024 / 1024 }
                  % else:
                    ${ _('First %s rows') % (hasattr(DOWNLOAD_ROW_LIMIT, 'get') and DOWNLOAD_ROW_LIMIT.get()) }
                  % endif
                  </span>
                </label>
                <div data-bind="visible: saveTarget() == 'hdfs-file'" class="inline">
                  <input data-bind="value: savePath, valueUpdate: 'afterkeydown', filechooser: { value: savePath, isNestedModal: true }, filechooserOptions: { uploadFile: false, skipInitialPathIfEmpty: true, linkMarkup: true }, hdfsAutocomplete: savePath" type="text" name="target_file" placeholder="${_('Path to CSV file')}" class="pathChooser margin-left-10">
                </div>
                <label class="radio" data-bind="visible: saveTarget() == 'hdfs-file'">
                  <input data-bind="checked: saveOverwrite" type="checkbox" name="overwrite">
                  ${ _('Overwrite') }
                </label>
              </div>
            </div>
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="hdfs-directory">
                  &nbsp;${ _('All') }
                </label>
                <div data-bind="visible: saveTarget() == 'hdfs-directory'" class="inline">
                  <input data-bind="value: savePath, valueUpdate:'afterkeydown', filechooser: { value: savePath, isNestedModal: true }, filechooserOptions: { uploadFile: false, skipInitialPathIfEmpty: true, displayOnlyFolders: true, linkMarkup: true }, hdfsAutocomplete: savePath" type="text" name="target_dir" placeholder="${_('Path to empty directory')}" class="pathChooser margin-left-10 input-xlarge">
                </div>
                <div class="inline-block" data-bind="visible: saveTarget() == 'hdfs-directory', tooltip: { title: '${ _ko("Save the complete result as TSV") }', placement: 'top' }" style="padding: 8px">
                  <i class="fa fa-fw fa-question-circle muted"></i>
                </div>
              </div>
            </div>
            ${ _('Dashboard') }
            <br>
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="hive-table">
                  &nbsp;${ _('Table') }
                </label>
                <div data-bind="visible: saveTarget() == 'hive-table'" class="inline">
                  <input data-bind="hiveChooser: savePath, valueUpdate:'afterkeydown', skipColumns: true, apiHelperUser: '${ user }', apiHelperType: 'hive'" type="text" name="target_table" class="input-xlarge margin-left-10"  pattern="^([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]*$" title="${ _('Only alphanumeric and underscore characters') }" placeholder="${_('Table name or <database>.<table>')}">
                </div>
              </div>
            </div>
            % if ENABLE_SQL_INDEXER.get():
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="search-index">
                  &nbsp;${ _('Index') }
                </label>
                <div class="inline-block" data-bind="tooltip: { title: '${ _ko("Index the data to make Dashboard explorations faster") }', placement: 'top' }">
                  <i class="fa fa-fw fa-question-circle muted"></i>
                </div>
                <div data-bind="visible: saveTarget() == 'search-index'" class="inline">
                  <input data-bind="value: savePath, valueUpdate: 'afterkeydown'" type="text" name="target_index" class="input-xlarge margin-left-10" placeholder="${_('Index name')}">
                </div>
              </div>
            </div>
            % endif
          </fieldset>
        </form>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
        <button data-bind="click: trySaveResults, css: {'disabled': !isValidDestination()}" class="btn btn-primary disable-enter disable-feedback">${_('Export')}</button>
      </div>
    </div>

    <div class="modal hide fade downloadProgressModal" data-bind="attr: { 'id': 'downloadProgressModal' + snippet.id() }">
      <div class="modal-header">
        <!-- ko if: isDownloading -->
        <h2 class="modal-title">${_('Your download is being prepared')}</h2>
        <!-- /ko -->
        <!-- ko if: downloadTruncated -->
        <h2 class="modal-title">${_('Your downloaded results have been truncated')}</h2>
        <!-- /ko -->
      </div>
      <div class="modal-body">
        <!-- ko if: isDownloading -->
        ${ _('Please wait, it might take a while...') } <i class="fa fa-spinner fa-spin"></i>
        <!-- /ko -->
        <!-- ko if: downloadTruncated -->
        ${ _('The number of resulting rows was too big to be downloaded and the resulting file has been truncated to') }
        <strong data-bind="text: downloadCounter"></strong>
        ${ _('rows.') }
        <!-- /ko -->
      </div>
      <div class="modal-footer">
        <!-- ko if: isDownloading -->
        <button data-bind="click: cancelDownload" class="btn btn-danger disable-feedback">${_('Cancel Download')}</button>
        <!-- /ko -->
        <!-- ko if: downloadTruncated -->
        <button class="btn disable-feedback" data-dismiss="modal">${_('Close')}</button>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      function DownloadResultsViewModel (params, element) {
        var self = this;
        self.$downloadForm = $(element).find(".download-form");
        self.snippet = params.snippet;
        self.notebook = params.notebook;
        self.gridSideBtn = ko.observable(params.gridSideBtn);

        self.saveTarget = ko.observable('hdfs-file');
        self.savePath = ko.observable('');
        self.saveOverwrite = ko.observable(false);

        self.isDownloading = ko.observable(false);
        self.downloadTruncated = ko.observable(false);
        self.downloadCounter = ko.observable(0);

        self.checkDownloadInterval = -1;

        if (!self.snippet.downloadResultViewModel) {
          self.snippet.downloadResultViewModel = ko.observable({saveTarget: self.saveTarget});
        }

        self.saveResultsModalId = '#saveResultsModal' + self.snippet.id();
        self.downloadProgressModalId = '#downloadProgressModal' + self.snippet.id();

        $('.saveResultsModal, .downloadProgressModal').on('show', function () {
          self.snippet.saveResultsModalVisible(true);
        });

        $('.saveResultsModal, .downloadProgressModal').on('hide', function () {
          self.snippet.saveResultsModalVisible(false);
        });

        self.isValidDestination = ko.pureComputed(function () {
          return self.savePath() !== '' && (self.saveTarget() != 'hive-table' || /^([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]*$/.test(self.savePath())) || self.saveTarget() == 'dashboard';
        });

        self.clipboardClass = ko.pureComputed(function () {
          return 'download pointer clipboard' + self.snippet.id().split('-')[0];
        });

        var clipboard = new Clipboard('.clipboard' + self.snippet.id().split('-')[0], {
          text: function () {
            if (self.snippet.result && self.snippet.result.data()) {
              var data = self.snippet.result.data();
              var result = '';
              for (var i = 1; i < self.snippet.result.meta().length; i++) { // Skip the row number column
                result += hueUtils.html2text(self.snippet.result.meta()[i].name) + '\t';
              }
              result += '\n';
              data.forEach(function (row) {
                for (var i = 1; i < row.length; i++) { // Skip the row number column
                  result += hueUtils.html2text(row[i]) + '\t';
                }
                result += '\n';
              });
              return result;
            } else {
              return window.I18n('Error while copying results.');
            }
          }
        });

        clipboard.on('success', function (e) {
          $.jHueNotify.info(self.snippet.result.data().length + ' ' + window.I18n('result(s) copied to the clipboard'));
          e.clearSelection();
        });

        self.trySaveResults = function () {
          if (self.isValidDestination()) {
            self.saveResults();
            $(self.saveResultsModalId + ' button.btn-primary').button('loading');
            $(self.saveResultsModalId + ' .loader').show();
          }
        };

        self.saveResults = function() {
          var self = this;

          $.post("${ url('notebook:export_result') }", {
            notebook: ko.mapping.toJSON(self.notebook.getContext()),
            snippet: ko.mapping.toJSON(self.snippet.getContext()),
            format: ko.mapping.toJSON(self.saveTarget()),
            destination: ko.mapping.toJSON(self.savePath()),
            overwrite: ko.mapping.toJSON(self.saveOverwrite()),
            is_embedded: ko.mapping.toJSON(true),
            start_time: ko.mapping.toJSON((new Date()).getTime())
          },
          function(resp) {
            if (resp.status == 0) {
              $(".modal-backdrop").remove();
              if (self.saveTarget() == 'hdfs-file') {
                $(self.saveResultsModalId).modal('hide');
                huePubSub.publish('open.link', resp.watch_url);
              } else if (self.saveTarget() == 'search-index') {
                $(self.saveResultsModalId).modal('hide');
                huePubSub.publish('open.importer.query', resp);
              } else if (self.saveTarget() == 'dashboard') {
                 $(self.saveResultsModalId).modal('hide');
                huePubSub.publish('open.link', resp.watch_url);
              } else if (resp.history_uuid) {
                $(self.saveResultsModalId).modal('hide');
                huePubSub.publish('notebook.task.submitted', resp.history_uuid);
              } else if (resp && resp.message) {
                $(document).trigger("error", resp.message);
              }
            } else {
              $(document).trigger('error', resp.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          }).done(function() {
            $(self.saveResultsModalId + ' button.btn-primary').button('reset');
            $(self.saveResultsModalId + ' .loader').hide();
          });
        };

        self.cancelDownload = function() {
          console.log('Cancel download');
          self.isDownloading(false);
          window.clearInterval(self.checkDownloadInterval);
          $(self.downloadProgressModalId).modal('hide');
        };
      }

      DownloadResultsViewModel.prototype.download = function (format) {
        if (typeof trackOnGA == 'function') {
          trackOnGA('notebook/download/' + format);
        }

        var self = this;
        $.cookie('download-' + self.snippet.id(), null, { expires: -1, path: '/' })
        self.$downloadForm.find('input[name=\'format\']').val(format);
        self.$downloadForm.find('input[name=\'notebook\']').val(ko.mapping.toJSON(self.notebook.getContext()));
        self.$downloadForm.find('input[name=\'snippet\']').val(ko.mapping.toJSON(self.snippet.getContext()));

        self.isDownloading(true);
        self.downloadTruncated(false);
        self.downloadCounter(0);

        var timesChecked = 0;
        self.checkDownloadInterval = window.setInterval(function () {
          if ($.cookie('download-' + self.snippet.id()) === null || typeof $.cookie('download-' + self.snippet.id()) === 'undefined') {
            if (timesChecked == 10) {
              $(self.downloadProgressModalId).modal('show');
            }
          }
          else {
            window.clearInterval(self.checkDownloadInterval);
            try {
              var cookieContent = $.cookie('download-' + self.snippet.id());
              var result = JSON.parse(cookieContent.substr(1, cookieContent.length - 2).replace(/\\"/g, '"').replace(/\\054/g, ','));
              self.downloadTruncated(result.truncated);
              self.downloadCounter(result.row_counter);
              self.isDownloading(false);
              self.notebook.avoidClosing = false;
              if (self.downloadTruncated()) {
                $(self.downloadProgressModalId).modal('show');
              }
              else {
                $(self.downloadProgressModalId).modal('hide');
              }
            }
            catch (e) {
              self.isDownloading(false);
              $(self.downloadProgressModalId).modal('hide');
              self.notebook.avoidClosing = false;
            }
          }
          timesChecked++;
        }, 500, 'editor');

        self.notebook.avoidClosing = true;
        self.$downloadForm.submit();
      };

      DownloadResultsViewModel.prototype.downloadXls = function () {
        var self = this;
        self.download("xls");
      };

      DownloadResultsViewModel.prototype.downloadCsv = function () {
        var self = this;
        self.download("csv");
      };

      ko.components.register('downloadSnippetResults', {
        viewModel: { createViewModel: function (params, componentInfo) {
          return new DownloadResultsViewModel(params, componentInfo.element);
        }},
        template: { element: 'download-results-template' }
      });
    })();
  </script>
</%def>

<%def name="aceKeyboardShortcuts()">
  <script type="text/html" id="ace-keyboard-shortcuts-template">
    <div class="editor-help two-pane">
      <div class="two-pane-left">
        <ul class="nav nav-list">
          <li class="active">
            <a href="#help-editor-syntax" data-bind="click: function(){ $('a[href=\'#help-editor-syntax\']').tab('show'); }">
            ${ _('Syntax')}
            </a>
          </li>
          <li>
            <a href="#help-editor-shortcut" data-bind="click: function(){ $('a[href=\'#help-editor-shortcut\']').tab('show'); }">
            ${ _('Keyboard Shortcuts')}
            </a>
          </li>
        </ul>
      </div>
      <div class="tab-content">
        <div class="tab-pane" id="help-editor-shortcut" style="min-height: 500px">
          <input class="clearable pull-right margin-right-5" type="text" placeholder="${ _('Search...')}" data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
          <div class="clearfix"></div>
          <!-- ko ifnot: query -->
          <ul class="nav nav-tabs" data-bind="foreach: categories">
            <li data-bind="css: { 'active': $parent.activeCategory().label === $data.label }"><a href="javascript: void(0);" data-bind="click: function () { $parent.activeCategory($data); }, text: label"></a></li>
          </ul>
          <div class="tab-content" data-bind="with: activeCategory">
            <div class="tab-pane active">
              <table class="table table-condensed">
                <thead>
                  <tr>
                    <th>${ _('Windows/Linux')}</th>
                    <th>${ _('Mac')}</th>
                    <th>${ _('Action')}</th>
                  </tr>
                </thead>
                <tbody data-bind="foreach: shortcuts">
                  <tr>
                    <td data-bind="text: shortcut" style="width: 25%;"></td>
                    <td data-bind="text: macShortcut" style="width: 25%;"></td>
                    <td data-bind="text: description" style="width: 50%;"></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- /ko -->
          <!-- ko if: query -->
          <ul class="nav nav-tabs">
            <li class="active"><a href="javascript:void(0);">${ _('Search result')}</a></li>
          </ul>
          <div class="tab-content">
            <div class="tab-pane active">
              <!-- ko if: filteredShortcuts().length -->
              <table class="table table-condensed">
                <thead>
                <tr>
                  <th>${ _('Windows/Linux')}</th>
                  <th>${ _('Mac')}</th>
                  <th>${ _('Action')}</th>
                </tr>
                </thead>
                <tbody data-bind="foreach: filteredShortcuts">
                <tr>
                  <td data-bind="text: shortcut" style="width: 25%;"></td>
                  <td data-bind="text: macShortcut" style="width: 25%;"></td>
                  <td data-bind="text: description" style="width: 50%;"></td>
                </tr>
                </tbody>
              </table>
              <!-- /ko -->
              <!-- ko ifnot: filteredShortcuts().length -->
              <div>
                <em>${ _('No shortcuts found.') }</em>
              </div>
              <!-- /ko -->
            </div>
          </div>
          <!-- /ko -->
        </div>
        <div class="tab-pane active" id="help-editor-syntax">
          <ul class="nav nav-tabs">
            <li class="active">
              <a href="#help-editor-syntax-comment" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-comment\']').tab('show'); }">
                ${ _('Comments')}
              </a>
            </li>
            <li>
              <a href="#help-editor-syntax-click" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-click\']').tab('show'); }">
                ${ _('Click')}
              </a>
            </li>
            <li>
              <a href="#help-editor-syntax-multiquery" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-multiquery\']').tab('show'); }">
                ${ _('Multi Query')}
              </a>
            </li>
            <li>
              <a href="#help-editor-syntax-variable" data-bind="click: function(){ $('a[href=\'#help-editor-syntax-variable\']').tab('show'); }">
                ${ _('Variables')}
              </a>
            </li>
          </ul>
          <div class="tab-content">
            <div class="tab-pane active" id="help-editor-syntax-comment">
              <div>${ _('A comment is text that is not executed. It can be of two types:')}</div>
              <ul class="nav help-list-spacing margin-top-10">
                <li>
                  <b>${ _('Single Line') }</b>
                  <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('-- Comment')}'),
                    lines: 1,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-20"></div>
                </li>
                <li>
                  <b>${ _('Multi Line') }</b>
                  <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('/* Multi Line\\n  Comment */')}'),
                    lines: 2,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-20"></div>
                </li>
                <li>
                  <b>${ _('Tip') }</b>
                  <div>
                    ${ _('Use ') } <span class="muted">CTRL + ?</span> ${ _('or') } <span class="muted">Cmd + ?</span> ${ _('to comment/uncomment the selection.') }
                  </div>
                </li>
              </ul>
            </div>
            <div class="tab-pane" id="help-editor-syntax-click">
              <ul class="nav help-list-spacing">
                <li>
                  <b>${ _('Double Click')}</b>
                  <div>${ _('Double clicking the row number selects all rows.')}</div>
                </li>
                <li>
                  <b>${ _('Drag & Drop')}</b>
                  <div>${ _('Dragging and dropping a table name from the assistant onto the editor inserts sample queries in the editor.')}</div>
                </li>
                <li>
                  <b>${ _('Right Click')}</b>
                  <div>${ _('Right clicking on an element of a query will bring up the appropriate browser for that element.')}</div>
                  <div>${ _('Clickable items are highlighted on mouse hover.')}</div>
                  <div><span class="muted">${ _('e.g.: function, column, table names, SELECT *') }</span></div>
                </li>
                <li>
                  <b>${ _('Single Click')}</b>
                  <div>${ _('Single clicking the row number selects the whole row.')}</div>
                </li>
              </ul>
            </div>
            <div class="tab-pane" id="help-editor-syntax-multiquery">
              <div>${ _('Multiple queries can be embedded in a single editor and separated via semicolon.')}</div>
              <div>${ _('The cursor points to the query that will be executed.')}</div>
              <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                  value: ko.observable('${ _('select * from customers;\\nselect * from web_logs;')}'),
                  lines: 2,
                  mode: 'impala',
                  aceOptions: {
                    readOnly: true
                  }}}" class="margin-top-10 margin-bottom-20"></div>
            </div>
            <div class="tab-pane" id="help-editor-syntax-variable">
              <span>${ _('Variables are used to easily configure parameters in a query. They can be of two types:')}</span>
              <ul class="nav help-list-spacing">
                <li>
                  <div class="margin-top-20"><b>${ _('Single Valued')}</b><span class="muted padding-left-20">${ _('${variable_name}')}</span></div>
                  <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('select * from web_logs where country_code = "${country_code}"')}'),
                    lines: 1,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-10"></div>
                  <div>${ _('The variable can have a default value.')}</div>
                  <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('select * from web_logs where country_code = "${country_code=US}"')}'),
                    lines: 1,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-10"></div>
                </li>
                <li>
                  <div class="margin-top-30"><b>${ _('Multi Valued')}</b><span class="muted padding-left-20">${ _('${variable_name=variable_value1, variable_value2,...}')}</span></div>
                  <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('select * from web_logs where country_code = "${country_code=CA, FR, US}"')}'),
                    lines: 1,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-10"></div>
                  <div>${ _('The displayed text can be changed.')}</div>
                  <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"')}'),
                    lines: 1,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-20"></div>
                </li>
                <span>${ _('For values that are not textual, omit the quotes.')}</span>
                <div data-bind="component: { name: 'hue-simple-ace-editor-multi', params: {
                    value: ko.observable('${ _('select * from boolean_table where boolean_column = ${boolean_column}')}'),
                    lines: 1,
                    mode: 'impala',
                    aceOptions: {
                      readOnly: true
                    }}}" class="margin-top-10 margin-bottom-20"></div>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      function AceKeyboardShortcutsViewModel () {
        var self = this;

        self.categories = [{
          label: '${ _('Line Operations')}',
          shortcuts: [{ shortcut: 'Ctrl-D', macShortcut: 'Command-D', description: '${ _('Remove line')}' },
            { shortcut: 'Alt-Shift-Down', macShortcut: 'Command-Option-Down', description: '${ _('Copy lines down')}' },
            { shortcut: 'Alt-Shift-Up', macShortcut: 'Command-Option-Up', description: '${ _('Copy lines up')}' },
            { shortcut: 'Alt-Down', macShortcut: 'Option-Down', description: '${ _('Move lines down')}' },
            { shortcut: 'Alt-Up', macShortcut: 'Option-Up', description: '${ _('Move lines up')}' },
            { shortcut: 'Alt-Delete', macShortcut: 'Ctrl-K', description: '${ _('Remove to line end')}' },
            { shortcut: 'Alt-Backspace', macShortcut: 'Command-Backspace', description: '${ _('Remove to line start')}' },
            { shortcut: 'Ctrl-Backspace', macShortcut: 'Option-Backspace, Ctrl-Option-Backspace', description: '${ _('Remove word left')}' },
            { shortcut: 'Ctrl-Delete', macShortcut: 'Option-Delete', description: '${ _('Remove word right')}' },
            { shortcut: '---', macShortcut: 'Ctrl-O', description: '${ _('Split line')}' }]
        },{
          label: '${ _('Selection')}',
          shortcuts: [{ shortcut: 'Ctrl-A', macShortcut: 'Command-A', description: '${ _('Select all')}' },
            { shortcut: 'Shift-Left', macShortcut: 'Shift-Left', description: '${ _('Select left')}' },
            { shortcut: 'Shift-Right', macShortcut: 'Shift-Right', description: '${ _('Select right')}' },
            { shortcut: 'Ctrl-Shift-Left', macShortcut: 'Option-Shift-Left', description: '${ _('Select word left')}' },
            { shortcut: 'Ctrl-Shift-Right', macShortcut: 'Option-Shift-Right', description: '${ _('Select word right')}' },
            { shortcut: 'Shift-Home', macShortcut: 'Shift-Home', description: '${ _('Select line start')}' },
            { shortcut: 'Shift-End', macShortcut: 'Shift-End', description: '${ _('Select line end')}' },
            { shortcut: 'Alt-Shift-Right', macShortcut: 'Command-Shift-Right', description: '${ _('Select to line end')}' },
            { shortcut: 'Alt-Shift-Left', macShortcut: 'Command-Shift-Left', description: '${ _('Select to line start')}' },
            { shortcut: 'Shift-Up', macShortcut: 'Shift-Up', description: '${ _('Select up')}' },
            { shortcut: 'Shift-Down', macShortcut: 'Shift-Down', description: '${ _('Select down')}' },
            { shortcut: 'Shift-PageUp', macShortcut: 'Shift-PageUp', description: '${ _('Select page up')}' },
            { shortcut: 'Shift-PageDown', macShortcut: 'Shift-PageDown', description: '${ _('Select page down')}' },
            { shortcut: 'Ctrl-Shift-Home', macShortcut: 'Command-Shift-Up', description: '${ _('Select to start')}' },
            { shortcut: 'Ctrl-Shift-End', macShortcut: 'Command-Shift-Down', description: '${ _('Select to end')}' },
            { shortcut: 'Ctrl-Shift-D', macShortcut: 'Command-Shift-D', description: '${ _('Duplicate selection')}' },
            { shortcut: 'Ctrl-Shift-P', macShortcut: '---', description: '${ _('Select to matching bracket')}' }]
        },{
          label: '${ _('Multi-cursor')}',
          shortcuts: [{ shortcut: 'Ctrl-Alt-Up', macShortcut: 'Ctrl-Option-Up', description: '${ _('Add multi-cursor above')}' },
            { shortcut: 'Ctrl-Alt-Down', macShortcut: 'Ctrl-Option-Down', description: '${ _('Add multi-cursor below')}' },
            { shortcut: 'Ctrl-Alt-Right', macShortcut: 'Ctrl-Option-Right', description: '${ _('Add next occurrence to multi-selection')}' },
            { shortcut: 'Ctrl-Alt-Left', macShortcut: 'Ctrl-Option-Left', description: '${ _('Add previous occurrence to multi-selection')}' },
            { shortcut: 'Ctrl-Alt-Shift-Up', macShortcut: 'Ctrl-Option-Shift-Up', description: '${ _('Move multicursor from current line to the line above')}' },
            { shortcut: 'Ctrl-Alt-Shift-Down', macShortcut: 'Ctrl-Option-Shift-Down', description: '${ _('Move multicursor from current line to the line below')}' },
            { shortcut: 'Ctrl-Alt-Shift-Right', macShortcut: 'Ctrl-Option-Shift-Right', description: '${ _('Remove current occurrence from multi-selection and move to next')}' },
            { shortcut: 'Ctrl-Alt-Shift-Left', macShortcut: 'Ctrl-Option-Shift-Left', description: '${ _('Remove current occurrence from multi-selection and move to previous')}' },
            { shortcut: 'Ctrl-Shift-L', macShortcut: 'Ctrl-Shift-L', description: '${ _('Select all from multi-selection')}' }]
        },{
          label: '${ _('Go to')}',
          shortcuts: [{ shortcut: 'Left', macShortcut: 'Left, Ctrl-B', description: '${ _('Go to left')}' },
            { shortcut: 'Right', macShortcut: 'Right, Ctrl-F', description: '${ _('Go to right')}' },
            { shortcut: 'Ctrl-Left', macShortcut: 'Option-Left', description: '${ _('Go to word left')}' },
            { shortcut: 'Ctrl-Right', macShortcut: 'Option-Right', description: '${ _('Go to word right')}' },
            { shortcut: 'Up', macShortcut: 'Up, Ctrl-P', description: '${ _('Go line up')}' },
            { shortcut: 'Down', macShortcut: 'Down, Ctrl-N', description: '${ _('Go line down')}' },
            { shortcut: 'Alt-Left, Home', macShortcut: 'Command-Left, Home, Ctrl-A', description: '${ _('Go to line start')}' },
            { shortcut: 'Alt-Right, End', macShortcut: 'Command-Right, End, Ctrl-E', description: '${ _('Go to line end')}' },
            { shortcut: 'PageUp', macShortcut: 'Option-PageUp', description: '${ _('Go to page up')}' },
            { shortcut: 'PageDown', macShortcut: 'Option-PageDown, Ctrl-V', description: '${ _('Go to page down')}' },
            { shortcut: 'Ctrl-Home', macShortcut: 'Command-Home, Command-Up', description: '${ _('Go to start')}' },
            { shortcut: 'Ctrl-End', macShortcut: 'Command-End, Command-Down', description: '${ _('Go to end')}' },
            { shortcut: 'Ctrl-L, Ctrl-J', macShortcut: 'Command-L, Command-J', description: '${ _('Go to line')}' },
            { shortcut: 'Ctrl-Down', macShortcut: 'Command-Down', description: '${ _('Scroll line down')}' },
            { shortcut: 'Ctrl-Up', macShortcut: '---', description: '${ _('Scroll line up')}' },
            { shortcut: 'Ctrl-P', macShortcut: '---', description: '${ _('Go to matching bracket')}' },
            { shortcut: '---', macShortcut: 'Option-PageDown', description: '${ _('Scroll page down')}' },
            { shortcut: '---', macShortcut: 'Option-PageUp', description: '${ _('Scroll page up')}' }]
        },{
          label: '${ _('Find/Replace')}',
          shortcuts: [{ shortcut: 'Ctrl-F', macShortcut: 'Command-F', description: '${ _('Find')}' },
            { shortcut: 'Ctrl-H', macShortcut: 'Command-Option-F', description: '${ _('Replace')}' },
            { shortcut: 'Ctrl-K', macShortcut: 'Command-G', description: '${ _('Find next')}' },
            { shortcut: 'Ctrl-Shift-K', macShortcut: 'Command-Shift-G', description: '${ _('Find previous')}' }]
        },{
          label: '${ _('Folding')}',
          shortcuts: [{ shortcut: 'Alt-L, Ctrl-F1', macShortcut: 'Command-Option-L, Command-F1', description: '${ _('Fold selection')}' },
            { shortcut: 'Alt-Shift-L, Ctrl-Shift-F1', macShortcut: 'Command-Option-Shift-L, Command-Shift-F1', description: '${ _('Unfold')}' },
            { shortcut: 'Alt-0', macShortcut: 'Command-Option-0', description: '${ _('Fold all')}' },
            { shortcut: 'Alt-Shift-0', macShortcut: 'Command-Option-Shift-0', description: '${ _('Unfold all')}' }]
        },{
          label: '${ _('Other')}',
          shortcuts: [
            { shortcut: 'Ctrl-Space', macShortcut: 'Ctrl-Space', description: '${ _('Autocomplete when Live Autocompletion is off')}' },
            { shortcut: 'Ctrl-Enter', macShortcut: 'Command-Enter', description: '${ _('Execute the active query')}' },
            { shortcut: 'Ctrl-E', macShortcut: 'Command-E', description: '${ _('Create a new query')}' },
            { shortcut: 'Ctrl-S', macShortcut: 'Command-S', description: '${ _('Save the query')}' },
            { shortcut: 'Ctrl-Shift-P', macShortcut: 'Command-Shift-P', description: '${ _('Switch to/from presentation mode')}' },
            { shortcut: 'Ctrl-Alt-T', macShortcut: 'Command-Option-T', description: '${ _('Switch to/from dark editor theme')}' },
            { shortcut: 'Ctrl-i|Ctrl-Shift-f', macShortcut: 'Command-i|Command-Shift-f', description: '${ _('Format selection or all')}' },
            { shortcut: 'Tab', macShortcut: 'Tab', description: '${ _('Indent')}' },
            { shortcut: 'Shift-Tab', macShortcut: 'Shift-Tab', description: '${ _('Outdent')}' },
            { shortcut: 'Ctrl-Z', macShortcut: 'Command-Z', description: '${ _('Undo')}' },
            { shortcut: 'Ctrl-Shift-Z, Ctrl-Y', macShortcut: 'Command-Shift-Z, Command-Y', description: '${ _('Redo')}' },
            { shortcut: 'Ctrl-/', macShortcut: 'Command-/', description: '${ _('Toggle comment')}' },
            { shortcut: 'Ctrl-T', macShortcut: 'Ctrl-T', description: '${ _('Transpose letters')}' },
            { shortcut: 'Ctrl-Shift-U', macShortcut: 'Ctrl-Shift-U', description: '${ _('Change to lower case')}' },
            { shortcut: 'Ctrl-U', macShortcut: 'Ctrl-U', description: '${ _('Change to upper case')}' },
            { shortcut: 'Insert', macShortcut: 'Insert', description: '${ _('Overwrite')}' },
            { shortcut: 'Ctrl-Shift-E', macShortcut: 'Command-Shift-E', description: '${ _('Macros replay')}' },
            { shortcut: 'Ctrl-Alt-E', macShortcut: '---', description: '${ _('Macros recording')}' },
            { shortcut: 'Delete', macShortcut: '---', description: '${ _('Delete')}' },
            { shortcut: '---', macShortcut: 'Ctrl-L', description: '${ _('Center selection')}' }]
        },{
          id: 'settings',
          label: '${ _('Settings')}',
          shortcuts: [{ shortcut: 'Ctrl - ,', macShortcut: 'Command - ,', description: '${ _('Show the settings menu where you can control autocomplete behaviour, syntax checker, dark theme and various editor settings.')}' }]
        }];

        self.query = ko.observable('');

        self.activeCategory = ko.observable(self.categories[0]);

        self.filteredShortcuts = ko.pureComputed(function () {
          var query = (self.query() || '').toLowerCase();
          if (query !== '') {
            var result = [];
            self.categories.forEach(function (category) {
              category.shortcuts.forEach(function (shortcut) {
                if (shortcut.description.toLowerCase().indexOf(query) !== -1 ||
                  shortcut.shortcut.toLowerCase().indexOf(query) !== -1 ||
                  shortcut.macShortcut.toLowerCase().indexOf(query) !== -1) {
                  result.push(shortcut);
                };
              })
            });
            return result;
          }
          return [];
        });
      }

      ko.components.register('aceKeyboardShortcuts', {
        viewModel: AceKeyboardShortcutsViewModel,
        template: { element: 'ace-keyboard-shortcuts-template' }
      });
    })();
  </script>
</%def>
