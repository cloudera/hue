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

<%def name="config()">

  <style>
    .config-property {
      display: block;
      vertical-align: top;
      margin-bottom: 20px;
      position: relative;
    }

    .config-label {
      display: inline-block;
      min-width: 130px;
      margin: 4px 10px;
      float:left;
      text-align: right;
    }

    .config-controls {
      display: inline-block;
    }

    .config-property-remove {
      display: inline-block;
      vertical-align: top;
      position: relative;
      margin-top: 6px;
      margin-left: 10px;
    }

    .property-help {
      display: inline-block;
      width: 10px;
      height: 14px;
      margin-left: 7px;
      font-size: 14px;
      color: #888;
    }

    .config-actions {
      display: inline-block;
      font-size: 13px;
      margin-top: -3px;
      margin-left: 15px;
      vertical-align: text-top;
    }
  </style>

  <script type="text/html" id="property-selector-template">
    <!-- ko foreach: selectedProperties -->
    <div>
      <div class="config-property-remove">
        <a class="inactive-action" href="javascript:void(0)" data-bind="click: function() { $parent.removeProperty($data) }" title="${ _('Remove') }">
          <i class="fa fa-times"></i>
        </a>
      </div>
      <!-- ko template: {
        name: 'property',
        data: {
          type: type(),
          label: nice_name,
          helpText: help_text,
          value: value,
          property: $data,
          visibleObservable: $parent.visibleObservable
        }
      } --><!-- /ko -->
    </div>
    <!-- /ko -->
    <div class="config-property-available margin-left-10" data-bind="visible: availableProperties().length > 0">
      <select data-bind="options: availableProperties, optionsText: 'nice_name', optionsCaption: '${_ko('Add a property...')}', value: propertyToAdd"></select>
      <div style="display: inline-block; vertical-align: top; margin-top: 6px; margin-left: 6px;">
        <a class="inactive-action pointer" data-bind="click: addProperty, visible: propertyToAdd() != null">
          <i class="fa fa-plus"></i>
        </a>
      </div>
    </div>
  </script>

  <script type="text/html" id="multi-group-selector-template">
    <div class="jHueSelector" style="position: relative;" data-bind="style: { 'width': width + 'px' }">
      <div class="jHueSelectorHeader" data-bind="style: { 'width': (width-8) + 'px' }">
        <input style="float:right;position: relative; margin: 0;" type="text" placeholder="${_('Search')}" data-bind="textInput: searchQuery">
        <label><input type="checkbox" data-bind="checked: allSelected">${_('Select all')}</label>
      </div>
      <div class="jHueSelectorBody" data-bind="style: { 'height': (height - 33) + 'px' }">
        <ul>
          <!-- ko foreach: searchResultKeys -->
          <li class="selectorDivider"><strong data-bind="text: $data"></strong></li>
          <!-- ko foreach: $parent.searchResult()[$data] -->
          <li><label><input type="checkbox" class="selector" data-bind="checked: altChecked"><!-- ko text: label --><!-- /ko --></label></li>
          <!-- /ko -->
          <!-- /ko -->
        </ul>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      function MultiGroupAlternative(alt, params, initiallyChecked) {
        var self = this;
        self.altChecked = ko.observable(initiallyChecked || false);
        self.label = params.optionsText ? alt[params.optionsText] : alt;
        var value = params.optionsValue ? alt[params.optionsValue] : alt;
        self.altChecked.subscribe(function (newValue) {
          if (newValue) {
            params.selectedOptions.push(value);
          } else {
            params.selectedOptions.remove(value);
          }
        });
      }

      function MultiGroupSelectorViewModel(params) {
        var self = this;
        self.width = params.width || 600;
        self.height = params.height || 300;

        var textAccessor = function (alt) {
          if (params.optionsText) {
            return alt[params.optionsText];
          }
          return alt;
        };

        self.searchQuery = ko.observable();

        var addToIndexedLists = function (index, key, value) {
          if (! index[key]) {
            index[key] = [];
          }
          index[key].push(value);
        };

        self.searchResult = ko.pureComputed(function () {
          if (self.searchQuery()) {
            var lowerQuery = self.searchQuery().toLowerCase();
            var result = {};
            Object.keys(self.addressBook()).forEach(function (key) {
              self.addressBook()[key].forEach(function (alt) {
                if (alt.label.toLowerCase().indexOf(lowerQuery) !== -1) {
                  addToIndexedLists(result, key, alt);
                }
              });
            });
            return result;
          }
          return self.addressBook();
        });

        var initiallyCheckedIndex = {};
        params.selectedOptions().forEach(function (alt) {
          initiallyCheckedIndex[alt] = true;
        });

        self.addressBook = ko.pureComputed(function () {
          var result = {};
          ko.unwrap(params.options).forEach(function (alt) {
            addToIndexedLists(result, textAccessor(alt).charAt(0).toUpperCase(), new MultiGroupAlternative(alt, params, initiallyCheckedIndex[params.optionsValue ? alt[params.optionsValue] : alt]));
          });
          Object.keys(result).forEach(function (key) {
            result[key].sort();
          });
          return result;
        });

        self.searchResultKeys = ko.pureComputed(function () {
          return Object.keys(self.searchResult()).sort();
        });

        self.allSelected = ko.observable(false);

        self.allSelected.subscribe(function (newValue) {
          self.searchResultKeys().forEach(function (key) {
            self.searchResult()[key].forEach(function (alt) {
              alt.altChecked(newValue);
            })
          })
        })
      }

      ko.components.register('multi-group-selector', {
        viewModel: MultiGroupSelectorViewModel,
        template: {element: 'multi-group-selector-template'}
      });
    })();
  </script>

  <script type="text/javascript">
    (function () {

      function PropertySelectorViewModel(params) {
        var self = this;
        var allProperties = params.properties;

        self.selectedProperties = ko.observableArray();
        self.availableProperties = ko.observableArray();
        self.propertyToAdd = ko.observable(null);

        var setInitialProperties = function () {
          self.selectedProperties([]);
          self.availableProperties([]);
          allProperties().forEach(function (property) {
            if (property.defaultValue && ko.mapping.toJSON(property.value) !== ko.mapping.toJSON(property.defaultValue)) {
              self.selectedProperties.push(property);
            } else {
              self.availableProperties.push(property);
            }
          });
          self.sort();
        };

        setInitialProperties();
        self.visibleObservable = params.visibleObservable || ko.observable();

        self.visibleObservable.subscribe(function (newValue) {
          if (!newValue) {
            setInitialProperties();
          }
        });
      }

      var niceNameSort = function (a, b) {
        return a.nice_name().localeCompare(b.nice_name());
      }

      PropertySelectorViewModel.prototype.sort = function () {
        var self = this;
        self.availableProperties.sort(niceNameSort);
        self.selectedProperties.sort(niceNameSort);
      }

      PropertySelectorViewModel.prototype.addProperty = function () {
        var self = this;
        if (self.propertyToAdd()) {
          switch (self.propertyToAdd().type()) {
            case 'csv-hdfs-files':
              self.propertyToAdd().value('');
              break;
            case 'hdfs-files':
              self.propertyToAdd().value([{ path: ko.observable(''), type: ko.observable('') }]);
              break;
            case 'functions':
              self.propertyToAdd().value([{ name: ko.observable(''), class_name: ko.observable('') }]);
              break;
            case 'settings':
              self.propertyToAdd().value([{ key: ko.observable(''), value: ko.observable('') }]);
          }
          self.selectedProperties.push(self.propertyToAdd());
          self.availableProperties.remove(self.propertyToAdd());
          self.propertyToAdd(null);
          self.sort();
        }
      };

      PropertySelectorViewModel.prototype.removeProperty = function (property) {
        var self = this;
        property.value(property.defaultValue());
        self.selectedProperties.remove(property);
        self.availableProperties.push(property);
        self.sort();
      }

      ko.components.register('property-selector', {
        viewModel: PropertySelectorViewModel,
        template: {element: 'property-selector-template'}
      });
    })();
  </script>

  <script type="text/html" id="property">
    <div class="config-property" data-bind="visibleOnHover: { selector: '.hover-actions' }">
      <label class="config-label" data-bind="click: function(data, event){ $(event.target).siblings('.config-controls').find('.config-property-add-value a').click(); }">
        <!-- ko text: label --><!-- /ko --><!-- ko if: typeof helpText !== 'undefined' --><div class="property-help" data-bind="tooltip: { title: helpText(), placement: 'bottom' }"><i class="fa fa-question-circle-o"></i></div><!-- /ko -->
      </label>
      <div class="config-controls">
        <!-- ko template: { name: 'property-' + type } --><!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="property-jvm">
    <div data-bind="component: { name: 'jvm-memory-input', params: { value: value } }"></div>
  </script>

  <script type="text/html" id="property-number">
    <input type="text" class="input-small" data-bind="numericTextInput: { value: value, precision: 1, allowEmpty: true }, valueUpdate:'afterkeydown', attr: { 'title': typeof title === 'undefined' ? '' : title }"/>
  </script>

  <script type="text/html" id="property-string">
    <!-- ko if: typeof property !== 'undefined' && typeof property.options !== 'undefined' && property.options().length > 0 -->
    <div class="selectize-wrapper" style="min-width: 200px;">
      <select placeholder="${ _('Key') }" data-bind="selectize: $.map($parent.options(), function (option) { return { value: option } }), value: value, options: $.map($parent.options(), function (option) { return { value: option } }), optionsText: 'value', optionsValue: 'value'"></select>
    </div>
    <!-- /ko -->
    <!-- ko if: typeof property === 'undefined' || typeof property.options === 'undefined' || property.options().length === 0 -->
    <input class="input" type="text" data-bind="textInput: value, valueUpdate:'afterkeydown'" />
    <!-- /ko -->
  </script>

  <script type="text/html" id="property-boolean">
    <input class="input-small" type="checkbox" data-bind="checked: value" />
  </script>

  <script type="text/html" id="property-csv">
    <div data-bind="component: { name: 'csv-list-input', params: { value: value, placeholder: typeof placeholder === 'undefined' ? '' : placeholder } }"></div>
  </script>

  <script type="text/html" id="property-parameters">
    <div data-bind="component: { name: 'name-value-list-input', params: { values: value, visibleObservable: visibleObservable, property: property } }"></div>
  </script>

  <script type="text/html" id="property-settings">
    <div data-bind="component: { name: 'key-value-list-input', params: { values: value, visibleObservable: visibleObservable, property: property } }"></div>
  </script>

  <script type="text/html" id="property-hdfs-files">
    <div data-bind="component: { name: 'hdfs-file-list-input', params: { values: value, visibleObservable: visibleObservable } }"></div>
  </script>

  <script type="text/html" id="property-csv-hdfs-files">
    <div data-bind="component: { name: 'csv-list-input', params: { value: value, inputTemplate: 'property-hdfs-file', placeholder: typeof placeholder === 'undefined' ? '' : placeholder } }"></div>
  </script>

  <script type="text/html" id="property-hdfs-file">
    <div class="input-append">
      <input type="text" style="min-width: 300px" class="filechooser-input" data-bind="value: value, valueUpdate:'afterkeydown', filechooser: { value: value, isAddon: true}, filechooserOptions: { skipInitialPathIfEmpty: true }" placeholder="${ _('Path to the file, e.g. hdfs://localhost:8020/user/hue') }"/>
    </div>
  </script>

  <script type="text/html" id="property-functions">
    <div data-bind="component: { name: 'function-list-input', params: { values: value, visibleObservable: visibleObservable } }"></div>
  </script>

  <script type="text/html" id="jvm-memory-input-template">
    <input type="text" class="input-small" data-bind="numericTextInput: { value: value, precision: 0, allowEmpty: true }" /> <select class="input-mini" data-bind="options: units, value: selectedUnit" />
  </script>

  <script type="text/javascript">
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
    })();
  </script>

  <script type="text/html" id="key-value-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: values().length" class="unstyled">
      <li style="clear:both;">
        <!-- ko if: $parent.options.length > 0 -->
        <div class="selectize-wrapper" style="width: 200px;">
          <select placeholder="${ _('Key') }" data-bind="selectize: $parent.options, selectizeOptions: {create: true}, value: key, options: $parent.options, optionsText: 'value', optionsValue: 'value'"></select>
        </div>
        <!-- /ko -->
        <div class="input-append" style="margin-bottom: 4px">
          <!-- ko if: $parent.options.length === 0 -->
          <input type="text" class="config-property-input-small" style="width: 182px; margin-right: 4px;" placeholder="${ _('Key') }" data-bind="textInput: key, valueUpdate: 'afterkeydown'"/>
          <!-- /ko -->
          <input type="text" class="config-property-input-mini" style="width: 182px;" placeholder="${ _('Value') }" data-bind="textInput: value, valueUpdate: 'afterkeydown'"/>
          <span class="add-on move-widget muted" data-bind="visible: $parent.values().length > 1"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div class="config-property-add-value" style="margin-top: 5px; float: left">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
    <div class="clearfix"></div>
  </script>

  <script type="text/javascript">
    (function () {

      function KeyValueListInputViewModel(params) {
        var self = this;

        self.values = ko.observableArray(params.values().filter(function (value) {
          return value.key && value.key() && value.value && value.value();
        }));

        self.values.subscribe(function (newValues) {
          params.values(self.values().filter(function (value) {
            return value.key && value.key() && value.value && value.value();
          }))
        });

        self.options = typeof params.property.options !== 'undefined' ? $.map(params.property.options(), function (option) {
          return { value: option }
        }) : [];

        if (self.options.length > 0) {
          self.values().forEach(function (value) {
            if (self.options.indexOf(value.key()) === -1) {
              self.options.push({ value: value.key() });
            }
          })
        }
        params.visibleObservable.subscribe(function (newValue) {
          if (!newValue) {
            self.values($.grep(self.values(), function (value) {
              return value.key() && value.value();
            }))
          }
        });

        this._editorSettingsUpdate = huePubSub.subscribe('editor.settings.update', function (data) {
          var setting;
          for (var i = 0; i < self.values.length; i++) {
            if (self.values().key == data.key) {
              setting = self.values()[i];
              break;
            }
          }
          if (!setting) {
            self.addValue();
            setting = self.values()[self.values().length - 1];
          }
          setting.key(data.key);
          setting.value(data.value);
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

      KeyValueListInputViewModel.prototype.dispose = function () {
        this._editorSettingsUpdate.remove();
      };

      ko.components.register('key-value-list-input', {
        viewModel: KeyValueListInputViewModel,
        template: { element: 'key-value-list-input-template' }
      });
    })();
  </script>

  <script type="text/html" id="name-value-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: values().length" class="unstyled">
      <li style="clear:both;">
        <!-- ko if: $parent.options.length > 0 -->
        <div class="selectize-wrapper" style="min-width: 200px;">
          <select placeholder="${ _('Name') }" data-bind="selectize: $parent.options, value: name, options: $parent.options, optionsText: 'value', optionsValue: 'value'"></select>
        </div>
        <!-- /ko -->
        <div class="input-append" style="margin-bottom: 4px">
          <!-- ko if: $parent.options.length === 0 -->
          <input type="text" class="config-property-input-small" style="width: 182px; margin-right: 4px;" placeholder="${ _('Name') }" data-bind="textInput: name, valueUpdate: 'afterkeydown'"/>
          <!-- /ko -->
          <input type="text" class="config-property-input-small" style="width: 182px;" placeholder="${ _('Value') }" data-bind="textInput: value, valueUpdate: 'afterkeydown'"/>
          <span class="add-on move-widget muted" data-bind="visible: $parent.values().length > 1"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div class="config-property-add-value" style="margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      function NameValueListInputViewModel(params) {
        var self = this;
        self.values = params.values;
        self.options = typeof params.property.options !== 'undefined' ? $.map(params.property.options(), function (option) {
          return { value: option }
        }) : [];

        if (self.options.length > 0) {
          self.values().forEach(function (value) {
            if (self.options.indexOf(value.name()) === -1) {
              self.options.push({ value: value.name() });
            }
          })
        }
        params.visibleObservable.subscribe(function (newValue) {
          if (!newValue) {
            self.values($.grep(self.values(), function (value) {
              return value.name() && value.value();
            }))
          }
        });
      }

      NameValueListInputViewModel.prototype.addValue = function () {
        var self = this;
        var newValue = {
          name: ko.observable(''),
          value: ko.observable('')
        };
        self.values.push(newValue);
      };

      NameValueListInputViewModel.prototype.removeValue = function (valueToRemove) {
        var self = this;
        self.values.remove(valueToRemove);
      };

      ko.components.register('name-value-list-input', {
        viewModel: NameValueListInputViewModel,
        template: { element: 'name-value-list-input-template' }
      });
    })();
  </script>

  <script type="text/html" id="function-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: values().length" class="unstyled">
      <li>
        <div class="input-append" style="margin-bottom: 4px">
          <input type="text" class="config-property-input-small" style="width: 182px; margin-right: 4px;" placeholder="${ _('Name, e.g. foo') }" data-bind="textInput: name, valueUpdate: 'afterkeydown'"/>
          <input type="text" class="config-property-input-small" style="width: 150px" placeholder="${ _('Class, e.g. org.hue.Bar') }" data-bind="textInput: class_name, valueUpdate: 'afterkeydown'"/>
          <span class="add-on move-widget muted" data-bind="visible: $parent.values().length > 1"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div class="config-property-add-value" style="margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
  </script>

  <script type="text/javascript">
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
    })();
  </script>

  <script type="text/html" id="hdfs-file-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: values().length" class="unstyled">
      <li>
        <div class="input-append" style="margin-bottom: 4px">
          <input type="text" class="filechooser-input input-xxlarge" data-bind="value: path, valueUpdate:'afterkeydown', filechooser: { value: path, isAddon: true }, filechooserOptions: { skipInitialPathIfEmpty: true }" placeholder="${ _('Path to the file, e.g. hdfs://localhost:8020/user/hue/file.hue') }"/>
          <span class="add-on move-widget muted" data-bind="visible: $parent.values().length > 1"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div class="config-property-add-value" style="margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var identifyType = function (path) {
        switch (path.substr(path.lastIndexOf('.') + 1).toLowerCase()) {
          case 'jar':
            return 'jar';
          case 'zip':
          case 'tar':
          case 'rar':
          case 'bz2':
          case 'gz':
          case 'tgz':
            return 'archive';
        }
        return 'file';
      };

      function HdfsFileListInputViewModel(params) {
        var self = this;
        self.values = params.values;
        $.each(self.values(), function (idx, value) {
          value.path.subscribe(function (newPath) {
            value.type(identifyType(newPath));
          });
        });
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
        });
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
    })();
  </script>

  <script type="text/html" id="csv-list-input-template">
    <ul data-bind="sortable: { data: values, options: { axis: 'y', containment: 'parent', handle: '.move-widget' }}, visible: values().length" class="unstyled">
      <li style="margin-bottom: 4px">
        <div class="input-append">
          <!-- ko ifnot: $parent.inputTemplate -->
          <input type="text" data-bind="textInput: value, valueUpdate: 'afterkeydown', attr: { placeholder: $parent.placeholder }"/>
          <!-- /ko -->
          <!-- ko template: { if: $parent.inputTemplate, name: $parent.inputTemplate } --><!-- /ko -->
          <span class="add-on move-widget muted" data-bind="visible: $parent.values().length > 1"><i class="fa fa-arrows"></i></span>
          <a class="add-on muted" href="javascript: void(0);" data-bind="click: function(){ $parent.removeValue($data); }"><i class="fa fa-minus"></i></a>
        </div>
      </li>
    </ul>
    <div class="config-property-add-value" style="margin-top: 5px;">
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
  </script>

  <script type="text/javascript">
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
    })();
  </script>
</%def>
