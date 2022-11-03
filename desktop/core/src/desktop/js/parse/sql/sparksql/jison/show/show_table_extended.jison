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
 : ShowTableExtended
 ;

Auxiliary_EDIT
 : ShowTableExtended_EDIT
 ;

ShowTableExtended
 : 'SHOW' 'TABLE' 'EXTENDED' OptionalFromOrInDatabase LikeRegex OptionalPartitionSpec
 ;

ShowTableExtended_EDIT
 : 'SHOW' 'TABLE' 'CURSOR'
   {
     parser.suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromOrInDatabase 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords([{ value: 'FROM', weight: 2 }, { value: 'IN', weight: 2 }, { value: 'LIKE', weight: 1 }]);
     } else {
       parser.suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' 'TABLE' 'EXTENDED' FromOrInDatabase_EDIT
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromOrInDatabase LikeRegex OptionalPartitionSpec 'CURSOR'
   {
     if (!$6) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromOrInDatabase LikeRegex PartitionSpec_EDIT
 | 'SHOW' 'TABLE' 'EXTENDED' FromOrInDatabase_EDIT LikeRegex OptionalPartitionSpec
 ;