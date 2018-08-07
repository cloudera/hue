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

const Topic = require('./Topic');
const extractorUtils = require('./extractorUtils');

const LOG_NAME = 'ditamapParser.js: ';

/**
 * @typedef {Object} KeyDef
 * @property {string} [text]
 * @property {string} [href]
 * @property {boolean} [external]
 */

/**
 * @typedef {Object} DitamapParseResult
 * @property {Topic[]} topics - The topic tree
 * @property {Object} topicIndex - Key value pairs of all topics ('ref': Topic)
 * @property {Object.<string, KeyDef>} keyDefs - Key value pairs of key definitions, i.e. { 'impala23': { text: 'Impala 2.3' } }
 */

/**
 * Extracts topics from a given ditamap file
 *
 * @param {string} ditamapFile
 * @param {string} docRootPath - The root path of the documents
 *
 * @return {Promise<DitamapParseResult>} - A promise of the Topic tree and index
 */
const parseDitamap = (ditamapFile, docRootPath) => new Promise((resolve, reject) => {
  let parseResult = {
    topics: [],
    topicIndex: {},
    keyDefs: {}
  };
  extractFromDitamapFile(ditamapFile, docRootPath, parseResult).then(() => {
    resolve(parseResult);
  }).catch(reject);
});

const extractFromDitamapFile = (ditamapFile, docRootPath, parseResult) => new Promise((resolve, reject) => {
  extractorUtils.readFile(docRootPath + ditamapFile).then(contents => {
    let mapNode = libxml.parseXmlString(contents).get('//map');
    extractFromMapNode(mapNode, ditamapFile, docRootPath, parseResult).then(resolve).catch(reject);
  }).catch(reject);
});

const extractFromMapNode = (mapNode, ditamapFile, docRootPath, parseResult) => {
  let promises = [];

  let handleMapNodeChildren = (childNodes, currentTopic) => {
    childNodes.forEach(node => {
      switch (node.name()) {
        case 'topicref': {
          if (extractorUtils.hasAttributes(node, 'href')) {
            if (~node.attr('href').value().indexOf('.ditamap')) {
              promises.push(extractFromDitamapFile(node.attr('href').value(), docRootPath, parseResult));
              break;
            }
            let topic = new Topic(docRootPath, node.attr('href').value());
            if (currentTopic) {
              currentTopic.children.push(topic);
            } else {
              parseResult.topics.push(topic);
            }
            parseResult.topicIndex[node.attr('href').value().replace(/#.*$/, '')] = topic;
            handleMapNodeChildren(node.childNodes(), topic);
          } else {
            console.log('%s: Couldn\'t handle "topicref" node: %s in file %s%s', LOG_NAME,  node.toString(), docRootPath, ditamapFile);
          }
          break;
        }
        case 'mapref': {
          if (extractorUtils.hasAttributes(node, 'href')) {
            promises.push(extractFromDitamapFile(node.attr('href').value(), docRootPath, parseResult));
          } else {
            console.log('%s: Couldn\'t handle "mapref" node: \n%s in file %s%s', LOG_NAME,  node.toString(), docRootPath, ditamapFile);
          }
          break;
        }
        case 'keydef':
          if (extractorUtils.hasAttributes(node, 'keys')) {
            let valNode = node.get('topicmeta/keywords/keyword');
            if (valNode) {
              parseResult.keyDefs[node.attr('keys').value()] = { text: valNode.text() };
            } else if (node.attr('href')) {
              if (!node.attr('href').value() && node.text().trim()) {
                parseResult.keyDefs[node.attr('keys').value()] = { text: node.text() };
              } else {
                parseResult.keyDefs[node.attr('keys').value()] = {
                  href: node.attr('href').value(),
                  external: node.attr('scope') && node.attr('scope').value() === 'external'
                }
              }
            }
          }
        case 'comment':
        case 'text':
        case 'title':
        case 'topichead':
        case 'topicmeta':
          break;
        default:
          console.log('%s: Couldn\'t handle map node: \n%s in file %s%s', LOG_NAME,  node.toString(), docRootPath, ditamapFile);
      }
    })
  };

  handleMapNodeChildren(mapNode.childNodes());

  return Promise.all(promises);
};

module.exports = {
  parseDitamap: parseDitamap
};