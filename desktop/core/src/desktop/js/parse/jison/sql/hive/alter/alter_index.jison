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
 : AlterIndex
 ;

DataDefinition_EDIT
 : AlterIndex_EDIT
 ;

AlterIndex
 : 'ALTER' 'INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'REBUILD'
   {
     parser.addTablePrimary($5);
   }
 ;

AlterIndex_EDIT
 : 'ALTER' 'INDEX' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'ALTER' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ALTER' 'INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier_EDIT
 | 'ALTER' 'INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($5);
   }
 | 'ALTER' 'INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($5);
     if (!$6) {
       parser.suggestKeywords(['PARTITION', 'REBUILD']);
     } else {
       parser.suggestKeywords(['REBUILD']);
     }
   }
 ;
