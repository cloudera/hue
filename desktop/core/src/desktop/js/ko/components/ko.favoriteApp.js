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
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <div class="inline pointer favorite-app" data-bind="click: setAsFavoriteApp, tooltip: { placement: 'bottom', title: isFavorite() ? '${I18n(
    'Unset from default application'
  )}' : '${I18n('Set as default application')}' }">
    <i class="fa inactive-action" data-bind="css: { 'fa-star-o': !isFavorite(), 'fa-star': isFavorite }"></i>
  </div>
`;

class FavoriteApp {
  constructor(params) {
    const self = this;
    self.isFavorite = ko.observable(false);
    self.app = params.app;
    self.interpreter = params.interpreter;

    self.parseCurrentFavorite = function(data, announce) {
      self.isFavorite(false);
      if (data.status === 0 && data.data && data.data.default_app) {
        try {
          const defaultApp = JSON.parse(data.data.default_app);
          self.isFavorite(
            defaultApp.app === self.app &&
              ((self.app === 'editor' && defaultApp.interpreter === self.interpreter) ||
                self.app !== 'editor')
          );
          if (announce) {
            huePubSub.publish('hue.new.default.app', defaultApp);
          }
        } catch (e) {
          console.error('There was a problem decoding the default app setting.');
        }
      }
    };

    self.setAsFavoriteApp = function(vm, e) {
      e.originalEvent.stopPropagation();
      e.originalEvent.stopImmediatePropagation();
      const postParams = {
        app: self.app
      };
      if (self.interpreter !== '') {
        postParams['interpreter'] = self.interpreter;
      }
      const post = {};
      if (self.isFavorite()) {
        post['delete'] = true;
      } else {
        post['set'] = ko.mapping.toJSON(postParams);
      }
      $.post('/desktop/api2/user_preferences/default_app', post, data => {
        self.parseCurrentFavorite(data, true);
      });
    };

    // Load the fav app status
    $.get('/desktop/api2/user_preferences/default_app', data => {
      self.parseCurrentFavorite(data);
    });
  }
}

componentUtils.registerComponent('hue-favorite-app', FavoriteApp, TEMPLATE);
