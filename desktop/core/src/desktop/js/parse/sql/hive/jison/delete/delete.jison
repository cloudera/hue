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

DataManipulation
 : DeleteStatement
 ;

DataManipulation_EDIT
 : DeleteStatement_EDIT
 ;

DeleteStatement
 : 'DELETE' 'FROM' SchemaQualifiedTableIdentifier OptionalWhereClause
   {
     parser.addTablePrimary($3);
   }
 ;

DeleteStatement_EDIT
 : 'DELETE' 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'DELETE' 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DELETE' 'FROM' SchemaQualifiedTableIdentifier 'CURSOR' OptionalWhereClause
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords(['WHERE']);
     }
   }
 | 'DELETE' 'FROM' SchemaQualifiedTableIdentifier_EDIT OptionalWhereClause
 | 'DELETE' 'FROM' SchemaQualifiedTableIdentifier WhereClause_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;
