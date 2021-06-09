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
import MetastoreViewModel from 'apps/tableBrowser/metastoreViewModel';
import I18n from 'utils/i18n';
import { CONFIG_REFRESHED_TOPIC, GET_KNOWN_CONFIG_TOPIC } from 'config/events';
import waitForRendered from 'utils/timing/waitForRendered';
import getParameter from 'utils/url/getParameter';
import replaceURL from 'utils/url/replaceURL';

import 'components/er-diagram/webcomp';

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
    sqlAnalyzerEnabled: window.HAS_SQL_ANALYZER,
    navigatorEnabled: window.HAS_CATALOG,
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
        waitForRendered(
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
                $(selector).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
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

  const configUpdated = config => {
    viewModel.appConfig(config && config['app_config']);
  };

  huePubSub.publish(GET_KNOWN_CONFIG_TOPIC, configUpdated);
  huePubSub.subscribe(CONFIG_REFRESHED_TOPIC, configUpdated);

  if (getParameter('refresh') === 'true') {
    // TODO: Use connectors in the table browser
    const connector = {
      id: viewModel.source().type,
      dialect: viewModel.source().type
    };
    if (viewModel.source().type === 'hive' || viewModel.source().type === 'impala') {
      connector.optimizer = 'api';
    }
    dataCatalog
      .getEntry({
        namespace: viewModel.source().namespace().namespace,
        compute: viewModel.source().namespace().compute,
        connector: connector,
        path: [],
        definition: { type: 'source' }
      })
      .then(entry => {
        entry.clearCache({
          silenceErrors: true
        });
        replaceURL('?');
      });
  }
});
