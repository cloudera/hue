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
 : ShowCreateTableStatement
 ;

DataDefinition_EDIT
 : ShowCreateTableStatement_EDIT
 ;

ShowCreateTableStatement
 : 'SHOW' 'CREATE' TableOrView RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($4);
   }
 ;

ShowCreateTableStatement_EDIT
 : 'SHOW' 'CREATE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE', 'VIEW']);
   }
 | 'SHOW' 'CREATE' TableOrView 'CURSOR'
   {
     if ($3.isView) {
       parser.suggestTables({ onlyViews: true });
     } else {
       parser.suggestTables();
     }
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'CREATE' TableOrView RegularOrBackTickedSchemaQualifiedName_EDIT
   {
     if (parser.yy.result.suggestTables && $3.isView) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'SHOW' 'CREATE' 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['TABLE', 'VIEW']);
   }
 ;

TableOrView
 : 'TABLE'
 | 'VIEW'   -> { isView: true }
 ;
