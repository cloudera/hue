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
 : CreateTemporaryMacro
 ;

DataDefinition_EDIT
 : CreateTemporaryMacro_EDIT
 ;

CreateTemporaryMacro
 : 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments ValueExpression
 ;

CreateTemporaryMacro_EDIT
 : 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments_EDIT
 | 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments_EDIT ValueExpression
 | 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments 'CURSOR'
   {
     parser.suggestFunctions();
   }
 | 'CREATE' 'TEMPORARY' 'MACRO' RegularIdentifier MacroArguments ValueExpression_EDIT
 ;

MacroArguments
 : '(' ')'
 | '(' MacroArgumentList ')'
 ;

MacroArguments_EDIT
 : '(' MacroArgumentList_EDIT RightParenthesisOrError
 ;

MacroArgumentList
 : MacroArgument
 | MacroArgumentList ',' MacroArgument
 ;

MacroArgumentList_EDIT
 : MacroArgument_EDIT
 | MacroArgumentList ',' MacroArgument_EDIT
 | MacroArgument_EDIT ',' MacroArgumentList
 | MacroArgumentList ',' MacroArgument_EDIT ',' MacroArgumentList
 ;

MacroArgument
 : RegularIdentifier ColumnDataType
 ;

MacroArgument_EDIT
 : RegularIdentifier 'CURSOR'
   {
     parser.suggestKeywords(parser.getColumnDataTypeKeywords());
   }
 | RegularIdentifier ColumnDataType_EDIT
 ;
