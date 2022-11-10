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
 : InsertTableStatement
 ;

DataManipulation_EDIT
 : InsertTableStatement_EDIT
 ;

InsertTableStatement
 : 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList ValuesClauseOrQuerySpecification
 ;

InsertTableStatement_EDIT
 : 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalParenthesizedColumnList
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.tablesOnly = true;
     }
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList 'CURSOR'
   {
     if (!$5 && !$4) {
       parser.suggestKeywords(['PARTITION', 'SELECT', 'VALUES']);
     } else {
       parser.suggestKeywords(['SELECT', 'VALUES']);
     }
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier PartitionSpec_EDIT OptionalParenthesizedColumnList
   {
     parser.addTablePrimary($3);
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier PartitionSpec_EDIT OptionalParenthesizedColumnList ValuesClauseOrQuerySpecification
   {
     parser.addTablePrimary($3);
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier OptionalPartitionSpec ParenthesizedColumnList_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier OptionalPartitionSpec ParenthesizedColumnList_EDIT ValuesClauseOrQuerySpecification
   {
     parser.addTablePrimary($3);
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalParenthesizedColumnList ValuesClauseOrQuerySpecification
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.tablesOnly = true;
     }
   }
 | 'INSERT' OptionalInsertOptions 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList ValuesClauseOrQuerySpecification
   {
     if ($2.tableKeywords) {
       parser.suggestKeywords($2.tableKeywords);
     }
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList 'CURSOR' ValuesClauseOrQuerySpecification
   {
     if (!$4 && !$5) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'INSERT' OptionalInsertOptions SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList ValuesClauseOrQuerySpecification_EDIT
 ;