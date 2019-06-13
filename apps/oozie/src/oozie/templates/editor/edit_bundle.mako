## -*- coding: utf-8 -*-
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

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="properties" file="coordinator_properties.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Edit Bundle"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='bundles') }

<style type="text/css">
  .steps {
    min-height: 350px;
    margin-top: 10px;
  }
  #add-dataset-form, #edit-dataset-form {
    display: none;
  }
  .nav {
    margin-bottom: 0;
  }
  .help-block {
    color: #999999;
  }
</style>

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>


<div class="container-fluid">

  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Properties') }</li>
          <li class="active"><a href="#properties"><i class="fa fa-reorder"></i> ${ _('Edit properties') }</a></li>

          <li class="nav-header">${ _('Coordinators') }</li>
          % if bundle.is_editable(user):
          <li><a href="#addBundledCoordinator"><i class="fa fa-plus"></i> ${ _('Add') }</a></li>
          % endif
          <li><a href="#listCoordinators"><i class="fa fa-cloud"></i> ${ _('Show selected') }</a></li>

          % if bundle.is_editable(user):
              <li class="nav-header">${ _('History') }</li>
              <li><a href="#listHistory"><i class="fa fa-archive"></i> ${ _('Show history') }</a></li>
          % endif

          % if bundle:
              <li class="nav-header">${ _('Actions') }</li>
              <li>
                <a id="submit-btn" href="javascript:void(0)" data-submit-url="${ url('oozie:submit_bundle', bundle=bundle.id) }"
                   title="${ _('Submit this bundle') }" rel="tooltip" data-placement="right"><i class="fa fa-play"></i> ${ _('Submit') }
                </a>
              </li>
              <li>
                <a id="clone-btn" href="javascript:void(0)" data-clone-url="${ url('oozie:clone_bundle', bundle=bundle.id) }"
                   title="${ _('Copy this bundle') }" rel="tooltip" data-placement="right"><i class="fa fa-files-o"></i> ${ _('Copy') }
                </a>
             </li>
          % endif

        </ul>
      </div>
    </div>

    <div class="span10">
      <div class="card card-small">
      <h1 class="card-heading simple">${ _('Bundle Editor : ') } ${ bundle.name }</h1>
      <form id="jobForm" class="form-horizontal" action="${ url('oozie:edit_bundle', bundle=bundle.id) }" method="POST">
        ${ csrf_token(request) | n,unicode }
      <div id="properties" class="section">
        <ul class="nav nav-pills">
          <li class="active"><a href="#step1" class="step">${ _('Step 1: General') }</a></li>
          <li><a href="#step2" class="step">${ _('Step 2: Advanced settings') }</a></li>
        </ul>

        ${ bundled_coordinator_formset.management_form | n,unicode }

        <div class="steps">
            <div id="step1" class="stepDetails">
              <div class="alert alert-info"><h3>${ _('Bundle data') }</h3></div>
              <div class="fieldWrapper">
                ${ utils.render_field_no_popover(bundle_form['name'], extra_attrs = {'validate':'true'}) }
                ${ utils.render_field_no_popover(bundle_form['description']) }
                <div class="row-fluid">
                  <div class="span6">
                    ${ utils.render_field(bundle_form['kick_off_time']) }
                  </div>
                  <div class="span6">
                    <div class="alert alert-warning">
                      ${ _('UTC time only. (e.g. if you want 10pm PST (UTC+8) set it 8 hours later to 6am the next day.') }
                    </div>
                  </div>
                </div>
                ${ bundle_form['parameters'] | n,unicode }
                <div class="hide">
                  ${ utils.render_field_no_popover(bundle_form['is_shared']) }
                  ${ bundle_form['schema_version']  | n,unicode }
                </div>
              </div>
            </div>

            <div id="step2" class="stepDetails hide">
              <div class="alert alert-info"><h3>${ _('Advanced settings') }</h3></div>
              ${ properties.print_key_value(bundle_form['parameters'], 'parameters') }
              ${ bundle_form['schema_version'] | n,unicode }
            </div>
          </div>

        <div class="form-actions">
          <a id="backBtn" class="btn disabled">${ _('Back') }</a>
          <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
          % if bundle.is_editable(user):
            <input type="submit" class="btn btn-primary save" style="margin-left: 30px" value="${ _('Save bundle') }" />
          % endif
        </div>
      </div>


        <div id="listCoordinators" class="section hide">
          <div class="alert alert-info">
            <h3>${ _('Coordinators') }</h3>
          </div>

          <div>
            % if bundled_coordinator_formset.forms:
            <table class="table table-condensed" cellpadding="0" cellspacing="0" data-missing="#bundled_coordinator_missing">
              <thead>
                <tr>
                  <th data-row-selector-exclude="true">${ _('Name') }</th>
                  <th>${ _('Description') }</th>
                  % if bundle.is_editable(user):
                    <th>${ _('Delete') }</th>
                  % endif
                </tr>
              </thead>
              <tbody>
              % for form in bundled_coordinator_formset.forms:
                % for hidden in form.hidden_fields():
                  ${ hidden | n,unicode }
                % endfor
                <tr title="${ _('Click to view the coordinator') }" rel="tooltip">
                  <td>
                    <a href="${ url('oozie:edit_coordinator', coordinator=form.instance.coordinator.id) }" target="_blank">
                    <i class="fa fa-share"></i> ${ form.instance.coordinator.name }
                    </a>
                  </td>
                  <td>
                    % if bundle.is_editable(user):
                      <a href="javascript:void(0)" class="editBundledCoordinator"
                         data-url="${ url('oozie:edit_bundled_coordinator', bundle=bundle.id, bundled_coordinator=form.instance.id) }" data-row-selector="true"
                         />
                    % endif
                    ${ form.instance.coordinator.description }
                  </td>
                  % if bundle.is_editable(user):
                    <td data-row-selector-exclude="true">
                      <a class="btn btn-small delete-row" href="javascript:void(0);">${ _('Delete') }${ form['DELETE'] | n,unicode }</a>
                    </td>
                  % endif
                </tr>

                <div class="hide">
                  % for field in form.visible_fields():
                  ${ field.errors | n,unicode }
                  ${ field.label }: ${ field | n,unicode }
                  % endfor
                </div>
              % endfor
              </tbody>
            </table>
            % endif
          </div>
          <%
            klass = "alert alert-error"
            if bundled_coordinator_formset.forms:
              klass += " hide"
          %>
          <div id="bundled_coordinator_missing" data-missing-bind="true" class="${ klass }">
            ${ _('There are currently no coordinator in this bundle.') } <a href="#addBundledCoordinator">${ _('Do you want to add a coordinator ?') }</a>
          </div>
            % if bundled_coordinator_formset.forms and bundle.is_editable(user):
              <div class="form-actions" style="padding-left:10px">
                <input type="submit" class="btn btn-primary" value="${ _('Save') }" />
              </div>
            % endif
        </div>

        <div id="editBundledCoordinator" class="section hide"></div>

        <div id="createBundledCoordinator" class="section hide">
          ${ bundled_coordinator_html_form | n,unicode }
        </div>

        <div id="listHistory" class="section hide">
          <div class="alert alert-info"><h3>${ _('History') }</h3></div>
          % if bundle.is_editable(user):
          <div class="tab-pane" id="history">
            <table class="table">
              <thead>
              <tr>
                <th>${ _('Date') }</th>
                <th>${ _('Id') }</th>
              </tr>
              </thead>
              <tbody>
              % if not history:
              <tr>
                <td>${ _('N/A') }</td><td></td>
              </tr>
              % endif
              % for record in history:
              <tr>
                <td>
                  ${ utils.format_date(record.submission_date) }
                </td>
                <td>
                  <a href="${ record.get_absolute_oozie_url() }" data-row-selector="true">
                    ${ record.oozie_job_id }
                  </a>
                </td>
              </tr>
              % endfor
              </tbody>
            </table>
          </div>
          % endif
        </div>

    </div>
      </div>
  </div>
  </form>

</div>

<div id="submit-job-modal" class="modal hide"></div>


% if bundle.id:
  <div class="modal hide" id="edit-dataset-modal" style="z-index:1500;width:850px"></div>

  <style type="text/css">
    .delete-row input {
      display: none;
    }
  </style>

  <script type="text/javascript">

    /**
     * Initial state is used to define when to display the "initial state" of a table.
     * IE: if there are no formset forms to display, show an "empty" message.
     *
     * First, we build a registry of all functions that need to pass in order for us to display the initial state.
     * Things that 'remove' or 'add' elements will need to trigger 'reinit' and 'initOff' events on their respective 'initial state' elements.
     * 'Initial state' elements should have 'data-missing-bind="true"' so that custom events can be binded to them.
     *
     * args:
     *  test_func - function that, if true, will indicate that the initial state should be shown.
     *  hook - If we do show the initial state, run this function before showing it.
     */
    var initialStateRegistry = {};

    $("*[data-missing-bind='true']").on('register', function (e, test_func, hook) {
      var id = $(this).attr('id');
      if (!initialStateRegistry[id]) {
        initialStateRegistry[id] = [];
      }
      initialStateRegistry[id].push({ test:test_func, hook:hook });
    });

    $("*[data-missing-bind='true']").on('reinit', function (e) {
      var show = true;
      var id = $(this).attr('id');
      for (var i in initialStateRegistry[id]) {
        show = show && initialStateRegistry[id][i].test();
      }
      if (show) {
        for (var i in initialStateRegistry[id]) {
          if (!!initialStateRegistry[id][i].hook) {
            initialStateRegistry[id][i].hook();
          }
        }
        $(this).show();
      }
    });

    $("*[data-missing-bind='true']").on('initOff', function (e) {
      $(this).hide();
    });


    $(document).ready(function () {
      var ViewModel = function() {
        var self = this;

        self.parameters = ko.observableArray(${ bundle.parameters | n });
        self.add_parameters = function() {
          self.parameters.push({name: "", value: ""});
        };
        self.remove_parameters = function(val) {
          self.parameters.remove(val);
        };

        self.create_bundled_coordinator_parameters = ko.observableArray([]);
        self.add_create_bundled_coordinator_parameters = function() {
          self.create_bundled_coordinator_parameters.push({name: "", value: ""});
        };
        self.remove_create_bundled_coordinator_parameters = function(val) {
          self.create_bundled_coordinator_parameters.remove(val);
        };

        self.saveBundle = function(form) {
          var form = $("#jobForm");

          $("<input>").attr("type", "hidden")
                  .attr("name", "parameters")
                  .attr("value", ko.utils.stringifyJson(self.parameters))
                  .appendTo(form);

          return true;
        };
      };


      window.viewModel = new ViewModel();
      ko.applyBindings(window.viewModel, document.getElementById('step2'));
      ko.applyBindings(window.viewModel, document.getElementById('createBundledCoordinator'));

      % if not bundle.is_editable(user):
        $("#jobForm input, select").attr("disabled", "disabled");
        $("#jobForm .btn").not("#nextBtn, #backBtn").attr("disabled", "disabled").addClass("btn-disabled");
      % endif

      $('.delete-row').click(function () {
        var el = $(this);
        var row = el.closest('tr');
        var table = el.closest('table');
        el.find(':input').attr('checked', 'checked');
        row.hide();
        $(table.attr('data-missing')).trigger('reinit', table);
      });

      $('.delete-row').closest('table').each(function () {
        var table = $(this);
        var id = table.attr('data-missing');
        if (!!id) {
          $(id).trigger('register', [ function () {
            return table.find('tbody tr').length == table.find('tbody tr:hidden').length;
          }, function () {
            table.hide();
          } ]);
        }
      });

      $(".editBundledCoordinator").click(function () {
        var el = $(this);
        $.ajax({
          url:el.data("url"),
          beforeSend:function (xhr) {
            xhr.setRequestHeader("X-Requested-With", "Hue");
          },
          dataType:"json",
          success:function (response) {
            $("#editBundledCoordinator").html(response['data']);
            routie("editBundledCoordinator");
          }
        });
      });

      $("a[data-row-selector='true']").jHueRowSelector();


      $("*[rel=popover]").popover({
        placement:'top',
        trigger:'hover'
      });

      var currentStep = "step1";

      routie({
        "step1":function () {
          showStep("step1");
        },
        "step2":function () {
          if (validateStep("step1")) {
            showStep("step2");
          }
        },
        "properties":function () {
          showSection("properties");
        },
        "listCoordinators":function () {
          showSection("listCoordinators");
        },
        "addBundledCoordinator":function () {
          showSection("createBundledCoordinator");
        },
        "editBundledCoordinator":function () {
          showSection("editBundledCoordinator");
        },
        "listHistory":function () {
          showSection("listHistory");
        }
      });

      function highlightMenu(section) {
        $(".nav-list li").removeClass("active");
        $("a[href='#" + section + "']").parent().addClass("active");
      }

      function showStep(step) {
        showSection("properties");
        currentStep = step;
        if (step != "step1") {
          $("#backBtn").removeClass("disabled");
        }
        else {
          $("#backBtn").addClass("disabled");
        }
        if (step != $(".stepDetails:last").attr("id")) {
          $("#nextBtn").removeClass("disabled");
        }
        else {
          $("#nextBtn").addClass("disabled");
        }
        $("a.step").parent().removeClass("active");
        $("a.step[href='#" + step + "']").parent().addClass("active");
        $(".stepDetails").hide();
        $("#" + step).show();
      }

      function showSection(section) {
        $(".section").hide();
        $("#" + section).show();
        highlightMenu(section);
      }

      function validateStep(step) {
        var proceed = true;
        $("#" + step).find("[validate=true]").each(function () {
          if ($(this).val().trim() == "") {
            proceed = false;
            routie(step);
            $(this).parents(".control-group").addClass("error");
            $(this).parent().find(".help-inline").remove();
            $(this).after("<span class=\"help-inline\"><strong>${ _('This field is required.') }</strong></span>");
          }
        });
        return proceed;
      }

      $("#backBtn").click(function () {
        var nextStep = (currentStep.substr(4) * 1 - 1);
        if (nextStep >= 1) {
          routie("step" + nextStep);
        }
      });

      $("#nextBtn").click(function () {
        var nextStep = (currentStep.substr(4) * 1 + 1);
        if (nextStep <= $(".step").length) {
          routie("step" + nextStep);
        }
      });

      $("[validate=true]").change(function () {
        $(this).parents(".control-group").removeClass("error");
        $(this).parent().find(".help-inline").remove();
      });

      $("#id_workflow").change(function () {
        $("#workflowName").text($("#id_workflow option[value='" + $(this).val() + "']").text());
      });

      $("#clone-btn").on("click", function () {
        var _url = $(this).data("clone-url");
        $.post(_url, function (data) {
          window.location = data.url;
        });
      });

      $("#submit-btn").on("click", function () {
        var _url = $(this).data("submit-url");
        $.get(_url, function (response) {
            $("#submit-job-modal").html(response);
            $("#submit-job-modal").modal("show");
          }
        );
      });

      $(".save").click(function () {
        window.viewModel.saveBundle();
      });

      $("a[rel='tooltip']").tooltip();
    });
  </script>
% endif


${ utils.decorate_datetime_fields(False) }

${ commonfooter(request, messages) | n,unicode }
