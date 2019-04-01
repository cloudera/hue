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

import Dropzone from 'dropzone';
import $ from 'jquery';
import ko from 'knockout';

import I18n from 'utils/i18n';

// TODO: Depends on Dropzone

ko.bindingHandlers.dropzone = {
  init: function(element, valueAccessor) {
    const value = ko.unwrap(valueAccessor());
    if (value.disabled) {
      return;
    }
    const options = {
      autoDiscover: false,
      maxFilesize: 5000000,
      previewsContainer: '#progressStatusContent',
      previewTemplate:
        '<div class="progress-row">' +
        '<span class="break-word" data-dz-name></span>' +
        '<div class="pull-right">' +
        '<span class="muted" data-dz-size></span>&nbsp;&nbsp;' +
        '<span data-dz-remove><a href="javascript:undefined;" title="' +
        I18n('Cancel upload') +
        '"><i class="fa fa-fw fa-times"></i></a></span>' +
        '<span style="display: none" data-dz-uploaded><i class="fa fa-fw fa-check muted"></i></span>' +
        '</div>' +
        '<div class="progress-row-bar" data-dz-uploadprogress></div>' +
        '</div>',
      sending: function() {
        $('.hoverMsg').addClass('hide');
        $('#progressStatus').removeClass('hide');
        $('#progressStatusBar').removeClass('hide');
        $('#progressStatus .progress-row').remove();
        $('#progressStatusBar div').css('width', '0');
      },
      uploadprogress: function(file, progress) {
        $('[data-dz-name]').each((cnt, item) => {
          if ($(item).text() === file.name) {
            $(item)
              .parents('.progress-row')
              .find('[data-dz-uploadprogress]')
              .width(progress.toFixed() + '%');
            if (progress.toFixed() === '100') {
              $(item)
                .parents('.progress-row')
                .find('[data-dz-remove]')
                .hide();
              $(item)
                .parents('.progress-row')
                .find('[data-dz-uploaded]')
                .show();
            }
          }
        });
      },
      totaluploadprogress: function(progress) {
        $('#progressStatusBar div').width(progress.toFixed() + '%');
      },
      canceled: function() {
        $.jHueNotify.info(I18n('The upload has been canceled'));
      },
      complete: function(file) {
        if (file.xhr.response !== '') {
          const response = JSON.parse(file.xhr.response);
          if (response && response.status != null) {
            if (response.status !== 0) {
              $(document).trigger('error', response.data);
              if (value.onError) {
                value.onError(file.name);
              }
            } else {
              $(document).trigger('info', response.path + ' ' + I18n('uploaded successfully'));
              if (value.onComplete) {
                value.onComplete(response.path);
              }
            }
          }
        }
      },
      queuecomplete: function() {
        window.setTimeout(() => {
          $('#progressStatus').addClass('hide');
          $('#progressStatusBar').addClass('hide');
          $('#progressStatusBar div').css('width', '0');
        }, 2500);
      },
      createImageThumbnails: false
    };

    $.extend(options, value);

    $(element).addClass('dropzone');

    new Dropzone(element, options);
  }
};
