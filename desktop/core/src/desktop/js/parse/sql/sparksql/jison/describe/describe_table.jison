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
 : DescribeTable
 ;

Auxiliary_EDIT
 : DescribeTable_EDIT
 ;

DescribeTable
 : DescribeOrDesc OptionalTable OptionalExtended SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalColumnIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

DescribeTable_EDIT
 : DescribeOrDesc OptionalTable OptionalExtended SchemaQualifiedTableIdentifier_EDIT
 | DescribeOrDesc OptionalTable OptionalExtended SchemaQualifiedTableIdentifier OptionalPartitionSpec OptionalColumnIdentifier 'CURSOR'
   {
     parser.addTablePrimary($4);
     if (!$5 && !$6) {
       parser.suggestKeywords(['PARTITION']);
     }
     if (!$6) {
       parser.suggestColumns();
     }
   }
 | DescribeOrDesc OptionalTable OptionalExtended SchemaQualifiedTableIdentifier PartitionSpec_EDIT OptionalColumnIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

OptionalColumnIdentifier
 :
 | ColumnIdentifier
 ;