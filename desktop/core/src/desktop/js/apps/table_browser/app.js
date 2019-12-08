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
import * as ko from 'knockout';

import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import MetastoreViewModel from 'apps/table_browser/metastoreViewModel';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';

const HUE_PUB_SUB_EDITOR_ID = 'metastore';

if (ko.options) {
  ko.options.deferUpdates = true;
}

huePubSub.subscribe('app.dom.loaded', app => {
  if (app !== 'metastore') {
    return;
  }

  const options = {
    user: window.LOGGED_USERNAME,
    optimizerEnabled: window.HAS_OPTIMIZER,
    navigatorEnabled: window.HAS_CATALOG,
    optimizerUrl: window.OPTIMIZER_URL,
    navigatorUrl: window.CATALOG_URL
  };

  const viewModel = new MetastoreViewModel(options);

  huePubSub.subscribe(
    'metastore.scroll.to.top',
    () => {
      $('.page-content').scrollTop(0);
    },
    HUE_PUB_SUB_EDITOR_ID
  );

  huePubSub.subscribe(
    'metastore.clear.selection',
    () => {
      viewModel.sources().forEach(source => {
        source.namespaces().forEach(namespace => {
          namespace.selectedDatabases.removeAll();
          namespace.databases().forEach(database => {
            database.selectedTables.removeAll();
          });
        });
      });
    },
    HUE_PUB_SUB_EDITOR_ID
  );

  viewModel.currentTab.subscribe(tab => {
    if (tab === 'relationships') {
      // viewModel.database().table().getRelationships();
    } else if (tab === 'sample') {
      const selector = 'samplesTable';
      const bannerTopHeight = window.BANNER_TOP_HTML ? 30 : 0;
      if ($(selector).parents('.dataTables_wrapper').length === 0) {
        hueUtils.waitForRendered(
          selector,
          el => el.find('td').length > 0,
          () => {
            $(selector).dataTable({
              bPaginate: false,
              bLengthChange: false,
              bInfo: false,
              bDestroy: true,
              bFilter: false,
              bAutoWidth: false,
              oLanguage: {
                sEmptyTable: I18n('No data available'),
                sZeroRecords: I18n('No matching records')
              },
              fnDrawCallback: () => {
                $(selector)
                  .parents('.dataTables_wrapper')
                  .css('overflow-x', 'hidden');
                $(selector).jHueTableExtender2({
                  fixedHeader: true,
                  fixedFirstColumn: true,
                  includeNavigator: false,
                  lockSelectedRow: false,
                  parentId: 'sample',
                  classToRemove: 'sample-table',
                  mainScrollable: '.page-content',
                  stickToTopPosition: 51 + bannerTopHeight,
                  clonedContainerPosition: 'fixed',
                  app: 'metastore'
                });
                $(selector).jHueHorizontalScrollbar();
              },
              aoColumnDefs: [
                {
                  sType: 'numeric',
                  aTargets: ['sort-numeric']
                },
                {
                  sType: 'string',
                  aTargets: ['sort-string']
                },
                {
                  sType: 'date',
                  aTargets: ['sort-date']
                }
              ]
            });
          }
        );
      }
    }
  });

  ko.applyBindings(viewModel, $('#metastoreComponents')[0]);

  huePubSub.subscribe('cluster.config.set.config', clusterConfig => {
    viewModel.appConfig(clusterConfig && clusterConfig['app_config']);
  });

  huePubSub.publish('cluster.config.get.config');

  if (location.getParameter('refresh') === 'true') {
    dataCatalog
      .getEntry({
        namespace: viewModel.source().namespace().namespace,
        compute: viewModel.source().namespace().compute,
        sourceType: viewModel.source().type,
        path: [],
        definition: { type: 'source' }
      })
      .done(entry => {
        entry.clearCache({
          invalidate: viewModel.source().type === 'impala' ? 'invalidate' : 'cache',
          silenceErrors: true
        });
        hueUtils.replaceURL('?');
      });
  }
});
