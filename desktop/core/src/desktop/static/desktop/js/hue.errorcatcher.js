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

(function () {

  /**
   * @param {string} [msg] - the error message
   * @param {string} [url] - the error url
   * @param {string} [line] - the error line number
   * @param {string} [column] - the error column number
   * @param {Object} [error] - available in some browsers, it contains the stack
   */
  window.onerror = function (msg, url, line, column, error) {
    if (msg && msg.isTrigger === 3) {
      return;
    }
    try {
      console.error('Hue detected a Javascript error: ', url, line, column, msg);
      var xmlHTTP = new XMLHttpRequest();
      var params = {
        msg: msg,
        url: url,
        line: line,
        column: column
      };
      if (error && error.stack) {
        params.stack = error.stack;
      }

      xmlHTTP.onreadystatechange = function () {
        if (xmlHTTP.readyState == 4 && xmlHTTP.status == 200) {
          console.warn('JS error sent correctly to the Hue logs');
        }
      }
      xmlHTTP.open('POST', '/desktop/log_js_error', true);
      xmlHTTP.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
      if (!XMLHttpRequest.prototype.isAugmented) {
        xmlHTTP.setRequestHeader('X-CSRFToken', window.CSRF_TOKEN); // from common_header_footer_components
      }
      xmlHTTP.send('jserror=' + JSON.stringify(params));
    }
    catch (e) {}
    return false;
  }

})()