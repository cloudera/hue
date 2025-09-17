// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

/**
 * Decodes common HTML entities to their corresponding characters without interpreting HTML.
 * Safe to use for text content only.
 */
export function decodeHtmlEntities(input: unknown): unknown {
  if (typeof input !== 'string') {
    return input;
  }
  if (!input) {
    return '';
  }
  // Use a DOM element to decode entities safely
  const textarea = document.createElement('textarea');
  textarea.innerHTML = input;
  return textarea.value;
}

export default decodeHtmlEntities;
