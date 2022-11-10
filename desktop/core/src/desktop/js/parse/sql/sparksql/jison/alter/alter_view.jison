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
 : AlterView
 ;

DataDefinition_EDIT
 : AlterView_EDIT
 ;

AlterView
 : 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier AlterViewOperations
   {
     parser.addTablePrimary($3);
   }
 ;

AlterView_EDIT
 : 'ALTER' 'VIEW' 'CURSOR' OptionalAlterViewOperations
   {
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier_EDIT OptionalAlterViewOperations
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier 'CURSOR' OptionalAlterViewOperations
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords(['AS SELECT', 'RENAME TO', 'SET TBLPROPERTIES', 'UNSET TBLPROPERTIES']);
     }
   }
 | 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier AlterViewOperations_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

OptionalAlterViewOperations
 :
 | AlterViewOperations
 ;

AlterViewOperations
 : AlterSetTblPropertiesOperations
 | AsQuerySpecification
 | 'RENAME' 'TO' RegularOrBacktickedIdentifier
 ;

AlterViewOperations_EDIT
 : AlterSetTblPropertiesOperations_EDIT
 | 'SET' 'CURSOR'
   {
     parser.suggestKeywords(['TBLPROPERTIES']);
   }
 | AsQuerySpecification_EDIT
 | 'RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 ;

OptionalAsQuerySpecification
 :
 | AsQuerySpecification
 ;

AsQuerySpecification
 : 'AS' QuerySpecification
 ;

AsQuerySpecification_EDIT
 : 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'AS' QuerySpecification_EDIT
 ;