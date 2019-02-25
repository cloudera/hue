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

${ commonheader(_("Create database"), 'metastore', user, request) | n,unicode }

<span class="notebook">

${layout.metastore_menubar()}

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>
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
                sql : {
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

            <h3>${_('Create a new database')}</h3>

            <ul id="step-nav" class="nav nav-pills">
              <li class="active"><a href="#step/1" class="step">${_('Step 1: Name')}</a></li>
              <li><a href="#step/2" class="step">${_('Step 2: Location')}</a></li>
            </ul>

            <form action="${ url(app_name + ':create_database')}" method="POST" id="mainForm" class="form-horizontal">
              ${ csrf_token(request) | n,unicode }
              <div class="steps">
                <div id="step1" class="stepDetails">
                    <fieldset>
                        <div class="alert alert-info"><h3>${_('Create a database')}</h3>${_("Let's start with a name and description for where we'll store your data.")}</div>
                        <div class="control-group">
                            ${comps.bootstrapLabel(database_form["name"])}
                            <div class="controls">
                                ${comps.field(database_form["name"], attrs=dict(
                                    placeholder=_('database_name'),
                                  )
                                )}
                                <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                <p class="help-block">
                                    ${_('Name of the new database. Database names must be globally unique. Database names tend to correspond to the directory where the data will be stored.')}
                                </p>
                            </div>
                        </div>
                        <div class="control-group">
                            ${comps.bootstrapLabel(database_form["comment"])}
                            <div class="controls">
                                ${comps.field(database_form["comment"], attrs=dict(
                                  placeholder=_('Optional'),
                                  )
                                )}
                                <p class="help-block">
                                    ${_("Use a database comment to describe the database. For example, note the data's provenance and any caveats users need to know.")}
                                </p>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div id="step2" class="stepDetails hide">
                  <fieldset>
                      <div class="alert alert-info"><h3>${_("Choose Where Your Database's Data is Stored")}</h3>
                      </div>
                      <div class="control-group">
                          <label class="control-label">${_('Location')}</label>
                          <div class="controls">
                              <label class="checkbox">
                                  ${comps.field(database_form["use_default_location"],
                                  render_default=True
                                  )}
                                  ${_('Use default location')}
                              </label>
                              <span class="help-block">
                                  ${_('Store your database in the default location (controlled by Hive, and typically')} <em>/user/hive/warehouse/database_name</em>).
                              </span>
                          </div>
                      </div>

                      <div id="location" class="control-group hide">
                          ${comps.bootstrapLabel(database_form["external_location"])}
                          <div class="controls">
                              ${comps.field(database_form["external_location"],
                              placeholder="/user/user_name/data_dir",
                              klass="pathChooser input-xxlarge",
                              file_chooser=True,
                              show_errors=False
                              )}
                              <span  class="help-inline error-inline hide">${_('This field is required.')}</span>
                              <span class="help-block">
                              ${_("Enter the path (on HDFS) to your database's data location.")}
                              </span>
                          </div>
                      </div>
                  </fieldset>
              </div>
              </div>
              <div class="form-actions" style="padding-left: 10px">
                  <button type="button" id="backBtn" class="btn hide">${_('Back')}</button>
                  <button type="button" id="nextBtn" class="btn btn-primary">${_('Next')}</button>
                  <input id="submit" type="submit" name="create" class="btn btn-primary hide" value="${_('Create database')}" />
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
    height: 250px;
  }

  .inputs-list {
    list-style: none outside none;
    margin-left: 0;
  }

  .remove {
    float: right;
  }

  .error-inline {
    color: #B94A48;
    font-weight: bold;
  }

  .steps {
    min-height: 350px;
    margin-top: 10px;
  }

  div .alert {
    margin-bottom: 30px;
  }
</style>

</div>

<script type="text/javascript">

  (function () {

    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    function CreateDatabaseViewModel() {
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
      var viewModel = new CreateDatabaseViewModel();

      ko.applyBindings(viewModel);

      // Routing
      var step = 1;
      routie({
        'step/1': function(node_type) {
          $("#step-nav").children().removeClass("active");
          $("#step-nav").children(":nth-child(1)").addClass("active");
          $('.stepDetails').hide();
          $('#step1').show();
          $("#backBtn").hide();
          $("#nextBtn").show();
          $("#submit").hide();
        },
        'step/2': function(node_type) {
          $("#step-nav").children().removeClass("active");
          $("#step-nav").children(":nth-child(2)").addClass("active");
          $('.stepDetails').hide();
          $('#step2').show();
          $("#backBtn").show();
          $("#nextBtn").hide();
          $("#submit").show();
        }
      });
      routie('step/' + step);

      // events
      $(".fileChooserBtn").click(function (e) {
        e.preventDefault();
        var _destination = $(this).attr("data-filechooser-destination");
        $("#filechooser").jHueFileChooser({
          initialPath: $("input[name='" + _destination + "']").val(),
          onFolderChoose: function (filePath) {
            $("input[name='" + _destination + "']").val(filePath);
            $("#chooseFile").modal("hide");
          },
          createFolder: false,
          selectFolder: true,
          uploadFile: false
        });
        $("#chooseFile").modal("show");
      });

      $("#id_use_default_location").change(function () {
        if (!$(this).is(":checked")) {
          $("#location").slideDown();
        }
        else {
          $("#location").slideUp();
        }
      });

      $("#submit").click(function() {
        return validate();
      });

      $("#nextBtn").click(function () {
        if (validate()) {
          routie('step/' + ++step);
        }
      });

      $("#backBtn").click(function () {
        // To get to the current step
        // users will have to get through all previous steps.
        routie('step/' + --step);
      });

      $(".step").click(function() {
        return validate();
      });

      // Validation
      function validate() {
        switch(step) {
          case 1:
            var databaseNameFld = $("input[name='name']");
            if (!isValid($.trim(databaseNameFld.val()))) {
              showFieldError(databaseNameFld);
              return false;
            } else {
              hideFieldError(databaseNameFld);
            }
          break;

          case 2:
            var externalLocationFld = $("input[name='external_location']");
            if (!($("#id_use_default_location").is(":checked"))) {
              if (!isValid($.trim(externalLocationFld.val()))) {
                showFieldError(externalLocationFld);
                return false;
              }
              else {
                hideFieldError(externalLocationFld);
              }
            }
          break;
        }

        return true;
      }

      function isValid(str) {
        return (str != "" && str.indexOf(" ") == -1);
      }

      function showFieldError(field) {
        field.nextAll(".error-inline").not(".error-inline-bis").removeClass("hide");
      }

      function hideFieldError(field) {
        if (!(field.nextAll(".error-inline").hasClass("hide"))) {
          field.nextAll(".error-inline").addClass("hide");
        }
      }
    });
  })();
</script>


</span>

${ commonfooter(request, messages) | n,unicode }
