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


${ commonheader(_('Query'), app_name, user, "68px") | n,unicode }


<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: true, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
          data-bind="click: saveNotebook, css: {'btn': true}">
        <i class="fa fa-save"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <button type="button" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("New...") }"
          data-bind="click: newNotebook, css: {'btn': true}">
        <i class="fa fa-file-o"></i>
      </button>
      <button type="button" title="${ _('Open') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("New...") }"
          data-bind="click: newNotebook, css: {'btn': true}">
        <i class="fa fa-folder-open-o"></i>
      </button>      
      <a class="btn" href="${ url('spark:list_notebooks') }" title="${ _('Notebooks') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-terminal"></i>
      </a>
    % endif
  </div>


  <ul class="nav nav-tabs">
    <!-- ko foreach: notebooks -->
      <li data-bind="css: { active: $parent.selectedNotebook() === $data }">
        <a href="javascript:void(0)" data-bind="text: name, click: $parent.selectedNotebook.bind(null, $data)"></a>
      </li>
    <!-- /ko -->
    <li>
      <a href="javascript:void(0)" data-bind="click: newNotebook"><i class="fa fa-plus" title="${ _('Add a new notebook') }"></i></a>
    </li>
  </ul>
</div>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
        <div class="tab-content" data-bind="foreach: notebooks">
          <div class="tab-pane" data-bind="css: { active: $parent.selectedNotebook() === $data }, template: { name: 'notebook'}">
          </div>
        </div>
    </div>
  </div>
</div>


<script type="text/html" id="notebook">
      <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
        sortable: { template: 'snippet', data: snippets, isEnabled: $root.isEditing,
        options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
            'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});},
            'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); $('.card-body').slideUp('fast'); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
            dragged: function(widget){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}">
  </div>

  <div style="margin: 20px">
    <a href="javascript: void(0)" data-bind="click: newSnippet">
      <i class="fa fa-plus" title="${ _('Add') }"></i> ${ _('Add a new snippet') }
    </a>
    <select data-bind="options: availableSnippets, value: selectedSnippet">
    </select>    
  </div>
</script>


<script type="text/html" id="snippet">
  <div class="row-fluid">
    <div data-bind="css: klass, attr: {'id': 'snippet_' + id()}">

      <h2 class="card-heading simple">

        <span data-bind="visible: $root.isEditing">
          <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
          <a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a>
          <a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a>
          &nbsp;
        </span>

        <!-- ko if: type() == 'hive' -->
        <img src="/beeswax/static/art/icon_beeswax_48.png" class="snippet-icon">
        <!-- /ko -->

        <!-- ko if: type() == 'impala' -->
        <img src="/impala/static/art/icon_impala_48.png" class="snippet-icon">
        <!-- /ko -->

        <!-- ko if: type() == 'scala' -->
        <img src="/spark/static/art/icon_spark_48.png" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">scala</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'python' -->
        <img src="/spark/static/art/icon_spark_48.png" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">python</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'sql' -->
        <img src="/spark/static/art/icon_spark_48.png" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">sql</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'pig' -->
        <img src="/pig/static/art/icon_pig_48.png" class="snippet-icon">
        <!-- /ko -->


        <span data-bind="editable: id, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
        <div class="inline pull-right">
          <strong class="muted" data-bind="text: status"></strong> &nbsp;
          <a href="javascript:void(0)" data-bind="visible: $root.isEditing, click: function(){ remove($parent, $data);}"><i class="fa fa-times"></i></a>
        </div>
      </h2>

      <div class="row-fluid">
        <div data-bind="css: editorKlass">
          <textarea data-bind="value: statement, codemirror: { 'id': id(), 'lineNumbers': true, 'matchBrackets': true, 'mode': editorMode(), 'enter': execute }"></textarea>
          <a href="javascript:void(0)" data-bind="click: execute" class="btn codeMirror-overlaybtn">${ _('Go!') }</a>
        </div>
      </div>

      <div data-bind="css: resultsKlass">
        <table class="table table-condensed">
          <thead>
            <tr data-bind="foreach: result.meta">
              <th data-bind="text: $data.name"></th>
            </tr>
          </thead>
          <tbody data-bind="foreach: result.data">
            <tr data-bind="foreach: $data">
              <td data-bind="text: $data"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</script>


<link rel="stylesheet" href="/static/css/common_dashboard.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<link rel="stylesheet" href="/spark/static/css/spark.css">
<link rel="stylesheet" href="/static/ext/css/bootstrap-editable.css">

<script src="/static/ext/js/codemirror-3.11.js"></script>
<script src="/static/js/codemirror-pig.js"></script>
<script src="/static/js/codemirror-hql.js"></script>
<script src="/static/js/codemirror-python.js"></script>
<script src="/static/js/codemirror-clike.js"></script>

<script src="/static/js/codemirror-show-hint.js"></script>

<script src="/static/js/codemirror-isql-hint.js"></script>
<script src="/static/js/codemirror-hql-hint.js"></script>
<script src="/static/js/codemirror-pig-hint.js"></script>
<script src="/static/js/codemirror-python-hint.js"></script>
<script src="/static/js/codemirror-clike-hint.js"></script>

<script src="/static/ext/js/markdown.min.js"></script>

<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.hue-bindings.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/spark.vm.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript" charset="utf-8">

  // text/x-pig
  // text/x-scala
  // text/x-python
  // text/x-impalaql
  // text/x-hiveql

  ko.bindingHandlers.codemirror = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = $.extend(valueAccessor(), {
        extraKeys: {
          "Ctrl-Space": function (cm) {
            switch (valueAccessor().mode) {
              case "text/x-pig":
                CodeMirror.availableVariables = [];
                CodeMirror.showHint(cm, CodeMirror.pigHint);
                break;
              case "text/x-python":
                CodeMirror.showHint(cm, CodeMirror.pythonHint);
                break;
              default:
                break;
            }
          },
          "Ctrl-Enter": function () {
            valueAccessor().enter();
          }
        }
      });
      var editor = CodeMirror.fromTextArea(element, options);

      element.editor = editor;
      $("#snippet_"+options.id).data("editor", editor);
      editor.setValue(allBindingsAccessor().value());
      window.setTimeout(function () {
        editor.refresh();
      }, 100);
      editor.setSize("100%", "100px");
      var wrapperElement = $(editor.getWrapperElement());

      editor.on("change", function () {
        allBindingsAccessor().value(editor.getValue());
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        wrapperElement.remove();
      });
    }
  };

  viewModel = new EditorViewModel(${ notebooks_json | n,unicode });
  ko.applyBindings(viewModel);
  viewModel.init();


  $(document).ready(function(){

  });


</script>

${ commonfooter(messages) | n,unicode }
