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

/* eslint-disable no-restricted-syntax */

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
const saveTopics = (topics, outputPath, makoPath, isImpala) => {
  const index = {};
  const topLevel = [];
  const savePromises = [];

  const saveTopicsInternal = (topics, parent) => {
    topics.forEach(topic => {
      const entry = {
        title: topic.fragment.title
          .text()
          .replace(/[\n\r]/g, '')
          .trim(),
        ref: topic.ref,
        children: []
      };
      if (!parent) {
        topLevel.push(entry);
      } else {
        parent.children.push(entry);
      }

      let fileName = topic.ref.replace('.xml', '.json');
      if (fileName.indexOf('.json') === -1) {
        fileName += '.json';
      }
      index[topic.ref] = fileName;

      const filePath = outputPath + fileName;
      savePromises.push(
        new Promise((resolve, reject) => {
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
        })
      );
      saveTopicsInternal(topic.children, entry);
    });
  };

  saveTopicsInternal(topics);

  const indexTypes = {
    impala: {
      staticPrefix: "':'${ static('desktop/docs/impala/",
      docIndexRegex: /window\.IMPALA_DOC_INDEX.*\n/,
      docIndexPrefix: 'window.IMPALA_DOC_INDEX = {',
      topLevelRegex: /window\.IMPALA_DOC_TOP_LEVEL.*\n/,
      topLevelPrefix: 'window.IMPALA_DOC_TOP_LEVEL = ['
    },
    hive: {
      staticPrefix: "':'${ static('desktop/docs/hive/",
      docIndexRegex: /window\.HIVE_DOC_INDEX.*\n/,
      docIndexPrefix: 'window.HIVE_DOC_INDEX = {',
      topLevelRegex: /window\.HIVE_DOC_TOP_LEVEL.*\n/,
      topLevelPrefix: 'window.HIVE_DOC_TOP_LEVEL = ['
    }
  };

  if (makoPath) {
    const indexType = isImpala ? indexTypes.impala : indexTypes.hive;
    savePromises.push(
      new Promise((resolve, reject) => {
        fs.readFile(makoPath, 'utf-8', (err, contents) => {
          if (err) {
            reject(err);
            return;
          }
          const indexStrings = [];
          Object.keys(index).forEach(key => {
            indexStrings.push("'" + key + indexType.staticPrefix + index[key] + "') }'");
          });
          contents = contents.replace(
            indexType.docIndexRegex,
            indexType.docIndexPrefix + indexStrings.join(',') + '};\n'
          );

          const createTopicJs = entry => {
            return (
              "{title:'" +
              entry.title +
              "',ref:'" +
              entry.ref +
              "',children:[" +
              entry.children.map(createTopicJs).join(',') +
              ']}'
            );
          };

          contents = contents.replace(
            indexType.topLevelRegex,
            indexType.topLevelPrefix + topLevel.map(createTopicJs).join(',') + '];\n'
          );
          fs.writeFile(makoPath.replace('.template', ''), contents, err => {
            if (err) {
              reject(err);
              return;
            }
            console.log('%s: %s written.', LOG_NAME, makoPath.replace('.template', ''));
            resolve();
          });
        });
      })
    );
  }

  return Promise.all(savePromises);
};

module.exports = {
  saveTopics: saveTopics
};

/* eslint-enable no-restricted-syntax */
