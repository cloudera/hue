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

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      ${ fb_components.file_sidebar(path_enc, dirname_enc, stats, view) }
    </div>
    <div class="span10">
      <div class="card card-small">
      % if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs)}
      %endif
        <div class="card-body">
          <p>
        % if stats['size'] == 0:
          <div class="center empty-wrapper">
            <i class="fa fa-frown-o"></i>
            <h1>${_('The current file is empty.')}</h1>
            <br />
          </div>
        % else:
          % if not view['compression'] or view['compression'] in ("none", "avro"):
          <div class="pagination">
            <ul>
              <li class="first-block prev disabled"><a href="javascript:void(0);" data-bind="click: firstBlock">${_('First Block')}</a></li>
              <li class="previous-block disabled"><a href="javascript:void(0);" data-bind="click: previousBlock">${_('Previous Block')}</a></li>
              <li class="next-block"><a href="javascript:void(0);" data-bind="click: nextBlock">${_('Next Block')}</a></li>
              <li class="last-block next"><a href="javascript:void(0);" data-bind="click: lastBlock">${_('Last Block')}</a></li>
            </ul>

            <form action="${url('filebrowser.views.view', path=path_enc)}" method="GET" class="form-inline pull-right">
              <span>${_('Viewing Bytes:')}</span>
              <input type="text" name="begin" value="${view['offset'] + 1}" data-bind="value: begin" class="input-mini" />
              -
              <input type="text" name="end" value="${view['end']}" data-bind="value: end" class="input-mini" /> of
              <span>${stats['size']}</span>
              <span>${_('(%(length)s B block size)' % dict(length=view['length']))}</span>
              % if view['mode']:
                <input type="hidden" name="mode" value="${view['mode']}"/>
              % endif
            </form>
          </div>
          % endif

          %if 'contents' in view:
            % if view['masked_binary_data']:
              <div class="alert-message warning">${_("Warning: some binary data has been masked out with '&#xfffd'.")}</div>
            % endif
          % endif

          <div>
          % if 'contents' in view:
            <div id="file-contents"><pre>${view['contents']}</pre></div>
          % else:
            <table>
              % for offset, words, masked in view['xxd']:
              <tr>
                <td>${stringformat(offset, "07x")}:&nbsp;</td>
                <td>
                  % for word in words:
                    % for byte in word:
                      ${stringformat(byte, "02x")}
                    % endfor
                  % endfor
                </td>
                <td>
                  &nbsp;&nbsp;${masked}
                </td>
              </tr>
              % endfor
            </table>
          % endif
          </div>

          % if not view['compression'] or view['compression'] in ("none", "avro"):
            <div class="pagination">
              <ul>
                <li class="first-block prev disabled"><a href="javascript:void(0);" data-bind="click: firstBlock">${_('First Block')}</a></li>
                <li class="previous-block disabled"><a href="javascript:void(0);" data-bind="click: previousBlock">${_('Previous Block')}</a></li>
                <li class="next-block"><a href="javascript:void(0);" data-bind="click: nextBlock">${_('Next Block')}</a></li>
                <li class="last-block next"><a href="javascript:void(0);" data-bind="click: lastBlock">${_('Last Block')}</a></li>
              </ul>
            </div>
          % endif
        % endif
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

  <script type="text/javascript" charset="utf-8">
    function displayViewModel(base_url, compression, mode, begin, end, length, size, max_size) {
      var self = this;

      self.base_url = ko.observable(base_url);
      self.compression = ko.observable(compression);
      self.mode = ko.observable(mode);
      self.begin = ko.observable(begin);
      self.end = ko.observable(end);
      self.length = ko.observable(length);
      self.size = ko.observable(size);

      self.offset = ko.computed(function() {
        return self.begin() - 1;
      });

      self.url = ko.computed(function() {
        return self.base_url()
          + "?offset=" + self.offset()
          + "&length=" + self.length()
          + "&compression="+ self.compression()
          + "&mode=" + self.mode();
      });

      var change_length = function() {
        var length = self.end() - self.offset();
        if (length > max_size) {
          length = max_size;
        }
        self.length(length);
      };
      self.begin.subscribe(change_length);
      self.end.subscribe(change_length);

      var reloading = false;
      self.reload = function() {
        if (!reloading) {
          reloading = true;
          window.location.href = self.url();
        }
      };

      self.toggleDisables = function() {
        if (self.offset() + self.length() >= self.size()) {
          $(".next-block").addClass("disabled");
          $(".last-block").addClass("disabled");
        } else {
          $(".next-block").removeClass("disabled");
          $(".last-block").removeClass("disabled");
        }

        if (self.offset() <= 0) {
          $(".first-block").addClass("disabled");
          $(".previous-block").addClass("disabled");
        } else {
          $(".first-block").removeClass("disabled");
          $(".previous-block").removeClass("disabled");
        }
      };

      self.begin.subscribe(self.toggleDisables);
      self.end.subscribe(self.toggleDisables);

      var changeBlock = function(begin, end) {
        if (begin < self.size() && end > 0 && end > begin && !reloading) {
          self.begin(begin);
          self.end(end);
          self.toggleDisables();
          self.reload();
        }
      };

      self.nextBlock = function() {
        var offset = self.offset() + self.length();
        changeBlock(offset + 1, offset + self.length());
      };

      self.previousBlock = function() {
        var offset = ( self.offset() >= self.length() ) ? self.offset() - self.length() : 0;
        changeBlock(offset + 1, offset + self.length());
      };

      self.lastBlock = function() {
        var offset = self.size() - self.length();
        if (offset < 0) {
          offset = 0;
        }
        changeBlock(offset + 1, offset + self.length());
      };

      self.firstBlock = function() {
        changeBlock(1, self.length());
      }
    };
    var viewModel = new displayViewModel(
      "${ base_url }",
      "${view['compression']}",
      "${ view['mode'] }",
      ${view['offset'] + 1},
      ${view['end']},
      ${view['length']},
      ${stats['size']},
      ${view['max_chunk_size']}
    );

    $(window).load(function(){
      $("#refreshBtn").click(function(){
        window.location.reload();
      });
      ko.applyBindings(viewModel);
      viewModel.toggleDisables();
    });
  </script>

${ commonfooter(messages) | n,unicode }
