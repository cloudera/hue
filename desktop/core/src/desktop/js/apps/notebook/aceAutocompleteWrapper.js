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

import HdfsAutocompleter from 'utils/hdfsAutocompleter';

class AceAutocompleteWrapper {
  /**
   * @param {Object} options {object}
   * @param options.snippet
   * @param options.user
   * @param options.optEnabled
   * @param {Number} options.timeout
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.snippet = options.snippet;
    self.timeout = options.timeout;

    self.topTables = {};

    const initializeAutocompleter = function() {
      self.autocompleter = new HdfsAutocompleter({
        user: options.user,
        snippet: options.snippet,
        timeout: options.timeout
      });
    };
    self.snippet.type.subscribe(() => {
      initializeAutocompleter();
    });
    initializeAutocompleter();
  }

  // TODO: See why we need this one.
  initializeAutocompleter() {}

  // ACE Format for autocompleter
  getCompletions(editor, session, pos, prefix, callback) {
    const self = this;
    if (!self.autocompleter) {
      return;
    }

    const before = editor.getTextBeforeCursor();
    const after = editor.getTextAfterCursor(';');

    try {
      self.autocomplete(
        before,
        after,
        result => {
          callback(null, result);
        },
        editor
      );
    } catch (err) {
      editor.hideSpinner();
    }
  }

  getDocTooltip(item) {
    const self = this;
    return self.autocompleter.getDocTooltip(item);
  }

  autocomplete(beforeCursor, afterCursor, callback, editor) {
    const self = this;
    if (self.autocompleter) {
      self.autocompleter.autocomplete(beforeCursor, afterCursor, callback, editor);
    }
  }
}

export default AceAutocompleteWrapper;
