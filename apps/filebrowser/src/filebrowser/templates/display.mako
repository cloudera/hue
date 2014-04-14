## -*- coding: utf-8 -*-
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
  import datetime
  from django.template.defaultfilters import urlencode, stringformat, date, filesizeformat, time
  from filebrowser.views import truncate
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>
<%
  path_enc = urlencode(path)
  dirname_enc = urlencode(view['dirname'])
  base_url = url('filebrowser.views.view', path=path_enc)
%>
<%namespace name="fb_components" file="fb_components.mako" />

${ commonheader(_('%(filename)s - File Viewer') % dict(filename=truncate(filename)), 'filebrowser', user) | n,unicode }
${ fb_components.menubar() }

<script src="/static/ext/js/jquery/plugins/jquery.visible.min.js" type="text/javascript" charset="utf-8"></script>

<style type="text/css">
  #fileArea {
    overflow: auto;
    background-color: #F5F5F5;
    position: relative;
  }

  #fileArea.loading {
    opacity: .7;
  }

  #loader {
    position: fixed;
    margin-top: 40px;
    font-size: 50px;
    text-align: center;
    width: 140px;
    height: 140px;
    line-height: 140px;
    -webkit-border-radius: 20px;
    -moz-border-radius: 20px;
    border-radius: 20px;
  }

  .binary {
    font-family: "Courier New", Courier, monospace;
  }

  pre {
    border: none;
  }

  pre a {
    color: #444;
    cursor: default;
  }

  pre a:hover {
    color: #444;
    text-decoration: none;
  }
</style>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      ${ fb_components.file_sidebar(path_enc, dirname_enc, stats, view) }
    </div>
    <div class="span10">
      <div class="card card-small" style="margin-bottom: 5px">
        % if not view['compression'] or view['compression'] in ("none", "avro"):
          <div class="pull-right" style="margin-right: 20px; margin-top: 14px">
            <div class="form-inline" style="display: inline">
              <span>${_('Page')}</span>
              <input type="text" data-bind="value: page, valueUpdate: 'afterkeydown', event: { change: pageChanged }" style="width: 40px; text-align: center"/>
              <span data-bind="visible: totalPages() > MAX_PAGES_TO_ENABLE_SCROLLING || viewModel.mode() == 'binary'">
              to <input type="text" data-bind="value: upperPage, valueUpdate: 'afterkeydown', event: { change: upperPageChanged }" style="width: 40px; text-align: center"/></span>
              of <span data-bind="text: totalPages"></span>
            </div>
            <div class="pagination" style="display: inline;">
              <ul style="margin-bottom: -10px; margin-left: 10px">
                <li class="first-page prev disabled"><a href="javascript:void(0);" data-bind="click: firstPage" title="${_('First page')}"><i class="fa fa-fast-backward"></i></a></li>
                <li class="previous-page disabled"><a href="javascript:void(0);" data-bind="click: previousPage" title="${_('Previous page')}"><i class="fa fa-backward"></i></a></li>
                <li class="next-page"><a href="javascript:void(0);" data-bind="click: nextPage" title="${_('Next page')}"><i class="fa fa-forward"></i></a></li>
                <li class="last-page next"><a href="javascript:void(0);" data-bind="click: lastPage" title="${_('Last page')}"><i class="fa fa-fast-forward"></i></a></li>
              </ul>
            </div>
          </div>
        % endif
        % if breadcrumbs:
          ${fb_components.breadcrumbs(path, breadcrumbs)}
        %endif
        <div class="card-body">
        <p>
          % if stats['size'] == 0:
            <div class="center empty-wrapper">
              <i class="fa fa-frown-o"></i>

              <h1>${_('The current file is empty.')}</h1>
              <br/>
            </div>
          % else:
          % if 'contents' in view and view['masked_binary_data']:
            <div class="alert alert-warning">${_("Warning: some binary data has been masked out with '&#xfffd'.")}</div>
          % endif
            <div id="fileArea" data-bind="css: {'loading': isLoading}">
              <div id="loader" data-bind="visible: isLoading">
                <!--[if !IE]><!--><i class="fa fa-spinner fa-spin"></i><!--<![endif]-->
                <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
              </div>
              % if 'contents' in view:
                <pre></pre>
              % else:
                <table class="binary">
                  <tbody>
                  </tbody>
                </table>
              % endif
            </div>
          % endif
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

<%
  MAX_ALLOWED_PAGES_PER_REQUEST = 255
%>

function displayViewModel(params) {
  var self = this;

  self.MAX_ALLOWED_PAGES_PER_REQUEST = ${MAX_ALLOWED_PAGES_PER_REQUEST};
  self.MAX_PAGES_TO_ENABLE_SCROLLING = 300;
  self.PAGES_PER_CHUNK = 50;

  self.base_url = ko.observable(params.base_url);
  self.compression = ko.observable(params.compression);
  self.mode = ko.observable(params.mode);
  self.begin = ko.observable(params.begin);
  self.end = ko.observable(params.end);
  self.length = ko.observable(params.length);
  self.size = ko.observable(params.size);
  self.page = ko.observable(1);
  self.isLoading = ko.observable(true);

  self.totalPages = ko.computed(function () {
    return Math.max(Math.floor(self.size() / self.length()), 1);
  });

  self.upperPage = ko.observable(Math.min(self.totalPages(), 50));

  self.begin = ko.computed(function () {
    return (self.page() - 1) * self.length();
  });

  self.offset = ko.computed(function () {
    return ((self.page() - 1) * self.length()) - 1;
  });

  self.url = ko.computed(function () {
    return self.base_url()
            + "?offset=" + self.offset()
            + "&length=" + self.length()
            + "&compression=" + self.compression()
            + "&mode=" + self.mode();
  });

  self.jsonParams = ko.computed(function () {
    return {
      offset: self.begin(),
      length: self.length() * (self.upperPage() - self.page() + 1),
      compression: self.compression(),
      mode: self.mode()
    }
  });

  self.toggleDisables = function () {
    $(".next-page").removeClass("disabled");
    $(".last-page").removeClass("disabled");
    $(".first-page").removeClass("disabled");
    $(".previous-page").removeClass("disabled");

    if (self.page() == self.totalPages() || self.upperPage() == self.totalPages()) {
      $(".next-page").addClass("disabled");
      $(".last-page").addClass("disabled");
    }
    if (self.page() == 1) {
      $(".first-page").addClass("disabled");
      $(".previous-page").addClass("disabled");
    }
  };

  self.pageChanged = function () {
    self.page(self.page() * 1);
    self.upperPage(self.upperPage() * 1);
    if (self.page() > self.totalPages()) {
      self.page(self.totalPages());
    }
    if (self.page() < 1 || !$.isNumeric(self.page())) {
      self.page(1);
    }
    if (self.page() > self.upperPage()) {
      self.upperPage(self.page());
    }
    changePage();
  };

  self.upperPageChanged = function () {
    self.page(self.page() * 1);
    self.upperPage(self.upperPage() * 1);
    if (self.upperPage() > self.totalPages()) {
      self.upperPage(self.totalPages());
    }
    if (self.upperPage() < 1 || !$.isNumeric(self.upperPage())) {
      self.upperPage(1);
    }
    if (self.upperPage() < self.page()) {
      self.page(self.upperPage());
    }
    if (self.upperPage() - self.page() > self.MAX_ALLOWED_PAGES_PER_REQUEST) {
      self.upperPage(self.page() + self.MAX_ALLOWED_PAGES_PER_REQUEST);
      $.jHueNotify.info("${_('Sorry, you cannot request for more than %s pages.' % MAX_ALLOWED_PAGES_PER_REQUEST)}");
    }
    changePage();
  };

  self.page.subscribe(function (value) {
    self.toggleDisables();
  });

  self.upperPage.subscribe(function (value) {
    self.toggleDisables();
  });

  var changePage = function () {
    getContent(function () {
      if (viewModel.totalPages() >= viewModel.MAX_PAGES_TO_ENABLE_SCROLLING || viewModel.mode() == "binary") {
        window.location.hash = "#p" + viewModel.page() + (viewModel.page() != viewModel.upperPage() ? "-p" + viewModel.upperPage() : "");
        $("#fileArea").scrollTop(0);
      }
      else {
        window.location.hash = "#page" + viewModel.page();
      }
    });
  };

  self.nextPage = function () {
    self.page(self.page() * 1);
    self.upperPage(self.upperPage() * 1);
    if (!($(".next-page").hasClass("disabled"))) {
      if (viewModel.page() == viewModel.upperPage()) {
        viewModel.page(viewModel.page() + 1);
        viewModel.upperPage(viewModel.upperPage() + 1);
      }
      else {
        var _difference = self.upperPage() - self.page();
        self.page(self.upperPage() + 1);
        self.upperPage(Math.min(self.page() + _difference, self.totalPages()));
      }
      changePage();
    }
  };

  self.previousPage = function () {
    self.page(self.page() * 1);
    self.upperPage(self.upperPage() * 1);
    if (!($(".previous-page").hasClass("disabled"))) {
      if (viewModel.page() == viewModel.upperPage()) {
        viewModel.page(viewModel.page() - 1);
        viewModel.upperPage(viewModel.upperPage() - 1);
      }
      else {
        var _difference = self.upperPage() - self.page();
        self.upperPage(self.page() - 1);
        self.page(Math.max(self.page() - _difference - 1, 1));
      }
      changePage();
    }
  };

  self.lastPage = function () {
    if (!($(".last-page").hasClass("disabled"))) {
      var _page = viewModel.totalPages();
      if (_page > 50) {
        _page = Math.min(viewModel.totalPages() - viewModel.totalPages()%50 + 1, viewModel.totalPages());
      }
      viewModel.page(_page);
      viewModel.upperPage(viewModel.totalPages());
      changePage();
    }
  };

  self.firstPage = function () {
    if (!($(".first-page").hasClass("disabled"))) {
      viewModel.page(1);
      viewModel.upperPage(Math.min(self.totalPages(), 50));
      changePage();
    }
  }
}
;

var viewModel = new displayViewModel({
          base_url: "${ base_url }",
          compression: "${view['compression']}",
          mode: "${ view['mode'] }",
          begin: ${view['offset'] + 1},
          end: ${view['end']},
          length: ${view['length']},
          size: ${stats['size']},
          max_size: ${view['max_chunk_size']}
        }
);

function resizeText() {
  $("#fileArea").height($(window).height() - $("#fileArea").offset().top - 26);
  $("#loader").css("marginLeft", ($("#fileArea").width() - $("#loader").width()) / 2);
}

function formatHex(number, padding) {
  if ("undefined" != typeof number){
    var _filler = "";
    for (var i = 0; i < padding - 1; i++) {
      _filler += "0";
    }
    return (_filler + number.toString(16)).substr(-padding);
  }
  return "";
}

var pages = {};

function pageContent(page) {
  var _html = "";
  if ($("#page" + page).length == 0) {
    if (pages[page] == null) {
      _html += "<a id='page" + page + "'><div style='height: " + $("#fileArea").height() + "px'></div></a>";
    }
    else {
      _html += "<a id='page" + page + "'><div style='display: inline'>" + $("<span>").text(pages[page]).html() + "</div></a>";
    }
  }
  else {
    if (pages[page] == null) {
      $("#page" + page).html("<div style='height: " + $("#fileArea").height() + "px'></div>");
    }
    else {
      $("#page" + page).html("<div style='display: inline'>" + $("<span>").text(pages[page]).html() + "</div>");
    }

  }
  return _html;
}

function renderPages() {
  var _html = "";
  if (viewModel.totalPages() < viewModel.MAX_PAGES_TO_ENABLE_SCROLLING) { // enable scrolling
    for (var i = 1; i <= viewModel.totalPages(); i++) {
      _html += pageContent(i);
    }
  }
  else {
    _html += pageContent(viewModel.page());
  }
  if (_html != "") {
    $("#fileArea pre").html(_html);
  }
}


function getContent(callback) {
  viewModel.isLoading(true);
  var _baseUrl = "${url('filebrowser.views.view', path=path_enc)}";
  $.getJSON(_baseUrl, viewModel.jsonParams(), function (data) {
    if (data.view.contents != null) {
      pages[viewModel.page()] = data.view.contents;
      renderPages();
    }
    if (data.view.xxd != null) {
      pages[viewModel.page()] = data.view.xxd;
      var _html = "";
      $(data.view.xxd).each(function (cnt, item) {
        _html += "<tr><td>" + formatHex(item[0], 7) + ":&nbsp;</td><td>";
        for (var i = 0; i < item[1].length; i++) {
          _html += formatHex(item[1][i][0], 2) + " " + formatHex(item[1][i][1], 2) + " ";
        }
        _html += "</td><td>&nbsp;&nbsp;" + $("<span>").text(item[2]).html() + "</td></tr>";
      });
      $(".binary tbody").html(_html);
    }
    if (callback) {
      callback();
    }
    viewModel.isLoading(false);
  });
}


$(document).ready(function () {
  ko.applyBindings(viewModel);

  $(document).ajaxError(function () {
    $.jHueNotify.error("${_('There was an unexpected server error.')}");
  });

  var _hash = window.location.hash;
  if (_hash != "") {
    var _hashPage = 1;
    var _hashUpperPage = 1;
    if (_hash.indexOf("-") > -1) {
      _hashPage = _hash.split("-")[0].substr(2) * 1;
      _hashUpperPage = _hash.split("-")[1].substr(1) * 1;
    }
    else {
      _hashPage = _hash.substr(2) * 1;
      _hashUpperPage = Math.min(viewModel.totalPages(), _hashPage + 50 - 1);
    }
    if (isNaN(_hashPage)) {
      _hashPage = 1;
    }
    if (isNaN(_hashUpperPage)) {
      _hashUpperPage = Math.min(viewModel.totalPages(), 50);
    }
    if (_hashUpperPage - _hashPage > viewModel.MAX_ALLOWED_PAGES_PER_REQUEST) {
      _hashUpperPage = _hashPage + viewModel.MAX_ALLOWED_PAGES_PER_REQUEST;
    }
    viewModel.page(_hashPage);
    viewModel.upperPage(_hashUpperPage);
  }

  viewModel.toggleDisables();

  window.setTimeout(function () {
    getContent(function () {
      if (window.location.hash != "") {
        window.location.hash = "#page" + viewModel.page();
        window.location.hash = "#p" + viewModel.page() + (viewModel.page() != viewModel.upperPage() ? "-p" + viewModel.upperPage() : "");
      }
    });
  }, 100);

  resizeText();

  var _resizeTimeout = -1;
  $(window).on("resize", function () {
    window.clearTimeout(_resizeTimeout);
    _resizeTimeout = window.setTimeout(function () {
      resizeText();
      renderPages();
    }, 300);
  });

  $("#fileArea").jHueScrollUp();

  if (viewModel.totalPages() < viewModel.MAX_PAGES_TO_ENABLE_SCROLLING && viewModel.mode() == "text") { // enable scrolling
    var _fileAreaScrollTimeout = -1;
    $("#fileArea").on("scroll", function () {
      if ($("#fileArea").scrollTop() < 30) {
        viewModel.page(1);
        viewModel.upperPage(viewModel.page());
      }
      else {
        for (var i = 1; i <= viewModel.totalPages(); i++) {
          if ($("#page" + i + " div").visible(true)) {
            viewModel.page(i);
            viewModel.upperPage(viewModel.page());
          }
        }
      }
      window.clearTimeout(_fileAreaScrollTimeout);
      _fileAreaScrollTimeout = window.setTimeout(function () {
        location.hash = "#p" + viewModel.page();
        if (pages[viewModel.page()] == null) {
          getContent();
        }
      }, 100);
    });
  }

});
</script>

${ commonfooter(messages) | n,unicode }
