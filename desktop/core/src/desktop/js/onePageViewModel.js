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
import _ from 'lodash';
import ko from 'knockout';
import page from 'page';

import hueUtils from 'utils/hueUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

class OnePageViewModel {
  constructor() {
    const self = this;

    self.embeddable_cache = {};
    self.currentApp = ko.observable();
    self.currentContextParams = ko.observable(null);
    self.currentQueryString = ko.observable(null);
    self.isLoadingEmbeddable = ko.observable(false);
    self.extraEmbeddableURLParams = ko.observable('');

    self.getActiveAppViewModel = function(callback) {
      const checkInterval = window.setInterval(() => {
        const $koElement = $('#' + self.currentApp() + 'Components');
        if (
          $koElement.length > 0 &&
          ko.dataFor($koElement[0]) &&
          !(ko.dataFor($koElement[0]) instanceof OnePageViewModel)
        ) {
          window.clearInterval(checkInterval);
          callback(ko.dataFor($koElement[0]));
        }
      }, 25);
    };

    self.changeEditorType = function(type) {
      self.getActiveAppViewModel(viewModel => {
        if (viewModel && viewModel.selectedNotebook) {
          hueUtils.waitForObservable(viewModel.selectedNotebook, () => {
            if (viewModel.editorType() !== type) {
              viewModel.selectedNotebook().selectedSnippet(type);
              viewModel.editorType(type);
              viewModel.newNotebook(type);
            }
          });
        }
      });
    };

    self.currentApp.subscribe(newApp => {
      huePubSub.publish('set.current.app.name', newApp);
      self.getActiveAppViewModel(viewModel => {
        huePubSub.publish('set.current.app.view.model', viewModel);
      });
    });

    huePubSub.subscribe('get.current.app.view.model', () => {
      self.getActiveAppViewModel(viewModel => {
        huePubSub.publish('set.current.app.view.model', viewModel);
      });
    });

    huePubSub.subscribe('get.current.app.name', () => {
      huePubSub.publish('set.current.app.name', self.currentApp());
    });

    huePubSub.subscribe('open.editor.query', uuid => {
      self.loadApp('editor');
      self.getActiveAppViewModel(viewModel => {
        viewModel.openNotebook(uuid);
      });
    });

    huePubSub.subscribe('open.importer.query', data => {
      self.loadApp('importer');
      self.getActiveAppViewModel(viewModel => {
        hueUtils.waitForVariable(viewModel.createWizard, () => {
          hueUtils.waitForVariable(viewModel.createWizard.prefill, () => {
            viewModel.createWizard.prefill.source_type(data['source_type']);
            viewModel.createWizard.prefill.target_type(data['target_type']);
            viewModel.createWizard.prefill.target_path(data['target_path']);
            viewModel.createWizard.destination.outputFormat(data['target_type']);
          });
          hueUtils.waitForVariable(viewModel.createWizard.source.query, () => {
            viewModel.createWizard.source.query({ id: data.id, name: data.name });
          });
          hueUtils.waitForVariable(viewModel.createWizard.loadSampleData, () => {
            viewModel.createWizard.loadSampleData(data);
          });
        });
      });
    });

    huePubSub.subscribe('resize.form.actions', () => {
      document.styleSheets[0].addRule(
        '.form-actions',
        'width: ' + $('.page-content').width() + 'px'
      );
      if ($('.content-panel:visible').length > 0) {
        document.styleSheets[0].addRule('.form-actions', 'margin-left: -11px !important');
      }
    });

    huePubSub.subscribe('split.panel.resized', () => {
      huePubSub.publish('resize.form.actions');
      huePubSub.publish('resize.plotly.chart');
    });

    huePubSub.publish('resize.form.actions');

    huePubSub.subscribe('open.editor.new.query', statementOptions => {
      self.loadApp('editor'); // Should open in Default

      self.getActiveAppViewModel(viewModel => {
        const editorType = statementOptions['type'] || 'hive'; // Next: use file extensions and default type of Editor for SQL
        viewModel.newNotebook(editorType, () => {
          self.changeEditorType(editorType);

          if (statementOptions['statementPath']) {
            viewModel
              .selectedNotebook()
              .snippets()[0]
              .statementType(statementOptions['statementType']);
            viewModel
              .selectedNotebook()
              .snippets()[0]
              .statementPath(statementOptions['statementPath']);
          }
          if (statementOptions['directoryUuid']) {
            viewModel.selectedNotebook().directoryUuid(statementOptions['directoryUuid']);
          }
        });
      });
    });

    const loadedJs = [];
    const loadedCss = [];
    const loadedApps = [];

    $('script[src]').each(function() {
      loadedJs.push($(this).attr('src'));
    });

    $('link[href]').each(function() {
      loadedCss.push($(this).attr('href'));
    });

    const loadScript = function(scriptUrl) {
      const deferred = $.Deferred();
      $.ajax({
        url: scriptUrl,
        converters: {
          'text script': function(text) {
            return text;
          }
        }
      })
        .done(contents => {
          loadedJs.push(scriptUrl);
          deferred.resolve({ url: scriptUrl, contents: contents });
        })
        .fail(() => {
          deferred.resolve('');
        });
      return deferred.promise();
    };

    const loadScripts = function(scriptUrls) {
      const promises = [];
      while (scriptUrls.length) {
        const scriptUrl =
          typeof window.adaptHueEmbeddedUrls !== 'undefined'
            ? window.adaptHueEmbeddedUrls(scriptUrls.shift())
            : scriptUrls.shift();
        if (loadedJs.indexOf(scriptUrl) !== -1) {
          continue;
        }
        promises.push(loadScript(scriptUrl));
      }
      return promises;
    };

    const addGlobalCss = function($el) {
      const cssFile = $el.attr('href').split('?')[0];
      if (loadedCss.indexOf(cssFile) === -1) {
        loadedCss.push(cssFile);
        $.ajaxSetup({ cache: true });
        if (typeof window.adaptHueEmbeddedUrls !== 'undefined') {
          $el.attr('href', window.adaptHueEmbeddedUrls($el.attr('href')));
        }
        if (window.DEV) {
          $el.attr('href', $el.attr('href') + '?dev=' + Math.random());
        }
        $el.clone().appendTo($('head'));
        $.ajaxSetup({ cache: false });
      }
      $el.remove();
    };

    // Only load CSS and JS files that are not loaded before
    self.processHeaders = function(response) {
      const promise = $.Deferred();
      const $rawHtml = $('<span>').html(response);

      const $allScripts = $rawHtml.find('script[src]');
      const scriptsToLoad = $allScripts
        .map(function() {
          return $(this).attr('src');
        })
        .toArray();
      $allScripts.remove();

      $rawHtml.find('link[href]').each(function() {
        addGlobalCss($(this)); // Also removes the elements;
      });

      $rawHtml.find('a[href]').each(function() {
        let link = $(this).attr('href');
        if (link.startsWith('/') && !link.startsWith('/hue')) {
          link = window.HUE_BASE_URL + '/hue' + link;
        }
        $(this).attr('href', link);
      });

      if (typeof adaptHueEmbeddedUrls !== 'undefined') {
        $rawHtml.find('img[src]').each(function() {
          const $img = $(this);
          $img.attr('src', window.adaptHueEmbeddedUrls($img.attr('src')));
        });
      }

      $rawHtml.unwrap('span');

      const scriptPromises = loadScripts(scriptsToLoad);

      const evalScriptSync = function() {
        if (scriptPromises.length) {
          // Evaluate the scripts in the order they were defined in the page
          const nextScriptPromise = scriptPromises.shift();
          nextScriptPromise.done(scriptDetails => {
            if (scriptDetails.contents) {
              $.globalEval(scriptDetails.contents);
            }
            evalScriptSync();
          });
        } else {
          // All evaluated
          promise.resolve($rawHtml);
        }
      };

      evalScriptSync();
      return promise;
    };

    huePubSub.subscribe('hue4.process.headers', opts => {
      self.processHeaders(opts.response).done(rawHtml => {
        opts.callback(rawHtml);
      });
    });

    self.loadApp = function(app, loadDeep) {
      if (self.currentApp() === 'editor' && $('#editorComponents').length) {
        const vm = ko.dataFor($('#editorComponents')[0]);
        if (vm.isPresentationMode()) {
          vm.selectedNotebook().isPresentationMode(false);
        }
      }

      if (
        self.currentApp() === 'editor' &&
        self.embeddable_cache['editor'] &&
        !$('#editorComponents').length
      ) {
        self.embeddable_cache['editor'] = undefined;
      }

      self.currentApp(app);
      if (!app.startsWith('security')) {
        self.lastContext = null;
      }
      window.SKIP_CACHE.forEach(skipped => {
        huePubSub.publish('app.dom.unload', skipped);
        $('#embeddable_' + skipped).html('');
      });
      self.isLoadingEmbeddable(true);
      loadedApps.forEach(loadedApp => {
        window.pauseAppIntervals(loadedApp);
        huePubSub.pauseAppSubscribers(loadedApp);
      });
      $('.tooltip').hide();
      huePubSub.publish('hue.datatable.search.hide');
      huePubSub.publish('hue.scrollleft.hide');
      huePubSub.publish('context.panel.visible', false);
      huePubSub.publish('context.panel.visible.editor', false);
      if (app === 'filebrowser') {
        $(window).unbind('hashchange.fblist');
      }
      if (app.startsWith('oozie')) {
        huePubSub.clearAppSubscribers('oozie');
      }
      if (app.startsWith('security')) {
        $('#embeddable_security_hive').html('');
        $('#embeddable_security_hdfs').html('');
        $('#embeddable_security_hive2').html('');
        $('#embeddable_security_solr').html('');
      }
      if (typeof self.embeddable_cache[app] === 'undefined') {
        if (loadedApps.indexOf(app) === -1) {
          loadedApps.push(app);
        }
        let baseURL = window.EMBEDDABLE_PAGE_URLS[app].url;
        if (self.currentContextParams() !== null) {
          if (loadDeep && self.currentContextParams()[0]) {
            baseURL += self.currentContextParams()[0];
          } else {
            const route = new page.Route(baseURL);
            route.keys.forEach(key => {
              if (key.name === 0) {
                if (typeof self.currentContextParams()[key.name] !== 'undefined') {
                  if (app === 'filebrowser') {
                    baseURL = baseURL
                      .replace('*', encodeURIComponent(self.currentContextParams()[key.name]))
                      .replace(/#/g, '%23');
                  } else {
                    baseURL = baseURL.replace(
                      '*',
                      encodeURI(self.currentContextParams()[key.name])
                    ); // We have some really funky stuff in here, this should be encodeURIComponent
                  }
                } else {
                  baseURL = baseURL.replace('*', '');
                }
              } else {
                baseURL = baseURL.replace(
                  ':' + key.name,
                  encodeURI(self.currentContextParams()[key.name])
                ); // We have some really funky stuff in here, this should be encodeURIComponent
              }
            });
          }
          self.currentContextParams(null);
        }
        if (self.currentQueryString() !== null) {
          baseURL += (baseURL.indexOf('?') > -1 ? '&' : '?') + encodeURI(self.currentQueryString());
          self.currentQueryString(null);
        }

        $.ajax({
          url:
            baseURL +
            (baseURL.indexOf('?') > -1 ? '&' : '?') +
            'is_embeddable=true' +
            self.extraEmbeddableURLParams(),
          beforeSend: function(xhr) {
            xhr.setRequestHeader('X-Requested-With', 'Hue');
          },
          dataType: 'html',
          success: function(response, status, xhr) {
            const type = xhr.getResponseHeader('Content-Type');
            if (type.indexOf('text/') > -1) {
              window.clearAppIntervals(app);
              huePubSub.clearAppSubscribers(app);
              self.extraEmbeddableURLParams('');

              self.processHeaders(response).done($rawHtml => {
                if (window.SKIP_CACHE.indexOf(app) === -1) {
                  self.embeddable_cache[app] = $rawHtml;
                }
                $('#embeddable_' + app).html($rawHtml);
                huePubSub.publish('app.dom.loaded', app);
                window.setTimeout(() => {
                  self.isLoadingEmbeddable(false);
                }, 0);
              });
            } else {
              if (type.indexOf('json') > -1) {
                const presponse = JSON.parse(response);
                if (presponse && presponse.url) {
                  window.location.href = window.HUE_BASE_URL + presponse.url;
                  return;
                }
              }
              window.location.href = window.HUE_BASE_URL + baseURL;
            }
          },
          error: function(xhr) {
            console.error('Route loading problem', xhr);
            if ((xhr.status === 401 || xhr.status === 403) && app !== '403') {
              self.loadApp('403');
            } else if (app !== '500') {
              self.loadApp('500');
            } else {
              $.jHueNotify.error(
                I18n(
                  'It looks like you are offline or an unknown error happened. Please refresh the page.'
                )
              );
            }
          }
        });
      } else {
        self.isLoadingEmbeddable(false);
      }
      window.document.title = 'Hue - ' + window.EMBEDDABLE_PAGE_URLS[app].title;
      window.resumeAppIntervals(app);
      huePubSub.resumeAppSubscribers(app);
      $('.embeddable').hide();
      $('#embeddable_' + app).show();
      huePubSub.publish('app.gained.focus', app);
      huePubSub.publish('resize.form.actions');
    };

    self.dropzoneError = function(filename) {
      self.loadApp('importer');
      self.getActiveAppViewModel(vm => {
        vm.createWizard.source.path(DROPZONE_HOME_DIR + '/' + filename);
      });
      $('.dz-drag-hover').removeClass('dz-drag-hover');
    };

    const openImporter = function(path) {
      self.loadApp('importer');
      self.getActiveAppViewModel(vm => {
        vm.createWizard.source.path(path);
      });
    };

    self.dropzoneComplete = function(path) {
      if (path.toLowerCase().endsWith('.csv')) {
        openImporter(path);
      } else {
        huePubSub.publish('open.link', '/filebrowser/view=' + path);
      }
      $('.dz-drag-hover').removeClass('dz-drag-hover');
    };

    huePubSub.subscribe('open.in.importer', openImporter);

    huePubSub.subscribe('assist.dropzone.complete', self.dropzoneComplete);

    // prepend /hue to all the link on this page
    $(window.IS_EMBEDDED ? '.hue-embedded-container a[href]' : 'a[href]').each(function() {
      let link = $(this).attr('href');
      if (link.startsWith('/') && !link.startsWith('/hue')) {
        link = window.HUE_BASE_URL + '/hue' + link;
      }
      $(this).attr('href', link);
    });

    if (window.IS_EMBEDDED) {
      page.base(window.location.pathname + window.location.search);
      page.baseSearch = window.location.search.replace('?', '');
      if (!window.location.hash) {
        window.location.hash = '#!/editor?type=impala';
      }
      page({ hashbang: true });
    } else {
      page.base(window.HUE_BASE_URL + '/hue');
    }

    const getUrlParameter = function(name) {
      if (window.IS_EMBEDDED) {
        if (~window.location.hash.indexOf('?')) {
          const paramString = window.location.hash.substring(window.location.hash.indexOf('?'));
          const params = paramString.split('&');
          for (let i = 0; i < params.length; i++) {
            if (~params[i].indexOf(name + '=')) {
              return params[i].substring(name.length + 2);
            }
          }
        }
        return '';
      } else {
        return window.location.getParameter(name) || '';
      }
    };

    self.lastContext = null;

    let pageMapping = [
      { url: '/403', app: '403' },
      { url: '/500', app: '500' },
      { url: '/about/', app: 'admin_wizard' },
      { url: '/about/admin_wizard', app: 'admin_wizard' },
      {
        url: '/accounts/logout',
        app: function() {
          location.href = window.HUE_BASE_URL + '/accounts/logout';
        }
      },
      {
        url: '/dashboard/admin/collections',
        app: function(ctx) {
          page('/home/?type=search-dashboard');
        }
      },
      { url: '/dashboard/*', app: 'dashboard' },
      {
        url: '/desktop/api/desktop/api2/doc/export*',
        app: function() {
          const documents = getUrlParameter('documents');
          location.href = window.HUE_BASE_URL + '/desktop/api2/doc/export?documents=' + documents;
        }
      },
      { url: '/desktop/dump_config', app: 'dump_config' },
      {
        url: '/desktop/debug/threads',
        app: function() {
          self.loadApp('threads');
          self.getActiveAppViewModel(viewModel => {
            viewModel.fetchThreads();
          });
        }
      },
      {
        url: '/desktop/metrics',
        app: function() {
          self.loadApp('metrics');
          self.getActiveAppViewModel(viewModel => {
            viewModel.fetchMetrics();
          });
        }
      },
      {
        url: '/desktop/connectors',
        app: function() {
          self.loadApp('connectors');
          self.getActiveAppViewModel(viewModel => {
            viewModel.fetchConnectors();
          });
        }
      },
      {
        url: '/desktop/analytics',
        app: function() {
          self.loadApp('analytics');
          self.getActiveAppViewModel(viewModel => {
            viewModel.fetchAnalytics();
          });
        }
      },
      {
        url: '/desktop/download_logs',
        app: function() {
          location.href = window.HUE_BASE_URL + '/desktop/download_logs';
        }
      },
      {
        url: '/editor',
        app: function() {
          // Defer to allow window.location param update
          _.defer(() => {
            if (typeof self.embeddable_cache['editor'] === 'undefined') {
              if (getUrlParameter('editor') !== '') {
                self.extraEmbeddableURLParams('&editor=' + getUrlParameter('editor'));
              } else if (getUrlParameter('type') !== '' && getUrlParameter('type') !== 'notebook') {
                self.extraEmbeddableURLParams('&type=' + getUrlParameter('type'));
              }
              self.loadApp('editor');
            } else {
              self.loadApp('editor');
              if (getUrlParameter('editor') !== '') {
                self.getActiveAppViewModel(viewModel => {
                  self.isLoadingEmbeddable(true);
                  viewModel.openNotebook(getUrlParameter('editor')).always(() => {
                    self.isLoadingEmbeddable(false);
                  });
                });
              } else if (getUrlParameter('type') !== '') {
                self.changeEditorType(getUrlParameter('type'));
              }
            }
          });
        }
      },
      {
        url: '/notebook/editor',
        app: function(ctx) {
          page('/editor?' + ctx.querystring);
        }
      },
      { url: '/filebrowser/view=*', app: 'filebrowser' },
      {
        url: '/filebrowser/download=*',
        app: function(ctx) {
          location.href = window.HUE_BASE_URL + '/filebrowser/download=' + ctx.params[0];
        }
      },
      {
        url: '/filebrowser/*',
        app: function() {
          page('/filebrowser/view=' + DROPZONE_HOME_DIR);
        }
      },
      { url: '/hbase/', app: 'hbase' },
      { url: '/help', app: 'help' },
      {
        url: '/home2*',
        app: function(ctx) {
          page(ctx.path.replace(/home2/gi, 'home'));
        }
      },
      { url: '/home*', app: 'home' },
      { url: '/catalog', app: 'catalog' },
      { url: '/kafka/', app: 'kafka' },
      { url: '/indexer/topics/*', app: 'kafka' },
      { url: '/indexer/indexes', app: 'indexes' },
      { url: '/indexer/indexes/*', app: 'indexes' },
      { url: '/indexer/', app: 'indexes' },
      { url: '/indexer/importer/', app: 'importer' },
      {
        url: '/indexer/importer/prefill/*',
        app: function(ctx) {
          self.loadApp('importer');
          self.getActiveAppViewModel(viewModel => {
            const _params = ctx.path.match(
              /\/indexer\/importer\/prefill\/?([^/]+)\/?([^/]+)\/?([^/]+)?/
            );
            if (!_params) {
              console.warn('Could not match ' + ctx.path);
            }
            hueUtils.waitForVariable(viewModel.createWizard, () => {
              hueUtils.waitForVariable(viewModel.createWizard.prefill, () => {
                viewModel.createWizard.prefill.source_type(_params && _params[1] ? _params[1] : '');
                viewModel.createWizard.prefill.target_type(_params && _params[2] ? _params[2] : '');
                viewModel.createWizard.prefill.target_path(_params && _params[3] ? _params[3] : '');
              });
            });
          });
        }
      },
      {
        url: '/jobbrowser/jobs/job_*',
        app: function(ctx) {
          page.redirect(
            '/jobbrowser#!id=application_' + _.trimRight(ctx.params[0], '/').split('/')[0]
          );
        }
      },
      {
        url: '/jobbrowser/jobs/application_*',
        app: function(ctx) {
          page.redirect(
            '/jobbrowser#!id=application_' + _.trimRight(ctx.params[0], '/').split('/')[0]
          );
        }
      },
      { url: '/jobbrowser*', app: 'jobbrowser' },
      { url: '/logs', app: 'logs' },
      {
        url: '/metastore',
        app: function() {
          page('/metastore/tables');
        }
      },
      { url: '/metastore/*', app: 'metastore' },
      {
        url: '/notebook',
        app: function(ctx) {
          self.loadApp('notebook');
          const notebookId = hueUtils.getSearchParameter('?' + ctx.querystring, 'notebook');
          if (notebookId !== '') {
            self.getActiveAppViewModel(viewModel => {
              self.isLoadingEmbeddable(true);
              viewModel.openNotebook(notebookId).always(() => {
                self.isLoadingEmbeddable(false);
              });
            });
          } else {
            self.getActiveAppViewModel(viewModel => {
              viewModel.newNotebook('notebook');
            });
          }
        }
      },
      {
        url: '/notebook/notebook',
        app: function(ctx) {
          page('/notebook?' + ctx.querystring);
        }
      },
      {
        url: '/notebook/notebooks',
        app: function(ctx) {
          page('/home/?' + ctx.querystring);
        }
      },
      {
        url: '/oozie/editor/bundle/list',
        app: function(ctx) {
          page('/home/?type=oozie-bundle');
        }
      },
      { url: '/oozie/editor/bundle/*', app: 'oozie_bundle' },
      {
        url: '/oozie/editor/coordinator/list',
        app: function(ctx) {
          page('/home/?type=oozie-coordinator');
        }
      },
      { url: '/oozie/editor/coordinator/*', app: 'oozie_coordinator' },
      {
        url: '/oozie/editor/workflow/list',
        app: function(ctx) {
          page('/home/?type=oozie-workflow');
        }
      },
      { url: '/oozie/editor/workflow/*', app: 'oozie_workflow' },
      { url: '/oozie/list_oozie_info', app: 'oozie_info' },
      {
        url: '/oozie/list_oozie_sla',
        app: function() {
          page.redirect('/jobbrowser/#!slas');
        }
      },
      {
        url: '/pig',
        app: function() {
          self.loadApp('editor');
          self.changeEditorType('pig');
        }
      },
      { url: '/search/*', app: 'dashboard' },
      {
        url: '/security/hdfs',
        app: function(ctx) {
          if (self.lastContext == null || ctx.path !== self.lastContext.path) {
            self.loadApp('security_hdfs');
          }
          self.lastContext = ctx;
        }
      },
      {
        url: '/security/hive',
        app: function(ctx) {
          if (self.lastContext == null || ctx.path !== self.lastContext.path) {
            self.loadApp('security_hive');
          }
          self.lastContext = ctx;
        }
      },
      {
        url: '/security/hive2',
        app: function(ctx) {
          if (self.lastContext == null || ctx.path !== self.lastContext.path) {
            self.loadApp('security_hive2');
          }
          self.lastContext = ctx;
        }
      },
      {
        url: '/security/solr',
        app: function(ctx) {
          if (self.lastContext == null || ctx.path !== self.lastContext.path) {
            self.loadApp('security_solr');
          }
          self.lastContext = ctx;
        }
      },
      {
        url: '/security',
        app: function() {
          page('/security/hive');
        }
      },
      { url: '/sqoop', app: 'sqoop' },
      { url: '/jobsub', app: 'jobsub' },
      { url: '/useradmin/configurations/', app: 'useradmin_configurations' },
      { url: '/useradmin/groups/', app: 'useradmin_groups' },
      { url: '/useradmin/groups/new', app: 'useradmin_newgroup' },
      { url: '/useradmin/groups/edit/:group', app: 'useradmin_editgroup' },
      { url: '/useradmin/permissions/', app: 'useradmin_permissions' },
      { url: '/useradmin/permissions/edit/*', app: 'useradmin_editpermission' },
      { url: '/useradmin/users/', app: 'useradmin_users' },
      { url: '/useradmin/users/add_ldap_users', app: 'useradmin_addldapusers' },
      { url: '/useradmin/users/add_ldap_groups', app: 'useradmin_addldapgroups' },
      { url: '/useradmin/users/edit/:user', app: 'useradmin_edituser' },
      { url: '/useradmin/users/new', app: 'useradmin_newuser' },
      { url: '/useradmin', app: 'useradmin_users' }
    ];

    window.OTHER_APPS.forEach(otherApp => {
      pageMapping.push({
        url: '/' + otherApp + '*',
        app: ctx => {
          self.currentContextParams(ctx.params);
          self.currentQueryString(ctx.querystring);
          self.loadApp(otherApp, true);
        }
      });
    });

    if (typeof window.HUE_EMBEDDED_PAGE_MAPPINGS !== 'undefined') {
      pageMapping = pageMapping.concat(window.HUE_EMBEDDED_PAGE_MAPPINGS);
    }

    pageMapping.forEach(mapping => {
      page(
        mapping.url,
        _.isFunction(mapping.app)
          ? mapping.app
          : ctx => {
              self.currentContextParams(ctx.params);
              self.currentQueryString(ctx.querystring);
              self.loadApp(mapping.app);
            }
      );
    });

    huePubSub.subscribe('cluster.config.set.config', clusterConfig => {
      page('/', () => {
        page(clusterConfig['main_button_action'].page);
      });
      page('*', ctx => {
        console.error('Route not found', ctx);
        self.loadApp('404');
      });
      page();
    });

    huePubSub.subscribe('open.link', href => {
      if (href) {
        const prefix = window.IS_EMBEDDED ? '' : '/hue';
        if (href.startsWith('/') && !href.startsWith(prefix)) {
          page(window.HUE_BASE_URL + prefix + href);
        } else if (href.indexOf('#') == 0) {
          // Only place that seem to use this is hbase onclick row
          window.location.hash = href;
        } else {
          page(href);
        }
      } else {
        console.warn('Received an open.link without href.');
      }
    });
  }
}

export default OnePageViewModel;
