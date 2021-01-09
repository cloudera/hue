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
 : TableDefinition
 ;

DataDefinition_EDIT
 : TableDefinition_EDIT
 ;

TableDefinition
 : 'CREATE' 'TABLE' SchemaQualifiedIdentifier 'AS' QuerySpecification
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier 'WITH (' TableWithDefinition ')'
 ;

TableWithDefinition
 : TableWithDefinitionLine
 | TableWithDefinitionLine ',' TableWithDefinition
 ;

TableWithDefinitionLine
 : SchemaQualifiedIdentifier '=' GeneralLiteral
 ;

TableDefinition_EDIT
 : 'CREATE' 'TABLE'_EDIT
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS', "WITH ("]);
   }
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier 'AS' QuerySpecification_EDIT
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier 'WITH (' TableWithDefinition_EDIT ')'
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier_EDIT 'AS' QuerySpecification
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier_EDIT 'WITH (' TableWithDefinition 'CURSOR'
   {
     parser.suggestKeywords([')']);
   }
 | 'CREATE' 'TABLE' SchemaQualifiedIdentifier_EDIT 'WITH (' TableWithDefinition ')'
 ;

TableWithDefinition_EDIT
 : TableWithDefinitionLine_EDIT
 | TableWithDefinitionLine 'CURSOR'
   {
     parser.suggestKeywords([',', ')']);
   }
 | TableWithDefinitionLine ',' TableWithDefinition_EDIT
 ;

TableWithDefinitionLine_EDIT
 : SchemaQualifiedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | SchemaQualifiedIdentifier '=' GeneralLiteral_EDIT
 | SchemaQualifiedIdentifier_EDIT '=' GeneralLiteral
 ;