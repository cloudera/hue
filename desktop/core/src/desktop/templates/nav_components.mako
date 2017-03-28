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

<%def name="nav_tags(readOnly=False)">
  <link href="${ static('desktop/ext/css/selectize.css') }" rel="stylesheet">

  <script type="text/html" id="nav-tags-template">
     <!-- ko if: loading -->
     <div style="width: 100%; height: 20px; left: 6px; top: 8px; position: relative;" data-bind="hueSpinner: { spin: loading }"></div>
     <!-- /ko -->
     <div style="width: 100%" data-bind="ifnot: loading">
       <textarea style="width: 100%" data-bind="tagEditor: {
          placeholder: '${_ko('No tags')}',
          readOnly: '${ readOnly }' === 'True',
          hasErrors: hasErrors,
          errorMessage: '${_ko("Tags could not be loaded.")}',
          setTags: currentTags,
          onSave: onSave,
          validRegExp: '^[a-zA-z0-9_\-]{1,50}$',
          invalidMessage: '${_ko("Tags can only contain 1 to 50 alphanumeric characters, '_' or '-'.")}',
          load: loadTags
        }"></textarea>
       <div class="selectize-error" style="display: none;"><i class="fa fa-exclamation-triangle"></i> <span class="message"></span></div>
     </div>
  </script>

  <script type="text/javascript">
    (function () {
      /**
       * @param {object} params
       * @param {String} sourceType
       * @param {String} defaultDatabase
       * @param {object[]} [params.identifierChain]
       * @param {String} [params.database]
       * @param {String} [params.table]
       * @param {String} [params.column]
       *
       * @constructor
       */
      function NavTags(params) {
        var self = this;
        var apiHelper = ApiHelper.getInstance();

        var identifierChain = ko.unwrap(params.identifierChain);
        if (! params.identifierChain) {
          identifierChain = [];
          if (params.database) {
            identifierChain.push({ name: ko.unwrap(params.database) });
          }
          if (params.table) {
            identifierChain.push({ name: ko.unwrap(params.table) });
          }
          if (params.column) {
            identifierChain.push({ name: ko.unwrap(params.column) });
          }
        }

        self.identity;
        self.hasErrors = ko.observable(false);
        self.loading = ko.observable(true);
        self.navEntity = ko.observable();
        self.currentTags = ko.observableArray();
        self.allTags = ko.observableArray();

        var fetchNavEntity = function () {
          var fetchDeferral = $.Deferred();
          apiHelper.fetchNavEntity({
            sourceType: ko.unwrap(params.sourceType),
            identifierChain: identifierChain,
            isView: typeof params.fetchedData !== 'undefined' && typeof params.fetchedData() !== 'undefined' && params.fetchedData().is_view,
            defaultDatabase: ko.unwrap(params.defaultDatabase),
            silenceErrors: true,
            noCache: true,
            successCallback: function (data) {
              fetchDeferral.resolve(data.entity);
            },
            errorCallback: function (error) {
              fetchDeferral.reject()
            }
          });
          return fetchDeferral;
        };


        var fetchAllTags = function () {
          var fetchDeferral = $.Deferred();
          apiHelper.listNavTags({
            successCallback: function (data) {
              fetchDeferral.resolve(Object.keys(data.tags));
            },
            silenceErrors: true,
            errorCallback: function (error) {
              hueUtils.logError(error);
              fetchDeferral.reject()
            }
          });
          return fetchDeferral;
        };

        self.loading(true);
        $.when(fetchNavEntity(), fetchAllTags()).done(function (entity, allTags) {
          self.identity = entity.identity;
          self.currentTags(entity.tags);
          self.allTags(allTags);
        }).fail(function () {
          self.hasErrors(true);
        }).always(function () {
          self.loading(false);
        });

        self.loadTags = function (query, callback) {
          callback($.map(self.allTags(), function (tag) { return { value: tag, text: tag }}));
        };

        self.onSave = function (value) {
          self.loading(true);
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
            if (! tagIndex[oldTag]) {
              tagsToRemove.push(oldTag);
            }
          });

          self.loading(true);
          self.hasErrors(false);
          var addTagsDeferral = $.Deferred();
          if (tagsToAdd.length > 0) {
            if (typeof self.identity === 'undefined' || self.identity === null) {
              addTagsDeferral.reject('${ _("Can\'t add tags without an entity.") }');
            } else {
              addTagsDeferral = apiHelper.addNavTags(self.identity, tagsToAdd);
            }
          } else {
            addTagsDeferral.resolve();
          }

          var removeTagsDeferral = $.Deferred();
          if (tagsToRemove.length > 0) {
            if (typeof self.identity === 'undefined' || self.identity === null) {
              removeTagsDeferral.reject('Can\'t remove tags without an entity');
            } else {
              removeTagsDeferral = apiHelper.deleteNavTags(self.identity, tagsToRemove);
            }
          } else {
            removeTagsDeferral.resolve();
          }

          var fetchAllTagsDeferral = $.Deferred();

          $.when(addTagsDeferral, removeTagsDeferral).done(function () {
            self.currentTags(newTags);
            fetchAllTags().done(function (tags) {
              self.allTags(tags);
              fetchAllTagsDeferral.resolve();
            }).fail(fetchAllTagsDeferral.reject);
          }).fail(fetchAllTagsDeferral.reject);

          $.when(addTagsDeferral, removeTagsDeferral, fetchAllTagsDeferral).fail(function (addTagsError, removeTagsError) {
            if (typeof addTagsError !== 'undefined') {
              hueUtils.logError(addTagsError);
              $(document).trigger('error', '${ _("Could not add tags, see the server log for details.") }');
            }
            if (typeof removeTagsError !== 'undefined') {
              hueUtils.logError(removeTagsError);
              $(document).trigger('error', '${ _("Could not remove tags, see the server log for details.") }');
            }
            self.hasErrors(true);
          }).always(function () {
            self.loading(false);
          });
        };
      }

      ko.components.register('nav-tags', {
        viewModel: NavTags,
        template: { element: 'nav-tags-template' }
      });
    })();
  </script>
</%def>
