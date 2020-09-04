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
  processor: null,
  focusedProcess: null,

  classNames: ["em-swimlane-consolidated-process"],
  classNameBindings: ['focused'],

  focused: Ember.computed("process", "focusedProcess", function () {
    return this.get("process") === this.get("focusedProcess");
  }),

  fromPos: Ember.computed("process.consolidateStartTime", "processor.timeWindow", function () {
    var time = this.get("process.consolidateStartTime");
    if(time) {
      return this.get("processor").timeToPositionPercent(time);
    }
  }),

  toPos: Ember.computed("process.consolidateEndTime", "processor.timeWindow", function () {
    var time = this.get("process.consolidateEndTime");
    if(time) {
      return this.get("processor").timeToPositionPercent(time);
    }
  }),

  didInsertElement: Ember.observer("fromPos", "toPos", function () {

    let myContext = {currentComp: this.$(),  that: this };
    
    Ember.run.scheduleOnce('afterRender', myContext, function() {
      var fromPos = myContext.that.get("fromPos"),
          toPos = myContext.that.get("toPos"),
          thisElement = myContext.currentComp;

      if(fromPos && toPos) {
        thisElement.show();
        thisElement.css({
          left: fromPos + "%",
          right: (100 - toPos) + "%",
          "background-color": myContext.that.get("process").getConsolidateColor(),
          "z-index": parseInt(toPos - fromPos)
        });
      }
      else {
        thisElement.hide();
      }
    });
  }),

  sendMouseAction: function (name, mouseEvent) {
    var fromPos = this.get("fromPos") || 0,
        toPos = this.get("toPos") || 0;

    this.sendAction(name, "consolidated-process", this.get("process"), {
      mouseEvent: mouseEvent,
      contribution: parseInt(toPos - fromPos)
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
