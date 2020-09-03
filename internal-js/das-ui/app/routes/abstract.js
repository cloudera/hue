/*
 * This file was originally copied from Apache Tez and has been modified. The modifications are subject to the
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
import DS from 'ember-data';

import LoaderService from '../services/loader';
import UnlinkedPromise from '../errors/unlinked-promise';
import NameMixin from '../mixins/name';

var MoreObject = more.Object;

export default Ember.Route.extend(NameMixin, {
  title: null, // Must be set by inheriting class

  loaderNamespace: null,
  isLoading: false,
  currentPromiseId: null,
  loadedValue: null,

  isLeafRoute: false,
  breadcrumbs: null,
  childCrumbs: null,

  currentQuery: {},

  loaderQueryParams: {},

  init: function () {
    var namespace = this.get("loaderNamespace");
    if(namespace) {
      this.setLoader(namespace);
    }
  },

  model: function(params/*, transition*/) {
    this.set("currentQuery", this.queryFromParams(params));
    Ember.run.later(this, "loadData");
  },

  queryFromParams: function (params) {
    var query = {};

    MoreObject.forEach(this.get("loaderQueryParams"), function (name, paramKey) {
      var value = Ember.get(params, paramKey);
      if(value) {
        query[name] = value;
      }
    });

    return query;
  },

  setDocTitle: function () {
    //Ember.$(document).attr('title', "Tez UI : " + this.get('title'));
  },

  setupController: function (controller, model) {
    this._super(controller, model);
    this.setDocTitle();
  },

  checkAndCall: function (id, functionName, query, options, value) {
    if(id === this.get("currentPromiseId")) {
      return this[functionName](value, query, options);
    }
    else {
      throw new UnlinkedPromise();
    }
  },

  loadData: function (options) {
    var promiseId = Math.random(),
        query = this.get("currentQuery");

    options = options || {};

    this.set('currentPromiseId', promiseId);

    return Ember.RSVP.resolve().
      then(this.checkAndCall.bind(this, promiseId, "setLoading", query, options)).
      then(this.checkAndCall.bind(this, promiseId, "beforeLoad", query, options)).
      then(this.checkAndCall.bind(this, promiseId, "load", query, options)).
      then(this.checkAndCall.bind(this, promiseId, "afterLoad", query, options)).
      then(this.checkAndCall.bind(this, promiseId, "setValue", query, options)).
      catch(this.onLoadFailure.bind(this));
  },

  setLoading: function (/*query, options*/) {
    this.set('isLoading', true);
    this.set('controller.isLoading', true);
  },
  beforeLoad: function (value/*, query, options*/) {
    return value;
  },
  load: function (value/*, query, options*/) {
    return value;
  },
  afterLoad: function (value/*, query, options*/) {
    return value;
  },
  setValue: function (value/*, query, options*/) {
    this.set('loadedValue', value);

    this.set('isLoading', false);
    this.set('controller.isLoading', false);

    this.send("setLoadTime", this.getLoadTime(value));

    return value;
  },
  onLoadFailure: function (error) {
    if(error instanceof UnlinkedPromise) {
      Ember.Logger.warn("Slow down, you are refreshing too fast!");
    }
    else {
      throw(error);
    }
  },

  getLoadTime: function (value) {
    if(value instanceof DS.RecordArray) {
      value = value.get("content.0.record");
    }
    else if(Array.isArray(value)) {
      value = value[0];
    }

    if(value) {
      return Ember.get(value, "loadTime");
    }
  },

  _setControllerModel: Ember.observer("loadedValue", function () {
    var controller = this.get("controller");
    if(controller) {
      controller.set("model", this.get("loadedValue"));
    }
  }),

  setLoader: function (nameSpace) {
    this.set("loader", LoaderService.create({
      nameSpace: nameSpace,
      store: this.get("store"),
      container: Ember.getOwner(this)
    }));
  },

  startCrumbBubble: function () {
    this.send("bubbleBreadcrumbs", []);
  },

  actions: {
    setBreadcrumbs: function (crumbs) {
      var name = this.get("name");
      if(crumbs && crumbs[name]) {
        this.set("breadcrumbs", crumbs[name]);
      }
      return true;
    },
    bubbleBreadcrumbs: function (crumbs) {
      crumbs.unshift.apply(crumbs, this.get("breadcrumbs"));
      return true;
    },
    reload: function () {
      Ember.run.later(this, "loadData", {reload: true});
    },
    willTransition: function () {
      this.set("loadedValue", null);
    },
  }
});
