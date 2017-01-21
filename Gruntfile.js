module.exports = function(grunt) {
  'use strict';

  var config = {};
  grunt.loadNpmTasks('grunt-contrib-less');

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
          'desktop/core/src/desktop/static/desktop/css/responsive.css': 'desktop/core/src/desktop/static/desktop/less/responsive.less'
        }
      }
    }
  });
};
