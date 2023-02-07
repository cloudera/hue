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
 : CreateDatabase
 ;

DataDefinition_EDIT
 : CreateDatabase_EDIT
 ;

CreateDatabase
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularOrBacktickedIdentifier OptionalComment OptionalLocation OptionalWithDbProperties
 ;

CreateDatabase_EDIT
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' DatabaseOrSchema IfNotExists_EDIT
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularOrBacktickedIdentifier OptionalComment OptionalLocation OptionalWithDbProperties
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' DatabaseOrSchema IfNotExists_EDIT RegularOrBacktickedIdentifier OptionalComment OptionalLocation OptionalWithDbProperties
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularOrBacktickedIdentifier 'CURSOR' OptionalComment OptionalLocation OptionalWithDbProperties
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$6, $7, $8],
       [{ value: 'COMMENT', weight: 3 }, { value: 'LOCATION', weight: 2 }, { value: 'WITH DBPROPERTIES', weight: 1 }],
       [true, true, true]);
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularOrBacktickedIdentifier Comment 'CURSOR' OptionalLocation OptionalWithDbProperties
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$7, $8],
       [{ value: 'LOCATION', weight: 2 }, { value: 'WITH DBPROPERTIES', weight: 1 }],
       [true, true]);
     if (keywords.length) {
       parser.suggestKeywords(keywords);
     }
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularOrBacktickedIdentifier OptionalComment Location 'CURSOR' OptionalWithDbProperties
   {
     if (!$8) {
       parser.suggestKeywords(["WITH DBPROPERTIES"]);
     }
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularOrBacktickedIdentifier OptionalComment OptionalLocation WithDbProperties_EDIT
 ;

OptionalLocation
 :
 | Location
 ;

Location
 : 'LOCATION' QuotedValue
 ;

OptionalWithDbProperties
 :
 | WithDbProperties
 ;

WithDbProperties
 : 'WITH' 'DBPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

WithDbProperties_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DBPROPERTIES']);
   }
 ;