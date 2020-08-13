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

TableConstraint
 : TableConstraintLeftPart OptionalDisable OptionalNovalidate OptionalRelyOrNorely
 ;

TableConstraint_EDIT
 : TableConstraintLeftPart_EDIT OptionalDisable OptionalNovalidate OptionalRelyOrNorely
 | TableConstraintLeftPart OptionalDisable OptionalNovalidate OptionalRelyOrNorely 'CURSOR'
   {
     parser.suggestKeywordsForOptionalsLR([$4, $3, $2], [
       [{ value: 'RELY', weight: 1 }, { value: 'NORELY', weight: 1 }],
       { value: 'NOVALIDATE', weight: 2 },
       { value: 'DISABLE', weight: 3 }
     ]);
   }
 ;

TableConstraintLeftPart
 : 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification
 | 'CONSTRAINT' RegularOrBacktickedIdentifier 'CHECK' '(' ValueExpression ')'
 | 'CONSTRAINT' RegularOrBacktickedIdentifier 'UNIQUE' ParenthesizedColumnList
 ;

TableConstraintLeftPart_EDIT
 : 'CONSTRAINT' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['CHECK', 'FOREIGN KEY', 'UNIQUE']);
   }
 | 'CONSTRAINT' RegularOrBacktickedIdentifier ForeignKeySpecification_EDIT
 ;

ForeignKeySpecification
 : 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList
   {
     parser.addTablePrimary($5);
   }
 ;

ForeignKeySpecification_EDIT
 : 'FOREIGN' 'CURSOR'
   {
     parser.suggestKeywords(['KEY']);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList_EDIT
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'CURSOR'
   {
     parser.suggestKeywords(['REFERENCES']);
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier_EDIT
 | 'FOREIGN' 'KEY' ParenthesizedColumnList 'REFERENCES' SchemaQualifiedTableIdentifier ParenthesizedColumnList_EDIT
   {
     parser.addTablePrimary($5);
   }
 ;
