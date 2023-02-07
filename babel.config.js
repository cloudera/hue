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

const aceRegex = /.*\/js\/ext\/ace\/ace.js$/;
const parserFileRegex = /.*desktop\/js\/parse\/.*Parser.js$/;

module.exports = function (api) {
  api.cache(true);
  api.assertVersion('^7.4.5');

  const presets = ['babel-preset-typescript-vue3', '@babel/typescript', '@babel/preset-env', '@babel/preset-react'];
  const plugins = [
    [
      'module-resolver',
      {
        root: ['./desktop/core/src/desktop/js']
      }
    ],
    '@babel/plugin-syntax-dynamic-import',
    [
      '@babel/plugin-proposal-decorators',
      {
        legacy: true
      }
    ],
    [
      '@babel/proposal-class-properties',
      {
        loose: true
      }
    ],
    ['@babel/plugin-proposal-private-methods', { loose: true }],
    '@babel/proposal-object-rest-spread'
  ];

  const overrides = [
    {
      test: parserFileRegex,
      compact: false
    },
    {
      test: aceRegex,
      compact: false
    }
  ];
  const env = {
    test: {
      presets: ['@babel/typescript', '@babel/preset-env'],
      plugins: [
        [
          'module-resolver',
          {
            root: ['./desktop/core/src/desktop/js']
          }
        ],
        '@babel/plugin-syntax-dynamic-import'
      ]
    }
  };

  return {
    env,
    overrides,
    presets,
    plugins
  };
};
