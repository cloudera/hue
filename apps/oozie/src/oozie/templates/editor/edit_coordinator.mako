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
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="properties" file="coordinator_properties.mako" />
<%namespace name="coordinator_data" file="create_coordinator_data.mako" />
<%namespace name="coordinator_utils" file="coordinator_utils.mako" />


${ commonheader(_("Edit Coordinator"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='coordinators') }

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

          % if coordinator.coordinatorworkflow:
            <li class="nav-header">${ _('Workflow') }</li>
            <li id="workflowName"><a href="${ coordinator.coordinatorworkflow.get_absolute_url() }" target="_blank"><i class="fa fa-code-fork"></i> ${ coordinator.coordinatorworkflow}</a></li>
          % endif

          <li class="nav-header">${ _('Datasets') }</li>
          % if coordinator.is_editable(user):
          <li><a href="#createDataset"><i class="fa fa-plus"></i> ${ _('Create new') }</a></li>
          % endif
          <li><a href="#listDataset"><i class="fa fa-cloud"></i> ${ _('Show existing') }</a></li>

          % if coordinator.is_editable(user):
            <li class="nav-header">${ _('History') }</li>
            <li><a href="#listHistory"><i class="fa fa-archive"></i> ${ _('Show history') }</a></li>
          % endif

          % if coordinator:
            <li class="nav-header">${ _('Actions') }</li>
            <li><a id="submit-btn" href="javascript:void(0)" data-submit-url="${ url('oozie:submit_coordinator', coordinator=coordinator.id) }" title="${ _('Submit this coordinator') }" rel="tooltip" data-placement="right"><i class="fa fa-play"></i> ${ _('Submit') }</a></li>
            <li><a id="clone-btn" href="javascript:void(0)" data-clone-url="${ url('oozie:clone_coordinator', coordinator=coordinator.id) }" title="${ _('Copy this coordinator') }" rel="tooltip" data-placement="right"><i class="fa fa-files-o"></i> ${ _('Copy') }</a></li>
          % endif

        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${ _('Coordinator Editor : ') } ${ coordinator.name }</h1>
      <form id="jobForm" class="form-horizontal" action="${ url('oozie:edit_coordinator', coordinator=coordinator.id) }" method="POST">
      ${ csrf_token(request) | n,unicode }
      <div id="properties" class="section">
        <ul class="nav nav-pills">
          <li class="active"><a href="#step1" class="step">${ _('Step 1: General') }</a></li>
          <li><a href="#step2" class="step">${ _('Step 2: Frequency') }</a></li>
          <li><a href="#step3" class="step">${ _('Step 3: Inputs') }</a></li>
          <li><a href="#step4" class="step">${ _('Step 4: Outputs') }</a></li>
          <li><a href="#step5" class="step">${ _('Step 5: Advanced settings') }</a></li>
        </ul>

        ${ dataset_formset.management_form | n,unicode }
        ${ data_input_formset.management_form | n,unicode }
        ${ data_output_formset.management_form | n,unicode }
        ${ properties.init_viewmodel(coordinator) }

        <div class="steps">
          <div id="step1" class="stepDetails">
            <div class="alert alert-info"><h3>${ _('Schedule') }</h3></div>
            <div class="fieldWrapper">
              ${ utils.render_field_no_popover(coordinator_form['name'], extra_attrs = {'validate':'true'}) }
              ${ utils.render_field_no_popover(coordinator_form['description']) }
              ${ utils.render_field_no_popover(coordinator_form['coordinatorworkflow'], extra_attrs = {'validate':'true'}) }
              ${ coordinator_form['parameters'] | n,unicode }
              <div class="hide">
                ${ utils.render_field_no_popover(coordinator_form['is_shared']) }
                ${ utils.render_field(coordinator_form['timeout']) }
                ${ coordinator_form['schema_version']  | n,unicode }
              </div>
            </div>
          </div>

          <div id="step2" class="stepDetails hide">
            <div class="alert alert-info"><h3>${ _('Frequency') }</h3></div>
            <div class="fieldWrapper">
              <div class="row-fluid">
                <div class="alert alert-warning">
                  ${ _('UTC time only. (e.g. if you want 10pm PST (UTC+8) set it 8 hours later to 6am the next day.') }
                </div>
              </div>
            </div>
            <div class="fieldWrapper">
              % if enable_cron_scheduling:
                ${ coordinator_utils.frequency_fields() }
              % else:
                <div class="row-fluid">
                  <div class="span6">
                    ${ utils.render_field_no_popover(coordinator_form['frequency_number']) }
                  </div>
                  <div class="span6">
                    ${ utils.render_field_no_popover(coordinator_form['frequency_unit']) }
                  </div>
                </div>
              % endif
            </div>
            <div class="fieldWrapper">
              <div class="row-fluid">
                <div class="span6">
                ${ utils.render_field_no_popover(coordinator_form['start']) }
                </div>
                <div class="span6">
                ${ utils.render_field_no_popover(coordinator_form['end']) }
                </div>
              </div>
              ${ utils.render_field_no_popover(coordinator_form['timezone']) }
            </div>
          </div>

          <div id="step3" class="stepDetails hide">
            % if coordinator.coordinatorworkflow:
              <div class="alert alert-info"><h3>${ _('Inputs') }</h3>
              ${ _('The inputs and outputs of the workflow must be mapped to some data.') }
              ${ _('The data is represented by some datasets that can be created ') }<a href="#createDataset" class="btn btn-small">${ _('here') }</a>.
              </div>
            % else:
              <div class="alert alert-info"><h3>${ _('Inputs') }</h3></div>
              <div class="alert">${ _('This type of coordinator does not require any dataset.') }</div>
            % endif
            % if data_input_formset.forms:
              <table class="table table-condensed" cellpadding="0" cellspacing="0" data-missing="#dataset_input_missing">
                <thead>
                <tr>
                  <th width="10%">${ _('Name') }</th>
                  <th width="10%">${ _('Dataset') }</th>
                  <th>${ _('Path') }</th>
                % if coordinator.is_editable(user):
                  <th width="1%">${ _('Delete') }</th>
                % endif
                </tr>
                </thead>
                <tbody>
                % for form in data_input_formset.forms:
                <tr>
                  ${ form['id'] | n,unicode }
                  <td>${ form['name'] | n,unicode }</td>
                  <td>${ form['dataset'] | n,unicode }</td>
                  <td>${ form['dataset'].form.instance.dataset.uri }</td>
                % if coordinator.is_editable(user):
                  <td><a class="btn btn-small delete-row" href="javascript:void(0);">${ _('Delete') }${ form['DELETE'] | n,unicode }</a></td>
                % endif
                </tr>
                % endfor
                </tbody>
              </table>
            % endif
            <br/>
            <%
              klass = "alert alert-error"
              if data_input_formset.forms:
                klass += " hide"
            %>
            <div id="dataset_input_missing" data-missing-bind="true" class="${klass}">
              ${ _('There are currently no defined inputs.') }
            </div>

            % if coordinator.is_editable(user):
              ${ coordinator_data.print_datasets(_('Datasets'), 'dataset_input', new_data_input_formset, 'input', not len(data_input_formset.forms)) }
            % endif
          </div>

          <div id="step4" class="stepDetails hide">
            % if coordinator.coordinatorworkflow:
              <div class="alert alert-info"><h3>${ _('Outputs') }</h3>
                ${ _('The inputs and outputs of the workflow must be mapped to some data.') }
                ${ _('The data is represented by some datasets that can be created ') }<a href="#createDataset" class="btn btn-small">${ _('here') }</a>.
              </div>
            % else:
              <div class="alert alert-info"><h3>${ _('Outputs') }</h3></div>
              <div class="alert">${ _('This type of coordinator does not require any dataset.') }</div>
            % endif

            % if data_output_formset.forms:
            <table class="table table-condensed" cellpadding="0" cellspacing="0" data-missing="#dataset_output_missing">
              <thead>
                <tr>
                  <th width="10%">${ _('Name') }</th>
                  <th width="10%">${ _('Dataset') }</th>
                  <th>${ _('Path') }</th>
                  % if coordinator.is_editable(user):
                    <th width="1%">${ _('Delete') }</th>
                  % endif
                </tr>
              </thead>
              <tbody>
                % for form in data_output_formset.forms:
                  <tr>
                    ${ form['id'] | n,unicode }
                    <td>${ form['name'] | n,unicode }</td>
                    <td>${ form['dataset'] | n,unicode }</td>
                    <td>${ form['dataset'].form.instance.dataset.uri }</td>
                    % if coordinator.is_editable(user):
                      <td><a class="btn btn-small delete-row" href="javascript:void(0);">${ _('Delete') }${ form['DELETE'] | n,unicode }</a></td>
                    % endif
                  </tr>
                % endfor
              </tbody>
            </table>
            % endif
            <br/>
            <%
              klass = "alert alert-error"
              if data_output_formset.forms:
                klass += " hide"
            %>
            <div id="dataset_output_missing" data-missing-bind="true" class="${klass}">
            ${ _('There are currently no defined outputs.') }
            </div>

            % if coordinator.is_editable(user):
              ${ coordinator_data.print_datasets(_('Datasets'), 'dataset_output', new_data_output_formset, 'output', not len(data_output_formset.forms)) }
            % endif
          </div>

          <div id="step5" class="stepDetails hide">
            <div class="alert alert-info"><h3>${ _('Advanced settings') }</h3></div>
            <div id="properties-settings">
              ${ properties.print_key_value(coordinator_form['parameters'], 'parameters') }
              ${ properties.print_key_value(coordinator_form['job_properties'], 'job_properties') }
            </div>
              ${ utils.render_field(coordinator_form['timeout']) }
            <div class="row-fluid">
              <div class="span6">
                ${ utils.render_field(coordinator_form['concurrency']) }
              </div>
              <div class="span6">
                ${ utils.render_field(coordinator_form['throttle']) }
              </div>
            </div>

            ${ utils.render_field(coordinator_form['execution']) }
            ${ coordinator_form['schema_version'] | n,unicode }

            <div class="control-group">
              <label class="control-label">
                <a href="#" id="advanced-btn" onclick="$('#advanced-container').toggle('hide')">
                <i class="fa fa-share"></i> ${ _('Advanced') }</a>
              </label>
              <div class="controls"></div>
            </div>

            <div id="advanced-container" class="hide">
              <div id="slaEditord">
                <div class="control-group">
                  <label class="control-label">${ _('SLA Configuration') }</label>
                  <div class="controls">
                      ${ utils.slaForm() }
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <div class="form-actions" id="bottom-nav">
          <a id="backBtn" class="btn disabled">${ _('Back') }</a>
          <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
          % if coordinator.is_editable(user):
            <a class="btn btn-primary save" data-bind="visible: isSaveVisible()" style="margin-left: 30px">${ _('Save coordinator') }</a>
          % endif
        </div>

        </div>

        <div id="createDataset" class="section hide">
          <div class="alert alert-info"><h3>${ _('Create a new dataset') }</h3></div>
          <div class="alert alert-warning"><b>${ _('Warning') }</b>: ${ _('Save your modifications before creating a new dataset.') }</div>
          <div id="add-dataset-body">
            <%include file="create_coordinator_dataset.mako"/>
          </div>
          <div class="form-actions">
            <a href="#" class="btn btn-primary" id="add-dataset-btn">${ _('Create dataset') }</a>
          </div>
        </div>

        <div id="editDataset" class="section hide">
          <div class="alert alert-info"><h3>${ _('Edit dataset') }</h3></div>
          <div class="alert alert-warning"><b>${ _('Warning') }</b>: ${ _('Save your modifications before editing a dataset.') }</div>
          <div id="edit-dataset-body">
          </div>
          <div class="form-actions">
            <a href="#" class="btn btn-primary" id="update-dataset-btn">${ _('Update dataset') }</a>
            <a href="#listDataset" class="btn">${ _('Cancel') }</a>
          </div>
        </div>


        <div id="listDataset" class="section hide">
          <div class="alert alert-info"><h3>${ _('Existing datasets') }</h3></div>
          % if coordinator.id:
          <div>
            % if dataset_formset.forms:
            <table class="table table-condensed" cellpadding="0" cellspacing="0" data-missing="#dataset_missing">
              <thead>
                <tr>
                  <th>${ _('Name') }</th>
                  <th>${ _('Description') }</th>
                  <th>${ _('Frequency') }</th>
                  <th>${ _('Start') }</th>
                  <th>${ _('URI') }</th>
                  <th>${ _('Timezone') }</th>
                  <th>${ _('Done flag') }</th>
                  % if coordinator.is_editable(user):
                    <th>${ _('Delete') }</th>
                  % endif
                </tr>
              </thead>
              <tbody>
              % for form in dataset_formset.forms:
                % for hidden in form.hidden_fields():
                  ${ hidden | n,unicode }
                % endfor
                <tr title="${ _('Click to view the dataset') }" rel="tooltip">
                  <td>
                  % if coordinator.is_editable(user):
                    <a href="javascript:void(0)" class="editDataset" data-url="${ url('oozie:edit_coordinator_dataset', dataset=form.instance.id) }" data-row-selector="true"/>
                  % endif
                  ${ form.instance.name }
                  </td>
                  <td>${ form.instance.description }</td>
                  <td>${ form.instance.text_frequency }</td>
                  <td>${ form.instance.start }</td>
                  <td>${ form.instance.uri }</td>
                  <td>${ form.instance.timezone }</td>
                  <td>${ form.instance.done_flag }</td>
                  % if coordinator.is_editable(user):
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
            if dataset_formset.forms:
              klass += " hide"
          %>
          <div id="dataset_missing" data-missing-bind="true" class="${klass}">
            ${ _('There are currently no datasets.') } <a href="#createDataset">${ _('Do you want to create a new dataset ?') }</a>
          </div>
            % if dataset_formset.forms and coordinator.is_editable(user):
            <div class="form-actions" style="padding-left:10px">
              <a class="btn btn-primary save">${ _('Save coordinator') }</a>
            </div>
            % endif
          % endif
        </div>

        <div id="listHistory" class="section hide">
          <div class="alert alert-info"><h3>${ _('History') }</h3></div>
          % if coordinator.is_editable(user):
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

      </form>

    </div>
    </div>

  </div>

</div>

<div id="submit-job-modal" class="modal hide"></div>

<form class="form-horizontal" id="add-dataset-form"></form>
<form class="form-horizontal" id="edit-dataset-form"></form>

% if enable_cron_scheduling:
<link href="${ static('desktop/css/jqCron.css') }" rel="stylesheet" type="text/css" />
<script src="${ static('desktop/js/jqCron.js') }" type="text/javascript"></script>
% endif

<script type="text/javascript" src="${ static('oozie/js/coordinator.js') }"></script>


% if coordinator.id:
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

      % if not coordinator.is_editable(user):
        $("#jobForm input, select").attr("disabled", "disabled");
        $("#jobForm .btn").not("#nextBtn, #backBtn").attr("disabled", "disabled").addClass("btn-disabled");
      % endif

      $("#datasets-btn").click(function () {
        $('[href=\'#datasets\']').tab('show');
      });

      $('#add-dataset-btn').click(function () {
        $("#add-dataset-form").empty();
        window.viewModel.updateInstance();
        $("#add-dataset-body").find("input").each(function () {
          $(this).clone().appendTo($("#add-dataset-form"));
        });
        // select clone does not set a value! http://bugs.jquery.com/ticket/1294
        $("#add-dataset-body").find("select").each(function () {
          var _clone = $(this).clone();
          _clone.val($(this).val());
          _clone.appendTo($("#add-dataset-form"));
        });
        $.post("${ url('oozie:create_coordinator_dataset', coordinator=coordinator.id) }",
            $("#add-dataset-form").serialize(),
            function (response) {
              if (response['status'] != 0) {
                $("#add-dataset-form").empty();
                $('#add-dataset-body').html(response['data']);
                decorateDateTime();
                ko.cleanNode($('#add-dataset-body')[0]);
                ko.applyBindings(window.viewModel, $('#add-dataset-body')[0]);
              } else {
                window.location.replace(response['data']);
                window.location.reload();
              }
            }
        );
      });

      $(".editDataset").click(function () {
        var el = $(this);
        $.ajax({
          url:el.data("url"),
          beforeSend:function (xhr) {
            xhr.setRequestHeader("X-Requested-With", "Hue");
          },
          dataType:"json",
          success:function (response) {
            $("#edit-dataset-body").html(response['data']);
            decorateDateTime();
            ko.cleanNode($('#edit-dataset-body')[0]);
            $("#edit-dataset-body").data("url", el.data("url"));
            ko.applyBindings(window.viewModel, $('#edit-dataset-body')[0]);
            routie("editDataset");
          }
        });
      });

      $('#update-dataset-btn').click(function () {
        $("#edit-dataset-form").empty();
        window.viewModel.updateInstance();
        $("#edit-dataset-body").find("input, select").each(function () {
          // Don't clone as it is duplicating ids.
          $(this).appendTo($("#edit-dataset-form"));
        });
        $.post($("#edit-dataset-body").data("url"),
            $("#edit-dataset-form").serialize(),
            function (response) {
              if (response['status'] != 0) {
                $("#edit-dataset-form").empty();
                $('#edit-dataset-body').html(response['data']);
                decorateDateTime();
              } else {
                window.location.replace(response['data']);
                window.location.reload();
              }
            }
        );
      });

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

      $("a[data-row-selector='true']").jHueRowSelector();

      var slaModel = function() {
        var self = this;
        self.sla = ko.mapping.fromJS(${ coordinator.sla_jsescaped | n,unicode });
      };

      % if enable_cron_scheduling:
        ${ utils.cron_js() }
        initCoordinator(${ coordinator_frequency | n,unicode }, cron_i18n); // cron_i18n comes from utils.inc.mako
      % endif

      window.slaModel = new slaModel();
      ko.applyBindings(window.slaModel, document.getElementById('slaEditord'));

      window.viewModel.isSaveVisible = ko.observable(false);


      ko.applyBindings(window.viewModel, $('#bottom-nav')[0]);
      ko.applyBindings(window.viewModel, $('#properties-settings')[0]);
      ko.applyBindings(window.viewModel, $('#step3')[0]);
      ko.applyBindings(window.viewModel, $('#step4')[0]);
      ko.applyBindings(window.viewModel, $('#createDataset')[0]);

      $("*[rel=popover]").popover({
        placement:'top',
        trigger:'hover'
      });

      var currentStep = "step1";

      routie({
        "step1":function () {
          showStep("step1");
          window.viewModel.isSaveVisible(false);
        },
        "step2":function () {
          if (validateStep("step1")) {
            showStep("step2");
            window.viewModel.isSaveVisible(false);
          }
        },
        "step3":function () {
          if (validateStep("step1") && validateStep("step2")) {
            showStep("step3");
            window.viewModel.isSaveVisible(false);
          }
        },
        "step4":function () {
          if (validateStep("step1") && validateStep("step2")) {
            showStep("step4");
            window.viewModel.isSaveVisible(true);
          }
        },
        "step5":function () {
          if (validateStep("step1") && validateStep("step2")) {
            showStep("step5");
            window.viewModel.isSaveVisible(true);
          }
        },
        "properties":function () {
          showSection("properties");
        },
        "createDataset":function () {
          window.viewModel.reset();
          showSection("createDataset");
        },
        "editDataset":function () {
          if ($("#edit-dataset-body").children().length > 0) {
            showSection("editDataset");
          }
          else {
            routie("listDataset");
          }
        },
        "listDataset":function () {
          showSection("listDataset");
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

      $(".save").click(function () {
        window.viewModel.submit();
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

      $("a[rel='tooltip']").tooltip();
    });

    ${ utils.slaGlobal() }

  </script>
% endif

${ utils.decorate_datetime_fields() }

${ commonfooter(request, messages) | n,unicode }
