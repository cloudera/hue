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
from desktop.conf import USE_NEW_SIDE_PANELS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
from django.utils.translation import ugettext as _
from metadata.conf import has_navigator
%>

<%def name="nav_tags()">
  <link href="${ static('desktop/ext/css/selectize.css') }" rel="stylesheet">

  <script type="text/html" id="nav-tags-template">
     <!-- ko if: loading -->
     <div style="width: 100%; height: 20px; left: 6px; top: 8px; position: relative;" data-bind="hueSpinner: { spin: loading }"></div>
     <!-- /ko -->
     <div style="width: 100%" data-bind="ifnot: loading">
       <textarea style="width: 100%" data-bind="tagEditor: {
          placeholder: '${_ko('No tags found...')}',
          setTags: currentTags,
          onSave: onSave,
          load: loadTags
        }"></textarea>
     </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require([
          'knockout',
          'desktop/js/apiHelper',
          'selectize'
        ], factory);
      } else {
        factory(ko, ApiHelper);
      }
    }(function (ko, ApiHelper) {

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
        self.loading = ko.observable(true);
        self.navEntity = ko.observable();
        self.currentTags = ko.observableArray();
        self.allTags = ko.observableArray();

        apiHelper.fetchNavEntity({
          sourceType: ko.unwrap(params.sourceType),
          identifierChain: identifierChain,
          defaultDatabase: ko.unwrap(params.defaultDatabase),
          silenceErrors: true,
          noCache: true,
          successCallback: function (data) {
            self.identity = data.entity.identity;
            self.currentTags(data.entity.tags);
            self.loading(false);
          },
          errorCallback: function () {
            self.loading(false);
          }
        });

        var fetchAllTags = function () {
          var fetchDeferral = $.Deferred();
          apiHelper.listNavTags({
            successCallback: function (data) {
              self.allTags(Object.keys(data.tags));
              fetchDeferral.resolve();
            },
            silenceErrors: true,
            errorCallback: fetchDeferral.reject
          });
          return fetchDeferral.promise();
        };
        fetchAllTags();

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

          var deferrals = [];
          if (tagsToAdd.length > 0) {
            deferrals.push(apiHelper.addNavTags(self.identity, tagsToAdd));
          }
          if (tagsToRemove.length > 0) {
            deferrals.push(apiHelper.deleteNavTags(self.identity, tagsToRemove));
          }
          self.currentTags(newTags);
          deferrals.push(fetchAllTags());

          var doneLoading = function () {
            self.loading(false);
          };

          $.when.apply($, deferrals).then(doneLoading, doneLoading);
        };
      }

      ko.components.register('nav-tags', {
        viewModel: NavTags,
        template: { element: 'nav-tags-template' }
      });
    }));
  </script>
</%def>
