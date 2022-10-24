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

DataManipulation
 : InsertOverwriteDirectory
 ;

DataManipulation_EDIT
 : InsertOverwriteDirectory_EDIT
 ;

InsertOverwriteDirectory
 : 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath OptionalSparkFormatOrHiveFormat ValuesClauseOrQuerySpecification
 ;

InsertOverwriteDirectory_EDIT
 : 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath_EDIT
 | 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath OptionalSparkFormatOrHiveFormat 'CURSOR'
   {
     var keywords = $4 && $4.suggestKeywords || [];
     keywords.push('SELECT');
     keywords.push('VALUES');
     parser.suggestKeywords(keywords);
   }
 | 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath SparkFormatOrHiveFormat_EDIT
 | 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath OptionalSparkFormatOrHiveFormat 'CURSOR' ValuesClauseOrQuerySpecification
   {
     parser.checkForKeywords($4);
   }
 | 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath SparkFormatOrHiveFormat_EDIT ValuesClauseOrQuerySpecification
 | 'INSERT' OptionalInsertOptions DirectoryWithOrWithoutPath OptionalSparkFormatOrHiveFormat ValuesClauseOrQuerySpecification_EDIT
 ;

DirectoryWithOrWithoutPath
 : 'DIRECTORY_PATH' DirectoryHdfsPathRight
 | 'DIRECTORY'
 ;

DirectoryWithOrWithoutPath_EDIT
 : 'DIRECTORY_PATH' DirectoryHdfsPathRight_EDIT
   {
     parser.suggestHdfs($2);
   }
 ;

OptionalSparkFormatOrHiveFormat
 : OptionalRowFormat OptionalStoredAs
   {
     if (!$1 && !$2) {
       $$ = { suggestKeywords: ['ROW FORMAT', 'STORED AS', 'USING'] }
     } else if ($1 && !$2) {
       if ($1.suggestKeywords) {
         $1.suggestKeywords.push('STORED AS');
       } else {
         $$ = { suggestKeywords: ['STORED AS'] }
       }
     }
   }
 | 'USING' DataSource OptionalOptions
   {
     if (!$3) {
       $$ = { suggestKeywords: ['OPTIONS'] }
     }
   }
 ;

SparkFormatOrHiveFormat_EDIT
 : RowFormat_EDIT OptionalStoredAs
 | OptionalRowFormat StoredAs_EDIT
 | 'USING' 'CURSOR'
   {
     parser.suggestKeywords(parser.getDataSourceKeywords());
   }
 ;

OptionalLocal
 :
 | 'LOCAL'
 ;

OptionalHdfsPath
 :
 | PushHdfsLexerState HdfsPath PopLexerState
 ;

DirectoryHdfsPathRight
 : 'HDFS_PATH' 'HDFS_END_QUOTE'
 ;

DirectoryHdfsPathRight_EDIT
 : 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_PATH' 'HDFS_END_QUOTE' -> { path: $1 }
 | 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'             -> { path: $1 }
 | 'HDFS_PATH' 'PARTIAL_CURSOR'                              -> { path: $1 }
 | 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'                         -> { path: '' }
 | 'PARTIAL_CURSOR'                                          -> { path: '' }
 ;
