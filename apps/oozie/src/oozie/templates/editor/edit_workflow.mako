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

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='workflows') }


<div id="workflow" class="container-fluid">
  <div class="ribbon-wrapper hide">
    <div class="ribbon">${ _('Unsaved') }</div>
  </div>

  <h1 data-bind="text: '${ _('Workflow') } ' + name()"></h1>

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
                  <i class="icon-plus"></i> ${ _('Streaming') }
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
          </div>
        </div>
        <div class="form-actions center">
          <a data-bind="click: function() { save() }" href="javascript:void(0);" class="btn btn-primary">${ _('Save') }</a>
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
            <button data-bind="click: function() { save() }" class="btn btn-primary">${ _('Save') }</button>
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
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-primary" href="javascript:void(0);">${_('Yes')}</a>
  </div>
</div>


<div id="modal-window" class="modal hide fade"></div>

<style type="text/css">
#modal-window .modal-content {
  height: 300px;
  overflow: auto;
}

#node-modal {
  width: auto;
}

#node-modal .modal-content {
  background: white;
  max-height: 500px;
  overflow-x: hidden;
  overflow-y: scroll;
  padding: 5px;
}

.action {border-style:solid; border-width:1px; border-color:LightGrey; padding: 3px;}

.action-link:hover, .edit-node-link:hover {cursor: pointer;}

#graph {
  text-align: center;
}

.node-link-hover {
  background: gray;
}

.node-fork-hover {
  background: green;
}

.popover {
  z-index: 2060 !important;
  margin-left: 166px!important;
}


.ribbon-wrapper {
  width: 85px;
  height: 88px;
  overflow: hidden;
  position: fixed;
  top: 74px;
  right: -3px;
  right: 20px\9; /* IE8 */
  width: 125px\9; /* IE8 */
}

.ribbon {
  font: bold 15px sans-serif;
  text-align: center;
  text-shadow: rgba(255,255,255,0.5) 0px 1px 0px;
  -webkit-transform: rotate(45deg);
  -moz-transform:    rotate(45deg);
  -ms-transform:     rotate(45deg);
  -o-transform:      rotate(45deg);
  position: relative;
  padding: 7px 0;
  left: -5px;
  top: 15px;
  width: 120px;
  background-color: #da4f49;
  *background-color: #bd362f;
  background-image: -moz-linear-gradient(top, #ee5f5b, #bd362f);
  background-image: -webkit-gradient(linear, 0 0, 0 100%, from(#ee5f5b), to(#bd362f));
  background-image: -webkit-linear-gradient(top, #ee5f5b, #bd362f);
  background-image: -o-linear-gradient(top, #ee5f5b, #bd362f);
  background-image: linear-gradient(to bottom, #ee5f5b, #bd362f);
  background-repeat: repeat-x;
  color: #ffffff;
  -webkit-box-shadow: 0px 0px 3px rgba(0,0,0,0.3);
  -moz-box-shadow:    0px 0px 3px rgba(0,0,0,0.3);
  box-shadow:         0px 0px 3px rgba(0,0,0,0.3);
}

.ribbon:before, .ribbon:after {
  content: "";
  border-top:   3px solid #c09853;
  border-left:  3px solid transparent;
  border-right: 3px solid transparent;
  position:absolute;
  bottom: -3px;
}

.ribbon:before {
  left: 0;
}
.ribbon:after {
  right: 0;
}
</style>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-autocomplete-1.9.1.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js" type="text/javascript" charset="utf-8"></script>


% for form_info in action_forms:
  ${ actions.action_form(action_form=form_info[1], node_type=form_info[0], template=True) }
% endfor

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
        <div class="span10 edit-node-link" title="Edit" data-bind="attr: { 'data-node-type': node_type() }">
          <span class="label label-info" data-bind="text: (name()) ? name() : node_type() + '-' + id()"></span>
        </div>
      </div>

      <div class="row-fluid">
        <div class="span10 action-link" title="Edit">
          <span data-bind="text: node_type"></span>
          <br/>
          <span class="node-description" data-bind="text: description"></span>
        </div>
      </div>

      <div class="row-fluid">
        <div class="span10">
          <button data-bind="click: function(data, event) { $root.cloneNode.call($root, data, event); }"  class="btn" name="clone_action" title="${ _('Clone') }" type="button"><i class="icon-retweet"></i></button>
          <button data-bind="click: function(data, event) { $root.removeNode.call($root, data, event); }"  class="btn" name="delete_action" title="${ _('Delete') }" type="button"><i class="icon-remove"></i></button>
        </div>
        <div class="span2">
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
        <div class="span10 edit-node-link"  data-bind="attr: { 'data-node-type': node_type() }" title="Edit">
          <span class="label label-info" data-bind="text: (name()) ? name() : node_type() + '-' + id()"></span>
        </div>
      </div>

      <div class="row-fluid">
        <div class="span10 action-link" title="Edit">
          <span data-bind="text: node_type"></span>
          <br/>
          <span class="node-description" data-bind="text: description()"></span>
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

<script type="text/html" id="decisionTemplate">
  <div class="node node-decision row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span10 edit-node-link"  data-bind="attr: { 'data-node-type': node_type() }" title="Edit">
          <span class="label label-info" data-bind="text: (name()) ? name() : node_type() + '-' + id()"></span>
        </div>
      </div>

      <div class="row-fluid">
        <div class="span10 action-link" title="Edit">
          <span data-bind="text: node_type"></span>
          <br/>
          <span class="node-description" data-bind="text: description()"></span>
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

    <div class="row-fluid node-decision-end">
      <div class="node-decision-end">&nbsp;</div>
    </div>
  </div>
</script>

<script type="text/html" id="joinTemplate">
  <div class="node node-join row-fluid">
    <div class="action span12">
      <div class="row-fluid">
        <div class="span10">
          <span class="label label-info" data-bind="text: (name()) ? name() : node_type() + '-' + id()"></span>
        </div>
      </div>

      <div class="row-fluid">
        <div class="span10">
          <span data-bind="text: node_type()"></span>
        </div>
      </div>
    </div>

  </div>
  <div class="row-fluid" data-bind="template: { name: 'linkTemplate', foreach: links() }"></div>
</script>

<script type="text/html" id="linkTemplate">
  <div class="node-link">&nbsp;</div>
</script>

<script type="text/javascript" src="/oozie/static/js/workflow.js"></script>

<script type="text/javascript">
$.extend(Workflow.prototype, {
  save: function( options ) {
    var self = this;

    var options = options || {};

    data = $.extend(true, {}, self.model);

    var nodes = [];
    $.each(self.registry.nodes, function(key, node) {
      // Create object with members from the actual model to address JSON.stringify bug
      // JSON.stringify does not pick up members specified in prototype prior to object creation.
      var model = {};
      for (var key in node.model) {
        model[key] = node.model[key];
      }
      nodes.push(model);
    });
    data['nodes'] = nodes;

    var request = $.extend({
      url: self.url() + '/save',
      type: 'POST',
      data: { workflow: JSON.stringify(data) },
      success: function() {
        $.jHueNotify.info("${ _('Workflow saved') }");
        workflow.is_dirty( false );
      },
      error: function() {
        $.jHueNotify.error("${ _('Could not save workflow') }");
      }
    }, options);

    var success_handler = request['success'];
    request['success'] = function(data, event) {
      if ($.isFunction(success_handler)) {
        success_handler(data, event);
      }

      self.reload(data.data);
    };

    $.ajax(request);
  }
});

/**
 * Known issues with this way of doing things...
 *  - 2 Layers of models.
 */
// Fetch all nodes from server.
var workflow_model = {
  id: ${ workflow.id },
  name: "${ workflow.name }",
  description: "${ workflow.description }",
  start: ${ workflow.start.id },
  end: ${ workflow.end.id },
  job_xml: "${ workflow.job_xml }",
  deployment_dir: "${ workflow.deployment_dir }",
  is_shared: "${ workflow.is_shared }" == "True",
  parameters: ${ workflow.parameters },
  job_properties: ${ workflow.job_properties }
};
var registry = new Registry();
var workflow = new Workflow({
  model: workflow_model,
  registry: registry
});
var modal = new Modal($('#node-modal'));
workflow.load();

$('#workflow').on('click', '.edit-node-link', function(e) {
  var node = ko.contextFor(this).$data;
  var backup = ko.mapping.toJS(node);
  normalize_model_fields(backup);

  modal.setTemplate(node.edit_template);
  modal.show(node);
  modal.recenter(280, 250);
  modal.addDecorations();

  var cancel_edit = function(e) {
    ko.mapping.fromJS(backup, node);
    modal.hide();

    // Prevent event propagation
    return false;
  };

  var try_save = function(e) {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
    }
  };

  $('.modal-backdrop').on('click', cancel_edit);
  modal.el.on('click', '.close', cancel_edit);
  modal.el.on('click', '.cancelButton', cancel_edit);
  modal.el.on('click', '.doneButton', try_save);
});

$('#workflow').on('click', '.new-node-link', function(e) {
  var node_type = $(this).attr('data-node-type');
  var template = node_type + 'EditTemplate';
  var NodeModel = nodeModelChooser(node_type);
  var model = new NodeModel({
    id: IdGeneratorTable[node_type].nextId(),
    node_type: node_type
  });
  var node = new Node(workflow, model, registry);

  self.registry.add(model.id, node);

  modal.setTemplate(template);
  modal.show(node);
  modal.recenter(280, 250);
  modal.addDecorations();

  var cancel_edit = function(e) {
    // Didn't save, erase node.
    node.erase();
    modal.hide();
  };

  var try_save = function(e) {
    if (node.validate()) {
      workflow.is_dirty( true );
      modal.hide();
      // save, add kill, add node to workflow.
      node.addChild(workflow.kill);
      workflow.nodes()[workflow.nodes().length - 2].append(node);
      $('#workflow').trigger('workflow:rebuild');
    }
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
  window.setTimeout(checkModelDirtiness, 500);
});

function checkModelDirtiness() {
  if (workflow.is_dirty()) {
    $(".ribbon-wrapper").fadeIn();
  }
  else {
    $(".ribbon-wrapper").hide();
    window.setTimeout(checkModelDirtiness, 500);
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

${ commonfooter(messages) }
