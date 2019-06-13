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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />

${ commonheader(_('Create table from file'), 'metastore', user, request) | n,unicode }
<span class="notebook">
${ layout.metastore_menubar() }

<script src="${ static('metastore/js/metastore.ko.js') }"></script>

${ assist.assistJSModels() }

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
</style>

${ assist.assistPanel() }

<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>


<div class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full">
      <div class="vertical-full row-fluid panel-container">

        <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
          <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
          <div class="assist" data-bind="component: {
              name: 'assist-panel',
              params: {
                user: '${user.username}',
                sql: {
                  navigationSettings: {
                    openItem: false,
                    showStats: true
                  }
                },
                visibleAssistPanels: ['sql']
              }
            }"></div>
        </div>
        <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>

        <div class="content-panel">

          <div class="metastore-main">
            <h3>
              <div class="inline-block pull-right" style="margin-top: -8px">
                <a href="${ url('beeswax:import_wizard', database=database) }" title="${_('Create a new table from a file')}" class="inactive-action"><i class="fa fa-files-o"></i></a>
                <a href="${ url('beeswax:create_table', database=database) }" title="${_('Create a new table manually')}" class="inactive-action margin-left-10"><i class="fa fa-wrench"></i></a>
              </div>

              <ul id="breadcrumbs" class="nav nav-pills hue-breadcrumbs-bar">
                <li>
                  <a href="${url('metastore:databases')}">${_('Databases')}</a><span class="divider">&gt;</span>
                </li>
                <li>
                  <a href="${ url('metastore:show_tables', database=database) }">${database}</a><span class="divider">&gt;</span>
                </li>
                <li>
                    <span style="padding-left:12px">${_('Create a new table from a file')}</span>
                </li>
              </ul>
            </h3>

            <ul class="nav nav-pills">
                <li><a id="step1" href="#">${_('Step 1: Choose File')}</a></li>
                <li class="active"><a href="#">${_('Step 2: Choose Delimiter')}</a></li>
                <li><a id="step3" href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form id="delimiterForm" action="${action}" method="POST" class="form-horizontal">
              ${ csrf_token(request) | n,unicode }
              <div class="hide">
                  ${util.render_form(file_form)}
                  ${comps.field(delim_form['file_type'])}
              </div>
              <fieldset>
                  <div class="alert alert-info margin-top-10"><h3>${_('Choose a Delimiter')}</h3>
                      % if initial:
                          ${_('Beeswax has determined that this file is delimited by')} <strong>${delim_readable}</strong>.
                      % endif
                  </div>
                  <div class="control-group">
                      ${comps.bootstrapLabel(delim_form["delimiter"])}
                      <div class="controls">
                          ${comps.field(delim_form["delimiter"], render_default=True)}
                          <input id="submit_preview" class="btn btn-info" type="submit" value="${_('Preview')}" name="submit_preview"/>
                          <span class="help-block">
                          ${_('Enter the column delimiter which must be a single character. Use syntax like "\\001" or "\\t" for special characters.')}
                          </span>
                      </div>
                  </div>
                  <div class="control-group">
                      <label class="control-label">${_('Table preview')}</label>
                      <div class="controls">
                          <div class="scrollable">
                              <table class="table table-condensed">
                                  <thead>
                                  <tr>
                                    % for i in range(n_cols):
                                        <th>col_${i+1}</th>
                                    % endfor
                                  </tr>
                                  </thead>
                                  <tbody>
                                    % for row in fields_list:
                                    <tr>
                                      % for val in row:
                                        ${ comps.getEllipsifiedCell(val, "left")}
                                      % endfor
                                    </tr>
                                    % endfor
                                  </tbody>
                              </table>
                          </div>
                      </div>
                  </div>
              </fieldset>

              <div class="form-actions" style="padding-left: 10px">
                  <input class="btn" type="submit" value="${_('Previous')}" name="cancel_delim"/>
                  <input class="btn btn-primary" type="submit" name="submit_delim" value="${_('Next')}" />
              </div>
            </form>

          </div>

        </div>
      </div>
    </div>
  </div>
</div>




<style type="text/css">
  .scrollable {
    width: 100%;
    overflow-x: auto;
  }
</style>

<script type="text/javascript">
  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    function ImportWizardChooseDelimiterViewModel() {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);


      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/' + tableDef.database + '/' + tableDef.name + '?source=' + tableDef.sourceType + '&namespace=' + tableDef.namespace.id;
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        location.href = '/metastore/tables/' + databaseDef.name + '?source=' + databaseDef.sourceType + '&namespace=' + databaseDef.namespace.id;
      });
    }

    $(document).ready(function () {

      var viewModel = new ImportWizardChooseDelimiterViewModel(options);

      ko.applyBindings(viewModel);

      if (location.getParameter("error") != "") {
        $.jHueNotify.error(location.getParameter("error"));
      }


      $("[rel='tooltip']").tooltip();

      $(".scrollable").width($(".form-actions").width() - 170);

      $("#id_delimiter_1").css("margin-left", "4px").attr("placeholder", "${_('Type your delimiter here')}").hide();
      $("#id_delimiter_0").change(function () {
        if ($(this).val() == "__other__") {
          $("#id_delimiter_1").show();
        }
        else {
          $("#id_delimiter_1").hide();
          $("#id_delimiter_1").val('');
        }
      });

      $("#id_delimiter_0").change();

      $("#step1").click(function (e) {
        e.preventDefault();
        $("input[name='cancel_delim']").click();
      });
      $("#step3").click(function (e) {
        e.preventDefault();
        $("input[name='submit_delim']").click();
      });
      $("body").keypress(function (e) {
        if (e.which == 13) {
          e.preventDefault();
          $("input[name='submit_delim']").click();
        }
      });
    });
  })();
</script>

</span>

${ commonfooter(request, messages) | n,unicode }
