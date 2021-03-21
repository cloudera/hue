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

SqlSyntax
 : NewStatement SqlStatements EOF
 ;

SqlAutocomplete
 : NewStatement SqlStatements EOF
   {
     return parser.yy.result;
   }
 | NewStatement SqlStatements_EDIT EOF
   {
     return parser.yy.result;
   }
 ;

NewStatement
 : /* empty */
   {
     parser.prepareNewStatement();
   }
 ;

SqlStatements
 :
 | SqlStatement
   {
     parser.addStatementLocation(@1);
   }
 | SqlStatements ';' NewStatement SqlStatements
 ;

SqlStatements_EDIT
 : SqlStatement_EDIT
   {
     parser.addStatementLocation(@1);
   }
 | SqlStatement_EDIT ';' NewStatement SqlStatements
   {
     parser.addStatementLocation(@1);
   }
 | SqlStatements ';' NewStatement SqlStatement_EDIT
   {
     parser.addStatementLocation(@4);
   }
 | SqlStatements ';' NewStatement SqlStatement_EDIT ';' NewStatement SqlStatements
   {
     parser.addStatementLocation(@4);
   }
 ;

SqlStatement
 : DataDefinition
 | DataManipulation
 | QuerySpecification
 ;

SqlStatement_EDIT
 : AnyCursor
   {
     parser.suggestDdlAndDmlKeywords();
   }
 | CommonTableExpression 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | DataDefinition_EDIT
 | DataManipulation_EDIT
 | QuerySpecification_EDIT
 | SetSpecification_EDIT
 ;

NonReservedKeyword
 : 'ROLE'
 | 'OPTION'
 | 'STRUCT'
 ;

RegularIdentifier
 : 'REGULAR_IDENTIFIER'
 | 'VARIABLE_REFERENCE'
 | NonReservedKeyword
 ;

// This is a work-around for error handling when a statement starts with some token that the parser can understand but
// it's not a valid statement (see ErrorStatement). It contains everything except valid starting tokens ('SELECT', 'USE' etc.)
NonStartingToken
 : '!'
 | '('
 | ')'
 | '*'
 | ','
 | '-'
 | '.'
 | '<'
 | '='
 | '>'
 | '['
 | ']'
 | '~'
 | 'ALL'
 | 'ANALYTIC'
 | 'AND'
 | 'ARITHMETIC_OPERATOR'
 | 'ARRAY'
 | 'AS'
 | 'ASC'
 | 'AVG'
 | 'BACKTICK'
 | 'BETWEEN'
 | 'BIGINT'
 | 'BOOLEAN'
 | 'BY'
 | 'CASE'
 | 'CAST'
 | 'CHAR'
 | 'COMPARISON_OPERATOR'
 | 'COUNT'
 | 'CROSS'
 | 'CURRENT'
 | 'DATABASE'
 | 'DECIMAL'
 | 'DESC'
 | 'DISTINCT'
 | 'DOUBLE'
 | 'DOUBLE_QUOTE'
 | 'ELSE'
 | 'END'
 | 'EXISTS'
 | 'FALSE'
 | 'FLOAT'
 | 'FOLLOWING'
 | 'FROM'
 | 'FULL'
 | 'GROUP'
 | 'HAVING'
 | 'HDFS_START_QUOTE'
 | 'IF'
 | 'IN'
 | 'INNER'
 | 'INT'
 | 'INTO'
 | 'IS'
 | 'JOIN'
 | 'LEFT'
 | 'LIKE'
 | 'LIMIT'
 | 'MAP'
 | 'MAX'
 | 'MIN'
 | 'NOT'
 | 'NULL'
 | 'ON'
 | 'OPTION'
 | 'OR'
 | 'ORDER'
 | 'OUTER'
 | 'OVER'
 | 'PARTITION'
 | 'PRECEDING'
 | 'PURGE'
 | 'RANGE'
 | 'REGEXP'
 | 'REGULAR_IDENTIFIER'
 | 'RIGHT'
 | 'RLIKE'
 | 'ROLE'
 | 'ROW'
 | 'ROWS'
 | 'SCHEMA'
 | 'SEMI'
 | 'SET'
 | 'SINGLE_QUOTE'
 | 'SMALLINT'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'STRING'
 | 'STRUCT'
 | 'SUM'
 | 'TABLE'
 | 'THEN'
 | 'TIMESTAMP'
 | 'TINYINT'
 | 'TRUE'
 | 'UNION'
 | 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER_E'
 | 'VALUES'
 | 'VAR_POP'
 | 'VAR_SAMP'
 | 'VARCHAR'
 | 'VARIABLE_REFERENCE'
 | 'VARIANCE'
 | 'WHEN'
 | 'WHERE'
 ;

// ===================================== Commonly used constructs =====================================

Commas
 : ','
 | Commas ','
 ;

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

FromOrIn
 : 'FROM'
 | 'IN'
 ;

DatabaseOrSchema
 : 'DATABASE'
 | 'SCHEMA'
 ;

SingleQuotedValue
 : 'SINGLE_QUOTE' 'VALUE' 'SINGLE_QUOTE'  -> $2
 | 'SINGLE_QUOTE' 'SINGLE_QUOTE'          -> ''
 ;

SingleQuotedValue_EDIT
 : 'SINGLE_QUOTE' 'PARTIAL_VALUE'
 ;

DoubleQuotedValue
 : 'DOUBLE_QUOTE' 'VALUE' 'DOUBLE_QUOTE'  -> $2
 | 'DOUBLE_QUOTE' 'DOUBLE_QUOTE'          -> ''
 ;

DoubleQuotedValue_EDIT
 : 'DOUBLE_QUOTE' 'PARTIAL_VALUE'
 ;

QuotedValue
 : SingleQuotedValue
 | DoubleQuotedValue
 ;

QuotedValue_EDIT
 : SingleQuotedValue_EDIT
 | DoubleQuotedValue_EDIT
 ;

OptionalFromDatabase
 :
 | FromOrIn DatabaseIdentifier
 ;

OptionalFromDatabase_EDIT
 : FromOrIn DatabaseIdentifier_EDIT
 ;

OptionalCascade
 :
 | 'CASCADE'
 ;

OptionalIfExists
 :
 | 'IF' 'EXISTS'
   {
     parser.yy.correlatedSubQuery = false;
   }
 ;

OptionalIfExists_EDIT
 : 'IF' 'CURSOR'
   {
     parser.suggestKeywords(['EXISTS']);
   }
 ;

OptionalIfNotExists
 :
 | 'IF' 'NOT' 'EXISTS'
   {
     parser.yy.correlatedSubQuery = false;
   }
 ;

OptionalIfNotExists_EDIT
 : 'IF' 'CURSOR'
   {
     parser.suggestKeywords(['NOT EXISTS']);
   }
 | 'IF' 'NOT' 'CURSOR'
   {
     parser.suggestKeywords(['EXISTS']);
   }
 ;

OptionalInDatabase
 :
 | 'IN' DatabaseIdentifier
 | 'IN' DatabaseIdentifier_EDIT
 ;

OptionalPartitionSpec
 :
 | PartitionSpec
 ;

OptionalPartitionSpec_EDIT
 : PartitionSpec_EDIT
 ;

PartitionSpec
 : 'PARTITION' '(' PartitionSpecList ')'
 ;

PartitionSpec_EDIT
 : 'PARTITION' '(' PartitionSpecList_EDIT RightParenthesisOrError
 ;

RangePartitionSpec
 : UnsignedValueSpecification RangePartitionComparisonOperator 'VALUES' RangePartitionComparisonOperator UnsignedValueSpecification
 ;

RangePartitionSpec_EDIT
 : UnsignedValueSpecification 'CURSOR'
   {
     parser.suggestKeywords(['<', '<=', '<>', '=', '>', '>=']);
   }
 | UnsignedValueSpecification RangePartitionComparisonOperator 'CURSOR'
   {
     parser.suggestKeywords(['VALUES']);
   }
 | UnsignedValueSpecification RangePartitionComparisonOperator 'VALUES' 'CURSOR'
   {
     parser.suggestKeywords(['<', '<=', '<>', '=', '>', '>=']);
   }
 | UnsignedValueSpecification 'CURSOR' 'VALUES' RangePartitionComparisonOperator UnsignedValueSpecification
   {
     parser.suggestKeywords(['<', '<=', '<>', '=', '>', '>=']);
   }
 | UnsignedValueSpecification RangePartitionComparisonOperator 'CURSOR' RangePartitionComparisonOperator UnsignedValueSpecification
   {
     parser.suggestKeywords(['VALUES']);
   }
 | UnsignedValueSpecification RangePartitionComparisonOperator 'VALUES' 'CURSOR' UnsignedValueSpecification
   {
     parser.suggestKeywords(['<', '<=', '<>', '=', '>', '>=']);
   }
 ;

RangePartitionComparisonOperator
 : 'COMPARISON_OPERATOR'
 | '='
 | '<'
 | '>'
 ;

ConfigurationName
 : RegularIdentifier
 | 'CURSOR'
 ;

PartialBacktickedOrAnyCursor
 : AnyCursor
 | PartialBacktickedIdentifier
 ;

PartialBacktickedOrCursor
 : 'CURSOR'
 | PartialBacktickedIdentifier
 ;

PartialBacktickedOrPartialCursor
 : 'PARTIAL_CURSOR'
 | PartialBacktickedIdentifier
 ;

PartialBacktickedIdentifier
 : 'BACKTICK' 'PARTIAL_VALUE'
 ;

RightParenthesisOrError
 : ')'
 | error
 ;

OptionalParenthesizedColumnList
 :
 | ParenthesizedColumnList
 ;

OptionalParenthesizedColumnList_EDIT
 : ParenthesizedColumnList_EDIT
 ;

ParenthesizedColumnList
 : '(' ColumnList ')'
 ;

ParenthesizedColumnList_EDIT
 : '(' ColumnList_EDIT RightParenthesisOrError
 | '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestColumns();
   }
 ;

ColumnList
 : ColumnIdentifier
 | ColumnList ',' ColumnIdentifier
 ;

ColumnList_EDIT
 : ColumnList ',' AnyCursor
   {
     parser.suggestColumns();
   }
 | ColumnList ',' AnyCursor ',' ColumnList
   {
     parser.suggestColumns();
   }
 ;

ParenthesizedSimpleValueList
 : '(' SimpleValueList ')'
 ;

SimpleValueList
 : UnsignedValueSpecification
 | SimpleValueList ',' UnsignedValueSpecification
 ;

SchemaQualifiedTableIdentifier
 : RegularOrBacktickedIdentifier
   {
     parser.addTableLocation(@1, [ { name: $1 } ]);
     $$ = { identifierChain: [ { name: $1 } ] };
   }
 | RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@1, [ { name: $1 } ]);
     parser.addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] };
   }
 ;

SchemaQualifiedTableIdentifier_EDIT
 : PartialBacktickedIdentifier
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier '.' RegularOrBacktickedIdentifier
   {
     parser.suggestDatabases();
     $$ = { identifierChain: [{ name: $1 }] };
   }
 | RegularOrBacktickedIdentifier '.' PartialBacktickedOrPartialCursor
   {
     parser.suggestTablesOrColumns($1);
   }
 ;

SchemaQualifiedIdentifier
 : RegularOrBacktickedIdentifier                                       -> [{ name: $1 }]
 | RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier  -> [{ name: $1 }, { name: $2 }]
 ;

SchemaQualifiedIdentifier_EDIT
 : PartialBacktickedIdentifier
   {
     parser.suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier '.' RegularOrBacktickedIdentifier
   {
     parser.suggestDatabases();
     $$ = { identifierChain: [{ name: $1 }] };
   }
 | RegularOrBacktickedIdentifier '.' PartialBacktickedOrPartialCursor
 ;

DatabaseIdentifier
 : RegularOrBacktickedIdentifier
 ;

DatabaseIdentifier_EDIT
 : PartialBacktickedOrCursor
   {
     parser.suggestDatabases();
   }
 ;

PartitionSpecList
 : PartitionExpression
 | PartitionSpecList ',' PartitionExpression
 ;

PartitionSpecList_EDIT
 : PartitionExpression_EDIT
 | PartitionSpecList ',' PartitionExpression_EDIT
 | PartitionExpression_EDIT ',' PartitionSpecList
 | PartitionSpecList ',' PartitionExpression_EDIT ',' PartitionSpecList
 ;

PartitionExpression
 : ColumnIdentifier '=' ValueExpression
 ;

PartitionExpression_EDIT
 : ColumnIdentifier '=' ValueExpression_EDIT
 | ColumnIdentifier '=' AnyCursor
   {
     parser.valueExpressionSuggest();
   }
 | PartialBacktickedIdentifier '=' ValueExpression
   {
     parser.suggestColumns();
   }
 | AnyCursor
   {
     parser.suggestColumns();
   }
 ;

RegularOrBacktickedIdentifier
 : RegularIdentifier
 | 'BACKTICK' 'VALUE' 'BACKTICK'  -> $2
 | 'BACKTICK' 'BACKTICK'          -> ''
 ;

// TODO: Same as SchemaQualifiedTableIdentifier?
RegularOrBackTickedSchemaQualifiedName
 : RegularOrBacktickedIdentifier
   {
     parser.addTableLocation(@1, [ { name: $1 } ]);
     $$ = { identifierChain: [ { name: $1 } ] };
   }
 | RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@1, [ { name: $1 } ]);
     parser.addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] };
   }
 ;

RegularOrBackTickedSchemaQualifiedName_EDIT
 : PartialBacktickedIdentifier
   {
     parser.suggestTables();
     parser.suggestDatabases({ prependDot: true });
   }
 | RegularOrBacktickedIdentifier '.' PartialBacktickedOrPartialCursor
   {
     parser.suggestTablesOrColumns($1);
   }
 ;


LocalOrSchemaQualifiedName
 : RegularOrBackTickedSchemaQualifiedName
 | RegularOrBackTickedSchemaQualifiedName RegularOrBacktickedIdentifier  -> { identifierChain: $1.identifierChain, alias: $2 }
 ;

LocalOrSchemaQualifiedName_EDIT
 : RegularOrBackTickedSchemaQualifiedName_EDIT
 | RegularOrBackTickedSchemaQualifiedName_EDIT RegularOrBacktickedIdentifier
 ;

ColumnReference
 : BasicIdentifierChain
   {
     parser.yy.locations[parser.yy.locations.length - 1].type = 'column';
   }
 | BasicIdentifierChain '.' '*'
   {
     parser.addAsteriskLocation(@3, $1.concat({ asterisk: true }));
   }
 ;

ColumnReference_EDIT
 : BasicIdentifierChain_EDIT
 ;

BasicIdentifierChain
 : ColumnIdentifier
   {
     $$ = [ $1.identifier ];
     parser.yy.firstChainLocation = parser.addUnknownLocation($1.location, [ $1.identifier ]);
   }
 | BasicIdentifierChain '.' ColumnIdentifier
   {
     if (parser.yy.firstChainLocation) {
       parser.yy.firstChainLocation.firstInChain = true;
       delete parser.yy.firstChainLocation;
     }
     $1.push($3.identifier);
     parser.addUnknownLocation($3.location, $1.concat());
   }
 ;

// TODO: Merge with DerivedColumnChain_EDIT ( issue is starting with PartialBacktickedOrPartialCursor)
BasicIdentifierChain_EDIT
 : BasicIdentifierChain '.' PartialBacktickedOrPartialCursor
   {
     parser.suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: [{ value: '*', weight: 10000 }] };
   }
 | BasicIdentifierChain '.' PartialBacktickedOrPartialCursor '.' BasicIdentifierChain
   {
     parser.suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: [{ value: '*', weight: 10000 }] };
   }
 ;

DerivedColumnChain
 : ColumnIdentifier  -> [ $1.identifier ]
 | DerivedColumnChain '.' ColumnIdentifier
   {
     $1.push($3.identifier);
   }
 ;

DerivedColumnChain_EDIT
 : PartialBacktickedIdentifierOrPartialCursor
   {
     parser.suggestColumns();
   }
 | DerivedColumnChain '.' PartialBacktickedIdentifierOrPartialCursor
   {
     parser.suggestColumns({ identifierChain: $1 });
   }
 | DerivedColumnChain '.' PartialBacktickedIdentifierOrPartialCursor '.' DerivedColumnChain
   {
     parser.suggestColumns({ identifierChain: $1 });
   }
 | PartialBacktickedIdentifierOrPartialCursor '.' DerivedColumnChain
   {
     parser.suggestColumns();
   }
 ;

ColumnIdentifier
 : RegularOrBacktickedIdentifier                                                                               -> { identifier: { name: $1 }, location: @1 }
 ;

PartialBacktickedIdentifierOrPartialCursor
 : PartialBacktickedIdentifier
 | 'PARTIAL_CURSOR'
 ;

PrimitiveType
 : 'BIGINT'
 | 'BOOLEAN'
 | 'CHAR' OptionalTypeLength
 | 'DECIMAL' OptionalTypePrecision
 | 'DOUBLE'
 | 'FLOAT'
 | 'INT'
 | 'SMALLINT'
 | 'STRING'
 | 'TIMESTAMP'
 | 'TINYINT'
 | 'VARCHAR' OptionalTypeLength
 ;

OptionalTypeLength
 :
 | '(' 'UNSIGNED_INTEGER' ')'
 ;

OptionalTypePrecision
 :
 | '(' 'UNSIGNED_INTEGER' ')'
 | '(' 'UNSIGNED_INTEGER' ',' 'UNSIGNED_INTEGER' ')'
 ;

ValueExpression
 : NonParenthesizedValueExpressionPrimary
 ;

ValueExpression_EDIT
 : NonParenthesizedValueExpressionPrimary_EDIT
 ;

ValueExpression_EDIT
 : ValueExpression 'NOT' 'CURSOR'
   {
     parser.suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'LIKE', 'REGEXP', 'RLIKE']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpressionList
 : ValueExpression
   {
     $1.position = 1;
   }
 | ValueExpressionList ',' ValueExpression
   {
     $3.position = $1.position + 1;
     $$ = $3;
   }
 ;

ValueExpressionList_EDIT
 : ValueExpression_EDIT
   {
     $1.position = 1;
   }
 | ValueExpressionList ',' ValueExpression_EDIT
   {
     $1.position += 1;
   }
 | ValueExpression_EDIT ',' ValueExpressionList
   {
     $1.position = 1;
   }
 | ValueExpressionList ',' ValueExpression_EDIT ',' ValueExpressionList
   {
     $1.position += 1;
   }
 | ValueExpressionList ',' AnyCursor
   {
     parser.valueExpressionSuggest();
     $1.position += 1;
   }
 | ValueExpressionList ',' AnyCursor ',' ValueExpressionList
   {
     parser.valueExpressionSuggest();
     $1.position += 1;
   }
 | ValueExpressionList 'CURSOR' ',' ValueExpressionList
   {
     parser.suggestValueExpressionKeywords($1);
   }
 | AnyCursor ',' ValueExpressionList
   {
     parser.valueExpressionSuggest();
     $$ = { cursorAtStart : true, position: 1 };
   }
 | AnyCursor ','
   {
     parser.valueExpressionSuggest();
     $$ = { cursorAtStart : true, position: 1 };
   }
 | ',' AnyCursor
   {
     parser.valueExpressionSuggest();
     $$ = { position: 2 };
   }
 | ',' AnyCursor ',' ValueExpressionList
   {
     parser.valueExpressionSuggest();
     $$ = { position: 2 };
   }
 ;

InValueList
 : NonParenthesizedValueExpressionPrimary
 | InValueList ',' NonParenthesizedValueExpressionPrimary
 ;

NonParenthesizedValueExpressionPrimary
 : UnsignedValueSpecification
 | ColumnOrArbitraryFunctionRef  -> { types: ['COLREF'], columnReference: $1.chain }
 | 'NULL'                        -> { types: [ 'NULL' ], text: $1 }
 ;

NonParenthesizedValueExpressionPrimary_EDIT
 : UnsignedValueSpecification_EDIT
 | ColumnOrArbitraryFunctionRef_EDIT
   {
     if ($1.suggestKeywords) {
       $$ = { types: ['COLREF'], columnReference: $1, suggestKeywords: $1.suggestKeywords };
     } else {
       $$ = { types: ['COLREF'], columnReference: $1 };
     }
   }
 ;

ColumnOrArbitraryFunctionRef
 : BasicIdentifierChain
   {
     var lastLoc = parser.yy.locations[parser.yy.locations.length - 1];
     if (lastLoc.type !== 'variable') {
       lastLoc.type = 'column';
     }
     // used for function references with db prefix
     var firstLoc = parser.yy.locations[parser.yy.locations.length - $1.length];
     $$ = { chain: $1, firstLoc: firstLoc, lastLoc: lastLoc }
   }
 | BasicIdentifierChain '.' '*'
   {
     parser.addAsteriskLocation(@3, $1.concat({ asterisk: true }));
   }
 ;

ColumnOrArbitraryFunctionRef_EDIT
 : BasicIdentifierChain_EDIT
 ;

SignedInteger
 : UnsignedNumericLiteral
 | '-' UnsignedNumericLiteral
 | '+' UnsignedNumericLiteral
 ;

UnsignedValueSpecification
 : UnsignedLiteral
 ;

UnsignedValueSpecification_EDIT
 : UnsignedLiteral_EDIT
   {
     parser.suggestValues($1);
   }
 ;

UnsignedLiteral
 : UnsignedNumericLiteral  -> { types: [ 'NUMBER' ], text: $1 }
 | GeneralLiteral
 ;

UnsignedLiteral_EDIT
 : GeneralLiteral_EDIT
 ;

UnsignedNumericLiteral
 : ExactNumericLiteral
 | ApproximateNumericLiteral
 ;

ExactNumericLiteral
 : 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER' '.'                     -> $1 + $2
 | 'UNSIGNED_INTEGER' '.' 'UNSIGNED_INTEGER'  -> $1 + $2 + $3
 | '.' 'UNSIGNED_INTEGER'                     -> $1 + $2
 ;

ApproximateNumericLiteral
 : UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'                        -> $1 + $2
 | '.' UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'                    -> $1 + $2 + $3
 | 'UNSIGNED_INTEGER' '.' UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER' -> $1 + $2 + $3 + $4
 ;

GeneralLiteral
 : SingleQuotedValue
   {
     if (/\$\{[^}]*\}/.test($1)) {
       parser.addVariableLocation(@1, $1);
       $$ = { types: [ 'STRING' ], columnReference: [{ name: $1 }], text: "'" + $1 + "'" }
     } else {
       $$ = { types: [ 'STRING' ] }
     }
   }
 | DoubleQuotedValue
   {
     if (/\$\{[^}]*\}/.test($1)) {
       parser.addVariableLocation(@1, $1);
       $$ = { types: [ 'STRING' ], columnReference: [{ name: $1 }], text: '"' + $1 + '"' }
     } else {
       $$ = { types: [ 'STRING' ], text: '"' + $1 + '"' }
     }
   }
 | TruthValue         -> { types: [ 'BOOLEAN' ], text: $1 }
 ;

GeneralLiteral_EDIT
 : SingleQuotedValue_EDIT
  {
    $$ = { partialQuote: '\'', missingEndQuote: parser.yy.missingEndQuote };
  }
 | DoubleQuotedValue_EDIT
  {
    $$ = { partialQuote: '"', missingEndQuote: parser.yy.missingEndQuote };
  }
 ;

TruthValue
 : 'TRUE'
 | 'FALSE'
 ;

OptionalNot
 :
 | 'NOT'
 ;

TableReference
 : TablePrimaryOrJoinedTable
 ;

TableReference_EDIT
 : TablePrimaryOrJoinedTable_EDIT
 ;

TablePrimaryOrJoinedTable
 : TablePrimary
   {
     $$ = $1;

     if (parser.yy.latestTablePrimaries.length > 0) {
       var idx = parser.yy.latestTablePrimaries.length - 1;
       var tables = [];
       do {
         var tablePrimary = parser.yy.latestTablePrimaries[idx];
         if (!tablePrimary.subQueryAlias) {
           tables.unshift(tablePrimary.alias ? { identifierChain: tablePrimary.identifierChain, alias: tablePrimary.alias } : { identifierChain: tablePrimary.identifierChain })
         }
         idx--;
       } while (idx >= 0 && tablePrimary.join && !tablePrimary.subQueryAlias)

       if (tables.length > 0) {
         $$.suggestJoins = {
           prependJoin: true,
           tables: tables
         };
       }
      }
   }
 | JoinedTable
 ;

TablePrimaryOrJoinedTable_EDIT
 : TablePrimary_EDIT
 | JoinedTable_EDIT
 ;

JoinedTable
 : TablePrimary Joins  -> $2
 ;

JoinedTable_EDIT
 : TablePrimary Joins_EDIT
 | TablePrimary_EDIT Joins
 ;

TablePrimary
 : TableOrQueryName OptionalCorrelationName
   {
     $$ = {
       primary: $1
     }
     if ($1.identifierChain) {
       if ($2) {
         $1.alias = $2.alias
         parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
       }
       parser.addTablePrimary($1);
     }

     var keywords = [];
     if (!$2) {
       keywords = ['AS'];
     } else if ($2.suggestKeywords) {
       keywords = $2.suggestKeywords;
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 | DerivedTable OptionalCorrelationName
   {
     $$ = {
       primary: $1
     };

     if ($2) {
       $$.primary.alias = $2.alias;
       parser.addTablePrimary({ subQueryAlias: $2.alias });
       parser.addSubqueryAliasLocation($2.location, $2.alias, $1.identifierChain);
     }

     var keywords = [];
     if (!$2) {
       keywords = ['AS'];
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalCorrelationName
   {
     if ($2) {
       parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
     }
   }
 | DerivedTable_EDIT OptionalCorrelationName
   {
     if ($2) {
       parser.addTablePrimary({ subQueryAlias: $2.alias });
       parser.addSubqueryAliasLocation($2.location, $2.alias);
     }
   }
 | DerivedTable OptionalCorrelationName_EDIT
 ;

TableOrQueryName
 : SchemaQualifiedTableIdentifier
 ;

TableOrQueryName_EDIT
 : SchemaQualifiedTableIdentifier_EDIT
 ;

DerivedTable
 : TableSubQuery
 ;

DerivedTable_EDIT
 : TableSubQuery_EDIT
 ;

OptionalOnColumn
 :
 | 'ON' ValueExpression
 ;

OptionalOnColumn_EDIT
 : 'ON' 'CURSOR'
   {
     parser.valueExpressionSuggest();
   }
 | 'ON' ValueExpression_EDIT
 ;

PushQueryState
 :
   {
     parser.pushQueryState();
   }
 ;

PopQueryState
 :
   {
     parser.popQueryState();
   }
 ;

TableSubQuery
 : '(' TableSubQueryInner ')'  -> $2
 | '(' DerivedTable OptionalCorrelationName ')'
   {
     if ($3) {
       $2.alias = $3.alias;
       parser.addTablePrimary({ subQueryAlias: $3.alias });
       parser.addSubqueryAliasLocation($3.location, $3.alias, $2.identifierChain);
     }
     $$ = $2;
   }
 ;

TableSubQuery_EDIT
 : '(' TableSubQueryInner_EDIT RightParenthesisOrError
 | '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['SELECT']);
   }
 ;

TableSubQueryInner
 : PushQueryState SubQuery
   {
     var subQuery = parser.getSubQuery($2);
     subQuery.columns.forEach(function (column) {
       parser.expandIdentifierChain({ wrapper: column });
       delete column.linked;
     });
     parser.popQueryState(subQuery);
     $$ = subQuery;
   }
 ;

TableSubQueryInner_EDIT
 : PushQueryState SubQuery_EDIT PopQueryState
 ;

SubQuery
 : QueryExpression
 ;

SubQuery_EDIT
 : QueryExpression_EDIT
 ;

QueryExpression
 : QueryExpressionBody
 ;

QueryExpression_EDIT
 : QueryExpressionBody_EDIT
 ;

QueryExpressionBody
 : NonJoinQueryExpression
 ;

QueryExpressionBody_EDIT
 : NonJoinQueryExpression_EDIT
 ;

NonJoinQueryExpression
 : NonJoinQueryTerm
 ;

NonJoinQueryExpression_EDIT
 : NonJoinQueryTerm_EDIT
 ;

NonJoinQueryTerm
 : NonJoinQueryPrimary
 ;

NonJoinQueryTerm_EDIT
 : NonJoinQueryPrimary_EDIT
 ;

NonJoinQueryPrimary
 : SimpleTable
 ;

NonJoinQueryPrimary_EDIT
 : SimpleTable_EDIT
 ;

SimpleTable
 : QuerySpecification
 ;

SimpleTable_EDIT
 : QuerySpecification_EDIT
 ;

OptionalCorrelationName
 :
 | RegularOrBacktickedIdentifier        -> { alias: $1, location: @1 }
 | QuotedValue                          -> { alias: $1, location: @1 }
 | 'AS' RegularOrBacktickedIdentifier  -> { alias: $2, location: @2 }
 | 'AS' QuotedValue                    -> { alias: $2, location: @2 }
 ;

OptionalCorrelationName_EDIT
 : PartialBacktickedIdentifier
 | QuotedValue_EDIT
 | 'AS' PartialBacktickedIdentifier
 | 'AS' QuotedValue_EDIT
 | 'AS' 'CURSOR'
 ;

WindowExpression
 : '(' OptionalPartitionBy OptionalOrderByAndWindow ')'
 ;

WindowExpression_EDIT
 : '(' PartitionBy_EDIT OptionalOrderByAndWindow RightParenthesisOrError
   {
     if (parser.yy.result.suggestFunctions) {
       parser.suggestAggregateFunctions();
     }
   }
 | '(' OptionalPartitionBy OptionalOrderByAndWindow_EDIT RightParenthesisOrError
   {
     if (parser.yy.result.suggestFunctions) {
       parser.suggestAggregateFunctions();
     }
   }
 | '(' AnyCursor OptionalPartitionBy OptionalOrderByAndWindow RightParenthesisOrError
   {
     if (!$3 && !$4) {
       parser.suggestKeywords([{ value: 'PARTITION BY', weight: 2 }, { value: 'ORDER BY', weight: 1 }]);
     } else if (!$3) {
       parser.suggestKeywords(['PARTITION BY']);
     }
   }
 | '(' 'PARTITION' 'BY' ValueExpressionList 'CURSOR' OptionalOrderByAndWindow RightParenthesisOrError
    {
      if (!$6) {
        parser.suggestValueExpressionKeywords($4, [{ value: 'ORDER BY', weight: 2 }]);
      } else {
        parser.suggestValueExpressionKeywords($4);
      }
    }
  ;

OptionalPartitionBy
 :
 | PartitionBy
 ;

PartitionBy
 : 'PARTITION' 'BY' ValueExpressionList  -> $3
 ;

PartitionBy_EDIT
 : 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'PARTITION' 'BY' 'CURSOR'
   {
     parser.valueExpressionSuggest();
   }
 | 'PARTITION' 'BY' ValueExpressionList_EDIT
 ;

OptionalOrderByAndWindow
 :
 | OrderByClause OptionalWindowSpec
 ;

OptionalOrderByAndWindow_EDIT
  : OrderByClause_EDIT
    {
      // Only allowed in last order by
      delete parser.yy.result.suggestAnalyticFunctions;
    }
  | OrderByClause 'CURSOR' OptionalWindowSpec
    {
      var keywords = [];
      if ($1.suggestKeywords) {
        keywords = parser.createWeightedKeywords($1.suggestKeywords, 2);
      }
      if (!$3) {
        keywords = keywords.concat([{ value: 'RANGE BETWEEN', weight: 1 }, { value: 'ROWS BETWEEN', weight: 1 }]);
      }
      parser.suggestKeywords(keywords);
    }
  | OrderByClause WindowSpec_EDIT
  ;

OptionalWindowSpec
 :
 | WindowSpec
 ;

WindowSpec
 : RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing
 | RowsOrRange 'UNBOUNDED' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing
 ;

WindowSpec_EDIT
 : RowsOrRange 'CURSOR'
   {
     parser.suggestKeywords(['BETWEEN']);
   }
 | RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing 'CURSOR'
   {
     if (!$4 && !$5) {
       parser.suggestKeywords(['CURRENT ROW', 'UNBOUNDED PRECEDING']);
     } else if (!$5) {
       parser.suggestKeywords(['AND']);
     }
   }
 | RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding_EDIT OptionalAndFollowing
 | RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing_EDIT
 | RowsOrRange 'UNBOUNDED' PopLexerState OptionalCurrentOrPreceding 'CURSOR'
 | RowsOrRange 'UNBOUNDED' PopLexerState OptionalCurrentOrPreceding_EDIT
 ;

PopLexerState
 :
  {
    lexer.popState();
  }
 ;

PushHdfsLexerState
 :
  {
    lexer.begin('hdfs');
  }
 ;

HdfsPath
 : 'HDFS_START_QUOTE' 'HDFS_PATH' 'HDFS_END_QUOTE'
 ;

HdfsPath_EDIT
 : 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_PATH' 'HDFS_END_QUOTE'
    {
      parser.suggestHdfs({ path: $2 });
    }
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'
   {
     parser.suggestHdfs({ path: $2 });
   }
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR'
    {
      parser.suggestHdfs({ path: $2 });
    }
 | 'HDFS_START_QUOTE' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'
   {
     parser.suggestHdfs({ path: '' });
   }
 | 'HDFS_START_QUOTE' 'PARTIAL_CURSOR'
    {
      parser.suggestHdfs({ path: '' });
    }
 ;

RowsOrRange
 : 'ROWS'
 | 'RANGE'
 ;

OptionalCurrentOrPreceding
 :
 | IntegerOrUnbounded 'PRECEDING'
 | 'CURRENT' 'ROW'
 ;

OptionalCurrentOrPreceding_EDIT
 : IntegerOrUnbounded 'CURSOR'
   {
     parser.suggestKeywords(['PRECEDING']);
   }
 | 'CURRENT' 'CURSOR'
   {
     parser.suggestKeywords(['ROW']);
   }
 ;

OptionalAndFollowing
 :
 | 'AND' 'CURRENT' 'ROW'
 | 'AND' IntegerOrUnbounded 'FOLLOWING'
 ;

OptionalAndFollowing_EDIT
 : 'AND' 'CURSOR'
   {
     parser.suggestKeywords(['CURRENT ROW', 'UNBOUNDED FOLLOWING']);
   }
 | 'AND' 'CURRENT' 'CURSOR'
   {
     parser.suggestKeywords(['ROW']);
   }
 | 'AND' IntegerOrUnbounded 'CURSOR'
   {
     parser.suggestKeywords(['FOLLOWING']);
   }
 ;

IntegerOrUnbounded
 : 'UNSIGNED_INTEGER'
 | 'UNBOUNDED'
 ;
