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

Auxiliary
 : AnalyzeTables
 ;

Auxiliary_EDIT
 : AnalyzeTables_EDIT
 ;

AnalyzeTable
 : 'ANALYZE' 'TABLES' OptionalFromOrInDatabase 'COMPUTE' 'STATISTICS' OptionalNoScan
 ;

AnalyzeTable_EDIT
 : 'ANALYZE' 'TABLES' OptionalFromOrInDatabase 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['FROM', 'IN', 'COMPUTE STATISTICS']);
     } else {
       parser.suggestKeywords(['COMPUTE STATISTICS']);
     }
   }
 | 'ANALYZE' 'TABLES' FromOrInDatabase_EDIT
 | 'ANALYZE' 'TABLES' OptionalFromOrInDatabase 'COMPUTE' 'CURSOR'
   {
     parser.suggestKeywords(['STATISTICS']);
   }
 | 'ANALYZE' 'TABLES' OptionalFromOrInDatabase 'COMPUTE' 'STATISTICS' OptionalNoScan 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['NOSCAN']);
     }
   }
 ;


OptionalNoScan
 :
 | 'NOSCAN'
 ;