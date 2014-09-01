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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_("Create database"), 'metastore', user) | n,unicode }
${layout.metastore_menubar()}

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span3">
        <div class="sidebar-nav">
            <ul class="nav nav-list">
                <li class="nav-header">${_('Actions')}</li>
                <li><a href="${ url(app_name + ':create_database')}">${_('Create a new database')}</a></li>
            </ul>
        </div>
    </div>

    <div class="span9">
      <div class="card" style="margin-top: 0">
        <h1 class="card-heading simple">${_('Create a new database')}</h1>
        <div class="card-body">
          <p>

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
      </p>
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


<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
$(document).ready(function () {
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
</script>

${ commonfooter(messages) | n,unicode }
