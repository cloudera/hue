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

OptionalClusteredBy
 :
 | ClusteredBy
 ;

ClusteredBy
 : 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy 'INTO' 'UNSIGNED_INTEGER' 'BUCKETS'
 ;

ClusteredBy_EDIT
 : 'CLUSTERED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalSortedBy
 | 'CLUSTERED' 'BY' ParenthesizedColumnList_EDIT OptionalSortedBy 'INTO' 'UNSIGNED_INTEGER' 'BUCKETS'
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords([{ value: 'INTO', weight: 1 }, { value: 'SORTED BY', weight: 2 }]);
     } else {
       parser.suggestKeywords(['INTO']);
     }
   }
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy 'INTO' 'UNSIGNED_INTEGER' 'CURSOR'
   {
     parser.suggestKeywords(['BUCKETS']);
   }
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy_EDIT 'INTO' 'UNSIGNED_INTEGER' 'BUCKETS'
 | 'CLUSTERED' 'BY' ParenthesizedColumnList OptionalSortedBy_EDIT
 ;

OptionalSortedBy
 :
 | 'SORTED' 'BY' ParenthesizedSortList
 ;

OptionalSortedBy_EDIT
 : 'SORTED' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
   }
 | 'SORTED' 'BY' ParenthesizedSortList_EDIT
 ;

ParenthesizedSortList
 : '(' SortList ')'
 ;

ParenthesizedSortList_EDIT
 : '(' SortList_EDIT RightParenthesisOrError
 ;

SortList
 : SortIdentifier
 | SortList ',' SortIdentifier
 ;

SortList_EDIT
 : SortIdentifier_EDIT
 | SortIdentifier_EDIT ',' SortList
 | SortList ',' SortIdentifier_EDIT
 | SortList ',' SortIdentifier_EDIT ',' SortList
 ;

SortIdentifier
 : ColumnIdentifier OptionalAscOrDesc
 ;

SortIdentifier_EDIT
 : ColumnIdentifier OptionalAscOrDesc 'CURSOR'
   {
     parser.checkForKeywords($2);
   }
 | ColumnIdentifier_EDIT OptionalAscOrDesc
 | AnyCursor OptionalAscOrDesc
   {
     parser.suggestColumns();
   }
 ;