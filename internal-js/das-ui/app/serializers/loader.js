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

var MoreObject = more.Object;

// TODO - Move to more js
function mapObject(hash, map, thisArg) {
  var mappedObject = Ember.Object.create();
  MoreObject.forEach(map, function (key, value) {
    if(MoreObject.isString(value)) {
      mappedObject.set(key, Ember.get(hash, value));
    }
    else if (MoreObject.isFunction(value)) {
      mappedObject.set(key, value.call(thisArg, hash));
    }
    else {
      Ember.assert("Unknown mapping value");
    }
  });
  return mappedObject;
}

export default DS.JSONSerializer.extend({
  _isLoader: true,

  mergedProperties: ["maps"],
  maps: null,

  extractId: function (modelClass, resourceHash) {
    var id = this._super(modelClass, resourceHash.data),
        nameSpace = resourceHash.nameSpace;

    if(nameSpace) {
      return nameSpace + ":" + id;
    }
    return id;
  },
  extractAttributes: function (modelClass, resourceHash) {
    var maps = this.get('maps'),
        data = resourceHash.data;
    return this._super(modelClass, maps ? mapObject(data, maps, this) : data);
  },
  extractRelationships: function (modelClass, resourceHash) {
    return this._super(modelClass, resourceHash.data);
  },

  extractSinglePayload: function (payload) {
    return payload;
  },
  extractArrayPayload: function (payload) {
    return payload;
  },

  normalizeSingleResponse: function (store, primaryModelClass, payload, id, requestType) {
    payload.data = this.extractSinglePayload(payload.data);
    return this._super(store, primaryModelClass, payload, id, requestType);
  },

  normalizeArrayResponse: function (store, primaryModelClass, payload, id, requestType) {
    var nameSpace = payload.nameSpace,
        meta = payload.data.meta;

    // convert into a _normalizeResponse friendly format
    payload = this.extractArrayPayload(payload.data);
    Ember.assert("Loader expects an array in return for a query", Array.isArray(payload));
    payload = payload.map(function (item) {
      return {
        nameSpace: nameSpace,
        data: item
      };
    });
    payload.meta = meta;

    return this._super(store, primaryModelClass, payload, id, requestType);
  }
});
