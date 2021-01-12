/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const path = require('path');
const { VueLoaderPlugin } = require('vue-loader');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const DIST_DIR = path.join(__dirname, 'npm_dist');
const JS_ROOT = path.join(__dirname, '/desktop/core/src/desktop/js');

const defaultConfig = Object.assign({}, require('./webpack.config'), {
  mode: 'production',
  optimization: {
    minimize: true
  },
  plugins: []
});

const npmSetupPlugins = [
  new CleanWebpackPlugin([DIST_DIR]),
  new CopyWebpackPlugin({
    patterns: [
      { from: './package.json', to: `${DIST_DIR}/package.json` },
      { from: './NPM-README.md', to: `${DIST_DIR}/README.md` },

      { from: JS_ROOT, to: `${DIST_DIR}/src` }
    ]
  })
];

const webComponentsConfig = Object.assign({}, defaultConfig, {
  entry: {
    'er-diagram': [`${JS_ROOT}/components/er-diagram/webcomp.ts`],
    'query-editor': [`${JS_ROOT}/apps/editor/components/aceEditor/QueryEditorWebComponent.ts`]
  },
  output: {
    path: `${DIST_DIR}/components`
  },
  plugins: npmSetupPlugins.concat(new VueLoaderPlugin())
});

const parserConf = Object.assign({}, defaultConfig, {
  entry: {
    calciteAutocompleteParser: [`${JS_ROOT}/parse/sql/calcite/calciteAutocompleteParser.js`],
    calciteSyntaxParser: [`${JS_ROOT}/parse/sql/calcite/calciteSyntaxParser.js`],

    druidAutocompleteParser: [`${JS_ROOT}/parse/sql/druid/druidAutocompleteParser.js`],
    druidSyntaxParser: [`${JS_ROOT}/parse/sql/druid/druidSyntaxParser.js`],

    elasticsearchAutocompleteParser: [
      `${JS_ROOT}/parse/sql/elasticsearch/elasticsearchAutocompleteParser.js`
    ],
    elasticsearchSyntaxParser: [`${JS_ROOT}/parse/sql/elasticsearch/elasticsearchSyntaxParser.js`],

    flinkAutocompleteParser: [`${JS_ROOT}/parse/sql/flink/flinkAutocompleteParser.js`],
    flinkSyntaxParser: [`${JS_ROOT}/parse/sql/flink/flinkSyntaxParser.js`],

    genericAutocompleteParser: [`${JS_ROOT}/parse/sql/generic/genericAutocompleteParser.js`],
    genericSyntaxParser: [`${JS_ROOT}/parse/sql/generic/genericSyntaxParser.js`],

    hiveAutocompleteParser: [`${JS_ROOT}/parse/sql/hive/hiveAutocompleteParser.js`],
    hiveSyntaxParser: [`${JS_ROOT}/parse/sql/hive/hiveSyntaxParser.js`],

    impalaAutocompleteParser: [`${JS_ROOT}/parse/sql/impala/impalaAutocompleteParser.js`],
    impalaSyntaxParser: [`${JS_ROOT}/parse/sql/impala/impalaSyntaxParser.js`],

    ksqlAutocompleteParser: [`${JS_ROOT}/parse/sql/ksql/ksqlAutocompleteParser.js`],
    ksqlSyntaxParser: [`${JS_ROOT}/parse/sql/ksql/ksqlSyntaxParser.js`],

    phoenixAutocompleteParser: [`${JS_ROOT}/parse/sql/phoenix/phoenixAutocompleteParser.js`],
    phoenixSyntaxParser: [`${JS_ROOT}/parse/sql/phoenix/phoenixSyntaxParser.js`],

    prestoAutocompleteParser: [`${JS_ROOT}/parse/sql/presto/prestoAutocompleteParser.js`],
    prestoSyntaxParser: [`${JS_ROOT}/parse/sql/presto/prestoSyntaxParser.js`],

    dasksqlAutocompleteParser: [`${JS_ROOT}/parse/sql/dasksql/dasksqlAutocompleteParser.js`],
    dasksqlSyntaxParser: [`${JS_ROOT}/parse/sql/dasksql/dasksqlSyntaxParser.js`]
  },
  performance: {
    hints: false,
    maxEntrypointSize: 1500000,
    maxAssetSize: 1500000
  },
  output: {
    path: `${DIST_DIR}/parsers`,
    library: '[name]',
    libraryExport: 'default',
    libraryTarget: 'umd',
    umdNamedDefine: true,
    globalObject: `(typeof self !== 'undefined' ? self : this)`
  }
});

module.exports = [webComponentsConfig, parserConf];
