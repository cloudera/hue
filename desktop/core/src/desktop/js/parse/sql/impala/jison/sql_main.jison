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
 | 'ICEBERG'
 | 'KEY'
 | 'OPTION'
 | 'OWNER'
 | 'SERVER'
 | 'SPEC'
 | 'STRUCT'
 | 'SYSTEM_TIME'
 | 'SYSTEM_VERSION'
 | 'UNSET'
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
 : TableOrQueryName OptionalCorrelationName OptionalAsOf OptionalTableSample
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
     if ($4 && $4.suggestKeywords) {
       keywords = $4.suggestKeywords;
     } else {
       if (!$4) {
         keywords.push({ value: 'TABLESAMPLE', weight: 3 });
       }
       if (!$4 && !$3) {
         keywords.push({ value: 'FOR SYSTEM_TIME AS OF', weight: 4 });
         keywords.push({ value: 'FOR SYSTEM_VERSION AS OF', weight: 4 });
       }
       if (!$4 && !$3 && !$2) {
         keywords.push({ value: 'AS', weight: 5 });
       }
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
       keywords = parser.getKeywordsForOptionalsLR([$3, $2], [{ value: 'TABLESAMPLE', weight: 3 }, { value: 'AS', weight: 4 }], [true, true]);
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalCorrelationName OptionalAsOf OptionalTableSample
   {
     if ($2) {
       parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
     }
   }
 | TableOrQueryName OptionalCorrelationName OptionalAsOf TableSample_EDIT
   {
     if ($2) {
       $1.alias = $2.alias;
       parser.addTableAliasLocation($2.location, $2.alias, $1.identifierChain);
     }
     parser.addTablePrimary($1);
   }
 | TableOrQueryName OptionalCorrelationName AsOf_EDIT OptionalTableSample
 | DerivedTable_EDIT OptionalCorrelationName OptionalTableSample
   {
     if ($2) {
       parser.addTablePrimary({ subQueryAlias: $2.alias });
       parser.addSubqueryAliasLocation($2.location, $2.alias);
     }
   }
 | DerivedTable OptionalCorrelationName_EDIT OptionalTableSample
 ;

OptionalAsOf
 :
 | AsOf
 ;

AsOf
 : 'FOR' SystemTimeOrSystemVersion 'AS' 'OF' ValueExpression
 ;


AsOf_EDIT
 : 'FOR' 'CURSOR'
   {
     parser.suggestKeywords(['SYSTEM_TIME AS OF', 'SYSTEM_VERSION AS OF']);
   }
 | 'FOR' SystemTimeOrSystemVersion 'CURSOR'
   {
     parser.suggestKeywords(['AS OF']);
   }
 | 'FOR' SystemTimeOrSystemVersion 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['OF']);
   }
 | 'FOR' SystemTimeOrSystemVersion 'AS' 'OF' 'CURSOR'
   {
     parser.valueExpressionSuggest();
   }
 ;

SystemTimeOrSystemVersion
 : 'SYSTEM_TIME'
 | 'SYSTEM_VERSION'
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


