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

const parseHivePseudoJson = (pseudoJson: string): { [key: string]: string } => {
  // Hive returns a pseudo-json with parameters, like
  // "{Lead Developer=John Foo, Lead Developer Email=jfoo@somewhere.com, date=2013-07-11 }"
  const parsedParams: { [key: string]: string } = {};
  if (pseudoJson && pseudoJson.length > 2) {
    const splits = pseudoJson.substring(1, pseudoJson.length - 1).split(', ');
    splits.forEach(part => {
      if (part.indexOf('=') > -1) {
        parsedParams[part.split('=')[0]] = part.split('=')[1];
      }
    });
  }
  return parsedParams;
};

export default parseHivePseudoJson;
