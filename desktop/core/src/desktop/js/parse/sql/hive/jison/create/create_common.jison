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

DataDefinition_EDIT
 : 'CREATE' OptionalTemporary OptionalTransactional OptionalExternal OptionalRemote 'CURSOR'
   {
     if ($5) {
       parser.suggestKeywords(['DATABASE']);
     } else if ($4) {
       parser.suggestKeywords(['TABLE']);
     } else {
       if ($2 && !$3) {
         parser.suggestKeywords(['EXTERNAL TABLE', 'FUNCTION', 'MACRO', 'TABLE']);
       } else if (!$2 && !$3) {
         parser.suggestKeywords(['CONNECTOR', 'DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'INDEX', 'MATERIALIZED VIEW',
           'REMOTE DATABASE', 'ROLE', 'SCHEDULED QUERY', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE',
           'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'TEMPORARY TABLE', 'TRANSACTIONAL TABLE', 'VIEW']);
       } else if ($3) {
         parser.suggestKeywords(['TABLE']);
       }
     }
   }
 ;

OptionalComment
 :
 | Comment
 ;

OptionalRemote
 :
 | 'REMOTE'
 ;

Comment
 : 'COMMENT' QuotedValue
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

ParenthesizedColumnSpecificationList
 : '(' ColumnSpecificationList ')'                              -> $2
 | '(' ColumnSpecificationList ',' TableConstraints ')'  -> $2
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' TableConstraints_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords([{ value: 'PRIMARY KEY', weight: 2 }, { value: 'CONSTRAINT', weight: 1 }]);
   }
 ;

ColumnSpecificationList
 : ColumnSpecification                              -> [$1]
 | ColumnSpecificationList ',' ColumnSpecification  -> $1.concat($3)
 ;

ColumnSpecificationList_EDIT
 : ColumnSpecification_EDIT
 | ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecificationList ',' ColumnSpecification_EDIT
 | ColumnSpecificationList ',' ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecification 'CURSOR'
   {
     parser.checkForKeywords($1);
   }
 | ColumnSpecification 'CURSOR' ',' ColumnSpecificationList
   {
     parser.checkForKeywords($1);
   }
 | ColumnSpecificationList ',' ColumnSpecification 'CURSOR'
   {
     parser.checkForKeywords($3);
   }
 | ColumnSpecificationList ',' ColumnSpecification 'CURSOR' ',' ColumnSpecificationList
   {
     parser.checkForKeywords($3);
   }
 ;

ColumnSpecification
 : ColumnIdentifier ColumnDataType OptionalColumnOptions OptionalComment
   {
     $$ = $1;
     $$.type = $2;
     var keywords = [];
     if (!$4) {
       keywords = keywords.concat([
         { value: 'COMMENT', weight: 1 },
         { value: 'CHECK', weight: 2 },
         { value: 'PRIMARY KEY', weight: 2 },
         { value: 'UNIQUE', weight: 2 },
         { value: 'NOT NULL', weight: 2 },
         { value: 'DEFAULT', weight: 2 }
       ]);
       if (!$3 && $2.toLowerCase() === 'double') {
         keywords.push({ value: 'PRECISION', weight: 3 });
       } else if ($3 && $3.suggestKeywords) {
         keywords = keywords.concat($3.suggestKeywords)
       }
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

ColumnSpecification_EDIT
 : ColumnIdentifier 'CURSOR' OptionalColumnOptions OptionalComment
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | ColumnIdentifier ColumnDataType_EDIT OptionalColumnOptions OptionalComment
 ;

OptionalColumnOptions
 :
 | ColumnOptions
 ;

ColumnOptions
 : ColumnOption
 | ColumnOptions ColumnOption
 ;

ColumnOption
 : 'PRIMARY' 'KEY' ColumnOptionOptionals                  -> $3
 | 'PRIMARY'                                              -> { suggestKeywords: [{ value: 'KEY', weight: 3 }] }
 | 'UNIQUE' ColumnOptionOptionals                         -> $2
 | 'NOT' 'NULL' ColumnOptionOptionals                     -> $3
 | 'NOT'                                                  -> { suggestKeywords: [{ value: 'NULL', weight: 3 }] }
 | 'DEFAULT' DefaultValue ColumnOptionOptionals           -> $3
 | 'CHECK' '(' ValueExpression ')' ColumnOptionOptionals  -> $5
 | 'DEFAULT'
   {
     $$ = {
       suggestKeywords: [
         { value: 'LITERAL', weight: 3 },
         { value: 'CURRENT_USER()', weight: 3 },
         { value: 'CURRENT_DATE()', weight: 3 },
         { value: 'CURRENT_TIMESTAMP()', weight: 3 },
         { value: 'NULL', weight: 3 }
       ]
     }
   }
 ;

ColumnOptionOptionals
 : OptionalEnableOrDisable OptionalNovalidate OptionalRelyOrNorely
   {
     var keywords = [];
     if (!$3) {
       keywords.push({ value: 'RELY', weight: 3 });
       keywords.push({ value: 'NORELY', weight: 3 });
       if (!$2) {
         keywords.push({ value: 'NOVALIDATE', weight: 3 });
         if (!$1) {
           keywords.push({ value: 'RELY', weight: 3 });
           keywords.push({ value: 'NORELY', weight: 3 });
         }
       }
     }
     if (keywords.length) {
       $$ = { suggestKeywords: keywords };
     }
   }
 ;

DefaultValue
 : 'LITERAL'
 | 'CURRENT_USER' '(' ')'
 | 'CURRENT_DATE' '(' ')'
 | 'CURRENT_TIMESTAMP' '(' ')'
 | 'NULL'
 ;

OptionalEnableOrDisable
 :
 | 'ENABLE'
 | 'DISABLE'
 ;

OptionalDisable
 :
 | 'DISABLE'
 ;

OptionalNovalidate
 :
 | 'NOVALIDATE'
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
 : 'ARRAY' '<' ColumnDataType '>'
 ;

ArrayType_INVALID
 : 'ARRAY' '<' '>'
 ;

ArrayType_EDIT
 : 'ARRAY' '<' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | 'ARRAY' '<' ColumnDataType_EDIT GreaterThanOrError
 ;

MapType
 : 'MAP' '<' PrimitiveType ',' ColumnDataType '>'
 ;

MapType_INVALID
 : 'MAP' '<' '>'
 ;

MapType_EDIT
 : 'MAP' '<' PrimitiveType ',' ColumnDataType_EDIT GreaterThanOrError
 | 'MAP' '<' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 | 'MAP' '<' PrimitiveType ',' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | 'MAP' '<' ',' AnyCursor GreaterThanOrError
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 ;

StructType
 : 'STRUCT' '<' StructDefinitionList '>'
 ;

StructType_INVALID
 : 'STRUCT' '<' '>'
 ;

StructType_EDIT
 : 'STRUCT' '<' StructDefinitionList_EDIT GreaterThanOrError
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

StructDefinition
 : RegularOrBacktickedIdentifier ':' ColumnDataType OptionalComment
 ;

StructDefinition_EDIT
 : Commas RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     parser.suggestKeywords(['COMMENT']);
   }
 | Commas RegularOrBacktickedIdentifier ':' AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | Commas RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 | RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     parser.suggestKeywords(['COMMENT']);
   }
 | RegularOrBacktickedIdentifier ':' AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 ;

UnionType
 : 'UNIONTYPE' '<' ColumnDataTypeList '>'
 ;

UnionType_INVALID
 : 'UNIONTYPE' '<' '>'
 ;

UnionType_EDIT
 : 'UNIONTYPE' '<' ColumnDataTypeList_EDIT GreaterThanOrError
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
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | Commas ColumnDataType_EDIT
 | AnyCursor
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | ColumnDataType_EDIT
 ;

GreaterThanOrError
 : '>'
 | error
 ;

TableConstraints
 : PrimaryKeySpecification
 | ConstraintList
 | PrimaryKeySpecification ',' ConstraintList
 ;

TableConstraints_EDIT
 : PrimaryKeySpecification_EDIT
 | PrimaryKeySpecification ',' 'CURSOR'
   {
     parser.suggestKeywords(['CONSTRAINT']);
   }
 | ConstraintList_EDIT
 | PrimaryKeySpecification ',' ConstraintList_EDIT
 | PrimaryKeySpecification_EDIT ',' ConstraintList
 ;

ConstraintList
 : TableConstraint
 | ConstraintList ',' TableConstraint
 ;

ConstraintList_EDIT
 : TableConstraint_EDIT
 | ConstraintList ',' TableConstraint_EDIT
 ;

PrimaryKeySpecification
 : PrimaryKey ParenthesizedColumnList OptionalDisable OptionalNovalidate OptionalRelyOrNorely
 ;

PrimaryKeySpecification_EDIT
 : PrimaryKey_EDIT
 | PrimaryKey ParenthesizedColumnList_EDIT
 | PrimaryKey ParenthesizedColumnList OptionalDisable OptionalNovalidate OptionalRelyOrNorely 'CURSOR'
   {
     parser.suggestKeywordsForOptionalsLR([$5, $4, $3], [
        [{ value: 'RELY', weight: 1 }, { value: 'NORELY', weight: 1 }],
        { value: 'NOVALIDATE', weight: 2 },
        { value: 'DISABLE', weight: 1 }]);
   }
 ;

OptionalRelyOrNorely
 :
 | 'RELY'
 | 'NORELY'
 ;

PrimaryKey
 : 'PRIMARY' 'KEY'
 ;

PrimaryKey_EDIT
 : 'PRIMARY' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 ;

ParenthesizedSkewedValueList
 : '(' SkewedValueList ')'
 ;

SkewedValueList
 : ParenthesizedSimpleValueList
 | SkewedValueList ',' ParenthesizedSimpleValueList
 ;

OptionalStoredAsOrBy
 :
 | StoredAsOrBy
 ;

StoredAsOrBy
 : StoredAs
 | StoredBy           -> { storedBy: true, suggestKeywords: ['STORED AS', 'WITH SERDEPROPERTIES'] }
 | StoredBy WithSerdeproperties
 | StoredBy WithSerdeproperties StoredAs
 | StoredBy StoredAs
 ;

StoredAsOrBy_EDIT
 : 'STORED' 'CURSOR'
   {
     parser.suggestKeywords(['AS', 'BY']);
   }
 | StoredBy_EDIT
 | StoredBy 'STORED' 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | StoredBy StoredAs_EDIT
 | StoredBy WithSerdeproperties_EDIT
 | StoredBy_EDIT StoredAs
 | StoredBy WithSerdeproperties_EDIT StoredAs
 | StoredAs_EDIT
 ;

OptionalStoredAs
 :           -> { suggestKeywords: ['STORED AS'] }
 | StoredAs
 ;

StoredAs
 : 'STORED' 'AS' FileFormat
 ;

StoredAs_EDIT
 : 'STORED' 'AS' 'CURSOR'
   {
     parser.suggestFileFormats();
   }
 ;

StoredBy
 : 'STORED' 'BY' QuotedValue
   {
     $$ = { storedBy: true }
   }
 | 'STORED' 'BY' 'ICEBERG'
   {
     $$ = { storedBy: true }
   }
 ;

StoredBy_EDIT
 : 'STORED' 'BY' 'CURSOR'
   {
     parser.suggestKeywords(['ICEBERG']);
   }
 ;

FileFormat
 : 'AVRO'
 | 'INPUTFORMAT' QuotedValue 'OUTPUTFORMAT' QuotedValue
 | 'JSONFILE'
 | 'ORC'
 | 'PARQUET'
 | 'RCFILE'
 | 'SEQUENCEFILE'
 | 'TEXTFILE'
 ;

OptionalTblproperties
 :
 | TblProperties
 ;

TblProperties
 : 'TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

AsSelectStatement
 : 'AS' CommitLocations QuerySpecification
 ;

AsSelectStatement_EDIT
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
