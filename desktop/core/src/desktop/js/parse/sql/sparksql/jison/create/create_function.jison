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
 : CreateFunction
 ;

DataDefinition_EDIT
 : CreateFunction_EDIT
 ;

CreateFunction
 : 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' OptionalIfNotExists ColumnOrArbitraryFunctionRef 'AS' QuotedValue OptionalResourceLocation
 ;

CreateFunction_EDIT
 : 'CREATE' OptionalOrReplace OptionalTemporary 'CURSOR' 'FUNCTION'
   {
     if (!$3 && !$2) {
       parser.suggestKeywords([{ value: 'OR REPLACE', weight: 2 }, { value: 'TEMPORARY', weight: 1 }])
     } else if (!$3 && $2) {
       parser.suggestKeywords(['TEMPORARY']);
     }
   }
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$5) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' IfNotExists_EDIT
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' OptionalIfNotExists ColumnOrArbitraryFunctionRef 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' OptionalIfNotExists ColumnOrArbitraryFunctionRef 'AS' QuotedValue OptionalResourceLocation 'CURSOR'
   {
     if (!$9) {
       parser.suggestKeywords(['USING']);
     }
   }
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' OptionalIfNotExists ColumnOrArbitraryFunctionRef 'AS' QuotedValue ResourceLocation_EDIT
 | 'CREATE' OptionalOrReplace OptionalTemporary 'CURSOR' 'FUNCTION' OptionalIfNotExists ColumnOrArbitraryFunctionRef 'AS' QuotedValue OptionalResourceLocation
   {
     if (!$3 && !$2) {
       parser.suggestKeywords([{ value: 'OR REPLACE', weight: 2 }, { value: 'TEMPORARY', weight: 1 }])
     } else if (!$3 && $2) {
       parser.suggestKeywords(['TEMPORARY']);
     }
   }
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' OptionalIfNotExists 'CURSOR' ColumnOrArbitraryFunctionRef 'AS' QuotedValue OptionalResourceLocation
   {
     if (!$5) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' OrReplace_EDIT OptionalTemporary 'FUNCTION' OptionalIfNotExists ColumnOrArbitraryFunctionRef 'AS' QuotedValue OptionalResourceLocation
 | 'CREATE' OptionalOrReplace OptionalTemporary 'FUNCTION' IfNotExists_EDIT ColumnOrArbitraryFunctionRef 'AS' QuotedValue OptionalResourceLocation
 ;

OptionalResourceLocation
 :
 | ResourceLocation
 ;

ResourceLocation
 : 'USING' JarFileOrArchive QuotedValue
 ;

ResourceLocation_EDIT
 : 'USING' 'CURSOR'
   {
     parser.suggestKeywords(['ARCHIVE', 'FILE', 'JAR']);
   }
 ;

JarFileOrArchive
 : 'ARCHIVE'
 | 'FILE'
 | 'JAR'
 ;