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
from desktop.views import commonheader, commonfooter, commonshare
from django.utils.translation import ugettext as _
%>

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Workflow Editor"), "Oozie", user, "40px") | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("workflow") > -1) {
      location.href = "/oozie/editor/workflow/edit/?" + window.location.hash.substr(1);
    }
  }
</script>


<div id="editor">

<%dashboard:layout_toolbar>
  <%def name="skipLayout()"></%def>
  <%def name="widgetSectionName()">${ _('ACTIONS') }</%def>
  <%def name="widgets()">
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableHiveAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableHiveAction());}}}"
         title="${_('Hive Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableHive2Action(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableHive2Action());}}}"
         title="${_('HiveServer2 Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon"><sup style="color: #338bb8; margin-left: -4px; top: -14px; font-size: 12px">2</sup></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true},
                    draggable: {data: draggablePigAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggablePigAction());}}}"
         title="${_('Pig Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_pig_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableJavaAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableJavaAction());}}}"
         title="${_('Java program')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-code-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSqoopAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSqoopAction());}}}"
         title="${_('Sqoop 1')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_sqoop_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableMapReduceAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableMapReduceAction());}}}"
         title="${_('MapReduce job')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-archive-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSubworkflowAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSubworkflowAction());}}}"
         title="${_('Sub workflow')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-code-fork"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableShellAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableShellAction());}}}"
         title="${_('Shell')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-terminal"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSshAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSshAction());}}}"
         title="${_('Ssh')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-tty"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableFsAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableFsAction());}}}"
         title="${_('HDFS Fs')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableEmailAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableEmailAction());}}}"
         title="${_('Email')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-envelope-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableStreamingAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableStreamingAction());}}}"
         title="${_('Streaming')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-exchange"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableDistCpAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableDistCpAction());}}}"
         title="${_('Distcp')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-files-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableKillNode(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableKillNode());}}}"
         title="${_('Kill')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-stop"></i></a>
    </div>
</%def>
</%dashboard:layout_toolbar>



<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">

    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}, visible: workflow.id() != null">
      <i class="fa fa-fw fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-fw fa-pencil"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsModal" data-bind="css: {'btn': true}">
      <i class="fa fa-fw fa-cog"></i>
    </button>

    <a title="${ _('Workspace') }" target="_blank" rel="tooltip" data-placement="right"
        data-original-title="${ _('Go upload additional files and libraries to the deployment directory on HDFS') }"
        data-bind="css: {'btn': true}, attr: {href: '/filebrowser/view' + $root.workflow.properties.deployment_dir() }">
      <i class="fa fa-fw fa-folder-open"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: $root.save, css: {'btn': true}">
      <i class="fa fa-fw fa-save"></i>
    </button>

    <a class="share-link btn" rel="tooltip" data-placement="bottom" data-bind="click: openShareModal,
        attr: {'data-original-title': '${ _("Share") } ' + name},
        css: {'isShared': isShared(), 'btn': true},
        visible: workflow.id() != null">
      <i class="fa fa-users"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a class="btn" href="${ url('oozie:new_workflow') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-fw fa-file-o"></i>
    </a>

    <a class="btn" href="${ url('oozie:list_editor_workflows') }" title="${ _('Workflows') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-fw fa-tags"></i>
    </a>
  </div>

  <form class="form-search">
    <div class="inline object-name">
      <span data-bind="editable: $root.workflow.name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
    </div>
    <div class="inline object-description">
      <span data-bind="editable: $root.workflow.properties.description, editableOptions: {enabled: $root.isEditing(), placement: 'right', emptytext: '${_('Add a description...')}'}"></span>
    </div>
  </form>
</div>



<div id="emptyDashboard" data-bind="fadeVisible: !isEditing() && oozieColumns().length == 0">
  <div style="float:left; padding-top: 90px; margin-right: 20px; text-align: center; width: 260px">${ _('Click on the pencil to get started with your dashboard!') }</div>
  <img src="/static/art/hint_arrow.png" />
</div>

<div id="emptyDashboardEditing" data-bind="fadeVisible: isEditing() && oozieColumns().length == 0 && previewColumns() == ''">
  <div style="float:right; padding-top: 90px; margin-left: 20px; text-align: center; width: 260px">${ _('Pick an index and Click on a layout to start your dashboard!') }</div>
  <img src="/static/art/hint_arrow_horiz_flipped.png" />
</div>


<div data-bind="css: {'dashboard': true, 'readonly': ! isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="template: { name: 'column-template', foreach: oozieColumns}">
    </div>
    <div class="clearfix"></div>
  </div>
</div>


<script type="text/html" id="column-template">
  <div data-bind="css: klass()" style="min-height: 50px !important;">
    <div data-bind="template: { name: 'row-template', data: oozieStartRow }" style="margin-top: 50px"></div>

    <div class="container-fluid" data-bind="visible: $root.isEditing() && oozieRows().length > 0">
      <div class="row-fluid">
        <div data-bind="visible: enableOozieDropOnBefore, css: {'span4 offset4': true, 'drop-target': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(x, y){ var _w = $root.addDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
        <div data-bind="visible: ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}"></div>
      </div>
    </div>
    <div data-bind="template: { name: 'internal-row-template', foreach: oozieRows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing() && rows().length > 0">
      <div class="row-fluid">
        <div data-bind="visible: enableOozieDropOnAfter, css: {'span4 offset4': true, 'drop-target': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }">
          <span data-bind="visible: oozieRows().length == 0">${ _('Drop your action here') }</span>
        </div>
        <div data-bind="visible: ! enableOozieDropOnAfter(), css: {'drop-target drop-target-disabled': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}"></div>
      </div>
    </div>

    <div data-bind="template: { name: 'row-template', data: oozieEndRow }"></div>

    <div data-bind="template: { name: 'row-template', data: oozieKillRow }" style="margin-top: 60px"></div>
  </div>
</script>


<script type="text/html" id="internal-column-template">
  <div data-bind="css: klass(), style: {'minHeight': '50px !important', 'width': percWidth() + '%' }">
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="visible: ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}"></div>
      <div data-bind="visible: enableOozieDropOnBefore, css: {'drop-target': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
    </div>
    <div data-bind="template: { name: 'internal-row-template', foreach: rows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="visible: ! enableOozieDropOnAfter(), css: {'drop-target drop-target-disabled': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}"></div>
      <div data-bind="visible: enableOozieDropOnAfter, css: {'drop-target': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }"></div>
    </div>
  </div>
</script>


<script type="text/html" id="row-template">
  <div class="container-fluid">
    <div class="row-fluid">
      <div class="span4 offset4">
        <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
          sortable: { template: 'widget-template', data: widgets, allowDrop: $root.isEditing() && widgets().length < 1, isEnabled: $root.isEditing() && widgets().length < 1,
          options: {'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
              'stop': function(event, ui){},
              'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
              dragged: function(widget){widgetDraggedAdditionalHandler(widget)}}">
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="internal-row-template">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="visible: $index() > 0 && $root.isEditing() && ! $root.isRowBeforeJoin($data) && ! $root.isRowAfterFork($data)" style="margin-bottom: 10px">
      <div data-bind="css: {'span1': true, 'offset3andhalf': ($root.isEditing() && $parents.length <= 2 && columns().length == 0), 'offset4': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}"></div>
      <div data-bind="css: {'span10': ($parents.length > 2 || columns().length > 0), 'span4': ($parents.length <= 2 && columns().length == 0), 'offset3andhalf': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}"></div>
        <div style="text-align: left" data-bind="visible: $root.isEditing() && enableOozieDropOnBefore(), css: {'drop-target': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}"></div>
    </div>
    <div class="row-fluid" data-bind="style: {'width': columns().length < 5 ? '100%' : (columns().length * 25)+'%' }">
      <div data-bind="css: {'span1': true, 'offset3andhalf': ($root.isEditing() && $parents.length <= 2 && columns().length == 0), 'offset4': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && enableOozieDropOnSide() && !($data.widgets().length > 0 && ['join-widget', 'decision-widget'].indexOf($data.widgets()[0].widgetType()) > -1), css: {'drop-target drop-target-side': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div  data-bind="css: {'span10': ($parents.length > 2 || columns().length > 0), 'span4': ($parents.length <= 2 && columns().length == 0), 'offset3andhalf': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}">
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
      <div  data-bind="css: {'span1': true, 'readonly no-margin': ! $root.isEditing()}, style: {'margin': ! $root.isEditing() ? '0':''}">
        <div data-bind="visible: $root.isEditing() && enableOozieDropOnSide() && !($data.widgets().length > 0 && ['join-widget', 'decision-widget'].indexOf($data.widgets()[0].widgetType()) > -1), css: {'drop-target drop-target-side': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, false); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
    </div>
  </div>

</script>

<script type="text/html" id="widget-template">
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass() + (ooziePropertiesExpanded()?' expanded-widget':''),
      draggable: {data: $data, isEnabled: true, options: {'handle': '.move-widget', 'opacity': 0.7, 'refreshPositions': true, 'start': function(event, ui){ $root.setCurrentlyDraggedWidget($data, event.toElement); }, 'stop': function(event, ui){ $root.enableSideDrop($data); }, 'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();  var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.currentTarget).find('h2').text());_title.appendTo(_par);_par.css('minHeight', '10px');_par.width(120);return _par;}}}">
    <h2 class="card-heading simple" data-bind="visible: widgetType() != 'start-widget' && widgetType() != 'end-widget' &&
        id() != '17c9c895-5a16-7443-bb81-f34b30b21548' && (['fork-widget', 'join-widget', 'decision-widget'].indexOf(widgetType()) == -1 || $root.isEditing())">

      <span data-bind="visible: $root.isEditing() && oozieMovable() && ! oozieExpanded() && ! ooziePropertiesExpanded() && $root.newAction() == null">
        <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
        &nbsp;
        <a href="javascript:void(0)" class="move-widget clone-widget"><i class="fa fa-copy"></i></a>
        &nbsp;
      </span>

      <!-- ko if: widgetType() == 'hive-widget' -->
      <img src="/oozie/static/art/icon_beeswax_48.png" class="widget-icon">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'hive2-widget' -->
      <img src="/oozie/static/art/icon_beeswax_48.png" class="widget-icon"><sup style="color: #338bb8; margin-left: -4px">2</sup>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'pig-widget' -->
      <img src="/oozie/static/art/icon_pig_48.png" class="widget-icon">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'java-widget' -->
      <a class="widget-icon"><i class="fa fa-file-code-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'sqoop-widget' -->
      <img src="/oozie/static/art/icon_sqoop_48.png" class="widget-icon">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'mapreduce-widget' -->
      <a class="widget-icon"><i class="fa fa-file-archive-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'subworkflow-widget' -->
      <a class="widget-icon"><i class="fa fa-code-fork"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'shell-widget' -->
      <a class="widget-icon"><i class="fa fa-terminal"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'ssh-widget' -->
      <a class="widget-icon"><i class="fa fa-tty"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'fs-widget' -->
      <a class="widget-icon"><i class="fa fa-file-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'email-widget' -->
      <a class="widget-icon"><i class="fa fa-envelope-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'streaming-widget' -->
      <a class="widget-icon"><i class="fa fa-exchange"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'distcp-widget' -->
      <a class="widget-icon"><i class="fa fa-files-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'kill-widget' -->
      <a class="widget-icon"><i class="fa fa-stop"></i></a>
      <!-- /ko -->

      <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>

      <!-- ko if: widgetType() == 'decision-widget' -->
        <div class="inline pull-right" data-bind="visible: $root.isEditing() && $root.workflow.getNodeById(id()) && $root.workflow.getNodeById(id()).children().length <= 1 && ! oozieExpanded() && ! ooziePropertiesExpanded()">
          <a href="javascript:void(0)" data-bind="click: function(w){addActionDemiModalFieldCancel();$root.removeWidget(w);}"><i class="fa fa-times"></i></a>
        </div>
      <!-- /ko -->
      <!-- ko if: widgetType() != 'decision-widget' -->
        <div class="inline pull-right" data-bind="visible: $root.isEditing() && (['start-widget', 'end-widget', 'fork-widget', 'join-widget'].indexOf(widgetType()) == -1) && ! oozieExpanded() && ! ooziePropertiesExpanded()">
          <a href="javascript:void(0)" data-bind="click: function(w){addActionDemiModalFieldCancel();$root.removeWidget(w);}"><i class="fa fa-times"></i></a>
        </div>
      <!-- /ko -->
      <!-- ko if: ooziePropertiesExpanded() -->
        <div class="inline pull-right">
          <a href="javascript:void(0)" data-bind="click: toggleProperties"><i class="fa fa-caret-square-o-left"></i></a>
        </div>
      <!-- /ko -->
    </h2>
    <div class="card-body" style="padding: 0; position: relative">
      <div class="advanced-triangle-container" data-bind="visible: $root.isEditing() && ! ooziePropertiesExpanded() && oozieMovable(), click: toggleProperties">
        <div class="advanced-triangle">
          <a href="javascript:void(0)"><i class="fa fa-cogs"></i></a>
        </div>
      </div>
      <div data-bind="template: { name: function() { return widgetType(); }}" class="widget-main-section"></div>
    </div>
  </div>
</script>


<script type="text/html" id="fork-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px">
    <div class="big-icon"><i class="fa fa-sitemap"></i></div>
    <div data-bind="visible: $root.isEditing" style="padding-left: 10px; padding-bottom: 10px">
      <a class="pointer" data-bind="click: function() { $root.convertToDecision($parent, $data) }">${_('Convert to Decision')} <i class="fa fa-wrench"></i></a>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="join-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px">
    <div class="big-icon"><i class="fa fa-sitemap fa-rotate-180"></i></div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="decision-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px">
    <div class="big-icon" data-bind="visible: ! $root.isEditing()"><i class="fa fa-magic"></i></div>

    <div data-bind="visible: $root.isEditing" style="padding: 10px">
      <ul data-bind="foreach: children" class="unstyled">
        <li>${ _('To') }
        <select data-bind="options: $root.workflow.nodeIds,
                     optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
                     value: $data['to']
                     ">
        </select>
        ${ _('if') } <input type="text" data-bind="value: $data['condition']" />
        </li>
      </ul>
      <a data-bind="click: function(){  children.push({'to': '', 'condition': ''});}">${ _('Jump to another node') } <i class="fa fa-plus"></i></a>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="kill-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px">
    <div class="big-icon" data-bind="visible: id() == '17c9c895-5a16-7443-bb81-f34b30b21548'" title="${ _('It is where we finish if failure!') }"><i class="fa fa-stop"></i></div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: $parent.ooziePropertiesExpanded">
        <h6 class="field-title">${ _('Message') }</h6>
        <textarea class="span12" data-bind="value: properties.message" />
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="start-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px;">
    <div class="big-icon" title="${ _('It is where we start!') }"><i class="fa fa-flag-checkered"></i></div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="end-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px">
    <div class="big-icon" title="${ _('It is where we successfully finish!') }"><i class="fa fa-dot-circle-o"></i></div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="common-action-properties">
  <div class="properties">
    <h6>${ _('Prepare') }</h6>
    <ul data-bind="visible: properties.prepares().length > 0, foreach: properties.prepares" class="unstyled">
      <li>
        <div style="display: inline-block; width: 60px" data-bind="text: type"></div>
        <input type="text" class="filechooser-input input-xlarge"
            data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.prepares.help_text }"/>
        <a href="#" data-bind="click: function(){ $parent.properties.prepares.remove(this); $(document).trigger('drawArrows') }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>
    <a class="pointer" data-bind="click: function(){ properties.prepares.push({'type': 'mkdir', 'value': ''}); $(document).trigger('drawArrows') }">
      ${ _('Directory') } <i class="fa fa-plus"></i>
    </a>
    <a class="pointer" data-bind="click: function(){ properties.prepares.push({'type': 'delete', 'value': ''}); $(document).trigger('drawArrows') }">
      ${ _('Delete') } <i class="fa fa-plus"></i>
    </a>

    <h6>${ _('Job XML') }</h6>
    <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: properties.job_xml, filechooserOptions: globalFilechooserOptions, attr: { placeholder: $root.workflow_properties.job_xml.help_text }"/>

    <h6>
      <a class="pointer" data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); $(document).trigger('drawArrows') }">
        ${ _('Properties') } <i class="fa fa-plus"></i>
      </a>
    </h6>
    <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
      <li>
        <input type="text" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }"/>
        <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }"/>
        <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>
    <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

    <h6>
      <a class="pointer" data-bind="click: function(){ properties.archives.push({'name': ''});$(document).trigger('drawArrows') }">
        ${ _('Archives') } <i class="fa fa-plus"></i>
      </a>
    </h6>
    <ul data-bind="visible: properties.archives().length > 0, foreach: properties.archives" class="unstyled">
      <li>
        <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: name, filechooserOptions: globalFilechooserOptions, value: name, attr: { placeholder: $root.workflow_properties.archives.help_text }"/>
        <a href="#" data-bind="click: function(){ $parent.properties.archives.remove(this); $(document).trigger('drawArrows') }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>
    <em data-bind="visible: properties.archives().length == 0">${ _('No archives defined.') }</em>
  </div>
</script>


<script type="text/html" id="common-properties-pig-arguments">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.arguments.push({'value': ''}); $(document).trigger('drawArrows') }">
      ${ _('Arguments') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="visible: properties.arguments().length > 0, foreach: properties.arguments">
    <li>
      <input type="text" class="span11" data-bind="value: value"/>
      <a href="#" data-bind="click: function(){ $parent.properties.arguments.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
  <em data-bind="visible: properties.arguments().length == 0">${ _('No arguments defined.') }</em>
</script>


<script type="text/html" id="common-properties-arguments">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.arguments.push({'value': ''}); $(document).trigger('drawArrows') }">
      ${ _('Arguments') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="visible: properties.arguments().length > 0, foreach: properties.arguments">
    <li style="margin-bottom: 3px">
      <input type="text" class="span11" data-bind="value: value, attr: { placeholder: $root.workflow_properties.arguments.help_text }"/>
      <a href="#" data-bind="click: function(){ $parent.properties.arguments.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
</script>


<script type="text/html" id="common-properties-files">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.files.push({'value': ''}); $(document).trigger('drawArrows') }">
      ${ _('Files') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="foreach: properties.files">
    <li style="margin-bottom: 3px">
      <input type="text" class="filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions"/>
      <a href="#" data-bind="click: function(){ $parent.properties.files.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
</script>


<script type="text/html" id="common-properties-parameters">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.parameters.push({'value': ''}); $(document).trigger('drawArrows')}">
      ${ _('Parameters') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="foreach: properties.parameters">
    <li style="margin-bottom: 3px">
      <input type="text" class="filechooser-input seventy" data-bind="value: value, filechooser: value, filechooserOptions: globalFilechooserOptions, filechooserDisabled: true, filechooserPrefixSeparator: '=', event: { change: enableFilechooser, keyup: enableFilechooser }, attr: { placeholder: $parent.actionParametersUI }, typeahead: { target: value, source: $parent.actionParameters, sourceSuffix: '=', triggerOnFocus: true }"/>
      <a href="#" data-bind="click: function(){ $parent.properties.parameters.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
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
  <em data-bind="visible: $root.credentials() == null || $root.credentials().length == 0">${ _('No available credentials.') }</em>
  <select data-bind="visible: $root.credentials() != null && $root.credentials().length > 0, options: $root.credentials, value: properties.credentials" size="5" multiple="true"></select>
</script>


<script type="text/html" id="common-action-sla">
  <div data-bind="with: properties">
     ${ utils.slaForm() }
  </div>
</script>


<script type="text/html" id="common-fs-link">
  <!-- ko if: with_label -->
    <a data-bind="attr: {href: '/filebrowser/view' + $data.path }" target="_blank" title="${ _('Open') }">
      <pan data-bind="text: $data.path"></span>
    </a>
  <!-- /ko -->

   <!-- ko if: ! with_label -->
     <a data-bind="attr: {href: '/filebrowser/view' + $data.path }" target="_blank" title="${ _('Open') }">
       <i class="fa fa-external-link-square"></i>
     </a>
   <!-- /ko -->
</script>



<script type="text/html" id="hive-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <input type="text" class="filechooser-input" data-bind="filechooser: properties.script_path, filechooserOptions: globalFilechooserOptions, attr: { placeholder:  $root.workflow_properties.script_path.help_text }"/>
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: false}}'></span>

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-parameters' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="template: { name: 'common-action-properties' }"></span>
          <br/>
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


<script type="text/html" id="hive2-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <input type="text" class="filechooser-input" data-bind="filechooser: properties.script_path, filechooserOptions: globalFilechooserOptions, attr: { placeholder:  $root.workflow_properties.script_path.help_text }"/>
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: false}}'></span>

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-parameters' }"></div>
        </div>
      </div>
    </div>


    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="text: $root.workflow_properties.jdbc_url.label"></span>
          <input type="text" data-bind="value: properties.jdbc_url" />
          <br/>
          <span data-bind="text: $root.workflow_properties.password.label"></span>
          <input type="text" data-bind="value: properties.password" />
          <br/>
          <span data-bind="template: { name: 'common-action-properties' }"></span>
          <br/>
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


<script type="text/html" id="pig-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <input type="text" class="filechooser-input" data-bind="filechooser: properties.script_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.script_path, attr: { placeholder:  $root.workflow_properties.script_path.help_text }" />
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: false}}'></span>

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-parameters' }"></div>
          <div class="span6" data-bind="template: { name: 'common-properties-files' }"></div>
        </div>

      </div>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="template: { name: 'common-properties-pig-arguments' }"></span>
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
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <pan data-bind="text: properties.main_class" />
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <span data-bind="text: $root.workflow_properties.jar_path.label" style="display: inline-block; width: 75px"></span>
        <input type="text" class="filechooser-input input-xlarge"
            data-bind="filechooser: properties.jar_path, filechooserOptions: globalFilechooserOptions, attr: { placeholder: $root.workflow_properties.jar_path.help_text }"
        />
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.jar_path(), with_label: false}}'></span>

        <br/>
        <span data-bind="text: $root.workflow_properties.main_class.label" style="display: inline-block; width: 75px"></span>
        <input type="text" class="input-xlarge" data-bind="value: properties.main_class, attr: { placeholder: $root.workflow_properties.main_class.help_text }" />

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-arguments' }"></div>
          <div class="span6" data-bind="template: { name: 'common-properties-files' }"></div>
        </div>

      </div>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <h6>
            <a class="pointer" data-bind="click: function(){ properties.java_opts.push({'value': ''}); }">
              <span data-bind="text: $root.workflow_properties.java_opts.label"></span> <i class="fa fa-plus"></i>
            </a>
          </h6>
          <ul class="unstyled" data-bind="foreach: properties.java_opts">
            <li>
              <input type="text" data-bind="value: value, attr: { placeholder: $root.workflow_properties.java_opts.help_text }" class="input-xlarge"/>
              <a href="#" data-bind="click: function(){ $parent.properties.java_opts.remove(this); }">
                <i class="fa fa-minus"></i>
              </a>
            </li>
          </ul>

          <span data-bind="text: $root.workflow_properties.capture_output.label"></span>
          <input type="checkbox" data-bind="checked: properties.capture_output" />
          <br/>
          <br/>

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


<script type="text/html" id="sqoop-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <span data-bind="text: $root.workflow_properties.command.label"></span>
        <input type="text" data-bind="value: properties.command" />
        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-parameters' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <a href="javascript:void(0)">
        <span type="text" data-bind="text: properties.command().slice(0, 70), attr: { title: properties.command() }" />...
      </a>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
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


<script type="text/html" id="mapreduce-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <span data-bind="text: $root.workflow_properties.jar_path.label"></span>
        <input type="text" class="filechooser-input" data-bind="filechooser: properties.jar_path, filechooserOptions: globalFilechooserOptions, value: properties.jar_path" />
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.jar_path(), with_label: false} }'></span>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); $(document).trigger('drawArrows') }">
            ${ _('Properties') } <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
          <li>
            <input type="text" class="span4" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }"/>
            <input type="text" class="filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }"/>
            <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.jar_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
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


<script type="text/html" id="subworkflow-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <select data-bind="options: $root.subworfklows, optionsText: 'name', optionsValue: 'value', value: properties.workflow"></select>
        <span data-bind="visible: properties.workflow().length > 0">
          <a href="#" data-bind="attr: { href: '${ url('oozie:edit_workflow') }' + '?workflow=' + properties.workflow() }" target="_blank" title="${ _('Open') }">
            <i class="fa fa-external-link-square"></i>
          </a>
        </span>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <!-- ko if: $root.getSubWorkflow(properties.workflow()) -->
        <span data-bind="with: $root.getSubWorkflow(properties.workflow())">
          <a href="#" data-bind="attr: { href: '${ url('oozie:edit_workflow') }' + '?workflow=' + $data.value() }" target="_blank" title="${ _('Open') }">
            <span data-bind="text: $data.name"></span>
          </a>
        </span>
      <!-- /ko -->
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="text: $root.workflow_properties.propagate_configuration.label"></span>
          <input type="checkbox" data-bind="checked: properties.propagate_configuration" />

          <br/>

          <h6>
            <a class="pointer" data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); $(document).trigger('drawArrows') }">
              ${ _('Properties') } <i class="fa fa-plus"></i>
            </a>
          </h6>
          <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
            <li>
              <input type="text" data-bind="value: name"/>
              <input type="text" data-bind="value: value"/>
              <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
                <i class="fa fa-minus"></i>
              </a>
            </li>
          </ul>
          <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

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


<script type="text/html" id="shell-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <input type="text" data-bind="value: properties.shell_command" />
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.shell_command(), with_label: false} }'></span>

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-arguments' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.shell_command(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="text: $root.workflow_properties.capture_output.label"></span>
          <input type="checkbox" data-bind="checked: properties.capture_output" />
          <br/>

          <h6>
            <a class="pointer" data-bind="click: function(){ properties.env_var.push({'value': ''}); }">
              <span data-bind="text: $root.workflow_properties.env_var.label"></span> <i class="fa fa-plus"></i>
            </a>
          </h6>
          <ul data-bind="foreach: properties.env_var" class="unstyled">
            <li>
              <input type="text" class="input-xlarge" data-bind="value: value, attr: { placeholder: $root.workflow_properties.env_var.help_text }"/>
              <a href="#" data-bind="click: function(){ $parent.properties.env_var.remove(this); }">
                <i class="fa fa-minus"></i>
              </a>
            </li>
          </ul>

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


<script type="text/html" id="ssh-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">

      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <span data-bind="text: $root.workflow_properties.host.label"></span>
        <input type="text" data-bind="value: properties.host" />
        <br/>

        <span data-bind="text: $root.workflow_properties.ssh_command.label"></span>
        <input type="text" data-bind="value: properties.ssh_command" />
        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-arguments' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="text: properties.host" />
      <span data-bind="text: properties.ssh_command().slice(0, 75)" />
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="text: $root.workflow_properties.capture_output.label"></span>
          <input type="checkbox" data-bind="checked: properties.capture_output" />
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


<script type="text/html" id="fs-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="text: '${ _("Delete") }', visible: properties.deletes().length > 0"></span>
      <ul data-bind="foreach: properties.deletes" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
        </li>
      </ul>

      <span data-bind="text: '${ _("Create") }', visible: properties.mkdirs().length > 0 || properties.touchzs().length > 0"></span>
      <ul data-bind="foreach: properties.mkdirs" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
        </li>
      </ul>
      <ul data-bind="foreach: properties.touchzs" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
        </li>
      </ul>

      <span data-bind="text: '${ _("Move") }', visible: properties.moves().length > 0"></span>
      <ul data-bind="foreach: properties.moves" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: source(), with_label: true} }, visible: source().length > 0'></span>
          ${ _('to') }
          <span data-bind='template: { name: "common-fs-link", data: {path: destination(), with_label: true} }, visible: destination().length > 0'></span>
        </li>
      </ul>

      <span data-bind="text: '${ _("Change permissions") }', visible: properties.chmods().length > 0"></span>
      <ul data-bind="foreach: properties.chmods" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
          ${ _('to') }
          <span data-bind="text: permissions"/>
          <span data-bind="visible: ! dir_files(), text: '${ _('for directories') }'"/>
          <span data-bind="visible: dir_files(), text: '${ _('for directories and files') }'"/>
          <span data-bind="visible: recursive, text: '${ _('recursivelt') }'"/>
        </li>
      </ul>

      <span data-bind="text: '${ _("Change groups") }', visible: properties.chgrps().length > 0"></span>
      <ul data-bind="foreach: properties.chgrps" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
          ${ _('to') }
          <span data-bind="text: group"/>
          <span data-bind="visible: ! dir_files(), text: '${ _('for directories') }'"/>
          <span data-bind="visible: dir_files(), text: '${ _('for directories and files') }'"/>
          <span data-bind="visible: recursive, text: '${ _('recursively') }'"/>
        </li>
      </ul>
    </div>


    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <h6>
          <a class="pointer" data-bind="click: function(){ properties.deletes.push(ko.mapping.fromJS({'value': ''})); }">
            <span data-bind="text: $root.workflow_properties.deletes.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.deletes" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.deletes.help_text }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.deletes.remove(this); }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.mkdirs.push(ko.mapping.fromJS({'value': ''})); }">
            <span data-bind="text: $root.workflow_properties.mkdirs.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.mkdirs" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.mkdirs.help_text }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.mkdirs.remove(this); }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.touchzs.push(ko.mapping.fromJS({'value': ''})); }">
            <span data-bind="text: $root.workflow_properties.touchzs.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.touchzs" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.touchzs.help_text }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.touchzs.remove(this); }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.moves.push(ko.mapping.fromJS({'source': '', 'destination': ''})); }">
            <span data-bind="text: $root.workflow_properties.moves.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.moves" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: source, filechooserOptions: globalFilechooserOptions, value: source" placeholder="${ _('Source path') }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: source(), with_label: false} }, visible: source().length > 0'></span>

            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: destination, filechooserOptions: globalFilechooserOptions, value: destination" placeholder="${ _('New destination path') }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: destination(), with_label: false} }, visible: destination().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.moves.remove(this); }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

      </div>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.chmods.push(ko.mapping.fromJS({'value': '', 'permissions': '755', 'dir_files': false, 'recursive': false})); }">
            <span data-bind="text: $root.workflow_properties.chmods.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.chmods" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.chmods.help_text }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>

            <input type="text" class="input-small" data-bind="value: permissions" placeholder="${ _('755, -rwxrw-rw-') }"/>
            ${ _('Only for directories') }
            <input type="checkbox" data-bind="checked: dir_files"/>
            ${ _('Recursive to sub directories') }
            <input type="checkbox" data-bind="checked: recursive"/>
            <a href="#" data-bind="click: function(){ $parent.properties.chmods.remove(this); }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.chgrps.push(ko.mapping.fromJS({'value': '', 'group': '', 'dir_files': false, 'recursive': false})); }">
            <span data-bind="text: $root.workflow_properties.chgrps.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.chgrps" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.chgrps.help_text }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>

            <input type="text" class="input-small" data-bind="value: group" placeholder="${ _('e.g. newgroup') }"/>
            ${ _('Only for directories') }
            <input type="checkbox" data-bind="checked: dir_files"/>
            ${ _('Recursive to sub directories') }
            <input type="checkbox" data-bind="checked: recursive"/>
            <a href="#" data-bind="click: function(){ $parent.properties.chgrps.remove(this); }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

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


<script type="text/html" id="email-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <span data-bind="text: $root.workflow_properties.to.label" style="display: inline-block; width: 80px"></span>
        <input type="text" data-bind="value: properties.to, attr: { placeholder: $root.workflow_properties.to.help_text }" />
        <br/>

        <span data-bind="text: $root.workflow_properties.subject.label" style="display: inline-block; width: 80px"></span>
        <input type="text" data-bind="value: properties.subject, attr: { placeholder: $root.workflow_properties.subject.help_text }" />
        <br/>

        <span data-bind="text: $root.workflow_properties.body.label" style="display: inline-block; width: 80px"></span>
        <textarea data-bind="value: properties.body, attr: { placeholder: $root.workflow_properties.body.help_text }"></textarea>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      ${ _('To') }
      <span data-bind="text: properties.to"/>
      <br/>
      ${ _('About') }
      <span data-bind="text: properties.subject"/>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <span data-bind="text: $root.workflow_properties.cc.label"></span>
          <input type="text" data-bind="value: properties.cc, attr: { placeholder: $root.workflow_properties.cc.help_text }" />
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


<script type="text/html" id="streaming-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <span data-bind="text: $root.workflow_properties.mapper.label"></span>
        <input type="text" data-bind="value: properties.mapper" />
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.mapper(), with_label: false} }'></span>
        <br/>

        <span data-bind="text: $root.workflow_properties.reducer.label"></span
        <input type="text" data-bind="value: properties.reducer" />
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.reducer(), with_label: false} }'></span>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="text: $root.workflow_properties.mapper.label, visible: properties.mapper().length > 0"></span>
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.mapper(), with_label: true} }, visible: properties.mapper().length > 0'></span>
      </br>
      <span data-bind="text: $root.workflow_properties.reducer.label, visible: properties.reducer().length > 0"></span>
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.reducer(), with_label: true} }, visible: properties.reducer().length > 0'></span>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
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


<script type="text/html" id="distcp-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.distcp_parameters.push(ko.mapping.fromJS({'value': ''}));}">
            <span data-bind="text: $root.workflow_properties.distcp_parameters.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.distcp_parameters" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.distcp_parameters.help_text }"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.distcp_parameters.remove(this);  }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

      </div>
    </div>
    
    <div data-bind="visible: ! $root.isEditing()">
      ${ _('Parameters') }
      <ul data-bind="foreach: properties.distcp_parameters" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
        </li>
      </ul>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">

		 <h6>${ _('Prepare') }</h6>
		   <ul data-bind="visible: properties.prepares().length > 0, foreach: properties.prepares" class="unstyled">
		     <li>
		       <div style="display: inline-block; width: 60px" data-bind="text: type"></div>
		       <input type="text" class="filechooser-input input-xlarge"
		            data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.prepares.help_text }"/>
		        <a href="#" data-bind="click: function(){ $parent.properties.prepares.remove(this); $(document).trigger('drawArrows') }">
		          <i class="fa fa-minus"></i>
		        </a>
		      </li>
		   </ul>
		   <a class="pointer" data-bind="click: function(){ properties.prepares.push({'type': 'mkdir', 'value': ''}); $(document).trigger('drawArrows') }">
		     ${ _('Directory') } <i class="fa fa-plus"></i>
		   </a>
		   <a class="pointer" data-bind="click: function(){ properties.prepares.push({'type': 'delete', 'value': ''}); $(document).trigger('drawArrows') }">
		     ${ _('Delete') } <i class="fa fa-plus"></i>
		   </a>
		
		   <h6>
		     <a class="pointer" data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); $(document).trigger('drawArrows') }">
		       ${ _('Properties') } <i class="fa fa-plus"></i>
		     </a>
		   </h6>
           <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
           <li>
             <input type="text" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }"/>
             <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }"/>
             <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
               <i class="fa fa-minus"></i>
              </a>
             </li>
           </ul>
           <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

           <h6>             
             <span data-bind="text: $root.workflow_properties.java_opts.label"></span>             
           </h6>
           <input type="text" class="input-xlarge" data-bind="value: properties.java_opts, attr: { placeholder: $root.workflow_properties.java_opts.help_text }" />
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


<div id="addActionDemiModal" class="demi-modal demi-modal-half hide" data-backdrop="false">
  <div class="modal-body">
    <table data-bind="foreach: addActionProperties">
      <tr>
        <td data-bind="text: label" style="width: 1%; padding-right: 10px" class="no-wrap"></td>
        <td>
          <!-- ko if: type() == '' -->
          <input type="text" class="filechooser-input" data-bind="value: value, valueUpdate:'afterkeydown', filechooser: value, filechooserOptions: globalFilechooserOptions, attr: { placeholder: help_text }">
          <!-- /ko -->
          <!-- ko if: type() == 'text' -->
          <input type="text" data-bind="value: value, valueUpdate:'afterkeydown', attr: { placeholder: help_text }" class="input-xlarge"/>
          <!-- /ko -->
          <!-- ko if: type() == 'textarea' -->
          <textarea data-bind="value: value, valueUpdate:'afterkeydown'" class="input-xlarge"></textarea>
          <!-- /ko -->
          <!-- ko if: type() == 'workflow' -->
          <select data-bind="options: $root.subworfklows, optionsText: 'name', optionsValue: 'value', value: value"></select>
          <!-- /ko -->

          <!-- ko if: type() == 'distcp' -->
          ${ _('Source') }
          <input type="text" class="filechooser-input" data-bind="value: value()[0].value, valueUpdate:'afterkeydown', filechooser: value()[0].value, filechooserOptions: globalFilechooserOptions" placeholder="${ _('e.g. ${nameNode1}/path/to/input.txt') }">
          ${ _('Destination') }
          <input type="text" class="filechooser-input" data-bind="value: value()[1].value, valueUpdate:'afterkeydown', filechooser: value()[1].value, filechooserOptions: globalFilechooserOptions" placeholder="${ _('e.g. ${nameNode2}/path/to/output.txt') }">
          <!-- /ko -->

          <!-- ko if: ['jar_path', 'script_path', 'mapper', 'reducer'].indexOf(name()) != -1 &&  value().length > 0 -->
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false}}'></span>
          <!-- /ko -->
          <!-- ko if: name() == 'workflow' && $root.getSubWorkflow(value())-->
          <span data-bind="with: $root.getSubWorkflow(value())">
            <a href="#" data-bind="attr: { href: '${ url('oozie:edit_workflow') }' + '?workflow=' + $data.value() }" target="_blank" title="${ _('Open') }">
              <i class="fa fa-external-link-square"></i>
            </a>
          </span>
          <!-- /ko -->
        </td>
      </tr>
    </table>

    <br/>
    <a class="btn btn-primary disable-feedback" data-bind="css: {'disabled': ! addActionPropertiesFilledOut()}, click: function(field){ addActionPropertiesFilledOut() ? addActionDemiModalFieldPreview(field) : void(0) } ">
      ${ _('Add') }
    </a>
  </div>
</div>

<div id="settingsModal" class="modal fade hide">
  <div class="modal-header" style="padding-bottom: 2px">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="myModalLabel">${ _('Workflow Settings') }</h3>
  </div>
  <div class="modal-body">
      <h4>${ _('Variables') }</h4>
      <ul data-bind="foreach: $root.workflow.properties.parameters" class="unstyled">
        <!-- ko if: name() != 'oozie.use.system.libpath' -->
        <li>
          <input type="text" data-bind="value: name"/>
          <input type="text" data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.workflow.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
        <!-- /ko -->
      </ul>
      <a class="pointer" data-bind="click: function(){ $root.workflow.properties.parameters.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i> ${ _('Add parameter') }
      </a>

      <h4>${_("Workspace")}</h4>
      <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: {value: $root.workflow.properties.deployment_dir, displayJustLastBit: true}, filechooserOptions: globalFilechooserOptions" rel="tooltip"/>

	  <h4>${ _('Hadoop Properties') }</h4>
      <ul data-bind="foreach: $root.workflow.properties.properties" class="unstyled">
        <li>
          <input type="text" data-bind="value: name"/>
          <input type="text" data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.workflow.properties.properties.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <a class="pointer"  data-bind="click: function(){ $root.workflow.properties.properties.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i> ${ _('Add property') }
      </a>

      <h4>${ _("Toggle arrows") }</h4>
      <a title="${ _('Toggle arrow showing') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleArrows, css: {'btn': true, 'btn-inverse': hasArrows}">
        <i class="fa fa-fw fa-long-arrow-down"></i>
      </a>

      <h4>${ _("Job XML") }</h4>
      <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: $root.workflow.properties.job_xml, filechooserOptions: globalFilechooserOptions"/>

      <h4>${ _('SLA Configuration') }</h4>
      <div class="sla-form" data-bind="with: $root.workflow.properties">
        ${ utils.slaForm() }
      </div>
  </div>
</div>


<div id="submit-wf-modal" class="modal hide"></div>

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


</div>

<div id="exposeOverlay"></div>

<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<link rel="stylesheet" href="/oozie/static/css/common-editor.css">
<link rel="stylesheet" href="/oozie/static/css/workflow-editor.css">


${ dashboard.import_layout() }

${ commonshare() | n,unicode }

<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/share.vm.js"></script>
<script src="/static/js/jquery.hdfsautocomplete.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }

<script src="/oozie/static/js/workflow-editor.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.curvedarrow.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">
  ${ utils.slaGlobal() }

  var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflow_properties_json | n,unicode }, ${ subworkflows_json | n,unicode });
  ko.applyBindings(viewModel, $("#editor")[0]);

  var shareViewModel = setupSharing("#documentShareModal");
  shareViewModel.setDocId(${ doc1_id });

  viewModel.init();
  fullLayout(viewModel);

  var globalFilechooserOptions = {
    skipInitialPathIfEmpty: true,
    showExtraHome: true,
    uploadFile: true,
    createFolder: true,
    extraHomeProperties: {
      label: '${ _('Workspace') }',
      icon: 'fa-folder-open',
      path: viewModel.workflow.properties.deployment_dir()
    }
  }

  function enableFilechooser(va, evt) {
    if ($(evt.target).val().indexOf('=') > 0) {
      $(evt.target).next().removeAttr('disabled').removeClass('disabled');
    }
    else {
      $(evt.target).next().attr('disabled', 'disabled').addClass('disabled');
    }
  }

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


  function showAddActionDemiModal(widget) {
    viewModel.newAction(widget);
    $("#exposeOverlay").fadeIn(300);
    var _el = $("#wdg_" + widget.id());
    _el.css("zIndex", "1032");
    var lastSeenPosition = _el.position();
    var _width = _el.width();

    _el.css("position", "absolute");
    _el.css({
      "top": (lastSeenPosition.top) + "px",
      "left": lastSeenPosition.left + "px",
      "width": 450
    });
    $("#addActionDemiModal").width(_el.width()).css("top", _el.offset().top + 25).css("left", _el.offset().left).modal("show");
    $("html, body").animate({
      scrollTop: $("#addActionDemiModal").offset().top - 200
    }, 200);
  }

  function addActionDemiModalFieldPreview(field) {
    if (viewModel.newAction() != null) {
      var _el = $("#wdg_" + viewModel.newAction().id());
      _el.css("position", "static");
      _el.css("width", "");
      viewModel.workflow.addNode(viewModel.newAction());
      $("#addActionDemiModal").modal("hide");
      $("#wdg_" + viewModel.newAction().id()).css("zIndex", "0");
      $("#exposeOverlay").fadeOut(300);
      viewModel.newAction(null);
    }
  }

  function addActionDemiModalFieldCancel() {
    $("#exposeOverlay").fadeOut(300);
    $("#addActionDemiModal").modal("hide");
    if (viewModel.newAction()){
      viewModel.removeWidgetById(viewModel.newAction().id());
    }
    viewModel.newAction(null);
  }

  function linkWidgets(fromId, toId) {
    var _from = $("#wdg_" + (typeof fromId == "function" ? fromId() : fromId));
    var _to = $("#wdg_" + (typeof toId == "function" ? toId() : toId));
    if (_from.length > 0 && _to.length > 0){
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
        strokeStyle: viewModel.isEditing()?'#e5e5e5':'#dddddd'
      });
    }
  }

  function drawArrows(){
    $("canvas").remove();
    if (viewModel.oozieColumns()[0].rows().length > 3){
      var _links = viewModel.workflow.linkMapping();
      Object.keys(_links).forEach(function(id){
        if (_links[id].length > 0){
          _links[id].forEach(function(nextId){
            linkWidgets(id, nextId);
          });
        }
      });
    }
  }

  var _linkMappingTimeout = -1;
  $(document).on("drawArrows", function(){
    window.clearTimeout(_linkMappingTimeout);
    _linkMappingTimeout = window.setTimeout(renderChangeables, 25);
  });

  $(document).on("removeArrows", function(){
    $("canvas").remove();
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
    if (viewModel.hasArrows()){
      drawArrows();
    }
  }

  var lastSeenPosition = null;
  var lastExpandedWidget = null;
  function setLastExpandedWidget(widget) {
    lastExpandedWidget = widget;
    var _el = $("#wdg_" + widget.id());
    if (_el.width() < 400){
      _el.css("z-index", "1032");
      lastSeenPosition = _el.position();
      var _width = _el.width();

      _el.css("position", "absolute");
      _el.css({
        "top": (lastSeenPosition.top) + "px",
        "left": lastSeenPosition.left + "px",
        "width": _width
      });
      _el.width(500);
      $("#exposeOverlay").fadeIn(300);  
      widget.oozieExpanded(true);
    }
    else {
      widget.oozieExpanded(false);
    }
  }

  function toggleProperties(widget) {
    if (widget.oozieMovable()) {
      var _el = $("#wdg_" + widget.id());
      if (!widget.ooziePropertiesExpanded()) {
        setLastExpandedWidget(widget);
        _el.find(".prop-editor").show();
        widget.ooziePropertiesExpanded(true);
      }
      else {
        if (widget.oozieExpanded()){
          exposeOverlayClickHandler();
        }
        else {
          _el.find(".prop-editor").hide();
          widget.ooziePropertiesExpanded(false);
        }
      }
      $(document).trigger("drawArrows");
    }
  }

  function exposeOverlayClickHandler() {
    if (lastExpandedWidget) {
      var _el = $("#wdg_" + lastExpandedWidget.id());
      _el.find(".prop-editor").hide();
      _el.removeAttr("style");
      lastExpandedWidget.ooziePropertiesExpanded(false);
      lastExpandedWidget.oozieExpanded(false);
    }
    addActionDemiModalFieldCancel();
    $("#exposeOverlay").fadeOut(300);
    $(document).trigger("drawArrows");
  }

  $(document).ready(function(){
    renderChangeables();

    $("#exposeOverlay").on("click", exposeOverlayClickHandler);

    $(document).keyup(function(e) {
      if (e.keyCode == 27) {
        exposeOverlayClickHandler();
        addActionDemiModalFieldCancel();
        $("#addActionDemiModal").modal("hide");
      }
    });

    var resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        renderChangeables();
      }, 200);
    });

    $(document).on("click", ".widget-main-section", function(e){
      if (! $(e.target).is("a") && ! $(e.target).is("input") && ! $(e.target).is("i") && ! $(e.target).is("button")){
        setLastExpandedWidget(ko.dataFor($(e.target).parents(".card-widget")[0]));
      }
    });

  });

</script>

${ commonfooter(messages) | n,unicode }
