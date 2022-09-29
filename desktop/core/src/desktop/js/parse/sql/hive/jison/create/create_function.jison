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
 : CreateFunction
 ;

DataDefinition_EDIT
 : CreateFunction_EDIT
 ;

CreateFunction
 : 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'AS' SingleQuotedValue OptionalUsing
 ;

CreateFunction_EDIT
 : 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'AS' SingleQuotedValue OptionalUsing_EDIT
 | 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'AS' SingleQuotedValue OptionalUsing 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['USING']);
     } else {
       parser.suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
     }
   }
 ;

OptionalUsing
 :
 | 'USING' OneOrMoreFunctionResources
 ;

OptionalUsing_EDIT
 : 'USING' 'CURSOR'
   {
     parser.suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
   }
 ;

OneOrMoreFunctionResources
 : FunctionResource
 | OneOrMoreFunctionResources ',' FunctionResource
 ;

FunctionResource
 : FunctionResourceType SingleQuotedValue
 ;

FunctionResourceType
 : 'ARCHIVE'
 | 'FILE'
 | 'JAR'
 ;
