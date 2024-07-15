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

import sanitizeHtml, { IOptions } from 'sanitize-html';

const deXSS = (
  str?: undefined | boolean | string | number | null | unknown,
  options?: IOptions
): string => {
  if (str === null) {
    return 'null';
  }
  //Fix for sanitize HTML returns empty string for boolean false values.
  if (typeof str === 'boolean') {
    return str.toString();
  }
  if (typeof str !== 'undefined') {
    // This handles cases where 'str' is a object, ensuring it is properly
    // serialized into a JSON format before sanitization.
    let finalStr: string;
    if (typeof str === 'object' && !Array.isArray(str)) {
      finalStr = JSON.stringify(str);
    } else {
      finalStr = str.toString();
    }
    return sanitizeHtml(finalStr, options) || '';
  }
  return '';
};

export default deXSS;
