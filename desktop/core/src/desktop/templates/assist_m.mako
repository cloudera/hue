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
from desktop.views import commonheader_m, commonfooter_m
from django.utils.translation import ugettext as _
%>

<%namespace name="assist" file="assist.mako" />

${ commonheader_m(_('Assist'), 'assist', user, request) | n,unicode }

<script src="${ static('metastore/js/metastore.ko.js') }"></script>

${ assist.assistJSModels() }

${ assist.assistPanel() }

<style type="text/css">
  .assist {
    margin-left: -10px;
    margin-right: -10px;
  }

  .assist-tables > li {
    line-height: 26px;
  }

</style>


<div class="assist" data-bind="component: {
    name: 'assist-panel',
    params: {
      user: '${user.username}',
      sql: {
        navigationSettings: {
          openDatabase: false,
          openItem: false,
          showStats: false,
          pinEnabled: false
        },
      },
      visibleAssistPanels: ['sql']
    }
  }"></div>


<script type="text/javascript">
  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    function AssistViewModel(options) {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

      self.sqlSourceTypes = [];
      self.availableLanguages = [];

      if (options.languages && options.snippetViewSettings) {
        $.each(options.languages, function (idx, language) {
          self.availableLanguages.push({
            type: language.type,
            name: language.name,
            interface: language.interface,
          });
          var viewSettings = options.snippetViewSettings[language.type];
          if (viewSettings && viewSettings.sqlDialect) {
            self.sqlSourceTypes.push({
              type: language.type,
              name: language.name
            })
          }
        });
      }

      var sqlSourceTypes = $.grep(self.sqlSourceTypes, function(language) { return language.type == self.editorType(); });
      if (sqlSourceTypes.length > 0) {
        self.activeSqlSourceType = sqlSourceTypes[0].type;
      } else {
        self.activeSqlSourceType = null;
      }
    }

    $(document).ready(function () {

      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }"
        }
      }

      var viewModel = new AssistViewModel(options);
      ko.applyBindings(viewModel);

      function resizeViewport() {
        $('.assist').height($(window).height() - 90);
      }

      resizeViewport();

      $(window).on('resize', resizeViewport);
    });
  })();
</script>


${ commonfooter_m(request, messages) | n,unicode }
