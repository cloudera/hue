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
 : InsertWithoutQuery
 | InsertWithoutQuery QuerySpecification
 | FromClause Inserts
 | FromClause SelectWithoutTableExpression OptionalSelectConditions
 ;

InsertStatement_EDIT
 : InsertWithoutQuery_EDIT
 | InsertWithoutQuery 'CURSOR'
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
 | InsertWithoutQuery_EDIT QuerySpecification
 | InsertWithoutQuery QuerySpecification_EDIT
 | FromClause Inserts_EDIT
   {
     if (!$2.keepTables) {
       delete parser.yy.result.suggestTables;
       delete parser.yy.result.suggestDatabases;
     }
   }
 | FromClause_EDIT
 | FromClause_EDIT Inserts
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

InsertWithoutQuery
 : 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalPartitionSpec ValuesClause
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
   }
 | 'INSERT' 'OVERWRITE' OptionalTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalIfNotExists
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (!$5 && !$6) {
       $$ = { suggestKeywords: ['PARTITION'] }
     } else if (!$6) {
       $$ = { suggestKeywords: ['IF NOT EXISTS'] }
     }
   }
 | 'INSERT' 'OVERWRITE' 'LOCAL' 'DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs
   {
     if (!$6 && !$7) {
       $$ = { suggestKeywords: [{ value: 'ROW FORMAT', weight: 2 }, { value: 'STORED AS', weight: 1}] };
     } else if (!$7) {
       $$ = { suggestKeywords: ['STORED AS'] };
     }
   }
 | 'INSERT' 'OVERWRITE_DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs
    {
      if (!$4 && !$5) {
        $$ = { suggestKeywords: [{ value: 'ROW FORMAT', weight: 2 }, { value: 'STORED AS', weight: 1}] };
      } else if (!$5) {
        $$ = { suggestKeywords: ['STORED AS'] };
      }
    }
  | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList
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

InsertWithoutQuery_EDIT
 : 'INSERT' 'CURSOR'
   {
     parser.suggestKeywords(['OVERWRITE', 'INTO']);
   }
 | 'INSERT' 'OVERWRITE' OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['DIRECTORY', 'LOCAL DIRECTORY', 'TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     $$ = { keepTables: true }
   }
 | 'INSERT' 'OVERWRITE' OptionalTable SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalParenthesizedColumnList
   {
     $$ = { keepTables: true }
   }
 | 'INSERT' 'OVERWRITE' OptionalTable SchemaQualifiedTableIdentifier PartitionSpec_EDIT OptionalIfNotExists
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | 'INSERT' 'OVERWRITE' OptionalTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalIfNotExists_EDIT
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
   }
 | 'INSERT' 'OVERWRITE' 'LOCAL' 'CURSOR'
   {
     parser.suggestKeywords(['DIRECTORY']);
   }
 | 'INSERT' 'OVERWRITE' 'LOCAL' 'DIRECTORY' HdfsPath_EDIT OptionalInsertRowFormat OptionalStoredAs
 | 'INSERT' 'OVERWRITE' 'LOCAL' 'DIRECTORY' HdfsPath InsertRowFormat_EDIT OptionalStoredAs
 | 'INSERT' 'OVERWRITE' 'LOCAL' 'DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs_EDIT
 | 'INSERT' 'OVERWRITE_DIRECTORY' HdfsPath_EDIT OptionalInsertRowFormat OptionalStoredAs  // DIRECTORY is a non-reserved keyword
 | 'INSERT' 'OVERWRITE_DIRECTORY' HdfsPath InsertRowFormat_EDIT OptionalStoredAs
 | 'INSERT' 'OVERWRITE_DIRECTORY' HdfsPath OptionalInsertRowFormat OptionalStoredAs_EDIT
 | 'INSERT' 'INTO' OptionalTable 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['TABLE']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     $$ = { keepTables: true }
   }
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec OptionalParenthesizedColumnList
   {
     $$ = { keepTables: true }
   }
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier PartitionSpec_EDIT OptionalParenthesizedColumnList
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 | 'INSERT' 'INTO' OptionalTable SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalParenthesizedColumnList_EDIT
   {
     $4.owner = 'insert';
     parser.addTablePrimary($4);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.owner = 'insert';
     }
   }
 ;

Inserts
 : GenericInsert
 | Inserts GenericInsert
 ;

Inserts_EDIT
 : GenericInsert_EDIT
 | Inserts GenericInsert_EDIT
 | GenericInsert_EDIT Inserts
 | Inserts GenericInsert_EDIT Inserts
 ;

// TODO: Verify unions in insert
GenericInsert
 : InsertWithoutQuery SelectWithoutTableExpression OptionalSelectConditions
 ;

GenericInsert_EDIT
 : InsertWithoutQuery_EDIT
 | InsertWithoutQuery_EDIT SelectWithoutTableExpression OptionalSelectConditions
 | InsertWithoutQuery 'CURSOR'
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords(parser.createWeightedKeywords($1.suggestKeywords, 2).concat([{ value: 'SELECT', weight: 1}]));
     } else {
       parser.suggestKeywords(['SELECT']);
     }
   }
 | InsertWithoutQuery SelectWithoutTableExpression_EDIT OptionalSelectConditions
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
 | InsertWithoutQuery SelectWithoutTableExpression OptionalSelectConditions_EDIT
 ;

OptionalTable
 :
 | 'TABLE'
 ;

OptionalInsertRowFormat
 :
 | 'ROW' 'FORMAT' DelimitedRowFormat
 ;

InsertRowFormat_EDIT
 : 'ROW' 'CURSOR'
   {
     parser.suggestKeywords(['FORMAT DELIMITED']);
   }
 | 'ROW' 'FORMAT' 'CURSOR'
   {
     parser.suggestKeywords(['DELIMITED']);
   }
 | 'ROW' 'FORMAT' DelimitedRowFormat_EDIT
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
     var keywords = parser.getSelectListKeywords();
     if (!$2 || $2 === 'ALL') {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (!$2) {
       keywords.push({ value: 'ALL', weight: 2 });
       keywords.push({ value: 'DISTINCT', weight: 2 });
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns();
   }
 ;
