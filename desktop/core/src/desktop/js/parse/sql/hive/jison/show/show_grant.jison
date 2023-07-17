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
 : ShowGrantStatement
 ;

DataDefinition_EDIT
 : ShowGrantStatement_EDIT
 ;

ShowGrantStatement
 : 'SHOW' 'GRANT' OptionalPrincipalName
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'ALL'
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' SchemaQualifiedTableIdentifier
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'TABLE' SchemaQualifiedTableIdentifier
 ;

ShowGrantStatement_EDIT
 : 'SHOW' 'GRANT' PrincipalName_EDIT
   {
     parser.suggestKeywords(['ON']);
   }
 | 'SHOW' 'GRANT' PrincipalName_EDIT 'ON' 'ALL'
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'TABLE']);
     parser.suggestTables();
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' SchemaQualifiedTableIdentifier_EDIT
 | 'SHOW'  'GRANT' OptionalPrincipalName 'ON' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'CURSOR' SchemaQualifiedTableIdentifier_EDIT
 ;

OptionalPrincipalName
 :
 | RegularIdentifier
 ;

PrincipalName_EDIT
 : 'CURSOR'
 | RegularIdentifier 'CURSOR'
 ;
