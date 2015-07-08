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
  <div class="editor" data-bind="attr: {id: UUID()}, aceEditor: {value: snippet, aceInstance: ace, mode: mode, onChange: onChangeHandler, onAfterExec: onAfterExecHandler, extraCompleters: completers, errors: errors }">
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

<script src="${ static('spark/js/ace.autocomplete.js') }" type="text/javascript" charset="utf-8"></script>

<script>


  var AceAutocomplete = new Autocomplete({
   autocompleteBaseURL: "/beeswax/api/autocomplete/",
   autocompleteApp: "beeswax",
   autocompleteUser: "hue",
   autocompleteFailsQuietlyOn: [500] // error codes from beeswax/views.py - autocomplete
  });

  var DEFAULT_DB = "default";

  function newCompleter(items) {
    return {
      getCompletions: function(editor, session, pos, prefix, callback) {
        callback(null, items);
      }
    }
  }

  function fieldsAutocomplete(editor, valueAccessor) {
    try {
      var _before = editor.getTextBeforeCursor(";");
      var _after = editor.getTextAfterCursor(";");
      var _statement = _before + _after;
      var _foundTable = "";
      if (_before.substr(-1) == "."){ // gets the table alias
        _foundTable = _before.split(" ").pop().slice(0, -1);
      }
      else { // gets the standard table
        var _from = _statement.toUpperCase().indexOf("FROM");
        if (_from > -1) {
          var _match = _statement.toUpperCase().substring(_from).match(/ ON| LIMIT| WHERE| GROUP| SORT| ORDER BY|;/);
          var _to = _statement.length;
          if (_match) {
            _to = _match.index;
          }
          var _found = _statement.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
        }

        for (var i = 0; i < _found.length; i++) {
          if ($.trim(_found[i]) != "" && _foundTable == "") {
            _foundTable = $.trim(_found[i]).split(" ")[0];
          }
        }
      }

      if (_foundTable != "") {
          editor.showSpinner();
          // fill up with fields
          AceAutocomplete.getTableColumns(DEFAULT_DB, _foundTable, _statement, function(data){
            var _fieldNames = data.split(" ");
            var _fields = [];
            _fieldNames.forEach(function(fld){
              _fields.push({value: fld, score: (fld == "*") ? 1001: 1000, meta: "column"});
            });
            valueAccessor().extraCompleters([newCompleter(_fields)]);
            editor.hideSpinner();
          });
      }
    }
    catch (e) {
    }
  }

  function onAfterExecHandler(e, editor, valueAccessor) {
    editor.session.getMode().$id = valueAccessor().mode(); // forces the id again because of Ace command internals
    if ((editor.session.getMode().$id == "ace/mode/hivesql" || editor.session.getMode().$id == "ace/mode/impalasql") && e.args == "."){
      fieldsAutocomplete(editor, valueAccessor);
    }
        // if it's pig and before it's LOAD ' we disable the autocomplete and show a filechooser btn
    if (editor.session.getMode().$id = "ace/mode/pig" && e.args) {
      var _textBefore = editor.getTextBeforeCursor();
      if ((e.args == "'" && _textBefore.toUpperCase().indexOf("LOAD ") > -1 && _textBefore.toUpperCase().indexOf("LOAD ") == _textBefore.toUpperCase().length - 5)
          || _textBefore.toUpperCase().indexOf("LOAD '") > -1 && _textBefore.toUpperCase().indexOf("LOAD '") == _textBefore.toUpperCase().length - 6){
        editor.disableAutocomplete();
        var _btn = editor.showFileButton();
        _btn.on("click", function(ie){
          ie.preventDefault();
          if ($(".filechooser-content").data("spinner") == null){
            $(".filechooser-content").data("spinner", $(".filechooser-content").html());
          }
          else {
            $(".filechooser-content").html($(".filechooser-content").data("spinner"));
          }
          $(".filechooser-content").jHueFileChooser({
            onFileChoose: function (filePath) {
              editor.session.insert(editor.getCursorPosition(), filePath + "'");
              editor.hideFileButton();
              editor.enableAutocomplete();
              $(".filechooser").hide();
            },
            selectFolder: false,
            createFolder: false
          });
          $(".filechooser").css({ "top": $(ie.currentTarget).position().top, "left": $(ie.currentTarget).position().left}).show();
        });
      }
      else {
        editor.hideFileButton();
        editor.enableAutocomplete();
      }
      if (e.args != "'" && _textBefore.toUpperCase().indexOf("LOAD '") > -1 && _textBefore.toUpperCase().indexOf("LOAD '") == _textBefore.toUpperCase().length - 6) {
        editor.hideFileButton();
        editor.enableAutocomplete();
      }
    }

  }


  function onChangeHandler(event, editor, valueAccessor) {
    valueAccessor().extraCompleters([]);
    editor.session.getMode().$id = valueAccessor().mode();

    var _before = editor.getTextBeforeCursor(";");
    var _beforeU = _before.toUpperCase();
    var _after = editor.getTextAfterCursor(";");
    var _afterU = _after.toUpperCase();
    if (editor.session.getMode().$id == "ace/mode/hivesql" || editor.session.getMode().$id == "ace/mode/impalasql") {
      if ($.trim(_before).substr(-1) != ".") {
        if ((_beforeU.indexOf(" FROM ") > -1 || _beforeU.indexOf(" TABLE ") > -1 || _beforeU.indexOf(" STATS ") > -1) && _beforeU.indexOf(" ON ") == -1 && _beforeU.indexOf(" ORDER BY ") == -1 && _beforeU.indexOf(" WHERE ") == -1 ||
            _beforeU.indexOf("REFRESH") > -1 || _beforeU.indexOf("METADATA") > -1 || _beforeU.indexOf("DESCRIBE") > -1) {
          editor.showSpinner();
          valueAccessor().extraCompleters([]);
          AceAutocomplete.getTables(DEFAULT_DB, function (data) {
            var _tableNames = data.split(" ");
            var _tables = [];
            _tableNames.forEach(function (tbl) {
              _tables.push({value: tbl, score: 1000, meta: "table"});
            });
            valueAccessor().extraCompleters([newCompleter(_tables)]);
            editor.hideSpinner();
          });
        }
        if (_beforeU.indexOf("SELECT ") > -1 && _beforeU.indexOf(" FROM ") == -1) { //  && !CodeMirror.fromDot
          if (_afterU.indexOf("FROM ") > -1) {
            fieldsAutocomplete(editor, valueAccessor);
          }
          else {
            console.log("table magic")
          }
        }
        else {
          if ((_beforeU.indexOf("WHERE") > -1 || _beforeU.indexOf("ORDER BY") > -1) && _beforeU.match(/ ON| LIMIT| GROUP| SORT/) == null) {
            fieldsAutocomplete(editor, valueAccessor);
          }
          else {
            console.log("do other stuff")
          }
        }
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
    var snippy3 = new Snip("ace/mode/hivesql");
    snippy3.snippet("SELECT * FROM sample_07 sa, web_logs w");
    viewModel.editors.push(snippy3);
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
