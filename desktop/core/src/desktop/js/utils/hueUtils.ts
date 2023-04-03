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

import { hueLocalStorage, withLocalStorage } from './storageUtils';

import logError from './logError';

import exitFullScreen from './screen/exitFullsScreen';
import goFullScreen from './screen/goFullScreen';
import isFullScreen from './screen/isFullScreen';
import scrollbarWidth from './screen/scrollbarWidth';
import toggleFullScreen from './screen/toggleFullScreen';

import bootstrapRatios from './html/bootstrapRatios';
import deXSS from './html/deXSS';
import escapeOutput from './html/escapeOutput';
import getFileBrowseButton from './html/getFileBrowseButton';
import getStyleFromCSSClass from './html/getStyleFromCSSClass';
import highlight from './html/highlight';
import html2text from './html/html2text';
import htmlEncode from './html/htmlEncode';
import isOverflowing from './html/isOverflowing';
import stripHtmlFromFunctions from './html/stripHtmlForFunctions';

import deleteAllEmptyStringKeys from './string/deleteAllEmptyStringKeys';
import equalIgnoreCase from './string/equalIgnoreCase';
import parseHivePseudoJson from './string/parseHivePseudoJson';
import includesComplexDBTypeDefinition from './string/includesComplexDBTypeDefinition';
import UUID from './string/UUID';

import waitForObservable from './timing/waitForObservable';
import waitForRendered from './timing/waitForRendered';
import waitForVariable from './timing/waitForVariable';

import changeURL from './url/changeURL';
import changeURLParameter from './url/changeURLParameter';
import getParameter from './url/getParameter';
import getSearchParameter from './url/getSearchParameter';
import removeURLParameter from './url/removeURLParameter';
import replaceURL from './url/replaceURL';

export default {
  bootstrapRatios,
  changeURL,
  changeURLParameter,
  deleteAllEmptyStringKeys,
  deXSS,
  equalIgnoreCase,
  escapeOutput,
  exitFullScreen,
  getFileBrowseButton,
  getParameter,
  getSearchParameter,
  getStyleFromCSSClass,
  goFullScreen,
  highlight,
  /**
   * Exposed here for legacy code using global window.hueUtils, use utils/storageUtils instead.
   * @deprecated
   */
  hueLocalStorage,
  html2text,
  htmlEncode,
  includesComplexDBTypeDefinition,
  isFullScreen,
  isOverflowing,
  logError,
  parseHivePseudoJson,
  removeURLParameter,
  replaceURL,
  scrollbarWidth,
  stripHtmlFromFunctions,
  toggleFullScreen,
  UUID,
  waitForObservable,
  waitForRendered,
  waitForVariable,
  /**
   * Exposed here for legacy code using global window.hueUtils, use utils/storageUtils instead.
   * @deprecated
   */
  withLocalStorage
};
