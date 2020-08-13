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
 : CreateIndex
 ;

DataDefinition_EDIT
 : CreateIndex_EDIT
 ;

CreateIndex
 : 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat
   OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalComment
 ;

CreateIndex_EDIT
 : 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON TABLE']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable_EDIT
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' 'CURSOR'
   {
     parser.suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType_EDIT OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable_EDIT ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList_EDIT
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType WithDeferredRebuild_EDIT OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties InTable_EDIT OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable RowFormat_EDIT OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat StoredAsOrBy_EDIT OptionalHdfsLocation
   OptionalTblproperties OptionalComment
   {
     if ($13 && parser.yy.result.suggestKeywords && parser.yy.result.suggestKeywords.length === 2) {
       parser.suggestKeywords(['AS']);
     }
   }
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy HdfsLocation_EDIT
   OptionalTblproperties OptionalComment
 | 'CREATE' 'INDEX' RegularOrBacktickedIdentifier 'ON' 'TABLE' ExistingTable ParenthesizedIndexColumnList
   'AS' IndexType OptionalWithDeferredRebuild OptionalIdxProperties OptionalInTable OptionalRowFormat OptionalStoredAsOrBy OptionalHdfsLocation
   OptionalTblproperties OptionalComment 'CURSOR'
   {
     if (!$10 && !$11 && !$12 && !$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'WITH DEFERRED REBUILD', weight: 7 }, { value: 'IDXPROPERTIES', weight: 6 }, { value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$11 && !$12 && !$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'IDXPROPERTIES', weight: 6 }, { value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$12 && !$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'IN TABLE', weight: 5 }, { value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$13 && !$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'ROW FORMAT', weight: 4 }, { value: 'STORED AS', weight: 4 }, { value: 'STORED BY', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if ($13 && $13.suggestKeywords && !$14 && !$15 && !$16) {
       parser.suggestKeywords(parser.createWeightedKeywords($13.suggestKeywords, 5).concat([{ value: 'STORED AS', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]));
     } else if (!$14 && !$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'STORED AS', weight: 4 }, { value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$15 && !$16 && !$17) {
       parser.suggestKeywords([{ value: 'LOCATION', weight: 3 }, { value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$16 && !$17) {
       parser.suggestKeywords([{ value: 'TBLPROPERTIES', weight: 2 }, { value: 'COMMENT', weight: 1 }]);
     } else if (!$17) {
       parser.suggestKeywords([{ value: 'COMMENT', weight: 1 }]);
     }
   }
 ;

ExistingTable
 : SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($1);
   }
 ;

ExistingTable_EDIT
 : SchemaQualifiedTableIdentifier_EDIT
 ;

IndexType
 : QuotedValue
 ;

IndexType_EDIT
 : QuotedValue_EDIT
   {
     parser.suggestKeywords(['\'BITMAP\'', '\'COMPACT\'']);
   }
 ;

OptionalWithDeferredRebuild
 :
 | 'WITH' 'DEFERRED' 'REBUILD'
 ;

WithDeferredRebuild_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DEFERRED REBUILD']);
   }
 | 'WITH' 'DEFERRED' 'CURSOR'
   {
     parser.suggestKeywords(['REBUILD']);
   }
 ;

OptionalIdxProperties
 :
 | 'IDXPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalInTable
 :
 | 'IN' 'TABLE' SchemaQualifiedTableIdentifier
 ;

InTable_EDIT
 : 'IN' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'IN' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'IN' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 ;

ParenthesizedIndexColumnList
 : '(' IndexColumnList ')'
 ;

ParenthesizedIndexColumnList_EDIT
 : '(' IndexColumnList_EDIT RightParenthesisOrError
   {
     parser.suggestColumns();
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
