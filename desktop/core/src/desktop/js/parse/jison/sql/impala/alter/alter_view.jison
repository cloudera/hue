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

AlterStatement
 : AlterView
 ;

AlterStatement_EDIT
 : AlterView_EDIT
 ;

AlterView
 : AlterViewLeftSide 'SET' 'OWNER' RoleOrUser RegularOrBacktickedIdentifier
 | AlterViewLeftSide 'AS' QuerySpecification
 | AlterViewLeftSide 'RENAME' 'TO' RegularOrBacktickedIdentifier
 | AlterViewLeftSide 'RENAME' 'TO' RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier
 ;

AlterView_EDIT
 : AlterViewLeftSide_EDIT
 | AlterViewLeftSide 'CURSOR'
   {
     parser.suggestKeywords(['AS', 'RENAME TO', 'SET OWNER']);
   }
 | AlterViewLeftSide 'SET' 'CURSOR'
   {
     parser.suggestKeywords(['OWNER ROLE', 'OWNER USER']);
   }
 | AlterViewLeftSide 'SET' 'OWNER' 'CURSOR'
   {
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 | AlterViewLeftSide 'SET' 'OWNER' RoleOrUser 'CURSOR'
 | AlterViewLeftSide 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | AlterViewLeftSide 'AS' QuerySpecification_EDIT
 | AlterViewLeftSide 'RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | AlterViewLeftSide 'RENAME' 'TO' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
   }
 ;

AlterViewLeftSide
 : 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

AlterViewLeftSide_EDIT
 : 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'ALTER' 'VIEW' 'CURSOR'
   {
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 ;
