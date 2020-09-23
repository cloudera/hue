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
 : 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'ROLE', 'SELECT', 'UPDATE']);
   }
 ;

OptionalOnSpecification
 :
 | 'ON' ObjectSpecification
 ;

OnSpecification_EDIT
 : 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'TABLE']);
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ON' ObjectSpecification_EDIT
 ;

ObjectSpecification
 : 'DATABASE' RegularOrBacktickedIdentifier
 | 'TABLE' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($2);
   }
 | SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($1);
   }
 ;

ObjectSpecification_EDIT
 : 'DATABASE' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 | SchemaQualifiedTableIdentifier_EDIT
 ;

PrivilegeTypeList
 : PrivilegeTypeWithOptionalColumn
   {
     if ($1.toUpperCase() === 'ALL') {
       $$ = { singleAll: true };
     }
   }
 | PrivilegeTypeList ',' PrivilegeTypeWithOptionalColumn
 ;

PrivilegeTypeList_EDIT
 : PrivilegeTypeWithOptionalColumn_EDIT
 | PrivilegeTypeList ',' PrivilegeTypeWithOptionalColumn_EDIT
 | PrivilegeTypeWithOptionalColumn_EDIT ',' PrivilegeTypeList
 | PrivilegeTypeList ',' PrivilegeTypeWithOptionalColumn_EDIT ',' PrivilegeTypeList
 | 'CURSOR' ',' PrivilegeTypeList
   {
     parser.suggestKeywords(['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']);
   }
 | PrivilegeTypeList ',' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']);
   }
 | PrivilegeTypeList ',' 'CURSOR' ',' PrivilegeTypeList
   {
     parser.suggestKeywords(['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']);
   }
 ;

PrivilegeTypeWithOptionalColumn
 : PrivilegeType OptionalParenthesizedColumnList
 ;

PrivilegeTypeWithOptionalColumn_EDIT
 : PrivilegeType ParenthesizedColumnList_EDIT
 ;

PrincipalSpecificationList
 : PrincipalSpecification
 | PrincipalSpecificationList ',' PrincipalSpecification
 ;

PrincipalSpecificationList_EDIT
 : PrincipalSpecificationList ',' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'CURSOR' ',' PrincipalSpecificationList
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | PrincipalSpecificationList ',' 'CURSOR' ',' PrincipalSpecificationList
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 ;

PrincipalSpecification
 : 'USER' RegularOrBacktickedIdentifier
 | 'GROUP' RegularOrBacktickedIdentifier
 | 'ROLE' RegularOrBacktickedIdentifier
 ;

PrincipalSpecification_EDIT
 : 'USER' 'CURSOR'
 | 'GROUP' 'CURSOR'
 | 'ROLE' 'CURSOR'
 ;

UserOrRoleList
 : RegularOrBacktickedIdentifier
 | UserOrRoleList ',' RegularOrBacktickedIdentifier
 ;

OptionalWithAdminOption
 :
 | 'WITH' 'ADMIN' 'OPTION'
 ;

WithAdminOption_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['ADMIN OPTION']);
   }
 | 'WITH' 'ADMIN' 'CURSOR'
   {
     parser.suggestKeywords(['OPTION']);
   }
 ;
