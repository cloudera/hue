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
 : AggregateFunctionDefinition
 ;

DataDefinition_EDIT
 : AggregateFunctionDefinition_EDIT
 ;

AggregateFunctionDefinition
 : 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 ;

AggregateFunctionDefinition_EDIT
 : 'CREATE' 'AGGREGATE' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF NOT EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists_EDIT SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList 'CURSOR'
   {
     parser.suggestKeywords(['RETURNS']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   'CURSOR'
   {
     parser.suggestKeywords(['LOCATION']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn 'CURSOR'
   {
     if (!$9) {
       parser.suggestKeywords([{value: 'INIT_FN', weight: 2 }, {value: 'UPDATE_FN', weight: 1 }]);
     } else {
       parser.suggestKeywords([{value: 'UPDATE_FN', weight: 1 }]);
     }
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn 'CURSOR'
   {
     parser.suggestKeywords(['MERGE_FN']);
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate 'CURSOR'
   {
     if (!$12 && !$13 && !$14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'PREPARE_FN', weight: 5 }, {value: 'CLOSE_FN', weight: 4 }, {value: 'SERIALIZE_FN', weight: 3 }, {value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($12 && !$13 && !$14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'CLOSE_FN', weight: 4 }, {value: 'SERIALIZE_FN', weight: 3 }, {value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($13 && !$14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'SERIALIZE_FN', weight: 3 }, {value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($14 && !$15 && !$16) {
       parser.suggestKeywords([{value: 'FINALIZE_FN', weight: 2 }, {value: 'INTERMEDIATE', weight: 1 }]);
     } else if ($15 && !$16) {
       parser.suggestKeywords([{value: 'INTERMEDIATE', weight: 1 }]);
     }
   }
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation_EDIT OptionalInitFn
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn_EDIT OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn_EDIT OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn_EDIT  OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn_EDIT OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn_EDIT OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn Intermediate_EDIT
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType_EDIT
   HdfsLocation OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation_EDIT OptionalInitFn UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn_EDIT UpdateFn MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 | 'CREATE' 'AGGREGATE' 'FUNCTION' OptionalIfNotExists SchemaQualifiedIdentifier ParenthesizedArgumentList ReturnType
   HdfsLocation OptionalInitFn UpdateFn_EDIT MergeFn OptionalPrepareFn OptionalCloseFn OptionalSerializeFn OptionalFinalizeFn OptionalIntermediate
 ;

OptionalInitFn
 :
 | 'INIT_FN' '=' FunctionReference
 ;

OptionalInitFn_EDIT
 : 'INIT_FN' '=' FunctionReference_EDIT
 ;

UpdateFn
 : 'UPDATE_FN' '=' FunctionReference
 ;

UpdateFn_EDIT
 : 'UPDATE_FN' '=' FunctionReference_EDIT
 ;

MergeFn
 : 'MERGE_FN' '=' FunctionReference
 ;

MergeFn_EDIT
 : 'MERGE_FN' '=' FunctionReference_EDIT
 ;

OptionalPrepareFn
 :
 | 'PREPARE_FN' '=' FunctionReference
 ;

OptionalPrepareFn_EDIT
 : 'PREPARE_FN' '=' FunctionReference_EDIT
 ;

OptionalCloseFn
 :
 | 'CLOSE_FN' '=' FunctionReference
 ;

OptionalCloseFn_EDIT
 : 'CLOSE_FN' '=' FunctionReference_EDIT
 ;

OptionalSerializeFn
 :
 | 'SERIALIZE_FN' '=' FunctionReference
 ;

OptionalSerializeFn_EDIT
 : 'SERIALIZE_FN' '=' FunctionReference_EDIT
 ;

OptionalFinalizeFn
 :
 | 'FINALIZE_FN' '=' FunctionReference
 ;

OptionalFinalizeFn_EDIT
 : 'FINALIZE_FN' '=' FunctionReference_EDIT
 ;

OptionalIntermediate
 :
 | 'INTERMEDIATE' PrimitiveType
 ;

Intermediate_EDIT
 : 'INTERMEDIATE' 'CURSOR'
   {
     parser.suggestKeywords(parser.getTypeKeywords());
   }
 ;

FunctionReference
 : SingleQuotedValue
 ;

FunctionReference_EDIT
 : SingleQuotedValue_EDIT
   {
     parser.suggestFunctions();
     parser.suggestAggregateFunctions();
     parser.suggestAnalyticFunctions();
   }
 ;
