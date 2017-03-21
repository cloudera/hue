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
 : AlterIndex
 | AlterTable
 | AlterView
 | Msck
 | ReloadFunction
 ;

AlterStatement_EDIT
 : AlterIndex_EDIT
 | AlterTable_EDIT
 | AlterView_EDIT
 | Msck_EDIT
 | ReloadFunction_EDIT
 | 'ALTER' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['INDEX', 'TABLE', 'VIEW']);
     } else {
       parser.suggestKeywords(['TABLE', 'VIEW']);
     }
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
     if (parser.isHive()) {
       if (!$3) {
         parser.suggestKeywords([{ value: 'IF NOT EXISTS', weight: 3 }, { value: 'COLUMNS', weight: 2 }, { value: 'PARTITION', weight: 1 }]);
       } else {
         parser.suggestKeywords(['PARTITION']);
       }
     } else if (parser.isImpala()) {
       parser.suggestKeywords([{ value: 'COLUMNS', weight: 2 }, { value: 'PARTITION', weight: 1 }]);
     }
   }
 | AlterTableLeftSide AnyReplace 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists_EDIT
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec HdfsLocation_EDIT OptionalPartitionSpecs
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs_EDIT
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec OptionalHdfsLocation OptionalPartitionSpecs 'CURSOR'
   {
     if (parser.isHive()) {
       if (!$5 && !$6) {
         parser.suggestKeywords(['LOCATION', 'PARTITION']);
       } else if ($6 && $6.suggestKeywords) {
         var keywords = parser.createWeightedKeywords($6.suggestKeywords, 2);
         keywords.push({ value: 'PARTITION', weight: 1 });
         parser.suggestKeywords(keywords);
       } else {
         parser.suggestKeywords(['PARTITION']);
       }
     }
   }
 | AlterTableLeftSide AnyAdd OptionalIfNotExists PartitionSpec_EDIT OptionalHdfsLocation OptionalPartitionSpecs
 | AlterTableLeftSide HiveSpecificOperations_EDIT
 | AlterTableLeftSide OptionalPartitionOperations_EDIT
 | AlterTableLeftSide DropOperations_EDIT
 | AlterTableLeftSide 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['ADD COLUMNS', 'ADD IF NOT EXISTS', 'ADD PARTITION', 'ARCHIVE PARTITION', 'CHANGE',
         'CLUSTERED BY', 'CONCATENATE', 'COMPACT', 'DISABLE NO_DROP', 'DISABLE OFFLINE', 'DROP', 'ENABLE NO_DROP',
         'ENABLE OFFLINE', 'EXCHANGE PARTITION', 'NOT SKEWED', 'NOT STORED AS DIRECTORIES', 'PARTITION',
         'RECOVER PARTITIONS', 'RENAME TO', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDE',
         'SET SERDEPROPERTIES', 'SET SKEWED LOCATION', 'SET TBLPROPERTIES', 'SKEWED BY', 'TOUCH', 'UNARCHIVE PARTITION']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['ADD COLUMNS', 'ADD PARTITION', 'CHANGE', 'DROP COLUMN', 'DROP PARTITION', 'PARTITION',
         'RENAME TO', 'REPLACE COLUMNS', 'SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDEPROPERTIES',
         'SET TBLPROPERTIES', 'SET UNCACHED']);
     }
   }
 | AlterTableLeftSide PartitionSpec 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['ADD COLUMNS', 'CHANGE', 'COMPACT', 'CONCATENATE', 'DISABLE NO_DROP', 'DISABLE OFFLINE',
         'ENABLE NO_DROP', 'ENABLE OFFLINE', 'RENAME TO PARTITION', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION',
         'SET SERDE', 'SET SERDEPROPERTIES']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDEPROPERTIES', 'SET TBLPROPERTIES',
         'SET UNCACHED']);
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
        parser.suggestKeywords(['CACHED IN', 'FILEFORMAT', 'LOCATION', 'SERDEPROPERTIES','TBLPROPERTIES', 'UNCACHED']);
      }
    }
 | AlterTableLeftSide 'SET' 'CURSOR'
    {
      if (parser.isHive()) {
        parser.suggestKeywords(['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES', 'SKEWED LOCATION', 'TBLPROPERTIES']);
      } else if (parser.isImpala()) {
        parser.suggestKeywords(['CACHED IN', 'FILEFORMAT', 'LOCATION', 'SERDEPROPERTIES', 'TBLPROPERTIES', 'UNCACHED']);
      }
    }
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations_EDIT
 | AlterTableLeftSide AnyRename 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
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

OptionalPartitionOperations
 : 'SET' AnyFileFormat FileFormat
 | 'SET' HdfsLocation
 | 'SET' HiveOrImpalaTblproperties ParenthesizedPropertyAssignmentList
 | 'SET' '<hive>SERDE' QuotedValue OptionalWithSerdeproperties
 | 'SET' HiveOrImpalaSerdeproperties ParenthesizedPropertyAssignmentList
 | 'SET' CachedIn
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
     if (parser.isHive() && !$2) {
       parser.suggestKeywords(['COLUMN']);
     }
     parser.suggestColumns();
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification_EDIT OptionalHiveFirstOrAfter OptionalHiveCascadeOrRestrict
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
   }
 | AnyChange OptionalHiveColumn ColumnIdentifier ColumnSpecification OptionalHiveFirstOrAfter_EDIT OptionalHiveCascadeOrRestrict
 | HiveEnableOrDisable 'CURSOR'
   {
     parser.suggestKeywords(['NO_DROP', 'OFFLINE']);
   }
 | 'SET' AnyFileFormat 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 | 'SET' HdfsLocation_EDIT
 | 'SET' CachedIn_EDIT
 | 'SET' '<hive>SERDE' QuotedValue OptionalWithSerdeproperties 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['WITH SERDEPROPERTIES']);
     }
   }
 | 'SET' '<hive>SERDE' QuotedValue WithSerdeproperties_EDIT
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
 : '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' '<hive>TABLE' RegularOrBackTickedSchemaQualifiedName
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
 | '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | '<hive>EXCHANGE' ExchangePartitionSpec 'WITH' '<hive>TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
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
     if (parser.isHive()) {
       parser.suggestKeywords([{ value: 'PARTITION', weight: 1}, { value: 'IF EXISTS', weight: 2 }]);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['COLUMN', 'PARTITION']);
       parser.suggestColumns();
     }
   }
 | 'DROP' OneOrMorePartitionSpecs_EDIT OptionalHivePurge
 | 'DROP' OneOrMorePartitionSpecs OptionalHivePurge 'CURSOR'
   {
     if (parser.isHive() && !$3) {
       parser.suggestKeywords(['PURGE']);
     }
   }
 | 'DROP' 'IF' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['EXISTS']);
     }
   }
 | 'DROP' 'IF' 'EXISTS' 'CURSOR'
    {
      if (parser.isHive()) {
        parser.suggestKeywords(['PARTITION']);
      }
    }
 | 'DROP' 'IF' 'EXISTS' OneOrMorePartitionSpecs_EDIT OptionalHivePurge
 | 'DROP' 'IF' 'EXISTS' OneOrMorePartitionSpecs OptionalHivePurge 'CURSOR'
   {
     if (parser.isHive() && !$3) {
       parser.suggestKeywords(['PURGE']);
     }
   }
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

OptionalCascadeOrRestrict
 :
 | '<hive>CASCADE'
 | '<hive>RESTRICT'
 ;

AlterView
 : AlterViewLeftSide 'SET' '<hive>TBLPROPERTIES' ParenthesizedPropertyAssignmentList
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
       parser.suggestKeywords(['AS', 'RENAME TO']);
     } else {
       parser.suggestKeywords(['AS']);
     }
   }
 | AlterViewLeftSide 'SET' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['TBLPROPERTIES']);
     }
   }
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