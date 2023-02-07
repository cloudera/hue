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

Auxiliary
 : ShowCreateTable
 ;

Auxiliary_EDIT
 : ShowCreateTable_EDIT
 ;

ShowCreateTable
 : 'SHOW' 'CREATE' 'TABLE' SchemaQualifiedTableIdentifier OptionalAsSerde
   {
     parser.addTablePrimary($4);
   }
 ;

ShowCreateTable_EDIT
 : 'SHOW' 'CREATE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'SHOW' 'CREATE' 'TABLE' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'SHOW' 'CREATE' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 | 'SHOW' 'CREATE' 'TABLE' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.suggestKeywords(["AS SERDE"]);
   }
 | 'SHOW' 'CREATE' 'TABLE' SchemaQualifiedTableIdentifier AsSerde_EDIT
 ;

OptionalAsSerde
 :
 | AsSerde
 ;

AsSerde
 : 'AS' 'SERDE'
 ;

AsSerde_EDIT
 : 'AS' 'CURSOR'
   {
     parser.suggestKeywords(["SERDE"]);
   }
 ;