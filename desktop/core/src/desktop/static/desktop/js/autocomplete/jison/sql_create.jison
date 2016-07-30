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
 ;

CreateStatement_EDIT
 : DatabaseDefinition_EDIT
 | TableDefinition_EDIT
 | AnyCreate OptionalHiveTemporary OptionalExternal 'CURSOR'
   {
     if ($3) {
       suggestKeywords(['TABLE']);
     } else if (isHive()) {
       if ($2) {
         suggestKeywords(['EXTERNAL TABLE', 'TABLE']);
       } else {
         suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE', 'TEMPORARY TABLE']);
       }
     } else if (isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
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
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
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
 : HiveOrImpalaComment SingleQuotedValue
 ;

Comment_INVALID
 : HiveOrImpalaComment SINGLE_QUOTE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE
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
       keywords.push('LIKE');
       if (isImpala()) {
         keywords.push('LIKE PARQUET');
       }
     } else {
       keywords.push('AS');
       if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('COMMENT');
       }
       if (!$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('PARTITIONED BY');
       }
       if (isImpala() && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('WITH SERDEPROPERTIES');
       }
       if (isHive() && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('CLUSTERED BY');
       }
       if (isHive() && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('SKEWED BY');
       } else if (isHive() && $6 && $6.suggestKeywords && !$7 && !$8 && !$9 && !$10) {
         keywords = keywords.concat($6.suggestKeywords); // Get the last optional from SKEWED BY
       }
       if (!$7 && !$8 && !$9 && !$10) {
         keywords.push('ROW FORMAT');
         keywords.push('STORED AS');
         if (isHive()) {
          keywords.push('STORED BY');
         }
       } else if ($7 && $7.suggestKeywords && !$8 && !$9 && !$10) {
         keywords = keywords.concat($7.suggestKeywords);
       }
       if (!$8 && !$9 && !$10) {
         keywords.push('LOCATION');
       }
       if (!$9 && !$10) {
         keywords.push('TBLPROPERTIES');
       }
       if (isImpala() && !$10) {
         keywords.push('CACHED IN');
       }
     }

     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

// Hack as no space is required between table name and '(' which would be read as UDF(
// can be dropped if switched to LR(*)
TableIdentifierAndOptionalColumnSpecification
 : SchemaQualifiedTableIdentifier OptionalColumnSpecificationsOrLike  -> $2
 | 'UDF(' DropLastLocation ColumnSpecificationList ')'
 | RegularOrBacktickedIdentifier AnyDot 'UDF(' DropLastLocation ColumnSpecificationList ')'
 ;

TableIdentifierAndOptionalColumnSpecification_EDIT
 : SchemaQualifiedTableIdentifier OptionalColumnSpecificationsOrLike_EDIT
 | 'UDF(' DropLastLocation ColumnSpecificationList_EDIT RightParenthesisOrError
 | RegularOrBacktickedIdentifier AnyDot 'UDF(' DropLastLocation ColumnSpecificationList_EDIT RightParenthesisOrError
 ;

DropLastLocation
 : /* Empty */
   {
     if (parser.yy.locations.length > 0) {
       parser.yy.locations.pop();
     }
   }
 ;

OptionalHiveTemporary
 :
 | '<hive>TEMPORARY'
 ;

OptionalExternal
 :
 | '<hive>EXTERNAL'
 | '<impala>EXTERNAL'
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
 | ColumnSpecificationList ',' ColumnSpecification
 ;

ColumnSpecificationList_EDIT
 : ColumnSpecification_EDIT
 | ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecificationList ',' ColumnSpecification_EDIT
 | ColumnSpecificationList ',' ColumnSpecification_EDIT ',' ColumnSpecificationList
 ;

ColumnSpecification
 : ColumnIdentifier ColumnDataType OptionalComment
 ;

ColumnSpecification_EDIT
 : ColumnIdentifier 'CURSOR' OptionalComment
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | ColumnIdentifier ColumnDataType_EDIT
 | ColumnIdentifier ColumnDataType OptionalComment 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['COMMENT']);
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

Commas
 : ','
 | Commas ','
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

ParenthesizedColumnList
 : '(' ColumnList ')'
 ;

ColumnList
 : ColumnIdentifier
 | ColumnList ',' ColumnIdentifier
 ;

OptionalHiveClusteredBy
 :
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 ;

OptionalHiveClusteredBy_EDIT
 : '<hive>CLUSTERED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['INTO', 'SORTED BY']);
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

ParenthesizedSimpleValueList
 : '(' SimpleValueList ')'
 ;

SimpleValueList
 : UnsignedValueSpecification
 | SimpleValueList ',' UnsignedValueSpecification
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
     if (isHive()) {
       suggestKeywords(['AVRO', 'INPUTFORMAT', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
     } else {
       suggestKeywords(['AVRO', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
     }
   }
 ;

HiveOrImpalaFormat
 : '<hive>FORMAT'
 | '<impala>FORMAT'
 ;

HiveOrImpalaStored
 : '<hive>STORED'
 | '<impala>STORED'
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
 : '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
   {
     if (!$2 && !$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: ['COLLECTION ITEMS TERMINATED BY', 'FIELDS TERMINATED BY', 'LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS'] };
     } else if ($2 && $2.suggestKeywords && !$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: $2.suggestKeywords.concat(['COLLECTION ITEMS TERMINATED BY', 'LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS']) };
     } else if (!$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: ['COLLECTION ITEMS TERMINATED BY', 'LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS'] };
     } else if (!$4 && !$5 && !$6) {
       $$ = { suggestKeywords: ['LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS'] };
     } else if (!$5 && !$6) {
       $$ = { suggestKeywords: ['LINES TERMINATED BY', 'NULL DEFINED AS'] };
     } else if (!$6) {
       $$ = { suggestKeywords: ['NULL DEFINED AS'] };
     }
   }
 | '<hive>SERDE' QuotedValue OptionalHiveWithSerdeproperties
   {
     if (!$3) {
       $$ = { suggestKeywords: ['WITH SERDEPROPERTIES'] };
     }
   }
 ;

HiveRowFormat_EDIT
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
       $$ = { suggestKeywords: ['FIELDS TERMINATED BY', 'LINES TERMINATED BY'] };
     } else if ($2 && $2.suggestKeywords && !$3) {
       $$ = { suggestKeywords: $2.suggestKeywords.concat(['LINES TERMINATED BY']) };
     } else if (!$3) {
       $$ = { suggestKeywords: ['LINES TERMINATED BY'] };
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

HiveOrImpalaFields
 : '<hive>FIELDS'
 | '<impala>FIELDS'
 ;

HiveOrImpalaTerminated
 : '<hive>TERMINATED'
 | '<impala>TERMINATED'
 ;

HiveOrImpalaEscaped
 : '<hive>ESCAPED'
 | '<impala>ESCAPED'
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

HiveOrImpalaLines
 : '<hive>LINES'
 | '<impala>LINES'
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
 | '<impala>CACHED' 'IN' QuotedValue
 ;

OptionalImpalaCachedIn_EDIT
 : '<impala>CACHED' 'CURSOR'
   {
     suggestKeywords(['IN']);
   }
 ;

QuotedValue
 : SingleQuotedValue
 | DoubleQuotedValue
 ;

HiveOrImpalaTblproperties
 : '<hive>TBLPROPERTIES'
 | '<impala>TBLPROPERTIES'
 ;

HiveOrImpalaPartitioned
 : '<hive>PARTITIONED'
 | '<impala>PARTITIONED'
 ;