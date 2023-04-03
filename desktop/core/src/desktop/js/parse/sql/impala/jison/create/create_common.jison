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
 : 'CREATE' OptionalExternal 'CURSOR'
   {
     if ($2) {
       parser.suggestKeywords(['TABLE']);
     } else {
       parser.suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
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
 | '(' ColumnSpecificationList ',' PrimaryKeySpecification ')'  -> $2
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' PrimaryKeySpecification_EDIT RightParenthesisOrError
 | '(' ColumnSpecificationList ',' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['PRIMARY KEY']);
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
 : ColumnIdentifier ColumnDataType OptionalColumnOptions
   {
     $$ = $1;
     $$.type = $2;
     var keywords = [];
     if (!$3['primary']) {
       keywords.push('PRIMARY KEY');
     }
     if (!$3['encoding']) {
       keywords.push('ENCODING');
     }
     if (!$3['compression']) {
       keywords.push('COMPRESSION');
     }
     if (!$3['default']) {
       keywords.push('DEFAULT');
     }
     if (!$3['block_size']) {
       keywords.push('BLOCK_SIZE');
     }
     if (!$3['null']) {
       keywords.push('NOT NULL');
       keywords.push('NULL');
     }
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
 : PrimaryKey                                        -> 'primary'
 | 'ENCODING' RegularIdentifier                      -> 'encoding'
 | 'COMPRESSION' RegularIdentifier                   -> 'compression'
 | 'DEFAULT' NonParenthesizedValueExpressionPrimary  -> 'default'
 | 'BLOCK_SIZE' UnsignedNumericLiteral               -> 'block_size'
 | 'NOT' 'NULL'                                      -> 'null'
 | 'NULL'                                            -> 'null'
 | Comment                                           -> 'comment'
 ;

ColumnOption_EDIT
 : PrimaryKey_EDIT
 | 'NOT' 'CURSOR'
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

PrimaryKeySpecification
 : PrimaryKey ParenthesizedColumnList
 ;

PrimaryKeySpecification_EDIT
 : PrimaryKey_EDIT
 | PrimaryKey_EDIT ParenthesizedColumnList
 | PrimaryKey ParenthesizedColumnList_EDIT
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

DelimitedRowFormat
 : 'DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy
   {
     if (!$2 && !$3) {
       $$ = { suggestKeywords: [{ value: 'FIELDS TERMINATED BY', weight: 2 }, { value: 'LINES TERMINATED BY', weight: 1 }] };
     } else if ($2 && $2.suggestKeywords && !$3) {
       $$ = { suggestKeywords: parser.createWeightedKeywords($2.suggestKeywords, 2).concat(['LINES TERMINATED BY']) };
     } else if (!$3) {
       $$ = { suggestKeywords: [{ value: 'LINES TERMINATED BY', weight: 1 }] };
     }
   }
 ;

DelimitedRowFormat_EDIT
 : 'DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalLinesTerminatedBy
 | 'DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy_EDIT
 ;

OptionalFieldsTerminatedBy
 :
 | 'FIELDS' 'TERMINATED' 'BY' SingleQuotedValue  -> { suggestKeywords: ['ESCAPED BY'] }
 | 'FIELDS' 'TERMINATED' 'BY' SingleQuotedValue 'ESCAPED' 'BY' SingleQuotedValue
 ;

OptionalFieldsTerminatedBy_EDIT
 : 'FIELDS' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'FIELDS' 'TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'FIELDS' 'TERMINATED' 'BY' SingleQuotedValue 'ESCAPED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

OptionalLinesTerminatedBy
 :
 | 'LINES' 'TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalLinesTerminatedBy_EDIT
 : 'LINES' 'CURSOR'
   {
     parser.suggestKeywords(['TERMINATED BY']);
   }
 | 'LINES' 'TERMINATED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 ;

TblProperties
 : 'TBLPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

ParenthesizedArgumentList
 : '(' ')'
 | '(' ArgumentList OptionalVariableArguments')'
 ;

ParenthesizedArgumentList_EDIT
 : '(' ArgumentList_EDIT RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 | '(' ArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['...']);
   }
 ;

ArgumentList
 : PrimitiveType
 | ArgumentList ',' PrimitiveType
 ;

ArgumentList_EDIT
 : AnyCursor
 | ArgumentList ',' AnyCursor
 | AnyCursor ',' ArgumentList
 | ArgumentList ',' AnyCursor ',' ArgumentList
 ;

OptionalVariableArguments
 :
 | '...'
 ;

ReturnType
 : 'RETURNS' PrimitiveType
 ;

ReturnType_EDIT
 : 'RETURNS' 'CURSOR'
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 ;

