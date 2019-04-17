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
 | IndexDefinition
 | MacroDefinition
 ;

CreateStatement_EDIT
 : DatabaseDefinition_EDIT
 | TableDefinition_EDIT
 | ViewDefinition_EDIT
 | FunctionDefinition_EDIT
 | IndexDefinition_EDIT
 | MacroDefinition_EDIT
 | AnyCreate OptionalHiveTemporary OptionalHiveTransactional OptionalExternal 'CURSOR'
   {
     if ($4) {
       parser.suggestKeywords(['TABLE']);
     } else if (parser.isHive()) {
       if ($2 && !$3) {
         parser.suggestKeywords(['EXTERNAL TABLE', 'FUNCTION', 'MACRO', 'TABLE']);
       } else if (!$2 && !$3) {
         parser.suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'TEMPORARY TABLE', 'TRANSACTIONAL TABLE', 'VIEW']);
       } else if ($3) {
         parser.suggestKeywords(['TABLE']);
       }
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     } else {
       parser.suggestKeywords(['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
 ;

DatabaseDefinition
 : AnyCreate DatabaseOrSchema OptionalIfNotExists
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinition_EDIT
 : AnyCreate DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.addNewDatabaseLocation(@5, [{ name: $5 }]);
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinitionOptionals
 : OptionalComment OptionalHdfsLocation OptionalHiveDbProperties
   {
     var keywords = [];
     if (!$3 && parser.isHive()) {
       keywords.push('WITH DBPROPERTIES');
     }
     if (!$2 && !$3) {
       keywords.push('LOCATION');
     }
     if (!$1 && !$2 && !$3) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment_INVALID OptionalHdfsLocation OptionalHiveDbProperties
 | OptionalComment HdfsLocation_EDIT OptionalHiveDbProperties
 ;

OptionalHiveComment
 :
 | HiveComment
 ;

HiveComment
 : '<hive>COMMENT' QuotedValue
 ;

OptionalImpalaComment
 :
 | ImpalaComment
 ;

ImpalaComment
 : '<impala>COMMENT' QuotedValue
 ;

OptionalComment
 :
 | Comment
 ;

Comment
 : HiveOrImpalaComment QuotedValue
 ;

OptionalComment_INVALID
 : Comment_INVALID
 ;

Comment_INVALID
 : HiveOrImpalaComment SINGLE_QUOTE
 | HiveOrImpalaComment DOUBLE_QUOTE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE
 | HiveOrImpalaComment DOUBLE_QUOTE VALUE
 ;


OptionalHiveDbProperties
 :
 | HiveDbProperties
 ;

HiveDbProperties
 : '<hive>WITH' '<hive>DBPROPERTIES' ParenthesizedPropertyAssignmentList
 | '<hive>WITH' '<hive>DBPROPERTIES'
 | '<hive>WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DBPROPERTIES']);
   }
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
 : AnyCreate OptionalHiveTemporary OptionalHiveTransactional OptionalExternal AnyTable OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : AnyCreate OptionalHiveTemporary OptionalHiveTransactional OptionalExternal AnyTable OptionalIfNotExists TableDefinitionRightPart_EDIT
 | AnyCreate OptionalHiveTemporary OptionalHiveTransactional OptionalExternal AnyTable OptionalIfNotExists 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate OptionalHiveTemporary OptionalHiveTransactional OptionalExternal AnyTable OptionalIfNotExists_EDIT
 ;

TableDefinitionRightPart
 : TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 ;

TableDefinitionRightPart_EDIT
 : TableIdentifierAndOptionalColumnSpecification_EDIT OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment PartitionedBy_EDIT OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy SortBy_EDIT OptionalImpalaComment
   OptionalClusteredBy  OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   ClusteredBy_EDIT OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy SkewedBy_EDIT OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy RowFormat_EDIT OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat ImpalaWithSerdeproperties_EDIT OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties StoredAsOrBy_EDIT
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   HiveWithSerdeproperties_EDIT OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties HdfsLocation_EDIT OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation CachedIn_EDIT OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation CachedIn WithReplication_EDIT OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties OptionalAsSelectStatement_EDIT
 | TableIdentifierAndOptionalColumnSpecification OptionalHiveComment OptionalPartitionedBy OptionalSortBy OptionalImpalaComment
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalImpalaWithSerdeproperties OptionalStoredAsOrBy
   OptionalHiveWithSerdeproperties OptionalHdfsLocation OptionalCachedInOrUncached OptionalTblproperties 'CURSOR'
   {
     var keywords = [];
     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
       keywords.push({ value: 'LIKE', weight: 1 });
       if (parser.isImpala()) {
         keywords.push({ value: 'LIKE PARQUET', weight: 1 });
       }
     } else {
       if (parser.isHive() && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'COMMENT', weight: 13 });
       }
       if (!$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'PARTITIONED BY', weight: 12 });
         if (parser.isImpala()) {
           keywords.push({ value: 'PARTITION BY', weight: 12 });
         }
       }
       if (!$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'SORT BY', weight: 11 });
       }
       if (parser.isImpala() && !$5 && !$6 && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'COMMENT', weight: 10 });
       }
       if (parser.isHive() && !$6 && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'CLUSTERED BY', weight: 9 });
       }
       if (parser.isHive() && !$7 && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'SKEWED BY', weight: 8 });
       } else if (parser.isHive() && $7 && $7.suggestKeywords && !$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords = keywords.concat(parser.createWeightedKeywords($7.suggestKeywords, 8)); // Get the last optional from SKEWED BY
       }
       if (!$8 && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'ROW FORMAT', weight: 7 });
       } else if ($8 && $8.suggestKeywords && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords = keywords.concat(parser.createWeightedKeywords($8.suggestKeywords, 7));
       }
       if (parser.isImpala() && !$9 && !$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'WITH SERDEPROPERTIES', weight: 6 });
       }
       if (!$10 && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'STORED AS', weight: 5 });
         if (parser.isHive()) {
           keywords.push({ value: 'STORED BY', weight: 5 });
         }
       }
       if (parser.isHive() && $10 && $10.storedBy && !$11 && !$12 && !$13 && !$14) {
         keywords.push({ value: 'WITH SERDEPROPERTIES', weight: 6 });
       }
       if (!$12 && !$13 && !$14) {
         keywords.push({ value: 'LOCATION', weight: 4 });
       }
       if (parser.isImpala() && !$13 && !$14) {
         keywords.push({ value: 'CACHED IN', weight: 3 }, { value: 'UNCACHED', weight: 3 });
       } else if (parser.isImpala() && $13 && $13.suggestKeywords && !$14) {
         keywords = keywords.concat(parser.createWeightedKeywords($13.suggestKeywords, 3));
       }
       if (!$14) {
         keywords.push({ value: 'TBLPROPERTIES', weight: 2 });
       }
       keywords.push({ value: 'AS', weight: 1 });
     }

     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
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
 | '<impala>LIKE_PARQUET' HdfsPath          -> []
 | 'LIKE' SchemaQualifiedTableIdentifier    -> []
 ;

OptionalColumnSpecificationsOrLike_EDIT
 : ParenthesizedColumnSpecificationList_EDIT
 | '<impala>LIKE_PARQUET' HdfsPath_EDIT
 | 'LIKE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     if (parser.isImpala()) {
       parser.suggestKeywords(['PARQUET']);
     }
   }
 | 'LIKE' SchemaQualifiedTableIdentifier_EDIT
 ;

ParenthesizedColumnSpecificationList
 : '(' ColumnSpecificationList ')'                              -> $2
 | '(' ColumnSpecificationList ',' ConstraintSpecification ')'  -> $2
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' ConstraintSpecification_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' 'CURSOR' RightParenthesisOrError
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['PRIMARY KEY']);
     } else if (parser.isHive()) {
       parser.suggestKeywords([{ value: 'PRIMARY KEY', weight: 2 }, { value: 'CONSTRAINT', weight: 1 }]);
     }
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
     if (parser.isImpala()) {
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
     }
     if (!$3['comment']) {
       keywords.push('COMMENT');
       if (parser.isHive() && $2.toLowerCase() === 'double') {
         keywords.push({ value: 'PRECISION', weight: 2 });
       }
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
 : ImpalaPrimaryKey                                          -> 'primary'
 | '<impala>ENCODING' RegularIdentifier                      -> 'encoding'
 | '<impala>COMPRESSION' RegularIdentifier                   -> 'compression'
 | '<impala>DEFAULT' NonParenthesizedValueExpressionPrimary  -> 'default'
 | '<impala>BLOCK_SIZE' UnsignedNumericLiteral               -> 'block_size'
 | 'NOT' 'NULL'                                              -> 'null'
 | 'NULL'                                                    -> 'null'
 | Comment                                                   -> 'comment'
 ;

ColumnOption_EDIT
 : ImpalaPrimaryKey_EDIT
 | 'NOT' 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['NULL']);
     }
   }
 ;

ColumnDataType
 : PrimitiveType
 | ArrayType
 | MapType
 | StructType
 | UnionType
 | ArrayType_INVALID
 | MapType_INVALID
 | StructType_INVALID
 | UnionType_INVALID
 ;

ColumnDataType_EDIT
 : ArrayType_EDIT
 | MapType_EDIT
 | StructType_EDIT
 | UnionType_EDIT
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

UnionType
 : '<hive>UNIONTYPE' '<' ColumnDataTypeList '>'
 ;

UnionType_INVALID
 : '<hive>UNIONTYPE' '<' '>'
 ;

UnionType_EDIT
 : '<hive>UNIONTYPE' '<' ColumnDataTypeList_EDIT GreaterThanOrError
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

ConstraintSpecification
 : ImpalaPrimaryKeySpecification
 | HivePrimaryKeySpecification
 | '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification
 | HivePrimaryKeySpecification ',' '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification
 ;

ConstraintSpecification_EDIT
 : ImpalaPrimaryKeySpecification_EDIT
 | HivePrimaryKeySpecification_EDIT
 | HivePrimaryKeySpecification ',' 'CURSOR'
   {
     parser.suggestKeywords(['CONSTRAINT']);
   }
 | HivePrimaryKeySpecification ',' '<hive>CONSTRAINT' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FOREIGN KEY']);
   }
 | HivePrimaryKeySpecification ',' '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification_EDIT
 | HivePrimaryKeySpecification_EDIT ',' '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification
 | '<hive>CONSTRAINT' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FOREIGN KEY']);
   }
 | '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification_EDIT
 | 'CURSOR' '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification
   {
     parser.suggestKeywords(['PRIMARY KEY']);
   }
 ;

HivePrimaryKeySpecification
 : HivePrimaryKey ParenthesizedColumnList '<hive>DISABLE' '<hive>NOVALIDATE'
 ;

HivePrimaryKeySpecification_EDIT
 : HivePrimaryKey_EDIT
 | HivePrimaryKey ParenthesizedColumnList_EDIT
 | HivePrimaryKey ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['DISABLE NOVALIDATE']);
   }
 | HivePrimaryKey ParenthesizedColumnList '<hive>DISABLE' 'CURSOR'
   {
     parser.suggestKeywords(['NOVALIDATE']);
   }
 | HivePrimaryKey ParenthesizedColumnList_EDIT '<hive>DISABLE' '<hive>NOVALIDATE'
 ;

HiveForeignKeySpecification
 : '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList '<hive>DISABLE' '<hive>NOVALIDATE' OptionalRelyNoRely
   {
     parser.addTablePrimary($5);
   }
 ;

HiveForeignKeySpecification_EDIT
 : '<hive>FOREIGN' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList_EDIT
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['REFERENCES']);
   }
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' SchemaQualifiedTableIdentifier_EDIT
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList_EDIT
   {
     parser.addTablePrimary($5);
   }
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList 'CURSOR'
   {
     parser.addTablePrimary($5);
     parser.suggestKeywords(['DISABLE NOVALIDATE']);
   }
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList '<hive>DISABLE' 'CURSOR'
   {
     parser.addTablePrimary($5);
     parser.suggestKeywords(['NOVALIDATE']);
   }
 | '<hive>FOREIGN' '<hive>KEY' ParenthesizedColumnList '<hive>REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList '<hive>DISABLE' '<hive>NOVALIDATE' OptionalRelyNoRely 'CURSOR'
   {
     parser.addTablePrimary($5);
     if (!$9) {
       parser.suggestKeywords(['NORELY', 'RELY']);
     }
   }
 ;

OptionalRelyNoRely
 :
 | '<hive>RELY'
 | '<hive>NORELY'
 ;

ImpalaPrimaryKeySpecification
 : ImpalaPrimaryKey ParenthesizedColumnList
 ;

ImpalaPrimaryKeySpecification_EDIT
 : ImpalaPrimaryKey_EDIT
 | ImpalaPrimaryKey_EDIT ParenthesizedColumnList
 | ImpalaPrimaryKey ParenthesizedColumnList_EDIT
 ;

ImpalaPrimaryKey
 : '<impala>PRIMARY' '<impala>KEY'
 ;

ImpalaPrimaryKey_EDIT
 : '<impala>PRIMARY' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 ;

HivePrimaryKey
 : '<hive>PRIMARY' '<hive>KEY'
 ;

HivePrimaryKey_EDIT
 : '<hive>PRIMARY' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 ;

OptionalPartitionedBy
 :
 | PartitionedBy
 ;

PartitionedBy
 : HiveOrImpalaPartitioned 'BY' ParenthesizedColumnSpecificationList
 | 'PARTITION' 'BY' HashClauses
 | 'PARTITION' 'BY' HashClauses ',' RangeClause
 | 'PARTITION' 'BY' RangeClause
 ;

PartitionedBy_EDIT
 : HiveOrImpalaPartitioned 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | HiveOrImpalaPartitioned 'CURSOR' ParenthesizedColumnSpecificationList
   {
     parser.suggestKeywords(['BY']);
   }
 | HiveOrImpalaPartitioned 'BY' ParenthesizedColumnSpecificationList_EDIT
 | HiveOrImpalaPartitioned ParenthesizedColumnSpecificationList_EDIT
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
 : '<impala>HASH' OptionalParenthesizedColumnList '<impala>PARTITIONS' UnsignedNumericLiteral
 ;

HashClause_EDIT
 : '<impala>HASH' OptionalParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 | '<impala>HASH' ParenthesizedColumnList_EDIT
 | '<impala>HASH' OptionalParenthesizedColumnList '<impala>PARTITIONS' 'CURSOR'
 | '<impala>HASH' ParenthesizedColumnList_EDIT '<impala>PARTITIONS' UnsignedNumericLiteral
 ;

RangeClause
 : AnyRange ParenthesizedColumnList ParenthesizedPartitionValuesList
 ;

RangeClause_EDIT
 : AnyRange 'CURSOR'
 | AnyRange ParenthesizedColumnList_EDIT
 | AnyRange ParenthesizedColumnList 'CURSOR'
 | AnyRange ParenthesizedColumnList ParenthesizedPartitionValuesList_EDIT
 | AnyRange ParenthesizedColumnList_EDIT ParenthesizedPartitionValuesList
 ;

OptionalSortBy
 :
 | SortBy
 ;

SortBy
 : '<impala>SORT' 'BY' ParenthesizedColumnList
 ;

SortBy_EDIT
 : '<impala>SORT' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | '<impala>SORT' 'BY' ParenthesizedColumnList_EDIT
 ;

ParenthesizedPartitionValuesList
 : '(' PartitionValueList ')'
 ;

ParenthesizedPartitionValuesList_EDIT
 : '(' 'CURSOR' RightParenthesisOrError
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['PARTITION']);
     }
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
     if (parser.isImpala()) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | PartitionValueList ',' 'CURSOR' ',' PartitionValueList
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | PartitionValueList ',' PartitionValue_EDIT
 | PartitionValueList ',' PartitionValue_EDIT ',' PartitionValueList
 ;

PartitionValue
 : 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' LessThanOrEqualTo ValueExpression
 | 'PARTITION' 'VALUES' LessThanOrEqualTo ValueExpression
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES'
 | '<impala>PARTITION_VALUE' '=' ValueExpression
 ;

PartitionValue_EDIT
 : 'PARTITION' 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['VALUE', 'VALUES']);
     }
   }
 | '<impala>PARTITION_VALUE' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | '<impala>PARTITION_VALUE' '=' 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | 'PARTITION' ValueExpression_EDIT
   {
     if ($2.endsWithLessThanOrEqual && parser.isImpala()) {
      parser.suggestKeywords(['VALUES']);
     }
   }
 | 'PARTITION' ValueExpression 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['<', '<=']);
     }
   }
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'CURSOR'
   {
    if (parser.isImpala()) {
      parser.suggestKeywords(['VALUES']);
    }
   }
 | 'PARTITION' ValueExpression_EDIT LessThanOrEqualTo 'VALUES'
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['<', '<=']);
     }
   }
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' LessThanOrEqualTo 'CURSOR'
   {
     if (parser.isImpala()) {
      parser.suggestFunctions();
     }
   }
 | 'PARTITION' ValueExpression LessThanOrEqualTo 'VALUES' LessThanOrEqualTo ValueExpression_EDIT
 | 'PARTITION' 'VALUES' 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['<', '<=']);
     }
   }
 | 'PARTITION' 'VALUES' LessThanOrEqualTo 'CURSOR'
   {
     if (parser.isImpala()) {
      parser.suggestFunctions();
     }
   }
 | 'PARTITION' 'VALUES' LessThanOrEqualTo ValueExpression_EDIT
 ;

LessThanOrEqualTo
 : '<'
 | 'COMPARISON_OPERATOR' // This is fine for autocompletion
 ;

OptionalClusteredBy
 :
 | ClusteredBy
 ;

ClusteredBy
 : '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 ;

ClusteredBy_EDIT
 : '<hive>CLUSTERED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalHiveSortedBy
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords([{ value: 'INTO', weight: 1 }, { value: 'SORTED BY', weight: 2 }]);
     } else {
       parser.suggestKeywords(['INTO']);
     }
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' 'CURSOR'
   {
     parser.suggestKeywords(['BUCKETS']);
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy_EDIT 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy_EDIT
 ;

OptionalHiveSortedBy
 :
 | '<hive>SORTED' 'BY' ParenthesizedSortList
 ;

OptionalHiveSortedBy_EDIT
 : '<hive>SORTED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | '<hive>SORTED' 'BY' ParenthesizedSortList_EDIT
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

OptionalSkewedBy
 :
 | SkewedBy
 ;

SkewedBy
 : '<hive>SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList  -> { suggestKeywords: ['STORED AS DIRECTORIES'] }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList '<hive>STORED_AS_DIRECTORIES' // Hack otherwise ambiguous with OptionalHiveStoredAsOrBy
 ;

SkewedBy_EDIT
 : '<hive>SKEWED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 ;

ParenthesizedSkewedValueList
 : '(' SkewedValueList ')'
 ;

SkewedValueList
 : ParenthesizedSimpleValueList
 | SkewedValueList ',' ParenthesizedSimpleValueList
 ;

OptionalRowFormat
 :
 | RowFormat
 ;

RowFormat
 : 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat
   {
     $$ = $3
   }
 ;

RowFormat_EDIT
 : 'ROW' 'CURSOR'
   {
     parser.suggestKeywords(['FORMAT']);
   }
 | 'ROW' HiveOrImpalaFormat 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['DELIMITED', 'SERDE']);
     } else {
       parser.suggestKeywords(['DELIMITED']);
     }
   }
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat_EDIT
 ;

OptionalStoredAsOrBy
 :
 | StoredAsOrBy
 ;

StoredAsOrBy
 : StoredAs
 | '<hive>STORED' 'BY' QuotedValue
  {
    $$ = { storedBy: true }
  } 
 ;

StoredAsOrBy_EDIT
 : HiveOrImpalaStored 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['AS', 'BY']);
     } else {
       parser.suggestKeywords(['AS']);
     }
   }
 | StoredAs_EDIT
 ;

OptionalStoredAs
 :           -> { suggestKeywords: ['STORED AS'] }
 | StoredAs
 ;

StoredAs
 : HiveOrImpalaStored AnyAs FileFormat
 ;

StoredAs_EDIT
 : HiveOrImpalaStored AnyAs 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 ;

FileFormat
 : '<hive>AVRO'
 | '<hive>INPUTFORMAT' QuotedValue '<hive>OUTPUTFORMAT' QuotedValue
 | '<hive>JSONFILE'
 | '<hive>ORC'
 | '<hive>PARQUET'
 | '<hive>RCFILE'
 | '<hive>SEQUENCEFILE'
 | '<hive>TEXTFILE'
 | '<impala>AVRO'
 | '<impala>KUDU'
 | '<impala>ORC'
 | '<impala>PARQUET'
 | '<impala>RCFILE'
 | '<impala>SEQUENCEFILE'
 | '<impala>TEXTFILE'
 ;

HiveOrImpalaRowFormat
 : HiveRowFormat
 | ImpalaRowFormat
 ;

HiveOrImpalaRowFormat_EDIT
 : ImpalaRowFormat_EDIT
 | HiveRowFormat_EDIT
 ;

HiveRowFormat
 : HiveDelimitedRowFormat
 | '<hive>SERDE' QuotedValue
 ;

HiveRowFormat_EDIT
 : HiveDelimitedRowFormat_EDIT
 ;

HiveDelimitedRowFormat
 : '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
   {
     if (!$2 && !$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: [{ value: 'FIELDS TERMINATED BY', weight: 5 }, { value: 'COLLECTION ITEMS TERMINATED BY', weight: 4 }, { value: 'MAP KEYS TERMINATED BY', weight: 3 }, { value: 'LINES TERMINATED BY', weight: 2 }, { value: 'NULL DEFINED AS', weight: 1 }]};
     } else if ($2 && $2.suggestKeywords && !$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: parser.createWeightedKeywords($2.suggestKeywords, 5).concat([{ value: 'COLLECTION ITEMS TERMINATED BY', weight: 4 }, { value: 'MAP KEYS TERMINATED BY', weight: 3 }, { value: 'LINES TERMINATED BY', weight: 2 }, { value: 'NULL DEFINED AS', weight: 1 }]) };
     } else if (!$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: [{ value: 'COLLECTION ITEMS TERMINATED BY', weight: 4 }, { value: 'MAP KEYS TERMINATED BY', weight: 3 }, { value: 'LINES TERMINATED BY', weight: 2 }, { value: 'NULL DEFINED AS', weight: 1 }] };
     } else if (!$4 && !$5 && !$6) {
       $$ = { suggestKeywords: [{ value: 'MAP KEYS TERMINATED BY', weight: 3 }, { value: 'LINES TERMINATED BY', weight: 2 }, { value: 'NULL DEFINED AS', weight: 1 }] };
     } else if (!$5 && !$6) {
       $$ = { suggestKeywords: [{ value: 'LINES TERMINATED BY', weight: 2 }, { value: 'NULL DEFINED AS', weight: 1 }] };
     } else if (!$6) {
       $$ = { suggestKeywords: [{ value: 'NULL DEFINED AS', weight: 1 }] };
     }
   }
 ;

HiveDelimitedRowFormat_EDIT
 : '<hive>DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy_EDIT OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy_EDIT
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy_EDIT OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs_EDIT
 ;

ImpalaRowFormat
 : '<impala>DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy
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

ImpalaRowFormat_EDIT
 : '<impala>DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalLinesTerminatedBy
 | '<impala>DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy_EDIT
 ;

OptionalFieldsTerminatedBy
 :
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue  -> { suggestKeywords: ['ESCAPED BY'] }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue HiveOrImpalaEscaped 'BY' SingleQuotedValue
 ;

OptionalFieldsTerminatedBy_EDIT
 : HiveOrImpalaFields 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue 'ESCAPED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalCollectionItemsTerminatedBy
 :
 | '<hive>COLLECTION' '<hive>ITEMS' '<hive>TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalCollectionItemsTerminatedBy_EDIT
 : '<hive>COLLECTION' 'CURSOR'
   {
     parser.suggestKeywords(['ITEMS TERMINATED BY']);
   }
 | '<hive>COLLECTION' '<hive>ITEMS' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | '<hive>COLLECTION' '<hive>ITEMS' '<hive>TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalMapKeysTerminatedBy
 :
 | 'MAP' '<hive>KEYS' '<hive>TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalMapKeysTerminatedBy_EDIT
 : 'MAP' 'CURSOR'
   {
     parser.suggestKeywords(['KEYS TERMINATED BY']);
   }
 | 'MAP' '<hive>KEYS' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'MAP' '<hive>KEYS' '<hive>TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalLinesTerminatedBy
 :
 | HiveOrImpalaLines HiveOrImpalaTerminated 'BY' SingleQuotedValue
 ;

OptionalLinesTerminatedBy_EDIT
 : HiveOrImpalaLines 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | HiveOrImpalaLines HiveOrImpalaTerminated 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalNullDefinedAs
 :
 | 'NULL' '<hive>DEFINED' '<hive>AS' SingleQuotedValue
 ;

OptionalNullDefinedAs_EDIT
 : 'NULL' 'CURSOR'
   {
     parser.suggestKeywords(['DEFINED AS']);
   }
 | 'NULL' '<hive>DEFINED' 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 ;

OptionalWithSerdeproperties
 :
 | ImpalaWithSerdeproperties
 | HiveWithSerdeproperties
 ;

OptionalImpalaWithSerdeproperties
 :
 | ImpalaWithSerdeproperties
 ;

OptionalHiveWithSerdeproperties
 :
 | HiveWithSerdeproperties
 ;

ImpalaWithSerdeproperties
 :'<impala>WITH' '<impala>SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

HiveWithSerdeproperties
 :'<hive>WITH' '<hive>SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;
  
WithSerdeproperties_EDIT
 : HiveWithSerdeproperties_EDIT
 | ImpalaWithSerdeproperties_EDIT
 ;

HiveWithSerdeproperties_EDIT
 : '<hive>WITH' 'CURSOR'
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 | '<hive>WITH' 'CURSOR' ParenthesizedPropertyAssignmentList
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 ;

ImpalaWithSerdeproperties_EDIT
 : '<impala>WITH' 'CURSOR'
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 | '<impala>WITH' 'CURSOR' ParenthesizedPropertyAssignmentList
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 ;

OptionalTblproperties
 :
 | TblProperties
 ;
 
TblProperties
 : HiveOrImpalaTblproperties ParenthesizedPropertyAssignmentList
 ;

OptionalHiveTblproperties
 :
 | '<hive>TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalAsSelectStatement
 :
 | AnyAs CommitLocations QuerySpecification
 ;

OptionalAsSelectStatement_EDIT
 : AnyAs CommitLocations 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | AnyAs CommitLocations QuerySpecification_EDIT
 ;

CommitLocations
 : /* empty */
   {
     parser.commitLocations();
   }
 ;

ViewDefinition
 : AnyCreate AnyView OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification
 ;

ViewDefinition_EDIT
 : AnyCreate AnyView OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | AnyCreate AnyView OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate AnyView OptionalIfNotExists_EDIT
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedViewColumnList_EDIT OptionalComment OptionalHiveTblproperties
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties 'CURSOR'
   {
     var keywords = [{value: 'AS', weight: 1 }];
     if (!$7) {
       if (parser.isHive()) {
         keywords.push({ value: 'TBLPROPERTIES', weight: 2 });
       }
       if (!$6) {
         keywords.push({ value: 'COMMENT', weight: 3 });
       }
     }
     parser.suggestKeywords(keywords);
   }
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification_EDIT
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedIdentifier_EDIT OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification
 ;

FunctionDefinition
 : ImpalaFunctionDefinition
 | ImpalaAggregateFunctionDefinition
 | HiveFunctionDefinition
 | HiveTemporaryFunction
 ;

FunctionDefinition_EDIT
 : ImpalaFunctionDefinition_EDIT
 | ImpalaAggregateFunctionDefinition_EDIT
 | HiveFunctionDefinition_EDIT
 | HiveTemporaryFunction_EDIT
 ;

ImpalaFunctionDefinition
 : AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation ImpalaSymbol
 ;

ImpalaFunctionDefinition_EDIT
 : AnyCreate '<impala>FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation ImpalaSymbol
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList 'CURSOR'
   {
     parser.suggestKeywords(['RETURNS']);
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns 'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation 'CURSOR'
   {
     parser.suggestKeywords(['SYMBOL']);
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation ImpalaSymbol
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList_EDIT ImpalaReturns HdfsLocation ImpalaSymbol
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT HdfsLocation ImpalaSymbol
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation_EDIT ImpalaSymbol
 ;

ImpalaAggregateFunctionDefinition
 : AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 ;

ImpalaAggregateFunctionDefinition_EDIT
 : AnyCreate '<impala>AGGREGATE' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList_EDIT ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList 'CURSOR'
   {
     parser.suggestKeywords(['RETURNS']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn 'CURSOR'
   {
     if (!$9) {
       parser.suggestKeywords([{value: 'INIT_FN', weight: 2 }, {value: 'UPDATE_FN', weight: 1 }]);
     } else {
       parser.suggestKeywords([{value: 'UPDATE_FN', weight: 1 }]);
     }
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn 'CURSOR'
   {
     parser.suggestKeywords(['MERGE_FN']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate 'CURSOR'
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
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation_EDIT OptionalImpalaInitFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn_EDIT OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn_EDIT OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn_EDIT  OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn_EDIT OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn_EDIT OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn Intermediate_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation_EDIT OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn_EDIT ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn_EDIT ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn OptionalIntermediate
 ;

HiveFunctionDefinition
 : AnyCreate '<hive>FUNCTION' SchemaQualifiedIdentifier '<hive>AS' SingleQuotedValue OptionalHiveUsing
 ;

HiveFunctionDefinition_EDIT
 : AnyCreate '<hive>FUNCTION' SchemaQualifiedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | AnyCreate '<hive>FUNCTION' SchemaQualifiedIdentifier '<hive>AS' SingleQuotedValue OptionalHiveUsing_EDIT
 | AnyCreate '<hive>FUNCTION' SchemaQualifiedIdentifier '<hive>AS' SingleQuotedValue OptionalHiveUsing 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['USING']);
     } else {
       parser.suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
     }
   }
 ;

HiveTemporaryFunction
 : AnyCreate '<hive>TEMPORARY' '<hive>FUNCTION' RegularIdentifier '<hive>AS' SingleQuotedValue
 ;

HiveTemporaryFunction_EDIT
 : AnyCreate '<hive>TEMPORARY' '<hive>FUNCTION' RegularIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 ;

ParenthesizedImpalaArgumentList
 : '(' ')'
 | '(' ImpalaArgumentList OptionalVariableArguments')'
 ;

ParenthesizedImpalaArgumentList_EDIT
 : '(' ImpalaArgumentList_EDIT RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 | '(' ImpalaArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['...']);
   }
 ;

ImpalaArgumentList
 : PrimitiveType
 | ImpalaArgumentList ',' PrimitiveType
 ;

ImpalaArgumentList_EDIT
 : AnyCursor
 | ImpalaArgumentList ',' AnyCursor
 | AnyCursor ',' ImpalaArgumentList
 | ImpalaArgumentList ',' AnyCursor ',' ImpalaArgumentList
 ;

OptionalVariableArguments
 :
 | '<impala>...'
 ;

ImpalaReturns
 : '<impala>RETURNS' PrimitiveType
 ;

ImpalaReturns_EDIT
 : '<impala>RETURNS' 'CURSOR'
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 ;

ImpalaSymbol
 : '<impala>SYMBOL' '=' SingleQuotedValue
 ;

OptionalImpalaInitFn
 :
 | '<impala>INIT_FN' '=' FunctionReference
 ;

OptionalImpalaInitFn_EDIT
 : '<impala>INIT_FN' '=' FunctionReference_EDIT
 ;

ImpalaUpdateFn
 : '<impala>UPDATE_FN' '=' FunctionReference
 ;

ImpalaUpdateFn_EDIT
 : '<impala>UPDATE_FN' '=' FunctionReference_EDIT
 ;

ImpalaMergeFn
 : '<impala>MERGE_FN' '=' FunctionReference
 ;

ImpalaMergeFn_EDIT
 : '<impala>MERGE_FN' '=' FunctionReference_EDIT
 ;

OptionalImpalaPrepareFn
 :
 | '<impala>PREPARE_FN' '=' FunctionReference
 ;

OptionalImpalaPrepareFn_EDIT
 : '<impala>PREPARE_FN' '=' FunctionReference_EDIT
 ;

OptionalImpalaCloseFn
 :
 | '<impala>CLOSE_FN' '=' FunctionReference
 ;

OptionalImpalaCloseFn_EDIT
 : '<impala>CLOSE_FN' '=' FunctionReference_EDIT
 ;

OptionalImpalaSerializeFn
 :
 | '<impala>SERIALIZE_FN' '=' FunctionReference
 ;

OptionalImpalaSerializeFn_EDIT
 : '<impala>SERIALIZE_FN' '=' FunctionReference_EDIT
 ;

OptionalImpalaFinalizeFn
 :
 | '<impala>FINALIZE_FN' '=' FunctionReference
 ;

OptionalImpalaFinalizeFn_EDIT
 : '<impala>FINALIZE_FN' '=' FunctionReference_EDIT
 ;

OptionalIntermediate
 :
 | '<impala>INTERMEDIATE' PrimitiveType
 ;

Intermediate_EDIT
 : '<impala>INTERMEDIATE' 'CURSOR'
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

OptionalHiveUsing
 :
 | '<hive>USING' OneOrMoreFunctionResources
 ;

OptionalHiveUsing_EDIT
 : '<hive>USING' 'CURSOR'
   {
     parser.suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
   }
 ;

OneOrMoreFunctionResources
 : FunctionResource
 | OneOrMoreFunctionResources ',' FunctionResource
 ;

FunctionResource
 : FunctionResourceType SingleQuotedValue
 ;

FunctionResourceType
 : '<hive>ARCHIVE'
 | '<hive>FILE'
 | '<hive>JAR'
 ;

AnyView
 : '<hive>VIEW'
 | 'VIEW'
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
 : ColumnReference OptionalComment 'CURSOR'                                        --> $2
 | ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList                     --> $2
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR'                     --> $4
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList  --> $4
 ;

RoleDefinition
 : AnyCreate AnyRole RegularIdentifier
 ;

AnyRole
 : '<hive>ROLE'
 | '<impala>ROLE'
 | 'ROLE'
 ;

IndexDefinition
 : AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat
   OptionalStoredAsOrBy  OptionalHdfsLocation OptionalTblproperties OptionalComment
 ;

IndexDefinition_EDIT
 : AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON TABLE']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable_EDIT
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' 'CURSOR'
   {
     parser.suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType_EDIT OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable_EDIT ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild_EDIT OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable_EDIT OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable RowFormat_EDIT OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat StoredAsOrBy_EDIT OptionalHdfsLocation
   OptionalTblproperties OptionalComment
   {
     if ($13 && parser.yy.result.suggestKeywords && parser.yy.result.suggestKeywords.length === 2) {
       parser.suggestKeywords(['AS']);
     }
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy HdfsLocation_EDIT
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment 'CURSOR'
   {
     if (!$10 && !$11 && !$12 && !$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'WITH DEFERRED REBUILD', weight: 7 }, { value: 'IDXPROPERTIES', weight: 6 }, { value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$11 && !$12 && !$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'IDXPROPERTIES', weight: 6 }, { value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$12 && !$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if ($13 && $13.suggestKeywords && !$14 && !$15 && !$16) {
       parser.suggestKeywords(parser.createWeightedKeywords($13.suggestKeywords, 5).concat([{ value: 'STORED AS', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]));
     } else if (!$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'STORED AS', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$16 && !$17) {
       parser.suggestKeywords([{ value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$17) {
       parser.suggestKeywords([{ value: 'COMMENT', weight: 1 }]);
     }
   }
 ;

ExistingTable
 : SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($1);
   }
 ;

ExistingTable_EDIT
 : SchemaQualifiedTableIdentifier_EDIT
 ;

IndexType
 : QuotedValue
 ;

IndexType_EDIT
 : QuotedValue_EDIT
   {
     parser.suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 ;

OptionalWithDeferredRebuild
 :
 | '<hive>WITH' '<hive>DEFERRED' '<hive>REBUILD'
 ;

OptionalWithDeferredRebuild_EDIT
 : '<hive>WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DEFERRED REBUILD']);
   }
 | '<hive>WITH' '<hive>DEFERRED' 'CURSOR'
   {
     parser.suggestKeywords(['REBUILD']);
   }
 ;

OptionalIdxProperties
 :
 | '<hive>IDXPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalInTable
 :
 | 'IN' '<hive>TABLE' SchemaQualifiedTableIdentifier
 ;

OptionalInTable_EDIT
 : 'IN' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'IN' '<hive>TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'IN' '<hive>TABLE' SchemaQualifiedTableIdentifier_EDIT
 ;


ParenthesizedIndexColumnList
 : '(' IndexColumnList ')'
 ;

ParenthesizedIndexColumnList_EDIT
 : '(' IndexColumnList_EDIT RightParenthesisOrError
   {
     parser.suggestColumns();
   }
 ;

IndexColumnList
 : ColumnReference
 | IndexColumnList ',' ColumnReference
 ;

IndexColumnList_EDIT
 : AnyCursor
 | IndexColumnList ',' AnyCursor
 | AnyCursor ',' IndexColumnList
 | IndexColumnList ',' AnyCursor ',' IndexColumnList
 ;

MacroDefinition
 : AnyCreate '<hive>TEMPORARY' '<hive>MACRO' RegularIdentifier MacroArguments ValueExpression
 ;

MacroDefinition_EDIT
 : AnyCreate '<hive>TEMPORARY' '<hive>MACRO' RegularIdentifier MacroArguments_EDIT
 | AnyCreate '<hive>TEMPORARY' '<hive>MACRO' RegularIdentifier MacroArguments_EDIT ValueExpression
 | AnyCreate '<hive>TEMPORARY' '<hive>MACRO' RegularIdentifier MacroArguments 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | AnyCreate '<hive>TEMPORARY' '<hive>MACRO' RegularIdentifier MacroArguments ValueExpression_EDIT
 ;

MacroArguments
 : '(' ')'
 | '(' MacroArgumentList ')'
 ;

MacroArguments_EDIT
 : '(' MacroArgumentList_EDIT RightParenthesisOrError
 ;


MacroArgumentList
 : MacroArgument
 | MacroArgumentList ',' MacroArgument
 ;

MacroArgumentList_EDIT
 : MacroArgument_EDIT
 | MacroArgumentList ',' MacroArgument_EDIT
 | MacroArgument_EDIT ',' MacroArgumentList
 | MacroArgumentList ',' MacroArgument_EDIT ',' MacroArgumentList
 ;

MacroArgument
 : RegularIdentifier ColumnDataType
 ;

MacroArgument_EDIT
 : RegularIdentifier 'CURSOR'
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | RegularIdentifier ColumnDataType_EDIT
 ;