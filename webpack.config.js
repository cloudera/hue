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

const { BUNDLES, getPluginConfig } = require('./desktop/core/src/desktop/js/webpack/configUtils');

module.exports = {
  devtool: false,
  entry: {
    hue: ['./desktop/core/src/desktop/js/hue.js'],
    notebook: ['./desktop/core/src/desktop/js/apps/notebook/app.js'],
    tableBrowser: ['./desktop/core/src/desktop/js/apps/tableBrowser/app.js'],
    jobBrowser: ['./desktop/core/src/desktop/js/apps/jobBrowser/app.js']
  },
  mode: 'development',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
      { test: /\.js$/, use: ['source-map-loader'], enforce: 'pre' },
      { test: /\.(html)$/, loader: 'html?interpolate&removeComments=false' },
      { test: /\.less$/, loader: 'style-loader!css-loader!less-loader' },
      { test: /\.s[ac]ss$/, loader: 'style-loader!css-loader!sass-loader' },
      { test: /\.css$/, loader: 'style-loader!css-loader' },
      { test: /\.(woff2?|ttf|eot|svg)$/, loader: 'file-loader' },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          shadowMode: true,
          loaders: {
            less: ['vue-style-loader', 'css-loader', 'less-loader', 'sass-loader']
          }
        }
      }
    ]
  },
  optimization: {
    //minimize: true,
    minimize: false,
    splitChunks: {
      chunks: 'all'
    },
    runtimeChunk: {
      name: 'hue'
    }
  },
  output: {
    path: __dirname + '/desktop/core/src/desktop/static/desktop/js/bundles/hue',
    filename: '[name]-bundle-[hash].js',
    chunkFilename: '[name]-chunk-[hash].js'
  },
  performance: {
    maxEntrypointSize: 400 * 1024, // 400kb
    maxAssetSize: 400 * 1024 // 400kb
  },
  plugins: getPluginConfig(BUNDLES.HUE),
  resolve: {
    extensions: ['.json', '.jsx', '.js', '.tsx', '.ts', '.vue'],
    modules: ['node_modules', 'js'],
    alias: {
      bootstrap: __dirname + '/node_modules/bootstrap-2.3.2/js',
      vue$: __dirname + '/node_modules/vue/dist/vue.esm.browser.min.js'
    }
  }
};
