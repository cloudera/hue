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

%left 'AND' 'OR'
%left 'BETWEEN'
%left 'NOT' '!' '~'
%left '=' '<' '>' 'COMPARISON_OPERATOR'
%left '-' '*' 'ARITHMETIC_OPERATOR'

%left ';' ','
%nonassoc 'CURSOR' 'PARTIAL_CURSOR'
%nonassoc 'IN' 'IS' 'LIKE' 'RLIKE' 'REGEXP' 'EXISTS' NEGATION

%start Sql

%%

NonReservedKeyword
 : '<hive>ADD'
 | '<hive>ADMIN'
 | '<hive>AFTER'
 | '<hive>ANALYZE'
 | '<hive>ARCHIVE'
 | '<hive>AVRO'
 | '<hive>BUCKET'
 | '<hive>BUCKETS'
 | '<hive>CACHE'
 | '<hive>CASCADE'
 | '<hive>CHANGE'
 | '<hive>CLUSTERED'
 | '<hive>COLLECTION'
 | '<hive>COLUMNS'
 | '<hive>COMMENT'
 | '<hive>COMPACT'
 | '<hive>COMPACTIONS'
 | '<hive>COMPUTE'
 | '<hive>CONCATENATE'
 | '<hive>DATA'
 | '<hive>DATABASES'
 | '<hive>DEFERRED'
 | '<hive>DEFINED'
 | '<hive>DELIMITED'
 | '<hive>DEPENDENCY'
 | '<hive>DIRECTORY'
 | '<hive>DISABLE'
 | '<hive>ENABLE'
 | '<hive>ESCAPED'
 | '<hive>EXCHANGE'
 | '<hive>EXPLAIN'
 | '<hive>EXPORT'
 | '<hive>FIELDS'
 | '<hive>FILE'
 | '<hive>FILEFORMAT'
 | '<hive>FIRST'
 | '<hive>FORMAT'
 | '<hive>FUNCTIONS'
 | '<hive>INPATH'
 | '<hive>INPUTFORMAT'
 | '<hive>JAR'
 | '<hive>IDXPROPERTIES'
 | '<hive>ITEMS'
 | '<hive>KEYS'
 | '<hive>LINES'
 | '<hive>LOAD'
 | '<hive>LOCATION'
 | '<hive>LOCKS'
 | '<hive>METADATA'
 | '<hive>MSCK'
 | '<hive>NOSCAN'
 | '<hive>NO_DROP'
 | '<hive>OFFLINE'
 | '<hive>ORC'
 | '<hive>OUTPUTFORMAT'
 | '<hive>OVERWRITE'
 | '<hive>PARQUET'
 | '<hive>PARTITIONED'
 | '<hive>PARTITIONS'
 | '<hive>PRIVILEGES'
 | '<hive>PURGE'
 | '<hive>RCFILE'
 | '<hive>REBUILD'
 | '<hive>RELOAD'
 | '<hive>REPAIR'
 | '<hive>REPLICATION'
 | '<hive>RECOVER'
 | '<hive>RENAME'
 | '<hive>REPLACE'
 | '<hive>RESTRICT'
 | '<hive>ROLE'
 | '<hive>ROLES'
 | '<hive>SCHEMAS'
 | '<hive>SEQUENCEFILE'
 | '<hive>SERDE'
 | '<hive>SERDEPROPERTIES'
 | '<hive>SETS'
 | '<hive>SHOW'
 | '<hive>SKEWED'
 | '<hive>SORTED'
 | '<hive>STATISTICS'
 | '<hive>STORED'
 | '<hive>STRING'
 | '<hive>STRUCT'
 | '<hive>TABLES'
 | '<hive>TBLPROPERTIES'
 | '<hive>TEMPORARY'
 | '<hive>TERMINATED'
 | '<hive>TEXTFILE'
 | '<hive>TINYINT'
 | '<hive>TOUCH'
 | '<hive>TRANSACTIONS'
 | '<hive>UNARCHIVE'
 | '<hive>UNIONTYPE'
 | '<hive>USE'
 | '<hive>VIEW'
// | '<hive>ASC'      // These cause conflicts, we could use a separate lexer state for DESCRIBE, ALTER, GRANT, REVOKE and SHOW
// | '<hive>CLUSTER'
// | '<hive>DESC'
// | '<hive>DISTRIBUTE'
// | '<hive>FORMATTED'
// | '<hive>FUNCTION'
// | '<hive>INDEX'
// | '<hive>INDEXES'
// | '<hive>LOCK'
// | '<hive>SCHEMA'
// | '<hive>SHOW_DATABASE'
// | '<hive>SORT'
 ;

NonReservedKeyword
 : '<impala>ANALYTIC'
 | '<impala>ANTI'
 | '<impala>CURRENT'
 | '<impala>GRANT'
 | '<impala>ROLE'
 | '<impala>ROLES'
 | '<impala>URI'
 | '<impala>SERVER'
// | '<impala>BROADCAST'
// | '<impala>NOSHUFFLE'
// | '<impala>SHUFFLE'
// TODO: Check if following are true
 | '<impala>BLOCK_SIZE'
 | '<impala>COMPRESSION'
 | '<impala>DEFAULT'
 | '<impala>ENCODING'
 | '<impala>KEY'
 ;

NonReservedKeyword
 : 'ROLE'
 | 'OPTION'
 ;

RegularIdentifier
 : 'REGULAR_IDENTIFIER'
 | 'VARIABLE_REFERENCE'
 | NonReservedKeyword
 ;

NewStatement
 : /* empty */
   {
     prepareNewStatement();
   }
 ;

Sql
 : NewStatement SqlStatements EOF
   {
     return parser.yy.result;
   }
 | NewStatement SqlStatements_EDIT EOF
   {
     return parser.yy.result;
   }
 ;

SqlStatements
 :
 | DataDefinition
 | DataManipulation
 | QuerySpecification
 | SetSpecification
 | ExplainClause DataDefinition
 | ExplainClause DataManipulation
 | ExplainClause QuerySpecification
 | SqlStatements ';' NewStatement SqlStatements
 ;

SqlStatements_EDIT
 : SqlStatement_EDIT
 | SqlStatement_EDIT ';' NewStatement SqlStatements
 | SqlStatements ';' NewStatement SqlStatement_EDIT
 | SqlStatements ';' NewStatement SqlStatement_EDIT ';' NewStatement SqlStatements
 ;

SqlStatement_EDIT
 : AnyCursor
   {
     if (isHive()) {
       suggestDdlAndDmlKeywords(['EXPLAIN', 'FROM']);
     } else if (isImpala()) {
       suggestDdlAndDmlKeywords(['EXPLAIN']);
     } else {
       suggestDdlAndDmlKeywords();
     }
   }
 | CommonTableExpression 'CURSOR'
   {
     if (isHive() || isImpala()) {
       suggestKeywords(['INSERT', 'SELECT']);
     } else {
       suggestKeywords(['SELECT']);
     }
   }
 | ExplainClause_EDIT
 | DataDefinition_EDIT
 | DataManipulation_EDIT
 | QuerySpecification_EDIT
 | ExplainClause DataDefinition_EDIT
 | ExplainClause DataManipulation_EDIT
 | ExplainClause QuerySpecification_EDIT
 | ExplainClause_EDIT DataDefinition
 | ExplainClause_EDIT DataManipulation
 | ExplainClause_EDIT QuerySpecification
 ;

SetSpecification
 : 'SET' SetOption '=' SetValue
 ;

SetOption
 : RegularIdentifier
 | SetOption AnyDot RegularIdentifier
 ;

SetValue
 : RegularIdentifier
 | SignedInteger
 | SignedInteger RegularIdentifier
 | QuotedValue
 | 'TRUE'
 | 'FALSE'
 | 'NULL'
 ;

ExplainClause
 : '<hive>EXPLAIN' OptionalHiveExplainTypes
 | '<impala>EXPLAIN'
 ;

ExplainClause_EDIT
 : '<hive>EXPLAIN' OptionalHiveExplainTypes 'CURSOR'
   {
     if (!$2) {
       suggestDdlAndDmlKeywords([{ value: 'AUTHORIZATION', weight: 2 }, { value: 'DEPENDENCY', weight: 2 }, { value: 'EXTENDED', weight: 2 }]);
     } else {
       suggestDdlAndDmlKeywords();
     }
   }
 | '<impala>EXPLAIN' 'CURSOR'
   {
     suggestDdlAndDmlKeywords();
   }
 ;

OptionalHiveExplainTypes
 :
 | '<hive>AUTHORIZATION'
 | '<hive>DEPENDENCY'
 | '<hive>EXTENDED'
 ;

// This is a work-around for error handling when a statement starts with some token that the parser can understand but
// it's not a valid statement (see ErrorStatement). It contains everything except valid starting tokens ('SELECT', 'USE' etc.)
NonStartingToken
 : '<hive>ADMIN' | '<hive>ALL' | '<hive>ARRAY' | '<hive>AS' | '<hive>AUTHORIZATION' | '<hive>AVRO' | '<hive>BINARY' | '<hive>BUCKET' | '<hive>BUCKETS' | '<hive>CACHE' | '<hive>CLUSTER' | '<hive>CLUSTERED' | '<hive>COLLECTION' | '<hive>COMPUTE' | '<hive>CONF' | '<hive>CROSS' | '<hive>CUBE' | '<hive>CURRENT' | '<hive>DATE' | '<hive>DEFERRED' | '<hive>DELIMITED' | '<hive>DEPENDENCY' | '<hive>DIRECTORY' | '<hive>DISTRIBUTE' | '<hive>DISTRIBUTED' | '<hive>ESCAPED' | '<hive>EXTENDED' | '<hive>EXTERNAL' | '<hive>FIELDS' | '<hive>FILE' | '<hive>FOR' | '<hive>FORMAT' | '<hive>FUNCTION' | '<hive>GRANT' | '<hive>GROUPING' | '<hive>IDXPROPERTIES' | '<hive>LATERAL' | '<hive>LOCAL' | '<hive>LOCK' | '<hive>MACRO' | '<hive>OVERWRITE' | '<hive>PARTITION' | '<hive>PRIVILEGES' | '<hive>REBUILD' | '<hive>REPAIR' | '<hive>REPLICATION' |'<hive>ROLLUP' | '<hive>SETS' | '<hive>STATISTICS' | '<hive>SHOW_DATABASE' | '<hive>TABLE' | '<hive>USER' | '<hive>ASC' | '<hive>COLUMNS' | '<hive>COMMENT' | '<hive>COMPACTIONS' | '<hive>DATA' | '<hive>DATABASES' | '<hive>DEFINED' | '<hive>DESC' |  '<hive>FORMATTED' | '<hive>FUNCTIONS' | '<hive>INDEX' | '<hive>INDEXES' | '<hive>INPATH' | '<hive>INPUTFORMAT' | '<hive>ITEMS' | '<hive>JAR' | '<hive>KEYS' | '<hive>LINES' | '<hive>LOCATION' | '<hive>LOCKS' | '<hive>MAP' | '<hive>METADATA' | '<hive>NONE' | '<hive>NOSCAN' | '<hive>OF' | '<hive>ORC' | '<hive>OUT' | '<hive>OUTPUTFORMAT' | '<hive>PARQUET' | '<hive>PARTITIONED' | '<hive>PARTITIONS' | '<hive>RCFILE' | '<hive>ROLE' | '<hive>ROLES' | '<hive>SCHEMA' | '<hive>SCHEMAS' | '<hive>SEQUENCEFILE' | '<hive>SERDE' | '<hive>SERDEPROPERTIES' | '<hive>SKEWED' | '<hive>SORTED' | '<hive>STORED' | '<hive>STORED_AS_DIRECTORIES' | '<hive>STRING' | '<hive>STRUCT' | '<hive>TABLES' | '<hive>TABLESAMPLE' | '<hive>TBLPROPERTIES' | '<hive>TEMPORARY' | '<hive>TERMINATED' | '<hive>TEXTFILE' | '<hive>TINYINT' | '<hive>TRANSACTIONS' | '<hive>UNIONTYPE' | '<hive>USING' | '<hive>VIEW' | '<hive>WINDOW' | '<hive>.' | '<hive>[' | '<hive>]'
 | '<impala>AGGREGATE' | '<impala>AVRO' | '<impala>CACHED' | '<impala>CLOSE_FN' | '<impala>COLUMN' | '<impala>COMMENT' | '<impala>DATA' | '<impala>DATABASES' | '<impala>DELIMITED' | '<impala>ESCAPED' | '<impala>EXTENDED' |'<impala>EXTERNAL' | '<impala>FIELDS' | '<impala>FINALIZE_FN' | '<impala>FIRST' | '<impala>FORMAT' | '<impala>FORMATTED' | '<impala>FUNCTION' | '<impala>FUNCTIONS' | '<impala>GROUP' | '<impala>HASH' | '<impala>INCREMENTAL' | '<impala>INTERVAL' | '<impala>INIT_FN' | '<impala>INPATH' | '<impala>KEY' | '<impala>KUDU' | '<impala>LAST' | '<impala>LIMIT' | '<impala>LINES' | '<impala>LOCATION' | '<impala>MERGE_FN' | '<impala>NULLS' | '<impala>PARTITIONS' | '<impala>PREPARE_FN' | '<impala>PRIMARY' | '<impala>REAL' | '<impala>RETURNS' | '<impala>SCHEMAS' | '<impala>SERIALIZE_FN' | '<impala>SERVER' | '<impala>STATS' | '<impala>STRAIGHT_JOIN' | '<impala>SYMBOL' | '<impala>TABLE' | '<impala>TABLES' | '<impala>URI' | '<impala>USING' | '<impala>ANALYTIC' | '<impala>ANTI' | '<impala>CURRENT' | '<impala>GRANT' | '<impala>NOSHUFFLE' | '<impala>PARQUET' | '<impala>PARTITIONED' | '<impala>RCFILE' | '<impala>ROLE' | '<impala>ROLES' | '<impala>SEQUENCEFILE' | '<impala>SERDEPROPERTIES' | '<impala>SHUFFLE' | '<impala>STORED' | '<impala>TBLPROPERTIES' | '<impala>TERMINATED' | '<impala>TEXTFILE' | '<impala>UPDATE_FN' | '<impala>BROADCAST' | '<impala>...' | '<impala>.' | '<impala>[' | '<impala>]'
 | 'ALL' | 'AS' | 'ASC' | 'BETWEEN' | 'BIGINT' | 'BOOLEAN' | 'BY' | 'CASE' | 'CHAR' | 'CURRENT' | 'DATABASE' | 'DECIMAL' | 'DISTINCT' | 'DOUBLE' | 'DESC' | 'ELSE' | 'END' | 'EXISTS' | 'FALSE' | 'FLOAT' | 'FOLLOWING' | 'FROM' | 'FULL' | 'GROUP' | 'HAVING' | 'IF' | 'IN' | 'INNER' | 'INSERT' | 'INT' | 'INTO' | 'IS' | 'JOIN' | 'LEFT' | 'LIKE' | 'LIMIT' | 'NOT' | 'NULL' | 'ON' | 'OPTION' | 'ORDER' | 'OUTER' | 'OVER' | 'PARTITION' | 'PRECEDING' | 'RANGE' | 'REGEXP' | 'RIGHT' | 'RLIKE' | 'ROW' | 'ROWS' | 'SCHEMA' | 'SEMI' | 'SET' | 'SMALLINT' | 'STRING' | 'TABLE' | 'THEN' | 'TIMESTAMP' | 'TINYINT' | 'TRUE' | 'UNION' | 'VALUES' | 'VARCHAR' | 'WHEN' | 'WHERE' | 'WITH' | 'ROLE'
 | 'AVG' | 'CAST' | 'COUNT' | 'MAX' | 'MIN' | 'STDDEV_POP' | 'STDDEV_SAMP' | 'SUM' | 'VARIANCE' | 'VAR_POP' | 'VAR_SAMP'
 | '<hive>COLLECT_SET' | '<hive>COLLECT_LIST' | '<hive>CORR' | '<hive>COVAR_POP' | '<hive>COVAR_SAMP' | '<hive>HISTOGRAM_NUMERIC' | '<hive>NTILE' | '<hive>PERCENTILE' | '<hive>PERCENTILE_APPROX'
 | '<impala>APPX_MEDIAN' | '<impala>EXTRACT' | '<impala>GROUP_CONCAT' | '<impala>STDDEV' | '<impala>VARIANCE_POP' | '<impala>VARIANCE_SAMP'
 | 'ANALYTIC'
 | 'UNSIGNED_INTEGER' | 'UNSIGNED_INTEGER_E' | 'REGULAR_IDENTIFIER' | 'HDFS_START_QUOTE' | 'AND' | 'OR' | '=' | '<' | '>' | 'COMPARISON_OPERATOR' | '-' | '*' | 'ARITHMETIC_OPERATOR' | ',' | '.' | '~' | '!' | '(' | ')' | '[' | ']' | 'VARIABLE_REFERENCE' | 'BACKTICK' | 'SINGLE_QUOTE' | 'DOUBLE_QUOTE'
 ;

DataDefinition
 : DescribeStatement
 ;

DataDefinition_EDIT
 : DescribeStatement_EDIT
 ;

// ===================================== Commonly used constructs =====================================

AggregateOrAnalytic
 : '<impala>AGGREGATE'
 | '<impala>ANALYTIC'
 ;

Commas
 : ','
 | Commas ','
 ;

AnyAs
 : 'AS'
 | '<hive>AS'
 ;

AnyCreate
 : 'CREATE'
 | '<hive>CREATE'
 | '<impala>CREATE'
 ;

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

AnyDot
 : '.'
 | '<impala>.'
 | '<hive>.'
 ;

AnyFromOrIn
 : 'FROM'
 | 'IN'
 ;

AnyGroup
 : 'GROUP'
 | '<hive>GROUP'
 | '<impala>GROUP'
 ;

AnyPartition
 : 'PARTITION'
 | '<hive>PARTITION'
 ;

AnyTable
 : 'TABLE'
 | '<hive>TABLE'
 | '<impala>TABLE'
 ;

DatabaseOrSchema
 : 'DATABASE'
 | 'SCHEMA'
 | '<hive>SCHEMA'
 ;

FromOrIn
 : 'FROM'
 | 'IN'
 ;

HiveIndexOrIndexes
 : '<hive>INDEX'
 | '<hive>INDEXES'
 ;

HiveOrImpalaComment
 : '<hive>COMMENT'
 | '<impala>COMMENT'
 ;

HiveOrImpalaCreate
 : '<hive>CREATE'
 | '<impala>CREATE'
 ;

HiveOrImpalaCurrent
 : '<hive>CURRENT'
 | '<impala>CURRENT'
 ;

HiveOrImpalaDatabasesOrSchemas
 : '<hive>DATABASES'
 | '<hive>SCHEMAS'
 | '<impala>DATABASES'
 | '<impala>SCHEMAS'
 ;

HiveOrImpalaEscaped
 : '<hive>ESCAPED'
 | '<impala>ESCAPED'
 ;

HiveOrImpalaExternal
 : '<hive>EXTERNAL'
 | '<impala>EXTERNAL'
 ;

HiveOrImpalaFields
 : '<hive>FIELDS'
 | '<impala>FIELDS'
 ;

HiveOrImpalaFormat
 : '<hive>FORMAT'
 | '<impala>FORMAT'
 ;

HiveOrImpalaLeftSquareBracket
 : '<hive>['
 | '<impala>['
 ;

HiveOrImpalaLines
 : '<hive>LINES'
 | '<impala>LINES'
 ;

HiveOrImpalaLocation
 : '<hive>LOCATION'
 | '<impala>LOCATION'
 ;

HiveOrImpalaRightSquareBracket
 : '<hive>]'
 | '<impala>]'
 ;

HiveOrImpalaPartitioned
 : '<hive>PARTITIONED'
 | '<impala>PARTITIONED'
 ;

HiveOrImpalaStored
 : '<hive>STORED'
 | '<impala>STORED'
 ;

HiveOrImpalaTables
 : '<hive>TABLES'
 | '<impala>TABLES'
 ;

HiveOrImpalaTblproperties
 : '<hive>TBLPROPERTIES'
 | '<impala>TBLPROPERTIES'
 ;

HiveOrImpalaTerminated
 : '<hive>TERMINATED'
 | '<impala>TERMINATED'
 ;

HiveRoleOrUser
 : '<hive>ROLE'
 | '<hive>USER'
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

OptionalHiveExtended
 :
 | '<hive>EXTENDED'
 ;

OptionalHiveExtendedOrFormatted
 :
 | '<hive>EXTENDED'
 | '<hive>FORMATTED'
 ;

OptionalExternal
 :
 | '<hive>EXTERNAL'
 | '<impala>EXTERNAL'
 ;

OptionalImpalaExtendedOrFormatted
 :
 | '<impala>EXTENDED'
 | '<impala>FORMATTED'
 ;

OptionallyFormattedIndex
 : '<hive>FORMATTED' HiveIndexOrIndexes
 | HiveIndexOrIndexes
 ;

OptionallyFormattedIndex_EDIT
 : '<hive>FORMATTED' 'CURSOR'
   {
     suggestKeywords(['INDEX', 'INDEXES']);
   }
 | 'CURSOR' HiveIndexOrIndexes
   {
     suggestKeywords(['FORMATTED']);
   }
 ;

OptionalFromDatabase
 :
 | FromOrIn DatabaseIdentifier
 ;

OptionalFromDatabase_EDIT
 : FromOrIn DatabaseIdentifier_EDIT
 ;

OptionalHiveCascadeOrRestrict
 :
 | '<hive>CASCADE'
 | '<hive>RESTRICT'
 ;

OptionalHiveTemporary
 :
 | '<hive>TEMPORARY'
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
     suggestKeywords(['EXISTS']);
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
     suggestKeywords(['NOT EXISTS']);
   }
 | 'IF' 'NOT' 'CURSOR'
   {
     suggestKeywords(['EXISTS']);
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
 : AnyPartition '(' PartitionSpecList ')'
 ;

PartitionSpec_EDIT
 : AnyPartition '(' PartitionSpecList_EDIT RightParenthesisOrError
 ;

ConfigurationName
 : RegularIdentifier
 | 'CURSOR'
 | ConfigurationName '<hive>.' RegularIdentifier
 | ConfigurationName '<hive>.' 'PARTIAL_CURSOR'
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
     suggestColumns();
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
     suggestColumns();
   }
 | ColumnList ',' ColumnIdentifier_EDIT
 | ColumnIdentifier_EDIT ',' ColumnList
 | ColumnList ',' ColumnIdentifier_EDIT ',' ColumnList
 | ColumnList ',' AnyCursor ',' ColumnList
   {
     suggestColumns();
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
     addTableLocation(@1, [ { name: $1 } ]);
     $$ = { identifierChain: [ { name: $1 } ] };
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     addDatabaseLocation(@1, [ { name: $1 } ]);
     addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] };
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier ImpalaFields
   {
     // This is a special case for Impala expression like "SELECT | FROM db.table.col"
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ].concat($4) };
   }
 ;

SchemaQualifiedTableIdentifier_EDIT
 : PartialBacktickedIdentifier
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     suggestDatabases();
     $$ = { identifierChain: [{ name: $1 }] };
   }
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     // In Impala you can have statements like 'SELECT ... FROM testTable t, t.|'
     suggestTablesOrColumns($1);
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier ImpalaFields_EDIT
   {
     // TODO: switch to suggestColumns, it's currently handled in sqlAutocompleter2.js
     // Issue is that suggestColumns is deleted if no tables are defined and this is
     // Impala only cases like "SELECT | FROM db.table.col"
     suggestTables({ identifierChain: [{ name: $1 }, { name: $3 }].concat($4) });
   }
 ;

ImpalaFields
 : ImpalaField               -> [$1]
 | ImpalaFields ImpalaField
   {
     $1.push($2);
   }
 ;

ImpalaFields_EDIT
 : ImpalaField_EDIT                            -> []
 | ImpalaFields ImpalaField_EDIT               -> $1
 | ImpalaFields ImpalaField_EDIT ImpalaFields  -> $1
 | ImpalaField_EDIT ImpalaFields               -> []
 ;

ImpalaField
 : '<impala>.' RegularOrBacktickedIdentifier  -> { name: $2 }
 ;

ImpalaField_EDIT
 : '<impala>.' PartialBacktickedOrPartialCursor
 ;

SchemaQualifiedIdentifier
 : RegularOrBacktickedIdentifier
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
 ;

SchemaQualifiedIdentifier_EDIT
 : PartialBacktickedIdentifier
   {
     suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     suggestDatabases();
     $$ = { identifierChain: [{ name: $1 }] };
   }
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
 ;

DatabaseIdentifier
 : RegularOrBacktickedIdentifier
 ;

DatabaseIdentifier_EDIT
 : PartialBacktickedOrCursor
   {
     suggestDatabases();
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
 | ColumnIdentifier // Hive allows partial partition specs in some cases
 ;

PartitionExpression_EDIT
 : ColumnIdentifier '=' ValueExpression_EDIT
 | ColumnIdentifier '=' AnyCursor
   {
     valueExpressionSuggest();
   }
 | PartialBacktickedIdentifier '=' ValueExpression
   {
     suggestColumns();
   }
 | AnyCursor
   {
     suggestColumns();
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
     addTableLocation(@1, [ { name: $1 } ]);
     $$ = { identifierChain: [ { name: $1 } ] };
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     addDatabaseLocation(@1, [ { name: $1 } ]);
     addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] };
   }
 ;

RegularOrBackTickedSchemaQualifiedName_EDIT
 : PartialBacktickedIdentifier
   {
     suggestTables();
     suggestDatabases({ prependDot: true });
   }
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     suggestTablesOrColumns($1);
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
 | BasicIdentifierChain AnyDot '*'
   {
     addAsteriskLocation(@3, $1.concat({ asterisk: true }));
   }
 ;

ColumnReference_EDIT
 : BasicIdentifierChain_EDIT
 ;

BasicIdentifierChain
 : ColumnIdentifier
   {
     $$ = [$1];
     addUnknownLocation(@1, [$1]);
   }
 | BasicIdentifierChain AnyDot ColumnIdentifier
   {
     $1.push($3);
     addUnknownLocation(@3, $1.concat());
   }
 ;

// TODO: Merge with DerivedColumnChain_EDIT ( issue is starting with PartialBacktickedOrPartialCursor)
BasicIdentifierChain_EDIT
 : ColumnIdentifier_EDIT
   {
     if ($1.insideKey) {
       suggestKeyValues({ identifierChain: [{ name: $1.name }] });
       suggestColumns();
       suggestFunctions();
     }
   }
 | BasicIdentifierChain AnyDot ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       suggestKeyValues({ identifierChain: $1.concat({ name: $3.name }) });
       suggestColumns();
       suggestFunctions();
     }
   }
 | BasicIdentifierChain AnyDot ColumnIdentifier_EDIT AnyDot BasicIdentifierChain
 | ColumnIdentifier_EDIT AnyDot BasicIdentifierChain
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor
   {
     suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: [{ value: '*', weight: 1099 }] };
   }
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor AnyDot BasicIdentifierChain
   {
     suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: [{ value: '*', weight: 1099 }] };
   }
 ;

DerivedColumnChain
 : ColumnIdentifier  -> [ $1 ]
 | DerivedColumnChain AnyDot ColumnIdentifier
   {
     $1.push($3);
   }
 ;

DerivedColumnChain_EDIT
 : ColumnIdentifier_EDIT
   {
     if ($1.insideKey) {
       suggestKeyValues({ identifierChain: [{ name: $1.name }] });
       suggestColumns();
       suggestFunctions();
     }
   }
 | DerivedColumnChain AnyDot ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       suggestKeyValues({ identifierChain: $1.concat({ name: $3.name }) });
       suggestColumns();
       suggestFunctions();
     }
   }
 | DerivedColumnChain AnyDot ColumnIdentifier_EDIT AnyDot DerivedColumnChain
   {
     if ($3.insideKey) {
       suggestKeyValues({ identifierChain: $1.concat({ name: $3.name }) });
       suggestColumns();
       suggestFunctions();
     }
   }
 | ColumnIdentifier_EDIT AnyDot DerivedColumnChain
   {
     if ($1.insideKey) {
       suggestKeyValues({ identifierChain: [{ name: $1.name }] });
       suggestColumns();
       suggestFunctions();
     }
   }
 | PartialBacktickedIdentifierOrPartialCursor
   {
     suggestColumns();
   }
 | DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor
   {
     suggestColumns({ identifierChain: $1 });
   }
 | DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor AnyDot DerivedColumnChain
   {
     suggestColumns({ identifierChain: $1 });
   }
 | PartialBacktickedIdentifierOrPartialCursor AnyDot DerivedColumnChain
   {
     suggestColumns();
   }
 ;

ColumnIdentifier
 : RegularOrBacktickedIdentifier OptionalMapOrArrayKey
   {
     if ($2) {
       $$ = { name: $1, keySet: true };
     } else {
       $$ = { name: $1 };
     }
   }
 ;

ColumnIdentifier_EDIT
 : RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket AnyCursor HiveOrImpalaRightSquareBracketOrError
   {
     $$ = { name: $1, insideKey: true }
   }
 | RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket ValueExpression_EDIT HiveOrImpalaRightSquareBracketOrError
   {
     $$ = { name: $1 }
   }
 ;

PartialBacktickedIdentifierOrPartialCursor
 : PartialBacktickedIdentifier
 | 'PARTIAL_CURSOR'
 ;

OptionalMapOrArrayKey
 :
 | HiveOrImpalaLeftSquareBracket ValueExpression HiveOrImpalaRightSquareBracket
 | HiveOrImpalaLeftSquareBracket HiveOrImpalaRightSquareBracket
 ;

HiveOrImpalaRightSquareBracketOrError
 : HiveOrImpalaRightSquareBracket
 | error
 ;

// TODO: Support | DECIMAL(precision, scale)  -- (Note: Available in Hive 0.13.0 and later)
PrimitiveType
 : 'TINYINT'
 | '<hive>TINYINT'
 | 'SMALLINT'
 | 'INT'
 | 'BIGINT'
 | 'BOOLEAN'
 | 'FLOAT'
 | 'DOUBLE'
 | '<impala>REAL'
 | 'STRING'
 | '<hive>STRING'
 | 'DECIMAL' OptionalTypePrecision
 | 'CHAR' OptionalTypeLength
 | 'VARCHAR' OptionalTypeLength
 | 'TIMESTAMP'
 | '<hive>BINARY'
 | '<hive>DATE'
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
 : HiveDescribeStatement
 | ImpalaDescribeStatement
 ;

DescribeStatement_EDIT
 : HiveDescribeStatement_EDIT
 | ImpalaDescribeStatement_EDIT
 ;

HiveDescribeStatement
 : '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain
   {
     addTablePrimary($3);
     addColumnLocation(@4, $4);
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier
   {
     addTablePrimary($3);
   }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalHiveExtended DatabaseIdentifier
   {
     addDatabaseLocation(@4, [{ name: $4 }]);
   }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalHiveExtended RegularIdentifier
 ;

HiveDescribeStatement_EDIT
 : '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain_EDIT
   {
     addTablePrimary($3);
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier DerivedColumnChain
   {
     if (!$2) {
       suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier
   {
     if (!$2) {
       suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier 'CURSOR'
   {
     addTablePrimary($3);
     suggestColumns();
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'FUNCTION', 'SCHEMA']);
     }
     suggestTables();
     suggestDatabases({ appendDot: true });
    }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalHiveExtended DatabaseIdentifier_EDIT
   {
     if (!$3) {
       suggestKeywords(['EXTENDED']);
     }
   }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalHiveExtended 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        suggestKeywords(['EXTENDED']);
      }
    }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalHiveExtended 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['EXTENDED']);
     }
   }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalHiveExtended 'CURSOR' RegularIdentifier
    {
      if (!$3) {
        suggestKeywords(['EXTENDED']);
      }
    }
 ;

ImpalaDescribeStatement
 : '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted SchemaQualifiedTableIdentifier
   {
     addTablePrimary($3);
   }
 | '<impala>DESCRIBE' 'DATABASE' OptionalImpalaExtendedOrFormatted DatabaseIdentifier
   {
     addDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

ImpalaDescribeStatement_EDIT
 : '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       suggestKeywords([{ value: 'DATABASE', weight: 2 }, { value: 'EXTENDED', weight: 1 }, { value: 'FORMATTED', weight: 1 }]);
     }
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier
   {
     addTablePrimary($4);
     if (!$2) {
       suggestKeywords([{ value: 'DATABASE', weight: 2 }, { value: 'EXTENDED', weight: 1 }, { value: 'FORMATTED', weight: 1 }]);
     }
   }
 | '<impala>DESCRIBE' 'DATABASE' OptionalImpalaExtendedOrFormatted 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
     suggestDatabases();
   }
 | '<impala>DESCRIBE' 'DATABASE' OptionalImpalaExtendedOrFormatted 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        suggestKeywords(['EXTENDED', 'FORMATTED']);
      }
      addDatabaseLocation(@5, [{ name: $5 }]);
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
     addCommonTableExpressions($1);
   }
 | CommonTableExpression SelectStatement_EDIT OptionalUnions
   {
     addCommonTableExpressions($1);
   }
 | CommonTableExpression SelectStatement OptionalUnions_EDIT
   {
     addCommonTableExpressions($1);
   }
 | CommonTableExpression_EDIT
 | CommonTableExpression_EDIT '(' QuerySpecification ')'
 | CommonTableExpression_EDIT SelectStatement OptionalUnions
 ;

OptionallyParenthesizedSelectStatement
 : SelectStatement
 | '(' SelectStatement ')' // Impala specific
 ;

OptionallyParenthesizedSelectStatement_EDIT
 : SelectStatement_EDIT
 | '(' SelectStatement_EDIT RightParenthesisOrError
 ;

SelectStatement
 : 'SELECT' OptionalAllOrDistinct SelectList                  -> { selectList: $3 }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression  -> { selectList: $3, tableExpression: $4 }
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
     suggestKeywords(['ALL', 'DISTINCT', 'SELECT']);
   }
 | 'UNION' NewStatement 'CURSOR' SelectStatement
   {
     suggestKeywords(['ALL', 'DISTINCT']);
   }
 | 'UNION' NewStatement OptionalAllOrDistinct SelectStatement_EDIT
 ;

SelectStatement_EDIT
 : 'SELECT' OptionalAllOrDistinct SelectList_EDIT
   {
     if ($3.cursorAtStart) {
       var keywords = [];
       if ($2) {
         keywords = [{ value: '*', weight: 1099 }];
       } else {
         keywords = [{ value: '*', weight: 1099 }, 'ALL', 'DISTINCT'];
       }
       if (isImpala()) {
         keywords.push('STRAIGHT_JOIN');
       }
       suggestKeywords(keywords);
     } else {
       checkForSelectListKeywords($3);
     }
     if ($3.suggestFunctions) {
       suggestFunctions();
     }
     if ($3.suggestColumns) {
       suggestColumns({ identifierChain: [], source: 'select' });
     }
     if ($3.suggestTables) {
       suggestTables({ prependQuestionMark: true, prependFrom: true });
     }
     if ($3.suggestDatabases) {
       suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     }
     if ($3.suggestAggregateFunctions && (!$2 || $2 === 'ALL')) {
       suggestAggregateFunctions();
       suggestAnalyticFunctions();
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR'
   {
     var keywords = [];
     if ($2) {
       keywords = [{ value: '*', weight: 1099 }];
       if ($2 === 'ALL') {
         suggestAggregateFunctions();
         suggestAnalyticFunctions();
       }
     } else {
       keywords = [{ value: '*', weight: 1099 }, 'ALL', 'DISTINCT'];
       suggestAggregateFunctions();
       suggestAnalyticFunctions();
     }
     if (isImpala()) {
       keywords.push('STRAIGHT_JOIN');
     }
     suggestKeywords(keywords);
     suggestFunctions();
     suggestColumns({ identifierChain: [], source: 'select' });
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression_EDIT
 | 'SELECT' OptionalAllOrDistinct SelectList_EDIT TableExpression
   {
     selectListNoTableSuggest($3, $2);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'select';
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR' TableExpression
   {
     var keywords = [];
     if ($2) {
       keywords = [{ value: '*', weight: 1099 }];
       if ($2 === 'ALL') {
         suggestAggregateFunctions();
         suggestAnalyticFunctions();
       }
     } else {
       keywords = [{ value: '*', weight: 1099 }, 'ALL', 'DISTINCT'];
       suggestAggregateFunctions();
       suggestAnalyticFunctions();
     }
     if (isImpala()) {
       keywords.push('STRAIGHT_JOIN');
     }
     suggestKeywords(keywords);
     suggestFunctions();
     suggestColumns({ identifierChain: [], source: 'select' });
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' TableExpression
   {
     checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' TableExpression
   {
     checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR'
   {
     checkForSelectListKeywords($3);
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
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
 | WithQueries ',' WithQuery   -> $1.concat([$3]);
 ;

WithQueries_EDIT
 : WithQuery_EDIT
 | WithQueries ',' WithQuery_EDIT
 | WithQuery_EDIT ',' WithQueries
 | WithQueries ',' WithQuery_EDIT ',' WithQueries
 ;

WithQuery
 : RegularOrBacktickedIdentifier AnyAs '(' TableSubQueryInner ')'
 ;

WithQuery_EDIT
 : RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 | RegularOrBacktickedIdentifier AnyAs '(' AnyCursor RightParenthesisOrError
   {
     suggestKeywords(['SELECT']);
   }
 | RegularOrBacktickedIdentifier AnyAs '(' TableSubQueryInner_EDIT RightParenthesisOrError
 ;

OptionalAllOrDistinct
 :
 | '<hive>ALL'
 | 'ALL'
 | 'DISTINCT'
 ;

TableExpression
 : FromClause OptionalSelectConditions
 ;

TableExpression_EDIT
 : FromClause_EDIT OptionalSelectConditions
 | FromClause 'CURSOR' OptionalSelectConditions OptionalJoins
   {
     var keywords = [];

     if ($1) {
       if (!$1.hasLateralViews && typeof $1.tableReferenceList.hasJoinCondition !== 'undefined' && !$1.tableReferenceList.hasJoinCondition) {
         keywords.push({ value: 'ON', weight: 3 });
         if (isImpala()) {
           keywords.push({ value: 'USING', weight: 3 });
         }
       }
       if ($1.suggestKeywords) {
         keywords = createWeightedKeywords($1.suggestKeywords, 3);
       }
       if ($1.tableReferenceList.suggestJoinConditions) {
         suggestJoinConditions($1.tableReferenceList.suggestJoinConditions);
       }
       if ($1.tableReferenceList.suggestJoins) {
         suggestJoins($1.tableReferenceList.suggestJoins);
       }
       if (!$1.hasLateralViews && $1.tableReferenceList.suggestKeywords) {
         keywords = keywords.concat(createWeightedKeywords($1.tableReferenceList.suggestKeywords, 3));
       }

       // Lower the weights for 'TABLESAMPLE' and 'LATERAL VIEW'
       keywords.forEach(function (keyword) {
         if (keyword.value === 'TABLESAMPLE' || keyword.value === 'LATERAL VIEW') {
           keyword.weight = 1.1;
         }
       });

       if (!$1.hasLateralViews && $1.tableReferenceList.types) {
         var veKeywords = getValueExpressionKeywords($1.tableReferenceList);
         keywords = keywords.concat(veKeywords.suggestKeywords);
         if (veKeywords.suggestColRefKeywords) {
           suggestColRefKeywords(veKeywords.suggestColRefKeywords);
           addColRefIfExists($1.tableReferenceList);
         }
       }
     }

     if ($3.empty && $4 && $4.joinType.toUpperCase() === 'JOIN') {
       keywords = keywords.concat(['FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']);
       if (isHive()) {
         keywords = keywords.concat(['CROSS', 'LEFT SEMI']);
       } else if (isImpala()) {
         keywords = keywords.concat(['INNER', 'LEFT ANTI', 'LEFT SEMI', 'RIGHT ANTI', 'RIGHT SEMI']);
       } else {
         keywords.push('INNER');
       }
       suggestKeywords(keywords);
       return;
     }

     if ($3.suggestKeywords) {
       keywords = keywords.concat(createWeightedKeywords($3.suggestKeywords, 2));
     }

     if ($3.suggestFilters) {
       suggestFilters($3.suggestFilters);
     }
     if ($3.suggestGroupBys) {
       suggestGroupBys($3.suggestGroupBys);
     }
     if ($3.suggestOrderBys) {
       suggestOrderBys($3.suggestOrderBys);
     }

     if ($3.empty) {
       keywords.push({ value: 'UNION', weight: 2.11 });
     }

     keywords = keywords.concat([{ value: 'FULL JOIN', weight: 1 }, { value: 'FULL OUTER JOIN', weight: 1 }, { value: 'JOIN', weight: 1 }, { value: 'LEFT JOIN', weight: 1 }, { value: 'LEFT OUTER JOIN', weight: 1 }, { value: 'RIGHT JOIN', weight: 1 }, { value: 'RIGHT OUTER JOIN', weight: 1 }]);
     if (isHive()) {
       keywords = keywords.concat([{ value: 'CROSS JOIN', weight: 1 }, { value: 'LEFT SEMI JOIN', weight: 1 }]);
     } else if (isImpala()) {
       keywords = keywords.concat([{ value: 'INNER JOIN', weight: 1 },  { value: 'LEFT ANTI JOIN', weight: 1 }, { value: 'LEFT SEMI JOIN', weight: 1 }, { value: 'RIGHT ANTI JOIN', weight: 1 }, { value: 'RIGHT SEMI JOIN', weight: 1 }]);
     } else {
       keywords.push({ value: 'INNER JOIN', weight: 1 });
     }
     suggestKeywords(keywords);
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
       return;
     }
     var keywords = [];

     if ($2.suggestColRefKeywords) {
       suggestColRefKeywords($2.suggestColRefKeywords);
       addColRefIfExists($2);
     }

     if ($2.suggestKeywords && $2.suggestKeywords.length) {
       keywords = keywords.concat(createWeightedKeywords($2.suggestKeywords, 2));
     }

     if ($2.cursorAtEnd) {
       keywords.push({ value: 'UNION', weight: 2.11 });
     }
     suggestKeywords(keywords);
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
     if (isHive()) {
       $$ = { tableReferenceList : $2, suggestKeywords: ['LATERAL VIEW'] }
     } else {
       $$ = { tableReferenceList : $2 }
     }
     if (isHive() && $3) {
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
       suggestTables();
       suggestDatabases({ appendDot: true });
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
 : OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR(
       [$1, $2, $3, $4, $5, $6, $6, $7, $8],
       [{ value: 'WHERE', weight: 9 }, { value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, true, isHive(), true, isHive(), isHive() && !$5, true, isImpala()]);

     if (keywords.length > 0) {
       $$ = { suggestKeywords: keywords, empty: !$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 };
     } else {
       $$ = {};
     }

     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8) {
       $$.suggestFilters = { prefix: 'WHERE', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8) {
       $$.suggestGroupBys = { prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$5 && !$6 && !$7 && !$8) {
       $$.suggestOrderBys = { prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause_EDIT OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'where';
     }
     if ($1.emptyFilter) {
       suggestFilters({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | OptionalWhereClause GroupByClause_EDIT OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'group by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause_EDIT OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'order by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OffsetClause_EDIT
 ;

OptionalSelectConditions_EDIT
 : WhereClause 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR(
       [$3, $4, $5, $6, $7, $7, $8, $9],
       [{ value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, isHive(), true, isHive(), isHive() && !$6, true, isImpala()]);
     if ($1.suggestKeywords) {
       keywords = keywords.concat(createWeightedKeywords($1.suggestKeywords, 1));
     }
     $$ = getValueExpressionKeywords($1, keywords);
     $$.cursorAtEnd = !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9;
     if ($1.columnReference) {
       $$.columnReference = $1.columnReference;
     }
     if (!$3) {
       suggestGroupBys({ prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     if (!$3 && !$4 && !$5 && !$6) {
       suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | OptionalWhereClause GroupByClause 'CURSOR' OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR(
       [$4, $5, $6, $7, $7, $8, $9],
       [{ value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, isHive(), true, isHive(), isHive() && !$6, true, isImpala()]);
     if ($2.suggestKeywords) {
       keywords = keywords.concat(createWeightedKeywords($2.suggestKeywords, 8));
     }
     $$ = getValueExpressionKeywords($2, keywords);
     if ($2.columnReference) {
       $$.columnReference = $2.columnReference;
     }
     $$.cursorAtEnd = !$4 && !$5 && !$6 && !$7 && !$8 && !$9;
     if (!$4 && !$5 && !$6) {
       suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause 'CURSOR' OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR(
       [$5, $6, $7, $7, $8, $9],
       [{ value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [isHive(), true, isHive(), isHive() && !$6, true, isImpala()]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$5 && !$6 && !$7 && !$8 && !$9 };
     if (!$5 && !$6) {
       suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause 'CURSOR' OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR([$6, $7, $8, $9], [{ value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, isHive(), true, isImpala()]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$6 && !$7 && !$8 && !$9 };
     if (!$6) {
       suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }

   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause 'CURSOR' OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR([$7, $8, $9], [[{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [isHive(), true, isImpala()]);
     if ($5.suggestKeywords) {
       keywords = keywords.concat(createWeightedKeywords($5.suggestKeywords, 5));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$7 && !$8 && !$9 };
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy 'CURSOR' OptionalLimitClause OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR([$8, $9], [{ value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, isImpala()]);
     if ($6.suggestKeywords) {
       keywords = keywords.concat(createWeightedKeywords($6.suggestKeywords, 4));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$8 && !$9 };
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause 'CURSOR' OptionalOffsetClause
   {
     var keywords = getKeywordsForOptionalsLR([$9], [{ value: 'OFFSET', weight: 2 }], [isImpala()]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$9 };
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
 | 'WHERE' 'CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     suggestKeywords(['EXISTS', 'NOT EXISTS']);
     $$ = { emptyFilter: true }
   }
 ;

OptionalGroupByClause
 :
 | GroupByClause
 ;

GroupByClause
 : AnyGroup 'BY' GroupByColumnList OptionalHiveGroupingSetsCubeOrRollup
   {
     if (!$4) {
       $$ = $3;
       if (isHive()) {
         if (!$$.suggestKeywords) {
           $$.suggestKeywords = [];
         }
         $$.suggestKeywords.push('GROUPING SETS');
         $$.suggestKeywords.push('WITH CUBE');
         $$.suggestKeywords.push('WITH ROLLUP');
       }
     }
   }
 ;

GroupByClause_EDIT
 : AnyGroup 'BY' GroupByColumnList_EDIT OptionalHiveGroupingSetsCubeOrRollup
   {
     suggestSelectListAliases();
   }
 | AnyGroup 'BY' 'CURSOR' OptionalHiveGroupingSetsCubeOrRollup
   {
     valueExpressionSuggest();
     suggestSelectListAliases();
     suggestGroupBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 | AnyGroup 'CURSOR'
   {
     suggestKeywords(['BY']);
     suggestGroupBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 | AnyGroup 'BY' GroupByColumnList OptionalHiveGroupingSetsCubeOrRollup_EDIT
 ;

OptionalHiveGroupingSetsCubeOrRollup
 :
 | HiveGroupingSets
 | 'WITH' '<hive>CUBE'
 | 'WITH' '<hive>ROLLUP'
 ;

OptionalHiveGroupingSetsCubeOrRollup_EDIT
 : HiveGroupingSets_EDIT
 | 'WITH' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['CUBE', 'ROLLUP']);
     }
   }
 ;

HiveGroupingSets
 : '<hive>GROUPING' '<hive>SETS' '(' ColumnGroupingSets ')'
 ;

HiveGroupingSets_EDIT
 : '<hive>GROUPING' 'CURSOR'
   {
     suggestKeywords(['SETS']);
   }
 | '<hive>GROUPING' '<hive>SETS' '(' ColumnGroupingSets_EDIT RightParenthesisOrError
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
     suggestColumns();
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
     valueExpressionSuggest();
   }
 | 'CURSOR' ',' GroupByColumnList
   {
     valueExpressionSuggest();
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
     valueExpressionSuggest();
   }
 | AnyCursor
   {
     valueExpressionSuggest();
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
       suggestOrderBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | 'ORDER' 'CURSOR'
   {
     suggestKeywords(['BY']);
     suggestOrderBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
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
     valueExpressionSuggest();
     suggestAnalyticFunctions();
     suggestSelectListAliases();
   }
 | OrderByColumnList ',' OrderByIdentifier_EDIT                        -> { emptyOrderBy: false }
 | OrderByColumnList ',' OrderByIdentifier_EDIT ','                    -> { emptyOrderBy: false }
 | OrderByColumnList ',' OrderByIdentifier_EDIT ',' OrderByColumnList  -> { emptyOrderBy: false }
 ;

OrderByIdentifier
 : ValueExpression OptionalAscOrDesc OptionalImpalaNullsFirstOrLast  -> mergeSuggestKeywords($2, $3)
 ;

OrderByIdentifier_EDIT
 : ValueExpression_EDIT OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
   {
     suggestSelectListAliases();
   }
 | ValueExpression OptionalAscOrDesc OptionalImpalaNullsFirstOrLast_EDIT
 | AnyCursor OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
   {
     $$ = { emptyOrderBy: true }
     valueExpressionSuggest();
     suggestAnalyticFunctions();
     suggestSelectListAliases();
   }
 ;

OptionalAscOrDesc
 :
  {
    $$ = { suggestKeywords: ['ASC', 'DESC'] };
  }
 | 'ASC'
 | '<hive>ASC'
 | 'DESC'
 | '<hive>DESC'
 ;

OptionalImpalaNullsFirstOrLast
 :
  {
    if (isImpala()) {
      $$ = { suggestKeywords: ['NULLS FIRST', 'NULLS LAST'] };
    } else {
      $$ = {};
    }
  }
 | '<impala>NULLS' '<impala>FIRST'
 | '<impala>NULLS' '<impala>LAST'
 ;

OptionalImpalaNullsFirstOrLast_EDIT
 : '<impala>NULLS' 'CURSOR'
   {
     suggestKeywords(['FIRST', 'LAST']);
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
 : '<hive>CLUSTER' 'BY' ColumnList
 ;

ClusterByClause_EDIT
 : '<hive>CLUSTER' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | '<hive>CLUSTER' 'BY' 'CURSOR'
   {
     suggestColumns();
     suggestSelectListAliases();
   }
 | '<hive>CLUSTER' 'BY' ColumnList_EDIT
   {
     suggestSelectListAliases();
   }
 ;

DistributeByClause
 : '<hive>DISTRIBUTE' 'BY' ColumnList
 ;

DistributeByClause_EDIT
 : '<hive>DISTRIBUTE' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | '<hive>DISTRIBUTE' 'BY' 'CURSOR'
   {
     suggestColumns();
     suggestSelectListAliases();
   }
 | '<hive>DISTRIBUTE' 'BY' ColumnList_EDIT
   {
     suggestSelectListAliases();
   }
 ;

SortByClause
 : '<hive>SORT' 'BY' SortByList  -> $3
 ;

SortByClause_EDIT
 : '<hive>SORT' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | '<hive>SORT' 'BY' SortByList_EDIT
   {
     suggestSelectListAliases();
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
 : ColumnIdentifier OptionalAscOrDesc  -> $2
 ;

SortByIdentifier_EDIT
 : ColumnIdentifier_EDIT OptionalAscOrDesc
 | AnyCursor OptionalAscOrDesc
   {
     suggestColumns();
   }
 ;

OptionalLimitClause
 :
 | LimitClause
 ;

LimitClause
 : 'LIMIT' UnsignedNumericLiteral
 | '<impala>LIMIT' ValueExpression
 ;

LimitClause_EDIT
 : 'LIMIT' 'CURSOR'
 | '<impala>LIMIT' 'CURSOR'
   {
     suggestFunctions({ types: ['BIGINT'] });
   }
 | '<impala>LIMIT' ValueExpression_EDIT
   {
     delete parser.yy.result.suggestColumns;
   }
 ;

OptionalOffsetClause
 :
 | OffsetClause
 ;

OffsetClause
 : '<impala>OFFSET' ValueExpression
 ;

OffsetClause_EDIT
 : '<impala>OFFSET' 'CURSOR'
   {
     suggestFunctions({ types: ['BIGINT'] });
   }
 | '<impala>OFFSET' ValueExpression_EDIT
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
     suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'LIKE']);
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
     // $3.position = $1.position + 1;
     // $$ = $3
     $1.position += 1;
   }
 | ValueExpressionList ',' AnyCursor
   {
     valueExpressionSuggest();
     $1.position += 1;
   }
 | ValueExpressionList ',' AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
     $1.position += 1;
   }
 | ValueExpressionList 'CURSOR' ',' ValueExpressionList
   {
     suggestValueExpressionKeywords($1);
   }
 | AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
     $$ = { cursorAtStart : true, position: 1 };
   }
 | AnyCursor ','
   {
     valueExpressionSuggest();
     $$ = { cursorAtStart : true, position: 1 };
   }
 | ',' AnyCursor
   {
     valueExpressionSuggest();
     $$ = { position: 2 };
   }
 | ',' AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
     $$ = { position: 2 };
   }
 ;

InValueList
 : NonParenthesizedValueExpressionPrimary
 | InValueList ',' NonParenthesizedValueExpressionPrimary
 ;

InValueList_EDIT
 : NonParenthesizedValueExpressionPrimary_EDIT
 | InValueList ',' AnyCursor
 | InValueList ',' NonParenthesizedValueExpressionPrimary_EDIT
 | InValueList ',' NonParenthesizedValueExpressionPrimary_EDIT ',' InValueList
 | NonParenthesizedValueExpressionPrimary_EDIT ',' InValueList
 ;

NonParenthesizedValueExpressionPrimary
 : UnsignedValueSpecification
 | ColumnReference             -> { types: ['COLREF'], columnReference: $1 }
 | UserDefinedFunction
 | 'NULL'                      -> { types: [ 'NULL' ] }
 | ImpalaInterval              -> { types: [ 'TIMESTAMP' ] }
 ;

NonParenthesizedValueExpressionPrimary_EDIT
 : UnsignedValueSpecification_EDIT
 | ColumnReference_EDIT
   {
     if ($1.suggestKeywords) {
       $$ = { types: ['COLREF'], columnReference: $1, suggestKeywords: $1.suggestKeywords };
     } else {
       $$ = { types: ['COLREF'], columnReference: $1 };
     }
   }
 | UserDefinedFunction_EDIT
 | ImpalaInterval_EDIT
 ;

ImpalaInterval
 : '<impala>INTERVAL' SignedInteger RegularIdentifier
 ;

ImpalaInterval_EDIT
 : '<impala>INTERVAL' SignedInteger 'CURSOR'
   {
     suggestKeywords(['DAYS', 'HOURS', 'MICROSECONDS', 'MILLISECONDS', 'MINUTES', 'MONTHS', 'NANOSECONDS', 'SECONDS', 'WEEKS', 'YEARS']);
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
     suggestValues($1);
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
 | 'UNSIGNED_INTEGER' AnyDot
 | 'UNSIGNED_INTEGER' AnyDot 'UNSIGNED_INTEGER'
 | AnyDot 'UNSIGNED_INTEGER'
 ;

ApproximateNumericLiteral
 : UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | AnyDot UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER' AnyDot UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 ;

GeneralLiteral
 : SingleQuotedValue  -> { types: [ 'STRING' ] }
 | DoubleQuotedValue  -> { types: [ 'STRING' ] }
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
       $$ = { valueExpression: $1, alias: $2 };
       if (!parser.yy.selectListAliases) {
         parser.yy.selectListAliases = [];
       }
       parser.yy.selectListAliases.push({ name: $2, types: $1.types || ['T'] });
     } else {
       $$ = { valueExpression: $1 }
     }
   }
 | '*'
   {
     addAsteriskLocation(@1, [{ asterisk: true }]);
     $$ = { asterisk: true }
   }
 ;

SelectSpecification_EDIT
 : ValueExpression_EDIT OptionalCorrelationName
 | AnyCursor AnyAs RegularOrBacktickedIdentifier
   {
     suggestFunctions();
     suggestColumns();
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
     checkForSelectListKeywords($1);
   }
 | SelectList 'CURSOR' ',' SelectList
   {
     checkForSelectListKeywords($1);
   }
 | SelectList ',' AnyCursor
   {
     $$ = { suggestKeywords: [{ value: '*', weight: 1099 }], suggestTables: true, suggestDatabases: true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | SelectList ',' SelectSpecification_EDIT                 -> $3
 | SelectList ',' AnyCursor SelectList
   {
     $$ = { suggestKeywords: [{ value: '*', weight: 1099 }], suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' AnyCursor ','
   {
     $$ = { suggestKeywords: [{ value: '*', weight: 1099 }], suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' SelectSpecification_EDIT ','             -> $3
 | SelectList ',' AnyCursor ',' SelectList
   {
     $$ = { suggestKeywords: [{ value: '*', weight: 1099 }], suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' SelectSpecification_EDIT ',' SelectList  -> $3
 ;

DerivedColumn_TWO
 : ColumnIdentifier
   {
     addColumnLocation(@1, [$1]);
   }
 | ColumnIdentifier AnyDot '*'
   {
     addColumnLocation(@1, [$1]);
   }
 | ColumnIdentifier AnyDot DerivedColumnChain
   {
     addColumnLocation(@2, [$1].concat($3));
   }
 ;

DerivedColumn_EDIT_TWO
 : ColumnIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $1.key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $1 ]
     });
   }
 | ColumnIdentifier AnyDot DerivedColumnChain '<impala>.' 'PARTIAL_CURSOR'
   {
      $3.unshift($1);
      suggestColumns({
        identifierChain: $3
      });
    }
 | ColumnIdentifier AnyDot DerivedColumnChain '<hive>.' 'PARTIAL_CURSOR'
   {
      $3.unshift($1);
      suggestColumns({
        identifierChain: $3
      });
    }
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
       suggestTables();
       suggestDatabases({ appendDot: true });
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
 : JoinType OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
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
     parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
   }
 | Joins JoinType OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
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
     parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
   }
 ;

Joins_INVALID
 : JoinType OptionalImpalaBroadcastOrShuffle                                           -> { joinType: $1 }
 | JoinType OptionalImpalaBroadcastOrShuffle Joins                                     -> { joinType: $1 }
 ;

OptionalImpalaBroadcastOrShuffle
 :
 | '<impala>BROADCAST'
 | '<impala>SHUFFLE'
 ;

Join_EDIT
 : JoinType_EDIT OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
 | JoinType_EDIT OptionalImpalaBroadcastOrShuffle
 | JoinType OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT OptionalJoinCondition
 | JoinType OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | JoinType OptionalImpalaBroadcastOrShuffle 'CURSOR' OptionalJoinCondition
   {
     if (!$2 && isImpala()) {
       suggestKeywords(['[BROADCAST]', '[SHUFFLE]']);
     }
     if (!$2) {
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
         suggestJoins({
           prependJoin: false,
           joinType: $1,
           tables: tables
         })
       }
     }
     suggestTables();
     suggestDatabases({
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
 | '<hive>CROSS' 'JOIN'           -> 'CROSS JOIN'
 | 'INNER' 'JOIN'                 -> 'INNER JOIN'
 | 'FULL' 'JOIN'                  -> 'FULL JOIN'
 | 'FULL' 'OUTER' 'JOIN'          -> 'FULL OUTER JOIN'
 | 'LEFT' 'JOIN'                  -> 'LEFT JOIN'
 | 'LEFT' '<impala>ANTI' 'JOIN'   -> 'LEFT ANTI JOIN'
 | 'LEFT' 'OUTER' 'JOIN'          -> 'LEFT OUTER JOIN'
 | 'LEFT' 'SEMI' 'JOIN'           -> 'LEFT SEMI JOIN'
 | 'RIGHT' 'JOIN'                 -> 'RIGHT JOIN'
 | 'RIGHT' '<impala>ANTI' 'JOIN'  -> 'RIGHT ANTI JOIN'
 | 'RIGHT' 'OUTER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'SEMI' 'JOIN'          -> 'RIGHT SEMI JOIN'
 ;

JoinType_EDIT
 : '<hive>CROSS' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'INNER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'FULL' 'OUTER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'FULL' 'CURSOR' 'JOIN'
   {
     suggestKeywords(['OUTER']);
   }
 | 'LEFT' 'SEMI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'LEFT' 'OUTER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'LEFT' '<impala>ANTI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'LEFT' 'CURSOR' 'JOIN'
   {
     if (isImpala()) {
       suggestKeywords(['ANTI', 'OUTER', 'SEMI']);
     } else if (isHive()) {
       suggestKeywords(['OUTER', 'SEMI']);
     } else {
       suggestKeywords(['OUTER']);
     }
   }
 | 'RIGHT' '<impala>ANTI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'RIGHT' 'OUTER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'RIGHT' 'SEMI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'RIGHT' 'CURSOR' 'JOIN'
   {
     if (isImpala()) {
       suggestKeywords(['ANTI', 'SEMI', 'OUTER']);
     } else {
       suggestKeywords(['OUTER']);
     }
   }
 ;

OptionalJoinCondition
 :                                       -> { noJoinCondition: true, suggestKeywords: isImpala() ? ['ON', 'USING'] : ['ON'] }
 | 'ON' ValueExpression                  -> { valueExpression: $2 }
 | '<impala>USING' '(' UsingColList ')'  -> {}
 ;

UsingColList
 : RegularOrBacktickedIdentifier
 | UsingColList ',' RegularOrBacktickedIdentifier
 ;

JoinCondition_EDIT
 : 'ON' ValueExpression_EDIT
 | 'ON' 'CURSOR'
   {
     valueExpressionSuggest();
     suggestJoinConditions({ prependOn: false });
   }
 ;

TablePrimary
 : TableOrQueryName OptionalTableSample OptionalCorrelationName
   {
     if ($1.identifierChain) {
       if ($3) {
         $1.alias = $3
       }
       addTablePrimary($1);
     }
     // Right-to-left for cursor after TablePrimary
     $$.suggestKeywords = getKeywordsForOptionalsLR([$3, $2], [{ value: 'AS', weight: 1 }, { value: 'TABLESAMPLE', weight: 2 }], [true, isHive()]);
   }
 | DerivedTable OptionalCorrelationName
   {
     if ($2) {
       $1.alias = $2;
       addTablePrimary({ subQueryAlias: $2 });
     } else {
       $$.suggestKeywords = [{ value: 'AS', weight: 1 }];
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalTableSample OptionalCorrelationName
 | TableOrQueryName OptionalTableSample_EDIT OptionalCorrelationName
   {
     if ($3) {
       $1.alias = $3;
     }
     addTablePrimary($1);
   }
 | DerivedTable_EDIT OptionalCorrelationName
   {
     if ($2) {
       addTablePrimary({ subQueryAlias: $2 });
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
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' '<hive>OF' 'UNSIGNED_INTEGER' OptionalOnColumn ')'
 ;

OptionalTableSample_EDIT
 : '<hive>TABLESAMPLE' '(' AnyCursor RightParenthesisOrError
   {
     suggestKeywords(['BUCKET']);
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(['OUT OF']);
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(['OF']);
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' '<hive>OF' 'UNSIGNED_INTEGER' OptionalOnColumn 'CURSOR' RightParenthesisOrError
   {
     if (!$8) {
       suggestKeywords(['ON']);
     }
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' '<hive>OF' 'UNSIGNED_INTEGER' OptionalOnColumn_EDIT RightParenthesisOrError
 ;

OptionalOnColumn
 :
 | 'ON' ValueExpression
 ;

OptionalOnColumn_EDIT
 : 'ON' 'CURSOR'
   {
     valueExpressionSuggest();
   }
 | 'ON' ValueExpression_EDIT
 ;

PushQueryState
 :
   {
     pushQueryState();
   }
 ;

PopQueryState
 :
   {
     popQueryState();
   }
 ;

TableSubQuery
 : '(' TableSubQueryInner ')'  -> $2
 | '(' DerivedTable OptionalCorrelationName ')'
   {
     if ($3) {
       $2.alias = $3;
       addTablePrimary({ subQueryAlias: $3 });
     }
     $$ = $2;
   }
 ;

TableSubQuery_EDIT
 : '(' TableSubQueryInner_EDIT RightParenthesisOrError
 | '(' AnyCursor RightParenthesisOrError
   {
     suggestKeywords(['SELECT']);
   }
 ;

TableSubQueryInner
 : PushQueryState SubQuery
   {
     var subQuery = getSubQuery($2);
     subQuery.columns.forEach(function (column) {
       expandIdentifierChain(column);
       delete column.linked;
     });
     popQueryState(subQuery);
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
 | RegularOrBacktickedIdentifier
 | AnyAs RegularOrBacktickedIdentifier  -> $2
 ;

OptionalCorrelationName_EDIT
 : PartialBacktickedIdentifier
 | AnyAs PartialBacktickedIdentifier
 | AnyAs 'CURSOR'
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
 : ArbitraryFunction
 | AggregateFunction OptionalOverClause
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
 : ArbitraryFunction_EDIT
 | AggregateFunction_EDIT
 | AggregateFunction OptionalOverClause_EDIT
 | AnalyticFunction_EDIT
 | AnalyticFunction_EDIT OverClause
 | AnalyticFunction 'CURSOR'
   {
     suggestKeywords(['OVER']);
   }
 | AnalyticFunction OverClause_EDIT
 | CastFunction_EDIT
 | ExtractFunction_EDIT
 ;

ArbitraryFunction
 : RegularIdentifier ArbitraryFunctionRightPart
   {
     addFunctionLocation(@1, $1);
     if ($2.expression) {
       $$ = { function: $1, expression: $2.expression, types: findReturnTypes($1) }
     } else {
       $$ = { function: $1, types: findReturnTypes($1) }
     }
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart
   {
     addFunctionLocation(@1, $1);
     if ($2.expression) {
       $$ = { function: $1, expression: $2.expression, types: findReturnTypes($1) }
     } else {
       $$ = { function: $1, types: findReturnTypes($1) }
     }
   }
 ;

ArbitraryFunction_EDIT
 : RegularIdentifier ArbitraryFunctionRightPart_EDIT
   {
     addFunctionLocation(@1, $1);
     if ($2.position) {
       applyArgumentTypesToSuggestions($1, $2.position);
     }
     $$ = { types: findReturnTypes($1) };
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart_EDIT
   {
     addFunctionLocation(@1, $1);
     if ($2.position) {
       applyArgumentTypesToSuggestions($1, $2.position);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

ArbitraryFunctionName
 : 'IF'
 | '<hive>ARRAY'
 | '<hive>BINARY'
 | '<hive>MAP'
 ;

ArbitraryFunctionRightPart
 : '(' ')'
 | '(' ValueExpressionList ')'  -> { expression: $2 }
 ;

ArbitraryFunctionRightPart_EDIT
 : '(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { position: 1 }
   }
 | '(' ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3);
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
 : 'ANALYTIC' '(' ')'                      -> { types: findReturnTypes($1) }
 | 'ANALYTIC' '(' ValueExpressionList ')'  -> { function: $1, expression: $2, types: findReturnTypes($1) }
 ;

AnalyticFunction_EDIT
 : 'ANALYTIC' '(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyArgumentTypesToSuggestions($1, 1);
     $$ = { types: findReturnTypes($1) };
   }
 | 'ANALYTIC' '(' ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3);
     $$ = { types: findReturnTypes($1) };
   }
 | 'ANALYTIC' '(' ValueExpressionList_EDIT RightParenthesisOrError
   {
     applyArgumentTypesToSuggestions($1, $3.position);
     $$ = { types: findReturnTypes($1) };
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
 | '(' OptionalPartitionBy OptionalOrderByAndWindow_EDIT RightParenthesisOrError
 | '(' AnyCursor OptionalPartitionBy OptionalOrderByAndWindow RightParenthesisOrError
   {
     if (!$3 && !$4) {
       suggestKeywords([{ value: 'PARTITION BY', weight: 2 }, { value: 'ORDER BY', weight: 1 }]);
     } else if (!$3) {
       suggestKeywords(['PARTITION BY']);
     }
   }
 | '(' AnyPartition 'BY' ValueExpressionList 'CURSOR' OptionalOrderByAndWindow RightParenthesisOrError
    {
      if (!$6) {
        suggestValueExpressionKeywords($4, [{ value: 'ORDER BY', weight: 2 }]);
      } else {
        suggestValueExpressionKeywords($4);
      }
    }
  ;

OptionalPartitionBy
 :
 | PartitionBy
 ;

PartitionBy
 : AnyPartition 'BY' ValueExpressionList  -> $3
 ;

PartitionBy_EDIT
 : AnyPartition 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | AnyPartition 'BY' 'CURSOR'
   {
     valueExpressionSuggest();
   }
 | AnyPartition 'BY' ValueExpressionList_EDIT
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
        keywords = createWeightedKeywords($1.suggestKeywords, 2);
      }
      if (!$3) {
        keywords = keywords.concat([{ value: 'RANGE BETWEEN', weight: 1 }, { value: 'ROWS BETWEEN', weight: 1 }]);
      }
      suggestKeywords(keywords);
    }
  | OrderByClause WindowSpec_EDIT
  ;

OptionalWindowSpec
 :
 | WindowSpec
 ;

WindowSpec
 : RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing
 ;

WindowSpec_EDIT
 : RowsOrRange 'CURSOR'
   {
     suggestKeywords(['BETWEEN']);
   }
 | RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing 'CURSOR'
   {
     if (!$4 && !$5) {
       suggestKeywords(['CURRENT ROW', 'UNBOUNDED PRECEDING']);
     } else if (!$5) {
       suggestKeywords(['AND']);
     }
   }
 | RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding_EDIT OptionalAndFollowing
 | RowsOrRange 'BETWEEN' PopLexerState OptionalCurrentOrPreceding OptionalAndFollowing_EDIT
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
      suggestHdfs({ path: $2 });
    }
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'
   {
     suggestHdfs({ path: $2 });
   }
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR'
    {
      suggestHdfs({ path: $2 });
    }
 | 'HDFS_START_QUOTE' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'
   {
     suggestHdfs({ path: '' });
   }
 | 'HDFS_START_QUOTE' 'PARTIAL_CURSOR'
    {
      suggestHdfs({ path: '' });
    }
 ;

RowsOrRange
 : 'ROWS'
 | 'RANGE'
 ;

OptionalCurrentOrPreceding
 :
 | IntegerOrUnbounded 'PRECEDING'
 | AnyCurrent 'ROW'
 ;

OptionalCurrentOrPreceding_EDIT
 : IntegerOrUnbounded 'CURSOR'
   {
     suggestKeywords(['PRECEDING']);
   }
 | AnyCurrent 'CURSOR'
   {
     suggestKeywords(['ROW']);
   }
 ;

AnyCurrent
 : 'CURRENT'
 | '<hive>CURRENT'
 | '<impala>CURRENT'
 ;

OptionalAndFollowing
 :
 | 'AND' AnyCurrent 'ROW'
 | 'AND' IntegerOrUnbounded 'FOLLOWING'
 ;

OptionalAndFollowing_EDIT
 : 'AND' 'CURSOR'
   {
     suggestKeywords(['CURRENT ROW', 'UNBOUNDED FOLLOWING']);
   }
 | 'AND' AnyCurrent 'CURSOR'
   {
     suggestKeywords(['ROW']);
   }
 | 'AND' IntegerOrUnbounded 'CURSOR'
   {
     suggestKeywords(['FOLLOWING']);
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
     valueExpressionSuggest();
     suggestAggregateFunctions();
     suggestSelectListAliases(true);
   }
 | 'HAVING' ValueExpression_EDIT
   {
     suggestAggregateFunctions();
     suggestSelectListAliases(true);
   }
 ;

OptionalWindowClause
 :
 | WindowClause
 ;

WindowClause
 : '<hive>WINDOW' RegularOrBacktickedIdentifier '<hive>AS' WindowExpression
 ;

WindowClause_EDIT
 : '<hive>WINDOW' RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 | '<hive>WINDOW' RegularOrBacktickedIdentifier '<hive>AS' WindowExpression_EDIT
 ;

CastFunction
 : 'CAST' '(' ValueExpression AnyAs PrimitiveType ')'  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ')'                                      -> { types: [ 'T' ] }
 ;

CastFunction_EDIT
 : 'CAST' '(' AnyCursor AnyAs PrimitiveType RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' AnyCursor AnyAs RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression_EDIT AnyAs PrimitiveType RightParenthesisOrError  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ValueExpression_EDIT AnyAs RightParenthesisOrError                -> { types: [ 'T' ] }
 | 'CAST' '(' ValueExpression_EDIT RightParenthesisOrError                      -> { types: [ 'T' ] }
 | 'CAST' '(' ValueExpression 'CURSOR' PrimitiveType RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3, [{ value: 'AS', weight: 2 }]);
     $$ =  { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3, [{ value: 'AS', weight: 2 }]);
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression AnyAs 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' AnyAs 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 ;

CountFunction
 : 'COUNT' '(' '*' ')'                                        -> { types: findReturnTypes($1) }
 | 'COUNT' '(' ')'                                            -> { types: findReturnTypes($1) }
 | 'COUNT' '(' OptionalAllOrDistinct ValueExpressionList ')'  -> { types: findReturnTypes($1) }
 ;

CountFunction_EDIT
 : 'COUNT' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     if (!$3) {
       var keywords = isImpala() ? [{ value: '*', weight: 1099 }, 'ALL', 'DISTINCT'] : [{ value: '*', weight: 1099 }, 'DISTINCT'];
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
       suggestKeywords(keywords);
     }
     $$ = { types: findReturnTypes($1) };
   }
 | 'COUNT' '(' OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($4);
     $$ = { types: findReturnTypes($1) };
   }
 | 'COUNT' '(' OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart && !$3) {
       if (isImpala()) {
         suggestKeywords(['ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['DISTINCT']);
       }
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

OtherAggregateFunction
 : OtherAggregateFunction_Type '(' OptionalAllOrDistinct ')'                      -> { types: findReturnTypes($1) }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ValueExpressionList ')'  -> { types: findReturnTypes($1) }
 ;

OtherAggregateFunction_EDIT
 : OtherAggregateFunction_Type '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     if (!$3) {
       var keywords = [];
       if ($1.toLowerCase() === 'group_concat') {
         keywords = ['ALL'];
       } else if (isImpala()) {
         keywords = ['ALL', 'DISTINCT'];
       } else {
         keywords = ['DISTINCT'];
       }
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
       suggestKeywords(keywords);
     }
     applyArgumentTypesToSuggestions($1, 1);
     $$ = { types: findReturnTypes($1) };
   }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($4);
     $$ = { types: findReturnTypes($1) };
   }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart && !$3) {
       var keywords = [];
       if ($1.toLowerCase() === 'group_concat') {
         keywords = ['ALL'];
       } else if (isImpala()) {
         keywords = ['ALL', 'DISTINCT'];
       } else {
         keywords = ['DISTINCT'];
       }
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
       suggestKeywords(keywords);
     }
     if (parser.yy.result.suggestFunctions && !parser.yy.result.suggestFunctions.types) {
       applyArgumentTypesToSuggestions($1, $4.position);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

OtherAggregateFunction_Type
 : '<impala>APPX_MEDIAN'
 | 'AVG'
 | '<hive>COLLECT_SET'
 | '<hive>COLLECT_LIST'
 | '<hive>CORR'
 | '<hive>COVAR_POP'
 | '<hive>COVAR_SAMP'
 | '<impala>GROUP_CONCAT'
 | '<hive>HISTOGRAM_NUMERI'
 | '<impala>STDDEV'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'MAX'
 | 'MIN'
 | '<hive>NTILE'
 | '<hive>PERCENTILE'
 | '<hive>PERCENTILE_APPROX'
 | 'VARIANCE'
 | '<impala>VARIANCE_POP'
 | '<impala>VARIANCE_SAMP'
 | 'VAR_POP'
 | 'VAR_SAMP'
 ;

ExtractFunction
 : '<impala>EXTRACT' '(' ValueExpression FromOrComma ValueExpression ')'
 | '<impala>EXTRACT' '(' ')'
 ;

ExtractFunction_EDIT
 : '<impala>EXTRACT' '(' AnyCursor FromOrComma ValueExpression RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' AnyCursor FromOrComma RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['STRING', 'TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression_EDIT FromOrComma ValueExpression RightParenthesisOrError
   {
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression_EDIT FromOrComma RightParenthesisOrError
   {
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression_EDIT RightParenthesisOrError
   {
     applyTypeToSuggestions(['STRING', 'TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression FromOrComma AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' FromOrComma AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
     applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
    applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression 'CURSOR' ValueExpression RightParenthesisOrError
   {
     if ($3.types[0] === 'STRING') {
       suggestValueExpressionKeywords($3, ['FROM']);
     } else {
       suggestValueExpressionKeywords($3);
     }
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     if ($3.types[0] === 'STRING') {
       suggestValueExpressionKeywords($3, ['FROM']);
     } else {
       suggestValueExpressionKeywords($3);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

FromOrComma
 : 'FROM'
 | ','
 ;

SumFunction
 : 'SUM' '(' OptionalAllOrDistinct ValueExpression ')'  -> { types: findReturnTypes($1) }
 | 'SUM' '(' ')'                                        -> { types: findReturnTypes($1) }
 ;

SumFunction_EDIT
 : 'SUM' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyArgumentTypesToSuggestions($1, 1);
     if (!$3) {
       var keywords = isImpala() ? ['ALL', 'DISTINCT'] : ['DISTINCT'];
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
       suggestKeywords(keywords);
     }
     $$ = { types: findReturnTypes($1) };
   }
 | 'SUM' '(' OptionalAllOrDistinct ValueExpression 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($4);
     $$ = { types: findReturnTypes($1) };
   }
 | 'SUM' '(' OptionalAllOrDistinct ValueExpression_EDIT RightParenthesisOrError
   {
     if (parser.yy.result.suggestFunctions && ! parser.yy.result.suggestFunctions.types) {
       applyArgumentTypesToSuggestions($1, 1);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

LateralView
 : '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction RegularOrBacktickedIdentifier LateralViewColumnAliases  -> { lateralView: { udtf: $4, tableAlias: $5, columnAliases: $6 }}
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction RegularOrBacktickedIdentifier
   {
     if ($4.function.toLowerCase() === 'explode') {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: ['key', 'value'] }, suggestKeywords: ['AS'] };
     } else if ($4.function.toLowerCase() === 'posexplode') {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: ['pos', 'val'] }, suggestKeywords: ['AS'] };
     } else {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: [] }, suggestKeywords: ['AS'] };
     }
   }
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction LateralViewColumnAliases                                -> { lateralView: { udtf: $4, columnAliases: $5 }}
 ;

LateralView_EDIT
 : '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction_EDIT
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction_EDIT RegularOrBacktickedIdentifier
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction_EDIT RegularOrBacktickedIdentifier LateralViewColumnAliases
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction RegularOrBacktickedIdentifier LateralViewColumnAliases_EDIT
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction PartialBacktickedOrCursor
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction PartialBacktickedOrCursor LateralViewColumnAliases
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter 'CURSOR'
   {
     if (!$3) {
       suggestKeywords([{ value: 'OUTER', weight: 2 }, { value: 'explode', weight: 1 }, { value: 'posexplode', weight: 1 }]);
     } else {
       suggestKeywords(['explode', 'posexplode']);
     }
   }
 | '<hive>LATERAL' 'CURSOR'
   {
     suggestKeywords(['VIEW']);
   }
 ;

OptionalOuter
 :
 | 'OUTER'
 ;

LateralViewColumnAliases
 : '<hive>AS' RegularOrBacktickedIdentifier                                    -> [ $2 ]
 | '<hive>AS' RegularOrBacktickedIdentifier ',' RegularOrBacktickedIdentifier  -> [ $2, $4 ]
 ;

LateralViewColumnAliases_EDIT
 : '<hive>AS' PartialBacktickedOrCursor
 | '<hive>AS' RegularOrBacktickedIdentifier ',' PartialBacktickedOrAnyCursor
 ;