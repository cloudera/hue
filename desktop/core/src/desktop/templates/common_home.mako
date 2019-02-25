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

  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf
  from desktop.auth.backend import is_admin
%>

<%namespace name="docBrowser" file="/document_browser.mako" />

<%def name="homeJSModels(is_embeddable=False)">
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>
  <script src="${ static('desktop/js/home2.vm.js') }"></script>

  ${ docBrowser.docBrowser(is_embeddable) }
</%def>


<%def name="navbar()">
<div class="navbar hue-title-bar nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="app-header">
            <a href="${ url('desktop_views_home2') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" alt="${ _('Home icon') }" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>
</%def>

<%def name="vm(is_embeddable=False)">
<script type="text/html" id="document-template">
  <tr>
    <td style="width: 26px"></td>
    <td><a data-bind="attr: { href: absoluteUrl }, html: name"></a></td>
    <td data-bind="text: ko.mapping.toJSON($data)"></td>
  </tr>
</script>

<script type="text/javascript">
  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        superuser: '${ is_admin(user) }' === 'True',
        i18n: {
          errorFetchingTableDetails: '${_('An error occurred fetching the table details. Please try again.')}',
          errorFetchingTableFields: '${_('An error occurred fetching the table fields. Please try again.')}',
          errorFetchingTableSample: '${_('An error occurred fetching the table sample. Please try again.')}',
          errorRefreshingTableStats: '${_('An error occurred refreshing the table stats. Please try again.')}',
          errorLoadingDatabases: '${ _('There was a problem loading the databases. Please try again.') }',
          errorLoadingTablePreview: '${ _('There was a problem loading the table preview. Please try again.') }'
        }
      };

      var viewModel = new HomeViewModel(options);

      var loadUrlParam = function () {
        if (window.location.pathname.indexOf('/home') > -1) {
          if (location.getParameter('uuid')) {
            viewModel.openUuid(location.getParameter('uuid'));
          } else if (location.getParameter('path')) {
            viewModel.openPath(location.getParameter('path'));
          } else if (viewModel.activeEntry() && viewModel.activeEntry().loaded()) {
            var rootEntry = viewModel.activeEntry();
            while (rootEntry && !rootEntry.isRoot()) {
              rootEntry = rootEntry.parent;
            }
            viewModel.activeEntry(rootEntry);
          } else {
            viewModel.activeEntry().load(function () {
              if (viewModel.activeEntry().entries().length === 1 && viewModel.activeEntry().entries()[0].definition().type === 'directory') {
                viewModel.activeEntry(viewModel.activeEntry().entries()[0]);
                viewModel.activeEntry().load();
              }
            });
          }
        }
      };
      window.onpopstate = loadUrlParam;
      loadUrlParam();

      viewModel.activeEntry.subscribe(function (newEntry) {
        var filterType = window.location.pathname.indexOf('/home') > -1 && window.location.getParameter('type') != '' ? 'type=' + window.location.getParameter('type') : '';
        if (typeof newEntry !== 'undefined' && newEntry.definition().uuid && !newEntry.isRoot()) {
          if (window.location.getParameter('uuid') === '' || window.location.getParameter('uuid') !== newEntry.definition().uuid){
            hueUtils.changeURL('${ is_embeddable and '/hue' or ''}/home/?uuid=' + newEntry.definition().uuid + '&' + filterType);
          }
        } else if (typeof newEntry === 'undefined' || newEntry.isRoot()) {
          var url = '${ is_embeddable and '/hue' or ''}/home/' + (filterType ? '?' + filterType : '');
          if (window.location.pathname + window.location.search !== url) {
            hueUtils.changeURL(url);
          }
        }
      });

      ko.applyBindings(viewModel, $('#homeComponents')[0]);
    });
  })();

</script>
</%def>
