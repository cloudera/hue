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

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Workflow Editor"), "Oozie", user) | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("workflow") > -1) {
      location.href = "/oozie/editor/workflow/edit/?" + window.location.hash.substr(1);
    }
  }
</script>


<%dashboard:layout_toolbar>
  <%def name="skipLayout()"></%def>
  <%def name="widgets()">
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableHiveAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'start': function(event, ui){$root.setCurrentDraggedWidget(draggableHiveAction());}}}"
         title="${_('Hive Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true},
                    draggable: {data: draggablePigAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'start': function(event, ui){$root.setCurrentDraggedWidget(draggablePigAction());}}}"
         title="${_('Pig Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_pig_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableJavaAction(), isEnabled: true,
                    options: {'start': function(event, ui){$root.setCurrentDraggedWidget(draggableJavaAction());}}}"
         title="${_('Java program')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-code-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableMapReduceAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('MapReduce job')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-files-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSubworkflowAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Sub workflow')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-code-fork"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true }" rel="tooltip" data-placement="top">
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableStopNode(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Kill')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-stop"></i></a>
    </div>
</%def>
</%dashboard:layout_toolbar>


<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Gen XML') }" rel="tooltip" data-placement="bottom" data-bind="click: gen_xml, css: {'btn': true}">
      <i class="fa fa-file-code-o"></i>
    </a>
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Workspace') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal" data-bind="css: {'btn': true}">
        <i class="fa fa-folder-open"></i>
      </button>
      <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal" data-bind="css: {'btn': true}">
        <i class="fa fa-cog"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: $root.save, css: {'btn': true}">
        <i class="fa fa-save"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <a class="btn" href="${ url('oozie:new_workflow') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-file-o"></i>
      </a>
      <a class="btn" href="${ url('oozie:list_editor_workflows') }" title="${ _('Workflows') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-tags"></i>
      </a>
    % endif
  </div>

  <form class="form-search" style="margin: 0">
    <strong>${_("Name")}</strong>
    <input data-bind="value: $root.workflow.name"/>
  </form>
</div>



 <div id="emptyDashboard" data-bind="fadeVisible: !isEditing() && columns().length == 0">
  <div style="float:left; padding-top: 90px; margin-right: 20px; text-align: center; width: 260px">${ _('Click on the pencil to get started with your dashboard!') }</div>
    <img src="/static/art/hint_arrow.png" />
  </div>

  <div id="emptyDashboardEditing" data-bind="fadeVisible: isEditing() && columns().length == 0 && previewColumns() == ''">
    <div style="float:right; padding-top: 90px; margin-left: 20px; text-align: center; width: 260px">${ _('Pick an index and Click on a layout to start your dashboard!') }</div>
    <img src="/static/art/hint_arrow_horiz_flipped.png" />
  </div>


  <div data-bind="visible: isEditing() && previewColumns() != '' && columns().length == 0, css:{'with-top-margin': isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="visible: previewColumns() == 'oneSixthLeft'">
      <div class="span2 preview-row"></div>
      <div class="span10 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'full'">
      <div class="span12 preview-row">
      </div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'magic'">
      <div class="span12 preview-row">
        <div style="text-align: center; color:#EEE; font-size: 180px; margin-top: 80px">
          <i class="fa fa-magic"></i>
        </div>
      </div>
    </div>
  </div>
</div>

<div data-bind="css: {'dashboard': true, 'with-top-margin': isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="template: { name: 'column-template', foreach: columns}">
    </div>
    <div class="clearfix"></div>
  </div>
</div>

<script type="text/html" id="column-template">
  <div data-bind="css: klass">
    <div data-bind="template: { name: 'row-template', data: oozieStartRow }"></div>

    <div class="container-fluid" data-bind="visible: $root.isEditing() && oozieRows().length > 0">
      <div data-bind="css: {'drop-target': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(true, 1); _r.addWidget(widget); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'drop-target-highlight', 'greedy': true, 'stop': function(event, ui){}}}"></div>
    </div>
    <div data-bind="template: { name: 'internal-row-template', foreach: oozieRows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing() && rows().length > 0">
      <div data-bind="css: {'drop-target': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(false, $data.rows().length - 1); _r.addWidget(widget); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'drop-target-highlight', 'greedy': true, 'stop': function(event, ui){}}}"></div>
    </div>

    <div data-bind="template: { name: 'row-template', data: oozieEndRow }"></div>
  </div>
</script>


<script type="text/html" id="internal-column-template">
  <div data-bind="css: klass">
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="css: {'drop-target': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(true); _r.addWidget(widget); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'drop-target-highlight', 'greedy': true, 'stop': function(event, ui){}}}"></div>
    </div>
    <div data-bind="template: { name: 'internal-row-template', foreach: rows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="css: {'drop-target': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(); _r.addWidget(widget); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'drop-target-highlight', 'greedy': true, 'stop': function(event, ui){}}}"></div>
    </div>
  </div>
</script>


<script type="text/html" id="row-template">
  <div class="container-fluid">
    <div class="row-fluid">
      <div class="span12">
        <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
          sortable: { template: 'widget-template', data: widgets, allowDrop: $root.isEditing() && widgets().length < 1, isEnabled: $root.isEditing() && widgets().length < 1,
          options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
              'stop': function(event, ui){},
              'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();  var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
              dragged: function(widget){widgetDraggedAdditionalHandler(widget)}}">
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="internal-row-template">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="visible: $index() > 0" style="margin-bottom: 10px">
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}"></div>
      <div data-bind="css: {'span10': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing(), css: {'drop-target': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}"></div>
    </div>
    <div class="row-fluid">
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing(), css: {'drop-target drop-target-side': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div  data-bind="css: {'span10': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: columns().length == 0, css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
          sortable: { template: 'widget-template', data: widgets, allowDrop: enableOozieDrop, isEnabled: enableOozieDrop,
          options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
              'stop': function(event, ui){},
              'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();  var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
              dragged: function(widget){widgetDraggedAdditionalHandler(widget)}}">
        </div>
        <div class="container-fluid" data-bind="visible: columns().length > 0" style="border: 1px solid #e5e5e5; border-top: none; background-color: #F3F3F3;">
          <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing}">
            <div data-bind="template: { name: 'internal-column-template', foreach: columns}">
            </div>
          </div>
        </div>
      </div>
      <div  data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing(), css: {'drop-target drop-target-side': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
    </div>
  </div>

</script>

<script type="text/html" id="widget-template">
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass">
    <h2 class="card-heading simple">
      <span data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
        &nbsp;
      </span>
      <!-- ko if: $root.collection && $root.collection.getFacetById(id()) -->
      <span data-bind="with: $root.collection.getFacetById(id())">
        <span data-bind="editable: label, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
      </span>
      <!-- /ko -->
      <!-- ko if: typeof $root.collection == 'undefined' || $root.collection.getFacetById(id()) == null -->
        <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
      <!-- /ko -->
      <div class="inline pull-right" data-bind="visible: $root.isEditing() && ['start-widget', 'end-widget', 'fork-widget', 'join-widget'].indexOf(widgetType()) == -1">
        <a href="javascript:void(0)" data-bind="click: $root.removeWidget"><i class="fa fa-times"></i></a>
      </div>
    </h2>
    <div class="card-body" style="padding: 5px;">
      <div data-bind="template: { name: function() { return widgetType(); }}" class="widget-main-section"></div>
    </div>
  </div>
</script>


<script type="text/html" id="fork-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      To:
      <span data-bind="foreach: children">
        <span data-bind="text: $data['to']" /></span>
      </span>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="join-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      Then --> <span data-bind="text: children()[0]['to']" /></span>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="start-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <!-- ko if: children().length == 1 -->
      Start --> <input type="text" data-bind="value: children()[0]['to']" />
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="end-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="common-action-properties">
  ${ _('Prepare') }
  <ul data-bind="foreach: properties.prepares">
    <li>
      <span data-bind="text: type"></span>
      <input data-bind="value: value"/>
      <a href="#" data-bind="click: function(){ $parent.properties.prepares.remove(this); }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
  <button data-bind="click: function(){ properties.prepares.push({'type': 'mkdir', 'value': ''}); }">
    ${ _('Directory') } <i class="fa fa-plus"></i>
  </button>
  <button data-bind="click: function(){ properties.prepares.push({'type': 'delete', 'value': ''}); }">
    ${ _('Delete') } <i class="fa fa-plus"></i>
  </button>
  <br/>
  ${ _('Job XML') } <input type="text" data-bind="value: properties.job_xml" />
  <br/>
  ${ _('Properties') }
  <ul data-bind="foreach: properties.properties">
    <li>
      <input data-bind="value: name"/>
      <input data-bind="value: value"/>
      <a href="#" data-bind="click: function(){ $parent.properties.properties.remove(this); }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
  <button data-bind="click: function(){ properties.properties.push({'name': '', 'value': ''}); }">
    <i class="fa fa-plus"></i>
  </button>
  <br/>
  ${ _('Archives') }
  <ul data-bind="foreach: properties.archives">
    <li>
      <input data-bind="value: name"/>
      <a href="#" data-bind="click: function(){ $parent.properties.archives.remove(this); }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
  <button data-bind="click: function(){ properties.archives.push({'name': ''}); }">
    <i class="fa fa-plus"></i>
  </button>
</script>


<script type="text/html" id="hive-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Hive') }</a></li>
        <li><a href="#properties" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon">
        </div>
        <div class="tab-pane" id="properties">
          <span data-bind="template: { name: 'common-action-properties' }"></span>
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="pig-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#action-' + id()}" data-toggle="tab">${ _('Pig') }</a></li>
        <li><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'action-' + id() }">
          <img src="/oozie/static/art/icon_pig_48.png" class="app-icon">
          <input type="text" data-bind="value: properties.script_path" />
          </br>
	      ${ _('Variables') }
	      <ul data-bind="foreach: properties.arguments">
	        <li>
	          <input data-bind="value: value"/>
	          <a href="#" data-bind="click: function(){ $parent.properties.arguments.remove(this); }">
	            <i class="fa fa-minus"></i>
	          </a>
	        </li>
	      </ul>
          <button data-bind="click: function(){ properties.arguments.push({'value': ''}); }">
            <i class="fa fa-plus"></i>
          </button>	
          </br>
          ${ _('Files') }
          <ul data-bind="foreach: properties.files">
            <li>
              <input data-bind="value: value"/>
              <a href="#" data-bind="click: function(){ $parent.properties.files.remove(this); }">
                <i class="fa fa-minus"></i>
              </a>
            </li>
          </ul>
          <button data-bind="click: function(){ properties.files.push({'value': ''}); }">
            <i class="fa fa-plus"></i>
          </button>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="template: { name: 'common-action-properties' }"></span>
          <br/>
          <br/>
          ${ _('Parameters') }
          <ul data-bind="foreach: properties.parameters">
            <li>
              <input data-bind="value: value"/>
              <a href="#" data-bind="click: function(){ $parent.properties.parameters.remove(this); }">
                <i class="fa fa-minus"></i>
              </a>
            </li>
          </ul>
          <button data-bind="click: function(){ properties.parameters.push({'value': ''}); }">
            <i class="fa fa-plus"></i>
          </button>
          </br>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'sla-' + id() }">
          <div class="control-group">
            <label class="control-label">${ _('SLA Configuration') }</label>
            <div class="controls" data-bind="with: properties">
              ${ utils.slaForm() }
            </div>
          </div>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'credentials-' + id() }">
          <select data-bind="options: $root.credentials, value: properties.credentials" size="5" multiple="true"></select>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'transitions-' + id() }">
          <!-- ko if: children().length == 2 -->
          OK --> <input type="text" data-bind="value: children()[0]['to']" />
          <br/>
          KO --> <input type="text" data-bind="value: children()[1]['error']" />
          <!-- /ko -->
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="java-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Java') }</a></li>
        <li><a href="#properties" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <input type="text" data-bind="value: properties.jar_path" />
        </div>
        <div class="tab-pane" id="properties">
          <span data-bind="template: { name: 'common-action-properties' }"></span>
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="subworkflow-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Sub-workflow') }</a></li>
        <li><a href="#properties" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <input type="text" data-bind="value: properties.subworkflow" />
        </div>
        <div class="tab-pane" id="properties">
          <span data-bind="template: { name: 'common-action-properties' }"></span>
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="fork-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="decision-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="enkill-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<div id="addActionDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" data-bind="click: addActionDemiModalFieldCancel" class="pull-right"><i class="fa fa-times"></i></a>

    <ul data-bind="foreach: addActionProperties">
      <li>
        <span data-bind="text: label"></span>
        <input data-bind="value: value"/>
      </li>
    </ul>

    <!-- ko if: addActionWorkflows().length > 0 -->
      <select data-bind="options: addActionWorkflows, optionsText: 'name', value: selectedSubWorkflow"></select>
    <!-- /ko -->

    <br/>
    <a data-bind="click: addActionDemiModalFieldPreview">
      Add
    </a>
  </div>
</div>


<div id="settingsDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 30px; text-align: center; line-height: 28px">

      ${ _('Oozie Parameters') }
      <ul data-bind="foreach: $root.workflow.properties.parameters">
        <li>
          <input data-bind="value: name"/>
          <input data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.workflow.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <button data-bind="click: function(){ $root.workflow.properties.parameters.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i>
      </button>

      <br/>
      ${_("Workspace")}
      <input data-bind="value: $root.workflow.properties.deployment_dir"/>

	  <br/>
	  ${ _('Hadoop Properties') }
	  <ul data-bind="foreach: $root.workflow.properties.properties">
	    <li>
	      <input data-bind="value: name"/>
	      <input data-bind="value: value"/>
	      <a href="#" data-bind="click: function(){ $root.workflow.properties.properties.remove(this); }">
	        <i class="fa fa-minus"></i>
	      </a>
	    </li>
	  </ul>
	  <button data-bind="click: function(){ $root.workflow.properties.properties.push({'name': '', 'value': ''}); }">
	    <i class="fa fa-plus"></i>
	  </button>

      <br/>
      ${ _("Job XML") }
      <input data-bind="value: $root.workflow.properties.job_xml"/>

      <br/>
      <div class="control-group">
        <label class="control-label">${ _('SLA Configuration') }</label>
        <div class="controls" data-bind="with: $root.workflow.properties">
          ${ utils.slaForm() }
        </div>
      </div>
    </div>
  </div>
</div>


<div id="submit-wf-modal" class="modal hide"></div>


<link rel="stylesheet" href="/oozie/static/css/workflow-editor.css">
<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">


${ dashboard.import_layout() }


<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }

<script src="/oozie/static/js/workflow-editor.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.curvedarrow.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">
  ${ utils.slaGlobal() }


  var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode }, ${ credentials_json | n,unicode });
  ko.applyBindings(viewModel);

  viewModel.init();
  fullLayout(viewModel);

  function columnDropAdditionalHandler(widget) {
    widgetDraggedAdditionalHandler(widget);
  }

  function widgetDraggedAdditionalHandler(widget) {
    viewModel.workflow.newNode(widget);
    $("canvas").remove();
    showAddActionDemiModal(widget);
  }


  $(document).on("showSubmitPopup", function(event, data){
    $('#submit-wf-modal').html(data);
    $('#submit-wf-modal').modal('show');
  });


  var newAction = null;

  function showAddActionDemiModal(widget) {
    newAction = widget;
    $("#addActionDemiModal").modal("show");
  }

  function addActionDemiModalFieldPreview(field) {
    if (newAction != null) {
      viewModel.workflow.addNode(newAction);
      $("#addActionDemiModal").modal("hide");
    }
  }

  function addActionDemiModalFieldCancel() {
    viewModel.removeWidgetById(newAction.id());
  }

  function linkWidgets(fromId, toId) {
    var _from = $("#wdg_" + (typeof fromId == "function"?fromId():fromId));
    var _to = $("#wdg_" + (typeof toId == "function"?toId():toId));

    var _fromCenter = {
      x: _from.position().left + _from.outerWidth() / 2,
      y: _from.position().top + _from.outerHeight()
    }

    var _toCenter = {
      x: _to.position().left + _to.outerWidth() / 2,
      y: _to.position().top
    }

    var _curveCoords = {};

    if (_fromCenter.x == _toCenter.x) {
      _curveCoords.x = _fromCenter.x;
      _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
    }
    else {
      _curveCoords.x = _fromCenter.x - (_fromCenter.x - _toCenter.x) / 4;
      _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
    }

    $(document.body).curvedArrow({
      p0x: _fromCenter.x,
      p0y: _fromCenter.y,
      p1x: _curveCoords.x,
      p1y: _curveCoords.y,
      p2x: _toCenter.x,
      p2y: _toCenter.y,
      lineWidth: 2,
      size: 10,
      strokeStyle: '#CCCCCC'
    });

  }

  function drawArrows(){
    $("canvas").remove();
    var _links = viewModel.workflow.linkMapping();
    Object.keys(_links).forEach(function(id){
      if (_links[id].length > 0){
        _links[id].forEach(function(nextId){
          linkWidgets(id, nextId);
        });
      }
    });
  }

  var _linkMappingTimeout = -1;
  $(document).on("drawArrows", function(){
    window.clearTimeout(_linkMappingTimeout);
    _linkMappingTimeout = window.setTimeout(drawArrows, 25);
  });

  $(document).on("editingToggled", function(){
    $("canvas").remove();
    window.setTimeout(drawArrows, 100);
  });

</script>

${ commonfooter(messages) | n,unicode }
