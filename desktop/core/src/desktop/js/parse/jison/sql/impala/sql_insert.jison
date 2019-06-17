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

DataManipulation
 : InsertStatement
 ;

InsertStatement
 : InsertOrUpsertStatement
 | CommonTableExpression InsertOrUpsertStatement
 ;

DataManipulation_EDIT
 : InsertOrUpsertStatement_EDIT
 | CommonTableExpression InsertOrUpsertStatement_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression_EDIT InsertOrUpsertStatement
 ;

OptionalTable
 :
 | 'TABLE'
 ;

SelectWithoutTableExpression
 : 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList  -> { selectList: $4 }
 ;

SelectWithoutTableExpression_EDIT
 : 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList 'CURSOR'
   {
     $$ = $4;
     $$.cursorAtEnd = true;
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList_EDIT
   {
     parser.selectListNoTableSuggest($4, $2);
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin 'CURSOR'
   {
     var keywords = parser.getSelectListKeywords();
     if (!$2 || $2 === 'ALL') {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (!$3 && !$2) {
       keywords.push({ value: 'ALL', weight: 2 });
       keywords.push({ value: 'DISTINCT', weight: 2 });
     }
     if (!$3) {
       keywords.push({ value: 'STRAIGHT_JOIN', weight: 1 });
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns();
   }
 ;

InsertOrUpsertStatement
 : InsertOrUpsertStatementWithoutCTE
 ;

InsertOrUpsertStatement_EDIT
 : InsertOrUpsertStatementWithoutCTE_EDIT
 ;

InsertOrUpsertStatementWithoutCTE
 : InsertOrUpsertLeftPart OptionalShuffleOrNoShuffle SelectStatement OptionalUnions
 | InsertOrUpsertLeftPart 'VALUES' RowValuesLists
 ;

InsertOrUpsertStatementWithoutCTE_EDIT
 : InsertOrUpsertLeftPart_EDIT
 | InsertOrUpsertLeftPart OptionalShuffleOrNoShuffle 'CURSOR'
   {
     var keywords = $1.suggestKeywords && !$2 ? parser.createWeightedKeywords($1.suggestKeywords, 2) : [];
     if (!$2) {
       keywords = keywords.concat(['[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES'])
     } else {
       keywords = keywords.concat(['SELECT'])
     }
     parser.suggestKeywords(keywords);
   }
 | InsertOrUpsertLeftPart_EDIT OptionalShuffleOrNoShuffle SelectStatement OptionalUnions
 | InsertOrUpsertLeftPart OptionalShuffleOrNoShuffle SelectStatement_EDIT OptionalUnions
 | InsertOrUpsertLeftPart OptionalShuffleOrNoShuffle SelectStatement OptionalUnions_EDIT
 | InsertOrUpsertLeftPart_EDIT 'VALUES' RowValuesLists
 | InsertOrUpsertLeftPart 'VALUES' RowValuesLists_EDIT
 ;

InsertOrUpsertLeftPart
 : UpsertStatementLeftPart
 | InsertLeftPart
 ;

InsertOrUpsertLeftPart_EDIT
 : UpsertStatementLeftPart_EDIT
 | InsertLeftPart_EDIT
 ;

UpsertStatementLeftPart
 : 'UPSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList
   {
     $4.owner = 'upsert';
     parser.addTablePrimary($4);
   }
 ;

UpsertStatementLeftPart_EDIT
 : 'UPSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO']);
   }
 | 'UPSERT' 'INTO' OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'UPSERT' 'INTO' OptionalTable 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     $5.owner = 'upsert';
     parser.addTablePrimary($5);
   }
 | 'UPSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList
 | 'UPSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList_EDIT
   {
     $4.owner = 'upsert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'upsert';
     }
   }
 ;


InsertLeftPart
 : 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (!$6) {
       $$ = { suggestKeywords: ['PARTITION'] };
     }
   }
 ;

InsertLeftPart_EDIT
 : 'INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO', 'OVERWRITE']);
   }
 | 'INSERT' IntoOrOverwrite OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'INSERT' IntoOrOverwrite OptionalTable 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     $5.owner = 'insert';
     parser.addTablePrimary($5);
   }
 | 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList OptionalPartitionSpec
 | 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList_EDIT OptionalPartitionSpec
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec_EDIT
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 ;

IntoOrOverwrite
 : 'INTO'
 | 'OVERWRITE'
 ;

OptionalShuffleOrNoShuffle
 :
 | 'SHUFFLE'
 | 'NOSHUFFLE'
 ;

RowValuesLists
 : ParenthesizedValueExpressionList
 | RowValuesLists ',' ParenthesizedValueExpressionList
 ;

RowValuesLists_EDIT
 : ParenthesizedValueExpressionList_EDIT
 | RowValuesLists ',' ParenthesizedValueExpressionList_EDIT
 | RowValuesLists ',' ParenthesizedValueExpressionList_EDIT ',' RowValuesLists
 | ParenthesizedValueExpressionList_EDIT ',' RowValuesLists
 ;

ParenthesizedValueExpressionList
 : '(' ValueExpressionList ')'
 ;

ParenthesizedValueExpressionList_EDIT
 : '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestFunctions();
   }
 | '(' ValueExpressionList_EDIT RightParenthesisOrError
 ;

