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
 : CreateStatement
 ;

DataDefinition_EDIT
 : CreateStatement_EDIT
 ;

CreateStatement
 : DatabaseDefinition
 | TableDefinition
 | ViewDefinition
 | RoleDefinition
 ;

CreateStatement_EDIT
 : DatabaseDefinition_EDIT
 | TableDefinition_EDIT
 | ViewDefinition_EDIT
 | 'CREATE' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
   }
 ;

DatabaseDefinition
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinition_EDIT
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists_EDIT
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.addNewDatabaseLocation(@5, [{ name: $5 }]);
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinitionOptionals
 : OptionalComment
   {
     if (!$1) {
       parser.suggestKeywords(['COMMENT']);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment_INVALID
 ;

OptionalComment
 :
 | Comment
 ;

Comment
 : 'COMMENT' QuotedValue
 ;

OptionalComment_INVALID
 : Comment_INVALID
 ;

Comment_INVALID
 : 'COMMENT' SINGLE_QUOTE
 | 'COMMENT' DOUBLE_QUOTE
 | 'COMMENT' SINGLE_QUOTE VALUE
 | 'COMMENT' DOUBLE_QUOTE VALUE
 ;

TableDefinition
 : 'CREATE' 'TABLE' OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : 'CREATE' 'TABLE' OptionalIfNotExists TableDefinitionRightPart_EDIT
 | 'CREATE' 'TABLE' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'TABLE' OptionalIfNotExists_EDIT
 ;

TableDefinitionRightPart
 : TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalAsSelectStatement
 ;

TableDefinitionRightPart_EDIT
 : TableIdentifierAndOptionalColumnSpecification_EDIT OptionalPartitionedBy OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification PartitionedBy_EDIT OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy OptionalAsSelectStatement_EDIT
 | TableIdentifierAndOptionalColumnSpecification OptionalPartitionedBy 'CURSOR'
   {
     var keywords = [];
     if (!$1 && !$2) {
       keywords.push({ value: 'LIKE', weight: 1 });
     } else {
       if (!$2) {
         keywords.push({ value: 'PARTITIONED BY', weight: 12 });
       }
       keywords.push({ value: 'AS', weight: 1 });
     }

     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
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
 | 'LIKE' SchemaQualifiedTableIdentifier    -> []
 ;

OptionalColumnSpecificationsOrLike_EDIT
 : ParenthesizedColumnSpecificationList_EDIT
 | 'LIKE' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'LIKE' SchemaQualifiedTableIdentifier_EDIT
 ;

ParenthesizedColumnSpecificationList
 : '(' ColumnSpecificationList ')'                              -> $2
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
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
 : ColumnIdentifier ColumnDataType OptionalColumnOptions
   {
     $$ = $1;
     $$.type = $2;
     var keywords = [];
     if (!$3['comment']) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       $$.suggestKeywords = keywords;
     }
   }
 ;

ColumnSpecification_EDIT
 : ColumnIdentifier 'CURSOR' OptionalColumnOptions
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | ColumnIdentifier ColumnDataType_EDIT OptionalColumnOptions
 | ColumnIdentifier ColumnDataType ColumnOptions_EDIT
 ;

OptionalColumnOptions
 :                      -> {}
 | ColumnOptions
 ;

ColumnOptions
 : ColumnOption
   {
     $$ = {};
     $$[$1] = true;
   }
 | ColumnOptions ColumnOption
   {
     $1[$2] = true;
   }
 ;

ColumnOptions_EDIT
 : ColumnOption_EDIT
 | ColumnOption_EDIT ColumnOptions
 | ColumnOptions ColumnOption_EDIT
 | ColumnOptions ColumnOption_EDIT ColumnOptions
 ;

ColumnOption
 : 'NOT' 'NULL'                                              -> 'null'
 | 'NULL'                                                    -> 'null'
 | Comment                                                   -> 'comment'
 ;

ColumnOption_EDIT
 : 'NOT' 'CURSOR'
   {
     parser.suggestKeywords(['NULL']);
   }
 ;

ColumnDataType
 : PrimitiveType
 | ArrayType
 | MapType
 | StructType
 | ArrayType_INVALID
 | MapType_INVALID
 | StructType_INVALID
 ;

ColumnDataType_EDIT
 : ArrayType_EDIT
 | MapType_EDIT
 | StructType_EDIT
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

OptionalPartitionedBy
 :
 | PartitionedBy
 ;

PartitionedBy
 : 'PARTITION' 'BY' RangeClause
 ;

PartitionedBy_EDIT
 : 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'PARTITION' 'BY' 'CURSOR'
   {
     parser.suggestKeywords(['RANGE']);
   }
 | 'PARTITION' 'BY' RangeClause_EDIT
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
 ;

PartitionValue_EDIT
 : 'PARTITION' 'CURSOR'
   {
     parser.suggestKeywords(['VALUE', 'VALUES']);
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

ViewDefinition
 : 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
 ;

ViewDefinition_EDIT
 : 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedViewColumnList_EDIT OptionalComment
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'CURSOR'
   {
     var keywords = [{value: 'AS', weight: 1 }];
     if (!$6) {
       keywords.push({ value: 'COMMENT', weight: 3 });
     }
     parser.suggestKeywords(keywords);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification_EDIT
 | 'CREATE' 'VIEW' OptionalIfNotExists SchemaQualifiedIdentifier_EDIT OptionalParenthesizedViewColumnList OptionalComment 'AS' QuerySpecification
 ;

OptionalParenthesizedViewColumnList
 :
 | ParenthesizedViewColumnList
 ;

ParenthesizedViewColumnList
 : '(' ViewColumnList ')'
 ;

ParenthesizedViewColumnList_EDIT
 : '(' ViewColumnList_EDIT RightParenthesisOrError
   {
     if (!$2) {
       parser.suggestKeywords(['COMMENT']);
     }
   }
 ;

ViewColumnList
 : ColumnReference OptionalComment
 | ViewColumnList ',' ColumnReference OptionalComment
 ;

ViewColumnList_EDIT
 : ColumnReference OptionalComment 'CURSOR'                                        -> $2
 | ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList                     -> $2
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR'                     -> $4
 | ViewColumnList ',' ColumnReference OptionalComment 'CURSOR' ',' ViewColumnList  -> $4
 ;

RoleDefinition
 : 'CREATE' 'ROLE' RegularIdentifier
 ;
