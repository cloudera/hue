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
  .CodeMirror {
    border: 1px solid #CDCDCD;
  }

  #content-editor {
    outline: 0;
    border: 1px solid #CDCDCD;
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
    padding: 12px 15px;
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
      <li><a href="#extra" data-toggle="tab">${_('Advanced')}</a></li>
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="visual">

        <div class="row-fluid">
          <div class="span9">
            <div id="toolbar"></div>
            <div id="content-editor" class="clear" style="margin-top: 20px; min-height: 300px">${ hue_core.result.get_template() | n,unicode }</div>
            <div id="load-template" class="btn-group">
              <a title="Layout" class="btn toolbar-btn toolbar-cmd">
                <i class="icon-th-large" style="margin-top:2px;"></i>
              </a>
            </div>
          </div>
          <div class="span3">
            <div class="widget-box">
              <div class="widget-title">
								<span class="icon">
									<i class="icon-th-list"></i>
								</span>
                <h5>${_('Available Fields')}</h5>
              </div>
              <div class="widget-content">
                <select data-bind="options: availableFields, value: selectedVisualField" class="input-medium chzn-select"></select>
                <a title="${ _('Click on this button to add the field') }"  style="margin-top:-22px" class="btn btn-small" data-bind="click: $root.addFieldToVisual">
                  <i class="icon-plus"></i>
                </a>
              </div>
            </div>
            <div class="widget-box">
              <div class="widget-title">
								<span class="icon">
									<i class="icon-magic"></i>
								</span>
                <h5>${_('Available Functions')}</h5>
              </div>
              <div class="widget-content">
                <select id="visualFunctions" data-bind="value: selectedVisualFunction" class="input-medium chzn-select">
                  <option title="${ _('Formats a date in the DD-MM-YYYY format') }" value="{{#date}} {{/date}}">{{#date}}</option>
                  <option title="${ _('Formats a date in the HH:mm:ss format') }" value="{{#time}} {{/time}}">{{#time}}</option>
                  <option title="${ _('Formats a date in the DD-MM-YYYY HH:mm:ss format') }" value="{{#datetime}} {{/datetime}}">{{#datetime}}</option>
                  <option title="${ _('Formats a date in the full format') }" value="{{#fulldate}} {{/fulldate}}">{{#fulldate}}</option>
                  <option title="${ _('Formats a date as a Unix timestamp') }" value="{{#timestamp}} {{/timestamp}}">{{#timestamp}}</option>
                  <option title="${ _('Downloads the linked file') }" value="{{#downloadfile}} {{/downloadfile}}">{{#downloadfile}}</option>
                  <option title="${ _('Links to the file') }" value="{{#viewfile}} {{/viewfile}}">{{#viewfile}}</option>
                </select>
                <a title="${ _('Click on this button to add the field') }"  style="margin-top:-22px" class="btn btn-small" data-bind="click: $root.addFunctionToVisual">
                  <i class="icon-plus"></i>
                </a>
                <br/>
                <p class="muted"></p>
              </div>
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
            <div class="widget-box" style="margin-top: 0">
              <div class="widget-title">
								<span class="icon">
									<i class="icon-th-list"></i>
								</span>
                <h5>${_('Available Fields')}</h5>
              </div>
              <div class="widget-content">
                <select data-bind="options: availableFields, value: selectedSourceField" class="input-medium chzn-select"></select>
                <a title="${ _('Click on this button to add the field') }"  style="margin-top:-22px" class="btn btn-small" data-bind="click: $root.addFieldToSource">
                  <i class="icon-plus"></i>
                </a>
              </div>
            </div>
            <div class="widget-box">
              <div class="widget-title">
								<span class="icon">
									<i class="icon-magic"></i>
								</span>
                <h5>${_('Available Functions')}</h5>
              </div>
              <div class="widget-content">
                <select id="sourceFunctions" data-bind="value: selectedSourceFunction" class="input-medium chzn-select">
                  <option title="${ _('Formats a date in the DD-MM-YYYY format') }" value="{{#date}} {{/date}}">{{#date}}</option>
                  <option title="${ _('Formats a date in the HH:mm:ss format') }" value="{{#time}} {{/time}}">{{#time}}</option>
                  <option title="${ _('Formats a date in the DD-MM-YYYY HH:mm:ss format') }" value="{{#datetime}} {{/datetime}}">{{#datetime}}</option>
                  <option title="${ _('Formats a date in the full format') }" value="{{#fulldate}} {{/fulldate}}">{{#fulldate}}</option>
                  <option title="${ _('Formats a date as a Unix timestamp') }" value="{{#timestamp}} {{/timestamp}}">{{#timestamp}}</option>
                  <option title="${ _('Downloads the linked file') }" value="{{#downloadfile}} {{/downloadfile}}">{{#downloadfile}}</option>
                  <option title="${ _('Links to the file') }" value="{{#viewfile}} {{/viewfile}}">{{#viewfile}}</option>
                </select>
                <a title="${ _('Click on this button to add the field') }"  style="margin-top:-22px" class="btn btn-small" data-bind="click: $root.addFunctionToSource">
                  <i class="icon-plus"></i>
                </a>
                <br/>
                <p class="muted"></p>
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
            <textarea id="template-extra">${ hue_core.result.get_extracode() | n,unicode }</textarea>
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

  </%def>
</%layout:skeleton>

<span id="extraCode">
  ${ hue_core.result.get_extracode() | n,unicode }
</span>

<link rel="stylesheet" href="/static/ext/farbtastic/farbtastic.css">
<link rel="stylesheet" href="/static/ext/css/freshereditor.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/farbtastic/farbtastic.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/shortcut.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/freshereditor.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.0.js"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-xml.js"></script>
<script src="/static/ext/js/mustache.js"></script>

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
      self.availableFields = ko.observableArray(${ hue_core.fields | n,unicode });
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
    $(".chzn-select").chosen();

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
      excludes: ['strikethrough', 'removeFormat', 'backcolor', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
    });
    $("#content-editor").freshereditor("edit", true);

    // Force refresh on tab change
    $("a[data-toggle='tab']").on("shown", function (e) {
      if ($(e.target).attr("href") == "#source") {
        templateSourceMirror.setValue($("#content-editor").html());
        templateSourceMirror.refresh();
      }
      if ($(e.target).attr("href") == "#extra") {
        templateExtraMirror.refresh();
      }
      if ($(e.target).attr("href") == "#preview") {
        $("#preview-container").empty();
        $(samples).each(function (cnt, item) {
          item.viewfile = function () {
            return function (val) {
              return '<a href="/filebrowser/view/' + $.trim(Mustache.render(val, item)) + '">' + $.trim(Mustache.render(val, item)) + '</a>';
            }
          };
          item.downloadfile = function () {
            return function (val) {
              return '<a href="/filebrowser/download/' + $.trim(Mustache.render(val, item)) + '?disposition=inline">' + $.trim(Mustache.render(val, item)) + '</a>';
            }
          };
          item.date = function () {
            return function (val) {
              return genericFormatDate(val, item, "DD-MM-YYYY");
            }
          };
          item.time = function () {
            return function (val) {
              return genericFormatDate(val, item, "HH:mm:ss");
            }
          };
          item.datetime = function () {
            return function (val) {
              return genericFormatDate(val, item, "DD-MM-YYYY HH:mm:ss");
            }
          };
          item.fulldate = function () {
            return function (val) {
              return genericFormatDate(val, item, null);
            }
          };
          item.timestamp = function () {
            return function (val) {
              var d = moment(Mustache.render(val, item));
              if (d.isValid()) {
                return d.valueOf();
              }
              else {
                return Mustache.render(val, item);
              }
            }
          };
          $("<div>").addClass("preview-row").html(Mustache.render($("#content-editor").html(), item)).appendTo($("#preview-container"));
        });
      }
    });

    var sourceDelay = -1;
    templateSourceMirror.on("change", function () {
      clearTimeout(sourceDelay);
      sourceDelay = setTimeout(function () {
        $("#content-editor").html(templateSourceMirror.getValue());
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

    $("#load-template-modal").modal({
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
      $.ajax("${ url('search:admin_core_template', core=hue_core.name) }", {
        data: {
          'template': ko.utils.stringifyJson($("#content-editor").html()),
          'extracode': ko.utils.stringifyJson(templateExtraMirror.getValue())
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $.jHueNotify.info("${_('Template updated')}");
        },
        error: function (data) {
          $.jHueNotify.error("${_('Error: ')}" + data);
        },
        complete: function () {
          $("#save-template").button('reset');
        }
      });
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
