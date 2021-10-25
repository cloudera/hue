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
 : UpsertStatement
 ;

UpsertStatement
 : UpsertValuesStatement
 ;

DataManipulation_EDIT
 : UpsertValuesStatement_EDIT
 ;

UpsertValuesStatement
 : 'UPSERT' 'INTO' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList 'VALUES' InsertValuesList
   {
     $3.owner = 'upsert';
     parser.addTablePrimary($3);
   }
 | 'UPSERT' 'INTO' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList SelectStatement
   {
     $3.owner = 'upsert';
     parser.addTablePrimary($3);
   }
 ;

UpsertValuesStatement_EDIT
 : 'UPSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO']);
   }
 | 'UPSERT' 'INTO' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'UPSERT' 'INTO'  SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList SelectStatement
 | 'UPSERT' 'INTO'  SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList SelectStatement_EDIT
 | 'UPSERT' 'INTO'  SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList OptionalValues
 | 'UPSERT' 'INTO'  SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList_EDIT OptionalValues
   {
     $3.owner = 'upsert';
     parser.addTablePrimary($3);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'upsert';
     }
   }
 | 'UPSERT' 'INTO' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList 'CURSOR' OptionalInsertValuesList
   {
     $3.owner = 'upsert';
     parser.addTablePrimary($3);
     parser.suggestKeywords(['VALUES', 'SELECT']);
   }
 ;

OptionalValues
 :
 | 'VALUES' OptionalInsertValuesList
 ;

OptionalInsertValuesList
 :
 | InsertValuesList
 ;

InsertValuesList
 : ParenthesizedRowValuesList
 | InsertValuesList ',' ParenthesizedRowValuesList
 ;

ParenthesizedRowValuesList
 : '(' InValueList ')'
 ;
