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
import ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <div class="btn-group pull-right">
    <!-- ko if: window.IS_K8S_ONLY -->
      <a class="btn btn-flat" style="padding-right: 4px" title="${I18n(
        'Query browser'
      )}" data-bind="hueLink: '/jobbrowser#!queries', click: function() { huePubSub.publish('show.jobs.panel', {interface: 'queries'}); huePubSub.publish('hide.jobs.panel'); }">
        <span>${I18n('Queries')}</span>
      </a>
    <!-- /ko -->
    <!-- ko ifnot: window.IS_K8S_ONLY -->
      <a class="btn btn-flat" style="padding-right: 4px" title="${I18n(
        'Job browser'
      )}" data-bind="hueLink: '/jobbrowser#!jobs', click: function() { huePubSub.publish('hide.jobs.panel'); }">
        <span>${I18n(window.IS_EMBEDDED || window.IS_MULTICLUSTER_ONLY ? 'Queries' : 'Jobs')}</span>
      </a>
    <!-- /ko -->
    <button class="btn btn-flat btn-toggle-jobs-panel" title="${I18n(
      'Jobs preview'
    )}" data-bind="click: function() { huePubSub.publish('toggle.jobs.panel'); }, style: {'paddingLeft': jobCount() > 0 ? '0': '4px'}">
      <span class="jobs-badge" data-bind="visible: jobCount() > 0, text: jobCount"></span>
      <i class="fa fa-tasks"></i>
    </button>
  </div>
`;

const JB_CHECK_INTERVAL_IN_MILLIS = 30000;

class JobBrowserPanel {
  constructor(params) {
    const self = this;

    const $container = $(window.HUE_CONTAINER);
    const $jobsPanel = $('#jobsPanel');
    const $toggle = $('.btn-toggle-jobs-panel');

    const reposition = function() {
      $jobsPanel.css('top', $toggle.offset().top + $toggle.height() + 15 + 'px');
      $jobsPanel.css('left', $container.offset().left + $container.width() - 630 + 'px');
    };

    huePubSub.subscribe('hide.jobs.panel', () => {
      $(window).off('resize', reposition);
      $jobsPanel.hide();
    });

    huePubSub.subscribe('show.jobs.panel', options => {
      if (window.IS_K8S_ONLY) {
        huePubSub.publish('context.selector.set.cluster', 'impala');
      }

      huePubSub.publish('hide.history.panel');
      $(window).on('resize', reposition);
      reposition();
      $jobsPanel.show();
      huePubSub.publish('mini.jb.navigate', {
        section: options && options.interface ? options.interface : 'jobs',
        compute: options && options.compute
      });
      if (options && options.id) {
        huePubSub.publish('mini.jb.open.job', options.id);
      }
    });

    huePubSub.subscribe('toggle.jobs.panel', () => {
      if ($jobsPanel.is(':visible')) {
        huePubSub.publish('hide.jobs.panel');
      } else {
        huePubSub.publish('show.jobs.panel');
      }
    });

    self.jobCounts = ko.observable({ yarn: 0, schedules: 0 });
    self.jobCount = ko.pureComputed(() => {
      let total = 0;
      Object.keys(self.jobCounts()).forEach(value => {
        total += self.jobCounts()[value];
      });
      return total;
    });
    self.onePageViewModel = params.onePageViewModel;

    let lastYarnBrowserRequest = null;
    const checkYarnBrowserStatus = function() {
      return $.post('/jobbrowser/jobs/', {
        format: 'json',
        state: 'running',
        user: window.LOGGED_USERNAME
      })
        .done(data => {
          if (data != null && data.jobs != null) {
            huePubSub.publish('jobbrowser.data', data.jobs);
            self.jobCounts()['yarn'] = data.jobs.length;
            self.jobCounts.valueHasMutated();
          }
        })
        .fail(response => {
          console.log(response);
        });
    };
    let lastScheduleBrowserRequest = undefined;
    const checkScheduleBrowserStatus = function() {
      return $.post(
        '/jobbrowser/api/jobs',
        {
          interface: ko.mapping.toJSON('schedules'),
          filters: ko.mapping.toJSON([
            { text: 'user:' + window.LOGGED_USERNAME },
            { time: { time_value: 7, time_unit: 'days' } },
            { states: ['running'] },
            { pagination: { page: 1, offset: 1, limit: 1 } }
          ])
        },
        data => {
          if (data != null && data.total != null) {
            huePubSub.publish('jobbrowser.schedule.data', data.apps);
            self.jobCounts()['schedules'] = data.total;
            self.jobCounts.valueHasMutated();
          }
        }
      );
    };

    let checkJobBrowserStatusIdx = -1;
    const checkJobBrowserStatus = function() {
      lastYarnBrowserRequest = checkYarnBrowserStatus();
      if (window.ENABLE_QUERY_SCHEDULING) {
        lastScheduleBrowserRequest = checkScheduleBrowserStatus();
      }

      $.when
        .apply($, [lastYarnBrowserRequest, lastScheduleBrowserRequest])
        .done(() => {
          window.clearTimeout(checkJobBrowserStatusIdx);
          checkJobBrowserStatusIdx = window.setTimeout(
            checkJobBrowserStatus,
            JB_CHECK_INTERVAL_IN_MILLIS
          );
        })
        .fail(() => {
          window.clearTimeout(checkJobBrowserStatusIdx);
        });
    };

    // Load the mini jobbrowser
    $.ajax({
      url: '/jobbrowser/apps?is_embeddable=true&is_mini=true',
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-Requested-With', 'Hue');
      },
      dataType: 'html',
      success: function(response) {
        params.onePageViewModel.processHeaders(response).done(rawHtml => {
          $('#mini_jobbrowser').html(rawHtml);
          //ko.bindingHandlers.delayedOverflow.init($('#mini_jobbrowser')[0]);
        });
      }
    });

    if (!window.IS_EMBEDDED && !window.IS_K8S_ONLY) {
      checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);

      huePubSub.subscribe('check.job.browser', checkYarnBrowserStatus);
      huePubSub.subscribe('check.schedules.browser', checkScheduleBrowserStatus);
    }
  }
}

componentUtils.registerComponent('hue-job-browser-links', JobBrowserPanel, TEMPLATE);
