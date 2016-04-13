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

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="tableStats" file="/table_stats.mako" />
<%namespace name="require" file="/require.mako" />


${ commonheader(_('Create table from file'), 'metastore', user) | n,unicode }
${ layout.metastore_menubar() }

${ require.config() }

${ tableStats.tableStats() }
${ assist.assistPanel() }


<script src="${ static('desktop/ext/js/d3.v3.js') }" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
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
                  sourceTypes: [{
                    name: 'hive',
                    type: 'hive'
                  }],
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

        <div class="right-panel">

          <div class="metastore-main">
            <h3>
              <div class="inline-block pull-right" style="margin-top: -8px">
                <a href="${ url('beeswax:create_table', database=database) }" title="${_('Create a new table manually')}" class="inactive-action margin-left-10"><i class="fa fa-plus"></i></a>
              </div>

              <ul id="breadcrumbs" class="nav nav-pills hueBreadcrumbBar">
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
              <li class="active"><a href="${ url(app_name + ':import_wizard', database=database) }">${_('Step 1: Choose File')}</a></li>
              <li><a id="step2" href="#">${_('Step 2: Choose Delimiter')}</a></li>
              <li><a href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form action="${action}" method="POST" class="form-horizontal">
              ${ csrf_token(request) | n,unicode }
              <fieldset>
                <div class="alert alert-info margin-top-10"><h3>${_('Name Your Table and Choose A File')}</h3></div>
                <div class="control-group">
                    ${comps.bootstrapLabel(file_form["name"])}
                    <div class="controls">
                        ${comps.field(file_form["name"], placeholder=_('table_name'), show_errors=False)}
                        <span  class="help-inline">${unicode(file_form["name"].errors) | n}</span>
                    <span class="help-block">
                        ${_('Name of the new table. Table names must be globally unique. Table names tend to correspond to the directory where the data will be stored.')}
                    </span>
                    </div>
                </div>
                <div class="control-group">
                    ${comps.bootstrapLabel(file_form["comment"])}
                    <div class="controls">
                        ${comps.field(file_form["comment"],
                        placeholder=_("Optional"),
                        klass="",
                        show_errors=False
                        )}
                        <span  class="help-inline">${unicode(file_form["comment"].errors) | n}</span>
                    <span class="help-block">
                    ${_("Use a table comment to describe the table.  For example, note the data's provenance and any caveats users need to know.")}
                    </span>
                    </div>
                </div>
                <div class="control-group">
                    ${comps.bootstrapLabel(file_form["path"])}
                    <div class="controls">
                        ${comps.field(file_form["path"],
                        placeholder="/user/user_name/data_dir",
                        klass="pathChooser input-xxlarge",
                        file_chooser=True,
                        show_errors=False
                        )}
                        <span  class="help-inline">${unicode(file_form["path"].errors) | n}</span>
                    <span class="help-block">
                    ${_('The HDFS path to the file on which to base this new table definition. It can be compressed (gzip) or not.')}
                    </span>
                    </div>
                </div>
                <div class="control-group">
                  ${comps.bootstrapLabel(file_form["do_import"])}
                  <div class="controls">
                    ${comps.field(file_form["do_import"], render_default=True)}
                    <span class="help-block">
                    ${_('Check this box to import the data in this file after creating the table definition. Leave it unchecked to define an empty table.')}
                    <div id="fileWillBeMoved" class="alert">
                        <strong>${_('Warning:')}</strong> ${_('The selected file is going to be moved during the import.')}
                    </div>
                  </span>
                  </div>
                </div>
              </fieldset>
              <div class="form-actions" style="padding-left: 10px">
                  <input type="submit" class="btn btn-primary" name="submit_file" value="${_('Next')}" />
              </div>
            </form>

          </div>

        </div>
      </div>
    </div>
  </div>
</div>



<div id="chooseFile" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Choose a file')}</h3>
    </div>
    <div class="modal-body">
        <div id="filechooser">
        </div>
    </div>
    <div class="modal-footer">
    </div>
</div>


<style type="text/css">
  #filechooser {
    min-height: 100px;
    overflow-y: auto;
    margin-top: 10px;
  }

  #fileWillBeMoved {
    margin-top: 10px;
  }
</style>

<script type="text/javascript" charset="utf-8">

  require([
    "knockout",
    "ko.charts",
    "desktop/js/assist/assistHelper",
    "assistPanel",
    "tableStats",
    "knockout-mapping",
    "knockout-sortable",
    "ko.editable",
    "ko.hue-bindings"
  ], function (ko, charts, AssistHelper) {

    ko.options.deferUpdates = true;

    function MetastoreViewModel(options) {
      var self = this;
      self.assistHelper = AssistHelper.getInstance(options);
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.assistHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);


      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/' + tableDef.database + '/' + tableDef.name;
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        location.href = '/metastore/tables/' + databaseDef.name;
      });
    }

    $(document).ready(function () {

      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }"
        }
      }

      var viewModel = new MetastoreViewModel(options);

      ko.applyBindings(viewModel);

      if (location.getParameter("error") != "") {
        $.jHueNotify.error(location.getParameter("error"));
      }

      $(".fileChooserBtn").click(function (e) {
        e.preventDefault();
        var _destination = $(this).attr("data-filechooser-destination");
        $("#filechooser").jHueFileChooser({
          initialPath: $("input[name='" + _destination + "']").val(),
          onFileChoose: function (filePath) {
            $("input[name='" + _destination + "']").val(filePath);
            $("#chooseFile").modal("hide");
          },
          createFolder: false
        });
        $("#chooseFile").modal("show");
      });
      $("#id_do_import").change(function () {
        if ($(this).is(":checked")) {
          $("#fileWillBeMoved").show();
        }
        else {
          $("#fileWillBeMoved").hide();
        }
      });
      $("#step2").click(function (e) {
        e.preventDefault();
        $("input[name='submit_file']").click();
      });
      $("body").keypress(function (e) {
        if (e.which == 13) {
          e.preventDefault();
          $("input[name='submit_file']").click();
        }
      });

    });
  });

</script>


${ commonfooter(request, messages) | n,unicode }
