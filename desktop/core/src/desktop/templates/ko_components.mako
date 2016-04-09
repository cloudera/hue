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

<%def name="jvmMemoryInput()">
  <script type="text/html" id="jvm-memory-input-template">
    <input type="text" class="input-small" data-bind="numericTextInput: { value: value, precision: 0, allowEmpty: true }" /> <select class="input-mini" data-bind="options: units, value: selectedUnit" />
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
        var JVM_MEM_PATTERN = /([0-9]+)([MG])$/;
        var UNITS = {'MB': 'M', 'GB': 'G'};

        function JvmMemoryInputViewModel(params) {
          this.valueObservable = params.value;
          this.units = Object.keys(UNITS);
          this.selectedUnit = ko.observable();
          this.value = ko.observable('');

          var match = JVM_MEM_PATTERN.exec(this.valueObservable());
          if (match && match.length === 3) {
            this.value(match[1]);
            this.selectedUnit(match[2] === 'M' ? 'MB' : 'GB');
          }

          this.value.subscribe(this.updateValueObservable, this);
          this.selectedUnit.subscribe(this.updateValueObservable, this);
        }

        JvmMemoryInputViewModel.prototype.updateValueObservable = function () {
          if (isNaN(this.value()) || this.value() === '') {
            this.valueObservable(undefined);
          } else {
            this.valueObservable(this.value() + UNITS[this.selectedUnit()]);
          }
        };

        ko.components.register('jvm-memory-input', {
          viewModel: JvmMemoryInputViewModel,
          template: { element: 'jvm-memory-input-template' }
        });
      }());
    }));
  </script>
</%def>

<%def name="keyValueListInput()">
  <script type="text/html" id="key-value-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent' }}, visible: values().length" class="unstyled">
      <li>
        <div class="input-append" style="margin-bottom: 4px">
          <input type="text" style="width: 130px" placeholder="${ _('Key') }" data-bind="textInput: key, valueUpdate: 'afterkeydown'"/>
          <input type="text" style="width: 130px" placeholder="${ _('Value') }" data-bind="textInput: value, valueUpdate: 'afterkeydown'"/>
          <span class="add-on move-widget muted"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div style="min-width: 280px; margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
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

        function KeyValueListInputViewModel(params) {
          var self = this;
          self.values = params.values;
          params.visibleObservable.subscribe(function (newValue) {
            if (!newValue) {
              self.values($.grep(self.values(), function (value) {
                return value.key() && value.value();
              }))
            }
          });
        }

        KeyValueListInputViewModel.prototype.addValue = function () {
          var self = this;
          var newValue = {
            key: ko.observable(''),
            value: ko.observable('')
          };
          self.values.push(newValue);
        };

        KeyValueListInputViewModel.prototype.removeValue = function (valueToRemove) {
          var self = this;
          self.values.remove(valueToRemove);
        };

        ko.components.register('key-value-list-input', {
          viewModel: KeyValueListInputViewModel,
          template: { element: 'key-value-list-input-template' }
        });
      }());
    }));
  </script>
</%def>

<%def name="functionListInput()">
  <script type="text/html" id="function-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent' }}, visible: values().length" class="unstyled">
      <li>
        <div class="input-append" style="margin-bottom: 4px">
          <input type="text" style="width: 110px" placeholder="${ _('Name, e.g. foo') }" data-bind="textInput: name, valueUpdate: 'afterkeydown'"/>
          <input type="text" style="width: 150px" placeholder="${ _('Class, e.g. org.hue.Bar') }" data-bind="textInput: class_name, valueUpdate: 'afterkeydown'"/>
          <span class="add-on move-widget muted"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div style="min-width: 280px; margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
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

        function FunctionListInputViewModel(params) {
          var self = this;
          self.values = params.values;
          params.visibleObservable.subscribe(function (newValue) {
            if (!newValue) {
              self.values($.grep(self.values(), function (value) {
                return value.name() && value.class_name();
              }))
            }
          });
        }

        FunctionListInputViewModel.prototype.addValue = function () {
          var self = this;
          var newValue = {
            name: ko.observable(''),
            class_name: ko.observable('')
          };
          self.values.push(newValue);
        };

        FunctionListInputViewModel.prototype.removeValue = function (valueToRemove) {
          var self = this;
          self.values.remove(valueToRemove);
        };

        ko.components.register('function-list-input', {
          viewModel: FunctionListInputViewModel,
          template: { element: 'function-list-input-template' }
        });
      }());
    }));
  </script>
</%def>

<%def name="hdfsFileListInput()">
  <script type="text/html" id="hdfs-file-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent' }}, visible: values().length" class="unstyled">
      <li>
        <div class="input-append" style="margin-bottom: 4px">
          <input type="text" class="filechooser-input" data-bind="value: path, valueUpdate:'afterkeydown', filechooser: { value: path, isAddon: true }" placeholder="${ _('Path to the file, e.g. hdfs://localhost:8020/user/hue/file.hue') }"/>
          <span class="add-on move-widget muted"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div style="min-width: 280px; margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
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

        var identifyType = function (path) {
          switch (path.substr(path.lastIndexOf('.') + 1).toLowerCase()) {
            case 'jar':
              return 'jar'
            case 'zip':
            case 'tar':
            case 'rar':
            case 'bz2':
            case 'gz':
            case 'tgz':
              return 'archive';
          }
          return 'file';
        }

        function HdfsFileListInputViewModel(params) {
          var self = this;
          self.values = params.values;
          $.each(self.values(), function (idx, value) {
            value.path.subscribe(function (newPath) {
              value.type(identifyType(newPath));
            });
          })
          params.visibleObservable.subscribe(function (newValue) {
            if (!newValue) {
              self.values($.grep(self.values(), function (value) {
                return value.path();
              }))
            }
          });
        }

        HdfsFileListInputViewModel.prototype.addValue = function () {
          var self = this;
          var newValue = {
            path: ko.observable(''),
            type: ko.observable('')
          };
          newValue.path.subscribe(function (newPath) {
            newValue.type(identifyType(newPath));
          })
          self.values.push(newValue);
        };

        HdfsFileListInputViewModel.prototype.removeValue = function (valueToRemove) {
          var self = this;
          self.values.remove(valueToRemove);
        };

        ko.components.register('hdfs-file-list-input', {
          viewModel: HdfsFileListInputViewModel,
          template: { element: 'hdfs-file-list-input-template' }
        });
      }());
    }));
  </script>
</%def>

<%def name="csvListInput()">
  <script type="text/html" id="csv-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent' }}, visible: values().length" class="unstyled">
      <li style="margin-bottom: 4px">
        <div class="input-append">
          <!-- ko ifnot: $parent.inputTemplate -->
          <input type="text" data-bind="textInput: value, valueUpdate: 'afterkeydown', attr: { placeholder: $parent.placeholder }"/>
          <!-- /ko -->
          <!-- ko template: { if: $parent.inputTemplate, name: $parent.inputTemplate } --><!-- /ko -->
          <span class="add-on move-widget muted"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div style="min-width: 280px; margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
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
        function CsvListInputViewModel(params) {
          this.valueObservable = params.value;
          this.isArray = $.isArray(this.valueObservable());
          this.placeholder = params.placeholder || '';
          this.inputTemplate = params.inputTemplate || null;

          var initialValues;
          if (this.isArray) {
            initialValues = ko.mapping.toJS(this.valueObservable());
          } else {
            initialValues = this.valueObservable() != null ? this.valueObservable().split(",") : [];
          }
          for (var i = 0; i < initialValues.length; i++) {
            initialValues[i] = {value: ko.observable(initialValues[i].trim())};
            initialValues[i].value.subscribe(this.updateValueObservable, this);
          }
          this.values = ko.observableArray(initialValues);
          this.values.subscribe(this.updateValueObservable, this);
        }

        CsvListInputViewModel.prototype.addValue = function () {
          var newValue = {value: ko.observable('')};
          newValue.value.subscribe(this.updateValueObservable, this);
          this.values.push(newValue);
        };

        CsvListInputViewModel.prototype.removeValue = function (valueToRemove) {
          this.values.remove(valueToRemove);
        };

        CsvListInputViewModel.prototype.updateValueObservable = function () {
          var cleanValues = $.map(this.values(), function (item) {
            return item.value();
          });
          cleanValues = $.grep(cleanValues, function (value) {
            return value;
          });
          this.valueObservable(this.isArray ? cleanValues : cleanValues.join(','));
        };

        ko.components.register('csv-list-input', {
          viewModel: CsvListInputViewModel,
          template: { element: 'csv-list-input-template' }
        });
      }());
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
            <i style="margin-left: 6px; color: #338bb8;" class="fa snippet-icon" data-bind="css: $root.getSnippetViewSettings(type()).snippetIcon"></i>
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