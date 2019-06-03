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

DataDefinition
 : CreateStatement
 ;

DataDefinition_EDIT
 : CreateStatement_EDIT
 ;

CreateStatement
 : DatabaseDefinition
 | TableDefinition
 | ViewDefinition
 | RoleDefinition
 | FunctionDefinition
 ;

CreateStatement_EDIT
 : DatabaseDefinition_EDIT
 | TableDefinition_EDIT
 | ViewDefinition_EDIT
 | FunctionDefinition_EDIT
 | 'CREATE' 'EXTERNAL' 'CURSOR'
   {
     if ($2) {
       parser.suggestKeywords(['TABLE']);
     } else {
       parser.suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
 ;

DatabaseDefinition
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinition_EDIT
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists_EDIT
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.addNewDatabaseLocation(@5, [{ name: $5 }]);
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinitionOptionals
 : OptionalComment OptionalHdfsLocation
   {
     var keywords = [];
     if (!$2) {
       keywords.push('LOCATION');
     }
     if (!$1 && !$2) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment_INVALID OptionalHdfsLocation
 | OptionalComment HdfsLocation_EDIT
 ;

OptionalComment
 :
 | Comment
 ;

Comment
 : 'COMMENT' QuotedValue
 ;

OptionalComment_INVALID
 : Comment_INVALID
 ;

Comment_INVALID
 : 'COMMENT' SINGLE_QUOTE
 | 'COMMENT' DOUBLE_QUOTE
 | 'COMMENT' SINGLE_QUOTE VALUE
 | 'COMMENT' DOUBLE_QUOTE VALUE
 ;

ParenthesizedPropertyAssignmentList
 : '(' PropertyAssignmentList ')'
 ;

PropertyAssignmentList
 : PropertyAssignment
 | PropertyAssignmentList ',' PropertyAssignment
 ;

PropertyAssignment
 : QuotedValue '=' UnsignedValueSpecification
 ;

TableDefinition
 : 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists TableDefinitionRightPart_EDIT
 | 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists_EDIT
 ;

TableDefinitionRightPart
 : TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 ;

TableDefinitionRightPart_EDIT
 : TableIdentifierAndOptionalColumnSpecification_EDIT OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification PartitionedBy_EDIT OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy SortBy_EDIT OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   RowFormat_EDIT OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat WithSerdeproperties_EDIT OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties StoredAs_EDIT
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   HdfsLocation_EDIT OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation CachedIn_EDIT OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation CachedIn WithReplication_EDIT OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement_EDIT
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalSortBy OptionalComment
   OptionalRowFormat OptionalWithSerdeproperties OptionalStoredAs
   OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties 'CURSOR'
   {
     var keywords = [];
     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
       keywords.push({ value: 'LIKE', weight: 1 });
       keywords.push({ value: 'LIKE PARQUET', weight: 1 });
     } else {
       if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'PARTITIONED BY', weight: 12 });
         keywords.push({ value: 'PARTITION BY', weight: 12 });
       }
       if (!$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'SORT BY', weight: 11 });
       }
       if (!$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'COMMENT', weight: 10 });
       }
       if (!$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'ROW FORMAT', weight: 7 });
       } else if ($5 && $5.suggestKeywords && !$6 && !$7 && !$8 && !$9 && !$10 && !$10) {
         keywords = keywords.concat(parser.createWeightedKeywords($5.suggestKeywords, 7));
       }
       if (!$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'WITH SERDEPROPERTIES', weight: 6 });
       }
       if (!$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'STORED AS', weight: 5 });
       }
       if (!$8 && !$9 && !$10) {
         keywords.push({ value: 'LOCATION', weight: 4 });
       }
       if (!$9 && !$10) {
         keywords.push({ value: 'CACHED IN', weight: 3 }, { value: 'UNCACHED', weight: 3 });
       } else if ($9 && $9.suggestKeywords && !$10) {
         keywords = keywords.concat(parser.createWeightedKeywords($9.suggestKeywords, 3));
       }
       if (!$10) {
         keywords.push({ value: 'TBLPROPERTIES', weight: 2 });
       }
       keywords.push({ value: 'AS', weight: 1 });
     }

     parser.suggestKeywords(keywords);
   }
 ;

TableIdentifierAndOptionalColumnSpecification
 : SchemaQualifiedIdentifier OptionalColumnSpecificationsOrLike
   {
     parser.addNewTableLocation(@1, $1, $2);
     $$ = $2;
   }
 ;

TableIdentifierAndOptionalColumnSpecification_EDIT
 : SchemaQualifiedIdentifier OptionalColumnSpecificationsOrLike_EDIT
 | SchemaQualifiedIdentifier_EDIT OptionalColumnSpecificationsOrLike
 ;

OptionalColumnSpecificationsOrLike
 :
 | ParenthesizedColumnSpecificationList
 | 'LIKE_PARQUET' HdfsPath                  -> []
 | 'LIKE' SchemaQualifiedTableIdentifier    -> []
 ;

OptionalColumnSpecificationsOrLike_EDIT
 : ParenthesizedColumnSpecificationList_EDIT
 | 'LIKE_PARQUET' HdfsPath_EDIT
 | 'LIKE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     parser.suggestKeywords(['PARQUET']);
   }
 | 'LIKE' SchemaQualifiedTableIdentifier_EDIT
 ;

ParenthesizedColumnSpecificationList
 : '(' ColumnSpecificationList ')'                              -> $2
 | '(' ColumnSpecificationList ',' PrimaryKeySpecification ')'  -> $2
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' PrimaryKeySpecification_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['PRIMARY KEY']);
   }
 ;

ColumnSpecificationList
 : ColumnSpecification                              -> [$1]
 | ColumnSpecificationList ',' ColumnSpecification  -> $1.concat($3)
 ;

ColumnSpecificationList_EDIT
 : ColumnSpecification_EDIT
 | ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecificationList ',' ColumnSpecification_EDIT
 | ColumnSpecificationList ',' ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecification 'CURSOR'
   {
     parser.checkForKeywords($1);
   }
 | ColumnSpecification 'CURSOR' ',' ColumnSpecificationList
   {
     parser.checkForKeywords($1);
   }
 | ColumnSpecificationList ',' ColumnSpecification 'CURSOR'
   {
     parser.checkForKeywords($3);
   }
 | ColumnSpecificationList ',' ColumnSpecification 'CURSOR' ',' ColumnSpecificationList
   {
     parser.checkForKeywords($3);
   }
 ;

ColumnSpecification
 : ColumnIdentifier ColumnDataType OptionalColumnOptions
   {
     $$ = $1;
     $$.type = $2;
     var keywords = [];
     if (!$3['primary']) {
       keywords.push('PRIMARY KEY');
     }
     if (!$3['encoding']) {
       keywords.push('ENCODING');
     }
     if (!$3['compression']) {
       keywords.push('COMPRESSION');
     }
     if (!$3['default']) {
       keywords.push('DEFAULT');
     }
     if (!$3['block_size']) {
       keywords.push('BLOCK_SIZE');
     }
     if (!$3['null']) {
       keywords.push('NOT NULL');
       keywords.push('NULL');
     }
     if (!$3['comment']) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

ColumnSpecification_EDIT
 : ColumnIdentifier 'CURSOR' OptionalColumnOptions
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | ColumnIdentifier ColumnDataType_EDIT OptionalColumnOptions
 | ColumnIdentifier ColumnDataType ColumnOptions_EDIT
 ;

OptionalColumnOptions
 :                      -> {}
 | ColumnOptions
 ;

ColumnOptions
 : ColumnOption
   {
     $$ = {};
     $$[$1] = true;
   }
 | ColumnOptions ColumnOption
   {
     $1[$2] = true;
   }
 ;

ColumnOptions_EDIT
 : ColumnOption_EDIT
 | ColumnOption_EDIT ColumnOptions
 | ColumnOptions ColumnOption_EDIT
 | ColumnOptions ColumnOption_EDIT ColumnOptions
 ;

ColumnOption
 : PrimaryKey                                        -> 'primary'
 | 'ENCODING' RegularIdentifier                      -> 'encoding'
 | 'COMPRESSION' RegularIdentifier                   -> 'compression'
 | 'DEFAULT' NonParenthesizedValueExpressionPrimary  -> 'default'
 | 'BLOCK_SIZE' UnsignedNumericLiteral               -> 'block_size'
 | 'NOT' 'NULL'                                      -> 'null'
 | 'NULL'                                            -> 'null'
 | Comment                                           -> 'comment'
 ;

ColumnOption_EDIT
 : PrimaryKey_EDIT
 | 'NOT' 'CURSOR'
   {
     parser.suggestKeywords(['NULL']);
   }
 ;

ColumnDataType
 : PrimitiveType
 | ArrayType
 | MapType
 | StructType
 | ArrayType_INVALID
 | MapType_INVALID
 | StructType_INVALID
 ;

ColumnDataType_EDIT
 : ArrayType_EDIT
 | MapType_EDIT
 | StructType_EDIT
 ;

ArrayType
 : 'ARRAY' '<' ColumnDataType '>'
 ;

ArrayType_INVALID
 : 'ARRAY' '<' '>'
 ;

ArrayType_EDIT
 : 'ARRAY' '<' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | 'ARRAY' '<' ColumnDataType_EDIT GreaterThanOrError
 ;

MapType
 : 'MAP' '<' PrimitiveType ',' ColumnDataType '>'
 ;

MapType_INVALID
 : 'MAP' '<' '>'
 ;

MapType_EDIT
 : 'MAP' '<' PrimitiveType ',' ColumnDataType_EDIT GreaterThanOrError
 | 'MAP' '<' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 | 'MAP' '<' PrimitiveType ',' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | 'MAP' '<' ',' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 ;

StructType
 : 'STRUCT' '<' StructDefinitionList '>'
 ;

StructType_INVALID
 : 'STRUCT' '<' '>'
 ;

StructType_EDIT
 : 'STRUCT' '<' StructDefinitionList_EDIT GreaterThanOrError
 ;

StructDefinitionList
 : StructDefinition
 | StructDefinitionList ',' StructDefinition
 ;

StructDefinitionList_EDIT
 : StructDefinition_EDIT
 | StructDefinition_EDIT Commas
 | StructDefinition_EDIT Commas StructDefinitionList
 | StructDefinitionList ',' StructDefinition_EDIT
 | StructDefinitionList ',' StructDefinition_EDIT Commas StructDefinitionList
 ;

StructDefinition
 : RegularOrBacktickedIdentifier ':' ColumnDataType OptionalComment
 ;

StructDefinition_EDIT
 : Commas RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     parser.suggestKeywords(['COMMENT']);
   }
 | Commas RegularOrBacktickedIdentifier ':' AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | Commas RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 | RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     parser.suggestKeywords(['COMMENT']);
   }
 | RegularOrBacktickedIdentifier ':' AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 ;

ColumnDataTypeList
 : ColumnDataType
 | ColumnDataTypeList ',' ColumnDataType
 ;

ColumnDataTypeList_EDIT
 : ColumnDataTypeListInner_EDIT
 | ColumnDataTypeListInner_EDIT Commas
 | ColumnDataTypeList ',' ColumnDataTypeListInner_EDIT
 | ColumnDataTypeListInner_EDIT Commas ColumnDataTypeList
 | ColumnDataTypeList ',' ColumnDataTypeListInner_EDIT Commas ColumnDataTypeList
 ;

ColumnDataTypeListInner_EDIT
 : Commas AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | Commas ColumnDataType_EDIT
 | AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | ColumnDataType_EDIT
 ;

GreaterThanOrError
 : '>'
 | error
 ;

PrimaryKeySpecification
 : PrimaryKey ParenthesizedColumnList
 ;

PrimaryKeySpecification_EDIT
 : PrimaryKey_EDIT
 | PrimaryKey_EDIT ParenthesizedColumnList
 | PrimaryKey ParenthesizedColumnList_EDIT
 ;

PrimaryKey
 : 'PRIMARY' 'KEY'
 ;

PrimaryKey_EDIT
 : 'PRIMARY' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 ;

OptionalPartitionedBy
 :
 | PartitionedBy
 ;

PartitionedBy
 : 'PARTITIONED' 'BY' ParenthesizedColumnSpecificationList
 | 'PARTITION' 'BY' HashClauses
 | 'PARTITION' 'BY' HashClauses ',' RangeClause
 | 'PARTITION' 'BY' RangeClause
 ;

PartitionedBy_EDIT
 : 'PARTITIONED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'PARTITIONED' 'CURSOR' ParenthesizedColumnSpecificationList
   {
     parser.suggestKeywords(['BY']);
   }
 | 'PARTITIONED' 'BY' ParenthesizedColumnSpecificationList_EDIT
 | 'PARTITIONED' ParenthesizedColumnSpecificationList_EDIT
 | 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'PARTITION' 'BY' 'CURSOR'
   {
     parser.suggestKeywords(['HASH', 'RANGE']);
   }
 | 'PARTITION' 'BY' HashClauses_EDIT
 | 'PARTITION' 'BY' RangeClause_EDIT
 | 'PARTITION' 'BY' HashClauses ',' 'CURSOR'
   {
     parser.suggestKeywords(['HASH', 'RANGE']);
   }
 | 'PARTITION' 'BY' HashClauses ',' RangeClause_EDIT
 | 'PARTITION' 'BY' HashClauses_EDIT ',' RangeClause
 ;

HashClauses
 : HashClause
 | HashClauses ',' HashClause
 ;

HashClauses_EDIT
 : HashClause_EDIT
 | HashClauses ',' HashClause_EDIT
 | HashClauses ',' HashClause_EDIT ',' HashClauses
 ;

HashClause
 : 'HASH' OptionalParenthesizedColumnList 'PARTITIONS' UnsignedNumericLiteral
 ;

HashClause_EDIT
 : 'HASH' OptionalParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 | 'HASH' ParenthesizedColumnList_EDIT
 | 'HASH' OptionalParenthesizedColumnList 'PARTITIONS' 'CURSOR'
 | 'HASH' ParenthesizedColumnList_EDIT 'PARTITIONS' UnsignedNumericLiteral
 ;

RangeClause
 : 'RANGE' ParenthesizedColumnList ParenthesizedPartitionValuesList
 ;

RangeClause_EDIT
 : 'RANGE' 'CURSOR'
 | 'RANGE' ParenthesizedColumnList_EDIT
 | 'RANGE' ParenthesizedColumnList 'CURSOR'
 | 'RANGE' ParenthesizedColumnList ParenthesizedPartitionValuesList_EDIT
 | 'RANGE' ParenthesizedColumnList_EDIT ParenthesizedPartitionValuesList
 ;

OptionalSortBy
 :
 | SortBy
 ;

SortBy
 : 'SORT' 'BY' ParenthesizedColumnList
 ;

SortBy_EDIT
 : 'SORT' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'SORT' 'BY' ParenthesizedColumnList_EDIT
 ;

ParenthesizedPartitionValuesList
 : '(' PartitionValueList ')'
 ;

ParenthesizedPartitionValuesList_EDIT
 : '(' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['PARTITION']);
   }
 |'(' PartitionValueList_EDIT RightParenthesisOrError
 ;

PartitionValueList
 : PartitionValue
 | PartitionValueList ',' PartitionValue
 ;

PartitionValueList_EDIT
 : PartitionValue_EDIT
 | PartitionValueList ',' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | PartitionValueList ',' 'CURSOR' ',' PartitionValueList
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | PartitionValueList ',' PartitionValue_EDIT
 | PartitionValueList ',' PartitionValue_EDIT ',' PartitionValueList
 ;

PartitionValue
 : 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' LessThanOrEqualTo ValueExpression
 | 'PARTITION' 'VALUES' LessThanOrEqualTo ValueExpression
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES'
 | 'PARTITION_VALUE' '=' ValueExpression
 ;

PartitionValue_EDIT
 : 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['VALUE', 'VALUES']);
   }
 | 'PARTITION_VALUE' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | 'PARTITION_VALUE' '=' 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | 'PARTITION' ValueExpression_EDIT
   {
     if ($2.endsWithLessThanOrEqual) {
      parser.suggestKeywords(['VALUES']);
     }
   }
 | 'PARTITION' ValueExpression 'CURSOR'
   {
     parser.suggestKeywords(['<', '<=']);
   }
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'CURSOR'
   {
     parser.suggestKeywords(['VALUES']);
   }
 | 'PARTITION' ValueExpression_EDIT LessThanOrEqualTo 'VALUES'
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' 'CURSOR'
   {
     parser.suggestKeywords(['<', '<=']);
   }
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' LessThanOrEqualTo 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' LessThanOrEqualTo ValueExpression_EDIT
 | 'PARTITION' 'VALUES' 'CURSOR'
   {
     parser.suggestKeywords(['<', '<=']);
   }
 | 'PARTITION' 'VALUES' LessThanOrEqualTo 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | 'PARTITION' 'VALUES' LessThanOrEqualTo ValueExpression_EDIT
 ;

LessThanOrEqualTo
 : '<'
 | 'COMPARISON_OPERATOR' // This is fine for autocompletion
 ;

ParenthesizedSortList
 : '(' SortList ')'
 ;

ParenthesizedSortList_EDIT
 : '(' SortList_EDIT RightParenthesisOrError
 ;

SortList
 : SortIdentifier
 | SortList ',' SortIdentifier
 ;

SortList_EDIT
 : SortIdentifier_EDIT
 | SortIdentifier_EDIT ',' SortList
 | SortList ',' SortIdentifier_EDIT
 | SortList ',' SortIdentifier_EDIT ',' SortList
 ;

SortIdentifier
 : ColumnIdentifier OptionalAscOrDesc
 ;

SortIdentifier_EDIT
 : ColumnIdentifier OptionalAscOrDesc 'CURSOR'
   {
     parser.checkForKeywords($2);
   }
 | ColumnIdentifier_EDIT OptionalAscOrDesc
 | AnyCursor OptionalAscOrDesc
   {
     parser.suggestColumns();
   }
 ;

OptionalRowFormat
 :
 | RowFormat
 ;

RowFormat
 : 'ROW' 'FORMAT' RowFormat
   {
     $$ = $3
   }
 ;

RowFormat_EDIT
 : 'ROW' 'CURSOR'
   {
     parser.suggestKeywords(['FORMAT']);
   }
 | 'ROW' 'FORMAT' 'CURSOR'
   {
     parser.suggestKeywords(['DELIMITED']);
   }
 | 'ROW' 'FORMAT' RowFormat_EDIT
 ;

OptionalStoredAs
 :           -> { suggestKeywords: ['STORED AS'] }
 | StoredAs
 ;

StoredAs
 : 'STORED' 'AS' FileFormat
 ;

StoredAs_EDIT
 : 'STORED' 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'STORED' 'AS' 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 ;

FileFormat
 : 'AVRO'
 | 'KUDU'
 | 'ORC'
 | 'PARQUET'
 | 'RCFILE'
 | 'SEQUENCEFILE'
 | 'TEXTFILE'
 ;

RowFormat
 : 'DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy
   {
     if (!$2 && !$3) {
       $$ = { suggestKeywords: [{ value: 'FIELDS TERMINATED BY', weight: 2 }, { value: 'LINES TERMINATED BY', weight: 1 }] };
     } else if ($2 && $2.suggestKeywords && !$3) {
       $$ = { suggestKeywords: parser.createWeightedKeywords($2.suggestKeywords, 2).concat(['LINES TERMINATED BY']) };
     } else if (!$3) {
       $$ = { suggestKeywords: [{ value: 'LINES TERMINATED BY', weight: 1 }] };
     }
   }
 ;

RowFormat_EDIT
 : 'DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalLinesTerminatedBy
 | 'DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy_EDIT
 ;

OptionalFieldsTerminatedBy
 :
 | 'FIELDS' 'TERMINATED' 'BY' SingleQuotedValue  -> { suggestKeywords: ['ESCAPED BY'] }
 | 'FIELDS' 'TERMINATED' 'BY' SingleQuotedValue 'ESCAPED' 'BY' SingleQuotedValue
 ;

OptionalFieldsTerminatedBy_EDIT
 : 'FIELDS' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'FIELDS' 'TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'FIELDS' 'TERMINATED' 'BY' SingleQuotedValue 'ESCAPED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalLinesTerminatedBy
 :
 | 'LINES' 'TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalLinesTerminatedBy_EDIT
 : 'LINES' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'LINES' 'TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalWithSerdeproperties
 :
 | WithSerdeproperties
 ;

WithSerdeproperties
 : 'WITH' 'SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

WithSerdeproperties_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 | 'WITH' 'CURSOR' ParenthesizedPropertyAssignmentList
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 ;

OptionalTblproperties
 :
 | TblProperties
 ;

TblProperties
 : 'TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalAsSelectStatement
 :
 | 'AS' CommitLocations QuerySpecification
 ;

OptionalAsSelectStatement_EDIT
 : 'AS' CommitLocations 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'AS' CommitLocations QuerySpecification_EDIT
 ;

CommitLocations
 : /* empty */
   {
     parser.commitLocations();
   }
 ;

ViewDefinition
 : 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
 ;

ViewDefinition_EDIT
 : 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedViewColumnList_EDIT OptionalComment
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'CURSOR'
   {
     var keywords = [{value: 'AS', weight: 1 }];
     if (!$6) {
       keywords.push({ value: 'COMMENT', weight: 3 });
     }
     parser.suggestKeywords(keywords);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier_EDIT OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
 ;

FunctionDefinition
 : GenericFunctionDefinition
 | AggregateFunctionDefinition
 ;

FunctionDefinition_EDIT
 : GenericFunctionDefinition_EDIT
 | AggregateFunctionDefinition_EDIT
 ;

GenericFunctionDefinition
 : 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation SymbolDefinition
 ;

GenericFunctionDefinition_EDIT
 : 'CREATE' 'FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation SymbolDefinition
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList 'CURSOR'
   {
     parser.suggestKeywords(['RETURNS']);
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType 'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation 'CURSOR'
   {
     parser.suggestKeywords(['SYMBOL']);
   }
 | 'CREATE' 'FUNCTION' OptionalIfNotExists_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation_EDIT
 | 'CREATE' 'FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation SymbolDefinition
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT ReturnType HdfsLocation SymbolDefinition
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT HdfsLocation SymbolDefinition
 | 'CREATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType HdfsLocation_EDIT SymbolDefinition
 ;

AggregateFunctionDefinition
 : 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 ;

AggregateFunctionDefinition_EDIT
 : 'CREATE' 'AGGREGATE' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList 'CURSOR'
   {
     parser.suggestKeywords(['RETURNS']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn 'CURSOR'
   {
     if (!$9) {
       parser.suggestKeywords([{value: 'INIT_FN', weight: 2 }, {value: 'UPDATE_FN', weight: 1 }]);
     } else {
       parser.suggestKeywords([{value: 'UPDATE_FN', weight: 1 }]);
     }
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn 'CURSOR'
   {
     parser.suggestKeywords(['MERGE_FN']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate 'CURSOR'
   {
     if (!$12 && !$13 && !$14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'PREPARE_FN', weight: 5 }, {value: 'CLOSE_FN', weight: 4 }, {value: 'SERIALIZE_FN', weight: 3 }, {value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($12 && !$13 && !$14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'CLOSE_FN', weight: 4 }, {value: 'SERIALIZE_FN', weight: 3 }, {value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($13 && !$14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'SERIALIZE_FN', weight: 3 }, {value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($15 && !$16) {
       parser.suggestKeywords([{value: 'INTERMEDIATE', weight: 1 }]);
     }
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation_EDIT OptionalInitFn
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn_EDIT OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn_EDIT OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn_EDIT  OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn_EDIT OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn_EDIT OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn Intermediate_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation_EDIT OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn_EDIT UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn_EDIT MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 ;

ParenthesizedArgumentList
 : '(' ')'
 | '(' ArgumentList OptionalVariableArguments')'
 ;

ParenthesizedArgumentList_EDIT
 : '(' ArgumentList_EDIT RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 | '(' ArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['...']);
   }
 ;

ArgumentList
 : PrimitiveType
 | ArgumentList ',' PrimitiveType
 ;

ArgumentList_EDIT
 : AnyCursor
 | ArgumentList ',' AnyCursor
 | AnyCursor ',' ArgumentList
 | ArgumentList ',' AnyCursor ',' ArgumentList
 ;

OptionalVariableArguments
 :
 | '...'
 ;

ReturnType
 : 'RETURNS' PrimitiveType
 ;

ReturnType_EDIT
 : 'RETURNS' 'CURSOR'
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 ;

SymbolDefinition
 : 'SYMBOL' '=' SingleQuotedValue
 ;

OptionalInitFn
 :
 | 'INIT_FN' '=' FunctionReference
 ;

OptionalInitFn_EDIT
 : 'INIT_FN' '=' FunctionReference_EDIT
 ;

UpdateFn
 : 'UPDATE_FN' '=' FunctionReference
 ;

UpdateFn_EDIT
 : 'UPDATE_FN' '=' FunctionReference_EDIT
 ;

MergeFn
 : 'MERGE_FN' '=' FunctionReference
 ;

MergeFn_EDIT
 : 'MERGE_FN' '=' FunctionReference_EDIT
 ;

OptionalPrepareFn
 :
 | 'PREPARE_FN' '=' FunctionReference
 ;

OptionalPrepareFn_EDIT
 : 'PREPARE_FN' '=' FunctionReference_EDIT
 ;

OptionalCloseFn
 :
 | 'CLOSE_FN' '=' FunctionReference
 ;

OptionalCloseFn_EDIT
 : 'CLOSE_FN' '=' FunctionReference_EDIT
 ;

OptionalSerializeFn
 :
 | 'SERIALIZE_FN' '=' FunctionReference
 ;

OptionalSerializeFn_EDIT
 : 'SERIALIZE_FN' '=' FunctionReference_EDIT
 ;

OptionalFinalizeFn
 :
 | 'FINALIZE_FN' '=' FunctionReference
 ;

OptionalFinalizeFn_EDIT
 : 'FINALIZE_FN' '=' FunctionReference_EDIT
 ;

OptionalIntermediate
 :
 | 'INTERMEDIATE' PrimitiveType
 ;

Intermediate_EDIT
 : 'INTERMEDIATE' 'CURSOR'
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 ;

FunctionReference
 : SingleQuotedValue
 ;

FunctionReference_EDIT
 : SingleQuotedValue_EDIT
   {
     parser.suggestFunctions();
     parser.suggestAggregateFunctions();
     parser.suggestAnalyticFunctions();
   }
 ;

OptionalParenthesizedViewColumnList
 :
 | ParenthesizedViewColumnList
 ;

ParenthesizedViewColumnList
 : '(' ViewColumnList ')'
 ;

ParenthesizedViewColumnList_EDIT
 : '(' ViewColumnList_EDIT RightParenthesisOrError
   {
     if (!$2) {
       parser.suggestKeywords(['COMMENT']);
     }
   }
 ;

ViewColumnList
 : ColumnReference OptionalComment
 | ViewColumnList ',' ColumnReference OptionalComment
 ;

ViewColumnList_EDIT
 : ColumnReference OptionalComment 'CURSOR'                                        -> $2
 | ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList                     -> $2
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR'                     -> $4
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList  -> $4
 ;

RoleDefinition
 : 'CREATE' 'ROLE' RegularIdentifier
 ;
