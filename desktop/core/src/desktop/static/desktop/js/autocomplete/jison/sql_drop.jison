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
 : DropStatement
 ;

DataDefinition_EDIT
 : DropStatement_EDIT
 ;

DropStatement
 : DropDatabaseStatement
 | DropTableStatement
 ;

DropStatement_EDIT
 : 'DROP' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
 | DropDatabaseStatement_EDIT
 | DropTableStatement_EDIT
 ;

DropDatabaseStatement
 : 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 ;

DropDatabaseStatement_EDIT
 : 'DROP' DatabaseOrSchema OptionalIfExists
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR' RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 ;

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists TablePrimary
 ;

DropTableStatement_EDIT
 : 'DROP' AnyTable OptionalIfExists_EDIT
 | 'DROP' AnyTable OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'DROP' AnyTable OptionalIfExists TablePrimary_EDIT
   {
     if ($4.identifierChain && $4.identifierChain.length === 1) {
       suggestTablesOrColumns($4.identifierChain[0].name);
     } else if ($4.identifierChain && $4.identifierChain.length === 0) {
       suggestTables();
       suggestDatabases({ appendDot: true });
     }
   }
 | 'DROP' AnyTable OptionalIfExists_EDIT TablePrimary
 | 'DROP' AnyTable OptionalIfExists TablePrimary 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   }
 ;