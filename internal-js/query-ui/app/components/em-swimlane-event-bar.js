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

  bar: null,
  barIndex: 0,

  process: null,
  processor: null,

  classNames: ["em-swimlane-event-bar"],

  fromEvent: Ember.computed("process.events.@each.name", "bar.fromEvent", function () {
    var events = this.get("process.events"),
        fromEventName = this.get("bar.fromEvent");
    return events.find(function (event) {
      return event.name === fromEventName;
    });
  }),
  toEvent: Ember.computed("process.events.@each.name", "bar.toEvent", function () {
    var events = this.get("process.events"),
        toEventName = this.get("bar.toEvent");
    return events.find(function (event) {
      return event.name === toEventName;
    });
  }),

  didInsertElement: Ember.observer("fromEvent.time", "toEvent.time",
      "barIndex", "processor.timeWindow", function () {

    var processor = this.get("processor"),
        fromEventPos = processor.timeToPositionPercent(this.get("fromEvent.time")),
        toEventPos = processor.timeToPositionPercent(this.get("toEvent.time")),
        color = this.get("bar.color") || this.get("process").getBarColor(this.get("barIndex"));

    let myContext = {currentComp: this.$(), eventBar : this.$(".event-bar"), that: this };

    Ember.run.scheduleOnce('afterRender', myContext, function() {
      if(fromEventPos && toEventPos) {
        myContext.currentComp.show();
        myContext.eventBar.css({
          left: fromEventPos + "%",
          right: (100 - toEventPos) + "%",
          "background-color": color,
          "border-color": myContext.that.get("process").getColor()
        });
      }
      else {
        myContext.currentComp.hide();
      }
    });
  }),

  sendMouseAction: function (name, mouseEvent) {
    this.sendAction(name, "event-bar", this.get("process"), {
      mouseEvent: mouseEvent,
      bar: this.get("bar"),
      fromEvent: this.get("fromEvent"),
      toEvent: this.get("toEvent")
    });
  },

  mouseEnter: function (mouseEvent) {
    this.sendMouseAction("showTooltip", mouseEvent);
  },

  mouseLeave: function (mouseEvent) {
    this.sendMouseAction("hideTooltip", mouseEvent);
  },

  mouseUp: function (mouseEvent) {
    this.sendMouseAction("click", mouseEvent);
  }

});
