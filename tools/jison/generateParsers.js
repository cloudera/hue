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

import { identifySqlParsers } from './parserDefinitions.js';
import { deleteFile, readFile, writeFile } from './utils.js';
import jisonCli from 'jison/lib/cli.js';

const findParsersToGenerateFromArgs = parserDefinitions => {
  process.argv.shift(); // drop "node"
  process.argv.shift(); // drop "generateParsers.js"
  const foundDefinitions = new Set();
  const invalid = [];
  if (process.argv[0] === 'all') {
    Object.values(parserDefinitions).forEach(definition => foundDefinitions.add(definition));
  } else {
    process.argv.forEach(arg => {
      if (parserDefinitions[arg]) {
        foundDefinitions.add(parserDefinitions[arg]);
      } else {
        let found = false;
        Object.keys(parserDefinitions).forEach(key => {
          if (key.indexOf(arg) === 0) {
            found = true;
            foundDefinitions.add(parserDefinitions[key]);
          }
        });
        if (!found) {
          invalid.push(arg);
        }
      }
    });
  }
  if (invalid.length) {
    throw new Error(`Could not find parser definitions for '${invalid.join(", '")}'`);
  }
  return [...foundDefinitions];
};

const getConcatenatedContent = async sources => {
  const contents = [];
  for (const source of sources) {
    // We know the file exists, verified in parserDefinitions.js
    contents.push(await readFile(source));
  }
  return contents.join();
};

const generateParser = async parserDefinition => {
  const jisonContents = await getConcatenatedContent(parserDefinition.sources);
  await writeFile(parserDefinition.targetJison, jisonContents);

  const generatedParserFileName = `${parserDefinition.parserName}.js`;
  const options = {
    file: parserDefinition.targetJison,
    outfile: generatedParserFileName,
    'module-type': 'js'
  };
  if (parserDefinition.lexer) {
    options.lexfile = parserDefinition.lexer;
  }

  try {
    jisonCli.main(options); // Writes the generated parser in the current folder
  } catch (err) {
    console.error('Failed calling jison cli');
    throw err;
  }

  // Remove the concatenated jison file
  deleteFile(parserDefinition.targetJison);

  const generatedFileContents = await readFile(generatedParserFileName);
  const modifiedContents = await parserDefinition.afterParse(generatedFileContents);

  // Write a modified version of the parser to the defined outputFolder
  await writeFile(`${parserDefinition.outputFolder}/${generatedParserFileName}`, modifiedContents);

  // Remove the generated parser
  deleteFile(generatedParserFileName);
};

try {
  console.log('Identifying parsers...');
  const parserDefinitions = await identifySqlParsers();

  const definitionsToGenerate = findParsersToGenerateFromArgs(parserDefinitions);
  const totalParserCount = definitionsToGenerate.length;
  if (totalParserCount > 1) {
    console.log(`Generating ${totalParserCount} parser(s)...`);
  }

  for (let i = 0; i < definitionsToGenerate.length; i++) {
    const parserDefinition = definitionsToGenerate[i];
    console.log(
      `Generating "${parserDefinition.parserName}"${
        definitionsToGenerate.length > 1 ? ` (${i + 1}/${totalParserCount})` : ''
      }...`
    );
    await generateParser(parserDefinition);
  }

  console.log('Done!');
} catch (err) {
  console.log(err);
}
/* eslint-enable no-restricted-syntax */
