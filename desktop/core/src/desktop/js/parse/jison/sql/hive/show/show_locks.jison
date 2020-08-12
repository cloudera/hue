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
 : ShowLocksStatement
 ;

DataDefinition_EDIT
 : ShowLocksStatement_EDIT
 ;

ShowLocksStatement
 : 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName 'EXTENDED'
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec 'EXTENDED'
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' DatabaseOrSchema RegularOrBacktickedIdentifier
 ;

ShowLocksStatement_EDIT
 : 'SHOW' 'LOCKS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
     parser.suggestKeywords(['DATABASE', 'SCHEMA']);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
    {
      parser.addTablePrimary($3);
      parser.suggestKeywords(['EXTENDED', 'PARTITION']);
    }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT 'EXTENDED'
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec 'EXTENDED'
 | 'SHOW' 'LOCKS' DatabaseOrSchema 'CURSOR'
   {
     parser.suggestDatabases();
   }
 ;
