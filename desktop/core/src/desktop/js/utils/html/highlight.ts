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

const highlight = (text: string, searchTerm: string): string => {
  if (searchTerm === '' || text === '') {
    return text;
  }

  let remText = text;
  let highLightedText = '';
  searchTerm = searchTerm.toLowerCase();

  let startIndex;
  do {
    const remLowerText = remText.toLowerCase();
    startIndex = remLowerText.indexOf(searchTerm);
    if (startIndex >= 0) {
      highLightedText += `${remText.substring(0, startIndex)}<strong>${remText.substring(
        startIndex,
        startIndex + searchTerm.length
      )}</strong>`;
      remText = remText.substring(startIndex + searchTerm.length);
    } else {
      highLightedText += remText;
    }
  } while (startIndex >= 0);

  return highLightedText;
};

export default highlight;
