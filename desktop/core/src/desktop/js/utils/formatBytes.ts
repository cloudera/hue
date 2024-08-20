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

const formatBytes = (bytes?: number, decimalPoints: number = 2): string => {
  if (bytes === -1 || bytes == undefined) {
    return 'Not available';
  }
  if (bytes === 0) {
    return '0 Byte';
  }
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const dm = i === 0 ? 0 : decimalPoints; // Don't show decimal points for Bytes
  return (bytes / Math.pow(k, i)).toFixed(dm) + ' ' + sizes[i];
};

export default formatBytes;
