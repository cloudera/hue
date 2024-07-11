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

import { getLastKnownConfig } from 'config/hueConfig';
import { GLOBAL_ERROR_TOPIC } from 'reactComponents/GlobalAlert/events';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { withLocalStorage } from 'utils/storageUtils';
import changeURL from 'utils/url/changeURL';

import Job from './Job';
import Jobs from './Jobs';

export default class JobBrowserViewModel {
  constructor(isMiniJobBrowser) {
    this.assistAvailable = ko.observable(true);
    this.isLeftPanelVisible = ko.observable();
    withLocalStorage('assist.assist_panel_visible', this.isLeftPanelVisible, true);
    this.isLeftPanelVisible.subscribe(() => {
      huePubSub.publish('assist.forceRender');
    });

    this.appConfig = ko.observable();
    this.clusterType = ko.observable();
    this.isMini = ko.observable(isMiniJobBrowser);

    this.cluster = ko.observable();
    this.compute = ko.observable();
    this.compute.subscribe(() => {
      if (this.interface()) {
        this.jobs.fetchJobs();
      }
    });

    this.availableInterfaces = ko.pureComputed(() => {
      const isDialectEnabled = dialect =>
        this.appConfig()?.editor?.interpreter_names?.indexOf(dialect) >= 0;

      const historyInterfaceCondition = () => window.ENABLE_HISTORY_V2;

      const jobsInterfaceCondition = () =>
        !getLastKnownConfig().has_computes &&
        this.appConfig()?.browser?.interpreter_names.indexOf('yarn') !== -1 &&
        (!this.cluster() || this.cluster().type.indexOf('altus') === -1);

      const dataEngInterfaceCondition = () => this.cluster()?.type === 'altus-de';

      const enginesInterfaceCondition = () => this.cluster()?.type === 'altus-engines';

      const dataWarehouseInterfaceCondition = () => this.cluster()?.type === 'altus-dw';

      const dataWarehouse2InterfaceCondition = () => this.cluster()?.type === 'altus-dw2';

      const schedulerInterfaceCondition = () =>
        window.USER_HAS_OOZIE_ACCESS &&
        (!this.cluster() || this.cluster().type.indexOf('altus') === -1) &&
        this.appConfig()?.scheduler;

      const schedulerExtraInterfaceCondition = () =>
        !this.isMini() && schedulerInterfaceCondition();

      const schedulerBeatInterfaceCondition = () =>
        this.appConfig()?.scheduler?.interpreter_names.indexOf('celery-beat') !== -1;

      const livyInterfaceCondition = () =>
        !this.isMini() &&
        this.appConfig()?.editor &&
        (this.appConfig().editor.interpreter_names.indexOf('pyspark') !== -1 ||
          this.appConfig().editor.interpreter_names.indexOf('sparksql') !== -1);

      const queryInterfaceCondition = () =>
        window.ENABLE_QUERY_BROWSER &&
        !getLastKnownConfig().has_computes &&
        this.appConfig()?.editor.interpreter_names.indexOf('impala') !== -1 &&
        (!this.cluster() || this.cluster().type.indexOf('altus') === -1);

      const queryHiveInterfaceCondition = () => {
        return window.ENABLE_HIVE_QUERY_BROWSER && !getLastKnownConfig().has_computes;
      };

      const scheduleHiveInterfaceCondition = () => window.ENABLE_QUERY_SCHEDULING;

      const hiveQueriesInterfaceCondition = () =>
        window.ENABLE_QUERY_STORE && isDialectEnabled('hive');
      const impalaQueriesInterfaceCondition = () =>
        window.ENABLE_QUERY_STORE && isDialectEnabled('impala');

      const interfaces = [
        { interface: 'jobs', label: I18n('Jobs'), condition: jobsInterfaceCondition },
        { interface: 'dataeng-jobs', label: I18n('Jobs'), condition: dataEngInterfaceCondition },
        {
          interface: 'dataeng-clusters',
          label: I18n('Clusters'),
          condition: dataEngInterfaceCondition
        },
        {
          interface: 'dataware-clusters',
          label: I18n('Clusters'),
          condition: dataWarehouseInterfaceCondition
        },
        {
          interface: 'dataware2-clusters',
          label: I18n('Warehouses'),
          condition: dataWarehouse2InterfaceCondition
        },
        { interface: 'engines', label: '', condition: enginesInterfaceCondition },
        { interface: 'queries-impala', label: 'Impala', condition: queryInterfaceCondition },
        { interface: 'queries-hive', label: 'Hive', condition: queryHiveInterfaceCondition },
        {
          interface: 'schedule-hive',
          label: I18n('Hive Schedules'),
          condition: scheduleHiveInterfaceCondition
        },
        {
          interface: 'celery-beat',
          label: I18n('Scheduled Tasks'),
          condition: schedulerBeatInterfaceCondition
        },
        { interface: 'history', label: I18n('History'), condition: historyInterfaceCondition },
        {
          interface: 'workflows',
          label: I18n('Workflows'),
          condition: schedulerInterfaceCondition
        },
        {
          interface: 'schedules',
          label: I18n('Schedules'),
          condition: schedulerInterfaceCondition
        },
        {
          interface: 'bundles',
          label: I18n('Bundles'),
          condition: schedulerExtraInterfaceCondition
        },
        { interface: 'slas', label: I18n('SLAs'), condition: schedulerExtraInterfaceCondition },
        { interface: 'livy-sessions', label: 'Livy', condition: livyInterfaceCondition },
        {
          interface: 'hive-queries',
          label: I18n('Hive Queries'),
          condition: hiveQueriesInterfaceCondition
        },
        {
          interface: 'impala-queries',
          label: I18n('Impala Queries'),
          condition: impalaQueriesInterfaceCondition
        }
      ];

      return interfaces.filter(i => i.condition());
    });

    this.availableInterfaces.subscribe(newInterfaces => {
      if (
        this.interface() &&
        !newInterfaces.some(newInterface => newInterface.interface === this.interface())
      ) {
        this.selectInterface(newInterfaces[0]);
      }
    });

    this.slasLoadedOnce = false;
    this.slasLoading = ko.observable(true);

    this.oozieInfoLoadedOnce = false;
    this.oozieInfoLoading = ko.observable(true);

    this.interface = ko.observable();

    this.jobs = new Jobs(this);
    this.job = ko.observable();

    this.updateJobTimeout = -1;
    this.updateJobsTimeout = -1;
    this.jobUpdateCounter = 0;
    this.exponentialFactor = 1;

    this.job.subscribe(val => {
      this.monitorJob(val);
    });

    this.breadcrumbs = ko.observableArray([]);

    this.resetBreadcrumbs();
  }

  contextId(id) {
    if (this.isMini()) {
      return id + '-mini';
    }
    return id;
  }

  showTab(anchor) {
    $(`a[href='${this.contextId(anchor)}']`).tab('show');
  }

  loadSlaPage() {
    if (!this.slasLoadedOnce) {
      $.ajax({
        url: '/oozie/list_oozie_sla/?is_embeddable=true',
        beforeSend: xhr => {
          xhr.setRequestHeader('X-Requested-With', 'Hue');
        },
        dataType: 'html',
        success: response => {
          this.slasLoading(false);
          $('#slas').html(response);
        }
      });
    }
  }

  loadOozieInfoPage() {
    if (!this.oozieInfoLoadedOnce) {
      this.oozieInfoLoadedOnce = true;
      this.oozieInfoLoading(true);
      $.ajax({
        url: '/oozie/list_oozie_info/?is_embeddable=true',
        beforeSend: xhr => {
          xhr.setRequestHeader('X-Requested-With', 'Hue');
        },
        dataType: 'html'
      })
        .done(response => {
          $('#oozieInfo').html(response);
        })
        .fail(err => {
          this.oozieInfoLoadedOnce = false;
          this.selectInterface('schedules');
          huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: I18n('Failed loading Oozie Info.') });
        })
        .always(() => {
          this.oozieInfoLoading(false);
        });
    }
  }

  isValidInterface(name) {
    const flatAvailableInterfaces = this.availableInterfaces().map(i => i.interface);
    if (flatAvailableInterfaces.indexOf(name) !== -1 || name === 'oozie-info') {
      return name;
    } else {
      return flatAvailableInterfaces[0];
    }
  }

  selectInterface(selectedInterface) {
    const validSelectedInterface = this.isValidInterface(selectedInterface);
    this.interface(validSelectedInterface);
    this.resetBreadcrumbs();

    if (!this.isMini()) {
      huePubSub.publish('graph.stop.refresh.view');
      if (window.location.hash !== '#!' + validSelectedInterface) {
        changeURL('#!' + validSelectedInterface);
      }
    }
    this.jobs.selectedJobs([]);
    this.job(null);

    if (validSelectedInterface === 'slas' && !this.isMini()) {
      this.loadSlaPage();
    } else if (validSelectedInterface === 'oozie-info' && !this.isMini()) {
      this.loadOozieInfoPage();
    } else if (
      validSelectedInterface !== 'hive-queries' ||
      validSelectedInterface !== 'impala-queries'
    ) {
      this.jobs.fetchJobs();
    }
  }

  onClusterSelect() {
    let interfaceToSet = this.interface();
    if (
      !this.availableInterfaces().some(
        availableInterface => availableInterface.interface === interfaceToSet
      )
    ) {
      interfaceToSet = this.availableInterfaces()[0].interface;
    }
    this.selectInterface(interfaceToSet);
  }

  monitorJob(job) {
    window.clearTimeout(this.updateJobTimeout);
    window.clearTimeout(this.updateJobsTimeout);
    this.jobUpdateCounter = 0;
    this.exponentialFactor = 1;
    if (
      this.interface() &&
      this.interface() !== 'slas' &&
      this.interface() !== 'oozie-info' &&
      this.interface !== 'hive-queries' &&
      this.interface !== 'impala-queries'
    ) {
      if (job) {
        if (job.apiStatus() === 'RUNNING') {
          const _updateJob = () => {
            this.jobUpdateCounter++;
            const updateLogs = this.jobUpdateCounter % this.exponentialFactor === 0;
            if (updateLogs && this.exponentialFactor < 50) {
              this.exponentialFactor *= 2;
            }
            const def = job.updateJob(updateLogs);
            if (def) {
              def.done(() => {
                this.updateJobTimeout = setTimeout(
                  _updateJob,
                  window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS
                );
              });
            }
          };
          this.updateJobTimeout = setTimeout(_updateJob, window.JB_SINGLE_CHECK_INTERVAL_IN_MILLIS);
        }
      } else {
        const _updateJobs = () => {
          const updateRequest = this.jobs.updateJobs();
          if (updateRequest?.done) {
            updateRequest.done(() => {
              setTimeout(_updateJobs, window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS);
            });
          }
        };
        this.updateJobsTimeout = setTimeout(_updateJobs, window.JB_MULTI_CHECK_INTERVAL_IN_MILLIS);
      }
    }
  }

  resetBreadcrumbs(extraCrumbs) {
    let crumbs = [{ id: '', name: this.interface(), type: this.interface() }];
    if (extraCrumbs) {
      crumbs = crumbs.concat(extraCrumbs);
    }
    this.breadcrumbs(crumbs);
  }

  getHDFSPath(path) {
    if (path.startsWith('hdfs://')) {
      const bits = path.substr(7).split('/');
      bits.shift();
      return '/' + bits.join('/');
    }
    return path;
  }

  formatProgress(progress) {
    if (typeof progress === 'function') {
      progress = progress();
    }
    if (!isNaN(progress)) {
      return Math.round(progress * 100) / 100 + '%';
    }
    return progress;
  }

  load() {
    let h = window.location.hash;
    if (!this.isMini()) {
      huePubSub.publish('graph.stop.refresh.view');
    }

    h = h.indexOf('#!') === 0 ? h.substr(2) : '';
    switch (h) {
      case '':
        h = 'jobs';
      case 'slas':
      case 'oozie-info':
      case 'jobs':
      case 'queries-impala':
      case 'queries-hive':
      case 'celery-beat':
      case 'schedule-hive':
      case 'history':
      case 'workflows':
      case 'schedules':
      case 'bundles':
      case 'dataeng-clusters':
      case 'dataware-clusters':
      case 'dataware2-clusters':
      case 'engines':
      case 'dataeng-jobs':
      case 'livy-sessions':
      case 'hive-queries':
      case 'impala-queries':
        this.selectInterface(h);
        break;
      default:
        if (h.indexOf('id=') === 0 && !this.isMini()) {
          new Job(this, { id: h.substr(3) }).fetchJob();
        } else {
          this.selectInterface('reset');
        }
    }
  }
}
