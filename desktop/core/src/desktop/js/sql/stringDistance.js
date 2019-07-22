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

/**
 * Calculates the Optimal String Alignment distance between two strings. Returns 0 when the strings are equal and the
 * distance when not, distances is less than or equal to the length of the longest string.
 *
 * @param strA
 * @param strB
 * @param [ignoreCase]
 * @returns {number} The similarity
 */
const stringDistance = function(strA, strB, ignoreCase) {
  if (ignoreCase) {
    strA = strA.toLowerCase();
    strB = strB.toLowerCase();
  }

  // TODO: Consider other algorithms for performance
  const strALength = strA.length;
  const strBLength = strB.length;
  if (strALength === 0) {
    return strBLength;
  }
  if (strBLength === 0) {
    return strALength;
  }

  const distances = new Array(strALength);

  let cost, deletion, insertion, substitution, transposition;
  for (let i = 0; i <= strALength; i++) {
    distances[i] = new Array(strBLength);
    distances[i][0] = i;
    for (let j = 1; j <= strBLength; j++) {
      if (!i) {
        distances[0][j] = j;
      } else {
        cost = strA[i - 1] === strB[j - 1] ? 0 : 1;
        deletion = distances[i - 1][j] + 1;
        insertion = distances[i][j - 1] + 1;
        substitution = distances[i - 1][j - 1] + cost;
        if (deletion <= insertion && deletion <= substitution) {
          distances[i][j] = deletion;
        } else if (insertion <= deletion && insertion <= substitution) {
          distances[i][j] = insertion;
        } else {
          distances[i][j] = substitution;
        }

        if (i > 1 && j > 1 && strA[i] === strB[j - 1] && strA[i - 1] === strB[j]) {
          transposition = distances[i - 2][j - 2] + cost;
          if (transposition < distances[i][j]) {
            distances[i][j] = transposition;
          }
        }
      }
    }
  }

  return distances[strALength][strBLength];
};

export default stringDistance;
