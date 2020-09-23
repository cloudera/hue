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

const CleanWebpackPlugin = require('clean-webpack-plugin');
const {
  BUNDLES,
  getPluginConfig,
  splitChunksName
} = require('./desktop/core/src/desktop/js/webpack/configUtils');
const shared = require('./webpack.config');

module.exports = {
  devtool: shared.devtool,
  entry: {
    login: ['./desktop/core/src/desktop/js/login.js']
  },
  mode: shared.mode,
  module: shared.module,
  performance: shared.performance,
  optimization: {
    minimize: true,
    splitChunks: {
      name: splitChunksName
    }
  },
  output: {
    path: __dirname + '/desktop/core/src/desktop/static/desktop/js/bundles/login',
    filename: shared.output.filename
  },
  plugins: getPluginConfig(BUNDLES.LOGIN).concat([
    new CleanWebpackPlugin([
      `${__dirname}/desktop/core/src/desktop/static/desktop/js/bundles/login`
    ])
  ]),
  resolve: shared.resolve
};
