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
 : AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'INTO' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     addTablePrimary($9);
   }
 ;

LoadStatement_EDIT
 : AnyLoad 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['DATA LOCAL INPATH', 'DATA INPATH']);
     } else if (isImpala()) {
       suggestKeywords(['DATA INPATH']);
     }
   }
 | AnyLoad AnyData OptionalHiveLocal 'CURSOR'
   {
     if (isHive() && !$3) {
       suggestKeywords(['INPATH', 'LOCAL INPATH']);
     } else {
       suggestKeywords(['INPATH']);
     }
   }
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath_EDIT OptionalOverwrite
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'CURSOR'
   {
     if (!$6) {
       suggestKeywords(['OVERWRITE INTO TABLE', 'INTO TABLE']);
     } else {
       suggestKeywords(['INTO TABLE']);
     }
   }
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'INTO' 'CURSOR'
   {
     suggestKeywords([ 'TABLE' ]);
   }
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'INTO' AnyTable 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'INTO' AnyTable SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'INTO' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     addTablePrimary($9);
     if (!$10) {
       suggestKeywords(['PARTITION']);
     }
   }
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath OptionalOverwrite 'INTO' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     addTablePrimary($9);
   }
 | AnyLoad AnyData OptionalHiveLocal AnyInpath HdfsPath_EDIT OptionalOverwrite 'INTO' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     addTablePrimary($9);
   }
 ;

OptionalOverwrite
 :
 | '<hive>OVERWRITE'
 | '<impala>OVERWRITE'
 ;

OptionalHiveLocal
 :
 | '<hive>LOCAL'
 ;

AnyLoad
 : '<hive>LOAD'
 | '<impala>LOAD'
 ;

AnyData
 : '<hive>DATA'
 | '<impala>DATA'
 ;

AnyInpath
 : '<hive>INPATH'
 | '<impala>INPATH'
 ;
