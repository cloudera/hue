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
  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf
  from django.utils.translation import ugettext as _
%>

<%namespace name="docBrowser" file="/document_browser.mako" />

<%def name="homeJSModels(is_embeddable=False)">
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
  <script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
  <script src="${ static('desktop/js/apiHelper.js') }"></script>
  <script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
  <script src="${ static('desktop/js/ko.editable.js') }"></script>
  <script src="${ static('desktop/js/ko.switch-case.js') }"></script>
  <script src="${ static('desktop/js/jquery.huedatatable.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery.mCustomScrollbar.concat.min.js') }"></script>
  <script src="${ static('desktop/js/home2.vm.js') }"></script>

  ${ docBrowser.docBrowser(is_embeddable) }
</%def>


<%def name="navbar()">
<div class="page-header">
  <h1 class="currentApp">
    <a href="${ url('desktop.views.home2') }">
      <img src="${ static('desktop/art/home.png') }" class="app-icon" />
      ${ _('My documents') }
    </a>
  </h1>
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

<script type="text/javascript" charset="utf-8">
  (function () {
    ko.options.deferUpdates = true;

    var userGroups = [];
    % for group in user.groups.all():
      userGroups.push('${ group }');
    % endfor

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        userGroups: userGroups,
        superuser: '${ user.is_superuser }' === 'True',
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
        if (location.getParameter('uuid')) {
          viewModel.openUuid(location.getParameter('uuid'));
        } else if (location.getParameter('path')) {
          viewModel.openPath(location.getParameter('path'));
        } else if (viewModel.activeEntry() && viewModel.activeEntry().loaded()) {
          var rootEntry = viewModel.activeEntry();
          while (rootEntry && ! rootEntry.isRoot()) {
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
      };
      window.onpopstate = loadUrlParam;
      loadUrlParam();

      %if not is_embeddable:
      viewModel.activeEntry.subscribe(function (newEntry) {
        if (typeof newEntry !== 'undefined' && newEntry.definition().uuid && ! newEntry.isRoot()) {
          hueUtils.changeURL('/home?uuid=' + newEntry.definition().uuid);
        } else if (typeof newEntry === 'undefined' || newEntry.isRoot()) {
          hueUtils.changeURL('/home');
        }
      });
      %endif

      ko.applyBindings(viewModel, $('#homeComponents')[0]);

      huePubSub.publish('init.tour');

    });
  })();

  huePubSub.subscribe('init.tour', function(){
    if ($.totalStorage("jHueTourHideModal") == null || $.totalStorage("jHueTourHideModal") == false) {
      $("#jHueTourModal").modal();
      $.totalStorage("jHueTourHideModal", true);
      $("#jHueTourModalChk").attr("checked", "checked");
      $("#jHueTourModalChk").on("change", function () {
        $.totalStorage("jHueTourHideModal", $(this).is(":checked"));
      });
      $("#jHueTourModalClose").on("click", function () {
        $("#jHueTourFlag").click();
        $("#jHueTourModal").modal("hide");
      });
    }
  });
</script>
</%def>

<%def name="tour()">
<div id="jHueTourModal" class="modal hide fade" tabindex="-1">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true"></button>
    <h3 class="modal-title">${_('Did you know?')}</h3>
  </div>
  <div class="modal-body">
    <ul class="nav nav-tabs" style="margin-bottom: 0">
      <li class="active"><a href="#tourStep1" data-toggle="tab">${ _('Step 1:') } ${ _('Add data') }</a></li>
      <li><a href="#tourStep2" data-toggle="tab">${ _('Step 2:') }  ${ _('Query data') }</a></li>
      <li><a href="#tourStep3" data-toggle="tab">${ _('Step 3:') } ${_('Do more!') }</a></li>
    </ul>

    <div class="tab-content">
      <div id="tourStep1" class="tab-pane active">
        <div class="pull-left step-icon"><i class="fa fa-download"></i></div>
        <div style="margin: 40px">
          <p>
            ${ _('With') }  <span class="badge badge-info"><i class="fa fa-file"></i> File Browser</span>
            ${ _('and the apps in the') }  <span class="badge badge-info">Data Browsers <b class="caret"></b></span> ${ _('section, upload, view your data and create tables.') }
          </p>
          <p>
            ${ _('Pre-installed samples are also already there.') }
          </p>
        </div>
      </div>

      <div id="tourStep2" class="tab-pane">
          <div class="pull-left step-icon"><i class="fa fa-search"></i></div>
          <div style="margin: 40px">
            <p>
              ${ _('Then query and visualize the data with the') } <span class="badge badge-info">Query Editors <b class="caret"></b></span>
               ${ _('and') }  <span class="badge badge-info">Search <b class="caret"></b></span>
            </p>
          </div>
      </div>

      <div id="tourStep3" class="tab-pane">
        <div class="pull-left step-icon"><i class="fa fa-flag-checkered"></i></div>
        <div style="margin: 40px">
          % if tours_and_tutorials:
          <p>
            ${ _('Tours were created to guide you around.') }
            ${ _('You can see the list of tours by clicking on the checkered flag icon') } <span class="badge badge-info"><i class="fa fa-flag-checkered"></i></span>
            ${ ('at the top right of this page.') }
          </p>
          % endif
          <p>
            ${ _('Additional documentation is available at') } <a href="http://learn.gethue.com">learn.gethue.com</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <label class="checkbox" style="float:left"><input id="jHueTourModalChk" type="checkbox" />${_('Do not show this dialog again')}</label>
    <a id="jHueTourModalClose" href="#" class="btn btn-primary disable-feedback">${_('Got it!')}</a>
  </div>
</div>
</%def>
