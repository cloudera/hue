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
 | 'CREATE' OptionalTemporary OptionalTransactional OptionalExternal 'CURSOR'
   {
     if ($4) {
       parser.suggestKeywords(['TABLE']);
     } else {
       if ($2 && !$3) {
         parser.suggestKeywords(['EXTERNAL TABLE', 'FUNCTION', 'MACRO', 'TABLE']);
       } else if (!$2 && !$3) {
         parser.suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'TEMPORARY TABLE', 'TRANSACTIONAL TABLE', 'VIEW']);
       } else if ($3) {
         parser.suggestKeywords(['TABLE']);
       }
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
 : OptionalComment OptionalHdfsLocation OptionalDbProperties
   {
     var keywords = [];
     if (!$3) {
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
 : OptionalComment_INVALID OptionalHdfsLocation OptionalDbProperties
 | OptionalComment HdfsLocation_EDIT OptionalDbProperties
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


OptionalDbProperties
 :
 | DbProperties
 ;

DbProperties
 : 'WITH' 'DBPROPERTIES' ParenthesizedPropertyAssignmentList
 | 'WITH' 'DBPROPERTIES'
 | 'WITH' 'CURSOR'
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
 : 'CREATE' OptionalTemporary OptionalTransactional OptionalExternal 'TABLE' OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : 'CREATE' OptionalTemporary OptionalTransactional OptionalExternal 'TABLE' OptionalIfNotExists TableDefinitionRightPart_EDIT
 | 'CREATE' OptionalTemporary OptionalTransactional OptionalExternal 'TABLE' OptionalIfNotExists 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' OptionalTemporary OptionalTransactional OptionalExternal 'TABLE' OptionalIfNotExists_EDIT
 ;

TableDefinitionRightPart
 : TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 ;

TableDefinitionRightPart_EDIT
 : TableIdentifierAndOptionalColumnSpecification_EDIT OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment PartitionedBy_EDIT
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   ClusteredBy_EDIT OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy SkewedBy_EDIT OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy RowFormat_EDIT OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat StoredAsOrBy_EDIT
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   WithSerdeproperties_EDIT OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties HdfsLocation_EDIT OptionalTblproperties OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties OptionalAsSelectStatement_EDIT
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalSkewedBy OptionalRowFormat OptionalStoredAsOrBy
   OptionalWithSerdeproperties OptionalHdfsLocation OptionalTblproperties 'CURSOR'
   {
     var keywords = [];
     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
       keywords.push({ value: 'LIKE', weight: 1 });
     } else {
       if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'COMMENT', weight: 10 });
       }
       if (!$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'PARTITIONED BY', weight: 9 });
       }
       if (!$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'CLUSTERED BY', weight: 8 });
       }
       if (!$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'SKEWED BY', weight: 7 });
       } else if ($5 && $5.suggestKeywords && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords = keywords.concat(parser.createWeightedKeywords($5.suggestKeywords, 7)); // Get the last optional from SKEWED BY
       }
       if (!$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'ROW FORMAT', weight: 6 });
       } else if ($6 && $6.suggestKeywords && !$7 && !$8 && !$9 && !$10) {
         keywords = keywords.concat(parser.createWeightedKeywords($6.suggestKeywords, 6));
       }
       if (!$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'STORED AS', weight: 5 });
         keywords.push({ value: 'STORED BY', weight: 5 });
       } else if ($7 && $7.storedBy && !$8 && !$9 && !$10) {
         keywords.push({ value: 'WITH SERDEPROPERTIES', weight: 4 });
       }
       if (!$9 && !$10) {
         keywords.push({ value: 'LOCATION', weight: 3 });
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
 | 'LIKE' SchemaQualifiedTableIdentifier    -> []
 ;

OptionalColumnSpecificationsOrLike_EDIT
 : ParenthesizedColumnSpecificationList_EDIT
 | 'LIKE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
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
     parser.suggestKeywords([{ value: 'PRIMARY KEY', weight: 2 }, { value: 'CONSTRAINT', weight: 1 }]);
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
     if (!$3['comment']) {
       keywords.push('COMMENT');
       if ($2.toLowerCase() === 'double') {
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

ColumnOption
 : Comment                                                   -> 'comment'
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
 : 'UNIONTYPE' '<' ColumnDataTypeList '>'
 ;

UnionType_INVALID
 : 'UNIONTYPE' '<' '>'
 ;

UnionType_EDIT
 : 'UNIONTYPE' '<' ColumnDataTypeList_EDIT GreaterThanOrError
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
 : PrimaryKeySpecification
 | 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification
 | PrimaryKeySpecification ',' 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification
 ;

ConstraintSpecification_EDIT
 : PrimaryKeySpecification_EDIT
 | PrimaryKeySpecification ',' 'CURSOR'
   {
     parser.suggestKeywords(['CONSTRAINT']);
   }
 | PrimaryKeySpecification ',' 'CONSTRAINT' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FOREIGN KEY']);
   }
 | PrimaryKeySpecification ',' 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification_EDIT
 | PrimaryKeySpecification_EDIT ',' 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification
 | 'CONSTRAINT' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FOREIGN KEY']);
   }
 | 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification_EDIT
 | 'CURSOR' 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification
   {
     parser.suggestKeywords(['PRIMARY KEY']);
   }
 ;

PrimaryKeySpecification
 : PrimaryKey ParenthesizedColumnList 'DISABLE' 'NOVALIDATE'
 ;

PrimaryKeySpecification_EDIT
 : PrimaryKey_EDIT
 | PrimaryKey ParenthesizedColumnList_EDIT
 | PrimaryKey ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['DISABLE NOVALIDATE']);
   }
 | PrimaryKey ParenthesizedColumnList 'DISABLE' 'CURSOR'
   {
     parser.suggestKeywords(['NOVALIDATE']);
   }
 | PrimaryKey ParenthesizedColumnList_EDIT 'DISABLE' 'NOVALIDATE'
 ;

ForeignKeySpecification
 : 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList 'DISABLE' 'NOVALIDATE' OptionalRelyNoRely
   {
     parser.addTablePrimary($5);
   }
 ;

ForeignKeySpecification_EDIT
 : 'FOREIGN' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList_EDIT
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['REFERENCES']);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier_EDIT
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList_EDIT
   {
     parser.addTablePrimary($5);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList 'CURSOR'
   {
     parser.addTablePrimary($5);
     parser.suggestKeywords(['DISABLE NOVALIDATE']);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList 'DISABLE' 'CURSOR'
   {
     parser.addTablePrimary($5);
     parser.suggestKeywords(['NOVALIDATE']);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList 'DISABLE' 'NOVALIDATE' OptionalRelyNoRely 'CURSOR'
   {
     parser.addTablePrimary($5);
     if (!$9) {
       parser.suggestKeywords(['NORELY', 'RELY']);
     }
   }
 ;

OptionalRelyNoRely
 :
 | 'RELY'
 | 'NORELY'
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
 : 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy 'INTO' 'UNSIGNED_INTEGER' 'BUCKETS'
 ;

ClusteredBy_EDIT
 : 'CLUSTERED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalSortedBy
 | 'CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalSortedBy 'INTO' 'UNSIGNED_INTEGER' 'BUCKETS'
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords([{ value: 'INTO', weight: 1 }, { value: 'SORTED BY', weight: 2 }]);
     } else {
       parser.suggestKeywords(['INTO']);
     }
   }
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy 'INTO' 'UNSIGNED_INTEGER' 'CURSOR'
   {
     parser.suggestKeywords(['BUCKETS']);
   }
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy_EDIT 'INTO' 'UNSIGNED_INTEGER' 'BUCKETS'
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy_EDIT
 ;

OptionalSortedBy
 :
 | 'SORTED' 'BY' ParenthesizedSortList
 ;

OptionalSortedBy_EDIT
 : 'SORTED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'SORTED' 'BY' ParenthesizedSortList_EDIT
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
 : 'SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList  -> { suggestKeywords: ['STORED AS DIRECTORIES'] }
 | 'SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList 'STORED_AS_DIRECTORIES' // Hack otherwise ambiguous with OptionalStoredAsOrBy
 ;

SkewedBy_EDIT
 : 'SKEWED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'SKEWED' 'BY' ParenthesizedColumnList 'CURSOR'
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
 : 'ROW' 'FORMAT' RowFormatSpec
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
     parser.suggestKeywords(['DELIMITED', 'SERDE']);
   }
 | 'ROW' 'FORMAT' RowFormatSpec_EDIT
 ;

OptionalStoredAsOrBy
 :
 | StoredAsOrBy
 ;

StoredAsOrBy
 : StoredAs
 | 'STORED' 'BY' QuotedValue
  {
    $$ = { storedBy: true }
  }
 ;

StoredAsOrBy_EDIT
 : 'STORED' 'CURSOR'
   {
     parser.suggestKeywords(['AS', 'BY']);
   }
 | StoredAs_EDIT
 ;

OptionalStoredAs
 :           -> { suggestKeywords: ['STORED AS'] }
 | StoredAs
 ;

StoredAs
 : 'STORED' 'AS' FileFormat
 ;

StoredAs_EDIT
 : 'STORED' 'AS' 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 ;

FileFormat
 : 'AVRO'
 | 'INPUTFORMAT' QuotedValue 'OUTPUTFORMAT' QuotedValue
 | 'JSONFILE'
 | 'ORC'
 | 'PARQUET'
 | 'RCFILE'
 | 'SEQUENCEFILE'
 | 'TEXTFILE'
 ;

RowFormatSpec
 : DelimitedRowFormat
 | 'SERDE' QuotedValue
 ;

RowFormatSpec_EDIT
 : DelimitedRowFormat_EDIT
 ;

DelimitedRowFormat
 : 'DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy OptionalLinesTerminatedBy OptionalNullDefinedAs
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

DelimitedRowFormat_EDIT
 : 'DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | 'DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy_EDIT OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | 'DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy_EDIT
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | 'DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy_EDIT OptionalNullDefinedAs
 | 'DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs_EDIT
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

OptionalCollectionItemsTerminatedBy
 :
 | 'COLLECTION' 'ITEMS' 'TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalCollectionItemsTerminatedBy_EDIT
 : 'COLLECTION' 'CURSOR'
   {
     parser.suggestKeywords(['ITEMS TERMINATED BY']);
   }
 | 'COLLECTION' 'ITEMS' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'COLLECTION' 'ITEMS' 'TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalMapKeysTerminatedBy
 :
 | 'MAP' 'KEYS' 'TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalMapKeysTerminatedBy_EDIT
 : 'MAP' 'CURSOR'
   {
     parser.suggestKeywords(['KEYS TERMINATED BY']);
   }
 | 'MAP' 'KEYS' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'MAP' 'KEYS' 'TERMINATED' 'CURSOR'
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

OptionalNullDefinedAs
 :
 | 'NULL' 'DEFINED' 'AS' SingleQuotedValue
 ;

OptionalNullDefinedAs_EDIT
 : 'NULL' 'CURSOR'
   {
     parser.suggestKeywords(['DEFINED AS']);
   }
 | 'NULL' 'DEFINED' 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 ;

OptionalWithSerdeproperties
 :
 | WithSerdeproperties
 ;

WithSerdeproperties
 :'WITH' 'SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
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
 : 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalTblproperties 'AS' QuerySpecification
 ;

ViewDefinition_EDIT
 : 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalTblproperties 'AS' QuerySpecification
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedViewColumnList_EDIT OptionalComment OptionalTblproperties
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalTblproperties 'CURSOR'
   {
     var keywords = [{value: 'AS', weight: 1 }];
     if (!$7) {
       keywords.push({ value: 'TBLPROPERTIES', weight: 2 });
       if (!$6) {
         keywords.push({ value: 'COMMENT', weight: 3 });
       }
     }
     parser.suggestKeywords(keywords);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalTblproperties 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalTblproperties 'AS' QuerySpecification_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier_EDIT OptionalParenthesizedViewColumnList OptionalComment OptionalTblproperties 'AS' QuerySpecification
 ;

FunctionDefinition
 : TemporaryFunction
 ;

FunctionDefinition_EDIT
 : TemporaryFunction_EDIT
 ;

FunctionDefinition
 : 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'AS' SingleQuotedValue OptionalUsing
 ;

FunctionDefinition_EDIT
 : 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'AS' SingleQuotedValue OptionalUsing_EDIT
 | 'CREATE' 'FUNCTION' SchemaQualifiedIdentifier 'AS' SingleQuotedValue OptionalUsing 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['USING']);
     } else {
       parser.suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
     }
   }
 ;

TemporaryFunction
 : 'CREATE' 'TEMPORARY' 'FUNCTION' RegularIdentifier 'AS' SingleQuotedValue
 ;

TemporaryFunction_EDIT
 : 'CREATE' 'TEMPORARY' 'FUNCTION' RegularIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
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

OptionalUsing
 :
 | 'USING' OneOrMoreFunctionResources
 ;

OptionalUsing_EDIT
 : 'USING' 'CURSOR'
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
 : 'ARCHIVE'
 | 'FILE'
 | 'JAR'
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

IndexDefinition
 : 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat
   OptionalStoredAsOrBy  OptionalHdfsLocation OptionalTblproperties OptionalComment
 ;

IndexDefinition_EDIT
 : 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON TABLE']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable_EDIT
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' 'CURSOR'
   {
     parser.suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType_EDIT OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable_EDIT ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild_EDIT OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable_EDIT OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable RowFormat_EDIT OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat StoredAsOrBy_EDIT OptionalHdfsLocation
   OptionalTblproperties OptionalComment
   {
     if ($13 && parser.yy.result.suggestKeywords && parser.yy.result.suggestKeywords.length === 2) {
       parser.suggestKeywords(['AS']);
     }
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy HdfsLocation_EDIT
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
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
 | 'WITH' 'DEFERRED' 'REBUILD'
 ;

OptionalWithDeferredRebuild_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DEFERRED REBUILD']);
   }
 | 'WITH' 'DEFERRED' 'CURSOR'
   {
     parser.suggestKeywords(['REBUILD']);
   }
 ;

OptionalIdxProperties
 :
 | 'IDXPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalInTable
 :
 | 'IN' 'TABLE' SchemaQualifiedTableIdentifier
 ;

OptionalInTable_EDIT
 : 'IN' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'IN' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'IN' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
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
 : 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments ValueExpression
 ;

MacroDefinition_EDIT
 : 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments_EDIT
 | 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments_EDIT ValueExpression
 | 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments ValueExpression_EDIT
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
