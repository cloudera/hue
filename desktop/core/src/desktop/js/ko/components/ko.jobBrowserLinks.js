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
import * as ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { initializeMiniJobBrowser } from '../../apps/jobBrowser/miniJobBrowser';
import DisposableComponent from './DisposableComponent';

export const NAME = 'hue-job-browser-links';

const TEMPLATE = `
  <div class="btn-group pull-right">
    <!-- ko if: window.IS_K8S_ONLY -->
      <a class="btn btn-flat" style="padding-right: 4px" title="${I18n(
        'Query browser'
      )}" data-bind="hueLink: '/jobbrowser#!queries', click: function() { huePubSub.publish('show.jobs.panel', {interface: 'queries'}); huePubSub.publish('hide.jobs.panel'); }">
        <span>${I18n('Queries')}</span>
      </a>
    <!-- /ko -->
    <!-- ko if: window.HAS_JOB_BROWSER && !window.getLastKnownConfig().has_computes -->
    <!-- ko ifnot: window.IS_K8S_ONLY -->
      <a class="btn btn-flat" style="padding-right: 4px" title="${I18n(
        'Job browser'
      )}" data-bind="hueLink: '/jobbrowser#!jobs', click: function() { huePubSub.publish('hide.jobs.panel'); }">
        <span>${I18n(window.IS_MULTICLUSTER_ONLY ? 'Queries' : 'Jobs')}</span>
      </a>
    <!-- /ko -->
    <button class="btn btn-flat btn-toggle-jobs-panel" title="${I18n(
      'Jobs preview'
    )}" data-bind="click: function() { huePubSub.publish('toggle.jobs.panel'); }, style: {'paddingLeft': jobCount() > 0 ? '0': '4px'}">
      <span class="jobs-badge" data-bind="visible: jobCount() > 0, text: jobCount"></span>
      <i class="fa fa-tasks"></i>
    </button>
    <!-- /ko -->
  </div>
`;

const JB_CHECK_INTERVAL_IN_MILLIS = 30000;

class JobBrowserPanel extends DisposableComponent {
  constructor(params) {
    super();
    const $container = $('body');

    this.initialized = false;

    const reposition = function () {
      const $jobsPanel = $('#jobsPanel');
      const $toggle = $('.btn-toggle-jobs-panel');
      $jobsPanel.css('top', $toggle.offset().top + $toggle.height() + 15 + 'px');
      $jobsPanel.css('left', $container.offset().left + $container.width() - 630 + 'px');
    };

    super.subscribe('hide.jobs.panel', () => {
      $(window).off('resize', reposition);
      $('#jobsPanel').hide();
    });

    super.subscribe('show.jobs.panel', options => {
      if (!this.initialized) {
        this.initialized = true;
        initializeMiniJobBrowser();
      }
      if (window.IS_K8S_ONLY) {
        huePubSub.publish('context.selector.set.cluster', 'impala');
      }

      huePubSub.publish('hide.history.panel');
      $(window).on('resize', reposition);
      reposition();
      $('#jobsPanel').show();
      huePubSub.publish('mini.jb.navigate', {
        section: options && options.interface ? options.interface : 'jobs',
        compute: options && options.compute
      });
      if (options && options.id) {
        huePubSub.publish('mini.jb.open.job', options.id);
      }
    });

    super.subscribe('toggle.jobs.panel', () => {
      if ($('#jobsPanel').is(':visible')) {
        huePubSub.publish('hide.jobs.panel');
      } else {
        huePubSub.publish('show.jobs.panel');
      }
    });

    this.jobCounts = ko.observable({ yarn: 0, schedules: 0, history: 0 });
    this.jobCount = ko.pureComputed(() => {
      let total = 0;
      Object.keys(this.jobCounts()).forEach(value => {
        total += this.jobCounts()[value];
      });
      return total;
    });
    this.onePageViewModel = params.onePageViewModel;

    let lastYarnBrowserRequest = null;
    const checkYarnBrowserStatus = () => {
      return $.post('/jobbrowser/jobs/', {
        format: 'json',
        state: 'running',
        user: window.LOGGED_USERNAME
      })
        .done(data => {
          if (data != null && data.jobs != null) {
            huePubSub.publish('jobbrowser.data', data.jobs);
            this.jobCounts()['yarn'] = data.jobs.length;
            this.jobCounts.valueHasMutated();
          }
        })
        .fail(response => {
          console.warn(response);
        });
    };
    let lastScheduleBrowserRequest = undefined;
    const checkScheduleBrowserStatus = () => {
      return $.post(
        '/scheduler/api/schedule/list',
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
            this.jobCounts()['schedules'] = data.total;
            this.jobCounts.valueHasMutated();
          }
        }
      );
    };
    let lastHistoryBrowserRequest = null;
    const checkHistoryBrowserStatus = () => {
      return $.post('/jobbrowser/api/jobs/history', {
        interface: ko.mapping.toJSON('history'),
        filters: ko.mapping.toJSON([
          { states: ['running'] },
          { text: 'user:' + window.LOGGED_USERNAME },
          { time: { time_value: 7, time_unit: 'days' } },
          { pagination: { page: 1, offset: 1, limit: 1 } }
        ])
      })
        .done(data => {
          if (data != null && data.apps != null) {
            this.jobCounts()['history'] = data.apps.length;
            this.jobCounts.valueHasMutated();
          }
        })
        .fail(response => {
          console.warn(response);
        });
    };

    let checkJobBrowserStatusIdx = -1;
    const checkJobBrowserStatus = function () {
      lastYarnBrowserRequest = checkYarnBrowserStatus();
      if (window.ENABLE_QUERY_SCHEDULING) {
        lastScheduleBrowserRequest = checkScheduleBrowserStatus();
      }
      if (window.ENABLE_HISTORY_V2) {
        lastHistoryBrowserRequest = checkHistoryBrowserStatus();
      }

      $.when
        .apply($, [lastYarnBrowserRequest, lastScheduleBrowserRequest, lastHistoryBrowserRequest])
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

    // Load the mini jobbrowser DOM and insert it in the #mini_jobrowser element
    // Any script or styles are also inserted in the header and thus loaded async.
    $.ajax({
      url: '/jobbrowser/apps?is_embeddable=true&is_mini=true',
      beforeSend: function (xhr) {
        xhr.setRequestHeader('X-Requested-With', 'Hue');
      },
      dataType: 'html',
      success: function (response) {
        params.onePageViewModel
          .processHeadersSecure(response)
          .done(({ rawHtml, scriptsToLoad }) => {
            $('#mini_jobbrowser').html(rawHtml);
            const loadScripts = scriptsToLoad.map(src =>
              params.onePageViewModel.loadScript_nonce(src)
            );
            Promise.all(loadScripts);
            //ko.bindingHandlers.delayedOverflow.init($('#mini_jobbrowser')[0]);
          });
      }
    });

    if (!window.IS_K8S_ONLY) {
      checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);

      super.subscribe('check.job.browser', checkYarnBrowserStatus);
      super.subscribe('check.schedules.browser', checkScheduleBrowserStatus);
      super.subscribe('check.history.browser', checkHistoryBrowserStatus);
    }
  }
}

componentUtils.registerComponent(NAME, JobBrowserPanel, TEMPLATE);
