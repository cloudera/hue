/*
 * This file was originally copied from Apache Ambari and has been modified. The modifications are subject to the
 * following provisions.
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

import Ember from 'ember';

import LoaderAdapter from './loader';
import ENV from '../config/environment';

export default LoaderAdapter.extend({
  serverName: null, //Must be set by inheriting classes

  host: Ember.computed("serverName", function () {
    var serverName = this.get("serverName");
    return this.get(`env.app.hosts.${serverName}`);
  }),
  namespace: Ember.computed("serverName", function () {
    var serverName = this.get("serverName");
    var prefix = serverName == "studio" ? ENV.rootURL + '/' : '';
    return prefix + this.get(`env.app.namespaces.webService.${serverName}`);
  }),
  pathTypeHash: Ember.computed("serverName", function () {
    var serverName = this.get("serverName");
    return this.get(`env.app.paths.${serverName}`);
  }),

  ajaxOptions: function(url, method, options) {
    options = options || {};
    options.crossDomain = true;
    options.xhrFields = {
      withCredentials: true
    };
    options.targetServer = this.get('serverName');
    return this._super(url, method, options);
  },

  pathForType: function(type) {
    var serverName = this.get("serverName"),
        path = this.get("pathTypeHash")[type];
    Ember.assert(`Path not found for type:${type} to server:${serverName}`, path);
    return path;
  },

  normalizeErrorResponse: function (status, headers, payload) {
    var title;
    switch(typeof payload) {
      case "object":
        title = payload.message;
      break;
      case "string":
        let html = Ember.$(payload.bold());
        html.find('script').remove();
        html.find('style').remove();
        payload = html.text().trim();
      break;
    }

    return [{
      title: title,
      status: status,
      headers: headers,
      detail: payload
    }];
  },

  _loaderAjax: function (url, queryParams, namespace) {
    var requestInfo = {
          adapterName: this.get("name"),
          url: url
        },
        that = this;

    return this._super(url, queryParams, namespace).catch(function (error) {
      var message = `${error.message} »`,
          status = Ember.get(error, "errors.0.status");

      if(status === 0) {
        let outOfReachMessage = that.get("outOfReachMessage");
        message = `${message} ${outOfReachMessage}`;
      }
      else {
        let title = Ember.get(error, "errors.0.title") || `Error accessing ${url}`;
        message = `${message} ${status}: ${title}`;
      }

      requestInfo.responseHeaders = Ember.get(error, "errors.0.headers");
      if(queryParams) {
        requestInfo.queryParams = queryParams;
      }
      if(namespace) {
        requestInfo.namespace = namespace;
      }

      Ember.setProperties(error, {
        message: message,
        details: Ember.get(error, "errors.0.detail"),
        requestInfo: requestInfo
      });

      throw(error);
    });
  }
});
