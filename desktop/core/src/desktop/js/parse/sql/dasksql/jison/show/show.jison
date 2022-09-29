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
 : ShowStatement
 ;

DataDefinition_EDIT
 : ShowStatement_EDIT
 ;

ShowStatement
 : ShowColumnsStatement
 | ShowSchemasStatement
 | ShowTablesStatement
 ;

ShowColumnsStatement
 : 'SHOW' 'COLUMNS' 'FROM' SchemaQualifiedTableIdentifier
 ;

ShowSchemasStatement
 : 'SHOW' 'SCHEMAS'
 | 'SHOW' 'SCHEMAS' 'LIKE' SingleQuotedValue
 ;

ShowTablesStatement
 : 'SHOW' 'TABLES' 'FROM' DatabaseIdentifier
 ;

ShowStatement_EDIT
 : 'SHOW' 'CURSOR'
   {
     parser.suggestKeywords(['SCHEMAS', 'TABLES', 'COLUMNS']);
   }
 | ShowColumnsStatement_EDIT
 | ShowSchemasStatement_EDIT
 | ShowTablesStatement_EDIT
 ;

ShowSchemasStatement_EDIT
 : 'SHOW' 'SCHEMAS' 'CURSOR'
   {
     parser.suggestKeywords(['LIKE']);
   }
 ;

ShowColumnsStatement_EDIT
 : 'SHOW' 'COLUMNS' 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'SHOW' 'COLUMNS' 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'SHOW' 'COLUMNS' 'FROM' SchemaQualifiedTableIdentifier_EDIT
 ;

ShowTablesStatement_EDIT
 : 'SHOW' 'TABLES' 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'SHOW' 'TABLES' 'FROM' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: false });
   }
 ;