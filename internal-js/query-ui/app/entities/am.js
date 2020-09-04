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

import Entity from './entity';

export default Entity.extend({

  idsToJoin: null,
  deferred: null,

  resetJoiner: Ember.on("init", function () {
    this.set("idsToJoin", []);
    this.set("deferred", Ember.RSVP.defer());
  }),

  queryRecord: function (loader, id, options, query, urlParams) {
    this.get("idsToJoin").push(query[this.get("queryPropertyToJoin")]);

    // Yup, only the last query would be taken by design
    Ember.run.once(this, "queryJoinedRecords", loader, options, query, urlParams);

    return this.get("deferred.promise").then(function (recordHash) {
      return recordHash[id];
    });
  },

  queryJoinedRecords: function (loader, options, query, urlParams) {
    var deferred = this.get("deferred");

    query[this.get("queryPropertyToJoin")] = this.get("idsToJoin").join(",");
    this.query(loader, query, options, urlParams).then(function (records) {
      deferred.resolve(records.reduce(function (recordHash, record) {
        recordHash[record.get("entityID")] = record;
        return recordHash;
      }, {}));
    }, function (error) {
      deferred.reject(error);
    }).finally(this.resetJoiner.bind(this));
  }

});
