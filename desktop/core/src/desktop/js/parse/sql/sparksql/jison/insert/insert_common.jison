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

DataManipulation_EDIT
 : 'INSERT' OptionalInsertOptions 'CURSOR'
   {
     var keywords = $2.tableKeywords || [];
     if ($2.directoryKeywords) {
       keywords = keywords.concat($2.directoryKeywords);
     }
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
     if ($2.suggestTables) {
       parser.suggestTables({ tablesOnly: true });
       parser.suggestDatabases({ appendDot: true });
     }
   }
 ;

OptionalInsertOptions
 :                     -> { suggestTables: true, tableKeywords: ['INTO', 'INTO TABLE', 'OVERWRITE', 'OVERWRITE TABLE', 'TABLE'], directoryKeywords: ['OVERWRITE DIRECTORY', 'OVERWRITE LOCAL DIRECTORY'] }
 | 'INTO'              -> { suggestTables: true, tableKeywords: ['TABLE'] }
 | 'OVERWRITE'         -> { suggestTables: true, tableKeywords: ['TABLE'], directoryKeywords: ['DIRECTORY', 'LOCAL DIRECTORY'] }
 | 'INTO' 'TABLE'      -> { suggestTables: true }
 | 'OVERWRITE' 'TABLE' -> { suggestTables: true }
 | 'TABLE'             -> { suggestTables: true }
 | 'OVERWRITE' 'LOCAL' -> { directoryKeywords: ['DIRECTORY'] }
 ;

// TODO: FROM x SELECT y ...
ValuesClauseOrQuerySpecification
 : ValuesClause
 | QuerySpecification
 ;

ValuesClauseOrQuerySpecification_EDIT
 : QuerySpecification_EDIT
 ;

ValuesClause
 : 'VALUES' ValuesList
 ;

ValuesList
 : ParenthesizedRowValuesList
 | ValuesList ',' ParenthesizedRowValuesList
 ;

ParenthesizedRowValuesList
 : '(' InValueList ')'
 ;