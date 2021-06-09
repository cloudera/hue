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

const bootstrapRatios = {
  span3(): number {
    if (window.innerWidth >= 1200) {
      return 23.07692308;
    } else if (window.innerWidth >= 768 && window.innerWidth <= 979) {
      return 22.9281768;
    } else {
      return 23.17073171;
    }
  },
  span9(): number {
    if (window.innerWidth >= 1200) {
      return 74.35897436;
    } else if (window.innerWidth >= 768 && window.innerWidth <= 979) {
      return 74.30939227;
    } else {
      return 74.3902439;
    }
  },
  margin(): number {
    return 2.56410256;
  }
};

export default bootstrapRatios;
