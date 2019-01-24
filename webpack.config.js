var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var WebpackShellPlugin = require('webpack-shell-plugin');

new webpack.ProvidePlugin({
  $: 'jquery',
  jQuery: 'jquery',
  'window.jQuery': 'jquery'
});

module.exports = {
  devtool: 'source-map',
  mode: 'development',
  optimization: {
    minimize: true
  },
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
      bootstrap: 'bootstrap/js',
      'cloudera-ui': 'cui',
      _: 'lodash',
      komapping: 'knockout.mapping',
      'query-command-supported': 'query-command-supported/src/queryCommandSupported',
      pubsub: 'pubsub.js/pubsub',
    }
  },
  entry: {
    hue: ['./desktop/core/src/desktop/js/hue.js']
  },
  output: {
    path:  __dirname + '/desktop/core/src/desktop/static/desktop/js',
    filename: 'hue-bundle-[hash].js'
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
      // expose lodash and jquery for knockout templates to access
      { test: /lodash$/, loader: 'expose-loader?_' },
      { test: /jquery/, loader: 'expose-loader?$!expose-loader?jQuery' },

      // needed for moment-timezone
      { include: /\.json$/, loaders: ['json-loader'] }
    ]
  },

  plugins: [
    new WebpackShellPlugin({ onBuildStart:[__dirname + '/tools/scripts/clean_js_bundles.sh ' +  __dirname ] }),
    new BundleTracker({ filename: './webpack-stats.json' }),
    new webpack.BannerPlugin('\nLicensed to Cloudera, Inc. under one\nor more contributor license agreements.  See the NOTICE file\ndistributed with this work for additional information\nregarding copyright ownership.  Cloudera, Inc. licenses this file\nto you under the Apache License, Version 2.0 (the\n"License"); you may not use this file except in compliance\nwith the License.  You may obtain a copy of the License at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n'),
  ]
};