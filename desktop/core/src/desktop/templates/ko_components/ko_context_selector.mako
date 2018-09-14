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

<%def name="contextSelector()">

  <script type="text/html" id="hue-context-selector-template">
    <!-- ko if: loadingContext -->
    <i class="fa fa-spinner fa-spin muted"></i>
    <!-- /ko -->

    <div class="inline-block" style="display:none;" data-bind="visible: !loadingContext()">
      <!-- ko if: window.HAS_MULTI_CLUSTER -->
      <!-- ko if: availableComputes().length > 0 && !hideComputes -->
      <!-- ko ifnot: hideLabels --><span class="editor-header-title">${ _('Compute') }</span><!-- /ko -->
      <div data-bind="component: { name: 'hue-drop-down', params: { value: compute, entries: availableComputes, labelAttribute: 'name', searchable: true, linkTitle: '${ _ko('Active compute') }' } }" style="display: inline-block"></div>
      <!-- /ko -->
      <!-- ko if: availableComputes().length === 0 && !hideComputes -->
      <span class="editor-header-title"><i class="fa fa-warning"></i> ${ _('No computes found') }</span>
      <!-- /ko -->

      <!-- ko if: availableNamespaces().length > 0 && !hideNamespaces -->
      <!-- ko ifnot: hideLabels --><span class="editor-header-title">${ _('Namespace') }</span><!-- /ko -->
      <div data-bind="component: { name: 'hue-drop-down', params: { value: namespace, entries: availableNamespaces, labelAttribute: 'name', searchable: true, linkTitle: '${ _ko('Active namespace') }' } }" style="display: inline-block"></div>
      <!-- /ko -->
      <!-- ko if: availableNamespaces().length === 0 && !hideNamespaces -->
      <span class="editor-header-title"><i class="fa fa-warning"></i> ${ _('No namespaces found') }</span>
      <!-- /ko -->
      <!-- /ko -->

      <!-- ko if: availableDatabases().length > 0 && !hideDatabases-->
      <!-- ko ifnot: hideLabels --><span class="editor-header-title">${ _('Database') }</span><!-- /ko -->
      <div data-bind="component: { name: 'hue-drop-down', params: { value: database, entries: availableDatabases, foreachVisible: true, searchable: true, linkTitle: '${ _ko('Active database') }' } }" style="display: inline-block"></div>
      <!-- /ko -->
      <!-- ko if: availableDatabases().length === 0  && !hideDatabases -->
      <span class="editor-header-title"><i class="fa fa-warning"></i> ${ _('No databases found') }</span>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      /**
       * This is a component for compute, namespace and database selection. All parameters are optional except the
       * sourceType, if for instance no database and namespace observables are provided it will only show compute
       * selection.
       *
       * If it's desired to just show namespaces for a given compute you can force hide the compute selection by
       * setting hideComputes to true and the value of the compute observable will be used.
       *
       * Example:
       *
       *   <!-- ko component: {
       *     name: 'hue-context-selector',
       *     params: {
       *       sourceType: 'impala',
       *       compute: myComputeObservable,
       *       namespace: myNamespaceObservable,
       *     }
       *   } --><!-- /ko -->
       *
       * @param {Object} params
       * @param {ko.observable|string} params.sourceType
       * @param {ko.observable} [params.compute]
       * @param {ko.observable} [params.namespace]
       * @param {ko.observable} [params.database]
       * @param {ko.observableArray} [params.availableDatabases]
       * @param {boolean} [params.hideComputes] - Can be used to force hide compute selection even if a compute
       *                                          observable is provided.
       * @param {boolean} [params.hideNamespaces] - Can be used to force hide namespace selection even if a namespace
       *                                            observable is provided.
       * @param {boolean} [params.hideDatabases] - Can be used to force hide database selection even if a database
       *                                           observable is provided.
       * @param {function} [params.onComputeSelect] - Callback when a new compute is selected (after initial set)
       * @constructor
       */
      var HueContextSelector = function (params) {
        var self = this;

        var apiHelper = ApiHelper.getInstance();

        self.sourceType = params.sourceType;
        self.disposals = [];

        self.loadingComputes = ko.observable(false);
        self.availableComputes = ko.observableArray();
        self.compute = params.compute;
        self.hideComputes = params.hideComputes || !self.compute;
        self.hideLabels = params.hideLabels;

        if (params.compute) {
          self.loadingComputes(true);
          self.lastComputesPromise = ContextCatalog.getComputes({ sourceType: ko.unwrap(self.sourceType) }).done(function (computes) {
            self.availableComputes(computes);
            if (!self.compute() && apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedCompute')) {
              var lastSelectedCompute = apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedCompute');
              var found = computes.some(function (compute) {
                if (compute.id === lastSelectedCompute.id) {
                  self.compute(lastSelectedCompute);
                  return true;
                }
              });

              // If we can't find exact match we pick first based on type
              if (!found) {
                computes.some(function (compute) {
                  if (compute.type === lastSelectedCompute.type) {
                    self.compute(compute);
                    return true;
                  }
                });
              }
            }

            if (!self.compute()) {
              self.compute(computes[0]);
            }

            var computeSub = self.compute.subscribe(function (newCompute) {
              if (params.onComputeSelect) {
                params.onComputeSelect(newCompute);
              }
              apiHelper.setInTotalStorage('contextSelector', 'lastSelectedCompute', newCompute);
            });
            self.disposals.push(function () {
              computeSub.dispose();
            })
          }).always(function () {
            self.loadingComputes(false);
          });
        } else {
          self.lastComputesPromise = $.Deferred().resolve().promise();
        }


        self.loadingNamespaces = ko.observable(false);
        self.availableNamespaces = ko.observableArray();
        self.namespace = params.namespace;
        self.hideNamespaces = params.hideNamespaces || !self.namespace;

        self.lastNamespacePromise = undefined;
        self.reloadNamespaces = function () {
          if (params.namespace) {
            self.loadingNamespaces(true);
            self.lastNamespacePromise = ContextCatalog.getNamespaces({ sourceType: ko.unwrap(self.sourceType) }).done(function (context) {
              self.availableNamespaces(context.namespaces);
              if (!self.namespace()) {
                self.namespace(apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace'));
              }
              if (!self.namespace() || !context.namespaces.some(function (namespace) {
                if (namespace.id === self.namespace().id) {
                  self.namespace(namespace);
                  return true;
                }})) {
                self.namespace(context.namespaces[0]);
              }
              var namespaceSub = self.namespace.subscribe(function (newNamespace) {
                apiHelper.setInTotalStorage('contextSelector', 'lastSelectedNamespace', newNamespace);
              });
              self.disposals.push(function () {
                namespaceSub.dispose();
              })
            }).always(function () {
              self.loadingNamespaces(false);
            });
          } else {
            self.lastNamespacePromise = $.Deferred().resolve().promise();
          }
        };
        self.reloadNamespaces();

        self.loadingDatabases = ko.observable(false);
        self.availableDatabases = params.availableDatabases || ko.observableArray();
        self.database = params.database;
        self.hideDatabases = params.hideDatabases || !self.database;

        var updateDatabaseThrottle = -1;
        self.updateDatabases = function () {
          if (!self.hideDatabases) {
            self.loadingDatabases(true);
            $.when(self.lastNamespacePromise, self.lastComputesPromise).done(function () {
              window.clearTimeout(updateDatabaseThrottle);
              updateDatabaseThrottle = window.setTimeout(function () {
                DataCatalog.getEntry({
                  sourceType: ko.unwrap(self.sourceType),
                  namespace: self.namespace(),
                  compute: self.compute(),
                  path: [],
                  definition: { type: 'source' }
                }).done(function (sourceEntry) {
                  sourceEntry.getChildren({ silenceErrors: true }).done(function (databaseEntries) {
                    var databaseNames = [];
                    databaseEntries.forEach(function (databaseEntry) {
                      databaseNames.push(databaseEntry.name);
                    });
                    self.availableDatabases(databaseNames);
                  }).fail(function () {
                    self.availableDatabases([]);
                  }).always(function () {
                    if (self.database() && self.availableDatabases().indexOf(self.database()) === -1) {
                      if (self.availableDatabases().length === 0 || self.availableDatabases().indexOf('default') !== -1) {
                        self.database('default');
                      } else {
                        self.database(self.availableDatabases()[0])
                      }
                    }
                    self.loadingDatabases(false);

                    huePubSub.publish('assist.set.database', {
                      source: ko.unwrap(self.sourceType),
                      namespace: self.namespace(),
                      name: self.database()
                    });
                  });
                });
              }, 10);
            });
          } else if (self.database) {
            self.availableDatabases([]);
            self.database(undefined);
          }
        };

        self.updateDatabases();

        if (self.compute && self.namespace) {
          if (!self.namespace()) {
            self.namespace(apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace'));
          }
          if (!self.compute()) {
            self.compute(apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedCompute'));
          }

          $.when(self.lastNamespacePromise, self.lastComputesPromise).done(function () {
            var computeSub = self.compute.subscribe(function (newCompute) {
              // When the compute changes we set the corresponding namespace and update the databases
              if (newCompute) {
                var found = self.availableNamespaces().some(function (namespace) {
                  // TODO: Remove name check once compute.namespace is a namespace ID
                  if (namespace.name === newCompute.namespace || namespace.id === newCompute.namespace) {
                    if (!self.namespace() || self.namespace().id !== namespace.id) {
                      self.namespace(namespace);
                      self.updateDatabases();
                    }
                    return true;
                  }
                });
                if (!found && newCompute.namespace) {
                  self.namespace(newCompute.namespace);
                }
              }
            });
            self.disposals.push(function () {
              computeSub.dispose();
            });

            var namespaceSub = self.namespace.subscribe(function (newNamespace) {
              if (newNamespace) {
                // When the namespace changes we set the corresponding compute and update the databases
                var found = self.availableComputes().some(function (compute) {
                  if (compute.namespace === newNamespace.id) {
                    if (!self.compute() || self.compute().id !== compute.id) {
                      self.compute(compute);
                      self.updateDatabases();
                    }
                    return true;
                  }
                });
                if (!found) {
                  self.compute(undefined);
                }
              }
            });
            self.disposals.push(function () {
              namespaceSub.dispose();
            })
          });
        } else {
          self.updateDatabases();
        }

        if (self.database) {
          huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
            if (details.entry.isSource()) {
              if (ko.unwrap(self.sourceType) === details.entry.getSourceType()) {
                self.updateDatabases();
              }
            }
          });
        }

        if (self.namespace) {
          huePubSub.subscribe('context.catalog.namespaces.refreshed', function (sourceType) {
            if (ko.unwrap(self.sourceType) === sourceType) {
              self.reloadNamespaces();
            }
          });
        }

        self.loadingContext = ko.pureComputed(function () {
          return self.loadingNamespaces() || self.loadingComputes() || self.loadingDatabases();
        });
      };

      HueContextSelector.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      ko.components.register('hue-context-selector', {
        viewModel: HueContextSelector,
        template: { element: 'hue-context-selector-template' }
      });
    })();
  </script>

</%def>