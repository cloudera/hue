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

%lex
%options flex
%%

\s                                                                    { /* skip whitespace */ }
'--'.*                                                                { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]                                   { /* skip comments */ }

<<EOF>>                                                               { return 'EOF'; }
([^;"'`]|(["][^"]*["])|(['][^']*['])|([`][^`]*[`]))*[;]?              { return 'STATEMENT'; }

.                                                                     { /* skip unknown chars */ }

/lex

%start SqlStatementsParser

%%

SqlStatementsParser
 : Statements EOF
   {
     return $1;
   }
 | EOF
   {
     return [];
   }
 ;

Statements
 : 'STATEMENT'                                                        --> [{ type: 'statement', statement: $1, location: @1 }]
 | Statements 'STATEMENT'
   {
     $1.push({ type: 'statement', statement: $2, location: @2 });
   }
 ;