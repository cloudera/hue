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
 : DescribeHistoryStatement
 ;

DataDefinition_EDIT
 : DescribeHistoryStatement_EDIT
 ;

DescribeHistoryStatement
 : 'DESCRIBE' 'HISTORY' SchemaQualifiedTableIdentifier OptionalFromOrBetweenExpression
   {
     parser.addTablePrimary($3);
   }
 ;

DescribeHistoryStatement_EDIT
 : 'DESCRIBE' 'HISTORY' 'CURSOR' OptionalFromOrBetweenExpression
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DESCRIBE' 'HISTORY' SchemaQualifiedTableIdentifier_EDIT OptionalFromOrBetweenExpression
 | 'DESCRIBE' 'HISTORY' SchemaQualifiedTableIdentifier 'CURSOR' OptionalFromOrBetweenExpression
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords(['BETWEEN', 'FROM']);
     }
   }
 | 'DESCRIBE' 'HISTORY' SchemaQualifiedTableIdentifier FromOrBetweenExpression_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

OptionalFromOrBetweenExpression
 :
 | FromOrBetweenExpression
 ;

FromOrBetweenExpression
 : FromOrBetween ValueExpression
 ;

FromOrBetweenExpression_EDIT
 : FromOrBetween 'CURSOR'
   {
     parser.valueExpressionSuggest();
     delete parser.yy.result.suggestColumns;
   }
 | FromOrBetween ValueExpression_EDIT
   {
     delete parser.yy.result.suggestColumns;
   }
 ;

FromOrBetween
 : 'FROM'
 | 'BETWEEN'
 ;