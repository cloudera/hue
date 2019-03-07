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

import 'jquery/jquery.common';
import 'ext/bootstrap.2.3.2.min';
import 'ext/bootstrap-editable.1.5.1.min';
import _ from 'lodash';
import Dropzone from 'dropzone';
import filesize from 'filesize';
import qq from 'ext/fileuploader.custom';
import page from 'page';
import localforage from 'localforage';
import sprintf from 'sprintf-js';

import 'ko/ko.all';

import 'utils/customIntervals';
import 'utils/json.bigDataParse';
import apiHelper from 'api/apiHelper';
import CancellablePromise from 'api/cancellablePromise';
import contextCatalog from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import hueAnalytics from 'utils/hueAnalytics';
import HueColors from 'utils/hueColors';
import hueDebug from 'utils/hueDebug';
import hueDrop from 'utils/hueDrop';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import MultiLineEllipsisHandler from 'utils/multiLineEllipsisHandler';

import AceLocationHandler from 'sql/aceLocationHandler';
import SqlParseSupport from 'parse/sqlParseSupport';
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
import globalSearchParser from 'parse/globalSearchParser'; // ko inline autocomp
import HdfsAutocompleter from 'utils/hdfsAutocompleter';
import solrFormulaParser from 'parse/solrFormulaParser'; // simple ace editor
import solrQueryParser from 'parse/solrQueryParser'; // simple ace editor
import SqlAutocompleter from 'sql/sqlAutocompleter';
import sqlAutocompleteParser from 'parse/sqlAutocompleteParser'; // Notebook and used throughout via hue-simple-ace-editor ko component
import sqlStatementsParser from 'parse/sqlStatementsParser'; // In search.ko and notebook.ko

// TODO: Migrate away
window._ = _;
window.AceLocationHandler = AceLocationHandler;
window.apiHelper = apiHelper;
window.CancellablePromise = CancellablePromise;
window.contextCatalog = contextCatalog;
window.dataCatalog = dataCatalog;
window.Dropzone = Dropzone;
window.EditorViewModel = EditorViewModel;
window.filesize = filesize;
window.globalSearchParser = globalSearchParser;
window.HdfsAutocompleter = HdfsAutocompleter;
window.hueAnalytics = hueAnalytics;
window.HueColors = HueColors;
window.hueDebug = hueDebug;
window.hueDrop = hueDrop;
window.huePubSub = huePubSub;
window.hueUtils = hueUtils;
window.localforage = localforage;
window.MultiLineEllipsisHandler = MultiLineEllipsisHandler;
window.page = page;
window.PigFunctions = PigFunctions;
window.qq = qq;
window.solrFormulaParser = solrFormulaParser;
window.solrQueryParser = solrQueryParser;
window.sprintf = sprintf;
window.SqlAutocompleter = SqlAutocompleter;
window.sqlAutocompleteParser = sqlAutocompleteParser;
window.SqlFunctions = SqlFunctions;
window.SqlParseSupport = SqlParseSupport;
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
