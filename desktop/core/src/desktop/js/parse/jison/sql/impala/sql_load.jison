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

DataManipulation
 : LoadStatement
 ;

DataManipulation_EDIT
 : LoadStatement_EDIT
 ;

LoadStatement
 : 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($8);
   }
 ;

LoadStatement_EDIT
 : 'LOAD' 'CURSOR'
   {
     parser.suggestKeywords(['DATA INPATH']);
   }
 | 'LOAD' 'DATA' 'CURSOR'
   {
     parser.suggestKeywords(['INPATH']);
   }
 | 'LOAD' 'DATA' 'INPATH' HdfsPath_EDIT OptionalOverwrite
 | 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'CURSOR'
   {
     if (!$5) {
       parser.suggestKeywords(['OVERWRITE INTO TABLE', 'INTO TABLE']);
     } else {
       parser.suggestKeywords(['INTO TABLE']);
     }
   }
 | 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'CURSOR'
   {
     parser.suggestKeywords([ 'TABLE' ]);
   }
 | 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($8);
     if (!$9) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'LOAD' 'DATA' 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     parser.addTablePrimary($8);
   }
 | 'LOAD' 'DATA' 'INPATH' HdfsPath_EDIT OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($8);
   }
 ;

OptionalOverwrite
 :
 | 'OVERWRITE'
 ;
