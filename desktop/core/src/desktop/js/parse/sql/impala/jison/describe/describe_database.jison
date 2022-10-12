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
 : DescribeDatabaseStatement
 ;

DataDefinition_EDIT
 : DescribeDatabaseStatement_EDIT
 ;

DescribeDatabaseStatement
 : 'DESCRIBE' 'DATABASE' OptionalExtendedOrFormatted DatabaseIdentifier
   {
     parser.addDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DescribeDatabaseStatement_EDIT
 : 'DESCRIBE' 'DATABASE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
     }
     parser.suggestDatabases();
   }
 | 'DESCRIBE' 'DATABASE' OptionalExtendedOrFormatted 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        parser.suggestKeywords(['EXTENDED', 'FORMATTED']);
      }
      parser.addDatabaseLocation(@5, [{ name: $5 }]);
    }
 ;
