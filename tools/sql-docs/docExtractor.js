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

const program = require('commander');

const extractorUtils = require('./extractorUtils');
const ditamapParser = require('./ditamapParser');
const docXmlParser = require('./docXmlParser');
const topicLinker = require('./topicLinker');
const jsonHandler = require('./jsonHandler');

const LOG_NAME = 'docExtractor.js';

// Handle command line arguments
program
  .version('1.0')
  .option('-f, --folder [path]', 'the folder where the ditamap file(s) reside (required)')
  .option('-d, --ditamap [path]', 'comma-separated ditamap file names, the first will define the topic ' +
    'tree (at least one file is required). Note that there should be no whitespace around the \',\'')
  .option('-o, --output [path]', 'output folder where the json files will be written to (required)')
  .option('-c, --cssClassPrefix [prefix]', 'optional css class prefix')
  .option('-m, --mako [path]', 'optional path to a .mako file where the index is written, ' +
    'used for django if the output folder is a static resource')
  .parse(process.argv);

extractorUtils.checkArguments(program);

const ensureTrailingSlash = (path) => {
  if (!path.endsWith('/')) {
    return path + '/';
  }
  return path;
};

let ditamapFiles = program.ditamap.split(',').map(file => file.trim());

console.log('%s: Parsing ditamap file(s)...', LOG_NAME);
let ditamapParsePromises = ditamapFiles.map(ditamapFile => ditamapParser.parseDitamap(ditamapFile, ensureTrailingSlash(program.folder)));

Promise.all(ditamapParsePromises).then((parseResults) => {
  let cssClassPrefix = program.cssClassPrefix || '';
  if (cssClassPrefix && !/-$/.test(cssClassPrefix)) {
    cssClassPrefix += '-';
  }

  console.log('%s: Parsing topics...', LOG_NAME);
  docXmlParser.parseTopics(parseResults, cssClassPrefix).then(() => {
    console.log('%s: Linking topics...', LOG_NAME);
    topicLinker.linkTopics(parseResults, cssClassPrefix);

    console.log('%s: Saving topic tree json files...', LOG_NAME);
    jsonHandler.saveTopics(parseResults[0].topics, ensureTrailingSlash(program.output), program.mako).then((savedFiles) => {
      console.log('%s: Done! Saved %d files.', LOG_NAME, savedFiles.length);
    }).catch(err => {
      console.log('%s: Failed saving files!', LOG_NAME);
      console.log(err);
    });
  });
});

