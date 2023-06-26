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
 : 'REVOKE' OptionalGrantOptionFor PrivilegeType 'ON' ObjectSpecification 'FROM' RegularOrBacktickedIdentifier
 | 'REVOKE' OptionalGrantOptionFor PrivilegeType 'ON' ObjectSpecification 'FROM' GroupRoleOrUser RegularOrBacktickedIdentifier
 ;

RevokeOnStatement_EDIT
 : 'REVOKE' OptionalGrantOptionFor PrivilegeType_EDIT
 | 'REVOKE' GrantOptionFor 'CURSOR'
   {
     var keywords = parser.REVOKE_KEYWORDS.concat();
     var idx = keywords.indexOf('GRANT OPTION FOR');
     if (idx !== -1) {
       keywords.splice(idx, 1);
     }
     parser.suggestKeywords(keywords);
   }
 | 'REVOKE' GrantOptionFor_EDIT
 | 'REVOKE' OptionalGrantOptionFor PrivilegeType 'CURSOR'
   {
     if ($3.isCreate) {
       parser.suggestKeywords(['ON DATABASE', 'ON SERVER']);
     } else {
       parser.suggestKeywords(['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']);
     }
   }
 | 'REVOKE' OptionalGrantOptionFor PrivilegeType 'ON' 'CURSOR'
   {
     if ($3.isCreate) {
       parser.suggestKeywords(['DATABASE', 'SERVER']);
     } else {
       parser.suggestKeywords(['DATABASE', 'SERVER', 'TABLE', 'URI']);
     }
   }
 | 'REVOKE' OptionalGrantOptionFor PrivilegeType 'ON' ObjectSpecification_EDIT
 | 'REVOKE' OptionalGrantOptionFor PrivilegeType 'ON' ObjectSpecification 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'REVOKE' OptionalGrantOptionFor PrivilegeType 'ON' ObjectSpecification 'FROM' 'CURSOR'
   {
     if ($2) {
       parser.suggestKeywords(['ROLE']);
     } else {
       parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
     }
   }
 ;

OptionalGrantOptionFor
 :
 | GrantOptionFor
 ;

GrantOptionFor
 : 'GRANT' 'OPTION' 'FOR'
 ;

GrantOptionFor_EDIT
 : 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['OPTION FOR']);
   }
 | 'GRANT' 'OPTION' 'CURSOR'
   {
     parser.suggestKeywords(['FOR']);
   }
 ;