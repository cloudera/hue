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
 : GrantRoleStatement
 ;

DataDefinition_EDIT
 : GrantRoleStatement_EDIT
 ;

GrantRoleStatement
 : 'GRANT' 'ROLE' UserOrRoleList 'TO' PrincipalSpecificationList OptionalWithAdminOption
 ;

GrantRoleStatement_EDIT
 : 'GRANT' 'ROLE' UserOrRoleList 'TO' 'CURSOR'
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
