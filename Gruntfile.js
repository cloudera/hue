module.exports = function(grunt) {
  'use strict';

  var config = {};
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Project configuration.
  grunt.initConfig({
    config: config,
    less: {
      responsive: {
        options: {
          paths: ['desktop/core/src/desktop/static/desktop/less'],
          compress: false
        },
        files: {
          'desktop/core/src/desktop/static/desktop/css/hue.css': 'desktop/core/src/desktop/static/desktop/less/hue.less'
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
