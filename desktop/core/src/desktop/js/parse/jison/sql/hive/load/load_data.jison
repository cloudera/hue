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
 : LoadDataStatement
 ;

DataManipulation_EDIT
 : LoadDataStatement_EDIT
 ;

LoadDataStatement
 : 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalInputFormat
   {
     parser.addTablePrimary($9);
   }
 ;

LoadDataStatement_EDIT
 : 'LOAD' 'CURSOR'
   {
     parser.suggestKeywords(['DATA LOCAL INPATH', 'DATA INPATH']);
   }
 | 'LOAD' 'DATA' OptionalLocal 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['INPATH', 'LOCAL INPATH']);
     } else {
       parser.suggestKeywords(['INPATH']);
     }
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath_EDIT OptionalOverwrite
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['OVERWRITE INTO TABLE', 'INTO TABLE']);
     } else {
       parser.suggestKeywords(['INTO TABLE']);
     }
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'CURSOR'
   {
     parser.suggestKeywords([ 'TABLE' ]);
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalInputFormat
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalInputFormat 'CURSOR'
   {
     parser.addTablePrimary($9);
     if (!$10 && !$11) {
       parser.suggestKeywords(['INPUTFORMAT', 'PARTITION']);
     } else if ($10 && !$11) {
       parser.suggestKeywords(['INPUTFORMAT']);
     }
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT OptionalInputFormat
   {
     parser.addTablePrimary($9);
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec InputFormat_EDIT
   {
     parser.addTablePrimary($9);
   }
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath_EDIT OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalInputFormat
   {
     parser.addTablePrimary($9);
   }
 ;

OptionalOverwrite
 :
 | 'OVERWRITE'
 ;

OptionalLocal
 :
 | 'LOCAL'
 ;

OptionalInputFormat
 :
 | InputFormat
 ;

InputFormat
 : 'INPUTFORMAT' QuotedValue 'SERDE' QuotedValue
 ;

InputFormat_EDIT
 : 'INPUTFORMAT' QuotedValue 'CURSOR'
   {
     parser.suggestKeywords(['SERDE']);
   }
 ;
