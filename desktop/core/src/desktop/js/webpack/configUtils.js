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

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const RelativeBundleTracker = require('./relativeBundleTracker');
const AdjustMapPathsPlugin = require('./AdjustMapPathsPlugin');
const webpack = require('webpack');
const { VueLoaderPlugin } = require('vue-loader');

const BUNDLES = {
  HUE: 'hue',
  LOGIN: 'login',
  WORKERS: 'workers'
};

const getPluginConfig = (name, withAnalyzer) => {
  const plugins = [
    new webpack.ProgressPlugin(),
    new RelativeBundleTracker({
      path: '.',
      filename: `webpack-stats${name !== BUNDLES.HUE ? '-' + name : ''}.json`
    }),
    new webpack.BannerPlugin(
      '\nLicensed to Cloudera, Inc. under one\nor more contributor license agreements.  See the NOTICE file\ndistributed with this work for additional information\nregarding copyright ownership.  Cloudera, Inc. licenses this file\nto you under the Apache License, Version 2.0 (the\n"License"); you may not use this file except in compliance\nwith the License.  You may obtain a copy of the License at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n'
    ),
    new AdjustMapPathsPlugin()
  ];
  if (withAnalyzer) {
    plugins.push(new BundleAnalyzerPlugin({ analyzerPort: 9000 }));
  }
  if (name !== BUNDLES.WORKERS) {
    plugins.push(new VueLoaderPlugin());
  }
  return plugins;
};

const hashCode = str => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0;
  }
  return hash;
};

/**
 * @param {webpack.Module} module
 * @param {Set<compilation.Chunk>} chunks
 * @param {string} cacheGroupKey
 * @return {string}
 */
const splitChunksName = (module, chunks, cacheGroupKey) => {
  let fullName = cacheGroupKey !== 'default' ? cacheGroupKey + '~' : '';
  fullName += [...chunks].map(item => item.name).join('~');
  if (fullName.length > 75) {
    return fullName.slice(0, 65).replace(/~[^~]*$/, '') + '~' + hashCode(fullName);
  }
  return fullName;
};

module.exports = {
  BUNDLES: BUNDLES,
  getPluginConfig: getPluginConfig,
  splitChunksName: splitChunksName
};
