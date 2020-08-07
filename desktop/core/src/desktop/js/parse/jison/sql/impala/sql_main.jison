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
 | ExplainClause DataDefinition
 | ExplainClause DataManipulation
 | ExplainClause QuerySpecification
 ;

SqlStatement_EDIT
 : AnyCursor
   {
     parser.suggestDdlAndDmlKeywords(['EXPLAIN']);
   }
 | CommonTableExpression 'CURSOR'
   {
     parser.suggestKeywords(['INSERT', 'SELECT']);
   }
 | ExplainClause_EDIT
 | DataDefinition_EDIT
 | DataManipulation_EDIT
 | QuerySpecification_EDIT
 | SetSpecification_EDIT
 | ExplainClause DataDefinition_EDIT
 | ExplainClause DataManipulation_EDIT
 | ExplainClause QuerySpecification_EDIT
 | ExplainClause_EDIT DataDefinition
 | ExplainClause_EDIT DataManipulation
 | ExplainClause_EDIT QuerySpecification
 ;

NonReservedKeyword
 : 'DEFAULT'
 | 'KEY'
 | 'OPTION'
 | 'OWNER'
 | 'SERVER'
 | 'STRUCT'
 | 'URI'
 ;

RegularIdentifier
 : 'REGULAR_IDENTIFIER'
 | 'VARIABLE_REFERENCE'
 | NonReservedKeyword
 ;

ExplainClause
 : 'EXPLAIN'
 ;

ExplainClause_EDIT
 : 'EXPLAIN' 'CURSOR'
   {
     parser.suggestDdlAndDmlKeywords();
   }
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
 | '...'
 | '<'
 | '='
 | '>'
 | '['
 | ']'
 | 'AGGREGATE'
 | 'ALL'
 | 'ALLOCATE'
 | 'ANALYTIC'
 | 'AND'
 | 'ANTI'
 | 'ANY'
 | 'APPX_MEDIAN'
 | 'ARE'
 | 'ARITHMETIC_OPERATOR'
 | 'ARRAY'
 | 'ARRAY_AGG'
 | 'ARRAY_MAX_CARDINALITY'
 | 'AS'
 | 'ASC'
 | 'ASENSITIVE'
 | 'ASYMMETRIC'
 | 'AT'
 | 'ATOMIC'
 | 'AUTHORIZATION'
 | 'AVG'
 | 'AVRO'
 | 'BACKTICK'
 | 'BEGIN_FRAME'
 | 'BEGIN_PARTITION'
 | 'BETWEEN'
 | 'BIGINT'
 | 'BLOB'
 | 'BLOCK_SIZE'
 | 'BOOLEAN'
 | 'BOTH'
 | 'BROADCAST'
 | 'BY'
 | 'CACHED'
 | 'CALLED'
 | 'CARDINALITY'
 | 'CASCADE'
 | 'CASCADED'
 | 'CASE'
 | 'CAST'
 | 'CHAR'
 | 'CHARACTER'
 | 'CLOB'
 | 'CLOSE_FN'
 | 'COLLATE'
 | 'COLLECT'
 | 'COLUMN'
 | 'COMMIT'
 | 'COMPARISON_OPERATOR'
 | 'CONDITION'
 | 'CONNECT'
 | 'CONSTRAINT'
 | 'CONTAINS'
 | 'CONVERT'
 | 'COPY'
 | 'CORR'
 | 'CORRESPONDING'
 | 'COUNT'
 | 'COVAR_POP'
 | 'COVAR_SAMP'
 | 'CROSS'
 | 'CUBE'
 | 'CURRENT'
 | 'CURRENT_DATE'
 | 'CURRENT_DEFAULT_TRANSFORM_GROUP'
 | 'CURRENT_PATH'
 | 'CURRENT_ROLE'
 | 'CURRENT_ROW'
 | 'CURRENT_SCHEMA'
 | 'CURRENT_TIME'
 | 'CURRENT_TRANSFORM_GROUP_FOR_TYPE'
 | 'CYCLE'
 | 'DATA'
 | 'DATABASE'
 | 'DATABASES'
 | 'DEALLOCATE'
 | 'DEC'
 | 'DECFLOAT'
 | 'DECIMAL'
 | 'DECLARE'
 | 'DEFINE'
 | 'DELETE'
 | 'DELIMITED'
 | 'DEREF'
 | 'DESC'
 | 'DETERMINISTIC'
 | 'DISCONNECT'
 | 'DISTINCT'
 | 'DOUBLE'
 | 'DOUBLE_QUOTE'
 | 'DYNAMIC'
 | 'EACH'
 | 'ELEMENT'
 | 'ELSE'
 | 'EMPTY'
 | 'END'
 | 'END_FRAME'
 | 'END_PARTITION'
 | 'EQUALS'
 | 'ESCAPE'
 | 'ESCAPED'
 | 'EVERY'
 | 'EXCEPT'
 | 'EXEC'
 | 'EXECUTE'
 | 'EXISTS'
 | 'EXTENDED'
 | 'EXTERNAL'
 | 'EXTRACT'
 | 'FALSE'
 | 'FETCH'
 | 'FIELDS'
 | 'FILES'
 | 'FILTER'
 | 'FINALIZE_FN'
 | 'FIRST'
 | 'FLOAT'
 | 'FOLLOWING'
 | 'FOR'
 | 'FOREIGN'
 | 'FORMAT'
 | 'FORMATTED'
 | 'FRAME_ROW'
 | 'FREE'
 | 'FROM'
 | 'FULL'
 | 'FUNCTION'
 | 'FUNCTIONS'
 | 'FUSION'
 | 'GET'
 | 'GLOBAL'
 | 'GRANT'
 | 'GROUP'
 | 'GROUP_CONCAT'
 | 'GROUPING'
 | 'GROUPS'
 | 'HASH'
 | 'HAVING'
 | 'HDFS_START_QUOTE'
 | 'HOLD'
 | 'IF'
 | 'IGNORE'
 | 'ILIKE'
 | 'IN'
 | 'INCREMENTAL'
 | 'INDICATOR'
 | 'INIT_FN'
 | 'INITIAL'
 | 'INNER'
 | 'INOUT'
 | 'INPATH'
 | 'INSENSITIVE'
 | 'INT'
 | 'INTEGER'
 | 'INTERMEDIATE'
 | 'INTERSECT'
 | 'INTERSECTION'
 | 'INTERVAL'
 | 'INTO'
 | 'IREGEXP'
 | 'IS'
 | 'JOIN'
 | 'JSON_ARRAY'
 | 'JSON_ARRAYAGG'
 | 'JSON_EXISTS'
 | 'JSON_OBJECT'
 | 'JSON_OBJECTAGG'
 | 'JSON_QUERY'
 | 'JSON_TABLE'
 | 'JSON_TABLE_PRIMITIVE'
 | 'JSON_VALUE'
 | 'KEY'
 | 'KUDU'
 | 'LARGE'
 | 'LAST'
 | 'LATERAL'
 | 'LEADING'
 | 'LEFT'
 | 'LIKE'
 | 'LIKE_REGEX'
 | 'LIMIT'
 | 'LINES'
 | 'LISTAGG'
 | 'LOCAL'
 | 'LOCALTIMESTAMP'
 | 'LOCATION'
 | 'MAP'
 | 'MATCH'
 | 'MATCH_NUMBER'
 | 'MATCH_RECOGNIZE'
 | 'MATCHES'
 | 'MAX'
 | 'MERGE'
 | 'MERGE_FN'
 | 'METHOD'
 | 'MIN'
 | 'MODIFIES'
 | 'MULTISET'
 | 'NATIONAL'
 | 'NATURAL'
 | 'NCHAR'
 | 'NCLOB'
 | 'NDV'
 | 'NO'
 | 'NONE'
 | 'NORMALIZE'
 | 'NOSHUFFLE'
 | 'NOT'
 | 'NTH_VALUE'
 | 'NULL'
 | 'NULLS'
 | 'NUMERIC'
 | 'OCCURRENCES_REGEX'
 | 'OCTET_LENGTH'
 | 'OF'
 | 'OMIT'
 | 'ON'
 | 'ONE'
 | 'ONLY'
 | 'OPTION'
 | 'OR'
 | 'ORDER'
 | 'OUT'
 | 'OUTER'
 | 'OVER'
 | 'OVERLAPS'
 | 'OVERLAY'
 | 'OWNER'
 | 'PARQUET'
 | 'PARTITION'
 | 'PARTITIONED'
 | 'PARTITIONS'
 | 'PATTERN'
 | 'PER'
 | 'PERCENT'
 | 'PERCENTILE_CONT'
 | 'PERCENTILE_DISC'
 | 'PORTION'
 | 'POSITION'
 | 'POSITION_REGEX'
 | 'PRECEDES'
 | 'PRECEDING'
 | 'PREPARE'
 | 'PREPARE_FN'
 | 'PRIMARY'
 | 'PROCEDURE'
 | 'PTF'
 | 'PURGE'
 | 'RANGE'
 | 'RCFILE'
 | 'READS'
 | 'REAL'
 | 'RECOVER'
 | 'RECURSIVE'
 | 'REF'
 | 'REFERENCES'
 | 'REFERENCING'
 | 'REGEXP'
 | 'REGR_AVGX'
 | 'REGR_AVGY'
 | 'REGR_COUNT'
 | 'REGR_INTERCEPT'
 | 'REGR_R2REGR_SLOPE'
 | 'REGR_SXX'
 | 'REGR_SXY'
 | 'REGR_SYY'
 | 'REGULAR_IDENTIFIER'
 | 'RELEASE'
 | 'REPEATABLE'
 | 'REPLICATION'
 | 'RESTRICT'
 | 'RETURNS'
 | 'RIGHT'
 | 'RLIKE'
 | 'ROLE'
 | 'ROLES'
 | 'ROLLBACK'
 | 'ROLLUP'
 | 'ROW'
 | 'ROWS'
 | 'RUNNING'
 | 'SAVEPOINT'
 | 'SCHEMA'
 | 'SCHEMAS'
 | 'SCOPE'
 | 'SCROLL'
 | 'SEARCH'
 | 'SEEK'
 | 'SEMI'
 | 'SENSITIVE'
 | 'SEQUENCEFILE'
 | 'SERDEPROPERTIES'
 | 'SERIALIZE_FN'
 | 'SERVER'
 | 'SET'
 | 'SHUFFLE'
 | 'SIMILAR'
 | 'SINGLE_QUOTE'
 | 'SKIP'
 | 'SMALLINT'
 | 'SOME'
 | 'SORT'
 | 'SPECIFIC'
 | 'SPECIFICTYPE'
 | 'SQLEXCEPTION'
 | 'SQLSTATE'
 | 'SQLWARNING'
 | 'STATIC'
 | 'STATS'
 | 'STDDEV'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'STORED'
 | 'STRAIGHT_JOIN'
 | 'STRING'
 | 'STRUCT'
 | 'SUBMULTISET'
 | 'SUBSET'
 | 'SUBSTRING_REGEX'
 | 'SUCCEEDS'
 | 'SUM'
 | 'SYMBOL'
 | 'SYMMETRIC'
 | 'SYSTEM_TIME'
 | 'SYSTEM_USER'
 | 'TABLE'
 | 'TABLES'
 | 'TABLESAMPLE'
 | 'TBLPROPERTIES'
 | 'TERMINATED'
 | 'TEXTFILE'
 | 'THEN'
 | 'TIMESTAMP'
 | 'TIMEZONE_HOUR'
 | 'TIMEZONE_MINUTE'
 | 'TINYINT'
 | 'TRAILING'
 | 'TRANSLATE_REGEX'
 | 'TRANSLATION'
 | 'TREAT'
 | 'TRIGGER'
 | 'TRIM_ARRAY'
 | 'TRUE'
 | 'UESCAPE'
 | 'UNION'
 | 'UNIQUE'
 | 'UNNEST'
 | 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER_E'
 | 'UPDATE_FN'
 | 'URI'
 | 'USER'
 | 'USING'
 | 'VALUE_OF'
 | 'VALUES'
 | 'VAR_POP'
 | 'VAR_SAMP'
 | 'VARBINARY'
 | 'VARCHAR'
 | 'VARIABLE_REFERENCE'
 | 'VARIANCE'
 | 'VARIANCE_POP'
 | 'VARIANCE_SAMP'
 | 'VARYING'
 | 'VERSIONING'
 | 'WHEN'
 | 'WHENEVER'
 | 'WHERE'
 | 'WIDTH_BUCKET'
 | 'WINDOW'
 | 'WITHIN'
 | 'WITHOUT'
 | '~'
 ;

DataDefinition
 : DescribeStatement
 ;

DataDefinition_EDIT
 : DescribeStatement_EDIT
 ;

// ===================================== Commonly used constructs =====================================

AggregateOrAnalytic
 : 'AGGREGATE'
 | 'ANALYTIC'
 ;

Commas
 : ','
 | Commas ','
 ;

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

DatabaseOrSchema
 : 'DATABASE'
 | 'SCHEMA'
 ;

FromOrIn
 : 'FROM'
 | 'IN'
 ;

DatabasesOrSchemas
 : 'DATABASES'
 | 'SCHEMAS'
 ;

GroupRoleOrUser
 : 'GROUP'
 | 'ROLE'
 | 'USER'
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

OptionalAggregateOrAnalytic
 :
 | AggregateOrAnalytic
 ;

OptionalExternal
 :
 | 'EXTERNAL'
 ;

OptionalExtendedOrFormatted
 :
 | 'EXTENDED'
 | 'FORMATTED'
 ;

OptionalFromDatabase
 :
 | FromOrIn DatabaseIdentifier
 ;

OptionalFromDatabase_EDIT
 : FromOrIn DatabaseIdentifier_EDIT
 ;

OptionalCascadeOrRestrict
 :
 | 'CASCADE'
 | 'RESTRICT'
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
 | RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier FieldsList
   {
     // This is a special case for expression like "SELECT | FROM db.table.col"
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ].concat($4) };
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
     // You can have statements like 'SELECT ... FROM testTable t, t.|'
     parser.suggestTablesOrColumns($1);
   }
 | RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier FieldsList_EDIT
   {
     // TODO: switch to suggestColumns, it's currently handled in sqlAutocompleter2.js
     // Issue is that suggestColumns is deleted if no tables are defined and this is
     // only cases like "SELECT | FROM db.table.col"
     parser.suggestTables({ identifierChain: [{ name: $1 }, { name: $3 }].concat($4) });
   }
 ;

FieldsList
 : Field               -> [$1]
 | FieldsList Field
   {
     $1.push($2);
   }
 ;

FieldsList_EDIT
 : Field_EDIT                            -> []
 | FieldsList Field_EDIT               -> $1
 | FieldsList Field_EDIT FieldsList  -> $1
 | Field_EDIT FieldsList               -> []
 ;

Field
 : '.' RegularOrBacktickedIdentifier  -> { name: $2 }
 ;

Field_EDIT
 : '.' PartialBacktickedOrPartialCursor
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
 | ColumnIdentifier
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

OptionalCachedInOrUncached
 :
 | CachedIn OptionalWithReplication
   {
     if (!$2) {
       $$ = { suggestKeywords: ['WITH REPLICATION ='] };
     }
   }
 | 'UNCACHED'
 ;

OptionalCachedIn
 :
 | CachedIn OptionalWithReplication
   {
     if (!$2) {
       $$ = { suggestKeywords: ['WITH REPLICATION ='] };
     }
   }
 ;

CachedIn
 : 'CACHED' 'IN' QuotedValue
 ;

CachedIn_EDIT
 : 'CACHED' 'CURSOR'
   {
     parser.suggestKeywords(['IN']);
   }
 ;

OptionalWithReplication
 :
 | WithReplication
 ;

WithReplication
 : 'WITH' 'REPLICATION' '=' SignedInteger
 ;

WithReplication_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['REPLICATION =']);
   }
 | 'WITH' 'REPLICATION' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
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

PrimitiveType
 : 'TINYINT'
 | 'SMALLINT'
 | 'INT'
 | 'INTEGER'
 | 'BIGINT'
 | 'BOOLEAN'
 | 'FLOAT'
 | 'DOUBLE'
 | 'REAL'
 | 'STRING'
 | 'DECIMAL' OptionalTypePrecision
 | 'CHAR' OptionalTypeLength
 | 'VARCHAR' OptionalTypeLength
 | 'TIMESTAMP'
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
 : 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 | 'DESCRIBE' 'DATABASE' OptionalExtendedOrFormatted DatabaseIdentifier
   {
     parser.addDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DescribeStatement_EDIT
 : 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords([{ value: 'DATABASE', weight: 2 }, { value: 'EXTENDED', weight: 1 }, { value: 'FORMATTED', weight: 1 }]);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
     if (!$2) {
       parser.suggestKeywords([{ value: 'DATABASE', weight: 2 }, { value: 'EXTENDED', weight: 1 }, { value: 'FORMATTED', weight: 1 }]);
     }
   }
 | 'DESCRIBE' 'DATABASE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
     parser.suggestDatabases();
   }
 | 'DESCRIBE' 'DATABASE' OptionalExtendedOrFormatted 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
      }
      parser.addDatabaseLocation(@5, [{ name: $5 }]);
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
 : 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     $$ = { selectList: $4 };
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     $$ = { selectList: $4, tableExpression: $5 }
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
 : 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList_EDIT
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     if ($4.cursorAtStart) {
       var keywords = parser.getSelectListKeywords();
       if (!$3 && !$2) {
         keywords.push({ value: 'ALL', weight: 2 });
         keywords.push({ value: 'DISTINCT', weight: 2 });
       }
       if (!$3) {
         keywords.push({ value: 'STRAIGHT_JOIN', weight: 1 });
       }
       parser.suggestKeywords(keywords);
     } else {
       parser.checkForSelectListKeywords($4);
     }
     if ($4.suggestFunctions) {
       parser.suggestFunctions();
     }
     if ($4.suggestColumns) {
       parser.suggestColumns({ identifierChain: [], source: 'select' });
     }
     if ($4.suggestTables) {
       parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     }
     if ($4.suggestDatabases) {
       parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     }
     if ($4.suggestAggregateFunctions && (!$2 || $2 === 'ALL')) {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin 'CURSOR'
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4, true);
     var keywords = parser.getSelectListKeywords();
     if (!$2 || $2 === 'ALL') {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (!$3 && !$2) {
       keywords.push({ value: 'ALL', weight: 2 });
       keywords.push({ value: 'DISTINCT', weight: 2 });
     }
     if (!$3) {
       keywords.push({ value: 'STRAIGHT_JOIN', weight: 1 });
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns({ identifierChain: [], source: 'select' });
     parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList TableExpression_EDIT
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList_EDIT TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     parser.selectListNoTableSuggest($4, $2);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'select';
     }
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin 'CURSOR' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4, true);
     var keywords = parser.getSelectListKeywords();
     if (!$2 || $2 === 'ALL') {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (!$3 && !$2) {
       keywords.push({ value: 'ALL', weight: 2 });
       keywords.push({ value: 'DISTINCT', weight: 2 });
     }
     if (!$3) {
       keywords.push({ value: 'STRAIGHT_JOIN', weight: 1 });
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns({ identifierChain: [], source: 'select' });
     parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList 'CURSOR' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     parser.checkForSelectListKeywords($4);
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList 'CURSOR' ',' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     parser.checkForSelectListKeywords($4);
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList 'CURSOR'
   {
     parser.addClauseLocation('selectList', parser.firstDefined($3, @3, $2, @2, $1, @1), @4);
     parser.checkForSelectListKeywords($4);
     var keywords = ['FROM'];
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     parser.suggestTables({ prependFrom: true });
     parser.suggestDatabases({ prependFrom: true, appendDot: true });
   }
 ;

OptionalStraightJoin
 :
 | 'STRAIGHT_JOIN'
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
       if (typeof $1.tableReferenceList.hasJoinCondition !== 'undefined' && !$1.tableReferenceList.hasJoinCondition) {
         keywords.push({ value: 'ON', weight: 3 });
         keywords.push({ value: 'USING', weight: 3 });
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
       if ($1.tableReferenceList.suggestKeywords) {
         keywords = keywords.concat(parser.createWeightedKeywords($1.tableReferenceList.suggestKeywords, 3));
       }

       // Lower the weights for 'TABLESAMPLE' and 'LATERAL VIEW'
       keywords.forEach(function (keyword) {
         if (keyword.value === 'TABLESAMPLE' || keyword.value === 'LATERAL VIEW') {
           keyword.weight = 1.1;
         }
       });

       if ($1.tableReferenceList.types) {
         var veKeywords = parser.getValueExpressionKeywords($1.tableReferenceList);
         keywords = keywords.concat(veKeywords.suggestKeywords);
         if (veKeywords.suggestColRefKeywords) {
           parser.suggestColRefKeywords(veKeywords.suggestColRefKeywords);
           parser.addColRefIfExists($1.tableReferenceList);
         }
       }
     }

     if ($3.empty && $4 && $4.joinType.toUpperCase() === 'JOIN') {
       keywords = keywords.concat(['FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']);
       keywords = keywords.concat(['ANTI', 'CROSS', 'INNER', 'LEFT ANTI', 'LEFT INNER', 'LEFT SEMI', 'OUTER', 'RIGHT ANTI', 'RIGHT INNER', 'RIGHT SEMI', 'SEMI']);
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
       { value: 'ANTI JOIN', weight: 1 },
       { value: 'FULL JOIN', weight: 1 },
       { value: 'FULL OUTER JOIN', weight: 1 },
       { value: 'INNER JOIN', weight: 1 },
       { value: 'JOIN', weight: 1 },
       { value: 'LEFT ANTI JOIN', weight: 1 },
       { value: 'LEFT INNER JOIN', weight: 1 },
       { value: 'LEFT JOIN', weight: 1 },
       { value: 'LEFT OUTER JOIN', weight: 1 },
       { value: 'LEFT SEMI JOIN', weight: 1 },
       { value: 'OUTER JOIN', weight: 1 },
       { value: 'RIGHT ANTI JOIN', weight: 1 },
       { value: 'RIGHT INNER JOIN', weight: 1 },
       { value: 'RIGHT JOIN', weight: 1 },
       { value: 'RIGHT OUTER JOIN', weight: 1 },
       { value: 'RIGHT SEMI JOIN', weight: 1 },
       { value: 'SEMI JOIN', weight: 1 }
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
 : 'FROM' TableReferenceList
   {
     $$ = { tableReferenceList : $2 }
   }
 ;

FromClause_EDIT
 : 'FROM' 'CURSOR'
   {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
   }
 | 'FROM' TableReferenceList_EDIT
 ;

OptionalSelectConditions
 : OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$1, $2, $3, $4, $5, $6],
       [{ value: 'WHERE', weight: 9 },
        { value: 'GROUP BY', weight: 8 },
        { value: 'HAVING', weight: 7 },
        { value: 'ORDER BY', weight: 5 },
        { value: 'LIMIT', weight: 3 },
        { value: 'OFFSET', weight: 2 }],
       [true, true, true, true, true, true]);

     if (keywords.length > 0) {
       $$ = { suggestKeywords: keywords, empty: !$1 && !$2 && !$3 && !$4 && !$5 && !$6 };
     } else {
       $$ = {};
     }

     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = $5 ? @5 : undefined;

     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6) {
       $$.suggestFilters = { prefix: 'WHERE', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$2 && !$3 && !$4 && !$5 && !$6) {
       $$.suggestGroupBys = { prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$4 && !$5 && !$6) {
       $$.suggestOrderBys = { prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause_EDIT OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'where';
     }
   }
 | OptionalWhereClause GroupByClause_EDIT OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'group by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause_EDIT OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause_EDIT OptionalLimitClause OptionalOffsetClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'order by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause OffsetClause_EDIT
 ;

OptionalSelectConditions_EDIT
 : WhereClause 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$3, $4, $5, $6, $7],
       [{ value: 'GROUP BY', weight: 6 }, { value: 'HAVING', weight: 5 }, { value: 'ORDER BY', weight: 4 },  { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, true, true, true]);
     if ($1.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($1.suggestKeywords, 1));
     }
     $$ = parser.getValueExpressionKeywords($1, keywords);
     $$.cursorAtEnd = !$3 && !$4 && !$5 && !$6 && !$7;
     if ($1.columnReference) {
       $$.columnReference = $1.columnReference;
     }
     if (!$3) {
       parser.suggestGroupBys({ prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     if (!$3 && !$4 && !$5) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($5, @5, $4, @4, $3, @3, $1, @1);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause GroupByClause 'CURSOR' OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$4, $5, $6, $7],
       [{ value: 'HAVING', weight: 5 }, { value: 'ORDER BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, true, true]);
     if ($2.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($2.suggestKeywords, 6));
     }
     if ($2.valueExpression) {
       $$ = parser.getValueExpressionKeywords($2.valueExpression, keywords);
       if ($2.valueExpression.columnReference) {
         $$.columnReference = $2.valueExpression.columnReference;
       }
     } else {
       $$ = { suggestKeywords: keywords };
     }
     $$.cursorAtEnd = !$4 && !$5 && !$6 && !$7;
     if (!$4 && !$5) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($5, @5, $4, @4, $2, @2);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause 'CURSOR' OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$5, $6, $7],
       [{ value: 'ORDER BY', weight: 5 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, true]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$5 && !$6 && !$7 };
     if (!$5) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($5, @5, $3, @3);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause 'CURSOR' OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$6, $7], [{ value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, true]);
     if ($4.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($4.suggestKeywords, 4));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$6 && !$7 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($4, @4);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause LimitClause 'CURSOR' OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$7], [{ value: 'OFFSET', weight: 2 }], [true]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$7 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = @5;
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
 : 'GROUP' 'BY' GroupByColumnList
   {
     $$ = { valueExpression: $3 };
   }
 ;

GroupByClause_EDIT
 : 'GROUP' 'BY' GroupByColumnList_EDIT
   {
     parser.suggestSelectListAliases();
   }
 | 'GROUP' 'BY' 'CURSOR'
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
 : ValueExpression OptionalAscOrDesc OptionalNullsFirstOrLast  -> parser.mergeSuggestKeywords($2, $3)
 ;

OrderByIdentifier_EDIT
 : ValueExpression_EDIT OptionalAscOrDesc OptionalNullsFirstOrLast
   {
     parser.suggestSelectListAliases();
   }
 | ValueExpression OptionalAscOrDesc NullsFirstOrLast_EDIT
 | AnyCursor OptionalAscOrDesc OptionalNullsFirstOrLast
   {
     $$ = { emptyOrderBy: true }
     parser.valueExpressionSuggest();
     parser.suggestAnalyticFunctions();
     parser.suggestSelectListAliases();
   }
 ;

OptionalAscOrDesc
 :
  {
    $$ = { suggestKeywords: ['ASC', 'DESC'] };
  }
 | 'ASC'
 | 'DESC'
 ;

OptionalNullsFirstOrLast
 :
  {
    $$ = { suggestKeywords: ['NULLS FIRST', 'NULLS LAST'] };
  }
 | 'NULLS' 'FIRST'
 | 'NULLS' 'LAST'
 ;

NullsFirstOrLast_EDIT
 : 'NULLS' 'CURSOR'
   {
     parser.suggestKeywords(['FIRST', 'LAST']);
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
 : 'LIMIT' ValueExpression
 ;

LimitClause_EDIT
 : 'LIMIT' 'CURSOR'
   {
     parser.suggestKeywords([{ value: '10', weight: 10000 }, { value: '100', weight: 10000 }, { value: '1000', weight: 10000 }, { value: '5000', weight: 10000 }, { value: '10000', weight: 10000 }])
     parser.suggestFunctions({ types: ['BIGINT'] });
   }
 | 'LIMIT' ValueExpression_EDIT
   {
     delete parser.yy.result.suggestColumns;
   }
 ;

OptionalOffsetClause
 :
 | OffsetClause
 ;

OffsetClause
 : 'OFFSET' ValueExpression
 ;

OffsetClause_EDIT
 : 'OFFSET' 'CURSOR'
   {
     parser.suggestFunctions({ types: ['BIGINT'] });
   }
 | 'OFFSET' ValueExpression_EDIT
   {
     delete parser.yy.result.suggestColumns;
   }
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
     parser.suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'ILIKE', 'IREGEXP', 'LIKE', 'REGEXP', 'RLIKE']);
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
 | IntervalSpecification         -> { types: [ 'TIMESTAMP' ], text: $1 }
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
 | IntervalSpecification_EDIT
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

IntervalSpecification
 : 'INTERVAL' SignedInteger RegularIdentifier  -> $1 + $2 + $3
 ;

IntervalSpecification_EDIT
 : 'INTERVAL' SignedInteger 'CURSOR'
   {
     parser.suggestKeywords(['DAYS', 'HOURS', 'MICROSECONDS', 'MILLISECONDS', 'MINUTES', 'MONTHS', 'NANOSECONDS', 'SECONDS', 'WEEKS', 'YEARS']);
   }
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

SelectSpecification
 : ValueExpression OptionalCorrelationName
   {
     if ($2) {
       parser.addColumnAliasLocation($2.location, $2.alias, @1);
       $$ = { valueExpression: $1, alias: $2.alias };
       if (!parser.yy.selectListAliases) {
         parser.yy.selectListAliases = [];
       }
       parser.yy.selectListAliases.push($1.function && $1.types && $1.types.length && $1.types[0] === 'UDFREF' ? { name: $2.alias, udfRef: $1.function, types: $1.types } : { name: $2.alias, types: $1.types || ['T'] });
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
 : JoinType OptionalBroadcastOrShuffle TablePrimary OptionalJoinCondition
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
 | Joins JoinType OptionalBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     if ($5 && $5.valueExpression) {
       $$ = $5.valueExpression;
     } else {
       $$ = {};
     }
     $$.joinType = $1;
     if ($5.noJoinCondition) {
       $$.suggestJoinConditions = { prependOn: true, tablePrimaries: parser.yy.latestTablePrimaries.concat() }
     }
     if ($5.suggestKeywords) {
       $$.suggestKeywords = $5.suggestKeywords;
     }
     if (parser.yy.latestTablePrimaries.length > 0) {
       parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
     }
   }
 ;

Joins_INVALID
 : JoinType OptionalBroadcastOrShuffle                                           -> { joinType: $1 }
 | JoinType OptionalBroadcastOrShuffle Joins                                     -> { joinType: $1 }
 ;

OptionalBroadcastOrShuffle
 :
 | 'BROADCAST'
 | 'SHUFFLE'
 ;

Join_EDIT
 : JoinType_EDIT OptionalBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType_EDIT OptionalBroadcastOrShuffle
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType OptionalBroadcastOrShuffle TablePrimary_EDIT OptionalJoinCondition
 | JoinType OptionalBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | JoinType OptionalBroadcastOrShuffle 'CURSOR' OptionalJoinCondition
   {
     if (!$2) {
       parser.suggestKeywords(['[BROADCAST]', '[SHUFFLE]']);
     }
     if (!$2 && parser.yy.latestTablePrimaries.length > 0) {
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
 : 'JOIN'                         -> 'JOIN'
 | 'ANTI' 'JOIN'          -> 'ANTI JOIN'
 | 'CROSS' 'JOIN'                 -> 'CROSS JOIN'
 | 'INNER' 'JOIN'                 -> 'INNER JOIN'
 | 'OUTER' 'JOIN'                 -> 'OUTER JOIN'
 | 'SEMI' 'JOIN'                  -> 'SEMI JOIN'
 | 'FULL' 'JOIN'                  -> 'FULL JOIN'
 | 'FULL' 'OUTER' 'JOIN'          -> 'FULL OUTER JOIN'
 | 'LEFT' 'JOIN'                  -> 'LEFT JOIN'
 | 'LEFT' 'ANTI' 'JOIN'   -> 'LEFT ANTI JOIN'
 | 'LEFT' 'INNER' 'JOIN'          -> 'LEFT INNER JOIN'
 | 'LEFT' 'OUTER' 'JOIN'          -> 'LEFT OUTER JOIN'
 | 'LEFT' 'SEMI' 'JOIN'           -> 'LEFT SEMI JOIN'
 | 'RIGHT' 'JOIN'                 -> 'RIGHT JOIN'
 | 'RIGHT' 'ANTI' 'JOIN'  -> 'RIGHT ANTI JOIN'
 | 'RIGHT' 'INNER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'OUTER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'SEMI' 'JOIN'          -> 'RIGHT SEMI JOIN'
 ;

JoinType_EDIT
 : 'ANTI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'CROSS' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'INNER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'OUTER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'SEMI' 'CURSOR'                  -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['OUTER'] }
 | 'LEFT' 'ANTI' 'CURSOR'   -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'INNER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'SEMI' 'CURSOR'           -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['ANTI', 'INNER', 'OUTER', 'SEMI'] }
 | 'RIGHT' 'ANTI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'INNER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'OUTER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'SEMI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'CURSOR' 'JOIN'          -> { suggestKeywords: ['ANTI', 'INNER', 'OUTER', 'SEMI'] }
 ;

OptionalJoinCondition
 :                                       -> { noJoinCondition: true, suggestKeywords: ['ON', 'USING'] }
 | 'ON' ValueExpression                  -> { valueExpression: $2 }
 | 'USING' '(' UsingColList ')'          -> {}
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
 : TableOrQueryName OptionalCorrelationName OptionalTableSample
   {
     $$ = {
       primary: $1
     }
     if ($1.identifierChain) {
       if ($2) {
         $1.alias = $2.alias;
         parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
       }
       parser.addTablePrimary($1);
     }
     var keywords = [];
     if ($3 && $3.suggestKeywords) {
       keywords = $3.suggestKeywords;
     } else if (!$2 && !$3) {
       keywords = [{ value: 'AS', weight: 2 }, { value: 'TABLESAMPLE', weight: 3 }];
     } else if (!$3) {
       keywords = [{ value: 'TABLESAMPLE', weight: 3 }];
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 | DerivedTable OptionalCorrelationName OptionalTableSample
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
     if ($3 && $3.suggestKeywords) {
       keywords = $3.suggestKeywords;
     } else {
       keywords = parser.getKeywordsForOptionalsLR([$3, $2], [{ value: 'TABLESAMPLE', weight: 1 }, { value: 'AS', weight: 2 }], [true, true]);
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalCorrelationName OptionalTableSample
   {
     if ($2) {
       parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
     }
   }
 | TableOrQueryName OptionalCorrelationName TableSample_EDIT
   {
     if ($2) {
       $1.alias = $2.alias;
       parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
     }
     parser.addTablePrimary($1);
   }
 | DerivedTable_EDIT OptionalCorrelationName OptionalTableSample
   {
     if ($2) {
       parser.addTablePrimary({ subQueryAlias: $2.alias });
       parser.addSubqueryAliasLocation($2.location, $2.alias);
     }
   }
 | DerivedTable OptionalCorrelationName_EDIT OptionalTableSample
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
 | 'TABLESAMPLE' 'SYSTEM' '(' 'UNSIGNED_INTEGER' ')'                                                  -> { suggestKeywords: ['REPEATABLE()'] }
 | 'TABLESAMPLE' 'SYSTEM' '(' 'UNSIGNED_INTEGER' ')' 'REPEATABLE' '(' 'UNSIGNED_INTEGER' ')'
 ;

TableSample_EDIT
 : 'TABLESAMPLE' 'CURSOR'
   {
     parser.suggestKeywords(['SYSTEM()']);
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
 : RowsOrRange 'BETWEEN' OptionalCurrentOrPreceding OptionalAndFollowing
 | RowsOrRange 'UNBOUNDED' OptionalCurrentOrPreceding OptionalAndFollowing
 ;

WindowSpec_EDIT
 : RowsOrRange 'CURSOR'
   {
     parser.suggestKeywords(['BETWEEN']);
   }
 | RowsOrRange 'BETWEEN' OptionalCurrentOrPreceding OptionalAndFollowing 'CURSOR'
   {
     if (!$3 && !$4) {
       parser.suggestKeywords(['CURRENT ROW', 'UNBOUNDED PRECEDING']);
     } else if (!$4) {
       parser.suggestKeywords(['AND']);
     }
   }
 | RowsOrRange 'BETWEEN' OptionalCurrentOrPreceding_EDIT OptionalAndFollowing
 | RowsOrRange 'BETWEEN' OptionalCurrentOrPreceding OptionalAndFollowing_EDIT
 | RowsOrRange 'UNBOUNDED' OptionalCurrentOrPreceding 'CURSOR'
 | RowsOrRange 'UNBOUNDED' OptionalCurrentOrPreceding_EDIT
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
