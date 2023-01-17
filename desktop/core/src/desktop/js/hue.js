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

import 'utils/publicPath';
import 'core-js/stable';
import 'regenerator-runtime/runtime';
import _ from 'lodash';
import $ from 'jquery/jquery.common';
import 'ext/bootstrap.2.3.2.min';
import 'ext/bootstrap-editable.1.5.1.min';
import 'utils/d3Extensions';
import d3v3 from 'd3v3';
import Dropzone from 'dropzone';
import filesize from 'filesize';
import localforage from 'localforage';
import nv from 'nvd3/nv.all';
import page from 'page';
import qq from 'ext/fileuploader.custom';
import sprintf from 'sprintf-js';

import ko from 'ko/ko.all';

import 'parse/parserTypeDefs';

import 'utils/customIntervals';
import 'utils/json.bigDataParse';
import apiHelper from 'api/apiHelper';
import CancellableJqPromise from 'api/cancellableJqPromise';
import { DOCUMENT_TYPE_I18n, DOCUMENT_TYPES } from 'doc/docSupport';
import contextCatalog from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import hueAnalytics, { setupGlobalListenersForAnalytics } from 'utils/hueAnalytics';
import HueColors from 'utils/hueColors';
import hueDebug from 'utils/hueDebug';
import hueDrop from 'utils/hueDrop';
import HueGeo from 'utils/hueGeo';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';
import MultiLineEllipsisHandler from 'utils/multiLineEllipsisHandler';

import sqlUtils from 'sql/sqlUtils';

import 'webComponents/HueIcons';
import 'components/sidebar/HueSidebarWebComponent';
import 'components/assist/AssistPanelWebComponent';

import 'ko/components/assist/assistViewModel';
import { BOTH_ASSIST_TOGGLE_EVENT } from 'ko/components/assist/events';
import OnePageViewModel from 'onePageViewModel';
import SidePanelViewModel from 'sidePanelViewModel';
import TopNavViewModel from 'topNavViewModel';

// TODO: Remove from global scope
import NotebookViewModel from 'apps/notebook/NotebookViewModel'; // In history, indexer, importer, editor etc.
import HdfsAutocompleter from 'utils/hdfsAutocompleter';
import SqlAutocompleter from 'sql/sqlAutocompleter';
import sqlStatementsParser from 'parse/sqlStatementsParser'; // In search.ko and notebook.ko
import hplsqlStatementsParser from 'parse/hplsqlStatementsParser';
import HueFileEntry from 'doc/hueFileEntry';
import HueDocument from 'doc/hueDocument';
import { getLastKnownConfig, refreshConfig } from 'config/hueConfig';
import { simpleGet } from 'api/apiUtils'; // In analytics.mako, metrics.mako, threads.mako
import Mustache from 'mustache'; // In hbase/templates/app.mako, jobsub.templates.js, search.ko.js, search.util.js
import { createReactComponents } from 'reactComponents/createRootElements.js';

// TODO: Migrate away
window._ = _;
window.apiHelper = apiHelper;
window.simpleGet = simpleGet;
window.CancellableJqPromise = CancellableJqPromise;
window.contextCatalog = contextCatalog;
window.d3v3 = d3v3;
window.dataCatalog = dataCatalog;
window.DOCUMENT_TYPE_I18n = DOCUMENT_TYPE_I18n;
window.DOCUMENT_TYPES = DOCUMENT_TYPES;
window.Dropzone = Dropzone;
window.NotebookViewModel = NotebookViewModel;
window.filesize = filesize;
window.getLastKnownConfig = getLastKnownConfig;
window.HdfsAutocompleter = HdfsAutocompleter;
window.hueAnalytics = hueAnalytics;
window.HueColors = HueColors;
window.hueDebug = hueDebug;
window.hueDebugAnalytics = false;
window.HueDocument = HueDocument;
window.hueDrop = hueDrop;
window.HueFileEntry = HueFileEntry;
window.HueGeo = HueGeo;
window.huePubSub = huePubSub;
window.hueUtils = hueUtils;
window.I18n = I18n;
window.localforage = localforage;
window.MultiLineEllipsisHandler = MultiLineEllipsisHandler;
window.Mustache = Mustache;
window.nv = nv;
window.page = page;
window.qq = qq;
window.sprintf = sprintf;
window.SqlAutocompleter = SqlAutocompleter;
window.sqlStatementsParser = sqlStatementsParser;
window.hplsqlStatementsParser = hplsqlStatementsParser;
window.sqlUtils = sqlUtils;
window.createReactComponents = createReactComponents;

$(document).ready(async () => {
  await refreshConfig(); // Make sure we have config up front

  createReactComponents('.main-page');

  const onePageViewModel = new OnePageViewModel();
  ko.applyBindings(onePageViewModel, $('.page-content')[0]);

  const sidePanelViewModel = new SidePanelViewModel();
  ko.applyBindings(sidePanelViewModel, $('.left-panel')[0]);
  ko.applyBindings(sidePanelViewModel, $('#leftResizer')[0]);
  ko.applyBindings(sidePanelViewModel, $('.right-panel')[0]);
  if (!window.ENABLE_NOTEBOOK_2) {
    ko.applyBindings(sidePanelViewModel, $('.context-panel')[0]);
  }

  const topNavViewModel = new TopNavViewModel(onePageViewModel);
  ko.applyBindings(topNavViewModel, $('.top-nav')[0]);

  $(document).on('hideHistoryModal', e => {
    $('#clearNotificationHistoryModal').modal('hide');
  });

  huePubSub.subscribe('query.and.watch', query => {
    $.post(
      query['url'],
      {
        format: 'json',
        sourceType: query['sourceType']
      },
      resp => {
        if (resp.history_uuid) {
          huePubSub.publish('open.editor.query', resp);
        } else if (resp.message) {
          $(document).trigger('error', resp.message);
        }
      }
    ).fail(xhr => {
      $(document).trigger('error', xhr.responseText);
    });
  });

  let clickThrottle = -1;

  $(window).click(e => {
    window.clearTimeout(clickThrottle);
    clickThrottle = window.setTimeout(() => {
      if (
        $(e.target).parents('.navbar-default').length > 0 &&
        $(e.target).closest('.history-panel').length === 0 &&
        $(e.target).closest('.btn-toggle-jobs-panel').length === 0 &&
        $(e.target).closest('.hamburger-hue').length === 0 &&
        $('.jobs-panel').is(':visible')
      ) {
        huePubSub.publish('hide.jobs.panel');
        huePubSub.publish('hide.history.panel');
      }
    }, 10);
  });

  setupGlobalListenersForAnalytics();

  $('.page-content').jHueScrollUp();
});

// Framework independent global keyboard shortcuts
document.addEventListener('keydown', e => {
  if (e.key === '.' && (e.metaKey || e.ctrlKey)) {
    huePubSub.publish(BOTH_ASSIST_TOGGLE_EVENT);
  }
});
