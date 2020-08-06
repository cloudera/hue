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

AlterStatement
 : AlterTable
 ;

AlterStatement_EDIT
 : AlterTable_EDIT
 ;

AlterTable
 : AlterTableLeftSide 'ADD' OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedInOrUncached
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'RANGE' 'PARTITION' RangePartitionSpec
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'RANGE' 'PARTITION_VALUE' '=' UnsignedValueSpecification
 | AlterTableLeftSide 'RENAME' 'TO' RegularOrBackTickedSchemaQualifiedName
 | AlterTableLeftSide 'ALTER' OptionalColumn ColumnIdentifier 'SET' KuduStorageAttribute SetValue
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide 'ALTER' OptionalColumn ColumnIdentifier 'DROP' 'DEFAULT'
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide 'SET' 'COLUMN' 'STATS' ColumnIdentifier ParenthesizedStatsList
   {
     parser.addColumnLocation($5.location, [ $5.identifier ]);
   }
 | AlterTableLeftSide 'SET' 'OWNER' RoleOrUser RegularOrBacktickedIdentifier
 | AlterTableLeftSide DropOperations
 | AlterTableLeftSide OptionalPartitionOperations
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations
 | AlterTableLeftSide 'RECOVER' 'PARTITIONS'
 ;

AlterTable_EDIT
 : AlterTableLeftSide_EDIT
 | AlterTableLeftSide_EDIT 'ADD' OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedInOrUncached
 | AlterTableLeftSide_EDIT 'RENAME' 'TO' RegularOrBackTickedSchemaQualifiedName
 | AlterTableLeftSide_EDIT 'ALTER' OptionalColumn ColumnIdentifier 'SET' KuduStorageAttribute SetValue
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide_EDIT 'ALTER' OptionalColumn ColumnIdentifier 'DROP' 'DEFAULT'
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide_EDIT 'SET' 'COLUMN' 'STATS' ColumnIdentifier ParenthesizedStatsList
   {
     parser.addColumnLocation($5.location, [ $5.identifier ]);
   }
 | AlterTableLeftSide_EDIT 'SET' 'OWNER' RoleOrUser RegularOrBacktickedIdentifier
 | AlterTableLeftSide_EDIT DropOperations
 | AlterTableLeftSide_EDIT OptionalPartitionOperations
 | AlterTableLeftSide_EDIT PartitionSpec OptionalPartitionOperations
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords([{ value: 'IF NOT EXISTS', weight: 4 }, { value: 'COLUMNS', weight: 3 }, { value: 'PARTITION', weight: 2 }, { value: 'RANGE PARTITION', weight: 1 }]);
     } else {
       parser.suggestKeywords([{ value: 'PARTITION', weight: 2 }, { value: 'RANGE PARTITION', weight: 1 }]);
     }
   }
 | AlterTableLeftSide 'REPLACE' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide 'ADD' OptionalIfNotExists_EDIT
 | AlterTableLeftSide 'ADD' OptionalIfNotExists PartitionSpec HdfsLocation_EDIT OptionalPartitionSpecs OptionalCachedInOrUncached
 | AlterTableLeftSide 'ADD' OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs_EDIT OptionalCachedInOrUncached
 | AlterTableLeftSide 'ADD' OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs CachedIn_EDIT
 | AlterTableLeftSide 'ADD' OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedInOrUncached 'CURSOR'
   {
     if (!$5 && !$6 && !$7) {
       parser.suggestKeywords(['LOCATION', 'CACHED IN', 'UNCACHED']);
     } else if (!$7) {
       parser.suggestKeywords(['CACHED IN', 'UNCACHED']);
     } else if ($7 && $7.suggestKeywords) {
       parser.suggestKeywords($7.suggestKeywords);
     }
   }
 | AlterTableLeftSide 'ADD' OptionalIfNotExists PartitionSpec_EDIT OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedIn
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'RANGE' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'RANGE' 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['VALUE']);
   }
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'RANGE' 'PARTITION_VALUE' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | AlterTableLeftSide 'ADD' OptionalIfNotExists 'RANGE' 'PARTITION' RangePartitionSpec_EDIT
 | AlterTableLeftSide 'ALTER' OptionalColumn 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['COLUMN']);
     }
     parser.suggestColumns();
   }
 | AlterTableLeftSide 'ALTER' OptionalColumn ColumnIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['DROP DEFAULT', 'SET BLOCK_SIZE', 'SET COMMENT', 'SET COMPRESSION', 'SET DEFAULT',
       'SET ENCODING']);
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide 'ALTER' OptionalColumn ColumnIdentifier 'DROP' 'CURSOR'
   {
     parser.suggestKeywords(['DEFAULT']);
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide 'ALTER' OptionalColumn ColumnIdentifier 'SET' 'CURSOR'
   {
     parser.suggestKeywords(['BLOCK_SIZE', 'COMMENT', 'COMPRESSION', 'DEFAULT', 'ENCODING']);
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide 'ALTER' OptionalColumn ColumnIdentifier 'SET' KuduStorageAttribute 'CURSOR'
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | AlterTableLeftSide 'SET' 'COLUMN' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | AlterTableLeftSide 'SET' 'COLUMN' 'STATS' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | AlterTableLeftSide 'SET' 'COLUMN' 'STATS' ColumnIdentifier 'CURSOR'
   {
     parser.addColumnLocation($5.location, [ $5.identifier ]);
   }
 | AlterTableLeftSide 'SET' 'COLUMN' 'STATS' ColumnIdentifier ParenthesizedStatsList_EDIT
   {
     parser.addColumnLocation($5.location, [ $5.identifier ]);
   }
 | AlterTableLeftSide 'SET' 'OWNER' 'CURSOR'
   {
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 | AlterTableLeftSide 'SET' 'OWNER' RoleOrUser 'CURSOR'
 | AlterTableLeftSide OptionalPartitionOperations_EDIT
 | AlterTableLeftSide DropOperations_EDIT
 | AlterTableLeftSide 'CURSOR'
   {
     parser.suggestKeywords(['ADD COLUMNS', 'ADD PARTITION', 'ADD RANGE PARTITION', 'ALTER', 'ALTER COLUMN', 'CHANGE',
       'DROP COLUMN', 'DROP PARTITION', 'DROP RANGE PARTITION', 'PARTITION', 'RECOVER PARTITIONS', 'RENAME TO',
       'REPLACE COLUMNS', 'SET CACHED IN', 'SET COLUMN STATS', 'SET FILEFORMAT', 'SET LOCATION', 'SET OWNER',
       'SET ROW FORMAT', 'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'SET UNCACHED']);
   }
 | AlterTableLeftSide PartitionSpec 'CURSOR'
   {
     parser.suggestKeywords(['SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET ROW FORMAT',
       'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'SET UNCACHED']);
   }
 | AlterTableLeftSide PartitionSpec AddOrReplace 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide PartitionSpec 'SET' 'CURSOR'
   {
     parser.suggestKeywords(['CACHED IN', 'FILEFORMAT', 'LOCATION', 'ROW FORMAT', 'SERDEPROPERTIES','TBLPROPERTIES', 'UNCACHED']);
   }
 | AlterTableLeftSide 'SET' 'CURSOR'
   {
     parser.suggestKeywords(['CACHED IN', 'COLUMN STATS', 'FILEFORMAT', 'LOCATION', 'OWNER ROLE', 'OWNER USER', 'ROW FORMAT', 'SERDEPROPERTIES', 'TBLPROPERTIES', 'UNCACHED']);
   }
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations_EDIT
 | AlterTableLeftSide 'RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | AlterTableLeftSide 'RENAME' 'TO' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
   }
 | AlterTableLeftSide 'RECOVER' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 ;

KuduStorageAttribute
 : 'BLOCK_SIZE'
 | 'COMMENT'
 | 'COMPRESSION'
 | 'DEFAULT'
 | 'ENCODING'
 ;

OptionalColumn
 :
 | 'COLUMN'
 ;


ParenthesizedStatsList
 : '(' StatsList ')'
 ;

ParenthesizedStatsList_EDIT
 : '(' StatsList_EDIT RightParenthesisOrError
 ;

StatsList
 : StatsAssignment
 | StatsList ',' StatsAssignment
 ;

StatsList_EDIT
 : StatsAssignment_EDIT
 | StatsList ',' StatsAssignment_EDIT
 | StatsList ',' StatsAssignment_EDIT ',' StatsList
 | StatsAssignment_EDIT ',' StatsList
 ;

StatsAssignment
 : QuotedValue '=' QuotedValue
 ;

StatsAssignment_EDIT
 : 'CURSOR'
   {
     parser.suggestIdentifiers(['\'avgSize\'', '\'maxSize\'', '\'numDVs\'', '\'numNulls\'']);
   }
 ;

OptionalPartitionOperations
 : 'SET' 'FILEFORMAT' FileFormat
 | 'SET' HdfsLocation
 | 'SET' 'TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 | 'SET' 'SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 | 'SET' CachedIn OptionalWithReplication
 | 'SET' 'ROW' 'FORMAT' DelimitedRowFormat
 | 'SET' 'UNCACHED'
 | AddReplaceColumns
 | 'CHANGE' ColumnIdentifier ColumnSpecification
   {
     parser.addColumnLocation($2.location, [ $2.identifier ]);
   }
 ;

OptionalPartitionOperations_EDIT
 : AddReplaceColumns_EDIT
 | 'CHANGE' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'CHANGE' ColumnIdentifier ColumnSpecification_EDIT
   {
     parser.addColumnLocation($2.location, [ $2.identifier ]);
   }
 | 'CHANGE' ColumnIdentifier ColumnSpecification 'CURSOR'
   {
     parser.addColumnLocation($2.location, [ $2.identifier ]);
   }
 | 'SET' 'FILEFORMAT' 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 | 'SET' HdfsLocation_EDIT
 | 'SET' CachedIn_EDIT
 | 'SET' CachedIn OptionalWithReplication 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['WITH REPLICATION =']);
     }
   }
 | 'SET' CachedIn WithReplication_EDIT
 | 'SET' 'ROW' 'CURSOR'
   {
     parser.suggestKeywords(['FORMAT']);
   }
 | 'SET' 'ROW' 'FORMAT' 'CURSOR'
   {
     parser.suggestKeywords(['DELIMITED']);
   }
 | 'SET' 'ROW' 'FORMAT' DelimitedRowFormat 'CURSOR'
   {
     if ($4.suggestKeywords) {
       parser.suggestKeywords($4.suggestKeywords);
     }
   }
 | 'SET' 'ROW' 'FORMAT' DelimitedRowFormat_EDIT
 ;

AddReplaceColumns
 : AddOrReplace 'COLUMNS' ParenthesizedColumnSpecificationList
 ;

AddReplaceColumns_EDIT
 : AddOrReplace 'COLUMNS' ParenthesizedColumnSpecificationList_EDIT
 | AddOrReplace 'COLUMNS' ParenthesizedColumnSpecificationList 'CURSOR'
 ;

ExchangePartitionSpec
 : 'PARTITION' '(' OneOrMorePartitionSpecLists ')'
 | 'PARTITION' '(' PartitionSpecList ')'
 ;

ExchangePartitionSpec_EDIT
 : 'PARTITION' '(' OneOrMorePartitionSpecLists_EDIT RightParenthesisOrError
 | 'PARTITION' '(' PartitionSpecList_EDIT RightParenthesisOrError
 ;

OneOrMorePartitionSpecLists
 : '(' PartitionSpecList ')'
 | OneOrMorePartitionSpecLists ',' '(' PartitionSpecList ')'
 ;

OneOrMorePartitionSpecLists_EDIT
 : '(' PartitionSpecList_EDIT RightParenthesisOrError
 | OneOrMorePartitionSpecLists ',' '(' PartitionSpecList_EDIT RightParenthesisOrError
 ;

DropOperations
 : 'DROP' OptionalIfExists PartitionSpec
 | 'DROP' OptionalIfExists 'RANGE'
 | 'DROP' OptionalIfExists 'RANGE' 'PARTITION' RangePartitionSpec
 | 'DROP' OptionalIfExists 'RANGE' 'PARTITION_VALUE' '=' UnsignedValueSpecification
 | 'DROP' 'COLUMN' ColumnIdentifier
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 ;

DropOperations_EDIT
 : 'DROP' OptionalIfExists 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords([{ value: 'COLUMN', weight: 1 }, { value: 'PARTITION', weight: 1 }, { value: 'RANGE PARTITION', weight: 1 }, { value: 'IF EXISTS', weight: 2 }]);
       parser.suggestColumns();
     } else {
       parser.suggestKeywords(['PARTITION', 'RANGE PARTITION']);
     }
   }
 | 'DROP' OptionalIfExists PartitionSpec_EDIT
 | 'DROP' OptionalIfExists PartitionSpec 'CURSOR'
 | 'DROP' OptionalIfExists_EDIT
 | 'DROP' OptionalIfExists 'RANGE' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | 'DROP' OptionalIfExists 'RANGE' 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['VALUE']);
   }
 | 'DROP' OptionalIfExists 'RANGE' 'PARTITION_VALUE' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | 'DROP' OptionalIfExists 'RANGE' 'PARTITION' RangePartitionSpec_EDIT
 | 'DROP' ColumnIdentifier_EDIT
 | 'DROP' 'COLUMN' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'DROP' 'COLUMN' ColumnIdentifier_EDIT
 ;

AlterTableLeftSide
 : 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

AlterTableLeftSide_EDIT
 : 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'ALTER' 'TABLE' 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 ;

AddOrReplace
 : 'ADD'
 | 'REPLACE'
 ;

OptionalPartitionSpecs
 :
 | PartitionSpecWithLocationList
 ;

PartitionSpecWithLocationList
 : PartitionSpecWithLocation
 | PartitionSpecWithLocationList PartitionSpecWithLocation  -> $2
 ;

OptionalPartitionSpecs_EDIT
 : PartitionSpecWithLocation_EDIT
 | PartitionSpecWithLocation_EDIT PartitionSpecWithLocationList
 | PartitionSpecWithLocationList PartitionSpecWithLocation_EDIT
 | PartitionSpecWithLocationList PartitionSpecWithLocation_EDIT PartitionSpecWithLocationList
 ;

PartitionSpecWithLocation_EDIT
 : PartitionSpec HdfsLocation_EDIT
 | PartitionSpec_EDIT OptionalHdfsLocation
 ;

PartitionSpecWithLocation
 : PartitionSpec OptionalHdfsLocation
   {
     if (!$2) {
       $$ = { suggestKeywords: ['LOCATION'] };
     }
   }
 ;
