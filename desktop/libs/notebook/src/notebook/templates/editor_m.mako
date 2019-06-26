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
  from desktop.views import commonheader_m, commonfooter_m
  from desktop import conf
  from django.utils.translation import ugettext as _
  from desktop.views import _ko
%>
<%namespace name="assist" file="/assist.mako" />

${ commonheader_m(editor_type, editor_type, user, request, "68px") | n,unicode }

<style>
  .ace-editor {
    width: 100%;
    height: 80px;
  }

  body.open .main-container {
    overflow: hidden;
    -webkit-transition: -webkit-transform 0.5s;
    transition: transform 0.5s;
    -webkit-box-shadow: 0px 0px 5px 0px rgba(0, 0, 0, 0.75);
    -moz-box-shadow: 0px 0px 5px 0px rgba(0, 0, 0, 0.75);
    box-shadow: 0px 0px 5px 0px rgba(0, 0, 0, 0.75);
  }

  body.open-left .main-container {
    -webkit-transform: rotateY(-32deg) scale(0.8) translateY(-120px) translateX(185px);
    transform: rotateY(-32deg) scale(0.8) translateY(-120px) translateX(185px);
  }

  body.open-right .main-container {
    -webkit-transform: rotateY(32deg) scale(0.8) translateY(-120px) translateX(-185px);
    transform: rotateY(32deg) scale(0.8) translateY(-120px) translateX(-185px);
  }

  .table-container {
    width: 100%;
    overflow-y: auto;
    _overflow: auto;
    margin: 0 0 1em;
  }

  .table-container::-webkit-scrollbar {
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
  }

  .table-container::-webkit-scrollbar-thumb {
    border-radius: 8px;
    border: 3px solid #fff;
    background-color: rgba(0, 0, 0, .3);
  }
</style>

<div class="container main-container">

<!-- ko with: selectedNotebook -->

  <!-- ko foreach: snippets  -->
  <div class="ace-editor" data-bind="attr: { id: id() }, aceEditor: {
        snippet: $data,
        contextTooltip: '${ _ko("Right-click for details") }',
        expandStar: '${ _ko("Shift + Click to replace with all columns") }',
        highlightedRange: result.statement_range,
        aceOptions: {
          showLineNumbers: $root.editorMode(),
          showGutter: $root.editorMode(),
          maxLines: $root.editorMode() ? null : 25,
          minLines: $root.editorMode() ? null : 3
        }
      }"></div>

  <a class="btn margin-top-10" href="javascript: void(0)" data-bind="attr: {'title': $root.editorMode() && result.statements_count() > 1 ? '${ _ko('Execute next statement')}' : '${ _ko('Execute or CTRL + ENTER') }'}, click: function() { wasBatchExecuted(false); execute(); }, visible: status() != 'running' && status() != 'loading', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }">
    <i class="fa fa-fw fa-play"></i> ${ _('Execute') }
  </a>

  <a class="btn margin-top-10" data-bind="click: cancel, visible: status() == 'running'" title="${ _('Cancel operation') }">
    <i class="fa fa-fw fa-stop"></i> ${ _('Cancel') }
  </a>

  <!-- ko if: result -->
  <div class="table-container">
    <table class="table table-condensed resultTable">
      <thead>
      <tr data-bind="foreach: result.meta">
        <th class="sorting" data-bind="text: ($index() == 0 ? '&nbsp;' : $data.name), css: typeof cssClass != 'undefined' ? cssClass : 'sort-string', attr: {title: $data.type }, style:{'width': $index() == 0 ? '1%' : ''}, click: function(obj, e){ $(e.target).parents('table').trigger('sort', obj); }"></th>
      </tr>
      </thead>
      <tbody data-bind="foreach: result.data">
        <tr data-bind="foreach: $data">
          <td data-bind="text: $data"></td>
        </tr>
      </tbody>
    </table>
  </div>
  <div data-bind="visible: status() == 'expired' && result.data() && result.data().length > 99, css: resultsKlass" style="display:none;">
    <pre class="margin-top-10"><i class="fa fa-check muted"></i> ${ _("Results have expired, rerun the query if needed.") }</pre>
  </div>
  <!-- /ko -->

  <!-- /ko -->

  <div class="clearfix"></div>

  <ul class="nav nav-tabs margin-top-20">
    <li class="active"><a href="#history"><i class="fa fa-clock-o"></i></a></li>
    <li><a href="#saved"><i class="fa fa-save"></i></a></li>
    <li><a href="#results"><i class="fa fa-table"></i></a></li>
  </ul>

  <!-- ko if: history().length > 0 -->
  <table class="table table-condensed margin-top-20 history-table" style="background: #FFF">
    <tbody data-bind="foreach: history">
    <!-- ko if: $index() < 10 -->
      <tr data-bind="click: function() { if (uuid() != $root.selectedNotebook().uuid()) { $root.openNotebook(uuid()); } }, css: { 'highlight': uuid() == $root.selectedNotebook().uuid(), 'pointer': uuid() != $root.selectedNotebook().uuid() }">
        <td class="muted" data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}">
          <span data-bind="momentFromNow: {data: lastExecuted, interval: 10000, titleFormat: 'LLL'}"></span>
        </td>
        <td class="muted" data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}">
          <!-- ko switch: status -->
          <!-- ko case: 'running' -->
          <div class="history-status" data-bind="tooltip: { title: '${ _ko("Query running") }', placement: 'bottom' }"><i class="fa fa-fighter-jet fa-fw"></i></div>
          <!-- /ko -->
          <!-- ko case: 'failed' -->
          <div class="history-status" data-bind="tooltip: { title: '${ _ko("Query failed") }', placement: 'bottom' }"><i class="fa fa-exclamation fa-fw"></i></div>
          <!-- /ko -->
          <!-- ko case: 'available' -->
          <div class="history-status" data-bind="tooltip: { title: '${ _ko("Result available") }', placement: 'bottom' }"><i class="fa fa-check fa-fw"></i></div>
          <!-- /ko -->
          <!-- ko case: 'expired' -->
          <div class="history-status" data-bind="tooltip: { title: '${ _ko("Result expired") }', placement: 'bottom' }"><i class="fa fa-unlink fa-fw"></i></div>
          <!-- /ko -->
          <!-- /ko -->
        </td>
        <td class="muted" data-bind="ellipsis: {data: name(), length: 30}, style: {'border-top-width': $index() == 0 ? '0' : ''}"></td>
        <td data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}"><div data-bind="highlight: { value: query, dialect: $parent.type }"></div></td>
      </tr>
    <!-- /ko -->
    </tbody>
  </table>
  <!-- /ko -->
<!-- /ko -->


</div>

<script type="text/javascript">
  if (ko.options) {
    ko.options.deferUpdates = true;
  }

  ace.config.set("basePath", "${ static('desktop/js/ace') }");

  var VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode }, {
    user: '${ user.username }',
    userId: ${ user.id },
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
      jar: {
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
      java: {
        snippetIcon: 'fa-file-archive-o '
      },
      py: {
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
      sqlite: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/sqlite',
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

  var viewModel;

  $(document).ready(function () {
    //$("body").swipe({fingers: 'all', swipeLeft: swipeLeft, swipeRight: swipeRight, allowPageScroll: "auto"});

    function swipeLeft() {
      if ($('body').hasClass('open-left')){
         $('body').removeClass('open open-left');
      }
      else {
        $('body').addClass('open open-right');
      }
    }

    function swipeRight() {
      if ($('body').hasClass('open-right')){
         $('body').removeClass('open open-right');
      }
      else {
        $('body').addClass('open open-left');
      }
    }

    viewModel = new EditorViewModel(${ editor_id or 'null' }, ${ notebooks_json | n,unicode }, VIEW_MODEL_OPTIONS);
    ko.applyBindings(viewModel);
    viewModel.init();
  });

</script>


${ commonfooter_m(request, messages) | n,unicode }
