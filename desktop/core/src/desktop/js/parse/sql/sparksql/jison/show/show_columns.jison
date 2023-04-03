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
 : ShowColumns
 ;

Auxiliary_EDIT
 : ShowColumns_EDIT
 ;

ShowColumns
 : 'SHOW' 'COLUMNS' FromOrIn SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier FromOrIn RegularOrBacktickedIdentifier
 ;

ShowColumns_EDIT
 : 'SHOW' 'COLUMNS' 'CURSOR'
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' 'COLUMNS' FromOrIn 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'SHOW' 'COLUMNS' FromOrIn SchemaQualifiedTableIdentifier_EDIT
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier FromOrIn 'CURSOR'
   {
     parser.suggestDatabases();
   }
 ;