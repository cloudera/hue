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
 : AlterTable
 ;

AlterStatement_EDIT
 : AlterTable_EDIT
 | 'ALTER' 'CURSOR'
   {
     suggestKeywords(['TABLE']);
   }
 ;

AlterTable
 : AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs
 | AlterTableLeftSide AnyRename 'TO' RegularOrBackTickedSchemaQualifiedName
 | AlterTableLeftSide HiveSpecificOperations
 | AlterTableLeftSide DropOperations
 | AlterTableLeftSide OptionalPartitionOperations
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations
 ;

AlterTable_EDIT
 : AlterTableLeftSide_EDIT
 | AlterTableLeftSide_EDIT AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs
 | AlterTableLeftSide_EDIT AnyRename 'TO' RegularOrBackTickedSchemaQualifiedName
 | AlterTableLeftSide_EDIT HiveSpecificOperations
 | AlterTableLeftSide_EDIT DropOperations
 | AlterTableLeftSide_EDIT OptionalPartitionOperations
 | AlterTableLeftSide_EDIT PartitionSpec OptionalPartitionOperations
 | AlterTableLeftSide AnyAdd OptionalIfNotExists 'CURSOR'
   {
     if (isHive()) {
       if (!$3) {
         suggestKeywords(['COLUMNS', 'IF NOT EXISTS', 'PARTITION']);
       } else {
         suggestKeywords(['PARTITION']);
       }
     } else if (isImpala()) {
       suggestKeywords(['COLUMNS', 'PARTITION']);
     }
   }
 | AlterTableLeftSide AnyReplace 'CURSOR'
   {
     suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists_EDIT
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation_EDIT OptionalPartitionSpecs
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs_EDIT
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs 'CURSOR'
   {
     if (isHive()) {
       if (!$5 && !$6) {
         suggestKeywords(['LOCATION', 'PARTITION']);
       } else if ($6 && $6.suggestKeywords) {
         suggestKeywords($6.suggestKeywords.concat(['PARTITION']));
       } else {
         suggestKeywords(['PARTITION']);
       }
     }
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec_EDIT OptionalHdfsLocation OptionalPartitionSpecs
 | AlterTableLeftSide HiveSpecificOperations_EDIT
 | AlterTableLeftSide OptionalPartitionOperations_EDIT
 | AlterTableLeftSide DropOperations_EDIT
 | AlterTableLeftSide 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['ADD COLUMNS', 'ADD IF NOT EXISTS', 'ADD PARTITION', 'ARCHIVE PARTITION', 'CHANGE',
         'CLUSTERED BY', 'CONCATENATE', 'COMPACT', 'DISABLE NO_DROP', 'DISABLE OFFLINE', 'DROP', 'ENABLE NO_DROP',
         'ENABLE OFFLINE', 'EXCHANGE PARTITION', 'NOT SKEWED', 'NOT STORED AS DIRECTORIES', 'PARTITION',
         'RECOVER PARTITIONS', 'RENAME TO', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDE',
         'SET SERDEPROPERTIES', 'SET SKEWED LOCATION', 'SET TBLPROPERTIES', 'SKEWED BY', 'TOUCH', 'UNARCHIVE PARTITION']);
     } else if (isImpala()) {
       suggestKeywords(['ADD COLUMNS', 'ADD PARTITION', 'CHANGE', 'DROP COLUMN', 'DROP PARTITION', 'PARTITION',
         'RENAME TO', 'REPLACE COLUMNS', 'SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDEPROPERTIES',
         'SET TBLPROPERTIES', 'SET UNCACHED']);
     }
   }
 | AlterTableLeftSide PartitionSpec 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['ADD COLUMNS', 'CHANGE', 'COMPACT', 'CONCATENATE', 'DISABLE NO_DROP', 'DISABLE OFFLINE',
         'ENABLE NO_DROP', 'ENABLE OFFLINE', 'RENAME TO PARTITION', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION',
         'SET SERDE', 'SET SERDEPROPERTIES']);
     } else if (isImpala()) {
       suggestKeywords(['SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDEPROPERTIES', 'SET TBLPROPERTIES',
         'SET UNCACHED']);
     }
   }
 | AlterTableLeftSide PartitionSpec AddOrReplace 'CURSOR'
   {
     suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide PartitionSpec 'SET' 'CURSOR'
    {
      if (isHive()) {
        suggestKeywords(['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES']);
      } else if (isImpala()) {
        suggestKeywords(['CACHED IN', 'FILEFORMAT', 'LOCATION', 'SERDEPROPERTIES','TBLPROPERTIES', 'UNCACHED']);
      }
    }
 | AlterTableLeftSide 'SET' 'CURSOR'
    {
      if (isHive()) {
        suggestKeywords(['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES', 'SKEWED LOCATION', 'TBLPROPERTIES']);
      } else if (isImpala()) {
        suggestKeywords(['CACHED IN', 'FILEFORMAT', 'LOCATION', 'SERDEPROPERTIES', 'TBLPROPERTIES', 'UNCACHED']);
      }
    }
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations_EDIT
 | AlterTableLeftSide AnyRename 'CURSOR'
   {
     suggestKeywords(['TO']);
   }
 ;

HiveSpecificOperations
 : HiveClusteredBy
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories
 | HiveExchange
 | '<hive>RECOVER' '<hive>PARTITIONS'
 | '<hive>TOUCH' OptionalPartitionSpec
 | HiveArchiveOrUnArchive PartitionSpec
 | 'NOT' '<hive>SKEWED'
 | 'NOT' '<hive>STORED_AS_DIRECTORIES'
 | 'SET' '<hive>SKEWED_LOCATION' ParenthesizedSkewedLocationList
 | PartitionSpec '<hive>RENAME' 'TO' PartitionSpec
 | PartitionSpec AnyChange '<hive>COLUMN' ParenthesizedColumnSpecificationList OptionalHiveCascadeOrRestrict
 ;

HiveSpecificOperations_EDIT
 : HiveArchiveOrUnArchive 'CURSOR'
   {
     suggestKeywords(['PARTITION']);
   }
 | HiveArchiveOrUnArchive PartitionSpec_EDIT
 | HiveClusteredBy_EDIT
 | HiveExchange_EDIT
 | 'NOT' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['SKEWED', 'STORED AS DIRECTORIES']);
     }
   }
 | 'NOT' '<hive>STORED' 'CURSOR'
   {
     suggestKeywords(['AS DIRECTORIES']);
   }
 | 'NOT' '<hive>STORED' '<hive>AS' 'CURSOR'
   {
     suggestKeywords(['DIRECTORIES']);
   }
 | PartitionSpec '<hive>RENAME' 'CURSOR'
   {
     suggestKeywords(['TO PARTITION']);
   }
 | PartitionSpec '<hive>RENAME' 'TO' 'CURSOR'
   {
     suggestKeywords(['PARTITION']);
   }
 | '<hive>RECOVER' 'CURSOR'
   {
     suggestKeywords(['PARTITIONS']);
   }
 | 'SET' '<hive>SKEWED' 'CURSOR'
   {
     suggestKeywords(['LOCATION']);
   }
 | 'SET' '<hive>SKEWED_LOCATION' ParenthesizedSkewedLocationList_EDIT
 | '<hive>SKEWED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList_EDIT
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList_EDIT 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories 'CURSOR'
   {
     if (!$6) {
       suggestKeywords(['STORED AS DIRECTORIES']);
     }
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'ON' ParenthesizedSkewedValueList OptionalStoredAsDirectories_EDIT
 | '<hive>TOUCH' 'CURSOR'
   {
     suggestKeywords(['PARTITION']);
   }
 | '<hive>TOUCH' OptionalPartitionSpec_EDIT
 ;

OptionalPartitionOperations
 : 'SET' AnyFileFormat FileFormat
 | 'SET' HdfsLocation
 | 'SET' HiveOrImpalaTblproperties ParenthesizedPropertyAssignmentList
 | 'SET' '<hive>SERDE' QuotedValue OptionalHiveWithSerdeproperties
 | 'SET' HiveOrImpalaSerdeproperties ParenthesizedPropertyAssignmentList
 | 'SET' ImpalaCachedIn
 | 'SET' '<impala>UNCACHED'
 | AddReplaceColumns
 | '<hive>CONCATENATE'
 | '<hive>COMPACT' QuotedValue
 | HiveEnableOrDisable HiveNoDropOrOffline
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict
 ;

OptionalPartitionOperations_EDIT
 : AddReplaceColumns_EDIT
 | AnyChange OptionalHiveColumn 'CURSOR'
   {
     if (isHive() && !$2) {
       suggestKeywords(['COLUMN']);
     }
     suggestColumns();
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification_EDIT OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict 'CURSOR'
   {
     if (isHive() && !$5 && !$6) {
       if ($4.suggestKeywords) {
         suggestKeywords($4.suggestKeywords.concat(['AFTER', 'CASCADE', 'FIRST', 'RESTRICT']));
       } else {
         suggestKeywords(['AFTER', 'CASCADE', 'FIRST', 'RESTRICT']);
       }
     } else if (isHive() && $5 && !$6) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter_EDIT OptionalHiveCascadeOrRestrict
 | HiveEnableOrDisable 'CURSOR'
   {
     suggestKeywords(['NO_DROP', 'OFFLINE']);
   }
 | 'SET' AnyFileFormat 'CURSOR'
   {
     suggestFileFormats();
   }
 | 'SET' HdfsLocation_EDIT
 | 'SET' ImpalaCachedIn_EDIT
 | 'SET' '<hive>SERDE' QuotedValue OptionalHiveWithSerdeproperties 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['WITH SERDEPROPERTIES']);
     }
   }
 | 'SET' '<hive>SERDE' QuotedValue OptionalHiveWithSerdeproperties_EDIT
 ;

AddReplaceColumns
 : AddOrReplace AnyColumns ParenthesizedColumnSpecificationList OptionalHiveCascadeOrRestrict
 ;

AddReplaceColumns_EDIT
 : AddOrReplace AnyColumns ParenthesizedColumnSpecificationList_EDIT OptionalHiveCascadeOrRestrict
 | AddOrReplace AnyColumns ParenthesizedColumnSpecificationList OptionalHiveCascadeOrRestrict 'CURSOR'
   {
     if (isHive() && !$4) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 ;

AnyColumns
 : '<hive>COLUMNS'
 | '<impala>COLUMNS'
 ;

HiveExchange
 : '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName
 ;

HiveExchange_EDIT
 : '<hive>EXCHANGE' 'CURSOR'
   {
     suggestKeywords(['PARTITION']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec 'CURSOR'
   {
     suggestKeywords(['WITH TABLE']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' 'CURSOR'
   {
     suggestKeywords(['TABLE']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' '<hive>TABLE' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName_EDIT
 | '<hive>EXCHANGE' ExchangePartitionSpec_EDIT
 | '<hive>EXCHANGE' ExchangePartitionSpec_EDIT 'WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName
 ;

ExchangePartitionSpec
 : 'PARTITION' '(' OneOrMorePartitionSpecLists ')'
 ;

ExchangePartitionSpec_EDIT
 : 'PARTITION' '(' OneOrMorePartitionSpecLists_EDIT RightParenthesisOrError
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
 : 'DROP' OneOrMorePartitionSpecs OptionalHivePurge
 | 'DROP' 'IF' 'EXISTS' OneOrMorePartitionSpecs OptionalHivePurge
 | 'DROP' ColumnIdentifier
 | 'DROP' '<impala>COLUMN' ColumnIdentifier
 ;

DropOperations
 : 'DROP' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['PARTITION', 'IF EXISTS']);
     } else if (isImpala()) {
       suggestKeywords(['COLUMN', 'PARTITION']);
       suggestColumns();
     }
   }
 | 'DROP' OneOrMorePartitionSpecs_EDIT OptionalHivePurge
 | 'DROP' OneOrMorePartitionSpecs OptionalHivePurge 'CURSOR'
   {
     if (isHive() && !$3) {
       suggestKeywords(['PURGE']);
     }
   }
 | 'DROP' 'IF' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['EXISTS']);
     }
   }
 | 'DROP' 'IF' 'EXISTS' 'CURSOR'
    {
      if (isHive()) {
        suggestKeywords(['PARTITION']);
      }
    }
 | 'DROP' 'IF' 'EXISTS' OneOrMorePartitionSpecs_EDIT OptionalHivePurge
 | 'DROP' 'IF' 'EXISTS' OneOrMorePartitionSpecs OptionalHivePurge 'CURSOR'
   {
     if (isHive() && !$3) {
       suggestKeywords(['PURGE']);
     }
   }
 | 'DROP' ColumnIdentifier_EDIT
 | 'DROP' '<impala>COLUMN' 'CURSOR'
   {
     suggestColumns();
   }
 | 'DROP' '<impala>COLUMN' ColumnIdentifier_EDIT
 ;

AlterTableLeftSide
 : 'ALTER' AnyTable SchemaQualifiedTableIdentifier
   {
     addTablePrimary($3);
   }
 ;

AlterTableLeftSide_EDIT
 : 'ALTER' AnyTable SchemaQualifiedTableIdentifier_EDIT
 | 'ALTER' AnyTable 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
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
     suggestColumns();
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
 : '<hive>NO_DROP'
 | '<hive>OFFLINE'
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
     if (isHive()) {
       suggestKeywords(['PARTITION']);
     }
   }
 | OneOrMorePartitionSpecs ',' AnyCursor ',' OneOrMorePartitionSpecs
   {
     if (isHive()) {
       suggestKeywords(['PARTITION']);
     }
   }
 | AnyCursor ',' OneOrMorePartitionSpecs
   {
     if (isHive()) {
       suggestKeywords(['PARTITION']);
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
 : PartitionSpec OptionalHdfsLocation_EDIT
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
     suggestColumns();
   }
 | ColumnReference_EDIT
 | AnyCursor '=' QuotedValue
   {
     suggestColumns();
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
     suggestKeywords(['AS DIRECTORIES']);
   }
 | '<hive>STORED' '<hive>AS' 'CURSOR'
   {
     suggestKeywords(['DIRECTORIES']);
   }
 ;


OptionalCascadeOrRestrict
 :
 | '<hive>CASCADE'
 | '<hive>RESTRICT'
 ;
