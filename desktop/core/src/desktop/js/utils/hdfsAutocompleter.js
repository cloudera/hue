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

import apiHelper from 'api/apiHelper';

const TIME_TO_LIVE_IN_MILLIS = 60000; // 1 minute

class HdfsAutocompleter {
  /**
   * @param {object} options
   * @param {string} options.user
   * @param {Number} options.timeout
   * @param {Snippet} options.snippet
   *
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.user = options.user;
    self.snippet = options.snippet;
    self.timeout = options.timeout;
  }

  getTotalStorageUserPrefix() {
    const self = this;
    return self.user;
  }

  hasExpired(timestamp) {
    return new Date().getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  }

  extractFields(data) {
    const files = data.files.map(file => {
      return {
        name: file.name,
        type: file.type
      };
    });

    files.sort((a, b) => a.name.localeCompare(b.name));

    const result = [];
    files.forEach((field, idx) => {
      if (field.name !== '..' && field.name !== '.') {
        result.push({
          value: field.name,
          score: 1000 - idx,
          meta: field.type
        });
      }
    });
    return result;
  }

  autocomplete(beforeCursor, afterCursor, callback, editor) {
    const self = this;

    const onFailure = function() {
      callback([]);
    };

    if (beforeCursor.match(/["'](?:\/[^\/]*)+/)) {
      const parts = beforeCursor.split('/');
      // Drop the first " or '
      parts.shift();
      // Last one is either partial name or empty
      parts.pop();

      const successCallback = function(data) {
        if (!data.error) {
          callback(self.extractFields(data));
        } else {
          onFailure();
        }
      };

      apiHelper.fetchHdfsPath({
        pathParts: parts,
        successCallback: successCallback,
        silenceErrors: true,
        errorCallback: onFailure,
        timeout: self.timeout,
        editor: editor
      });
    } else {
      onFailure();
    }
  }

  getDocTooltip(item) {}
}

export default HdfsAutocompleter;
