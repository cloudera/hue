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

import '@babel/polyfill';
import _ from 'lodash';
import $ from 'jquery/jquery.common';
import 'ext/bootstrap.2.3.2.min';
import 'ext/bootstrap-editable.1.5.1.min';

import 'utils/d3Extensions';
import * as d3 from 'd3';
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
import CancellablePromise from 'api/cancellablePromise';
import { DOCUMENT_TYPE_I18n, DOCUMENT_TYPES } from 'doc/docSupport';
import contextCatalog from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import hueAnalytics from 'utils/hueAnalytics';
import HueColors from 'utils/hueColors';
import hueDebug from 'utils/hueDebug';
import hueDrop from 'utils/hueDrop';
import HueGeo from 'utils/hueGeo';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';
import MultiLineEllipsisHandler from 'utils/multiLineEllipsisHandler';

import sqlUtils from 'sql/sqlUtils';
import { PigFunctions, SqlSetOptions, SqlFunctions } from 'sql/sqlFunctions';
import sqlWorkerHandler from 'sql/sqlWorkerHandler';

import 'assist/assistViewModel';
import OnePageViewModel from 'onePageViewModel';
import SideBarViewModel from 'sideBarViewModel';
import SidePanelViewModel from 'sidePanelViewModel';
import TopNavViewModel from 'topNavViewModel';

// TODO: Remove from global scope
import EditorViewModel from 'apps/notebook/editorViewModel'; // In history, indexer, importer, editor etc.
import EditorViewModel2 from 'apps/notebook2/editorViewModel'; // In history, indexer, importer, editor etc.
import HdfsAutocompleter from 'utils/hdfsAutocompleter';
import SqlAutocompleter from 'sql/sqlAutocompleter';
import sqlAutocompleteParser from 'parse/sqlAutocompleteParser'; // Notebook and used throughout via hue-simple-ace-editor ko component
import sqlStatementsParser from 'parse/sqlStatementsParser'; // In search.ko and notebook.ko
import HueFileEntry from 'doc/hueFileEntry';
import HueDocument from 'doc/hueDocument';

// TODO: Migrate away
window._ = _;
window.apiHelper = apiHelper;
window.CancellablePromise = CancellablePromise;
window.contextCatalog = contextCatalog;
window.d3 = d3;
window.d3v3 = d3v3;
window.dataCatalog = dataCatalog;
window.DOCUMENT_TYPE_I18n = DOCUMENT_TYPE_I18n;
window.DOCUMENT_TYPES = DOCUMENT_TYPES;
window.Dropzone = Dropzone;
if (window.ENABLE_NOTEBOOK_2) {
  window.EditorViewModel = EditorViewModel2;
} else {
  window.EditorViewModel = EditorViewModel;
}
window.filesize = filesize;
window.HdfsAutocompleter = HdfsAutocompleter;
window.hueAnalytics = hueAnalytics;
window.HueColors = HueColors;
window.hueDebug = hueDebug;
window.HueDocument = HueDocument;
window.hueDrop = hueDrop;
window.HueFileEntry = HueFileEntry;
window.HueGeo = HueGeo;
window.huePubSub = huePubSub;
window.hueUtils = hueUtils;
window.I18n = I18n;
window.localforage = localforage;
window.MultiLineEllipsisHandler = MultiLineEllipsisHandler;
window.nv = nv;
window.page = page;
window.PigFunctions = PigFunctions;
window.qq = qq;
window.sprintf = sprintf;
window.sqlAutocompleteParser = sqlAutocompleteParser;
window.SqlAutocompleter = SqlAutocompleter;
window.SqlFunctions = SqlFunctions;
window.SqlSetOptions = SqlSetOptions;
window.sqlStatementsParser = sqlStatementsParser;
window.sqlUtils = sqlUtils;
window.sqlWorkerHandler = sqlWorkerHandler;

$(document).ready(() => {
  const onePageViewModel = new OnePageViewModel();
  ko.applyBindings(onePageViewModel, $('.page-content')[0]);

  const sidePanelViewModel = new SidePanelViewModel();
  ko.applyBindings(sidePanelViewModel, $('.left-panel')[0]);
  ko.applyBindings(sidePanelViewModel, $('#leftResizer')[0]);
  ko.applyBindings(sidePanelViewModel, $('.right-panel')[0]);
  ko.applyBindings(sidePanelViewModel, $('.context-panel')[0]);

  const topNavViewModel = new TopNavViewModel(onePageViewModel);
  if (!window.IS_EMBEDDED) {
    ko.applyBindings(topNavViewModel, $('.top-nav')[0]);
  }

  const sidebarViewModel = new SideBarViewModel(onePageViewModel, topNavViewModel);
  ko.applyBindings(sidebarViewModel, $('.hue-sidebar')[0]);
  if (window.IS_MULTICLUSTER_ONLY) {
    ko.applyBindings(sidebarViewModel, $('.hue-dw-sidebar-container')[0]);
  }

  huePubSub.publish('cluster.config.get.config');

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
          huePubSub.publish('open.editor.query', resp.history_uuid);
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

  $('.page-content').jHueScrollUp();
});
