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
 : AlterStatement
 ;

DataDefinition_EDIT
 : AlterStatement_EDIT
 ;

AlterStatement
 : AlterDatabase
 | AlterIndex
 | AlterTable
 | AlterView
 | Msck
 | ReloadFunction
 | CommentOn
 ;

AlterStatement_EDIT
 : AlterDatabase_EDIT
 | AlterIndex_EDIT
 | AlterTable_EDIT
 | AlterView_EDIT
 | Msck_EDIT
 | ReloadFunction_EDIT
 | CommentOn_EDIT
 | 'ALTER' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['DATABASE', 'INDEX', 'SCHEMA', 'TABLE', 'VIEW']);
     } else {
       parser.suggestKeywords(['TABLE', 'VIEW']);
     }
   }
 ;

AlterDatabase
 : 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' '<hive>DBPROPERTIES' ParenthesizedPropertyAssignmentList
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
    }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' HdfsLocation
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
    }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' '<hive>OWNER' PrincipalSpecification
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
    }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' '<impala>OWNER' ImpalaRoleOrUser RegularOrBacktickedIdentifier
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
    }
 ;

AlterDatabase_EDIT
 : 'ALTER' DatabaseOrSchema 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestDatabases();
     }
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
     if (parser.isHive()) {
       parser.suggestKeywords(['SET DBPROPERTIES', 'SET LOCATION', 'SET OWNER']);
     }
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' 'CURSOR'
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
      if (parser.isHive()) {
        parser.suggestKeywords(['DBPROPERTIES', 'LOCATION', 'OWNER']);
      } else if (parser.isImpala()) {
        parser.suggestKeywords(['OWNER']);
      }
    }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' HdfsLocation_EDIT
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' '<hive>OWNER' 'CURSOR'
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' '<impala>OWNER' 'CURSOR'
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' '<hive>OWNER' PrincipalSpecification_EDIT
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
   }
 ;

AlterIndex
 : 'ALTER' '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>REBUILD'
   {
     parser.addTablePrimary($5);
   }
 ;

AlterIndex_EDIT
 : 'ALTER' '<hive>INDEX' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'ALTER' '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ALTER' '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier_EDIT
 | 'ALTER' '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     parser.addTablePrimary($5);
   }
 | 'ALTER' '<hive>INDEX' RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($5);
     if (!$6) {
       parser.suggestKeywords(['PARTITION', 'REBUILD']);
     } else {
       parser.suggestKeywords(['REBUILD']);
     }
   }
 ;

AlterTable
 : AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedInOrUncached
 | AlterTableLeftSide AnyAdd OptionalIfNotExists '<impala>RANGE' 'PARTITION' RangePartitionSpec
 | AlterTableLeftSide AnyAdd OptionalIfNotExists '<impala>RANGE' '<impala>PARTITION_VALUE' '=' UnsignedValueSpecification
 | AlterTableLeftSide AnyAdd '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HivePrimaryKeySpecification
 | AlterTableLeftSide AnyAdd '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification
 | AlterTableLeftSide AnyRename 'TO' RegularOrBackTickedSchemaQualifiedName
 | AlterTableLeftSide HiveSpecificOperations
 | AlterTableLeftSide ImpalaSpecificOperations
 | AlterTableLeftSide DropOperations
 | AlterTableLeftSide OptionalPartitionOperations
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations
 | AlterTableLeftSide '<impala>RECOVER' '<impala>PARTITIONS'
 ;

AlterTable_EDIT
 : AlterTableLeftSide_EDIT
 | AlterTableLeftSide_EDIT AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedInOrUncached
 | AlterTableLeftSide_EDIT AnyRename 'TO' RegularOrBackTickedSchemaQualifiedName
 | AlterTableLeftSide_EDIT HiveSpecificOperations
 | AlterTableLeftSide_EDIT ImpalaSpecificOperations
 | AlterTableLeftSide_EDIT DropOperations
 | AlterTableLeftSide_EDIT OptionalPartitionOperations
 | AlterTableLeftSide_EDIT PartitionSpec OptionalPartitionOperations
 | AlterTableLeftSide AnyAdd OptionalIfNotExists 'CURSOR'
   {
     if (!$3 && parser.isImpala()) {
       parser.suggestKeywords([{ value: 'IF NOT EXISTS', weight: 4 }, { value: 'COLUMNS', weight: 3 }, { value: 'PARTITION', weight: 2 }, { value: 'RANGE PARTITION', weight: 1 }]);
     } else if (!$3 && parser.isHive()) {
       parser.suggestKeywords([{ value: 'IF NOT EXISTS', weight: 3 }, { value: 'COLUMNS', weight: 2 }, { value: 'CONSTRAINT', weight: 1 }, {  value: 'PARTITION', weight: 1 }]);
     } else if (parser.isImpala()) {
       parser.suggestKeywords([{ value: 'PARTITION', weight: 2 }, { value: 'RANGE PARTITION', weight: 1 }]);
     } else if (parser.isHive()) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | AlterTableLeftSide AnyReplace 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists_EDIT
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec HdfsLocation_EDIT OptionalPartitionSpecs OptionalCachedInOrUncached
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs_EDIT OptionalCachedInOrUncached
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs CachedIn_EDIT
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedInOrUncached 'CURSOR'
   {
     if (parser.isHive()) {
       if (!$5 && !$6 && !$7) {
         parser.suggestKeywords(['LOCATION', 'PARTITION']);
       } else if ($6 && $6.suggestKeywords) {
         var keywords = parser.createWeightedKeywords($6.suggestKeywords, 2);
         keywords.push({ value: 'PARTITION', weight: 1 });
         parser.suggestKeywords(keywords);
       } else {
         parser.suggestKeywords(['PARTITION']);
       }
     } else if (parser.isImpala()) {
       if (!$5 && !$6 && !$7) {
         parser.suggestKeywords(['LOCATION', 'CACHED IN', 'UNCACHED']);
       } else if (!$7) {
         parser.suggestKeywords(['CACHED IN', 'UNCACHED']);
       } else if ($7 && $7.suggestKeywords) {
         parser.suggestKeywords($7.suggestKeywords);
       }
     }
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec_EDIT OptionalHdfsLocation OptionalPartitionSpecs OptionalCachedIn
 | AlterTableLeftSide AnyAdd OptionalIfNotExists '<impala>RANGE' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists '<impala>RANGE' 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['VALUE']);
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists '<impala>RANGE' '<impala>PARTITION_VALUE' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists '<impala>RANGE' 'PARTITION' RangePartitionSpec_EDIT
 | AlterTableLeftSide AnyAdd '<hive>CONSTRAINT' 'CURSOR'
 | AlterTableLeftSide AnyAdd '<hive>CONSTRAINT' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FOREIGN KEY', 'PRIMARY KEY']);
   }
 | AlterTableLeftSide AnyAdd '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HivePrimaryKeySpecification_EDIT
 | AlterTableLeftSide AnyAdd '<hive>CONSTRAINT' RegularOrBacktickedIdentifier HiveForeignKeySpecification_EDIT
 | AlterTableLeftSide HiveSpecificOperations_EDIT
 | AlterTableLeftSide ImpalaSpecificOperations_EDIT
 | AlterTableLeftSide OptionalPartitionOperations_EDIT
 | AlterTableLeftSide DropOperations_EDIT
 | AlterTableLeftSide 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['ADD COLUMNS', 'ADD IF NOT EXISTS', 'ADD PARTITION', 'ARCHIVE PARTITION', 'CHANGE',
         'CLUSTERED BY', 'CONCATENATE', 'COMPACT', 'DISABLE NO_DROP', 'DISABLE OFFLINE', 'DROP', 'ENABLE NO_DROP',
         'ENABLE OFFLINE', 'EXCHANGE PARTITION', 'NOT SKEWED', 'NOT STORED AS DIRECTORIES', 'PARTITION',
         'RECOVER PARTITIONS', 'RENAME TO', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION', 'SET OWNER', 'SET SERDE',
         'SET SERDEPROPERTIES', 'SET SKEWED LOCATION', 'SET TBLPROPERTIES', 'SKEWED BY', 'TOUCH', 'UNARCHIVE PARTITION']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['ADD COLUMNS', 'ADD PARTITION', 'ADD RANGE PARTITION', 'ALTER', 'ALTER COLUMN', 'CHANGE',
         'DROP COLUMN', 'DROP PARTITION', 'DROP RANGE PARTITION', 'PARTITION', 'RECOVER PARTITIONS', 'RENAME TO',
         'REPLACE COLUMNS', 'SET CACHED IN', 'SET COLUMN STATS', 'SET FILEFORMAT', 'SET LOCATION', 'SET OWNER',
         'SET ROW FORMAT', 'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'SET UNCACHED']);
     }
   }
 | AlterTableLeftSide PartitionSpec 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['ADD COLUMNS', 'CHANGE', 'COMPACT', 'CONCATENATE', 'DISABLE NO_DROP', 'DISABLE OFFLINE',
         'ENABLE NO_DROP', 'ENABLE OFFLINE', 'RENAME TO PARTITION', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION',
         'SET SERDE', 'SET SERDEPROPERTIES']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET ROW FORMAT',
       'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'SET UNCACHED']);
     }
   }
 | AlterTableLeftSide PartitionSpec AddOrReplace 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide PartitionSpec 'SET' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['CACHED IN', 'FILEFORMAT', 'LOCATION', 'ROW FORMAT', 'SERDEPROPERTIES','TBLPROPERTIES', 'UNCACHED']);
     }
   }
 | AlterTableLeftSide 'SET' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['FILEFORMAT', 'LOCATION', 'OWNER', 'SERDE', 'SERDEPROPERTIES', 'SKEWED LOCATION', 'TBLPROPERTIES']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['CACHED IN', 'COLUMN STATS', 'FILEFORMAT', 'LOCATION', 'OWNER ROLE', 'OWNER USER', 'ROW FORMAT', 'SERDEPROPERTIES', 'TBLPROPERTIES', 'UNCACHED']);
     }
   }
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations_EDIT
 | AlterTableLeftSide AnyRename 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | AlterTableLeftSide AnyRename 'TO' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
   }
 | AlterTableLeftSide '<impala>RECOVER' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 ;

HiveSpecificOperations
 : ClusteredBy
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories
 | HiveExchange
 | '<hive>RECOVER' '<hive>PARTITIONS'
 | '<hive>TOUCH' OptionalPartitionSpec
 | HiveArchiveOrUnArchive PartitionSpec
 | 'NOT' '<hive>SKEWED'
 | 'NOT' '<hive>STORED_AS_DIRECTORIES'
 | 'SET' '<hive>SKEWED_LOCATION' ParenthesizedSkewedLocationList
 | 'SET' '<hive>OWNER' PrincipalSpecification
 | PartitionSpec '<hive>RENAME' 'TO' PartitionSpec
 | PartitionSpec AnyChange '<hive>COLUMN' ParenthesizedColumnSpecificationList OptionalHiveCascadeOrRestrict
 ;

HiveSpecificOperations_EDIT
 : HiveArchiveOrUnArchive 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | HiveArchiveOrUnArchive PartitionSpec_EDIT
 | ClusteredBy_EDIT
 | HiveExchange_EDIT
 | 'NOT' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['SKEWED', 'STORED AS DIRECTORIES']);
     }
   }
 | 'NOT' '<hive>STORED' 'CURSOR'
   {
     parser.suggestKeywords(['AS DIRECTORIES']);
   }
 | 'NOT' '<hive>STORED' '<hive>AS' 'CURSOR'
   {
     parser.suggestKeywords(['DIRECTORIES']);
   }
 | PartitionSpec '<hive>RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['TO PARTITION']);
   }
 | PartitionSpec '<hive>RENAME' 'TO' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | '<hive>RECOVER' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 | 'SET' '<hive>SKEWED' 'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | 'SET' '<hive>SKEWED_LOCATION' ParenthesizedSkewedLocationList_EDIT
 | '<hive>SKEWED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'SET' '<hive>OWNER' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'SET' '<hive>OWNER' PrincipalSpecification_EDIT
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList_EDIT
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList_EDIT 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['STORED AS DIRECTORIES']);
     }
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories_EDIT
 | '<hive>TOUCH' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | '<hive>TOUCH' OptionalPartitionSpec_EDIT
 ;

ImpalaSpecificOperations
 : 'ALTER' OptionalImpalaColumn ColumnIdentifier 'SET' KuduStorageAttribute SetValue
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 | 'ALTER' OptionalImpalaColumn ColumnIdentifier 'DROP' '<impala>DEFAULT'
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 | 'SET' '<impala>COLUMN' '<impala>STATS' ColumnIdentifier ParenthesizedStatsList
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | 'SET' '<impala>OWNER' ImpalaRoleOrUser RegularOrBacktickedIdentifier
 ;

ImpalaSpecificOperations_EDIT
 : 'ALTER' OptionalImpalaColumn 'CURSOR'
   {
     if (parser.isImpala()) {
       if (!$2) {
         parser.suggestKeywords(['COLUMN']);
       }
       parser.suggestColumns();
     }
   }
 | 'ALTER' OptionalImpalaColumn ColumnIdentifier 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['DROP DEFAULT', 'SET BLOCK_SIZE', 'SET COMMENT', 'SET COMPRESSION', 'SET DEFAULT',
         'SET ENCODING']);
        parser.addColumnLocation($3.location, [ $3.identifier ]);
     }
   }
 | 'ALTER' OptionalImpalaColumn ColumnIdentifier 'DROP' 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['DEFAULT']);
       parser.addColumnLocation($3.location, [ $3.identifier ]);
     }
   }
 | 'ALTER' OptionalImpalaColumn ColumnIdentifier 'SET' 'CURSOR'
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['BLOCK_SIZE', 'COMMENT', 'COMPRESSION', 'DEFAULT', 'ENCODING']);
       parser.addColumnLocation($3.location, [ $3.identifier ]);
     }
   }
 | 'ALTER' OptionalImpalaColumn ColumnIdentifier 'SET' KuduStorageAttribute 'CURSOR'
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 | 'SET' '<impala>COLUMN' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | 'SET' '<impala>COLUMN' '<impala>STATS' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'SET' '<impala>COLUMN' '<impala>STATS' ColumnIdentifier 'CURSOR'
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | 'SET' '<impala>COLUMN' '<impala>STATS' ColumnIdentifier ParenthesizedStatsList_EDIT
   {
     parser.addColumnLocation($4.location, [ $4.identifier ]);
   }
 | 'SET' '<impala>OWNER' 'CURSOR'
   {
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 | 'SET' '<impala>OWNER' ImpalaRoleOrUser 'CURSOR'
 ;

KuduStorageAttribute
 : '<impala>BLOCK_SIZE'
 | '<impala>COMMENT'
 | '<impala>COMPRESSION'
 | '<impala>DEFAULT'
 | '<impala>ENCODING'
 ;

OptionalImpalaColumn
 :
 | '<impala>COLUMN'
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
 : 'SET' AnyFileFormat FileFormat
 | 'SET' HdfsLocation
 | 'SET' HiveOrImpalaTblproperties ParenthesizedPropertyAssignmentList
 | 'SET' '<hive>SERDE' QuotedValue OptionalWithSerdeproperties
 | 'SET' HiveOrImpalaSerdeproperties ParenthesizedPropertyAssignmentList
 | 'SET' CachedIn OptionalWithReplication
 | 'SET' 'ROW' '<impala>FORMAT' ImpalaRowFormat
 | 'SET' '<impala>UNCACHED'
 | AddReplaceColumns
 | '<hive>CONCATENATE'
 | '<hive>COMPACT' QuotedValue OptionalAndWait OptionalWithOverwriteTblProperties
 | HiveEnableOrDisable HiveNoDropOrOffline
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 ;

OptionalPartitionOperations_EDIT
 : AddReplaceColumns_EDIT
 | AnyChange OptionalHiveColumn 'CURSOR'
   {
     if (parser.isHive() && !$2) {
       parser.suggestKeywords(['COLUMN']);
     }
     parser.suggestColumns();
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification_EDIT OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict 'CURSOR'
   {
     if (parser.isHive() && !$5 && !$6) {
       if ($4.suggestKeywords) {
         var keywords = parser.createWeightedKeywords($4.suggestKeywords, 3);
         keywords = keywords.concat([{ value: 'AFTER', weight: 2 }, { value: 'FIRST', weight: 2 }, { value: 'CASCADE', weight: 1 }, { value: 'RESTRICT', weight: 1 }]);
         parser.suggestKeywords(keywords);
       } else {
         parser.suggestKeywords([{ value: 'AFTER', weight: 2 }, { value: 'FIRST', weight: 2 }, { value: 'CASCADE', weight: 1 }, { value: 'RESTRICT', weight: 1 }]);
       }
     } else if (parser.isHive() && $5 && !$6) {
       parser.suggestKeywords(['CASCADE', 'RESTRICT']);
     }
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter_EDIT OptionalHiveCascadeOrRestrict
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 | '<hive>COMPACT' QuotedValue OptionalAndWait OptionalWithOverwriteTblProperties 'CURSOR'
   {
     if (!$3 && !$4) {
       parser.suggestKeywords(['AND WAIT', 'WITH OVERWRITE TBLPROPERTIES']);
     } else if (!$4) {
       parser.suggestKeywords(['WITH OVERWRITE TBLPROPERTIES']);
     }
   }
 | '<hive>COMPACT' QuotedValue AndWait_EDIT OptionalWithOverwriteTblProperties
 | '<hive>COMPACT' QuotedValue OptionalAndWait WithOverwriteTblProperties_EDIT
 | HiveEnableOrDisable 'CURSOR'
   {
     parser.suggestKeywords(['NO_DROP', 'OFFLINE']);
   }
 | HiveEnableOrDisable HiveNoDropOrOffline_EDIT
 | 'SET' AnyFileFormat 'CURSOR'
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
     if (parser.isImpala()) {
       parser.suggestKeywords(['FORMAT']);
     }
   }
 | 'SET' 'ROW' '<impala>FORMAT' 'CURSOR'
   {
     parser.suggestKeywords(['DELIMITED']);
   }
 | 'SET' 'ROW' '<impala>FORMAT' ImpalaRowFormat 'CURSOR'
   {
     if ($4.suggestKeywords) {
       parser.suggestKeywords($4.suggestKeywords);
     }
   }
 | 'SET' 'ROW' '<impala>FORMAT' ImpalaRowFormat_EDIT
 | 'SET' '<hive>SERDE' QuotedValue OptionalWithSerdeproperties 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['WITH SERDEPROPERTIES']);
     }
   }
 | 'SET' '<hive>SERDE' QuotedValue WithSerdeproperties_EDIT
 ;

OptionalAndWait
 :
 | 'AND' '<hive>WAIT'
 ;

AndWait_EDIT
 : 'AND' 'CURSOR'
   {
     parser.suggestKeywords(['WAIT']);
   }
 ;

OptionalWithOverwriteTblProperties
 :
 | '<hive>WITH' '<hive>OVERWRITE' '<hive>TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

WithOverwriteTblProperties_EDIT
 : AnyWith 'CURSOR'
   {
     parser.suggestKeywords(['OVERWRITE TBLPROPERTIES']);
   }
 | '<hive>WITH' '<hive>OVERWRITE' 'CURSOR'
   {
     parser.suggestKeywords(['TBLPROPERTIES']);
   }
 ;

AddReplaceColumns
 : AddOrReplace AnyColumns ParenthesizedColumnSpecificationList OptionalHiveCascadeOrRestrict
 ;

AddReplaceColumns_EDIT
 : AddOrReplace AnyColumns ParenthesizedColumnSpecificationList_EDIT OptionalHiveCascadeOrRestrict
 | AddOrReplace AnyColumns ParenthesizedColumnSpecificationList OptionalHiveCascadeOrRestrict 'CURSOR'
   {
     if (parser.isHive() && !$4) {
       parser.suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 ;

AnyColumns
 : '<hive>COLUMNS'
 | '<impala>COLUMNS'
 ;

HiveExchange
 : '<hive>EXCHANGE' ExchangePartitionSpec '<hive>WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName
 ;

HiveExchange_EDIT
 : '<hive>EXCHANGE' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec 'CURSOR'
   {
     parser.suggestKeywords(['WITH TABLE']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec '<hive>WITH' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec '<hive>WITH' '<hive>TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec '<hive>WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName_EDIT
 | '<hive>EXCHANGE' ExchangePartitionSpec_EDIT
 | '<hive>EXCHANGE' ExchangePartitionSpec_EDIT '<hive>WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName
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
 : 'DROP' OptionalIfExists OneOrMorePartitionSpecs OptionalHivePurge
 | 'DROP' '<hive>CONSTRAINT' RegularOrBacktickedIdentifier
 | 'DROP' OptionalIfExists '<impala>RANGE'
 | 'DROP' OptionalIfExists '<impala>RANGE' 'PARTITION' RangePartitionSpec
 | 'DROP' OptionalIfExists '<impala>RANGE' '<impala>PARTITION_VALUE' '=' UnsignedValueSpecification
 | 'DROP' '<impala>COLUMN' ColumnIdentifier
   {
     parser.addColumnLocation($3.location, [ $3.identifier ]);
   }
 ;

DropOperations_EDIT
 : 'DROP' OptionalIfExists 'CURSOR'
   {
     if (parser.isHive() && !$2) {
       parser.suggestKeywords([{ value: 'CONSTRAINT', weight: 1}, { value: 'PARTITION', weight: 1}, { value: 'IF EXISTS', weight: 2 }]);
     } else if (parser.isHive()) {
        parser.suggestKeywords(['PARTITION']);
     } else if (parser.isImpala() && !$2) {
       parser.suggestKeywords([{ value: 'COLUMN', weight: 1 }, { value: 'PARTITION', weight: 1 }, { value: 'RANGE PARTITION', weight: 1 }, { value: 'IF EXISTS', weight: 2 }]);
       parser.suggestColumns();
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['PARTITION', 'RANGE PARTITION']);
     }
   }
 | 'DROP' OptionalIfExists OneOrMorePartitionSpecs_EDIT OptionalHivePurge
 | 'DROP' OptionalIfExists OneOrMorePartitionSpecs OptionalHivePurge 'CURSOR'
   {
     if (parser.isHive() && !$4) {
       parser.suggestKeywords(['PURGE']);
     }
   }
 | 'DROP' '<hive>CONSTRAINT' 'CURSOR'
 | 'DROP' OptionalIfExists_EDIT
 | 'DROP' OptionalIfExists '<impala>RANGE' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | 'DROP' OptionalIfExists '<impala>RANGE' 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['VALUE']);
   }
 | 'DROP' OptionalIfExists '<impala>RANGE' '<impala>PARTITION_VALUE' 'CURSOR'
   {
     parser.suggestKeywords(['=']);
   }
 | 'DROP' OptionalIfExists '<impala>RANGE' 'PARTITION' RangePartitionSpec_EDIT
 | 'DROP' ColumnIdentifier_EDIT
 | 'DROP' '<impala>COLUMN' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'DROP' '<impala>COLUMN' ColumnIdentifier_EDIT
 ;

AlterTableLeftSide
 : 'ALTER' AnyTable SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

AlterTableLeftSide_EDIT
 : 'ALTER' AnyTable SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'ALTER' AnyTable 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 ;

AnyChange
 : '<hive>CHANGE'
 | '<impala>CHANGE'
 ;

AnyFileFormat
 : '<hive>FILEFORMAT'
 | '<impala>FILEFORMAT'
 ;

AnyAdd
 : '<hive>ADD'
 | '<impala>ADD'
 ;

AnyReplace
 : '<hive>REPLACE'
 | '<impala>REPLACE'
 ;

AddOrReplace
 : AnyAdd
 | AnyReplace
 ;

OptionalHiveFirstOrAfter
 :
 | HiveAfterOrFirst ColumnIdentifier
 ;

HiveAfterOrFirst
 : '<hive>AFTER'
 | '<hive>FIRST'
 ;

OptionalHiveFirstOrAfter_EDIT
 : HiveAfterOrFirst 'CURSOR'
   {
     parser.suggestColumns();
   }
 | HiveAfterOrFirst ColumnIdentifier_EDIT
 ;

OptionalHiveColumn
 :
 | '<hive>COLUMN'
 ;

AnyRename
 : '<impala>RENAME'
 | '<hive>RENAME'
 ;

HiveEnableOrDisable
 : '<hive>ENABLE'
 | '<hive>DISABLE'
 ;

HiveNoDropOrOffline
 : '<hive>NO_DROP' OptionalCascade
 | '<hive>OFFLINE'
 ;

HiveNoDropOrOffline_EDIT
 : '<hive>NO_DROP' OptionalCascade 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['CASCADE']);
     }
   }
 ;

HiveOrImpalaSerdeproperties
 : '<hive>SERDEPROPERTIES'
 | '<impala>SERDEPROPERTIES'
 ;

HiveArchiveOrUnArchive
 : '<hive>ARCHIVE'
 | '<hive>UNARCHIVE'
 ;

OneOrMorePartitionSpecs
 : PartitionSpec
 | OneOrMorePartitionSpecs ',' PartitionSpec // Only Hive
 ;

OneOrMorePartitionSpecs_EDIT
 : PartitionSpec_EDIT
 | OneOrMorePartitionSpecs ',' AnyCursor
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | OneOrMorePartitionSpecs ',' AnyCursor ',' OneOrMorePartitionSpecs
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | AnyCursor ',' OneOrMorePartitionSpecs
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | OneOrMorePartitionSpecs ',' PartitionSpec_EDIT
 | PartitionSpec_EDIT ',' OneOrMorePartitionSpecs
 | OneOrMorePartitionSpecs ',' PartitionSpec_EDIT ',' OneOrMorePartitionSpecs
 ;

OptionalHivePurge
 :
 | '<hive>PURGE'
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

ParenthesizedSkewedLocationList
 : '(' SkewedLocationList ')'
 ;

ParenthesizedSkewedLocationList_EDIT
 : '(' SkewedLocationList_EDIT RightParenthesisOrError
 ;

SkewedLocationList
 : SkewedLocation
 | SkewedLocationList ',' SkewedLocation
 ;

SkewedLocationList_EDIT
 : SkewedLocation_EDIT
 | SkewedLocationList ',' SkewedLocation_EDIT
 | SkewedLocationList ',' SkewedLocation_EDIT ',' SkewedLocationList
 | SkewedLocation_EDIT ',' SkewedLocationList
 ;

SkewedLocation
 : ColumnReference '=' QuotedValue
 ;

SkewedLocation_EDIT
 : AnyCursor
   {
     parser.suggestColumns();
   }
 | ColumnReference_EDIT
 | AnyCursor '=' QuotedValue
   {
     parser.suggestColumns();
   }
 | ColumnReference_EDIT '=' QuotedValue
 | ColumnReferences '=' QuotedValue
 ;

OptionalStoredAsDirectories
 :
 | '<hive>STORED_AS_DIRECTORIES'
 ;

OptionalStoredAsDirectories_EDIT
 : '<hive>STORED' 'CURSOR'
   {
     parser.suggestKeywords(['AS DIRECTORIES']);
   }
 | '<hive>STORED' '<hive>AS' 'CURSOR'
   {
     parser.suggestKeywords(['DIRECTORIES']);
   }
 ;

AlterView
 : AlterViewLeftSide 'SET' '<hive>TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 | AlterViewLeftSide 'SET' '<impala>OWNER' ImpalaRoleOrUser RegularOrBacktickedIdentifier
 | AlterViewLeftSide AnyAs QuerySpecification
 | AlterViewLeftSide '<impala>RENAME' 'TO' RegularOrBacktickedIdentifier
 | AlterViewLeftSide '<impala>RENAME' 'TO' RegularOrBacktickedIdentifier '<impala>.' RegularOrBacktickedIdentifier
 ;

AlterView_EDIT
 : AlterViewLeftSide_EDIT
 | AlterViewLeftSide 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['AS', 'SET TBLPROPERTIES']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['AS', 'RENAME TO', 'SET OWNER']);
     } else {
       parser.suggestKeywords(['AS']);
     }
   }
 | AlterViewLeftSide 'SET' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['TBLPROPERTIES']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['OWNER ROLE', 'OWNER USER']);
     }
   }
 | AlterViewLeftSide 'SET' '<impala>OWNER' 'CURSOR'
   {
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 | AlterViewLeftSide 'SET' '<impala>OWNER' ImpalaRoleOrUser 'CURSOR'
 | AlterViewLeftSide AnyAs 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | AlterViewLeftSide AnyAs QuerySpecification_EDIT
 | AlterViewLeftSide '<impala>RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | AlterViewLeftSide '<impala>RENAME' 'TO' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
   }
 ;


AlterViewLeftSide
 : 'ALTER' AnyView SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

AlterViewLeftSide_EDIT
 : 'ALTER' AnyView SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'ALTER' AnyView 'CURSOR'
   {
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 ;

Msck
 : '<hive>MSCK' '<hive>REPAIR' '<hive>TABLE' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

Msck_EDIT
 : '<hive>MSCK' 'CURSOR'
   {
     parser.suggestKeywords(['REPAIR TABLE']);
   }
 | '<hive>MSCK' '<hive>REPAIR' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | '<hive>MSCK' '<hive>REPAIR' '<hive>TABLE' 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | '<hive>MSCK' '<hive>REPAIR' '<hive>TABLE' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 ;

ReloadFunction
 : '<hive>RELOAD' '<hive>FUNCTION'
 ;

ReloadFunction_EDIT
 : '<hive>RELOAD' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 ;

CommentOn
 : '<impala>COMMENT' 'ON' 'DATABASE' RegularOrBacktickedIdentifier 'IS' NullableComment
   {
     parser.addDatabaseLocation(@4, [ { name: $4 } ]);
   }
 ;

CommentOn_EDIT
 : '<impala>COMMENT' 'CURSOR'
   {
     parser.suggestKeywords(['ON DATABASE']);
   }
 | '<impala>COMMENT' 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE']);
   }
 | '<impala>COMMENT' 'ON' 'DATABASE' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | '<impala>COMMENT' 'ON' 'DATABASE' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.addDatabaseLocation(@4, [ { name: $4 } ]);
     parser.suggestKeywords(['IS']);
   }
 | '<impala>COMMENT' 'ON' 'DATABASE' RegularOrBacktickedIdentifier 'IS' 'CURSOR'
   {
     parser.addDatabaseLocation(@4, [ { name: $4 } ]);
     parser.suggestKeywords(['NULL']);
   }
 ;

NullableComment
 : QuotedValue
 | 'NULL'
 ;