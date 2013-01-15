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
  from django.template.defaultfilters import escapejs
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="actions" file="action_utils.mako" />
<%namespace name="controls" file="control_utils.mako" />
<%namespace name="workflows" file="workflow_utils.mako" />

${ commonheader(_("Oozie App"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='workflows') }


<div id="workflow" class="container-fluid">
  <div class="ribbon-wrapper hide">
    <div class="ribbon">${ _('Unsaved') }</div>
  </div>

  <h1 data-bind="text: '${ _('Workflow Editor : ') } ' + name()"></h1>

  <div class="well">
    <span data-bind="text: '${ _('Description') }: ' + description() || 'N/A'"></span>
    <div class="pull-right" style="margin-top:-5px">
      % if user_can_edit_job:
        <label>
            <a data-bind="attr: {href: '/filebrowser/view' + deployment_dir() }" class="btn">
              ${ _('Upload') }
            </a>
            ${ _('files to deployment directory.') }
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

  <form class="form-horizontal" id="jobForm" method="POST">

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
                <a data-node-type="mapreduce"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('MapReduce') }
                </a>
                <p/>
                <p>
                <a data-node-type="streaming"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> Streaming
                </a>
                <p/>
                <p>
                <a data-node-type="java"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Java') }
                </a>
                <p/>
                <p>
                <a data-node-type="pig"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Pig') }
                </a>
                <p/>
                <p>
                <a data-node-type="hive"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Hive') }
                </a>
                <p/>
                <p>
                <a data-node-type="sqoop"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Sqoop') }
                </a>
                <p/>
                <p>
                <a data-node-type="shell"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Shell') }
                </a>
                <p/>
                <p>
                <a data-node-type="ssh"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Ssh') }
                </a>
                <p/>
                <p>
                <a data-node-type="distcp"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('DistCp') }
                </a>
                <p/>
                <p>
                <a data-node-type="fs"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Fs') }
                </a>
                <p/>
                <p>
                <a data-node-type="email"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Email') }
                </a>
                <p/>
                <p>
                <a data-node-type="subworkflow"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Sub-workflow') }
                </a>
                <p/>
                <p>
                <a data-node-type="generic"
                  title="${ _('Click to add to the end of the workflow') }" class="btn new-node-link">
                  <i class="icon-plus"></i> ${ _('Generic') }
                </a>
                <p/>
              </div>
              <div class="tab-pane" id="import">
                <p>
                <a title="${ _('Click to add to the end of the workflow') }" class="btn import-jobsub-node-link">
                  <i class="icon-plus"></i> ${ _('Job Designer Workflow') }
                </a>
                <p/>
              </div>
            </div>
             % endif
          </div>

          <div class="span9">
            <h2>${ _('Flow') }</h2>
            <br/>
            <hr/>

            <div style="padding-top:50px" data-bind="visible: nodes().length < 3">
              ${ _('No actions: add some from the right panel') }
            </div>

            <div id="graph" class="row-fluid" data-bind="template: { name: function(item) { return item.view_template() }, foreach: nodes }"></div>
            <div id="new-node" class="row-fluid" data-bind="template: { name: 'nodeTemplate', if: new_node, data: new_node }"></div>
          </div>
        </div>
        <div class="form-actions center">
          <a data-bind="disable: workflow.read_only, visible: !workflow.read_only(), click: function() { save({ success: workflow_save_success, error: workflow_save_error }) }" href="javascript:void(0);" class="btn btn-primary">${ _('Save') }</a>
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
                ${ utils.render_field(workflow_form['name'], extra_attrs={'data-bind': 'value: %s' % workflow_form['name'].name}) }
                ${ utils.render_field(workflow_form['description'], extra_attrs={'data-bind': 'value: %s' % workflow_form['description'].name}) }
                ${ utils.render_field(workflow_form['is_shared'], extra_attrs={'data-bind': 'checked: %s' % workflow_form['is_shared'].name}) }

                <div class="control-group ">
                  <label class="control-label">
                    <a href="#" id="advanced-btn" onclick="$('#advanced-container').toggle('hide')">
                      <i class="icon-share-alt"></i> ${ _('advanced') }</a>
                  </label>
                  <div class="controls"></div>
                </div>

               <div id="advanced-container" class="hide">
                 % if user_can_edit_job:
                  ${ utils.render_field(workflow_form['deployment_dir'], extra_attrs={'data-bind': 'value: %s' % workflow_form['deployment_dir'].name}) }
                 % endif

                 <%
                 workflows.key_value_field(workflow_form['parameters'], {
                  'name': 'parameters',
                  'remove': '$root.removeParameter',
                  'add': '$root.addParameter',
                 })
                 %>

                 <%
                 workflows.key_value_field(workflow_form['job_properties'], {
                  'name': 'job_properties',
                  'remove': '$root.removeJobProperty',
                  'add': '$root.addJobProperty',
                 })
                 %>

                 ${ utils.render_field(workflow_form['job_xml'], extra_attrs={'data-bind': 'value: %s' % workflow_form['job_xml'].name}) }
               </div>

             </fieldset>
           </div>
        </div>
        <div class="form-actions center">
          % if user_can_edit_job:
            <button data-bind="disable: workflow.read_only, visible: !workflow.read_only(), click: function() { save({ success: workflow_save_success, error: workflow_save_error }) }" class="btn btn-primary">${ _('Save') }</button>
          % endif
          <a href="${ url('oozie:list_workflows') }" class="btn">${ _('Back') }</a>
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

<div id="node-modal" class="modal hide" data-bind="template: $data.template"></div>

<div id="confirmation" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3 class="message"></h3>
  </div>
  <div class="modal-body">
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-primary" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>


<div id="modal-window" class="modal hide fade"></div>

<script src="/static/ext/js/codemirror-3.0.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-xml.js"></script>
<script src="/static/ext/js/codemirror-closetag.js"></script>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-autocomplete-1.9.1.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js" type="text/javascript" charset="utf-8"></script>


% for form_info in action_forms:
  ${ actions.action_form(action_form=form_info[1], node_type=form_info[0], template=True) }
% endfor

${ actions.import_jobsub_form(template=True) }

${ controls.fork_form('fork', True, javascript_attrs={'convert': 'function(data, event) { $data.convertToDecision(); $data._workflow.rebuild(); }'}) }

${ controls.decision_form(link_form, default_link_form, 'decision', True) }

<script type="text/html" id="emptyTemplate"></script>

<script type="text/html" id="startTemplate">
  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links }"></div>
</script>

<script type="text/html" id="nodeTemplate">
  <div class="node node-action row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span12">
          <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
          <span data-bind="text: node_type" class="muted"></span>
          <div class="node-description" data-bind="text: description"></div>
        </div>
      </div>

      <div class="row-fluid node-action-bar">
        <div class="span12" style="text-align:right">
          <a class="btn btn-mini edit-node-link" title="${ _('Edit') }" rel="tooltip" data-bind="attr: { 'data-node-type': node_type() }"><i class="icon-pencil"></i></a>
          <a class="btn btn-mini clone-node-btn" title="${ _('Clone') }" rel="tooltip"><i class="icon-retweet"></i></a>
          <a class="btn btn-mini delete-node-btn" title="${ _('Delete') }" rel="tooltip"><i class="icon-trash"></i></a>
          &nbsp;
        </div>
      </div>
    </div>
  </div>

  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links }"></div>
</script>

<script type="text/html" id="forkTemplate">
  <div class="node node-fork row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span12 action-link" title="Edit">
          <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
          <span data-bind="text: node_type" class="muted"></span>
          <div class="node-description" data-bind="text: description()"></div>
        </div>
      </div>

      <div class="row-fluid node-action-bar">
        <div class="span12" style="text-align:right">
          <a class="btn btn-mini edit-node-link" title="${ _('Convert to Decision') }" data-bind="attr: { 'data-node-type': node_type() }" rel="tooltip"><i class="icon-wrench"></i></a>
          &nbsp;
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
  <div class="node node-join row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span12">
          <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
          <span data-bind="text: node_type()" class="muted"></span>
          <br/>&nbsp;
        </div>
      </div>
    </div>

  </div>
  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links() }"></div>
</script>

<script type="text/html" id="decisionTemplate">
  <div class="node node-decision row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span12 action-link">
          <h4 data-bind="text: (name()) ? name() : node_type() + '-' + id()"></h4>
          <span data-bind="text: node_type" class="muted"></span>
          <div class="node-description" data-bind="text: description()"></div>
        </div>
      </div>

      <div class="row-fluid node-action-bar">
        <div class="span12" style="text-align:right">
          <a class="btn btn-mini edit-node-link" title="${ _('Edit') }" data-bind="attr: { 'data-node-type': node_type() }" rel="tooltip"><i class="icon-pencil"></i></a>
          &nbsp;
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
  <div class="node node-decisionend row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span12">
          <h4 data-bind="text: 'end-' + id()"></h4>
          <span data-bind="text: node_type()" class="muted"></span>
          <br/>&nbsp;
        </div>
      </div>
    </div>

  </div>
  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links() }"></div>
</script>

<script type="text/html" id="linkTemplate">
  <div class="node-link">&nbsp;</div>
</script>

<link rel="stylesheet" href="/oozie/static/css/workflow.css">
<script type="text/javascript" src="/oozie/static/js/workflow.js"></script>

<script type="text/javascript">
/**
 * Component Initialization
 * Initialize the workflow, registry, modal, and import objects.
 */
 // Custom handlers for saving, loading, error checking, etc.
function import_load_available_nodes_success(data) {
  if (data.status == 0) {
    import_node.initialize(data.data);
  } else {
    $.jHueNotify.error("${ _('Received invalid response from server: ') }" + JSON.stringify(data));
  }
}

function workflow_save_success(data) {
  $.jHueNotify.info("${ _('Workflow saved') }");
  workflow.reload(data.data);
  workflow.is_dirty( false );
}

function workflow_save_error(data) {
  $.jHueNotify.error("${ _('Could not save workflow') }");
}

function workflow_load_success(data) {
  if (data.status == 0) {
    workflow.reload(data.data);
  } else {
    $.jHueNotify.error("${ _('Received invalid response from server: ') }" + JSON.stringify(data));
  }
}

function workflow_read_only_handler() {
  $.jHueNotify.error("${ _('Workflow is in read only mode.') }");
}

// Fetch all nodes from server.
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
  job_properties: ${ workflow.job_properties_escapejs | n,unicode }
});
var registry = new Registry();
var workflow = new Workflow({
  model: workflow_model,
  registry: registry,
  read_only: ${ str(not user_can_edit_job).lower() },
  read_only_error_handler: workflow_read_only_handler,
});
var import_node = new ImportNode({workflow: workflow});
var modal = new Modal($('#node-modal'));

// Load data.
workflow.load({ success: workflow_load_success });
import_node.loadAvailableNodes({ success: import_load_available_nodes_success });

/**
 * Modals
 */
// open a modal window for editing a node
function edit_node_modal(node, save, cancel) {
  var backup = ko.mapping.toJS(node);
  normalize_model_fields(backup);

  modal.hide();
  modal.setTemplate(node.edit_template);
  modal.show({node: node, read_only: workflow.read_only()});
  modal.recenter(280, 250);
  modal.addDecorations();

  var cancel_edit = cancel || function() {
    ko.mapping.fromJS(backup, node);
    modal.hide();

    // Prevent event propagation
    return false;
  };

  var try_save = save || function() {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
    }
  };

  $('.modal-backdrop').on('click', cancel_edit);
  modal.el.on('click', '.close', cancel_edit);
  modal.el.on('click', '.cancelButton', cancel_edit);
  modal.el.on('click', '.doneButton', try_save);

  modal.el.on('click', '.edit-node-link', function() {
    var link = ko.contextFor(this).$data;
    var parent = ko.contextFor(this).$parent;
    var node = parent.registry.get(link.child());

    cancel_edit();

    edit_node_modal(node);
  });
}

// Drag a new node onto the canvas
$('#workflow').on('mousedown', '.new-node-link', function(e) {
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
  el.offset({ top: e.pageY - el.height()/10, left: e.pageX - el.width()/10 });
  el.trigger($.Event("mousedown", {pageX: e.pageX, pageY: e.pageY, target: el[0], which: 1}));

  var cancel_edit = function(e) {
    // Didn't save, erase node.
    node.detach();
    node.erase();
    modal.hide();
    workflow.is_dirty( is_dirty );
    $('#workflow').trigger('workflow:rebuild');
  };

  var try_save = function(e) {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
      node.addChild(workflow.kill);
      $('#workflow').trigger('workflow:rebuild');
    }
  };

  // Remember to cleanup after.
  el.one('dragstop', function(e) {
    workflow.new_node(null);
    el.offset(old_position);
    if (node.findChildren().length > 0 || node.findParents().length > 1) {
      edit_node_modal(node, try_save, cancel_edit);
    } else {
      node.erase();
    }
  });
});

// Modal for editing a node
$('#workflow').on('click', '.edit-node-link', function(e) {
  var node = ko.contextFor(this).$data;
  edit_node_modal(node);
});

// Modal for cloning a node
$('#workflow').on('click', '.clone-node-btn', function(e) {
  var node = ko.contextFor(this).$data;
  var model_copy = $.extend(true, {}, node.model);
  var NodeModel = nodeModelChooser(node.node_type());
  model_copy.id = IdGeneratorTable[model_copy.node_type].nextId();
  model_copy.name += '-copy';
  model_copy.child_links = [];
  var model = new NodeModel(model_copy);
  var new_node = new Node(workflow, model, workflow.registry);
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
      // save, add kill, add node to workflow.
      new_node.addChild(workflow.kill);
      node.append(new_node);
      $('#workflow').trigger('workflow:rebuild');
    }
  };

  edit_node_modal(new_node, try_save, cancel_edit);
});

// Modal for deleting a node
$('#workflow').on('click', '.delete-node-btn', function(e) {
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

// Modal for importing a node
$('#workflow').on('click', '.import-jobsub-node-link', function(e) {
  var tempModelView = {
    selected_node: ko.observable(),
    available_nodes: ko.observableArray(import_node.getAvailableNodes()),
    setJobDesignerId: function(data, event) {
      tempModelView.selected_node(data);
      return true;
    }
  };

  modal.hide();
  modal.setTemplate('ImportNodeTemplate');
  modal.show({node: tempModelView, read_only: workflow.read_only()});
  modal.recenter(280, 250);
  modal.addDecorations();

  var cancel_edit = function() {
    modal.hide();

    // Prevent event propagation
    return false;
  };

  var try_save = function() {
    import_node.convertNode({
      success: function(data) {
        var node = data.data.node;
        var NodeModel = nodeModelChooser(node.node_type);
        node.id = IdGeneratorTable[node.node_type].nextId();
        node.name = node.id;
        node.child_links = [];
        var model = new NodeModel(node);
        var new_node = new Node(workflow, model, workflow.registry);
        workflow.registry.add(new_node.id(), new_node);

        // save, add kill, add node to workflow.
        new_node.addChild(workflow.kill);
        workflow.nodes()[workflow.nodes().length - 2].append(new_node);
        workflow.is_dirty( true );
        $('#workflow').trigger('workflow:rebuild');

        $.jHueNotify.info("${ _('Imported Job Designer workflow as node.') }");
      },
      error: function() {
        $.jHueNotify.error("${ _('Could not import Job Designer workflow as node.') }");
      }
    }, tempModelView.selected_node().id);
    modal.hide();
  };

  $('.modal-backdrop').on('click', cancel_edit);
  modal.el.on('click', '.close', cancel_edit);
  modal.el.on('click', '.cancelButton', cancel_edit);
  modal.el.on('click', '.doneButton', try_save);
});



ko.bindingHandlers.fileChooser = {
  init: function(element, valueAccessor, allBindings, model) {
    var self = $(element);
    self.after(getFileBrowseButton(self));
  }
};

ko.applyBindings(workflow, $('#workflow')[0]);

// Handles adding autocomplete to job properties.
// We need to propagate the selected value to knockoutjs.
var addAutoComplete = function(i, elem) {
  var propertiesHint = '';
  $(elem).autocomplete({
    source: propertiesHint,
    select: function(event, ui) {
      var context = ko.contextFor(this);
      context.$data.name = ui.item.value;
    }
  });
};

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
    modal.recenter(280, 250);
  }
};

$(document).ready(function () {
  window.setInterval(checkModelDirtiness, 500);
});

function checkModelDirtiness() {
  if (workflow.is_dirty()) {
    $(".ribbon-wrapper").fadeIn();
  } else {
    $(".ribbon-wrapper").hide();
  }
}

</script>

${ utils.path_chooser_libs(True) }

<script>
  $(document).ready(function(){
    $("input[name='job_xml']").next().remove();
    $("input[name='job_xml']").after(getFileBrowseButton($("input[name='job_xml']"), false));
  });
</script>

${ commonfooter(messages) | n,unicode }
