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
 : DatabaseDefinition
 ;

DataDefinition_EDIT
 : DatabaseDefinition_EDIT
 ;

DatabaseDefinition
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinition_EDIT
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists_EDIT
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.addNewDatabaseLocation(@5, [{ name: $5 }]);
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 ;

DatabaseDefinitionOptionals
 : OptionalComment OptionalHdfsLocation
   {
     var keywords = [];
     if (!$2) {
       keywords.push('LOCATION');
     }
     if (!$1 && !$2) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment_INVALID OptionalHdfsLocation
 | OptionalComment HdfsLocation_EDIT
 ;
