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
const util = require('util');

const LOG_NAME = 'extractorUtils.js';

/**
 * Utility function to read a text file using UTF-8 encoding
 *
 * @param {string} path
 * @return {Promise} - A promise, fulfilled with the file contents or rejected
 */
const readFile = path => new Promise((resolve, reject) => {
  fs.readFile(path, 'utf8', (err, contents) => {
    if (err) {
      console.log('%s: Could not read file \'%s\'', LOG_NAME, path);
      console.log(err);
      reject(err)
    } else {
      resolve(contents);
    }
  })
});

/**
 * Returns the parent folder of a file path
 *
 * @param {string} path
 * @return {string}
 */
const getParentFolder = path => path.substring(0, path.lastIndexOf('/') + 1);

/**
 * Checks arguments given on the command line, breaks the program if required ones are missing.
 *
 * @param {Object} program - See command lib
 */
const checkArguments = program => {
  if (!program.folder) {
    console.log('\n  No folder supplied!');
    program.help();
  }

  if (!program.ditamap) {
    console.log('\n  No ditamap file supplied!');
    program.help();
  }

  if (!program.output) {
    console.log('\n  No output path supplied!');
    program.help();
  }
};

/**
 * Helper method to check if a node has attributes that aren't empty
 *
 * @param node
 * @param {string|string[]} attributes
 * @return {boolean}
 */
const hasAttributes = (node, attributes) => {
  if (typeof attributes === 'string') {
    attributes = [attributes];
  }
  return attributes.every(attribute => node.attr(attribute) && node.attr(attribute).value().trim())
};

/**
 * Helper method to remove all attributes of a noce
 *
 * @param node
 */
const removeAllAttributes = node => {
  node.attrs().forEach(attr => {
    attr.remove();
  })
};

/**
 * Helper method to find a fragment with specified anchorId within a topic. If the anchor ID isn't found it will return
 * the closes possible parent.
 *
 * @param topic
 * @param anchorId
 * @return {[DocFragment]}
 */
const findFragmentInTopic = (topic, anchorId) => {
  if (!anchorId) {
    return topic.fragment;
  }
  let splitIds = anchorId.split('/');

  let findDeep = (fragments, id) => {
    let foundFragment = undefined;
    fragments.some(fragment => {
      if (fragment.id === id) {
        foundFragment = fragment;
        return true;
      }
      foundFragment = findDeep(fragment.children, id);
      return foundFragment;
    });
    return foundFragment;
  };

  let fragmentsToSearch = [ topic.fragment ];

  let result = undefined;
  while (splitIds.length) {
    result = findDeep(fragmentsToSearch, splitIds.shift());
    if (!result) {
      break;
    }
    fragmentsToSearch = result.children;
  }
  if (!result) {
    console.log('%s: Could not find id \'%s\' in ref \'%s\'', LOG_NAME, anchorId, topic.ref);
    return topic.fragment;
  }
  return result;
};

/**
 * @typedef {Object} FragmentSearchResult
 * @property {boolean} partOfTree - Whether or not the found fragment is part of the main tree
 * @property {DocFragment} [fragment]
 */

/**
 *
 * @param {DitamapParseResult[]} parseResults
 * @param {string} ref
 * @param {string} [anchorId]
 * @return {FragmentSearchResult}
 */
const findFragment = (parseResults, ref, anchorId) => {
  let result = { partOfTree: true, fragment: undefined };
  parseResults.some(parseResult => {
    let topic = parseResult.topicIndex[ref];
    if (topic) {
      result.fragment = findFragmentInTopic(topic, anchorId);
    } else {
      result.partOfTree = false;
    }
    return result.fragment;
  });
  return result;
};

module.exports = {
  readFile: readFile,
  getParentFolder: getParentFolder,
  checkArguments: checkArguments,
  hasAttributes: hasAttributes,
  removeAllAttributes: removeAllAttributes,
  findFragment: findFragment
};