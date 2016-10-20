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

${ commonheader_m(_('Editor'), editor_type, user, request, "68px") | n,unicode }



<!-- ko with: selectedNotebook -->
  <!-- ko if: history().length > 0 -->
  <table class="table table-condensed margin-top-10 history-table">
    <tbody data-bind="foreach: history">
      <tr data-bind="click: function() { if (uuid() != $root.selectedNotebook().uuid()) { $root.openNotebook(uuid()); } }, css: { 'highlight': uuid() == $root.selectedNotebook().uuid(), 'pointer': uuid() != $root.selectedNotebook().uuid() }">
        <td style="width: 100px" class="muted" data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}">
          <span data-bind="momentFromNow: {data: lastExecuted, interval: 10000, titleFormat: 'LLL'}"></span>
        </td>
        <td style="width: 25px" class="muted" data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}">
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
        <td style="width: 25px" class="muted" data-bind="ellipsis: {data: name(), length: 30}, style: {'border-top-width': $index() == 0 ? '0' : ''}"></td>
        <td data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}"><div data-bind="highlight: query(), flavor: $parent.type" class="history-item"></div></td>
      </tr>
    </tbody>
  </table>
  <!-- /ko -->
<!-- /ko -->



<script src="${ static('desktop/ext/js/knockout.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/js/ace/ace.js') }"></script>
<script src="${ static('desktop/js/ace/mode-impala.js') }"></script>
<script src="${ static('desktop/js/ace/mode-hive.js') }"></script>
<script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }"></script>
<script src="${ static('desktop/js/ko.switch-case.js') }"></script>
<script src="${ static('desktop/js/sqlFunctions.js') }"></script>
<script src="${ static('desktop/js/autocomplete/sql.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter2.js') }"></script>
<script src="${ static('desktop/js/hdfsAutocompleter.js') }"></script>
<script src="${ static('desktop/js/autocompleter.js') }"></script>
<script src="${ static('desktop/js/hue.json.js') }"></script>
<script src="${ static('notebook/js/notebook.ko.js') }"></script>

<script type="text/javascript">
  ko.options.deferUpdates = true;

  ace.config.set("basePath", "/static/desktop/js/ace");

    var VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode }, {
      user: '${ user.username }',
      userId: ${ user.id },
      assistAvailable: true,
      % if conf.USE_NEW_AUTOCOMPLETER.get():
      useNewAutocompleter: true,
      % endif
      autocompleteTimeout: ${ conf.EDITOR_AUTOCOMPLETE_TIMEOUT.get() },
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
        java : {
          snippetIcon: 'fa-file-archive-o '
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
      viewModel = new EditorViewModel(${ editor_id or 'null' }, ${ notebooks_json | n,unicode }, VIEW_MODEL_OPTIONS);
      ko.applyBindings(viewModel);
      viewModel.init();
    });

</script>


${ commonfooter_m(request, messages) | n,unicode }
