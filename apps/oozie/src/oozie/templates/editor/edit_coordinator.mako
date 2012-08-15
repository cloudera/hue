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

${ commonheader(_("Oozie App"), "oozie", "100px") }
${ layout.menubar(section='coordinators') }


<div class="container-fluid">
    <h1>${ _('Coordinator') } ${ coordinator.name }</h1>

    <div class="well">
      ${ _('Description') }: ${ coordinator.description or _("N/A") }
      % if coordinator.workflow:
      <br/>
        ${ _('Workflow') }: <a href="${ coordinator.workflow.get_absolute_url() }">${ coordinator.workflow }</a>
      % endif
    </div>

    <ul class="nav nav-tabs">
        <li class="active"><a href="#editor" data-toggle="tab">${ _('Editor') }</a></li>
        <li><a href="#datasets" data-toggle="tab">${ _('Datasets') }</a></li>
        <li><a href="#history" data-toggle="tab">${ _('History') }</a></li>
    </ul>

% if coordinator.id:
  <form class="form-horizontal" id="workflowForm" action="${ url('oozie:edit_coordinator', coordinator=coordinator.id) }" method="POST">
  % else:
  <form class="form-horizontal" id="workflowForm" action="${ url('oozie:edit_coordinator') }" method="POST">
  % endif

    <div class="tab-content">
      <div class="tab-pane active" id="editor">
      <div class="row-fluid">
          <div class="span2">
          </div>
          <div class="span8">
             <h2>${ _('Coordinator') }</h2>
             <div class="fieldWrapper">
               ${ utils.render_field(coordinator_form['name']) }
               ${ utils.render_field(coordinator_form['description']) }
               ${ utils.render_field(coordinator_form['workflow']) }
             </div>

            <hr/>
            <h2>${ _('Frequency') }</h2>

            <div class="fieldWrapper">
                  <div class="row-fluid">
                    <div class="span6">
                    ${ utils.render_field(coordinator_form['frequency_number']) }
                  </div>
                  <div class="span6">
                    ${ utils.render_field(coordinator_form['frequency_unit']) }
                  </div>
                </div>
            </div>

            <div class="fieldWrapper">
                <div class="row-fluid">
                  <div class="span6">
                ${ utils.render_field(coordinator_form['start']) }
              </div>
                <div class="span6">
                  ${ utils.render_field(coordinator_form['end']) }
                 </div>
              </div>
              ${ utils.render_field(coordinator_form['timezone']) }
            </div>

              ${ dataset_formset.management_form }
              ${ data_input_formset.management_form }
              ${ data_output_formset.management_form }

            % if coordinator.id:
              <hr/>
              <h2>Data</h2>
                <br/>
              <p>
                % if coordinator.workflow:
                  ${ _('The inputs and outputs of the workflow need to be mapped to some data on the') }
                  <a href="#" id="datasets-btn" class="btn">${ _('Datasets page') }</a>
                % endif
              </p>
              </br>
                <div class="row-fluid">
                  <h3>${ _('Inputs') }</h3>

                  % if data_input_formset.forms:
                  <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
                    <thead>
                      <tr>
                        <th>${ _('Name') }</th>
                        <th>${ _('Dataset') }</th>
                        <th>${ _('Path') }</th>
                        <th>${ _('Delete') }</th>
                      </tr>
                    </thead>
                    <tbody>
                      % for form in data_input_formset.forms:
                        <tr>
                           ${ form['id'] }
                           <td>${ form['name'] }</td>
                           <td>${ form['dataset'] }</td>
                           <td>${ form['dataset'].form.instance.dataset.uri }</td>
                           <td>${ form['DELETE'] }</td>
                        </tr>
                      % endfor
                    </tbody>
                  </table>
                  % else:
                    <br/>
                    <div class="alert alert-error">
                      ${ _('No inputs') }
                    </div>
                  % endif

                 <a class="btn" data-toggle="modal" href="#add-data-input-modal">${ _('Add') }</a>
                </div>

              <br/>

                <div class="row-fluid">
                  <h3>${ _('Outputs') }</h3>

                  % if data_output_formset.forms:
                  <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
                    <thead>
                      <tr>
                        <th>${ _('Name') }</th>
                        <th>${ _('Dataset') }</th>
                        <th>${ _('Path') }</th>
                        <th>${ _('Delete') }</th>
                      </tr>
                    </thead>
                    <tbody>
                      % for form in data_output_formset.forms:
                        <tr>
                           ${ form['id'] }
                           <td>${ form['name'] }</td>
                           <td>${ form['dataset'] }</td>
                           <td>${ form['dataset'].form.instance.dataset.uri }</td>
                           <td>${ form['DELETE'] }</td>
                        </tr>
                      % endfor
                    </tbody>
                  </table>
                  % else:
                    <br/>
                    <div class="alert alert-error">
                      ${ _('No outputs') }
                    </div>
                  % endif

                  <a class="btn" data-toggle="modal" href="#add-data-output-modal">${ _('Add') }</a>
                </div>
            % endif
         </div>
      </div>
      </div>

      <div class="tab-pane" id="datasets">
        <div class="row-fluid">
            <div class="span1">
              <table>
                <thead>
                  <tr>
                    <th>${ _('Add a new dataset') }</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><br/><a class="btn" data-toggle="modal" href="#add-dataset-modal">${ _('Create') }</a></td>
                  </tr>
                </tbody>
              </table>


            </div>
            <div class="span10">
              % if coordinator.id:
                <div>
              <table class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
                <thead>
                  <tr>
                    <th>${ _('Pick dataset as input/output') }</th>
                    <th>${ _('Name') }</th>
                    <th>${ _('Description') }</th>
                    <th>${ _('Frequency') }</th>
                    <th>${ _('Start') }</th>
                    <th>${ _('Uri') }</th>
                    <th>${ _('Timezone') }</th>
                    <th>${ _('Done flag') }</th>
                    <th>${ _('Delete') }</th>
                  </tr>
                </thead>
                <tbody>
                 % for form in dataset_formset.forms:
                  % for hidden in form.hidden_fields():
                    ${ hidden }
                  % endfor
                  <tr>
                    <td>
                      <a class="btn" data-toggle="modal" href="#add-data-input-modal">${ _('input') }</a>
                      <a class="btn" data-toggle="modal" href="#add-data-output-modal">${ _('output') }</a>
                      </td>
                    <td>${ form.instance.name }</td>
                    <td>${ form.instance.description }</td>
                    <td>${ form.instance.text_frequency }</td>
                    <td>${ form.instance.start }</td>
                    <td>${ form.instance.uri }</td>
                    <td>${ form.instance.timezone }</td>
                    <td>${ form.instance.done_flag }</td>
                    <td>${ form['DELETE'] }</td>
                  </tr>

                   <div class="hide">
                      % for field in form.visible_fields():
                              ${ field.errors }
                              ${ field.label }: ${ field }
                      % endfor
                      </div>

                 % endfor
                </tbody>
              </table>
             </div>
                % if not dataset_formset.forms:
                  <div class="alert alert-error">
                    ${ _('No datasets') }
                  </div>
                % endif
              % endif
            </div>
          </div>
      </div>

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
              ${ _('N/A') }
            % endif
            % for record in history:
                <tr>
                  <td><a href="${ url('oozie:list_history_record', record_id=record.id) }" data-row-selector="true"></a>${ record.submission_date }</td>
                  <td>${ record.oozie_job_id }</td>
                </tr>
            % endfor
          </tbody>
        </table>
      </div>

      <br/>

    </div>

    <div class="form-actions center">
      <a href="${ url('oozie:list_coordinator') }" class="btn">${ _('Back') }</a>
      <input class="btn btn-primary" type="submit" value="${ _('Save') }"></input>
    </div>

  </form>

% if coordinator.id:
  <div class="modal hide" id="add-dataset-modal" style="z-index:1500;width:850px">
    <form class="form-horizontal" id="add-dataset-form">
      <div class="modal-header">
        <button class="close" data-dismiss="modal">&times;</button>
        <h3>${ _('Create a dataset') }</h3>
      </div>

      <div class="modal-body" id="add-dataset-body">
          <%include file="create_coordinator_dataset.mako"/>
      </div>

      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${ _('Close') }</a>
        <a href="#" class="btn btn-primary" id="add-dataset-btn">${ _('Add dataset') }</a>
      </div>
    </form>
  </div>

  <div class="modal hide" id="add-data-input-modal">
    <form class="form-horizontal" id="add-data-input-form">
        <div class="modal-header">
          <button class="close" data-dismiss="modal">&times;</button>
          <h3>${ _('Create a data input') }</h3>
        </div>

        <div class="modal-body" id="add-data-input-body">
            <%include file="create_coordinator_data.mako" args="form=data_input_form"/>
        </div>

        <div class="modal-footer">
          <a href="#" class="btn" data-dismiss="modal">${ _('Close') }</a>
          <a href="#" class="btn btn-primary" id="add-data-input-btn">${ _('Add data input') }</a>
        </div>
    </form>
  </div>

  <div class="modal hide" id="add-data-output-modal">
    <form class="form-horizontal" id="add-data-output-form">
        <div class="modal-header">
          <button class="close" data-dismiss="modal">&times;</button>
          <h3>${ _('Create a data output') }</h3>
        </div>

        <div class="modal-body" id="add-data-output-body">
            <%include file="create_coordinator_data.mako" args="form=data_output_form"/>
        </div>

        <div class="modal-footer">
          <a href="#" class="btn" data-dismiss="modal">${ _('Close') }</a>
          <a href="#" class="btn btn-primary" id="add-data-output-btn">${ _('Add data output') }</a>
        </div>
    </form>
  </div>
</div>

<script src="/static/ext/js/knockout-2.0.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function() {
      $("#datasets-btn").click(function() {
        $('[href=#datasets]').tab('show');
      });

      $('#add-dataset-btn').click(function() {
        $.post("${ url('oozie:create_coordinator_dataset', coordinator=coordinator.id) }",
          $("#add-dataset-form").serialize(),
          function(response) {
            if (response['status'] != 0) {
              $('#add-dataset-body').html(response['data']);
            } else {
              window.location.replace(response['data']);
            }
          }
        );
     });

    $('#add-data-input-btn').click(function() {
      $.post("${ url('oozie:create_coordinator_data', coordinator=coordinator.id, data_type='input') }",
        $("#add-data-input-form").serialize(),
          function(response) {
            if (response['status'] != 0) {
              $('#add-data-input-body').html(response['data']);
            } else {
              window.location.replace(response['data']);
            }
          }
        );
     });

    $('#add-data-output-btn').click(function() {
      $.post("${ url('oozie:create_coordinator_data', coordinator=coordinator.id, data_type='output') }",
        $("#add-data-output-form").serialize(),
          function(response) {
            if (response['status'] != 0) {
              $('#add-data-output-body').html(response['data']);
            } else {
              window.location.replace(response['data']);
            }
          }
        );
     });

     $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>

% endif

${commonfooter(messages)}
