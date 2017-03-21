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

InsertStatement
 : HiveInsertStatement
 | InsertValuesStatement
 | ImpalaInsertStatement
 | CommonTableExpression HiveInsertStatement
 | CommonTableExpression ImpalaInsertStatement
 ;

DataManipulation_EDIT
 : HiveInsertStatement_EDIT
 | InsertValuesStatement_EDIT
 | ImpalaInsertStatement_EDIT
 | CommonTableExpression HiveInsertStatement_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression_EDIT HiveInsertStatement
 | CommonTableExpression ImpalaInsertStatement_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression_EDIT ImpalaInsertStatement
 ;

HiveInsertStatement
 : HiveInsertWithoutQuery QuerySpecification
 | FromClause HiveInserts
 | FromClause SelectWithoutTableExpression OptionalSelectConditions
 ;

HiveInsertStatement_EDIT
 : HiveInsertWithoutQuery_EDIT
 | HiveInsertWithoutQuery 'CURSOR'
   {
     var keywords = [];
     if ($1.suggestKeywords) {
       keywords = parser.createWeightedKeywords($1.suggestKeywords, 2).concat([{ value: 'SELECT', weight: 1}]);
     } else {
       keywords = ['SELECT'];
     }
     if ($1.addValues) {
       keywords.push({ weight: 1.1, value: 'VALUES' });
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 | HiveInsertWithoutQuery_EDIT QuerySpecification
 | HiveInsertWithoutQuery QuerySpecification_EDIT
 | FromClause HiveInserts_EDIT
   {
     if (!$2.keepTables) {
       delete parser.yy.result.suggestTables;
       delete parser.yy.result.suggestDatabases;
     }
   }
 | FromClause_EDIT
 | FromClause_EDIT HiveInserts
 | FromClause_EDIT SelectWithoutTableExpression OptionalSelectConditions
 | FromClause 'CURSOR'
   {
     parser.suggestKeywords(['INSERT INTO', 'INSERT OVERWRITE', 'SELECT']);
   }
 | FromClause SelectWithoutTableExpression_EDIT OptionalSelectConditions
   {
     if ($2.cursorAtEnd) {
       parser.checkForSelectListKeywords($2);
       var keywords = parser.yy.result.suggestKeywords || [];
       if ($3.suggestKeywords) {
         keywords = keywords.concat($3.suggestKeywords);
       }
       if (keywords.length > 0) {
         parser.suggestKeywords(keywords);
       }
     }
     delete parser.yy.result.suggestTables;
     delete parser.yy.result.suggestDatabases;
   }
 | FromClause SelectWithoutTableExpression OptionalSelectConditions_EDIT
   {
     if ($3.cursorAtStart) {
       parser.checkForSelectListKeywords($2.tableExpression);
     }
   }
 ;

HiveInsertWithoutQuery
 : '<hive>INSERT' '<hive>OVERWRITE' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalIfNotExists
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (!$5 && !$6) {
       $$ = { suggestKeywords: ['PARTITION'] }
     } else if (!$6) {
       $$ = { suggestKeywords: ['IF NOT EXISTS'] }
     }
   }
 | '<hive>INSERT' '<hive>OVERWRITE' '<hive>LOCAL' '<hive>DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs
   {
     if (!$6 && !$7) {
       $$ = { suggestKeywords: [{ value: 'ROW FORMAT', weight: 2 }, { value: 'STORED AS', weight: 1}] };
     } else if (!$7) {
       $$ = { suggestKeywords: ['STORED AS'] };
     }
   }
 | '<hive>INSERT' '<hive>OVERWRITE_DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs
    {
      if (!$4 && !$5) {
        $$ = { suggestKeywords: [{ value: 'ROW FORMAT', weight: 2 }, { value: 'STORED AS', weight: 1}] };
      } else if (!$5) {
        $$ = { suggestKeywords: ['STORED AS'] };
      }
    }
  | '<hive>INSERT' 'INTO' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (!$5 && !$6) {
       $$ = { suggestKeywords: ['PARTITION'], addValues: true };
     } else if (!$6) {
       $$ = { addValues: true };
     }
   }
 ;

HiveInsertWithoutQuery_EDIT
 : '<hive>INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['OVERWRITE', 'INTO']);
   }
 | '<hive>INSERT' '<hive>OVERWRITE' OptionalHiveTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['DIRECTORY', 'LOCAL DIRECTORY', 'TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     $$ = { keepTables: true }
   }
 | '<hive>INSERT' '<hive>OVERWRITE' OptionalHiveTable SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalParenthesizedColumnList
   {
     $$ = { keepTables: true }
   }
 | '<hive>INSERT' '<hive>OVERWRITE' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT OptionalIfNotExists
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | '<hive>INSERT' '<hive>OVERWRITE' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalIfNotExists_EDIT
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
   }
 | '<hive>INSERT' '<hive>OVERWRITE' '<hive>LOCAL' 'CURSOR'
   {
     parser.suggestKeywords(['DIRECTORY']);
   }
 | '<hive>INSERT' '<hive>OVERWRITE' '<hive>LOCAL' '<hive>DIRECTORY' HdfsPath_EDIT OptionalInsertRowFormat OptionalStoredAs
 | '<hive>INSERT' '<hive>OVERWRITE' '<hive>LOCAL' '<hive>DIRECTORY' HdfsPath OptionalInsertRowFormat_EDIT OptionalStoredAs
 | '<hive>INSERT' '<hive>OVERWRITE' '<hive>LOCAL' '<hive>DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs_EDIT
 | '<hive>INSERT' '<hive>OVERWRITE_DIRECTORY' HdfsPath_EDIT OptionalInsertRowFormat OptionalStoredAs  // DIRECTORY is a non-reserved keyword
 | '<hive>INSERT' '<hive>OVERWRITE_DIRECTORY' HdfsPath OptionalInsertRowFormat_EDIT OptionalStoredAs
 | '<hive>INSERT' '<hive>OVERWRITE_DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs_EDIT
 | '<hive>INSERT' 'INTO' OptionalHiveTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     $$ = { keepTables: true }
   }
 | '<hive>INSERT' 'INTO' OptionalHiveTable SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalParenthesizedColumnList
   {
     $$ = { keepTables: true }
   }
 | '<hive>INSERT' 'INTO' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT OptionalParenthesizedColumnList
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | '<hive>INSERT' 'INTO' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList_EDIT
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 ;

HiveInserts
 : HiveInsert
 | HiveInserts HiveInsert
 ;

HiveInserts_EDIT
 : HiveInsert_EDIT
 | HiveInserts HiveInsert_EDIT
 | HiveInsert_EDIT HiveInserts
 | HiveInserts HiveInsert_EDIT HiveInserts
 ;

// TODO: Verify Hive unions in insert
HiveInsert
 : HiveInsertWithoutQuery SelectWithoutTableExpression OptionalSelectConditions
 ;

HiveInsert_EDIT
 : HiveInsertWithoutQuery_EDIT
 | HiveInsertWithoutQuery_EDIT SelectWithoutTableExpression OptionalSelectConditions
 | HiveInsertWithoutQuery 'CURSOR'
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords(parser.createWeightedKeywords($1.suggestKeywords, 2).concat([{ value: 'SELECT', weight: 1}]));
     } else {
       parser.suggestKeywords(['SELECT']);
     }
   }
 | HiveInsertWithoutQuery SelectWithoutTableExpression_EDIT OptionalSelectConditions
   {
     if ($2.cursorAtEnd) {
       parser.checkForSelectListKeywords($2);
       var keywords = parser.yy.result.suggestKeywords || [];
       if ($3.suggestKeywords) {
         keywords = keywords.concat($3.suggestKeywords);
       }
       if (keywords.length > 0) {
         parser.suggestKeywords(keywords);
       }
     }
   }
 | HiveInsertWithoutQuery SelectWithoutTableExpression OptionalSelectConditions_EDIT
 ;

InsertValuesStatement
 : '<hive>INSERT' 'INTO' OptionalHiveTable SchemaQualifiedTableIdentifier OptionalPartitionSpec 'VALUES' InsertValuesList
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
   }
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier 'VALUES' InsertValuesList
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
   }
 ;

InsertValuesStatement_EDIT
 : 'INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO']);
   }
 | 'INSERT' 'INTO' OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier_EDIT
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier 'CURSOR'
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     parser.suggestKeywords(['VALUES']);
   }
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier_EDIT 'VALUES' InsertValuesList
 ;

InsertValuesList
 : ParenthesizedRowValuesList
 | RowValuesList ',' ParenthesizedRowValuesList
 ;

ParenthesizedRowValuesList
 : '(' InValueList ')'
 ;

OptionalTable
 :
 | 'TABLE'
 ;

AnyInsert
 : '<hive>INSERT'
 | 'INSERT'
 ;

OptionalInsertRowFormat
 :
 | 'ROW' '<hive>FORMAT' HiveDelimitedRowFormat
 ;

OptionalInsertRowFormat_EDIT
 : 'ROW' 'CURSOR'
   {
     parser.suggestKeywords(['FORMAT DELIMITED']);
   }
 | 'ROW' '<hive>FORMAT' 'CURSOR'
   {
     parser.suggestKeywords(['DELIMITED']);
   }
 | 'ROW' '<hive>FORMAT' HiveDelimitedRowFormat_EDIT
 ;

SelectWithoutTableExpression
 : 'SELECT' OptionalAllOrDistinct SelectList  -> { selectList: $3 }
 ;

SelectWithoutTableExpression_EDIT
 : 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR'
   {
     $$ = $3;
     $$.cursorAtEnd = true;
   }
 | 'SELECT' OptionalAllOrDistinct SelectList_EDIT
   {
     parser.selectListNoTableSuggest($3, $2);
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR'
   {
     var keywords = [];
     if ($2) {
       keywords = [{ value: '*', weight: 1000 }];
       if ($2 === 'ALL') {
         parser.suggestAggregateFunctions();
         parser.suggestAnalyticFunctions();
       }
     } else {
       keywords = [{ value: '*', weight: 1000 }, 'ALL', 'DISTINCT'];
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (parser.isImpala()) {
       keywords.push('STRAIGHT_JOIN');
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns();
   }
 ;

OptionalHiveTable
 :
 | '<hive>TABLE'
 ;

ImpalaInsertStatement
 : ImpalaInsertStatementWithoutCTE
 ;

ImpalaInsertStatement_EDIT
 : ImpalaInsertStatementWithoutCTE_EDIT
 ;

ImpalaInsertStatementWithoutCTE
 : ImpalaInsertLeftPart OptionalImpalaShuffleOrNoShuffle SelectStatement OptionalUnions
 | ImpalaInsertLeftPart 'VALUES' ImpalaRowValuesLists
 ;

ImpalaInsertStatementWithoutCTE_EDIT
 : ImpalaInsertLeftPart_EDIT
 | ImpalaInsertLeftPart OptionalImpalaShuffleOrNoShuffle 'CURSOR'
   {
     var keywords = $1.suggestKeywords && !$2 ? parser.createWeightedKeywords($1.suggestKeywords, 2) : [];
     if (!$2) {
       keywords = keywords.concat(['[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES'])
     } else {
       keywords = keywords.concat(['SELECT'])
     }
     parser.suggestKeywords(keywords);
   }
 | ImpalaInsertLeftPart_EDIT OptionalImpalaShuffleOrNoShuffle SelectStatement OptionalUnions
 | ImpalaInsertLeftPart OptionalImpalaShuffleOrNoShuffle SelectStatement_EDIT OptionalUnions
 | ImpalaInsertLeftPart OptionalImpalaShuffleOrNoShuffle SelectStatement OptionalUnions_EDIT
 | ImpalaInsertLeftPart_EDIT 'VALUES' ImpalaRowValuesLists
 | ImpalaInsertLeftPart 'VALUES' ImpalaRowValuesLists_EDIT
 ;

ImpalaInsertLeftPart
 : '<impala>INSERT' IntoOrOverwrite OptionalImpalaTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (!$6) {
       $$ = { suggestKeywords: ['PARTITION'] };
     }
   }
 ;

ImpalaInsertLeftPart_EDIT
 : '<impala>INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['INTO', 'OVERWRITE']);
   }
 | '<impala>INSERT' IntoOrOverwrite OptionalImpalaTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<impala>INSERT' IntoOrOverwrite OptionalImpalaTable 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
   }
 | '<impala>INSERT' IntoOrOverwrite OptionalImpalaTable SchemaQualifiedTableIdentifier_EDIT OptionalParenthesizedColumnList OptionalPartitionSpec
 | '<impala>INSERT' IntoOrOverwrite OptionalImpalaTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList_EDIT OptionalPartitionSpec
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | '<impala>INSERT' IntoOrOverwrite OptionalImpalaTable SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalPartitionSpec_EDIT
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
 | '<impala>OVERWRITE'
 ;

OptionalImpalaTable
 :
 | '<impala>TABLE'
 ;

OptionalImpalaShuffleOrNoShuffle
 :
 | '<impala>SHUFFLE'
 | '<impala>NOSHUFFLE'
 ;

ImpalaRowValuesLists
 : ParenthesizedImpalaRowValuesList
 | ImpalaRowValuesLists ',' ParenthesizedImpalaRowValuesList
 ;

ImpalaRowValuesLists_EDIT
 : ParenthesizedImpalaRowValuesList_EDIT
 | ImpalaRowValuesLists ',' ParenthesizedImpalaRowValuesList_EDIT
 | ImpalaRowValuesLists ',' ParenthesizedImpalaRowValuesList_EDIT ',' ImpalaRowValuesLists
 | ParenthesizedImpalaRowValuesList_EDIT ',' ImpalaRowValuesLists
 ;

ParenthesizedImpalaRowValuesList
 : '(' ValueExpressionList ')'
 ;

ParenthesizedImpalaRowValuesList_EDIT
 : '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestFunctions();
   }
 | '(' ValueExpressionList_EDIT RightParenthesisOrError
 ;