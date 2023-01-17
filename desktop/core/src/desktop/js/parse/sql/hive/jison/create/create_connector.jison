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
 : CreateConnector
 ;

DataDefinition_EDIT
 : CreateConnector_EDIT
 ;

CreateConnector
 : 'CREATE' 'CONNECTOR' OptionalIfNotExists RegularIdentifier OptionalType OptionalUrl OptionalComment
   OptionalWithDcproperties
 ;

CreateConnector_EDIT
 : 'CREATE' 'CONNECTOR' OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'CONNECTOR' OptionalIfNotExists_EDIT
 | 'CREATE' 'CONNECTOR' OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'CONNECTOR' OptionalIfNotExists_EDIT RegularIdentifier
 | 'CREATE' 'CONNECTOR' OptionalIfNotExists RegularIdentifier OptionalType OptionalUrl OptionalComment WithDcproperties_EDIT
 | 'CREATE' 'CONNECTOR' OptionalIfNotExists RegularIdentifier OptionalType OptionalUrl OptionalComment OptionalWithDcproperties 'CURSOR'
   {
     parser.suggestKeywordsForOptionalsLR([$8, $7, $6, $5], [
       { value: 'WITH DCPROPERTIES', weight: 1 },
       { value: 'COMMENT', weight: 2 },
       { value: 'URL', weight: 3 },
       { value: 'TYPE', weight: 4 }
     ]);
   }
 ;

OptionalType
 :
 | 'TYPE' QuotedValue
 ;

OptionalUrl
 :
 | 'URL' QuotedValue
 ;

OptionalWithDcproperties
 :
 | WithDcproperties
 ;

WithDcproperties
 : 'WITH' 'DCPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

WithDcproperties_EDIT
 : 'WITH' 'CURSOR'
   {
     parser.suggestKeywords(['DCPROPERTIES']);
   }
 ;