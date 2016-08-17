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
 | AnyCreate OptionalHiveTemporary OptionalExternal 'CURSOR'
   {
     if ($3) {
       suggestKeywords(['TABLE']);
     } else if (isHive()) {
       if ($2) {
         suggestKeywords(['EXTERNAL TABLE', 'FUNCTION', 'MACRO', 'TABLE']);
       } else {
         suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'TEMPORARY TABLE', 'VIEW']);
       }
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
 ;

DatabaseDefinition
 : AnyCreate DatabaseOrSchema OptionalIfNotExists
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
 ;

DatabaseDefinition_EDIT
 : AnyCreate DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
 ;

DatabaseDefinitionOptionals
 : OptionalComment OptionalHdfsLocation OptionalHiveDbProperties
   {
     var keywords = [];
     if (!$3 && isHive()) {
       keywords.push('WITH DBPROPERTIES');
     }
     if (!$2 && !$3) {
       keywords.push('LOCATION');
     }
     if (!$1 && !$2 && !$3) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment_INVALID OptionalHdfsLocation OptionalHiveDbProperties
 | OptionalComment OptionalHdfsLocation_EDIT OptionalHiveDbProperties
 ;

OptionalComment
 :
 | Comment
 ;

Comment
 : HiveOrImpalaComment QuotedValue
 ;

Comment_INVALID
 : HiveOrImpalaComment SINGLE_QUOTE
 | HiveOrImpalaComment DOUBLE_QUOTE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE
 | HiveOrImpalaComment DOUBLE_QUOTE VALUE
 ;

OptionalComment_INVALID
 : Comment_INVALID
 ;

OptionalHdfsLocation
 :
 | HdfsLocation
 ;

OptionalHdfsLocation_EDIT
 : HdfsLocation_EDIT
 ;

HdfsLocation
 : HiveOrImpalaLocation HdfsPath
 ;

HdfsLocation_EDIT
 : HiveOrImpalaLocation HdfsPath_EDIT
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

OptionalHiveDbProperties
 :
 | HiveDbProperties
 ;

HiveDbProperties
 : '<hive>WITH' 'DBPROPERTIES' ParenthesizedPropertyAssignmentList
 | '<hive>WITH' 'DBPROPERTIES'
 | '<hive>WITH' 'CURSOR'
   {
     suggestKeywords(['DBPROPERTIES']);
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
 : AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists TableDefinitionRightPart_EDIT
 | AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists 'CURSOR'
   {
     if (!$5) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists_EDIT
 ;

TableDefinitionRightPart
 : TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 ;

TableDefinitionRightPart_EDIT
 : TableIdentifierAndOptionalColumnSpecification_EDIT OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy_EDIT OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties_EDIT OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy_EDIT
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy_EDIT OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy_EDIT OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation_EDIT OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn_EDIT OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement_EDIT
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn 'CURSOR'
   {
     // TODO: Don't always sort the keywords as order is important
     var keywords = [];
     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
       keywords.push({ value: 'LIKE', weight: 1 });
       if (isImpala()) {
         keywords.push({ value: 'LIKE PARQUET', weight: 1 });
       }
     } else {
       if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'COMMENT', weight: 10 });
       }
       if (!$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'PARTITIONED BY', weight: 9 });
       }
       if (isImpala() && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'WITH SERDEPROPERTIES', weight: 8 });
       }
       if (isHive() && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'CLUSTERED BY', weight: 7 });
       }
       if (isHive() && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'SKEWED BY', weight: 6 });
       } else if (isHive() && $6 && $6.suggestKeywords && !$7 && !$8 && !$9 && !$10) {
         keywords = keywords.concat(createWeightedKeywords($6.suggestKeywords, 6)); // Get the last optional from SKEWED BY
       }
       if (!$7 && !$8 && !$9 && !$10) {
         keywords.push({ value: 'ROW FORMAT', weight: 5 });
         keywords.push({ value: 'STORED AS', weight: 5 });
         if (isHive()) {
           keywords.push({ value: 'STORED BY', weight: 5 });
         }
       } else if ($7 && $7.suggestKeywords && !$8 && !$9 && !$10) {
         keywords = keywords.concat(createWeightedKeywords($7.suggestKeywords, 5));
       }
       if (!$8 && !$9 && !$10) {
         keywords.push({ value: 'LOCATION', weight: 4 });
       }
       if (!$9 && !$10) {
         keywords.push({ value: 'TBLPROPERTIES', weight: 3 });
       }
       if (isImpala() && !$10) {
         keywords.push({ value: 'CACHED IN', weight: 2 });
       }
       keywords.push({ value: 'AS', weight: 1 });
     }

     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

TableIdentifierAndOptionalColumnSpecification
 : SchemaQualifiedTableIdentifier OptionalColumnSpecificationsOrLike  -> $2
 ;

TableIdentifierAndOptionalColumnSpecification_EDIT
 : SchemaQualifiedTableIdentifier OptionalColumnSpecificationsOrLike_EDIT
 ;

OptionalColumnSpecificationsOrLike
 :
 | ParenthesizedColumnSpecificationList
 | '<impala>LIKE_PARQUET' HdfsPath
 | 'LIKE' SchemaQualifiedTableIdentifier
 ;

OptionalColumnSpecificationsOrLike_EDIT
 : ParenthesizedColumnSpecificationList_EDIT
 | '<impala>LIKE_PARQUET' HdfsPath_EDIT
 | 'LIKE' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
     if (isImpala()) {
       suggestKeywords(['PARQUET']);
     }
   }
 | 'LIKE' SchemaQualifiedTableIdentifier_EDIT
 ;

ParenthesizedColumnSpecificationList
 : '(' ColumnSpecificationList ')'
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
 ;

ColumnSpecificationList
 : ColumnSpecification
 | ColumnSpecificationList ',' ColumnSpecification  -> $3
 ;

ColumnSpecificationList_EDIT
 : ColumnSpecification_EDIT
 | ColumnSpecification 'CURSOR'
   {
     checkForKeywords($1);
   }
 | ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecification 'CURSOR' ',' ColumnSpecificationList
   {
     checkForKeywords($1);
   }
 | ColumnSpecificationList ',' ColumnSpecification_EDIT
 | ColumnSpecificationList ',' ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecificationList ',' ColumnSpecification 'CURSOR' ',' ColumnSpecificationList
   {
     checkForKeywords($3);
   }
 ;

ColumnSpecification
 : ColumnIdentifier ColumnDataType OptionalComment
   {
     if (!$3) {
       $$ = { suggestKeywords: ['COMMENT'] };
     }
   }
 ;

ColumnSpecification_EDIT
 : ColumnIdentifier 'CURSOR' OptionalComment
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | ColumnIdentifier ColumnDataType_EDIT OptionalComment
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
 : '<hive>ARRAY' '<' ColumnDataType '>'
 ;

ArrayType_INVALID
 : '<hive>ARRAY' '<' '>'
 ;

ArrayType_EDIT
 : '<hive>ARRAY' '<' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | '<hive>ARRAY' '<' ColumnDataType_EDIT GreaterThanOrError
 ;

MapType
 : '<hive>MAP' '<' PrimitiveType ',' ColumnDataType '>'
 ;

MapType_INVALID
 : '<hive>MAP' '<' '>'
 ;

MapType_EDIT
 : '<hive>MAP' '<' PrimitiveType ',' ColumnDataType_EDIT GreaterThanOrError
 | '<hive>MAP' '<' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getTypeKeywords());
   }
 | '<hive>MAP' '<' PrimitiveType ',' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | '<hive>MAP' '<' ',' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 ;

StructType
 : '<hive>STRUCT' '<' StructDefinitionList '>'
 ;

StructType_INVALID
 : '<hive>STRUCT' '<' '>'
 ;

StructType_EDIT
 : '<hive>STRUCT' '<' StructDefinitionList_EDIT GreaterThanOrError
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
     suggestKeywords(['COMMENT']);
   }
 | Commas RegularOrBacktickedIdentifier ':' AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | Commas RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 | RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     suggestKeywords(['COMMENT']);
   }
 | RegularOrBacktickedIdentifier ':' AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
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
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | Commas ColumnDataType_EDIT
 | AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | ColumnDataType_EDIT
 ;

GreaterThanOrError
 : '>'
 | error
 ;

OptionalPartitionedBy
 :
 | HiveOrImpalaPartitioned 'BY' ParenthesizedColumnSpecificationList
 ;

OptionalPartitionedBy_EDIT
 : HiveOrImpalaPartitioned 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | HiveOrImpalaPartitioned 'CURSOR' ParenthesizedColumnSpecificationList
   {
     suggestKeywords(['BY']);
   }
 | HiveOrImpalaPartitioned 'BY' ParenthesizedColumnSpecificationList_EDIT
 | HiveOrImpalaPartitioned ParenthesizedColumnSpecificationList_EDIT
 ;

OptionalHiveClusteredBy
 :
 | HiveClusteredBy
 ;

HiveClusteredBy
 : '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 ;

OptionalHiveClusteredBy_EDIT
 : HiveClusteredBy_EDIT
 ;

HiveClusteredBy_EDIT
 : '<hive>CLUSTERED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalHiveSortedBy
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'CURSOR'
   {
     if (!$4) {
       suggestKeywords([{ value: 'INTO', weight: 1 }, { value: 'SORTED BY', weight: 2 }]);
     } else {
       suggestKeywords(['INTO']);
     }
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' 'CURSOR'
   {
     suggestKeywords(['BUCKETS']);
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
     suggestKeywords(['BY']);
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
     checkForKeywords($2);
   }
 | ColumnIdentifier_EDIT OptionalAscOrDesc
 | AnyCursor OptionalAscOrDesc
   {
     suggestColumns();
   }
 ;

OptionalHiveSkewedBy
 :
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList  -> { suggestKeywords: ['STORED AS DIRECTORIES'] }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList '<hive>STORED_AS_DIRECTORIES' // Hack otherwise ambiguous with OptionalHiveStoredAsOrBy
 ;

OptionalHiveSkewedBy_EDIT
 : '<hive>SKEWED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 ;

ParenthesizedSkewedValueList
 : '(' SkewedValueList ')'
 ;

SkewedValueList
 : ParenthesizedSimpleValueList
 | SkewedValueList ',' ParenthesizedSimpleValueList
 ;

OptionalStoredAsOrBy
 :
 | StoredAs
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat OptionalStoredAs
   {
     $$ = mergeSuggestKeywords($3, $4)
   }
 | '<hive>STORED' 'BY' QuotedValue OptionalHiveWithSerdeproperties
  {
    if (!$4) {
      $$ = { suggestKeywords: ['WITH SERDEPROPERTIES'] };
    }
  }
 ;

OptionalStoredAsOrBy_EDIT
 : HiveOrImpalaStored 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['AS', 'BY']);
     } else {
       suggestKeywords(['AS']);
     }
   }
 | StoredAs_EDIT
 | 'ROW' 'CURSOR'
   {
     suggestKeywords(['FORMAT']);
   }
 | 'ROW' HiveOrImpalaFormat 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['DELIMITED', 'SERDE']);
     } else {
       suggestKeywords(['DELIMITED']);
     }
   }
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat_EDIT
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat HiveOrImpalaStored 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat StoredAs_EDIT
 | '<hive>STORED' 'BY' QuotedValue OptionalHiveWithSerdeproperties_EDIT
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
     suggestFileFormats();
   }
 ;

FileFormat
 : '<hive>AVRO'
 | '<hive>INPUTFORMAT' QuotedValue '<hive>OUTPUTFORMAT' QuotedValue
 | '<hive>ORC'
 | '<hive>PARQUET'
 | '<hive>RCFILE'
 | '<hive>SEQUENCEFILE'
 | '<hive>TEXTFILE'
 | '<impala>AVRO'
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
 | '<hive>SERDE' QuotedValue OptionalHiveWithSerdeproperties
   {
     if (!$3) {
       $$ = { suggestKeywords: [{ value: 'WITH SERDEPROPERTIES', weight: 1 }] };
     }
   }
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
       $$ = { suggestKeywords: createWeightedKeywords($2.suggestKeywords, 5).concat([{ value: 'COLLECTION ITEMS TERMINATED BY', weight: 4 }, { value: 'MAP KEYS TERMINATED BY', weight: 3 }, { value: 'LINES TERMINATED BY', weight: 2 }, { value: 'NULL DEFINED AS', weight: 1 }]) };
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
       $$ = { suggestKeywords: createWeightedKeywords($2.suggestKeywords, 2).concat(['LINES TERMINATED BY']) };
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
     suggestKeywords(['TERMINATED BY']);
   }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue 'ESCAPED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OptionalCollectionItemsTerminatedBy
 :
 | '<hive>COLLECTION' '<hive>ITEMS' '<hive>TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalCollectionItemsTerminatedBy_EDIT
 : '<hive>COLLECTION' 'CURSOR'
   {
     suggestKeywords(['ITEMS TERMINATED BY']);
   }
 | '<hive>COLLECTION' '<hive>ITEMS' 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | '<hive>COLLECTION' '<hive>ITEMS' '<hive>TERMINATED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OptionalMapKeysTerminatedBy
 :
 | '<hive>MAP' '<hive>KEYS' '<hive>TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalMapKeysTerminatedBy_EDIT
 : '<hive>MAP' 'CURSOR'
   {
     suggestKeywords(['KEYS TERMINATED BY']);
   }
 | '<hive>MAP' '<hive>KEYS' 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | '<hive>MAP' '<hive>KEYS' '<hive>TERMINATED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OptionalLinesTerminatedBy
 :
 | HiveOrImpalaLines HiveOrImpalaTerminated 'BY' SingleQuotedValue
 ;

OptionalLinesTerminatedBy_EDIT
 : HiveOrImpalaLines 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | HiveOrImpalaLines HiveOrImpalaTerminated 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OptionalNullDefinedAs
 :
 | 'NULL' '<hive>DEFINED' '<hive>AS' SingleQuotedValue
 ;

OptionalNullDefinedAs_EDIT
 : 'NULL' 'CURSOR'
   {
     suggestKeywords(['DEFINED AS']);
   }
 | 'NULL' '<hive>DEFINED' 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 ;

OptionalHiveWithSerdeproperties
 :
 | 'WITH' '<hive>SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalHiveWithSerdeproperties_EDIT
 : OptionalImpalaWithSerdeproperties_EDIT
 ;

OptionalImpalaWithSerdeproperties
 :
 | 'WITH' '<impala>SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalImpalaWithSerdeproperties_EDIT
 : 'WITH' 'CURSOR'
   {
     suggestKeywords(['SERDEPROPERTIES']);
   }
 | 'WITH' 'CURSOR' ParenthesizedPropertyAssignmentList
   {
     suggestKeywords(['SERDEPROPERTIES']);
   }
 ;

OptionalTblproperties
 :
 | HiveOrImpalaTblproperties ParenthesizedPropertyAssignmentList
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
     suggestKeywords(['SELECT']);
   }
 | AnyAs CommitLocations QuerySpecification_EDIT
 ;

CommitLocations
 : /* empty */
   {
     commitLocations();
   }
 ;

OptionalImpalaCachedIn
 :
 | ImpalaCachedIn
 ;

OptionalImpalaCachedIn_EDIT
 : ImpalaCachedIn_EDIT
 ;

ImpalaCachedIn
 : '<impala>CACHED' 'IN' SingleQuotedValue
 ;

ImpalaCachedIn_EDIT
 : '<impala>CACHED' 'CURSOR'
   {
     suggestKeywords(['IN']);
   }
 ;

ViewDefinition
 : AnyCreate AnyView OptionalIfNotExists SchemaQualifiedTableIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification
 ;

ViewDefinition_EDIT
 : AnyCreate AnyView OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
     suggestDatabases({ appendDot: true });
   }
 | AnyCreate AnyView OptionalIfNotExists 'CURSOR' SchemaQualifiedTableIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate AnyView OptionalIfNotExists_EDIT
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedTableIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties 'CURSOR'
   {
     if (isHive() && !$6 && !$7) {
       suggestKeywords([{ value: 'COMMENT', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, {value: 'AS', weight: 1 }]);
     } else if (isHive() && !$7) {
       suggestKeywords([{ value: 'TBLPROPERTIES', weight: 2 }, {value: 'AS', weight: 1 }]);
     } else {
       suggestKeywords([{value: 'AS', weight: 1 }]);
     }
   }
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedTableIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs 'CURSOR'
   {
     suggestKeywords(['SELECT']);
   }
 | AnyCreate AnyView OptionalIfNotExists SchemaQualifiedTableIdentifier OptionalParenthesizedViewColumnList OptionalComment OptionalHiveTblproperties AnyAs QuerySpecification_EDIT
 ;

// TODO: rename SchemaQualifiedTableIdentifier to SchemaQualifiedIdentifier
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
 : AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation ImpalaSymbol
 ;

ImpalaFunctionDefinition_EDIT
 : AnyCreate '<impala>FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
     suggestDatabases({ appendDot: true });
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation ImpalaSymbol
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList 'CURSOR'
   {
     suggestKeywords(['RETURNS']);
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns 'CURSOR'
   {
     suggestKeywords(['LOCATION']);
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation 'CURSOR'
   {
     suggestKeywords(['SYMBOL']);
   }
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation_EDIT
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation ImpalaSymbol
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList_EDIT ImpalaReturns HdfsLocation ImpalaSymbol
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT HdfsLocation ImpalaSymbol
 | AnyCreate '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns HdfsLocation_EDIT ImpalaSymbol
 ;

ImpalaAggregateFunctionDefinition
 : AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 ;

ImpalaAggregateFunctionDefinition_EDIT
 : AnyCreate '<impala>AGGREGATE' 'CURSOR'
   {
     suggestKeywords(['FUNCTION']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
   {
     if (!$4) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['IF NOT EXISTS']);
     }
     suggestDatabases({ appendDot: true });
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList_EDIT ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList 'CURSOR'
   {
     suggestKeywords(['RETURNS']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   'CURSOR'
   {
     suggestKeywords(['LOCATION']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn 'CURSOR'
   {
     if (!$9) {
       suggestKeywords([{value: 'INIT_FN', weight: 2 }, {value: 'UPDATE_FN', weight: 1 }]);
     } else {
       suggestKeywords([{value: 'UPDATE_FN', weight: 1 }]);
     }
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn 'CURSOR'
   {
     suggestKeywords(['MERGE_FN']);
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn 'CURSOR'
   {
     if (!$12 && !$13 && !$14 && !$15) {
       suggestKeywords([{value: 'PREPARE_FN', weight: 4 }, {value: 'CLOSE_FN', weight: 3 }, {value: 'SERIALIZE_FN', weight: 2 }, {value: 'FINALIZE_FN', weight: 1 }]);
     } else if ($12 && !$13 && !$14 && !$15) {
       suggestKeywords([{value: 'CLOSE_FN', weight: 3 }, {value: 'SERIALIZE_FN', weight: 2 }, {value: 'FINALIZE_FN', weight: 1 }]);
     } else if ($13 && !$14 && !$15) {
       suggestKeywords([{value: 'SERIALIZE_FN', weight: 2 }, {value: 'FINALIZE_FN', weight: 1 }]);
     } else if ($14 && !$15) {
       suggestKeywords([{value: 'FINALIZE_FN', weight: 1 }]);
     }
   }
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation_EDIT OptionalImpalaInitFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn_EDIT OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn_EDIT OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn_EDIT  OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn_EDIT OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn_EDIT
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns_EDIT
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation_EDIT OptionalImpalaInitFn ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn_EDIT ImpalaUpdateFn ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 | AnyCreate '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfNotExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList ImpalaReturns
   HdfsLocation OptionalImpalaInitFn ImpalaUpdateFn_EDIT ImpalaMergeFn OptionalImpalaPrepareFn OptionalImpalaCloseFn OptionalImpalaSerializeFn OptionalImpalaFinalizeFn
 ;

HiveFunctionDefinition
 : AnyCreate '<hive>FUNCTION' SchemaQualifiedTableIdentifier '<hive>AS' SingleQuotedValue OptionalHiveUsing
 ;

HiveFunctionDefinition_EDIT
 : AnyCreate '<hive>FUNCTION' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 | AnyCreate '<hive>FUNCTION' SchemaQualifiedTableIdentifier '<hive>AS' SingleQuotedValue OptionalHiveUsing_EDIT
 | AnyCreate '<hive>FUNCTION' SchemaQualifiedTableIdentifier '<hive>AS' SingleQuotedValue OptionalHiveUsing 'CURSOR'
   {
     if (!$6) {
       suggestKeywords(['USING']);
     } else {
       suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
     }
   }
 ;

HiveTemporaryFunction
 : AnyCreate '<hive>TEMPORARY' '<hive>FUNCTION' RegularIdentifier '<hive>AS' SingleQuotedValue
 ;

HiveTemporaryFunction_EDIT
 : AnyCreate '<hive>TEMPORARY' '<hive>FUNCTION' RegularIdentifier 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 ;

ParenthesizedImpalaArgumentList
 : '(' ')'
 | '(' ImpalaArgumentList OptionalVariableArguments')'
 ;

ParenthesizedImpalaArgumentList_EDIT
 : '(' ImpalaArgumentList_EDIT RightParenthesisOrError
   {
     suggestKeywords(getTypeKeywords());
   }
 | '(' ImpalaArgumentList 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(['...']);
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
     suggestKeywords(getTypeKeywords());
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

FunctionReference
 : SingleQuotedValue
 ;

FunctionReference_EDIT
 : SingleQuotedValue_EDIT
   {
     suggestFunctions();
     suggestAggregateFunctions();
     suggestAnalyticFunctions();
   }
 ;

OptionalHiveUsing
 :
 | '<hive>USING' OneOrMoreFunctionResources
 ;

OptionalHiveUsing_EDIT
 : '<hive>USING' 'CURSOR'
   {
     suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
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

ViewColumnList
 : ColumnReference OptionalComment
 | ViewColumnList ',' ColumnReference OptionalComment
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
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 ;

ExistingTable
 : SchemaQualifiedTableIdentifier
   {
     addTablePrimary($1);
   }
 ;

ExistingTable_EDIT
 : SchemaQualifiedTableIdentifier_EDIT
 ;

IndexDefinition_EDIT
 : AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['ON TABLE']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     suggestKeywords(['TABLE']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable_EDIT
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' 'CURSOR'
   {
     suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType_EDIT OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable_EDIT ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild_EDIT OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable_EDIT OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy_EDIT OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation_EDIT
   OptionalTblproperties OptionalComment
 | AnyCreate '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' '<hive>TABLE' ExistingTable ParenthesizedIndexColumnList
   '<hive>AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment 'CURSOR'
   {
     if (!$10 && !$11 && !$12 && !$13 && !$14 && !$15 && !$16) {
       suggestKeywords([{ value: 'WITH DEFERRED REBUILD', weight: 7 }, { value: 'IDXPROPERTIES', weight: 6 }, { value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$11 && !$12 && !$13 && !$14 && !$15 && !$16) {
       suggestKeywords([{ value: 'IDXPROPERTIES', weight: 6 }, { value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$12 && !$13 && !$14 && !$15 && !$16) {
       suggestKeywords([{ value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$13 && !$14 && !$15 && !$16) {
       suggestKeywords([{ value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if ($13 && $13.suggestKeywords && !$14 && !$15 && !$16) {
       suggestKeywords(createWeightedKeywords($13.suggestKeywords, 4).concat([{ value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]));
     } else if (!$14 && !$15 && !$16) {
       suggestKeywords([{ value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$15 && !$16) {
       suggestKeywords([{ value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$16) {
       suggestKeywords([{ value: 'COMMENT', weight: 1 }]);
     }
   }
 ;

IndexType
 : QuotedValue
 ;

IndexType_EDIT
 : QuotedValue_EDIT
   {
     suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 ;

OptionalWithDeferredRebuild
 :
 | 'WITH' '<hive>DEFERRED' '<hive>REBUILD'
 ;

OptionalWithDeferredRebuild_EDIT
 : 'WITH' 'CURSOR'
   {
     suggestKeywords(['DEFERRED REBUILD']);
   }
 | 'WITH' '<hive>DEFERRED' 'CURSOR'
   {
     suggestKeywords(['REBUILD']);
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
     suggestKeywords(['TABLE']);
   }
 | 'IN' '<hive>TABLE' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | 'IN' '<hive>TABLE' SchemaQualifiedTableIdentifier_EDIT
 ;


ParenthesizedIndexColumnList
 : '(' IndexColumnList ')'
 ;

ParenthesizedIndexColumnList_EDIT
 : '(' IndexColumnList_EDIT RightParenthesisOrError
   {
     suggestColumns();
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
     suggestFunctions();
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
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | RegularIdentifier ColumnDataType_EDIT
 ;