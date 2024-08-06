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
import deleteAllEmptyStringKeys from 'utils/string/deleteAllEmptyStringKeys';
import changeURL from 'utils/url/changeURL';
import Jobs from './Jobs';

export default class Job {
  constructor(vm, job) {
    this.vm = vm;
    this.suffix = this.vm.isMini() ? '-mini' : '';

    this.paginationPage = ko.observable(1);
    this.paginationOffset = ko.observable(1); // Starting index
    this.paginationResultPage = ko.observable(50);
    this.totalApps = ko.observable((job.properties && job.properties.total_actions) || 0);
    this.hasPagination = ko.computed(
      () =>
        this.totalApps() &&
        ['workflows', 'schedules', 'bundles'].indexOf(this.vm.interface()) !== -1
    );
    this.pagination = ko.pureComputed(() => ({
      page: this.paginationPage(),
      offset: this.paginationOffset(),
      limit: this.paginationResultPage()
    }));

    this.pagination.subscribe(() => {
      if (this.vm.interface() === 'schedules') {
        this.updateJob(false, true);
      }
    });

    this.showPreviousPage = ko.computed(() => this.paginationOffset() > 1);
    this.showNextPage = ko.computed(
      () =>
        this.totalApps() != null &&
        this.paginationOffset() + this.paginationResultPage() < this.totalApps()
    );

    this.id = ko.observable(job.id || null);
    if (!this.vm.isMini()) {
      this.id.subscribe(() => {
        huePubSub.publish('graph.stop.refresh.view');
      });
    }
    this.doc_url = ko.observable(job.doc_url || null);
    this.doc_url_modified = ko.computed(() => {
      const url = this.doc_url();
      if (window.KNOX_BASE_URL.length && window.URL && url) {
        // KNOX
        try {
          const parsedDocUrl = new URL(url);
          const parsedKnoxUrl = new URL(window.KNOX_BASE_URL);
          parsedDocUrl.hostname = parsedKnoxUrl.hostname;
          parsedDocUrl.protocol = parsedKnoxUrl.protocol;
          parsedDocUrl.port = parsedKnoxUrl.port;
          const service = url.indexOf('livy') >= 0 ? '/livy' : '/impalaui';
          parsedDocUrl.pathname = parsedKnoxUrl.pathname + service + parsedDocUrl.pathname;
          return parsedDocUrl.toString();
        } catch (e) {
          return url;
        }
      } else if (window.KNOX_BASE_PATH.length && window.URL) {
        // DWX
        const parsedKnoxUrl = new URL(window.KNOX_BASE_URL);
        const parsedDocUrl = new URL(url);
        const service = url.indexOf('livy') >= 0 ? '/livy' : '/impalaui';
        parsedDocUrl.pathname = parsedKnoxUrl.pathname + service + window.KNOX_BASE_PATH;
      } else {
        return url;
      }
    });
    this.name = ko.observable(job.name || job.id || null);
    this.type = ko.observable(job.type || null);
    this.applicationType = ko.observable(job.applicationType || '');

    this.status = ko.observable(job.status || null);
    this.apiStatus = ko.observable(job.apiStatus || null);
    this.progress = ko.observable(job.progress || null);
    this.isRunning = ko.computed(
      () => ['RUNNING', 'PAUSED'].indexOf(this.apiStatus()) !== -1 || job.isRunning
    );

    this.isRunning.subscribe(() => {
      // The JB page for jobs is split in two tables, "Running" and "Completed", this esentially unchecks any job
      // that moves from one table to the other.
      ko.utils.arrayRemoveItem(this.vm.jobs.selectedJobs(), this);
    });

    this.user = ko.observable(job.user || null);
    this.queue = ko.observable(job.queue || null);
    this.cluster = ko.observable(job.cluster || null);
    this.duration = ko.observable(job.duration || null);
    this.submitted = ko.observable(job.submitted || null);
    this.canWrite = ko.observable(!!job.canWrite || null);

    this.logActive = ko.observable('default');
    this.logsByName = ko.observable({});
    this.logsListDefaults = ko.observable(['default', 'stdout', 'stderr', 'syslog']);
    this.logsList = ko.observable(this.logsListDefaults());
    this.logs = ko.pureComputed(() => this.logsByName()[this.logActive()]);

    this.properties = komapping.fromJS(
      (job.properties &&
        Object.keys(job.properties).reduce((p, key) => {
          p[key] = '';
          return p;
        }, {})) || { properties: '' }
    );
    Object.keys(job.properties || []).reduce((p, key) => {
      p[key](job.properties[key]);
      return p;
    }, this.properties);
    this.mainType = ko.observable(this.vm.interface());
    this.lastEvent = ko.observable(job.lastEvent || '');

    this.syncCoorEndTimeDateUI = ko.observable(null);
    this.syncCoorEndTimeTimeUI = ko.observable(null);
    this.syncCoorPauseTimeDateUI = ko.observable(null);
    this.syncCoorPauseTimeTimeUI = ko.observable(null);
    this.syncCoorConcurrency = ko.observable(null);

    this.coordinatorActions = ko.pureComputed(() => {
      if (this.mainType().indexOf('schedule') !== -1 && this.properties['tasks']) {
        const apps = this.properties['tasks']().map(instance => {
          const job = new CoordinatorAction(this.vm, komapping.toJS(instance), this);
          job.properties = komapping.fromJS(instance);
          return job;
        });
        const instances = new Jobs(this.vm);
        instances.apps(apps);
        instances.isCoordinator(true);
        return instances;
      }
    });

    this.textFilter = ko
      .observable('')
      .extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 1000 } });
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
    this.statesFilter = ko.computed(() => {
      const checkedStates = ko.utils.arrayFilter(this.statesValuesFilter(), state => {
        return state.checked();
      });
      return ko.utils.arrayMap(checkedStates, state => {
        return state.value();
      });
    });
    this.typesValuesFilter = ko.observableArray([
      komapping.fromJS({ value: 'map', name: I18n('Map'), checked: false, klass: 'green' }),
      komapping.fromJS({ value: 'reduce', name: I18n('Reduce'), checked: false, klass: 'orange' })
    ]);
    this.typesFilter = ko.computed(() => {
      const checkedTypes = ko.utils.arrayFilter(this.typesValuesFilter(), type => {
        return type.checked();
      });
      return ko.utils.arrayMap(checkedTypes, type => {
        return type.value();
      });
    });
    this.filters = ko.pureComputed(() => [
      { text: this.textFilter() },
      { states: komapping.toJS(this.statesFilter()) },
      { types: komapping.toJS(this.typesFilter()) }
    ]);
    this.forceUpdatingJob = ko.observable(false);
    this.filters.subscribe(() => {
      if (this.type() === 'schedule') {
        this.updateJob(false, true);
      } else {
        this.fetchProfile('tasks');
      }
    });
    this.metadataFilter = ko.observable('');
    this.metadataFilter.subscribe(newValue => {
      const tableRow = $('#jobbrowserJobMetadataTable tbody tr');
      tableRow.removeClass('hide');
      tableRow.each(function () {
        if ($(this).text().toLowerCase().indexOf(newValue.toLowerCase()) === -1) {
          $(this).addClass('hide');
        }
      });
    });
    this.propertiesFilter = ko.observable('');
    this.propertiesFilter.subscribe(newValue => {
      const tableRow = $('#jobbrowserJobPropertiesTable tbody tr');
      tableRow.removeClass('hide');
      tableRow.each(function () {
        if ($(this).text().toLowerCase().indexOf(newValue.toLowerCase()) === -1) {
          $(this).addClass('hide');
        }
      });
    });

    this.rerunModalContent = ko.observable('');

    this.hasKill = ko.pureComputed(
      () =>
        this.type() &&
        ([
          'MAPREDUCE',
          'SPARK',
          'workflow',
          'schedule',
          'bundle',
          'QUERY',
          'TEZ',
          'YarnV2',
          'DDL',
          'schedule-hive',
          'celery-beat',
          'history'
        ].indexOf(this.type()) !== -1 ||
          this.type().indexOf('Data Warehouse') !== -1 ||
          this.type().indexOf('Altus') !== -1)
    );
    this.killEnabled = ko.pureComputed(() => {
      // Impala can kill queries that are finished, but not yet terminated
      return this.hasKill() && this.canWrite() && this.isRunning();
    });

    this.hasResume = ko.pureComputed(
      () =>
        ['workflow', 'schedule', 'bundle', 'schedule-hive', 'celery-beat', 'history'].indexOf(
          this.type()
        ) !== -1
    );
    this.resumeEnabled = ko.pureComputed(
      () => this.hasResume() && this.canWrite() && this.apiStatus() === 'PAUSED'
    );

    this.hasRerun = ko.pureComputed(
      () => ['workflow', 'schedule-task'].indexOf(this.type()) !== -1
    );

    this.rerunEnabled = ko.pureComputed(
      () => this.hasRerun() && this.canWrite() && !this.isRunning()
    );

    this.hasPause = ko.pureComputed(
      () =>
        ['workflow', 'schedule', 'bundle', 'celery-beat', 'schedule-hive', 'history'].indexOf(
          this.type()
        ) !== -1
    );

    this.pauseEnabled = ko.pureComputed(
      () => this.hasPause() && this.canWrite() && this.apiStatus() === 'RUNNING'
    );

    this.hasIgnore = ko.pureComputed(() => ['schedule-task'].indexOf(this.type()) !== -1);

    this.ignoreEnabled = ko.pureComputed(
      () => this.hasIgnore() && this.canWrite() && !this.isRunning()
    );

    this.loadingJob = ko.observable(false);
    this.lastFetchJobRequest = null;
    this.lastUpdateJobRequest = null;
    this.lastFetchLogsRequest = null;
    this.lastFetchProfileRequest = null;
    this.lastFetchStatusRequest = null;

    this.updateClusterWorkers = ko.observable(1);
    this.updateClusterAutoResize = ko.observable(false);
    this.updateClusterAutoResizeMin = ko.observable(1);
    this.updateClusterAutoResizeMax = ko.observable(3);
    this.updateClusterAutoResizeCpu = ko.observable(80);
    this.updateClusterAutoPause = ko.observable();

    this.clusterConfigModified = ko.pureComputed(
      () =>
        (this.updateClusterWorkers() > 0 &&
          this.updateClusterWorkers() !== this.properties['properties']['workerReplicas']()) ||
        this.updateClusterAutoResize() !== this.properties['properties']['workerAutoResize']()
    );

    this.workflowGraphLoaded = false;

    this.lastArrowsPosition = {
      top: 0,
      left: 0
    };
    this.initialArrowsDrawingCount = 0;
  }

  previousPage() {
    this.paginationOffset(this.paginationOffset() - this.paginationResultPage());
  }

  nextPage() {
    this.paginationOffset(this.paginationOffset() + this.paginationResultPage());
  }

  showSyncCoorModal() {
    this.syncCoorEndTimeDateUI(this.properties['endTimeDateUI']());
    this.syncCoorEndTimeTimeUI(this.properties['endTimeTimeUI']());
    this.syncCoorPauseTimeDateUI(this.properties['pauseTimeDateUI']());
    this.syncCoorPauseTimeTimeUI(this.properties['pauseTimeTimeUI']());
    this.syncCoorConcurrency(this.properties['concurrency']());

    $(`#syncCoordinatorModal${this.suffix}`).modal('show');
  }

  _fetchJob(callback) {
    if (this.vm.interface() === 'engines') {
      huePubSub.publish('context.selector.set.cluster', 'AltusV2');
      return;
    }

    return $.post(
      '/jobbrowser/api/job/' + this.vm.interface(),
      {
        cluster: komapping.toJSON(this.vm.compute),
        app_id: komapping.toJSON(this.id),
        interface: komapping.toJSON(this.vm.interface),
        pagination: komapping.toJSON(this.pagination),
        filters: komapping.toJSON(this.filters)
      },
      data => {
        if (data.status === 0) {
          if (data.app) {
            huePubSub.publish('jobbrowser.data', [data.app]);
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

  _rewriteKnoxUrls(data) {
    if (data?.app?.type === 'SPARK' && data?.app?.properties?.metadata) {
      data.app.properties.metadata.forEach(item => {
        if (item.name === 'trackingUrl') {
          /*
            Rewrite tracking url
            Sample trackingUrl: http://<yarn>:8088/proxy/application_1652826179847_0003/
            Knox URL: https://<knox-base>/yarnuiv2/redirect#/yarn-app/application_1652826179847_0003/attempts
          */
          const matches = item.value.match('(application_[0-9_]+)');
          if (matches && matches.length > 1) {
            const applicationId = matches[1];
            item.value =
              window.KNOX_BASE_URL + '/yarnuiv2/redirect#/yarn-app/' + applicationId + '/attempts';
          }
        }
      });
    }
  }

  onTableRowClick(event, id) {
    const openInNewTab = event && (event.which === 2 || event.metaKey || event.ctrlKey);
    const idToOpen = id || this.id();
    if (idToOpen && idToOpen !== '-') {
      if (openInNewTab) {
        const urlParts = window.location.toString().split('#');
        const newUrl = urlParts[0] + '#!id=' + idToOpen;
        window.open(newUrl, '_blank');
      } else {
        this.id(idToOpen);
        this.fetchJob();
      }
    }
  }

  fetchJob() {
    // TODO: Remove cancelActiveRequest from apiHelper when in webpack
    apiHelper.cancelActiveRequest(this.lastFetchJobRequest);
    apiHelper.cancelActiveRequest(this.lastUpdateJobRequest);

    this.loadingJob(true);

    let jobInterface = this.vm.interface();
    if (/application_/.test(this.id()) || /job_/.test(this.id()) || /attempt_/.test(this.id())) {
      jobInterface = 'jobs';
    }
    if (/oozie-\w+-W/.test(this.id())) {
      jobInterface = 'workflows';
    } else if (/oozie-\w+-C/.test(this.id())) {
      jobInterface = 'schedules';
    } else if (/oozie-\w+-B/.test(this.id())) {
      jobInterface = 'bundles';
    } else if (/celery-beat-\w+/.test(this.id())) {
      jobInterface = 'celery-beat';
    } else if (/schedule-hive-\w+/.test(this.id())) {
      jobInterface = 'schedule-hive';
    } else if (/altus:dataeng/.test(this.id()) && /:job:/.test(this.id())) {
      jobInterface = 'dataeng-jobs';
    } else if (/altus:dataeng/.test(this.id()) && /:cluster:/.test(this.id())) {
      jobInterface = 'dataeng-clusters';
    } else if (/altus:dataware:k8/.test(this.id()) && /:cluster:/.test(this.id())) {
      jobInterface = 'dataware2-clusters';
    } else if (/altus:dataware/.test(this.id()) && /:cluster:/.test(this.id())) {
      jobInterface = 'dataware-clusters';
    } else if (/[a-z0-9]{16}:[a-z0-9]{16}/.test(this.id())) {
      jobInterface = 'queries-impala';
    } else if (/hive_[a-z0-9]*_[a-z0-9]*/.test(this.id())) {
      jobInterface = 'queries-hive';
    } else if (/livy-[0-9]+/.test(this.id())) {
      jobInterface = 'livy-sessions';
    }

    jobInterface =
      jobInterface.indexOf('dataeng') || jobInterface.indexOf('dataware')
        ? jobInterface
        : this.vm.isValidInterface(jobInterface); // TODO: support multi cluster selection in isValidInterface
    this.vm.interface(jobInterface);

    this.lastFetchJobRequest = this._fetchJob(data => {
      if (data.status === 0) {
        if (window.KNOX_BASE_URL && window.KNOX_BASE_URL.length) {
          this._rewriteKnoxUrls(data);
        }

        this.vm.interface(jobInterface);
        this.vm.job(new Job(this.vm, data.app));
        if (window.location.hash !== '#!id=' + this.vm.job().id()) {
          changeURL('#!id=' + this.vm.job().id());
        }
        const crumbs = [];
        if (/^appattempt_/.test(this.vm.job().id())) {
          crumbs.push({
            id: this.vm.job().properties['app_id'],
            name: this.vm.job().properties['app_id'],
            type: 'app'
          });
        }
        if (/^attempt_/.test(this.vm.job().id())) {
          crumbs.push({
            id: this.vm.job().properties['app_id'],
            name: this.vm.job().properties['app_id'],
            type: 'app'
          });
          crumbs.push({
            id: this.vm.job().properties['task_id'],
            name: this.vm.job().properties['task_id'],
            type: 'task'
          });
        }
        if (/^task_/.test(this.vm.job().id())) {
          crumbs.push({
            id: this.vm.job().properties['app_id'],
            name: this.vm.job().properties['app_id'],
            type: 'app'
          });
        }
        if (/_executor_/.test(this.vm.job().id())) {
          crumbs.push({
            id: this.vm.job().properties['app_id'],
            name: this.vm.job().properties['app_id'],
            type: 'app'
          });
        }
        const oozieWorkflow = this.vm
          .job()
          .name()
          .match(/oozie:launcher:T=.+?:W=.+?:A=.+?:ID=(.+?-oozie-\w+-W)$/i);
        if (oozieWorkflow) {
          crumbs.push({ id: oozieWorkflow[1], name: oozieWorkflow[1], type: 'workflow' });
        }

        if (/-oozie-\w+-W@/.test(this.vm.job().id())) {
          crumbs.push({
            id: this.vm.job().properties['workflow_id'],
            name: this.vm.job().properties['workflow_id'],
            type: 'workflow'
          });
        } else if (/-oozie-\w+-W/.test(this.vm.job().id())) {
          if (this.vm.job().properties['bundle_id']()) {
            crumbs.push({
              id: this.vm.job().properties['bundle_id'](),
              name: this.vm.job().properties['bundle_id'](),
              type: 'bundle'
            });
          }
          if (this.vm.job().properties['coordinator_id']()) {
            crumbs.push({
              id: this.vm.job().properties['coordinator_id'](),
              name: this.vm.job().properties['coordinator_id'](),
              type: 'schedule'
            });
          }
        } else if (/-oozie-\w+-C/.test(this.vm.job().id())) {
          if (this.vm.job().properties['bundle_id']()) {
            crumbs.push({
              id: this.vm.job().properties['bundle_id'](),
              name: this.vm.job().properties['bundle_id'](),
              type: 'bundle'
            });
          }
        }

        if (this.vm.job().type() === 'SPARK_EXECUTOR') {
          crumbs.push({
            id: this.vm.job().id(),
            name: this.vm.job().properties['executor_id'](),
            type: this.vm.job().type()
          });
        } else {
          crumbs.push({
            id: this.vm.job().id(),
            name: this.vm.job().name(),
            type: this.vm.job().type()
          });
        }

        this.vm.resetBreadcrumbs(crumbs);
        // Show is still bound to old job, setTimeout allows knockout model change event done at begining of this method to sends it's notification
        setTimeout(() => {
          if (
            this.vm.job().mainType() === 'queries-impala' &&
            !$(`#queries-page-plan${this.suffix}`).parent().children().hasClass('active')
          ) {
            $(`a[href="#queries-page-plan${this.suffix}"]`).tab('show');
          }
        }, 0);
        if (
          !this.vm.isMini() &&
          this.vm.job().type() === 'workflow' &&
          !this.vm.job().workflowGraphLoaded
        ) {
          this.vm.job().updateWorkflowGraph();
        }
        if (this.vm.isMini()) {
          if (this.vm.job().type() === 'workflow') {
            this.vm.job().fetchProfile('properties');
            $(`a[href="#workflow-page-metadata${this.suffix}"]`).tab('show');
          }
          $(`#rerun-modal${this.suffix}`).on('shown', () => {
            // Replaces dark modal backdrop from the end of the body tag to the closer scope
            // in order to activate z-index effect.
            const rerunModalData = $(this).data('modal');
            rerunModalData.$backdrop.appendTo('#jobbrowserMiniComponents');
          });
          $(`#killModal${this.suffix}`).on('shown', () => {
            const killModalData = $(this).data('modal');
            killModalData.$backdrop.appendTo('#jobbrowserMiniComponents');
          });
        }

        this.vm.job().fetchLogs();
      } else {
        huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
      }
    }).always(() => {
      this.loadingJob(false);
    });
  }

  updateJob(updateLogs, forceUpdate) {
    huePubSub.publish('graph.refresh.view');
    const deferred = $.Deferred();
    if (this.vm.job() === this && (this.apiStatus() === 'RUNNING' || forceUpdate)) {
      apiHelper.cancelActiveRequest(this.lastUpdateJobRequest);
      if (forceUpdate) {
        this.forceUpdatingJob(true);
      }
      this.lastUpdateJobRequest = this._fetchJob(data => {
        const requests = [];
        if (['schedule', 'workflow'].indexOf(this.vm.job().type()) >= 0) {
          deleteAllEmptyStringKeys(data.app); // It's preferable for our backend to return empty strings for various values in order to initialize them, but they shouldn't overwrite any values that are currently set.
          let selectedIDs = [];
          if (this.vm.job().coordinatorActions()) {
            selectedIDs = this.vm
              .job()
              .coordinatorActions()
              .selectedJobs()
              .map(coordinatorAction => {
                return coordinatorAction.id();
              });
          }
          this.vm.job = komapping.fromJS(data.app, {}, this.vm.job);
          if (selectedIDs.length > 0) {
            this.vm
              .job()
              .coordinatorActions()
              .selectedJobs(
                this.vm
                  .job()
                  .coordinatorActions()
                  .apps()
                  .filter(coordinatorAction => selectedIDs.indexOf(coordinatorAction.id()) !== -1)
              );
          }
          if (this.vm.job().type() === 'schedule') {
            this.totalApps(data.app.properties.total_actions);
          }
        } else {
          requests.push(this.vm.job().fetchStatus());
        }
        if (updateLogs !== false) {
          requests.push(this.vm.job().fetchLogs(this.vm.job().logActive()));
        }
        const profile = $('div[data-jobType] .tab-content .active').data('profile');
        if (profile) {
          requests.push(this.vm.job().fetchProfile(profile));
        }
        $.when.apply(this, requests).done(() => {
          deferred.resolve();
        });
      }).always(() => {
        this.forceUpdatingJob(false);
      });
    }
    return deferred;
  }

  fetchLogs(name) {
    name = name || 'default';
    apiHelper.cancelActiveRequest(this.lastFetchLogsRequest);
    this.lastFetchLogsRequest = $.post(
      '/jobbrowser/api/job/logs?is_embeddable=false',
      {
        cluster: komapping.toJSON(this.vm.compute),
        app_id: komapping.toJSON(this.id),
        interface: komapping.toJSON(this.vm.interface),
        type: komapping.toJSON(this.type),
        name: komapping.toJSON(name)
      },
      data => {
        if (data.status === 0) {
          const result = this.logsByName();
          result[name] = data.logs.logs;
          this.logsByName(result);
          if (data.logs.logsList && data.logs.logsList.length) {
            const logsListDefaults = this.logsListDefaults();
            this.logsList(
              logsListDefaults.concat(
                data.logs.logsList.filter(log => {
                  return logsListDefaults.indexOf(log) < 0;
                })
              )
            );
          }
          const visibleJbPanel = $('.jb-panel pre:visible');
          if (visibleJbPanel.length > 0) {
            visibleJbPanel
              .css('overflow-y', 'auto')
              .height(
                Math.max(
                  200,
                  $(window).height() -
                    visibleJbPanel.offset().top -
                    $('.page-content').scrollTop() -
                    75
                )
              );
          }
        } else {
          huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
        }
      }
    );
    return this.lastFetchLogsRequest;
  }

  submitQueryProfileDownloadForm(name) {
    const $downloadForm = $(
      '<form method="POST" class="download-form" style="display: inline" action="' +
        window.HUE_BASE_URL +
        '/jobbrowser/api/job/profile"></form>'
    );

    $('<input type="hidden" name="csrfmiddlewaretoken" />')
      .val(window.CSRF_TOKEN)
      .appendTo($downloadForm);
    $('<input type="hidden" name="cluster" />')
      .val(komapping.toJSON(this.vm.cluster))
      .appendTo($downloadForm);
    $('<input type="hidden" name="app_id" />')
      .val(komapping.toJSON(this.id))
      .appendTo($downloadForm);
    $('<input type="hidden" name="interface" />')
      .val(komapping.toJSON(this.vm.interface))
      .appendTo($downloadForm);
    $('<input type="hidden" name="app_type" />')
      .val(komapping.toJSON(this.type))
      .appendTo($downloadForm);
    $('<input type="hidden" name="app_property" />')
      .val(komapping.toJSON(name))
      .appendTo($downloadForm);
    $('<input type="hidden" name="app_filters" />')
      .val(komapping.toJSON(this.filters))
      .appendTo($downloadForm);

    $('#downloadProgressModal').append($downloadForm);

    huePubSub.publish('ignore.next.unload');
    $downloadForm.submit();
  }

  fetchProfile(name, callback) {
    apiHelper.cancelActiveRequest(this.lastFetchProfileRequest);
    this.lastFetchProfileRequest = $.post(
      '/jobbrowser/api/job/profile',
      {
        cluster: komapping.toJSON(this.vm.compute),
        app_id: komapping.toJSON(this.id),
        interface: komapping.toJSON(this.vm.interface),
        app_type: komapping.toJSON(this.type),
        app_property: komapping.toJSON(name),
        app_filters: komapping.toJSON(this.filters)
      },
      data => {
        if (data.status === 0) {
          this.properties[name](data[name]);
          if (callback) {
            callback(data);
          }
        } else {
          huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
        }
      }
    );
    return this.lastFetchProfileRequest;
  }

  fetchStatus() {
    apiHelper.cancelActiveRequest(this.lastFetchStatusRequest);
    this.lastFetchStatusRequest = $.post(
      '/jobbrowser/api/job',
      {
        cluster: komapping.toJSON(this.vm.compute),
        app_id: komapping.toJSON(this.id),
        interface: komapping.toJSON(this.mainType)
      },
      data => {
        if (data.status === 0) {
          this.status(data.app.status);
          this.apiStatus(data.app.apiStatus);
          this.progress(data.app.progress);
          this.canWrite(data.app.canWrite);
        } else {
          huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
        }
      }
    );
    return this.lastFetchStatusRequest;
  }

  control(action) {
    if (action === 'rerun') {
      $.get(
        `/oozie/rerun_oozie_job/${this.id()}/?format=json${
          this.vm.isMini() ? '&is_mini=true' : ''
        }`,
        response => {
          $(`#rerun-modal${this.suffix}`).modal('show');
          this.rerunModalContent(response);
        }
      );
    } else if (action === 'sync_coordinator') {
      const $syncCoordinatorModal = $('#syncCoordinatorModal');
      const endTimeDateUI = $syncCoordinatorModal.find('#endTimeDateUI').val();
      const endTimeTimeUI = $syncCoordinatorModal.find('#endTimeTimeUI').val();
      let endTime = '';
      if (endTimeDateUI !== '' && endTimeTimeUI !== '') {
        endTime = endTimeDateUI + 'T' + endTimeTimeUI;
      }
      const pauseTimeDateUI = $syncCoordinatorModal.find('#pauseTimeDateUI').val();
      const pauseTimeTimeUI = $syncCoordinatorModal.find('#pauseTimeTimeUI').val();
      let pauseTime = '';
      if (pauseTimeDateUI !== '' && pauseTimeTimeUI !== '') {
        pauseTime = pauseTimeDateUI + 'T' + pauseTimeTimeUI;
      }

      const clear_pause_time = $syncCoordinatorModal.find('#id_clearPauseTime')[0].checked;
      const concurrency = $syncCoordinatorModal.find('#id_concurrency').val();

      $.post(
        '/oozie/manage_oozie_jobs/' + this.id() + '/change',
        {
          end_time: endTime,
          pause_time: pauseTime,
          clear_pause_time: clear_pause_time,
          concurrency: concurrency
        },
        data => {
          if (data.status === 0) {
            huePubSub.publish(GLOBAL_INFO_TOPIC, {
              message: I18n('Successfully updated Coordinator Job Properties')
            });
          } else {
            huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
          }
        }
      ).fail(xhr => {
        huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: xhr.responseText });
      });
    } else if (action === 'sync_workflow') {
      $.get(
        '/oozie/sync_coord_workflow/' + this.id(),
        {
          format: 'json'
        },
        data => {
          $(document).trigger('showSubmitPopup', data);
        }
      ).fail(xhr => {
        huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: xhr.responseText });
      });
    } else {
      this.vm.jobs._control([this.id()], action, data => {
        huePubSub.publish(GLOBAL_INFO_TOPIC, data);
        this.fetchStatus();
      });
    }
  }

  updateClusterShow() {
    this.updateClusterWorkers(this.properties['properties']['workerReplicas']());
    this.updateClusterAutoResize(this.properties['properties']['workerAutoResize']());
    if (this.properties['properties']['workerAutoResize']()) {
      this.updateClusterAutoResizeMin(this.properties['properties']['workerAutoResizeMin']());
      this.updateClusterAutoResizeMax(this.properties['properties']['workerAutoResizeMax']());
      this.updateClusterAutoResizeCpu(this.properties['properties']['workerAutoResizeCpu']());
    }
  }

  updateCluster() {
    $.post(
      '/metadata/api/analytic_db/update_cluster/',
      {
        is_k8: this.vm.interface().indexOf('dataware2-clusters') !== -1,
        cluster_name: this.id(),
        workers_group_size: this.updateClusterWorkers(),
        auto_resize_changed:
          this.updateClusterAutoResize() !== this.properties['properties']['workerAutoResize'](),
        auto_resize_enabled: this.updateClusterAutoResize(),
        auto_resize_min: this.updateClusterAutoResizeMin(),
        auto_resize_max: this.updateClusterAutoResizeMax(),
        auto_resize_cpu: this.updateClusterAutoResizeCpu()
      },
      () => {
        this.updateJob();
      }
    );
  }

  troubleshoot() {
    $.post(
      '/metadata/api/workload_analytics/get_operation_execution_details',
      {
        operation_id: komapping.toJSON(this.id())
      },
      () => {}
    );
  }

  redrawOnResize() {
    huePubSub.publish('graph.draw.arrows');
  }

  initialArrowsDrawing() {
    if (this.initialArrowsDrawingCount < 20) {
      this.initialArrowsDrawingCount++;
      huePubSub.publish('graph.draw.arrows');
      window.setTimeout(this.initialArrowsDrawing, 100);
    } else if (this.initialArrowsDrawingCount < 30) {
      this.initialArrowsDrawingCount++;
      huePubSub.publish('graph.draw.arrows');
      window.setTimeout(this.initialArrowsDrawing, 500);
    } else {
      this.initialArrowsDrawingCount = 0;
    }
  }

  updateWorkflowGraph() {
    huePubSub.publish('graph.stop.refresh.view');

    $('canvas').remove();

    if (this.vm.job().type() === 'workflow') {
      $(`#workflow-page-graph${this.suffix}`).html(
        '<div class="hue-spinner"><i class="fa fa-spinner fa-spin hue-spinner-center hue-spinner-xlarge"></i></div>'
      );
      $.ajax({
        url: '/oozie/list_oozie_workflow/' + this.vm.job().id(),
        data: {
          graph: true,
          element: `workflow-page-graph${this.suffix}`,
          is_jb2: true
        },
        beforeSend: xhr => {
          xhr.setRequestHeader('X-Requested-With', 'Hue');
        },
        dataType: 'html',
        success: response => {
          this.workflowGraphLoaded = true;

          huePubSub.publish('hue4.process.headers', {
            response: response,
            callback: r => {
              $(`#workflow-page-graph${this.suffix}`).html(r);
              this.initialArrowsDrawing();
              $(window).on('resize', this.redrawOnResize);
            }
          });
        }
      });
    }
  }
}

class CoordinatorAction extends Job {
  constructor(vm, job, coordinator) {
    super(vm, job);
    this.coordinator = coordinator;
    this.canWrite = ko.pureComputed(() => this.coordinator.canWrite());
    this.resumeEnabled = ko.pureComputed(() => false);
  }
}
