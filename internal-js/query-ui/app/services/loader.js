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

export default Ember.Service.extend({

  nameSpace: '',
  store: Ember.inject.service('store'),
  cache: null,

  _setOptions: function (options) {
    var nameSpace = options.nameSpace;
    if(nameSpace) {
      // We need to validate only if nameSpace is passed. Else it would be stored in the global space
      Ember.assert(`Invalid nameSpace. Please pass a string instead of ${Ember.inspect(nameSpace)}`, typeof nameSpace === 'string');
      this.set("nameSpace", nameSpace);
    }
  },

  init: function (options) {
    this._super();
    this._setOptions(options || {});
    this.set("cache", Ember.Object.create());
  },

  checkRequisite: function (type) {
    var store = this.get("store"),
        adapter = store.adapterFor(type),
        serializer = store.serializerFor(type);

    Ember.assert(
      `No loader adapter found for type ${type}. Either extend loader and create a custom adapter or extend ApplicationAdapter from loader.`,
      adapter && adapter._isLoader
    );
    Ember.assert(
      `No loader serializer found for type ${type}. Either extend loader and create a custom serializer or extend ApplicationSerializer from loader.`,
      serializer && serializer._isLoader
    );
  },

  lookup: function (type, name, options) {
    name = Ember.String.dasherize(name);
    return this.get("container").lookup(type + ":" + name, options);
  },

  entityFor: function (entityName) {
    var entity = this.lookup("entitie", entityName);
    if(!entity) {
      entity = this.lookup("entitie", "entity", { singleton: false });
      entity.set("name", entityName);
    }
    return entity;
  },

  getCacheKey: function (type, query, id) {
    var parts = [type];

    if(id) {
      parts.push(id);
    }
    if(query) {
      parts.push(JSON.stringify(query));
    }

    return parts.join(":").replace(/\./g, ":");
  },

  loadNeed: function (record, needName, options, queryParams, urlParams) {
    var entity = this.entityFor(record.get("constructor.modelName"));
    return entity.loadNeed(this, record, needName, options, queryParams, urlParams);
  },

  normalizeOptions: function (options) {
    options = options || {};

    if(!options.cache){
      options = Ember.$.extend({}, options);
      options.cache = options.reload ? Ember.Object.create() : this.get("cache");
    }

    return options;
  },

  queryRecord: function(type, id, options, query, urlParams) {
    var entity = this.entityFor(type),
        cacheKey = this.getCacheKey(type, query, id),
        record;

    this.checkRequisite(type);

    options = this.normalizeOptions(options);

    record = options.cache.get(cacheKey);
    if(record) {
      return record;
    }

    record = entity.queryRecord(this, id, options, query, urlParams);
    options.cache.set(cacheKey, record);

    return record;
  },
  query: function(type, query, options, urlParams) {
    var entity = this.entityFor(type),
        cacheKey = this.getCacheKey(type, query),
        records;

    this.checkRequisite(type);

    options = this.normalizeOptions(options);

    records = options.cache.get(cacheKey);
    if(records) {
      return records;
    }

    records = entity.query(this, query, options, urlParams);
    options.cache.set(cacheKey, records);

    return records;
  },

  unloadAll: function (type, skipID) {
    var store = this.get("store"),
        loaderNS = this.get("nameSpace");

    store.peekAll(type).forEach(function (record) {
      var id = record.get("id");

      if(id.substr(0, id.indexOf(":")) === loaderNS && record.get("entityID") !== skipID) {
        store.unloadRecord(record);
      }
    });
  },
});
