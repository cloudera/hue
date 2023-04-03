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
 : GrantPrivilegeStatement
 ;

DataDefinition_EDIT
 : GrantPrivilegeStatement_EDIT
 ;

GrantPrivilegeStatement
 : 'GRANT' PrivilegeTypeList OptionalOnSpecification 'TO' PrincipalSpecificationList OptionalWithGrantOption
 ;

GrantPrivilegeStatement_EDIT
 : 'GRANT' PrivilegeTypeList_EDIT OptionalOnSpecification
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
