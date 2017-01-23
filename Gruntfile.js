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
          'desktop/core/src/desktop/static/desktop/css/hue3-extra.css': 'desktop/core/src/desktop/static/desktop/less/hue3-extra.less'
        }
      }
    },
    watch: {
      less: {
        files: [
          'desktop/core/src/desktop/static/desktop/less/*.less',
          'desktop/core/src/desktop/static/desktop/less/**/*.less'
        ],
        tasks: ['less']
      }
    }
  });
};
