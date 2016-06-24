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
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="snippetDbSelection()">
  <style>
    .db-selection-input {
      width: 175px !important;
      height: 12px !important;
      font-size: 12px !important;
      border: 1px solid rgba(0,0,0,0.2) !important;
      border-radius: 2px !important;
      box-shadow: none !important;
      margin-left: -1px;
    }
  </style>

  <script type="text/html" id="snippet-db-selection-template">
    <!-- ko ifnot: dbSelectionVisible -->
    <a class="inactive-action active-database margin-left-10" href="javascript:void(0)" data-bind="toggle: dbSelectionVisible, css: { 'blue': dbSelectionVisible }">
      <span data-bind="text: selectedDatabase, visible: ! dbSelectionVisible()"  title="${ _('Selected database') }"></span>
      <i class="fa fa-caret-down"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: dbSelectionVisible -->
    <input class="db-selection-input" type="text" data-bind="textInput: filter, attr: { 'placeHolder': selectedDatabase }, visible: dbSelectionVisible, style: { color: filterEdited() ? '#000' : '#AAA' }"/>
    <i class="fa fa-caret-down"></i>
    <!-- /ko -->
    <div data-bind="css: { 'open' : dbSelectionVisible }" style="display: inline-block;">
      <div class="dropdown-menu" data-bind="visible: filteredDatabases().length > 0" style="overflow-y: scroll; width: 190px; min-height: 34px; max-height: 200px;">
        <ul class="hue-inner-drop-down" data-bind="foreachVisible: { data: filteredDatabases, minHeight: 34, container: '.dropdown-menu' }">
          <li><a href="javascript:void(0)" data-bind="text: $data, click: function () { $parent.selectedDatabase($data); }"></a></li>
        </ul>
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {

      var SnippetDbSelection = function (params, element) {
        var self = this;
        self.dbSelectionVisible = ko.observable(false);
        self.selectedDatabase = params.selectedDatabase;
        self.availableDatabases = params.availableDatabases;

        var closeOnOutsideClick = function (e) {
          var $input = $(element).find('.db-selection-input');
          if (!$input.is($(e.target))) {
            self.dbSelectionVisible(false);
          }
        };

        var inputKeyup = function (e) {
          var $currentActive = $(element).find('.hue-inner-drop-down > .active');
          var activeTop = $currentActive.length !== 0 ? $currentActive.position().top : 0;
          var activeHeight = $currentActive.length !== 0 ? $currentActive.outerHeight(true) : $(element).find('.hue-inner-drop-down li:first-child').outerHeight(true);
          var containerHeight = $(element).find('.dropdown-menu').innerHeight();
          var containerScrollTop = $(element).find('.dropdown-menu').scrollTop();

          $currentActive.removeClass('active');
          if (e.keyCode === 27) {
            // esc
            self.dbSelectionVisible(false);
          } else if (e.keyCode === 38) {
            // up
            if ($currentActive.length !== 0 && $currentActive.prev().length !== 0) {
              if (activeTop < containerScrollTop + activeHeight) {
                $(element).find('.dropdown-menu').scrollTop(activeTop - containerHeight/2);
              }
              $currentActive.prev().addClass('active');
            }
          } else if (e.keyCode === 40) {
            // down
            if ($currentActive.length === 0) {
              $(element).find('.hue-inner-drop-down li:first-child').addClass('active');
            } else if ($currentActive.next().length !== 0) {
              if ((activeTop + activeHeight *3) > containerHeight - containerScrollTop) {
                $(element).find('.dropdown-menu').scrollTop(activeTop - containerHeight/2);
              }
              $currentActive.next().addClass('active');
            } else {
              $currentActive.addClass('active');
            }
          } else if (e.keyCode === 13) {
            // enter
            if ($currentActive.length > 0) {
              self.selectedDatabase(ko.dataFor($currentActive[0]));
              self.dbSelectionVisible(false);
              $(element).find('.dropdown-menu').scrollTop(0)
            }
          } else {
            $(element).find('.dropdown-menu').scrollTop(0)
          }
        };
        self.filter = ko.observable('');

        self.selectedDatabase.subscribe(function () {
          self.dbSelectionVisible(false);
        });

        self.filterEdited = ko.observable(false);

        self.filter.subscribe(function () {
          self.filterEdited(true);
          $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
        });
        self.dbSelectionVisible.subscribe(function (newValue) {
          self.filterEdited(false);
          if (newValue) {
            window.setTimeout(function () {
              self.filter('');
              $(window).on('click', closeOnOutsideClick);
              $(element).find('.db-selection-input').on('keyup', inputKeyup);
              $(element).find('.db-selection-input').focus();
            }, 0);
          } else {
            $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
            $(window).off('click', closeOnOutsideClick);
            $(element).find('.db-selection-input').off('keyup', inputKeyup);
          }
        });
        self.filteredDatabases = ko.pureComputed(function () {
          if (self.filter() === '' || ! self.filterEdited()) {
            return self.availableDatabases();
          } else {
            var lowerFilter = self.filter().toLowerCase();
            return self.availableDatabases().filter(function (database) {
              return database.toLowerCase().indexOf(lowerFilter) !== -1;
            });
          }
        });
      };

      ko.components.register('snippet-db-selection', {
        viewModel: {
          createViewModel: function(params, componentInfo) {
            return new SnippetDbSelection(params, componentInfo.element);
          }
        },
        template: { element: 'snippet-db-selection-template' }
      });
    }));
  </script>
</%def>

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
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {
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
      }());
    }));
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
      <a class="snippet-side-btn inactive-action dropdown-toggle pointer" style="padding-right:0" data-toggle="dropdown">
        <i class="fa fa-fw fa-download"></i>
      </a>
      <ul class="dropdown-menu less-padding">
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: downloadCsv, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }" title="${ _('Download first rows as CSV') }">
            <i class="fa fa-fw fa-file-o"></i> ${ _('CSV') }
          </a>
        </li>
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: downloadXls, event: { mouseover: function(){ window.onbeforeunload = null; }, mouseout: function() { window.onbeforeunload = $(window).data('beforeunload'); } }" title="${ _('Download first rows as XLS') }">
            <i class="fa fa-fw fa-file-excel-o"></i> ${ _('Excel') }
          </a>
        </li>
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: function() { $('#saveResultsModal').modal('show'); }" title="${ _('Save the results to HDFS or a new table') }">
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
                  &nbsp;${ _('In HDFS (small csv)') }
                </label>
                <div data-bind="visible: saveTarget() == 'hdfs-file'" class="inline">
                  <input data-bind="value: savePath, filechooser: { value: savePath, isNestedModal: true }, filechooserOptions: { uploadFile: false }, hdfsAutocomplete: savePath" type="text" name="target_file" placeholder="${_('Path to CSV file')}" class="pathChooser margin-left-10">
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
                  &nbsp;${ _('In HDFS (large file)') }
                </label>
                <div data-bind="visible: saveTarget() == 'hdfs-directory'" class="inline">
                  <input data-bind="value: savePath, filechooser: { value: savePath, isNestedModal: true }, filechooserOptions: { uploadFile: false }, hdfsAutocomplete: savePath" type="text" name="target_dir" placeholder="${_('Path to directory')}" class="pathChooser margin-left-10">
                  <i class="fa fa-question-circle muted" title="${ _("Use this option if you have a large result. It will rerun the entire query and save the results to the chosen HDFS directory.") }"></i>
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
          </fieldset>
        </form>
      </div>
      <div class="modal-footer">
        <button class="btn" data-dismiss="modal">${_('Cancel')}</button>
        <button data-bind="click: trySaveResults" class="btn btn-primary disable-feedback">${_('Save')}</button>
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {
      function DownloadResultsViewModel (params, element) {
        var self = this;
        self.$downloadForm = $(element).find(".download-form");
        self.snippet = params.snippet;
        self.notebook = params.notebook;

        self.saveTarget = ko.observable('hdfs-file');
        self.savePath = ko.observable('');
        self.saveOverwrite = ko.observable(true);

        self.trySaveResults = function() {
          self.saveResults();

          $("#saveResultsModal button.btn-primary").button('loading');
          $("#saveResultsModal .loader").show();
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
      };

      DownloadResultsViewModel.prototype.download = function (format) {
        if (typeof trackOnGA == 'function') {
          trackOnGA('notebook/download/' + format);
        }

        var self = this;
        self.$downloadForm.find('input[name=\'format\']').val(format);
        self.$downloadForm.find('input[name=\'notebook\']').val(ko.mapping.toJSON(self.notebook.getContext()));
        self.$downloadForm.find('input[name=\'snippet\']').val(ko.mapping.toJSON(self.snippet.getContext()));
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
    }));
  </script>
</%def>