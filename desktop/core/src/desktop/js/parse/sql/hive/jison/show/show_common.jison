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

DataDefinition_EDIT
 : 'SHOW' 'CURSOR'
   {
     parser.suggestKeywords('SHOW');
   }
 | 'SHOW' 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     // ROLES is considered a non-reserved keywords so we can't match it in ShowCurrentRolesStatement_EDIT
     if ($3.identifierChain && $3.identifierChain.length === 1 && $3.identifierChain[0].name.toLowerCase() === 'roles') {
       parser.suggestKeywords(['CURRENT']);
       parser.yy.locations.pop();
     } else {
       parser.addTablePrimary($3);
     }
   }
 | 'SHOW' 'CURSOR' LIKE SingleQuotedValue
   {
     parser.suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
   }
 ;

OptionalLike
 :
 | 'LIKE' SingleQuotedValue
 ;

Like_EDIT
 : 'LIKE' 'CURSOR'
 ;
