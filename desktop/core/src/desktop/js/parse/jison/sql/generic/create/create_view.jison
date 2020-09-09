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

DataDefinition
 : ViewDefinition
 ;

DataDefinition_EDIT
 : ViewDefinition_EDIT
 ;

ViewDefinition
 : 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
 ;

ViewDefinition_EDIT
 : 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedViewColumnList_EDIT OptionalComment
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'CURSOR'
   {
     var keywords = [{value: 'AS', weight: 1 }];
     if (!$6) {
       keywords.push({ value: 'COMMENT', weight: 3 });
     }
     parser.suggestKeywords(keywords);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier_EDIT OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
 ;

OptionalParenthesizedViewColumnList
 :
 | ParenthesizedViewColumnList
 ;

ParenthesizedViewColumnList
 : '(' ViewColumnList ')'
 ;

ParenthesizedViewColumnList_EDIT
 : '(' ViewColumnList_EDIT RightParenthesisOrError
   {
     if (!$2) {
       parser.suggestKeywords(['COMMENT']);
     }
   }
 ;

ViewColumnList
 : ColumnReference OptionalComment
 | ViewColumnList ',' ColumnReference OptionalComment
 ;

ViewColumnList_EDIT
 : ColumnReference OptionalComment 'CURSOR'                                        -> $2
 | ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList                     -> $2
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR'                     -> $4
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList  -> $4
 ;
