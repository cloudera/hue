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

const libxml = require('libxmljs');

/**
 * Class representing a doc topic
 */
class Topic {

  /**
   * Create a topic
   *
   * @param {string} docRootPath - The start path
   * @param {string} ref - The relative path of the topic
   */
  constructor (docRootPath, ref) {
    this.docRootPath = docRootPath;
    this.ref = ref;
    this.children = [];

    // These are set during parsing
    this.fragment = undefined;
    this.domXml = new libxml.Document().node('div');
  }

  toJson() {
    return JSON.stringify({
      body: this.domXml.toString(),
      title: this.fragment.title.text().replace(/[\n\r]/g, ' ').trim()
    });
  }
}

module.exports = Topic;