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
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <!-- ko if: loading -->
  <div style="width: 100%; height: 20px; left: 6px; top: 8px; position: relative;" data-bind="hueSpinner: { spin: loading }"></div>
  <!-- /ko -->
  <!-- ko if: !loading() && (!readOnly || readOnly && currentTags().length) -->
  <div class="hue-tags" style="width: 100%" data-bind="ifnot: loading, css: { 'read-only-tags': readOnly }">
   <textarea style="width: 100%" data-bind="tagEditor: {
      emptyPlaceholder: '${I18n('Add tags...')}',
      readOnly: readOnly,
      hasErrors: hasErrors,
      errorMessage: '${I18n('Tags could not be loaded.')}',
      setTags: currentTags,
      overflowEllipsis: overflowEllipsis,
      onSave: saveTags.bind($data),
      validRegExp: '^[a-zA-z0-9_\-]{1,50}$',
      invalidMessage: '${I18n('Tags can only contain 1 to 50 alphanumeric characters, _ or -.')}',
      load: getSelectizeTags
    }"></textarea>
   <div class="selectize-error" style="display: none;"><i class="fa fa-exclamation-triangle"></i> <span class="message"></span></div>
  </div>
  <!-- /ko -->
`;

class NavTags {
  /**
   * @param {object} params
   * @param {DataCatalogEntry} [params.catalogEntry]
   *
   * @constructor
   */
  constructor(params) {
    const self = this;

    self.hasErrors = ko.observable(false);
    self.loading = ko.observable(true);

    self.currentTags = ko.observableArray();
    self.allTags = ko.observableArray();

    self.catalogEntry = params.catalogEntry;
    self.overflowEllipsis = params.overflowEllipsis;
    self.readOnly =
      !window.USER_HAS_METADATA_WRITE_PERM || !!params.readOnly || window.HAS_READ_ONLY_CATALOG;

    self.getSelectizeTags = function(query, callback) {
      callback(
        $.map(self.allTags(), tag => {
          return { value: tag, text: tag };
        })
      );
    };

    self.loadTags();

    self.refreshSub = huePubSub.subscribe('data.catalog.entry.refreshed', details => {
      if (details.entry === self.catalogEntry) {
        self.loadTags();
      }
    });
  }

  dispose() {
    const self = this;
    self.refreshSub.remove();
  }

  loadTags() {
    const self = this;
    self.loading(true);
    self.hasErrors(false);

    const currentTagsPromise = ko
      .unwrap(self.catalogEntry)
      .getNavigatorMeta()
      .done(navigatorMeta => {
        self.currentTags((navigatorMeta && navigatorMeta.tags) || []);
      })
      .fail(() => {
        self.hasErrors(true);
      });

    const allTagsPromise = dataCatalog
      .getAllNavigatorTags({ silenceErrors: true })
      .done(tagList => {
        self.allTags(Object.keys(tagList));
      })
      .fail(() => {
        self.allTags([]);
      });

    $.when(currentTagsPromise, allTagsPromise).always(() => {
      self.loading(false);
    });
  }

  saveTags(value) {
    const self = this;
    const newTags = value.length > 0 ? value.split(',') : [];
    const tagsToRemove = [];
    const tagsToAdd = [];

    const tagIndex = {};
    self.currentTags().forEach(tag => {
      tagIndex[tag] = false;
    });
    newTags.forEach(newTag => {
      if (typeof tagIndex[newTag] !== 'undefined') {
        tagIndex[newTag] = true;
      } else {
        tagsToAdd.push(newTag);
      }
    });
    Object.keys(tagIndex).forEach(oldTag => {
      if (!tagIndex[oldTag]) {
        tagsToRemove.push(oldTag);
      }
    });

    self.loading(true);
    self.hasErrors(false);

    const addTagsPromise =
      tagsToAdd.length > 0
        ? ko.unwrap(self.catalogEntry).addNavigatorTags(tagsToAdd)
        : $.Deferred()
            .resolve()
            .promise();

    const deleteTagsPromise =
      tagsToRemove.length > 0
        ? ko.unwrap(self.catalogEntry).deleteNavigatorTags(tagsToRemove)
        : $.Deferred()
            .resolve()
            .promise();

    $.when(addTagsPromise, deleteTagsPromise)
      .done(() => {
        if (tagsToAdd.length || tagsToRemove.length) {
          dataCatalog.updateAllNavigatorTags(tagsToAdd, tagsToRemove);
          ko.unwrap(self.catalogEntry).save();
        }
        self.loadTags();
      })
      .fail(() => {
        self.hasErrors(true);
      })
      .always(() => {
        self.loading(false);
      });
  }
}

componentUtils.registerComponent('nav-tags', NavTags, TEMPLATE);
