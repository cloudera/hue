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
 : GrantStatement
 | RevokeStatement
 ;

DataDefinition_EDIT
 : GrantStatement_EDIT
 | RevokeStatement_EDIT
 ;

GrantStatement
 : 'GRANT' PrivilegeTypeList OptionalOnSpecification 'TO' PrincipalSpecificationList OptionalWithGrantOption
 | 'GRANT' UserOrRoleList 'TO' PrincipalSpecificationList OptionalWithAdminOption
 | 'GRANT' 'ROLE' UserOrRoleList 'TO' PrincipalSpecificationList OptionalWithAdminOption
 ;

GrantStatement_EDIT
 : 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'ROLE', 'SELECT', 'UPDATE']);
   }
 | 'GRANT' PrivilegeTypeList_EDIT OptionalOnSpecification
 | 'GRANT' PrivilegeTypeList OnSpecification_EDIT
 | 'GRANT' PrivilegeTypeList OptionalOnSpecification 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['ON', 'TO']);
     } else {
       parser.suggestKeywords(['TO']);
     }
   }
 | 'GRANT' PrivilegeTypeList OptionalOnSpecification 'TO' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'GRANT' PrivilegeTypeList OptionalOnSpecification 'TO' PrincipalSpecificationList_EDIT
 | 'GRANT' PrivilegeTypeList OptionalOnSpecification 'TO' PrincipalSpecificationList OptionalWithGrantOption 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['WITH GRANT OPTION']);
     }
   }
 | 'GRANT' PrivilegeTypeList OptionalOnSpecification 'TO' PrincipalSpecificationList WithGrantOption_EDIT
 | 'GRANT' UserOrRoleList 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | 'GRANT' UserOrRoleList 'TO' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'GRANT' UserOrRoleList 'TO' PrincipalSpecificationList_EDIT
 | 'GRANT' UserOrRoleList 'TO' PrincipalSpecificationList OptionalWithAdminOption 'CURSOR'
   {
     if (!$5) {
       parser.suggestKeywords(['WITH ADMIN OPTION']);
     }
   }
 | 'GRANT' UserOrRoleList 'TO' PrincipalSpecificationList WithAdminOption_EDIT
 | 'GRANT' 'ROLE' UserOrRoleList 'TO' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'GRANT' 'ROLE' UserOrRoleList 'TO' PrincipalSpecificationList_EDIT
 | 'GRANT' 'ROLE' UserOrRoleList 'TO' PrincipalSpecificationList OptionalWithAdminOption 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['WITH ADMIN OPTION']);
     }
   }
 | 'GRANT' 'ROLE' UserOrRoleList 'TO' PrincipalSpecificationList WithAdminOption_EDIT
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

PrivilegeType
 : 'ALL'
 | 'ALTER'
 | 'CREATE'
 | 'DELETE'
 | 'DROP'
 | 'INDEX'
 | 'INSERT'
 | 'LOCK'
 | 'SELECT'
 | 'SHOW_DATABASE'
 | 'UPDATE'
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

OptionalWithGrantOption
 :
 | 'WITH' 'GRANT' 'OPTION'
 ;

WithGrantOption_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['GRANT OPTION']);
   }
 | 'WITH' 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['OPTION']);
   }
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

RevokeStatement
 : 'REVOKE' PrivilegeTypeList OptionalOnSpecification 'FROM' PrincipalSpecificationList
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList OptionalOnSpecification 'FROM' PrincipalSpecificationList
 | 'REVOKE' UserOrRoleList 'FROM' PrincipalSpecificationList
 | 'REVOKE' 'ROLE' UserOrRoleList 'FROM' PrincipalSpecificationList
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' UserOrRoleList 'FROM' PrincipalSpecificationList
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' 'ROLE' UserOrRoleList 'FROM' PrincipalSpecificationList
 | 'REVOKE' 'ALL' PrivilegesOrGrantOption 'FROM' UserOrRoleList
 ;

RevokeStatement_EDIT
 : 'REVOKE' 'CURSOR'
   {
     parser.suggestKeywords(['ADMIN OPTION FOR', 'ALL', 'ALL GRANT OPTION FROM', 'ALL PRIVILEGES FROM', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'GRANT OPTION FOR', 'INDEX', 'INSERT', 'LOCK', 'ROLE', 'SELECT', 'UPDATE']);
   }
 | 'REVOKE' PrivilegeTypeList_EDIT
 | 'REVOKE' PrivilegeTypeList OnSpecification_EDIT
 | 'REVOKE' PrivilegeTypeList OptionalOnSpecification 'CURSOR'
   {
     if (!$3) {
       if ($2.singleAll) {
         parser.suggestKeywords(['FROM', 'GRANT OPTION', 'ON', 'PRIVILEGES FROM']);
       } else {
         parser.suggestKeywords(['FROM', 'ON']);
       }
     } else {
       parser.suggestKeywords(['FROM']);
     }
   }
 | 'REVOKE' PrivilegeTypeList OptionalOnSpecification 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'REVOKE' PrivilegeTypeList OptionalOnSpecification 'FROM' PrincipalSpecificationList_EDIT
 | 'REVOKE' 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['OPTION FOR']);
   }
 | 'REVOKE' 'GRANT' 'OPTION' 'CURSOR'
   {
     parser.suggestKeywords(['FOR']);
   }
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']);
   }
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList_EDIT
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList OnSpecification_EDIT
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList OptionalOnSpecification 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['FROM', 'ON']);
     } else {
       parser.suggestKeywords(['FROM']);
     }
   }
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList OptionalOnSpecification 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList OptionalOnSpecification 'FROM' PrincipalSpecificationList_EDIT
 | 'REVOKE' UserOrRoleList 'CURSOR'
   {
     if ($2.toUpperCase() === 'ADMIN') {
       parser.suggestKeywords(['FROM', 'OPTION FOR']);
     } else {
       parser.suggestKeywords(['FROM']);
     }
   }
 | 'REVOKE' UserOrRoleList 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'REVOKE' UserOrRoleList 'FROM' PrincipalSpecificationList_EDIT
 | 'REVOKE' 'ROLE' UserOrRoleList 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'REVOKE' 'ROLE' UserOrRoleList 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'REVOKE' 'ROLE' UserOrRoleList 'FROM' PrincipalSpecificationList_EDIT

 | 'REVOKE' 'ADMIN' 'OPTION' 'CURSOR'
   {
     parser.suggestKeywords(['FOR']);
   }
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' 'CURSOR'
   {
     parser.suggestKeywords(['ROLE']);
   }
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' UserOrRoleList 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' UserOrRoleList 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' UserOrRoleList 'FROM' PrincipalSpecificationList_EDIT
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' 'ROLE' UserOrRoleList 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' 'ROLE' UserOrRoleList 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'REVOKE' 'ADMIN' 'OPTION' 'FOR' 'ROLE' UserOrRoleList 'FROM' PrincipalSpecificationList_EDIT
 | 'REVOKE' 'ALL' PrivilegesOrGrantOption_EDIT
 | 'REVOKE' 'ALL' PrivilegesOrGrantOption 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 ;

PrivilegesOrGrantOption
 : 'PRIVILEGES'
 | 'GRANT' 'OPTION'
 ;

PrivilegesOrGrantOption_EDIT
 : 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['OPTION']);
   }
 ;
