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

import ko from 'knockout';

import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

class SideBarViewModel {
  constructor(onePageViewModel, topNavViewModel) {
    const self = this;

    self.items = ko.observableArray();

    self.pocClusterMode = topNavViewModel.pocClusterMode;

    huePubSub.subscribe('cluster.config.set.config', clusterConfig => {
      const items = [];

      if (clusterConfig && clusterConfig['app_config']) {
        const appsItems = [];
        const appConfig = clusterConfig['app_config'];
        if (appConfig['editor']) {
          let editor = null;
          if (
            clusterConfig['main_button_action'] &&
            clusterConfig['main_button_action'].page.indexOf('/editor') === 0
          ) {
            editor = clusterConfig['main_button_action'];
          }

          if (!editor) {
            const defaultEditor = appConfig['editor']['default_sql_interpreter'];
            if (defaultEditor) {
              const foundEditor = appConfig['editor']['interpreters'].filter(interpreter => {
                return interpreter.type === defaultEditor;
              });
              if (foundEditor.length === 1) {
                editor = foundEditor[0];
              }
            }
          }

          if (!editor && appConfig['editor']['interpreters'].length > 1) {
            editor = appConfig['editor']['interpreters'][1];
          }

          if (editor) {
            appsItems.push({
              displayName: I18n('Editor'),
              url: editor['page'],
              icon: 'editor'
            });
          } else {
            appsItems.push({
              displayName: appConfig['editor']['displayName'],
              url: appConfig['editor']['page'],
              icon: 'editor'
            });
          }
        }
        ['dashboard', 'scheduler'].forEach(appName => {
          if (appConfig[appName]) {
            appsItems.push({
              displayName: appConfig[appName]['displayName'],
              url: appConfig[appName]['page'],
              icon: appName
            });
          }
        });
        if (appsItems.length > 0) {
          items.push({
            isCategory: true,
            displayName: I18n('Apps'),
            children: appsItems
          });
        }

        const browserItems = [];
        browserItems.push({
          displayName: I18n('Documents'),
          url: '/home/',
          icon: 'documents'
        });
        if (appConfig['browser'] && appConfig['browser']['interpreters']) {
          appConfig['browser']['interpreters'].forEach(browser => {
            browserItems.push({
              displayName: browser.displayName,
              url: browser.page,
              icon: browser.type
            });
          });
        }
        if (browserItems.length > 0) {
          items.push({
            isCategory: true,
            displayName: I18n('Browsers'),
            children: browserItems
          });
        }

        const sdkItems = [];
        if (appConfig['sdkapps'] && appConfig['sdkapps']['interpreters']) {
          appConfig['sdkapps']['interpreters'].forEach(browser => {
            sdkItems.push({
              displayName: browser['displayName'],
              url: browser['page']
            });
          });
        }
        if (sdkItems.length > 0) {
          items.push({
            isCategory: true,
            displayName: appConfig['sdkapps']['displayName'],
            children: sdkItems
          });
        }
      }

      self.items(items);
    });

    self.leftNavVisible = topNavViewModel.leftNavVisible;
    self.onePageViewModel = onePageViewModel;
  }
}

export default SideBarViewModel;
