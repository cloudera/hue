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

CreateStatement
 : TableDefinition
 ;

CreateStatement_EDIT
 : TableDefinition_EDIT
 ;

TableDefinition
 : 'CREATE' OptionalExternal 'TABLE' OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : 'CREATE' OptionalExternal 'TABLE' OptionalIfNotExists TableDefinitionRightPart_EDIT
 | 'CREATE' OptionalExternal 'TABLE' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' OptionalExternal 'TABLE' OptionalIfNotExists_EDIT
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
       } else if ($5 && $5.suggestKeywords && !$6 && !$7 && !$8 && !$9 && !$10) {
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

OptionalPartitionedBy
 :
 | PartitionedBy
 ;

PartitionedBy
 : 'PARTITIONED' 'BY' ParenthesizedColumnSpecificationList
 | 'PARTITION' 'BY' HashClauses
 | 'PARTITION' 'BY' HashClauses ',' RangeClause
 | 'PARTITION' 'BY' RangeClause
 | 'PARTITIONED' 'BY' '(' ColumnIdentifierList ')'
 ;

ColumnIdentifierList
: ColumnIdentifier ',' ColumnIdentifierList
| ColumnIdentifier
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

OptionalRowFormat
 :
 | RowFormat
 ;

RowFormat
 : 'ROW' 'FORMAT' DelimitedRowFormat  -> $3
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
 | 'ROW' 'FORMAT' DelimitedRowFormat_EDIT
 ;

OptionalStoredAs
 :
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
