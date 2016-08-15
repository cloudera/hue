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

SqlStatements
 : error
 | NonStartingToken error // Having just ': error' does not work for some reason, jison bug?
 ;

SelectStatement
 : 'SELECT' OptionalAllOrDistinct SelectList_ERROR TableExpression
 | 'SELECT' OptionalAllOrDistinct SelectList_ERROR TableExpression_EDIT
 ;

SelectList_ERROR
 : SelectList ',' error ',' SelectList
 | error ',' SelectList
 | SelectList ',' error
 | error
 | error ',' AnyCursor
   {
     suggestFunctions();
     suggestColumns();
     suggestFunctions();
     $$ = { cursorAtStart : false, suggestAggregateFunctions: true };
   }
 | SelectList ',' error ',' SelectList_EDIT
 | SelectList ',' error ',' AnyCursor
   {
     suggestFunctions();
     suggestColumns();
     suggestFunctions();
     $$ = { cursorAtStart : false, suggestAggregateFunctions: true };
   }
 ;

LateralView
 : '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction RegularIdentifier error  -> []
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter UserDefinedFunction error                    -> []
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter error                                        -> []
 | '<hive>LATERAL' error                                                                   -> []
 ;

JoinTypes_EDIT
 : 'FULL' 'CURSOR' error
   {
     suggestKeywords(['JOIN', 'OUTER JOIN']);
   }
 | 'LEFT' 'CURSOR' error
   {
     if (isHive()) {
       suggestKeywords(['JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else if (isImpala()) {
       suggestKeywords(['ANTI JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else {
       suggestKeywords(['JOIN', 'OUTER JOIN']);
     }
   }
 | 'RIGHT' 'CURSOR' error
   {
     if (isImpala()) {
       suggestKeywords(['ANTI JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else {
       suggestKeywords(['JOIN', 'OUTER JOIN']);
     }
   }
 ;

DatabaseDefinition_EDIT
 : AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
 ;
