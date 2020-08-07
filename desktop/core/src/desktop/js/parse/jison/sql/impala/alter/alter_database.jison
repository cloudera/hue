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
 : AlterDatabase
 ;

DataDefinition_EDIT
 : AlterDatabase_EDIT
 ;

AlterDatabase
 : 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' 'OWNER' RoleOrUser RegularOrBacktickedIdentifier
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
    }
 ;

AlterDatabase_EDIT
 : 'ALTER' DatabaseOrSchema 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
     parser.suggestKeywords(['SET OWNER']);
   }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' 'CURSOR'
    {
      parser.addDatabaseLocation(@3, [ { name: $3 } ]);
      parser.suggestKeywords(['OWNER']);
    }
 | 'ALTER' DatabaseOrSchema RegularOrBacktickedIdentifier 'SET' 'OWNER' 'CURSOR'
   {
     parser.addDatabaseLocation(@3, [ { name: $3 } ]);
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 ;
