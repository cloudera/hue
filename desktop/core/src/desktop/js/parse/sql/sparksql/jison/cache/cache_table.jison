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
 : CacheTable
 ;

Auxiliary_EDIT
 : CacheTable_EDIT
 ;

CacheTable
 : 'CACHE' LazyTableOrTable SchemaQualifiedTableIdentifier OptionalCacheOptions OptionalCacheQuerySpecification
   {
     parser.addTablePrimary($3);
   }
 ;

CacheTable_EDIT
 : 'CACHE' LazyTable_EDIT
 | 'CACHE' LazyTableOrTable 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'CACHE' LazyTableOrTable SchemaQualifiedTableIdentifier_EDIT
 | 'CACHE' LazyTableOrTable SchemaQualifiedTableIdentifier OptionalCacheOptions 'CURSOR' OptionalCacheQuerySpecification
   {
     if (!$4 && !$6) {
       parser.suggestKeywords([{ value: 'OPTIONS', weight: 2 }, { value: 'AS SELECT', weight: 1 }, { value: 'SELECT', weight: 1 }]);
     } else if (!$4) {
       parser.suggestKeywords(['OPTIONS']);
     } else {
       parser.suggestKeywords(['AS SELECT', 'SELECT']);
     }
   }
 | 'CACHE' LazyTableOrTable SchemaQualifiedTableIdentifier CacheOptions_EDIT OptionalCacheQuerySpecification
 | 'CACHE' LazyTableOrTable SchemaQualifiedTableIdentifier OptionalCacheOptions CacheQuerySpecification_EDIT
 ;

LazyTableOrTable
 : 'LAZY' 'TABLE'
 | 'TABLE'
 ;

LazyTable_EDIT
 : 'LAZY' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 ;

OptionalCacheOptions
 :
 | CacheOptions
 ;

CacheOptions
 : 'OPTIONS' '(' QuotedValue OptionalEquals QuotedValue ')'
 ;

CacheOptions_EDIT
 : 'OPTIONS' '(' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(["'storageLevel'"]);
   }
 | 'OPTIONS' '(' QuotedValue OptionalEquals 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(["'NONE'", "'DISK_ONLY'", "'DISK_ONLY_2'", "'DISK_ONLY_3'", "'MEMORY_ONLY'", 
       "'MEMORY_ONLY_2'", "'MEMORY_ONLY_SER'", "'MEMORY_ONLY_SER_2'", "'MEMORY_AND_DISK'", "'MEMORY_AND_DISK_2'", 
       "'MEMORY_AND_DISK_SER'", "'MEMORY_AND_DISK_SER_2'", "'OFF_HEAP'"]);
   }
 ;

OptionalEquals
 :
 | '='
 ;

OptionalCacheQuerySpecification
 :
 | CacheQuerySpecification
 ;

CacheQuerySpecification
 : 'AS' QuerySpecification
 | QuerySpecification
 ;

CacheQuerySpecification_EDIT
 : 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | 'AS' QuerySpecification_EDIT
 | QuerySpecification_EDIT
 ;