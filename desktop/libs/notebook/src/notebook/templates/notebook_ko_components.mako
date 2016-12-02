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

from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko

try:
  from beeswax.conf import DOWNLOAD_CELL_LIMIT
except ImportError, e:
  LOG.warn("Hive app is not enabled")
  DOWNLOAD_CELL_LIMIT = None

try:
  from indexer.conf import ENABLE_NEW_INDEXER
except ImportError, e:
  LOG.warn("Indexer app is not enabled")
  ENABLE_NEW_INDEXER = None
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
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${ _('Add Snippet') }</h3>
      </div>
      <div class="modal-body" style="min-height: 100px">
        <ul class="snippet-list-alts" data-bind="foreach: availableSnippets">
          <li data-bind="click: function() { $parent.addNewSnippet($data) }">
            <div style="width: 30px; display:inline-block;">
            <!-- ko if: $root.getSnippetViewSettings(type()).snippetImage -->
            <img class="snippet-icon" data-bind="attr: { 'src': $root.getSnippetViewSettings(type()).snippetImage }">
            <!-- /ko -->
            <!-- ko if: $root.getSnippetViewSettings(type()).snippetIcon -->
            <i style="margin-left: 2px; color: #338bb8;" class="fa snippet-icon" data-bind="css: $root.getSnippetViewSettings(type()).snippetIcon"></i>
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

  <script type="text/javascript" charset="utf-8">
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
    <form method="POST" action="${ url('notebook:download') }" class="download-form" style="display: inline">
      ${ csrf_token(request) | n,unicode }
      <input type="hidden" name="notebook"/>
      <input type="hidden" name="snippet"/>
      <input type="hidden" name="format"/>
    </form>

    <div class="hover-dropdown" data-bind="visible: snippet.status() == 'available' && snippet.result.hasSomeResults() && snippet.result.type() == 'table'" style="display:none;">
      <a class="snippet-side-btn inactive-action dropdown-toggle pointer" style="padding-right:0" data-toggle="dropdown" title="${ _('Get results') }">
        <!-- ko ifnot: isDownloading -->
        <i class="fa fa-fw fa-download"></i>
        <!-- /ko -->

        <!-- ko if: isDownloading -->
        <i class="fa fa-fw fa-spinner fa-spin"></i>
        <!-- /ko -->
      </a>
      <ul class="dropdown-menu less-padding">
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: downloadCsv, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }" title="${ _('Download first %s cells as CSV') % DOWNLOAD_CELL_LIMIT.get() }">
            <i class="fa fa-fw fa-file-o"></i> ${ _('CSV') }
          </a>
        </li>
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: downloadXls, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }" title="${ _('Download first %s cells as XLS') % DOWNLOAD_CELL_LIMIT.get() }">
            <i class="fa fa-fw fa-file-excel-o"></i> ${ _('Excel') }
          </a>
        </li>
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: function() { $('#saveResultsModal').modal('show'); }" title="${ _('Save the results to a large file or a new table') }">
            <i class="fa fa-fw fa-save"></i> ${ _('Export') }
          </a>
        </li>
      </ul>
    </div>

    <div id="saveResultsModal" class="modal hide fade">
      <div class="loader hide">
        <div class="overlay"></div>
        <!--[if !IE]><!--><i class="fa fa-spinner fa-spin"></i><!--<![endif]-->
        <!--[if IE]><img class="spinner" src="${ static('desktop/art/spinner-big-inverted.gif') }"/><![endif]-->
      </div>

      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Save query result in')}</h3>
      </div>
      <div class="modal-body" style="padding: 4px">
        <form id="saveResultsForm" method="POST" class="form form-inline">
          ${ csrf_token(request) | n,unicode }
          <fieldset>
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="hdfs-file">
                  &nbsp;${ _('A file (max %s cells)') % DOWNLOAD_CELL_LIMIT.get() }
                </label>
                <div data-bind="visible: saveTarget() == 'hdfs-file'" class="inline">
                  <input data-bind="value: savePath, valueUpdate:'afterkeydown', filechooser: { value: savePath, isNestedModal: true }, filechooserOptions: { uploadFile: false, skipInitialPathIfEmpty: true, linkMarkup: true }, hdfsAutocomplete: savePath" type="text" name="target_file" placeholder="${_('Path to CSV file')}" class="pathChooser margin-left-10">
                </div>
                <label class="radio" data-bind="visible: saveTarget() == 'hdfs-file'">
                  <input data-bind="checked: saveOverwrite" type="checkbox" name="overwrite">
                  ${ _('Overwrite') }
                </label>
              </div>
            </div>
            <div class="control-group">
              <div class="controls" data-bind="visible: snippet.type() == 'hive'">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="hdfs-directory">
                  &nbsp;${ _('A file (large result)') }
                </label>
                <div data-bind="visible: saveTarget() == 'hdfs-directory'" class="inline">
                  <input data-bind="value: savePath, valueUpdate:'afterkeydown', filechooser: { value: savePath, isNestedModal: true }, filechooserOptions: { uploadFile: false, skipInitialPathIfEmpty: true, displayOnlyFolders: true, linkMarkup: true }, hdfsAutocomplete: savePath" type="text" name="target_dir" placeholder="${_('Path to empty directory')}" class="pathChooser margin-left-10">
                  <div class="inline-block" data-bind="tooltip: { title: '${ _ko("Use this option if you have a large result. It will rerun the entire query and save the results to the chosen HDFS directory.") }', placement: 'top' }" style="padding: 8px">
                    <i class="fa fa-fw fa-question-circle muted"></i>
                  </div>
                </div>
              </div>
            </div>
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="hive-table">
                  &nbsp;${ _('A new table') }
                </label>
                <div data-bind="visible: saveTarget() == 'hive-table'" class="inline">
                  <input data-bind="hivechooser: savePath" type="text" name="target_table" class="input-xlarge margin-left-10" placeholder="${_('Table name or <database>.<table>')}">
                </div>
              </div>
            </div>
            % if hasattr(ENABLE_NEW_INDEXER, 'get') and ENABLE_NEW_INDEXER.get():
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input data-bind="checked: saveTarget" type="radio" name="save-results-type" value="search-index">
                  &nbsp;${ _('A search dashboard') }
                </label>
                <div data-bind="visible: saveTarget() == 'search-index'" class="inline">
                  <input data-bind="value: savePath, valueUpdate:'afterkeydown'" type="text" name="target_index" class="input-xlarge margin-left-10" placeholder="${_('Index name')}">
                </div>
              </div>
            </div>
            % endif
          </fieldset>
        </form>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
        <button data-bind="click: trySaveResults, css: {'disabled': isPathEmpty}" class="btn btn-primary disable-feedback">${_('Save')}</button>
      </div>
    </div>

    <div id="downloadProgressModal" class="modal hide fade">
      <div class="modal-header">
        <!-- ko if: isDownloading -->
        <h3>${_('Your download is being prepared')}</h3>
        <!-- /ko -->
        <!-- ko if: downloadTruncated -->
        <h3>${_('Your downloaded results have been truncated')}</h3>
        <!-- /ko -->
      </div>
      <div class="modal-body" style="padding: 4px">
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

  <script type="text/javascript" charset="utf-8">
    (function () {

      function DownloadResultsViewModel (params, element) {
        var self = this;
        self.$downloadForm = $(element).find(".download-form");
        self.snippet = params.snippet;
        self.notebook = params.notebook;

        self.saveTarget = ko.observable('hdfs-file');
        self.savePath = ko.observable('');
        self.saveOverwrite = ko.observable(true);

        self.isDownloading = ko.observable(false);
        self.downloadTruncated = ko.observable(false);
        self.downloadCounter = ko.observable(0);

        self.checkDownloadInterval = -1;

        self.isPathEmpty = ko.pureComputed(function () {
          return self.savePath() === '';
        });

        self.trySaveResults = function () {
          if (!self.isPathEmpty()) {
            self.saveResults();
            $("#saveResultsModal button.btn-primary").button('loading');
            $("#saveResultsModal .loader").show();
          }
        };

        self.saveResults = function() {
          var self = this;

          $.post("${ url('notebook:export_result') }", {
            notebook: ko.mapping.toJSON(self.notebook.getContext()),
            snippet: ko.mapping.toJSON(self.snippet.getContext()),
            format: ko.mapping.toJSON(self.saveTarget()),
            destination: ko.mapping.toJSON(self.savePath()),
            overwrite: ko.mapping.toJSON(self.saveOverwrite())
          },
          function(data) {
            if (data.status == 0) {
              window.location.href = data.watch_url;
            } else {
              $(document).trigger('error', data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          }).done(function() {
            $("#saveResultsModal button.btn-primary").button('reset');
            $("#saveResultsModal .loader").hide();
          });
        };

        self.cancelDownload = function() {
          console.log('Cancel download');
          self.isDownloading(false);
          window.clearInterval(self.checkDownloadInterval);
          $('#downloadProgressModal').modal('hide');
        };
      };

      DownloadResultsViewModel.prototype.download = function (format) {
        if (typeof trackOnGA == 'function') {
          trackOnGA('notebook/download/' + format);
        }

        var self = this;
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
              $('#downloadProgressModal').modal('show');
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
                $('#downloadProgressModal').modal('show');
              }
              else {
                $('#downloadProgressModal').modal('hide');
              }
            }
            catch (e) {
              self.isDownloading(false);
              $('#downloadProgressModal').modal('hide');
              self.notebook.avoidClosing = false;
            }
          }
          timesChecked++;
        }, 500);

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
