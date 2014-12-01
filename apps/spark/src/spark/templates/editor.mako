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
  <span data-bind="template: { name: 'snippet', foreach: snippets }"></span>

  <div style="margin: 20px">
    <a href="javascript: void(0)" data-bind="click: newSnippet">
      <i class="fa fa-plus" title="${ _('Add') }"></i> ${ _('Add a new snippet') }
    </a>
    <select data-bind="options: availableSnippets, value: selectedSnippet">
    </select>    
  </div>
</script>


<script type="text/html" id="snippet">
  <div class="snippet" data-bind="attr: {'id': 'snippet_' + id()}">
    <span class="muted" data-bind="text: id"></span>

    <div class="pull-right">
      <strong class="muted" data-bind="text: type"></strong>
      <strong class="muted" data-bind="text: status"></strong>
    </div>
    <br/>
    <br/>
    <textarea data-bind="value: statement, codemirror: { 'id': id(), 'lineNumbers': true, 'matchBrackets': true, 'mode': editorMode(), 'enter': execute }"></textarea>
    <a href="javascript:void(0)" data-bind="click: execute" class="btn codeMirror-overlaybtn">${ _('Go!') }</a>

    <div data-bind="css: klass">
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
</script>


<link rel="stylesheet" href="/static/css/common_dashboard.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<link rel="stylesheet" href="/spark/static/css/spark.css">

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


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
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
