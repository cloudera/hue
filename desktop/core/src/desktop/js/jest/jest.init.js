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

// Ensure singletons
import 'core-js/stable';
import 'regenerator-runtime/runtime';

import 'apps/notebook2/execution/sessionManager';
import './jquery.setup';
import './sqlTestUtils';

import 'ext/bootstrap.2.3.2.min';
import axios from 'axios';
import $ from 'jquery';
import * as ko from 'knockout';
import komapping from 'knockout.mapping';

ko.mapping = komapping;

class Tooltip {}

class AceRange {}

class Autocomplete {}

const globalVars = {
  ko: ko,
  AUTOCOMPLETE_TIMEOUT: 1,
  CACHEABLE_TTL: 1,
  HAS_LINK_SHARING: true,
  HAS_OPTIMIZER: false,
  HUE_I18n: {},
  HUE_BASE_URL: '',
  HUE_CHARTS: {
    TYPES: 'bar'
  },
  LOGGED_USERNAME: 'foo',
  LOGGED_USER_ID: 'bar',
  PREVENT_AUTOFILL_INPUT_ATTRS:
    'autocorrect="off" autocomplete="do-not-autocomplete" autocapitalize="off" spellcheck="false"',
  STATIC_URLS: {
    'impala/art/icon_impala_48.png': 'impala/art/icon_impala_48.png',
    'beeswax/art/icon_beeswax_48.png': 'beeswax/art/icon_beeswax_48.png'
  },
  SQL_COLUMNS_KNOWN_FACET_VALUES: {
    type: { array: -1, boolean: -1 }
  },
  ace: {
    edit: () => ({
      setOptions: () => {},
      getSession: () => ({
        setMode: () => {},
        doc: {
          createAnchor: () => ({
            on: () => {},
            getPosition: () => ({
              row: 0
            }),
            setPosition: () => {},
            detach: () => {}
          })
        },
        getTextRange: () => {},
        addGutterDecoration: () => {},
        removeGutterDecoration: () => {}
      }),
      setTheme: () => {},
      getValue: () => '',
      getSelectionRange: () => ({ start: { row: 0, column: 0 }, end: { row: 0, column: 0 } }),
      on: () => {},
      off: () => {},
      commands: {
        on: () => {},
        off: () => {}
      },
      container: {
        addEventListener: () => {},
        removeEventListener: () => {}
      }
    }),
    require: () => ({
      Tooltip: Tooltip,
      Range: AceRange,
      Autocomplete: Autocomplete
    })
  }
};

Object.keys(globalVars).forEach(key => {
  global[key] = globalVars[key];
  global.window[key] = globalVars[key];
});

$.ajaxSetup({
  beforeSend: function () {
    console.warn('actual jQuery ajax called');
    console.trace();
  }
});

axios.interceptors.request.use(config => {
  console.warn('Actual axios ajax request made to url: ' + config.url);
  console.trace();
  return config;
});
