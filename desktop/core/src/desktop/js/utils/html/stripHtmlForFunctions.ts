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

const stripHtml = (html: string): string => {
  const tmp = document.createElement('DIV');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText;
};

const stripHtmlFromFunctions = (template: string): string => {
  // strips HTML from inside the functions
  let stripped = template;
  const mustacheFunctions = stripped.match(/{{#(.[\s\S]*?){{\//g);
  if (mustacheFunctions) {
    mustacheFunctions.forEach(fn => {
      stripped = stripped.replace(
        fn,
        fn.substr(0, fn.indexOf('}}') + 2) +
          stripHtml(fn.substr(fn.indexOf('}}') + 2).slice(0, -3)).trim() +
          '{{/'
      );
    });
  }
  return stripped;
};

export default stripHtmlFromFunctions;
