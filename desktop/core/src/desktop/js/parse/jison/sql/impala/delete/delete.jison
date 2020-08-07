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

DataManipulation
 : DeleteStatement
 ;

DataManipulation_EDIT
 : DeleteStatement_EDIT
 ;

DeleteStatement
 : 'DELETE' OptionalDeleteTableRef 'FROM' TableReference OptionalWhereClause
 ;

DeleteStatement_EDIT
 : 'DELETE' OptionalDeleteTableRef 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
     if (!$2) {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
     }
   }
 | 'DELETE' DeleteTableRef_EDIT
 | 'DELETE' OptionalDeleteTableRef 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DELETE' OptionalDeleteTableRef 'FROM' TableReference 'CURSOR' OptionalWhereClause
   {
     var keywords = [{ value: 'FULL JOIN', weight: 1 }, { value: 'FULL OUTER JOIN', weight: 1 }, { value: 'JOIN', weight: 1 }, { value: 'LEFT JOIN', weight: 1 }, { value: 'LEFT OUTER JOIN', weight: 1 }, { value: 'RIGHT JOIN', weight: 1 }, { value: 'RIGHT OUTER JOIN', weight: 1 }, { value: 'INNER JOIN', weight: 1 },  { value: 'LEFT ANTI JOIN', weight: 1 }, { value: 'LEFT SEMI JOIN', weight: 1 }, { value: 'RIGHT ANTI JOIN', weight: 1 }, { value: 'RIGHT SEMI JOIN', weight: 1 }];
     if (!$6) {
       keywords.push({ value: 'WHERE', weight: 3 });
     }
     if ($4.suggestJoinConditions) {
       parser.suggestJoinConditions($4.suggestJoinConditions);
     }
     if ($4.suggestJoins) {
       parser.suggestJoins($4.suggestJoins);
     }
     if ($4.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($4.suggestKeywords, 2));
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 | 'DELETE' DeleteTableRef_EDIT 'FROM'
 | 'DELETE' DeleteTableRef_EDIT 'FROM' TableReference OptionalWhereClause
 | 'DELETE' OptionalDeleteTableRef 'FROM' TableReference_EDIT OptionalWhereClause
 | 'DELETE' OptionalDeleteTableRef 'FROM' TableReference WhereClause_EDIT
 ;

OptionalDeleteTableRef
 :
 | TableReference
 ;

DeleteTableRef_EDIT
 : TableReference_EDIT
 ;
