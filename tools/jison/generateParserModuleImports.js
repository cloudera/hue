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

/* eslint-disable no-console */

const fs = require('fs');
const fsExtra = require('fs-extra');
const pathModule = require('path');
const { PARSER_FOLDER, LICENSE } = require('./generateParsers');

const fsPromises = fs.promises;

const SQL_PARSER_MODULES_PATH = `${PARSER_FOLDER}parserModules.ts`;
const SYNTAX_IMPORT_TEMPLATE =
  '  KEY: () => import(/* webpackChunkName: "KEY-parser" */ \'./KEY/KEYSyntaxParser\')';
const AUTOCOMPLETE_IMPORT_TEMPLATE =
  '  KEY: () => import(/* webpackChunkName: "KEY-parser" */ \'./KEY/KEYAutocompleteParser\')';
const GENERATED_NOTICE = `// PLEASE NOTE!
// Do not modify, the contents of this file is generated. 
// For more info see tools/jison/generateParserModuleImports.js
`;

const isFolder = async fileSystemEntry => {
  const entryPath = pathModule.join(PARSER_FOLDER, fileSystemEntry);
  return fsPromises.stat(entryPath).then(stats => stats.isDirectory());
};

const asyncFilter = async (arr, predicate) => {
  const orderedBooleans = await Promise.all(arr.map(predicate));
  return arr.filter((item, index) => orderedBooleans[index]);
};

const getParserNamesFromFolders = async () => {
  try {
    const fileSystemEntries = await fsPromises.readdir(PARSER_FOLDER);
    return await asyncFilter(fileSystemEntries, isFolder);
  } catch (err) {
    console.error(`Failed generating parser names from folders in ${PARSER_FOLDER}`);
    throw err;
  }
};

const getImports = async (parserNames, template, parserType) => {
  const parserExists = parserName =>
    fsExtra.pathExists(`${PARSER_FOLDER}/${parserName}/${parserName}${parserType}Parser.js`);

  const filtered = await asyncFilter(parserNames, parserExists);

  return filtered
    .map(parserName => template.replace(/KEY/g, parserName))
    .sort()
    .join(',\n');
};

const writeFile = async fileContent => {
  try {
    await fsExtra.ensureFile(SQL_PARSER_MODULES_PATH);
    await fsPromises.writeFile(SQL_PARSER_MODULES_PATH, fileContent);
  } catch (err) {
    console.error(`Failed writing data to file file: ${SQL_PARSER_MODULES_PATH}`, err);
    throw err;
  }
};

const generateParserModulesFile = async () => {
  try {
    // eslint-disable-next-line
    console.log('Generating file parserModules.ts...');

    const parserNames = await getParserNamesFromFolders();
    const syntaxImports = await getImports(parserNames, SYNTAX_IMPORT_TEMPLATE, 'Syntax');
    const autocompleteImports = await getImports(
      parserNames,
      AUTOCOMPLETE_IMPORT_TEMPLATE,
      'Autocomplete'
    );

    const exportSyntaxLines = `export const SYNTAX_MODULES = {\n${syntaxImports}\n};\n`;
    const exportAutoCompleteLines = `export const AUTOCOMPLETE_MODULES = {\n${autocompleteImports}\n};\n`;
    const fileContent = `${LICENSE}\n${GENERATED_NOTICE}\n${exportSyntaxLines}${exportAutoCompleteLines}`;
    await writeFile(fileContent);

    // eslint-disable-next-line
    console.log('Done writing parserModules.ts!\n');
  } catch (err) {
    console.error(`Failed generating parser modules import file: ${SQL_PARSER_MODULES_PATH}`, err);
  }
};

generateParserModulesFile();
