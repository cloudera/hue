var fs  = require('fs');
var webpack = require('webpack');
var path = require('path');

var jqueryShim = new webpack.ProvidePlugin({
  $: 'jquery',
  jQuery: 'jquery',
  'window.jQuery': 'jquery'
});

var PROD = JSON.parse(process.env.PROD_ENV || '0');

var plugins = [];

if (PROD) {
  plugins.push(new webpack.optimize.UglifyJsPlugin({ compress: { warnings: false } }));
}

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
      pubsub: 'pubsub.js/pubsub'
    }
  },
  entry: {
    cui: ['./desktop/core/src/desktop/static/desktop/js/cui.js']
  },
  output: {
    path: './desktop/core/src/desktop/static/desktop/js',
    filename: 'cui-bundle.js'
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

  plugins: plugins
};
