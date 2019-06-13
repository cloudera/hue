const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CleanObsoleteChunks = require('webpack-clean-obsolete-chunks');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

const path = require('path')
const each = require('lodash/fp/each')

// https://github.com/ezhome/webpack-bundle-tracker/issues/25
class RelativeBundleTracker extends BundleTracker {
  convertPathChunks(chunks){
    each(each(chunk => {
      chunk.path = path.relative(this.options.path, chunk.path)
    }))(chunks)
  }
  writeOutput(compiler, contents) {
    if (contents.status === 'done')  {
      this.convertPathChunks(contents.chunks)
    }

    super.writeOutput(compiler, contents)
  }
}


module.exports = {
  devtool: 'source-map',
  mode: 'development',
  performance: {
    maxEntrypointSize: 400 * 1024, // 400kb
    maxAssetSize: 400 * 1024 // 400kb
  },
  resolve: {
    extensions: ['.json', '.jsx', '.js'],
    modules: [
      'node_modules',
      'js'
    ],
    alias: {
      'bootstrap': __dirname + '/node_modules/bootstrap-2.3.2/js'
    }
  },
  entry: {
    login: ['./desktop/core/src/desktop/js/login.js']
  },
  optimization: {
    minimize: true,
  },
  output: {
    path:  __dirname + '/desktop/core/src/desktop/static/desktop/js/bundles/login',
    filename: '[name]-bundle-[hash].js'
  },
  module: {
    rules: [
      { test: /\.(html)$/, loader: 'html?interpolate&removeComments=false' },
      { test: /\.less$/, loader: 'style-loader!css-loader!less-loader' },
      { test: /\.css$/, loader: 'style-loader!css-loader' },
      { test: /\.(woff2?|ttf|eot|svg)$/, loader: 'file-loader' },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
      { include: /\.json$/, loaders: ['json-loader'] }
    ]
  },

  plugins: [
    // new BundleAnalyzerPlugin({ analyzerPort: 9000 }),
    new CleanObsoleteChunks(),
    new CleanWebpackPlugin([__dirname + '/desktop/core/src/desktop/static/desktop/js/bundles/login']),
    new RelativeBundleTracker({path: '.', filename: "webpack-stats-login.json"}),
    new webpack.BannerPlugin('\nLicensed to Cloudera, Inc. under one\nor more contributor license agreements.  See the NOTICE file\ndistributed with this work for additional information\nregarding copyright ownership.  Cloudera, Inc. licenses this file\nto you under the Apache License, Version 2.0 (the\n"License"); you may not use this file except in compliance\nwith the License.  You may obtain a copy of the License at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n')
  ]
};
