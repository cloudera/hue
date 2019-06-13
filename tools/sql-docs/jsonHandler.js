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

const fs = require('fs');
const mkdirp = require('mkdirp');
const path = require('path');

const LOG_NAME = 'jsonHandler.js';

/**
 * Saves the topics to json files in the given outputPath folder
 *
 * @param {Topic[]} topics
 * @param {string} outputPath
 * @param {string} [makoPath] - If set it will add the index and topic tree to this file
 * @return {Promise}
 */
const saveTopics = (topics, outputPath, makoPath) => {
  let index = {};
  let topLevel = [];
  let savePromises = [];

  let saveTopicsInternal = (topics, parent) => {
    topics.forEach(topic => {
      let entry = {
        title: topic.fragment.title.text().replace(/[\n\r]/g, '').trim(),
        ref: topic.ref,
        children: []
      };
      if (!parent) {
        topLevel.push(entry)
      } else {
        parent.children.push(entry);
      }

      let fileName = topic.ref.replace('.xml', '.json');
      index[topic.ref] = fileName;

      let filePath = outputPath + fileName;
      savePromises.push(new Promise((resolve, reject) => {
        mkdirp(path.dirname(filePath), err => {
          if (!err) {
            fs.writeFile(filePath, topic.toJson(), err => {
              if (err) {
                reject(err);
              } else {
                resolve();
              }
            });
          } else {
            reject(err);
          }
        });
      }));
      saveTopicsInternal(topic.children, entry);
    });
  };

  saveTopicsInternal(topics);

  if (makoPath) {
    savePromises.push(new Promise((resolve, reject) => {
      fs.readFile(makoPath, 'utf-8', (err, contents) => {
        if (err) {
          reject(err);
          return;
        }
        let indexStrings = [];
        Object.keys(index).forEach(key => {
          indexStrings.push('\'' + key + '\':\'${ static(\'desktop/docs/impala/' + index[key] + '\') }\'')
        });
        contents = contents.replace(/window\.IMPALA_DOC_INDEX.*\n/, 'window.IMPALA_DOC_INDEX = {' + indexStrings.join(',') + '};\n');

        let createTopicJs = (entry) => {
          return '{title:\'' + entry.title +'\',ref:\'' + entry.ref + '\',children:[' + entry.children.map(createTopicJs).join(',') + ']}';
        };

        contents = contents.replace(/window\.IMPALA_DOC_TOP_LEVEL.*\n/, 'window.IMPALA_DOC_TOP_LEVEL = [' + topLevel.map(createTopicJs).join(',') + '];\n');
        fs.writeFile(makoPath.replace('.template', ''), contents, (err) => {
          if (err) {
            reject(err);
            return;
          }
          console.log('%s: %s written.', LOG_NAME, makoPath.replace('.template', ''));
          resolve();
        })
      });
    }));
  }

  return Promise.all(savePromises);
};

module.exports = {
  saveTopics: saveTopics
};
