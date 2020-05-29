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

export const getSubQuery = cols => {
  const columns = [];
  cols.selectList.forEach(col => {
    const result = {};
    if (col.alias) {
      result.alias = col.alias;
    }
    if (col.valueExpression && col.valueExpression.columnReference) {
      result.identifierChain = col.valueExpression.columnReference;
    } else if (col.asterisk) {
      result.identifierChain = [{ asterisk: true }];
    }
    if (
      col.valueExpression &&
      col.valueExpression.types &&
      col.valueExpression.types.length === 1
    ) {
      result.type = col.valueExpression.types[0];
    }

    columns.push(result);
  });

  return {
    columns: columns
  };
};

export const applyTypeToSuggestions = (parser, types) => {
  if (types[0] === 'BOOLEAN') {
    return;
  }
  if (this.yy.result.suggestFunctions && !this.yy.result.suggestFunctions.types) {
    this.yy.result.suggestFunctions.types = types;
  }
  if (this.yy.result.suggestColumns && !this.yy.result.suggestColumns.types) {
    this.yy.result.suggestColumns.types = types;
  }
};

export const valueExpressionSuggest = (parser, oppositeValueExpression, operator) => {
  if (oppositeValueExpression && oppositeValueExpression.columnReference) {
    parser.suggestValues();
    parser.yy.result.colRef = { identifierChain: oppositeValueExpression.columnReference };
  }
  parser.suggestColumns();
  parser.suggestFunctions();
  let keywords = [
    { value: 'CASE', weight: 450 },
    { value: 'FALSE', weight: 450 },
    { value: 'NULL', weight: 450 },
    { value: 'TRUE', weight: 450 }
  ];
  if (typeof oppositeValueExpression === 'undefined' || typeof operator === 'undefined') {
    keywords = keywords.concat(['EXISTS', 'NOT']);
  }
  if (oppositeValueExpression && oppositeValueExpression.types[0] === 'NUMBER') {
    applyTypeToSuggestions(parser, ['NUMBER']);
  }
  parser.suggestKeywords(keywords);
};
