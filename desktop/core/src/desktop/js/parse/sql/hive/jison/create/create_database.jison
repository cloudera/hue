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
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 | 'CREATE_REMOTE' DatabaseOrSchema RegularIdentifier 'USING' RegularIdentifier OptionalDbProperties
   {
     parser.addNewDatabaseLocation(@3, [{ name: $3 }]);
   }
 ;

CreateDatabase_EDIT
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
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT
 | 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     parser.addNewDatabaseLocation(@4, [{ name: $4 }]);
   }
 | 'CREATE_REMOTE' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE']);
   }
 | 'CREATE_REMOTE' DatabaseOrSchema RegularIdentifier 'CURSOR'
   {
     parser.addNewDatabaseLocation(@3, [{ name: $3 }]);
     parser.suggestKeywords(['USING']);
   }
 | 'CREATE_REMOTE' DatabaseOrSchema RegularIdentifier 'USING' RegularIdentifier OptionalDbProperties 'CURSOR'
   {
     parser.addNewDatabaseLocation(@3, [{ name: $3 }]);
     parser.suggestKeywords(['WITH DBPROPERTIES']);
   }
 | 'CREATE_REMOTE' DatabaseOrSchema RegularIdentifier 'USING' RegularIdentifier DbProperties_EDIT
   {
     parser.addNewDatabaseLocation(@3, [{ name: $3 }]);
   }
 ;

DatabaseDefinitionOptionals
 : OptionalComment OptionalHdfsLocation OptionalManagedLocation OptionalDbProperties
   {
     var keywords = [];
     if (!$4) {
       keywords.push('WITH DBPROPERTIES');
     }
     if (!$3 && !$4) {
       keywords.push('MANAGEDLOCATION');
     }
     if (!$2 && !$3 && !$4) {
       keywords.push('LOCATION');
     }
     if (!$1 && !$2 && !$3 && !$4) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : Comment_INVALID OptionalHdfsLocation OptionalManagedLocation OptionalDbProperties
 | OptionalComment HdfsLocation_EDIT OptionalManagedLocation OptionalDbProperties
 | OptionalComment OptionalHdfsLocation ManagedLocation_EDIT OptionalDbProperties
 | OptionalComment OptionalHdfsLocation OptionalManagedLocation DbProperties_EDIT
 ;

Comment_INVALID
 : 'COMMENT' SINGLE_QUOTE
 | 'COMMENT' DOUBLE_QUOTE
 | 'COMMENT' SINGLE_QUOTE VALUE
 | 'COMMENT' DOUBLE_QUOTE VALUE
 ;

OptionalManagedLocation
 :
 | ManagedLocation
 ;

ManagedLocation
 : 'MANAGEDLOCATION' HdfsPath
 ;

ManagedLocation_EDIT
 : 'MANAGEDLOCATION' HdfsPath_EDIT
 ;

OptionalDbProperties
 :
 | DbProperties
 ;

DbProperties
 : 'WITH' 'DBPROPERTIES' ParenthesizedPropertyAssignmentList
 | 'WITH' 'DBPROPERTIES'
 ;

DbProperties_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DBPROPERTIES']);
   }
 ;
