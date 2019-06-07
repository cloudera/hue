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
                <a href="${ url('beeswax:create_table', database=database) }" title="${_('Create a new table manually')}" class="inactive-action margin-left-10"><i class="fa fa-plus"></i></a>
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
                    ${_('The path to the file(s) or directory on which to base this new table definition. It can be compressed (gzip) or not.')}
                    </span>
                    </div>
                </div>
                <div class="control-group">
                  ${comps.bootstrapLabel(file_form["load_data"])}
                  <div class="controls">
                    ${comps.field(file_form["load_data"], render_default=True)}
                    <span class="help-block">
                    ${_('Select whether table data should be imported, external or empty.')}
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

<script type="text/javascript">
  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    function ImportWizardChooseFileViewModel() {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);


      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/' + tableDef.database + '/' + tableDef.name  + '?source=' + tableDef.sourceType + '&namespace=' + tableDef.namespace.id;
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        location.href = '/metastore/tables/' + databaseDef.name + '?source=' + databaseDef.sourceType + '&namespace=' + databaseDef.namespace.id;
      });
    }

    $(document).ready(function () {

      var viewModel = new ImportWizardChooseFileViewModel();

      ko.applyBindings(viewModel);

      if (location.getParameter("error") != "") {
        $.jHueNotify.error(location.getParameter("error"));
      }

      $(".fileChooserBtn").click(function (e) {
        e.preventDefault();
        var _destination = $(this).attr("data-filechooser-destination");
        function handleChoice(filePath, isFile){
          if (filePath.toLowerCase().indexOf('s3a://') === 0 && isFile) {
            filePath = filePath.split('/');
            filePath.pop();
            filePath = filePath.join('/');
          }
          $("input[name='" + _destination + "']").val(filePath);
          $("#chooseFile").modal("hide");
          $('.pathChooser').trigger('change');
        }
        $("#filechooser").jHueFileChooser({
          initialPath: $("input[name='" + _destination + "']").val(),
          onFileChoose: function(path){ handleChoice(path, true) },
          onFolderChoose: function(path){ handleChoice(path, false) },
          createFolder: $('#id_load_data').val() === 'EXTERNAL',
          selectFolder: true,
          displayOnlyFolders: $('#id_load_data').val() === 'EXTERNAL'
        });
        $("#chooseFile").modal("show");
      });

      $("#id_load_data").change(function () {
        if ($(this).val() === 'IMPORT') {
          $("#fileWillBeMoved").show();
        }
        else {
          $("#fileWillBeMoved").hide();
        }
      });

      $('.pathChooser').change(function () {
        var initialLoadValue = $('#id_load_data').val();
        if ($(this).val().toLowerCase().indexOf('s3a://') === 0) {
          $('#id_load_data').val('EXTERNAL').trigger('change').find('option[value="IMPORT"]').attr('disabled', 'disabled');
        }
        else {
          $('#id_load_data').val(initialLoadValue).trigger('change').find('option[value="IMPORT"]').removeAttr('disabled');
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
  })();
</script>
</span>
${ commonfooter(request, messages) | n,unicode }
