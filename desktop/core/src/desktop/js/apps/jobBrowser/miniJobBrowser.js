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

import { GLOBAL_INFO_TOPIC } from 'reactComponents/GlobalAlert/events';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

import './components/hiveQueryPlan/webcomp';
import './components/queriesList/webcomp';
import './components/impalaQueries/webcomp';
import './eventListeners';
import JobBrowserViewModel from './knockout/JobBrowserViewModel';
import Job from './knockout/Job';

export const initializeMiniJobBrowser = () => {
  const jobBrowserViewModel = new JobBrowserViewModel(true);
  const openJob = id => {
    if (jobBrowserViewModel.job() == null) {
      jobBrowserViewModel.job(new Job(jobBrowserViewModel, {}));
    }
    jobBrowserViewModel.job().id(id);
    jobBrowserViewModel.job().fetchJob();
  };

  ko.applyBindings(jobBrowserViewModel, $('#jobbrowserMiniComponents')[0]);

  const configUpdated = clusterConfig => {
    jobBrowserViewModel.appConfig(clusterConfig && clusterConfig['app_config']);
    jobBrowserViewModel.clusterType(clusterConfig && clusterConfig['cluster_type']);
  };

  huePubSub.subscribe('cluster.config.set.config', configUpdated);
  huePubSub.publish('cluster.config.get.config', configUpdated);

  huePubSub.subscribe('submit.rerun.popup.return-mini', () => {
    huePubSub.publish(GLOBAL_INFO_TOPIC, { message: I18n('Rerun submitted.') });
    $('#rerun-modal-mini').modal('hide');

    jobBrowserViewModel.job().apiStatus('RUNNING');
    jobBrowserViewModel.monitorJob(jobBrowserViewModel.job());
  });

  huePubSub.subscribe('mini.jb.navigate', options => {
    if (options.compute) {
      jobBrowserViewModel.compute(options.compute);
    }
    $('#jobsPanel .nav-pills li').removeClass('active');
    const interfaceName = jobBrowserViewModel.isValidInterface(options.section);
    $('#jobsPanel .nav-pills li[data-interface="' + interfaceName + '"]').addClass('active');
    jobBrowserViewModel.selectInterface(interfaceName);
  });

  huePubSub.subscribe('mini.jb.open.job', openJob);

  huePubSub.subscribe('mini.jb.expand', () => {
    if (jobBrowserViewModel.job()) {
      huePubSub.publish('open.link', '/jobbrowser/#!id=' + jobBrowserViewModel.job().id());
    } else {
      huePubSub.publish('open.link', '/jobbrowser/#!' + jobBrowserViewModel.interface());
    }
  });
};
