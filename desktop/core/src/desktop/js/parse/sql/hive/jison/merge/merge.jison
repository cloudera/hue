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
 : MergeStatement
 ;

DataManipulation_EDIT
 : MergeStatement_EDIT
 ;

MergeStatement
 : MergeStatementLeftPart 'ON' ValueExpression WhenList
 ;

MergeStatement_EDIT
 : MergeStatementLeftPart_EDIT
 | MergeStatementLeftPart 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | MergeStatementLeftPart 'ON' 'CURSOR'
   {
     parser.valueExpressionSuggest();
   }
 | MergeStatementLeftPart 'ON' ValueExpression_EDIT
 | MergeStatementLeftPart 'ON' ValueExpression 'CURSOR'
   {
     parser.suggestValueExpressionKeywords($3, [{ value: 'WHEN', weight: 2 }]);
   }
 | MergeStatementLeftPart 'ON' ValueExpression WhenList_EDIT
 ;

MergeStatementLeftPart
 : 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' RegularIdentifier 'USING' MergeSource 'AS' RegularIdentifier
   {
     $3.alias = $5;
     parser.addTablePrimary($3);
     if ($7.subQuery) {
       parser.addTablePrimary({ subQueryAlias: $9 });
     } else {
       $7.alias = $9;
     }
   }
 ;

MergeStatementLeftPart_EDIT
 : 'MERGE' 'CURSOR'
   {
     parser.suggestKeywords(['INTO']);
   }
 | 'MERGE' 'INTO' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier_EDIT
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['AS T USING']);
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['T USING']);
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' RegularIdentifier 'CURSOR'
   {
     $3.alias = $5;
     parser.addTablePrimary($3);
     parser.suggestKeywords(['USING']);
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' RegularIdentifier 'USING' 'CURSOR'
   {
     $3.alias = $5;
     parser.addTablePrimary($3);
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' RegularIdentifier 'USING' MergeSource_EDIT
   {
     $3.alias = $5;
     parser.addTablePrimary($3);
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' RegularIdentifier 'USING' MergeSource 'CURSOR'
   {
     $3.alias = $5;
     parser.addTablePrimary($3);
     parser.suggestKeywords(['AS S ON']);
   }
 | 'MERGE' 'INTO' SchemaQualifiedTableIdentifier 'AS' RegularIdentifier 'USING' MergeSource 'AS' 'CURSOR'
   {
     $3.alias = $5;
     parser.addTablePrimary($3);
     parser.suggestKeywords(['S ON']);
   }
 ;

MergeSource
 : '(' TableSubQueryInner ')'  -> $2
 | SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($1);
   }
 ;

MergeSource_EDIT
 : '(' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['SELECT']);
   }
 | '(' TableSubQueryInner_EDIT RightParenthesisOrError
 | SchemaQualifiedTableIdentifier_EDIT
 ;

WhenList
 : WhenClause
 | WhenClause WhenClause
 | WhenClause WhenClause WhenClause
 ;

WhenList_EDIT
 : WhenClause_EDIT
   {
     if ($1.suggestThenKeywords) {
       parser.suggestKeywords(['DELETE', 'INSERT VALUES', 'UPDATE SET']);
     }
   }
 | WhenClause 'CURSOR'
   {
     if (!$1.notPresent) {
       parser.suggestKeywords(['WHEN']);
     }
   }
 | WhenClause WhenClause_EDIT
  {
     if (!$1.notPresent && $2.suggestThenKeywords) {
       var keywords = [];
       if (!$1.isDelete) {
         keywords.push('DELETE');
       }
       if (!$1.isInsert) {
         keywords.push('INSERT VALUES');
       }
       if (!$1.isUpdate) {
         keywords.push('UPDATE SET');
       }
       parser.suggestKeywords(keywords);
     }
   }
 | WhenClause WhenClause 'CURSOR'
   {
     if (!$2.notPresent) {
       parser.suggestKeywords(['WHEN']);
     }
   }
 | WhenClause WhenClause WhenClause_EDIT
   {
     if (!$2.notPresent && $3.suggestThenKeywords) {
       var keywords = [];
       if (!$1.isDelete && !$2.isDelete) {
         keywords.push('DELETE');
       }
       if (!$1.isInsert && !$2.isInsert) {
         keywords.push('INSERT VALUES');
       }
       if (!$1.isUpdate && !$2.isUpdate) {
         keywords.push('UPDATE SET');
       }
       parser.suggestKeywords(keywords);
     }
   }
 ;

WhenClause
 : 'WHEN' OptionalNot 'MATCHED' OptionalMatchCondition 'THEN' UpdateDeleteOrInsert  -> { notPresent: !!$2, isDelete: $6.isDelete, isInsert: $6.isInsert, isUpdate: $6.isUpdate }
 ;

WhenClause_EDIT
 : 'WHEN' OptionalNot 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['NOT MATCHED', 'MATCHED']);
     } else {
       parser.suggestKeywords(['MATCHED']);
     }
   }
 | 'WHEN' OptionalNot 'MATCHED' OptionalMatchCondition 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['AND', 'THEN']);
     } else {
       parser.suggestValueExpressionKeywords($4, [{ value: 'THEN', weight: 2 }]);
     }
   }
 | 'WHEN' OptionalNot 'MATCHED' MatchCondition_EDIT
 | 'WHEN' OptionalNot 'MATCHED' OptionalMatchCondition 'THEN' 'CURSOR' -> { suggestThenKeywords: true }
 | 'WHEN' OptionalNot 'MATCHED' OptionalMatchCondition 'THEN' UpdateDeleteOrInsert_EDIT
 ;

OptionalMatchCondition
 :
 | 'AND' ValueExpression -> $2
 ;

MatchCondition_EDIT
 : 'AND' 'CURSOR'
   {
     parser.valueExpressionSuggest();
   }
 ;

UpdateDeleteOrInsert
 : 'UPDATE' 'SET' SetClauseList        -> { isUpdate: true }
 | 'DELETE'                            -> { isDelete: true }
 | 'INSERT' ValuesClause  -> { isInsert: true }
 ;

UpdateDeleteOrInsert_EDIT
 : 'UPDATE' 'CURSOR'
   {
     parser.suggestKeywords(['SET']);
   }
 | 'UPDATE' 'SET' SetClauseList_EDIT
 | 'INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['VALUES']);
   }
 ;
