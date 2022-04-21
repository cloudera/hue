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
 : CreateMaterializedView
 ;

DataDefinition_EDIT
 : CreateMaterializedView_EDIT
 ;

CreateMaterializedView
 : 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier
    OptionalDisableRewrite OptionalComment OptionalPartitionedOn OptionalClusteredOrDistributedOn
    OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties
    AsSelectStatement
 ;

CreateMaterializedView_EDIT
 : 'CREATE' 'MATERIALIZED' 'CURSOR'
   {
     parser.suggestKeywords(['VIEW']);
   }
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   OptionalPartitionedOn OptionalClusteredOrDistributedOn OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties 'CURSOR'
   {
     var keywords = parser.getKeywordsForOptionalsLR([undefined, $12, $11, $10, $9, $8, $7, $6, $5], [
       { value: 'AS SELECT', weight: 1 },
       { value: 'TBLPROPERTIES', weight: 2 },
       { value: 'LOCATION', weight: 3 },
       [{ value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }],
       [{ value: 'CLUSTERED ON', weight: 5 }, { value: 'DISTRIBUTED ON', weight: 5 }],
       { value: 'PARTITIONED ON', weight: 6 },
       { value: 'COMMENT', weight: 7 },
       { value: 'DISABLE REWRITE', weight: 8 }
     ]);

     if (!$13 && !$12 && $11 && $11.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($11.suggestKeywords, 4));
     }
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
   }
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier DisableRewrite_EDIT OptionalComment
   OptionalPartitionedOn OptionalClusteredOrDistributedOn OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   PartitionedOn_EDIT OptionalClusteredOrDistributedOn OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   OptionalPartitionedOn ClusteredOrDistributedOn_EDIT OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   OptionalPartitionedOn OptionalClusteredOrDistributedOn RowFormat_EDIT OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   OptionalPartitionedOn OptionalClusteredOrDistributedOn OptionalRowFormat StoredAsOrBy_EDIT OptionalHdfsLocation
   OptionalTblproperties
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   OptionalPartitionedOn OptionalClusteredOrDistributedOn OptionalRowFormat OptionalStoredAsOrBy HdfsLocation_EDIT
   OptionalTblproperties
 | 'CREATE' 'MATERIALIZED' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalDisableRewrite OptionalComment
   OptionalPartitionedOn OptionalClusteredOrDistributedOn OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties AsSelectStatement_EDIT
 ;

OptionalPartitionedOn
 :
 | PartitionedOn
 ;

PartitionedOn
 : 'PARTITIONED' 'ON' ParenthesizedColumnList
 ;

PartitionedOn_EDIT
 : 'PARTITIONED' 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'PARTITIONED' 'ON' ParenthesizedColumnList_EDIT
 ;

OptionalClusteredOrDistributedOn
 :
 | ClusteredOn
 | DistributedOn SortedOn
 ;

ClusteredOrDistributedOn_EDIT
 : ClusteredOn_EDIT
 | DistributedOn_EDIT
 | DistributedOn 'CURSOR'
   {
     parser.suggestKeywords(['SORTED ON']);
   }
 | DistributedOn SortedOn_EDIT
 ;

ClusteredOn
 : 'CLUSTERED' 'ON' ParenthesizedColumnList
 ;

ClusteredOn_EDIT
 : 'CLUSTERED' 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'CLUSTERED' 'ON' ParenthesizedColumnList_EDIT
 ;

DistributedOn
 : 'DISTRIBUTED' 'ON' ParenthesizedColumnList
 ;

DistributedOn_EDIT
 : 'DISTRIBUTED' 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'DISTRIBUTED' 'ON' ParenthesizedColumnList_EDIT
 ;

SortedOn
 : 'SORTED' 'ON' ParenthesizedColumnList
 ;

SortedOn_EDIT
 : 'SORTED' 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'SORTED' 'ON' ParenthesizedColumnList_EDIT
 ;

OptionalDisableRewrite
 :
 | 'DISABLE' 'REWRITE'
 ;

DisableRewrite_EDIT
 : 'DISABLE' 'CURSOR'
   {
     parser.suggestKeywords(['REWRITE']);
   }
 ;
