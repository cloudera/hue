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
 : DescribeStatement
 ;

DataDefinition_EDIT
 : DescribeStatement_EDIT
 ;

DescribeStatement
 : 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

DescribeStatement_EDIT
 : 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(parser.DESCRIBE_KEYWORDS);
     }
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | 'DESCRIBE' OptionalExtendedOrFormatted 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
     if (!$2) {
       parser.suggestKeywords(parser.DESCRIBE_KEYWORDS);
     }
   }
 ;
