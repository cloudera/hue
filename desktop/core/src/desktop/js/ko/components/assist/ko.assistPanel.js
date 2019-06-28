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

import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import AssistInnerPanel from 'ko/components/assist/assistInnerPanel';

const TEMPLATE = `
  <script type="text/html" id="assist-panel-inner-header">
    <div class="assist-header assist-fixed-height" data-bind="visibleOnHover: { selector: '.assist-header-actions' }, css: { 'assist-resizer': $index() > 0 }" style="display:none;">
      <span data-bind="text: $parent.name"></span>
      <div class="assist-header-actions">
        <div class="inactive-action" data-bind="click: function () { $parent.visible(false) }"><i class="fa fa-times"></i></div>
      </div>
    </div>
  </script>
  
  <div class="assist-panel" data-bind="dropzone: { url: '/filebrowser/upload/file?dest=' + DROPZONE_HOME_DIR, params: {dest: DROPZONE_HOME_DIR}, clickable: false, paramName: 'hdfs_file', onComplete: function(path){ huePubSub.publish('assist.dropzone.complete', path); }, disabled: !window.SHOW_UPLOAD_BUTTON }">
    <!-- ko if: availablePanels().length > 1 -->
    <div class="assist-panel-switches">
      <!-- ko foreach: availablePanels -->
      <div class="inactive-action assist-type-switch" data-bind="click: function () { $parent.visiblePanel($data); }, css: { 'blue': $parent.visiblePanel() === $data }, style: { 'float': rightAlignIcon ? 'right' : 'left' },  attr: { 'title': name }">
        <!-- ko if: iconSvg --><span style="font-size:22px;"><svg class="hi"><use data-bind="attr: {'xlink:href': iconSvg }" xlink:href=''></use></svg></span><!-- /ko -->
        <!-- ko if: !iconSvg --><i class="fa fa-fw valign-middle" data-bind="css: icon"></i><!-- /ko -->
      </div>
      <!-- /ko -->
    </div>
    <!-- /ko -->
    <!-- ko with: visiblePanel -->
    <div class="assist-panel-contents" data-bind="style: { 'padding-top': $parent.availablePanels().length > 1 ? '10px' : '5px' }">
      <div class="assist-inner-panel">
        <div class="assist-flex-panel">
          <!-- ko component: panelData --><!-- /ko -->
        </div>
      </div>
    </div>
    <!-- /ko -->
  </div>
`;

class AssistPanel {
  /**
   * @param {Object} params
   * @param {string} params.user
   * @param {boolean} params.onlySql - For the old query editors
   * @param {string[]} params.visibleAssistPanels - Panels that will initially be shown regardless of total storage
   * @param {Object} params.sql
   * @param {Object[]} params.sql.sourceTypes - All the available SQL source types
   * @param {string} params.sql.sourceTypes[].name - Example: Hive SQL
   * @param {string} params.sql.sourceTypes[].type - Example: hive
   * @param {string} [params.sql.activeSourceType] - Example: hive
   * @param {Object} params.sql.navigationSettings - enable/disable the links
   * @param {boolean} params.sql.navigationSettings.openItem - Example: true
   * @param {boolean} params.sql.navigationSettings.showStats - Example: true
   * @constructor
   */
  constructor(params) {
    const self = this;
    const i18n = {
      errorLoadingDatabases: I18n('There was a problem loading the databases'),
      errorLoadingTablePreview: I18n('There was a problem loading the table preview')
    };
    const i18nCollections = {
      errorLoadingDatabases: I18n('There was a problem loading the indexes'),
      errorLoadingTablePreview: I18n('There was a problem loading the index preview')
    };

    self.tabsEnabled = window.USE_NEW_SIDE_PANELS;

    self.availablePanels = ko.observableArray();
    self.visiblePanel = ko.observable();

    self.lastOpenPanelType = ko.observable();
    window.apiHelper.withTotalStorage('assist', 'last.open.panel', self.lastOpenPanelType);

    huePubSub.subscribeOnce('cluster.config.set.config', clusterConfig => {
      if (clusterConfig && clusterConfig['app_config']) {
        const panels = [];
        const appConfig = clusterConfig['app_config'];

        if (appConfig['editor']) {
          const sqlPanel = new AssistInnerPanel({
            panelData: {
              name: 'hue-assist-db-panel',
              params: $.extend(
                {
                  i18n: i18n
                },
                params.sql
              )
            },
            name: I18n('SQL'),
            type: 'sql',
            icon: 'fa-database',
            minHeight: 75
          });
          panels.push(sqlPanel);

          huePubSub.subscribe('assist.show.sql', () => {
            if (self.visiblePanel() !== sqlPanel) {
              self.visiblePanel(sqlPanel);
            }
          });
        }

        if (self.tabsEnabled) {
          if (
            appConfig['browser'] &&
            appConfig['browser']['interpreter_names'].indexOf('hdfs') !== -1
          ) {
            panels.push(
              new AssistInnerPanel({
                panelData: {
                  name: 'hue-assist-hdfs-panel',
                  params: {}
                },
                name: I18n('HDFS'),
                type: 'hdfs',
                icon: 'fa-files-o',
                minHeight: 50
              })
            );
          }

          if (
            appConfig['browser'] &&
            appConfig['browser']['interpreter_names'].indexOf('s3') !== -1
          ) {
            panels.push(
              new AssistInnerPanel({
                panelData: {
                  name: 'hue-assist-s3-panel',
                  params: {}
                },
                name: I18n('S3'),
                type: 's3',
                icon: 'fa-cubes',
                minHeight: 50
              })
            );
          }

          if (
            appConfig['browser'] &&
            appConfig['browser']['interpreter_names'].indexOf('adls') !== -1
          ) {
            panels.push(
              new AssistInnerPanel({
                panelData: {
                  name: 'hue-assist-adls-panel',
                  params: {}
                },
                name: I18n('ADLS'),
                type: 'adls',
                icon: 'fa-windows',
                iconSvg: '#hi-adls',
                minHeight: 50
              })
            );
          }

          if (
            appConfig['browser'] &&
            appConfig['browser']['interpreter_names'].indexOf('indexes') !== -1
          ) {
            const solrPanel = new AssistInnerPanel({
              panelData: {
                name: 'hue-assist-db-panel',
                params: $.extend(
                  {
                    i18n: i18nCollections,
                    isSolr: true
                  },
                  params.sql
                )
              },
              name: I18n('Indexes'),
              type: 'solr',
              icon: 'fa-search-plus',
              minHeight: 75
            });
            panels.push(solrPanel);
            huePubSub.subscribe('assist.show.solr', () => {
              if (self.visiblePanel() !== solrPanel) {
                self.visiblePanel(solrPanel);
              }
            });
          }

          if (
            appConfig['browser'] &&
            appConfig['browser']['interpreter_names'].indexOf('kafka') !== -1
          ) {
            const streamsPanel = new AssistInnerPanel({
              panelData: $.extend(
                {
                  i18n: i18nCollections,
                  isStreams: true
                },
                params.sql
              ),
              name: I18n('Streams'),
              type: 'kafka',
              icon: 'fa-sitemap',
              minHeight: 75
            });
            panels.push(streamsPanel);
          }

          if (
            appConfig['browser'] &&
            appConfig['browser']['interpreter_names'].indexOf('hbase') !== -1
          ) {
            panels.push(
              new AssistInnerPanel({
                panelData: {
                  name: 'hue-assist-hbase-panel',
                  params: {}
                },
                name: I18n('HBase'),
                type: 'hbase',
                icon: 'fa-th-large',
                minHeight: 50
              })
            );
          }

          if (!window.IS_EMBEDDED) {
            const documentsPanel = new AssistInnerPanel({
              panelData: {
                name: 'hue-assist-documents-panel',
                params: {
                  user: params.user
                }
              },
              name: I18n('Documents'),
              type: 'documents',
              icon: 'fa-files-o',
              iconSvg: '#hi-documents',
              minHeight: 50,
              rightAlignIcon: true,
              visible:
                params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
            });

            panels.push(documentsPanel);

            huePubSub.subscribe('assist.show.documents', docType => {
              huePubSub.publish('left.assist.show');
              if (self.visiblePanel() !== documentsPanel) {
                self.visiblePanel(documentsPanel);
              }
              if (docType) {
                documentsPanel.panelData.setTypeFilter(docType);
              }
            });
          }

          if (window.HAS_GIT) {
            panels.push(
              new AssistInnerPanel({
                panelData: {
                  name: 'hue-assist-git-panel',
                  params: {}
                },
                name: I18n('Git'),
                type: 'git',
                icon: 'fa-github',
                minHeight: 50,
                rightAlignIcon: true
              })
            );
          }
        }

        self.availablePanels(panels);
      } else {
        self.availablePanels([
          new AssistInnerPanel({
            panelData: {
              name: 'hue-assist-db-panel',
              params: $.extend(
                {
                  i18n: i18n
                },
                params.sql
              )
            },
            name: I18n('SQL'),
            type: 'sql',
            icon: 'fa-database',
            minHeight: 75
          })
        ]);
      }

      if (!self.lastOpenPanelType()) {
        self.lastOpenPanelType(self.availablePanels()[0].type);
      }

      const lastFoundPanel = self.availablePanels().filter(panel => {
        return panel.type === self.lastOpenPanelType();
      });

      // always forces the db panel to load
      const dbPanel = self.availablePanels().filter(panel => {
        return panel.type === 'sql';
      });
      if (dbPanel.length > 0) {
        dbPanel[0].panelData.init();
      }

      self.visiblePanel.subscribe(newValue => {
        self.lastOpenPanelType(newValue.type);
        if (newValue.type !== 'sql' && !newValue.panelData.initialized) {
          newValue.panelData.init();
        }
      });

      self.visiblePanel(
        lastFoundPanel.length === 1 ? lastFoundPanel[0] : self.availablePanels()[0]
      );
    });

    window.setTimeout(() => {
      // Main initialization trigger in hue.mako, this is for Hue 3
      if (self.availablePanels().length === 0) {
        huePubSub.publish('cluster.config.get.config');
      }
    }, 0);
  }
}

componentUtils.registerComponent('assist-panel', AssistPanel, TEMPLATE);
