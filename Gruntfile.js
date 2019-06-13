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
          compress: true,
          banner: '/*!\nLicensed to Cloudera, Inc. under one\nor more contributor license agreements.  See the NOTICE file\ndistributed with this work for additional information\nregarding copyright ownership.  Cloudera, Inc. licenses this file\nto you under the Apache License, Version 2.0 (the\n"License"); you may not use this file except in compliance\nwith the License.  You may obtain a copy of the License at\n\nhttp://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n */',
          javascriptEnabled: true
        },
        files: {
          'desktop/core/src/desktop/static/desktop/css/hue-bootstrap-embedded.css': 'desktop/core/src/desktop/static/desktop/less/hue-bootstrap-embedded.less',
          'desktop/core/src/desktop/static/desktop/css/hue-embedded.css': 'desktop/core/src/desktop/static/desktop/less/hue-embedded.less',
          'desktop/core/src/desktop/static/desktop/css/home.css': 'desktop/core/src/desktop/static/desktop/less/home.less',
          'desktop/core/src/desktop/static/desktop/css/hue.css': 'desktop/core/src/desktop/static/desktop/less/hue.less',
          'desktop/core/src/desktop/static/desktop/css/hue3-extra.css': 'desktop/core/src/desktop/static/desktop/less/hue3-extra.less',
          'desktop/core/src/desktop/static/desktop/css/login.css': 'desktop/core/src/desktop/static/desktop/less/login.less',
          'desktop/core/src/desktop/static/desktop/css/login4.css': 'desktop/core/src/desktop/static/desktop/less/login4.less',
          'desktop/core/src/desktop/static/desktop/css/httperrors.css': 'desktop/core/src/desktop/static/desktop/less/httperrors.less',
          'apps/metastore/src/metastore/static/metastore/css/metastore.css': 'apps/metastore/src/metastore/static/metastore/less/metastore.less',
          'desktop/libs/notebook/src/notebook/static/notebook/css/notebook.css': 'desktop/libs/notebook/src/notebook/static/notebook/less/notebook.less',
          'desktop/libs/notebook/src/notebook/static/notebook/css/notebook-layout.css': 'desktop/libs/notebook/src/notebook/static/notebook/less/notebook-layout.less',
          'apps/oozie/src/oozie/static/oozie/css/workflow-editor.css': 'apps/oozie/src/oozie/static/oozie/less/workflow-editor.less',
          'apps/oozie/src/oozie/static/oozie/css/workflow.css': 'apps/oozie/src/oozie/static/oozie/less/workflow.less',
          'apps/oozie/src/oozie/static/oozie/css/common-editor.css': 'apps/oozie/src/oozie/static/oozie/less/common-editor.less',
          'apps/oozie/src/oozie/static/oozie/css/coordinator.css': 'apps/oozie/src/oozie/static/oozie/less/coordinator.less',
          'apps/oozie/src/oozie/static/oozie/css/coordinator-editor.css': 'apps/oozie/src/oozie/static/oozie/less/coordinator-editor.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/css/admin.css': 'desktop/libs/dashboard/src/dashboard/static/dashboard/less/admin.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/css/admin_mobile.css': 'desktop/libs/dashboard/src/dashboard/static/dashboard/less/admin_mobile.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/css/common_dashboard.css': 'desktop/libs/dashboard/src/dashboard/static/dashboard/less/common_dashboard.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/css/search.css': 'desktop/libs/dashboard/src/dashboard/static/dashboard/less/search.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/css/search_mobile.css': 'desktop/libs/dashboard/src/dashboard/static/dashboard/less/search_mobile.less',
          'apps/filebrowser/src/filebrowser/static/filebrowser/css/display.css': 'apps/filebrowser/src/filebrowser/static/filebrowser/less/display.less',
          'apps/filebrowser/src/filebrowser/static/filebrowser/css/listdir_components.css': 'apps/filebrowser/src/filebrowser/static/filebrowser/less/listdir_components.less',
          'apps/jobbrowser/src/jobbrowser/static/jobbrowser/css/jobbrowser.css': 'apps/jobbrowser/src/jobbrowser/static/jobbrowser/less/jobbrowser.less',
          'apps/jobbrowser/src/jobbrowser/static/jobbrowser/css/jobbrowser-embeddable.css': 'apps/jobbrowser/src/jobbrowser/static/jobbrowser/less/jobbrowser-embeddable.less',
          'apps/useradmin/src/useradmin/static/useradmin/css/useradmin.css': 'apps/useradmin/src/useradmin/static/useradmin/less/useradmin.less',
          'apps/hbase/src/hbase/static/hbase/css/hbase.css': 'apps/hbase/src/hbase/static/hbase/less/hbase.less',
          'apps/security/src/security/static/security/css/security.css': 'apps/security/src/security/static/security/less/security.less',
          'apps/sqoop/src/sqoop/static/sqoop/css/sqoop.css': 'apps/sqoop/src/sqoop/static/sqoop/less/sqoop.less',
          'desktop/libs/indexer/src/indexer/static/indexer/css/indexes.css': 'desktop/libs/indexer/src/indexer/static/indexer/less/indexes.less',
          'desktop/libs/indexer/src/indexer/static/indexer/css/importer.css': 'desktop/libs/indexer/src/indexer/static/indexer/less/importer.less'
        }
      }
    },
    watch: {
      options: {
        atBegin: true
      },
      less: {
        files: [
          'desktop/core/src/desktop/static/desktop/less/*.less',
          'desktop/core/src/desktop/static/desktop/less/**/*.less',
          'apps/metastore/src/metastore/static/metastore/less/*.less',
          'apps/metastore/src/metastore/static/metastore/less/**/*.less',
          'desktop/libs/notebook/src/notebook/static/notebook/less/*.less',
          'desktop/libs/notebook/src/notebook/static/notebook/less/**/*.less',
          'apps/oozie/src/oozie/static/oozie/less/*.less',
          'apps/oozie/src/oozie/static/oozie/less/**/*.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/less/*.less',
          'desktop/libs/dashboard/src/dashboard/static/dashboard/less/**/*.less',
          'apps/filebrowser/src/filebrowser/static/filebrowser/less/*.less',
          'apps/filebrowser/src/filebrowser/static/filebrowser/less/**/*.less',
          'apps/jobbrowser/src/jobbrowser/static/jobbrowser/less/*.less',
          'apps/jobbrowser/src/jobbrowser/static/jobbrowser/less/**/*.less',
          'apps/useradmin/src/useradmin/static/useradmin/less/*.less',
          'apps/useradmin/src/useradmin/static/useradmin/less/**/*.less',
          'apps/hbase/src/hbase/static/hbase/less/*.less',
          'apps/hbase/src/hbase/static/hbase/less/**/*.less',
          'apps/security/src/security/static/security/less/*.less',
          'apps/security/src/security/static/security/less/**/*.less',
          'apps/sqoop/src/sqoop/static/sqoop/less/*.less',
          'apps/sqoop/src/sqoop/static/sqoop/less/**/*.less'
        ],
        tasks: ['less']
      }
    },
  });
};