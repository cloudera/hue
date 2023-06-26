// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import fs from 'fs';

import { AutocompleteParser } from '../types';

interface TestCase {
  namePrefix: string; // ex. "should suggest keywords"
  beforeCursor: string;
  afterCursor: string;
  containsKeywords?: string[];
  noErrors?: boolean;
  expectedResult: {
    lowerCase?: boolean;
    suggestTables?: {
      identifierChain?: { name: string }[];
      onlyTables?: boolean;
    };
    suggestDatabases?: {
      appendDot?: boolean;
    };
  };
}

interface GroupedTestCases {
  jisonFile: string;
  testCases: TestCase[];
}

/**
 * Finds and parses x.test.json files given a list of jison files.
 * For example, if alter_table.jison is part of the structure it will look for alter_table.test.json, and if it
 * exists it'll parse it (TestCase[]). Test cases are grouped per found .jison file.
 */
export const extractTestCases = (
  jisonFolder: string,
  structureFiles: string[]
): GroupedTestCases[] => {
  const groupedTestCases: GroupedTestCases[] = [];
  structureFiles.forEach(jisonFile => {
    const testFile = `${jisonFolder}/${jisonFile.replace('.jison', '.test.json')}`;
    if (fs.existsSync(testFile)) {
      const fileJson = fs.readFileSync(testFile).toString();
      const testCases: TestCase[] = [];
      JSON.parse(fileJson).forEach((testCase: TestCase) => {
        testCases.push(testCase);
      });
      groupedTestCases.push({ jisonFile, testCases });
    }
  });
  return groupedTestCases;
};

const createAssertForAutocomplete = (
  parser: AutocompleteParser,
  debug = false
): ((testCase: TestCase) => void) => {
  const assertAutocomplete = (testCase: TestCase) => {
    expect(parser.parseSql(testCase.beforeCursor, testCase.afterCursor, debug)).toEqualDefinition(
      testCase
    );
  };
  return assertAutocomplete;
};

const prettyLineBreaks = (text: string): string => text.replace(/\n/g, '\\n').replace(/\r/g, '\\r');

export const runTestCases = (
  autocompleteParser: AutocompleteParser,
  groupedTestCases: GroupedTestCases[],
  debug = false
): void => {
  beforeAll(() => {
    // This guarantees that any parse errors are actually thrown
    (
      autocompleteParser as unknown as { yy: { parseError: (msg?: string) => void } }
    ).yy.parseError = msg => {
      throw Error(msg);
    };
  });

  const assertTestCase = createAssertForAutocomplete(autocompleteParser, debug);

  groupedTestCases.forEach(({ jisonFile, testCases }) => {
    // Each group (jison file) gets its own describe
    describe(jisonFile, () => {
      testCases.forEach(testCase => {
        it(`${testCase.namePrefix} given "${prettyLineBreaks(
          testCase.beforeCursor
        )}|${prettyLineBreaks(testCase.afterCursor)}"`, () => {
          assertTestCase(testCase);
        });
      });
    });
  });
};
