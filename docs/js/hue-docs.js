// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(document).ready(function () {
  $('.doc-title h1 a').html('<img src="../images/hue_logo.png" alt="Hue Logo">');
  $('.toc ul').treed();
  var $tocFilterContainer = $('<div>').addClass('toc-filter-container');
  $tocFilterContainer.prependTo($('.toc'));
  var $tocFilter = $('<input type="text">').addClass('form-control toc-filter').attr('placeholder', 'Filter Table of Content');
  $tocFilter.appendTo($tocFilterContainer);
  var tocTimeout = -1;
  $tocFilter.on('keyup', function (e) {
    if (![13, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
      window.clearTimeout(tocTimeout);
      tocTimeout = window.setTimeout(function () {
        $('.highlight').each(function () {
          $(this).replaceWith(this.childNodes);
        });
        $('.toc li a').highlight($tocFilter.val(), {
          bold: true,
          class: "highlight",
          ignoreCase: true,
          wholeWord: false
        });
        $('.toc li').each(function () {
          if ($(this).text().toLowerCase().indexOf($tocFilter.val().toLowerCase()) > -1) {
            $(this).show();
          }
          else {
            $(this).hide();
          }
        });
      }, 300);
    }
  });
  $(window).on('hashchange', function () {
    $('.toc a.highlighted').removeClass('highlighted');
    $('.toc a[href="' + window.location.hash + '"]').addClass('highlighted');
  });
});
