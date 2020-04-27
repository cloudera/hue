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
     parser.suggestDdlAndDmlKeywords(['EXPLAIN', 'FROM']);
   }
 | CommonTableExpression 'CURSOR'
   {
     parser.suggestKeywords(['INSERT', 'SELECT']);
   }
 | DataDefinition_EDIT
 | DataManipulation_EDIT
 | QuerySpecification_EDIT
 | SetSpecification_EDIT
 ;

NonReservedKeyword
 : 'ABORT'
 | 'ADD'
 | 'ADMIN'
 | 'AFTER'
 | 'ANALYZE'
 | 'ARCHIVE'
 | 'AST'
 | 'AVRO'
 | 'BUCKET'
 | 'BUCKETS'
 | 'CASCADE'
 | 'CBO'
 | 'CHANGE'
 | 'CHECK'
 | 'CLUSTERED'
 | 'COLLECTION'
 | 'COLUMNS'
 | 'COMMENT'
 | 'COMPACT'
 | 'COMPACTIONS'
 | 'COMPUTE'
 | 'CONCATENATE'
 | 'COST'
 | 'CURRENT_DATE'
 | 'CURRENT_TIMESTAMP'
 | 'CURRENT_USER'
 | 'DATA'
 | 'DATABASES'
 | 'DAY'
 | 'DAYOFWEEK'
 | 'DBPROPERTIES'
 | 'DEFAULT'
 | 'DEFERRED'
 | 'DEFINED'
 | 'DELIMITED'
 | 'DEPENDENCY'
 | 'DETAIL'
 | 'DIRECTORY'
 | 'DISABLE'
 | 'DISTRIBUTED'
 | 'DOUBLE_PRECISION'
 | 'ENABLE'
 | 'ESCAPED'
 | 'EXCHANGE'
 | 'EXPLAIN'
 | 'EXPORT'
 | 'EXPRESSION'
 | 'FIELDS'
 | 'FILE'
 | 'FILEFORMAT'
 | 'FIRST'
 | 'FORMAT'
 | 'FUNCTIONS'
 | 'HOUR'
 | 'IDXPROPERTIES'
 | 'INPATH'
 | 'INPUTFORMAT'
 | 'ITEMS'
 | 'JAR'
 | 'JOINCOST'
 | 'JSONFILE'
 | 'KEY'
 | 'KEYS'
 | 'LAST'
 | 'LINES'
 | 'LITERAL'
 | 'LOAD'
 | 'LOCATION'
 | 'LOCKS'
 | 'MATCHED'
 | 'MATERIALIZED'
 | 'MERGE'
 | 'METADATA'
 | 'MINUTE'
 | 'MONTH'
 | 'MSCK'
 | 'NO_DROP'
 | 'NORELY'
 | 'NOSCAN'
 | 'NOVALIDATE'
 | 'OFFLINE'
 | 'ONLY'
 | 'OPERATOR'
 | 'OPTION'
 | 'ORC'
 | 'OUTPUTFORMAT'
 | 'OVERWRITE'
 | 'OVERWRITE_DIRECTORY'
 | 'OWNER'
 | 'PARQUET'
 | 'PARTITIONED'
 | 'PARTITIONS'
 | 'PERCENT'
 | 'PRIVILEGES'
 | 'PURGE'
 | 'QUARTER'
 | 'RCFILE'
 | 'REBUILD'
 | 'RECOVER'
 | 'RELOAD'
 | 'RELY'
 | 'RENAME'
 | 'REPAIR'
 | 'REPLACE'
 | 'REPLICATION'
 | 'RESTRICT'
 | 'REWRITE'
 | 'ROLE'
 | 'ROLES'
 | 'SCHEMAS'
 | 'SECOND'
 | 'SEQUENCEFILE'
 | 'SERDE'
 | 'SERDEPROPERTIES'
 | 'SETS'
 | 'SHOW'
 | 'SKEWED_LOCATION'
 | 'SKEWED'
 | 'SORTED'
 | 'STATISTICS'
 | 'STORED'
 | 'STORED_AS_DIRECTORIES'
 | 'STRING'
 | 'STRUCT'
 | 'SUMMARY'
 | 'TABLES'
 | 'TBLPROPERTIES'
 | 'TEMPORARY'
 | 'TERMINATED'
 | 'TEXTFILE'
 | 'TINYINT'
 | 'TOUCH'
 | 'TRANSACTIONAL'
 | 'TRANSACTIONS'
 | 'UNARCHIVE'
 | 'UNIONTYPE'
 | 'UNIQUE'
 | 'USE'
 | 'VECTORIZATION'
 | 'VIEW'
 | 'WAIT'
 | 'WEEK'
 | 'YEAR'
// | 'ASC'      // These cause conflicts, we could use a separate lexer state for DESCRIBE, ALTER, GRANT, REVOKE and SHOW
// | 'CLUSTER'
// | 'DESC'
// | 'DISTRIBUTE'
// | 'FORMATTED'
// | 'INDEX'
// | 'INDEXES'
// | 'LOCK'
// | 'OVER'
// | 'SCHEMA'
// | 'SHOW_DATABASE'
// | 'SORT'
// | 'TABLESAMPLE'
// | 'WINDOW'
// | 'WITH'
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
 | 'ADMIN'
 | 'ALL'
 | 'ANALYTIC'
 | 'AND'
 | 'ARITHMETIC_OPERATOR'
 | 'ARRAY'
 | 'AS'
 | 'ASC'
 | 'AUTHORIZATION'
 | 'AVG'
 | 'AVRO'
 | 'BACKTICK'
 | 'BETWEEN'
 | 'BIGINT'
 | 'BINARY'
 | 'BOOLEAN'
 | 'BUCKET'
 | 'BUCKETS'
 | 'BY'
 | 'CACHE'
 | 'CASE'
 | 'CAST'
 | 'CHAR'
 | 'CLUSTER'
 | 'CLUSTERED'
 | 'COLLECT_LIST'
 | 'COLLECT_SET'
 | 'COLLECTION'
 | 'COLUMNS'
 | 'COMMENT'
 | 'COMPACTIONS'
 | 'COMPARISON_OPERATOR'
 | 'COMPUTE'
 | 'CONF'
 | 'CONSTRAINT'
 | 'CORR'
 | 'COUNT'
 | 'COVAR_POP'
 | 'COVAR_SAMP'
 | 'CROSS'
 | 'CUBE'
 | 'CURRENT'
 | 'DATA'
 | 'DATABASE'
 | 'DATABASES'
 | 'DATE'
 | 'DAY'
 | 'DAYOFWEEK'
 | 'DBPROPERTIES'
 | 'DECIMAL'
 | 'DEFERRED'
 | 'DEFINED'
 | 'DELIMITED'
 | 'DEPENDENCY'
 | 'DESC'
 | 'DIRECTORY'
 | 'DISTINCT'
 | 'DISTRIBUTE'
 | 'DISTRIBUTED'
 | 'DOUBLE'
 | 'DOUBLE_PRECISION'
 | 'DOUBLE_QUOTE'
 | 'ELSE'
 | 'END'
 | 'ESCAPED'
 | 'EXISTS'
 | 'EXTENDED'
 | 'EXTERNAL'
 | 'FALSE'
 | 'FIELDS'
 | 'FILE'
 | 'FLOAT'
 | 'FOLLOWING'
 | 'FOR'
 | 'FOREIGN'
 | 'FORMAT'
 | 'FORMATTED'
 | 'FROM'
 | 'FULL'
 | 'FUNCTION'
 | 'FUNCTIONS'
 | 'GRANT'
 | 'GROUP'
 | 'GROUPING'
 | 'HAVING'
 | 'HDFS_START_QUOTE'
 | 'HISTOGRAM_NUMERIC'
 | 'HOUR'
 | 'IDXPROPERTIES'
 | 'IF'
 | 'IN'
 | 'INDEX'
 | 'INDEXES'
 | 'INNER'
 | 'INPATH'
 | 'INPUTFORMAT'
 | 'INT'
 | 'INTEGER'
 | 'INTO'
 | 'IS'
 | 'ITEMS'
 | 'JAR'
 | 'JOIN'
 | 'JSONFILE'
 | 'KEY'
 | 'KEYS'
 | 'LAST'
 | 'LATERAL'
 | 'LEFT'
 | 'LIKE'
 | 'LIMIT'
 | 'LINES'
 | 'LOCAL'
 | 'LOCATION'
 | 'LOCK'
 | 'LOCKS'
 | 'MACRO'
 | 'MAP'
 | 'MATCHED'
 | 'MAX'
 | 'METADATA'
 | 'MIN'
 | 'MINUTE'
 | 'MONTH'
 | 'NONE'
 | 'NORELY'
 | 'NOSCAN'
 | 'NOT'
 | 'NOVALIDATE'
 | 'NTILE'
 | 'NULL'
 | 'NULLS'
 | 'OF'
 | 'ON'
 | 'OPTION'
 | 'OR'
 | 'ORC'
 | 'ORDER'
 | 'OUT'
 | 'OUTER'
 | 'OUTPUTFORMAT'
 | 'OVER'
 | 'OVERWRITE'
 | 'OWNER'
 | 'PARQUET'
 | 'PARTITION'
 | 'PARTITIONED'
 | 'PARTITIONS'
 | 'PERCENT'
 | 'PERCENTILE'
 | 'PERCENTILE_APPROX'
 | 'PRECEDING'
 | 'PRIMARY'
 | 'PRIVILEGES'
 | 'PURGE'
 | 'QUARTER'
 | 'RANGE'
 | 'RCFILE'
 | 'REBUILD'
 | 'REFERENCES'
 | 'REGEXP'
 | 'REGULAR_IDENTIFIER'
 | 'RELY'
 | 'REPAIR'
 | 'REPLICATION'
 | 'RIGHT'
 | 'RLIKE'
 | 'ROLE'
 | 'ROLES'
 | 'ROLLUP'
 | 'ROW'
 | 'ROWS'
 | 'SCHEMA'
 | 'SCHEMAS'
 | 'SECOND'
 | 'SEMI'
 | 'SEQUENCEFILE'
 | 'SERDE'
 | 'SERDEPROPERTIES'
 | 'SET'
 | 'SETS'
 | 'SHOW_DATABASE'
 | 'SINGLE_QUOTE'
 | 'SKEWED'
 | 'SMALLINT'
 | 'SORTED'
 | 'STATISTICS'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'STORED'
 | 'STORED_AS_DIRECTORIES'
 | 'STRING'
 | 'STRUCT'
 | 'SUM'
 | 'TABLE'
 | 'TABLES'
 | 'TABLESAMPLE'
 | 'TBLPROPERTIES'
 | 'TEMPORARY'
 | 'TERMINATED'
 | 'TEXTFILE'
 | 'THEN'
 | 'TIMESTAMP'
 | 'TINYINT'
 | 'TRANSACTIONAL'
 | 'TRANSACTIONS'
 | 'TRUE'
 | 'UNION'
 | 'UNIONTYPE'
 | 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER_E'
 | 'USER'
 | 'USING'
 | 'VALUES'
 | 'VAR_POP'
 | 'VAR_SAMP'
 | 'VARCHAR'
 | 'VARIABLE_REFERENCE'
 | 'VARIANCE'
 | 'VIEW'
 | 'VIEWS'
 | 'WAIT'
 | 'WEEK'
 | 'WHEN'
 | 'WHERE'
 | 'WINDOW'
 | 'YEAR'
 | '~'
 ;

DataDefinition
 : DescribeStatement
 ;

DataDefinition_EDIT
 : DescribeStatement_EDIT
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

IndexOrIndexes
 : 'INDEX'
 | 'INDEXES'
 ;

DatabasesOrSchemas
 : 'DATABASES'
 | 'SCHEMAS'
 ;

RoleOrUser
 : 'ROLE'
 | 'USER'
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

OptionalExtended
 :
 | 'EXTENDED'
 ;

OptionalExtendedOrFormatted
 :
 | 'EXTENDED'
 | 'FORMATTED'
 ;

OptionalExternal
 :
 | 'EXTERNAL'
 ;

OptionallyFormattedIndex
 : 'FORMATTED' IndexOrIndexes
 | IndexOrIndexes
 ;

OptionallyFormattedIndex_EDIT
 : 'FORMATTED' 'CURSOR'
   {
     parser.suggestKeywords(['INDEX', 'INDEXES']);
   }
 | 'CURSOR' IndexOrIndexes
   {
     parser.suggestKeywords(['FORMATTED']);
   }
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

OptionalCascadeOrRestrict
 :
 | 'CASCADE'
 | 'RESTRICT'
 ;

OptionalTemporary
 :
 | 'TEMPORARY'
 ;

OptionalTransactional
 :
 | 'TRANSACTIONAL'
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
 | ConfigurationName '.' RegularIdentifier
 | ConfigurationName '.' 'PARTIAL_CURSOR'
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
 : ColumnIdentifier_EDIT
 | ColumnList ',' AnyCursor
   {
     parser.suggestColumns();
   }
 | ColumnList ',' ColumnIdentifier_EDIT
 | ColumnIdentifier_EDIT ',' ColumnList
 | ColumnList ',' ColumnIdentifier_EDIT ',' ColumnList
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
 | ColumnIdentifier // Partial partition specs are allowed in some cases
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

OptionalHdfsLocation
 :
 | HdfsLocation
 ;

HdfsLocation
 : 'LOCATION' HdfsPath
 ;

HdfsLocation_EDIT
 : 'LOCATION' HdfsPath_EDIT
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
 : ColumnIdentifier_EDIT
   {
     if ($1.insideKey) {
       parser.suggestKeyValues({ identifierChain: [ $1.identifier ] });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | BasicIdentifierChain '.' ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       parser.suggestKeyValues({ identifierChain: $1.concat([ $3.identifier ]) });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | BasicIdentifierChain '.' ColumnIdentifier_EDIT '.' BasicIdentifierChain
 | ColumnIdentifier_EDIT '.' BasicIdentifierChain
 | BasicIdentifierChain '.' PartialBacktickedOrPartialCursor
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
 : ColumnIdentifier_EDIT
   {
     if ($1.insideKey) {
       parser.suggestKeyValues({ identifierChain: [ $1.identifier ] });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | DerivedColumnChain '.' ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       parser.suggestKeyValues({ identifierChain: $1.concat([ $3.identifier ]) });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | DerivedColumnChain '.' ColumnIdentifier_EDIT '.' DerivedColumnChain
   {
     if ($3.insideKey) {
       parser.suggestKeyValues({ identifierChain: $1.concat([ $3.identifier ]) });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | ColumnIdentifier_EDIT '.' DerivedColumnChain
   {
     if ($1.insideKey) {
       parser.suggestKeyValues({ identifierChain: [ $1.identifier ] });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | PartialBacktickedIdentifierOrPartialCursor
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
 | RegularOrBacktickedIdentifier '[' ValueExpression ']'  -> { identifier: { name: $1, keySet: true }, location: @1 }
 | RegularOrBacktickedIdentifier '[' ']'                  -> { identifier: { name: $1, keySet: true }, location: @1 }
 ;

ColumnIdentifier_EDIT
 : RegularOrBacktickedIdentifier '[' AnyCursor RightSquareBracketOrError             -> { identifier: { name: $1 }, insideKey: true }
 | RegularOrBacktickedIdentifier '[' ValueExpression_EDIT RightSquareBracketOrError  -> { identifier: { name: $1 }}
 ;

PartialBacktickedIdentifierOrPartialCursor
 : PartialBacktickedIdentifier
 | 'PARTIAL_CURSOR'
 ;

RightSquareBracketOrError
 : ']'
 | error
 ;

// TODO: Support | DECIMAL(precision, scale)  -- (Note: Available in Hive 0.13.0 and later)
PrimitiveType
 : 'BIGINT'
 | 'BINARY'
 | 'BOOLEAN'
 | 'CHAR' OptionalTypeLength
 | 'DATE'
 | 'DECIMAL' OptionalTypePrecision
 | 'DOUBLE'
 | 'DOUBLE_PRECISION'
 | 'FLOAT'
 | 'INT'
 | 'INTEGER'
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

// ===================================== DESCRIBE statement =====================================

DescribeStatement
 : 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
     parser.addColumnLocation(@4, $4);
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
   }
 | 'DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier
   {
     parser.addDatabaseLocation(@4, [{ name: $4 }]);
   }
 | 'DESCRIBE' 'FUNCTION' OptionalExtended RegularIdentifier
 ;

DescribeStatement_EDIT
 : 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain_EDIT OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier DerivedColumnChain OptionalPartitionSpec
   {
     if (!$2) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     if (!$2) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier 'CURSOR' OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
     parser.suggestColumns();
     if (!$5) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain 'CURSOR' OptionalPartitionSpec
   {
     if (!$6) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain OptionalPartitionSpec_EDIT
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT

 | 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'FUNCTION', 'SCHEMA']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
    }
 | 'DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier_EDIT
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED']);
     }
   }
 | 'DESCRIBE' DatabaseOrSchema OptionalExtended 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        parser.suggestKeywords(['EXTENDED']);
      }
    }
 | 'DESCRIBE' 'FUNCTION' OptionalExtended 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED']);
     }
   }
 | 'DESCRIBE' 'FUNCTION' OptionalExtended 'CURSOR' RegularIdentifier
    {
      if (!$3) {
        parser.suggestKeywords(['EXTENDED']);
      }
    }
 ;

// ===================================== SELECT statement =====================================

QuerySpecification
 : SelectStatement OptionalUnions                                   -> $1
 | CommonTableExpression SelectStatement OptionalUnions
 | CommonTableExpression '(' QuerySpecification ')' OptionalUnions  -> $3
 ;

QuerySpecification_EDIT
 : SelectStatement_EDIT OptionalUnions
 | SelectStatement OptionalUnions_EDIT
 | CommonTableExpression '(' QuerySpecification_EDIT ')'
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression SelectStatement_EDIT OptionalUnions
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression SelectStatement OptionalUnions_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression_EDIT
 | CommonTableExpression_EDIT '(' QuerySpecification ')'
 | CommonTableExpression_EDIT SelectStatement OptionalUnions
 ;

SelectStatement
 : 'SELECT' OptionalAllOrDistinct SelectList
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     $$ = { selectList: $3 };
   }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     $$ = { selectList: $3, tableExpression: $4 }
   }
 ;

OptionalUnions
 :
 | Unions
 ;

OptionalUnions_EDIT
 : Unions_EDIT
 ;

Unions
 : UnionClause
 | Unions UnionClause
 ;

Unions_EDIT
 : UnionClause_EDIT
 | Unions UnionClause_EDIT
 | UnionClause_EDIT Unions
 | Unions UnionClause_EDIT Unions
 ;

UnionClause
 : 'UNION' NewStatement OptionalAllOrDistinct SelectStatement
 ;

UnionClause_EDIT
 : 'UNION' NewStatement 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'DISTINCT', 'SELECT']);
   }
 | 'UNION' NewStatement 'CURSOR' SelectStatement
   {
     parser.suggestKeywords(['ALL', 'DISTINCT']);
   }
 | 'UNION' NewStatement OptionalAllOrDistinct SelectStatement_EDIT
 ;

SelectStatement_EDIT
 : 'SELECT' OptionalAllOrDistinct SelectList_EDIT
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     if ($3.cursorAtStart) {
       var keywords = parser.getSelectListKeywords();
       if (!$2) {
         keywords.push({ value: 'ALL', weight: 2 });
         keywords.push({ value: 'DISTINCT', weight: 2 });
       }
       parser.suggestKeywords(keywords);
     } else {
       parser.checkForSelectListKeywords($3);
     }
     if ($3.suggestFunctions) {
       parser.suggestFunctions();
     }
     if ($3.suggestColumns) {
       parser.suggestColumns({ identifierChain: [], source: 'select' });
     }
     if ($3.suggestTables) {
       parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     }
     if ($3.suggestDatabases) {
       parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     }
     if ($3.suggestAggregateFunctions && (!$2 || $2 === 'ALL')) {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR'
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3, true);
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
     parser.suggestColumns({ identifierChain: [], source: 'select' });
     parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression_EDIT
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList_EDIT TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.selectListNoTableSuggest($3, $2);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'select';
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3, true);
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
     parser.suggestColumns({ identifierChain: [], source: 'select' });
     parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR'
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.checkForSelectListKeywords($3);
     var keywords = ['FROM'];
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     parser.suggestTables({ prependFrom: true });
     parser.suggestDatabases({ prependFrom: true, appendDot: true });
   }
 ;

CommonTableExpression
 : 'WITH' WithQueries  -> $2
 ;

CommonTableExpression_EDIT
 : 'WITH' WithQueries_EDIT
 ;

WithQueries
 : WithQuery                   -> [$1]
 | WithQueries ',' WithQuery   -> $1.concat([$3])
 ;

WithQueries_EDIT
 : WithQuery_EDIT
 | WithQueries ',' WithQuery_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | WithQuery_EDIT ',' WithQueries
 | WithQueries ',' WithQuery_EDIT ',' WithQueries
   {
     parser.addCommonTableExpressions($1);
   }
 ;

WithQuery
 : RegularOrBacktickedIdentifier 'AS' '(' TableSubQueryInner ')'
   {
     parser.addCteAliasLocation(@1, $1);
     $4.alias = $1;
     $$ = $4;
   }
 ;

WithQuery_EDIT
 : RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | RegularOrBacktickedIdentifier 'AS' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['SELECT']);
   }
 | RegularOrBacktickedIdentifier 'AS' '(' TableSubQueryInner_EDIT RightParenthesisOrError
 ;

OptionalAllOrDistinct
 :
 | 'ALL'
 | 'DISTINCT'
 ;

TableExpression
 : FromClause OptionalSelectConditions
   {
     parser.addClauseLocation('whereClause', @1, $2.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);
   }
 ;

TableExpression_EDIT
 : FromClause_EDIT OptionalSelectConditions
   {
     parser.addClauseLocation('whereClause', @1, $2.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);
   }
 | FromClause 'CURSOR' OptionalSelectConditions OptionalJoins
   {
     var keywords = [];

     parser.addClauseLocation('whereClause', @1, $3.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);

     if ($1) {
       if (!$1.hasLateralViews && typeof $1.tableReferenceList.hasJoinCondition !== 'undefined' && !$1.tableReferenceList.hasJoinCondition) {
         keywords.push({ value: 'ON', weight: 3 });
       }
       if ($1.suggestKeywords) {
         keywords = parser.createWeightedKeywords($1.suggestKeywords, 3);
       }
       if ($1.tableReferenceList.suggestJoinConditions) {
         parser.suggestJoinConditions($1.tableReferenceList.suggestJoinConditions);
       }
       if ($1.tableReferenceList.suggestJoins) {
         parser.suggestJoins($1.tableReferenceList.suggestJoins);
       }
       if (!$1.hasLateralViews && $1.tableReferenceList.suggestKeywords) {
         keywords = keywords.concat(parser.createWeightedKeywords($1.tableReferenceList.suggestKeywords, 3));
       }

       // Lower the weights for 'TABLESAMPLE' and 'LATERAL VIEW'
       keywords.forEach(function (keyword) {
         if (keyword.value === 'TABLESAMPLE' || keyword.value === 'LATERAL VIEW') {
           keyword.weight = 1.1;
         }
       });

       if (!$1.hasLateralViews && $1.tableReferenceList.types) {
         var veKeywords = parser.getValueExpressionKeywords($1.tableReferenceList);
         keywords = keywords.concat(veKeywords.suggestKeywords);
         if (veKeywords.suggestColRefKeywords) {
           parser.suggestColRefKeywords(veKeywords.suggestColRefKeywords);
           parser.addColRefIfExists($1.tableReferenceList);
         }
       }
     }

     if ($3.empty && $4 && $4.joinType.toUpperCase() === 'JOIN') {
       keywords = keywords.concat(['CROSS', 'FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'LEFT SEMI', 'RIGHT', 'RIGHT OUTER']);
       parser.suggestKeywords(keywords);
       return;
     }

     if ($3.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($3.suggestKeywords, 2));
     }

     if ($3.suggestFilters) {
       parser.suggestFilters($3.suggestFilters);
     }
     if ($3.suggestGroupBys) {
       parser.suggestGroupBys($3.suggestGroupBys);
     }
     if ($3.suggestOrderBys) {
       parser.suggestOrderBys($3.suggestOrderBys);
     }

     if ($3.empty) {
       keywords.push({ value: 'UNION', weight: 2.11 });
     }

     keywords = keywords.concat([
       { value: 'CROSS JOIN', weight: 1 },
       { value: 'FULL JOIN', weight: 1 },
       { value: 'FULL OUTER JOIN', weight: 1 },
       { value: 'INNER JOIN', weight: 1 },
       { value: 'JOIN', weight: 1 },
       { value: 'LEFT JOIN', weight: 1 },
       { value: 'LEFT OUTER JOIN', weight: 1 },
       { value: 'LEFT SEMI JOIN', weight: 1 },
       { value: 'RIGHT JOIN', weight: 1 },
       { value: 'RIGHT OUTER JOIN', weight: 1 }
     ]);
     parser.suggestKeywords(keywords);
  }
 | FromClause OptionalSelectConditions_EDIT OptionalJoins
   {
     // A couple of things are going on here:
     // - If there are no SelectConditions (WHERE, GROUP BY, etc.) we should suggest complete join options
     // - If there's an OptionalJoin at the end, i.e. 'SELECT * FROM foo | JOIN ...' we should suggest
     //   different join types
     // - The FromClause could end with a valueExpression, in which case we should suggest keywords like '='
     //   or 'AND' based on type

     if (!$2) {
       parser.addClauseLocation('whereClause', @1);
       parser.addClauseLocation('limitClause', @1);
       return;
     }
     parser.addClauseLocation('whereClause', @1, $2.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);
     var keywords = [];

     if ($2.suggestColRefKeywords) {
       parser.suggestColRefKeywords($2.suggestColRefKeywords);
       parser.addColRefIfExists($2);
     }

     if ($2.suggestKeywords && $2.suggestKeywords.length) {
       keywords = keywords.concat(parser.createWeightedKeywords($2.suggestKeywords, 2));
     }

     if ($2.cursorAtEnd) {
       keywords.push({ value: 'UNION', weight: 2.11 });
     }
     parser.suggestKeywords(keywords);
   }
 ;

OptionalJoins
 :
 | Joins
 | Joins_INVALID
 ;

FromClause
 : 'FROM' TableReferenceList OptionalLateralViews
   {
     $$ = { tableReferenceList : $2, suggestKeywords: ['LATERAL VIEW'] }
     if ($3) {
       parser.yy.lateralViews = $3.lateralViews;
       $$.hasLateralViews = true;
       if ($3.suggestKeywords) {
         $$.suggestKeywords = $$.suggestKeywords.concat($3.suggestKeywords);
       }
     }
   }
 ;

FromClause_EDIT
 : 'FROM' 'CURSOR'
   {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
   }
 | 'FROM' TableReferenceList_EDIT OptionalLateralViews
   {
     if ($3) {
       parser.yy.lateralViews = $3.lateralViews;
     }
   }
 | 'FROM' TableReferenceList OptionalLateralViews_EDIT
 ;

OptionalSelectConditions
 : OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$1, $2, $3, $4, $5, $6, $6, $7],
       [{ value: 'WHERE', weight: 9 }, { value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true, true, true, true, !$5, true]);

     if (keywords.length > 0) {
       $$ = { suggestKeywords: keywords, empty: !$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 };
     } else {
       $$ = {};
     }

     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($6, @6, $5, @5, $4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = $7 ? @7 : undefined;

     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7) {
       $$.suggestFilters = { prefix: 'WHERE', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7) {
       $$.suggestGroupBys = { prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$5 && !$6 && !$7) {
       $$.suggestOrderBys = { prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause_EDIT OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'where';
     }
   }
 | OptionalWhereClause GroupByClause_EDIT OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'group by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause_EDIT OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'order by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT
 ;

OptionalSelectConditions_EDIT
 : WhereClause 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$3, $4, $5, $6, $7, $7, $8],
       [{ value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true, true, true, !$6, true]);
     if ($1.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($1.suggestKeywords, 1));
     }
     $$ = parser.getValueExpressionKeywords($1, keywords);
     $$.cursorAtEnd = !$3 && !$4 && !$5 && !$6 && !$7 && !$8;
     if ($1.columnReference) {
       $$.columnReference = $1.columnReference;
     }
     if (!$3) {
       parser.suggestGroupBys({ prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     if (!$3 && !$4 && !$5 && !$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $5, @5, $4, @4, $3, @3, $1, @1);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause GroupByClause 'CURSOR' OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$4, $5, $6, $7, $7, $8],
       [{ value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true, true, !$6, true]);
     if ($2.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($2.suggestKeywords, 8));
     }
     if ($2.valueExpression) {
       $$ = parser.getValueExpressionKeywords($2.valueExpression, keywords);
       if ($2.valueExpression.columnReference) {
         $$.columnReference = $2.valueExpression.columnReference;
       }
     } else {
       $$ = { suggestKeywords: keywords };
     }
     $$.cursorAtEnd = !$4 && !$5 && !$6 && !$7 && !$8;
     if (!$4 && !$5 && !$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $5, @5, $4, @4, $2, @2);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause 'CURSOR' OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$5, $6, $7, $7, $8],
       [{ value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true, !$6, true]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$5 && !$6 && !$7 && !$8 };
     if (!$5 && !$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $5, @5, $3, @3);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause 'CURSOR' OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$6, $7, $8],
       [{ value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }],
       [true, true, true]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$6 && !$7 && !$8 };
     if (!$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $4, @4);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause 'CURSOR' OptionalClusterOrDistributeBy OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$7, $8],
       [[{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'LIMIT', weight: 3 }],
       [true, true]);
     if ($5.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($5.suggestKeywords, 5));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$7 && !$8 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $5, @5);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy 'CURSOR' OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$8], [{ value: 'LIMIT', weight: 3 }], [true]);
     if ($6.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($6.suggestKeywords, 4));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$8 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = @6;
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause 'CURSOR'
   {
     $$ = { suggestKeywords: [], cursorAtEnd: true };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($6, @6, $5, @5, $4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = $7 ? @7 : undefined;
   }
 ;

OptionalWhereClause
 :
 | WhereClause
 ;

WhereClause
 : 'WHERE' SearchCondition  -> $2
 ;

WhereClause_EDIT
 : 'WHERE' SearchCondition_EDIT
   {
     if ($2.suggestFilters) {
       parser.suggestFilters({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | 'WHERE' 'CURSOR'
   {
     parser.suggestFunctions();
     parser.suggestColumns();
     parser.suggestKeywords(['EXISTS', 'NOT EXISTS']);
     parser.suggestFilters({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 ;

OptionalGroupByClause
 :
 | GroupByClause
 ;

GroupByClause
 : 'GROUP' 'BY' GroupByColumnList OptionalGroupingSetsCubeOrRollup
   {
     $$ = { valueExpression: $4 ? false : $3 };
     if (!$4) {
       $$.suggestKeywords = ['GROUPING SETS', 'WITH CUBE', 'WITH ROLLUP'];
     }
   }
 ;

GroupByClause_EDIT
 : 'GROUP' 'BY' GroupByColumnList_EDIT OptionalGroupingSetsCubeOrRollup
   {
     parser.suggestSelectListAliases();
   }
 | 'GROUP' 'BY' 'CURSOR' OptionalGroupingSetsCubeOrRollup
   {
     parser.valueExpressionSuggest();
     parser.suggestSelectListAliases();
     parser.suggestGroupBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 | 'GROUP' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
     parser.suggestGroupBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 | 'GROUP' 'BY' GroupByColumnList OptionalGroupingSetsCubeOrRollup_EDIT
 ;

OptionalGroupingSetsCubeOrRollup
 :
 | GroupingSets
 | 'WITH' 'CUBE'
 | 'WITH' 'ROLLUP'
 ;

OptionalGroupingSetsCubeOrRollup_EDIT
 : GroupingSets_EDIT
 | 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['CUBE', 'ROLLUP']);
   }
 ;

GroupingSets
 : 'GROUPING' 'SETS' '(' ColumnGroupingSets ')'
 ;

GroupingSets_EDIT
 : 'GROUPING' 'CURSOR'
   {
     parser.suggestKeywords(['SETS']);
   }
 | 'GROUPING' 'SETS' '(' ColumnGroupingSets_EDIT RightParenthesisOrError
 ;

ColumnGroupingSets
 :
 | ColumnReference
 | ColumnGroupingSets ',' ColumnGroupingSets
 | '(' ColumnGroupingSets ')'
 ;

ColumnGroupingSets_EDIT
 : ColumnGroupingSet_EDIT
 | ColumnGroupingSet_EDIT ',' ColumnGroupingSets
 | ColumnGroupingSets ',' ColumnGroupingSet_EDIT
 | ColumnGroupingSets ',' ColumnGroupingSet_EDIT ',' ColumnGroupingSets
 | '(' ColumnGroupingSets_EDIT RightParenthesisOrError
 ;

ColumnGroupingSet_EDIT
 : AnyCursor
   {
     parser.suggestColumns();
   }
 | ColumnReference_EDIT
 ;

GroupByColumnList
 : ValueExpression
 | GroupByColumnList ',' ValueExpression  -> $3
 ;

GroupByColumnList_EDIT
 : ValueExpression_EDIT
 | 'CURSOR' ValueExpression
   {
     parser.valueExpressionSuggest();
   }
 | 'CURSOR' ',' GroupByColumnList
   {
     parser.valueExpressionSuggest();
   }
 | ValueExpression_EDIT ',' GroupByColumnList
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT ','
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT ',' GroupByColumnList
 ;

GroupByColumnListPartTwo_EDIT
 : ValueExpression_EDIT
 | AnyCursor ValueExpression
   {
     parser.valueExpressionSuggest();
   }
 | AnyCursor
   {
     parser.valueExpressionSuggest();
   }
 ;

OptionalOrderByClause
 :
 | OrderByClause
 ;

OrderByClause
 : 'ORDER' 'BY' OrderByColumnList  -> $3
 ;

OrderByClause_EDIT
 : 'ORDER' 'BY' OrderByColumnList_EDIT
   {
     if ($3.emptyOrderBy) {
       parser.suggestOrderBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | 'ORDER' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
     parser.suggestOrderBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 ;

OrderByColumnList
 : OrderByIdentifier
 | OrderByColumnList ',' OrderByIdentifier  -> $3
 ;

OrderByColumnList_EDIT
 : OrderByIdentifier_EDIT
 | 'CURSOR' OrderByIdentifier
   {
     $$ = { emptyOrderBy: false }
     parser.valueExpressionSuggest();
     parser.suggestAnalyticFunctions();
     parser.suggestSelectListAliases();
   }
 | OrderByColumnList ',' OrderByIdentifier_EDIT                        -> { emptyOrderBy: false }
 | OrderByColumnList ',' OrderByIdentifier_EDIT ','                    -> { emptyOrderBy: false }
 | OrderByColumnList ',' OrderByIdentifier_EDIT ',' OrderByColumnList  -> { emptyOrderBy: false }
 ;

OrderByIdentifier
 : ValueExpression OptionalAscOrDesc OptionalNullsFirstOrLast
   {
     if ($2.suggestKeywords && $3.suggestKeywords) {
       $$ = parser.mergeSuggestKeywords($2, $3);
     } else {
       $$ = parser.mergeSuggestKeywords($3);
     }
   }
 ;

OrderByIdentifier_EDIT
 : ValueExpression_EDIT OptionalAscOrDesc OptionalNullsFirstOrLast
   {
     parser.suggestSelectListAliases();
   }
 | AnyCursor OptionalAscOrDesc OptionalNullsFirstOrLast
   {
     $$ = { emptyOrderBy: true }
     parser.valueExpressionSuggest();
     parser.suggestAnalyticFunctions();
     parser.suggestSelectListAliases();
   }
 | ValueExpression OptionalAscOrDesc NullsFirstOrLast_EDIT
 ;

OptionalAscOrDesc
 :                          -> { suggestKeywords: ['ASC', 'DESC'] };
 | 'ASC'
 | 'DESC'
 ;

OptionalNullsFirstOrLast
 :                          -> { suggestKeywords: ['NULLS FIRST', 'NULLS LAST'] }
 | NullsFirstOrLast
 ;

NullsFirstOrLast
 : 'NULLS' 'FIRST'
 | 'NULLS' 'LAST'
 ;

NullsFirstOrLast_EDIT
 : 'NULLS' 'CURSOR'
   {
     parser.suggestKeywords(['FIRST', 'LAST']);
   }
 ;

OptionalClusterOrDistributeBy
 :
 | ClusterOrDistributeBy
 ;

ClusterOrDistributeBy
 : ClusterByClause
 | DistributeByClause               -> { suggestKeywords: ['SORT BY'] }
 | DistributeByClause SortByClause
 | SortByClause
 ;

ClusterOrDistributeBy_EDIT
 : ClusterByClause_EDIT
 | DistributeByClause_EDIT
 | DistributeByClause SortByClause_EDIT
 | DistributeByClause_EDIT SortByClause
 | SortByClause_EDIT
 ;

ClusterByClause
 : 'CLUSTER' 'BY' ColumnList
 ;

ClusterByClause_EDIT
 : 'CLUSTER' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | 'CLUSTER' 'BY' 'CURSOR'
   {
     parser.suggestColumns();
     parser.suggestSelectListAliases();
   }
 | 'CLUSTER' 'BY' ColumnList_EDIT
   {
     parser.suggestSelectListAliases();
   }
 ;

DistributeByClause
 : 'DISTRIBUTE' 'BY' ColumnList
 ;

DistributeByClause_EDIT
 : 'DISTRIBUTE' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | 'DISTRIBUTE' 'BY' 'CURSOR'
   {
     parser.suggestColumns();
     parser.suggestSelectListAliases();
   }
 | 'DISTRIBUTE' 'BY' ColumnList_EDIT
   {
     parser.suggestSelectListAliases();
   }
 ;

SortByClause
 : 'SORT' 'BY' SortByList  -> $3
 ;

SortByClause_EDIT
 : 'SORT' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | 'SORT' 'BY' SortByList_EDIT
   {
     parser.suggestSelectListAliases();
   }
 ;

SortByList
 : SortByIdentifier
 | SortByList ',' SortByIdentifier  -> $3
 ;

SortByList_EDIT
 : SortByIdentifier_EDIT
 | SortByIdentifier_EDIT ',' SortByList
 | SortByList ',' SortByIdentifier_EDIT
 | SortByList ',' SortByIdentifier_EDIT ',' SortByList
 ;

SortByIdentifier
 : ColumnIdentifier OptionalAscOrDesc
   {
     parser.addColumnLocation($1.location, [ $1.identifier ]);
     $$ = $2;
   }
 ;

SortByIdentifier_EDIT
 : ColumnIdentifier_EDIT OptionalAscOrDesc
 | AnyCursor OptionalAscOrDesc
   {
     parser.suggestColumns();
   }
 ;

OptionalLimitClause
 :
 | LimitClause
 ;

LimitClause
 : 'LIMIT' UnsignedNumericLiteral
 | 'LIMIT' UnsignedNumericLiteral ',' UnsignedNumericLiteral
 | 'LIMIT' 'VARIABLE_REFERENCE'
 | 'LIMIT' 'VARIABLE_REFERENCE' ',' 'VARIABLE_REFERENCE'
 ;

LimitClause_EDIT
 : 'LIMIT' 'CURSOR'
 ;

SearchCondition
 : ValueExpression
 ;

SearchCondition_EDIT
 : ValueExpression_EDIT
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
 | ColumnOrArbitraryFunctionRef             -> { types: ['COLREF'], columnReference: $1.chain }
 | ColumnOrArbitraryFunctionRef ArbitraryFunctionRightPart
   {
     // We need to handle arbitrary UDFs here instead of inside UserDefinedFunction or there will be a conflict
     // with columnReference for functions like: db.udf(foo)
     var fn = $1.chain[$1.chain.length - 1].name.toLowerCase();
     $1.lastLoc.type = 'function';
     $1.lastLoc.function = fn;
     $1.lastLoc.location = {
       first_line: $1.lastLoc.location.first_line,
       last_line: $1.lastLoc.location.last_line,
       first_column: $1.lastLoc.location.first_column,
       last_column: $1.lastLoc.location.last_column - 1
     }
     if ($1.lastLoc !== $1.firstLoc) {
        $1.firstLoc.type = 'database';
     } else {
       delete $1.lastLoc.identifierChain;
     }
     if ($2.expression) {
       $$ = { function: fn, expression: $2.expression, types: parser.findReturnTypes(fn) }
     } else {
       $$ = { function: fn, types: parser.findReturnTypes(fn) }
     }
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart
  {
    parser.addFunctionLocation(@1, $1);
    if ($2.expression) {
      $$ = { function: $1, expression: $2.expression, types: parser.findReturnTypes($1) }
    } else {
      $$ = { function: $1, types: parser.findReturnTypes($1) }
    }
  }
 | UserDefinedFunction
 | 'NULL'                      -> { types: [ 'NULL' ] }
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
 | ColumnOrArbitraryFunctionRef ArbitraryFunctionRightPart_EDIT
   {
     var fn = $1.chain[$1.chain.length - 1].name.toLowerCase();
     $1.lastLoc.type = 'function';
     $1.lastLoc.function = fn;
     $1.lastLoc.location = {
       first_line: $1.lastLoc.location.first_line,
       last_line: $1.lastLoc.location.last_line,
       first_column: $1.lastLoc.location.first_column,
       last_column: $1.lastLoc.location.last_column - 1
     }
     if ($1.lastLoc !== $1.firstLoc) {
        $1.firstLoc.type = 'database';
     } else {
       delete $1.lastLoc.identifierChain;
     }
     if ($2.position) {
       parser.applyArgumentTypesToSuggestions(fn, $2.position);
     }
     $$ = { types: parser.findReturnTypes(fn) };
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.position) {
       parser.applyArgumentTypesToSuggestions($1, $2.position);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 | UserDefinedFunction_EDIT
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
 : UnsignedNumericLiteral  -> { types: [ 'NUMBER' ] }
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
 : UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | '.' UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER' '.' UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 ;

GeneralLiteral
 : SingleQuotedValue
   {
     if (/\$\{[^}]*\}/.test($1)) {
       parser.addVariableLocation(@1, $1);
       $$ = { types: [ 'STRING' ], columnReference: [{ name: $1 }] }
     } else {
       $$ = { types: [ 'STRING' ] }
     }
   }
 | DoubleQuotedValue
   {
     if (/\$\{[^}]*\}/.test($1)) {
       parser.addVariableLocation(@1, $1);
       $$ = { types: [ 'STRING' ], columnReference: [{ name: $1 }] }
     } else {
       $$ = { types: [ 'STRING' ] }
     }
   }
 | TruthValue         -> { types: [ 'BOOLEAN' ] }
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

SelectSpecification
 : ValueExpression OptionalCorrelationName
   {
     if ($2) {
       parser.addColumnAliasLocation($2.location, $2.alias, @1);
       $$ = { valueExpression: $1, alias: $2.alias };
       if (!parser.yy.selectListAliases) {
         parser.yy.selectListAliases = [];
       }
       parser.yy.selectListAliases.push({ name: $2.alias, types: $1.types || ['T'] });
     } else {
       $$ = { valueExpression: $1 }
     }
   }
 | '*'
   {
     parser.addAsteriskLocation(@1, [{ asterisk: true }]);
     $$ = { asterisk: true }
   }
 ;

SelectSpecification_EDIT
 : ValueExpression_EDIT OptionalCorrelationName
   {
     if ($2) {
       parser.addColumnAliasLocation($2.location, $2.alias, @1);
     }
   }

 | AnyCursor 'AS' RegularOrBacktickedIdentifier
   {
     parser.suggestFunctions();
     parser.suggestColumns();
     parser.addColumnAliasLocation(@3, $3, @1);
     $$ = { suggestAggregateFunctions: true };
   }
 | ValueExpression OptionalCorrelationName_EDIT  -> $2
 ;

SelectList
 : SelectSpecification                 -> [ $1 ]
 | SelectList ',' SelectSpecification
   {
     $1.push($3);
   }
 ;

SelectList_EDIT
 : SelectSpecification_EDIT
 | 'CURSOR' SelectList
   {
     $$ = { cursorAtStart : true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | 'CURSOR' ',' SelectList
   {
     $$ = { cursorAtStart : true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | SelectSpecification_EDIT ',' SelectList
 | SelectList 'CURSOR' SelectList
   {
     parser.checkForSelectListKeywords($1);
   }
 | SelectList 'CURSOR' ',' SelectList
   {
     parser.checkForSelectListKeywords($1);
   }
 | SelectList ',' AnyCursor
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestTables: true, suggestDatabases: true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | SelectList ',' SelectSpecification_EDIT                 -> $3
 | SelectList ',' AnyCursor SelectList
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' AnyCursor ','
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' SelectSpecification_EDIT ','             -> $3
 | SelectList ',' AnyCursor ',' SelectList
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' SelectSpecification_EDIT ',' SelectList  -> $3
 ;

TableReferenceList
 : TableReference
 | TableReferenceList ',' TableReference  -> $3
 ;

TableReferenceList_EDIT
 : TableReference_EDIT
 | TableReference_EDIT ',' TableReference
 | TableReferenceList ',' TableReference_EDIT
 | TableReferenceList ',' TableReference_EDIT ',' TableReferenceList
 | TableReferenceList ',' AnyCursor
   {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
   }
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

Joins
 : JoinType TablePrimary OptionalJoinCondition
   {
     if ($3 && $3.valueExpression) {
       $$ = $3.valueExpression;
     } else {
       $$ = {};
     }
     $$.joinType = $1;
     if ($3.noJoinCondition) {
       $$.suggestJoinConditions = { prependOn: true, tablePrimaries: parser.yy.latestTablePrimaries.concat() }
     }
     if ($3.suggestKeywords) {
       $$.suggestKeywords = $3.suggestKeywords;
     }
     if (parser.yy.latestTablePrimaries.length > 0) {
        parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
     }
   }
 | Joins JoinType TablePrimary OptionalJoinCondition
   {
     if ($4 && $4.valueExpression) {
       $$ = $4.valueExpression;
     } else {
       $$ = {};
     }
     $$.joinType = $1;
     if ($4.noJoinCondition) {
       $$.suggestJoinConditions = { prependOn: true, tablePrimaries: parser.yy.latestTablePrimaries.concat() }
     }
     if ($4.suggestKeywords) {
       $$.suggestKeywords = $4.suggestKeywords;
     }
     if (parser.yy.latestTablePrimaries.length > 0) {
       parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
     }
   }
 ;

Joins_INVALID
 : JoinType                                           -> { joinType: $1 }
 | JoinType Joins                                     -> { joinType: $1 }
 ;

Join_EDIT
 : JoinType_EDIT TablePrimary OptionalJoinCondition
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType_EDIT
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType TablePrimary_EDIT OptionalJoinCondition
 | JoinType TablePrimary JoinCondition_EDIT
 | JoinType 'CURSOR' OptionalJoinCondition
   {
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
         parser.suggestJoins({
           prependJoin: false,
           joinType: $1,
           tables: tables
         })
       }
     }
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 ;

Joins_EDIT
 : Join_EDIT
 | Join_EDIT Joins
 | Joins Join_EDIT
 | Joins Join_EDIT Joins
 ;

JoinType
 : 'CROSS' 'JOIN'                 -> 'CROSS JOIN'
 | 'FULL' 'JOIN'                  -> 'FULL JOIN'
 | 'FULL' 'OUTER' 'JOIN'          -> 'FULL OUTER JOIN'
 | 'INNER' 'JOIN'                 -> 'INNER JOIN'
 | 'JOIN'                         -> 'JOIN'
 | 'LEFT' 'INNER' 'JOIN'          -> 'LEFT INNER JOIN'
 | 'LEFT' 'JOIN'                  -> 'LEFT JOIN'
 | 'LEFT' 'OUTER' 'JOIN'          -> 'LEFT OUTER JOIN'
 | 'LEFT' 'SEMI' 'JOIN'           -> 'LEFT SEMI JOIN'
 | 'OUTER' 'JOIN'                 -> 'OUTER JOIN'
 | 'RIGHT' 'INNER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'JOIN'                 -> 'RIGHT JOIN'
 | 'RIGHT' 'OUTER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'SEMI' 'JOIN'          -> 'RIGHT SEMI JOIN'
 | 'SEMI' 'JOIN'                  -> 'SEMI JOIN'
 ;

JoinType_EDIT
 : 'CROSS' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['OUTER'] }
 | 'FULL' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'INNER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['OUTER', 'SEMI'] }
 | 'LEFT' 'INNER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'SEMI' 'CURSOR'           -> { suggestKeywords: ['JOIN'] }
 | 'OUTER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'CURSOR' 'JOIN'          -> { suggestKeywords: ['OUTER'] }
 | 'RIGHT' 'INNER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'OUTER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'SEMI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'SEMI' 'CURSOR'                  -> { suggestKeywords: ['JOIN'] }
 ;

OptionalJoinCondition
 :                                       -> { noJoinCondition: true, suggestKeywords: ['ON'] }
 | 'ON' ValueExpression                  -> { valueExpression: $2 }
 ;

UsingColList
 : RegularOrBacktickedIdentifier
 | UsingColList ',' RegularOrBacktickedIdentifier
 ;

JoinCondition_EDIT
 : 'ON' ValueExpression_EDIT
 | 'ON' 'CURSOR'
   {
     parser.valueExpressionSuggest();
     parser.suggestJoinConditions({ prependOn: false });
   }
 ;

TablePrimary
 : TableOrQueryName OptionalTableSample OptionalCorrelationName
   {
     $$ = {
       primary: $1
     }
     if ($1.identifierChain) {
       if ($3) {
         $1.alias = $3.alias
         parser.addTableAliasLocation($3.location, $3.alias, $1.identifierChain);
       }
       parser.addTablePrimary($1);
     }
     var keywords = [];
     // Right-to-left for cursor after TablePrimary
     keywords = parser.getKeywordsForOptionalsLR([$3, $2], [{ value: 'AS', weight: 2 }, { value: 'TABLESAMPLE', weight: 3 }], [true, true]);
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
     keywords = parser.getKeywordsForOptionalsLR([$2], [{ value: 'AS', weight: 2 }], [true]);
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalTableSample OptionalCorrelationName
   {
     if ($3) {
       parser.addTableAliasLocation($3.location, $3.alias, $1.identifierChain);
     }
   }
 | TableOrQueryName OptionalTableSample_EDIT OptionalCorrelationName
   {
     if ($3) {
       $1.alias = $3.alias;
       parser.addTableAliasLocation($3.location, $3.alias, $1.identifierChain);
     }
     parser.addTablePrimary($1);
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

OptionalTableSample
 :
 | 'TABLESAMPLE' '(' 'BUCKET' 'UNSIGNED_INTEGER' 'OUT' 'OF' 'UNSIGNED_INTEGER' OptionalOnColumn ')'
 | 'TABLESAMPLE' '(' ExactNumericLiteral 'PERCENT' ')'
 | 'TABLESAMPLE' '(' ExactNumericLiteral 'ROWS' ')'
 | 'TABLESAMPLE' '(' 'REGULAR_IDENTIFIER' ')'
 ;

OptionalTableSample_EDIT
 : 'TABLESAMPLE' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['BUCKET']);
   }
 | 'TABLESAMPLE' '(' 'BUCKET' 'UNSIGNED_INTEGER' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['OUT OF']);
   }
 | 'TABLESAMPLE' '(' 'BUCKET' 'UNSIGNED_INTEGER' 'OUT' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['OF']);
   }
 | 'TABLESAMPLE' '(' 'BUCKET' 'UNSIGNED_INTEGER' 'OUT' 'OF' 'UNSIGNED_INTEGER' OptionalOnColumn 'CURSOR' RightParenthesisOrError
   {
     if (!$8) {
       parser.suggestKeywords(['ON']);
     }
   }
 | 'TABLESAMPLE' '(' 'BUCKET' 'UNSIGNED_INTEGER' 'OUT' 'OF' 'UNSIGNED_INTEGER' OptionalOnColumn_EDIT RightParenthesisOrError
 | 'TABLESAMPLE' '(' ExactNumericLiteral 'CURSOR' RightParenthesisOrError
   {
     if ($3.indexOf('.') === -1 ) {
       parser.suggestKeywords(['PERCENT', 'ROWS']);
     } else {
       parser.suggestKeywords(['PERCENT']);
     }
   }
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

OptionalLateralViews
 :
 | OptionalLateralViews LateralView
   {
     if ($1 && $2.lateralView) {
       $1.lateralViews.push($2.lateralView);
       $$ = $1;
     } else if ($2.lateralView) {
       $$ = { lateralViews: [ $2.lateralView ] };
     }
     if ($2.suggestKeywords) {
       $$.suggestKeywords = $2.suggestKeywords
     }
   }
 ;

OptionalLateralViews_EDIT
 : OptionalLateralViews LateralView_EDIT OptionalLateralViews
 ;

UserDefinedFunction
 : AggregateFunction OptionalOverClause
   {
     if (!$2) {
       $1.suggestKeywords = ['OVER'];
     }
   }
 | AnalyticFunction OverClause
 | CastFunction
 | ExtractFunction
 ;

UserDefinedFunction_EDIT
 : AggregateFunction_EDIT
 | AggregateFunction OptionalOverClause_EDIT
 | AnalyticFunction_EDIT
 | AnalyticFunction_EDIT OverClause
 | AnalyticFunction 'CURSOR'
   {
     parser.suggestKeywords(['OVER']);
   }
 | AnalyticFunction OverClause_EDIT
 | CastFunction_EDIT
 | ExtractFunction_EDIT
 ;

ArbitraryFunction
 : RegularIdentifier ArbitraryFunctionRightPart
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.expression) {
       $$ = { function: $1, expression: $2.expression, types: parser.findReturnTypes($1) }
     } else {
       $$ = { function: $1, types: parser.findReturnTypes($1) }
     }
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.expression) {
       $$ = { function: $1, expression: $2.expression, types: parser.findReturnTypes($1) }
     } else {
       $$ = { function: $1, types: parser.findReturnTypes($1) }
     }
   }
 ;

ArbitraryFunction_EDIT
 : RegularIdentifier ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.position) {
       parser.applyArgumentTypesToSuggestions($1, $2.position);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.position) {
       parser.applyArgumentTypesToSuggestions($1, $2.position);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 ;

ArbitraryFunctionName
 : 'ARRAY'
 | 'BINARY'
 | 'IF'
 | 'MAP'
 | 'TRUNCATE'
 ;

ArbitraryFunctionRightPart
 : '(' ')'
 | '(' ValueExpressionList ')'  -> { expression: $2 }
 ;

ArbitraryFunctionRightPart_EDIT
 : '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { position: 1 }
   }
 | '(' ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3);
   }
 | '(' ValueExpressionList_EDIT RightParenthesisOrError      -> $2
 ;

AggregateFunction
 : CountFunction
 | SumFunction
 | OtherAggregateFunction
 ;

AggregateFunction_EDIT
 : CountFunction_EDIT
 | SumFunction_EDIT
 | OtherAggregateFunction_EDIT
 ;

AnalyticFunction
 : 'ANALYTIC' '(' ')'                      -> { types: parser.findReturnTypes($1) }
 | 'ANALYTIC' '(' ValueExpressionList ')'  -> { function: $1, expression: $2, types: parser.findReturnTypes($1) }
 ;

AnalyticFunction_EDIT
 : 'ANALYTIC' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | 'ANALYTIC' '(' ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | 'ANALYTIC' '(' ValueExpressionList_EDIT RightParenthesisOrError
   {
     parser.applyArgumentTypesToSuggestions($1, $3.position);
     $$ = { types: parser.findReturnTypes($1) };
   }
 ;

OptionalOverClause
 :
 | OverClause
 ;

OptionalOverClause_EDIT
 : OverClause_EDIT
 ;

OverClause
 : 'OVER' RegularOrBacktickedIdentifier
 | 'OVER' WindowExpression
 ;

OverClause_EDIT
 : 'OVER' WindowExpression_EDIT
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
     parser.suggestKeywords(['BETWEEN', 'UNBOUNDED']);
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
   {
     if (!$4) {
       parser.suggestKeywords(['PRECEDING']);
     }
   }
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

OptionalHavingClause
 :
 | HavingClause
 ;

HavingClause
 : 'HAVING' ValueExpression
 ;

HavingClause_EDIT
 : 'HAVING' 'CURSOR'
   {
     parser.valueExpressionSuggest();
     parser.suggestAggregateFunctions();
     parser.suggestSelectListAliases(true);
   }
 | 'HAVING' ValueExpression_EDIT
   {
     parser.suggestAggregateFunctions();
     parser.suggestSelectListAliases(true);
   }
 ;

OptionalWindowClause
 :
 | WindowClause
 ;

WindowClause
 : 'WINDOW' RegularOrBacktickedIdentifier 'AS' WindowExpression
 ;

WindowClause_EDIT
 : 'WINDOW' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'WINDOW' RegularOrBacktickedIdentifier 'AS' WindowExpression_EDIT
 ;

CastFunction
 : 'CAST' '(' ValueExpression 'AS' PrimitiveType ')'  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ')'                                      -> { types: [ 'T' ] }
 ;

CastFunction_EDIT
 : 'CAST' '(' AnyCursor 'AS' PrimitiveType RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' AnyCursor 'AS' RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression_EDIT 'AS' PrimitiveType RightParenthesisOrError  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ValueExpression_EDIT 'AS' RightParenthesisOrError                -> { types: [ 'T' ] }
 | 'CAST' '(' ValueExpression_EDIT RightParenthesisOrError                      -> { types: [ 'T' ] }
 | 'CAST' '(' ValueExpression 'CURSOR' PrimitiveType RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3, [{ value: 'AS', weight: 2 }]);
     $$ =  { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3, [{ value: 'AS', weight: 2 }]);
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression 'AS' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' 'AS' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 ;

CountFunction
 : 'COUNT' '(' '*' ')'                                        -> { types: parser.findReturnTypes($1) }
 | 'COUNT' '(' ')'                                            -> { types: parser.findReturnTypes($1) }
 | 'COUNT' '(' OptionalAllOrDistinct ValueExpressionList ')'  -> { types: parser.findReturnTypes($1) }
 ;

CountFunction_EDIT
 : 'COUNT' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     var keywords = parser.getSelectListKeywords();
     if (!$3) {
       keywords.push('DISTINCT');
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
     }
     parser.suggestKeywords(keywords);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | 'COUNT' '(' OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | 'COUNT' '(' OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart) {
       var keywords = parser.getSelectListKeywords();
       if (!$3) {
         keywords.push('DISTINCT');
       }
       parser.suggestKeywords(keywords);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 ;

ExtractFunction
 : 'EXTRACT' '(' DateField 'FROM' ValueExpression ')'  -> { types: ['INT', 'INTEGER'] }
 ;

ExtractFunction_EDIT
 : 'EXTRACT' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR']);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['FROM']);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'FROM' 'CURSOR' RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'FROM' ValueExpression_EDIT RightParenthesisOrError  -> { types: ['INT', 'INTEGER'] }
 | 'EXTRACT' '(' AnyCursor 'FROM' ValueExpression RightParenthesisOrError
   {
      parser.suggestKeywords(['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR']);
      $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'CURSOR' ValueExpression RightParenthesisOrError
   {
     parser.suggestKeywords(['FROM']);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 ;

DateField
 : 'DAY'
 | 'DAYOFWEEK'
 | 'HOUR'
 | 'MINUTE'
 | 'MONTH'
 | 'QUARTER'
 | 'SECOND'
 | 'WEEK'
 | 'YEAR'
 ;

OtherAggregateFunction
 : OtherAggregateFunction_Type '(' OptionalAllOrDistinct ')'                      -> { types: parser.findReturnTypes($1) }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ValueExpressionList ')'  -> { types: parser.findReturnTypes($1) }
 ;

OtherAggregateFunction_EDIT
 : OtherAggregateFunction_Type '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     var keywords = parser.getSelectListKeywords(true);
     if (!$3) {
       if ($1.toLowerCase() === 'group_concat') {
         keywords.push('ALL');
       } else {
         keywords.push('DISTINCT');
       }
     }
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart) {
       var keywords = parser.getSelectListKeywords(true);
       if (!$3) {
         if ($1.toLowerCase() === 'group_concat') {
           keywords.push('ALL');
         } else {
           keywords.push('DISTINCT');
         }
       }
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
       parser.suggestKeywords(keywords);
     }
     if (parser.yy.result.suggestFunctions && !parser.yy.result.suggestFunctions.types) {
       parser.applyArgumentTypesToSuggestions($1, $4.position);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 ;

OtherAggregateFunction_Type
 : 'AVG'
 | 'COLLECT_LIST'
 | 'COLLECT_SET'
 | 'CORR'
 | 'COVAR_POP'
 | 'COVAR_SAMP'
 | 'HISTOGRAM_NUMERIC'
 | 'MAX'
 | 'MIN'
 | 'NTILE'
 | 'PERCENTILE'
 | 'PERCENTILE_APPROX'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'VAR_POP'
 | 'VAR_SAMP'
 | 'VARIANCE'
 ;

FromOrComma
 : 'FROM'
 | ','
 ;

SumFunction
 : 'SUM' '(' OptionalAllOrDistinct ValueExpression ')'  -> { types: parser.findReturnTypes($1) }
 | 'SUM' '(' ')'                                        -> { types: parser.findReturnTypes($1) }
 ;

SumFunction_EDIT
 : 'SUM' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyArgumentTypesToSuggestions($1, 1);
     var keywords = parser.getSelectListKeywords(true);
     if (!$3) {
       keywords.push('DISTINCT');
     }
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | 'SUM' '(' OptionalAllOrDistinct ValueExpression 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | 'SUM' '(' OptionalAllOrDistinct ValueExpression_EDIT RightParenthesisOrError
   {
     if (parser.yy.result.suggestFunctions && ! parser.yy.result.suggestFunctions.types) {
       parser.applyArgumentTypesToSuggestions($1, 1);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 ;

LateralView
 : 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier LateralViewColumnAliases  -> { lateralView: { udtf: $4, tableAlias: $5, columnAliases: $6 }}
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier
   {
     if ($4.function.toLowerCase() === 'explode') {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: ['key', 'value'] }, suggestKeywords: ['AS'] };
     } else if ($4.function.toLowerCase() === 'posexplode') {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: ['pos', 'val'] }, suggestKeywords: ['AS'] };
     } else {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: [] }, suggestKeywords: ['AS'] };
     }
   }
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction LateralViewColumnAliases                                -> { lateralView: { udtf: $4, columnAliases: $5 }}
 ;

LateralView_EDIT
 : 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction_EDIT
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction_EDIT RegularOrBacktickedIdentifier
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction_EDIT RegularOrBacktickedIdentifier LateralViewColumnAliases
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier LateralViewColumnAliases_EDIT
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction PartialBacktickedOrCursor
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction PartialBacktickedOrCursor LateralViewColumnAliases
 | 'LATERAL' 'VIEW' OptionalOuter 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords([{ value: 'OUTER', weight: 2 }, { value: 'explode', weight: 1 }, { value: 'posexplode', weight: 1 }]);
     } else {
       parser.suggestKeywords(['explode', 'posexplode']);
     }
   }
 | 'LATERAL' 'CURSOR'
   {
     parser.suggestKeywords(['VIEW']);
   }
 ;

OptionalOuter
 :
 | 'OUTER'
 ;

LateralViewColumnAliases
 : 'AS' RegularOrBacktickedIdentifier                                    -> [ $2 ]
 | 'AS' RegularOrBacktickedIdentifier ',' RegularOrBacktickedIdentifier  -> [ $2, $4 ]
 ;

LateralViewColumnAliases_EDIT
 : 'AS' PartialBacktickedOrCursor
 | 'AS' RegularOrBacktickedIdentifier ',' PartialBacktickedOrAnyCursor
 ;
