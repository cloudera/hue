/*jshint node:true*/
/* global require, module */
/*
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */

var Funnel = require("broccoli-funnel");
var EmberApp = require('ember-cli/lib/broccoli/ember-app');
var MergeTrees = require('broccoli-merge-trees');

module.exports = function(defaults) {
  var app = new EmberApp(defaults, {
    // Add options here
    storeConfigInMeta: false,

    bootstrap: {
      // List of Bootstrap plugins to use
      plugins: ['dropdown']
    },
    SRI: {
      enabled: false
    },
    fingerprint: {
      enabled: process.env.EMBER_ENV == "production",
      exclude: ["png", "ico"]
    },
    minifyCSS: {
      enabled: false
    },
    codemirror: {
      modes: ['sql'],
      themes: ['solarized'],
      addons: ['merge']
    }
  });

  var configEnv = new Funnel('config', {
     srcDir: '/',
     include: ['*.env'],
     destDir: '/config'
  });
  var copyFonts = new Funnel('bower_components/font-awesome/', {
     srcDir: '/fonts',
     include: ['*.*'],
     destDir: '/fonts'
  });


  // Use `app.import` to add additional libraries to the generated
  // output files.
  //
  // If you need to use different assets in different
  // environments, specify an object as the first parameter. That
  // object's keys should be the environment name and the values
  // should be the asset to use in that environment.
  //
  // If the library that you are including contains AMD or ES6
  // modules that you would like to import into your application
  // please specify an object with the list of modules as keys
  // along with the exports of each module as its value.

  // Visualization libraries
  app.import('bower_components/d3/d3.js');
  app.import('bower_components/webcola/WebCola/cola.min.js');

  // JQuery
  app.import('bower_components/jquery-ui/jquery-ui.js');
  app.import('bower_components/jquery-ui/ui/tooltip.js');
  app.import('bower_components/jquery-ui/themes/base/jquery-ui.css');

  // More js
  app.import('bower_components/more-js/dist/more.js');

  // File downloader
  app.import('bower_components/file-saver.js/FileSaver.js');

  // Code mirror
  app.import('bower_components/codemirror/lib/codemirror.js');
  app.import('bower_components/codemirror/mode/sql/sql.js');
  app.import('bower_components/codemirror/addon/hint/sql-hint.js');
  app.import('bower_components/codemirror/addon/hint/show-hint.js');
  app.import('bower_components/codemirror/lib/codemirror.css');
  app.import('bower_components/codemirror/addon/hint/show-hint.css');
  app.import('bower_components/codemirror/addon/merge/merge.js');
  app.import('bower_components/codemirror/addon/merge/merge.css');

  //AlaSQL
  app.import('bower_components/alasql/dist/alasql.js');
  app.import('bower_components/sql-formatter/dist/sql-formatter.min.js');

  //Date time piker
  app.import('bower_components/smalot-bootstrap-datetimepicker/js/bootstrap-datetimepicker.min.js');
  app.import('bower_components/smalot-bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css');
  return app.toTree(new MergeTrees([configEnv, copyFonts]));
};
