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

import AbstractRoute from './abstract';

export default AbstractRoute.extend({

  entityType: '',
  fromId: null,

  load: function (value, query/*, options*/) {
    var loader,
        that = this,
        limit = this.get("controller.rowCount") || query.limit,
        entityType = this.get('entityType');

    if(query.id) {
      that.set("loadedRecords", []);
      loader = this.get("loader").queryRecord(entityType, query.id, {
        reload: true
      }).then(function (record) {
        return [record];
      },function () {
        return [];
      });
    }
    else {
      query = Ember.$.extend({}, query, {
        limit: limit + 1
      });
      loader = this.get("loader").query(entityType, query, {reload: true});
    }

    return loader.then(function (records) {
      if(records.get("length") > limit) {
        let lastRecord = records.popObject();
        that.set("controller.moreAvailable", true);
        that.set("fromId", lastRecord.get("entityID"));
      }
      else {
        that.set("controller.moreAvailable", false);
        that.set("fromId", null);
      }
      return records;
    });
  },

  loadNewPage: function () {
    var query = this.get("currentQuery"),
        that = this;

    query = Ember.$.extend({}, query, {
      fromId: this.get("fromId")
    });

    this.set("controller.loadingMore", true);
    return this.load(null, query).then(function (data) {
      if(that.get("controller.loadingMore")) {
        that.set("controller.loadingMore", false);
        that.get("loadedValue").pushObjects(data);
        return data;
      }
    });
  },

  actions: {
    loadPage: function (page) {
      var that = this;
      if(this.get("controller.moreAvailable") && !this.get("controller.loadingMore")) {
        this.send("resetTooltip");
        this.loadNewPage().then(function (data) {
          if(data) {
            that.set("controller.pageNum", page);
          }
          return data;
        });
      }
    },
    reload: function () {
      this.set("controller.loadingMore", false);
      this.set("controller.pageNum", 1);
      this._super();
    },
    willTransition: function () {
      this.set("controller.pageNum", 1);
      this._super();
    },
  }

});
