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

const TIP_PADDING = 15, // As in em-tooltip.css
      FADE_TIME = 150;

export default Ember.Component.extend({

  title: null,
  description: null,
  properties: null,
  contents: null,

  classNames: ["em-tooltip"],
  classNameBindings: ["arrowPos"],

  x: 0,
  y: 0,

  _contents: null,
  show: false,
  arrowPos: null,

  window: null,
  tip: null,
  bubbles: null,

  _contentObserver: Ember.on("init", Ember.observer("title", "description", "properties", "contents", function () {
    var contents,
        tip = this.get("tip");

    if(this.get("title") || this.get("description") || this.get("properties")){
      contents = [{
        title: this.get("title"),
        description: this.get("description"),
        properties: this.get("properties"),
      }];
    }
    else if(Array.isArray(this.get("contents"))){
      contents = this.get("contents");
    }

    this.set("show", false);
    if(contents) {
      if(tip) {
        tip.hide();
      }
      this.set("_contents", contents);

      this.set("show", true);
      Ember.run.later(this, function () {
        this.set("bubbles", this.$(".bubble"));
        Ember.run.debounce(this, "renderTip", 500);
      });
    }
    else if(tip){
      tip.stop(true).fadeOut(FADE_TIME);
    }
  })),

  didInsertElement: function () {
    Ember.run.scheduleOnce('afterRender', this, function() {
      this.setProperties({
        window: Ember.$(window),
        tip: this.$(),
      });
    });
    Ember.$(document).on("mousemove", this, this.onMouseMove);
  },

  willDestroyElement: function () {
    Ember.$(document).off("mousemove", this.onMouseMove);
  },

  onMouseMove: function (event) {
    event.data.setProperties({
      x: event.clientX,
      y: event.clientY
    });

    if(Ember.get(event, "data.tip") && event.data.get("tip").is(":visible")) {
      event.data.renderTip();
    }
  },

  getBubbleOffset: function (x, bubbleElement, winWidth) {
    var bubbleWidth = Math.max(bubbleElement.width(), 0),
        bubbleOffset = bubbleWidth >> 1;

    if(x - bubbleOffset - TIP_PADDING < 0) {
      bubbleOffset = x - TIP_PADDING;
    }
    else if(x + TIP_PADDING + bubbleOffset > winWidth) {
      bubbleOffset = x - (winWidth - bubbleWidth) + TIP_PADDING;
    }

    return -bubbleOffset;
  },

  renderTip: function () {
    if(this.get("show") && !this.get("isDestroyed")) {
      let x = this.get("x"),
          y = this.get("y"),

          winHeight = this.get("window").height(),
          winWidth = this.get("window").width(),

          showAbove = y < (winHeight >> 1),

          that = this,
          tip = this.get("tip");

      if(x > TIP_PADDING && x < winWidth - TIP_PADDING) {
        if(!showAbove) {
          y -= tip.height();
          this.set("arrowPos", "below");
        }
        else {
          this.set("arrowPos", "above");
        }
      }
      else {
        this.set("arrowPos", null);
      }

      tip.css({
        left: `${x}px`,
        top: `${y}px`,
      });

      tip.fadeIn({
        duration: FADE_TIME,
        start: function () {
          that.get("bubbles").each(function () {
            var bubble = Ember.$(this),
                bubbleOffset = that.getBubbleOffset(x, bubble, winWidth);
            bubble.css("left", `${bubbleOffset}px`);
          });
        }
      });
    }
  }

});
