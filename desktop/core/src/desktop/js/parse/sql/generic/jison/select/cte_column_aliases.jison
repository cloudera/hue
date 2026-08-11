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

WithQuery
 : RegularOrBacktickedIdentifier CteColumnAliasList 'AS' '(' TableSubQueryInner ')'
   {
     parser.addCteAliasLocation(@1, $1);
     $5.alias = $1;
     $5.columnAliases = $2;
     $$ = $5;
   }
 ;

WithQuery_EDIT
 : RegularOrBacktickedIdentifier CteColumnAliasList 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | RegularOrBacktickedIdentifier CteColumnAliasList 'AS' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['SELECT']);
   }
 | RegularOrBacktickedIdentifier CteColumnAliasList 'AS' '(' TableSubQueryInner_EDIT RightParenthesisOrError
 ;

CteColumnAliasList
 : '(' CteColumnAliases ')'  -> $2
 ;

CteColumnAliases
 : ColumnIdentifier                      -> [$1.identifier.name]
 | CteColumnAliases ',' ColumnIdentifier -> $1.concat([$3.identifier.name])
 ;
