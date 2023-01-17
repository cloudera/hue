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
 : RevokeGrantOptionForStatement
 ;

DataDefinition_EDIT
 : RevokeGrantOptionForStatement_EDIT
 ;

RevokeGrantOptionForStatement
 : 'REVOKE' 'GRANT' 'OPTION' 'FOR' PrivilegeTypeList OptionalOnSpecification 'FROM' PrincipalSpecificationList
 ;

RevokeGrantOptionForStatement_EDIT
 : 'REVOKE' 'GRANT' 'CURSOR'
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
 ;
