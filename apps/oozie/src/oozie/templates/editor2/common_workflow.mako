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


#
# Include this in order to use the functions:
# <%namespace name="workflow" file="common_workflow.mako" />
#

<%!
  from django.utils.translation import ugettext as _
  from desktop.views import _ko
%>

<%namespace name="utils" file="../utils.inc.mako" />


<%def name="render()">

<script type="text/html" id="doc-search-autocomp-item">
  <a>
    <div>
      <strong style="font-size: 14px;" data-bind="html: name"></strong>
      <div style="width: 190px; overflow: hidden; white-space: nowrap; text-overflow:ellipsis; font-size: 12px;" class="muted" data-bind="text: description"></div>
    </div>
  </a>
</script>

<div data-bind="css: {'dashboard': true, 'readonly': ! isEditing()}">
  % if layout_json != '':
  <div class="container-fluid">
    <div class="row-fluid" data-bind="template: { name: 'column-template', foreach: oozieColumns}">
    </div>
    <div class="clearfix"></div>
  </div>
  %endif
  % if layout_json == '':
   <div class="container-fluid" id="workflow_graph"/>
  %endif
</div>


<script type="text/html" id="column-template">
  <div data-bind="css: klass()" style="min-height: 50px !important;">
    <div data-bind="template: { name: 'row-template', data: oozieStartRow }" style="margin-top: 0"></div>
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

    <!-- ko if: $root.workflow.hasKillNode() -->
      <div data-bind="template: { name: 'row-template', data: oozieKillRow }" style="margin-top: 60px"></div>
    <!-- /ko -->
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
    <div class="row-fluid row-internal" data-bind="visible: $index() > 0 && $root.isEditing() && ! $root.isRowBeforeJoin($data) && ! $root.isRowAfterFork($data)" style="margin-bottom: 10px">
      <div data-bind="css: {'span1': true, 'offset3': ($root.isEditing() && $parents.length <= 2 && columns().length == 0), 'offset4': ($parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}"></div>
      <div data-bind="css: {'span10': ($parents.length > 2 || columns().length > 0), 'span4': ($parents.length <= 2 && columns().length == 0), 'offset3': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && ! enableOozieDropOnBefore(), css: {'drop-target drop-target-disabled': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}"></div>
        <div style="text-align: left" data-bind="visible: $root.isEditing() && enableOozieDropOnBefore(), css: {'drop-target': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addDraggedWidget($data); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div data-bind="css: {'span1': true, 'readonly': ! $root.isEditing()}"></div>
    </div>
    <div class="row-fluid" data-bind="style: {'width': columns().length < 5 ? '100%' : (columns().length * 25)+'%' }">
      <div data-bind="css: {'span1': true, 'offset3': ($root.isEditing() && $parents.length <= 2 && columns().length == 0), 'offset4': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}">
        <div data-bind="visible: $root.isEditing() && enableOozieDropOnSide() && !($data.widgets().length > 0 && ['join-widget', 'decision-widget'].indexOf($data.widgets()[0].widgetType()) > -1), css: {'drop-target drop-target-side': true, 'drop-target-dragging': $root.isDragging(), 'is-editing': $root.isEditing}, droppable: {enabled: $root.isEditing, onDrop: function(){ var _w = $root.addSideDraggedWidget($data, true); widgetDraggedAdditionalHandler(_w); } }"></div>
      </div>
      <div  data-bind="css: {'span10': ($parents.length > 2 || columns().length > 0), 'span4': ($parents.length <= 2 && columns().length == 0), 'offset3': (!$root.isEditing() && $parents.length <= 2 && columns().length == 0), 'readonly': ! $root.isEditing()}">
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
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass() + (ooziePropertiesExpanded()?' properties-expanded-widget':'') + (oozieExpanded()?' expanded-widget':'') + ($root.isRunning() && status() == ''?' widget-running':''),
      draggable: {data: $data, isEnabled: true, options: {'handle': '.move-widget', 'opacity': 0.7, 'refreshPositions': true, 'start': function(event, ui){ $root.setCurrentlyDraggedWidget($data, event.toElement || event.originalEvent.originalEvent.target); $root.isDragging(true); if ($.browser.mozilla || $.browser.msie) { ui.helper.css('margin-top', -$(window).scrollTop() ); } }, 'beforestop': function (event, ui) { if ($.browser.mozilla || $.browser.msie) { ui.helper.css('margin-top', 0 ); } }, 'stop': function(event, ui){ $root.enableSideDrop($data); $root.isDragging(false); }, 'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();  var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.currentTarget).find('h2 a.pointer').text());_title.appendTo(_par);_par.css('minHeight', '10px');_par.css('overflow', 'hidden');_par.width(180);return _par;}}}">
    <h2 class="card-heading simple" data-bind="visible: widgetType() != 'start-widget' && widgetType() != 'end-widget' &&
        id() != '17c9c895-5a16-7443-bb81-f34b30b21548' && (['fork-widget', 'join-widget', 'decision-widget'].indexOf(widgetType()) == -1 || $root.isEditing())">

      <span data-bind="visible: $root.isEditing() && oozieMovable() && ! oozieExpanded() && ! ooziePropertiesExpanded() && ($root.newAction() == null || $root.newAction().id() != id())">
        <a href="javascript:void(0)" class="move-widget" title="${ _('Move node') }"><i class="fa fa-arrows"></i></a>
        &nbsp;
        <a href="javascript:void(0)" class="move-widget clone-widget" title="${ _('Copy node') }"><i class="fa fa-copy"></i></a>
        &nbsp;
      </span>

      <!-- ko if: widgetType() == 'hive-widget' -->
      <img src="${ static('oozie/art/icon_beeswax_48.png') }" class="widget-icon" alt="${ _('Hive icon') }">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'hive2-widget' || widgetType() == 'hive-document-widget' -->
      <img src="${ static('oozie/art/icon_beeswax_48.png') }" class="widget-icon" alt="${ _('Hive icon') }"><sup style="color: #0B7FAD; margin-left: -4px">2</sup>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'impala-widget' || widgetType() == 'impala-document-widget' -->
      <img src="${ static('oozie/art/icon_impala_48.png') }" class="widget-icon" alt="${ _('Impala icon') }">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'altus-widget' -->
      <a class="widget-icon"><i class="fa fa-cloud"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'pig-widget' || widgetType() == 'pig-document-widget'  -->
      <img src="${ static('oozie/art/icon_pig_48.png') }" class="widget-icon" alt="${ _('Pig icon') }">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'java-widget' || widgetType() == 'java-document-widget' -->
      <a class="widget-icon"><i class="fa fa-file-code-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'sqoop-widget' || widgetType() == 'sqoop-document-widget' -->
      <img src="${ static('oozie/art/icon_sqoop_48.png') }" class="widget-icon" alt="${ _('Sqoop icon') }">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'mapreduce-widget' || widgetType() == 'mapreduce-document-widget' -->
      <a class="widget-icon"><i class="fa fa-file-archive-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'subworkflow-widget' -->
      <a class="widget-icon"><i class="fa fa-code-fork"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'shell-widget' || widgetType() == 'shell-document-widget' -->
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

      <!-- ko if: widgetType() == 'distcp-widget' || widgetType() == 'distcp-document-widget' -->
      <a class="widget-icon"><i class="fa fa-files-o"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'spark-widget' || widgetType() == 'spark-document-widget' -->
      <img src="${ static('oozie/art/icon_spark_48.png') }" class="widget-icon" alt="${ _('Spark icon') }">
      <!-- /ko -->

      <!-- ko if: widgetType() == 'generic-widget' -->
      <a class="widget-icon"><i class="fa fa-code"></i></a>
      <!-- /ko -->

      <!-- ko if: widgetType() == 'kill-widget' -->
      <a class="widget-icon"><i class="fa fa-stop"></i></a>
      <!-- /ko -->

      <span data-bind="visible: typeof $root.isViewer == 'undefined' || ! $root.isViewer(), editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}, attr: {'title': id().slice(0, 4)}"></span>
      <!-- ko if: typeof $root.isEmbeddable !== 'undefined' -->
        <a class="pointer" data-bind="visible: typeof $root.isEmbeddable != 'undefined' && $root.isEmbeddable(), click: function(){ huePubSub.publish('oozie.action.click', $data); }, text: name" title="${ _('View workflow action') }"></a>
      <!-- /ko -->
      <!-- ko if: typeof $root.isEmbeddable === 'undefined' -->
        <a class="pointer" data-bind="visible: typeof $root.isViewer != 'undefined' && $root.isViewer(), click: function(){ location.href = actionURL(); }, text: name" title="${ _('View workflow action') }"></a>
      <!-- /ko -->

      <div class="inline pull-right" data-bind="visible: (typeof $root.isViewer == 'undefined' || ! $root.isViewer()) && !$root.isEditing()" style="margin-right: 4px">
        <a href="javascript:void(0)" data-bind="click: function(w) { viewModel.showSubmitActionPopup(w); }"><i class="fa fa-play-circle-o"></i></a>
      </div>

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
      <!-- ko if: id() == '17c9c895-5a16-7443-bb81-f34b30b21548' && ooziePropertiesExpanded() -->
      <div class="advanced-triangle-container" data-bind="visible: $root.isEditing(), click: toggleProperties">
        <div class="advanced-triangle">
          <a href="javascript:void(0)"><i class="fa fa-caret-square-o-left"></i></a>
        </div>
      </div>
      <!-- /ko -->
      <div data-bind="template: { name: function() { return widgetType(); }}" class="widget-main-section"></div>
      <div data-bind="css: {'widget-statusbar': true, 'widget-statusbar-running': status() == 'running', 'widget-statusbar-failed': status() == 'failed', 'widget-statusbar-success': status() == 'success'}, style: {'width': progress() + '%'}"></div>
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
      <a class="custom-popover pull-right" href="javascript:void(0)" data-trigger="click" data-toggle="popover" data-placement="right" rel="popover"
        data-html="true" data-content="<strong>${ _('Examples of predicates:') }</strong><br/>
                <br/>${'${'} fs:fileSize(secondjobOutputDir) gt 10 * GB }
                <br/>
                ${"${"} hadoop:counters('secondjob')[RECORDS][REDUCE_OUT] lt 1000000 }
                <br/>
                <a href='http://oozie.apache.org/docs/4.1.0/WorkflowFunctionalSpec.html#a4.2_Expression_Language_Functions' target='_blank'>${ _('Click for more') }</a>">
          <i class="fa fa-question-circle" title="${ _('Click for more info') }"></i>
      </a>
      <ul data-bind="foreach: children" class="unstyled">
        <li>
          ${ _('If') } <input type="text" class="input-medium" data-bind="value: $data['condition']" />
          ${ _('go to') }
          <select data-bind="options: $root.workflow.nodeIds,
                     optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
                     value: $data['to'],
                     event: { change: function(){ $(document).trigger('drawArrows') } }
                     ">
          </select>
          <a class="pointer" data-bind="click: function(){ $parent.children.remove(this); $(document).trigger('drawArrows')}">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <a class="pointer" data-bind="click: function(){ children.push({'to': '', 'condition': '${'${'} 1 gt 0 }'}); $(document).trigger('drawArrows')}">
        ${ _('Jump to another node') } <i class="fa fa-plus"></i>
      </a>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="kill-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="min-height: 40px">
    <div class="big-icon" data-bind="visible: id() == '17c9c895-5a16-7443-bb81-f34b30b21548', attr: {'id': 'wdg_Kill'}" title="${ _('It is where we finish if failure!') }"><i class="fa fa-stop"></i></div>

    <div data-bind="visible: $root.isEditing" style="margin: 10px">
      <div data-bind="visible: $parent.ooziePropertiesExpanded">
        <h6 class="field-title">${ _('Message') }</h6>
        <textarea class="span12" data-bind="value: properties.message" />

        <h6 class="field-title">${ _('Email on error') } <input type="checkbox" data-bind="checked: properties.enableMail" style="margin-top: -3px;margin-left: 4px;" /></h6>

        <span data-bind="visible: properties.enableMail">
          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.to.label"></span>
            <input type="text" class="seventy" data-bind="value: properties.to, attr: { placeholder: $root.workflow_properties.to.help_text }"/>
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.cc.label"></span>
            <input type="text" class="seventy" data-bind="value: properties.cc, attr: { placeholder: $root.workflow_properties.cc.help_text }" />
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.subject.label"></span>
            <input type="text" class="seventy" data-bind="value: properties.subject, attr: { placeholder: $root.workflow_properties.subject.help_text }" />
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.body.label"></span>
            <textarea class="seventy" style="resize:both" data-bind="value: properties.body, attr: { placeholder: $root.workflow_properties.body.help_text }"></textarea>
          </div>
        </span>
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
        <input type="text" class="filechooser-input input-xlarge seventy"
            data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.prepares.help_text }"  validate="nonempty"/>
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

    <!-- ko if: properties.job_xml != null -->
      <h6>${ _('Job XML') }</h6>
      <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: properties.job_xml, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.job_xml, attr: { placeholder: $root.workflow_properties.job_xml.help_text }"/>
    <!-- /ko -->

    <h6>
      <a class="pointer" data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); $(document).trigger('drawArrows') }">
        ${ _('Properties') } <i class="fa fa-plus"></i>
      </a>
    </h6>
    <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
      <li>
        <input type="text" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }"/>
        <input type="text" class="filechooser-input input-xlarge thirty" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }" validate="nonempty"/>
        <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>
    <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

    <!-- ko if: properties.archives -->
    <h6>
      <a class="pointer" data-bind="click: function(){ properties.archives.push(ko.mapping.fromJS({'name': ''})); $(document).trigger('drawArrows') }">
        ${ _('Archives') } <i class="fa fa-plus"></i>
      </a>
    </h6>
    <ul data-bind="visible: properties.archives().length > 0, foreach: properties.archives" class="unstyled">
      <li>
        <input type="text" class="filechooser-input input-xlarge seventy" data-bind="filechooser: name(), filechooserFilter: 'zip,tar,tgz,tar.gz,jar', filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: name, value: name, attr: { placeholder: $root.workflow_properties.archives.help_text }" validate="nonempty"/>
        <span data-bind='template: { name: "common-fs-link", data: { path: name(), with_label: false} }'></span>
        <a href="#" data-bind="click: function(){ $parent.properties.archives.remove(this); $(document).trigger('drawArrows') }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>
    <em data-bind="visible: properties.archives().length == 0">${ _('No archives defined.') }</em>
    <!-- /ko -->

    <span data-bind="template: { name: 'common-properties-retry' }"></span>
  </div>
</script>


<script type="text/html" id="common-properties-retry">
  <h6>${ _('Retry ') }</h6>
  <a class="pointer" data-bind="click: function(){ properties.retry_max.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }, visible: properties.retry_max().length < 1">
    ${ _('Max') } <i class="fa fa-plus"></i>
  </a>
  <a class="pointer" data-bind="click: function(){ properties.retry_interval.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }, visible: properties.retry_interval().length < 1">
    ${ _('Interval') } <i class="fa fa-plus"></i>
  </a>

  <ul data-bind="visible: properties.retry_max().length > 0, foreach: properties.retry_max" class="unstyled">
    <li>
      ${ _('Max') } <input type="number" data-bind="value: value, attr: { placeholder: $root.workflow_properties.retry_max.help_text }"/>
      <a href="#" data-bind="click: function(){ $parent.properties.retry_max.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
  <ul data-bind="visible: properties.retry_interval().length > 0, foreach: properties.retry_interval" class="unstyled">
    <li>
      ${ _('Interval') } <input type="number" class="small" data-bind="value: value, attr: { placeholder: $root.workflow_properties.retry_interval.help_text }"/>
      <a href="#" data-bind="click: function(){ $parent.properties.retry_interval.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
</script>


<script type="text/html" id="common-properties-pig-arguments">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.arguments.push({'value': ''}); $(document).trigger('drawArrows') }">
      ${ _('Arguments') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="visible: properties.arguments().length > 0, foreach: properties.arguments">
    <li>
      <input type="text" class="input-medium" data-bind="value: value, attr: { placeholder: $root.workflow_properties.arguments.help_text }" validate="nonempty"/>
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
  <ul class="unstyled white sortable-arguments" data-bind="visible: properties.arguments().length > 0,  sortable: { allowDrop: false, data: properties.arguments, options: { axis: 'y', containment: 'parent' }}">
    <li style="margin-bottom: 3px">
      <span class="muted move-widget">
        <i class="fa fa-arrows"></i>
      </span>
      <textarea rows="1" style="resize: vertical" class="span11" data-bind="value: value, attr: { placeholder: $root.workflow_properties.arguments.help_text }, parseArguments: { list: $parent.properties.arguments, objectKey: 'value', callback: function(){ $(document).trigger('drawArrows'); } }" validate="nonempty"></textarea>
      <a href="#" data-bind="click: function(){ $parent.properties.arguments.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
</script>


<script type="text/html" id="common-properties-files">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.files.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }">
      ${ _('Files') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="foreach: properties.files">
    <li style="margin-bottom: 3px">
      <input type="text" class="filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value" validate="nonempty"/>
      <span data-bind='template: { name: "common-fs-link", data: { path: value(), with_label: false} }'></span>
      <a href="#" data-bind="click: function(){ $parent.properties.files.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
</script>


<script type="text/html" id="common-properties-parameters">
  <h6>
    <a class="pointer" data-bind="click: function(){ properties.parameters.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows')}">
      ${ _('Parameters') } <i class="fa fa-plus"></i>
    </a>
  </h6>
  <ul class="unstyled" data-bind="foreach: properties.parameters">
    <li style="margin-bottom: 3px">
      <input type="text" class="filechooser-input seventy" data-bind="value: value, filechooser: value, filechooserOptions: globalFilechooserOptions, filechooserPrefixSeparator: '=', hdfsAutocomplete: value, attr: { placeholder: ' ${ _ko("Fill me up!") }' + ' e.g. limit=${'${'}n}' }, typeahead: { target: value, source: $parent.actionParametersUI, sourceSuffix: '=', triggerOnFocus: true }, parseArguments: { list: $parent.properties.parameters, objectKey: 'value', callback: function(){ $(document).trigger('drawArrows'); } }"  validate="nonempty"/>
      <span data-bind='template: { name: "param-fs-link", data: {path: value()} }'></span>
      <a href="#" data-bind="click: function(){ $parent.properties.parameters.remove(this); $(document).trigger('drawArrows') }">
        <i class="fa fa-minus"></i>
      </a>
    </li>
  </ul>
</script>


<script type="text/html" id="common-action-transition">
  <!-- ko if: children().length == 2 -->
  <div>
  OK <i class="fa fa-long-arrow-right"></i>
  <select data-bind="options: $root.workflow.nodeIds,
      optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
      value: children()[0]['to']
      ">
  </select>
  </div>
  <div class="margin-top-10">
  KO <i class="fa fa-long-arrow-right"></i>
  <select data-bind="options: $root.workflow.nodeIds,
     optionsText: function(item) {return $root.workflow.nodeNamesMapping()[item]; },
   value: children()[1]['error']
     ">
  </select>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="common-action-credentials">
  <!-- ko if: $parent.widgetType() != 'impala-widget' && $parent.widgetType() != 'impala-document-widget' -->
    <em data-bind="visible: $root.credentials() == null || $root.credentials().length == 0">${ _('No available credentials.') }</em>
    <ul data-bind="visible: $root.credentials() != null && $root.credentials().length > 0, foreach: $root.credentials" class="unstyled">
      <li>
        <label class="checkbox"><input type="checkbox" data-bind="checkedValue: $data, checked: $parent.properties.credentials" /> <span data-bind="text: $data"></span></label>
      </li>
    </ul>

    <em data-bind="visible: properties.credentials && properties.credentials.indexOf('hbase') != -1">
      ${ _('Requires hbase-site.xml in job path') }
    </em>
  <!-- /ko -->

  <!-- ko if: $parent.widgetType() == 'impala-widget' || $parent.widgetType() == 'impala-document-widget' -->
    <input type="text" class="filechooser-input seventy" data-bind="filechooser: properties.key_tab_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.key_tab_path, attr: { placeholder:  $root.workflow_properties.key_tab_path.help_text }"/>
    <input type="text" data-bind="value: properties.user_principal, attr: { placeholder: $root.workflow_properties.user_principal.help_text }" />
  <!-- /ko -->
</script>


<script type="text/html" id="common-action-sla">
  <div data-bind="with: properties">
     ${ utils.slaForm() }
  </div>
</script>


<script type="text/html" id="common-fs-link">
 <!-- ko if: $data.path.length > 0 -->
   <!-- ko if: with_label -->
     <a data-bind="hueLink: '/filebrowser/view=' + ($data.path[0] != '/' && $data.path.indexOf('s3a://') !== 0 ? $root.workflow.properties.deployment_dir() + '/' : '') + $data.path, attr: { title: '${ _ko('Open') } '+ $data.path }">
      <span data-bind="text: $data.path.lastIndexOf('/') == $data.path.length - 1 ? $data.path : $data.path.split('/').pop()"></span>
     </a>
   <!-- /ko -->

   <!-- ko if: ! with_label -->
     <a data-bind="storageContextPopover: { path: ($data.path[0] != '/' && $data.path.indexOf('s3a://') !== 0 ? $root.workflow.properties.deployment_dir() + '/' : '') + $data.path, offset: { right: 5 }, orientation: 'left' }" title="${ _('Preview') }" href="javascript: void(0);">
       <i class="fa fa-external-link-square"></i>
     </a>
   <!-- /ko -->
 <!-- /ko -->
</script>

<script type="text/html" id="common-document-widget">
  <div data-bind="visible: !$root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <!-- ko if: associatedDocumentLoading -->
        <i class="fa fa-spinner fa-spin muted"></i>
      <!-- /ko -->
      <!-- ko with: associatedDocument -->
        <a data-bind="documentContextPopover: { uuid: absoluteUrl.split('=')[1], orientation: 'right', offset: { top: 5 } }" href="javascript: void(0);" title="${ _('Preview document') }">
          <span data-bind="text: name"></span> <i class="fa fa-info"></i>
        </a>
        <br/>
        <span data-bind='text: description' class="muted"></span>
      <!-- /ko -->
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: !$parent.ooziePropertiesExpanded()" class="nowrap">
        <div class="selectize-wrapper" style="width: 300px;">
          <select placeholder="${ _('Search your documents...') }" data-bind="documentChooser: { loading: associatedDocumentLoading, value: associatedDocumentUuid, document: associatedDocument, type: type }"></select>
        </div>
        <!-- ko if: associatedDocument -->
          <a data-bind="documentContextPopover: { uuid: associatedDocument().absoluteUrl.split('=')[1], orientation: 'right', offset: { top: 5 } }" href="javascript: void(0);" title="${ _('Preview document') }">
            <i class="fa fa-external-link-square"></i>
          </a>
          <div class="clearfix"></div>
          <div data-bind='text: associatedDocument().description' style="padding-left: 3px;" class="muted"></div>
        <!-- /ko -->
        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-parameters' }"></div>
          <div class="span6" data-bind="template: { name: 'common-properties-files' }"></div>
        </div>
      </div>
    </div>

</script>

<script type="text/html" id="param-fs-link">
  <!-- ko if: path.split('=', 2)[1] && path.split('=', 2)[1].charAt(0) == '/' -->
    <a data-bind="storageContextPopover: { path: $data.path.split('=', 2)[1], offset: { right: 5 }, orientation: 'left' }" title="${ _('Preview') }" href="javascript: void(0);">
      <i class="fa fa-external-link-square"></i>
    </a>
  <!-- /ko -->
</script>


<script type="text/html" id="logs-icon">
  <!-- ko if: $parent.widgetType() != 'subworkflow-widget' && $parent.logsURL() != '' && $parent.logsURL() != null -->
    <!-- ko if: typeof $root.isEmbeddable !== 'undefined' -->
    <a class="pull-right pointer logs-icon" data-bind="click: function(){ huePubSub.publish('oozie.action.logs.click', $parent); }" title="${ _('View logs') }"><i class="fa fa-tasks"></i></a>
    <!-- /ko -->
    <!-- ko if: typeof $root.isEmbeddable === 'undefined' -->
    <a class="pull-right pointer logs-icon" data-bind="hueLink: $parent.logsURL" title="${ _('View logs') }"><i class="fa fa-tasks"></i></a>
    <!-- /ko -->
  <!-- /ko -->
  <!-- ko if: $parent.widgetType() == 'subworkflow-widget' && $parent.externalIdUrl()-->
   <!-- ko if: typeof $root.isEmbeddable !== 'undefined' -->
     <a class="pull-right pointer logs-icon" data-bind="click: function(){ huePubSub.publish('browser.job.open.link', $parent.externalJobId); }" title="${ _('View the workflow') }"><img src="${static('oozie/art/icon_oozie_workflow_48.png')}" class="app-icon" alt="${ _('Oozie workflow icon') }"/></a>
   <!-- /ko -->
   <!-- ko if: typeof $root.isEmbeddable === 'undefined' -->
     <a class="pull-right pointer logs-icon" data-bind="hueLink: $parent.externalIdUrl" title="${ _('View the workflow') }"><img src="${static('oozie/art/icon_oozie_workflow_48.png')}" class="app-icon" alt="${ _('Oozie workflow icon') }"/></a>
   <!-- /ko -->
  <!-- /ko -->
</script>


<script type="text/html" id="hive-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <div class="airy">
          <input type="text" class="filechooser-input seventy" data-bind="filechooser: properties.script_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.script_path, attr: { placeholder:  $root.workflow_properties.script_path.help_text }" validate="nonempty"/>
          <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: false}}'></span>
        </div>
        <div class="airy">
          <span data-bind="text: $root.workflow_properties.hive_xml.label"></span>
          <input type="text" class="input-large filechooser-input seventy" data-bind="filechooser: properties.hive_xml, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.hive_xml, attr: { placeholder: $root.workflow_properties.hive_xml.help_text }"/>
        </div>
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
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <input type="text" class="filechooser-input seventy" data-bind="filechooser: properties.script_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.script_path, attr: { placeholder:  $root.workflow_properties.script_path.help_text }" validate="nonempty"/>
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
          <!-- ko if: typeof properties.jdbc_url != 'undefined' -->
          <span data-bind="text: $root.workflow_properties.jdbc_url.label"></span>
          <input type="text" data-bind="value: properties.jdbc_url, attr: { placeholder: $root.workflow_properties.jdbc_url.help_text }" />
          <br/>
          <!-- /ko -->
          <!-- ko if: typeof properties.password != 'undefined' -->
          <span data-bind="text: $root.workflow_properties.password.label"></span>
          <input type="text" data-bind="value: properties.password, attr: { placeholder: $root.workflow_properties.password.help_text }" />
          <br/>
          <!-- /ko -->
          <!-- ko if: typeof properties.impalad_host != 'undefined' -->
          <span data-bind="text: $root.workflow_properties.impalad_host.label"></span>
          <input type="text" data-bind="value: properties.impalad_host, attr: { placeholder: $root.workflow_properties.impalad_host.help_text }" />
          <br/>
          <!-- /ko -->
          <a class="pointer" data-bind="click: function(){ properties.arguments.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }">
            ${ _('Arguments') } <i class="fa fa-plus"></i>
          </a>
          <div class="row-fluid">
            <ul class="unstyled white sortable-arguments" data-bind="visible: properties.arguments().length > 0, sortable: { allowDrop: false, data: properties.arguments, options: { axis: 'y', containment: 'parent' }}">
              <li>
                <span class="muted move-widget">
                  <i class="fa fa-arrows"></i>
                </span>
                <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, attr: { placeholder: $root.workflow_properties.arguments.help_text }, parseArguments: { list: $parent.properties.arguments, objectKey: 'value', callback: function(){ $(document).trigger('drawArrows'); } }" validate="nonempty"/>
                <span data-bind='template: { name: "common-fs-link", data: {path: value, with_label: false}}'></span>
                <a href="#" data-bind="click: function(){ $parent.properties.arguments.remove(this); $(document).trigger('drawArrows') }">
                  <i class="fa fa-minus"></i>
                </a>
              </li>
            </ul>
            <em data-bind="visible: properties.arguments().length == 0">${ _('No arguments defined.') }</em>
          </div>
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


<script type="text/html" id="impala-widget">
  <span data-bind="template: { name: 'hive2-widget' }"></span>
</script>


<script type="text/html" id="altus-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: !$root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="text: properties.service"></span>
      <span data-bind="text: properties.command"></span>
      <span data-bind="text: properties.parameters"></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.service.label"></span>
          <input type="text" data-bind="value: properties.service, valueUpdate:'afterkeydown', attr: { placeholder:  $root.workflow_properties.service.help_text }" validate="nonempty"/>
        </div>
        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.command.label"></span>
          <input type="text" data-bind="value: properties.command, valueUpdate:'afterkeydown', attr: { placeholder:  $root.workflow_properties.command.help_text }" validate="nonempty"/>
        </div>
        <div class="row-fluid">
          <div class="span12" data-bind="template: { name: 'common-properties-parameters' }"></div>
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
          <div class="row-fluid">
            <span data-bind="text: $root.workflow_properties.capture_output.label"></span>
            <input type="checkbox" data-bind="checked: properties.capture_output" />

            <div class="span12" data-bind="template: { name: 'common-properties-parameters' }"></div>
          </div>
        </div>

        <div class="tab-pane" data-bind="attr: { id: 'sla-' + id() }">
          <span data-bind="template: { name: 'common-action-sla' }"></span>
        </div>

        ##<div class="tab-pane" data-bind="attr: { id: 'credentials-' + id() }">
        ##  <span data-bind="template: { name: 'common-action-credentials' }"></span>
        ##</div>

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
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.script_path(), with_label: true} }'></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <input type="text" class="filechooser-input seventy" data-bind="filechooser: properties.script_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.script_path, attr: { placeholder:  $root.workflow_properties.script_path.help_text }" validate="nonempty"/>
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


<script type="text/html" id="pig-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

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


<script type="text/html" id="spark-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="text: properties.app_name"></span>
      &nbsp;&nbsp;&nbsp;
      <span data-bind="text: properties.class"></span>
      <br/>
      <span data-bind="text: properties.jars"></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.jars.label"></span>
          <input type="text" data-bind="value: properties.jars, valueUpdate:'afterkeydown', attr: { placeholder:  $root.workflow_properties.jars.help_text }" validate="nonempty"/>
        </div>

        <div class="airy" data-bind="visible: $.grep( properties.jars().split(','), function(val, index) { return val.toLowerCase().endsWith('.jar'); }).length > 0">
          <span class="widget-label" data-bind="text: $root.workflow_properties.class.label"></span>
          <input type="text" class="input-xlarge seventy" data-bind="value: properties.class, attr: { placeholder: $root.workflow_properties.class.help_text }" />
        </div>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.spark_arguments.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }">
            ${ _('Arguments') } <i class="fa fa-plus"></i>
          </a>
        </h6>

        <div class="row-fluid">
          <div>
            <ul class="unstyled white sortable-arguments" data-bind="visible: properties.spark_arguments().length > 0, sortable: { allowDrop: false, data: properties.spark_arguments, options: { axis: 'y', containment: 'parent' }}">
              <li>
                <span class="muted move-widget">
                  <i class="fa fa-arrows"></i>
                </span>
                <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, attr: { placeholder:  $root.workflow_properties.spark_arguments.help_text }, parseArguments: { list: $parent.properties.spark_arguments, objectKey: 'value', callback: function(){ $(document).trigger('drawArrows'); } }" validate="nonempty"/>
                <span data-bind='template: { name: "common-fs-link", data: {path: value, with_label: false}}'></span>
                <a href="#" data-bind="click: function(){ $parent.properties.spark_arguments.remove(this); $(document).trigger('drawArrows') }">
                  <i class="fa fa-minus"></i>
                </a>
              </li>
            </ul>
            <em data-bind="visible: properties.spark_arguments().length == 0">${ _('No arguments defined.') }</em>
          </div>

          <div data-bind="template: { name: 'common-properties-files' }"></div>

          <span class="widget-label"  data-bind="text: $root.workflow_properties.spark_opts.label"></span>
          <input type="text" class="input-xlarge seventy" data-bind="value: properties.spark_opts, attr: { placeholder: $root.workflow_properties.spark_opts.help_text }" />

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
          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.spark_master.label"></span>
            <input type="text" class="input-medium" data-bind="value: properties.spark_master, attr: { placeholder: $root.workflow_properties.spark_master.help_text }" />
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.mode.label"></span>
            <input type="text" class="input-medium" data-bind="value: properties.mode, attr: { placeholder: $root.workflow_properties.mode.help_text }" />
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.app_name.label"></span>
            <input type="text" class="input-xlarge seventy" data-bind="value: properties.app_name, attr: { placeholder: $root.workflow_properties.app_name.help_text }" />
          </div>

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


<script type="text/html" id="spark-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.spark_master.label"></span>
            <input type="text" class="input-medium" data-bind="value: properties.spark_master, attr: { placeholder: $root.workflow_properties.spark_master.help_text }" />
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.mode.label"></span>
            <input type="text" class="input-medium" data-bind="value: properties.mode, attr: { placeholder: $root.workflow_properties.mode.help_text }" />
          </div>

          <div class="airy">
            <span class="widget-label" data-bind="text: $root.workflow_properties.app_name.label"></span>
            <input type="text" class="input-xlarge seventy" data-bind="value: properties.app_name, attr: { placeholder: $root.workflow_properties.app_name.help_text }" />
          </div>

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


<script type="text/html" id="generic-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.xml.label"></span>
          <textarea class="input-xlarge seventy" style="resize:both" data-bind="value: properties.xml, attr: { placeholder: $root.workflow_properties.xml.help_text }"></textarea>
        </div>

      </div>
    </div>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'sla-' + id() }">
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

<script type="text/html" id="hive-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

    <div data-bind="visible: $parent.ooziePropertiesExpanded">
      <ul class="nav nav-tabs">
        <li class="active"><a data-bind="attr: { href: '#properties-' + id()}" data-toggle="tab">${ _('Properties') }</a></li>
        <li><a data-bind="attr: { href: '#sla-' + id()}" href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a data-bind="attr: { href: '#credentials-' + id()}" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a data-bind="attr: { href: '#transitions-' + id()}" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" data-bind="attr: { id: 'properties-' + id() }">
          <!-- ko if: typeof properties.jdbc_url != 'undefined' -->
          <span data-bind="text: $root.workflow_properties.jdbc_url.label"></span>
          <input type="text" data-bind="value: properties.jdbc_url, attr: { placeholder: $root.workflow_properties.jdbc_url.help_text }" />
          <br/>
          <!-- /ko -->
          <!-- ko if: typeof properties.password != 'undefined' -->
          <span data-bind="text: $root.workflow_properties.password.label"></span>
          <input type="text" data-bind="value: properties.password, attr: { placeholder: $root.workflow_properties.password.help_text }" />
          <br/>
          <!-- /ko -->
          <!-- ko if: typeof properties.impalad_host != 'undefined' -->
          <span data-bind="text: $root.workflow_properties.impalad_host.label"></span>
          <input type="text" data-bind="value: properties.impalad_host, attr: { placeholder: $root.workflow_properties.impalad_host.help_text }" />
          <br/>
          <!-- /ko -->
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
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="impala-document-widget">
  <span data-bind="template: { name: 'hive-document-widget' }"></span>
</script>


<script type="text/html" id="java-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

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
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="java-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="text: properties.main_class" />
    </div>

    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <div class="airy">
          <span class="widget-label"  data-bind="text: $root.workflow_properties.jar_path.label"></span>
          <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: properties.jar_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.jar_path, attr: { placeholder: $root.workflow_properties.jar_path.help_text }" validate="nonempty"/>
          <span data-bind='template: { name: "common-fs-link", data: {path: properties.jar_path(), with_label: false}}'></span>
        </div>

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.main_class.label"></span>
          <input type="text" class="input-xlarge" data-bind="value: properties.main_class, attr: { placeholder: $root.workflow_properties.main_class.help_text }" validate="nonempty"/>
        </div>

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
        <span data-bind="text: $root.workflow_properties.command.label"></span><br/>
        <textarea data-bind="value: properties.command" class="input-xlarge seventy" style="resize:both" validate="nonempty"></textarea>

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-arguments' }"></div>
          <div class="span6" data-bind="template: { name: 'common-properties-files' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <div class="command-ellipsis">
        <span data-bind="text: properties.command(), attr: { title: properties.command() }" />
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


<script type="text/html" id="sqoop-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

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
        <input type="text" class="filechooser-input seventy" data-bind="filechooser: properties.jar_path, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.jar_path, value: properties.jar_path" validate="nonempty"/>
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.jar_path(), with_label: false} }'></span>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.job_properties.push({'name': '', 'value': ''}); $(document).trigger('drawArrows') }">
            ${ _('Properties') } <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
          <li>
            <input type="text" class="span4" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }" validate="nonempty"/>
            <input type="text" class="filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }" validate="nonempty"/>
            <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <div class="span12" data-bind="template: { name: 'common-properties-files' }"></div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
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
          <div class="properties">
            <h6>${ _('Prepare') }</h6>
            <ul data-bind="visible: properties.prepares().length > 0, foreach: properties.prepares" class="unstyled">
              <li>
                <div style="display: inline-block; width: 60px" data-bind="text: type"></div>
                <input type="text" class="filechooser-input input-xlarge"
                    data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.prepares.help_text }" validate="nonempty"/>
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

            <!-- ko if: properties.job_xml -->
              <h6>${ _('Job XML') }</h6>
              <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: properties.job_xml, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.job_xml, attr: { placeholder: $root.workflow_properties.job_xml.help_text }" validate="nonempty"/>
            <!-- /ko -->

            <h6>
              <a class="pointer" data-bind="click: function(){ properties.archives.push(ko.mapping.fromJS({'name': ''})); $(document).trigger('drawArrows') }">
                ${ _('Archives') } <i class="fa fa-plus"></i>
              </a>
            </h6>
            <ul data-bind="visible: properties.archives().length > 0, foreach: properties.archives" class="unstyled">
              <li>
                <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: name(), filechooserFilter: 'zip,tar,tgz,tar.gz,jar', filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: name, value: name, attr: { placeholder: $root.workflow_properties.archives.help_text }" validate="nonempty"/>
                <span data-bind='template: { name: "common-fs-link", data: { path: name(), with_label: false} }'></span>
                <a href="#" data-bind="click: function(){ $parent.properties.archives.remove(this); $(document).trigger('drawArrows') }">
                  <i class="fa fa-minus"></i>
                </a>
              </li>
            </ul>
            <em data-bind="visible: properties.archives().length == 0">${ _('No archives defined.') }</em>

            <span data-bind="template: { name: 'common-properties-retry' }"></span>
          </div>
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


<script type="text/html" id="mapreduce-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

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
        <select data-bind="valueAllowUnset: true, options: $root.subworkflows, optionsText: 'name', optionsValue: 'value', value: properties.workflow"></select>
        <span data-bind="visible: properties.workflow().length > 0">
          <a class="pointer" data-bind="hueLink: '${ url('oozie:edit_workflow') }' + '?workflow=' + properties.workflow()" title="${ _('Open') }">
            <i class="fa fa-external-link-square"></i>
          </a>
        </span>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.job_properties.push(ko.mapping.fromJS({'name': '', 'value': ''})); $(document).trigger('drawArrows') }">
            ${ _('Properties') } <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="visible: properties.job_properties().length > 0, foreach: properties.job_properties" class="unstyled">
          <li>
            <input type="text" class="span4" data-bind="value: name" placeholder="${ _('Name, e.g. input') }" validate="nonempty"/>

            <input type="text" class="filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, attr: { placeholder:  $root.workflow_properties.job_properties.help_text }" validate="nonempty" />
            <span data-bind='template: { name: "common-fs-link", data: {path: value, with_label: false}}'></span>

            <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
              <i class="fa fa-minus"></i>
             </a>
           </li>
         </ul>
        <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <!-- ko if: $root.getSubWorkflow(properties.workflow()) -->
        <span data-bind="with: $root.getSubWorkflow(properties.workflow())">
          <a class="pointer" data-bind="hueLink: '${ url('oozie:edit_workflow') }' + '?workflow=' + $data.value()" title="${ _('Open') }">
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

          <span data-bind="template: { name: 'common-properties-retry' }"></span>
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
        <input type="text" data-bind="value: properties.shell_command" validate="nospace"/>
        <span data-bind='template: { name: "common-fs-link", data: {path: properties.shell_command(), with_label: false} }'></span>

        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-arguments' }"></div>
          <div class="span6" data-bind="template: { name: 'common-properties-files' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="template: { name: 'common-fs-link', data: {path: properties.shell_command(), with_label: true} }"></span>
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


<script type="text/html" id="shell-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

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


<script type="text/html" id="ssh-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">
    <div data-bind="visible: $root.isEditing">

      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <div class="airy">
          <span class="widget-label widget-label-large" data-bind="text: $root.workflow_properties.host.label"></span>
          <input type="text" class="input-expandable" data-bind="value: properties.host" validate="nonempty"/>
        </div>
        <div class="airy">
          <span class="widget-label widget-label-large" data-bind="text: $root.workflow_properties.ssh_command.label"></span>
          <input type="text" class="input-expandable" data-bind="value: properties.ssh_command" validate="nonempty"/>
        </div>
        <div class="row-fluid">
          <div class="span6" data-bind="template: { name: 'common-properties-arguments' }"></div>
        </div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="text: properties.host" />
      <div class="command-ellipsis">
        <span data-bind="text: properties.ssh_command(), attr: { title: properties.ssh_command() }" />
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
          <span data-bind="text: $root.workflow_properties.capture_output.label"></span>
          <input type="checkbox" data-bind="checked: properties.capture_output" />

          <span data-bind="template: { name: 'common-properties-retry' }"></span>
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
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="text: '${ _ko("Delete") }', visible: properties.deletes().length > 0"></span>
      <ul data-bind="foreach: properties.deletes" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
        </li>
      </ul>

      <span data-bind="text: '${ _ko("Create") }', visible: properties.mkdirs().length > 0 || properties.touchzs().length > 0"></span>
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

      <span data-bind="text: '${ _ko("Move") }', visible: properties.moves().length > 0"></span>
      <ul data-bind="foreach: properties.moves" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: source(), with_label: true} }, visible: source().length > 0'></span>
          ${ _('to') }
          <span data-bind='template: { name: "common-fs-link", data: {path: destination(), with_label: true} }, visible: destination().length > 0'></span>
        </li>
      </ul>

      <span data-bind="text: '${ _ko("Change permissions") }', visible: properties.chmods().length > 0"></span>
      <ul data-bind="foreach: properties.chmods" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
          ${ _('to') }
          <span data-bind="text: permissions"/>
          <span data-bind="visible: ! dir_files(), text: '${ _ko('for directories') }'"/>
          <span data-bind="visible: dir_files(), text: '${ _ko('for directories and files') }'"/>
          <span data-bind="visible: recursive, text: '${ _ko('recursively') }'"/>
        </li>
      </ul>

      <span data-bind="text: '${ _ko("Change groups") }', visible: properties.chgrps().length > 0"></span>
      <ul data-bind="foreach: properties.chgrps" class="unstyled">
        <li>
          <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: true} }, visible: value().length > 0'></span>
          ${ _('to') }
          <span data-bind="text: group"/>
          <span data-bind="visible: ! dir_files(), text: '${ _ko('for directories') }'"/>
          <span data-bind="visible: dir_files(), text: '${ _ko('for directories and files') }'"/>
          <span data-bind="visible: recursive, text: '${ _ko('recursively') }'"/>
        </li>
      </ul>
    </div>


    <div data-bind="visible: $root.isEditing">
      <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
        <h6>
          <a class="pointer" data-bind="click: function(){ properties.deletes.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }">
            <span data-bind="text: $root.workflow_properties.deletes.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.deletes" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.deletes.help_text }" validate="nonempty"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.deletes.remove(this); $(document).trigger('drawArrows') }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.mkdirs.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }">
            <span data-bind="text: $root.workflow_properties.mkdirs.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.mkdirs" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.mkdirs.help_text }" validate="nonempty"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.mkdirs.remove(this); $(document).trigger('drawArrows') }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.touchzs.push(ko.mapping.fromJS({'value': ''})); $(document).trigger('drawArrows') }">
            <span data-bind="text: $root.workflow_properties.touchzs.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.touchzs" class="unstyled">
          <li>
            <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.touchzs.help_text }" validate="nonempty"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.touchzs.remove(this); $(document).trigger('drawArrows') }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

        <h6>
          <a class="pointer" data-bind="click: function(){ properties.moves.push(ko.mapping.fromJS({'source': '', 'destination': ''})); $(document).trigger('drawArrows') }">
            <span data-bind="text: $root.workflow_properties.moves.label"></span> <i class="fa fa-plus"></i>
          </a>
        </h6>
        <ul data-bind="foreach: properties.moves" class="unstyled">
          <li>
            <input type="text" class="filechooser-input thirty" data-bind="filechooser: source, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: source, value: source" placeholder="${ _('Source path') }" validate="nonempty"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: source(), with_label: false} }, visible: source().length > 0'></span>

            <input type="text" class="filechooser-input thirty" data-bind="filechooser: destination, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: destination, value: destination" placeholder="${ _('New destination path') }" validate="nonempty"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: destination(), with_label: false} }, visible: destination().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.moves.remove(this); $(document).trigger('drawArrows') }">
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
              <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.chmods.help_text }"/>
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
              <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.chgrps.help_text }"/>
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

          <span data-bind="template: { name: 'common-properties-retry' }"></span>
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
        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.to.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.to, attr: { placeholder: $root.workflow_properties.to.help_text }" validate="nonempty"/>
        </div>

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.cc.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.cc, attr: { placeholder: $root.workflow_properties.cc.help_text }"/>
        </div>

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.bcc.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.bcc, attr: { placeholder: $root.workflow_properties.bcc.help_text }"/>
        </div>

        <div data-bind="visible: $root.isEditing">
          <div data-bind="visible: ! $parent.ooziePropertiesExpanded()" class="nowrap">
            <span class="widget-label" data-bind="text: $root.workflow_properties.attachment.label"></span>
            <input type="text" class="filechooser-input seventy" data-bind="filechooser: properties.attachment, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: properties.attachment, value: properties.attachment, attr: { placeholder: $root.workflow_properties.bcc.help_text }"/>
          </div>
        </div>

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.content_type.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.content_type, attr: { placeholder: $root.workflow_properties.content_type.help_text }" validate="nonempty"/>
        </div>

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.subject.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.subject, attr: { placeholder: $root.workflow_properties.subject.help_text }" />
        </div>

        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.body.label"></span>
          <textarea class="seventy" style="resize:both" data-bind="value: properties.body, attr: { placeholder: $root.workflow_properties.body.help_text }"></textarea>
        </div>

      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
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
          <input type="text" class="seventy" data-bind="value: properties.cc, attr: { placeholder: $root.workflow_properties.cc.help_text }" />

          <span data-bind="template: { name: 'common-properties-retry' }"></span>
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
        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.mapper.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.mapper" validate="nonempty"/>
          <span data-bind='template: { name: "common-fs-link", data: {path: properties.mapper(), with_label: false} }'></span>
        </div>
        <div class="airy">
          <span class="widget-label" data-bind="text: $root.workflow_properties.reducer.label"></span>
          <input type="text" class="seventy" data-bind="value: properties.reducer" validate="nonempty"/>
          <span data-bind='template: { name: "common-fs-link", data: {path: properties.reducer(), with_label: false} }'></span>
        </div>
        <div data-bind="template: { name: 'common-properties-files' }"></div>
      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
      <span data-bind="text: $root.workflow_properties.mapper.label, visible: properties.mapper().length > 0"></span>
      <span data-bind='template: { name: "common-fs-link", data: {path: properties.mapper(), with_label: true} }, visible: properties.mapper().length > 0'></span>
      <br/>
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
        <ul class="unstyled white sortable-arguments" data-bind="sortable: { allowDrop: false, data: properties.distcp_parameters, options: { axis: 'y', containment: 'parent' }}">
          <li>
            <span class="muted move-widget">
              <i class="fa fa-arrows"></i>
            </span>
            <input type="text" class="input-xlarge filechooser-input seventy" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.distcp_parameters.help_text }, parseArguments: { list: $parent.properties.distcp_parameters, objectKey: 'value', callback: function(){ $(document).trigger('drawArrows'); } }" validate="nonempty"/>
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false} }, visible: value().length > 0'></span>
            <a href="#" data-bind="click: function(){ $parent.properties.distcp_parameters.remove(this);  }">
              <i class="fa fa-minus"></i>
            </a>
          </li>
        </ul>

      </div>
    </div>

    <div data-bind="visible: ! $root.isEditing()">
      <span data-bind="template: { name: 'logs-icon' }"></span>
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
               <input type="text" class="filechooser-input input-xlarge seventy"
                    data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.prepares.help_text }" validate="nonempty"/>
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
             <input type="text" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }" validate="nonempty"/>
             <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }"  validate="nonempty"/>
             <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
               <i class="fa fa-minus"></i>
              </a>
             </li>
           </ul>
           <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

           <h6>
             <span data-bind="text: $root.workflow_properties.java_opts.label"></span>
           </h6>
           <input type="text" class="input-xlarge seventy" data-bind="value: properties.java_opts, attr: { placeholder: $root.workflow_properties.java_opts.help_text }" />

           <span data-bind="template: { name: 'common-properties-retry' }"></span>
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

<script type="text/html" id="distcp-document-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())" style="padding: 10px">

    <span data-bind="template: { name: 'common-document-widget' }"></span>

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
               <input type="text" class="filechooser-input input-xlarge seventy"
                    data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.prepares.help_text }" validate="nonempty"/>
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
             <input type="text" data-bind="value: name" placeholder="${ _('name, e.g. mapred.job.queue.name') }" validate="nonempty"/>
             <input type="text" class="filechooser-input input-xlarge" data-bind="filechooser: value, filechooserOptions: globalFilechooserOptions, hdfsAutocomplete: value, value: value, attr: { placeholder: $root.workflow_properties.job_properties.help_text }"  validate="nonempty"/>
             <a href="#" data-bind="click: function(){ $parent.properties.job_properties.remove(this); $(document).trigger('drawArrows') }">
               <i class="fa fa-minus"></i>
              </a>
             </li>
           </ul>
           <em data-bind="visible: properties.job_properties().length == 0">${ _('No properties defined.') }</em>

           <h6>
             <span data-bind="text: $root.workflow_properties.java_opts.label"></span>
           </h6>
           <input type="text" class="input-xlarge seventy" data-bind="value: properties.java_opts, attr: { placeholder: $root.workflow_properties.java_opts.help_text }" />

           <span data-bind="template: { name: 'common-properties-retry' }"></span>
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

</%def>
