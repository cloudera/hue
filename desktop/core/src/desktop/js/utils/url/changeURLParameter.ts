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

import changeURL from './changeURL';
import getParameter from './getParameter';

const changeURLParameter = (param: string, value: string | null): void => {
  let newSearch = '';
  if (getParameter(param, true) !== null) {
    newSearch += '?';
    window.location.search
      .replace(/\?/gi, '')
      .split('&')
      .forEach(p => {
        if (p.split('=')[0] !== param) {
          newSearch += p;
        }
      });
    if (value) {
      newSearch += (newSearch !== '?' ? '&' : '') + param + '=' + value;
    }
  } else {
    newSearch =
      window.location.search +
      (value ? (window.location.search.indexOf('?') > -1 ? '&' : '?') + param + '=' + value : '');
  }

  if (newSearch === '?') {
    newSearch = '';
  }

  changeURL(window.location.pathname + newSearch);
};

export default changeURLParameter;
