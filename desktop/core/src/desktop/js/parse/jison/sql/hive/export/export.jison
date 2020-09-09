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
 : ExportStatement
 ;

DataManipulation_EDIT
 : ExportStatement_EDIT
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
