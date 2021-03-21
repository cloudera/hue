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
 : FunctionDefinition
 ;

DataDefinition_EDIT
 : FunctionDefinition_EDIT
 ;

FunctionDefinition
 : 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation SymbolDefinition
 ;

FunctionDefinition_EDIT
 : 'CREATE' 'FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation SymbolDefinition
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList 'CURSOR'
   {
     parser.suggestKeywords(['RETURNS']);
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType 'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation 'CURSOR'
   {
     parser.suggestKeywords(['SYMBOL']);
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation SymbolDefinition
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT ReturnType HdfsLocation SymbolDefinition
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT HdfsLocation SymbolDefinition
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation_EDIT SymbolDefinition
 ;

SymbolDefinition
 : 'SYMBOL' '=' SingleQuotedValue
 ;
