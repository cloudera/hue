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

export default Ember.Component.extend({

  process: null,
  blocking: null,

  processor: null,

  classNames: ["em-swimlane-blocking-event"],

  blockingEvent: Ember.computed("process.blockingEventName",
      "process.events.@each.name", function () {
    var events = this.get("process.events"),
        blockingEventName = this.get("process.blockingEventName");

    return events.find(function (event) {
      return event.name === blockingEventName;
    });
  }),

  didInsertElement: Ember.observer("blockingEvent.time", "processor.timeWindow", function () {
    var blockTime = this.get("blockingEvent.time"),
        blockerEventHeight;

    if(blockTime && this.get("blocking.endEvent.time") >= blockTime) {
      blockerEventHeight = (this.get("blocking.index") - this.get("process.index")) * 30;

      let myContext = {currentComp: this.$(), eventLine : this.$(".event-line"), that: this };
      Ember.run.scheduleOnce('afterRender', myContext, function() {
        myContext.currentComp.css({
          "left": myContext.that.get("processor").timeToPositionPercent(blockTime) + "%"
        });
        myContext.eventLine.css({
          "height": `${blockerEventHeight}px`,
          "border-color": myContext.that.get("process").getColor()
        });
      });
    }
  }),

  sendMouseAction: function (name, mouseEvent) {
    this.sendAction(name, "blocking-event", this.get("process"), {
      mouseEvent: mouseEvent,
      blocking: this.get("blocking"),
      blockingEvent: this.get("blockingEvent")
    });
  },

  mouseEnter: function (mouseEvent) {
    this.sendMouseAction("showTooltip", mouseEvent);
  },

  mouseLeave: function (mouseEvent) {
    this.sendMouseAction("hideTooltip", mouseEvent);
  },

});
