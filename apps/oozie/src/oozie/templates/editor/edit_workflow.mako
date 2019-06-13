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
<%namespace name="actions" file="action_utils.mako" />
<%namespace name="controls" file="control_utils.mako" />
<%namespace name="workflows" file="workflow_utils.mako" />

${ commonheader(_("Edit Workflow"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='workflows') }


<div id="workflow" class="container-fluid">
  <form class="form-horizontal" id="jobForm" method="POST">
  ${ csrf_token(request) | n,unicode }
  <div class="ribbon-wrapper hide">
    <div class="ribbon">${ _('Unsaved') }</div>
  </div>

  <div class="row-fluid">
  <div class="span2">
    <div id="workflowControls" class="sidebar-nav">
      <ul class="nav nav-list">
        <li class="nav-header">${ _('Editor') }</li>
        <li><a href="#editWorkflow"><i class="fa fa-code-fork"></i> ${ _('Workflow') }</a></li>
        <li><a href="#properties"><i class="fa fa-cog"></i> ${ _('Properties') }</a></li>
        % if user_can_edit_job:
          <li>
            <a data-bind="attr: {href: '/filebrowser/view=' + fixLeadingSlash(deployment_dir()) }" target="_blank" title="${ _('Go upload additional files and libraries to the deployment directory on HDFS') }" rel="tooltip" data-placement="right"><i class="fa fa-folder-open"></i> ${ _('Workspace') }</a>
          </li>
        % endif

        <li class="nav-header">${ _('Advanced') }</li>
        <li><a href="#importAction" title="${ _('Click to import an Oozie workflow action or Job Designer action') }" rel="tooltip" data-placement="right"><i class="fa fa-arrow-circle-o-down"></i> ${ _('Import action') }</a></li>
        % if user_can_edit_job:
          <li>
            <a title="${ _('Edit kill node') }" rel="tooltip" data-placement="right" href="#kill"><i class="fa fa-power-off"></i> ${ _('Kill node') }</a>
          </li>
        % endif

        % if user_can_edit_job:
          <li><a href="#listHistory"><i class="fa fa-archive"></i> ${ _('History') }</a></li>
        % endif

        <li class="nav-header">${ _('Actions') }</li>
        % if user_can_access_job:
          <li>
            <a id="submit-btn" href="javascript:void(0)" data-submit-url="${ url('oozie:submit_workflow', workflow=workflow.id) }" title="${ _('Submit this workflow') }" rel="tooltip" data-placement="right"><i class="fa fa-play"></i> ${ _('Submit') }</a>
          </li>
          <li>
            <a href="${ url('oozie:schedule_workflow', workflow=workflow.id) }" title="${ _('Schedule this workflow') }" rel="tooltip" data-placement="right"><i class="fa fa-calendar"></i> ${ _('Schedule') }</a>
          </li>
          <li>
            <a id="clone-btn" href="#" data-clone-url="${ url('oozie:clone_workflow', workflow=workflow.id) }" title="${ _('Copy this workflow') }" rel="tooltip" data-placement="right"><i class="fa fa-files-o"></i> ${ _('Copy') }</a>
          </li>
          <li>
            <a id="export-btn" href="${ url('oozie:export_workflow', workflow=workflow.id) }" title="${ _('Export this workflow') }" rel="tooltip" data-placement="right"><i class="fa fa-upload"></i> ${ _('Export') }</a>
          </li>
        % endif
      </ul>
    </div>
  </div>
  <div class="span10">
    <div id="properties" class="section hide">
    <div class="card card-small">

      <div class="alert alert-info"><h3 data-bind="text: name()"></h3></div>
      <div class="card-body">
        <p>
          <fieldset>
            ${ utils.render_field_with_error_js(workflow_form['name'], workflow_form['name'].name, extra_attrs={'data-bind': 'value: %s' % workflow_form['name'].name}) }
            ${ utils.render_field_with_error_js(workflow_form['description'], workflow_form['description'].name, extra_attrs={'data-bind': 'value: %s' % workflow_form['description'].name}) }
            <div class="hide">
              ${ utils.render_field_with_error_js(workflow_form['is_shared'], workflow_form['is_shared'].name, extra_attrs={'data-bind': 'checked: %s' % workflow_form['is_shared'].name}) }
            </div>

      <%
      workflows.key_value_field(workflow_form['parameters'].label, workflow_form['parameters'].help_text, {
      'name': 'parameters',
      'remove': '$root.removeParameter',
      'add': '$root.addParameter',
      })
      %>

      <%
      workflows.key_value_field(workflow_form['job_properties'].label, workflow_form['job_properties'].help_text, {
      'name': 'job_properties',
      'remove': '$root.removeJobProperty',
      'add': '$root.addJobProperty',
      })
      %>

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

        % if user_can_edit_job:
          ${ utils.render_field_with_error_js(workflow_form['deployment_dir'], workflow_form['deployment_dir'].name, extra_attrs={'data-bind': 'value: %s' % workflow_form['deployment_dir'].name}) }
        % endif

        ${ utils.render_field_with_error_js(workflow_form['job_xml'], workflow_form['job_xml'].name, extra_attrs={'data-bind': 'value: %s' % workflow_form['job_xml'].name}) }
      </div>

      </fieldset>
        </p>
      </div>
        </div>
    </div>

    <div id="editKill" class="section hide">
      <div class="card" style="padding-top:0; margin-top:0">
      <div class="alert alert-info">
        <h3>${ _('Kill node') }</h3>
        <p>${_('If the "to" field has content, then the workflow editor assumes that the defined email action is to be placed before the kill action.')}</p>
      </div>
      <div class="card-body">
        <p>
          <fieldset data-bind="with: context().node">
            <p>&nbsp;${_('Action enabled: ')} <i class="fa fa-check-square-o" data-bind="visible: to().length > 0"></i><i class="fa fa-square-o" data-bind="visible: to().length == 0"></i></p>

            % for form_info in action_forms:
              % if form_info[0] == 'email':
                ${ actions.action_form_fields(action_form=form_info[1], node_type=form_info[0], show_primary=False) }
              % endif
            % endfor
          </fieldset>
        </p>
      </div>
      </div>
    </div>

    <div id="importAction" class="section hide">
      <ul class="nav nav-tabs" style="margin-bottom: 0">
        <li class="active"><a href="#importJobsub" data-toggle="tab">${ _('Job Designer') }</a></li>
        <li><a href="#importOozie" data-toggle="tab">${ _('Oozie') }</a></li>
      </ul>
      <div class="card" style="margin-top: 0">
      <div class="tab-content">
        <div class="tab-pane active" id="importJobsub" data-bind="with: jobsub">
          <div class="alert alert-info">
            <h3>${ _('Import Action from Job Designer') }</h3>
            <p>${_('Click on a row to import the design as an action in the workflow. The action will be added to the beginning of the flow.')}</p>
          </div>
          <table id="jobsubActionsTable" class="table">
            <thead>
              <tr>
                <th>${ _('Name') }</th>
                <th>${ _('Description') }</th>
              </tr>
            </thead>
            <tbody data-bind="visible: workflows().length > 0, foreach: workflows">
              <tr class="action-row" rel="tooltip" title="${ _('Click to import action to workflow') }">
                <td>
                  <a href="javascript:void(0);" data-bind="text: $data.name"></a>
                </td>
                <td data-bind="text: $data.description"></td>
              </tr>
            </tbody>
            <tbody data-bind="visible: workflows().length == 0">
              <tr class="action-row">
                <td>${ _('N/A') }</td><td></td><td></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="tab-pane" id="importOozie" data-bind="with: oozie">
          <div class="alert alert-info"><h3>${ _('Import Action from Oozie') }</h3></div>
          <table id="oozieWorkflowsTable" class="table">
            <thead>
              <tr>
                <th>${ _('Name') }</th>
                <th>${ _('Description') }</th>
              </tr>
            </thead>
            <tbody data-bind="visible: workflows().length > 0, foreach: workflows">
              <tr class="action-row">
                <td>
                  <a href="javascript:void(0);" data-bind="text: $data.name"></a>
                </td>
                <td data-bind="text: $data.description"></td>
              </tr>
            </tbody>
            <tbody data-bind="visible: workflows().length == 0">
              <tr class="action-row">
                <td>${ _('N/A') }</td><td></td><td></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      </div>
    </div>

    <div id="importOozieAction" class="section hide" data-bind="if: selected_workflow()">
      <div class="alert alert-info">
        <h3>${ _('Import Action from Workflow: ') } <span data-bind="text: selected_workflow().name"></span></h3>
        <p>${_('Click on a row to import the action.')}</p>
      </div>
      <table id="oozieActionsTable" class="table">
        <thead>
          <tr>
            <th>${ _('Name') }</th>
            <th>${ _('Description') }</th>
          </tr>
        </thead>
        <tbody data-bind="visible: nodes().length > 0, foreach: nodes">
          <tr class="action-row" rel="tooltip" title="${ _('Click to import action to workflow') }">
            <td>
              <a href="javascript:void(0);" data-bind="text: $data.name"></a>
            </td>
            <td data-bind="text: $data.description"></td>
          </tr>
        </tbody>
        <tbody data-bind="visible: nodes().length == 0">
          <tr class="action-row">
            <td>${ _('N/A') }</td><td></td><td></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div id="editWorkflow" class="section hide">
      <div class="card" style="padding-top:0; margin-top:0">
      <div class="alert alert-info"><h3 data-bind="text: name()"></h3></div>
      <div class="card-body">
        <p>
      <div id="actionToolbar">
        <div class="draggable-button">
          <a data-node-type="mapreduce"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> MapReduce
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="streaming"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Streaming
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="java"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Java
          </a>
         </div>
        <div class="draggable-button">
          <a data-node-type="pig"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Pig
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="hive"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Hive
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="sqoop"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Sqoop
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="shell"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Shell
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="ssh"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Ssh
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="distcp"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> DistCp
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="fs"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Fs
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="email"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Email
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="subworkflow"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Sub-workflow
          </a>
        </div>
        <div class="draggable-button">
          <a data-node-type="generic"
             title="${ _('Drag and drop this action on the workflow') }" class="btn new-node-link">
            <i class="fa fa-arrows"></i> Generic
          </a>
        </div>
      </div>

      <div class="alert" data-bind="visible: nodes().length < 3">
        ${ _('No actions: drag some from the panel above') }
      </div>

      <div id="graph" class="row-fluid" data-bind="template: { name: function(item) { return item.view_template() }, foreach: nodes }"></div>
      <div id="new-node" class="row-fluid" data-bind="template: { name: 'nodeTemplate', 'if': new_node, data: new_node }"></div>

      </p>
    </div>
    </div>
    </div>

    <div id="listHistory" class="section hide">
      <div class="card" style="padding-top:0; margin-top:0">
        <div class="alert alert-info"><h3>${ _('History') }</h3></div>
        <div class="card-body">
          <p>
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
            % endif
          </p>
        </div>
      </div>
    </div>


  </div>
  </div>

  <div id="formActions" class="form-actions center">
  % if user_can_edit_job:
    <button data-bind="disable: workflow.read_only, visible: !workflow.read_only()" class="btn btn-primary" id="btn-save-wf">${ _('Save') }</button>
  % endif
    <a href="${ url('oozie:list_workflows') }" class="btn">${ _('Back') }</a>
  </div>
  </form>
</div>

<div id="node-modal" class="modal hide" data-bind="template: $data.template"></div>

<div id="confirmation" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title message"></h2>
  </div>
  <div class="modal-body">
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-primary" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>

<div id="runUnsaved" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('The workflow has some unsaved changes')}</h2>
  </div>
  <div class="modal-body">
    <p>
      ${_('Please save or undo your changes before submitting it.')}
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <a id="saveAndSubmitBtn" class="btn btn-primary" href="javascript:void(0);">${_('Save and submit')}</a>
  </div>
</div>


<div id="modal-window" class="modal hide fade"></div>

<div id="submit-wf-modal" class="modal hide"></div>


<script src="${ static('desktop/ext/js/codemirror-3.11.js') }"></script>
<link rel="stylesheet" href="${ static('desktop/ext/css/codemirror.css') }">
<script src="${ static('desktop/ext/js/codemirror-xml.js') }"></script>
<script src="${ static('desktop/ext/js/codemirror-closetag.js') }"></script>

<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="${ static('oozie/css/workflow.css') }">
<script type="text/javascript" src="${ static('oozie/js/workflow.utils.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.registry.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.modal.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.models.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.idgen.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.node-fields.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.node.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.js') }"></script>
<script type="text/javascript" src="${ static('oozie/js/workflow.import-node.js') }"></script>


% for form_info in action_forms:
  ${ actions.action_form_modal_template(action_form=form_info[1], node_type=form_info[0], template=True) }
% endfor

${ controls.fork_convert_form(node_type='fork', template=True, javascript_attrs={'convert': 'function(data, event) { $data.convertToDecision(); $data._workflow.rebuild(); }'}) }
${ controls.fork_edit_form(form=node_form, node_type='fork', template=True) }

${ controls.decision_form(node_form, link_form, default_link_form, 'decision', True) }

<script type="text/html" id="emptyTemplate"></script>

<script type="text/html" id="disabledNodeTemplate">
  <div class="node node-control row-fluid editor-action">
    <!-- ko if: node_type() == 'start' -->
      <ul class="nav nav-tabs" style="margin-bottom:0">
        <li class="active"><a data-toggle="tab" style="line-height:10px;background-color: #F9F9F9;"><i style="color:#DDD" class="fa fa-thumbs-up"></i> &nbsp;
          <strong style="color:#999" data-bind="text: node_type"></strong></a>
        </li>
      </ul>
      <div class="row-fluid">
        <div class="span12 action gradient" style="border:0"></div>
      </div>
    <!-- /ko -->
    <!-- ko if: node_type() == 'end' -->
      <div class="row-fluid">
        <div class="span12 action inverse_gradient" style="border:0"></div>
      </div>
      <div class="tabbable tabs-below">
        <ul class="nav nav-tabs" style="margin-bottom:0">
          <li class="active"><a data-toggle="tab" style="line-height:10px;background-color: #F9F9F9;"><i style="color:#DDD" class="fa fa-dot-circle-o"></i> &nbsp;
            <strong style="color:#999" data-bind="text: node_type"></strong></a>
          </li>
        </ul>
      </div>
    <!-- /ko -->
    <!-- ko if: links -->
      <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links }"></div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="nodeTemplate">
  <div class="node node-action row-fluid editor-action">
    <ul class="nav nav-tabs" style="margin-bottom:0">
      <li class="active"><a data-toggle="tab" style="line-height:10px;background-color: #F9F9F9;"><i style="color:#DDD" class="fa fa-cogs"></i> &nbsp;
        <strong style="color:#999" data-bind="text: node_type"></strong>
        &nbsp;&nbsp;
        <button type="button" class="btn btn-mini clone-node-btn" title="${ _('Copy') }" relz="tooltip"><i class="fa fa-files-o"></i></button>
        <button type="button" class="btn btn-mini delete-node-btn" title="${ _('Delete') }" relz="tooltip"><i class="fa fa-trash-o"></i></button>
      </a>
      </li>
    </ul>
    <div class="row-fluid">
      <div class="span12 action editor-action-body">
        <div class="pull-right" style="font-size: 30px; margin-top:14px; cursor:pointer"><a class="edit-node-link" title="${ _('Edit') }" relz="tooltip" data-bind="attr: { 'data-node-type': node_type() }"><i class="fa fa-pencil"></i></a></div>
        <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
        <div class="node-description muted" data-bind="text: description()"></div>
      </div>
    </div>
  </div>

  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links }"></div>
</script>

<script type="text/html" id="forkTemplate">
  <div class="node node-fork row-fluid">
    <div class="action span12">
      <ul class="nav nav-tabs" style="margin-bottom:0">
        <li class="active">
          <a class="action-link" data-toggle="tab" style="line-height:10px;background-color: #F9F9F9;">
            <i style="color:#DDD" class="fa fa-sitemap"></i> &nbsp; <strong style="color:#999" data-bind="text: node_type"></strong>
            &nbsp;&nbsp;
            <button type="button" class="btn btn-mini edit-node-link" title="${ _('Edit') }" relz="tooltip" data-bind="attr: { 'data-node-type': node_type() }"><i class="fa fa-pencil"></i></button>
            <button type="button" class="btn btn-mini convert-node-link" title="${ _('Convert to Decision') }" data-bind="attr: { 'data-node-type': node_type() }" relz="tooltip"><i class="fa fa-magic"></i></button>
          </a>
        </li>
      </ul>
      <div class="row-fluid">
        <div class="span12 action-link" style="text-align:left; padding:10px;border:1px solid #DDD; border-top:0">
          <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
          <div class="node-description muted" data-bind="text: description()"></div>
        </div>
      </div>
    </div>

    <div class="row-fluid node-fork-children">
      <div class="row-fluid node-fork-child" data-bind="foreach: children">
        <div data-bind="attr: {'class': 'span' + (((12 / $parent.children().length) > 4) ? (12 / $parent.children().length) : 4)}">
          <div class="row-fluid node-fork-child-link" data-bind="template: { name: 'linkTemplate', data: $parent.links()[$index()] }"></div>
          <div data-bind="template: { name: function(item) { return item.view_template() }, foreach: $data }"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="joinTemplate">
  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links() }"></div>
</script>

<script type="text/html" id="decisionTemplate">
  <div class="node node-decision row-fluid">
    <div class="action span12">
      <ul class="nav nav-tabs" style="margin-bottom:0">
        <li class="active">
          <a class="action-link" data-toggle="tab" style="line-height:10px;background-color: #F9F9F9;">
            <i style="color:#DDD" class="fa fa-magic"></i> &nbsp; <strong style="color:#999" data-bind="text: node_type"></strong>
            &nbsp;&nbsp;
            <button type="button" class="btn btn-mini edit-node-link" title="${ _('Edit') }" data-bind="attr: { 'data-node-type': node_type() }" relz="tooltip"><i class="fa fa-pencil"></i></button>
          </a>
        </li>
      </ul>
      <div class="row-fluid">
        <div class="span12 action-link" style="text-align:left; padding:10px;border:1px solid #DDD; border-top:0">
          <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
          <div class="node-description muted" data-bind="text: description()"></div>
        </div>
      </div>
    </div>

    <div class="row-fluid node-decision-children">
      <div class="row-fluid node-decision-child" data-bind="foreach: children">
        <div data-bind="attr: {class: 'span' + (((12 / $parent.children().length) > 4) ? (12 / $parent.children().length) : 4)}">
          <div class="row-fluid node-decision-child-link" data-bind="template: { name: 'linkTemplate', data: $parent.links()[$index()] }"></div>
          <div data-bind="template: { name: function(item) { return item.view_template() }, foreach: $data }"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="decisionEndTemplate">
  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links() }"></div>
</script>

<script type="text/html" id="linkTemplate">
  <div class="node-link">&nbsp;</div>
</script>

<script type="text/javascript">
/**
 * Component Initialization
 * Initialize the workflow, registry, modal, and import objects.
 */
 // Custom handlers for saving, loading, error checking, etc.
function interpret_server_error(data, premessage) {
  var message = premessage;
  if (data) {
    if (data.message) {
      message += ": " + data.message;
    }
  }
  return message;
}

function import_jobsub_load_success(data) {
  if (data.status == 0) {
    import_jobsub_action.initialize(data.data);
  } else {
    $(document).trigger("error", interpret_server_error(data, "${ _('Received invalid response from server') } "));
  }
}

function import_workflow_load_success(data) {
  if (data.status == 0) {
    import_workflow_action.initialize(data.data);
  } else {
    $(document).trigger("error", interpret_server_error(data, "${ _('Received invalid response from server') } "));
  }
}

function workflow_save_success(data) {
  if (data.status != 0) {
    $(document).trigger("error", interpret_server_error(data, "${ _('Could not save workflow') }"));
  } else {
    $(document).trigger("info", "${ _('Workflow saved') }");
    workflow.reload(data.data);
    workflow.is_dirty( false );
    workflow.loading( false );
    $("#btn-save-wf").button('reset');
  }
}

function workflow_save_error(jqXHR) {
  if (jqXHR.status !== 400) {
    $(document).trigger("error", interpret_server_error(jqXHR.responseJSON, "${ _('Could not save workflow') }"));
  } else {
    ko.mapping.fromJS(jqXHR.responseJSON.details.errors, workflow.errors);
    workflow.loading(false);
    $("#btn-save-wf").button('reset');
  }
}

function workflow_read_only_handler() {
  $(document).trigger("error", "${ _('Workflow is in read only mode.') }");
  workflow.loading(false);
}

var kill_view_model = null;
function workflow_load_success(data) {
  if (data.status == 0) {
    var workflow_model = new WorkflowModel(data.data);
    workflow.reload(workflow_model);

    //// Kill node
    kill_view_model = ManageKillModule($, workflow, nodeModelChooser, Node, NodeModel);
    ko.applyBindings(kill_view_model, $('#editKill')[0]);

  } else {
    $(document).trigger("error", interpret_server_error(data, "${ _('Error loading workflow') }"));
  }
  workflow.loading(false);
}

function workflow_load_error(jqXHR) {
  var data = jqXHR.responseJSON;
  $(document).trigger("error", interpret_server_error(jqXHR.responseJSON, "${ _('Error loading workflow') }"));
  workflow.loading(false);
}

function save_workflow(callback) {
  var _callbackFn = workflow_save_success;
  if (typeof callback != "undefined"){
    _callbackFn = callback;
  }
  workflow.loading(true);
  $("#btn-save-wf").button('loading');
  if (kill_view_model.enabled()) {
    if (kill_view_model.isValid()) {
      workflow.save({ success: _callbackFn, error: workflow_save_error });
    }
  } else {
    workflow.save({ success: _callbackFn, error: workflow_save_error });
  }
}

var OOZIE_CREDENTIALS = ${ credentials | n,unicode };

// Fetch workflow properties from server.
var workflow_model = new WorkflowModel({
  id: ${ workflow.id },
  name: "${ workflow.name }",
  description: "${ workflow.description }",
  start: ${ workflow.start.id },
  end: ${ workflow.end.id },
  job_xml: "${ workflow.job_xml }",
  deployment_dir: "${ workflow.deployment_dir }",
  is_shared: "${ workflow.is_shared }" == "True",
  parameters: ${ workflow.parameters_escapejs | n,unicode },
  job_properties: ${ workflow.job_properties_escapejs | n,unicode },
  data: ${ workflow.data_js_escaped | n,unicode }
});
var registry = new Registry();
var workflow = new Workflow({
  model: workflow_model,
  registry: registry,
  read_only: ${ str(not user_can_edit_job).lower() },
  read_only_error_handler: workflow_read_only_handler,
  el: '#editWorkflow'
});
var import_jobsub_action = new ImportJobsubAction({workflow: workflow});
var import_workflow_action = new ImportWorkflowAction({workflow: workflow});
var modal = new Modal($('#node-modal'));

// Fetch nodes
import_jobsub_action.fetchWorkflows({ success: import_jobsub_load_success });
import_workflow_action.fetchWorkflows({ success: import_workflow_load_success });
{
  var spinner = $('<img src="${ static('desktop/art/spinner.gif') }" />');
  workflow.loading.subscribe(function(value) {
    if (value) {
      $('#graph').append(spinner);
    } else {
      spinner.remove();
    }
  });
  workflow.loading(true);
  workflow.load({ success: workflow_load_success, error: workflow_load_error });
}

/**
 * Modals
 */
// Drag a new node onto the canvas
workflow.el.on('mousedown', '.new-node-link', function(e) {
  e.preventDefault();

  // Node starts off graph, then is validated/dropped onto graph, after being dragged onto graph.
  var node_type = $(this).attr('data-node-type');
  var NodeModel = nodeModelChooser(node_type);
  var model = new NodeModel({
    id: IdGeneratorTable[node_type].nextId(),
    node_type: node_type
  });
  var node = new Node(workflow, model, registry);
  workflow.registry.add(model.id, node);

  // Add to new node location, then drag and drop.
  workflow.new_node( node );
  workflow.draggables();

  // Reposition node to mouse pointer.
  var el = $("#new-node .node-action");
  var old_position = el.offset();

  // Trigger fake mousedown event to start dragging node.
  var is_dirty = workflow.is_dirty();
  el.offset({ top: e.pageY - el.height()/2, left: e.pageX - el.width()/10 });
  el.trigger($.Event("mousedown", {pageX: e.pageX, pageY: e.pageY, target: el[0], which: 1}));

  var cancel_edit = function(e) {
    // Didn't save, erase node.
    node.detach();
    node.erase();
    modal.hide();
    workflow.is_dirty( is_dirty );
    workflow.el.trigger('workflow:rebuild');
  };

  var try_save = function(e) {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
      if (!node.getErrorChild()) {
        node.putErrorChild(workflow.kill);
      }
      workflow.el.trigger('workflow:rebuild');
    }
  };

  // Remember to cleanup after.
  el.one('dragstop', function(e) {
    workflow.new_node(null);
    el.offset(old_position);
    if (node.findChildren().length > 0 || node.findParents().length > 1) {
      edit_node_modal(modal, workflow, node, try_save, cancel_edit);
    } else {
      node.erase();
    }
  });
});

// Modal for editing a node
workflow.el.on('click', '.edit-node-link', function(e) {
  var node = ko.contextFor(this).$data;
  edit_node_modal(modal, workflow, node);
});

// Modal for converting to a decision node
workflow.el.on('click', '.convert-node-link', function(e) {
  var node = ko.contextFor(this).$data;
  edit_node_modal(modal, workflow, node, null, null, 'forkConvertTemplate');
});

// Modal for cloning a node
workflow.el.on('click', '.clone-node-btn', function(e) {
  var node = ko.contextFor(this).$data;
  var model = node.toJS();
  model.id = IdGeneratorTable[model.node_type].nextId();
  model.name += '-copy';
  model.child_links = [];
  var new_node = new Node(workflow, model, workflow.registry);
  new_node.child_links.removeAll();
  workflow.registry.add(new_node.id(), new_node);

  var cancel_edit = function(e) {
    // Didn't save, erase node.
    new_node.erase();
    modal.hide();
  };

  var try_save = function(e) {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
      node.append(new_node);
      if (!new_node.getErrorChild()) {
        new_node.putErrorChild(workflow.kill);
      }
      workflow.el.trigger('workflow:rebuild');
    }
  };

  edit_node_modal(modal, workflow, new_node, try_save, cancel_edit);
});

// Modal for deleting a node
workflow.el.on('click', '.delete-node-btn', function(e) {
  var node = ko.contextFor(this).$data;
  $('#confirmation').find('h3').text('${ _('Confirm Delete') }');
  $('#confirmation').find('.modal-body').html('${ _('Are you sure you want to delete ') }<strong>' + node.name() + '</strong>?');
  $('#confirmation').find('.btn-primary').removeClass('btn-primary').addClass('btn-danger');
  $('#confirmation').find('.btn-danger').on('click', function () {
    node.detach();
    node.erase();
    workflow.rebuild();
    workflow.is_dirty(true);
    $('#confirmation').modal('hide');
    $('#confirmation').find('h3').text('');
    $('#confirmation').find('.modal-body').text('');
    $('#confirmation').find('.btn-danger').removeClass('btn-danger').addClass('btn-primary');
  });
  $('#confirmation').modal('show');
});

//// Import actions
var import_view_model = {
  jobsub: ko.observable(import_jobsub_action),
  oozie: ko.observable(import_workflow_action),
};

function importAction(workflow, model) {
  model.id = IdGeneratorTable[model.node_type].nextId();
  var node = new Node(workflow, model, workflow.registry);
  workflow.registry.add(model.id, node);

  // Add kill, add node to workflow as child of start.
  workflow.is_dirty( true );
  node.addChild(workflow.kill);
  workflow.registry.get(workflow.start()).append(node);
}

// Step 1 - Jobsub
// Select and import action
$('#importJobsub').on('click', '.action-row', function(e) {
  // Check ID to make sure we are not hitting N/A
  if ('id' in ko.contextFor($(this)[0]).$data) {
    // Select workflow, then fetch jobsub workflow.
    // Current KO context for clicked element should be the workflow.
    import_view_model.jobsub().selected_workflow(ko.contextFor($(this)[0]).$data);
    // Should only have 1 node since jobsub workflows are single node workflows.
    import_view_model.jobsub().fetchNodes({
      success: function(data) {
        if (data.status == 0) {
          import_view_model.jobsub().initialize({nodes: data.data.actions});

          // Remember, jobsub guarantees exactly one node.
          importAction(workflow, import_view_model.jobsub().nodes()[0]);

          workflow.el.trigger('workflow:rebuild');
          routie('editWorkflow');
          $(document).trigger("info", "${ _('Action imported at the top of the workflow.') } ");
        } else {
          $(document).trigger("error", interpret_server_error(data, "${ _('Received invalid response from server') }"));
        }
      }
    });
  }
});


// Step 1 - Oozie
// Select workflow
$('#importOozie').on('click', '.action-row', function(e) {
  // Check ID to make sure we are not hitting N/A
  if ('id' in ko.contextFor($(this)[0]).$data) {
    // Select workflow, then fetch oozie workflow.
    // Current KO context for clicked element should be the workflow.
    import_view_model.oozie().selected_workflow(ko.contextFor($(this)[0]).$data);
    import_view_model.oozie().fetchNodes({
      success: function(data) {
        if (data.status == 0) {
          import_view_model.oozie().initialize({nodes: data.data.actions});
          routie('importAction/oozie');
        } else {
          $(document).trigger("error", interpret_server_error(data, "${ _('Received invalid response from server') }"));
        }
      }
    });
  }
});

// Step 2 - Oozie
// Select and import action
$('#importOozieAction').on('click', '.action-row', function(e) {
  // Check ID to make sure we are not hitting N/A
  if ('id'  in ko.contextFor($(this)[0]).$data) {
    // Current KO context for clicked element should be the action
    importAction(workflow, ko.contextFor($(this)[0]).$data);

    workflow.el.trigger('workflow:rebuild');
    routie('editWorkflow');
    $(document).trigger("info", "${ _('Action imported at the top of the workflow.') }");
  }
});

// Bindings
ko.bindingHandlers.fileChooser = {
  init: function(element, valueAccessor, allBindings, model) {
    var self = $(element);
    self.after(hueUtils.getFileBrowseButton(self, true));
  }
};

ko.applyBindings(workflow, workflow.el[0]);
ko.applyBindings(workflow, $('#formActions')[0]);
ko.applyBindings(workflow, $('#properties')[0]);
ko.applyBindings(workflow, $('#workflowControls')[0]);
ko.applyBindings(import_view_model, $('#importAction')[0]);
ko.applyBindings(import_view_model.oozie(), $('#importOozieAction')[0]);


window.onbeforeunload = function (e) {
  if (workflow.is_dirty()) {
    var message = "${ _('You have unsaved changes in this workflow.') }";

    if (!e) e = window.event;
    e.cancelBubble = true;
    e.returnValue = message;

    if (e.stopPropagation) {
      e.stopPropagation();
      e.preventDefault();
    }
    return message;
  }
};

window.onresize = function () {
  if (modal) {
    modal.recenter(280, 0);
  }
};

function fixLeadingSlash(path) {
  if (path[0] != "/") {
    return "/" + path;
  }
  return path;
}

var AUTOCOMPLETE_PROPERTIES;

$(document).ready(function () {

  routie('editWorkflow');

  $("a[data-row-selector='true']").jHueRowSelector();

  var actionToolbarProperties = {
    docked: false,
    detachPosition: 0,
    initialWidth: 0
  }

  $(window).scroll(function () {
    if (!actionToolbarProperties.docked && ($('#actionToolbar').offset().top - 82 - $(window).scrollTop() < 0)) {
      $('#actionToolbar').addClass('shadowed');
      $('#actionToolbar').css('position', 'fixed');
      $('#actionToolbar').css('top', '82px');
      $('#graph').css('marginTop', ($('#actionToolbar').outerHeight() + 38) + 'px');
      $('#actionToolbar').width(actionToolbarProperties.initialWidth);
      actionToolbarProperties.detachPosition = $(window).scrollTop();
      actionToolbarProperties.docked = true;
    }
    else if (actionToolbarProperties.docked && $(window).scrollTop() < actionToolbarProperties.detachPosition) {
      $('#actionToolbar').removeClass('shadowed');
      $('#actionToolbar').css('position', '');
      $('#graph').css('marginTop', '');
      actionToolbarProperties.docked = false;
    }
    else {
      if (actionToolbarProperties.initialWidth == 0) {
        actionToolbarProperties.initialWidth = $('#actionToolbar').width();
      }
    }
  });

  window.setInterval(checkModelDirtiness, 500, 'oozie_workflow');
  $('#clone-btn').on('click', function () {
    var _url = $(this).data('clone-url');
    $.post(_url, function (data) {
      window.location = data.url;
    }).fail(function(){
      $(document).trigger("error", "${ _('There was a problem copying this workflow.') }");
    });
  });

  $('#submit-btn').on('click', function () {
    if (workflow.is_dirty()) {
      $("#runUnsaved").modal();
      $("#runUnsaved").data("submit-url", $(this).data('submit-url'));
    }
    else {
      submitWorkflow($(this).data('submit-url'));
    }
  });

  $("#saveAndSubmitBtn").on("click", function () {
    $("#runUnsaved").modal("hide");
    save_workflow(function (data) {
      workflow_save_success(data);
      submitWorkflow($("#runUnsaved").data('submit-url'));
    });
  });

  $('#btn-save-wf').on("click", function() {
    save_workflow();
    return false;
  });

  function submitWorkflow(url) {
    $.get(url, function (response) {
        $('#submit-wf-modal').html(response);
        $('#submit-wf-modal').modal('show');
      }
    ).fail(function(){
      $(document).trigger("error", "${ _('There was a problem submitting this workflow.') }");
    });
  }

  routie({
    'properties':function () {
      showSection('properties');
    },
    'kill':function() {
      showSection('editKill');
    },
    'importAction':function() {
      $("#importAction *[rel=tooltip]").tooltip();
      showSection('importAction');
    },
    'importAction/oozie':function() {
      $("#importOozieAction *[rel=tooltip]").tooltip();
      showSection('importOozieAction');
    },
    'editWorkflow':function() {
      showSection('editWorkflow');
    },
    'listHistory':function () {
      showSection('listHistory');
    }
  });

  function highlightMenu(section) {
    $('.nav-list li').removeClass('active');
    if (section == 'importOozieAction') {
      section = 'importAction';
    }
    $('a[href="#' + section + '"]:first').parent().addClass('active');
  }

  function showSection(section) {
    $('.section').hide();
    $('#' + section).show();
    highlightMenu(section);
    $(window).scrollTop(0);
    if (section == 'editWorkflow') {
      $('#actionToolbar').removeClass('shadowed');
      $('#actionToolbar').css('position', '');
      $('#graph').css('marginTop', '');
      actionToolbarProperties.docked = false;
      if (actionToolbarProperties.initialWidth == 0) {
        actionToolbarProperties.initialWidth = $('#actionToolbar').width();
      }
    }
  }

  // load the autocomplete properties
  $.getJSON("${ url('oozie:autocomplete_properties') }", function (data) {
    AUTOCOMPLETE_PROPERTIES = data.properties;
  });
});

function checkModelDirtiness() {
  if (workflow.is_dirty()) {
    $('.ribbon-wrapper').fadeIn();
  } else {
    $('.ribbon-wrapper').hide();
  }
}

${ utils.slaGlobal() }

</script>

${ utils.path_chooser_libs(True) }


<script>
  $(document).ready(function(){
    $("input[name='job_xml']").next().remove();
    $("input[name='job_xml']").after(hueUtils.getFileBrowseButton($("input[name='job_xml']"), false));
  });
</script>

${ commonfooter(request, messages) | n,unicode }
