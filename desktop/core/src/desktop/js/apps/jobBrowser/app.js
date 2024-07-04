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

import huePubSub from 'utils/huePubSub';

import './components/hiveQueryPlan/webcomp';
import './components/queriesList/webcomp';
import './components/impalaQueries/webcomp';
import './eventListeners';
import JobBrowserViewModel from './knockout/JobBrowserViewModel';
import Job from './knockout/Job';
import { GLOBAL_ERROR_TOPIC, GLOBAL_INFO_TOPIC } from 'reactComponents/GlobalAlert/events';
import I18n from 'utils/i18n';

huePubSub.subscribe('app.dom.loaded', app => {
  if (app !== 'jobbrowser') {
    return;
  }

  $(document).ready(() => {
    const jobBrowserViewModel = new JobBrowserViewModel(false);
    const openJob = id => {
      if (jobBrowserViewModel.job() == null) {
        jobBrowserViewModel.job(new Job(jobBrowserViewModel, {}));
      }
      jobBrowserViewModel.job().id(id);
      jobBrowserViewModel.job().fetchJob();
    };

    ko.applyBindings(jobBrowserViewModel, $('#jobbrowserComponents')[0]);

    const loadHash = () => {
      if (window.location.pathname.indexOf('jobbrowser') > -1) {
        jobBrowserViewModel.load();
      }
    };

    window.onhashchange = () => loadHash();

    huePubSub.subscribe(
      'oozie.action.logs.click',
      widget => {
        $.get(
          widget.logsURL(),
          {
            format: 'link'
          },
          data => {
            const id = data.job || data.attemptid;
            if (id) {
              openJob(id);
            } else {
              huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: I18n('No log available') });
            }
          }
        );
      },
      'jobbrowser'
    );

    huePubSub.subscribe(
      'oozie.action.click',
      widget => {
        openJob(widget.externalId());
      },
      'jobbrowser'
    );

    huePubSub.subscribe(
      'browser.job.open.link',
      id => {
        openJob(id);
      },
      'jobbrowser'
    );

    huePubSub.subscribe(
      'app.gained.focus',
      app => {
        if (app === 'jobbrowser') {
          huePubSub.publish('graph.draw.arrows');
          loadHash();
        }
      },
      'jobbrowser'
    );

    const configUpdated = clusterConfig => {
      jobBrowserViewModel.appConfig(clusterConfig && clusterConfig['app_config']);
      jobBrowserViewModel.clusterType(clusterConfig && clusterConfig['cluster_type']);
      loadHash();
    };

    huePubSub.subscribe('cluster.config.set.config', configUpdated);
    huePubSub.publish('cluster.config.get.config', configUpdated);

    huePubSub.subscribe(
      'submit.rerun.popup.return',
      data => {
        huePubSub.publish(GLOBAL_INFO_TOPIC, { message: I18n('Rerun submitted.') });
        $('#rerun-modal').modal('hide');

        jobBrowserViewModel.job().apiStatus('RUNNING');
        jobBrowserViewModel.monitorJob(jobBrowserViewModel.job());
      },
      'jobbrowser'
    );
  });
});
