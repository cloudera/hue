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

const wordPattern = new RegExp(
  ['[A-Z][a-z]+', '[A-Z]+(?=[A-Z][a-z])', '[A-Z]+', '[a-z]+', '[0-9]+'].join('|'),
  'g'
);

export const words = (string = '', pattern: RegExp | string = wordPattern): string[] => {
  return string.match(pattern) || [];
};

export const toCamelCase = (string = ''): string => {
  return words(string)
    .map((word, index) =>
      index === 0 ? word.toLowerCase() : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    )
    .join('');
};

export const convertKeysToCamelCase = <T>(input: T): T => {
  // If input is an array, recursively process each item
  if (Array.isArray(input)) {
    return input.map(item => convertKeysToCamelCase(item)) as T;
  }

  // If input is an object, recursively process its keys and values
  if (input !== null && typeof input === 'object') {
    return Object.keys(input).reduce((acc, key) => {
      const camelKey = toCamelCase(key);
      const value = convertKeysToCamelCase(input[key as keyof typeof input]); // Recursively process values
      return {
        ...acc,
        [camelKey]: value
      };
    }, {} as T);
  }

  return input; // If input is a primitive value, return it as is
};
