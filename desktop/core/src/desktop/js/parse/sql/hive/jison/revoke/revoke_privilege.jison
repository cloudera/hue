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
 : RevokePrivilegeStatement
 ;

DataDefinition_EDIT
 : RevokePrivilegeStatement_EDIT
 ;

RevokePrivilegeStatement
 : 'REVOKE' PrivilegeTypeList OptionalOnSpecification 'FROM' PrincipalSpecificationList
 ;

RevokePrivilegeStatement_EDIT
 : 'REVOKE' PrivilegeTypeList_EDIT
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
 ;
