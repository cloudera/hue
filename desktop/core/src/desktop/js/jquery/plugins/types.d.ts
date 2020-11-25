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

interface JQuery {
  jHueFileChooser(options: {
    suppressErrors: boolean;
    selectFolder: boolean;
    createFolder: boolean;
    uploadFile: boolean;
    initialPath: string;
    errorRedirectPath: string;
    forceRefresh: boolean;
    showExtraHome: boolean;
    extraHomeProperties: { [prop: string]: string };
    filterExtensions: string;
    displayOnlyFolders: boolean;
    onFolderChoose(path: string): void;
    onFileChoose(path: string): void;
  }): JQuery;
  modal(options?: string): JQuery;
}
