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


${ commonheader(_('Query'), app_name, user, "100px") | n,unicode }

<div class="card card-toolbar">
  <div style="float: left; margin-left: 20px">
    <div class="toolbar-label">${_('SPARK')}</div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': false }"
         title="${_('Spark Scala')}" rel="tooltip" data-placement="bottom">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
           <img src="/spark/static/art/icon_spark_48.png" class="app-icon" />
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': false }"
         title="${_('Spark Scala')}" rel="tooltip" data-placement="bottom">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
           <img src="/spark/static/art/icon_spark_48.png" class="app-icon" />
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': false }"
         title="${_('Spark Scala')}" rel="tooltip" data-placement="bottom">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
           <img src="/spark/static/art/icon_spark_48.png" class="app-icon" />
         </a>
    </div>    
    <div class="toolbar-label">${_('SPARK')}</div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': false }"
         title="${_('Hive Query')}" rel="tooltip" data-placement="bottom">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
           <img src="/beeswax/static/art/icon_beeswax_48.png" class="app-icon" />
         </a>
    </div>    
  </div>
  <div class="clearfix"></div>
</div>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">

        <ul class="nav nav-tabs">
          <!-- ko foreach: notebooks -->
            <li class="tab-pane" data-bind="css: { active: $parent.selectedNotebook() === $data }">
              <a href="javascript:void(0)" data-bind="text: id, click: $parent.selectedNotebook.bind(null, $data)"></a>
            </li>
          <!-- /ko -->
          <li class="tab-pane">
            <a href="javascript:void(0)" data-bind="click: newNotebook"><i class="fa fa-plus" title="${ _('Add a new notebook') }"></i></a>
          </li>
        </ul>

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

  <div class="snippet">
    <span class="muted" data-bind="text: id"></span>

    <div class="pull-right">
      <strong class="muted" data-bind="text: type"></strong>
      <strong class="muted" data-bind="text: status"></strong>
    </div>
    <br/>
    <br/>
    <textarea data-bind="value: statement, codemirror: { 'lineNumbers': true, 'matchBrackets': true, 'mode': 'text/x-hiveql', 'enter': execute }"></textarea>
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
<script src="/static/ext/js/codemirror-sql.js"></script>
<script src="/static/ext/js/codemirror-markdown.js"></script>
<script src="/static/ext/js/markdown.min.js"></script>


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/spark.vm.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript" charset="utf-8">

  ko.bindingHandlers.codemirror = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = $.extend(valueAccessor(), {
        extraKeys: {
          "Ctrl-Enter": function () {
            valueAccessor().enter();
          }
        }
      });
      var editor = CodeMirror.fromTextArea(element, options);
      element.editor = editor;
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
