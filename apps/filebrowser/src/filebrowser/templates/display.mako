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
  path_enc = path
  dirname_enc = urlencode(view['dirname'])
  base_url = url('filebrowser.views.view', path=path_enc)
%>
<%namespace name="fb_components" file="fb_components.mako" />

${ commonheader(_('%(filename)s - File Viewer') % dict(filename=truncate(filename)), 'filebrowser', user) | n,unicode }
${ fb_components.menubar() }

<link href="${ static('filebrowser/css/display.css') }" rel="stylesheet" />
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      ${ fb_components.file_sidebar(path_enc, dirname_enc, stats, view) }
    </div>
    <div class="span10">
      <div class="card card-small" style="margin-bottom: 5px">
        % if not view['compression'] or view['compression'] in ("none", "avro"):
          <div class="pull-right" style="margin-right: 20px; margin-top: 14px;">
            <div class="form-inline pagination-input-form inline">
              <span>${_('Page')}</span>
              <input type="text" data-bind="value: page, valueUpdate: 'afterkeydown', event: { change: pageChanged }" class="pagination-input" />
              <span data-bind="visible: totalPages() > MAX_PAGES_TO_ENABLE_SCROLLING || viewModel.mode() == 'binary'">
              to <input type="text" data-bind="value: upperPage, valueUpdate: 'afterkeydown', event: { change: upperPageChanged }" class="pagination-input"/></span>
              of <span data-bind="text: totalPages"></span>
            </div>
            <div class="pagination inline">
              <ul>
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
          %if view['compression'] in ('avro', 'gzip', 'parquet', 'snappy'):
            <p class="muted"><i class="fa fa-info-circle"></i> ${_('Output rendered from compressed %s file.') % view['compression']}</p>
          %endif
            <div id="fileArea" data-bind="css: {'loading': isLoading}">
              <div id="loader" data-bind="visible: isLoading">
                <!--[if !IE]><!--><i class="fa fa-spinner fa-spin"></i><!--<![endif]-->
                <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
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
        </div>
      </div>
    </div>
  </div>
</div>

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.visible.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-min.js') }" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript" charset="utf-8">
(function () {
  <%
    MAX_ALLOWED_PAGES_PER_REQUEST = 255
  %>

  var pages = {};

  function resizeText () {
    var _fileArea = $("#fileArea");
    if (_fileArea.height() > 0) {
      _fileArea.height($(window).height() - _fileArea.offset().top - 26);
      $("#loader").css("marginLeft", (_fileArea.width() - $("#loader").width()) / 2);
    }
  }

  function formatHex (number, padding) {
    if ("undefined" != typeof number){
      var _filler = "";
      for (var i = 0; i < padding - 1; i++) {
        _filler += "0";
      }
      return (_filler + number.toString(16)).substr(-padding);
    }
    return "";
  }

  function pageContent (page) {
    var _html = "";
    if ($("#page" + page).length == 0) {
      if (pages[page] == null) {
        _html += "<a id='page" + page + "'><div style='height: " + $("#fileArea").height() + "px'></div></a>";
      } else {
        _html += "<a id='page" + page + "'><div style='display: inline'>" + $("<span>").text(pages[page]).html() + "</div></a>";
      }
    } else {
      if (pages[page] == null) {
        $("#page" + page).html("<div style='height: " + $("#fileArea").height() + "px'></div>");
      } else {
        $("#page" + page).html("<div style='display: inline'>" + $("<span>").text(pages[page]).html() + "</div>");
      }
    }
    return _html;
  }

  function renderPages () {
    var _html = "";
    if (viewModel.totalPages() < viewModel.MAX_PAGES_TO_ENABLE_SCROLLING) { // enable scrolling
      for (var i = 1; i <= viewModel.totalPages(); i++) {
        _html += pageContent(i);
      }
    } else {
      _html += pageContent(viewModel.page());
    }
    if (_html != "") {
      $("#fileArea pre").html(_html);
    }
  }

  function getContent (callback) {
    var _baseUrl = "${url('filebrowser.views.view', path=path_enc)}";

    viewModel.isLoading(true);

    $.getJSON(_baseUrl, viewModel.jsonParams(), function (data) {
      var _html = "";

      if (data.view.contents != null) {
        pages[viewModel.page()] = data.view.contents;
        renderPages();
      }

      if (data.view.xxd != null) {
        pages[viewModel.page()] = data.view.xxd;

        $(data.view.xxd).each(function (cnt, item) {
          var i;
          _html += "<tr><td>" + formatHex(item[0], 7) + ":&nbsp;</td><td>";

          for (i = 0; i < item[1].length; i++) {
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

  function DisplayViewModel (params) {
    var self = this;

    function changePage () {
      getContent(function () {
        if (viewModel.totalPages() >= viewModel.MAX_PAGES_TO_ENABLE_SCROLLING || viewModel.mode() == "binary") {
          location.hash = "#p" + viewModel.page() + (viewModel.page() != viewModel.upperPage() ? "-p" + viewModel.upperPage() : "");
          $("#fileArea").scrollTop(0);
        } else {
          location.hash = "#page" + viewModel.page();
        }
      });
    }

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
      return Math.max(Math.ceil(self.size() / self.length()), 1);
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

    self.nextPage = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (! ($(".next-page").hasClass("disabled"))) {
        if (viewModel.page() == viewModel.upperPage()) {
          viewModel.page(viewModel.page() + 1);
          viewModel.upperPage(viewModel.upperPage() + 1);
        } else {
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
      if (! ($(".previous-page").hasClass("disabled"))) {
        if (viewModel.page() == viewModel.upperPage()) {
          viewModel.page(viewModel.page() - 1);
          viewModel.upperPage(viewModel.upperPage() - 1);
        } else {
          var _difference = self.upperPage() - self.page();
          self.upperPage(self.page() - 1);
          self.page(Math.max(self.page() - _difference - 1, 1));
        }
        changePage();
      }
    };

    self.lastPage = function () {
      if (! ($(".last-page").hasClass("disabled"))) {
        var _page = viewModel.totalPages();
        viewModel.page(viewModel.totalPages());
        viewModel.upperPage(viewModel.totalPages());
        changePage();
      }
    };

    self.firstPage = function () {
      if (! ($(".first-page").hasClass("disabled"))) {
        viewModel.page(1);
        viewModel.upperPage(Math.min(self.totalPages(), 50));
        changePage();
      }
    };
  }

  window.viewModel = new DisplayViewModel({
    base_url: "${ base_url }",
    compression: "${view['compression']}",
    mode: "${ view['mode'] }",
    begin: ${view['offset'] + 1},
    end: ${view['end']},
    length: ${view['length']},
    size: ${stats['size']},
    max_size: ${view['max_chunk_size']}
  });

  $(document).ready(function () {
    ko.applyBindings(viewModel);

    $(document).ajaxError(function () {
      $.jHueNotify.error("${_('There was an unexpected server error.')}");
    });

    var _hashPage, _hashUpperPage, _resizeTimeout, _fileAreaScrollTimeout, i,
      _hash = location.hash;

    _hashPage = 1;
    _hashUpperPage = 1;
    if (_hash != "") {

      if (_hash.indexOf("-") > -1) {
        _hashPage = _hash.split("-")[0].substr(2) * 1;
        _hashUpperPage = _hash.split("-")[1].substr(1) * 1;
      } else {
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
    }
    viewModel.page(_hashPage);
    viewModel.upperPage(_hashUpperPage);

    viewModel.toggleDisables();

    setTimeout(function () {
      getContent(function () {
        if (location.hash != "") {
          location.hash = "#page" + viewModel.page();
          location.hash = "#p" + viewModel.page() + (viewModel.page() != viewModel.upperPage() ? "-p" + viewModel.upperPage() : "");
        }
      });
    }, 100);

    resizeText();

    _resizeTimeout = -1;

    $(window).on("resize", function () {
      clearTimeout(_resizeTimeout);
      _resizeTimeout = setTimeout(function () {
        resizeText();
        renderPages();
      }, 300);
    });

    $("#fileArea").jHueScrollUp();

    if (viewModel.totalPages() < viewModel.MAX_PAGES_TO_ENABLE_SCROLLING && viewModel.mode() == "text") { // enable scrolling
      _fileAreaScrollTimeout = -1;
      $("#fileArea").on("scroll", function () {
        if (viewModel.compression() === 'gzip') {
          $("#fileArea").off("scroll");
          $(document).trigger('warn', "${_('Offsets are not supported with Gzip compression.')}");
          return false;
        }

        if ($("#fileArea").scrollTop() < 30) {
          viewModel.page(1);
          viewModel.upperPage(viewModel.page());
        } else {
          for (i = 1; i <= viewModel.totalPages(); i++) {
            if ($("#page" + i + " div").visible(true)) {
              viewModel.page(i);
              viewModel.upperPage(viewModel.page());
            }
          }
        }
        clearTimeout(_fileAreaScrollTimeout);
        _fileAreaScrollTimeout = setTimeout(function () {
          location.hash = "#p" + viewModel.page();
          if (pages[viewModel.page()] == null) {
            getContent();
          }
        }, 100);
      });
    }
  });
}());
</script>

${ commonfooter(messages) | n,unicode }
