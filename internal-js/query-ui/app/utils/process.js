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

var processIndex = 1;

export default Ember.Object.extend({
  _id: null,

  name: null,
  events: [], // An array of objects with name and time as mandatory(else error) properties.
  eventBars: null,

  index: 0,
  color: null,

  blockers: null, // Array of processes that's blocking the current process
  blocking: null, // Array of processes blocked by the current process

  blockingEventName: null,

  consolidateStartTime: Ember.computed.oneWay("startEvent.time"),
  consolidateEndTime: Ember.computed.oneWay("endEvent.time"),

  init: function () {
    this.set("_id", `process-id-${processIndex}`);
    processIndex++;
  },

  getColor: function (lightnessFactor) {
    var color = this.get("color"),
        l;

    if(!color) {
      return "#0";
    }
    l = color.l;
    if(lightnessFactor !== undefined) {
      l += 5 + 25 * lightnessFactor;
    }
    return `hsl( ${color.h}, ${color.s}%, ${l}% )`;
  },

  getBarColor: function (barIndex) {
    return this.getColor(1 - (barIndex / this.get("eventBars.length")));
  },

  getConsolidateColor: function () {
    return this.getColor();
  },

  startEvent: Ember.computed("events.@each.time", function () {
    var events = this.get("events"),
        startEvent;
    if(events) {
      startEvent = events[0];
        events.forEach(function (event) {
          if(startEvent.time > event.time) {
            startEvent = event;
          }
      });
    }
    return startEvent;
  }),

  endEvent: Ember.computed("events.@each.time", function () {
    var events = this.get("events"),
        endEvent;
    if(events) {
      endEvent = events[events.length - 1];
      events.forEach(function (event) {
        if(endEvent.time < event.time) {
          endEvent = event;
        }
      });
    }
    return endEvent;
  }),

  getAllBlockers: function (parentHash) {
    var blockers = [],
        currentId = this.get("_id");

    parentHash = parentHash || {}; // To keep a check on cyclic blockers

    parentHash[currentId] = true;
    if(this.get("blockers.length")) {
      this.get("blockers").forEach(function (blocker) {
        if(!parentHash[blocker.get("_id")]) {
          blockers.push(blocker);
          blockers.push.apply(blockers, blocker.getAllBlockers(parentHash));
        }
      });
    }
    parentHash[currentId] = false;

    return blockers;
  },

  getTooltipContents: function (type/*, options*/) {
    return [{
      title: this.get("name"),
      description: "Mouse on : " + type
    }];
  }

});
