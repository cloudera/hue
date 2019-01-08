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

const DocFragment = require('./DocFragment');
const Topic = require('./Topic');
const extractorUtils = require('./extractorUtils');
const libxml = require('libxmljs');

const LOG_NAME = 'docXmlParser.js';

const isHidden = (docElement) => docElement.attr('audience') &&
  (docElement.attr('audience').value() === 'hidden' || docElement.attr('audience').value() === 'PDF');

// Turn relative anchor or topic links into absolute
const makeAbsoluteRef = (href, topic) => {
  if (href.indexOf('#') === 0) {
    return topic.ref + href;
  }
  if (href.indexOf('#') === -1 && href.indexOf('.xml') === -1) {
    return topic.ref + '#' + href;
  }
  if (/^[^/]+\.xml.*$/.test(href) && ~topic.ref.indexOf('/')) {
    // Path is relative current doc (add parent folders if exists)
    return extractorUtils.getParentFolder(topic.ref) + href;
  }
  if (href.indexOf('..') !== -1) {
    // Make relative parent paths relative to start folder
    return (extractorUtils.getParentFolder(topic.ref) + href).replace(/[^/]+\/\.\.\//g, '');
  }
  return href;
};

const parseTopic = (topic, cssClassPrefix, conrefCallback) => {
  return new Promise((resolve, reject) => {
    extractorUtils.readFile(topic.docRootPath + (~topic.ref.indexOf('#') ? topic.ref.replace(/#.*$/, '') : topic.ref)).then(contents => {
      let xmlDoc = libxml.parseXmlString(contents);
      let docElement = xmlDoc.root();
      if (~topic.ref.indexOf('#')) {
        docElement = docElement.get('//*[@id=\'' + topic.ref.replace(/^.*#/, '') + '\']')
      }
      parseDocElement(docElement, topic.domXml, cssClassPrefix, topic, undefined, conrefCallback);

      resolve();
    }).catch(reject);
  })
};

const parseDocElement = (docElement, domElement, cssClassPrefix, topic, activeFragment, conrefCallback) => {
  // return in the switch stops the recursion at this node
  if (extractorUtils.hasAttributes(docElement, 'conref')) {
    let absoluteConRef = makeAbsoluteRef(docElement.attr('conref').value(), topic);
    docElement.attr('conref', absoluteConRef);
    conrefCallback(topic, absoluteConRef.replace(/#.*$/, ''));
  }

  if (docElement.attr('outputclass') && docElement.attr('outputclass').value() === 'toc') {
    domElement.node('toc');
    return;
  }

  switch (docElement.name()) {
    case 'concept':
    case 'conbody':
      domElement = domElement.node('div');
      break;
    case 'tgroup':
    case 'colspec':
    case 'dlentry':
      if (extractorUtils.hasAttributes(docElement, 'id')) {
        let id = docElement.attr('id') && docElement.attr('id').value();
        // Move id attribute to first child element
        for (let node of docElement.childNodes()) {
          if (node.type() === 'element') {
            node.attr({'id': id});
            break;
          }
        }
        docElement.attr('id').remove();
      }
      // skip creating corresponding DOM element
      break;
    case 'alt':
    case 'area':
    case 'b':
    case 'cite':
    case 'coords':
    case 'dd':
    case 'dl':
    case 'dt':
    case 'fn':
    case 'i':
    case 'li':
    case 'ol':
    case 'p':
    case 'shape':
    case 'q':
    case 'sup':
    case 'table':
    case 'tbody':
    case 'thead':
    case 'tt':
    case 'u':
    case 'ul':
      if (isHidden(docElement)) {
        return;
      }
      domElement = domElement.node(docElement.name());
      if (extractorUtils.hasAttributes(docElement, 'conref')) {
        domElement.attr('conref', docElement.attr('conref').value());
      }
      break;
    case 'sthead':
      domElement = domElement.node('tr');
      domElement.attr({ 'class': cssClassPrefix + 'doc-sthead' });
      break;
    case 'stentry':
      domElement = domElement.node('td');
      break;
    case 'simpletable':
      domElement = domElement.node('table');
      break;
    case 'strow':
    case 'row':
      domElement = domElement.node('tr');
      break;
    case 'entry':
      if (docElement.parent().name().toLowerCase() === 'row') {
        domElement = domElement.node('td');
      } else {
        console.log('%s: Got "entry" element without a parent "row": %s in ref %s', LOG_NAME, docElement.toString(), topic.ref);
        return;
      }
      break;
    case 'xref':
      if (extractorUtils.hasAttributes(docElement, 'href') && (!docElement.attr('scope') || docElement.attr('scope').value() !== 'external')) {
        docElement.attr('href', makeAbsoluteRef(docElement.attr('href').value(), topic));
      }
    case 'image':
    case 'imagemap':
    case 'keyword':
      // These elements are dealt with later, we don't deep clone as there might be child elements to parse
      domElement = domElement.node(docElement.name());
      docElement.attrs().forEach(attr => {
        domElement.attr(attr.name(), attr.value())
      });
      break;
    case 'object':
      if (extractorUtils.hasAttributes(docElement, ['data', 'outputclass'])) {
        domElement = domElement.node('iframe');
        domElement.attr({ 'class': cssClassPrefix + 'doc-iframe', 'src': docElement.attr('data').value() });
        if (extractorUtils.hasAttributes(docElement, 'width')) {
          domElement.attr({ 'width': docElement.attr('width').value() });
        }
        if (extractorUtils.hasAttributes(docElement, 'height')) {
          domElement.attr({ 'height': docElement.attr('height').value() });
        }
      } else {
        console.log('%s: Got "object" element without data and outputclass: %s in ref %s', LOG_NAME, docElement.toString(), topic.ref);
        return;
      }
      break;
    case 'pre': // Enables better styling if div + class
    case 'cmdname':
    case 'codeph':
    case 'filepath':
    case 'lines':
    case 'option':
    case 'parmname':
    case 'ph':
    case 'systemoutput':
    case 'term':
    case 'userinput':
    case 'apiname':
    case 'varname':
      if (isHidden(docElement)) {
        return;
      }
      domElement = domElement.node('span');
      domElement.attr({ 'class': cssClassPrefix + 'doc-' + docElement.name() });
      break;
    case 'codeblock':
    case 'conbodydiv':
    case 'example':
    case 'fig':
    case 'menucascade':
    case 'msgblock':
    case 'note':
    case 'section':
    case 'sectiondiv':
    case 'title':
    case 'uicontrol':
      if (isHidden(docElement)) {
        return;
      }
      domElement = domElement.node('div');
      domElement.attr({ 'class': cssClassPrefix + 'doc-' + docElement.name() });
      if (docElement.name() === 'title' && activeFragment && !activeFragment.title) {
        activeFragment.title = domElement;
      }
      break;
    case 'text':
      if (docElement.text().trim()) {
        let firstInDiv = domElement.name() === 'div' && domElement.childNodes().length === 0;
        domElement = domElement.node('text');
        domElement.replace(firstInDiv ? docElement.text().replace(/^[\n\r]*/, '') : docElement.text());
      }
      break;
    case 'abstract':
    case 'comment':
    case 'data':
    case 'draft-comment':
    case 'indexterm':
    case 'oxy_attributes':
    case 'oxy_comment_start':
    case 'oxy_comment_end':
    case 'oxy_delete':
    case 'oxy_insert_start':
    case 'oxy_insert_end':
    case 'prolog':
    case 'shortdesc':
    case 'titlealts':
      return;
    case undefined:
      if (/^<\!\[cdata.*/i.test(docElement.toString())) {
        if (docElement.text().trim()) {
          let firstInDiv = domElement.name() === 'div' && domElement.childNodes().length === 0;
          domElement = domElement.node('text');
          domElement.replace(firstInDiv ? docElement.text().replace(/^[\n\r]*/, '') : docElement.text());
        }
        break;
      }
    default:
      console.log('%s: Can\'t handle node: %s in ref %s', LOG_NAME, docElement.name(), topic.ref);
      return;
  }

  if (isHidden(docElement)) {
    domElement.attr({ 'style': 'display:none;' });
  }

  if (extractorUtils.hasAttributes(docElement, 'id')) {
    let fragmentId = docElement.attr('id') && docElement.attr('id').value();
    let newFragment = new DocFragment(fragmentId, domElement);
    if (!extractorUtils.hasAttributes(domElement, 'id') && domElement.type() === 'element') {
      domElement.attr({'id': fragmentId});
    }
    if (!topic.fragment) {
      topic.fragment = newFragment;
    } else {
      activeFragment.children.push(newFragment);
    }
    activeFragment = newFragment;
  }

  if (extractorUtils.hasAttributes(docElement, 'conref') && !extractorUtils.hasAttributes(domElement, 'conref')) {
    domElement.attr('conref', docElement.attr('conref').value());
  }
  docElement.childNodes().forEach(childNode => parseDocElement(childNode, domElement, cssClassPrefix, topic, activeFragment, conrefCallback));
};

/**
 * Parses all the topic xml files and sets the intermediary DOM on the topic, after this linkage is required to insert
 * any conrefs or keywords etc. that are only known after parsing all the topics.
 *
 * @param parseResults
 * @param cssClassPrefix
 * @return {Promise}
 */
const parseTopics = (parseResults, cssClassPrefix) => new Promise((resolve, reject) => {
  let topicIndex = {};
  let topicsToParse = [];

  let populateTopicsFromTree = topics => {
    topics.forEach(topic => {
      topicsToParse.push(topic);
      topicIndex[topic.ref] = true;
      populateTopicsFromTree(topic.children);
    })
  };

  // Topics might be referenced from within .xml files thar are not part of the ditamap, we add them here to make
  // sure they're parsed
  let conrefCallback = (sourceTopic, ref) => {
    if (!topicIndex[ref]) {
      let topic = new Topic(sourceTopic.docRootPath, ref);
      topicIndex[ref] = true;
      topicsToParse.push(topic);
      if (parseResults.length < 2) {
        // We add additional topics to any ditamap parseresults except the first one, this prevents
        // them from being part of the tree.
        parseResults.push({
          topics: [],
          topicIndex: {},
          keyDefs: {}
        })
      }
      parseResults[parseResults.length - 1].topicIndex[ref] = topic;
    }
  };

  parseResults.forEach(parseResult => populateTopicsFromTree(parseResult.topics));

  let parseNextTopic = () => {
    if (topicsToParse.length) {
      parseTopic(topicsToParse.shift(), cssClassPrefix, conrefCallback).then(parseNextTopic).catch(reject);
    } else {
      resolve();
    }
  };
  parseNextTopic();
});

module.exports = {
  parseTopics: parseTopics,
  isHidden: isHidden
};