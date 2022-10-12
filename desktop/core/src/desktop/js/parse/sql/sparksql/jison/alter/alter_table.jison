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
 : AlterTable
 ;

DataDefinition_EDIT
 : AlterTable_EDIT
 ;

AlterTable
 : 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier AlterTableOperations
   {
     parser.addTablePrimary($3);
   }
 ;

AlterTable_EDIT
 : 'ALTER' 'TABLE' 'CURSOR' OptionalAlterTableOperations
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalAlterTableOperations
 | 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier 'CURSOR' OptionalAlterTableOperations
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords([ 'ADD', 'ADD COLUMNS', 'ADD IF NOT EXISTS', 'ALTER', 'ALTER COLUMN', 'CHANGE',
         'CHANGE COLUMN', 'DROP', 'DROP COLUMN', 'DROP COLUMNS', 'DROP IF EXISTS', 'PARTITION', 'RECOVER PARTITIONS',
         'RENAME COLUMN', 'RENAME TO', 'REPLACE COLUMNS', 'SET', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDE',
         'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'UNSET TBLPROPERTIES']);
     }
   }
 | 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier AlterTableOperations_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

OptionalAlterTableOperations
 :
 | AlterTableOperations
 ;

AlterTableOperations
 : AlterAddOperations
 | AlterOrChange OptionalColumn ColumnIdentifier ColumnDataType OptionalComment
 | AlterDropOperations
 | PartitionSpec 'RENAME' 'TO' PartitionSpec
 | PartitionSpec 'REPLACE' 'COLUMNS' ParenthesizedColumnSpecificationList
 | 'RECOVER' 'PARTITIONS'
 | 'RENAME' 'COLUMN' ColumnIdentifier 'TO' ColumnIdentifier
 | 'RENAME' 'TO' RegularOrBacktickedIdentifier
 | 'REPLACE' 'COLUMNS' ParenthesizedColumnSpecificationList
 | AlterSetOperations
 | PartitionSpec AlterSetOperations
 | AlterSetTblPropertiesOperations
 ;

AlterTableOperations_EDIT
 : AlterAddOperations_EDIT
 | AlterOrChange OptionalColumn 'CURSOR'
   {
     if (!$2) {
        parser.suggestKeywords(['COLUMN']);
     }
     parser.suggestColumns();
   }
 | AlterOrChange OptionalColumn ColumnIdentifier 'CURSOR' OptionalComment
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 | AlterOrChange OptionalColumn ColumnIdentifier ColumnDataType 'CURSOR' OptionalComment
   {
     if (!$6) {
       parser.suggestKeywords(['COMMENT']);
     }
   }
 | AlterOrChange OptionalColumn ColumnIdentifier ColumnDataType_EDIT OptionalComment
 | AlterOrChange OptionalColumn 'CURSOR' ColumnDataType OptionalComment
   {
     if (!$2) {
        parser.suggestKeywords(['COLUMN']);
     }
     parser.suggestColumns();
   }
 | AlterDropOperations_EDIT
 | PartitionSpec 'CURSOR'
   {
     parser.suggestKeywords([
       'REPLACE COLUMNS', 'RENAME TO', 'SET', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDE', 'SET SERDEPROPERTIES']);
   }
 | PartitionSpec 'RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | PartitionSpec 'RENAME' 'TO' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITION']);
   }
 | PartitionSpec 'REPLACE' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | PartitionSpec 'REPLACE' 'COLUMNS' ParenthesizedColumnSpecificationList_EDIT
 | 'RECOVER' 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 | 'RENAME' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMN', 'TO']);
   }
 | 'RENAME' 'COLUMN' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'RENAME' 'COLUMN' ColumnIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['TO']);
   }
 | 'REPLACE' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | 'REPLACE' 'COLUMNS' ParenthesizedColumnSpecificationList_EDIT
 | AlterSetOperations_EDIT
 | PartitionSpec AlterSetOperations_EDIT
 | AlterSetTblPropertiesOperations_EDIT
 ;

AlterAddOperations
 : 'ADD' 'COLUMNS' ParenthesizedColumnSpecificationList
 | 'ADD' OptionalIfNotExists ParenthesizedPartitionList
 ;

AlterAddOperations_EDIT
 : 'ADD' OptionalIfNotExists 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['COLUMNS', 'IF NOT EXISTS']);
     }
   }
 | 'ADD' IfNotExists_EDIT
 | 'ADD' OptionalIfNotExists 'CURSOR' ParenthesizedPartitionList
   {
     if (!$2) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'ADD' IfNotExists_EDIT ParenthesizedPartitionList
 | 'ADD' 'COLUMNS' ParenthesizedColumnSpecificationList_EDIT
 ;

AlterDropOperations
 : 'DROP' OptionalIfExists PartitionSpec OptionalPurge
 | 'DROP' 'COLUMN' ColumnIdentifier
 | 'DROP' 'COLUMNS' ParenthesizedColumnIdentifierList
 ;

AlterDropOperations_EDIT
 : 'DROP' OptionalIfExists 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['COLUMN', 'COLUMNS', 'IF EXISTS', 'PARTITION'])
     } else {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'DROP' IfExists_EDIT
 | 'DROP' OptionalIfExists 'CURSOR' PartitionSpec OptionalPurge
   {
     if (!$2) {
       parser.suggestKeywords(['IF EXISTS'])
     }
   }
 | 'DROP' IfExists_EDIT PartitionSpec OptionalPurge
 | 'DROP' OptionalIfExists PartitionSpec OptionalPurge 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['PURGE'])
     }
   }
 | 'DROP' 'COLUMN' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'DROP' 'COLUMNS' ParenthesizedColumnIdentifierList_EDIT
 ;

AlterSetOperations
 : 'SET' 'FILEFORMAT' FileFormat
 | 'SET' 'LOCATION' QuotedValue
 | 'SET' 'SERDE' QuotedValue
 | 'SET' 'SERDE' QuotedValue 'WITH' 'SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 | 'SET' 'SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

AlterSetOperations_EDIT
 : 'SET' 'CURSOR'
   {
     parser.suggestKeywords(['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES', 'TBLPROPERTIES']);
   }
 | 'SET' 'FILEFORMAT' 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 | 'SET' 'SERDE' QuotedValue 'CURSOR'
   {
     parser.suggestKeywords(['WITH SERDEPROPERTIES']);
   }
 | 'SET' 'SERDE' QuotedValue 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['SERDEPROPERTIES']);
   }
 ;

AlterSetTblPropertiesOperations
 : 'SET' 'TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 | 'UNSET' 'TBLPROPERTIES' OptionalIfExists ParenthesizedPropertyList
 ;

AlterSetTblPropertiesOperations_EDIT
 : 'UNSET' 'CURSOR'
   {
     parser.suggestKeywords(['TBLPROPERTIES']);
   }
 | 'UNSET' 'TBLPROPERTIES' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'UNSET' 'TBLPROPERTIES' IfExists_EDIT
 | 'UNSET' 'TBLPROPERTIES' OptionalIfExists 'CURSOR' ParenthesizedPropertyList
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'UNSET' 'TBLPROPERTIES' IfExists_EDIT ParenthesizedPropertyList
 ;

OptionalColumn
 :
 | 'COLUMN'
 ;

OptionalPurge
 :
 | 'PURGE'
 ;

AlterOrChange
 : 'ALTER'
 | 'CHANGE'
 ;