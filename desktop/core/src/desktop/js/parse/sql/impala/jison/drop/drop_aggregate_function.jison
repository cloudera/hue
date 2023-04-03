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
 : DropAggregateFunctionStatement
 ;

DataDefinition_EDIT
 : DropAggregateFunctionStatement_EDIT
 ;

DropAggregateFunctionStatement
 : 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList
 ;

DropAggregateFunctionStatement_EDIT
 : 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'CURSOR' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList
   {
     parser.suggestKeywords(['AGGREGATE']);
   }
 | 'DROP' 'AGGREGATE' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists_EDIT
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT ParenthesizedArgumentList
 ;
