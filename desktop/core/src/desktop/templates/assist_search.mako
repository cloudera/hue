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
from desktop.conf import USE_NEW_SIDE_PANELS, VCS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko

from metadata.conf import has_navigator
from metastore.conf import ENABLE_NEW_CREATE_TABLE
from notebook.conf import ENABLE_QUERY_BUILDER
%>

<%def name="assistSearch()">
  <script type="text/html" id="nav-search-autocomp-item">
    <a>
      <div class="nav-autocomplete-item-link">
        <div class="nav-search-result-icon"><i class="fa fa-fw" data-bind="css: icon"></i></div>
        <div class="nav-search-result-text">
          <div class="nav-search-result-header" data-bind="html: label, style: { 'padding-top': description ? 0 : '9px' }"></div>
          <!-- ko if: description -->
          <div class="nav-search-result-description" data-bind="html: description"></div>
          <!-- /ko -->
        </div>
      </div>
    </a>
  </script>

  <script type="text/html" id="nav-search-autocomp-no-match">
    <div class="nav-autocomplete-item-link" style="height: 30px;">
      <div class="nav-autocomplete-empty">${ _('No recent match found') }</div>
    </div>
  </script>

  <script type="text/html" id="nav-search-autocomp-error">
    <div class="nav-autocomplete-item-link nav-autocomplete-error">
      <div class="nav-autocomplete-empty" data-bind="text: typeof message !== 'undefined' ? message : '${ _ko("Error loading suggestions, see log for details.") }'"></div>
    </div>
  </script>

  <script type="text/html" id="assist-panel-navigator-search">
    <!-- ko if: navigatorSearch.navigatorEnabled() -->
      <div class="search-container" data-bind="style: { 'padding-right': tabsEnabled ? null : '20px' }, with: navigatorSearch">
        <input placeholder="${ _('Search...') }" type="text" data-bind="autocomplete: {
          source: navAutocompleteSource,
          itemTemplate: 'nav-search-autocomp-item',
          noMatchTemplate: 'nav-search-autocomp-no-match',
          errorTemplate: 'nav-search-autocomp-error',
          classPrefix: 'nav-',
          showOnFocus: false,
          onEnter: performSearch,
          valueObservable: searchInput,
          onSelect: performSearch,
          limitWidthToInput: true,
          showSpinner: true,
          reopenPattern: /.*:$/
        },
        hasFocus: searchHasFocus,
        clearable: { value: searchInput, onClear: function () { searchActive(false); huePubSub.publish('autocomplete.close'); } },
        textInput: searchInput,
        valueUpdate: 'afterkeydown',
        attr: { placeholder: '${ _('Search ') }' + assistPanel.visiblePanel().name.replace(/s$/g, '') + (assistPanel.visiblePanel().type == 'sql' ? '${ _(' tables') }' : '${ _(' files') }' ) + '...' }">
        <a class="inactive-action" data-bind="click: performSearch"><i class="fa fa-search" data-bind="css: { 'blue': searchHasFocus() || searchActive() }"></i></a>
      </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="nav-search-result">
    <div class="nav-search-result assist-flex-panel">
      <div class="assist-flex-header">
        <div class="assist-inner-header" style="width: inherit;">${ _('Search result') }
          <div class="assist-db-header-actions">
            <a class="inactive-action" href="javascript:void(0)" data-bind="click: function() { searchActive(false); }"><i class="pointer fa fa-times" title="${ _('Close') }"></i></a>
          </div>
        </div>
      </div>
      <div class="assist-flex-fill" data-bind="niceScroll" style="overflow:hidden;">
        <!-- ko hueSpinner: { spin: searching, center: true, size: 'large' } --><!-- /ko -->
        <!-- ko if: !searching() -->
        <!-- ko if: hasErrors() -->
        <!-- ko if: errorMessage() !== '' -->
        <div class="result-entry" data-bind="text: errorMessage"></div>
        <!-- /ko -->
        <!-- ko if: errorMessage() === '' -->
        <div class="result-entry">${ _('Error searching, see logs for details.') }</div>
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko ifnot: hasErrors() -->
        <!-- ko if: searchResult().length == 0 -->
        <div class="result-entry">${ _('No result found.') }</div>
        <!-- /ko -->
        <div data-bind="foreach: searchResult">
          <div class="result-entry" data-bind="visibleOnHover: { override: statsVisible, selector: '.table-actions' }, event: { mouseover: showNavContextPopoverDelayed, mouseout: clearNavContextPopoverDelay }">
            <div class="left-col">
              <i class="fa fa-fw valign-middle" data-bind="css: icon"></i>
            </div>
            <div class="doc-col" data-bind="css: { 'doc-col-no-desc' : !hasDescription }">
              <!-- ko if: typeof click !== 'undefined' -->
                <a class="pointer" data-bind="click: click, html: hue_name" target="_blank"></a>
              <!-- /ko -->
              <!-- ko if: typeof click === 'undefined' && typeof link !== 'undefined'-->
                <a class="pointer" data-bind="hueLink: link, text: originalName, attr: { target: IS_HUE_4 ? '_self' : '_blank' }"></a>
              <!-- /ko -->
              <div class="doc-desc" data-bind="html: hue_description"></div>
            </div>
          </div>
        </div>
        <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">

    var NavigatorSearch = (function () {

      var NAV_FACET_ICON = 'fa-tags';

      var NAV_TYPE_ICONS = {
        'DATABASE': 'fa-database',
        'TABLE': 'fa-table',
        'VIEW': 'fa-eye',
        'FIELD': 'fa-columns',
        'PARTITION': 'fa-th',
        'SOURCE': 'fa-server',
        'OPERATION': 'fa-cogs',
        'OPERATION_EXECUTION': 'fa-cog',
        'DIRECTORY': 'fa-folder-o',
        'FILE': 'fa-file-o',
        'S3BUCKET': 'fa-cubes',
        'SUB_OPERATION': 'fa-code-fork',
        'COLLECTION': 'fa-search',
        'HBASE': 'fa-th-large',
        'HUE': 'fa-file-o'
      };

      function NavigatorSearch (assistPanel, navigationSettings) {
        var self = this;

        self.navigatorEnabled = ko.observable('${ has_navigator(user) }' === 'True');

        self.assistPanel = assistPanel;
        self.navigationSettings = navigationSettings;
        self.apiHelper = ApiHelper.getInstance();

        self.searchInput = ko.observable('').extend({rateLimit: 500});
        self.searchResult = ko.observableArray();

        self.hasErrors = ko.observable(false);
        self.errorMessage = ko.observable('');
        self.searchHasFocus = ko.observable(false);
        self.searching = ko.observable(false);
        self.searchActive = ko.observable(false);

        huePubSub.subscribe('assist.hide.search', function () {
          self.searchActive(false);
        });

        var lastQuery = -1;

        self.assistPanel.visiblePanel.subscribe(function(newValue) {
          if (self.navigatorEnabled() && self.searchActive()) {
            lastQuery = 'refresh';
            self.performSearch();
          }
        });

        self.performSearch = function () {
          huePubSub.publish('autocomplete.close');
          if (self.searchInput() === '') {
            self.searchActive(false);
            return;
          }
          if (!self.searchActive()) {
            self.searchActive(true);
          } else if (self.searchInput() === lastQuery) {
            return;
          }
          if (self.searching()) {
            window.setTimeout(function() {
              self.performSearch();
            }, 100);
            return;
          }
          lastQuery = self.searchInput();
          self.searching(true);
          self.hasErrors(false);
          self.errorMessage('');

          var showInAssist = function (entry) {
            self.searchInput('');
            self.searchHasFocus(false);
            var path = entry.parentPath.split('/').concat([entry.selectionName]).splice(1);
            window.setTimeout(function () {
              huePubSub.publish('sql.context.popover.hide');
              huePubSub.publish('assist.db.highlight', { sourceType: entry.sourceType.toLowerCase(), path: path });
            }, 200); // For animation effect
          };

          var showNavContextPopover = function (entry, event) {
            if (entry.type && entry.type !== 'TABLE' && entry.type !== 'VIEW' && entry.type !== 'DATABASE' && entry.type !== 'FIELD') {
              return;
            }
            var $source = $(event.target).closest('.result-entry');
            var offset = $source.offset();
            entry.statsVisible(true);
            var identifierChain = $.map(entry.parentPath.substring(1).split('/'), function (part) { return { name: part } }).concat({ name: entry.selectionName });
            if (identifierChain.length > 0 && identifierChain[0].name === '') {
              identifierChain.shift();
            }
            huePubSub.publish('sql.context.popover.show', {
              data: {
                type: entry.type === 'FIELD' ? 'column' : (entry.type === 'DATABASE' ? 'database' : 'table'),
                identifierChain: identifierChain
              },
              delayedHide: '.result-entry',
              orientation: 'right',
              sourceType: entry.sourceType.toLowerCase(),
              defaultDatabase: entry.type === 'DATABASE' ? entry.originalName : (identifierChain.length > 0 ? identifierChain[0].name : 'default'),
              pinEnabled: self.navigationSettings.pinEnabled,
              source: {
                element: event.target,
                left: offset.left,
                top: offset.top - 3,
                right: offset.left + $source.width() + 3,
                bottom: offset.top + $source.height() - 3
              }
            });
            huePubSub.subscribeOnce('sql.context.popover.hidden', function () {
              entry.statsVisible(false);
            });
          };

          var navContextPopoverTimeout = -1;

          var showNavContextPopoverDelayed = function (entry, event) {
            window.clearTimeout(navContextPopoverTimeout);
            navContextPopoverTimeout = window.setTimeout(function () {
              showNavContextPopover(entry, event);
            }, 500);
          };

          var clearNavContextPopoverDelay = function () {
            window.clearTimeout(navContextPopoverTimeout);
          };

          $.post('/desktop/api/search/entities', {
            query_s: ko.mapping.toJSON(self.searchInput()),
            limit: 25,
            sources: ko.mapping.toJSON([self.assistPanel.visiblePanel().type])
          }).done(function (data) {
            if (typeof data === 'undefined' || data === null) {
              data = {};
            }
            if (typeof data.entities === 'undefined') {
              data.entities = [];
            }
            if (data.status === -2) {
              self.hasErrors(true);
              if (typeof data.message !== 'undefined') {
                self.errorMessage(data.message);
              }
              return;
            }
            data.entities.forEach(function (entity) {
              entity.statsVisible = ko.observable(false);
              entity.showNavContextPopoverDelayed = showNavContextPopoverDelayed;
              entity.clearNavContextPopoverDelay = clearNavContextPopoverDelay;
              entity.icon = NAV_TYPE_ICONS[entity.type];
              switch (entity.type) {
                case 'DATABASE': { }
                case 'TABLE': { }
                case 'VIEW': { }
                case 'FIELD': {
                  entity.click = function () {
                    showInAssist(entity);
                  };
                  break;
                }
                case 'SOURCE': {
                  entity.originalDescription = '${ _("Cluster") }: ' + entity.clusterName;
                  entity.link = entity.sourceUrl;
                  break;
                }
                case 'OPERATION_EXECUTION': {
                  entity.link = '/jobbrowser/jobs/' + entity.jobID;
                  break;
                }
                case 'DIRECTORY': {
                  entity.originalDescription = entity.parentPath;
                  if (entity.sourceType == 'S3') {
                    entity.link = '/filebrowser/view=S3A://#s3a://' + entity.bucketName + '/' + entity.fileSystemPath;
                  } else {
                    entity.link = '/filebrowser/#' + entity.fileSystemPath;
                  }
                  break;
                }
                case 'FILE': {
                  entity.originalDescription = entity.parentPath;
                  if (entity.sourceType == 'S3') {
                    entity.link = '/filebrowser/view=S3A://#s3a://' + entity.bucketName + '/' + entity.fileSystemPath;
                  } else {
                    entity.link = '/filebrowser/#' + entity.fileSystemPath;
                  }
                  break;
                }
                case 'S3BUCKET': {
                  entity.originalDescription = '${ _("Region") }: ' + entity.region;
                  entity.link = '/filebrowser/view=S3A://#s3a://' + entity.originalName;
                  break;
                }
                case 'SUB_OPERATION': {
                  entity.originalDescription = entity.metaClassName;
                  break;
                }
                case 'PARTITION': {
                  entity.hue_description = entity.originalName;
                  break;
                }
                case 'OPERATION': {}
              }
              entity.hasDescription = typeof entity.originalDescription !== 'undefined' && entity.originalDescription !== null && entity.originalDescription.length > 0;
            });
            self.searchResult(data.entities);
          }).fail(function (xhr, textStatus, errorThrown) {
            self.hasErrors(true);
            $(document).trigger("error", xhr.responseText);
          }).always(function () {
            self.searching(false);
          });
        };

        var previousCall = null;
        self.navAutocompleteSource = function (request, callback) {
          var facetMatch = request.term.match(/([a-z]+):\s*(\S+)?$/i);
          var isFacet = facetMatch !== null;
          var partialMatch = isFacet ? null : request.term.match(/\S+$/);
          var partial = isFacet && facetMatch[2] ? facetMatch[2] : (partialMatch ? partialMatch[0] : '');
          var beforePartial = request.term.substring(0, request.term.length - partial.length);

          var visiblePanel = self.assistPanel.visiblePanel();

          self.apiHelper.cancelActiveRequest(previousCall);

          previousCall = self.apiHelper.navSearchAutocomplete({
            source: visiblePanel.type === 'sql' ?
                (visiblePanel.panelData.selectedSource() ? visiblePanel.panelData.selectedSource().sourceType : 'hive') : visiblePanel.type,
            query:  request.term,
            successCallback: function (data) {
              var values = [];
              var facetPartialRe = new RegExp(partial.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&"), 'i'); // Protect for 'tags:*axe'
              if (isFacet && typeof data.facets !== 'undefined') { // Is typed facet, e.g. type: type:bla
                var facetInQuery = facetMatch[1];
                if (typeof data.facets[facetInQuery] !== 'undefined') {
                  $.map(data.facets[facetInQuery], function (count, value) {
                    if (facetPartialRe.test(value)) {
                      values.push({ data: { label: facetInQuery + ':' + value, icon: NAV_FACET_ICON, description: count }, value: beforePartial + value})
                    }
                  });
                }
              } else {
                if (typeof data.facets !== 'undefined') {
                  Object.keys(data.facets).forEach(function (facet) {
                    if (facetPartialRe.test(facet)) {
                      if (Object.keys(data.facets[facet]).length > 0) {
                        values.push({ data: { label: facet + ':', icon: NAV_FACET_ICON, description: $.map(data.facets[facet], function (key, value) { return value + ' (' + key + ')'; }).join(', ') }, value: beforePartial + facet + ':'});
                      } else { // Potential facet from the list
                        values.push({ data: { label: facet + ':', icon: NAV_FACET_ICON, description: '' }, value: beforePartial + facet + ':'});
                      }
                    } else if (partial.length > 0) {
                      Object.keys(data.facets[facet]).forEach(function (facetValue) {
                        if (facetValue.indexOf(partial) !== -1) {
                          values.push({ data: { label: facet + ':' + facetValue, icon: NAV_FACET_ICON, description: facetValue }, value: beforePartial + facet + ':' + facetValue });
                        }
                      });
                    }
                  });
                }
              }

              if (values.length > 0) {
                values.push({ divider: true });
              }
              if (typeof data.results !== 'undefined') {
                var upToLastSpace = '';
                if (request.term.lastIndexOf(' ') > -1) {
                  upToLastSpace = request.term.substring(0, request.term.lastIndexOf(' ') + 1);
                }

                data.results.forEach(function (result) {
                  values.push({ data: { label: result.hue_name, icon: NAV_TYPE_ICONS[result.type],  description: result.hue_description }, value: upToLastSpace + result.originalName });
                });
              }

              if (values.length > 0 && values[values.length - 1].divider) {
                values.pop();
              }
              if (values.length === 0) {
                values.push({ noMatch: true });
              }
              callback(values);
            },
            silenceErrors: true,
            errorCallback: function (data) {
              if (typeof data.message !== 'undefined' && data.source === 'navigator') {
                callback([{ error: true, message: data.message }]);
              } else {
                callback([{ error: true }]);
              }
            }
          });
        };
      }

      return NavigatorSearch;
    })();
  </script>
</%def>
