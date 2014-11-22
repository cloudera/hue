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
                    options: {'refreshPositions': true, 'start': function(event, ui){$root.currentlyDraggedWidget(draggableHiveAction());}}}"
         title="${_('Hive Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true},
                    draggable: {data: draggablePigAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'start': function(event, ui){$root.currentlyDraggedWidget(draggablePigAction());}}}"
         title="${_('Pig Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_pig_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableJavaAction(), isEnabled: true,
                    options: {'start': function(event, ui){$root.currentlyDraggedWidget(draggableJavaAction());}}}"
         title="${_('Java program')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-code-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSqoopAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Sqoop 1')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_sqoop_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableMapReduceAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('MapReduce job')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-archive-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSubworkflowAction(), isEnabled: true,
                    options: {'start': function(event, ui){$root.currentlyDraggedWidget(draggableSubworkflowAction());}}}"
         title="${_('Sub workflow')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-code-fork"></i></a>
    </div>
    
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableShellAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Shell')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-terminal"></i></a>
    </div>
    
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSshAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Ssh')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-tty"></i></a>
    </div>
        
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableFsAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('HDFS Fs')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-o"></i></a>
    </div>    
    
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableEmailAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Email')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-envelope-o"></i></a>
    </div>    
    
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableStreamingAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Streaming')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-exchange"></i></a>
    </div>    

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableDistCpAction(), isEnabled: true,
                    options: {'start': function(event, ui){}}}"
         title="${_('Distcp')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-files-o"></i></a>
    </div>    

    <div data-bind="css: { 'draggable-widget': true }" rel="tooltip" data-placement="top">
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableKillNode(), isEnabled: true,
                    options: {'start': function(event, ui){$root.currentlyDraggedWidget(draggableKillNode());}}}"
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
    <a title="${ _('Import workflows') }" rel="tooltip" data-placement="bottom" data-bind="click: import_workflows, css: {'btn': true}">
      <i class="fa fa fa-download"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal" data-bind="css: {'btn': true}">
        <i class="fa fa-cog"></i>
      </button>
      <a title="${ _('Workspace') }" target="_blank" rel="tooltip" data-placement="right"
          data-original-title="${ _('Go upload additional files and libraries to the deployment directory on HDFS') }"
          data-bind="css: {'btn': true}, attr: {href: '/filebrowser/view' + $root.workflow.properties.deployment_dir() }">
        <i class="fa fa-folder-open"></i>
      </a>      
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

<div data-bind="css: {'dashboard': true, 'with-top-margin': isEditing(), 'readonly': ! isEditing()}">
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
      <div data-bind="visible: ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'is-editing': $root.isEditing}"></div>
      <div data-bind="visible: enableOozieDropOnBefore, css: {'drop-target': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(x, y){ var _w = $root.addDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
    </div>
    <div data-bind="template: { name: 'internal-row-template', foreach: oozieRows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing() && rows().length > 0">
      <div data-bind="visible: ! enableOozieDropOnAfter(), css: {'drop-target drop-target-disabled': true, 'is-editing': $root.isEditing}"></div>
      <div data-bind="visible: enableOozieDropOnAfter, css: {'drop-target': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }"></div>
    </div>

    <div data-bind="template: { name: 'row-template', data: oozieEndRow }"></div>
  </div>
</script>


<script type="text/html" id="internal-column-template">
  <div data-bind="css: klass">
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="visible: ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'is-editing': $root.isEditing}"></div>
      <div data-bind="visible: enableOozieDropOnBefore, css: {'drop-target': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
    </div>
    <div data-bind="template: { name: 'internal-row-template', foreach: rows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="visible: ! enableOozieDropOnAfter(), css: {'drop-target drop-target-disabled': true, 'is-editing': $root.isEditing}"></div>
      <div data-bind="visible: enableOozieDropOnAfter, css: {'drop-target': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }"></div>
    </div>
  </div>
</script>


<script type="text/html" id="row-template">
  <div class="container-fluid">
    <div class="row-fluid">
      <div class="span12">
        <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
          sortable: { template: 'widget-template', data: widgets, allowDrop: $root.isEditing() && widgets().length < 1, isEnabled: $root.isEditing() && widgets().length < 1,
          options: {'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
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
    <div class="row-fluid" data-bind="visible: $index() > 0 && $root.isEditing() && ! $root.isRowBeforeJoin($data) && ! $root.isRowAfterFork($data)" style="margin-bottom: 10px">
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}"></div>
      <div data-bind="css: {'span10': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'is-editing': $root.isEditing}"></div>
        <div style="text-align: left" data-bind="visible: $root.isEditing() && enableOozieDropOnBefore(), css: {'drop-target': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}"></div>
    </div>
    <div class="row-fluid">
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && enableOozieDropOnSide() && !($data.widgets().length > 0 && $data.widgets()[0].widgetType() == 'join-widget'), css: {'drop-target drop-target-side': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div  data-bind="css: {'span10': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: columns().length == 0, css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
          sortable: { template: 'widget-template', data: widgets, allowDrop: enableOozieDrop, isEnabled: enableOozieDrop,
          options: {'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
              'stop': function(event, ui){},
              'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();  var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
              dragged: function(widget){widgetDraggedAdditionalHandler(widget)}}">
        </div>
        <div class="container-fluid" data-bind="visible: columns().length > 0">
          <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing}">
            <div data-bind="template: { name: 'internal-column-template', foreach: columns}">
            </div>
          </div>
        </div>
      </div>
      <div  data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && enableOozieDropOnSide() && !($data.widgets().length > 0 && $data.widgets()[0].widgetType() == 'join-widget'),, css: {'drop-target drop-target-side': true, 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
    </div>
  </div>

</script>

<script type="text/html" id="widget-template">
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass, draggable: {data: $data, isEnabled: true, options: {'handle': '.move-widget', 'opacity': 0.7, 'refreshPositions': true, 'start': function(event, ui){ $root.setCurrentlyDraggedWidget($data, event.toElement); }, 'stop': function(event, ui){ $root.enableSideDrop($data); }, 'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();  var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}}}">
    <h2 class="card-heading simple">
      <span data-bind="visible: $root.isEditing() && oozieMovable()">
        <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
        &nbsp;
        <a href="javascript:void(0)" class="move-widget clone-widget"><i class="fa fa-copy"></i></a>
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
    <a class="pointer" data-bind="click: function() { $root.convertToDecision($parent, $data) }">Convert to Decision</a>
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
      <!-- ko if: children().length == 1 -->
      Then --> <span data-bind="text: children()[0]['to']"></span>
      <!-- /ko -->
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
    
    <div data-bind="visible: $root.isEditing">
      To:
      <span data-bind="foreach: children">
        <select data-bind="options: $root.workflow.nodeIds,
                     optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
                     value: $data['to']
                     ">
        </select>      
        if <input data-bind="value: $data['condition']" />
      </span>
      <a>${ _('Jump to another node') } <i class="fa fa-plus"></i></a>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="kill-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <input type="text" data-bind="value: properties.message" />
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

    <div data-bind="visible: $root.isEditing">
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
  <ul data-bind="foreach: properties.job_properties">
    <li>
      <input data-bind="value: name"/>
      <input data-bind="value: value"/>
      <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
  <button data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); }">
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


<script type="text/html" id="common-properties-arguments">
  ${ _('Arguments') }
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
</script>


<script type="text/html" id="common-properties-files">
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
</script>


<script type="text/html" id="common-properties-parameters">
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
</script>


<script type="text/html" id="common-action-transition">
  <!-- ko if: children().length == 2 -->
  OK -->
  <select data-bind="options: $root.workflow.nodeIds,
                     optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
                     value: children()[0]['to']
                     ">
  </select>
  <br/>
  KO -->
  <select data-bind="options: $root.workflow.nodeIds,
                     optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
                     value: children()[1]['error']
                     ">
  </select>
  <!-- /ko -->
</script>


<script type="text/html" id="common-action-credentials">
  <select data-bind="options: $root.credentials, value: properties.credentials" size="5" multiple="true"></select>
</script>


<script type="text/html" id="common-action-sla">
  <div class="control-group">
    <label class="control-label">${ _('SLA Configuration') }</label>
    <div class="controls" data-bind="with: properties">
      ${ utils.slaForm() }
    </div>
  </div>
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
        <li class="active"><a data-bind="attr: { href: '#action-' + id()}" data-toggle="tab">${ _('Hive') }</a></li>
        <li><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'action-' + id() }">
          <img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon">

          <span data-bind="text: $root.workflow_properties.script_path.label"></span>
          <input type="text" data-bind="value: properties.script_path" />                    
          </br>
          <span data-bind="template: { name: 'common-properties-parameters' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="template: { name: 'common-action-properties' }"></span>
          <br/>
          </br>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'sla-' + id() }">
          <span data-bind="template: { name: 'common-action-sla' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'credentials-' + id() }">
          <span data-bind="template: { name: 'common-action-credentials' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'transitions-' + id() }">
          <span data-bind="template: { name: 'common-action-transition' }"></span>
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

          <span data-bind="text: $root.workflow_properties.script_path.label"></span>
          <input type="text" data-bind="value: properties.script_path" />          
          </br>

	      <span data-bind="template: { name: 'common-properties-parameters' }"></span>
	      <br/>
	      <span data-bind="template: { name: 'common-properties-files' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="template: { name: 'common-properties-arguments' }"></span>
          <br/>        
          <span data-bind="template: { name: 'common-action-properties' }"></span>          
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'sla-' + id() }">
          <span data-bind="template: { name: 'common-action-sla' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'credentials-' + id() }">
          <span data-bind="template: { name: 'common-action-credentials' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'transitions-' + id() }">
          <span data-bind="template: { name: 'common-action-transition' }"></span>
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
        <li class="active"><a data-bind="attr: { href: '#action-' + id()}" data-toggle="tab">${ _('Java') }</a></li>
        <li><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'action-' + id() }">
          <i class="fa fa-file-code-o"></i>
          
          <span data-bind="text: $root.workflow_properties.jar_path.label"></span>          
          <input type="text" data-bind="value: properties.jar_path" />
          <br/>
          <span data-bind="text: $root.workflow_properties.main_class.label"></span>
          <input type="text" data-bind="value: properties.main_class" />
          </br>

          <span data-bind="template: { name: 'common-properties-parameters' }"></span>
          <br/>
          <span data-bind="template: { name: 'common-properties-files' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'properties-' + id() }">          
          <span data-bind="text: $root.workflow_properties.java_opts.label"></span>
          <ul data-bind="foreach: properties.java_opts">
            <li>
              <input data-bind="value: value"/>
              <a href="#" data-bind="click: function(){ $parent.properties.java_opts.remove(this); }">
                <i class="fa fa-minus"></i>
              </a>
            </li>
          </ul>
          <button data-bind="click: function(){ properties.java_opts.push({'value': ''}); }">
            <i class="fa fa-plus"></i>
          </button>        
          </br>
          <span data-bind="text: $root.workflow_properties.capture_output.label"></span>
          <input type="text" data-bind="value: properties.capture_output" />
          </br>

          <span data-bind="template: { name: 'common-action-properties' }"></span>
          <br/>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'sla-' + id() }">
          <span data-bind="template: { name: 'common-action-sla' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'credentials-' + id() }">
          <span data-bind="template: { name: 'common-action-credentials' }"></span>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'transitions-' + id() }">
          <span data-bind="template: { name: 'common-action-transition' }"></span>
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
          <span data-bind="text: $root.workflow_properties.workflow.label"></span>
          <input type="text" data-bind="value: properties.workflow" />
          <select data-bind="options: $root.addActionWorkflows, optionsText: 'name', value: properties.selectedSubWorkflow"></select>
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


<script type="text/html" id="sqoop-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Sqoop') }</a></li>
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


<script type="text/html" id="shell-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Ssh') }</a></li>
        <li><a href="#properties" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <i class="fa fa-terminal"></i>
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


<script type="text/html" id="ssh-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Ssh') }</a></li>
        <li><a href="#properties" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <i class="fa fa-tty"></i>
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


<script type="text/html" id="fs-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Fs') }</a></li>
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


<script type="text/html" id="email-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Email') }</a></li>
        <li><a href="#properties" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <i class="fa fa-envelope-o"></i>
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


<script type="text/html" id="streaming-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Streaming') }</a></li>
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


<script type="text/html" id="distcp-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Dist Cp') }</a></li>
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

  var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflow_properties_json | n,unicode });
  ko.applyBindings(viewModel);

  viewModel.init();
  fullLayout(viewModel);

  function columnDropAdditionalHandler(widget) {
    widgetDraggedAdditionalHandler(widget);
  }

  function widgetDraggedAdditionalHandler(widget) {
    $("canvas").remove();
    if (viewModel.currentlyDraggedWidget() && viewModel.currentlyDraggedWidget().id() == ""){
      viewModel.workflow.newNode(widget);
      showAddActionDemiModal(widget);
    }
    else {
      if (viewModel.currentlyDraggedOp() == "move"){
        viewModel.workflow.moveNode(widget);
      }
      else {
        viewModel.workflow.newNode(widget, viewModel.workflow.addNode);
      }
      $(document).trigger("drawArrows");
    }
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
    var _from = $("#wdg_" + (typeof fromId == "function" ? fromId() : fromId));
    var _to = $("#wdg_" + (typeof toId == "function" ? toId() : toId));

    var _fromCenter = {
      x: _from.position().left + _from.outerWidth() / 2,
      y: _from.position().top + _from.outerHeight() + 3
    }

    var _toCenter = {
      x: _to.position().left + _to.outerWidth() / 2,
      y: _to.position().top - 5
    }

    var _curveCoords = {};

    if (_fromCenter.x == _toCenter.x) {
      _curveCoords.x = _fromCenter.x;
      _curveCoords.y = _fromCenter.y + (_toCenter.y - _fromCenter.y) / 2;
    }
    else {
      if (_fromCenter.x > _toCenter.x) {
        _fromCenter.x = _fromCenter.x - 5;
        _toCenter.x = _toCenter.x + 5;
      }
      else {
        _fromCenter.x = _fromCenter.x + 5;
        _toCenter.x = _toCenter.x - 5;
      }
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
      strokeStyle: '#e5e5e5'
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
    _linkMappingTimeout = window.setTimeout(renderChangeables, 25);
  });

  $(document).on("editingToggled", function(){
    $("canvas").remove();
    window.setTimeout(renderChangeables, 100);
  });

  function resizeDrops() {
    $(".drop-target-side").each(function () {
      var _el = $(this);
      _el.height(0);
      window.setTimeout(function(){
        _el.height(_el.parent().parent().innerHeight() - 12);
      }, 20);
    });
  }

  function renderChangeables() {
    resizeDrops();
    drawArrows();
  }

  $(document).ready(function(){
    renderChangeables();

    var resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        renderChangeables();
      }, 200);
    });

  });

</script>

${ commonfooter(messages) | n,unicode }
