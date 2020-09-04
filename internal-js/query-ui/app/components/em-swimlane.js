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

import Processor from '../utils/processor';
import Process from '../utils/process';

export default Ember.Component.extend({

  classNames: ["em-swimlane"],

  processes: [],
  processor: null,

  nameComponent: "em-swimlane-process-name",
  visualComponent: "em-swimlane-process-visual",

  tooltipContents: null,
  focusedProcess: null,
  scroll: 0,

  consolidate: false,

  zoom: 100,

  startTime: Ember.computed("processes.@each.startEvent", function () {
    var startTime = this.get("processes.0.startEvent.time");
    this.get("processes").forEach(function (process) {
      var time = process.get("startEvent.time");
      if(startTime > time){
        startTime = time;
      }
    });
    return startTime;
  }),
  endTime: Ember.computed("processes.@each.endEvent", function () {
    var endTime = this.get("processes.0.endEvent.time");
    this.get("processes").forEach(function (process) {
      var time = process.get("endEvent.time");
      if(endTime < time){
        endTime = time;
      }
    });
    return endTime;
  }),

  processorSetup: Ember.on("init", Ember.observer("startTime", "endTime", "processes.length", function () {
    var processor = this.get("processor");
    if(processor ==  null) {
      processor = Processor.create();
      this.set("processor", processor);
    }
    processor.setProperties({
      startTime: this.get("startTime"),
      endTime: this.get("endTime"),
      processCount: this.get("processes.length")
    });
  })),

  didInsertElement: function () {
    Ember.run.scheduleOnce('afterRender', this, function() {
      this.onZoom();
      this.listenScroll();
    });
  },

  onZoom: Ember.observer("zoom", function () {
    var zoom = this.get("zoom");
    this.$(".zoom-panel").css("width", `${zoom}%`);
  }),

  listenScroll: function () {
    var that = this;
    this.$(".process-visuals").scroll(function () {
      that.set("scroll", Ember.$(this).scrollLeft());
    });
  },

  willDestroy: function () {
    // Release listeners
  },

  normalizedProcesses: Ember.computed("processes.@each.blockers", function () {
    var processes = this.get("processes"),
        normalizedProcesses,
        idHash = {},
        containsBlockers = false,
        processor = this.get("processor");

    // Validate and reset blocking
    processes.forEach(function (process) {
      if(!(process instanceof Process)) {
        Ember.Logger.error("em-swimlane : Unknown type, must be of type Process");
      }

      if(process.get("blockers.length")) {
        containsBlockers = true;
      }
      process.set("blocking", Ember.A());
    });

    if(containsBlockers) {
      normalizedProcesses = [];

      // Recreate blocking list
      processes.forEach(function (process) {
        var blockers = process.get("blockers");
        if(blockers) {
          blockers.forEach(function (blocker) {
            blocker.get("blocking").push(process);
          });
        }
      });

      // Give an array of the processes in blocking order
      processes.forEach(function (process) {
        if(process.get("blocking.length") === 0) { // The root processes
          normalizedProcesses.push(process);
          normalizedProcesses.push.apply(normalizedProcesses, process.getAllBlockers());
        }
      });
      normalizedProcesses.reverse();
      normalizedProcesses = normalizedProcesses.filter(function (process, index) {
        // Filters out the recurring processes in the list (after graph traversal), we just
        // need the top processes
        var id = process.get("_id");
        if(idHash[id] === undefined) {
          idHash[id] = index;
        }
        return idHash[id] === index;
      });
    }
    else {
      normalizedProcesses = processes;
    }

    // Set process colors & index
    normalizedProcesses.forEach(function (process, index) {
      process.setProperties({
        color: processor.createProcessColor(index),
        index: index
      });
    });

    return Ember.A(normalizedProcesses);
  }),

  actions: {
    showTooltip: function (type, process, options) {
      this.set("tooltipContents", process.getTooltipContents(type, options));
      this.set("focusedProcess", process);
    },
    hideTooltip: function () {
      this.set("tooltipContents", null);
      this.set("focusedProcess", null);
    },
    click: function (type, process, options) {
      this.sendAction("click", type, process, options);
    }
  }

});
