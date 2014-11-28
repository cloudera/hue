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

<%namespace name="common" file="common.mako" />

${ commonheader(_('Query'), app_name, user) | n,unicode }

${ common.navbar('editor') }


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">

      <div class="card card-home">
        <div id="snippets"></div>

        <div class="question">
          ${ _('What would you like to type?') }
          <select id="codeMode">
            <option value="markdown">Markdown</option>
            <option value="text/x-impalaql">Impala</option>
            <option value="text/x-hiveql">Hive</option>
            <option value="text/x-pig">Pig</option>
          </select>
        </div>
        <textarea id="mainEditor"></textarea>
      </div>

    </div>
  </div>
</div>

<textarea id="tempEditor"></textarea>

<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<link rel="stylesheet" href="/spark/static/css/spark.css">

<script src="/static/ext/js/codemirror-3.11.js"></script>
<script src="/static/js/codemirror-pig.js"></script>
<script src="/static/js/codemirror-hql.js"></script>
<script src="/static/ext/js/codemirror-sql.js"></script>
<script src="/static/ext/js/codemirror-markdown.js"></script>
<script src="/static/ext/js/markdown.min.js"></script>

<script type="text/javascript" charset="utf-8">

  var mainCodeMirror, tempCodeMirror, tempCodeMirrorUpdateFn;


  $(document).ready(function(){

    $("#codeMode").on("change", function(){
      mainCodeMirror.setOption("mode", $("#codeMode").val());
    });

    function replaceWithEditor(snippet) {
      snippet.html("");
      snippet.off("click");
      $(tempCodeMirror.getWrapperElement()).appendTo(snippet);
      $(tempCodeMirror.getWrapperElement()).show();
      tempCodeMirror.setOption("mode", snippet.data("mode"));
      tempCodeMirror.setValue(snippet.data("source"))
      tempCodeMirror.setSize("100%", "50px");
      tempCodeMirrorUpdateFn = function(){
        var _source = tempCodeMirror.getValue();
        snippet.html(markdown.toHTML(_source)).data("source", _source);
        snippet.on("click", function(){
          replaceWithEditor($(this));
        });
      }
    }

    function addSnippet(value, mode) {
      var _snippet = $("<div>").addClass("snippet").html(markdown.toHTML(value)).appendTo($("#snippets")).data("source", value).data("mode", mode);
      _snippet.on("click", function(){
        replaceWithEditor($(this));
      });
      mainCodeMirror.setValue("");
    }

    var mainEditor = $("#mainEditor")[0];
    var tempEditor = $("#tempEditor")[0];

    mainCodeMirror = CodeMirror(function (elt) {
      mainEditor.parentNode.replaceChild(elt, mainEditor);
    }, {
      value: mainEditor.value,
      readOnly: false,
      lineNumbers: true,
      mode: "markdown",
      extraKeys: {
        "Ctrl-Enter": function () {
          addSnippet(mainCodeMirror.getValue(), mainCodeMirror.getOption("mode"));
        }
      },
      onKeyEvent: function (e, s) {
        if (s.type == "keyup") {
        }
      }
    });

    tempCodeMirror = CodeMirror(function (elt) {
      tempEditor.parentNode.replaceChild(elt, tempEditor);
    }, {
      value: tempEditor.value,
      readOnly: false,
      lineNumbers: true,
      mode: "markdown",
      extraKeys: {
        "Ctrl-Enter": function () {
          tempCodeMirrorUpdateFn();
        }
      },
      onKeyEvent: function (e, s) {
        if (s.type == "keyup") {
        }
      }
    });

    $(tempCodeMirror.getWrapperElement()).hide();

  });


</script>

${ commonfooter(messages) | n,unicode }
