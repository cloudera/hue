/*
 Licensed to Cloudera, Inc. under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  Cloudera, Inc. licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

module.exports = function(grunt) {
  'use strict';

  var config = {};
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Project configuration.
  grunt.initConfig({
    config: config,
    less: {
      hue: {
        options: {
          paths: ['desktop/core/src/desktop/static/desktop/less'],
          compress: false
        },
        files: {
          'desktop/core/src/desktop/static/desktop/css/hue.css': 'desktop/core/src/desktop/static/desktop/less/hue.less',
          'desktop/core/src/desktop/static/desktop/css/hue3-extra.css': 'desktop/core/src/desktop/static/desktop/less/hue3-extra.less',
          'apps/metastore/src/metastore/static/metastore/css/metastore.css': 'apps/metastore/src/metastore/static/metastore/less/metastore.less',
          'desktop/libs/notebook/src/notebook/static/notebook/css/notebook.css': 'desktop/libs/notebook/src/notebook/static/notebook/less/notebook.less',
          'desktop/libs/notebook/src/notebook/static/notebook/css/notebook-layout.css': 'desktop/libs/notebook/src/notebook/static/notebook/less/notebook-layout.less'
        }
      }
    },
    watch: {
      less: {
        files: [
          'desktop/core/src/desktop/static/desktop/less/*.less',
          'desktop/core/src/desktop/static/desktop/less/**/*.less',
          'apps/metastore/src/metastore/static/metastore/less/*.less',
          'apps/metastore/src/metastore/static/metastore/less/**/*.less',
          'desktop/libs/notebook/src/notebook/static/notebook/less/*.less',
          'desktop/libs/notebook/src/notebook/static/notebook/less/**/*.less'
        ],
        tasks: ['less']
      }
    }
  });
};
