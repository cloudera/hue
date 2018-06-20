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
     if (parser.isHive()) {
       parser.suggestDdlAndDmlKeywords(['EXPLAIN', 'FROM']);
     } else if (parser.isImpala()) {
       parser.suggestDdlAndDmlKeywords(['EXPLAIN']);
     } else {
       parser.suggestDdlAndDmlKeywords();
     }
   }
 | CommonTableExpression 'CURSOR'
   {
     if (parser.isHive() || parser.isImpala()) {
       parser.suggestKeywords(['INSERT', 'SELECT']);
     } else {
       parser.suggestKeywords(['SELECT']);
     }
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
 : '<hive>ABORT'
 | '<hive>ADD'
 | '<hive>ADMIN'
 | '<hive>AFTER'
 | '<hive>ANALYZE'
 | '<hive>ARCHIVE'
 | '<hive>AVRO'
 | '<hive>BUCKET'
 | '<hive>BUCKETS'
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
 | '<hive>DBPROPERTIES'
 | '<hive>DEFERRED'
 | '<hive>DEFINED'
 | '<hive>DELIMITED'
 | '<hive>DEPENDENCY'
 | '<hive>DIRECTORY'
 | '<hive>DISABLE'
 | '<hive>DOUBLE_PRECISION'
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
 | '<hive>KEY'
 | '<hive>KEYS'
 | '<hive>LINES'
 | '<hive>LOAD'
 | '<hive>LOCATION'
 | '<hive>LOCKS'
 | '<hive>MATCHED'
 | '<hive>METADATA'
 | '<hive>MERGE'
 | '<hive>MSCK'
 | '<hive>NOSCAN'
 | '<hive>NOVALIDATE'
 | '<hive>NO_DROP'
 | '<hive>OFFLINE'
 | '<hive>ORC'
 | '<hive>OUTPUTFORMAT'
 | '<hive>OVERWRITE'
 | '<hive>OWNER'
 | '<hive>PARQUET'
 | '<hive>PARTITIONED'
 | '<hive>PARTITIONS'
 | '<hive>PERCENT'
 | '<hive>PRIVILEGES'
 | '<hive>PURGE'
 | '<hive>RCFILE'
 | '<hive>REBUILD'
 | '<hive>RELOAD'
 | '<hive>RELY'
 | '<hive>NORELY'
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
 | 'STRUCT'
 | '<hive>TABLES'
 | '<hive>TBLPROPERTIES'
 | '<hive>TEMPORARY'
 | '<hive>TERMINATED'
 | '<hive>TEXTFILE'
 | '<hive>TIMESTAMP'
 | '<hive>TINYINT'
 | '<hive>TOUCH'
 | '<hive>TRANSACTIONS'
 | '<hive>UNARCHIVE'
 | '<hive>UNIONTYPE'
 | '<hive>USE'
 | '<hive>USER'
 | '<hive>VIEW'
 | '<hive>WAIT'
 | '<hive>DAY'
 | '<hive>HOUR'
 | '<hive>MINUTE'
 | '<hive>MONTH'
 | '<hive>QUARTER'
 | '<hive>SECOND'
 | '<hive>WEEK'
 | '<hive>YEAR'
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
// | '<impala>ANTI'
 | '<impala>CURRENT'
 | '<impala>GRANT'
 | '<impala>RECOVER'
 | '<impala>ROLE'
 | '<impala>ROLES'
 | '<impala>URI'
 | '<impala>SERVER'
 | '<impala>UNKNOWN'
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

ExplainClause
 : '<hive>EXPLAIN' OptionalHiveExplainTypes
 | '<impala>EXPLAIN'
 ;

ExplainClause_EDIT
 : '<hive>EXPLAIN' OptionalHiveExplainTypes 'CURSOR'
   {
     if (!$2) {
       parser.suggestDdlAndDmlKeywords([{ value: 'AUTHORIZATION', weight: 2 }, { value: 'DEPENDENCY', weight: 2 }, { value: 'EXTENDED', weight: 2 }]);
     } else {
       parser.suggestDdlAndDmlKeywords();
     }
   }
 | '<impala>EXPLAIN' 'CURSOR'
   {
     parser.suggestDdlAndDmlKeywords();
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
 : '<hive>ADMIN' | '<hive>ALL' | '<hive>AS' | '<hive>AUTHORIZATION' | '<hive>AVRO' | '<hive>BINARY' | '<hive>BUCKET' | '<hive>BUCKETS' | '<hive>CACHE' | '<hive>CLUSTER' | '<hive>CLUSTERED' | '<hive>COLLECTION' | '<hive>COMPUTE' | '<hive>CONF' | '<hive>CONSTRAINT' | '<hive>CUBE' | '<hive>CURRENT' | '<hive>DBPROPERTIES' | '<hive>DATE' | '<hive>DEFERRED' | '<hive>DELIMITED' | '<hive>DEPENDENCY' | '<hive>DIRECTORY' | '<hive>DISTRIBUTE' | '<hive>DISTRIBUTED' | '<hive>DOUBLE_PRECISION' |'<hive>ESCAPED' | '<hive>EXTENDED' | '<hive>EXTERNAL' | '<hive>FIELDS' | '<hive>FILE' | '<hive>FOR' | '<hive>FOREIGN' | '<hive>FORMAT' | '<hive>FUNCTION' | '<hive>GRANT' | '<hive>GROUPING' | '<hive>IDXPROPERTIES' | '<hive>KEY' | '<hive>LATERAL' | '<hive>LOCAL' | '<hive>LOCK' | '<hive>MACRO' | '<hive>MATCHED' | '<hive>NORELY' | '<hive>NOVALIDATE' | '<hive>OVERWRITE' | '<hive>OWNER' | '<hive>PARTITION' | '<hive>PERCENT' | '<hive>PRIVILEGES' | '<hive>PRIMARY' | '<hive>REBUILD' | '<hive>REFERENCES' | '<hive>RELY' | '<hive>REPAIR' | '<hive>REPLICATION' |'<hive>ROLLUP' | '<hive>SETS' | '<hive>STATISTICS' | '<hive>SHOW_DATABASE' | '<hive>TABLE' | '<hive>TIMESTAMP' |'<hive>USER' | '<hive>ASC' | '<hive>COLUMNS' | '<hive>COMMENT' | '<hive>COMPACTIONS' | '<hive>DATA' | '<hive>DATABASES' | '<hive>DEFINED' | '<hive>DESC' |  '<hive>FORMATTED' | '<hive>FUNCTIONS' | '<hive>INDEX' | '<hive>INDEXES' | '<hive>INPATH' | '<hive>INPUTFORMAT' | '<hive>ITEMS' | '<hive>JAR' | '<hive>KEYS' | '<hive>LINES' | '<hive>LOCATION' | '<hive>LOCKS' | '<hive>METADATA' | '<hive>NONE' | '<hive>NOSCAN' | '<hive>OF' | '<hive>ORC' | '<hive>OUT' | '<hive>OUTPUTFORMAT' | '<hive>PARQUET' | '<hive>PARTITIONED' | '<hive>PARTITIONS' | '<hive>RCFILE' | '<hive>ROLE' | '<hive>ROLES' | '<hive>SCHEMA' | '<hive>SCHEMAS' | '<hive>SEQUENCEFILE' | '<hive>SERDE' | '<hive>SERDEPROPERTIES' | '<hive>SKEWED' | '<hive>SORTED' | '<hive>STORED' | '<hive>STORED_AS_DIRECTORIES' | '<hive>STRING' | '<hive>TABLES' | '<hive>TABLESAMPLE' | '<hive>TBLPROPERTIES' | '<hive>TEMPORARY' | '<hive>TERMINATED' | '<hive>TEXTFILE' | '<hive>TINYINT' | '<hive>TRANSACTIONS' | '<hive>UNIONTYPE' | '<hive>USING' | '<hive>VIEW' | '<hive>VIEWS' | '<hive>WAIT' | '<hive>WINDOW' | '<hive>.' | '<hive>[' | '<hive>]'
 | '<impala>AGGREGATE' | '<impala>AVRO' | '<impala>CACHED' | '<impala>CASCADE' | '<impala>CLOSE_FN' | '<impala>COLUMN' | '<impala>DATA' | '<impala>DATABASES' | '<impala>DELETE' | '<impala>DELIMITED' | '<impala>ESCAPED' | '<impala>EXTENDED' |'<impala>EXTERNAL' | '<impala>FIELDS' | '<impala>FILES' | '<impala>FINALIZE_FN' | '<impala>FIRST' | '<impala>FORMAT' | '<impala>FORMATTED' | '<impala>FUNCTION' | '<impala>FUNCTIONS' | '<impala>GROUP' | '<impala>HASH' | '<impala>ILIKE' | '<impala>INCREMENTAL' | '<impala>INTERMEDIATE' | '<impala>INTERVAL' | '<impala>INIT_FN' | '<impala>INPATH' | '<impala>IREGEXP' | '<impala>KEY' | '<impala>KUDU' | '<impala>LAST' | '<impala>LIMIT' | '<impala>LINES' | '<impala>LOCATION' | '<impala>MERGE_FN' | '<impala>NULLS' | '<impala>PARTITIONS' | '<impala>PREPARE_FN' | '<impala>PRIMARY' | '<impala>RANGE' | '<impala>REAL' | '<impala>RECOVER' | '<impala>REPEATABLE' | '<impala>REPLICATION' | '<impala>RESTRICT' | '<impala>RETURNS' | '<impala>SCHEMAS' | '<impala>SERIALIZE_FN' | '<impala>SERVER' | '<impala>SORT' | '<impala>STATS' | '<impala>STRAIGHT_JOIN' | '<impala>SYMBOL' | '<impala>TABLE' | '<impala>TABLES' | '<impala>TABLESAMPLE' | '<impala>URI' | '<impala>USING' | '<impala>ANALYTIC' | '<impala>ANTI' | '<impala>CURRENT' | '<impala>GRANT' | '<impala>NOSHUFFLE' | '<impala>PARQUET' | '<impala>PARTITIONED' | '<impala>RCFILE' | '<impala>ROLE' | '<impala>ROLES' | '<impala>SEQUENCEFILE' | '<impala>SERDEPROPERTIES' | '<impala>SHUFFLE' | '<impala>STORED' | '<impala>TBLPROPERTIES' | '<impala>TERMINATED' | '<impala>TEXTFILE' | '<impala>UPDATE_FN' | '<impala>BROADCAST' | '<impala>...' | '<impala>.' | '<impala>[' | '<impala>]'
 | 'ALL' | 'ARRAY' | 'AS' | 'ASC' | 'BETWEEN' | 'BIGINT' | 'BOOLEAN' | 'BY' | 'CASE' | 'CHAR' | 'CROSS' | 'CURRENT' | 'DATABASE' | 'DECIMAL' | 'DISTINCT' | 'DOUBLE' | 'DESC' | 'ELSE' | 'END' | 'EXISTS' | 'FALSE' | 'FLOAT' | 'FOLLOWING' | 'FROM' | 'FULL' | 'GROUP' | 'HAVING' | 'IF' | 'IN' | 'INNER' | 'INT' | 'INTO' | 'IS' | 'JOIN' | 'LEFT' | 'LIKE' | 'LIMIT' | 'MAP' | 'NOT' | 'NULL' | 'ON' | 'OPTION' | 'ORDER' | 'OUTER' | 'OVER' | 'PARTITION' | 'PRECEDING' | 'PURGE' | 'RANGE' | 'REGEXP' | 'RIGHT' | 'RLIKE' | 'ROW' | 'ROWS' | 'SCHEMA' | 'SEMI' | 'SET' | 'SMALLINT' | 'STRING' | 'STRUCT' | 'TABLE' | 'THEN' | 'TIMESTAMP' | 'TINYINT' | 'TRUE' | 'UNION' | 'VALUES' | 'VARCHAR' | 'WHEN' | 'WHERE' | 'WITH' | 'ROLE'
 | 'AVG' | 'CAST' | 'COUNT' | 'MAX' | 'MIN' | 'STDDEV_POP' | 'STDDEV_SAMP' | 'SUM' | 'VARIANCE' | 'VAR_POP' | 'VAR_SAMP'
 | '<hive>COLLECT_SET' | '<hive>COLLECT_LIST' | '<hive>CORR' | '<hive>COVAR_POP' | '<hive>COVAR_SAMP' | '<hive>DAY' | '<hive>DAYOFWEEK' | '<hive>HISTOGRAM_NUMERIC' | '<hive>HOUR' | '<hive>MINUTE' | '<hive>MONTH' | '<hive>NTILE' | '<hive>PERCENTILE' | '<hive>PERCENTILE_APPROX' | '<hive>QUARTER' | '<hive>SECOND' | '<hive>WEEK' | '<hive>YEAR'
 | '<impala>APPX_MEDIAN' | '<impala>EXTRACT' | '<impala>GROUP_CONCAT' | '<impala>NDV' | '<impala>STDDEV' | '<impala>VARIANCE_POP' | '<impala>VARIANCE_SAMP'
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
     parser.suggestKeywords(['INDEX', 'INDEXES']);
   }
 | 'CURSOR' HiveIndexOrIndexes
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
 | '<hive>CASCADE'
 ;

OptionalCascadeOrRestrict
 :
 | '<hive>CASCADE'
 | '<impala>CASCADE'
 | '<hive>RESTRICT'
 | '<impala>RESTRICT'
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
 : AnyPartition '(' PartitionSpecList ')'
 ;

PartitionSpec_EDIT
 : AnyPartition '(' PartitionSpecList_EDIT RightParenthesisOrError
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
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@1, [ { name: $1 } ]);
     parser.addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
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
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     parser.suggestDatabases();
     $$ = { identifierChain: [{ name: $1 }] };
   }
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     // In Impala you can have statements like 'SELECT ... FROM testTable t, t.|'
     parser.suggestTablesOrColumns($1);
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier ImpalaFields_EDIT
   {
     // TODO: switch to suggestColumns, it's currently handled in sqlAutocompleter2.js
     // Issue is that suggestColumns is deleted if no tables are defined and this is
     // Impala only cases like "SELECT | FROM db.table.col"
     parser.suggestTables({ identifierChain: [{ name: $1 }, { name: $3 }].concat($4) });
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
     parser.suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     parser.suggestDatabases();
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
 | ColumnIdentifier // Hive allows partial partition specs in some cases
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
 : HiveOrImpalaLocation HdfsPath
 ;

HdfsLocation_EDIT
 : HiveOrImpalaLocation HdfsPath_EDIT
 ;

OptionalCachedInOrUncached
 :
 | CachedIn OptionalWithReplication
   {
     if (!$2) {
       $$ = { suggestKeywords: ['WITH REPLICATION ='] };
     }
   }
 | '<impala>UNCACHED'
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
 : '<impala>CACHED' 'IN' QuotedValue
 ;

CachedIn_EDIT
 : '<impala>CACHED' 'CURSOR'
   {
     parser.suggestKeywords(['IN']);
   }
 ;

OptionalWithReplication
 :
 | WithReplication
 ;

WithReplication
 : 'WITH' '<impala>REPLICATION' '=' SignedInteger
 ;

WithReplication_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['REPLICATION =']);
   }
 | 'WITH' '<impala>REPLICATION' 'CURSOR'
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
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
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
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
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
 | BasicIdentifierChain AnyDot '*'
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
 | BasicIdentifierChain AnyDot ColumnIdentifier
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
 | BasicIdentifierChain AnyDot ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       parser.suggestKeyValues({ identifierChain: $1.concat([ $3.identifier ]) });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | BasicIdentifierChain AnyDot ColumnIdentifier_EDIT AnyDot BasicIdentifierChain
 | ColumnIdentifier_EDIT AnyDot BasicIdentifierChain
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor
   {
     parser.suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: [{ value: '*', weight: 10000 }] };
   }
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor AnyDot BasicIdentifierChain
   {
     parser.suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: [{ value: '*', weight: 10000 }] };
   }
 ;

DerivedColumnChain
 : ColumnIdentifier  -> [ $1.identifier ]
 | DerivedColumnChain AnyDot ColumnIdentifier
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
 | DerivedColumnChain AnyDot ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       parser.suggestKeyValues({ identifierChain: $1.concat([ $3.identifier ]) });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | DerivedColumnChain AnyDot ColumnIdentifier_EDIT AnyDot DerivedColumnChain
   {
     if ($3.insideKey) {
       parser.suggestKeyValues({ identifierChain: $1.concat([ $3.identifier ]) });
       parser.suggestColumns();
       parser.suggestFunctions();
     }
   }
 | ColumnIdentifier_EDIT AnyDot DerivedColumnChain
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
 | DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor
   {
     parser.suggestColumns({ identifierChain: $1 });
   }
 | DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor AnyDot DerivedColumnChain
   {
     parser.suggestColumns({ identifierChain: $1 });
   }
 | PartialBacktickedIdentifierOrPartialCursor AnyDot DerivedColumnChain
   {
     parser.suggestColumns();
   }
 ;

ColumnIdentifier
 : RegularOrBacktickedIdentifier                                                                               -> { identifier: { name: $1 }, location: @1 };
 | RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket ValueExpression HiveOrImpalaRightSquareBracket  -> { identifier: { name: $1, keySet: true }, location: @1 }
 | RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket HiveOrImpalaRightSquareBracket                  -> { identifier: { name: $1, keySet: true }, location: @1 }
 ;

ColumnIdentifier_EDIT
 : RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket AnyCursor HiveOrImpalaRightSquareBracketOrError             -> { identifier: { name: $1 }, insideKey: true }
 | RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket ValueExpression_EDIT HiveOrImpalaRightSquareBracketOrError  -> { identifier: { name: $1 }};
 ;

PartialBacktickedIdentifierOrPartialCursor
 : PartialBacktickedIdentifier
 | 'PARTIAL_CURSOR'
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
 | '<hive>DOUBLE_PRECISION'
 | '<impala>REAL'
 | 'STRING'
 | '<hive>STRING'
 | 'DECIMAL' OptionalTypePrecision
 | 'CHAR' OptionalTypeLength
 | 'VARCHAR' OptionalTypeLength
 | 'TIMESTAMP'
 | '<hive>TIMESTAMP'
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
 : '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
     parser.addColumnLocation(@4, $4);
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
   }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalHiveExtended DatabaseIdentifier
   {
     parser.addDatabaseLocation(@4, [{ name: $4 }]);
   }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalHiveExtended RegularIdentifier
 ;

HiveDescribeStatement_EDIT
 : '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain_EDIT OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier DerivedColumnChain OptionalPartitionSpec
   {
     if (!$2) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     if (!$2) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier 'CURSOR' OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
     parser.suggestColumns();
     if (!$5) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain 'CURSOR' OptionalPartitionSpec
   {
     if (!$6) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain OptionalPartitionSpec_EDIT
 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT

 | '<hive>DESCRIBE' OptionalHiveExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'FUNCTION', 'SCHEMA']);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
    }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalHiveExtended DatabaseIdentifier_EDIT
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED']);
     }
   }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalHiveExtended 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        parser.suggestKeywords(['EXTENDED']);
      }
    }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalHiveExtended 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED']);
     }
   }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalHiveExtended 'CURSOR' RegularIdentifier
    {
      if (!$3) {
        parser.suggestKeywords(['EXTENDED']);
      }
    }
 ;

ImpalaDescribeStatement
 : '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 | '<impala>DESCRIBE' 'DATABASE' OptionalImpalaExtendedOrFormatted DatabaseIdentifier
   {
     parser.addDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

ImpalaDescribeStatement_EDIT
 : '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords([{ value: 'DATABASE', weight: 2 }, { value: 'EXTENDED', weight: 1 }, { value: 'FORMATTED', weight: 1 }]);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<impala>DESCRIBE' OptionalImpalaExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
     if (!$2) {
       parser.suggestKeywords([{ value: 'DATABASE', weight: 2 }, { value: 'EXTENDED', weight: 1 }, { value: 'FORMATTED', weight: 1 }]);
     }
   }
 | '<impala>DESCRIBE' 'DATABASE' OptionalImpalaExtendedOrFormatted 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
     parser.suggestDatabases();
   }
 | '<impala>DESCRIBE' 'DATABASE' OptionalImpalaExtendedOrFormatted 'CURSOR' DatabaseIdentifier
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
       if (parser.isImpala() && !$3) {
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
     if (parser.isImpala() && !$3) {
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
     if (parser.isImpala() && !$3) {
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
 | '<impala>STRAIGHT_JOIN'
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
 : RegularOrBacktickedIdentifier AnyAs '(' TableSubQueryInner ')'
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
 | RegularOrBacktickedIdentifier AnyAs '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['SELECT']);
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
         if (parser.isImpala()) {
           keywords.push({ value: 'USING', weight: 3 });
         }
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
       keywords = keywords.concat(['FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']);
       if (parser.isHive()) {
         keywords = keywords.concat(['CROSS', 'INNER', 'LEFT SEMI']);
       } else if (parser.isImpala()) {
         keywords = keywords.concat(['ANTI', 'CROSS', 'INNER', 'LEFT ANTI', 'LEFT INNER', 'LEFT SEMI', 'OUTER', 'RIGHT ANTI', 'RIGHT INNER', 'RIGHT SEMI', 'SEMI']);
       } else {
         keywords.push('INNER');
       }
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
       { value: 'FULL JOIN', weight: 1 },
       { value: 'FULL OUTER JOIN', weight: 1 },
       { value: 'JOIN', weight: 1 },
       { value: 'LEFT JOIN', weight: 1 },
       { value: 'LEFT OUTER JOIN', weight: 1 },
       { value: 'RIGHT JOIN', weight: 1 },
       { value: 'RIGHT OUTER JOIN', weight: 1 }
     ]);
     if (parser.isHive()) {
       keywords = keywords.concat([
         { value: 'CROSS JOIN', weight: 1 },
         { value: 'INNER JOIN', weight: 1 },
         { value: 'LEFT SEMI JOIN', weight: 1 }
       ]);
     } else if (parser.isImpala()) {
       keywords = keywords.concat([
         { value: 'ANTI JOIN', weight: 1 },
         { value: 'INNER JOIN', weight: 1 },
         { value: 'LEFT ANTI JOIN', weight: 1 },
         { value: 'LEFT INNER JOIN', weight: 1 },
         { value: 'LEFT SEMI JOIN', weight: 1 },
         { value: 'OUTER JOIN', weight: 1 },
         { value: 'RIGHT ANTI JOIN', weight: 1 },
         { value: 'RIGHT INNER JOIN', weight: 1 },
         { value: 'RIGHT SEMI JOIN', weight: 1 },
         { value: 'SEMI JOIN', weight: 1 }
       ]);
     } else {
       keywords.push({ value: 'INNER JOIN', weight: 1 });
     }
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
     if (parser.isHive()) {
       $$ = { tableReferenceList : $2, suggestKeywords: ['LATERAL VIEW'] }
     } else {
       $$ = { tableReferenceList : $2 }
     }
     if (parser.isHive() && $3) {
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
 : OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$1, $2, $3, $4, $5, $6, $6, $7, $8],
       [{ value: 'WHERE', weight: 9 }, { value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, true, parser.isHive(), true, parser.isHive(), parser.isHive() && !$5, true, parser.isImpala()]);

     if (keywords.length > 0) {
       $$ = { suggestKeywords: keywords, empty: !$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 };
     } else {
       $$ = {};
     }

     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($6, @6, $5, @5, $4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = $7 ? @7 : undefined;

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
     var keywords = parser.getKeywordsForOptionalsLR(
       [$3, $4, $5, $6, $7, $7, $8, $9],
       [{ value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, true, parser.isHive(), true, parser.isHive(), parser.isHive() && !$6, true, parser.isImpala()]);
     if ($1.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($1.suggestKeywords, 1));
     }
     $$ = parser.getValueExpressionKeywords($1, keywords);
     $$.cursorAtEnd = !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9;
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
 | OptionalWhereClause GroupByClause 'CURSOR' OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$4, $5, $6, $7, $7, $8, $9],
       [{ value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [true, parser.isHive(), true, parser.isHive(), parser.isHive() && !$6, true, parser.isImpala()]);
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
     $$.cursorAtEnd = !$4 && !$5 && !$6 && !$7 && !$8 && !$9;
     if (!$4 && !$5 && !$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $5, @5, $4, @4, $2, @2);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause 'CURSOR' OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$5, $6, $7, $7, $8, $9],
       [{ value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'SORT BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }],
       [parser.isHive(), true, parser.isHive(), parser.isHive() && !$6, true, parser.isImpala()]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$5 && !$6 && !$7 && !$8 && !$9 };
     if (!$5 && !$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $5, @5, $3, @3);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause 'CURSOR' OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$6, $7, $8, $9], [{ value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, parser.isHive(), true, parser.isImpala()]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$6 && !$7 && !$8 && !$9 };
     if (!$6) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $6, @6, $4, @4);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause 'CURSOR' OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$7, $8, $9], [[{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [parser.isHive(), true, parser.isImpala()]);
     if ($5.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($5.suggestKeywords, 5));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$7 && !$8 && !$9 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($7, @7, $5, @5);
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy 'CURSOR' OptionalLimitClause OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$8, $9], [{ value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, parser.isImpala()]);
     if ($6.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($6.suggestKeywords, 4));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$8 && !$9 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = @6;
     $$.limitClauseLocation = $8 ? @8 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause 'CURSOR' OptionalOffsetClause
   {
     var keywords = parser.getKeywordsForOptionalsLR([$9], [{ value: 'OFFSET', weight: 2 }], [parser.isImpala()]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$9 };
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
 : AnyGroup 'BY' GroupByColumnList OptionalHiveGroupingSetsCubeOrRollup
   {
     $$ = { valueExpression: $4 ? false : $3 };
     if (!$4 && parser.isHive()) {
       $$.suggestKeywords = ['GROUPING SETS', 'WITH CUBE', 'WITH ROLLUP'];
     }
   }
 ;

GroupByClause_EDIT
 : AnyGroup 'BY' GroupByColumnList_EDIT OptionalHiveGroupingSetsCubeOrRollup
   {
     parser.suggestSelectListAliases();
   }
 | AnyGroup 'BY' 'CURSOR' OptionalHiveGroupingSetsCubeOrRollup
   {
     parser.valueExpressionSuggest();
     parser.suggestSelectListAliases();
     parser.suggestGroupBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 | AnyGroup 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
     parser.suggestGroupBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
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
     if (parser.isHive()) {
       parser.suggestKeywords(['CUBE', 'ROLLUP']);
     }
   }
 ;

HiveGroupingSets
 : '<hive>GROUPING' '<hive>SETS' '(' ColumnGroupingSets ')'
 ;

HiveGroupingSets_EDIT
 : '<hive>GROUPING' 'CURSOR'
   {
     parser.suggestKeywords(['SETS']);
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
 : ValueExpression OptionalAscOrDesc OptionalImpalaNullsFirstOrLast  -> parser.mergeSuggestKeywords($2, $3)
 ;

OrderByIdentifier_EDIT
 : ValueExpression_EDIT OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
   {
     parser.suggestSelectListAliases();
   }
 | ValueExpression OptionalAscOrDesc OptionalImpalaNullsFirstOrLast_EDIT
 | AnyCursor OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
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
 | '<hive>ASC'
 | 'DESC'
 | '<hive>DESC'
 ;

OptionalImpalaNullsFirstOrLast
 :
  {
    if (parser.isImpala()) {
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
 : '<hive>CLUSTER' 'BY' ColumnList
 ;

ClusterByClause_EDIT
 : '<hive>CLUSTER' 'CURSOR'
   {
     suggestKeywords: ['BY'];
   }
 | '<hive>CLUSTER' 'BY' 'CURSOR'
   {
     parser.suggestColumns();
     parser.suggestSelectListAliases();
   }
 | '<hive>CLUSTER' 'BY' ColumnList_EDIT
   {
     parser.suggestSelectListAliases();
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
     parser.suggestColumns();
     parser.suggestSelectListAliases();
   }
 | '<hive>DISTRIBUTE' 'BY' ColumnList_EDIT
   {
     parser.suggestSelectListAliases();
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
 | '<impala>LIMIT' ValueExpression
 ;

LimitClause_EDIT
 : 'LIMIT' 'CURSOR'
 | '<impala>LIMIT' 'CURSOR'
   {
     parser.suggestFunctions({ types: ['BIGINT'] });
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
     parser.suggestFunctions({ types: ['BIGINT'] });
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
     if (parser.isImpala()) {
       parser.suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'ILIKE', 'IREGEXP', 'LIKE', 'REGEXP', 'RLIKE']);
     } else {
       parser.suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'LIKE', 'REGEXP', 'RLIKE']);
     }
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
 | ImpalaInterval              -> { types: [ 'TIMESTAMP' ] }
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
 | ImpalaInterval_EDIT
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
 | BasicIdentifierChain AnyDot '*'
   {
     parser.addAsteriskLocation(@3, $1.concat({ asterisk: true }));
   }
 ;

ColumnOrArbitraryFunctionRef_EDIT
 : BasicIdentifierChain_EDIT
 ;

ImpalaInterval
 : '<impala>INTERVAL' SignedInteger RegularIdentifier
 ;

ImpalaInterval_EDIT
 : '<impala>INTERVAL' SignedInteger 'CURSOR'
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
 | 'UNSIGNED_INTEGER' AnyDot                     -> $1 + $2
 | 'UNSIGNED_INTEGER' AnyDot 'UNSIGNED_INTEGER'  -> $1 + $2 + $3
 | AnyDot 'UNSIGNED_INTEGER'                     -> $1 + $2
 ;

ApproximateNumericLiteral
 : UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | AnyDot UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER' AnyDot UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
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

 | AnyCursor AnyAs RegularOrBacktickedIdentifier
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
     if (parser.yy.latestTablePrimaries.length > 0) {
        parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
     }
   }
 | Joins JoinType OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
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
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType_EDIT OptionalImpalaBroadcastOrShuffle
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT OptionalJoinCondition
 | JoinType OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | JoinType OptionalImpalaBroadcastOrShuffle 'CURSOR' OptionalJoinCondition
   {
     if (!$2 && parser.isImpala()) {
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
 | '<impala>ANTI' 'JOIN'          -> 'ANTI JOIN'
 | 'CROSS' 'JOIN'                 -> 'CROSS JOIN'
 | 'INNER' 'JOIN'                 -> 'INNER JOIN'
 | 'OUTER' 'JOIN'                 -> 'OUTER JOIN'
 | 'SEMI' 'JOIN'                  -> 'SEMI JOIN'
 | 'FULL' 'JOIN'                  -> 'FULL JOIN'
 | 'FULL' 'OUTER' 'JOIN'          -> 'FULL OUTER JOIN'
 | 'LEFT' 'JOIN'                  -> 'LEFT JOIN'
 | 'LEFT' '<impala>ANTI' 'JOIN'   -> 'LEFT ANTI JOIN'
 | 'LEFT' 'INNER' 'JOIN'          -> 'LEFT INNER JOIN'
 | 'LEFT' 'OUTER' 'JOIN'          -> 'LEFT OUTER JOIN'
 | 'LEFT' 'SEMI' 'JOIN'           -> 'LEFT SEMI JOIN'
 | 'RIGHT' 'JOIN'                 -> 'RIGHT JOIN'
 | 'RIGHT' '<impala>ANTI' 'JOIN'  -> 'RIGHT ANTI JOIN'
 | 'RIGHT' 'INNER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'OUTER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'SEMI' 'JOIN'          -> 'RIGHT SEMI JOIN'
 ;

JoinType_EDIT
 : '<impala>ANTI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'CROSS' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'INNER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'OUTER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'SEMI' 'CURSOR'                  -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['OUTER'] }
 | 'LEFT' '<impala>ANTI' 'CURSOR'   -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'INNER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'SEMI' 'CURSOR'           -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'CURSOR' 'JOIN'           -> { suggestKeywords: parser.isImpala() ? ['ANTI', 'INNER', 'OUTER', 'SEMI'] : parser.isHive() ? ['OUTER', 'SEMI'] : ['OUTER'] }
 | 'RIGHT' '<impala>ANTI' 'CURSOR'  -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'INNER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'OUTER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'SEMI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'CURSOR' 'JOIN'          -> { suggestKeywords: parser.isImpala() ? ['ANTI', 'INNER', 'OUTER', 'SEMI'] : ['OUTER'] }
 ;

OptionalJoinCondition
 :                                       -> { noJoinCondition: true, suggestKeywords: parser.isImpala() ? ['ON', 'USING'] : ['ON'] }
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
     parser.valueExpressionSuggest();
     parser.suggestJoinConditions({ prependOn: false });
   }
 ;

TablePrimary
 : TableOrQueryName OptionalHiveTableSample OptionalCorrelationName OptionalImpalaTableSample
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
     if ($4 && $4.suggestKeywords) {
       keywords = $4.suggestKeywords;
     } else {
       // Right-to-left for cursor after TablePrimary
       keywords = parser.getKeywordsForOptionalsLR([$4, $3, $2], [{ value: 'TABLESAMPLE', weight: 1 }, { value: 'AS', weight: 2 }, { value: 'TABLESAMPLE', weight: 3 }], [parser.isImpala(), true, parser.isHive()]);
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 | DerivedTable OptionalCorrelationName OptionalImpalaTableSample
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
       keywords = parser.getKeywordsForOptionalsLR([$3, $2], [{ value: 'TABLESAMPLE', weight: 1 }, { value: 'AS', weight: 2 }], [parser.isImpala(), true]);
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalHiveTableSample OptionalCorrelationName OptionalImpalaTableSample
   {
     if ($3) {
       parser.addTableAliasLocation($3.location, $3.alias, $1.identifierChain);
     }
   }
 | TableOrQueryName OptionalHiveTableSample_EDIT OptionalCorrelationName OptionalImpalaTableSample
   {
     if ($3) {
       $1.alias = $3.alias;
       parser.addTableAliasLocation($3.location, $3.alias, $1.identifierChain);
     }
     parser.addTablePrimary($1);
   }
 | TableOrQueryName OptionalHiveTableSample OptionalCorrelationName OptionalImpalaTableSample_EDIT
   {
     if ($3) {
       $1.alias = $3.alias;
       parser.addTableAliasLocation($3.location, $3.alias, $1.identifierChain);
     }
     parser.addTablePrimary($1);
   }
 | DerivedTable_EDIT OptionalCorrelationName OptionalImpalaTableSample
   {
     if ($2) {
       parser.addTablePrimary({ subQueryAlias: $2.alias });
       parser.addSubqueryAliasLocation($2.location, $2.alias);
     }
   }
 | DerivedTable OptionalCorrelationName_EDIT OptionalImpalaTableSample
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

OptionalHiveTableSample
 :
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' '<hive>OF' 'UNSIGNED_INTEGER' OptionalOnColumn ')'
 | '<hive>TABLESAMPLE' '(' ExactNumericLiteral '<hive>PERCENT' ')'
 | '<hive>TABLESAMPLE' '(' ExactNumericLiteral 'ROWS' ')'
 | '<hive>TABLESAMPLE' '(' 'REGULAR_IDENTIFIER' ')'
 ;

OptionalHiveTableSample_EDIT
 : '<hive>TABLESAMPLE' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['BUCKET']);
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['OUT OF']);
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['OF']);
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' '<hive>OF' 'UNSIGNED_INTEGER' OptionalOnColumn 'CURSOR' RightParenthesisOrError
   {
     if (!$8) {
       parser.suggestKeywords(['ON']);
     }
   }
 | '<hive>TABLESAMPLE' '(' '<hive>BUCKET' 'UNSIGNED_INTEGER' '<hive>OUT' '<hive>OF' 'UNSIGNED_INTEGER' OptionalOnColumn_EDIT RightParenthesisOrError
 | '<hive>TABLESAMPLE' '(' ExactNumericLiteral 'CURSOR' RightParenthesisOrError
   {
     if ($3.indexOf('.') === -1 ) {
       parser.suggestKeywords(['PERCENT', 'ROWS']);
     } else {
       parser.suggestKeywords(['PERCENT']);
     }
   }
 ;

OptionalImpalaTableSample
 :
 | '<impala>TABLESAMPLE' '<impala>SYSTEM' '(' 'UNSIGNED_INTEGER' ')'                                                  --> { suggestKeywords: ['REPEATABLE()'] }
 | '<impala>TABLESAMPLE' '<impala>SYSTEM' '(' 'UNSIGNED_INTEGER' ')' '<impala>REPEATABLE' '(' 'UNSIGNED_INTEGER' ')'
 ;

OptionalImpalaTableSample_EDIT
 : '<impala>TABLESAMPLE' 'CURSOR'
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
 | AnyAs RegularOrBacktickedIdentifier  -> { alias: $2, location: @2 }
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
 : AggregateFunction OptionalOverClause
   {
     if (!$2) {
       $1.suggestKeywords = ['OVER'];
     }
   }
 | AnalyticFunction OverClause
 | CastFunction
 | HiveExtractFunction
 | ImpalaExtractFunction
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
 | HiveExtractFunction_EDIT
 | ImpalaExtractFunction_EDIT
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
 : 'IF'
 | 'ARRAY'
 | '<hive>BINARY'
 | 'MAP'
 | '<impala>REPLACE'
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
 | '(' AnyPartition 'BY' ValueExpressionList 'CURSOR' OptionalOrderByAndWindow RightParenthesisOrError
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
 : AnyPartition 'BY' ValueExpressionList  -> $3
 ;

PartitionBy_EDIT
 : AnyPartition 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | AnyPartition 'BY' 'CURSOR'
   {
     parser.valueExpressionSuggest();
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
     parser.suggestKeywords(parser.isHive() ? ['BETWEEN', 'UNBOUNDED'] : ['BETWEEN']);
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
     if (!$4 && parser.isHive()) {
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
 | AnyRange
 ;

OptionalCurrentOrPreceding
 :
 | IntegerOrUnbounded 'PRECEDING'
 | AnyCurrent 'ROW'
 ;

OptionalCurrentOrPreceding_EDIT
 : IntegerOrUnbounded 'CURSOR'
   {
     parser.suggestKeywords(['PRECEDING']);
   }
 | AnyCurrent 'CURSOR'
   {
     parser.suggestKeywords(['ROW']);
   }
 ;

AnyCurrent
 : 'CURRENT'
 | '<hive>CURRENT'
 | '<impala>CURRENT'
 ;

AnyRange
 : 'RANGE'
 | '<impala>RANGE'
 ;

OptionalAndFollowing
 :
 | 'AND' AnyCurrent 'ROW'
 | 'AND' IntegerOrUnbounded 'FOLLOWING'
 ;

OptionalAndFollowing_EDIT
 : 'AND' 'CURSOR'
   {
     parser.suggestKeywords(['CURRENT ROW', 'UNBOUNDED FOLLOWING']);
   }
 | 'AND' AnyCurrent 'CURSOR'
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
 : '<hive>WINDOW' RegularOrBacktickedIdentifier '<hive>AS' WindowExpression
 ;

WindowClause_EDIT
 : '<hive>WINDOW' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
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
     parser.valueExpressionSuggest();
     $$ = { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' AnyCursor AnyAs RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression_EDIT AnyAs PrimitiveType RightParenthesisOrError  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ValueExpression_EDIT AnyAs RightParenthesisOrError                -> { types: [ 'T' ] }
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
 | 'CAST' '(' ValueExpression AnyAs 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' AnyAs 'CURSOR' RightParenthesisOrError
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
       if (parser.isImpala()) {
         keywords.push('ALL');
       }
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
         if (parser.isImpala()) {
           keywords.push('ALL');
         }
       }
       parser.suggestKeywords(keywords);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 ;

HiveExtractFunction
 : '<hive>EXTRACT' '(' HiveDateField 'FROM' ValueExpression ')'  -> { types: ['INT'] }
 ;

HiveExtractFunction_EDIT
 : '<hive>EXTRACT' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR']);
     $$ = { types: ['INT'] }
   }
 | '<hive>EXTRACT' '(' HiveDateField 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['FROM']);
     $$ = { types: ['INT'] }
   }
 | '<hive>EXTRACT' '(' HiveDateField 'FROM' 'CURSOR' RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: ['INT'] }
   }
 | '<hive>EXTRACT' '(' HiveDateField 'FROM' ValueExpression_EDIT RightParenthesisOrError  -> { types: ['INT'] }
 | '<hive>EXTRACT' '(' AnyCursor 'FROM' ValueExpression RightParenthesisOrError
   {
      parser.suggestKeywords(['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR']);
      $$ = { types: ['INT'] }
   }
 | '<hive>EXTRACT' '(' HiveDateField 'CURSOR' ValueExpression RightParenthesisOrError
   {
     parser.suggestKeywords(['FROM']);
     $$ = { types: ['INT'] }
   }
 ;

HiveDateField
 : '<hive>DAY'
 | '<hive>DAYOFWEEK'
 | '<hive>HOUR'
 | '<hive>MINUTE'
 | '<hive>MONTH'
 | '<hive>QUARTER'
 | '<hive>SECOND'
 | '<hive>WEEK'
 | '<hive>YEAR'
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
       } else if (parser.isImpala()) {
         keywords.push('ALL');
         keywords.push('DISTINCT');
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
         } else if (parser.isImpala()) {
           keywords.push('ALL');
           keywords.push('DISTINCT');
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
 : '<impala>APPX_MEDIAN'
 | 'AVG'
 | '<hive>COLLECT_SET'
 | '<hive>COLLECT_LIST'
 | '<hive>CORR'
 | '<hive>COVAR_POP'
 | '<hive>COVAR_SAMP'
 | '<impala>GROUP_CONCAT'
 | '<hive>HISTOGRAM_NUMERIC'
 | '<impala>STDDEV'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'MAX'
 | 'MIN'
 | '<impala>NDV'
 | '<hive>NTILE'
 | '<hive>PERCENTILE'
 | '<hive>PERCENTILE_APPROX'
 | 'VARIANCE'
 | '<impala>VARIANCE_POP'
 | '<impala>VARIANCE_SAMP'
 | 'VAR_POP'
 | 'VAR_SAMP'
 ;

ImpalaExtractFunction
 : '<impala>EXTRACT' '(' ValueExpression FromOrComma ValueExpression ')'
 | '<impala>EXTRACT' '(' ')'
 ;

ImpalaExtractFunction_EDIT
 : '<impala>EXTRACT' '(' AnyCursor FromOrComma ValueExpression RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' AnyCursor FromOrComma RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions(['STRING', 'TIMESTAMP']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression_EDIT FromOrComma ValueExpression RightParenthesisOrError
   {
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression_EDIT FromOrComma RightParenthesisOrError
   {
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression_EDIT RightParenthesisOrError
   {
     parser.applyTypeToSuggestions(['STRING', 'TIMESTAMP']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression FromOrComma AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' FromOrComma AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
     parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
    parser.applyTypeToSuggestions($4.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression 'CURSOR' ValueExpression RightParenthesisOrError
   {
     if ($3.types[0] === 'STRING') {
       parser.suggestValueExpressionKeywords($3, ['FROM']);
     } else {
       parser.suggestValueExpressionKeywords($3);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
 | '<impala>EXTRACT' '(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     if ($3.types[0] === 'STRING') {
       parser.suggestValueExpressionKeywords($3, ['FROM']);
     } else {
       parser.suggestValueExpressionKeywords($3);
     }
     $$ = { types: parser.findReturnTypes($1) };
   }
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
       if (parser.isImpala()) {
         keywords.push('ALL');
       }
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
 : '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier LateralViewColumnAliases  -> { lateralView: { udtf: $4, tableAlias: $5, columnAliases: $6 }}
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier
   {
     if ($4.function.toLowerCase() === 'explode') {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: ['key', 'value'] }, suggestKeywords: ['AS'] };
     } else if ($4.function.toLowerCase() === 'posexplode') {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: ['pos', 'val'] }, suggestKeywords: ['AS'] };
     } else {
       $$ = { lateralView: { udtf: $4, tableAlias: $5, columnAliases: [] }, suggestKeywords: ['AS'] };
     }
   }
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction LateralViewColumnAliases                                -> { lateralView: { udtf: $4, columnAliases: $5 }}
 ;

LateralView_EDIT
 : '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction_EDIT
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction_EDIT RegularOrBacktickedIdentifier
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction_EDIT RegularOrBacktickedIdentifier LateralViewColumnAliases
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier LateralViewColumnAliases_EDIT
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction PartialBacktickedOrCursor
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction PartialBacktickedOrCursor LateralViewColumnAliases
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords([{ value: 'OUTER', weight: 2 }, { value: 'explode', weight: 1 }, { value: 'posexplode', weight: 1 }]);
     } else {
       parser.suggestKeywords(['explode', 'posexplode']);
     }
   }
 | '<hive>LATERAL' 'CURSOR'
   {
     parser.suggestKeywords(['VIEW']);
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