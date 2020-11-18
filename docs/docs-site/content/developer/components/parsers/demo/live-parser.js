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

const liveParsers = document.querySelectorAll('.live-parser-container');

function stringify(obj) {
  return JSON.stringify(obj, null, 2);
}

liveParsers.forEach(parserEl => {
  const scriptsContainer = parserEl.querySelector('.parser-scripts-container');
  const msg = parserEl.querySelector('.live-message');
  const select = parserEl.querySelector('select');
  const [queryText, jsonText] = parserEl.querySelectorAll('textarea');

  const parseQuery = () => {
    const parser = window[select.value];

    if (parser) {
      msg.innerHTML = 'Parser ready';

      const beforeCursor = queryText.value + ' ';
      const afterCursor = '';
      const debug = false;

      if (parser.parseSql) {
        const parsedObj = parser.parseSql(beforeCursor, afterCursor, debug);
        jsonText.value = stringify(parsedObj);
      } else if (parser.parseSyntax) {
        const parsedObj = parser.parseSyntax(beforeCursor.trim(), afterCursor);
        jsonText.value = stringify(parsedObj);
      } else {
        jsonText.value = '';
        msg.innerHTML = 'Invalid parser!';
      }
    } else {
      msg.innerHTML = 'Parser not loaded!';
    }
  };

  const loadParser = () => {
    const parser = window[select.value];

    if (parser) {
      parseQuery();
    } else {
      const parserFile = `/js/gethue/parsers/${select.value}.js`;

      const parserScript = document.createElement('script');
      parserScript.setAttribute('type', 'text/javascript');
      parserScript.setAttribute('src', parserFile);
      parserScript.addEventListener('load', parseQuery);
      parserScript.addEventListener('error', () => (msg.innerHTML = 'Parser loading failed!'));

      msg.innerHTML = 'Loading parser...';
      scriptsContainer.appendChild(parserScript);
    }
  };

  loadParser();

  select.onchange = loadParser;
  queryText.onkeyup = parseQuery;
});
