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
 : DropIndexStatement
 ;

DataDefinition_EDIT
 : DropIndexStatement_EDIT
 ;

DropIndexStatement
 : 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($6);
   }
 ;

DropIndexStatement_EDIT
 : 'DROP' 'INDEX' OptionalIfExists 'CURSOR'
   {
     parser.suggestKeywords(['IF EXISTS']);
   }
 | 'DROP' 'INDEX' OptionalIfExists_EDIT
 | 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier_EDIT
 ;
