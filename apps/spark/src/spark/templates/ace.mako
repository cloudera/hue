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
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport
  from django.utils.translation import ugettext as _
%>
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_("Notebooks"), "spark", user, "60px") | n,unicode }

<script src="${ static('desktop/ext/js/ace/ace.js') }"></script>
<script src="${ static('desktop/ext/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>

<style type="text/css" media="screen">
  .editor {
    height: 200px;
    margin: 20px;
  }
  .filechooser {
    position: absolute;
    display: none;
    z-index: 20000;
    background-color: #FFFFFF;
    padding: 10px;
    min-width: 350px;
  }
</style>

<!-- ko foreach: editors -->
  <div class="editor" data-bind="attr: {id: UUID()}, aceEditor: {value: snippet, ace: ace, mode: mode, onChange: changeEditor, onAfterExec: textInputHandler, extraCompleters: completers, errors: errors }">
  </div>
<!-- /ko -->

<div class="filechooser">
  <a class="pointer pull-right" data-bind="click: function(){ $('.filechooser').hide(); }"><i class="fa fa-times"></i></a>
  <div class="filechooser-content">
    <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
  </div>
</div>

<script src="${ static('desktop/ext/js/knockout.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-deferred-updates.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('beeswax/js/autocomplete.utils.js') }" type="text/javascript" charset="utf-8"></script>

<script>

  var HIVE_AUTOCOMPLETE_BASE_URL = "/beeswax/api/autocomplete/";
  var HIVE_AUTOCOMPLETE_FAILS_QUIETLY_ON = [500]; // error codes from beeswax/views.py - autocomplete
  var HIVE_AUTOCOMPLETE_USER = "hue";
  var HIVE_AUTOCOMPLETE_APP = "beeswax";

  var STATS_PROBLEMS = "${ _('There was a problem loading the stats.') }";

  var HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK = function (data) {
    if (data != null && data.error && typeof resetNavigator != "undefined") {
      resetNavigator();
    }
  };

  function newCompleter(items) {
    return {
      getCompletions: function(editor, session, pos, prefix, callback) {
        callback(null, items);
      }
    }
  }

  function textInputHandler(event, editor, valueAccessor) {

  }

  function changeEditor(event, editor, valueAccessor) {
    // if it's pig and before it's LOAD ' we disable the autocomplete and show a filechooser btn
    if (editor.session.getMode().$id = "ace/mode/pig") {

    }
    else {

      if (event.data.text == "."){
      editor.showSpinner();
      // fill up with fields
      hac_getTableColumns("default", "sample_07", editor.getValue(), function(data){
        var _fieldNames = data.split(" ");
        var _fields = [];
        _fieldNames.forEach(function(fld){
          _fields.push({value: fld, score: 1000, meta: "column"});
        });
        valueAccessor().extraCompleters([newCompleter(_fields)]);
        editor.hideSpinner();
      })
    }
    else {
      editor.showSpinner();
      valueAccessor().extraCompleters([]);
      hac_getTables("default", function(data){
        var _tableNames = data.split(" ");
        var _tables = [];
        _tableNames.forEach(function(tbl){
          _tables.push({value: tbl, score: 1000, meta: "table"});
        });
        valueAccessor().extraCompleters([newCompleter(_tables)]);
        editor.hideSpinner();
      });
    }

    }
  }

  function Snip(mode) {
    var self = this;
    self.ace = ko.observable(null);
    self.mode = ko.observable(mode);
    self.snippet = ko.observable("");
    self.completers = ko.observableArray([]);
    self.errors = ko.observableArray([]);
  }

  function AceViewModel() {
    var self = this;
    self.editors = ko.observableArray();
  }

  function addEditor() {
##    var snippy2 = new Snip("ace/mode/python");
##    snippy2.snippet("def nano:");
##    viewModel.editors.push(snippy2);
##    var snippy3 = new Snip("ace/mode/hivesql");
##    snippy3.snippet("SELECT * FROM sample_07");
##    viewModel.editors.push(snippy3);
    var snippy = new Snip("ace/mode/pig");
    snippy.snippet("A = LOAD ''");
    viewModel.editors.push(snippy);
  }

  var viewModel = new AceViewModel();
  ko.applyBindings(viewModel);
  addEditor();

  var extra = {
    getCompletions: function(editor, session, pos, prefix, callback) {
      callback(null, [
        {value: "sample_07", score: 1000, meta: "table"},
        {value: "code", score: 1000, meta: "column"},
        {value: "ud", score: 1000, meta: "column"}
      ]);
    }
  }


##
##  editor.completers.push({
##    getCompletions: function(editor, session, pos, prefix, callback) {
##      callback(null, [
##        {value: "default", score: 1000, meta: "database"},
##        {value: "sample_07", score: 1000, meta: "table"},
##        {value: "code", score: 1000, meta: "column"}
##      ]);
##    }
##  })
##
##          var snippetManager = ace.require("ace/snippets").snippetManager;
##        var config = ace.require("ace/config");
##
##      ace.config.loadModule("ace/snippets/python", function(m) {
##        if (m) {
##          snippetManager.files.python = m;
##          m.snippets = snippetManager.parseSnippetFile(m.snippetText);
##
##          // or do this if you already have them parsed
##          m.snippets.push({
##            content: "SELECT * FROM sample_07",
##            name: "SELECT * FROM sample_07",
##            tabTrigger: "sel07"
##          });
##          m.snippets.push({
##            content: "SELECT * FROM sample_08",
##            name: "SELECT * FROM sample_08",
##            tabTrigger: "sel08"
##          });
##          snippetManager.register(m.snippets, m.scope);
##          }
##        });
##
##


</script>


${commonfooter(messages) | n,unicode}
