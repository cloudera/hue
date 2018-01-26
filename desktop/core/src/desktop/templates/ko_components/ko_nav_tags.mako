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

<%def name="navTags()">
  <link href="${ static('desktop/ext/css/selectize.css') }" rel="stylesheet">

  <script type="text/html" id="nav-tags-template">
     <!-- ko if: loading -->
     <div style="width: 100%; height: 20px; left: 6px; top: 8px; position: relative;" data-bind="hueSpinner: { spin: loading }"></div>
     <!-- /ko -->
     <div style="width: 100%" data-bind="ifnot: loading">
       <textarea style="width: 100%" data-bind="tagEditor: {
          placeholder: '${_ko('No tags')}',
          readOnly: '${ not user.has_hue_permission(action="write", app="metadata") }' === 'True',
          hasErrors: hasErrors,
          errorMessage: '${_ko("Tags could not be loaded.")}',
          setTags: currentTags,
          onSave: saveTags.bind($data),
          validRegExp: '^[a-zA-z0-9_\-]{1,50}$',
          invalidMessage: '${_ko("Tags can only contain 1 to 50 alphanumeric characters, '_' or '-'.")}',
          load: getSelectizeTags
        }"></textarea>
       <div class="selectize-error" style="display: none;"><i class="fa fa-exclamation-triangle"></i> <span class="message"></span></div>
     </div>
  </script>

  <script type="text/javascript">
    (function () {
      /**
       * @param {object} params
       * @param {DataCatalogEntry} [params.catalogEntry]
       *
       * @constructor
       */
      function NavTags(params) {
        var self = this;

        self.hasErrors = ko.observable(false);
        self.loading = ko.observable(true);

        self.currentTags = ko.observableArray();
        self.allTags = ko.observableArray();

        self.catalogEntry = params.catalogEntry;

        self.getSelectizeTags = function (query, callback) {
          callback($.map(self.allTags(), function (tag) { return { value: tag, text: tag }}));
        };

        self.loadTags();
      }

      NavTags.prototype.loadTags = function () {
        var self = this;
        self.loading(true);
        self.hasErrors(false);

        var currentTagsPromise = self.catalogEntry.getNavigatorMeta().done(function (navigatorMeta) {
          self.currentTags((navigatorMeta && navigatorMeta.tags) || []);
        }).fail(function () {
          self.hasErrors(true);
        });

        var allTagsPromise = DataCatalog.getAllNavigatorTags({ silenceErrors: true }).done(function (tagList) {
          self.allTags(Object.keys(tagList));
        }).fail(function () {
          self.allTags([]);
        });

        $.when(currentTagsPromise, allTagsPromise).always(function () {
          self.loading(false);
        });
      };

      NavTags.prototype.saveTags = function (value) {
        var self = this;
        var newTags = value.length > 0 ? value.split(',') : [];
        var tagsToRemove = [];
        var tagsToAdd = [];

        var tagIndex = {};
        self.currentTags().forEach(function (tag) {
          tagIndex[tag] = false;
        });
        newTags.forEach(function (newTag) {
          if (typeof tagIndex[newTag] !== 'undefined') {
            tagIndex[newTag] = true;
          } else {
            tagsToAdd.push(newTag);
          }
        });
        Object.keys(tagIndex).forEach(function (oldTag) {
          if (!tagIndex[oldTag]) {
            tagsToRemove.push(oldTag);
          }
        });

        self.loading(true);
        self.hasErrors(false);

        var addTagsPromise = tagsToAdd.length > 0 ? self.catalogEntry.addNavigatorTags(tagsToAdd) : $.Deferred().resolve().promise();

        var deleteTagsPromise = tagsToRemove.length > 0 ? self.catalogEntry.deleteNavigatorTags(tagsToRemove) : $.Deferred().resolve().promise();

        addTagsPromise.fail(function (error) {
          hueUtils.logError(error);
          $(document).trigger('error', '${ _("Could not add tags, see the server log for details.") }');
        });

        deleteTagsPromise.fail(function (error) {
          hueUtils.logError(error);
          $(document).trigger('error', '${ _("Could not remove tags, see the server log for details.") }');
        });

        $.when(addTagsPromise, deleteTagsPromise).done(function () {
          if (tagsToAdd.length || tagsToRemove.length) {
            DataCatalog.updateAllNavigatorTags(tagsToAdd, tagsToRemove);
            self.catalogEntry.save();
          }
          self.loading(false);
          self.loadTags();
        });
      };

      ko.components.register('nav-tags', {
        viewModel: NavTags,
        template: { element: 'nav-tags-template' }
      });
    })();
  </script>
</%def>
