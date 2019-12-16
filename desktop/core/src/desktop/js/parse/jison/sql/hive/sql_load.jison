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
 | ImportStatement
 | ExportStatement
 ;

DataManipulation_EDIT
 : LoadStatement_EDIT
 | ImportStatement_EDIT
 | ExportStatement_EDIT
 ;

LoadStatement
 : 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalInputFormat
   {
     parser.addTablePrimary($9);
   }
 ;

LoadStatement_EDIT
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
 | 'LOAD' 'DATA' OptionalLocal 'INPATH' HdfsPath OptionalOverwrite 'INTO' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT OptionalInputFormat
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

ImportStatement
 : 'IMPORT' OptionalTableWithPartition PushHdfsLexerState 'FROM' HdfsPath OptionalHdfsLocation
 ;

ImportStatement_EDIT
 : 'IMPORT' 'CURSOR' OptionalTableWithPartition
   {
     if (!$3) {
       parser.suggestKeywords(['EXTERNAL TABLE', 'FROM', 'TABLE']);
     } else if (!$3.hasExternal) {
       parser.suggestKeywords(['EXTERNAL']);
     }
   }
 | 'IMPORT' TableWithPartition 'CURSOR'
   {
     if ($2.suggestKeywords) {
        parser.suggestKeywords(parser.createWeightedKeywords($2.suggestKeywords, 2).concat(['FROM']));
      } else {
        parser.suggestKeywords(['FROM']);
      }
   }
 | 'IMPORT' TableWithPartition_EDIT
 | 'IMPORT' OptionalTableWithPartition PushHdfsLexerState 'FROM' HdfsPath_EDIT OptionalHdfsLocation
 | 'IMPORT' OptionalTableWithPartition PushHdfsLexerState 'FROM' HdfsPath HdfsLocation_EDIT
 | 'IMPORT' OptionalTableWithPartition PushHdfsLexerState 'FROM' HdfsPath OptionalHdfsLocation 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['LOCATION']);
     }
   }
 | 'IMPORT' 'CURSOR' OptionalTableWithPartition PushHdfsLexerState 'FROM' HdfsPath OptionalHdfsLocation
   {
     if (!$3) {
       parser.suggestKeywords(['EXTERNAL TABLE', 'TABLE']);
     } else if (!$3.hasExternal) {
       parser.suggestKeywords(['EXTERNAL']);
     }
   }
| 'IMPORT' TableWithPartition_EDIT PushHdfsLexerState 'FROM' HdfsPath OptionalHdfsLocation
 | 'IMPORT' TableWithPartition 'CURSOR' PushHdfsLexerState 'FROM' HdfsPath OptionalHdfsLocation
    {
      if ($2.suggestKeywords) {
        parser.suggestKeywords(parser.createWeightedKeywords($2.suggestKeywords, 2).concat(['FROM']));
      }
    }
 ;

OptionalTableWithPartition
 :
 | TableWithPartition
 ;

TableWithPartition
 : 'EXTERNAL' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
     if (!$4) {
       $$ = { hasExternal: true, suggestKeywords: ['PARTITION'] };
     } else {
       $$ = { hasExternal: true }
     }
   }
 | 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($2);
     if (!$3) {
       $$ = { suggestKeywords: ['PARTITION'] };
     }
   }
 ;

TableWithPartition_EDIT
 : 'EXTERNAL' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'EXTERNAL' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'EXTERNAL' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'EXTERNAL' 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }

 | 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

ExportStatement
 : 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath
   {
     parser.addTablePrimary($3);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath 'FOR' 'REPLICATION' '(' QuotedValue ')'
   {
     parser.addTablePrimary($3);
   }
 ;

ExportStatement_EDIT
 : 'EXPORT' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'EXPORT' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($3);
     if (!$4) {
       parser.suggestKeywords([{ weight: 2, value: 'PARTITION' }, { weight: 1, value: 'TO' }]);
     } else {
       parser.suggestKeywords([ 'TO' ]);
     }
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['FOR replication()']);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath 'FOR' 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['replication()']);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath 'FOR' 'REPLICATION' '(' QuotedValue ')'
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR' PushHdfsLexerState 'TO' HdfsPath
   {
     parser.addTablePrimary($3);
     if (!$4) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR' PushHdfsLexerState 'TO' HdfsPath 'FOR' 'REPLICATION' '(' QuotedValue ')'
   {
     parser.addTablePrimary($3);
     if (!$4) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT PushHdfsLexerState 'TO' HdfsPath
   {
     parser.addTablePrimary($3);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT PushHdfsLexerState 'TO' HdfsPath 'FOR' 'REPLICATION' '(' QuotedValue ')'
   {
     parser.addTablePrimary($3);
   }
 | 'EXPORT' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec PushHdfsLexerState 'TO' HdfsPath_EDIT 'FOR' 'REPLICATION' '(' QuotedValue ')'
   {
     parser.addTablePrimary($3);
   }
 ;
