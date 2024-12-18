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
  import sys
  from django.template.defaultfilters import urlencode, stringformat, date, filesizeformat, time
  from filebrowser.views import truncate
  from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
  from desktop.views import commonheader, commonfooter

  if sys.version_info[0] > 2:
    from urllib.parse import quote as urllib_quote
    from django.utils.translation import gettext as _
  else:
    from urllib import quote as urllib_quote
    from django.utils.translation import ugettext as _
%>
<%  
  path_enc = urllib_quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
  dirname_enc = urlencode(view['dirname'])
  base_url = url('filebrowser:filebrowser.views.view', path=path_enc)
  edit_url = url('filebrowser:filebrowser_views_edit', path=path_enc)
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
            <li><a data-hue-analytics="filebrowser:back-btn-click" data-bind="click: goToParentDirectory" href=""><i class="fa fa-reply"></i> ${_('Back')}</a></li>

            <!-- ko if: $root.file().view.compression() && $root.file().view.compression() === "none" && $root.file().editable -->
              <li><a data-hue-analytics="filebrowser:edit-file-btn-click"class="pointer" data-bind="click: $root.editFile"><i class="fa fa-pencil"></i> ${_('Edit file')}</a></li>
            <!-- /ko -->

            <li><a data-hue-analytics="filebrowser:refresh-btn-click" class="pointer" data-bind="click: changePage"><i class="fa fa-refresh"></i> ${_('Refresh')}</a></li>

            <!-- ko if: $root.file().view.mode() === 'binary' -->
            <li><a data-hue-analytics="filebrowser:view-text-btn-click" class="pointer" data-bind="click: function(){ switchMode('text'); }"><i class="fa fa-font"></i> ${_('View as text')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.mode() === 'text' -->
              <li><a data-hue-analytics="filebrowser:view-binary-btn-click" class="pointer" data-bind="click: function(){ switchMode('binary'); }"><i class="fa fa-barcode"></i> ${_('View as binary')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() !== "gzip" && $root.file().path().toLowerCase().endsWith('.gz') -->
              <li><a data-hue-analytics="filebrowser:preview-gzip--btn-click" class="pointer" data-bind="click: function(){ switchCompression('gzip'); }"><i class="fa fa-youtube-play"></i> ${_('Preview as Gzip')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() !== "bz2" && ($root.file().path().toLowerCase().endsWith('.bz2') || $root.file().path().toLowerCase().endsWith('.bzip2'))-->
              <li><a data-hue-analytics="filebrowser:preview-bz2--btn-click" class="pointer" data-bind="click: function(){ switchCompression('bz2'); }"><i class="fa fa-youtube-play"></i> ${_('Preview as Bzip2')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() !== "avro" && $root.file().view.compression() !== "snappy_avro" && $root.file().path().toLowerCase().endsWith('.avro') -->
              <li><a data-hue-analytics="filebrowser:preview-avro--btn-click" class="pointer" data-bind="click: function(){ switchCompression('avro'); }"><i class="fa fa-youtube-play"></i> ${_('Preview as Avro')}</a></li>
            <!-- /ko -->

            <!-- ko if: $root.file().view.compression() && $root.file().view.compression() !== "none" -->
              <li><a data-hue-analytics="filebrowser:stop-preview--btn-click" class="pointer" data-bind="click: function(){ switchCompression('none'); }"><i class="fa fa-times-circle"></i> ${_('Stop preview')}</a></li>
            <!-- /ko -->
          <!-- /ko -->

          <!-- ko ifnot: $root.isViewing -->
            <li><a data-hue-analytics="filebrowser:view-file-btn-click" class="pointer" data-bind="click: $root.viewFile"><i class="fa fa-reply"></i> ${_('View file')}</a></li>
          <!-- /ko -->

          <!-- ko if: $root.isViewing -->
            <!-- ko if: $root.file().show_download_button -->
              <li><a data-hue-analytics="filebrowser:download-btn-click" class="pointer" data-bind="click: $root.downloadFile"><i class="fa fa-download"></i> ${_('Download')}</a></li>
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

<script type="application/json" id="FileViewOptions">
  ${ options_json | n }
</script>

<script src="${ static('desktop/js/file-display-inline.js') }" type="text/javascript"></script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
