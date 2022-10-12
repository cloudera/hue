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

ParenthesizedColumnIdentifierList
 : '(' ColumnIdentifierList ')'
 ;

ParenthesizedColumnIdentifierList_EDIT
 : '(' ColumnIdentifierList_EDIT RightParenthesisOrError
 ;

ColumnIdentifierList
 : ColumnIdentifier
 | ColumnIdentifierList ',' ColumnIdentifier
 ;

ColumnIdentifierList_EDIT
 : 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'CURSOR' ',' ColumnIdentifierList
   {
     parser.suggestColumns();
   }
 | ColumnIdentifierList ',' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | ColumnIdentifierList ',' 'CURSOR' ',' ColumnIdentifierList
   {
     parser.suggestColumns();
   }
 ;

ParenthesizedPartitionList
 : '(' PartitionList ')'
 ;

PartitionList
 : PartitionSpec
 | PartitionList, PartitionSpec
 ;
