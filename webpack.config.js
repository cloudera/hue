var fs  = require('fs');
var webpack = require('webpack');
var path = require('path');

var jqueryShim = new webpack.ProvidePlugin({
  $: 'jquery',
  jQuery: 'jquery',
  'window.jQuery': 'jquery'
});

// Note that since we are using 'npm install' and stopped using --legacy-bundling,
// we are not ensured which version is installed and where. We will try cloudera-ui
// first, and if it is not there we will let 'require' resolve it. The latter means
// that a version compatible with cloudera-ui and other libraries was installed at the
// top of the node_modules directory.
var lodashDir = path.resolve('node_modules/lodash');
if (!fs.exists(lodashDir)) {
  lodashDir = require.resolve('lodash');
}

module.exports = {
  devtool: 'source-map',
  progress: true,
  host: '0.0.0.0',
  port: '8080',
  resolve: {
    extensions: ['', '.json', '.jsx', '.js'],

    modulesDirectories: [
      'node_modules',
      'js',
      'desktop/core/src/desktop/static/desktop/js/cui'
    ],
    alias: {
      // any bootstrap modules should really resolve to node_modules/bootstrap/js
      bootstrap: 'bootstrap/js',
      'cloudera-ui': 'cui',
      _: 'lodash',
      komapping: 'knockout.mapping',
      'query-command-supported': 'query-command-supported/src/queryCommandSupported',
      pubsub: 'pubsub.js/pubsub',
    }
  },
  entry: {
    hue: ['./desktop/core/src/desktop/static/desktop/js/hue.js']
  },
  output: {
    path: './desktop/core/src/desktop/static/desktop/js',
    filename: 'hue-bundle.js'
  },
  module: {
    loaders: [
      { test: /\.(html)$/, loader: 'html?interpolate&removeComments=false' },
      { test: /\.less$/, loader: 'style-loader!css-loader!less-loader' },
      { test: /\.css$/, loader: 'style-loader!css-loader' },
      { test: /\.(woff2?|ttf|eot|svg)$/, loader: 'file-loader' },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015']
        }
      },

      // expose lodash and jquery for knockout templates to access
      { test: /lodash$/, loader: 'expose?_' },
      { test: /jquery/, loader: 'expose?$!expose?jQuery' },

      // needed for moment-timezone
      { include: /\.json$/, loaders: ['json-loader'] }
    ]
  },

  plugins: [
    new webpack.optimize.UglifyJsPlugin({ compress: { warnings: false } }),
    new webpack.BannerPlugin('\nLicensed to Cloudera, Inc. under one\nor more contributor license agreements.  See the NOTICE file\ndistributed with this work for additional information\nregarding copyright ownership.  Cloudera, Inc. licenses this file\nto you under the Apache License, Version 2.0 (the\n"License"); you may not use this file except in compliance\nwith the License.  You may obtain a copy of the License at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n'),
  ]
};
