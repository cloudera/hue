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

const extractorUtils = require('./extractorUtils');
const EXTERNAL_DOC_URL_PREFIX = 'https://www.cloudera.com/documentation/enterprise/latest/';

const LOG_NAME = 'topicLinker.js';

/**
 * Creates an external link
 *
 * @param node
 * @param {string} href
 * @param {string} [cssClassPrefix]
 */
const replaceWithExternalLink = (node, href, cssClassPrefix) => {
  node.name('a');
  extractorUtils.removeAllAttributes(node);
  node.attr({ 'class': cssClassPrefix + 'doc-external-link', 'href': href, 'target': '_blank' });
};

/**
 * Creates an internal link if the the ref is part of the topic tree, otherwise it will create an external link.
 *
 * @param node
 * @param {string} ref
 * @param {string} anchorId
 * @param {DitamapParseResult[]} parseResults
 * @param {string} cssClassPrefix
 */
const replaceWithInternalLink = (node, ref, anchorId, parseResults, cssClassPrefix) => {
  let fullRef = ref + (anchorId ? '#' + anchorId : '');

  let fragmentSearchResult = extractorUtils.findFragment(parseResults, ref, anchorId);
  if (fragmentSearchResult.fragment && fragmentSearchResult.partOfTree) {
    // Here the topic is parsed and it's part of the main topic tree
    node.name('a');
    extractorUtils.removeAllAttributes(node);
    node.attr({ 'class': cssClassPrefix + 'doc-internal-link', 'href': 'javascript:void(0);', 'data-doc-ref': ref });
    if (anchorId) {
      node.attr('data-doc-anchor-id', anchorId);
    }
  } else {
    // Here the topic is unknown or not part of the main topic tree so we make an external link instead
    let href = EXTERNAL_DOC_URL_PREFIX + fullRef.replace('.xml', '.html');
    replaceWithExternalLink(node, href, cssClassPrefix);
  }

  if (!node.text().trim()) {
    if (fragmentSearchResult.fragment) {
      fragmentSearchResult.fragment.title.childNodes().forEach(titleChild => {
        node.addChild(titleChild.clone());
      });
    } else {
      console.log('%s: Could not find suitable text for: %s#%s', LOG_NAME, ref, anchorId);
    }
  }
};

/**
 * Replaces keyword nodes with they're specified value.
 *
 * @param node
 * @param {DitamapParseResult[]} parseResults
 * @param {String} cssClassPrefix
 */
const handleKeywordNode = (node, parseResults, cssClassPrefix) => {
  if (!extractorUtils.hasAttributes(node, 'keyref')) {
    throw new Error('Found keyword without keyref attribute.');
    return;
  }

  let keyRef = node.attr('keyref').value();
  node.attr('keyref').remove();

  let keyDef = undefined;
  parseResults.some(parseResult => {
    if (parseResult.keyDefs[keyRef]) {
      keyDef = parseResult.keyDefs[keyRef];
      return true;
    }
  });

  if (!keyDef) {
    // Here there's no corresponding key definition parsed
    if (node.text().trim()) {
      node.replace(node.text());
    } else if (keyRef === 'distro') {
      // The 'distro' keyword is likely in the top level of the docs, and not part of any sub-maps so default to 'CDH'.
      node.replace('CDH');
    } else {
      // Haven't seen this case yet
      throw new Error('Unknown keyref found: ' + keyRef);
    }
    return;
  }

  if (keyDef.text && !keyDef.href) {
    // A simple reference to a text
    node.replace(keyDef.text);
    return;
  }

  if (keyDef.href) {
    if (keyDef.external) {
      replaceWithExternalLink(node, keyDef.href, cssClassPrefix);
      if (!node.text().trim()) {
        node.text(keyDef.text || keyDef.href);
      }
    } else {
      if (keyDef.href.indexOf('scalability_file_handle_cache') !== -1) {

      }
      replaceWithInternalLink(node, keyDef.href.replace(/#.*$/, ''), keyRef, parseResults, cssClassPrefix);
    }
    return;
  }

  throw new Error('Failed handling keyword node.')
};

/**
 * Replaces xref nodes with links
 *
 * @param node
 * @param {DitamapParseResult[]} parseResults
 * @param {string} cssClassPrefix
 */
let handkeXrefNode = (node, parseResults, cssClassPrefix) => {
  if (extractorUtils.hasAttributes(node, 'href')) {
    let href = node.attr('href').value();

    if (node.attr('scope') && node.attr('scope').value() === 'external') {
      replaceWithExternalLink(node, href, cssClassPrefix);
      if (!node.text()) {
        node.text(href)
      }
      return;
    }

    let ref = ~href.indexOf('#') ? href.replace(/#.*$/, '') : href;
    let anchorId = ~href.indexOf('#') && href.replace(/^.*#/, '');
    replaceWithInternalLink(node, ref, anchorId, parseResults, cssClassPrefix);
  }
  if (extractorUtils.hasAttributes(node, 'keyref')) {
    handleKeywordNode(node, parseResults, cssClassPrefix);
  }
};

/**
 * Generates a table of contents if the topic has children
 *
 * @param {Topic} topic
 * @param node
 */
const handleTocNode = (topic, node) => {
  if (topic.children.length) {
    node.name('div');
    let header = node.node('div');
    header.text('Continue reading:');
    let ul = node.node('ul');
    topic.children.forEach(childTopic => {
      let li = ul.node('li');
      let xrefNode = li.node('xref');
      xrefNode.attr('href', childTopic.ref);
    })
  } else {
    node.remove();
  }
};

/**
 * Recursively identifies and replaces certain elements with the previous parse results.
 *
 * @param node
 * @param {DitamapParseResult[]} parseResults
 * @param {string} cssClassPrefix
 * @param {Object} foundCssClasses - Map keeping track of all the added css classes
 * @return {Object} - The map of added css classes
 */
const linkNodesInDomXml = (node, parseResults, cssClassPrefix, foundCssClasses) => {
  switch (node.name()) {
    case 'keyword':
      handleKeywordNode(node, parseResults, cssClassPrefix);
      break;
    case 'xref':
      handkeXrefNode(node, parseResults, cssClassPrefix);
      break;
    case 'image':
      throw new Error('Unsupported image element found');
    case 'imagemap':
      throw new Error('Unsupported imagemap element found');
    default:
      break;
  }

  if (extractorUtils.hasAttributes(node, 'class')) {
    foundCssClasses[node.attr('class').value()] = true;
  }
  node.childNodes().forEach(childNode => linkNodesInDomXml(childNode, parseResults, cssClassPrefix, foundCssClasses));
  return foundCssClasses;
};

/**
 * Adds conrefs and table of contents before the linking of the topics.
 *
 * @param {Topic} topic
 * @param node
 * @param {DitamapParseResult[]} parseResults
 */
const insertConrefsAndToc = (topic, node, parseResults) => {
  if (node.name() === 'toc') {
    handleTocNode(topic, node);
  }
  if (extractorUtils.hasAttributes(node, 'conref')) {
    let conref = node.attr('conref').value();
    var splitRef = conref.split('#');
    let fragmentSearchResult = extractorUtils.findFragment(parseResults, splitRef[0], splitRef[1]);
    if (!fragmentSearchResult.fragment) {
      console.log(node.toString());
      console.log('%s: Could not find fragment for conref: %s', LOG_NAME, conref);
    } else {
      node = node.replace(fragmentSearchResult.fragment.domElement.clone());
      if (extractorUtils.hasAttributes(node, 'id')) {
        node.attr('id').remove();
      }
    }
  }
  node.childNodes().forEach(childNode => insertConrefsAndToc(topic, childNode, parseResults));
};

/**
 * Links all the nodes in a topic
 *
 * @param {Topic} topic
 * @param {DitamapParseResult[]} parseResults
 * @param {String} cssClassPrefix
 * @param {Object} foundCssClasses
 */
let linkNodesInTopic = (topic, parseResults, cssClassPrefix, foundCssClasses) => {
  // First insert all the conrefs and topics
  insertConrefsAndToc(topic, topic.domXml, parseResults);
  // Then deal with xrefs, keywords etc.
  linkNodesInDomXml(topic.domXml, parseResults, cssClassPrefix, foundCssClasses);
  topic.children.forEach(childTopic => linkNodesInTopic(childTopic, parseResults, cssClassPrefix, foundCssClasses));
};

/**
 * This links all the nodes after parsing, it replaces keywords, adds links for xrefs, builds table of contents etc.
 *
 * @param parseResults
 * @param cssClassPrefix
 */
const linkTopics = (parseResults, cssClassPrefix) => {
  let foundCssClasses = {};
  parseResults.forEach(parseResult => parseResult.topics.forEach(topic => {
    linkNodesInTopic(topic, parseResults, cssClassPrefix, foundCssClasses);
  }));
  console.log('%s: Found CSS classes: %s', LOG_NAME, Object.keys(foundCssClasses).join(','));
};

module.exports = {
  linkTopics: linkTopics
};