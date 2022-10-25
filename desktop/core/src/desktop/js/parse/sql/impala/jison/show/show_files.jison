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
 : ShowFilesStatement
 ;

DataDefinition_EDIT
 : ShowFilesStatement_EDIT
 ;

ShowFilesStatement
 : 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

ShowFilesStatement_EDIT
 : 'SHOW' 'FILES' 'CURSOR'
   {
     parser.suggestKeywords(['IN']);
   }
 | 'SHOW' 'FILES' 'IN' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName_EDIT OptionalPartitionSpec
 | 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($4);
     if (!$5) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec_EDIT
 | 'SHOW' 'FILES' 'CURSOR' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['IN']);
   }
 ;
