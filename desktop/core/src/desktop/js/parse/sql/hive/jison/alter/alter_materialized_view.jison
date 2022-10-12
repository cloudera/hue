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
 : AlterMaterializedView
 ;

DataDefinition_EDIT
 : AlterMaterializedView_EDIT
 ;

AlterMaterializedView
 : 'ALTER' 'MATERIALIZED' 'VIEW' SchemaQualifiedTableIdentifier EnableOrDisable 'REWRITE'
   {
     parser.addTablePrimary($4);
   }
 ;

AlterMaterializedView_EDIT
 : 'ALTER' 'MATERIALIZED' 'CURSOR'
   {
     parser.suggestKeywords(['VIEW']);
   }
 | 'ALTER' 'MATERIALIZED' 'VIEW' 'CURSOR'
   {
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ALTER' 'MATERIALIZED' 'VIEW' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'ALTER' 'MATERIALIZED' 'VIEW' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['DISABLE REWRITE', 'ENABLE REWRITE']);
   }
 | 'ALTER' 'MATERIALIZED' 'VIEW' SchemaQualifiedTableIdentifier EnableOrDisable 'CURSOR'
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['REWRITE']);
   }
 ;
