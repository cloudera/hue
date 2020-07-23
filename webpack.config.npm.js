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

const { VueLoaderPlugin } = require('vue-loader');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const webpackConfig = require('./webpack.config');

const distDir = `${__dirname}/npm_dist`;

module.exports = Object.assign({}, webpackConfig, {
  entry: {
    'er-diagram': ['./desktop/core/src/desktop/js/components/er-diagram/webcomp.ts']
  },
  mode: 'production',
  optimization: {
    minimize: true
  },
  output: {
    path: `${distDir}/web`
  },
  plugins: [
    new CleanWebpackPlugin([distDir]),
    new VueLoaderPlugin(),
    new CopyWebpackPlugin({
      patterns: [
        {from:'./package.json', to: `${distDir}/`},
        {from:'./NPM-README.md', to: `${distDir}/README.md`},

        {from:'./desktop/core/src/desktop/js/components', to: `${distDir}/components`},
        {from:'./desktop/core/src/desktop/js/utils/hueUtils.js', to: `${distDir}/utils/hueUtils.js`},

        {from:'./desktop/core/src/desktop/js/parse', to: `${distDir}/parse`},
        {from:'./desktop/core/src/desktop/js/sql', to: `${distDir}/sql`},
      ]
    })
  ]
});
