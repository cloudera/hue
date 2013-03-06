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

<%namespace name="layout" file="layout.mako" />
<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }

<style type="text/css">
  .preview-row:nth-child(odd) {
    background-color:#f9f9f9;
  }
  .tmpl {
    border: 1px solid #CCC;
    margin: 10px;
    height: 80px;
    cursor: pointer;
  }
  .tmpl:hover {
    border: 1px solid #999;
  }
  .tmpl.selected {
    border: 2px solid #999;
  }
  .space {
    display: block;
    font-size: 6px;
    height: 6px;
    line-height: 6px;
  }
</style>

<%layout:skeleton>
  <%def name="title()">
    <h1>${ _('Template Editor ') } : ${ hue_core.name }</h1>
  </%def>

  <%def name="navigation()">
    ${ layout.sidebar(hue_core.name, 'template') }
  </%def>

  <%def name="content()">
    <ul class="nav nav-tabs">
      <li class="active"><a href="#visual" data-toggle="tab">${_('Visual editor')}</a></li>
      <li><a href="#source" data-toggle="tab">${_('Source')}</a></li>
      <li><a href="#preview" data-toggle="tab">${_('Preview')}</a></li>
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="visual">

        <div class="row-fluid">
          <div class="span9">
            <div id="toolbar"></div>
            <div id="content-editor" class="clear">${ hue_core.result.get_template() | n,unicode }</div>
            <div id="load-template" class="btn-group">
              <a title="Load template" class="btn toolbar-btn toolbar-cmd">
                <i class="icon-paste" style="margin-top:2px;"></i>
              </a>
            </div>
          </div>

          <div class="span3">
            <div class="well available-fields">
              <h4>${_('Available Fields')}</h4>
              <ul data-bind="foreach: fields">
                <li class="field-button">
                  <a title="${ _('Click on this button to add the field') }" class="btn" data-bind="click: $root.addField">
                    <i class="icon-plus"></i>
                    &nbsp;
                    <span data-bind="text: $data"></span>
                  </a>
                  <span class="space">&nbsp;</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

      </div>
      <div class="tab-pane" id="source">
        <div class="row-fluid">
          <div class="span9">
            <textarea id="template-source"></textarea>
          </div>

          <div class="span3">
            <div class="well available-fields">
              <h4>${_('Available Fields')}</h4>
              <ul data-bind="foreach: fields">
                <li data-bind="text: $data, click: $root.addField"></li>
              </ul>
            </div>
          </div>
        </div>

      </div>

      <div class="tab-pane" id="preview">
        <div id="preview-container"></div>
      </div>
    </div>

    <div class="form-actions">
      <a class="btn" id="save-template">${_('Save')}</a>
      <a class="btn btn-primary" id="save-template">${_('Save and next')}</a>
    </div>

    <div id="load-template-modal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h3>${_('Load template')}</h3>
      </div>
      <div class="modal-body">
        <div class="tmpl">
          <div class="row-fluid">
            <div class="span1"><img src="http://twitter.com/api/users/profile_image/{{user_screen_name}}" style="margin:20px"></div>
            <div class="span9">
              <h5>{{user_name}}</h5>
              {{text}}
            </div>
            <div class="span2"><br><a class="btn" href="https://twitter.com/{{user_screen_name}}/status/{{id}}" target="_blank"><i class="icon-twitter"></i></a></div>
          </div>
        </div>
        <div class="tmpl">
          <h5>{{user_name}} <span style="color:#999">({{user_screen_name}})</span></h5>
          <p>{{text}}</p>
        </div>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <button type="button" id="load-template-btn" href="#" class="btn btn-primary" disabled="disabled">${_('Load template')}</button>
      </div>
    </div>


  </%def>
</%layout:skeleton>

<link rel="stylesheet" href="/static/ext/farbtastic/farbtastic.css">
<link rel="stylesheet" href="/static/ext/css/freshereditor.css">
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/farbtastic/farbtastic.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/shortcut.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/freshereditor.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.0.js"></script>
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<script src="/static/ext/js/codemirror-xml.js"></script>
<script src="/static/ext/js/mustache.js"></script>


<script type="text/javascript">
  $(document).ready(function () {
    function ViewModel() {
      var self = this;
      self.fields = ko.observableArray(${ hue_core.fields | n,unicode });
      self.lastIndex = ko.observable(0);

      setInterval(function() {
        var contentEditor = $('#content-editor');
        var range = window.getSelection().getRangeAt(0);
        if (range.startContainer && ( contentEditor.is(range.startContainer) || contentEditor.has(range.startContainer).length )) {
          // Use DOM methods instead of JQuery methods to interpret Text Nodes.
          // Node Type '3' is a text node.
          if (range.startContainer.nodeType == 3) {
            // Assuming 'content-editor' is parent.
            for (var i = 0; i < contentEditor[0].childNodes.length; ++i) {
              if (contentEditor[0].childNodes[i] == range.startContainer) {
                self.lastIndex(i);
                break;
              }
            }
          } else {
            // Start offset with respect to parent container.
            // Assuming this is 'content-editor'
            self.lastIndex(range.startOffset);
          }
        }
      }, 100);

      self.addField = function (field) {
        // Use DOM methods instead of JQuery methods to interpret Text Nodes.
        var contentEditor = $("#content-editor")[0];
        if (self.lastIndex() > contentEditor.childNodes.length || self.lastIndex() < 0) {
          self.lastIndex() = contentEditor.childNodes.length - 1;
        }
        var text = document.createTextNode("{{" + field + "}}");
        if (contentEditor.childNodes.length) {
          contentEditor.insertBefore(text, contentEditor.childNodes[self.lastIndex()]);
        } else {
          contentEditor.appendChild(text);
        }
      };
    };

    ko.applyBindings(new ViewModel());

    var samples = ${ sample_data | n,unicode };
    var templateEditor = $("#template-source")[0];

    var codeMirror = CodeMirror(function (elt) {
        templateEditor.parentNode.replaceChild(elt, templateEditor);
      }, {
        value: templateEditor.value,
        readOnly: false,
        lineNumbers: true
    });

    $("#content-editor").freshereditor({
        toolbar_selector: "#toolbar",
        excludes: ['strikethrough', 'removeFormat', 'backcolor', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
    });
    $("#content-editor").freshereditor("edit", true);

    // Force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#source") {
        codeMirror.setValue($("#content-editor").html());
        codeMirror.refresh();
      }
      if ($(e.target).attr("href") == "#preview") {
        $("#preview-container").empty();
        $(samples).each(function (cnt, item) {
          $("<div>").addClass("preview-row").html(Mustache.render($("#content-editor").html(), item)).appendTo($("#preview-container"));
        });
      }
    });

    var delay = -1;
    codeMirror.on("change", function () {
      clearTimeout(delay);
      delay = setTimeout(function () {
        $("#content-editor").html(codeMirror.getValue());
      }, 300);
    });

    $("#load-template").appendTo($("#toolbar .btn-toolbar")).removeClass("hide");

    $("#load-template-modal").modal({
      show: false
    });

    $("#load-template .btn").click(function(){
      $(".tmpl.selected").removeClass("selected");
      $("#load-template-modal").modal("show");
      $("#load-template-btn").attr("disabled", "disabled");
    });

    $(".tmpl").click(function(){
      $(".tmpl.selected").removeClass("selected");
      $(this).addClass("selected");
      $("#load-template-btn").removeAttr("disabled");
    });

    $("#load-template-btn").click(function(){
      $("#load-template-modal").modal("hide");
      $("#content-editor").html($(".tmpl.selected").html());
    });


    $("#save-template").click(function () {
      $.ajax("${ url('search:admin_core_template', core=hue_core.name) }", {
        data: {
          'template': ko.utils.stringifyJson($("#content-editor").html()),
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $.jHueNotify.info("${_('Template updated')}");
        },
        error: function (data) {
          $.jHueNotify.error("${_('Error: ')}" + data);
        },
        complete: function() {
          $("#save-template").button('reset');
        }
      });
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
