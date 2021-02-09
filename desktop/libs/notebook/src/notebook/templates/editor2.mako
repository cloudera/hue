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
  from desktop import conf
  from desktop.views import _ko, antixss
  from desktop.webpack_utils import get_hue_bundles
  from django.utils.translation import ugettext as _
  from metadata.conf import OPTIMIZER
  from notebook.conf import ENABLE_QUERY_SCHEDULING, ENABLE_EXTERNAL_STATEMENT, ENABLE_PRESENTATION
  from webpack_loader.templatetags.webpack_loader import render_bundle
%>

<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="notebookKoComponents" file="/common_notebook_ko_components.mako" />
<%namespace name="sqlSyntaxDropdown" file="/sql_syntax_dropdown.mako" />

<link rel="stylesheet" href="${ static('notebook/css/editor2.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">

## % if ENABLE_QUERY_SCHEDULING.get():
## <script src="${ static('oozie/js/coordinator-editor.ko.js') }"></script>
## <script src="${ static('oozie/js/list-oozie-coordinator.ko.js') }"></script>
## % endif
## <script src="${ static('desktop/js/ko.common-dashboard.js') }" type="text/javascript" charset="utf-8"></script>

% for bundle in get_hue_bundles('editor'):
  ${ render_bundle(bundle) | n,unicode }
% endfor

<script type="text/html" id="editor-snippet-icon">
  <!-- ko if: viewSettings().snippetImage -->
  <img class="snippet-icon-image" data-bind="attr: { 'src': viewSettings().snippetImage }" alt="${ _('Snippet icon') }">
  <!-- /ko -->
  <!-- ko if: viewSettings().snippetIcon -->
  <i class="fa snippet-icon" data-bind="css: viewSettings().snippetIcon"></i>
  <!-- /ko -->
</script>

<script type="text/html" id="editor-menu-buttons">
  <div class="pull-right margin-right-10">
% if ENABLE_PRESENTATION.get():
    <!-- ko with: selectedNotebook() -->
    <div class="btn-group">
      <a class="btn" data-bind="click: function() { isPresentationMode(!isPresentationMode()); },
      css: {'btn-inverse': $root.isPresentationMode()}, attr: {title: isPresentationMode() ? '${ _ko('Exit presentation') }' : '${ _ko('View as a presentation') }'}">
        <i class="fa fa-line-chart"></i>
      </a>

      <!-- ko if: $root.canSave() -->
      <a class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)"><span class="caret"></span></a>
      <ul class="dropdown-menu pull-right">
        <li>
          <a class="pointer" title="${ _ko('Whether to open in presentation or editor mode by default') }" data-bind="click: function() { isPresentationModeDefault(!isPresentationModeDefault()); }">
            <i class="fa" data-bind="css: {'fa-toggle-on': isPresentationModeDefault(), 'fa-toggle-off': !isPresentationModeDefault()}"></i> ${ _('Open as presentation') }
          </a>
        </li>
      </ul>
      <!-- /ko -->
    </div>
    <!-- /ko -->
% endif

    <div class="btn-group">
      <a class="btn" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: function() { if ($root.canSave() ) { saveNotebook() } else { $('#editorSaveAsModal').modal('show');} }, attr: { title: $root.canSave() ? '${ _ko('Save') }' : '${ _ko('Save As') }' }">
        <i class="fa fa-save"></i>
      </a>

      <!-- ko if: $root.canSave -->
      <a class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)"><span class="caret"></span></a>
      <ul class="dropdown-menu pull-right">
        <li>
          <a class="pointer" data-bind="click: function() { $('#editorSaveAsModal').modal('show'); }">
            <i class="fa fa-fw fa-save"></i> ${ _('Save as...') }
          </a>
        </li>
      </ul>
      <!-- /ko -->
    </div>

    <!-- ko template: { ifnot: editorMode() || isPresentationMode(), name: 'editor-execution-actions' }--><!-- /ko -->

    <!-- ko ifnot: isPresentationMode() -->
    <div class="dropdown pull-right margin-left-10">
      <a class="btn" data-toggle="dropdown" href="javascript: void(0)">
        <i class="fa fa-fw fa-ellipsis-v"></i>
      </a>
      <ul class="dropdown-menu pull-right">
        <li>
          <!-- ko if: editorMode -->
          <a href="javascript:void(0)" data-bind="click: function() { hueUtils.removeURLParameter('editor'); newNotebook($root.editorType(), null, selectedNotebook() ? $root.selectedNotebook().snippets()[0].currentQueryTab() : null, 'blank'); }, attr: { 'title': '${ _('New ') }' +  editorTitle() + '${ _(' Query') }' }">
            <i class="fa fa-fw fa-file-o"></i> ${ _('New') }
          </a>
          <!-- /ko -->
          <!-- ko ifnot: editorMode -->
          <a href="javascript:void(0)" data-bind="click: newNotebook">
            <i class="fa fa-fw fa-file-o"></i> ${ _('New Notebook') }
          </a>
          <!-- /ko -->
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="publish: { 'assist.show.documents': editorMode() ? 'query-' + editorType() : editorType() }">
            <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> <span data-bind="text: editorMode() ? '${ _ko('Queries') }' : '${ _ko('Notebooks') }'"></span>
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" title="${ _('Show Editor Help') }" data-toggle="modal" data-target="#editorHelpModal">
            <i class="fa fa-fw fa-question"></i>  ${ _('Help') }
          </a>
        </li>
        <li class="divider"></li>
        <!-- ko if: $root.canSave -->
        <!-- ko if: sharingEnabled -->
        <li>
          <a href="javascript:void(0)" class="share-link" data-bind="click: prepareShareModal,
              css: {'isShared': isShared()}">
            <i class="fa fa-fw fa-users"></i> ${ _('Share') }
          </a>
        </li>
        <!-- /ko -->
        <!-- /ko -->
        <li>
          <a href="javascript:void(0)" data-bind="click: showSessionPanel">
            <i class="fa fa-fw fa-cogs"></i> ${ _('Sessions') }
          </a>
        </li>
      </ul>
    </div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="doc-search-autocomp-item">
  <a>
    <div>
      <strong style="font-size: 14px;" data-bind="html: name"></strong>
      <div style="width: 190px; overflow: hidden; white-space: nowrap; text-overflow:ellipsis; font-size: 12px;" class="muted" data-bind="text: description"></div>
    </div>
  </a>
</script>

<script type="text/html" id="editor-longer-operation">
  <div rel="tooltip" data-placement="bottom" data-bind="tooltip, fadeVisible: showLongOperationWarning" title="${ _('The query is hanging and taking longer than expected.') }" class="inline-block margin-right-10">
    <i class="fa fa-exclamation-triangle warning"></i>
  </div>
</script>

<script type="text/html" id="editor-query-redacted">
  <div rel="tooltip" data-placement="bottom" data-bind="tooltip, fadeVisible: is_redacted" title="${ _('The current query has been redacted to hide sensitive information.') }" class="inline-block margin-right-10">
    <i class="fa fa-low-vision warning"></i>
  </div>
</script>

<script type="text/html" id="snippet-header-database-selection">
  <!-- ko if: isSqlDialect() || dialect() === 'spark2' -->
  <!-- ko component: {
    name: 'hue-context-selector',
    params: {
      connector: connector,
      compute: compute,
      namespace: namespace,
      availableDatabases: availableDatabases,
      database: database,
      hideDatabases: !isSqlDialect()
    }
  } --><!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="editor-snippet-settings">
  <div class="snippet-settings" data-bind="slideVisible: settingsVisible" style="position: relative; z-index: 100;">
    <div class="snippet-settings-header">
      <h4><i class="fa fa-cog"></i> ${ _('Settings') }</h4>
    </div>
    <div class="snippet-settings-body">
      <form class="form-horizontal">
% if ENABLE_EXTERNAL_STATEMENT.get():
        <!-- ko if: isSqlDialect -->
        <div class="config-property">
          <label class="config-label">${ _('Type') }</label>
          <div class="config-controls">
            <div style="padding-top: 4px; display: inline-block;" data-bind="component: { name: 'hue-drop-down', params: { value: statementType, entries: statementTypes, linkTitle: '${ _ko('Statement type') }' } }"></div>
          </div>
        </div>
        <!-- /ko -->
% endif
        <!-- ko template: { if: typeof properties().driverCores != 'undefined', name: 'property', data: { type: 'number', label: '${ _ko('Driver Cores') }', value: properties().driverCores, title: '${ _ko('Number of cores used by the driver, only in cluster mode (Default: 1)') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().executorCores != 'undefined', name: 'property', data: { type: 'number', label: '${ _ko('Executor Cores') }', value: properties().executorCores, title: '${ _ko('Number of cores per executor (Default: 1)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().numExecutors != 'undefined', name: 'property', data: { type: 'number', label: '${ _ko('Executors') }', value: properties().numExecutors, title: '${ _ko('Number of executors to launch (Default: 2)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().queue != 'undefined', name: 'property', data: { type: 'string', label: '${ _ko('Queue') }', value: properties().queue, title: '${ _ko('The YARN queue to submit to (Default: default)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().archives != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Archives') }', value: properties().archives, title: '${ _ko('Archives to be extracted into the working directory of each executor (YARN only)') }', placeholder: '${ _ko('e.g. file.zip') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().files != 'undefined', name: 'property', data: { type: 'hdfs-files', label: '${ _ko('Files') }', value: properties().files, visibleObservable: settingsVisible, title: '${ _ko('Files to be placed in the working directory of each executor.') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().functions != 'undefined', name: 'property', data: { type: 'functions', label: '${ _ko('Functions') }', value: properties().functions, visibleObservable: settingsVisible, title: '${ _ko('UDFs name and class') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().settings != 'undefined', name: 'property', data: { type: 'settings', label: '${ _ko('Settings') }', value: properties().settings, visibleObservable: settingsVisible, title: '${ _ko('Properties') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().spark_opts != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Spark Arguments') }', value: properties().spark_opts, title: '${ _ko('Names and values of Spark parameters') }', placeholder: '${ _ko('e.g. --executor-memory 20G --num-executors 50') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().parameters != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Parameters') }', value: properties().parameters, title: '${ _ko('Names and values of Pig parameters and options') }', placeholder: '${ _ko('e.g. input /user/data, -param input=/user/data, -optimizer_off SplitFilter, -verbose') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().hadoopProperties != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Hadoop properties') }', value: properties().hadoopProperties, title: '${ _ko('Name and values of Hadoop properties') }', placeholder: '${ _ko('e.g. mapred.job.queue.name=production, mapred.map.tasks.speculative.execution=false') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().resources != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Resources') }', value: properties().resources, title: '${ _ko('HDFS Files or compressed files') }', placeholder: '${ _ko('e.g. /tmp/file, /tmp.file.zip') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().capture_output != 'undefined', name: 'property', data: { type: 'boolean', label: '${ _ko('Capture output') }', value: properties().capture_output, title: '${ _ko('If capturing the output of the shell script') }' }} --><!-- /ko -->
      </form>
    </div>
    <a class="pointer demi-modal-chevron" data-bind="click: function() { settingsVisible(! settingsVisible()) }"><i class="fa fa-chevron-up"></i></a>
  </div>
</script>

<script type="text/html" id="editor-optimizer-alerts">
  <!-- ko if: window.HAS_OPTIMIZER && (dialect() == 'impala' || dialect() == 'hive') && ! $root.isPresentationMode() -->
  <div class="optimizer-container" data-bind="css: { 'active': showOptimizer }">
    <!-- ko if: hasSuggestion() -->
    <!-- ko with: suggestion() -->
    <!-- ko if: parseError -->
    <!-- ko if: $parent.compatibilityTargetPlatform().value === $parent.dialect() && $parent.compatibilitySourcePlatform().value === $parent.dialect() -->
    <div class="optimizer-icon error" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
      <i class="fa fa-exclamation"></i>
    </div>
    <!-- ko if: $parent.showOptimizer -->
    <span class="optimizer-explanation alert-error alert-neutral">${ _('The query has a parse error.') }</span>
    <!-- /ko -->
    <!-- /ko -->
    ## Oracle, MySQL compatibility... as they return a parseError and not encounteredString.
          <!-- ko if: $parent.compatibilityTargetPlatform().value !== $parent.dialect() || $parent.dialect() !== $parent.compatibilitySourcePlatform().value -->
    <div class="optimizer-icon warning" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
      <i class="fa fa-exclamation"></i>
    </div>
    <!-- ko if: $parent.showOptimizer -->
    <span class="optimizer-explanation alert-warning alert-neutral">${ _('This ') } <span data-bind="text: $parent.compatibilitySourcePlatform().name"></span> ${ _(' query is not compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.</span>
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: !parseError() && ($parent.compatibilityTargetPlatform().value !== $parent.dialect() || $parent.compatibilitySourcePlatform().value !== $parent.dialect()) -->
    <!-- ko if: queryError.encounteredString().length == 0 -->
    <div class="optimizer-icon success" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
      <i class="fa fa-check"></i>
    </div>
    <!-- ko if: $parent.showOptimizer -->
    <span class="optimizer-explanation alert-success alert-neutral">
              ${ _('The ') } <div data-bind="component: { name: 'hue-drop-down', params: { value: $parent.compatibilitySourcePlatform, entries: $parent.compatibilitySourcePlatforms, labelAttribute: 'name' } }" style="display: inline-block"></div>
      <!-- ko if: $parent.compatibilitySourcePlatform().value === $parent.dialect() -->
      ${ _(' query is compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.
                <a href="javascript:void(0)" data-bind="click: function() { $parent.dialect($parent.compatibilityTargetPlatform().value); }">${ _('Execute it with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span></a>.
      <!-- /ko -->
      <!-- ko if: $parent.compatibilitySourcePlatform().value !== $parent.dialect() -->
      ${ _(' query is compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.
      <!-- /ko -->
            </span>
    <!-- /ko -->
    <!-- /ko -->
    <!-- ko ifnot: queryError.encounteredString().length == 0 -->
    <div class="optimizer-icon warning" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
      <i class="fa fa-exclamation"></i>
    </div>
    <!-- ko if: $parent.showOptimizer -->
    <span class="optimizer-explanation alert-warning alert-neutral">${ _('This query is not compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.</span>
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: ! hasSuggestion() && topRisk() -->
    <!-- ko if: topRisk().risk === 'low' -->
    <div class="optimizer-icon success" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Some low risks were detected, see the assistant for details.') }">
      <i class="fa fa-check"></i>
    </div>
    <!-- /ko -->
    <!-- ko if: topRisk().risk == 'medium' -->
    <div class="optimizer-icon warning" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Some medium risks were detected, see the assistant for details.') }">
      <i class="fa fa-exclamation"></i>
    </div>
    <!-- /ko -->
    <!-- ko if: topRisk().risk == 'high' -->
    <div class="optimizer-icon error" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Some high risks were detected, see the assistant for details.') }">
      <i class="fa fa-exclamation"></i>
    </div>
    <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: hasSuggestion() == '' && ! topRisk() -->
    <div class="optimizer-icon success" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Query validated, no issues found.') }">
      <i class="fa fa-check"></i>
    </div>
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="editor-code-editor">
  <div style="width: 100%; height: 100%; position: relative;" class="editor-drop-target">
    <ace-editor-ko-bridge style="width:100%; height: 100%; position: relative;" data-bind="
      vueEvents: {
        'ace-created': function (event) {
          ace(event.detail);
        },
        'cursor-changed': function (event) {
          aceCursorPosition(event.detail);
        },
        'create-new-doc': function () {
          huePubSub.publish('editor.create.new');
        },
        'save-doc': function () {
          huePubSub.publish('editor.save');
        },
        'toggle-presentation-mode': function () {
          huePubSub.publish('editor.presentation.toggle');
        },
        'value-changed': function (event) {
          statement_raw(event.detail);
        }
      },
      vueKoProps: {
        executor: executor,
        valueObservable: statement_raw,
        cursorPositionObservable: aceCursorPosition,
        idObservable: id,
        aceOptions: {
          showLineNumbers: $root.editorMode(),
          showGutter: $root.editorMode(),
          maxLines: $root.editorMode() ? null : 25,
          minLines: $root.editorMode() ? null : 3
        }
      }
    "></ace-editor-ko-bridge>
    <!-- ko component: { name: 'hue-editor-droppable-menu', params: { editor: ace.bind($data), parentDropTarget: '.editor-drop-target' } } --><!-- /ko -->
  </div>
</script>

<script type="text/html" id="editor-execution-actions">
  <div class="btn-group">
    <!-- ko if: $root.selectedNotebook() -->
    <!-- ko with: $root.selectedNotebook() -->
    <a class="btn" rel="tooltip" data-placement="bottom" title="${ _("Execute all") }" data-bind="visible: ! isExecutingAll(), click: function() { executeAll(); }">
      <i class="fa fa-fw fa-play"></i>
    </a>
    <!-- ko if: ! (snippets()[executingAllIndex()] && snippets()[executingAllIndex()].isCanceling()) -->
    <a class="btn red" rel="tooltip" data-placement="bottom" title="${ _("Stop all") }" data-bind="visible: isExecutingAll(), click: function() { cancelExecutingAll(); }">
      <i class="fa fa-fw fa-stop"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: snippets()[executingAllIndex()] && snippets()[executingAllIndex()].isCanceling() -->
    <a class="btn" style="cursor: default;" title="${ _('Canceling operation...') }">
      <i class="fa fa-fw fa-spinner snippet-side-single fa-spin"></i>
    </a>
    <!-- /ko -->
    <!-- /ko -->

    <a class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)">
      <span class="caret"></span>
    </a>
    <ul class="dropdown-menu">
      <li>
        <a class="pointer" rel="tooltip" data-placement="bottom" data-bind="click: function() { $root.selectedNotebook().isHidingCode(! $root.isHidingCode()); }, attr: { 'title': $root.isHidingCode() ? '${ _ko('Show the logic') }' : '${ _ko('Hide the logic') }' }">
          <i class="fa fa-fw" data-bind="css: { 'fa-expand': $root.isHidingCode(), 'fa-compress': ! $root.isHidingCode() }"></i>
          <span data-bind="visible: $root.isHidingCode">${ _('Show the code') }</span>
          <span data-bind="visible: ! $root.isHidingCode()">${ _('Hide the code') }</span>
        </a>
      </li>
##    <li>
##      <a class="pointer" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
##        <i class="fa fa-fw fa-eraser"></i> ${ _('Clear results') }
##      </a>
##    </li>
      <li>
        <a href="javascript:void(0)" data-bind="click: displayCombinedContent, visible: ! $root.isPresentationMode() ">
          <i class="fa fa-fw fa-file-text-o"></i> ${ _('Show all content') }
        </a>
      </li>
    </ul>
    <!-- /ko -->
  </div>
</script>


## TODO: Move additional types to VariableSubstitution.vue
## <script type="text/html" id="snippet-variables">
##   <div class="variables" data-bind="with: variableSubstitutionHandler">
##     <ul data-bind="foreach: variables" class="unstyled inline">
##       <li>
##         <div class="input-prepend margin-top-10">
##           <!-- ko ifnot: path() -->
##           <span class="muted add-on" data-bind="text: name"></span>
##           <!-- /ko -->
##           <!-- ko if: path() -->
##           <a href="javascript:void(0);" data-bind="click: $root.showContextPopover" style="float: left"> <span class="muted add-on" data-bind="text: name"></span></a>
##           <!-- /ko -->
##           <!-- ko if: meta.type() === 'text' -->
##           <!-- ko if: meta.placeholder() -->
##           <input class="input-medium" type="text" data-bind="value: value, attr: { value: value, type: type, placeholder: meta.placeholder() || '${ _ko('Variable value') }' }, valueUpdate: 'afterkeydown', event: { 'keydown': $parent.onKeydownInVariable }, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
##           <!-- /ko -->
##           <!-- ko ifnot: meta.placeholder() -->
##           <!-- ko if: type() == 'datetime-local' -->
##           <input class="input-medium" type="text" data-bind="attr: { value: value }, value: value, datepicker: { momentFormat: 'YYYY-MM-DD HH:mm:ss.S' }">
##           <!-- /ko -->
##           <!-- ko if: type() == 'date' -->
##           <input class="input-medium" type="text" data-bind="attr: { value: value }, value: value, datepicker: { momentFormat: 'YYYY-MM-DD' }">
##           <!-- /ko -->
##           <!-- ko if: type() == 'checkbox' -->
##           <input class="input-medium" type="checkbox" data-bind="checked: value">
##           <!-- /ko -->
##           <!-- ko ifnot: (type() == 'datetime-local' || type() == 'date' || type() == 'checkbox') -->
##           <input class="input-medium" type="text" value="true" data-bind="value: value, attr: { value: value,  type: type() || 'text', step: step }, valueUpdate: 'afterkeydown', event: { 'keydown': $parent.onKeydownInVariable }, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
##           <!-- /ko -->
##           <!-- /ko -->
##           <!-- /ko -->
##           <!-- ko if: meta.type() === 'select' -->
##           <select data-bind="
##                 selectize: sample,
##                 optionsText: 'text',
##                 optionsValue: 'value',
##                 selectizeOptions: {
##                   create: function (input) {
##                     sampleUser().push({ text: ko.observable(input), value: ko.observable(input) });
##                     return { text: input, value: input };
##                   }
##                 },
##                 value: value,
##                 event: { 'keydown': $parent.onKeydownInVariable }
##               "></select>
##           <!-- /ko -->
##         </div>
##       </li>
##     </ul>
##   </div>
## </script>

<script type="text/html" id="editor-executable-snippet-body">
  <div style="padding:10px;">
    <form class="form-horizontal">
      <!-- ko if: dialect() == 'distcp' -->
      <div class="control-group">
        <label class="control-label">${_('Source')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().source_path, valueUpdate: 'afterkeydown', filechooser: properties().source_path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true }" placeholder="${ _('Source path to copy, e.g. ${nameNode1}/path/to/input.txt') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Destination')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().destination_path, valueUpdate: 'afterkeydown', filechooser: properties().destination_path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true }" placeholder="${ _('Destination path, e.g. ${nameNode2}/path/to/output.txt') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Variables')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().distcp_parameters != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Arguments") }', value: properties().distcp_parameters, title: '${ _ko("Arguments for the script") }', placeholder: '${ _ko("e.g. MAX=10, PATH=$PATH:/user/path") }' } } --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: dialect() == 'shell' -->
      <div class="control-group">
        <label class="control-label">${_('Script path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().command_path, valueUpdate: 'afterkeydown', filechooser: properties().command_path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Source path to the command') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Variables')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().arguments != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Arguments") }', value: properties().arguments, title: '${ _ko("Arguments for the script") }', placeholder: '${ _ko("e.g. MAX=10, PATH=$PATH:/user/path") }' } } --><!-- /ko -->
          <!-- ko template: { if: typeof properties().env_var != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Environment") }', value: properties().env_var, title: '${ _ko("Environment variable for the script") }', placeholder: '${ _ko("e.g. CLASSPATH=/path/file.jar") }' } } --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: dialect() == 'mapreduce' -->
      <div class="control-group">
        <label class="control-label">${_('Jar path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().app_jar, valueUpdate: 'afterkeydown', filechooser: properties().app_jar, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Source path to the main MapReduce jar') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Properties')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().hadoopProperties != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Hadoop Properties') }', value: properties().hadoopProperties, title: '${ _ko('Name and values of Hadoop properties') }', placeholder: '${ _ko('e.g. mapred.job.queue.name=production, mapred.map.tasks.speculative.execution=false') }'}} --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: dialect() === 'jar' || dialect() === 'java' -->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().app_jar, valueUpdate: 'afterkeydown', filechooser: properties().app_jar, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Path to application jar, e.g. hdfs://localhost:8020/user/hue/oozie-examples.jar') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Class')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().class, valueUpdate: 'afterkeydown'" placeholder="${ _('Class name of application, e.g. org.apache.oozie.example.SparkFileCopy') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Variables')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().arguments != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Arguments") }', value: properties().arguments, title: '${ _ko("Arguments for the script") }', placeholder: '${ _ko("e.g. MAX=10, PATH=$PATH:/user/path") }' } } --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: dialect() === 'py'-->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().py_file, valueUpdate: 'afterkeydown', filechooser: properties().py_file, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Path to python file, e.g. script.py') }"/>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: dialect() === 'spark2' -->
      <div class="control-group">
        <!-- ko template: { if: typeof properties().jars != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Libs') }', value: properties().jars, title: '${ _ko('Path to jar or python files.') }', placeholder: '${ _ko('e.g. /user/hue/pi.py') }'}} --><!-- /ko -->
      </div>
      <!-- ko if: $.grep(properties().jars(), function(val, index) { return val.toLowerCase().endsWith('.jar'); }).length > 0 -->
      <div class="control-group">
        <label class="control-label">
          ${_('Class')}
        </label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().class, valueUpdate: 'afterkeydown'" placeholder="${ _('Class name of application, e.g. org.apache.oozie.example.SparkFileCopy') }"/>
        </div>
      </div>
      <!-- /ko -->
      <div class="control-group">
        <!-- ko template: { if: typeof properties().spark_arguments != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Arguments') }', value: properties().spark_arguments, title: '${ _ko('Arguments to the application.') }', placeholder: '${ _ko('e.g. 10, /user/hue/input') }'}} --><!-- /ko -->
      </div>
      <!-- /ko -->
    </form>
  </div>
</script>

<script type="text/html" id="editor-snippet-execution-status">
  <div class="snippet-execution-status" data-bind="clickForAceFocus: ace.bind($data)">
    <a class="inactive-action pull-left snippet-logs-btn" href="javascript:void(0)" data-bind="
          visible: status() === 'running' && errors().length == 0,
          click: function() {
            huePubSub.publish('result.grid.hide.fixed.headers');
            $data.showLogs(!$data.showLogs());
          },
          css: {'blue': $data.showLogs}
        " title="${ _('Toggle Logs') }"><i class="fa fa-fw" data-bind="css: { 'fa-caret-right': !$data.showLogs(), 'fa-caret-down': $data.showLogs() }"></i></a>
    <div class="snippet-progress-container" data-bind="visible: status() != 'canceled' && status() != 'with-optimizer-report'">
      <!-- ko component: { name: 'executable-progress-bar', params: { activeExecutable: activeExecutable } } --><!-- /ko -->
    </div>
    <div class="snippet-error-container alert alert-error" style="margin-bottom: 0" data-bind="visible: errors().length > 0">
      <ul class="unstyled" data-bind="foreach: errors">
        <li data-bind="text: message"></li>
        <!-- ko if: help -->
        <li><a href="javascript:void(0)" data-bind="click: function() {
          huePubSub.publish('editor.settings.update', {
            key: $data.help.setting.name,
            value: $data.help.setting.value
          });
          $parent.settingsVisible(true);
        }">${ _("Update max_row_size setting.") }</a></li>
        <!-- /ko -->
      </ul>
    </div>
    <div class="snippet-error-container alert alert-error" style="margin-bottom: 0" data-bind="visible: aceErrors().length > 0">
      <ul class="unstyled" data-bind="foreach: aceErrors">
        <li data-bind="text: message"></li>
      </ul>
    </div>
    <div class="snippet-error-container alert" style="margin-bottom: 0" data-bind="visible: aceWarnings().length > 0">
      <ul class="unstyled" data-bind="foreach: aceWarnings">
        <li data-bind="text: message"></li>
      </ul>
    </div>
    <div class="snippet-error-container alert alert-error" style="margin-bottom: 0" data-bind="visible: status() == 'canceled', click: function() { status('ready'); }" title="${ _('Click to hide') }">
      <ul class="unstyled">
        <li>${ _("The statement was canceled.") }</li>
      </ul>
    </div>
  </div>
</script>

<script type="text/html" id="editor-snippet-code-resizer">
  <editor-resizer-ko-bridge data-bind="vueKoProps: {
      editorObservable: ace
    }"></editor-resizer-ko-bridge>
</script>

<script type="text/html" id="editor-snippet-type-controls">
  <div class="inactive-action dropdown hover-actions">
    <a class="snippet-side-btn" style="padding-right: 0; padding-left: 2px;" data-toggle="dropdown" href="javascript: void(0);">
      <span data-bind="template: { name: 'editor-snippet-icon', data: $data }"></span>
    </a>
    <a class="inactive-action dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0);">
      <i class="fa fa-caret-down"></i>
    </a>

    <ul class="dropdown-menu" data-bind="foreach: $root.availableSnippets">
      <li><a class="pointer" data-bind="click: function(){ $parent.changeDialect($data.type()); }, text: name"></a></li>
    </ul>
  </div>
</script>

<script type ="text/html" id="editor-execution-controls">
  <div class="snippet-actions" style="padding: 5px;">
    <div class="pull-left">
      <executable-actions-ko-bridge data-bind="vueKoProps: {
          executableObservable: activeExecutable,
          beforeExecute: beforeExecute
        }"></executable-actions-ko-bridge>
    </div>
    <!-- ko if: isSqlDialect() && !$root.isPresentationMode() -->
      <div class="pull-right" data-bind="component: { name: 'snippet-editor-actions', params: { snippet: $data } }"></div>
    <!-- /ko -->
    <div class="pull-right">
      <!-- ko if: status() === 'loading' -->
      <i class="fa fa-fw fa-spinner fa-spin"></i> ${ _('Creating session') }
      <!-- /ko -->
##      <!-- ko if: status() !== 'loading' && $root.editorMode() && result.statements_count() > 1 -->
##      ${ _('Statement ')} <span data-bind="text: (result.statement_id() + 1) + '/' + result.statements_count()"></span>
##      <div style="display: inline-block"
##           class="label label-info"
##           data-bind="attr: {
##           'title':'${ _ko('Showing results of the statement #')}' + (result.statement_id() + 1)}">
##        <div class="pull-left" data-bind="text: (result.statement_id() + 1)"></div><div class="pull-left">/</div><div class="pull-left" data-bind="text: result.statements_count()"></div>
##      </div>
##      <!-- /ko -->
    </div>

##  TODO: Move to snippet execution-actions
##  <a class="snippet-side-btn" data-bind="click: reexecute, visible: $root.editorMode() && result.statements_count() > 1, css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }" title="${ _('Restart from the first statement') }">
##    <i class="fa fa-fw fa-repeat snippet-side-single"></i>
##  </a>
##  <!-- ko if: !isCanceling() -->
##  <a class="snippet-side-btn red" data-bind="click: cancel, visible: status() == 'running' || status() == 'starting'" title="${ _('Cancel operation') }">
##    <i class="fa fa-fw fa-stop snippet-side-single"></i>
##  </a>
##  <!-- /ko -->
##  <!-- ko if: isCanceling() -->
##  <a class="snippet-side-btn" style="cursor: default;" title="${ _('Canceling operation...') }">
##    <i class="fa fa-fw fa-spinner snippet-side-single fa-spin"></i>
##  </a>
##  <!-- /ko -->
##  <div style="display: inline-block" class="inactive-action dropdown hover-actions pointer" data-bind="css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }">
##    <!-- ko if: isBatchable() && wasBatchExecuted() -->
##    <a class="snippet-side-btn" style="padding-right:0; padding-left: 2px" href="javascript: void(0)" title="${ _('Submit all the queries as a background batch job.') }" data-bind="click: function() { wasBatchExecuted(true); execute(); }, visible: status() != 'running' && status() != 'loading', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }">
##      <i class="fa fa-fw fa-send"></i>
##    </a>
##    <!-- /ko -->
##    <!-- ko if: ! isBatchable() || ! wasBatchExecuted() -->
##    <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="attr: {'title': $root.editorMode() && result.statements_count() > 1 ? '${ _ko('Execute next statement')}' : '${ _ko('Execute or CTRL + ENTER') }'}, click: function() { wasBatchExecuted(false); execute(); }, visible: status() != 'running' && status() != 'loading' && status() != 'starting', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }, style: {'padding-left': $parent.isBatchable() ? '2px' : '0' }">
##      <i class="fa fa-fw fa-play" data-bind="css: { 'snippet-side-single' : ! $parent.isBatchable() }"></i>
##    </a>
##    <!-- /ko -->
##    % if ENABLE_BATCH_EXECUTE.get():
##      <!-- ko if: isBatchable() && status() != 'running' && status() != 'loading' && ! $root.isPresentationMode() -->
##      <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'disabled': ! isReady(), 'blue': currentQueryTab() == 'queryExplain' }">
##        <i class="fa fa-caret-down"></i>
##      </a>
##      <ul class="dropdown-menu less-padding">
##        <li>
##          <a href="javascript:void(0)" data-bind="click: function() { wasBatchExecuted(false); $('.dropdown-toggle').dropdown('toggle'); execute(); }, style: { color: ! isReady() || status() === 'running' || status() === 'loading' ? '#999' : ''}, css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }" title="${ _('Execute interactively the current statement') }">
##            <i class="fa fa-fw fa-play"></i> ${_('Execute')}
##          </a>
##        </li>
##        <li>
##          <a href="javascript:void(0)" data-bind="click: function() { wasBatchExecuted(true); $('.dropdown-toggle').dropdown('toggle'); execute(); }, css: {'disabled': ! isReady() }" title="${ _('Submit all the queries as a background batch job.') }">
##            <i class="fa fa-fw fa-send"></i> ${_('Batch')}
##          </a>
##        </li>
##      </ul>
##      <!-- /ko -->
##    % endif
##  </div>
  </div>
</script>

<script type="text/html" id="editor-modals">
  <div id="editorHelpModal" class="modal transparent-modal hide" data-backdrop="true" style="width:980px;margin-left:-510px!important">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Editor help')}</h2>
    </div>
    <div class="modal-body">
      <!-- ko component: 'aceKeyboardShortcuts' --><!-- /ko -->
    </div>
    <div class="modal-footer">
      <a href="javascript: void(0)" class="btn" data-dismiss="modal">${_('Close')}</a>
    </div>
  </div>
  <div id="editorCombinedContentModal" class="modal hide" data-backdrop="true" style="width:780px;margin-left:-410px!important">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('All Notebook content')}</h2>
    </div>
    <div class="modal-body">
      <pre data-bind="oneClickSelect, text: combinedContent"></pre>
    </div>
    <div class="modal-footer">
      <a href="javascript: void(0)" class="btn" data-dismiss="modal">${_('Close')}</a>
    </div>
  </div>
  <div class="submit-modal-editor modal hide"></div>
  <div id="editorSaveAsModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <!-- ko if: $root.editorMode() -->
      <h2 class="modal-title">${_('Save query as...')}</h2>
      <!-- /ko -->
      <!-- ko ifnot: $root.editorMode() -->
      <h2 class="modal-title">${_('Save notebook as...')}</h2>
      <!-- /ko -->
    </div>

    <!-- ko if: $root.selectedNotebook() -->
    <div class="modal-body">
      <form class="form-horizontal">
        <div class="control-group">
          <label class="control-label">${_('Name')}</label>
          <div class="controls">
            <input type="text" class="input-xlarge" data-bind="value: $root.selectedNotebook().name, valueUpdate:'afterkeydown'"/>
          </div>
        </div>
        <div class="control-group">
          <label class="control-label">${_('Description')}</label>
          <div class="controls">
            <input type="text" class="input-xlarge" data-bind="value: $root.selectedNotebook().description, valueUpdate:'afterkeydown'" placeholder="${ _('(optional)') }"/>
          </div>
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
      <input type="button" class="btn btn-primary disable-feedback" value="${_('Save')}" data-dismiss="modal" data-bind="click: saveAsNotebook, enable: $root.selectedNotebook().name().length > 0"/>
    </div>
    <!-- /ko -->
  </div>

  <!-- ko if: $root.selectedNotebook() -->
  <!-- ko with: $root.selectedNotebook() -->
  <div id="editorRetryModal" class="modal hide fade" data-keyboard="false" data-backdrop="static">
    <div class="modal-header">
      <h2 class="modal-title">${_('Operation timed out')}</h2>
    </div>
    <div class="modal-body">
      <p>${_('The operation timed out. Do you want to retry?')}</p>
    </div>
    <div class="modal-footer">
      <a class="btn" data-bind="click: retryModalCancel">${_('No')}</a>
      <a class="btn btn-primary disable-feedback" data-bind="click: retryModalConfirm">${_('Yes, retry')}</a>
    </div>
  </div>
  <!-- /ko -->
  <!-- /ko -->

  <div class="ace-filechooser" style="display:none;">
    <div class="ace-filechooser-close">
      <a class="pointer" data-bind="click: function(){ $('.ace-filechooser').hide(); }"><i class="fa fa-times"></i></a>
    </div>
    <div class="ace-filechooser-content">
    </div>
  </div>
</script>

<script type="text/html" id="editor-navbar">
  <div class="navbar hue-title-bar">
    <div class="navbar-inner">
      <div class="container-fluid">
        <!-- ko template: { name: 'editor-menu-buttons' } --><!-- /ko -->
        <div class="nav-collapse">
          <ul class="nav editor-nav">
            <li class="app-header" style="display:none" data-bind="visible: true">
              <!-- ko if: editorMode -->
              <a data-bind="hueLink: '${ url('notebook:editor') }?type=' + editorType(), attr: { 'title': editorTitle() + '${ _(' Editor') }'}" style="cursor: pointer">
                <!-- ko template: { name: 'app-icon-template', data: { icon: editorType() } } --><!-- /ko -->
                <!-- ko switch: editorType() -->
                <!-- ko case: 'impala' -->Impala<!-- /ko -->
                <!-- ko case: 'rdbms' -->DB Query<!-- /ko -->
                <!-- ko case: 'pig' -->Pig<!-- /ko -->
                <!-- ko case: 'java' -->Java<!-- /ko -->
                <!-- ko case: 'spark2' -->Spark<!-- /ko -->
                <!-- ko case: 'sqoop1' -->Sqoop 1<!-- /ko -->
                <!-- ko case: 'distcp' -->DistCp<!-- /ko -->
                <!-- ko case: 'shell' -->Shell<!-- /ko -->
                <!-- ko case: 'mapreduce' -->MapReduce<!-- /ko -->
                <!-- ko case: ['beeswax', 'hive'] -->Hive<!-- /ko -->
                <!-- ko case: 'mapreduce' -->MapReduce<!-- /ko -->
                <!-- ko case: 'spark' -->Scala<!-- /ko -->
                <!-- ko case: 'pyspark' -->PySpark<!-- /ko -->
                <!-- ko case: 'r' -->R<!-- /ko -->
                <!-- ko case: 'jar' -->Spark Submit Jar<!-- /ko -->
                <!-- ko case: 'py' -->Spark Submit Python<!-- /ko -->
                <!-- ko case: 'solr' -->Solr SQL<!-- /ko -->
                <!-- ko case: 'kafkasql' -->Kafka SQL<!-- /ko -->
                <!-- ko case: 'markdown' -->Markdown<!-- /ko -->
                <!-- ko case: 'text' -->Text<!-- /ko -->
                <!-- ko case: 'clickhouse' -->ClickHouse<!-- /ko -->
                <!-- ko case: $default --><span data-bind="text: editorTitle()"></span><!-- /ko -->
                <!-- /ko -->
                <!-- ko component: { name: 'hue-favorite-app', params: { app: 'editor', interpreter: editorType() }} --><!-- /ko -->
              </a>
              <!-- /ko -->
              <!-- ko ifnot: editorMode -->
              <i class="fa fa-file-text-o app-icon" style="vertical-align: middle"></i>
              Notebook
              <!-- ko component: { name: 'hue-favorite-app', params: { app: 'notebook' }} --><!-- /ko -->
              <!-- /ko -->
            </li>

            <!-- ko with: selectedNotebook -->
            <li class="no-horiz-padding">
              <a>&nbsp;</a>
            </li>
            <li data-bind="visible: isHistory" style="display: none" class="no-horiz-padding muted">
              <a title="${ _('This is a history query') }"><i class="fa fa-fw fa-history"></i></a>
            </li>
            <li data-bind="visible: directoryUuid" style="display: none" class="no-horiz-padding muted">
              <a title="${ _('Open directory of this query') }" data-bind="hueLink: '/home/?uuid=' + directoryUuid()"
                 class="pointer inactive-action" href="javascript:void(0)"><i class="fa fa-fw fa-folder-o"></i>
              </a>
            </li>
            <li data-bind="visible: parentSavedQueryUuid" style="display: none" class="no-horiz-padding muted">
              <a title="${ _('Click to open original saved query') }" data-bind="click: function() { $root.openNotebook(parentSavedQueryUuid()) }" class="pointer inactive-action">
                <i class="fa fa-fw fa-file-o"></i>
              </a>
            </li>
            <li data-bind="visible: isSaved() && ! isHistory() && ! parentSavedQueryUuid()" style="display: none" class="no-horiz-padding muted">
              <a title="${ _('This is a saved query') }"><i class="fa fa-fw fa-file-o"></i></a>
            </li>
            <li data-bind="visible: isSchedulerJobRunning" style="display: none" class="no-horiz-padding muted">
              <a title="${ _('Click to open original saved query') }" data-bind="click: function() { $root.openNotebook(parentSavedQueryUuid()) }" class="pointer inactive-action">
                ${ _("Scheduling on") }
              </a>
            </li>
            <li class="query-name no-horiz-padding skip-width-calculation">
              <a href="javascript:void(0)">
                <div class="notebook-name-desc" data-bind="editable: name, editableOptions: { inputclass: 'notebook-name-input', enabled: true, placement: 'bottom', emptytext: '${_ko('Add a name...')}', tpl: '<input type=\'text\' maxlength=\'255\'>' }"></div>
              </a>
            </li>
            <li class="skip-width-calculation" data-bind="tooltip: { placement: 'bottom', title: description }">
              <a href="javascript:void(0)">
                <div class="notebook-name-desc" data-bind="editable: description, editableOptions: { type: 'textarea', enabled: true, placement: 'bottom', emptytext: '${_ko('Add a description...')}' }"></div>
              </a>
            </li>
            <!-- /ko -->
          </ul>
        </div>
      </div>
    </div>
  </div>
</script>

<div id="editorComponents" class="editor" data-bind="css: { 'editor-bottom-expanded': bottomExpanded, 'editor-top-expanded': topExpanded }">
  <!-- ko template: { name: 'editor-modals' } --><!-- /ko -->
  <!-- ko if: !isPresentationModeEnabled() || !isPresentationMode() -->
  <div class="editor-nav-bar">
    <!-- ko template: { name: 'editor-navbar' } --><!-- /ko -->
  </div>
  <!-- /ko -->
  <div class="editor-app" data-bind="with: firstSnippet">
    <!-- ko if: $parent.isPresentationModeEnabled() && $parent.isPresentationMode() -->
      <presentation-mode-ko-bridge style="width:100%; height: 100%; position: relative;" data-bind="
        vueEvents: {
          'before-execute': function (event) {
            activeExecutable(event.detail);
          },
          'close': function () {
            parentNotebook.isPresentationMode(false);
          },
          'variables-changed': function (event) {
            setVariables(event.detail);
          }
        },
        vueKoProps: {
          executor: executor,
          titleObservable: parentNotebook.name,
          descriptionObservable: parentNotebook.description
        }
      "></presentation-mode-ko-bridge>
    <!-- /ko -->
    <!-- ko ifnot: $parent.isPresentationModeEnabled() && $parent.isPresentationMode() -->
      <div class="editor-top">
        <div class="editor-top-actions">
          <!-- ko template: { name: 'editor-query-redacted' } --><!-- /ko -->
          <!-- ko template: { name: 'editor-longer-operation' } --><!-- /ko -->
          <div class="editor-top-right-actions">
            <!-- ko template: { name: 'snippet-header-database-selection' } --><!-- /ko -->
            <button title="${ _('Expand editor') }" data-bind="toggle: $root.topExpanded">
              <i class="fa" data-bind="css: { 'fa-expand': !$root.topExpanded(), 'fa-compress': $root.topExpanded() }"></i>
            </button>
          </div>
        </div>
        <div class="editor-settings-drawer">
          <!-- ko template: 'editor-snippet-settings' --><!-- /ko -->
        </div>
  ##      <!-- ko template: { name: 'editor-optimizer-alerts' } --><!-- /ko -->
        <div class="editor-code-editor">
          <!-- ko template: { name: 'editor-code-editor' } --><!-- /ko -->
        </div>
  ##      <!-- ko template: { name: 'snippet-variables' }--><!-- /ko -->
          <variable-substitution-ko-bridge data-bind="
            vueEvents: {
              'variables-changed': function (event) {
                setVariables(event.detail);
              }
            },
            vueKoProps: {
              initialVariables: executor.variables
            }
          "></variable-substitution-ko-bridge>
  ##      <!-- ko template: { name: 'editor-executable-snippet-body' } --><!-- /ko -->
        <div class="editor-execute-status">
          <!-- ko template: { name: 'editor-snippet-execution-status' } --><!-- /ko -->
        </div>
        <div class="editor-execute-actions">
          <!-- ko template: { name: 'editor-execution-controls' } --><!-- /ko -->
        </div>
      </div>
      <div class="editor-divider"></div>
      <div class="editor-bottom">
        <ul class="editor-bottom-tabs nav nav-tabs">
          <li data-bind="click: function() { currentQueryTab('queryHistory'); }, css: { 'active': currentQueryTab() == 'queryHistory' }">
            <a class="inactive-action" style="display:inline-block" href="#queryHistory" data-toggle="tab">${_('Query History')}</a>
          </li>
          <li data-bind="click: function(){ currentQueryTab('savedQueries'); }, css: { 'active': currentQueryTab() == 'savedQueries' }">
            <a class="inactive-action" style="display:inline-block" href="#savedQueries" data-toggle="tab">${_('Saved Queries')}</a>
          </li>
          <li data-bind="click: function() { currentQueryTab('queryResults'); }, css: {'active': currentQueryTab() == 'queryResults'}">
            <a class="inactive-action" style="display:inline-block" href="#queryResults" data-toggle="tab">${_('Results')}
  ##          <!-- ko if: result.rows() != null  -->
  ##          (<span data-bind="text: result.rows().toLocaleString() + (dialect() == 'impala' && result.rows() == 1024 ? '+' : '')" title="${ _('Number of rows') }"></span>)
  ##          <!-- /ko -->
            </a>
          </li>
          <li data-bind="click: function() { currentQueryTab('queryChart'); }, css: {'active': currentQueryTab() == 'queryChart'}">
            <a class="inactive-action" style="display:inline-block" href="#queryChart" data-toggle="tab">${_('Chart')}</a>
          </li>
          <!-- ko if: explanation -->
          <li data-bind="click: function() { currentQueryTab('queryExplain'); }, css: {'active': currentQueryTab() == 'queryExplain'}"><a class="inactive-action" href="#queryExplain" data-toggle="tab">${_('Explain')}</a></li>
          <!-- /ko -->
          <!-- ko foreach: pinnedContextTabs -->
          <li data-bind="click: function() { $parent.currentQueryTab(tabId) }, css: { 'active': $parent.currentQueryTab() === tabId }">
            <a class="inactive-action" data-toggle="tab" data-bind="attr: { 'href': '#' + tabId }">
              <i class="snippet-icon fa" data-bind="css: iconClass"></i> <span data-bind="text: title"></span>
              <div class="inline-block inactive-action margin-left-10 pointer" data-bind="click: function () { $parent.removeContextTab($data); }">
                <i class="snippet-icon fa fa-times"></i>
              </div>
            </a>
          </li>
          <!-- /ko -->

          <li data-bind="click: function(){ currentQueryTab('executionAnalysis'); }, css: {'active': currentQueryTab() == 'executionAnalysis'}">
            <a class="inactive-action" href="#executionAnalysis" data-toggle="tab">${_('Execution Analysis')}</a>
          </li>

          <li class="editor-bottom-tab-actions">
            <button data-bind="toggle: $root.bottomExpanded">
              <i class="fa" data-bind="css: { 'fa-expand': !$root.bottomExpanded(), 'fa-compress': $root.bottomExpanded() }"></i>
            </button>
          </li>
        </ul>
        <div class="editor-bottom-tab-content tab-content">
          <div class="tab-pane" id="queryHistory" data-bind="css: { 'active': currentQueryTab() === 'queryHistory' }">
            <div class="editor-bottom-tab-panel">
              <!-- ko component: {
                name: 'query-history',
                params: {
                  currentNotebook: parentNotebook,
                  openFunction: parentVm.openNotebook.bind(parentVm),
                  dialect: dialect
                }
              } --><!-- /ko -->
            </div>
          </div>

          <div class="tab-pane" id="savedQueries" data-bind="css: { 'active': currentQueryTab() === 'savedQueries' }" style="overflow: hidden">
            <div class="editor-bottom-tab-panel">
              <!-- ko component: {
                name: 'saved-queries',
                params: {
                  currentNotebook: parentNotebook,
                  openFunction: parentVm.openNotebook.bind(parentVm),
                  dialect: dialect,
                  currentTab: currentQueryTab
                }
              } --><!-- /ko -->
            </div>
          </div>

          <div class="tab-pane" id="queryResults" data-bind="css: {'active': currentQueryTab() == 'queryResults'}">
            <div class="execution-results-tab-panel">
              <result-table-ko-bridge class="table-results-bridge" data-bind="vueKoProps: {
                  executableObservable: activeExecutable
                }"></result-table-ko-bridge>
            </div>
          </div>

          <div class="tab-pane" id="queryChart" data-bind="css: {'active': currentQueryTab() == 'queryChart'}">
            <div class="editor-bottom-tab-panel editor-chart-panel">
              <!-- ko component: { name: 'snippet-result-chart', params: {
                activeExecutable: activeExecutable,
                editorMode: parentVm.editorMode,
                id: id,
                isPresentationMode: parentNotebook.isPresentationMode,
                resultsKlass: resultsKlass
              }} --><!-- /ko -->
            </div>
          </div>

          <!-- ko if: explanation -->
          <div class="tab-pane" id="queryExplain" data-bind="css: {'active': currentQueryTab() == 'queryExplain'}">
            <div class="editor-bottom-tab-panel">
              <div style="width: 100%; height: 100%; overflow-y: auto;">
                <pre class="no-margin-bottom" data-bind="text: explanation"></pre>
              </div>
            </div>
          </div>
          <!-- /ko -->

          <div class="tab-pane" id="executionAnalysis" data-bind="css: {'active': currentQueryTab() == 'executionAnalysis'}">
            <div class="execution-analysis-tab-panel">
              <execution-analysis-panel-ko-bridge class="execution-analysis-bridge" data-bind="
                vueKoProps: {
                  executableObservable: activeExecutable
                },
                vueEvents: {
                  'execution-error': function () { currentQueryTab('executionAnalysis') }
                }
              "></execution-analysis-panel-ko-bridge>
            </div>
          </div>

          <!-- ko foreach: pinnedContextTabs -->
          <div class="tab-pane" data-bind="attr: { 'id': tabId }, css: {'active': $parent.currentQueryTab() === tabId }">
            <div class="editor-bottom-tab-panel">
              <div style="display: flex; flex-direction: column; margin-top: 10px; overflow: hidden; height: 100%; position: relative;" data-bind="template: 'context-popover-contents'"></div>
            </div>
          </div>
          <!-- /ko -->
        </div>
      </div>
      <div class="hoverMsg hide">
        <p class="hoverText">${_('Drop a SQL file here')}</p>
      </div>
    <!-- /ko -->
  </div>
</div>

${ sqlSyntaxDropdown.sqlSyntaxDropdown() }

<script type="text/javascript">
  window.EDITOR_BINDABLE_ELEMENT = '#editorComponents';

  window.EDITOR_SUFFIX = 'editor';

  var HUE_PUB_SUB_EDITOR_ID = (window.location.pathname.indexOf('notebook') > -1) ? 'notebook' : 'editor';

  window.EDITOR_VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode,antixss }, {
    huePubSubId: HUE_PUB_SUB_EDITOR_ID,
    user: '${ user.username }',
    userId: ${ user.id },
    suffix: 'editor',
    assistAvailable: true,
    autocompleteTimeout: AUTOCOMPLETE_TIMEOUT,
    snippetViewSettings: {
      default: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/sql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      code: {
        placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
        snippetIcon: 'fa-code'
      },
      hive: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/hive',
        snippetImage: '${ static("beeswax/art/icon_beeswax_48.png") }',
        sqlDialect: true
      },
      impala: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/impala',
        snippetImage: '${ static("impala/art/icon_impala_48.png") }',
        sqlDialect: true
      },
      presto: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/presto',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      dasksql: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/dasksql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      elasticsearch: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/elasticsearch',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      druid: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/druid',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      bigquery: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/bigquery',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      phoenix: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/phoenix',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      ksql: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/ksql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      flink: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/flink',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      jar : {
        snippetIcon: 'fa-file-archive-o '
      },
      mysql: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      mysqljdbc: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      oracle: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/oracle',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      pig: {
        placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
        aceMode: 'ace/mode/pig',
        snippetImage: '${ static("pig/art/icon_pig_48.png") }'
      },
      postgresql: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/pgsql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      solr: {
        placeHolder: '${ _("Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space") }',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      kafkasql: {
        placeHolder: '${ _("Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space") }',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      java : {
        snippetIcon: 'fa-file-code-o'
      },
      py : {
        snippetIcon: 'fa-file-code-o'
      },
      pyspark: {
        placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
        aceMode: 'ace/mode/python',
        snippetImage: '${ static("spark/art/icon_spark_48.png") }'
      },
      r: {
        placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
        aceMode: 'ace/mode/r',
        snippetImage: '${ static("spark/art/icon_spark_48.png") }'
      },
      scala: {
        placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
        aceMode: 'ace/mode/scala',
        snippetImage: '${ static("spark/art/icon_spark_48.png") }'
      },
      spark: {
        placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
        aceMode: 'ace/mode/scala',
        snippetImage: '${ static("spark/art/icon_spark_48.png") }'
      },
      spark2: {
        snippetImage: '${ static("spark/art/icon_spark_48.png") }'
      },
      mapreduce: {
        snippetIcon: 'fa-file-archive-o'
      },
      shell: {
        snippetIcon: 'fa-terminal'
      },
      sqoop1: {
        placeHolder: '${ _("Example: import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1") }',
        snippetImage: '${ static("sqoop/art/icon_sqoop_48.png") }'
      },
      distcp: {
        snippetIcon: 'fa-files-o'
      },
      sqlite: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/sql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      text: {
        placeHolder: '${ _('Type your text here') }',
        aceMode: 'ace/mode/text',
        snippetIcon: 'fa-header'
      },
      markdown: {
        placeHolder: '${ _('Type your markdown here') }',
        aceMode: 'ace/mode/markdown',
        snippetIcon: 'fa-header'
      }
    }
  });

  if (window.WEB_SOCKETS_ENABLED) {
    const prefix = location.protocol === 'https:' ? 'wss://' : 'ws://';
    var editorWs = new WebSocket(prefix + window.location.host + '/ws/editor/results/' + 'userA' + '/');

    editorWs.onopen = function(e) {
      console.info('Notification socket open.');
    };

    editorWs.onmessage = function(e) {
      var data = JSON.parse(e.data);
      if (data['type'] === 'channel_name') {
        window.WS_CHANNEL = data['data'];
      } else if (data['type'] === 'query_result') {
        huePubSub.publish('editor.ws.query.fetch_result', data['data']);
      }
      console.log(data);
    };

    editorWs.onclose = function(e) {
      console.error('Chat socket closed unexpectedly');
    };
  }

  window.EDITOR_ENABLE_QUERY_SCHEDULING = '${ ENABLE_QUERY_SCHEDULING.get() }' === 'True';

  window.EDITOR_ID = ${ editor_id or 'null' };

  window.NOTEBOOKS_JSON = ${ notebooks_json | n,unicode };

  window.OPTIMIZER_AUTO_UPLOAD_QUERIES = '${ OPTIMIZER.AUTO_UPLOAD_QUERIES.get() }' === 'True';

  window.OPTIMIZER_AUTO_UPLOAD_DDL = '${ OPTIMIZER.AUTO_UPLOAD_DDL.get() }' === 'True';

  window.OPTIMIZER_QUERY_HISTORY_UPLOAD_LIMIT = ${ OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() };
</script>
