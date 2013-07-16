/*
 Licensed to Cloudera, Inc. under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  Cloudera, Inc. licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

/**
 * ID Generator
 * Generate a new ID starting from 1.
 * - Accepts a prefix that will be prepended like so: <prefix>:<id number>
 */
var IdGeneratorModule = function($) {
  return function(options) {
    var self = this;
    $.extend(self, options);

    self.counter = 1;

    self.nextId = function() {
      return ((self.prefix) ? self.prefix + ':' : '') + self.counter++;
    };
  };
};
var IdGenerator = IdGeneratorModule($);

var IdGeneratorTable = {
  mapreduce: new IdGenerator({prefix: 'mapreduce'}),
  streaming: new IdGenerator({prefix: 'streaming'}),
  java: new IdGenerator({prefix: 'java'}),
  pig: new IdGenerator({prefix: 'pig'}),
  hive: new IdGenerator({prefix: 'hive'}),
  sqoop: new IdGenerator({prefix: 'sqoop'}),
  shell: new IdGenerator({prefix: 'shell'}),
  ssh: new IdGenerator({prefix: 'ssh'}),
  distcp: new IdGenerator({prefix: 'distcp'}),
  fs: new IdGenerator({prefix: 'fs'}),
  email: new IdGenerator({prefix: 'email'}),
  subworkflow: new IdGenerator({prefix: 'subworkflow'}),
  generic: new IdGenerator({prefix: 'generic'}),
  fork: new IdGenerator({prefix: 'fork'}),
  decision: new IdGenerator({prefix: 'decision'}),
  join: new IdGenerator({prefix: 'join'}),
  decisionend: new IdGenerator({prefix: 'decisionend'}),
  kill: new IdGenerator({prefix: 'kill'})
};
