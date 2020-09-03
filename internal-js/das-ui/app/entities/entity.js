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

import Ember from 'ember';
import NameMixin from '../mixins/name';

var MoreObject = more.Object;

var Entity = Ember.Object.extend(NameMixin, {

  queryRecord: function (loader, id, options, query, urlParams) {
    var that = this;
    return this.get('store').queryRecord(this.get("name"), {
      id: id,
      nameSpace: loader.get('nameSpace'),
      params: query,
      urlParams: urlParams
    }).then(function (record) {
      that.resetAllNeeds(loader, record, options);
      return that._loadAllNeeds(loader, record, options, urlParams);
    });
  },

  query: function (loader, query, options, urlParams) {
    var that = this;
    return this.get('store').query(this.get("name"), {
      nameSpace: loader.get('nameSpace'),
      params: query,
      urlParams: urlParams
    }).then(function (records) {
      return Ember.RSVP.all(records.map(function (record) {
        that.resetAllNeeds(loader, record, options);
        return that._loadAllNeeds(loader, record, options, urlParams);
      })).then(function () {
       return records;
      });
    });
  },

  normalizeNeed: function(name, needOptions, parentModel, queryParams, urlParams) {
    var need = {
      name: name,
      type: name,
      idKey: "",

      loadType: "", // Possible values lazy, demand
      silent: false,

      //urlParams
      //queryParams
    },
    overrides = {};

    if(typeof needOptions === 'object') {
      if(MoreObject.isFunction(needOptions.urlParams)) {
        overrides.urlParams = needOptions.urlParams.call(needOptions, parentModel);
      }
      if(MoreObject.isFunction(needOptions.queryParams)) {
        overrides.queryParams = needOptions.queryParams.call(needOptions, parentModel);
      }

      overrides.idKey = needOptions.idKey;

      overrides = Ember.Object.create({}, needOptions, overrides);
    }
    else if(typeof needOptions === 'string') {
      overrides.idKey = needOptions;
    }

    if(typeof overrides.idKey === 'string') {
      overrides.withID = true;
      overrides.id = parentModel.get(overrides.idKey);
    }

    if(queryParams) {
      overrides.queryParams = Ember.$.extend({}, overrides.queryParams, queryParams);
    }
    if(urlParams) {
      overrides.urlParams = Ember.$.extend({}, overrides.urlParams, urlParams);
    }

    return Ember.Object.create(need, overrides);
  },

  setNeed: function (parentModel, name, model) {
    if(!parentModel.get("isDeleted")) {
      parentModel.set(name, model);
      parentModel.refreshLoadTime();
    }
    return parentModel;
  },

  _loadNeed: function (loader, parentModel, needOptions, options, index) {
    var needLoader,
        that = this,
        types = needOptions.type,
        type;

    if(!Array.isArray(types)) {
      types = [types];
    }

    index = index || 0;
    type = types[index];

    if(needOptions.withID) {
      needLoader = loader.queryRecord(
        type,
        needOptions.id,
        options,
        needOptions.queryParams,
        needOptions.urlParams
      );
    }
    else {
      needLoader = loader.query(
        type,
        needOptions.queryParams,
        options,
        needOptions.urlParams
      );
    }

    needLoader = needLoader.then(function (model) {
      that.setNeed(parentModel, needOptions.name, model);
      return model;
    });

    needLoader = needLoader.catch(function (err) {
      if(++index < types.length) {
        return that._loadNeed(loader, parentModel, needOptions, options, index);
      }

      if(needOptions.silent) {
        that.setNeed(parentModel, needOptions.name, null);
      }
      else {
        throw(err);
      }
    });

    return needLoader;
  },

  loadNeed: function (loader, parentModel, needName, options, queryParams, urlParams) {
    var needOptions = parentModel.get(`needs.${needName}`);
    Ember.assert(`Need '${needName}' not defined in model!`, needOptions);

    needOptions = this.normalizeNeed(needName, needOptions, parentModel, queryParams, urlParams);
    return this._loadNeed(loader, parentModel, needOptions, options);
  },

  _loadAllNeeds: function (loader, model, options/*, urlParams*/) {
    var needsPromise = this.loadAllNeeds(loader, model, options);

    if(needsPromise) {
      return needsPromise.then(function () {
        return model;
      });
    }

    return model;
  },

  loadAllNeeds: function (loader, parentModel, options, queryParams, urlParams) {
    var needLoaders = [],
        that = this,
        needs = parentModel.get("needs");

    if(needs) {
      MoreObject.forEach(needs, function (name, needOptions) {
        var loadNeed;

        needOptions = that.normalizeNeed(name, needOptions, parentModel, queryParams, urlParams);

        if(MoreObject.isFunction(needOptions.loadType)) {
          needOptions.loadType = needOptions.loadType.call(needOptions, parentModel);
        }

        loadNeed = needOptions.loadType !== "demand";

        if(options && options.demandNeeds) {
          loadNeed = options.demandNeeds.indexOf(name) !== -1;
        }

        if(loadNeed) {
          let needLoader = that._loadNeed(loader, parentModel, needOptions, options);

          if(needOptions.loadType !== "lazy") {
            needLoaders.push(needLoader);
          }
        }
      });
    }

    if(needLoaders.length) {
      return Ember.RSVP.all(needLoaders);
    }
  },

  resetAllNeeds: function (loader, parentModel/*, options*/) {
    var needs = parentModel.get("needs"),
        that = this;

    if(needs) {
      MoreObject.forEach(needs, function (name, needOptions) {
        needOptions = that.normalizeNeed(name, needOptions, parentModel);
        that.setNeed(parentModel, needOptions.name, null);
      });
    }

    return parentModel;
  },
});

export default Entity;
