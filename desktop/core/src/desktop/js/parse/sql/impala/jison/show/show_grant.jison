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
 : ShowGrantStatement
 ;

DataDefinition_EDIT
 : ShowGrantStatement_EDIT
 ;

ShowGrantStatement
 : 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'DATABASE' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@7, [ { name: $7 } ]);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'COLUMN' RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@7, [ { name: $7 } ]);
     parser.addTableLocation(@9, [ { name: $7 }, { name: $9 } ]);
     parser.addColumnLocation(@11, [ { name: $7 }, { name: $9 }, { name: $11 } ]);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'SERVER'
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'TABLE' SchemaQualifiedTableIdentifier
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'URI' RegularOrBacktickedIdentifier
 ;

ShowGrantStatement_EDIT
 : 'SHOW' 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser 'CURSOR'
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMN', 'DATABASE', 'SERVER', 'TABLE', 'URI']);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'COLUMN' 'CURSOR'
    {
      parser.suggestDatabases({
        appendDot: true
      });
      parser.suggestTables();
    }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'COLUMN' RegularOrBacktickedIdentifier '.' PartialBacktickedOrPartialCursor
    {
      parser.addDatabaseLocation(@7, [ { name: $7 } ]);
      parser.suggestTablesOrColumns($7);
    }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'COLUMN' RegularOrBacktickedIdentifier '.' RegularOrBacktickedIdentifier '.' PartialBacktickedOrPartialCursor
    {
      parser.addDatabaseLocation(@7, [ { name: $7 } ]);
      parser.addTableLocation(@9, [ { name: $7 }, { name: $9 } ]);
      parser.suggestColumns({
        identifierChain: [ { name: $7 }, { name: $9 } ]
      });
    }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'DATABASE' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'TABLE' 'CURSOR'
   {
     parser.suggestDatabases({
       appendDot: true
     });
     parser.suggestTables();
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'URI' 'CURSOR'
 ;
