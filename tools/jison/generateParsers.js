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
let exec = require('child_process').exec;

const LICENSE = '// Licensed to Cloudera, Inc. under one\n' +
  '// or more contributor license agreements.  See the NOTICE file\n' +
  '// distributed with this work for additional information\n' +
  '// regarding copyright ownership.  Cloudera, Inc. licenses this file\n' +
  '// to you under the Apache License, Version 2.0 (the\n' +
  '// "License"); you may not use this file except in compliance\n' +
  '// with the License.  You may obtain a copy of the License at\n' +
  '//\n' +
  '//     http://www.apache.org/licenses/LICENSE-2.0\n' +
  '//\n' +
  '// Unless required by applicable law or agreed to in writing, software\n' +
  '// distributed under the License is distributed on an "AS IS" BASIS,\n' +
  '// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n' +
  '// See the License for the specific language governing permissions and\n' +
  '// limitations under the License.\n';

const SQL_STATEMENTS_PARSER_JSDOC = '/**\n' +
  ' * @param {string} input\n' +
  ' *\n' +
  ' * @return {SqlStatementsParserResult}\n' +
  ' */\n';

const JISON_FOLDER = 'desktop/core/src/desktop/js/parse/jison/';
const TARGET_FOLDER = 'desktop/core/src/desktop/js/parse/';

const PARSERS = {
  globalSearchParser: {
    sources: ['globalSearchParser.jison'],
    target: 'globalSearchParser.jison',
    afterParse: (contents) => new Promise(resolve => {
      resolve(LICENSE +
        contents.replace('var globalSearchParser = ', 'import SqlParseSupport from \'parse/sqlParseSupport\';\n\nvar globalSearchParser = ') +
        '\nexport default globalSearchParser;\n');
    })
  },
  solrFormulaParser: {
    sources: ['solrFormulaParser.jison'],
    target: 'solrFormulaParser.jison',
    afterParse: (contents) => new Promise(resolve => {
      resolve(LICENSE + contents + 'export default solrFormulaParser;\n');
    })
  },
  solrQueryParser: {
    sources: ['solrQueryParser.jison'],
    target: 'solrQueryParser.jison',
    afterParse: (contents) => new Promise(resolve => {
      resolve(LICENSE + contents + 'export default solrQueryParser;\n');
    })
  },
  sqlAutocompleteParser: {
    sources: [
      'autocomplete_header.jison', 'sql_main.jison', 'sql_valueExpression.jison', 'sql_error.jison', 'sql_alter.jison',
      'sql_analyze.jison', 'sql_create.jison', 'sql_drop.jison', 'sql_grant.jison', 'sql_insert.jison', 'sql_load.jison',
      'sql_set.jison', 'sql_show.jison', 'sql_update.jison', 'sql_use.jison', 'autocomplete_footer.jison'
    ],
    target: 'sqlAutocompleteParser.jison',
    lexer: 'sql.jisonlex',
    afterParse: (contents) => new Promise(resolve => {
      resolve(LICENSE +
        contents.replace('var sqlAutocompleteParser = ', 'import SqlParseSupport from \'parse/sqlParseSupport\';\n\nvar sqlAutocompleteParser = ') +
        '\nexport default sqlAutocompleteParser;\n');
    })
  },
  sqlStatementsParser: {
    sources: ['sqlStatementsParser.jison'],
    target: 'sqlStatementsParser.jison',
    afterParse: (contents) => new Promise(resolve => {
      resolve(LICENSE + contents.replace('parse: function parse', SQL_STATEMENTS_PARSER_JSDOC + 'parse: function parse') + 'export default sqlStatementsParser;\n');
    })
  },
  sqlSyntaxParser: {
    sources: [
      'syntax_header.jison', 'sql_main.jison', 'sql_valueExpression.jison', 'sql_alter.jison', 'sql_analyze.jison',
      'sql_create.jison', 'sql_drop.jison', 'sql_grant.jison', 'sql_insert.jison', 'sql_load.jison', 'sql_set.jison',
      'sql_show.jison', 'sql_update.jison', 'sql_use.jison', 'syntax_footer.jison'
    ],
    target: 'sqlSyntaxParser.jison',
    lexer: 'sql.jisonlex',
    afterParse: (contents) => new Promise(resolve => {
      resolve(LICENSE +
        contents.replace('var sqlSyntaxParser = ', 'import SqlParseSupport from \'parse/sqlParseSupport\';\n\nvar sqlSyntaxParser = ')
          .replace('loc: yyloc,', 'loc: lexer.yylloc, ruleId: stack.slice(stack.length - 2, stack.length).join(\'\'),') +
        '\nexport default sqlSyntaxParser;\n');
    })
  },
};

const readFile = (path) => new Promise((resolve, reject) => {
  fs.readFile(path, (err, buf) => {
    if (err) {
      reject();
    }
    resolve(buf.toString());
  })
});

const writeFile = (path, contents) => new Promise((resolve, reject) => {
  fs.writeFile(path, contents, function(err, data) {
    if (err) {
      reject();
    }
    resolve();
  });
});

const deleteFile = (path) => {
  fs.unlinkSync(path);
};

const execCmd = (cmd) => new Promise((resolve, reject) => {
  exec(cmd, function(err, stdout, stderr) {
    if (err) {
      reject(stderr);
    }
    resolve();
  });
});

const generateParser = parserName => new Promise((resolve, reject) => {
  let parserConfig = PARSERS[parserName];

  let concatPromise = new Promise((resolve, reject) => {
    if (parserConfig.sources.length > 1 && parserConfig.target) {
      console.log('Concatenating files...');
      let promises = parserConfig.sources.map(fileName => readFile(JISON_FOLDER + fileName));

      Promise.all(promises).then(contents => {
        writeFile(JISON_FOLDER + parserConfig.target, contents).then(() => {
          resolve(JISON_FOLDER + parserConfig.target)
        })
      }).catch(reject);
    } else if (parserConfig.sources.length === 1) {
      resolve(JISON_FOLDER + parserConfig.sources[0]);
    } else {
      reject('No jison source specified');
    }
  });


  concatPromise.then((targetPath) => {
    let jisonCommand = 'jison ' + targetPath;
    if (parserConfig.lexer) {
      jisonCommand += ' ' + JISON_FOLDER + parserConfig.lexer
    }
    jisonCommand += ' -m js';
    console.log('Generating parser...');
    execCmd(jisonCommand).then(() => {
      if (parserConfig.sources.length > 1) {
        deleteFile(targetPath); // Remove concatenated file
      }
      console.log('Adjusting JS...');
      let generatedJsFileName = parserConfig.target.replace('.jison', '.js');
      readFile(generatedJsFileName).then(contents => {
        parserConfig.afterParse(contents).then(finalContents => {
          writeFile(TARGET_FOLDER + generatedJsFileName, finalContents).then(() => {
            deleteFile(generatedJsFileName);
            console.log('Done!\n');
            resolve();
          }).catch(reject);
        }).catch(reject);
      }).catch(reject);
    }).catch(reject);
  }).catch(reject);
});

let parsersToGenerate = [];
const invalid = [];

let all = false;
let appFound = false;
process.argv.forEach(arg => {
  if (appFound) {
    if (arg === 'all') {
      all = true;
    } else if (PARSERS[arg]) {
      parsersToGenerate.push(arg);
    } else {
      invalid.push(arg);
    }
  } else if (arg.indexOf('generateParsers.js') !== -1) {
    appFound = true;
  }
});

if (all) {
  parsersToGenerate = Object.keys(PARSERS);
}

if (invalid.length) {
  console.log('No parser config found for: \'' + invalid.join('\', \'') + '\'');
  console.log('\nPossible options are:\n  ' + ['all'].concat(Object.keys(PARSERS)).join('\n  ') + '\n');
  return;
}

parserCount = parsersToGenerate.length;
let idx = 0;

const generateRecursive = () => {
  idx++;
  if (parsersToGenerate.length) {
    let parserName = parsersToGenerate.pop();
    if (parserCount > 1) {
      console.log('Generating \'' + parserName + '\' (' + idx + '/' + parserCount + ')...');
    } else {
      console.log('Generating \'' + parserName + '\'...');
    }
    generateParser(parserName).then(generateRecursive).catch(error => {
      console.log(error);
      console.log('FAIL!');
    })
  }
};

generateRecursive();



