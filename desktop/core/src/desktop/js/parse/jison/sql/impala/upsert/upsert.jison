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
 : UpsertStatement
 ;

DataManipulation_EDIT
 : UpsertStatement_EDIT
 ;

UpsertStatement
 : UpsertStatementLeftPart OptionalShuffleOrNoShuffle SelectStatement OptionalUnions
 | UpsertStatementLeftPart 'VALUES' RowValuesLists
 ;

UpsertStatement_EDIT
 : UpsertStatementLeftPart_EDIT
 | UpsertStatementLeftPart OptionalShuffleOrNoShuffle 'CURSOR'
   {
     var keywords = $1.suggestKeywords && !$2 ? parser.createWeightedKeywords($1.suggestKeywords, 2) : [];
     if (!$2) {
       keywords = keywords.concat(['[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES'])
     } else {
       keywords = keywords.concat(['SELECT'])
     }
     parser.suggestKeywords(keywords);
   }
 | UpsertStatementLeftPart_EDIT OptionalShuffleOrNoShuffle SelectStatement OptionalUnions
 | UpsertStatementLeftPart OptionalShuffleOrNoShuffle SelectStatement_EDIT OptionalUnions
 | UpsertStatementLeftPart OptionalShuffleOrNoShuffle SelectStatement OptionalUnions_EDIT
 | UpsertStatementLeftPart_EDIT 'VALUES' RowValuesLists
 | UpsertStatementLeftPart 'VALUES' RowValuesLists_EDIT
 ;

UpsertStatementLeftPart
 : 'UPSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList
   {
     $4.owner = 'upsert';
     parser.addTablePrimary($4);
   }
 ;

UpsertStatementLeftPart_EDIT
 : 'UPSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO']);
   }
 | 'UPSERT' 'INTO' OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'UPSERT' 'INTO' OptionalTable 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     $5.owner = 'upsert';
     parser.addTablePrimary($5);
   }
 | 'UPSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList
 | 'UPSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList_EDIT
   {
     $4.owner = 'upsert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'upsert';
     }
   }
 ;
