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

const fs = require('fs');
const webpack = require('webpack');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const {
  BUNDLES,
  getPluginConfig,
  splitChunksName
} = require('./desktop/core/src/desktop/js/webpack/configUtils');

const config = {
  devtool: 'cheap-source-map',
  entry: {
    hue: { import: './desktop/core/src/desktop/js/hue.js' },
    editor: { import: './desktop/core/src/desktop/js/apps/editor/app.js', dependOn: 'hue' },
    notebook: { import: './desktop/core/src/desktop/js/apps/notebook/app.js', dependOn: 'hue' },
    tableBrowser: {
      import: './desktop/core/src/desktop/js/apps/tableBrowser/app.js',
      dependOn: 'hue'
    },
    jobBrowser: { import: './desktop/core/src/desktop/js/apps/jobBrowser/app.js', dependOn: 'hue' }
  },
  mode: 'development',
  module: {
    rules: [    
      {
        test: /\.vue$/,
        exclude: /node_modules/,
        use: 'vue-loader'
      },
      {
        test: /\.(jsx?|tsx?)$/,
        exclude: /node_modules/,
        use: [{
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }] 
      },
      {
        test: /\.(jsx?|tsx?)$/,
        enforce: "pre",
        use: ["source-map-loader"],
      },      
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        use: ['style-loader', 'css-loader', 'sass-loader']
      },
      {
        test: /\.less$/i,
        use: [
          { loader: "style-loader" },
          { loader: "css-loader" },
          {
              loader: "less-loader",
              options: {
                  lessOptions: {
                      // This is not ideal but required by antd library
                      javascriptEnabled: true,
                  }
              }
          }          
        ],
      },      
      {
        test: /\.html$/,
        exclude: /node_modules/,
        use: { loader: 'html', options: { interpolater: true, removeComments: false } }
      }
    ]
  },
  optimization: {
    minimize: false,
    splitChunks: {
      chunks: 'all',
      name: splitChunksName,
      maxSize: 1000000,
      hidePathInfo: true
    }
  },
  output: {
    path: __dirname + '/desktop/core/src/desktop/static/desktop/js/bundles/hue',
    filename: '[name]-bundle-[fullhash].js',
    chunkFilename: '[name]-chunk-[fullhash].js',
    clean: true,
    devtoolModuleFilenameTemplate(info) {
      // Prevents absolute paths in the generated sourceMaps
      return `webpack:///${info.resourcePath.replace(__dirname, '.')}`;
    }
  },
  performance: {
    maxEntrypointSize: 400 * 1024, // 400kb
    maxAssetSize: 400 * 1024 // 400kb
  },
  plugins: getPluginConfig(BUNDLES.HUE).concat([
    // Needed to wrap antd and prevent it from affecting global styles
    new webpack.NormalModuleReplacementPlugin( /node_modules\/antd\/lib\/style\/index\.less/, `${__dirname}/desktop/core/static/desktop/less/root-wrapped-antd.less`),
    new CleanWebpackPlugin([`${__dirname}/desktop/core/src/desktop/static/desktop/js/bundles/hue`]),    
  ]),
  resolve: {
    extensions: ['.json', '.jsx', '.js', '.tsx', '.ts', '.vue'],
    modules: ['node_modules', 'js'],
    alias: {
      bootstrap: __dirname + '/node_modules/bootstrap-2.3.2/js',
      vue$: __dirname + '/node_modules/vue/dist/vue.esm-browser.prod.js'
    }
  }
};

// To customize build configurations
const EXTEND_CONFIG_FILE = './webpack.config.extend.js';
if (fs.existsSync(EXTEND_CONFIG_FILE)) {
  const endedConfig = require(EXTEND_CONFIG_FILE);
  endedConfig(config);
  console.info('Webpack extended!');
}

module.exports = config;
