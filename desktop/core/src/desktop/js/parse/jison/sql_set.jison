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
 : SetRoleStatement
 | SetSpecification
 ;

DataDefinition_EDIT
 : SetRoleStatement_EDIT
 | 'SET' 'CURSOR'
   {
     parser.suggestSetOptions();
     if (parser.isHive()) {
       parser.suggestKeywords(['ROLE']);
     }
     if (parser.isImpala()) {
       parser.suggestKeywords(['ALL']);
     }
   }
 ;

SetSpecification
 : 'SET' SetOption '=' SetValue
 | 'SET' 'ALL'
 ;

SetOption
 : RegularIdentifier
 | SetOption AnyDot RegularIdentifier
 ;

SetValue
 : RegularIdentifier
 | SignedInteger
 | SignedInteger RegularIdentifier
 | QuotedValue
 | 'TRUE'
 | 'FALSE'
 | 'NULL'
 ;

SetRoleStatement
 : 'SET' '<hive>ROLE' RegularIdentifier
 | 'SET' '<hive>ROLE' '<hive>ALL'
 | 'SET' '<hive>ROLE' '<hive>NONE'
 ;

SetRoleStatement_EDIT
 : 'SET' '<hive>ROLE' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'NONE']);
   }
 ;