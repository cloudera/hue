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

AlterStatement
 : CommentOn
 ;

AlterStatement_EDIT
 : CommentOn_EDIT
 ;

CommentOn
 : 'COMMENT' 'ON' 'DATABASE' RegularOrBacktickedIdentifier 'IS' NullableComment
   {
     parser.addDatabaseLocation(@4, [ { name: $4 } ]);
   }
 ;

CommentOn_EDIT
 : 'COMMENT' 'CURSOR'
   {
     parser.suggestKeywords(['ON DATABASE']);
   }
 | 'COMMENT' 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE']);
   }
 | 'COMMENT' 'ON' 'DATABASE' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'COMMENT' 'ON' 'DATABASE' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.addDatabaseLocation(@4, [ { name: $4 } ]);
     parser.suggestKeywords(['IS']);
   }
 | 'COMMENT' 'ON' 'DATABASE' RegularOrBacktickedIdentifier 'IS' 'CURSOR'
   {
     parser.addDatabaseLocation(@4, [ { name: $4 } ]);
     parser.suggestKeywords(['NULL']);
   }
 ;

NullableComment
 : QuotedValue
 | 'NULL'
 ;
