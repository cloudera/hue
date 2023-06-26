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

Auxiliary_EDIT
 : 'ADD' 'CURSOR'
   {
     parser.suggestKeywords(['ARCHIVE', 'ARCHIVES', 'FILE', 'FILES', 'JAR', 'JARS']);
   }
 ;

FilePaths
 : FilePath
 | FilePaths 'WHITESPACE' FilePath
 ;

FilePaths_EDIT
 : FilePath_EDIT
 | FilePaths 'WHITESPACE' FilePath_EDIT
 ;

FilePath
 : 'FILE_QUOTE' FilePathWithWhitespace 'FILE_QUOTE'
 | 'FILE_PATH'
 ;

FilePath_EDIT
 : 'FILE_QUOTE' AnyCursor
   {
     parser.suggestHdfs({ path: '' });
   }
 | 'FILE_QUOTE' FilePathWithWhitespace AnyCursor
   {
     parser.suggestHdfs({ path: $2 });
   }
 | 'FILE_PATH' 'PARTIAL_CURSOR'
   {
     parser.suggestHdfs({ path: $1 });
   }
 ;

FilePathWithWhitespace
 : 'FILE_PATH'
 | FilePathWithWhitespace 'WHITESPACE' 'FILE_PATH' -> $1 + $2 + $3
 ;