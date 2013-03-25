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
          <div class="span12">
            <div id="toolbar"></div>
            <div id="content-editor" class="clear" style="margin-top: 20px">${ hue_core.result.get_template() | n,unicode }</div>
            <div id="load-template" class="btn-group">
              <a title="Load template" class="btn toolbar-btn toolbar-cmd">
                <i class="icon-paste" style="margin-top:2px;"></i>
              </a>
            </div>

            <div class="well available-fields" style="margin-top: 60px">
              <h4>${_('Available Fields')}</h4>
              <span data-bind="foreach: availableFields" class="field-button">
                  <a title="${ _('Click on this button to add the field') }"  style="margin-bottom:10px" class="btn btn-small" data-bind="click: $root.addFieldToVisual">
                    <i class="icon-plus"></i>
                    &nbsp;
                    <span data-bind="text: $data"></span>
                  </a>
                  &nbsp;
                </span>
            </div>
          </div>
        </div>

      </div>
      <div class="tab-pane" id="source">
        <div class="row-fluid">
          <div class="span12">
            <textarea id="template-source"></textarea>
            <div class="well available-fields" style="margin-top: 40px">
              <h4>${_('Available Fields')}</h4>
              <span data-bind="foreach: availableFields" class="field-button">
                  <a title="${ _('Click on this button to add the field') }"  style="margin-bottom:10px" class="btn btn-small" data-bind="click: $root.addFieldToSource">
                    <i class="icon-plus"></i>
                    &nbsp;
                    <span data-bind="text: $data"></span>
                  </a>
                  &nbsp;
                </span>
            </div>
          </div>
        </div>

      </div>

      <div class="tab-pane" id="preview">
        <div id="preview-container"></div>
      </div>
    </div>

    <div class="form-actions">
      <a class="btn btn-primary" id="save-template">${_('Save')}</a>
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

    $("#content-editor").on("mouseup", function () {
      storeSelection();
    });

    $("#content-editor").on("keyup", function () {
      storeSelection();
    });

    function storeSelection() {
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          range = sel.getRangeAt(0);
          $('#content-editor').data("range", range);
        }
      }
      else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        $('#content-editor').data("selection", document.selection);
      }
    }

    function pasteHtmlAtCaret(html) {
      var sel, range;
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          if ($('#content-editor').data("range")) {
            range = $('#content-editor').data("range");
          }
          else {
            range = sel.getRangeAt(0);
          }
          range.deleteContents();

          // Range.createContextualFragment() would be useful here but is
          // non-standard and not supported in all browsers (IE9, for one)
          var el = document.createElement("div");
          el.innerHTML = html;
          var frag = document.createDocumentFragment(), node, lastNode;
          while ((node = el.firstChild)) {
            lastNode = frag.appendChild(node);
          }
          range.insertNode(frag);

          // Preserve the selection
          if (lastNode) {
            range = range.cloneRange();
            range.setStartAfter(lastNode);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      } else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        if ($('#content-editor').data("selection")) {
          $('#content-editor').data("selection").createRange().pasteHTML(html);
        }
        else {
          document.selection.createRange().pasteHTML(html);
        }
      }
    }

    function ViewModel() {
      var self = this;
      self.availableFields = ko.observableArray(${ hue_core.fields | n,unicode });
      self.lastIndex = ko.observable(0);
      self.addFieldToVisual = function (field) {
        $("#content-editor").focus();
        pasteHtmlAtCaret("{{" + field + "}}");
      };
      self.addFieldToSource = function (field) {
        codeMirror.replaceSelection("{{" + field + "}}")
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
