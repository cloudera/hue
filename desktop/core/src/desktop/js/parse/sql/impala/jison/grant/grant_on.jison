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
 : GrantOnStatement
 ;

DataDefinition_EDIT
 : GrantOnStatement_EDIT
 ;

GrantOnStatement
 : 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' RegularOrBacktickedIdentifier OptionalWithGrantOption
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' GroupRoleOrUser RegularOrBacktickedIdentifier OptionalWithGrantOption
 ;

GrantOnStatement_EDIT
 : 'GRANT' PrivilegeType_EDIT
 | 'GRANT' PrivilegeType 'CURSOR'
   {
     if ($2.isCreate) {
       parser.suggestKeywords(['ON DATABASE', 'ON SERVER']);
     } else {
       parser.suggestKeywords(['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']);
     }
   }
 | 'GRANT' PrivilegeType 'ON' 'CURSOR'
   {
     if ($2.isCreate) {
        parser.suggestKeywords(['DATABASE', 'SERVER']);
     } else {
        parser.suggestKeywords(['DATABASE', 'SERVER', 'TABLE', 'URI']);
     }
   }
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification_EDIT
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' RegularOrBacktickedIdentifier OptionalWithGrantOption 'CURSOR'
   {
     if (!$7) {
       parser.suggestKeywords(['WITH GRANT OPTION']);
     }
   }
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' RegularOrBacktickedIdentifier WithGrantOption_EDIT
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' GroupRoleOrUser RegularOrBacktickedIdentifier OptionalWithGrantOption 'CURSOR'
   {
     if (!$8) {
       parser.suggestKeywords(['WITH GRANT OPTION']);
     }
   }
 | 'GRANT' PrivilegeType 'ON' ObjectSpecification 'TO' GroupRoleOrUser RegularOrBacktickedIdentifier WithGrantOption_EDIT
 ;

ObjectSpecification
 : 'DATABASE' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@2, [ { name: $2 } ]);
   }
 | 'TABLE' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($2);
   }
 | 'SERVER' RegularOrBacktickedIdentifier
 | 'URI' RegularOrBacktickedIdentifier
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
 ;

PrivilegeType
 : 'ALL'
 | 'ALTER'
 | 'CREATE'  -> { isCreate: true }
 | 'DROP'
 | 'INSERT'
 | 'REFRESH'
 | 'SELECT' OptionalParenthesizedColumnList
 ;

PrivilegeType_EDIT
 : 'SELECT' ParenthesizedColumnList_EDIT
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
