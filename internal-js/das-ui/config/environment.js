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

const DEFAULT_APP_CONF = require('./default-app-conf');

module.exports = function(environment) {
  var ENV = {
    modulePrefix: 'hivestudio',
    environment: environment,
    locationType: 'hash',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      },
      EXTEND_PROTOTYPES: {
        // Prevent Ember Data from overriding Date.parse.
        Date: false
      }
    },

    APP: DEFAULT_APP_CONF,

    contentSecurityPolicy: {
      'connect-src': "* 'self'",
      'child-src': "'self' 'unsafe-inline'",
      'style-src': "'self' 'unsafe-inline'",
      'script-src': "'self' 'unsafe-eval' 'unsafe-inline'"
    }

  };


  ENV.APP.DASLITE = process.env.DASLITE=="true";

  ENV.APP.DISABLE_UDF_SETTINGS = true;

  if (environment === 'development') {
    // ENV.APP.LOG_RESOLVER = true;
    // ENV.APP.LOG_ACTIVE_GENERATION = true;
    // ENV.APP.LOG_TRANSITIONS = true;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = true;
    // ENV.APP.LOG_VIEW_LOOKUPS = true;

    // Change the value to false to prevent the service checks. This is required in development mode
    // as service checks take up time and hence increase the overall development time.
    ENV.APP.SHOULD_PERFORM_SERVICE_CHECK = false;

    ENV.rootURL = '';
    // Use this value if you want to test das behind knox gateway with ember server --proxy
    // ENV.rootURL = '/gateway/ui/das';
  }
  if (environment === 'test') {
    // Testem prefers this...
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';
  }

  if (environment === 'production') {
    /* We use a value '/dasroot/..' which forms a unique string to be replaced
       by knox, in normal case browser takes care of converting this into the
       equivalent '/' */
    ENV.rootURL = '/dasroot/..';
  }

  if (environment === 'dp-production') {
    ENV.rootURL = '/das';
  }

  if (environment === 'test') {
    ENV.rootURL = '/';
  }

  ENV.i18n = {
    defaultLocale: 'en'
  };

  ENV.APP.SHOULD_AUTO_REFRESH_TABLES = true;
  ENV.APP.SHOULD_AUTO_REFRESH_DATABASES = true;
  ENV.APP.SHOULD_AUTO_REFRESH_REPL_INFO = true;

  return ENV;
};
