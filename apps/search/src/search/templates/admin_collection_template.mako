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

${ commonheader(_('Search'), "search", user, "29px") | n,unicode }

<style type="text/css">
  .CodeMirror {
    border: 1px dotted #DDDDDD;
  }

  #content-editor {
    outline: 0;
    margin-top: 20px;
    min-height: 400px;
  }

  #content-editor [class*="span"], .tmpl [class*="span"] {
    background-color: #eee;
    -webkit-border-radius: 3px;
    -moz-border-radius: 3px;
    border-radius: 3px;
    min-height: 40px;
    line-height: 40px;
    background-color: #F3F3F3;
    border: 2px dashed #DDD;
  }

  .tmpl {
    margin: 10px;
    height: 60px;
  }

  .tmpl [class*="span"] {
    color: #999;
    font-size: 12px;
    text-align: center;
    font-weight: bold;
  }

  .preview-row:nth-child(odd) {
    background-color: #f9f9f9;
  }

  .widget-box {
    background: none repeat scroll 0 0 #F9F9F9;
    border-top: 1px solid #CDCDCD;
    border-left: 1px solid #CDCDCD;
    border-right: 1px solid #CDCDCD;
    clear: both;
    margin-top: 10px;
    margin-bottom: 16px;
    position: relative;
    min-width: 260px;
  }

  .widget-title {
    background-color: #efefef;
    background-image: -webkit-gradient(linear, 0 0%, 0 100%, from(#fdfdfd), to(#eaeaea));
    background-image: -webkit-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -moz-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -ms-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -o-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#fdfdfd', endColorstr='#eaeaea', GradientType=0); /* IE6-9 */
    border-bottom: 1px solid #CDCDCD;
    height: 36px;
  }

  .widget-title span.icon {
    border-right: 1px solid #cdcdcd;
    padding: 9px 10px 7px 11px;
    float: left;
    opacity: .7;
  }

  .widget-title h5 {
    color: #666666;
    text-shadow: 0 1px 0 #ffffff;
    float: left;
    font-size: 12px;
    font-weight: bold;
    padding: 12px;
    line-height: 12px;
    margin: 0;
  }

  .widget-content {
    padding: 12px 8px;
    border-bottom: 1px solid #cdcdcd;
  }

  .carousel-control {
    top: 100%;
    outline: none;
  }
  .carousel-control:focus {
    outline: none;
  }

  .tab-content {
    overflow: inherit;
  }

  .chosen-container, .chosen-select {
    float: left;
  }

  .plus-btn {
    float: left;
    height: 25px;
    line-height: 15px!important;
    margin-left: 4px;
    min-height: 25px;
  }
</style>

<%layout:skeleton>
  <%def name="title()">
    <h4>${ _('Snippet editor for') } <strong>${ hue_collection.name }</strong></h4>
  </%def>

  <%def name="navigation()">
    ${ layout.sidebar(hue_collection, 'template') }
  </%def>

  <%def name="content()">
    <ul class="nav nav-tabs" style="margin-bottom:0; margin-top:10px">
      <li class="active"><a href="#visual" data-toggle="tab">${_('Visual Editor')}</a></li>
      <li><a href="#preview" data-toggle="tab">${_('Preview')}</a></li>
      <li><a href="#source" data-toggle="tab">${_('Source')}</a></li>
      <li><a href="#extra" data-toggle="tab">${_('Advanced')}</a></li>
    </ul>
    <div class="well">
    <div class="tab-content">
      <div class="tab-pane active" id="visual">
        <div class="row-fluid">
          <div class="span9">
            <div id="toolbar"></div>
            <div id="content-editor" class="clear">${ hue_collection.result.get_template() | n,unicode }</div>
            <div id="cloud-template" class="btn-group">
              <a title="${_('Cloud Template')}" class="btn toolbar-btn toolbar-cmd">
                <i class="fa fa-cloud-download" style="margin-top:2px;"></i>
              </a>
            </div>
            <div id="load-template" class="btn-group">
              <a title="${_('Layout')}" class="btn toolbar-btn toolbar-cmd">
                <i class="fa fa-th-large" style="margin-top:2px;"></i>
              </a>
            </div>
          </div>
          <div class="span3">
            <div class="card card-home">
              <h2 class="card-heading simple">${_('Available Fields')}</h2>
              <div class="card-body">
                <p>
                  <select data-bind="options: availableFields, value: selectedVisualField" class="input-large chosen-select"></select>
                  <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.addFieldToVisual">
                    <i class="fa fa-plus"></i>
                  </button>
                  <div class="clearfix"></div>
                </p>
              </div>
            </div>
            <div class="card card-home">
              <h2 class="card-heading simple">${_('Available Functions')}</h2>
              <div class="card-body">
                <select id="visualFunctions" data-bind="value: selectedVisualFunction" class="input-large chosen-select">
                  <option title="${ _('Formats date or timestamp in DD-MM-YYYY') }" value="{{#date}} {{/date}}">{{#date}}</option>
                  <option title="${ _('Formats date or timestamp in HH:mm:ss') }" value="{{#time}} {{/time}}">{{#time}}</option>
                  <option title="${ _('Formats date or timestamp in DD-MM-YYYY HH:mm:ss') }" value="{{#datetime}} {{/datetime}}">{{#datetime}}</option>
                  <option title="${ _('Formats a date in the full format') }" value="{{#fulldate}} {{/fulldate}}">{{#fulldate}}</option>
                  <option title="${ _('Formats a date as a Unix timestamp') }" value="{{#timestamp}} {{/timestamp}}">{{#timestamp}}</option>
                  <option title="${ _('Formats a Unix timestamp as Ns, Nmin, Ndays... ago') }" value="{{#fromnow}} {{/fromnow}}">{{#fromnow}}</option>
                  <option title="${ _('Downloads and embed the file in the browser') }" value="{{#embeddeddownload}} {{/embeddeddownload}}">{{#embeddeddownload}}</option>
                  <option title="${ _('Downloads the linked file') }" value="{{#download}} {{/download}}">{{#download}}</option>
                  <option title="${ _('Preview file in File Browser') }" value="{{#preview}} {{/preview}}">{{#preview}}</option>
                  <option title="${ _('Truncate a value after 100 characters') }" value="{{#truncate100}} {{/truncate100}}">{{#truncate100}}</option>
                  <option title="${ _('Truncate a value after 250 characters') }" value="{{#truncate250}} {{/truncate250}}">{{#truncate250}}</option>
                  <option title="${ _('Truncate a value after 500 characters') }" value="{{#truncate500}} {{/truncate500}}">{{#truncate500}}</option>
                </select>
                <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.addFunctionToVisual">
                  <i class="fa fa-plus"></i>
                </button>
                <div class="clearfix"></div>
                <p class="muted" style="margin-top: 10px"></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tab-pane" id="source">
        <div class="row-fluid">
          <div class="span9" style="padding-top: 10px">
            <textarea id="template-source"></textarea>
          </div>
          <div class="span3">
            <div class="card card-home">
              <h2 class="card-heading simple">${_('Available Fields')}</h2>
              <div class="card-body">
                <p>
                  <select data-bind="options: availableFields, value: selectedSourceField" class="input-medium chosen-select"></select>
                  <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.addFieldToSource">
                    <i class="fa fa-plus"></i>
                  </button>
                  <div class="clearfix"></div>
                </p>
              </div>
            </div>
            <div class="card card-home">
              <h2 class="card-heading simple">${_('Available Functions')}</h2>
              <div class="card-body">
                <select id="sourceFunctions" data-bind="value: selectedSourceFunction" class="input-medium chosen-select">
                  <option title="${ _('Formats a date in the DD-MM-YYYY format') }" value="{{#date}} {{/date}}">{{#date}}</option>
                  <option title="${ _('Formats a date in the HH:mm:ss format') }" value="{{#time}} {{/time}}">{{#time}}</option>
                  <option title="${ _('Formats a date in the DD-MM-YYYY HH:mm:ss format') }" value="{{#datetime}} {{/datetime}}">{{#datetime}}</option>
                  <option title="${ _('Formats a date in the full format') }" value="{{#fulldate}} {{/fulldate}}">{{#fulldate}}</option>
                  <option title="${ _('Formats a date as a Unix timestamp') }" value="{{#timestamp}} {{/timestamp}}">{{#timestamp}}</option>
                  <option title="${ _('Shows the relative time') }" value="{{#fromnow}} {{/fromnow}}">{{#fromnow}}</option>
                  <option title="${ _('Downloads and embed the file in the browser') }" value="{{#embeddeddownload}} {{/embeddeddownload}}">{{#embeddeddownload}}</option>
                  <option title="${ _('Downloads the linked file') }" value="{{#download}} {{/download}}">{{#download}}</option>
                  <option title="${ _('Preview file in File Browser') }" value="{{#preview}} {{/preview}}">{{#preview}}</option>
                  <option title="${ _('Truncate a value after 100 characters') }" value="{{#truncate100}} {{/truncate100}}">{{#truncate100}}</option>
                  <option title="${ _('Truncate a value after 250 characters') }" value="{{#truncate250}} {{/truncate250}}">{{#truncate250}}</option>
                  <option title="${ _('Truncate a value after 500 characters') }" value="{{#truncate500}} {{/truncate500}}">{{#truncate500}}</option>
                </select>
                <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.addFunctionToSource">
                  <i class="fa fa-plus"></i>
                </button>
                <div class="clearfix"></div>
                <p class="muted" style="margin-top: 10px"></p>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="tab-pane" id="preview">
        <div id="preview-container"></div>
      </div>

      <div class="tab-pane" id="extra">
        <div class="row-fluid">
          <div class="span12">
            <span class="muted"> ${ _('Here you can define custom CSS classes or Javascript functions that you can use in your template.') }</span><br/><br/>
            <textarea id="template-extra">${ hue_collection.result.get_extracode() | n,unicode }</textarea>
          </div>
        </div>

      </div>
    </div>

    <div class="form-actions">
      <a class="btn btn-primary" id="save-template">${_('Save')}</a>
    </div>

    <div id="load-template-modal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h3>${_('Insert layout')}</h3>
      </div>
      <div class="modal-body">
        <div id="layoutCarousel" class="carousel slide">
          <div class="carousel-inner">
            <div class="item active">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span12">12</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span1">1</div>
                  <div class="span11">11</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span2">2</div>
                  <div class="span10">10</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span3">3</div>
                  <div class="span9">9</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span4">4</div>
                  <div class="span8">8</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span6">6</div>
                  <div class="span6">6</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span4">4</div>
                  <div class="span4">4</div>
                  <div class="span4">4</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span3">3</div>
                  <div class="span3">3</div>
                  <div class="span3">3</div>
                  <div class="span3">3</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span8">8</div>
                  <div class="span4">4</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span9">9</div>
                  <div class="span3">3</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span10">10</div>
                  <div class="span2">2</div>
                </div>
              </div>
            </div>
            <div class="item">
              <div class="tmpl">
                <div class="row-fluid">
                  <div class="span11">11</div>
                  <div class="span1">1</div>
                </div>
              </div>
            </div>
          </div>
          <a class="left carousel-control" href="#layoutCarousel" data-slide="prev">&laquo;</a>
          <a class="right carousel-control" href="#layoutCarousel" data-slide="next">&raquo;</a>
        </div>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <button type="button" id="load-template-btn" href="#" class="btn btn-primary" disabled="disabled">${_('Insert layout')}</button>
      </div>
    </div>

    <div id="cloud-template-modal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h3>${_('Load a template')}</h3>
      </div>
      <div class="modal-body">
        <div id="cloud-loader" style="text-align: center">
          <img src="/static/art/spinner.gif" />
        </div>
      </div>
      <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <button type="button" id="cloud-template-btn" href="#" class="btn btn-primary" disabled="disabled">${_('Load template')}</button>
      </div>
    </div>
    </div>
  </%def>
</%layout:skeleton>

<span id="extraCode">
  ${ hue_collection.result.get_extracode() | n,unicode }
</span>

<link rel="stylesheet" href="/static/css/freshereditor.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/shortcut.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/freshereditor.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-xml.js"></script>
<script src="/static/ext/js/mustache.js"></script>
<script src="/search/static/js/search.utils.js"></script>

<script type="text/javascript">

  $(document).ready(function () {
    $("#layoutCarousel").carousel("pause");

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
      self.availableFields = ko.observableArray(${ hue_collection.fields(user) | n,unicode });
      self.selectedVisualField = ko.observable();
      self.selectedVisualFunction = ko.observable();
      self.selectedVisualFunction.subscribe(function (newValue) {
        var _vf = $("#visualFunctions");
        _vf.siblings(".muted").text(_vf.find(":selected").attr("title"));
      });
      self.selectedSourceField = ko.observable();
      self.selectedSourceFunction = ko.observable();
      self.selectedSourceFunction.subscribe(function (newValue) {
        var _sf = $("#sourceFunctions");
        _sf.siblings(".muted").text(_sf.find(":selected").attr("title"));
      });
      self.lastIndex = ko.observable(0);
      self.addFieldToVisual = function () {
        $("#content-editor").focus();
        pasteHtmlAtCaret("{{" + self.selectedVisualField() + "}}");
      };
      self.addFieldToSource = function () {
        templateSourceMirror.replaceSelection("{{" + self.selectedSourceField() + "}}");
      };
      self.addFunctionToVisual = function () {
        $("#content-editor").focus();
        pasteHtmlAtCaret(self.selectedVisualFunction());
      };
      self.addFunctionToSource = function () {
        templateSourceMirror.replaceSelection(self.selectedSourceFunction());
      };
    };

    var viewModel = new ViewModel();
    ko.applyBindings(viewModel);
    $(".chosen-select").chosen({width: "75%"});

    var samples = ${ sample_data | n,unicode };
    var templateSourceEl = $("#template-source")[0];
    var templateSourceMirror = CodeMirror(function (elt) {
      templateSourceEl.parentNode.replaceChild(elt, templateSourceEl);
    }, {
      value: templateSourceEl.value,
      readOnly: false,
      lineNumbers: true
    });

    var templateExtraEl = $("#template-extra")[0];
    var templateExtraMirror = CodeMirror(function (elt) {
      templateExtraEl.parentNode.replaceChild(elt, templateExtraEl);
    }, {
      value: templateExtraEl.value,
      readOnly: false,
      lineNumbers: true
    });

    $("#content-editor").freshereditor({
      toolbar_selector: "#toolbar",
      excludes: ['strikethrough', 'removeFormat', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
    });
    $("#content-editor").freshereditor("edit", true);

    // Force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#source") {
        templateSourceMirror.setValue(stripHtmlFromFunctions($("#content-editor").html()));
        templateSourceMirror.setSize("100%", 450);
        window.setTimeout(function(){
          for (var i = 0; i < templateSourceMirror.lineCount(); i++) {
            templateSourceMirror.indentLine(i);
          }
        }, 100);

        templateSourceMirror.refresh();
      }
      if ($(e.target).attr("href") == "#extra") {
        templateExtraMirror.setSize("100%", 420);
        templateExtraMirror.refresh();
      }
      if ($(e.target).attr("href") == "#preview") {
        $("#preview-container").empty();
        var _mustacheTmpl = fixTemplateDotsAndFunctionNames($("#content-editor").html());
        $(samples).each(function (cnt, item) {
          addTemplateFunctions(item);
          $("<div>").addClass("preview-row").html(Mustache.render(_mustacheTmpl, item)).appendTo($("#preview-container"));
        });
      }
    });

    var sourceDelay = -1;
    templateSourceMirror.on("change", function () {
      clearTimeout(sourceDelay);
      sourceDelay = setTimeout(function () {
        $("#content-editor").html(stripHtmlFromFunctions(templateSourceMirror.getValue()));
      }, 300);
    });

    var extraDelay = -1;
    templateExtraMirror.on("change", function () {
      clearTimeout(extraDelay);
      extraDelay = setTimeout(function () {
        $("#extraCode").html($.parseHTML(templateExtraMirror.getValue()));
      }, 300);
    });

    $("#load-template").prependTo($("#toolbar .btn-toolbar")).removeClass("hide");
    $("#cloud-template").prependTo($("#toolbar .btn-toolbar")).removeClass("hide");

    $("#load-template-modal").modal({
      show: false
    });

    $("#cloud-template-modal").modal({
      show: false
    });

    $("#load-template .btn").on("hover", function () {
      $("#load-template").popover("hide");
    });

    $("#load-template .btn").click(function () {
      $("#load-template-btn").button("reset");
      $("#load-template").popover("hide");
      $("#load-template-modal").modal("show");
    });

    $("#cloud-template .btn").click(function () {
      $("#cloud-loader").show();
      $(".cloud-tmpl").remove();
      $("#load-template").popover("hide");
      $("#cloud-template-modal").modal("show");
      $.get("/search/static/templates/templates.xml", function (xml) {
        var $xml = $(xml);
        $.each($xml.find("template"), function () {
          var _this = $(this);
          var _tmpl = $("<div>");
          _tmpl.addClass("cloud-tmpl").html("<h4>" + _this.find("title").text() + "</h4><img src='" + _this.find("img").text() + "'/>");
          _tmpl.data("source", _this.find("source").text());
          _tmpl.data("additional", _this.find("additional").text());
          _tmpl.appendTo("#cloud-template-modal .modal-body");
          _tmpl.on("click", function () {
            $(".cloud-tmpl").removeClass("selected");
            $(this).addClass("selected");
            $("#cloud-template-btn").button("reset");
          });
        });
        $("#cloud-loader").hide();
      });
    });

    $("#cloud-template-btn").on("click", function () {
      templateSourceMirror.setValue($(".cloud-tmpl.selected").data("source"));
      $("#content-editor").html(stripHtmlFromFunctions(templateSourceMirror.getValue()));
      templateExtraMirror.setValue($(".cloud-tmpl.selected").data("additional"));
      $("#cloud-template-modal").modal("hide");
    });

    if ($("#content-editor").text().trim() == "") {
      $("#load-template").popover({
        placement: "bottom",
        title: "${ _('Start with this!') }",
        content: "${ _('You can add a layout from here') }"
      });
      $("#load-template").popover("show");
    }

    $("#load-template-btn").click(function () {
      $("#load-template-modal").modal("hide");
      $("#content-editor").focus();
      var _clone = $("#layoutCarousel .item.active .tmpl").clone();
      _clone.find("[class*='span']").text("");
      pasteHtmlAtCaret(_clone.html());
    });

    $("body").click(function () {
      $("#load-template").popover("hide");
    });

    $("#save-template").click(function () {
      $.ajax("${ url('search:admin_collection_template', collection_id=hue_collection.id) }", {
        data: {
          'template': ko.utils.stringifyJson($("#content-editor").html()),
          'extracode': ko.utils.stringifyJson(templateExtraMirror.getValue())
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $(document).trigger("info", "${_('Template updated')}");
        },
        error: function (data) {
          $(document).trigger("error", "${_('Error: ')}" + data);
        },
        complete: function () {
          $("#save-template").button('reset');
        }
      });
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
