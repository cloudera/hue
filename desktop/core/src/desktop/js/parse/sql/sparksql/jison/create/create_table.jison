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
 : CreateTable
 ;

DataDefinition_EDIT
 : CreateTable_EDIT
 ;

CreateTable
 : 'CREATE' 'TABLE' OptionalIfNotExists CreateTableOptions
 | 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists CreateTableOptions
 ;

CreateTable_EDIT
 : 'CREATE' 'EXTERNAL' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'CREATE' 'TABLE' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'TABLE' IfNotExists_EDIT
 | 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'EXTERNAL' 'TABLE' IfNotExists_EDIT
 | 'CREATE' 'TABLE' OptionalIfNotExists 'CURSOR' CreateTableOptions
     {
       if (!$3) {
         parser.suggestKeywords(['IF NOT EXISTS']);
       }
     }
   | 'CREATE' 'TABLE' IfNotExists_EDIT CreateTableOptions
   | 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists 'CURSOR' CreateTableOptions
     {
       if (!$4) {
         parser.suggestKeywords(['IF NOT EXISTS']);
       }
     }
   | 'CREATE' 'EXTERNAL' 'TABLE' IfNotExists_EDIT CreateTableOptions
   | 'CREATE' 'TABLE' OptionalIfNotExists CreateTableOptions_EDIT
   | 'CREATE' 'EXTERNAL' 'TABLE' OptionalIfNotExists CreateTableOptions_EDIT
 ;

CreateTableOptions
 : SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier 'USING' DataSource OptionalRowFormat
   OptionalStoredAs OptionalTblProperties OptionalLocation
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList 'USING' DataSource OptionalOptions
   OptionalPartitionedBy OptionalClusteredBy OptionalLocation OptionalComment OptionalTblProperties
   OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalRowFormat OptionalStoredAs OptionalLocation OptionalTblProperties
   OptionalAsQuerySpecification
 ;

CreateTableOptions_EDIT
 : SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       delete parser.yy.result.suggestTables
     }
   }
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalPartitionedBy
   OptionalClusteredBy OptionalRowFormat OptionalStoredAs OptionalLocation OptionalTblProperties
   'CURSOR' OptionalAsQuerySpecification
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$9, $8, $7, $6, $5, $4, $3, undefined, undefined],
       [{ value: 'TBLPROPERTIES', weight: 2 },
        { value: 'LOCATION', weight: 3 },
        { value: 'STORED AS', weight: 4 },
        { value: 'ROW FORMAT', weight: 5 },
        { value: 'CLUSTERED BY', weight: 6 },
        { value: 'PARTITIONED BY', weight: 7 },
        { value: 'COMMENT', weight: 8 },
        { value: 'USING', weight: 9 },
        { value: 'LIKE', weight: 9 }]);

     if ($6 && $6.suggestKeywords && !$7 && !$8 && !$9) {
       keywords = keywords.concat($6.suggestKeywords);
     }
     if (!$11) {
       keywords.push({ value: 'AS', weight: 1 });
     }
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
   }
 | SchemaQualifiedTableIdentifier 'LIKE' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier_EDIT
 | SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['USING']);
   }
 | SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier 'USING' 'CURSOR'
   {
     parser.suggestKeywords(parser.getDataSourceKeywords());
   }
 | SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier 'USING' DataSource OptionalRowFormat OptionalStoredAs OptionalTblProperties OptionalLocation 'CURSOR'
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$9, $8, $7, $6],
       [{ value: 'LOCATION', weight: 1 },
        { value: 'TBLPROPERTIES', weight: 2 },
        { value: 'STORED AS', weight: 3 },
        { value: 'ROW FORMAT', weight: 4 }]);
     if ($6 && $6.suggestKeywords && !$7 && !$8 && !$9) {
       keywords = keywords.concat($6.suggestKeywords);
     }
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
   }
 | SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier 'USING' DataSource RowFormat_EDIT OptionalStoredAs OptionalTblProperties OptionalLocation
 | SchemaQualifiedTableIdentifier 'LIKE' SchemaQualifiedTableIdentifier 'USING' DataSource OptionalRowFormat StoredAs_EDIT OptionalTblProperties OptionalLocation
 | SchemaQualifiedTableIdentifier ParenthesizedColumnSpecificationList_EDIT OptionalComment OptionalPartitionedBy OptionalClusteredBy OptionalRowFormat OptionalStoredAs OptionalLocation OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList 'USING' 'CURSOR'
   {
     parser.suggestKeywords(parser.getDataSourceKeywords());
   }
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList 'USING' DataSource OptionalOptions OptionalPartitionedBy OptionalClusteredBy OptionalLocation OptionalComment OptionalTblProperties 'CURSOR' OptionalAsQuerySpecification
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$10, $9, $8, $7, $6, $5],
       [{ value: 'TBLPROPERTIES', weight: 2 },
        { value: 'COMMENT', weight: 3 },
        { value: 'LOCATION', weight: 4 },
        { value: 'CLUSTERED BY', weight: 5 },
        { value: 'PARTITIONED BY', weight: 6 },
        { value: 'OPTIONS', weight: 7 }]);
     if (!$12) {
       keywords.push({ value: 'AS', weight: 1 });
     }
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
   }
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList 'USING' DataSource OptionalOptions PartitionedBy_EDIT OptionalClusteredBy OptionalLocation OptionalComment OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList 'USING' DataSource OptionalOptions OptionalPartitionedBy ClusteredBy_EDIT OptionalLocation OptionalComment OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList 'USING' DataSource OptionalOptions OptionalPartitionedBy OptionalClusteredBy OptionalLocation OptionalComment OptionalTblProperties AsQuerySpecification_EDIT

 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment PartitionedBy_EDIT OptionalClusteredBy OptionalRowFormat OptionalStoredAs OptionalLocation OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalPartitionedBy ClusteredBy_EDIT OptionalRowFormat OptionalStoredAs OptionalLocation OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalPartitionedBy OptionalClusteredBy RowFormat_EDIT OptionalStoredAs OptionalLocation OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalPartitionedBy OptionalClusteredBy OptionalRowFormat StoredAs_EDIT OptionalLocation OptionalTblProperties OptionalAsQuerySpecification
 | SchemaQualifiedTableIdentifier OptionalParenthesizedColumnSpecificationList OptionalComment OptionalPartitionedBy OptionalClusteredBy OptionalRowFormat OptionalStoredAs OptionalLocation OptionalTblProperties AsQuerySpecification_EDIT
 ;

OptionalExternal
 :
 | 'EXTERNAL'
 ;

DataSource
 : 'CSV'
 | 'JDBC'
 | 'ORC'
 | 'PARQUET'
 | 'TXT'
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

OptionalTblProperties
 :
 | TblProperties
 ;

TblProperties
 : 'TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalOptions
 :
 | Options
 ;

Options
 : 'OPTIONS' ParenthesizedPropertyAssignmentList
 ;

OptionalPartitionedBy
 :
 | PartitionedBy
 ;

PartitionedBy
 : 'PARTITIONED' 'BY' ParenthesizedColumnSpecificationList
 | 'PARTITIONED' 'BY' '(' ColumnIdentifierList ')'
 ;

PartitionedBy_EDIT
 : 'PARTITIONED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

// Extension of RowFormatSpec in hive/create/row_format.jison
RowFormatSpec
 : 'SERDE' QuotedValue WithSerdeProperties
 ;