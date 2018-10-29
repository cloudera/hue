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
from desktop.views import _ko
from django.utils.translation import ugettext as _
%>

<%def name="navProperties()">

  <script type="text/html" id="nav-property-edit-popover-content">
    <div class="hue-nav-property-edit-content">
      <a href="javascript: void(0);" class="close-popover"><i class="fa fa-times"></i></a>
      <div class="control-group" data-bind="css: { 'error': keyInvalid }">
        <label class="control-label">${ _("Key") }</label>
        <div class="controls">
          <input type="text" placeholder="${ _("Key") }" data-bind="textInput: key">
        </div>
      </div>
      <div class="control-group" data-bind="css: { 'error': valueInvalid }">
        <label class="control-label">${ _("Value") }</label>
        <div class="controls">
          <input type="text" placeholder="${ _("Value") }" data-bind="textInput: value">
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="nav-properties-template">
     <!-- ko if: loading -->
     <div class="hue-nav-properties"><div data-bind="hueSpinner: { spin: loading, inline: true }"></div></div>
     <!-- /ko -->
     <!-- ko ifnot: loading -->
     <!-- ko ifnot: editMode -->

     <div class="hue-nav-properties" data-bind="click: startEdit, visibleOnHover: { selector: '.editable-inline-action' }">
       <!-- ko ifnot: properties().length -->
       <div class="hue-nav-properties-empty">${ _("Add properties...") }</div>
       <!-- /ko -->
       <!-- ko foreach: properties -->
       <div class="hue-nav-property"><div class="hue-nav-property-key" data-bind="text: key, attr: { 'title': key }"></div><div class="hue-nav-property-value" data-bind="text: value, attr: { 'title': value }"></div></div>
       <!-- /ko -->
       <div class="editable-inline-action" title="${ _("Edit") }"><a href="javascript: void(0);" data-bind="click: startEdit"><i class="fa fa-pencil"></i></a></div>
     </div>
     <!-- /ko -->
     <!-- ko if: editMode -->
     <div class="hue-nav-properties hue-nav-properties-edit">
       <!-- ko foreach: editProperties -->
       <div class="hue-nav-property hue-nav-property-edit" data-bind="css: { 'hue-nav-property-invalid': invalid }, templatePopover: { trigger: 'click', placement: 'bottom', visible: editPropertyVisible, contentTemplate: 'nav-property-edit-popover-content' }">
         <div class="hue-nav-property-key" data-bind="text: key, attr: { 'title': key }"></div><div class="hue-nav-property-value" data-bind="text: value, attr: { 'title': value }"></div>
         <div class="hue-nav-property-remove"><a href="javascript: void(0);" title="${ _("Remove") }" data-bind="click: function (entry) { $parent.removeProperty(entry); }"><i class="fa fa-times"></i></a></div>
       </div>
       <!-- /ko -->
       <div class="hue-nav-property-add"><a href="javascript: void(0);" title="${ _("Add") }" data-bind="click: addProperty"><i class="fa fa-plus"></i></a></div>
       <div class="hue-nav-properties-edit-actions">
         <a href="javascript: void(0);" title="${ _("Save") }" data-bind="click: saveEdit"><i class="fa fa-check"></i></a>
         <a href="javascript: void(0);" title="${ _("Cancel") }" data-bind="click: cancelEdit"><i class="fa fa-close"></i></a>
       </div>
     </div>
     <!-- /ko -->
     <!-- /ko -->
  </script>

  <script type="text/javascript">
    (function () {

      function NavProperty(key, value, isNew) {
        var self = this;
        self.key = ko.observable(key);
        self.keyEdited = ko.observable(false);

        self.value = ko.observable(value);
        self.valueEdited = ko.observable(false);

        self.editPropertyVisible = ko.observable(isNew);

        var keySub = self.key.subscribe(function () {
          keySub.dispose();
          self.keyEdited(true);
        });

        var valueSub = self.value.subscribe(function () {
          valueSub.dispose();
          self.valueEdited(true);
        });

        var editSub = self.editPropertyVisible.subscribe(function () {
          editSub.dispose();
          keySub.dispose();
          valueSub.dispose();
          self.keyEdited(true);
          self.valueEdited(true);
        });

        self.keyInvalid = ko.pureComputed(function () {
          return self.keyEdited() && !self.key();
        });

        self.valueInvalid = ko.pureComputed(function () {
          return self.valueEdited() && !self.value();
        });

        self.invalid = ko.pureComputed(function () {
          return self.keyInvalid() || self.valueInvalid() || (!self.editPropertyVisible() && !self.key() && !self.value());
        })
      }

      /**
       * @param {object} params
       * @param {DataCatalogEntry} [params.catalogEntry]
       *
       * @constructor
       */
      function NavProperties(params, element) {
        var self = this;

        self.element = element;
        self.hasErrors = ko.observable(false);
        self.loading = ko.observable(true);
        self.properties = ko.observableArray();
        self.editProperties = ko.observableArray();

        self.catalogEntry = params.catalogEntry;
        self.editMode = ko.observable(false);

        self.loadProperties();

        self.refreshSub = huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
          if (details.entry === self.catalogEntry) {
            self.loadProperties();
          }
        });
      }

      NavProperties.prototype.startEdit = function () {
        var self = this;
        var editProperties = [];
        self.properties().forEach(function (property) {
          editProperties.push(new NavProperty(property.key(), property.value()));
        });
        self.editProperties(editProperties);
        self.editMode(true);

        $(document).on('click.navProperties', function (event) {
          if ($.contains(document, event.target) && !$.contains(self.element, event.target) &&
              !self.editProperties().some(function (prop) { return prop.editPropertyVisible() })) {
            self.saveEdit();
          }
        });
      };

      NavProperties.prototype.cancelEdit = function () {
        var self = this;
        $(document).off('click.navProperties');
        self.editMode(false);
      };

      NavProperties.prototype.saveEdit = function () {
        var self = this;

        var someInvalid = self.editProperties().some(function (property) {
          return !property.key() || !property.value();
        });

        if (someInvalid) {
          return;
        }

        $(document).off('click.navProperties');
        self.editMode(false);
        if (ko.mapping.toJSON(self.editProperties()) !== ko.mapping.toJSON(self.properties())) {
          self.loading(true);
          self.catalogEntry.getNavigatorMeta().done(function (navigatorMeta) {
            var keysAfterEdit = {};
            var modifiedCustomMetadata = {};

            if (!navigatorMeta.properties) {
              navigatorMeta.properties = {};
            }

            self.editProperties().forEach(function (property) {
              if (navigatorMeta.properties[property.key()] !== property.value()) {
                modifiedCustomMetadata[property.key()] = property.value();
              }
              keysAfterEdit[property.key()] = true;
            });

            var deletedCustomMetadataKeys = [];
            self.properties().forEach(function (property) {
              if (!keysAfterEdit[property.key()]) {
                deletedCustomMetadataKeys.push(property.key());
              }
            });

            self.catalogEntry.updateNavigatorCustomMetadata(modifiedCustomMetadata, deletedCustomMetadataKeys).always(function () {
              self.loadProperties();
            });
          }).fail(function () {
            self.loadProperties();
          });
        }
      };

      NavProperties.prototype.removeProperty = function (property) {
        var self = this;
        self.editProperties.remove(property);
      };

      NavProperties.prototype.addProperty = function () {
        var self = this;
        var newProperty = new NavProperty('', '', true);
        newProperty.editPropertyVisible(true);
        self.editProperties.push(newProperty);
      };

      NavProperties.prototype.dispose = function () {
        var self = this;
        self.refreshSub.remove();
      };

      NavProperties.prototype.loadProperties = function () {
        var self = this;
        self.loading(true);
        self.hasErrors(false);

        ko.unwrap(self.catalogEntry).getNavigatorMeta().done(function (navigatorMeta) {
          var newProps = [];
          if (navigatorMeta.properties) {
            Object.keys(navigatorMeta.properties).forEach(function (key) {
              if (!key.startsWith('__cloudera_internal')) {
                newProps.push(new NavProperty(key, navigatorMeta.properties[key]));
              }
            });
            newProps.sort(function (a, b) {
              return a.key().localeCompare(b.key());
            })
          }
          self.properties(newProps);
        }).fail(function () {
          self.hasErrors(true);
        }).always(function () {
          self.loading(false);
        });
      };

      ko.components.register('nav-properties', {
        viewModel: {
          createViewModel: function(params, componentInfo) {
            return new NavProperties(params, componentInfo.element);
          }
        },
        template: { element: 'nav-properties-template' }
      });
    })();
  </script>
</%def>
