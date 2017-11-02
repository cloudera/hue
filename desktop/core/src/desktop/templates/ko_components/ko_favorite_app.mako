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

<%def name="favoriteApp()">

  <script type="text/html" id="hue-favorite-app-template">
    <!-- ko if: isHue4 -->
    <div class="inline pointer favorite-app" data-bind="click: setAsFavoriteApp, tooltip: { placement: 'bottom', title: isFavorite() ? '${ _ko("Unset from default application") }' : '${ _ko("Set as default application") }' }">
      <i class="fa inactive-action" data-bind="css: { 'fa-star-o': !isFavorite(), 'fa-star': isFavorite }"></i>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/javascript">
    (function () {

      var FavoriteApp = function (params) {
        var self = this;
        self.isHue4 = ko.observable(params.hue4);
        self.isFavorite = ko.observable(false);
        self.app = params.app;
        self.interpreter = params.interpreter;

        self.parseCurrentFavorite = function (data, announce) {
          self.isFavorite(false);
          if (data.status === 0 && data.data && data.data.default_app) {
            try {
              var defaultApp = JSON.parse(data.data.default_app);
              self.isFavorite(defaultApp.app === self.app && ((self.app === 'editor' && defaultApp.interpreter === self.interpreter) || self.app !== 'editor'));
              if (announce) {
                huePubSub.publish('hue.new.default.app', defaultApp);
              }
            } catch (e) {
              console.error('${ _ko("There was a problem decoding the default app setting.") }');
            }
          }
        };

        self.setAsFavoriteApp = function (vm, e) {
          e.originalEvent.stopPropagation();
          e.originalEvent.stopImmediatePropagation();
          var postParams = {
            app: self.app
          };
          if (self.interpreter !== '') {
            postParams['interpreter'] = self.interpreter;
          }
          var post = {};
          if (self.isFavorite()) {
            post['delete'] = true;
          }
          else {
            post['set'] = ko.mapping.toJSON(postParams);
          }
          $.post('/desktop/api2/user_preferences/default_app', post, function (data) {
            self.parseCurrentFavorite(data, true);
          });
        };

        if (self.isHue4()) {
          // Load the fav app status
          $.get('/desktop/api2/user_preferences/default_app', function (data) {
            self.parseCurrentFavorite(data);
          });
        }
      };

      ko.components.register('hue-favorite-app', {
        viewModel: FavoriteApp,
        template: {element: 'hue-favorite-app-template'}
      });
    })();
  </script>
</%def>