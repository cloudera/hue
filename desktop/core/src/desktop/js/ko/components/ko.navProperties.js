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
import ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <script type="text/html" id="nav-property-edit-popover-content">
    <div class="hue-nav-property-edit-content">
      <a href="javascript: void(0);" class="close-popover"><i class="fa fa-times"></i></a>
      <div class="control-group" data-bind="css: { 'error': keyInvalid }">
        <label class="control-label">${I18n('Key')}</label>
        <div class="controls">
          <input type="text" placeholder="${I18n('Key')}" data-bind="textInput: key">
        </div>
      </div>
      <div class="control-group" data-bind="css: { 'error': valueInvalid }">
        <label class="control-label">${I18n('Value')}</label>
        <div class="controls">
          <input type="text" placeholder="${I18n('Value')}" data-bind="textInput: value">
        </div>
      </div>
    </div>
  </script>

  <!-- ko if: loading -->
  <div class="hue-nav-properties"><div data-bind="hueSpinner: { spin: loading, inline: true }"></div></div>
  <!-- /ko -->
  <!-- ko ifnot: loading -->
  <!-- ko ifnot: editMode -->

  <!-- ko ifnot: window.HAS_READ_ONLY_CATALOG -->
  <div class="hue-nav-properties" data-bind="click: startEdit, visibleOnHover: { selector: '.editable-inline-action' }">
    <!-- ko if: !properties().length -->
    <div class="hue-nav-properties-empty">${I18n('Add properties...')}</div>
    <!-- /ko -->
    <!-- ko foreach: properties -->
    <div class="hue-nav-property"><div class="hue-nav-property-key" data-bind="text: key, attr: { 'title': key }"></div><div class="hue-nav-property-value" data-bind="text: value, attr: { 'title': value }"></div></div>
    <!-- /ko -->
    <div class="editable-inline-action" title="${I18n(
      'Edit'
    )}"><a href="javascript: void(0);" data-bind="click: startEdit"><i class="fa fa-pencil"></i></a></div>
  </div>
  <!-- /ko -->

  <!-- ko if: window.HAS_READ_ONLY_CATALOG && properties().length -->
  <div class="hue-nav-properties">
    <!-- ko foreach: properties -->
    <div class="hue-nav-property"><div class="hue-nav-property-key" data-bind="text: key, attr: { 'title': key }"></div><div class="hue-nav-property-value" data-bind="text: value, attr: { 'title': value }"></div></div>
    <!-- /ko -->
  </div>
  <!-- /ko -->

  <!-- /ko -->
  <!-- ko if: editMode -->
  <div class="hue-nav-properties hue-nav-properties-edit">
    <!-- ko foreach: editProperties -->
    <div class="hue-nav-property hue-nav-property-edit" data-bind="css: { 'hue-nav-property-invalid': invalid }, templatePopover: { trigger: 'click', placement: 'bottom', visible: editPropertyVisible, contentTemplate: 'nav-property-edit-popover-content' }">
      <div class="hue-nav-property-key" data-bind="text: key, attr: { 'title': key }"></div><div class="hue-nav-property-value" data-bind="text: value, attr: { 'title': value }"></div>
      <div class="hue-nav-property-remove"><a href="javascript: void(0);" title="${I18n(
        'Remove'
      )}" data-bind="click: function (entry) { $parent.removeProperty(entry); }"><i class="fa fa-times"></i></a></div>
    </div>
    <!-- /ko -->
    <div class="hue-nav-property-add"><a href="javascript: void(0);" title="${I18n(
      'Add'
    )}" data-bind="click: addProperty"><i class="fa fa-plus"></i></a></div>
    <div class="hue-nav-properties-edit-actions">
      <a href="javascript: void(0);" title="${I18n(
        'Save'
      )}" data-bind="click: saveEdit"><i class="fa fa-check"></i></a>
      <a href="javascript: void(0);" title="${I18n(
        'Cancel'
      )}" data-bind="click: cancelEdit"><i class="fa fa-close"></i></a>
    </div>
  </div>
  <!-- /ko -->
  <!-- /ko -->
`;

class NavProperty {
  constructor(key, value, isNew) {
    const self = this;
    self.key = ko.observable(key);
    self.keyEdited = ko.observable(false);

    self.value = ko.observable(value);
    self.valueEdited = ko.observable(false);

    self.editPropertyVisible = ko.observable(isNew);

    const keySub = self.key.subscribe(() => {
      keySub.dispose();
      self.keyEdited(true);
    });

    const valueSub = self.value.subscribe(() => {
      valueSub.dispose();
      self.valueEdited(true);
    });

    const editSub = self.editPropertyVisible.subscribe(() => {
      editSub.dispose();
      keySub.dispose();
      valueSub.dispose();
      self.keyEdited(true);
      self.valueEdited(true);
    });

    self.keyInvalid = ko.pureComputed(() => {
      return self.keyEdited() && !self.key();
    });

    self.valueInvalid = ko.pureComputed(() => {
      return self.valueEdited() && !self.value();
    });

    self.invalid = ko.pureComputed(() => {
      return (
        self.keyInvalid() ||
        self.valueInvalid() ||
        (!self.editPropertyVisible() && !self.key() && !self.value())
      );
    });
  }
}

class NavProperties {
  /**
   * @param {object} params
   * @param {DataCatalogEntry} [params.catalogEntry]
   *
   * @constructor
   */
  constructor(params, element) {
    const self = this;

    self.element = element;
    self.hasErrors = ko.observable(false);
    self.loading = ko.observable(true);
    self.properties = ko.observableArray();
    self.editProperties = ko.observableArray();

    self.catalogEntry = params.catalogEntry;
    self.editMode = ko.observable(false);

    self.loadProperties();

    self.refreshSub = huePubSub.subscribe('data.catalog.entry.refreshed', details => {
      if (details.entry === self.catalogEntry) {
        self.loadProperties();
      }
    });
  }

  startEdit() {
    if (window.HAS_READ_ONLY_CATALOG) {
      return;
    }
    const self = this;
    const editProperties = [];
    self.properties().forEach(property => {
      editProperties.push(new NavProperty(property.key(), property.value()));
    });
    self.editProperties(editProperties);
    self.editMode(true);

    $(document).on('click.navProperties', event => {
      if (
        $.contains(document, event.target) &&
        !$.contains(self.element, event.target) &&
        !self.editProperties().some(prop => {
          return prop.editPropertyVisible();
        })
      ) {
        self.saveEdit();
      }
    });
  }

  cancelEdit() {
    const self = this;
    $(document).off('click.navProperties');
    self.editMode(false);
  }

  saveEdit() {
    const self = this;

    const someInvalid = self.editProperties().some(property => {
      return !property.key() || !property.value();
    });

    if (someInvalid) {
      return;
    }

    $(document).off('click.navProperties');
    self.editMode(false);
    if (ko.mapping.toJSON(self.editProperties()) !== ko.mapping.toJSON(self.properties())) {
      self.loading(true);
      self.catalogEntry
        .getNavigatorMeta()
        .done(navigatorMeta => {
          const keysAfterEdit = {};
          const modifiedCustomMetadata = {};

          if (!navigatorMeta.properties) {
            navigatorMeta.properties = {};
          }

          self.editProperties().forEach(property => {
            if (navigatorMeta.properties[property.key()] !== property.value()) {
              modifiedCustomMetadata[property.key()] = property.value();
            }
            keysAfterEdit[property.key()] = true;
          });

          const deletedCustomMetadataKeys = [];
          self.properties().forEach(property => {
            if (!keysAfterEdit[property.key()]) {
              deletedCustomMetadataKeys.push(property.key());
            }
          });

          self.catalogEntry
            .updateNavigatorCustomMetadata(modifiedCustomMetadata, deletedCustomMetadataKeys)
            .always(() => {
              self.loadProperties();
            });
        })
        .fail(() => {
          self.loadProperties();
        });
    }
  }

  removeProperty(property) {
    const self = this;
    self.editProperties.remove(property);
  }

  addProperty() {
    const self = this;
    const newProperty = new NavProperty('', '', true);
    newProperty.editPropertyVisible(true);
    self.editProperties.push(newProperty);
  }

  dispose() {
    const self = this;
    self.refreshSub.remove();
  }

  loadProperties() {
    const self = this;
    self.loading(true);
    self.hasErrors(false);

    ko.unwrap(self.catalogEntry)
      .getNavigatorMeta()
      .done(navigatorMeta => {
        const newProps = [];
        if (navigatorMeta.properties) {
          Object.keys(navigatorMeta.properties).forEach(key => {
            if (!key.startsWith('__cloudera_internal')) {
              newProps.push(new NavProperty(key, navigatorMeta.properties[key]));
            }
          });
          newProps.sort((a, b) => {
            return a.key().localeCompare(b.key());
          });
        }
        self.properties(newProps);
      })
      .fail(() => {
        self.hasErrors(true);
      })
      .always(() => {
        self.loading(false);
      });
  }
}

componentUtils.registerComponent(
  'nav-properties',
  {
    createViewModel: function(params, componentInfo) {
      return new NavProperties(params, componentInfo.element);
    }
  },
  TEMPLATE
);
