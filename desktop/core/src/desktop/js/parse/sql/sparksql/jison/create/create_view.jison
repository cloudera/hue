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
 : CreateView
 ;

DataDefinition_EDIT
 : CreateView_EDIT
 ;

CreateView
 : CreateViewLeftPart SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalTblProperties AsQuerySpecification
 ;

CreateView_EDIT
 : CreateViewLeftPart_EDIT
 | CreateViewLeftPart_EDIT SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalTblProperties
 | CreateViewLeftPart_EDIT SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalTblProperties AsQuerySpecification
 | CreateViewLeftPart 'CURSOR'
   {
     parser.checkForKeywords($1);
     parser.suggestDatabases({ appendDot: true });
   }
 | CreateViewLeftPart SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       delete parser.yy.result.suggestTables;
     }
   }
 | CreateViewLeftPart SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalTblProperties 'CURSOR'
   {
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR(
       [undefined, $5, $4],
       [{ value: 'AS', weight: 1 },
        { value: 'TBLPROPERTIES', weight: 2 },
        { value: 'COMMENT', weight: 3 }]));
   }
 | CreateViewLeftPart SchemaQualifiedTableIdentifier ParenthesizedColumnSpecificationList_EDIT OptionalComment OptionalTblProperties
 | CreateViewLeftPart SchemaQualifiedTableIdentifier ParenthesizedColumnSpecificationList_EDIT OptionalComment OptionalTblProperties AsQuerySpecification
 | CreateViewLeftPart SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalTblProperties AsQuerySpecification_EDIT
 | CreateViewLeftPart 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalTblProperties AsQuerySpecification
   {
     parser.checkForKeywords($1);
   }
 ;

CreateViewLeftPart
 : 'CREATE' OptionalOrReplace OptionalTemporary 'VIEW' OptionalIfNotExists
   {
     if (!$5) {
       $$ = { suggestKeywords: ['IF NOT EXISTS'] };
     }
   }
 ;

CreateViewLeftPart_EDIT
 : 'CREATE' OptionalOrReplace OptionalTemporary 'CURSOR' 'VIEW' OptionalIfNotExists
   {
     if (!$3 && !$2) {
       parser.yy.suggestKeywords(['OR REPLACE', 'GLOBAL TEMPORARY', 'TEMPORARY']);
     } else if (!$2) {
       parser.yy.suggestKeywords(['GLOBAL TEMPORARY', 'TEMPORARY']);
     }
   }
 | 'CREATE' OrReplace_EDIT OptionalTemporary 'VIEW' OptionalIfNotExists
 | 'CREATE' OptionalOrReplace Temporary_EDIT 'VIEW' OptionalIfNotExists
 | 'CREATE' OptionalOrReplace OptionalTemporary 'VIEW' IfNotExists_EDIT
 ;
