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
<%namespace name="properties" file="job_action_properties.mako" />

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='workflows') }


<div class="container-fluid">
  <h1>${ _('Workflow') } ${ workflow.name }</h1>

  <div class="well">
    ${ _('Description:') } ${ workflow.description or "N/A" }
    <div class="pull-right" style="margin-top:-5px">
      % if user_can_edit_job:
        <label>
            <a href="/filebrowser/view${ workflow.deployment_dir }" class="btn">
              ${ _('Upload') }
            </a>
            ${ _('files to deployment directory') }
        </label>
      % endif
    </div>
  </div>

  <ul class="nav nav-tabs">
    <li class="active"><a href="#editor" data-toggle="tab">${ _('Editor') }</a></li>
    <li><a href="#properties" data-toggle="tab">${ _('Properties') }</a></li>
    % if user_can_edit_job:
      <li><a href="#history" data-toggle="tab">${ _('History') }</a></li>
    % endif
  </ul>

  <form class="form-horizontal" id="jobForm" action="${ url('oozie:edit_workflow', workflow=workflow.id) }" method="POST">

    <div class="tab-content">
      <div class="tab-pane active" id="editor">
        <div class="row-fluid">
          <div class="span2">
            % if user_can_edit_job:
            <h2>${ _('Actions') }</h2>
            <br/>
            <ul class="nav nav-tabs">
              <li class="active">
                <a href="#add" data-toggle="tab">${ _('Add') }</a>
              </li>
              <li>
                <a href="#import" data-toggle="tab">${ _('Import') }</a>
              </li>
             </ul>

            <div class="tab-content">
              <div class="tab-pane active" id="add">
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='mapreduce', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('MapReduce') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='streaming', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Streaming') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='java', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Java') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='pig', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Pig') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='hive', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Hive') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='sqoop', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Sqoop') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='shell', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Shell') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='ssh', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('Ssh') }
                </a>
                <p/>
                <p>
                <a href="${ url('oozie:new_action', workflow=workflow.id, node_type='distcp', parent_action_id=workflow.end.get_parents()[0].id) }"
                  title="${ _('Click to add to the end') }" class="btn">
                  <i class="icon-plus"></i> ${ _('DistCp') }
                </a>
                <p/>
              </div>
              <div class="tab-pane" id="import">
                <p>
                <a href="javascript:void(0);" title="${ _('Click to add to the end') }" class="btn modalWindow"
                  data-modal-url="${ url('oozie:import_action', workflow=workflow.id, parent_action_id=workflow.end.get_parents()[0].id) }"
                  data-modal-id="#modal-window">
                  <i class="icon-plus"></i> ${ _('Job Design') }
                </a>
                <p/>
              </div>
            </div>
            % endif
          </div>

          <div class="span9">
            <h2>${ _('Flow') }</h2>
            <br/>

            ${ actions_formset.management_form }

            <hr/>

            % if workflow.node_set.count() == 3:
              <div style="padding-top:50px">
                ${ _('No actions: add some from the right panel') }
              </div>
            % endif

            ${ graph }
          </div>
        </div>
        <div class="form-actions center">
          <a href="${ url('oozie:list_workflows') }" class="btn">${ _('Back') }</a>
        </div>
      </div>

      <div class="tab-pane" id="properties">
        <div class="row-fluid">
          <div class="span1"></div>
          <div class="span8">
            <h2>${ _('Properties') }</h2>
            <br/>
              <fieldset>
                ${ utils.render_field(workflow_form['name']) }
                ${ utils.render_field(workflow_form['description']) }
                ${ utils.render_field(workflow_form['is_shared']) }

                <div class="control-group ">
                  <label class="control-label">
                    <a href="#" id="advanced-btn" onclick="$('#advanced-container').toggle('hide')">
                      <i class="icon-share-alt"></i> ${ _('advanced') }</a>
                  </label>
                  <div class="controls"></div>
                </div>

               <div id="advanced-container" class="hide">
                 % if user_can_edit_job:
                   ${ utils.render_field(workflow_form['deployment_dir']) }
                 % endif
                 ## to remove
                 ${ properties.print_key_value(workflow_form['parameters'], 'parameters', parameters) }
                 ${ workflow_form['parameters'] }
                 ## to remove
                 ${ properties.print_key_value(workflow_form['job_properties'], 'job_properties', job_properties) }
                 ${ workflow_form['job_properties'] }
                 ${ workflow_form['schema_version'] }
                 % if user_can_edit_job:
                   ${ utils.render_field(workflow_form['job_xml']) }
                 % endif
               </div>

             </fieldset>
           </div>
        </div>
        <div class="form-actions center">
          <a href="${ url('oozie:list_workflows') }" class="btn">${ _('Back') }</a>
          % if user_can_edit_job:
            <button class="btn btn-primary">${ _('Save') }</button>
          % endif
        </div>
        <div class="span3"></div>
      </div>

      % if user_can_edit_job:
        <div class="tab-pane" id="history">
          % if not history:
            ${ _('N/A') }
          % else:
          <table class="table">
            <thead>
              <tr>
                <th>${ _('Date') }</th>
                <th>${ _('Id') }</th>
              </tr>
            </thead>
            <tbody>
              % for record in history:
                <tr>
                  <td>
                    <a href="${ url('oozie:list_history_record', record_id=record.id) }" data-row-selector="true"></a>
                    ${ utils.format_date(record.submission_date) }
                  </td>
                  <td>${ record.oozie_job_id }</td>
                </tr>
              % endfor
            </tbody>
          </table>
          % endif
        </div>
      % endif
    </div>
  </form>
</div>


<div id="confirmation" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3 class="message"></h3>
  </div>
  <div class="modal-footer">
    <a class="btn primary" href="javascript:void(0);">${_('Yes')}</a>
    <a href="#" class="btn secondary" data-dismiss="modal">${_('No')}</a>
  </div>
</div>


<div id="modal-window" class="modal hide fade"></div>


<style type="text/css">
modal-window .modal-content {
  height: 300px;
  overflow: auto;
}
</style>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  confirmed = false;
  $(document).ready(function(){
    $(".action-link").click(function(){
      window.location = $(this).attr('data-edit');
    });

    $("*[name=delete_action]").click(function(){
      if (!confirmed) {
        var _this = $(this);
        $("#confirmation .message").text('${ _("Are you sure you would like to delete this action?") }');
        $("#confirmation").modal("show");
        $("#confirmation a.primary").click(function() {
          confirmed = true;
          _this.trigger('click');
        });
      }
      return confirmed;
    });

    $(".modalWindow").click(function(){
      var _this = $(this);
      $.ajax({
        url: _this.attr("data-modal-url"),
        beforeSend: function(xhr){
          xhr.setRequestHeader("X-Requested-With", "Hue");
        },
        dataType: "html",
        success: function(data){
          var id = _this.attr("data-modal-id");
          $(id).html(data);
          $(id).modal("show");
        }
      });
    });

    ko.applyBindings(window.viewModelparameters, $("#parameters")[0]);
    ko.applyBindings(window.viewModeljob_properties, $("#job_properties")[0]);

    $('#jobForm').submit(function() {
      window.viewModelparameters.pre_submit();
      window.viewModeljob_properties.pre_submit();
    })

    $("a[data-row-selector='true']").jHueRowSelector();

    $("*[rel=popover]").popover({
      placement: 'right',
      trigger: 'hover'
    });
  });
</script>

${ utils.path_chooser_libs(True) }

${ commonfooter(messages) }
