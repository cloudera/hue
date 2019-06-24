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
const program = require('commander');

const EPub = require('epub');

const Topic = require('./Topic');
const libxml = require('libxmljs');

const outputPath = './desktop/core/src/desktop/static/desktop/docs/hive/';
const mako = './desktop/core/src/desktop/templates/sql_doc_index.mako';

const jsonHandler = require('./jsonHandler');

// Handle command line arguments
program
  .version('1.0')
  .option('-e, --epub [path]', 'the path to the Hive epub file')
  .parse(process.argv);

const epub = new EPub(program.epub);

const convertToPre = (element, fragments) => {
  switch (element.name()) {
    case 'div':
      element.childNodes().forEach(node => {
        convertToPre(node, fragments);
      });
      break;
    case 'text':
      if (fragments.length === 1) {
        fragments.push(element.text().replace(/^\n/, ''));
      } else {
        fragments.push(element.text());
      }
      break;
    case 'code':
      if (element.attr('class') && element.attr('class').value().indexOf('value') !== -1) {
        fragments.push('<span class="hue-doc-varname">');
        element.childNodes().forEach(node => {
          convertToPre(node, fragments);
        });
        fragments.push('</span>');
        break;
      }
    default:
      element.childNodes().forEach(node => {
        convertToPre(node, fragments);
      });
  }
};

const adaptElement = (element) => {
  if (element.attr('class') && element.attr('class').value().indexOf('syntaxhighlighter') !== -1) {
    let fragments = ['<div class="hue-doc-codeblock">'];
    element.childNodes().forEach(childNode => {
      convertToPre(childNode, fragments);
    });
    fragments.push('</div>');
    let replacement = fragments.join('');
    element.replace(libxml.parseHtmlFragment(replacement).root());
  } else if (element.attr('class')) {
    element.attr('class').remove();
  }
  element.childNodes().forEach(adaptElement);
};

epub.on("end", function(){
  let savePromises = [];

  let rootTopics = [];
  let topicStack = [];

  let lastTopicPerLevel = {};

  let promises = [];

  epub.flow.forEach(chapter => {
    promises.push(new Promise((resolve, reject) => {
      let topic = new Topic('/', chapter.id);
      topic.fragment = {
        title : {
          text: () => chapter.title.replace(/LanguageManual\s(.+)/, '$1')
        }
      };

      epub.getChapter(chapter.id, (error, text) => {
        try {
          let contents = libxml.parseHtmlFragment('<div>' + text + '</div>');
          topic.domXml = contents.root();
          adaptElement(topic.domXml);
          resolve();
        } catch (error) {
          reject();
        }
      });

      if (lastTopicPerLevel[chapter.level - 1]) {
        lastTopicPerLevel[chapter.level - 1].children.push(topic);
      }

      if (chapter.level === 0) {
        rootTopics.push(topic);
      }

      lastTopicPerLevel[chapter.level] = topic;
    }));
  });

  Promise.all(promises).then(() => {
    jsonHandler.saveTopics(rootTopics, outputPath, mako, false).then(() => {
      console.log('Done.');
    }).catch(() => {
      console.log('Fail.');
    });
  });
});

epub.parse();
