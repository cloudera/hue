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
import komapping from 'knockout.mapping';

import apiHelper from 'api/apiHelper';
import { GLOBAL_ERROR_TOPIC, GLOBAL_INFO_TOPIC } from 'reactComponents/GlobalAlert/events';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import Job from './Job';

export default class Jobs {
  constructor(vm) {
    this.vm = vm;
    this.apps = ko.observableArray().extend({ rateLimit: 50 });
    this.runningApps = ko.pureComputed(() => this.apps().filter(app => app.isRunning()));
    this.finishedApps = ko.pureComputed(() => this.apps().filter(app => !app.isRunning()));
    this.totalApps = ko.observable(null);
    this.isCoordinator = ko.observable(false);

    this.loadingJobs = ko.observable(false);
    this.selectedJobs = ko.observableArray();

    this.hasKill = ko.pureComputed(
      () =>
        !this.isCoordinator() &&
        [
          'jobs',
          'workflows',
          'schedules',
          'bundles',
          'queries-impala',
          'dataeng-jobs',
          'dataeng-clusters',
          'dataware-clusters',
          'dataware2-clusters',
          'celery-beat',
          'schedule-hive',
          'history'
        ].indexOf(this.vm.interface()) !== -1
    );
    this.killEnabled = ko.pureComputed(
      () =>
        this.hasKill() &&
        this.selectedJobs().length &&
        this.selectedJobs().every(job => job.killEnabled())
    );

    this.hasResume = ko.pureComputed(
      () =>
        !this.isCoordinator() &&
        [
          'workflows',
          'schedules',
          'bundles',
          'dataware2-clusters',
          'celery-beat',
          'schedule-hive',
          'history'
        ].indexOf(this.vm.interface()) !== -1
    );
    this.resumeEnabled = ko.pureComputed(
      () =>
        this.hasResume() &&
        this.selectedJobs().length &&
        this.selectedJobs().every(job => job.resumeEnabled())
    );

    this.hasRerun = ko.pureComputed(() => this.isCoordinator());
    this.rerunEnabled = ko.pureComputed(() => {
      const validSelectionCount =
        this.selectedJobs().length === 1 ||
        (this.selectedJobs().length > 1 && this.vm.interface() === 'schedules');
      return (
        this.hasRerun() &&
        validSelectionCount &&
        this.selectedJobs().every(job => job.rerunEnabled())
      );
    });

    this.hasPause = ko.pureComputed(
      () =>
        !this.isCoordinator() &&
        [
          'workflows',
          'schedules',
          'bundles',
          'dataware2-clusters',
          'celery-beat',
          'schedule-hive',
          'history'
        ].indexOf(this.vm.interface()) !== -1
    );
    this.pauseEnabled = ko.pureComputed(
      () =>
        this.hasPause() &&
        this.selectedJobs().length &&
        this.selectedJobs().every(job => job.pauseEnabled())
    );

    this.hasIgnore = ko.pureComputed(() => this.isCoordinator());
    this.ignoreEnabled = ko.pureComputed(
      () =>
        this.hasIgnore() &&
        this.selectedJobs().length &&
        this.selectedJobs().every(job => job.ignoreEnabled())
    );

    this.textFilter = ko.observable(`user:${window.LOGGED_USERNAME} `).extend({
      rateLimit: {
        method: 'notifyWhenChangesStop',
        timeout: 1000
      }
    });
    this.statesValuesFilter = ko.observableArray([
      komapping.fromJS({
        value: 'completed',
        name: I18n('Succeeded'),
        checked: false,
        klass: 'green'
      }),
      komapping.fromJS({
        value: 'running',
        name: I18n('Running'),
        checked: false,
        klass: 'orange'
      }),
      komapping.fromJS({ value: 'failed', name: I18n('Failed'), checked: false, klass: 'red' })
    ]);

    this.statesFilter = ko.computed(() =>
      this.statesValuesFilter()
        .filter(state => state.checked())
        .map(state => state.value())
    );
    this.timeValueFilter = ko.observable(7).extend({ throttle: 500 });
    this.timeUnitFilter = ko.observable('days').extend({ throttle: 500 });
    this.timeUnitFilterUnits = ko.observable([
      { value: 'days', name: I18n('days') },
      { value: 'hours', name: I18n('hours') },
      { value: 'minutes', name: I18n('minutes') }
    ]);

    this.hasPagination = ko.computed(
      () => ['workflows', 'schedules', 'bundles'].indexOf(this.vm.interface()) !== -1
    );
    this.paginationPage = ko.observable(1);
    this.paginationOffset = ko.observable(1); // Starting index
    this.paginationResultPage = ko.observable(100);
    this.pagination = ko.computed(() => ({
      page: this.paginationPage(),
      offset: this.paginationOffset(),
      limit: this.paginationResultPage()
    }));

    this.showPreviousPage = ko.computed(() => this.paginationOffset() > 1);
    this.showNextPage = ko.computed(
      () =>
        this.totalApps() && this.paginationOffset() + this.paginationResultPage() < this.totalApps()
    );

    this.searchFilters = ko.pureComputed(() => [
      { text: this.textFilter() },
      { time: { time_value: this.timeValueFilter(), time_unit: this.timeUnitFilter() } },
      { states: komapping.toJS(this.statesFilter()) }
    ]);
    this.searchFilters.subscribe(() => {
      this.paginationOffset(1);
    });
    this.paginationFilters = ko.pureComputed(() => [{ pagination: this.pagination() }]);
    this.filters = ko.pureComputed(() => this.searchFilters().concat(this.paginationFilters()));
    this.filters.subscribe(() => {
      this.fetchJobs();
    });

    this.lastFetchJobsRequest = null;
    this.lastUpdateJobsRequest = null;
    this.showJobCountBanner = ko.pureComputed(() => this.apps().length === window.MAX_JOB_FETCH);

    this.createClusterShow = ko.observable(false);
    this.createClusterName = ko.observable('');
    this.createClusterWorkers = ko.observable(1);
    this.createClusterShowWorkers = ko.observable(false);
    this.createClusterAutoResize = ko.observable(false);
    this.createClusterAutoPause = ko.observable(false);
  }

  _control(app_ids, action, callback) {
    $.post(
      '/jobbrowser/api/job/action/' + this.vm.interface() + '/' + action,
      {
        app_ids: komapping.toJSON(app_ids),
        interface: komapping.toJSON(this.vm.interface),
        operation: komapping.toJSON({ action: action })
      },
      data => {
        if (data.status === 0) {
          if (callback) {
            callback(data);
          }
          if (this.vm.interface().indexOf('clusters') !== -1 && action === 'kill') {
            huePubSub.publish('context.catalog.refresh');
            this.selectedJobs([]);
          }
        } else {
          huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
        }
      }
    ).always(() => {});
  }

  previousPage() {
    this.paginationOffset(this.paginationOffset() - this.paginationResultPage());
  }

  nextPage() {
    this.paginationOffset(this.paginationOffset() + this.paginationResultPage());
  }

  _fetchJobs(callback) {
    return $.post(
      '/jobbrowser/api/jobs/' + this.vm.interface(),
      {
        cluster: komapping.toJSON(this.vm.compute),
        interface: komapping.toJSON(this.vm.interface),
        filters: komapping.toJSON(this.filters)
      },
      data => {
        if (data.status === 0) {
          if (data.apps?.length) {
            huePubSub.publish('jobbrowser.data', data.apps);
          }
          if (callback) {
            callback(data);
          }
        } else {
          huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
        }
      }
    );
  }

  fetchJobs() {
    if (this.vm.interface() === 'hive-queries' || this.vm.interface() === 'impala-queries') {
      return;
    }

    apiHelper.cancelActiveRequest(this.lastUpdateJobsRequest);
    apiHelper.cancelActiveRequest(this.lastFetchJobsRequest);

    this.loadingJobs(true);
    this.vm.job(null);
    this.lastFetchJobsRequest = this._fetchJobs(data => {
      const apps = [];
      if (data?.apps) {
        data.apps.forEach(job => {
          apps.push(new Job(this.vm, job));
        });
      }
      this.apps(apps);
      this.totalApps(data?.total || 0);
    }).always(() => {
      this.loadingJobs(false);
    });
  }

  updateJobs() {
    if (this.vm.interface() === 'hive-queries' || this.vm.interface() === 'impala-queries') {
      return;
    }

    apiHelper.cancelActiveRequest(this.lastUpdateJobsRequest);

    this.lastFetchJobsRequest = this._fetchJobs(data => {
      if (data?.apps) {
        let i = 0,
          j = 0;
        const newJobs = [];

        while ((this.apps().length === 0 || i < this.apps().length) && j < data.apps.length) {
          // Nothing displayed or compare existing
          if (this.apps().length === 0 || this.apps()[i].id() !== data.apps[j].id) {
            // New Job
            newJobs.unshift(new Job(this.vm, data.apps[j]));
            j++;
          } else {
            // Updated jobs
            if (this.apps()[i].status() !== data.apps[j].status) {
              this.apps()[i].status(data.apps[j].status);
              this.apps()[i].apiStatus(data.apps[j].apiStatus);
              this.apps()[i].canWrite(data.apps[j].canWrite);
            }
            i++;
            j++;
          }
        }

        if (i < this.apps().length) {
          this.apps.splice(i, this.apps().length - i);
        }

        newJobs.forEach(job => {
          this.apps.unshift(job);
        });

        this.totalApps(data.total);
      }
    });
    return this.lastFetchJobsRequest;
  }

  createClusterFormReset() {
    this.createClusterName('');
    this.createClusterWorkers(1);
    this.createClusterAutoResize(false);
    this.createClusterAutoPause(false);
  }

  createCluster() {
    if (this.vm.interface().indexOf('dataeng') !== -1) {
      $.post(
        '/metadata/api/dataeng/create_cluster/',
        {
          cluster_name: 'cluster_name',
          cdh_version: 'CDH515',
          public_key: 'public_key',
          instance_type: 'm4.xlarge',
          environment_name:
            'crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:analytics/236ebdda-18bd-428a-9d2b-cd6973d42946',
          workers_group_size: '3',
          namespace_name:
            'crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:analytics/7ea35fe5-dbc9-4b17-92b1-97a1ab32e410'
        },
        () => {
          this.updateJobs();
          huePubSub.publish('context.catalog.refresh');
        }
      );
    } else {
      $.post(
        '/metadata/api/analytic_db/create_cluster/',
        {
          is_k8: this.vm.interface().indexOf('dataware2-clusters') !== -1,
          cluster_name: this.createClusterName(),
          cluster_hdfs_host: 'hdfs-namenode',
          cluster_hdfs_port: 9820,
          cdh_version: 'CDH515',
          public_key: 'public_key',
          instance_type: 'm4.xlarge',
          environment_name:
            'crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:jheyming-secure/b4e6d99a-261f-4ada-9b4a-576aa0af8979',
          workers_group_size: this.createClusterWorkers(),
          namespace_name:
            'crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:analytics/7ea35fe5-dbc9-4b17-92b1-97a1ab32e410'
        },
        () => {
          this.createClusterFormReset();
          this.updateJobs();
          huePubSub.publish('context.catalog.refresh');
        }
      );
    }
    this.createClusterShow(false);
  }

  control(action) {
    const suffix = this.vm.isMini() ? '-mini' : '';
    if (action === 'rerun') {
      $.get(
        `/oozie/rerun_oozie_coord/${this.vm.job().id()}/?format=json${
          this.vm.isMini() ? '&is_mini=true' : ''
        }`,
        response => {
          $(`#rerun-modal${suffix}`).modal('show');
          this.vm.job().rerunModalContent(response);
          // Force Knockout to handle the update of rerunModalContent before trying to modify its DOM
          ko.tasks.runEarly();

          const frag = document.createDocumentFragment();
          this.vm
            .job()
            .coordinatorActions()
            .selectedJobs()
            .forEach(item => {
              const option = $('<option>', {
                value: item.properties.number(),
                selected: true
              });
              option.appendTo($(frag));
            });
          $(`#id_actions${suffix}`).find('option').remove();
          $(frag).appendTo(`#id_actions${suffix}`);
        }
      );
    } else if (action === 'ignore') {
      $.post(
        '/oozie/manage_oozie_jobs/' + this.vm.job().id() + '/ignore',
        {
          actions: this.vm
            .job()
            .coordinatorActions()
            .selectedJobs()
            .map(wf => wf.properties.number())
            .join(' ')
        },
        () => {
          this.vm.job().apiStatus('RUNNING');
          this.vm.job().updateJob();
        }
      );
    } else {
      this._control(
        this.selectedJobs().map(job => job.id()),
        action,
        data => {
          huePubSub.publish(GLOBAL_INFO_TOPIC, data);
          this.updateJobs();
        }
      );
    }
  }
}
