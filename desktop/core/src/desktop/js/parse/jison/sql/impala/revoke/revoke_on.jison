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
 : RevokeOnStatement
 ;

DataDefinition_EDIT
 : RevokeOnStatement_EDIT
 ;

RevokeOnStatement
 : 'REVOKE' PrivilegeType 'ON' ObjectSpecification 'FROM' RegularOrBacktickedIdentifier
 | 'REVOKE' PrivilegeType 'ON' ObjectSpecification 'FROM' GroupRoleOrUser RegularOrBacktickedIdentifier
 ;

RevokeOnStatement_EDIT
 : 'REVOKE' PrivilegeType_EDIT
 | 'REVOKE' PrivilegeType 'CURSOR'
   {
     if ($2.isCreate) {
       parser.suggestKeywords(['ON DATABASE', 'ON SERVER']);
     } else {
       parser.suggestKeywords(['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']);
     }
   }
 | 'REVOKE' PrivilegeType 'ON' 'CURSOR'
   {
     if ($2.isCreate) {
       parser.suggestKeywords(['DATABASE', 'SERVER']);
     } else {
       parser.suggestKeywords(['DATABASE', 'SERVER', 'TABLE', 'URI']);
     }
   }
 | 'REVOKE' PrivilegeType 'ON' ObjectSpecification_EDIT
 | 'REVOKE' PrivilegeType 'ON' ObjectSpecification 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'REVOKE' PrivilegeType 'ON' ObjectSpecification 'FROM' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 ;
