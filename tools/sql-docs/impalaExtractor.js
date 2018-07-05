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

let fs = require('fs');
let libxml = require('libxmljs');

let keyDefs = {};
let pathToXref = {};
let knownTitles = {};
let xrefs = {};
let conRefs = {};

let handleChildNodes = (x, path, body) => {
  x.childNodes().forEach(y => {
    handleElement(y, path, body);
  });
};

let addStartElement = (x, path, body, elemName, classes) => {
  let start = '<' + elemName;
  if (x.attr('id')) {
    let id = path.substring(path.lastIndexOf('/' + 1)) + '_' + x.attr('id').value();
    start += ' id="' + id + '"';
  }
  if (classes) {
    start += ' class="' + classes + '"';
  }
  start += '>';
  body.push(start);
};

let wrapHtmlElement = (x, path, body, elemName, classes) => {
  addStartElement(x, path, body, elemName, classes);
  handleChildNodes(x, path, body);
  body.push('</' + elemName + '> ');
};

let handleElement = (x, path, body) => {
  if (x.name() === 'text') {
    if (x.text().trim()) {
      body.push(x.text());
    }
  } else if (x.name() === 'xref') {
    body.push({
      xrefNode: x,
      path: path
    });
  } else {
    if (!x.childNodes().length) {
      if (x.name() === 'keyword' && x.attr('keyref')) {
        if (keyDefs[x.attr('keyref').value()]) {
          body.push(keyDefs[x.attr('keyref').value()]);
        } else {
          body.push(x.attr('keyref').value())
        }
      } else if (x.attr('conref') && x.attr('conref').value().indexOf('impala_common.xml') !== -1) {
        var id = x.attr('conref').value().replace(/^.*common\//, '');
        if (conRefs[id]) {
          handleElement(conRefs[id], path, body);
        } else {
          console.log('concept ref not found with id: ' + id);
        }
      }
    } else {
      switch (x.name()) {
        case 'title': { wrapHtmlElement(x, path, body, 'h4'); break; }
        case 'p': {
          wrapHtmlElement(x, path, body, 'p');
          break;
        }
        case 'concept': {
          if (!x.attr('audience') || x.attr('audience').value() !== 'hidden') {
            wrapHtmlElement(x, path, body, 'div');
            if (x.attr('id') && x.get('title')) {
              var titleParts = [];
              handleElement(x.get('title'), path, titleParts);
              knownTitles[path.substring(path.indexOf('topics/')) + '#' + x.attr('id').value()] = titleParts.join('');
            }
          }
          break;
        }
        case 'conbody': {
          wrapHtmlElement(x, path, body, 'div');
          if (x.parent().get('title')) {
            var titleParts = [];
            handleElement(x.parent().get('title'), path, titleParts);
            knownTitles[path.substring(path.indexOf('topics/'))] = titleParts.join('');
          }
          break;
        }
        case 'codeph':
        case 'cmdname':
        case 'ph': { wrapHtmlElement(x, path, body, 'span', 'sql-docs-inline-code'); break; }
        case 'codeblock': {
          addStartElement(x, path, body, 'div', 'sql-docs-code-block');
          var preChildren = [];
          handleChildNodes(x, path, preChildren);
          preChildren.forEach(function (child) {
            body.push(child.replace(/^\s*/g, '').replace(/\n/g, '<br/>'));
          });
          body.push('</div>');
          break;
        }
        case 'keyword': { wrapHtmlElement(x, path, body, 'span'); break; }
        case 'varname':
        case 'filepath':
        case 'term': { wrapHtmlElement(x, path, body, 'span', 'sql-docs-variable'); break; }
        case 'note': { wrapHtmlElement(x, path, body, 'div', 'sql-docs-note'); break; }
        case 'b': { wrapHtmlElement(x, path, body, 'b'); break; }
        case 'q':  { wrapHtmlElement(x, path, body, 'q'); break; }
        case 'i': { wrapHtmlElement(x, path, body, 'i'); break; }
        case 'sup': { wrapHtmlElement(x, path, body, 'sup'); break; }
        case 'ul': { wrapHtmlElement(x, path, body, 'ul'); break; }
        case 'li': { wrapHtmlElement(x, path, body, 'li'); break; }
        case 'indexterm':
        case 'metadata':
        case 'fig':
        case 'prolog':
        case 'titlealts':
        case 'uicontrol':
        case 'table':
        case 'navtitle': break;
        default: console.log('Could not process element of type: ' + x.name() + ' in ' + path);
      }
    }
  }
};

let parseDml = (path) => {
  return new Promise((resolve) => {
    fs.readFile(path, 'utf8', (err, data) => {
      try {
        let xmlDoc = libxml.parseXmlString(data);
        let body = [];
        var titleParts = [];
        handleChildNodes(xmlDoc.get('//title'), path, titleParts);
        if (xmlDoc.root().attr('id')) {
          knownTitles[path.substring(path.indexOf('topics/')) + '#' + xmlDoc.root().attr('id').value()] = titleParts.join('');
        }
        xmlDoc.get('//title').remove();
        xmlDoc.childNodes().forEach(x => {
          handleElement(x, path, body);
        });
        resolve({ title: titleParts.join(''), body: body});
      } catch (err) {
        console.log(path);
        console.log(err);
      }
    });
  });
};

class Topic {
  constructor (ref, node, promises) {
    this.ref = ref;
    this.path = '../Impala/docs/' + ref;
    this.children = [];
    this.title = '';
    this.body = [];
    if (pathToXref[this.ref]) {
      pathToXref[this.ref].parsed = true;
    }
    promises.push(parseDml(this.path).then(parseResult => {
      this.title = parseResult.title;
      this.body = parseResult.body;
    }));

    if (node.childNodes().length) {
      node.childNodes().forEach(x => {
        if (x.name() === 'topicref' && x.attr('href').value() !== 'topics/impala_functions.xml') {
          this.children.push(new Topic(x.attr('href').value(), x, promises));
        }
      });
    }
  }
}

 fs.readFile('../Impala/docs/impala_keydefs.ditamap', 'utf8', (err, keyDefRaw) => {
  if (err) {
    console.log('Could not find the Impala docs! (../Impala/docs/impala_keydefs.ditamap)');
    console.log('Make sure you have Impala checked out in an "Impala" folder next to the hue folder');
    return;
  }

  libxml.parseXmlString(keyDefRaw).get('//map').childNodes().forEach(x => {
   if (x.name() === 'keydef' && x.attr('keys')) {
     let valNode = x.get('topicmeta/keywords/keyword');
     if (valNode) {
       keyDefs[x.attr('keys').value()] = valNode.text();
     } else if (x.attr('href')) {
       xrefs[x.attr('keys')] = {
         ref: x.attr('href').value(),
         parsed: false,
         external: x.attr('scope') && x.attr('scope').value() === 'external'
       };
       pathToXref[x.attr('href').value()] = xrefs[x.attr('keys')];
     }
   }
  });

  let stringifyTopic = (topic, prefix) => {
     let result = prefix + '{\n' + prefix + '  id: \'' + topic.ref + '\',\n' + prefix + '  title: \'' + topic.title + '\',\n' + prefix + '  weight: 1,\n' + prefix + '  bodyMatch: ko.observable(),\n' + prefix + '  open: ko.observable(false),\n' + prefix +'  titleMatch: ko.observable()';

     if (topic.body.length) {
       var bodyString = '';
       topic.body.forEach(function (bodyElement) {
         if (typeof bodyElement === 'string') {
           bodyString += bodyElement;
         } else if (bodyElement.xrefNode) {
           if (bodyElement.xrefNode.attr('href')) {
             if (bodyElement.xrefNode.attr('scope') && bodyElement.xrefNode.attr('scope').value() === 'external') {
               bodyString += '<a target="_blank" href="' + bodyElement.xrefNode.attr('href').value() + '">' + bodyElement.xrefNode.text() + '</a>'
             } else {
               let href = bodyElement.xrefNode.attr('href').value();
               if (href.indexOf('#') === 0) {
                 href = bodyElement.path.substring(bodyElement.path.indexOf('topics/')) + href;
               } else if (href.indexOf('topics/') !== -1) {
                 href = href.substring(href.indexOf('topics')); // clean up [..]/topic/ etc.
               } else {
                 href = 'topics/' + href;
               }
               var split = href.split('#');

               var unknown = false;
               let title = href;
               if (knownTitles[href]) {
                 title = bodyElement.xrefNode.text() || knownTitles[href];
               } else if (knownTitles[split[0]]) {
                 title = bodyElement.xrefNode.text() || knownTitles[split[0]];
               } else if (bodyElement.xrefNode.text()) {
                 unknown = true;
                 title = bodyElement.xrefNode.text();
               } else if (split[1]) {
                 unknown = true;
                 title = split[1].replace(/_/g, ' ');
               } else {
                 unknown = true;
                 title = href.replace('topics/', '').replace('.xml', '').replace(/_/g, ' ');
               }

               if (unknown) {
                 bodyString += '<span>' + title + '</span>'; // Unknown = not parsed reference as some docs are excluded
               } else {
                 bodyString += '<a href="javascript: void(0);" class="lang-ref-link" data-target="' + href + '">' + title + '</a>';
               }
             }
           }
         }
       });
       result += ',\n' + prefix + '  body: \'' + bodyString.replace(/([^\\])\\([^\\])/g, '$1\\\\$2').replace(/'/g, '\\\'').replace(/\n/g, '\' + \n' + prefix + '    \'') + '\''
     }
     if (topic.children.length) {
       result += ',\n' + prefix + '  children: [\n';
       let stringifiedChildren = [];
       topic.children.forEach(child => {
         stringifiedChildren.push(stringifyTopic(child, prefix + '  '))
       });
       result += stringifiedChildren.join(',\n');
       result += prefix + ']';
     } else {
       result += ',\n' + prefix + '  children: []\n';
     }
     result += prefix + '}';
     return result;
   };

  fs.readFile('../Impala/docs/shared/impala_common.xml', 'utf-8', (err, commonRaw) => {

    let handleCommonChildren = children => {
      children.forEach(child => {
        if (child.attr('id')) {
          conRefs[child.attr('id').value()] = child;
        }
        if (child.childNodes().length) {
          handleCommonChildren(child.childNodes());
        }
      })
    };

    handleCommonChildren(libxml.parseXmlString(commonRaw).get('//conbody').childNodes());

    fs.readFile('../Impala/docs/impala_sqlref.ditamap', 'utf8', (err, mapRaw) => {
      let topics = [];
      let promises = [];

      libxml.parseXmlString(mapRaw).get('//map').childNodes().forEach(x => {
        if (x.name() === 'topicref' && x.attr('href').value() !== 'topics/impala_functions.xml') {
          topics.push(new Topic(x.attr('href').value(), x, promises));
        }
      });

      Promise.all(promises).then(() => {
        fs.readFile('tools/jison/license.txt', 'utf-8', (err, licenseHeader) => {
          let result = licenseHeader + '\n\n\n// NOTE: This is a generated file!\n// Run \'node tools/sql-docs/impalaExtractor.js\' to generate.\n\n\nvar impalaLangRefTopics = [\n';
          let stringifiedTopics = [];
          topics.forEach(topic => {
            stringifiedTopics.push(stringifyTopic(topic, ''));
          });
          result += stringifiedTopics.join(',\n');
          result += '\n];';
          fs.writeFile('desktop/core/src/desktop/static/desktop/js/sqlImpalaLangRef.js', result, () => {
            console.log('desktop/core/src/desktop/static/desktop/js/sqlImpalaLangRef.js updated!');
          })
        })
      });
    });
  })
});