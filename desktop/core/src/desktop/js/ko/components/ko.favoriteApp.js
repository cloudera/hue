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

import * as ko from 'knockout';

import ApiHelper from 'api/apiHelper';
import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

export const NAME = 'hue-favorite-app';

const TEMPLATE = `
  <div class="inline pointer favorite-app" data-bind="click: setAsFavoriteApp.bind($data), tooltip: { placement: 'bottom', title: isFavorite() ? '${I18n(
    'Unset from default application'
  )}' : '${I18n('Set as default application')}' }">
    <i class="fa inactive-action" data-bind="css: { 'fa-star-o': !isFavorite(), 'fa-star': isFavorite }"></i>
  </div>
`;

class FavoriteApp {
  constructor(params) {
    this.isFavorite = ko.observable(false);
    this.app = params.app;
    this.interpreter = params.interpreter;

    ApiHelper.fetchFavoriteApp().then(this.updateFromApiResponse.bind(this));
  }

  updateFromApiResponse(data, announce) {
    this.isFavorite(false);
    if (data.status === 0 && data.data && data.data.default_app) {
      try {
        const defaultApp = JSON.parse(data.data.default_app);
        this.isFavorite(
          defaultApp.app === this.app &&
            ((this.app === 'editor' && defaultApp.interpreter === this.interpreter) ||
              this.app !== 'editor')
        );
        if (announce) {
          huePubSub.publish('hue.new.default.app', defaultApp);
        }
      } catch (e) {
        console.error('There was a problem decoding the default app setting.');
      }
    }
  }

  async setAsFavoriteApp(vm, e) {
    e.originalEvent.stopPropagation();
    e.originalEvent.stopImmediatePropagation();
    const post = {};
    if (this.isFavorite()) {
      post.delete = true;
    } else {
      const postParams = {
        app: this.app
      };
      if (this.interpreter !== '') {
        postParams.interpreter = this.interpreter;
      }
      post.set = JSON.stringify(postParams);
    }
    this.updateFromApiResponse(await ApiHelper.setFavoriteAppAsync(post), true);
  }
}

componentUtils.registerComponent(NAME, FavoriteApp, TEMPLATE);
