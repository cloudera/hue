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
 : InsertStatement
 ;

DataManipulation_EDIT
 : InsertStatement_EDIT
 ;

InsertStatement
 : InsertLeftPart OptionalShuffleOrNoShuffle SelectStatement OptionalUnions
 | InsertLeftPart 'VALUES' RowValuesLists
 ;

InsertStatement_EDIT
 : InsertLeftPart_EDIT
 | InsertLeftPart OptionalShuffleOrNoShuffle 'CURSOR'
   {
     var keywords = $1.suggestKeywords && !$2 ? parser.createWeightedKeywords($1.suggestKeywords, 2) : [];
     if (!$2) {
       keywords = keywords.concat(['[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES'])
     } else {
       keywords = keywords.concat(['SELECT'])
     }
     parser.suggestKeywords(keywords);
   }
 | InsertLeftPart_EDIT OptionalShuffleOrNoShuffle SelectStatement OptionalUnions
 | InsertLeftPart OptionalShuffleOrNoShuffle SelectStatement_EDIT OptionalUnions
 | InsertLeftPart OptionalShuffleOrNoShuffle SelectStatement OptionalUnions_EDIT
 | InsertLeftPart_EDIT 'VALUES' RowValuesLists
 | InsertLeftPart 'VALUES' RowValuesLists_EDIT
 ;

InsertLeftPart
 : 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (!$6) {
       $$ = { suggestKeywords: ['PARTITION'] };
     }
   }
 ;

InsertLeftPart_EDIT
 : 'INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO', 'OVERWRITE']);
   }
 | 'INSERT' IntoOrOverwrite OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'INSERT' IntoOrOverwrite OptionalTable 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     $5.owner = 'insert';
     parser.addTablePrimary($5);
   }
 | 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList OptionalPartitionSpec
 | 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList_EDIT OptionalPartitionSpec
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | 'INSERT' IntoOrOverwrite OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec_EDIT
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 ;

IntoOrOverwrite
 : 'INTO'
 | 'OVERWRITE'
 ;
