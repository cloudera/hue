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

const program = require('commander');

const EPub = require('epub');

const Topic = require('./Topic');
const libxml = require('libxmljs');
const extractorUtils = require('./extractorUtils');

const outputPath = '../../desktop/core/src/desktop/static/desktop/docs/hive/';
const mako = '../../desktop/core/src/desktop/templates/sql_doc_index.mako';

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

const adaptElement = element => {
  if (element.attr('class') && element.attr('class').value().indexOf('syntaxhighlighter') !== -1) {
    const fragments = ['<div class="hue-doc-codeblock">'];
    element.childNodes().forEach(childNode => {
      convertToPre(childNode, fragments);
    });
    fragments.push('</div>');
    const replacement = fragments.join('');
    element.replace(libxml.parseHtmlFragment(replacement).root());
  } else if (element.attr('class')) {
    if (element.attr('class').value().indexOf('admonition') !== -1) {
      element.attr({ class: 'hue-doc-note-hive' });
    } else {
      element.attr('class').remove();
    }
  }

  switch (element.name()) {
    case 'a':
      if (element.attr('href') && element.attr('href').value().indexOf('/links') === 0) {
        // Internal link
        let ref = element
          .attr('href')
          .value()
          .replace(/\/links\/_[0-9]+\//, '');
        extractorUtils.removeAllAttributes(element);

        const anchorMatch = ref.match(/.html#(.+)$/);
        if (anchorMatch) {
          element.attr('data-doc-anchor-id', anchorMatch[1]);
          ref = ref.replace('#' + anchorMatch[1], '');
        }
        ref = '_' + ref.replace('.html', '');
        element.attr({
          class: 'hue-doc-internal-link',
          href: 'javascript:void(0);',
          'data-doc-ref': ref
        });
      } else if (element.attr('href')) {
        // External link
        const href = element.attr('href').value();
        extractorUtils.removeAllAttributes(element);
        element.attr({ class: 'hue-doc-external-link', href: href, target: '_blank' });
      }
      break;
    case 'h1':
      element.text(element.text().replace(/LanguageManual\s(.+)/, '$1'));
      element.attr({ class: 'hue-doc-title-hive' });
      break;
    case 'table':
    case 'td':
    case 'th':
    case 'tr':
      element.attr({ class: 'hue-doc-' + element.name() + '-hive' });
    default:
  }

  element.childNodes().forEach(adaptElement);
};

epub.on('end', () => {
  const rootTopics = [];

  const lastTopicPerLevel = {};

  const promises = [];

  epub.flow.forEach(chapter => {
    promises.push(
      new Promise((resolve, reject) => {
        const topic = new Topic('/', chapter.id);
        topic.fragment = {
          title: {
            text: () => chapter.title.replace(/LanguageManual\s(.+)/, '$1')
          }
        };

        epub.getChapter(chapter.id, (error, text) => {
          try {
            const contents = libxml.parseHtmlFragment('<div>' + text + '</div>');
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
      })
    );
  });

  Promise.all(promises).then(() => {
    const rootTopic = rootTopics[0];
    rootTopic.children.forEach(childTopic => {
      rootTopics.push(childTopic);
    });
    rootTopic.children = [];

    jsonHandler
      .saveTopics(rootTopics, outputPath, mako, false)
      .then(() => {
        console.log('Done.');
      })
      .catch(() => {
        console.log('Fail.');
      });
  });
});

epub.parse();

/* eslint-enable no-restricted-syntax */
