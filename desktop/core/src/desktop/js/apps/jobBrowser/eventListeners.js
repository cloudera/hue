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

import $ from 'jquery';
import huePubSub from '../../utils/huePubSub';
import { GLOBAL_ERROR_TOPIC, GLOBAL_INFO_TOPIC } from 'reactComponents/GlobalAlert/events';

$(document).off('shown', '.jb-logs-link');
$(document).on('shown', '.jb-logs-link', e => {
  const dest = $(e.target).attr('href');
  if (dest.indexOf('logs') > -1 && $(dest).find('pre:visible').length > 0) {
    $(dest)
      .find('pre')
      .css('overflow-y', 'auto')
      .height(
        Math.max(
          200,
          $(window).height() -
            $(dest).find('pre').offset().top -
            $('.page-content').scrollTop() -
            75
        )
      );
  }
});

$(document).off('showSubmitPopup');
$(document).on('showSubmitPopup', (event, data) => {
  const syncWorkflowModal = $('#syncWorkflowModal');
  syncWorkflowModal.empty();
  syncWorkflowModal.html(data);
  syncWorkflowModal.modal('show');
  syncWorkflowModal.on('hidden', () => {
    huePubSub.publish('hide.datepicker');
  });

  syncWorkflowModal.find('.submit-form').on('submit', function (e) {
    e.preventDefault();
    $.ajax({
      type: 'POST',
      cache: false,
      url: $(this).attr('action'),
      data: $(this).serialize(),
      success: function (data) {
        $('#syncWorkflowModal').modal('hide');
        if (data && data.status === 0) {
          huePubSub.publish(GLOBAL_INFO_TOPIC, data);
        } else {
          huePubSub.publish(GLOBAL_ERROR_TOPIC, data);
        }
      },
      error: function (data) {
        $('#syncWorkflowModal').modal('hide');
        huePubSub.publish(GLOBAL_ERROR_TOPIC, data);
      }
    });
  });
});
