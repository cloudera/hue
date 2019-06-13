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
  import urllib
  from django.template.defaultfilters import urlencode, stringformat, date, filesizeformat, time
  from filebrowser.views import truncate
  from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>
<%
  path_enc = urllib.quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
  dirname_enc = urlencode(view['dirname'])
  base_url = url('filebrowser.views.view', path=path_enc)
  edit_url = url('filebrowser_views_edit', path=path_enc)
%>
<%namespace name="fb_components" file="fb_components.mako" />

%if not is_embeddable:
${ commonheader(_('%(filename)s - File Viewer') % dict(filename=truncate(filename)), 'filebrowser', user, request) | n,unicode }
%endif


${ fb_components.menubar() }

<div id="fileviewerComponents" class="container-fluid">
  <link href="${ static('filebrowser/css/display.css') }" rel="stylesheet" type="text/css">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav margin-top-10">
        <!-- ko if: $root.file -->
        <ul class="nav nav-list">
          <!-- ko if: $root.isViewing -->
            <li><a href="${url('filebrowser.views.view', path=dirname_enc)}"><i class="fa fa-reply"></i> ${_('Back')}</a></li>

            <!-- ko if: $root.file().view.compression() && $root.file().view.compression() === "none" && $root.file().editable -->
              <li><a class="pointer" data-bind="click: $root.editFile"><i class="fa fa-pencil"></i> ${_('Edit file')}</a></li>
            <!-- /ko -->

            <li><a class="pointer" data-bind="click: changePage"><i class="fa fa-refresh"></i> ${_('Refresh')}</a></li>

            <!-- ko if: $root.file().view.mode() === 'binary' -->
            <li><a class="pointer" data-bind="click: function(){ switchMode('text'); }"><i class="fa fa-font"></i> ${_('View as text')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.mode() === 'text' -->
              <li><a class="pointer" data-bind="click: function(){ switchMode('binary'); }"><i class="fa fa-barcode"></i> ${_('View as binary')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() !== "gzip" && $root.file().path().toLowerCase().endsWith('.gz') -->
              <li><a class="pointer" data-bind="click: function(){ switchCompression('gzip'); }"><i class="fa fa-youtube-play"></i> ${_('Preview as Gzip')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() !== "bz2" && ($root.file().path().toLowerCase().endsWith('.bz2') || $root.file().path().toLowerCase().endsWith('.bzip2'))-->
              <li><a class="pointer" data-bind="click: function(){ switchCompression('bz2'); }"><i class="fa fa-youtube-play"></i> ${_('Preview as Bzip2')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() !== "avro" && $root.file().view.compression() !== "snappy_avro" && $root.file().path().toLowerCase().endsWith('.avro') -->
              <li><a class="pointer" data-bind="click: function(){ switchCompression('avro'); }"><i class="fa fa-youtube-play"></i> ${_('Preview as Avro')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() && $root.file().view.compression() !== "none" -->
              <li><a class="pointer" data-bind="click: function(){ switchCompression('none'); }"><i class="fa fa-times-circle"></i> ${_('Stop preview')}</a></li>
            <!-- /ko -->
          <!-- /ko -->

          <!-- ko ifnot: $root.isViewing -->
            <li><a class="pointer" data-bind="click: $root.viewFile"><i class="fa fa-reply"></i> ${_('View file')}</a></li>
          <!-- /ko -->

          <!-- ko if: $root.isViewing -->
            <!-- ko if: $root.file().show_download_button -->
              <li><a class="pointer" data-bind="click: $root.downloadFile"><i class="fa fa-download"></i> ${_('Download')}</a></li>
            <!-- /ko -->
          <!-- /ko -->

           <!-- ko if: $root.file().stats -->
           <li class="white margin-top-20">
            <dl class="muted">
              <dt>${_('Last modified')}</dt>
              <dd data-bind="text: localeFormat($root.file().stats.mtime()*1000)"></dd>
              <dt>${_('User')}</dt>
              <dd data-bind="text: $root.file().stats.user"></dd>
              <dt>${_('Group')}</dt>
              <dd data-bind="text: $root.file().stats.group"></dd>
              <dt>${_('Size')}</dt>
              <dd data-bind="text: filesize($root.file().stats.size())"></dd>
              <dt>${_('Mode')}</dt>
              <dd data-bind="text: $root.file().stats.mode().toString(8)"></dd>
            </dl>
           </li>
           <!-- /ko -->
        </ul>
        <!-- /ko -->
      </div>
    </div>
    <div class="span10">
      <div class="card card-small" style="margin-bottom: 5px">
        <!-- ko if: $root.isViewing() && $root.file() && ($root.file().view.compression() === null || $root.file().view.compression() === "avro" || $root.file().view.compression() === "none") -->
          <div class="pull-right" style="margin-right: 20px; margin-top: 14px;">
            <div class="form-inline pagination-input-form inline">
              <span>${_('Page')}</span>
              <input type="text" data-bind="value: page, valueUpdate: 'afterkeydown', event: { change: pageChanged }" class="pagination-input" />
              ${_('to')} <input type="text" data-bind="value: upperPage, valueUpdate: 'afterkeydown', event: { change: upperPageChanged }" class="pagination-input"/>
              ${_('of')} <span data-bind="text: totalPages"></span>
            </div>
            <div class="pagination inline">
              <ul>
                <li class="first-page prev" data-bind="css: {'disabled': page() == 1}"><a href="javascript:void(0);" data-bind="click: firstPage" title="${_('First page')}"><i class="fa fa-fast-backward"></i></a></li>
                <li class="previous-page" data-bind="css: {'disabled': page() == 1}"><a href="javascript:void(0);" data-bind="click: previousPage" title="${_('Previous page')}"><i class="fa fa-backward"></i></a></li>
                <li class="next-page" data-bind="css: {'disabled': page() == totalPages() || upperPage() == totalPages()}"><a href="javascript:void(0);" data-bind="click: nextPage" title="${_('Next page')}"><i class="fa fa-forward"></i></a></li>
                <li class="last-page next" data-bind="css: {'disabled': page() == totalPages() || upperPage() == totalPages()}"><a href="javascript:void(0);" data-bind="click: lastPage" title="${_('Last page')}"><i class="fa fa-fast-forward"></i></a></li>
              </ul>
            </div>
          </div>
        <!-- /ko -->
        % if breadcrumbs:
          ${fb_components.breadcrumbs(path, breadcrumbs)}
        %endif
        <div class="card-body" style="padding: 0">
            <!-- ko if: $root.file() && $root.file().stats.size() === 0 && $root.isViewing() -->
            <div class="center empty-wrapper">
              <h1>${_('The current file is empty.')}</h1>
              <br/>
            </div>
            <!-- /ko -->
            <!-- ko if: $root.file -->
              <!-- ko ifnot: $root.file().stats.size() === 0 -->
                <!-- ko if: $root.file().view.contents && $root.file().view.masked_binary_data() -->
                <div class="alert alert-warning">${_("Warning: some binary data has been masked out with '&#xfffd'.")}</div>
                <!-- /ko -->
                <!-- ko if: ['avro', 'bz2', 'gzip', 'parquet', 'snappy'].indexOf($root.file().view.compression()) > -1 -->
                <div class="alert alert-warning"><i class="fa fa-info-circle"></i> ${_('Output rendered from compressed %s file.') % view['compression']}</div>
                <!-- /ko -->
              <!-- /ko -->
            <!-- /ko -->
            <!-- ko hueSpinner: { spin: !$root.file() && isLoading(), center: true, size: 'xlarge' } --><!-- /ko -->
            <!-- ko if: $root.isViewing -->
            <div id="fileArea" data-bind="css: {'loading': isLoading}, visible: $root.file() && $root.file().stats.size()" class="monospace" >
              <!-- ko hueSpinner: { spin: isLoading, center: true, size: 'xlarge' } --><!-- /ko -->
              <pre></pre>
              <table class="binary">
                <tbody>
                </tbody>
              </table>
            </div>
            <!-- /ko -->
            <!-- ko if not: $root.isViewing -->
            <div id="fileeditor"></div>
            <!-- /ko -->
        </div>
      </div>

    </div>
  </div>
</div>

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.visible.min.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
(function () {
  <%
    MAX_ALLOWED_PAGES_PER_REQUEST = 255
  %>

  var pages = {};

  var viewModel = new DisplayViewModel({
    base_url: "${ base_url }",
    compression: "${view['compression']}",
    mode: "${ view['mode'] }",
    begin: ${view['offset'] + 1},
    end: ${view['end']},
    length: ${view['length']},
    size: ${stats['size']},
    max_size: ${view['max_chunk_size']}
  });

  function resizeText() {
    hueUtils.waitForRendered('#fileArea', function(el){ return el.is(':visible') }, function(){
      $("#fileArea").height($(window).height() - $("#fileArea").offset().top - 30);
    });
  }

  function formatHex(number, padding) {
    if ("undefined" != typeof number) {
      var _filler = "";
      for (var i = 0; i < padding - 1; i++) {
        _filler += "0";
      }
      return (_filler + number.toString(16)).substr(-padding);
    }
    return "";
  }

  function renderPages() {
    var _html = "";
    for (var i = viewModel.page(); i <= viewModel.upperPage(); i++) {
      _html += "<a id='page" + i + "'><div class='fill-file-area'></div></a>";
    }
    $("#fileArea pre").html(_html);
  }

  var getChunks = function (startPage, endPage, view) {
    var chunkSize = view.length / (endPage - startPage + 1);
    return view.contents.match(new RegExp('[\\s\\S]{1,' + chunkSize + '}', 'g'));
  }

  function getContent (callback) {
    var _baseUrl = "${url('filebrowser.views.view', path=path_enc)}";

    viewModel.isLoading(true);

    var startPage = viewModel.page();
    var endPage = viewModel.upperPage();

    var params = {
      offset: (startPage - 1) * viewModel.length(),
      length: viewModel.length() * (endPage - startPage + 1),
      compression: viewModel.compression(),
      mode: viewModel.mode()
    };

    $.getJSON(_baseUrl, params, function (data) {
      var _html = "";

      viewModel.file(ko.mapping.fromJS(data, { 'ignore': ['view.contents', 'view.xxd'] }));
      if (data.view.contents) {
        $('#fileArea pre').show();
        $('.binary').hide();
        var chunks = getChunks(startPage, endPage, data.view)
        for (var i = startPage; i <= endPage; i++) {
          pages[i] = chunks.shift();
        }
        if ($("#fileArea pre").children().length == 0) {
          renderPages();
        }
        $.each(pages, function (page, content) {
          var $page = $('#page' + page);
          if ($page.children('.fill-file-area').length > 0) {
            $page.html("<div style='display: inline'>" + $("<span>").text(content).html() + "</div>")
          }
        });
      }

      if (data.view.xxd != null) {
        pages[startPage] = data.view.xxd;
        $('#fileArea pre').hide();
        $('.binary').show();

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

  function DisplayViewModel (params) {
    var self = this;

    self.changePage = function () {
      renderPages();
      getContent(function () {
        $("#fileArea").scrollTop(0);
      });
    }

    self.MAX_ALLOWED_PAGES_PER_REQUEST = ${ MAX_ALLOWED_PAGES_PER_REQUEST };
    self.PAGES_PER_CHUNK = 50;

    self.isViewing = ko.observable(true);
    self.isViewing.subscribe(function(val){
      if (val){
        window.setTimeout(resizeText, 0);
      }
    });

    self.base_url = ko.observable(params.base_url);
    self.compression = ko.observable(params.compression);
    self.mode = ko.observable(params.mode);
    self.mode.subscribe(function(val){
      window.setTimeout(resizeText, 0);
    });
    self.begin = ko.observable(params.begin);
    self.end = ko.observable(params.end);
    self.length = ko.observable(params.length);
    self.size = ko.observable(params.size);
    self.page = ko.observable(1);
    self.isLoading = ko.observable(false);

    self.file = ko.observable();

    self.totalPages = ko.computed(function () {
      return Math.max(Math.ceil(self.size() / self.length()), 1);
    });

    self.upperPage = ko.observable(Math.min(self.totalPages(), 50));

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

    self.switchMode = function (newMode) {
      self.mode(newMode);
      self.changePage();
    }

    self.switchCompression = function (newCompression) {
      self.compression(newCompression);
      self.page(1);
      self.upperPage(1);
      self.changePage();
    }

    self.editFile = function() {
      self.isViewing(false);
      self.isLoading(true);
      $.ajax({
        url: '${ edit_url }' + '?is_embeddable=true',
        beforeSend:function (xhr) {
          xhr.setRequestHeader('X-Requested-With', 'Hue');
        },
        dataType:'html',
        success:function (response) {
          $('#fileeditor').html(response);
          self.isLoading(false);
        }
      });
    }

    self.viewFile = function() {
      $('#fileeditor').html('');
      self.isViewing(true);
      self.page(1);
      self.upperPage(1);
      self.changePage();
    }

    self.downloadFile = function () {
      huePubSub.publish('open.link', "${url('filebrowser_views_download', path=path_enc)}");
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
      self.changePage();
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
      self.changePage();
    };

    self.nextPage = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (!($("#fileviewerComponents .next-page").hasClass("disabled"))) {
        if (self.page() == self.upperPage()) {
          self.page(self.page() + 1);
          self.upperPage(self.upperPage() + 1);
        } else {
          var _difference = self.upperPage() - self.page();
          self.page(self.upperPage() + 1);
          self.upperPage(Math.min(self.page() + _difference, self.totalPages()));
        }
        self.changePage();
      }
    };

    self.previousPage = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (!($("#fileviewerComponents .previous-page").hasClass("disabled"))) {
        if (self.page() == self.upperPage()) {
          self.page(self.page() - 1);
          self.upperPage(self.upperPage() - 1);
        } else {
          var _difference = self.upperPage() - self.page();
          self.upperPage(self.page() - 1);
          self.page(Math.max(self.page() - _difference - 1, 1));
        }
        self.changePage();
      }
    };

    self.lastPage = function () {
      if (!($("#fileviewerComponents .last-page").hasClass("disabled"))) {
        var lastDiff = self.upperPage() - self.page() + 1;
        self.page(Math.max(1, self.totalPages() - lastDiff));
        self.upperPage(self.totalPages());
        self.changePage();
      }
    };

    self.firstPage = function () {
      if (!($("#fileviewerComponents .first-page").hasClass("disabled"))) {
        var lastDiff = self.upperPage() - self.page() + 1;
        self.page(1);
        if (lastDiff > 1) {
          self.upperPage(Math.min(self.totalPages(), lastDiff))
        } else {
          self.upperPage(Math.min(self.totalPages(), 50));
        }
        self.changePage();
      }
    };
  }

  $(document).ready(function () {
    ko.applyBindings(viewModel, $('#fileviewerComponents')[0]);

    % if not is_embeddable:
    $(document).ajaxError(function () {
      $.jHueNotify.error("${_('There was an unexpected server error.')}");
    });
    % endif

    setTimeout(function () {
      resizeText();
      getContent();
    }, 100);

    var _resizeTimeout = -1;

    $(window).on("resize", function () {
      clearTimeout(_resizeTimeout);
      _resizeTimeout = setTimeout(function () {
        resizeText();
        $('#fileviewerComponents .fill-file-area').css('height', $("#fileArea").height() + 'px');
      }, 300);
    });

    $("#fileArea").jHueScrollUp();
  });
}());
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
